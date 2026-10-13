"""E0: carga, limpeza e descrição do CIRA-CIC-DoHBrw-2020.

Lê as três classes de data/raw/cira/Total_CSVs.zip, mede o efeito de cada regra
de limpeza ao lado da Tabela I do artigo, aplica a regra adotada e grava o
conjunto limpo em data/processed/cira.parquet. As contagens, a tabela máquina
por classe, o período de captura e as estatísticas descritivas vão para
results/e0/dados/cira/seed42/, e a leitura dos números para
results/e0/dados/RESUMO.md.

Depois separa treino e teste com a seed 42 e grava em split_counts.json, na
mesma pasta, as amostras por classe no treino, em cada fold de validação e no
teste, ao lado das contagens da Fig. 4 do artigo.

Nenhum modelo é treinado. A seed só entra no sorteio do teste e dos folds.

Uso: uv run python scripts/e0_dados.py
"""

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CIRA_ZIP_MEMBERS,
    CIRA_ZIP_PATH,
    CLASS_NAMES,
    DATA_RAW_DIR,
    FEATURE_COLUMNS,
    ID_COLUMNS,
    PROJECT_ROOT,
    SEED_FIEL,
    SKEW_COLUMNS,
    SKEW_SENTINEL,
    TABLE_I_COUNTS,
    TEST_SIZE,
)
from doh_ids.data import class_counts, clean_flows, feature_matrix, load_cira
from doh_ids.runlog import save_run
from doh_ids.splits import fit_scaler, seen_in_train, stratified_split

MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"

# Colunas gravadas no Parquet: os atributos, o rótulo e a máquina local.
TABLE_COLUMNS = FEATURE_COLUMNS + ["label", "group"]

# Duas definições de linha repetida: idêntica em tudo, ou com o mesmo vetor de
# 29 atributos, que é o que o modelo enxerga.
EXACT = ID_COLUMNS + FEATURE_COLUMNS + ["label"]

# O artigo não descreve a limpeza, só as contagens finais da Tabela I. Cada
# regra candidata é medida: nome, remove NaN, remove infinito, colunas que
# definem linha repetida.
CLEANING_RULES = [
    ("nenhuma (bruto)", False, False, None),
    ("NaN", True, False, None),
    ("infinito", False, True, None),
    ("duplicatas exatas", False, False, EXACT),
    ("duplicatas nos 29 atributos", False, False, FEATURE_COLUMNS),
    ("NaN e infinito", True, True, None),
    ("NaN e duplicatas exatas", True, False, EXACT),
    ("NaN e duplicatas nos 29 atributos", True, False, FEATURE_COLUMNS),
    ("NaN, infinito e duplicatas exatas", True, True, EXACT),
    ("NaN, infinito e duplicatas nos 29 atributos", True, True, FEATURE_COLUMNS),
]
ADOPTED_RULE = "NaN"

# Amostras por classe no treino e no teste do artigo, na ordem de CLASS_NAMES:
# soma de cada linha das matrizes de confusão da Fig. 4a (treino) e 4b (teste).
FIG4_TRAIN_COUNTS = [800829, 17771, 224598]
FIG4_TEST_COUNTS = [88980, 1975, 24955]

# Validação cruzada de 10 folds sobre o treino, como diz a legenda da Fig. 4a.
# O artigo não tem conjunto de validação separado.
CV_FOLDS = 10


def sha256_of(path: Path) -> str:
    """Devolve o SHA-256 do arquivo, em hexadecimal."""
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def read_manifest_entry() -> dict:
    """Devolve a entrada do zip no manifesto, depois de conferir o SHA-256 do arquivo."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    zip_name = CIRA_ZIP_PATH.relative_to(DATA_RAW_DIR).as_posix()
    entry = next(item for item in manifest["files"] if item["path"] == zip_name)
    found = sha256_of(CIRA_ZIP_PATH)
    if found != entry["sha256"]:
        raise SystemExit(f"SHA-256 de {zip_name} difere do manifesto: encontrado {found}.")
    return entry


def cleaning_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Mede cada regra de limpeza: fluxos que ficam por classe e diferença para a Tabela I."""
    rows = []
    for name, drop_nan, drop_inf, duplicate_columns in CLEANING_RULES:
        cleaned, removed = clean_flows(raw, drop_nan, drop_inf, duplicate_columns)
        kept = class_counts(cleaned)
        difference = np.subtract(kept, TABLE_I_COUNTS).tolist()
        rows.append([name, *kept, *removed, *difference])
    columns = (
        ["regra"]
        + CLASS_NAMES
        + [f"removidas {name}" for name in CLASS_NAMES]
        + [f"diferença {name}" for name in CLASS_NAMES]
    )
    return pd.DataFrame(rows, columns=columns)


def capture_tables(flows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Monta a tabela máquina por classe e a tabela de período de captura por classe.

    Usa `group` e `TimeStamp`, por isso roda antes de os identificadores saírem.
    """
    class_name = flows["label"].map(dict(enumerate(CLASS_NAMES)))
    day = pd.to_datetime(flows["TimeStamp"], format="%Y-%m-%d %H:%M:%S").dt.strftime("%Y-%m-%d")

    machines = pd.crosstab(flows["group"], class_name)[CLASS_NAMES]
    machines.index.name = "máquina"
    machines.columns.name = None
    period = pd.DataFrame(
        {
            "máquinas": flows["group"].groupby(class_name).nunique(),
            "dias": day.groupby(class_name).nunique(),
            "primeiro dia": day.groupby(class_name).min(),
            "último dia": day.groupby(class_name).max(),
        }
    ).loc[CLASS_NAMES]
    period.index.name = "classe"
    return machines, period


def shared_with_malicious(values: pd.Series, label: pd.Series) -> int:
    """Conta os valores distintos que aparecem na classe maliciosa e também em outra."""
    malicious = label == CLASS_NAMES.index("Malicious-DoH")
    return len(set(values[malicious]) & set(values[~malicious]))


def repeated_vectors(flows: pd.DataFrame) -> tuple[list[int], int]:
    """Conta os vetores de 29 atributos repetidos no conjunto limpo.

    Devolve as linhas por classe que repetem um vetor já visto, em qualquer
    classe, e o número de vetores distintos presentes em mais de uma classe.
    A primeira ocorrência não conta como repetida; as classes estão na ordem
    dos códigos, então um vetor comum a duas classes conta na de código maior.
    """
    repeated = flows[flows.duplicated(subset=FEATURE_COLUMNS)]
    one_per_class = flows[FEATURE_COLUMNS + ["label"]].drop_duplicates()
    in_many_classes = one_per_class[one_per_class.duplicated(subset=FEATURE_COLUMNS, keep=False)]
    return class_counts(repeated), len(in_many_classes[FEATURE_COLUMNS].drop_duplicates())


def sentinel_counts(flows: pd.DataFrame) -> dict:
    """Conta, por coluna de assimetria e por classe, as linhas com o valor sentinela."""
    is_sentinel = flows[SKEW_COLUMNS] == SKEW_SENTINEL
    by_column = {column: class_counts(flows[is_sentinel[column]]) for column in SKEW_COLUMNS}
    return {"by_column": by_column, "rows_with_any": int(is_sentinel.any(axis=1).sum())}


def descriptive_statistics(flows: pd.DataFrame) -> pd.DataFrame:
    """Devolve as estatísticas descritivas de cada atributo, uma linha por classe e atributo."""
    described = flows.groupby("label")[FEATURE_COLUMNS].describe().stack(level=0)
    described.index = described.index.set_levels(CLASS_NAMES, level=0)
    described.index.names = ["classe", "atributo"]
    return described


def outside_unit_interval(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Conta os valores do teste normalizado que caem fora do intervalo de 0 a 1."""
    # O scaler conhece só o treino: no teste, o valor abaixo do mínimo ou acima
    # do máximo do treino sai do intervalo.
    X_test = fit_scaler(train).transform(feature_matrix(test))
    outside = pd.DataFrame((X_test < 0) | (X_test > 1), columns=FEATURE_COLUMNS)
    by_column = outside.sum()
    return {
        "values": int(by_column.sum()),
        "rows": int(outside.any(axis=1).sum()),
        "by_column": by_column[by_column > 0].to_dict(),
    }


def validation_fold_rows(train: pd.DataFrame) -> list[list[int]]:
    """Conta as amostras por classe do fold de validação de cada uma das 10 rodadas."""
    # Os folds são sorteados só dentro do treino; o teste não participa.
    folds = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED_FIEL)
    return [
        class_counts(train.iloc[validation]) for _, validation in folds.split(train, train["label"])
    ]


def split_counts(table: pd.DataFrame) -> dict:
    """Separa treino e teste e conta as amostras por classe em cada conjunto.

    Devolve o conteúdo de split_counts.json: treino e teste ao lado da Fig. 4,
    os folds de validação, os valores do teste normalizado fora do intervalo de
    0 a 1 e as linhas do teste cujo vetor de atributos existe no treino.
    """
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."
    assert len(train) + len(test) == len(table), "Linha fora do treino e do teste."
    train_rows, test_rows = class_counts(train), class_counts(test)
    train_difference = np.subtract(train_rows, FIG4_TRAIN_COUNTS).tolist()
    test_difference = np.subtract(test_rows, FIG4_TEST_COUNTS).tolist()
    # A Fig. 4b soma 115.910 fluxos no teste. Com fração de 10% a biblioteca
    # arredonda o teste para cima, 115.911, e o fluxo a mais é Non-DoH. O
    # tamanho não é forçado; qualquer outra diferença interrompe o script.
    assert train_difference == [-1, 0, 0], f"Treino {train_rows} difere da Fig. 4a."
    assert test_difference == [1, 0, 0], f"Teste {test_rows} difere da Fig. 4b."

    validation_rows = validation_fold_rows(train)
    seen_rows = class_counts(test[seen_in_train(train, test)])
    return {
        "classes": CLASS_NAMES,
        "seed": SEED_FIEL,
        "test_size": TEST_SIZE,
        "train": {
            "rows": train_rows,
            "total": len(train),
            "fig4a": FIG4_TRAIN_COUNTS,
            "difference": train_difference,
        },
        "test": {
            "rows": test_rows,
            "total": len(test),
            "fig4b": FIG4_TEST_COUNTS,
            "difference": test_difference,
        },
        "validation_folds": {
            "n_folds": CV_FOLDS,
            "validation_rows": validation_rows,
            "train_rows": np.subtract(train_rows, validation_rows).tolist(),
        },
        "test_outside_unit_interval": outside_unit_interval(train, test),
        "test_seen_in_train": {
            "rows": seen_rows,
            "total": sum(seen_rows),
            "fraction": np.divide(seen_rows, test_rows).tolist(),
            "fraction_total": sum(seen_rows) / len(test),
        },
    }


def markdown_table(frame: pd.DataFrame) -> str:
    """Escreve a tabela, com o índice na primeira coluna, em Markdown."""
    frame = frame.reset_index()
    lines = [" | ".join(frame.columns), " | ".join("---" for _ in frame.columns)]
    lines += [" | ".join(str(value) for value in row) for row in frame.itertuples(index=False)]
    return "\n".join(f"| {line} |" for line in lines)


def summary_text(
    rules: pd.DataFrame, machines: pd.DataFrame, period: pd.DataFrame, metrics: dict
) -> str:
    """Monta o texto de RESUMO.md a partir dos números medidos nesta execução."""
    difference_columns = [f"diferença {name}" for name in CLASS_NAMES]
    exact_rules = rules.loc[(rules[difference_columns] == 0).all(axis=1), "regra"].tolist()
    adopted = rules.set_index("regra").loc[ADOPTED_RULE]
    sentinel = pd.DataFrame(metrics["skew_sentinel"]["by_column"], index=CLASS_NAMES).T
    sentinel.index.name = "coluna"
    return f"""# E0: dados do CIRA-CIC-DoHBrw-2020

Gerado por `scripts/e0_dados.py`. Os números vêm de `cira/seed42/metrics.json`
e dos arquivos CSV da mesma pasta.

## Fonte

Membros {", ".join(f"`{member}`" for member in CIRA_ZIP_MEMBERS)} de
`Total_CSVs.zip`, lidos direto do zip. O membro `l1-doh.csv` não é lido: ele
repete os fluxos dos dois arquivos `l2`. Fluxos brutos por classe
({", ".join(CLASS_NAMES)}): {metrics["raw_rows"]}, total {sum(metrics["raw_rows"])}.

## Regras de limpeza ao lado da Tabela I

Tabela I do artigo: {TABLE_I_COUNTS}. As três primeiras colunas numéricas são
os fluxos que ficam; "removidas" são os que saem; "diferença" é o que fica
menos a Tabela I.

{markdown_table(rules.set_index("regra"))}

Regra adotada: remover as linhas com `NaN` em algum dos 29 atributos, e só
isso. Diferença para a Tabela I: {adopted[difference_columns].tolist()}.
Regras com diferença zero nas três classes: {exact_rules}.
O artigo não descreve a limpeza; a regra adotada é a mais simples entre as que
chegam às contagens publicadas. Valores ausentes por coluna, no bruto:
{metrics["nan_by_column"]}.

## O que fica no conjunto limpo

- Fluxos por classe: {metrics["clean_rows"]}, total {sum(metrics["clean_rows"])}.
- Linhas cujo vetor de 29 atributos repete o de uma linha anterior:
  {metrics["repeated_vectors_by_class"]}. Elas não são removidas: removê-las
  é a regra "NaN e duplicatas nos 29 atributos" da tabela acima.
- Vetores de 29 atributos presentes em mais de uma classe:
  {metrics["vectors_in_more_than_one_class"]}.
- Linhas com o valor {SKEW_SENTINEL} em alguma coluna de assimetria:
  {metrics["skew_sentinel"]["rows_with_any"]}. O extrator DoHLyzer grava esse
  valor quando o desvio padrão é zero. Por coluna e por classe:

{markdown_table(sentinel)}

## Máquinas e período de captura

Medido no conjunto limpo, antes de os identificadores serem descartados. A
máquina é o endereço da rede local que aparece na origem ou no destino do fluxo.

{markdown_table(period)}

{markdown_table(machines)}

Máquinas em que há fluxo malicioso e também fluxo de outra classe:
{metrics["machines_shared_with_malicious"]}. Dias em que há fluxo malicioso e
também fluxo de outra classe: {metrics["days_shared_with_malicious"]}.

## Arquivo gerado

`data/processed/cira.parquet`, com os 29 atributos, `label` e `group`.
SHA-256: `{metrics["parquet_sha256"]}`.
"""


def main() -> None:
    """Roda a carga, mede as regras de limpeza e grava o Parquet e os resultados."""
    start = time.perf_counter()
    manifest_entry = read_manifest_entry()

    raw = load_cira()
    raw_rows = class_counts(raw)
    # Cada membro do zip traz uma classe, na ordem dos códigos: contagem
    # diferente da registrada indica membro errado ou fluxo lido em dobro.
    expected_rows = [manifest_entry["rows"][member] for member in CIRA_ZIP_MEMBERS]
    assert raw_rows == expected_rows, f"Bruto {raw_rows} difere do manifesto {expected_rows}."
    print(f"Bruto por classe: {raw_rows}, total {len(raw)}")

    rules = cleaning_table(raw)
    print(rules.to_string(index=False))

    adopted = dict((name, rule) for name, *rule in CLEANING_RULES)[ADOPTED_RULE]
    cleaned, _ = clean_flows(raw, *adopted)
    clean_rows = class_counts(cleaned)
    assert clean_rows == TABLE_I_COUNTS, f"Limpo {clean_rows} difere da Tabela I {TABLE_I_COUNTS}."

    machines, period = capture_tables(cleaned)
    day = cleaned["TimeStamp"].str[:10]

    # A partir daqui os identificadores não existem mais na tabela.
    table = cleaned[TABLE_COLUMNS].reset_index(drop=True)
    assert list(table.columns) == TABLE_COLUMNS
    assert feature_matrix(table).shape[1] == 29
    assert not set(ID_COLUMNS) & set(table.columns)
    assert np.isfinite(feature_matrix(table)).all(axis=None), "NaN ou infinito na saída."

    CIRA_PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(CIRA_PARQUET_PATH, index=False)

    nan_by_column = raw[FEATURE_COLUMNS].isna().sum()
    repeated_by_class, in_many_classes = repeated_vectors(table)
    metrics = {
        "classes": CLASS_NAMES,
        "raw_rows": raw_rows,
        "nan_by_column": nan_by_column[nan_by_column > 0].to_dict(),
        "cleaning_rules": rules.to_dict(orient="records"),
        "adopted_rule": ADOPTED_RULE,
        "table_i": TABLE_I_COUNTS,
        "clean_rows": clean_rows,
        "repeated_vectors_by_class": repeated_by_class,
        "vectors_in_more_than_one_class": in_many_classes,
        "skew_sentinel": sentinel_counts(table),
        "machines_shared_with_malicious": shared_with_malicious(cleaned["group"], cleaned["label"]),
        "days_shared_with_malicious": shared_with_malicious(day, cleaned["label"]),
        "capture_by_class": period.reset_index().to_dict(orient="records"),
        "parquet_columns": TABLE_COLUMNS,
        "parquet_sha256": sha256_of(CIRA_PARQUET_PATH),
    }
    counts = split_counts(table)
    run_dir = save_run(
        experiment="e0",
        track="dados",
        slice_name="cira",
        seed=SEED_FIEL,
        metrics=metrics,
        config={
            "zip_members": CIRA_ZIP_MEMBERS,
            "adopted_rule": ADOPTED_RULE,
            "test_size": TEST_SIZE,
            "cv_folds": CV_FOLDS,
        },
        data_sha256=manifest_entry["sha256"],
        timings={"total_seconds": round(time.perf_counter() - start, 1)},
    )
    rules.to_csv(run_dir / "limpeza_combinacoes.csv", index=False)
    machines.to_csv(run_dir / "maquina_por_classe.csv")
    period.to_csv(run_dir / "periodo_por_classe.csv")
    descriptive_statistics(table).to_csv(run_dir / "estatisticas_descritivas.csv")
    counts_text = json.dumps(counts, indent=2, sort_keys=True, ensure_ascii=False)
    (run_dir / "split_counts.json").write_text(counts_text + "\n", encoding="utf-8")
    summary = summary_text(rules, machines, period, metrics)
    (run_dir.parents[1] / "RESUMO.md").write_text(summary, encoding="utf-8")

    print(f"Limpo por classe: {clean_rows}, total {len(table)}")
    print(period.to_string())
    print(machines.to_string())
    print(
        f"Parquet: {CIRA_PARQUET_PATH.relative_to(PROJECT_ROOT)} sha256 {metrics['parquet_sha256']}"
    )
    print(f"Treino por classe: {counts['train']['rows']}, Fig. 4a {FIG4_TRAIN_COUNTS}")
    print(f"Teste por classe: {counts['test']['rows']}, Fig. 4b {FIG4_TEST_COUNTS}")
    print(f"Validação por classe em cada fold: {counts['validation_folds']['validation_rows']}")
    print(f"Teste normalizado fora de 0 a 1: {counts['test_outside_unit_interval']}")
    print(f"Teste com vetor de atributos presente no treino: {counts['test_seen_in_train']}")
    print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
