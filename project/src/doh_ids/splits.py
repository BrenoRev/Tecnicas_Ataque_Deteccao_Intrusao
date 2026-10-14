"""Separação de treino e teste e ajuste do normalizador."""

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import CLASS_NAMES, FEATURE_COLUMNS, N_SUBSETS, TEST_SIZE, smote_seed
from doh_ids.data import feature_matrix

NON_DOH = CLASS_NAMES.index("Non-DoH")
BENIGN = CLASS_NAMES.index("Benign-DoH")
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")


def stratified_split(flows: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa os fluxos em treino (90%) e teste (10%), mantendo a proporção das classes.

    Devolve `(train, test)` com o índice original de `flows`: nenhuma linha
    fica nos dois conjuntos e nenhuma fica de fora.
    """
    # O artigo separa 10% para teste (Seção III-B) e não diz que o sorteio é por
    # classe; as somas por classe das matrizes da Fig. 4 só fecham se for.
    train, test = train_test_split(
        flows, test_size=TEST_SIZE, stratify=flows["label"], random_state=seed
    )
    return train, test


def fit_scaler(train: pd.DataFrame) -> MinMaxScaler:
    """Ajusta o `MinMaxScaler` nos 29 atributos do treino e devolve o objeto ajustado.

    O teste é transformado com este mesmo objeto, por `scaler.transform`.
    """
    # O scaler é ajustado só no treino (Seção III-C do artigo); ajustado no
    # conjunto todo, vaza o mínimo e o máximo do teste. Por isso o teste
    # normalizado pode ter valor fora do intervalo de 0 a 1.
    return MinMaxScaler().fit(feature_matrix(train))


def seen_in_train(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Marca as linhas do teste cujo vetor de 29 atributos também existe no treino.

    Devolve um vetor booleano na ordem das linhas de `test`. Os atributos são
    comparados por igualdade exata, sem normalizar e sem olhar a classe.
    """
    # Índices disjuntos não impedem que dois fluxos com os mesmos 29 valores
    # caiam um em cada conjunto: para o modelo, essa linha do teste já foi vista.
    train_vectors = feature_matrix(train).drop_duplicates()
    merged = feature_matrix(test).merge(
        train_vectors, on=FEATURE_COLUMNS, how="left", indicator=True
    )
    return (merged["_merge"] == "both").to_numpy()


def balanced_subsets(
    X_train: np.ndarray, y_train: np.ndarray, seed: int
) -> tuple[list[tuple[np.ndarray, np.ndarray]], list[dict]]:
    """Monta os três subconjuntos balanceados de treino do artigo (Seção III-B).

    Recebe o treino já normalizado. Divide o Non-DoH em três partes disjuntas,
    repete todos os maliciosos e todos os benignos em cada uma e iguala os
    benignos aos maliciosos com SMOTE. O teste não entra aqui.

    Devolve a lista de três pares `(X, y)` e o resumo, com um dicionário por
    subconjunto: `class_counts` (posição é o código da classe), `ratio` (as
    contagens divididas pela da classe maliciosa) e `synthetic_benign_fraction`.
    Em cada par as linhas reais vêm primeiro, na ordem parte de Non-DoH,
    benignos, maliciosos; as sintéticas ficam no fim.
    """
    y_train = np.asarray(y_train)
    non_doh = np.flatnonzero(y_train == NON_DOH)
    benign = np.flatnonzero(y_train == BENIGN)
    malicious = np.flatnonzero(y_train == MALICIOUS)

    # O artigo divide o Non-DoH em três partes e não diz como sorteia. As linhas
    # são embaralhadas antes do corte, para a parte não depender da ordem da
    # tabela, e o sorteio usa a própria seed da execução, para a divisão mudar
    # junto com o split quando a seed muda.
    shuffled = np.random.default_rng(seed).permutation(non_doh)
    parts = np.array_split(shuffled, N_SUBSETS)

    subsets = []
    summary = []
    for index, part in enumerate(parts):
        rows = np.concatenate([part, benign, malicious])
        # O artigo não informa o alvo nem os parâmetros do SMOTE (Seção III-B).
        # Só a classe benigna é aumentada, até o tamanho da maliciosa, com os
        # vizinhos no padrão da biblioteca: Non-DoH e maliciosos ficam só com
        # amostras reais.
        smote = SMOTE(
            sampling_strategy={BENIGN: len(malicious)}, random_state=smote_seed(seed, index)
        )
        X, y = smote.fit_resample(X_train[rows], y_train[rows])
        subsets.append((X, y))

        counts = np.bincount(y, minlength=len(CLASS_NAMES)).tolist()
        summary.append(
            {
                "class_counts": counts,
                "ratio": [count / counts[MALICIOUS] for count in counts],
                "synthetic_benign_fraction": (counts[BENIGN] - len(benign)) / counts[BENIGN],
            }
        )
    return subsets, summary
