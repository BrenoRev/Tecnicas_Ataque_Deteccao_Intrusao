"""Explicabilidade com SHAP sobre os Random Forests base (Seção VI do artigo)."""

import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import CLASS_NAMES, FEATURE_COLUMNS


def stratified_sample(flows: pd.DataFrame, per_class: int, seed: int) -> pd.DataFrame:
    """Sorteia, sem reposição, até `per_class` fluxos de cada classe.

    A classe com menos fluxos que `per_class` entra inteira. Devolve as linhas
    na ordem das classes.
    """
    parts = [
        group.sample(n=min(per_class, len(group)), random_state=seed)
        for _, group in flows.groupby("label")
    ]
    return pd.concat(parts)


def forest_shap_values(
    forest: RandomForestClassifier, X: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Calcula os valores SHAP de um Random Forest para as linhas de `X`.

    Devolve o array de forma (amostras, atributos, classes) e o valor base de
    cada classe. Para cada linha e classe, o valor base mais a soma dos valores
    dos atributos é a probabilidade que o modelo dá à classe.
    """
    # Sem dados de referência, o TreeExplainer usa a contagem de amostras de
    # treino guardada em cada nó das árvores: o valor base é a probabilidade
    # média de cada classe no subconjunto em que o Random Forest foi treinado.
    explainer = shap.TreeExplainer(forest)
    values = explainer.shap_values(X)
    # A classe é o último eixo. Versões antigas da biblioteca devolviam uma
    # lista com um array por classe, e o código escrito para elas indexa o
    # eixo errado sem levantar erro.
    assert values.shape == (len(X), len(FEATURE_COLUMNS), len(CLASS_NAMES)), (
        f"Forma inesperada dos valores SHAP: {values.shape}."
    )
    return values, np.asarray(explainer.expected_value)


def global_importance(values: np.ndarray) -> pd.DataFrame:
    """Resume os valores SHAP na importância global de cada atributo, por classe.

    A importância é a média do valor absoluto sobre as amostras, a medida do
    eixo horizontal da Fig. 5 do artigo. Devolve uma linha por classe e
    atributo, com as colunas `class_name`, `feature`, `mean_abs_shap` e `rank`,
    ordenada pela classe e, dentro dela, do atributo mais importante (posto 1)
    para o menos importante.
    """
    mean_abs = np.abs(values).mean(axis=0)
    tables = []
    for class_index, class_name in enumerate(CLASS_NAMES):
        table = pd.DataFrame(
            {
                "class_name": class_name,
                "feature": FEATURE_COLUMNS,
                "mean_abs_shap": mean_abs[:, class_index],
            }
        )
        # Ordenação estável: no empate vale a ordem das colunas, e duas
        # execuções dão o mesmo ranking.
        table = table.sort_values("mean_abs_shap", ascending=False, kind="stable")
        table["rank"] = range(1, len(table) + 1)
        tables.append(table)
    return pd.concat(tables, ignore_index=True)


def original_units(scaler: MinMaxScaler, X: np.ndarray) -> pd.DataFrame:
    """Desfaz a normalização e devolve os atributos na unidade do dataset, com os nomes.

    O modelo recebe os atributos em [0, 1]. Para ler um limiar na unidade do
    artigo, como os segundos de `Duration`, o eixo é convertido de volta.
    """
    return pd.DataFrame(scaler.inverse_transform(X), columns=FEATURE_COLUMNS)


def rank_agreement(importance_a: pd.Series, importance_b: pd.Series, top: int) -> float:
    """Mede a concordância entre dois rankings de importância nos atributos do topo.

    Cada série tem o atributo no índice e a importância no valor. Devolve a
    correlação de postos de Spearman calculada sobre os atributos que estão
    entre os `top` primeiros de pelo menos um dos dois rankings: 1.0 quando a
    ordem deles é a mesma nos dois.
    """
    # Os dez primeiros de um ranking podem não ser os dez primeiros do outro.
    # A união dos dois topos entra na conta, para o atributo que cai do topo
    # em um dos modelos reduzir a concordância em vez de sumir dela.
    top_a = importance_a.sort_values(ascending=False, kind="stable").index[:top]
    top_b = importance_b.sort_values(ascending=False, kind="stable").index[:top]
    features = top_a.union(top_b)
    return float(spearmanr(importance_a[features], importance_b[features]).statistic)
