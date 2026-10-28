"""E0: carga, limpeza e descrição do CIRA-CIC-DoHBrw-2020.

Lê as três classes de data/raw/cira/Total_CSVs.zip, mede o efeito de cada regra
de limpeza ao lado da Tabela I do artigo, aplica a regra adotada e grava o
conjunto limpo em data/processed/cira.parquet. As contagens, a tabela máquina
por classe, o período de captura e as estatísticas descritivas vão para
results/e0/dados/cira/seed42/, e a leitura dos números para
results/e0/dados/RESUMO.md.

Depois separa treino e teste com a seed 42 e grava em split_counts.json, na
mesma pasta, as amostras por classe no treino, em cada fold de validação e no
teste, ao lado das contagens da Fig. 4 do artigo, e as linhas do teste cujo
vetor de atributos também existe no treino.

Por fim desenha a figura equivalente à Fig. 2 do artigo, a densidade por classe
de três atributos, e grava na mesma pasta a imagem e, em CSV, as curvas
desenhadas.

Nenhum modelo é treinado. A seed só entra no sorteio do teste e dos folds.

Uso: uv run python scripts/e0_dados.py
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy.stats import gaussian_kde
from sklearn.model_selection import StratifiedKFold

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CIRA_ZIP_MEMBERS,
    CIRA_ZIP_PATH,
    CLASS_NAMES,
    CV_FOLDS,
    CV_SHUFFLE,
    DATA_RAW_DIR,
    FEATURE_COLUMNS,
    FIG2_GRID_POINTS,
    FIG2_PANELS,
    FIG4_TEST_COUNTS,
    FIG4_TRAIN_COUNTS,
    ID_COLUMNS,
    PROJECT_ROOT,
    SEED_FIEL,
    SKEW_COLUMNS,
    SKEW_SENTINEL,
    TABLE_I_COUNTS,
    TEST_SIZE,
)
from doh_ids.data import class_counts, clean_flows, feature_matrix, load_cira, sha256_of
from doh_ids.runlog import save_run
from doh_ids.splits import fit_scaler, seen_in_train, stratified_split
from doh_ids.summary import frame_markdown_table

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

# Cores das classes na Fig. 2 do artigo, na ordem dos códigos.
FIG2_COLORS = ["tab:blue", "tab:green", "tab:red"]


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


def capture_day(flows: pd.DataFrame) -> pd.Series:
    """Devolve o dia de captura de cada fluxo, em texto no formato ano-mês-dia."""
    return pd.to_datetime(flows["TimeStamp"], format="%Y-%m-%d %H:%M:%S").dt.strftime("%Y-%m-%d")


def capture_tables(flows: pd.DataFrame, day: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Monta a tabela máquina por classe e a tabela de período de captura por classe.

    Usa `group` e o dia de captura, por isso roda antes de os identificadores saírem.
    """
    class_name = flows["label"].map(dict(enumerate(CLASS_NAMES)))

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
    """Conta as amostras por classe do fold de validação de cada rodada."""
    # Os folds são sorteados só dentro do treino; o teste não participa.
    folds = StratifiedKFold(n_splits=CV_FOLDS, shuffle=CV_SHUFFLE, random_state=SEED_FIEL)
    return [
        class_counts(train.iloc[validation]) for _, validation in folds.split(train, train["label"])
    ]


def seen_in_train_counts(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Conta, por classe, as linhas do teste cujo vetor de atributos existe no treino.

    Separa dois casos: o vetor está no treino com o mesmo rótulo da linha do
    teste, ou está com outro rótulo. Uma linha entra nos dois quando o treino
    tem o vetor dela com mais de um rótulo; `both_labels_rows` conta essas.
    """
    seen = seen_in_train(train, test)
    same_label = np.zeros(len(test), dtype=bool)
    other_label = np.zeros(len(test), dtype=bool)
    for code in range(len(CLASS_NAMES)):
        of_class = (test["label"] == code).to_numpy()
        same_label |= of_class & seen_in_train(train[train["label"] == code], test)
        other_label |= of_class & seen_in_train(train[train["label"] != code], test)
    assert np.array_equal(same_label | other_label, seen), "Linha vista sem rótulo no treino."

    seen_rows, test_rows = class_counts(test[seen]), class_counts(test)
    return {
        "rows": seen_rows,
        "total": sum(seen_rows),
        "fraction": np.divide(seen_rows, test_rows).tolist(),
        "fraction_total": sum(seen_rows) / len(test),
        "same_label_rows": class_counts(test[same_label]),
        "other_label_rows": class_counts(test[other_label]),
        "both_labels_rows": class_counts(test[same_label & other_label]),
    }


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
            "shuffle": CV_SHUFFLE,
            "validation_rows": validation_rows,
            "train_rows": np.subtract(train_rows, validation_rows).tolist(),
        },
        "test_outside_unit_interval": outside_unit_interval(train, test),
        "test_seen_in_train": seen_in_train_counts(train, test),
    }


def fig2_densities(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estima a densidade por classe dos três atributos da Fig. 2 do artigo.

    Devolve as curvas, uma linha por atributo, classe e ponto do eixo, e a
    cobertura: por atributo e classe, quantos fluxos caem na faixa do eixo, a
    posição do pico da curva e os quartis do atributo em todos os fluxos da
    classe. Usa o conjunto limpo inteiro, sem normalizar e sem amostrar.
    """
    curves, coverage = [], []
    for column, _, low, high, log_scale in FIG2_PANELS:
        # No eixo logarítmico a densidade é estimada sobre o logaritmo do valor,
        # e a área sob a curva vale 1 por década, não por unidade do atributo.
        to_axis = np.log10 if log_scale else np.asarray
        grid = np.linspace(to_axis(low), to_axis(high), FIG2_GRID_POINTS)
        x = 10**grid if log_scale else grid
        for code, name in enumerate(CLASS_NAMES):
            values = table.loc[table["label"] == code, column]
            # A densidade usa só os fluxos dentro da faixa do eixo. Com todos
            # os fluxos, os valores extremos alargam a banda do estimador e a
            # curva fica plana na faixa que a figura do artigo mostra.
            inside = values[values.between(low, high)].to_numpy()
            # Estimador de núcleo gaussiano, como o artigo declara na Seção
            # III-A, com a largura de banda padrão da biblioteca (regra de
            # Scott). Cada classe é estimada sozinha: a área de cada curva é 1,
            # como na figura do artigo, em que a classe benigna, a menor, tem
            # pico da mesma ordem das outras.
            density = gaussian_kde(to_axis(inside))(grid)
            curves.append(
                pd.DataFrame({"atributo": column, "classe": name, "x": x, "densidade": density})
            )
            quartiles = values.quantile([0.25, 0.5, 0.75]).tolist()
            coverage.append(
                [column, name, len(values), len(inside), x[density.argmax()], *quartiles]
            )
    columns = ["atributo", "classe", "fluxos", "fluxos na faixa", "pico da densidade"]
    columns += ["1º quartil", "mediana", "3º quartil"]
    return pd.concat(curves, ignore_index=True), pd.DataFrame(coverage, columns=columns)


def draw_fig2(curves: pd.DataFrame) -> Figure:
    """Desenha os três painéis da Fig. 2 do artigo, com uma curva por classe."""
    # A figura é criada sem a interface pyplot, que abriria uma janela: assim o
    # script roda em máquina sem tela.
    figure = Figure(figsize=(15, 4), layout="constrained")
    axes = figure.subplots(1, len(FIG2_PANELS))
    for axis, letter, (column, unit, _, _, log_scale) in zip(axes, "abc", FIG2_PANELS, strict=True):
        panel = curves[curves["atributo"] == column]
        for name, color in zip(CLASS_NAMES, FIG2_COLORS, strict=True):
            curve = panel[panel["classe"] == name]
            axis.plot(curve["x"], curve["densidade"], color=color, label=name)
        if log_scale:
            axis.set_xscale("log")
        scale = ", escala logarítmica" if log_scale else ""
        axis.set_xlabel(f"({letter}) {column} ({unit}{scale})")
        axis.set_ylabel("Densidade (1/década)" if log_scale else f"Densidade (1/{unit})")
        axis.set_ylim(bottom=0)
        axis.legend(title="Classe")
    return figure


def write_fig2(run_dir: Path, curves: pd.DataFrame, coverage: pd.DataFrame) -> None:
    """Grava em `run_dir` a imagem da figura, as curvas desenhadas e a cobertura."""
    # A imagem depende da versão da biblioteca e das fontes da máquina. As
    # curvas vão também em CSV, com seis algarismos significativos: é esse
    # arquivo que duas execuções comparam.
    curves.to_csv(run_dir / "fig2_densidade.csv", index=False, float_format="%.6g")
    coverage.to_csv(run_dir / "fig2_faixa.csv", index=False, float_format="%.6g")
    # Sem o campo com a versão da biblioteca, a imagem só muda se o desenho mudar.
    draw_fig2(curves).savefig(run_dir / "fig2_densidade.png", dpi=150, metadata={"Software": None})


# Afirmações do artigo sobre a Fig. 2 (Seção III-A e legenda), cada uma com as
# comparações que a põem à prova: estatística, atributo, as duas classes e a
# relação que o artigo afirma entre a primeira e a segunda.
FIG2_CLAIMS = [
    (
        "(a) os bytes recebidos são mais no Malicious-DoH do que no Non-DoH e no Benign-DoH",
        [
            ("mediana", "FlowBytesReceived", "Malicious-DoH", "Non-DoH", "maior que"),
            ("mediana", "FlowBytesReceived", "Malicious-DoH", "Benign-DoH", "maior que"),
        ],
    ),
    (
        "(b) e (c) os fluxos DoH têm variância do comprimento de pacote menor que a dos Non-DoH",
        [
            ("mediana", "PacketLengthVariance", "Benign-DoH", "Non-DoH", "menor que"),
            ("mediana", "PacketLengthVariance", "Malicious-DoH", "Non-DoH", "menor que"),
        ],
    ),
    (
        "a variância do Malicious-DoH é sempre relativamente alta, ao contrário da do Benign-DoH",
        [("1º quartil", "PacketLengthVariance", "Malicious-DoH", "Benign-DoH", "maior que")],
    ),
]


def fig2_verdicts(coverage: pd.DataFrame) -> str:
    """Confronta cada afirmação do artigo sobre a Fig. 2 com as medianas e os quartis medidos."""
    measured = coverage.set_index(["atributo", "classe"])
    lines = []
    for claim, comparisons in FIG2_CLAIMS:
        lines.append(f"- **Afirmação: {claim}.**")
        for statistic, column, first, second, expected in comparisons:
            value = measured.loc[(column, first), statistic]
            reference = measured.loc[(column, second), statistic]
            if value == reference:
                found = "igual a"
            else:
                found = "maior que" if value > reference else "menor que"
            verdict = "sustenta" if found == expected else "não sustenta"
            lines.append(
                f"  - {statistic} de `{column}`: {value:.6g} no {first}, {found} {reference:.6g} "
                f"no {second}. O número {verdict} a afirmação para o {first} diante do {second}."
            )
    return "\n".join(lines)


def fig2_summary_text(coverage: pd.DataFrame) -> str:
    """Monta a seção de RESUMO.md sobre a figura equivalente à Fig. 2 do artigo."""
    panels = pd.DataFrame(
        [
            [column, unit, f"{low} a {high}", "logarítmico" if log_scale else "linear"]
            for column, unit, low, high, log_scale in FIG2_PANELS
        ],
        columns=["atributo", "unidade", "faixa do eixo", "eixo"],
    )
    measured = coverage.copy()
    fractions = measured["fluxos na faixa"] / measured["fluxos"]
    measured.insert(4, "fração na faixa", [f"{fraction:.2%}" for fraction in fractions])
    number_columns = ["pico da densidade", "1º quartil", "mediana", "3º quartil"]
    measured[number_columns] = measured[number_columns].map(lambda value: f"{value:.6g}")
    return f"""
## Fig. 2: densidade por classe

Figura em `cira/seed42/fig2_densidade.png`, com as curvas desenhadas em
`cira/seed42/fig2_densidade.csv` e os números desta seção em
`cira/seed42/fig2_faixa.csv`. Medida no conjunto limpo inteiro, antes de separar
treino e teste e sem normalizar. Nenhum fluxo é sorteado.

Como a Fig. 2 do artigo, a figura tem três painéis, um por atributo, e uma curva
por classe, estimada com núcleo gaussiano (KDE) e a largura de banda padrão do
SciPy, em {FIG2_GRID_POINTS} pontos do eixo. Cada classe é estimada sozinha: a
área de cada curva é 1. As faixas dos eixos foram lidas na figura do artigo, que
não diz como recortou os dados nem que largura de banda usou:

{frame_markdown_table(panels.set_index("atributo"))}

A densidade usa só os fluxos dentro da faixa do eixo; "fração na faixa" diz
quantos são. Fluxo com variância zero fica fora do terceiro painel, porque o
eixo é logarítmico. Nesse painel a densidade é estimada sobre o logaritmo de
base 10 da variância. "Pico da densidade" é o valor do atributo em que a curva
da classe é mais alta. Os quartis são do atributo em todos os fluxos da classe,
dentro e fora da faixa.

{frame_markdown_table(measured.set_index("atributo"))}

O que o artigo afirma (Seção III-A e legenda da Fig. 2), para ler ao lado da
tabela:

- (a) o número de bytes enviados ou recebidos é maior no Malicious-DoH do que no
  Non-DoH e no Benign-DoH. Comparar as linhas de `FlowBytesReceived`.
- (b) e (c) os fluxos DoH têm comprimento de pacote mais regular, com variância
  menor que a dos Non-DoH, o que a figura do artigo mostra como uma curva
  estreita para o Malicious-DoH. Comparar o primeiro e o terceiro quartis de
  `PacketLengthVariance`.
- A variância do Malicious-DoH é sempre relativamente alta, ao contrário da do
  Benign-DoH. Comparar o primeiro quartil de `PacketLengthVariance` das duas
  classes.

### Veredito por afirmação

Cada afirmação é confrontada com a mediana, ou com o primeiro quartil, do
atributo em todos os fluxos de cada classe, lidos da tabela acima. É uma
comparação de dois números, não um teste estatístico, e não olha a forma das
curvas.

{fig2_verdicts(coverage)}
"""


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

Gerado por `scripts/e0_dados.py`. Os números vêm de `cira/seed42/metrics.json`,
de `cira/seed42/split_counts.json` e dos arquivos CSV da mesma pasta.

## Fonte

Membros {", ".join(f"`{member}`" for member in CIRA_ZIP_MEMBERS)} de
`Total_CSVs.zip`, lidos direto do zip. O membro `l1-doh.csv` não é lido: ele
repete os fluxos dos dois arquivos `l2`. Fluxos brutos por classe
({", ".join(CLASS_NAMES)}): {metrics["raw_rows"]}, total {sum(metrics["raw_rows"])}.

## Regras de limpeza ao lado da Tabela I

Tabela I do artigo: {TABLE_I_COUNTS}. As três primeiras colunas numéricas são
os fluxos que ficam; "removidas" são os que saem; "diferença" é o que fica
menos a Tabela I.

{frame_markdown_table(rules.set_index("regra"))}

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

{frame_markdown_table(sentinel)}

## Máquinas e período de captura

Medido no conjunto limpo, antes de os identificadores serem descartados. A
máquina é o endereço da rede local que aparece na origem ou no destino do fluxo.

{frame_markdown_table(period)}

{frame_markdown_table(machines)}

Máquinas em que há fluxo malicioso e também fluxo de outra classe:
{metrics["machines_shared_with_malicious"]}. Dias em que há fluxo malicioso e
também fluxo de outra classe: {metrics["days_shared_with_malicious"]}.

## Arquivo gerado

`data/processed/cira.parquet`, com os 29 atributos, `label` e `group`.
SHA-256: `{metrics["parquet_sha256"]}`.
"""


def split_summary_text(counts: dict) -> str:
    """Monta a seção de RESUMO.md sobre treino, validação e teste a partir de `counts`."""
    train, test, folds = counts["train"], counts["test"], counts["validation_folds"]
    seen = counts["test_seen_in_train"]
    sets = pd.DataFrame(
        {
            "treino": train["rows"],
            "Fig. 4a": train["fig4a"],
            "diferença no treino": train["difference"],
            "teste": test["rows"],
            "Fig. 4b": test["fig4b"],
            "diferença no teste": test["difference"],
        },
        index=pd.Index(CLASS_NAMES, name="classe"),
    )
    seen_table = pd.DataFrame(
        {
            "linhas do teste": test["rows"],
            "vetor presente no treino": seen["rows"],
            "fração": [f"{fraction:.2%}" for fraction in seen["fraction"]],
            "com o mesmo rótulo": seen["same_label_rows"],
            "com outro rótulo": seen["other_label_rows"],
            "com os dois": seen["both_labels_rows"],
        },
        index=pd.Index(CLASS_NAMES, name="classe"),
    )
    fold_table = pd.DataFrame(
        folds["validation_rows"],
        columns=CLASS_NAMES,
        index=pd.RangeIndex(1, folds["n_folds"] + 1, name="fold"),
    )
    outside = counts["test_outside_unit_interval"]
    clean_total = train["total"] + test["total"]
    return f"""
## Treino, validação e teste

Gerado de `cira/seed42/split_counts.json`. Sorteio estratificado por classe,
seed {counts["seed"]}, fração de teste {counts["test_size"]}. Treino:
{train["total"]} fluxos; teste: {test["total"]}.

{frame_markdown_table(sets)}

As matrizes da Fig. 4 somam {sum(train["fig4a"])} fluxos no treino e
{sum(test["fig4b"])} no teste. A fração {counts["test_size"]} de {clean_total}
fluxos não é um número inteiro, e a biblioteca arredonda o tamanho do teste
para cima: o teste fica com {test["total"]} fluxos, e o fluxo que passa do
treino para o teste é Non-DoH. O tamanho não é forçado para igualar a figura.

### Validação

O artigo não tem conjunto de validação separado: a validação é cruzada, com
{folds["n_folds"]} folds estratificados sorteados só dentro do treino
(embaralhamento: {folds["shuffle"]}, seed {counts["seed"]}). O teste não entra
em nenhum fold. Amostras por classe no fold de validação de cada rodada:

{frame_markdown_table(fold_table)}

### Teste com vetor de atributos presente no treino

Linhas do teste cujos 29 atributos são iguais aos de alguma linha do treino:
{seen["total"]} de {test["total"]} ({seen["fraction_total"]:.2%}). Os índices
de treino e teste são disjuntos; o que se repete é o vetor de atributos, porque
o conjunto limpo mantém as linhas repetidas. "Com o mesmo rótulo" conta a linha
do teste cujo vetor está no treino com a classe dela; "com outro rótulo", a que
tem o vetor no treino com classe diferente; "com os dois", a que está nos dois
casos.

{frame_markdown_table(seen_table)}

### Teste normalizado

O normalizador é ajustado só no treino. No teste normalizado,
{outside["values"]} valores em {outside["rows"]} linhas ficam fora do
intervalo de 0 a 1, nas colunas {outside["by_column"]}.
"""


def model_table(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Devolve o conjunto limpo só com as colunas do Parquet, sem os identificadores."""
    table = cleaned[TABLE_COLUMNS].reset_index(drop=True)
    assert list(table.columns) == TABLE_COLUMNS
    assert feature_matrix(table).shape[1] == len(FEATURE_COLUMNS)
    assert not set(ID_COLUMNS) & set(table.columns)
    assert np.isfinite(feature_matrix(table)).all(axis=None), "NaN ou infinito na saída."
    return table


def write_tables(
    run_dir: Path,
    rules: pd.DataFrame,
    machines: pd.DataFrame,
    period: pd.DataFrame,
    table: pd.DataFrame,
    counts: dict,
) -> None:
    """Grava em `run_dir` os arquivos CSV e o split_counts.json."""
    rules.to_csv(run_dir / "limpeza_combinacoes.csv", index=False)
    machines.to_csv(run_dir / "maquina_por_classe.csv")
    period.to_csv(run_dir / "periodo_por_classe.csv")
    descriptive_statistics(table).to_csv(run_dir / "estatisticas_descritivas.csv")
    counts_text = json.dumps(counts, indent=2, sort_keys=True, ensure_ascii=False)
    (run_dir / "split_counts.json").write_text(counts_text + "\n", encoding="utf-8")


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

    day = capture_day(cleaned)
    machines, period = capture_tables(cleaned, day)

    # A partir daqui os identificadores não existem mais na tabela.
    table = model_table(cleaned)
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
    curves, coverage = fig2_densities(table)
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
            "cv_shuffle": CV_SHUFFLE,
        },
        data_sha256=manifest_entry["sha256"],
        timings={"total_seconds": round(time.perf_counter() - start, 1)},
    )
    write_tables(run_dir, rules, machines, period, table, counts)
    write_fig2(run_dir, curves, coverage)
    summary = summary_text(rules, machines, period, metrics) + split_summary_text(counts)
    summary += fig2_summary_text(coverage)
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
