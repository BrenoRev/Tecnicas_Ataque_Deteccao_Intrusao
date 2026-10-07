"""Carga e limpeza do CIRA-CIC-DoHBrw-2020: rótulo de três classes e 29 atributos."""

import hashlib
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from doh_ids.config import (
    CIRA_LOCAL_PREFIX,
    CIRA_ZIP_MEMBERS,
    CIRA_ZIP_PATH,
    CLASS_NAMES,
    FEATURE_COLUMNS,
    ID_COLUMNS,
    LABEL_COLUMN,
    LABEL_ENCODING,
)


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
    columns = ID_COLUMNS + FEATURE_COLUMNS + [LABEL_COLUMN]
    with zipfile.ZipFile(zip_path) as archive:
        members = [
            pd.read_csv(archive.open(member), usecols=columns)[columns]
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
