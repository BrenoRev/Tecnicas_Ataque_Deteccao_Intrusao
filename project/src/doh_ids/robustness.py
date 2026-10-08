"""Robustez à manipulação da duração: retirada de colunas e fragmentação de fluxos."""

import numpy as np
import pandas as pd

from doh_ids.config import CLASS_NAMES, FEATURE_COLUMNS, FRAGMENTED_COLUMNS

MALICIOUS = CLASS_NAMES.index("Malicious-DoH")


def kept_features(dropped: list[str]) -> list[str]:
    """Devolve os nomes dos atributos que ficam depois de retirar `dropped`, na ordem original.

    Levanta `ValueError` se `dropped` tiver um nome que não é atributo do modelo.
    """
    unknown = [name for name in dropped if name not in FEATURE_COLUMNS]
    if unknown:
        raise ValueError(f"Não é atributo do modelo: {unknown}.")
    return [name for name in FEATURE_COLUMNS if name not in dropped]


def drop_features(X: np.ndarray, dropped: list[str]) -> np.ndarray:
    """Retira da matriz de atributos as colunas `dropped` e mantém as demais na ordem.

    `X` tem os 29 atributos na ordem de `FEATURE_COLUMNS`, normalizados ou não.
    """
    X = np.asarray(X)
    assert X.shape[1] == len(FEATURE_COLUMNS), "A matriz precisa ter todos os atributos."
    kept = kept_features(dropped)
    # A matriz normalizada não tem nome de coluna: a posição de cada atributo é
    # a que ele tem em FEATURE_COLUMNS.
    return X[:, [FEATURE_COLUMNS.index(name) for name in kept]]


def fragment_malicious(flows: pd.DataFrame, factor: int) -> pd.DataFrame:
    """Troca cada fluxo Malicious-DoH por um fragmento dele, de duração `factor` vezes menor.

    Simula no espaço de atributos uma sessão de túnel cortada em `factor`
    fluxos iguais: a duração e os bytes enviados e recebidos são divididos por
    `factor`. As taxas de bytes por segundo, que são o quociente dos dois, e
    todos os outros atributos ficam como estão. Os fluxos das outras classes
    não mudam.

    `flows` tem os atributos e `label`, e é para ser o teste: o treino nunca
    passa por aqui. Devolve uma cópia; `flows` não é alterado.
    """
    fragmented = flows.copy()
    # Os bytes são inteiros na tabela e o fragmento pode ter valor fracionário.
    fragmented[FRAGMENTED_COLUMNS] = fragmented[FRAGMENTED_COLUMNS].astype(float)
    # Só a classe que o atacante controla é alterada.
    malicious = fragmented["label"] == MALICIOUS
    fragmented.loc[malicious, FRAGMENTED_COLUMNS] /= factor
    return fragmented
