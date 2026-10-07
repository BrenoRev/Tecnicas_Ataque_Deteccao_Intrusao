"""Modelos do artigo: os Random Forests base, o empilhamento (Seção IV) e os de comparação."""

import numpy as np
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from doh_ids.config import (
    MAX_FEATURES,
    N_ESTIMATORS,
    N_JOBS,
    TABLE_II_FOREST_TREES,
    TABLE_II_TREE_DEPTH,
)


def base_forests(
    subsets: list[tuple[np.ndarray, np.ndarray]],
    seed: int,
    max_depth: int | None,
    class_weight: str | None = None,
    max_features: int | str = MAX_FEATURES,
) -> list[RandomForestClassifier]:
    """Treina um Random Forest em cada subconjunto balanceado.

    `max_depth` é a profundidade máxima das árvores; `None` deixa a árvore
    crescer sem limite. `class_weight` e `max_features` são repassados ao
    Random Forest; os valores padrão são os da reprodução do artigo. Devolve os
    modelos já ajustados, na ordem dos subconjuntos.
    """
    forests = []
    for X, y in subsets:
        # Árvores, atributos por divisão e índice de Gini vêm da Seção IV-A do
        # artigo. A profundidade vem de quem chama, porque o artigo admite duas
        # leituras: 5 (Seção IV-B) ou sem limite (linha 3 do Algoritmo 1). O
        # artigo não menciona peso de classe: o balanceamento é feito só pelos
        # subconjuntos, e por padrão o modelo fica sem class_weight. Peso de
        # classe e atributos por divisão só mudam no estudo de sensibilidade.
        forest = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=max_depth,
            max_features=max_features,
            criterion="gini",
            class_weight=class_weight,
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
    forests: list[RandomForestClassifier],
    X_train: np.ndarray,
    y_train: np.ndarray,
    seed: int,
    use_probas: bool = False,
) -> StackingClassifier:
    """Empilha os Random Forests já treinados sob uma regressão logística.

    `X_train` e `y_train` são os dados do meta-classificador: ele é ajustado
    sobre as predições dos bases neles. Na reprodução do artigo são o treino
    original normalizado, só com amostras reais. Com `use_probas` o
    meta-classificador recebe as probabilidades por classe de cada base, nove
    entradas, em vez dos três rótulos. Os bases não são treinados de novo.
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
    # Non-DoH e Malicious-DoH. Essa codificação é uma propriedade da entrada, e
    # não a explicação do resultado: a classe que o meta devolve para cada
    # combinação de rótulos é medida e gravada pelo script do experimento. Os
    # demais parâmetros da regressão logística também não estão no artigo e
    # ficam no padrão do scikit-learn. A outra leitura da entrada, com as
    # probabilidades, só entra no estudo de sensibilidade.
    stacked = StackingClassifier(
        classifiers=forests,
        meta_classifier=LogisticRegression(random_state=seed),
        use_probas=use_probas,
        use_clones=False,
        fit_base_estimators=False,
    )
    return stacked.fit(X_train, y_train)


def fit_baseline(
    name: str, X: np.ndarray, y: np.ndarray, seed: int
) -> DecisionTreeClassifier | XGBClassifier | RandomForestClassifier:
    """Treina um dos três modelos de comparação da Tabela II do artigo.

    `name` é a chave do modelo em `config.TABLE_II`: `decision_tree`, `xgboost`
    ou `random_forest`. `X` e `y` são o treino normalizado e já balanceado com
    SMOTE. Devolve o modelo ajustado.
    """
    # A Tabela II só informa a profundidade máxima da árvore de decisão e o
    # número de árvores do Random Forest. Todos os outros hiperparâmetros ficam
    # no padrão do scikit-learn e do XGBoost, porque o artigo não os informa.
    models = {
        "decision_tree": DecisionTreeClassifier(max_depth=TABLE_II_TREE_DEPTH, random_state=seed),
        "xgboost": XGBClassifier(random_state=seed, n_jobs=N_JOBS),
        "random_forest": RandomForestClassifier(
            n_estimators=TABLE_II_FOREST_TREES, random_state=seed, n_jobs=N_JOBS
        ),
    }
    model = models[name].fit(X, y)
    if name == "random_forest":
        # Mesmo cuidado dos Random Forests base: com um núcleo na predição, a
        # soma das probabilidades das árvores tem sempre a mesma ordem.
        model.set_params(n_jobs=1)
    return model
