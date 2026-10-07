import numpy as np
import pandas as pd
import pytest
from explainerdashboard import ExplainerDashboard
from sklearn.ensemble import RandomForestClassifier

import scripts.painel_xai as painel
from doh_ids.config import CLASS_NAMES, FEATURE_COLUMNS
from doh_ids.data import feature_matrix
from doh_ids.explain import (
    forest_shap_values,
    global_importance,
    original_units,
    rank_agreement,
    stratified_sample,
)
from doh_ids.splits import fit_scaler

SEED = 42
N_SAMPLES = 40


@pytest.fixture
def forest_and_rows(synthetic_flows):
    """Um Random Forest pequeno e as linhas a explicar, com as três classes."""
    X = feature_matrix(synthetic_flows).to_numpy()
    forest = RandomForestClassifier(n_estimators=3, max_depth=3, random_state=SEED)
    forest.fit(X, synthetic_flows["label"])
    rows = synthetic_flows.groupby("label").head(N_SAMPLES)
    return forest, feature_matrix(rows).to_numpy()


def test_shap_values_have_samples_features_classes_shape(forest_and_rows):
    forest, X = forest_and_rows

    values, base_values = forest_shap_values(forest, X)

    assert values.shape == (len(X), len(FEATURE_COLUMNS), len(CLASS_NAMES))
    # A classe é o último eixo: só nessa indexação o valor base mais a soma dos
    # atributos reproduz a probabilidade que o modelo dá a cada classe.
    for class_index in range(len(CLASS_NAMES)):
        explained = base_values[class_index] + values[:, :, class_index].sum(axis=1)
        assert explained == pytest.approx(forest.predict_proba(X)[:, class_index])


def test_global_importance_has_one_ordered_row_per_feature_and_class():
    rng = np.random.default_rng(SEED)
    values = rng.normal(size=(N_SAMPLES, len(FEATURE_COLUMNS), len(CLASS_NAMES)))
    # O último atributo domina a última classe, com valores dos dois sinais:
    # a média simples o deixaria perto de zero; a do valor absoluto, no topo.
    values[:, -1, -1] = 100.0 * np.where(np.arange(N_SAMPLES) % 2 == 0, 1.0, -1.0)

    importance = global_importance(values)

    assert len(importance) == len(FEATURE_COLUMNS) * len(CLASS_NAMES)
    for class_name, table in importance.groupby("class_name", sort=False):
        assert sorted(table["feature"]) == sorted(FEATURE_COLUMNS)
        assert table["rank"].tolist() == list(range(1, len(FEATURE_COLUMNS) + 1))
        assert table["mean_abs_shap"].is_monotonic_decreasing
        if class_name == CLASS_NAMES[-1]:
            assert table.iloc[0]["feature"] == FEATURE_COLUMNS[-1]
            assert table.iloc[0]["mean_abs_shap"] == pytest.approx(100.0)


def test_original_units_turns_normalized_duration_back_into_seconds(synthetic_flows):
    train = synthetic_flows.copy()
    # Duração de 0 a 120 segundos no treino: 40 segundos é um terço da faixa.
    train["Duration"] = np.linspace(0.0, 120.0, len(train))
    scaler = fit_scaler(train)
    X = np.zeros((3, len(FEATURE_COLUMNS)))
    X[:, FEATURE_COLUMNS.index("Duration")] = [0.0, 1 / 3, 1.0]

    restored = original_units(scaler, X)

    assert list(restored.columns) == FEATURE_COLUMNS
    assert restored["Duration"].tolist() == pytest.approx([0.0, 40.0, 120.0])


def test_rank_agreement_is_one_for_equal_rankings_and_lower_when_swapped():
    importance = pd.Series(np.arange(len(FEATURE_COLUMNS), 0, -1.0), index=FEATURE_COLUMNS)
    swapped = importance.copy()
    first, second = FEATURE_COLUMNS[0], FEATURE_COLUMNS[1]
    swapped[first], swapped[second] = importance[second], importance[first]

    # A escala não importa, só a ordem.
    assert rank_agreement(importance, 2 * importance, top=10) == pytest.approx(1.0)
    assert rank_agreement(importance, swapped, top=10) < 1.0


def test_stratified_sample_takes_the_requested_rows_of_each_class_and_follows_the_seed(
    synthetic_flows,
):
    # A menor classe da tabela sintética tem 60 fluxos: menos que os 100 pedidos.
    per_class = 100

    sample = stratified_sample(synthetic_flows, per_class, SEED)

    # A classe com menos fluxos que o pedido entra inteira; as outras, com o pedido.
    assert sample["label"].value_counts().sort_index().tolist() == [per_class, 60, per_class]
    assert sample.index.is_unique
    assert sample.equals(synthetic_flows.loc[sample.index])
    # A mesma seed sorteia as mesmas linhas; outra seed, linhas diferentes.
    assert stratified_sample(synthetic_flows, per_class, SEED).index.equals(sample.index)
    assert not stratified_sample(synthetic_flows, per_class, SEED + 1).index.equals(sample.index)


def test_dashboard_is_built_in_memory_without_writing_any_file(
    synthetic_flows, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    dashboard = painel.build_dashboard(synthetic_flows)

    assert isinstance(dashboard, ExplainerDashboard)
    assert isinstance(dashboard.explainer.model, RandomForestClassifier)
    # O painel não pode deixar modelo nem explicador serializado no disco.
    assert list(tmp_path.iterdir()) == []
