"""Sistema do artigo ajustado de ponta a ponta: normalizador, subconjuntos, bases e meta."""

import time

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import CLASS_NAMES, CV_FOLDS, CV_SHUFFLE, FEATURE_COLUMNS
from doh_ids.data import feature_matrix
from doh_ids.models import base_forests, stacked_forest
from doh_ids.splits import balanced_subsets, fit_scaler

LABELS = list(range(len(CLASS_NAMES)))
NON_DOH = CLASS_NAMES.index("Non-DoH")
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")


def fit_system(
    train: pd.DataFrame, seed: int, max_depth: int | None
) -> tuple[MinMaxScaler, StackingClassifier, list[dict], dict]:
    """Ajusta o sistema inteiro só com `train`: normalizador, subconjuntos, bases e meta.

    `max_depth` é a profundidade máxima dos Random Forests base. Devolve o
    normalizador, o modelo empilhado, o resumo dos subconjuntos e os tempos de
    cada etapa, em segundos.
    """
    scaler = fit_scaler(train)
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    assert X_train.shape[1] == len(FEATURE_COLUMNS), "O modelo espera todos os atributos."

    # O artigo cita "one-sided selection with SMOTE" uma única vez (Seção III-B)
    # e não descreve a seleção: ela não é aplicada. O Non-DoH só é dividido em
    # três partes.
    start = time.perf_counter()
    subsets, summary = balanced_subsets(X_train, y_train, seed)
    subsets_seconds = time.perf_counter() - start

    # Cada linha de Non-DoH do treino está em exatamente um subconjunto, e cada
    # subconjunto tem todos os maliciosos do treino (Seção III-B): nenhuma linha
    # real foi perdida nem repetida na divisão.
    train_counts = np.bincount(y_train, minlength=len(CLASS_NAMES))
    assert sum(entry["class_counts"][NON_DOH] for entry in summary) == train_counts[NON_DOH], (
        "O Non-DoH dos subconjuntos não soma o Non-DoH do treino."
    )
    assert all(entry["class_counts"][MALICIOUS] == train_counts[MALICIOUS] for entry in summary), (
        "Subconjunto sem todos os maliciosos do treino."
    )

    start = time.perf_counter()
    forests = base_forests(subsets, seed, max_depth)
    base_seconds = time.perf_counter() - start

    start = time.perf_counter()
    stacked = stacked_forest(forests, X_train, y_train, seed)
    meta_seconds = time.perf_counter() - start

    timings = {
        "subsets_seconds": round(subsets_seconds, 1),
        "base_fit_seconds": round(base_seconds, 1),
        "meta_fit_seconds": round(meta_seconds, 1),
    }
    return scaler, stacked, summary, timings


def cross_validated_confusion(
    train: pd.DataFrame, seed: int, max_depth: int | None
) -> list[list[int]]:
    """Soma as matrizes de confusão dos folds de validação, para comparar com a Fig. 4a.

    Cada linha do treino é predita uma vez, pelo sistema ajustado nos outros
    nove folds. A matriz tem a classe real na linha e a predita na coluna.
    """
    # A legenda da Fig. 4a diz que a matriz do treino vem de validação cruzada
    # de 10 folds e não detalha o procedimento. A figura soma o treino original,
    # sem amostra sintética: por isso o normalizador, os subconjuntos, o SMOTE,
    # os bases e o meta são refeitos com os nove folds de treino, e o fold
    # deixado de fora só é transformado e predito.
    folds = StratifiedKFold(n_splits=CV_FOLDS, shuffle=CV_SHUFFLE, random_state=seed)
    total = np.zeros((len(LABELS), len(LABELS)), dtype=int)
    for fit_rows, held_out_rows in folds.split(train, train["label"]):
        scaler, stacked, _, _ = fit_system(train.iloc[fit_rows], seed, max_depth)
        held_out = train.iloc[held_out_rows]
        predicted = stacked.predict(scaler.transform(feature_matrix(held_out)))
        total += confusion_matrix(held_out["label"], predicted, labels=LABELS)
    return total.tolist()
