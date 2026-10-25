"""E6, dados: conferência e carga do segundo dataset.

Lê o DoH-Tunnel-Traffic-HKD (data/raw/hkd/) e o dataset combinado CIRA + HKD
(data/raw/combinado/), confere o cabeçalho de cada arquivo contra as 35 colunas
do CIRA-CIC-DoHBrw-2020, conta os fluxos por classe, por origem e por
ferramenta ao lado das contagens do README de cada dataset e mede as réplicas
do HKD. Aplica a mesma limpeza usada no CIRA e grava três tabelas em
data/processed/: hkd.parquet, combinado.parquet (como publicado) e
combinado_sem_replicas.parquet (cada fluxo do HKD uma única vez).

As contagens de cada tabela vão para results/e6/dados/<tabela>/seed42/, e a
leitura dos números, com a justificativa da escolha do dataset, para
results/e6/dados/RESUMO.md.

Nenhum modelo é treinado e nada é sorteado: a seed só dá nome à pasta.

Uso: uv run python scripts/e6_dados.py
"""

import codecs
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from doh_ids.config import (
    CLASS_NAMES,
    COMBINED_CSV_PATHS,
    COMBINED_PARQUET_PATH,
    COMBINED_UNIQUE_PARQUET_PATH,
    DATA_RAW_DIR,
    FEATURE_COLUMNS,
    HKD_AUGMENTED_CSV_PATH,
    HKD_CSV_PATH,
    HKD_PARQUET_PATH,
    HKD_REPLICAS,
    HKD_ROUNDING_TOLERANCE,
    ID_COLUMNS,
    ORIGINS,
    PROJECT_ROOT,
    README_CLASS_ROWS,
    README_TOOL_ROWS,
    SECOND_DATASET_COLUMNS,
    SEED_FIEL,
    TABLE_I_COUNTS,
    TOOL_ORIGIN,
)
from doh_ids.data import (
    CSV_COLUMNS,
    class_counts,
    clean_flows,
    column_differences,
    feature_matrix,
    load_combined,
    load_hkd,
    read_flow_csv,
    read_header,
    sha256_of,
    without_replicas,
)
from doh_ids.runlog import save_run
from doh_ids.summary import frame_markdown_table

MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"

# A mesma limpeza adotada no CIRA: sai a linha com valor ausente em algum dos 29
# atributos, e só ela. Os argumentos são remover ausentes, remover infinitos e
# colunas que definem linha repetida.
CLEANING = {"drop_nan": True, "drop_inf": False, "duplicate_columns": None}

HKD_TOOLS = [tool for tool, origin in TOOL_ORIGIN.items() if origin == "HKD"]

# Tabelas gravadas: nome, que é também o da pasta de resultados, pasta dos
# arquivos de origem em data/raw/ e caminho do Parquet.
SLICES = [
    ("hkd", "hkd/", HKD_PARQUET_PATH),
    ("combinado", "combinado/", COMBINED_PARQUET_PATH),
    ("combinado_sem_replicas", "combinado/", COMBINED_UNIQUE_PARQUET_PATH),
]


def checked_sha256(manifest: dict, path: Path) -> str:
    """Devolve o SHA-256 do arquivo, depois de conferi-lo com o manifesto."""
    name = path.relative_to(DATA_RAW_DIR).as_posix()
    entry = next(item for item in manifest["files"] if item["path"] == name)
    found = sha256_of(path)
    if found != entry["sha256"]:
        raise SystemExit(f"SHA-256 de {name} difere do manifesto: encontrado {found}.")
    return found


def header_report(path: Path) -> dict:
    """Compara o cabeçalho do arquivo com as 35 colunas esperadas e diz se ele tem BOM."""
    header = read_header(path)
    with path.open("rb") as file:
        has_bom = file.read(len(codecs.BOM_UTF8)) == codecs.BOM_UTF8
    report = {"bom": has_bom, "columns": len(header), "same_order": header == CSV_COLUMNS}
    report |= column_differences(header)
    # Coluna ausente ou com outro nome faria o modelo receber atributo trocado.
    assert report["same_order"], f"Cabeçalho de {path.name} difere do esperado: {report}."
    return report


def tool_counts(flows: pd.DataFrame) -> dict:
    """Conta os fluxos de cada ferramenta de túnel, na ordem de TOOL_ORIGIN."""
    return {tool: int((flows["tool"] == tool).sum()) for tool in TOOL_ORIGIN}


def origin_counts(flows: pd.DataFrame) -> dict:
    """Conta os fluxos por classe dentro de cada conjunto de origem."""
    return {origin: class_counts(flows[flows["origin"] == origin]) for origin in ORIGINS}


def hkd_capture(path: Path) -> dict:
    """Mede, nos identificadores do HKD, as máquinas e o período de captura.

    Lê o arquivo de novo, com os identificadores, só para esta descrição: eles
    não entram em nenhuma das tabelas gravadas.
    """
    raw = read_flow_csv(path)
    machines = sorted(set(raw["SourceIP"]) | set(raw["DestinationIP"]))
    day = pd.to_datetime(raw["TimeStamp"], format="%Y/%m/%d %H:%M").dt.strftime("%Y-%m-%d")
    return {
        "machines": machines,
        "rows_between_two_distinct_machines": int((raw["SourceIP"] != raw["DestinationIP"]).sum()),
        "first_day": day.min(),
        "last_day": day.max(),
        "integer_valued_features": [
            column for column in FEATURE_COLUMNS if pd.api.types.is_integer_dtype(raw[column])
        ],
    }


def replica_report(replicated: pd.DataFrame, hkd: pd.DataFrame) -> dict:
    """Confere que `replicated` é `hkd` com cada fluxo repetido HKD_REPLICAS vezes.

    `replicated` são as linhas do HKD de um arquivo replicado e `hkd`, os fluxos
    de Total-48h.csv. Interrompe o script se algum fluxo tiver outro número de
    cópias ou se os fluxos distintos não forem os de `hkd`.
    """
    key = FEATURE_COLUMNS + ["tool"]
    copies = replicated.groupby(key).size()
    assert (copies == HKD_REPLICAS).all(), f"Fluxo com número de cópias fora de {HKD_REPLICAS}."

    # Os arquivos replicados gravam os números arredondados, então os fluxos
    # não são idênticos aos de Total-48h.csv. Ordenadas pelos atributos, as
    # duas tabelas ficam alinhadas e são comparadas com tolerância.
    distinct = without_replicas(replicated).sort_values(key).reset_index(drop=True)
    original = hkd.sort_values(key).reset_index(drop=True)
    assert len(distinct) == len(original), "Fluxos distintos em número diferente do HKD."
    assert (distinct["tool"] == original["tool"]).all(), "Ferramenta diferente da do HKD."
    difference = np.abs(feature_matrix(distinct) - feature_matrix(original)).to_numpy().max()
    assert difference <= HKD_ROUNDING_TOLERANCE, f"Diferença de {difference} para o HKD."
    return {
        "rows": len(replicated),
        "distinct_flows": len(distinct),
        "copies_per_flow": HKD_REPLICAS,
        "max_difference_to_total_48h": float(difference),
    }


def cleaned_table(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[int]]:
    """Aplica a limpeza e devolve a tabela a gravar e as linhas removidas por classe."""
    cleaned, removed = clean_flows(raw, **CLEANING)
    table = cleaned.reset_index(drop=True)
    assert list(table.columns) == SECOND_DATASET_COLUMNS
    assert feature_matrix(table).shape[1] == len(FEATURE_COLUMNS)
    assert not set(ID_COLUMNS) & set(table.columns)
    assert np.isfinite(feature_matrix(table)).all(axis=None), "NaN ou infinito na saída."
    assert set(table["label"]) <= set(range(len(CLASS_NAMES))), "Rótulo fora de 0, 1 e 2."
    assert set(table["origin"]) <= set(ORIGINS), "Origem desconhecida."
    return table, removed


def table_metrics(raw: pd.DataFrame, table: pd.DataFrame, removed: list[int], path: Path) -> dict:
    """Grava a tabela em Parquet e devolve as contagens antes e depois da limpeza."""
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(path, index=False)
    nan_by_column = raw[FEATURE_COLUMNS].isna().sum()
    return {
        "classes": CLASS_NAMES,
        "raw_rows": class_counts(raw),
        "raw_rows_by_origin": origin_counts(raw),
        "raw_rows_by_tool": tool_counts(raw),
        "nan_by_column": nan_by_column[nan_by_column > 0].to_dict(),
        "infinite_values": int(np.isinf(feature_matrix(raw)).sum().sum()),
        "removed_rows": removed,
        "clean_rows": class_counts(table),
        "clean_rows_by_origin": origin_counts(table),
        "clean_rows_by_tool": tool_counts(table),
        "parquet_columns": SECOND_DATASET_COLUMNS,
        "parquet_sha256": sha256_of(path),
    }


def range_table(cira: pd.DataFrame, hkd: pd.DataFrame) -> pd.DataFrame:
    """Compara, por atributo, a faixa de valores do HKD com a do CIRA.

    `cira` são os fluxos limpos do CIRA, das três classes, e `hkd`, os do HKD.
    Conta os fluxos do HKD abaixo do mínimo e acima do máximo do CIRA.
    """
    cira, hkd = feature_matrix(cira), feature_matrix(hkd)
    table = pd.DataFrame(
        {
            "mínimo CIRA": cira.min(),
            "máximo CIRA": cira.max(),
            "mínimo HKD": hkd.min(),
            "máximo HKD": hkd.max(),
            "fluxos do HKD abaixo do mínimo": (hkd < cira.min()).sum(),
            "fluxos do HKD acima do máximo": (hkd > cira.max()).sum(),
        }
    )
    table.index.name = "atributo"
    return table


def median_table(cira_malicious: pd.DataFrame, hkd: pd.DataFrame) -> pd.DataFrame:
    """Põe lado a lado a mediana de cada atributo no malicioso do CIRA e no HKD."""
    table = pd.DataFrame(
        {
            "CIRA, Malicious-DoH": feature_matrix(cira_malicious).median(),
            "HKD": feature_matrix(hkd).median(),
        }
    )
    table.index.name = "atributo"
    return table


def count_tables(metrics: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Monta as tabelas de fluxos por classe e por ferramenta das três tabelas gravadas."""
    by_class, by_tool = {}, {"README do combinado": README_TOOL_ROWS}
    for name, values in metrics.items():
        by_class[f"{name}, bruto"] = values["raw_rows"]
        by_class[f"{name}, removidas"] = values["removed_rows"]
        by_class[f"{name}, limpo"] = values["clean_rows"]
        by_tool[f"{name}, bruto"] = values["raw_rows_by_tool"]
        by_tool[f"{name}, limpo"] = values["clean_rows_by_tool"]
    by_class = pd.DataFrame(by_class, index=pd.Index(CLASS_NAMES, name="classe"))
    by_class.insert(0, "README do combinado", README_CLASS_ROWS)
    by_tool = pd.DataFrame(by_tool)
    by_tool.insert(0, "origem", pd.Series(TOOL_ORIGIN))
    by_tool.index.name = "ferramenta"
    return by_class, by_tool


def summary_text(metrics: dict, headers: dict, medians: pd.DataFrame, ranges: pd.DataFrame) -> str:
    """Monta o texto de RESUMO.md a partir dos números medidos nesta execução."""
    hkd, combined = metrics["hkd"], metrics["combinado"]
    unique = metrics["combinado_sem_replicas"]
    capture, replicas = hkd["capture"], combined["hkd_replicas"]
    by_class, by_tool = count_tables(metrics)
    header_table = pd.DataFrame(headers).T
    header_table.index.name = "arquivo"
    by_origin = pd.DataFrame(unique["clean_rows_by_origin"], index=CLASS_NAMES)
    by_origin.index.name = "classe"
    outside = ranges[ranges.columns[-2:]]
    outside = outside[outside.sum(axis=1) > 0]
    outside_text = frame_markdown_table(outside) if len(outside) else "Nenhum."
    shown = ["Duration", "FlowBytesSent", "FlowBytesReceived", "PacketLengthMean"]
    return f"""# E6, dados: segundo dataset

Gerado por `scripts/e6_dados.py`. Os números vêm dos arquivos `metrics.json` de
`hkd/seed42/`, `combinado/seed42/` e `combinado_sem_replicas/seed42/` e dos
arquivos CSV de `hkd/seed42/`.

## Fonte

- DoH-Tunnel-Traffic-HKD: `hkd/DoH-CSVs/DoH-CSVs-48h/Total-48h.csv`, com
  {sum(hkd["raw_rows"])} fluxos, todos de túnel DoH.
  `hkd/Total-48h-Augmentation.csv` é lido só para a conferência das réplicas.
- Combinado CIRA-CIC-DoHBrw-2020 + DoH-Tunnel-Traffic-HKD: Non-DoH das linhas
  `NonDoH` de `combinado/l1-total-add.csv`, Benign-DoH das linhas `Benign` de
  `combinado/l2-total-add.csv` e Malicious-DoH de todas as linhas de
  `combinado/l3-total-add.csv`, que traz a ferramenta de túnel.

## Compatibilidade de colunas

Cabeçalho de cada arquivo comparado, pelo nome, com as {len(CSV_COLUMNS)}
colunas do CIRA-CIC-DoHBrw-2020: {len(ID_COLUMNS)} identificadores,
{len(FEATURE_COLUMNS)} atributos e o rótulo. `missing` lista as colunas
esperadas que faltam e `unexpected`, as que sobram.

{frame_markdown_table(header_table)}

Diferenças de formato, sem efeito nos atributos:

- `bom` diz se o arquivo começa com a marca de ordem de bytes do UTF-8. A
  leitura a descarta nos arquivos que a têm.
- Em `Total-48h.csv`, os atributos {capture["integer_valued_features"]} só têm
  valores inteiros. A carga converte os 29 atributos para decimal.
- Os identificadores do fluxo não são copiados para as tabelas gravadas.

## Fluxos por classe, origem e ferramenta

"Bruto" é o que a carga lê, "removidas" o que a limpeza tira e "limpo" o que é
gravado. A limpeza é a mesma do CIRA: sai a linha com valor ausente em algum
dos 29 atributos. A coluna do README traz as contagens que o `README.txt` do
dataset combinado informa.

{frame_markdown_table(by_class)}

{frame_markdown_table(by_tool)}

- O combinado bruto tem as contagens do README, por classe e por ferramenta.
- Valores ausentes no combinado, por coluna: {combined["nan_by_column"]}. No
  HKD: {hkd["nan_by_column"]}. Valores infinitos: {combined["infinite_values"]}
  no combinado e {hkd["infinite_values"]} no HKD.
- Todas as linhas removidas são do CIRA. Depois da limpeza, a parte do CIRA
  dentro do combinado tem {combined["clean_rows_by_origin"]["CIRA"]} fluxos por
  classe; a Tabela I do artigo tem {TABLE_I_COUNTS}.

Combinado sem réplicas, limpo, por origem:

{frame_markdown_table(by_origin)}

## Réplicas do HKD

- `Total-48h-Augmentation.csv`: {hkd["augmented_file"]["rows"]} linhas,
  {hkd["augmented_file"]["distinct_flows"]} fluxos distintos, cada um
  exatamente {hkd["augmented_file"]["copies_per_flow"]} vezes.
- Linhas das ferramentas do HKD em `l3-total-add.csv`: {replicas["rows"]},
  {replicas["distinct_flows"]} fluxos distintos, cada um exatamente
  {replicas["copies_per_flow"]} vezes.
- Nos dois arquivos, os fluxos distintos são os de `Total-48h.csv`: mesma
  ferramenta e maior diferença absoluta em um atributo de
  {replicas["max_difference_to_total_48h"]:.1e}, que é arredondamento.
- `combinado_sem_replicas` fica com a primeira linha de cada fluxo do HKD:
  saem {unique["replicas_removed"]} linhas, todas da classe Malicious-DoH, que
  passa de {combined["raw_rows"][2]} para {unique["raw_rows"][2]} fluxos antes
  da limpeza. As linhas do CIRA ficam todas, inclusive as repetidas.

## HKD ao lado do tráfego malicioso do CIRA

Descrição dos conjuntos inteiros, sem separar treino e teste e sem normalizar;
nenhum modelo é ajustado aqui. Os fluxos do CIRA são os do combinado limpo.

- Máquinas do HKD: {capture["machines"]}. Em
  {capture["rows_between_two_distinct_machines"]} dos {sum(hkd["raw_rows"])}
  fluxos, origem e destino são máquinas diferentes dessa lista. Captura de
  {capture["first_day"]} a {capture["last_day"]}.
- Mediana de quatro atributos; os 29 estão em `hkd/seed42/medianas_malicioso.csv`:

{frame_markdown_table(medians.loc[shown])}

- Faixa de valores de cada atributo, em `hkd/seed42/faixa_por_atributo.csv`. A
  faixa do CIRA é a dos fluxos limpos das três classes. Atributos em que algum
  fluxo do HKD fica abaixo do mínimo ou acima do máximo do CIRA:

{outside_text}

## Justificativa da escolha do segundo dataset

**Quais dados.** O segundo dataset é o combinado CIRA-CIC-DoHBrw-2020 +
DoH-Tunnel-Traffic-HKD, publicado pelos autores do HKD, na forma sem réplicas:
{sum(unique["clean_rows"])} fluxos depois da limpeza, {unique["clean_rows"]} por
classe ({", ".join(CLASS_NAMES)}). Ao lado dele ficam o combinado como publicado
({sum(combined["clean_rows"])} fluxos) e o HKD sozinho
({sum(hkd["clean_rows"])} fluxos).

**Por que foram escolhidos.** Primeiro, os atributos são os mesmos do dataset do
artigo: os cinco arquivos lidos têm as {len(CSV_COLUMNS)} colunas do
CIRA-CIC-DoHBrw-2020, com os mesmos nomes e na mesma ordem, e o `README.txt` do
HKD informa que os atributos foram extraídos das capturas com o DoHLyzer. O
sistema é aplicado sem mudar a entrada. Segundo, o HKD traz tráfego de túnel de
três ferramentas que o CIRA não tem ({", ".join(HKD_TOOLS)}), capturado em
outras máquinas, de {capture["first_day"]} a {capture["last_day"]}; as máquinas e
o período do CIRA estão em `results/e0/dados/RESUMO.md`. Terceiro, o
combinado é o único dos dois com as três classes: o HKD sozinho só tem a classe
Malicious-DoH e não permite treinar o sistema; ele serve para avaliar, nas
ferramentas novas, o sistema treinado no CIRA.

**O que representam, e as ressalvas.** No combinado sem réplicas, o tráfego novo
são {sum(unique["clean_rows_by_origin"]["HKD"])} fluxos do HKD, todos na classe
Malicious-DoH. Os fluxos Non-DoH e Benign-DoH vêm do CIRA, porque o HKD só tem
tráfego de túnel: depois da limpeza, a parte do CIRA dentro do combinado tem as
contagens por classe da Tabela I do artigo. O segundo dataset difere do
primeiro, portanto, só na classe maliciosa. O combinado como publicado repete
cada fluxo do HKD {replicas["copies_per_flow"]} vezes; o `README.txt` do HKD
descreve o arquivo de origem como "augmented assuming 20 client PCs". Com as
réplicas, uma separação aleatória entre treino e teste põe cópias do mesmo fluxo
nos dois lados, e o teste mediria, nas ferramentas novas, fluxos que o modelo já
viu no treino. Por isso o sistema é treinado e avaliado na forma sem réplicas, e
a forma publicada fica ao lado, para comparação.

## Arquivos gerados

Em `data/processed/`, com os 29 atributos, `label`, `origin` e `tool`:

- `hkd.parquet`, SHA-256 `{hkd["parquet_sha256"]}`;
- `combinado.parquet`, SHA-256 `{combined["parquet_sha256"]}`;
- `combinado_sem_replicas.parquet`, SHA-256 `{unique["parquet_sha256"]}`.
"""


def check_combined(raw: pd.DataFrame, cleaned: pd.DataFrame) -> None:
    """Confere o combinado contra o README do dataset e a parte do CIRA contra a Tabela I."""
    assert class_counts(raw) == README_CLASS_ROWS, f"Classes {class_counts(raw)} fora do README."
    assert tool_counts(raw) == README_TOOL_ROWS, f"Ferramentas {tool_counts(raw)} fora do README."
    # A limpeza só pode tirar linha do CIRA, e o que sobra dele é a Tabela I:
    # qualquer outra contagem indica arquivo errado ou fluxo lido em dobro.
    clean_by_origin = origin_counts(cleaned)
    assert clean_by_origin["CIRA"] == TABLE_I_COUNTS, f"CIRA limpo: {clean_by_origin['CIRA']}."
    assert clean_by_origin["HKD"] == origin_counts(raw)["HKD"], "Linha do HKD removida na limpeza."


def load_checked_sources() -> tuple[dict, dict]:
    """Lê o HKD e o combinado e confere as réplicas.

    Devolve as três tabelas brutas, pelo nome, e os dois relatórios de réplicas:
    o do combinado e o do arquivo replicado do HKD.
    """
    hkd = load_hkd()
    assert set(hkd["origin"]) == {"HKD"}, "Ferramenta do CIRA no arquivo do HKD."
    combined = load_combined()
    unique = without_replicas(combined)
    reports = {
        "combined": replica_report(combined[combined["origin"] == "HKD"], hkd),
        "augmented": replica_report(load_hkd(HKD_AUGMENTED_CSV_PATH), hkd),
    }
    # Sem as réplicas, o que sobra do HKD são os fluxos de Total-48h.csv, e
    # nenhuma linha do CIRA sai.
    assert origin_counts(unique)["HKD"] == class_counts(hkd), "Sobrou réplica do HKD."
    assert origin_counts(unique)["CIRA"] == origin_counts(combined)["CIRA"]
    return {"hkd": hkd, "combinado": combined, "combinado_sem_replicas": unique}, reports


def save_slices(metrics: dict, headers: dict, sha256: dict, start: float) -> Path:
    """Registra as métricas de cada tabela e devolve a pasta que reúne as três."""
    # O registro guarda um único hash por execução: nas tabelas do combinado,
    # são os dos arquivos de nível 1, 2 e 3, nessa ordem, separados por espaço.
    combined_sha256 = " ".join(sha256[path] for path in COMBINED_CSV_PATHS)
    for name, folder, _ in SLICES:
        metrics[name]["source_files"] = {
            file: report for file, report in headers.items() if file.startswith(folder)
        }
        run_dir = save_run(
            experiment="e6",
            track="dados",
            slice_name=name,
            seed=SEED_FIEL,
            metrics=metrics[name],
            config={"cleaning": CLEANING, "hkd_replicas": HKD_REPLICAS},
            data_sha256=sha256[HKD_CSV_PATH] if name == "hkd" else combined_sha256,
            timings={"total_seconds": round(time.perf_counter() - start, 1)},
        )
        print(f"{name}: bruto {metrics[name]['raw_rows']}, limpo {metrics[name]['clean_rows']}")
        print(f"  removidas na limpeza: {metrics[name]['removed_rows']}")
        print(f"  por origem: {metrics[name]['clean_rows_by_origin']}")
        print(f"  por ferramenta: {metrics[name]['clean_rows_by_tool']}")
        print(f"  resultados em {run_dir.relative_to(PROJECT_ROOT)}")
    return run_dir.parents[1]


def main() -> None:
    """Confere os arquivos, grava os três Parquets e os resultados."""
    start = time.perf_counter()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_files = [HKD_CSV_PATH, HKD_AUGMENTED_CSV_PATH, *COMBINED_CSV_PATHS]
    sha256 = {path: checked_sha256(manifest, path) for path in source_files}
    headers = {path.relative_to(DATA_RAW_DIR).as_posix(): header_report(path) for path in sha256}
    print(pd.DataFrame(headers).T.to_string())

    raw, replicas = load_checked_sources()
    tables, metrics = {}, {}
    for name, _, parquet_path in SLICES:
        tables[name], removed = cleaned_table(raw[name])
        metrics[name] = table_metrics(raw[name], tables[name], removed, parquet_path)
    check_combined(raw["combinado"], tables["combinado"])
    # O README do HKD dá as contagens do arquivo replicado: as de Total-48h.csv
    # são essas divididas pelo número de cópias.
    hkd_tools = {tool: README_TOOL_ROWS[tool] // HKD_REPLICAS for tool in HKD_TOOLS}
    assert {tool: metrics["hkd"]["raw_rows_by_tool"][tool] for tool in HKD_TOOLS} == hkd_tools

    cira = tables["combinado"][tables["combinado"]["origin"] == "CIRA"]
    ranges = range_table(cira, tables["hkd"])
    medians = median_table(cira[cira["label"] == CLASS_NAMES.index("Malicious-DoH")], tables["hkd"])
    readme = {"readme_class_rows": README_CLASS_ROWS, "readme_tool_rows": README_TOOL_ROWS}
    metrics["hkd"] |= {
        "augmented_file": replicas["augmented"],
        "capture": hkd_capture(HKD_CSV_PATH),
        "flows_outside_cira_range": ranges[ranges.columns[-2:]].sum(axis=1).to_dict(),
    }
    metrics["combinado"] |= readme | {
        "hkd_replicas": replicas["combined"],
        "table_i": TABLE_I_COUNTS,
    }
    metrics["combinado_sem_replicas"] |= readme | {
        "replicas_removed": len(raw["combinado"]) - len(raw["combinado_sem_replicas"])
    }

    results_dir = save_slices(metrics, headers, sha256, start)
    hkd_dir = results_dir / "hkd" / f"seed{SEED_FIEL}"
    ranges.to_csv(hkd_dir / "faixa_por_atributo.csv")
    medians.to_csv(hkd_dir / "medianas_malicioso.csv")
    summary = summary_text(metrics, headers, medians, ranges)
    (results_dir / "RESUMO.md").write_text(summary, encoding="utf-8")
    print(f"Réplicas do HKD no combinado: {replicas['combined']}")
    print(f"Réplicas do HKD no arquivo replicado: {replicas['augmented']}")
    print(f"Captura do HKD: {metrics['hkd']['capture']}")
    print(f"Valores ausentes no combinado, por coluna: {metrics['combinado']['nan_by_column']}")
    print(f"Fluxos do HKD fora da faixa do CIRA: {metrics['hkd']['flows_outside_cira_range']}")
    print(medians.to_string())


if __name__ == "__main__":
    main()
