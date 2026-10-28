"""Carga e limpeza dos datasets: rótulo de três classes e 29 atributos.

Cobre o CIRA-CIC-DoHBrw-2020, o DoH-Tunnel-Traffic-HKD e o combinado dos dois.
"""

import hashlib
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from doh_ids.config import (
    CIRA_LOCAL_PREFIX,
    CIRA_TOOLS,
    CIRA_ZIP_MEMBERS,
    CIRA_ZIP_PATH,
    CLASS_NAMES,
    COMBINED_BENIGN_LABEL,
    COMBINED_CSV_PATHS,
    COMBINED_NON_DOH_LABEL,
    DOH_COLUMN,
    FEATURE_COLUMNS,
    HKD_CSV_PATH,
    ID_COLUMNS,
    LABEL_COLUMN,
    LABEL_ENCODING,
    MALICIOUS_ZIP_MEMBER,
    MALICIOUS_ZIP_PATH,
    SECOND_DATASET_COLUMNS,
    SECOND_DATASET_ENCODING,
    TOOL_ORIGIN,
)

# As 35 colunas dos CSVs publicados, na ordem do cabeçalho.
CSV_COLUMNS = ID_COLUMNS + FEATURE_COLUMNS + [LABEL_COLUMN]


def sha256_of(path: Path) -> str:
    """Devolve o SHA-256 do arquivo, em hexadecimal."""
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def local_machine(flows: pd.DataFrame) -> pd.Series:
    """Devolve, para cada fluxo, o endereço da máquina local que o gerou.

    Os fluxos são bidirecionais e `SourceIP` às vezes é o resolvedor: a máquina
    local é o endereço da rede de captura que aparece na origem ou, se a origem
    for externa, no destino.
    """
    source_is_local = flows["SourceIP"].str.startswith(CIRA_LOCAL_PREFIX)
    return flows["SourceIP"].where(source_is_local, flows["DestinationIP"])


def load_cira(zip_path: Path = CIRA_ZIP_PATH) -> pd.DataFrame:
    """Lê os fluxos das três classes direto do zip publicado, sem limpar nada.

    Devolve os cinco identificadores, os 29 atributos, `label` com o código
    inteiro da classe e `group` com a máquina local. Cada linha dos três
    membros de `CIRA_ZIP_MEMBERS` entra uma única vez; linhas repetidas não são
    removidas.

    Levanta `ValueError` se houver rótulo desconhecido ou fluxo sem máquina local.
    """
    # As colunas são pedidas pelo nome: uma coluna a mais no arquivo não entra,
    # e uma coluna a menos interrompe a leitura.
    with zipfile.ZipFile(zip_path) as archive:
        members = [
            pd.read_csv(archive.open(member), usecols=CSV_COLUMNS)[CSV_COLUMNS]
            for member in CIRA_ZIP_MEMBERS
        ]
    flows = pd.concat(members, ignore_index=True)

    label = flows.pop(LABEL_COLUMN).map(LABEL_ENCODING)
    if label.isna().any():
        raise ValueError(f"Rótulo fora de {list(LABEL_ENCODING)} em {zip_path.name}.")
    flows["label"] = label.astype(int)

    flows["group"] = local_machine(flows)
    if not flows["group"].str.startswith(CIRA_LOCAL_PREFIX).all():
        raise ValueError(f"Fluxo sem endereço da rede {CIRA_LOCAL_PREFIX}x em {zip_path.name}.")
    return flows


def load_malicious_by_tool(zip_path: Path = MALICIOUS_ZIP_PATH) -> pd.DataFrame:
    """Lê os fluxos maliciosos de cada ferramenta de túnel direto do zip publicado.

    Devolve os 29 atributos e `tool`, a ferramenta que gerou o fluxo, que é o
    nome da pasta do arquivo dentro do zip. Só entram as linhas com a coluna
    `DoH` verdadeira; nada mais é limpo e linhas repetidas não são removidas.

    Levanta `ValueError` se a coluna `DoH` de algum arquivo não for booleana.
    """
    columns = FEATURE_COLUMNS + [DOH_COLUMN]
    tools = []
    with zipfile.ZipFile(zip_path) as archive:
        for tool in CIRA_TOOLS:
            member = MALICIOUS_ZIP_MEMBER.format(tool=tool)
            # Os identificadores do fluxo não são pedidos ao leitor: não chegam
            # a entrar na tabela.
            raw = pd.read_csv(archive.open(member), usecols=columns)
            if raw[DOH_COLUMN].dtype != bool:
                raise ValueError(f"Coluna {DOH_COLUMN} não booleana em {member}.")
            flows = raw.loc[raw[DOH_COLUMN], FEATURE_COLUMNS]
            tools.append(flows.assign(tool=tool))
    return pd.concat(tools, ignore_index=True)


def column_differences(header: list[str]) -> dict[str, list[str]]:
    """Compara o cabeçalho de um CSV com as 35 colunas esperadas, pelo nome.

    Devolve `missing`, as colunas esperadas que o cabeçalho não tem, e
    `unexpected`, as do cabeçalho que não são esperadas. Uma coluna com o nome
    escrito de outro jeito aparece nas duas listas.
    """
    return {
        "missing": [column for column in CSV_COLUMNS if column not in header],
        "unexpected": [column for column in header if column not in CSV_COLUMNS],
    }


def read_header(path: Path) -> list[str]:
    """Lê só o cabeçalho de um CSV do HKD ou do combinado e devolve os nomes das colunas."""
    return list(pd.read_csv(path, encoding=SECOND_DATASET_ENCODING, nrows=0).columns)


def read_flow_csv(path: Path) -> pd.DataFrame:
    """Lê um CSV do HKD ou do combinado e devolve as 35 colunas, na ordem esperada.

    As colunas são pedidas pelo nome: a leitura é interrompida se faltar alguma.
    """
    return pd.read_csv(path, encoding=SECOND_DATASET_ENCODING, usecols=CSV_COLUMNS)[CSV_COLUMNS]


def _labelled_flows(raw: pd.DataFrame, class_name: str, with_tool: bool) -> pd.DataFrame:
    """Monta a tabela do segundo dataset a partir das linhas de uma classe.

    Com `with_tool`, a coluna de rótulo do CSV traz a ferramenta de túnel, e a
    origem é o conjunto de onde a ferramenta vem. Sem ele, o fluxo não tem
    ferramenta e vem do CIRA, o único dos dois conjuntos com tráfego que não é
    de túnel.
    """
    # No HKD três atributos só têm valores inteiros e seriam lidos como
    # inteiros: todos passam a decimal, para as tabelas terem o mesmo tipo.
    flows = raw[FEATURE_COLUMNS].astype(float)
    flows["label"] = CLASS_NAMES.index(class_name)
    if with_tool:
        flows["tool"] = raw[LABEL_COLUMN]
        flows["origin"] = flows["tool"].map(TOOL_ORIGIN)
        if flows["origin"].isna().any():
            raise ValueError(f"Ferramenta fora de {list(TOOL_ORIGIN)} na coluna {LABEL_COLUMN}.")
    else:
        flows["tool"] = None
        flows["origin"] = "CIRA"
    # Os identificadores não são copiados. A máquina local também não é
    # derivada: no HKD todo fluxo tem as mesmas duas máquinas, uma em cada
    # ponta, e a regra que vale no CIRA não separa nada.
    return flows[SECOND_DATASET_COLUMNS]


def load_hkd(path: Path = HKD_CSV_PATH) -> pd.DataFrame:
    """Lê os fluxos do DoH-Tunnel-Traffic-HKD, sem limpar nada.

    Devolve os 29 atributos, `label`, `origin` e `tool`. O dataset só tem
    tráfego de túnel: todo fluxo recebe o código de Malicious-DoH, e a
    ferramenta vem da coluna de rótulo do arquivo.

    Levanta `ValueError` se houver ferramenta desconhecida.
    """
    return _labelled_flows(read_flow_csv(path), "Malicious-DoH", with_tool=True)


def load_combined(paths: list[Path] = COMBINED_CSV_PATHS) -> pd.DataFrame:
    """Lê as três classes do dataset combinado CIRA + HKD, sem limpar nada.

    `paths` são os arquivos de nível 1, 2 e 3, nessa ordem. Non-DoH vem das
    linhas `NonDoH` do nível 1, Benign-DoH das linhas `Benign` do nível 2 e
    Malicious-DoH de todas as linhas do nível 3, que traz a ferramenta. Devolve
    os 29 atributos, `label`, `origin` e `tool`; linhas repetidas não são
    removidas.

    Levanta `ValueError` se houver ferramenta desconhecida no nível 3.
    """
    level1, level2, level3 = (read_flow_csv(path) for path in paths)
    # As linhas DoH do nível 1 e Malicious do nível 2 repetem os fluxos do
    # nível 3 com rótulo menos detalhado: lidas também, contariam em dobro.
    non_doh = level1[level1[LABEL_COLUMN] == COMBINED_NON_DOH_LABEL]
    benign = level2[level2[LABEL_COLUMN] == COMBINED_BENIGN_LABEL]
    classes = [
        _labelled_flows(non_doh, "Non-DoH", with_tool=False),
        _labelled_flows(benign, "Benign-DoH", with_tool=False),
        _labelled_flows(level3, "Malicious-DoH", with_tool=True),
    ]
    return pd.concat(classes, ignore_index=True)


def without_replicas(flows: pd.DataFrame) -> pd.DataFrame:
    """Devolve a tabela do segundo dataset com cada fluxo do HKD uma única vez.

    Réplica é a linha do HKD com os mesmos 29 atributos e a mesma ferramenta de
    uma linha anterior; de cada grupo fica a primeira. As linhas do CIRA ficam
    todas, inclusive as repetidas, e o índice original é mantido.
    """
    replica = (flows["origin"] == "HKD") & flows.duplicated(subset=FEATURE_COLUMNS + ["tool"])
    return flows[~replica]


def feature_matrix(flows: pd.DataFrame) -> pd.DataFrame:
    """Devolve só os 29 atributos do modelo, selecionados pelo nome e na ordem fixa."""
    # Selecionar "tudo menos o rótulo" deixaria passar identificador ou coluna
    # auxiliar que alguém acrescente à tabela.
    return flows[FEATURE_COLUMNS]


def class_counts(flows: pd.DataFrame) -> list[int]:
    """Conta os fluxos de cada classe; a posição na lista é o código da classe."""
    return np.bincount(flows["label"], minlength=len(CLASS_NAMES)).tolist()


def clean_flows(
    flows: pd.DataFrame,
    drop_nan: bool,
    drop_inf: bool,
    duplicate_columns: list[str] | None,
) -> tuple[pd.DataFrame, list[int]]:
    """Aplica a regra de limpeza pedida e conta o que saiu de cada classe.

    `drop_nan` e `drop_inf` removem as linhas com valor ausente ou infinito em
    algum dos 29 atributos. `duplicate_columns` lista as colunas que definem
    uma linha repetida; de cada grupo de repetidas fica a primeira. `None` não
    remove repetidas.

    Devolve os fluxos que ficaram, com o índice original, e a lista de linhas
    removidas por classe.
    """
    features = feature_matrix(flows)
    keep = pd.Series(True, index=flows.index)
    if drop_nan:
        keep &= ~features.isna().any(axis=1)
    if drop_inf:
        keep &= ~np.isinf(features).any(axis=1)
    cleaned = flows[keep]
    if duplicate_columns is not None:
        cleaned = cleaned.drop_duplicates(subset=duplicate_columns)
    removed = np.subtract(class_counts(flows), class_counts(cleaned)).tolist()
    return cleaned, removed
