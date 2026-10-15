"""Modelos do artigo: os Random Forests base e o empilhamento (Seção IV)."""

import numpy as np
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from doh_ids.config import MAX_DEPTH, MAX_FEATURES, N_ESTIMATORS, N_JOBS


def base_forests(
    subsets: list[tuple[np.ndarray, np.ndarray]], seed: int
) -> list[RandomForestClassifier]:
    """Treina um Random Forest em cada subconjunto balanceado.

    Devolve os modelos já ajustados, na ordem dos subconjuntos.
    """
    forests = []
    for X, y in subsets:
        # Árvores, atributos por divisão e índice de Gini vêm da Seção IV-A do
        # artigo; a profundidade, da Seção IV-B. O artigo não menciona peso de
        # classe: o balanceamento é feito só pelos subconjuntos, e o modelo
        # fica sem class_weight.
        forest = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            max_features=MAX_FEATURES,
            criterion="gini",
            class_weight=None,
            random_state=seed,
            n_jobs=N_JOBS,
        )
        forest.fit(X, y)
        # Na predição em paralelo as probabilidades das árvores são somadas na
        # ordem em que as threads terminam, e a soma de ponto flutuante depende
        # da ordem. Com um núcleo a ordem é sempre a das árvores, e duas
        # execuções dão o mesmo resultado até a última casa.
        forest.set_params(n_jobs=1)
        forests.append(forest)
    return forests


def stacked_forest(
    forests: list[RandomForestClassifier], X_train: np.ndarray, y_train: np.ndarray, seed: int
) -> StackingClassifier:
    """Empilha os Random Forests já treinados sob uma regressão logística.

    `X_train` e `y_train` são o treino original normalizado, só com amostras
    reais: é sobre as predições dos bases nele que o meta-classificador é
    ajustado. Os bases não são treinados de novo.
    """
    # O artigo cita o StackingClassifier do mlxtend (Seção IV-B), que por padrão
    # ajusta todos os bases no mesmo conjunto. Como o artigo treina cada base
    # em um subconjunto diferente (Seção III-B), os bases entram já treinados.
    #
    # O artigo não diz com que dados o meta-classificador é treinado. Usamos o
    # treino original normalizado, como indica a linha 5 do Algoritmo 1, que
    # calcula os rótulos de cada amostra do conjunto de treino antes de empilhar.
    #
    # O artigo também não diz o que o meta-classificador recebe. Fica o padrão
    # da biblioteca: o rótulo predito por cada base, três entradas. A regressão
    # logística lê os códigos 0, 1 e 2 como número, e Benign-DoH fica entre
    # Non-DoH e Malicious-DoH. Os demais parâmetros da regressão logística
    # também não estão no artigo e ficam no padrão do scikit-learn.
    stacked = StackingClassifier(
        classifiers=forests,
        meta_classifier=LogisticRegression(random_state=seed),
        use_probas=False,
        use_clones=False,
        fit_base_estimators=False,
    )
    return stacked.fit(X_train, y_train)
