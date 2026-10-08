import numpy as np
import pandas as pd
import pytest

from doh_ids.config import (
    FEATURE_COLUMNS,
    ID_COLUMNS,
    LABEL_COLUMN,
    LABEL_ENCODING,
    NAN_COLUMNS,
)

# Fluxos por classe, na ordem dos códigos 0, 1 e 2: muito Non-DoH, pouco
# Benign-DoH e Malicious-DoH intermediário, como no CIRA-CIC-DoHBrw-2020.
CLASS_SIZES = [1800, 60, 480]
FIXTURE_SEED = 0
# Uma em cada vinte linhas do CSV bruto fica sem as duas colunas de tempo de resposta.
NAN_EVERY = 20


@pytest.fixture
def synthetic_flows():
    """Fluxos já limpos: as 29 colunas de atributo e `label` inteiro em {0, 1, 2}."""
    rng = np.random.default_rng(FIXTURE_SEED)
    label = np.repeat([0, 1, 2], CLASS_SIZES)
    # A média de cada atributo é deslocada pelo código da classe, para os modelos
    # terem o que aprender.
    values = rng.normal(loc=label[:, None], scale=1.0, size=(len(label), len(FEATURE_COLUMNS)))
    flows = pd.DataFrame(values, columns=FEATURE_COLUMNS)
    flows["label"] = label
    return flows


@pytest.fixture
def synthetic_raw_csv(synthetic_flows):
    """As 35 colunas do CSV real: identificadores, atributos e `Label` em texto.

    Devolve um DataFrame; o teste que precisa de arquivo grava em `tmp_path`.
    """
    rng = np.random.default_rng(FIXTURE_SEED)
    n = len(synthetic_flows)
    local_ip = np.array([f"192.168.20.{host}" for host in rng.integers(100, 200, size=n)])
    remote_ip = np.full(n, "1.1.1.1")
    local_port = rng.integers(1024, 65536, size=n)
    remote_port = np.full(n, 443)
    # Os fluxos são bidirecionais: a máquina local aparece ora na origem, ora no destino.
    local_is_source = np.arange(n) % 2 == 0
    first_flow = pd.Timestamp("2020-01-14 15:49:11")

    raw = pd.DataFrame(
        {
            "SourceIP": np.where(local_is_source, local_ip, remote_ip),
            "DestinationIP": np.where(local_is_source, remote_ip, local_ip),
            "SourcePort": np.where(local_is_source, local_port, remote_port),
            "DestinationPort": np.where(local_is_source, remote_port, local_port),
            "TimeStamp": (first_flow + pd.to_timedelta(np.arange(n), unit="s")).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
    )
    raw[FEATURE_COLUMNS] = synthetic_flows[FEATURE_COLUMNS]
    # Os valores ausentes aparecem só nessas duas colunas e sempre nas mesmas linhas.
    raw.loc[np.arange(n) % NAN_EVERY == 0, NAN_COLUMNS] = np.nan
    text_of_code = {code: text for text, code in LABEL_ENCODING.items()}
    raw[LABEL_COLUMN] = synthetic_flows["label"].map(text_of_code)
    assert list(raw.columns) == ID_COLUMNS + FEATURE_COLUMNS + [LABEL_COLUMN]
    return raw
