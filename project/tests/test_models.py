import numpy as np
import pytest

from doh_ids.config import (
    MAX_DEPTH,
    MAX_FEATURES,
    N_ESTIMATORS,
    TABLE_II_FOREST_TREES,
    TABLE_II_TREE_DEPTH,
)
from doh_ids.data import feature_matrix
from doh_ids.models import base_forests, fit_baseline, stacked_forest
from doh_ids.splits import balanced_subsets, balanced_train, fit_scaler, stratified_split

SEED = 42


def fitted_model(flows, seed):
    """Modelo empilhado ajustado no treino sintético e o teste normalizado."""
    train, test = stratified_split(flows, SEED)
    scaler = fit_scaler(train)
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    subsets, _ = balanced_subsets(X_train, y_train, seed)
    stacked = stacked_forest(base_forests(subsets, seed, MAX_DEPTH), X_train, y_train, seed)
    return stacked, scaler.transform(feature_matrix(test))


def test_stacked_model_has_three_bases_and_meta_with_three_inputs(synthetic_flows):
    stacked, _ = fitted_model(synthetic_flows, SEED)

    assert len(stacked.clfs_) == 3
    assert stacked.meta_clf_.n_features_in_ == 3


def test_base_forests_use_the_hyperparameters_of_config(synthetic_flows):
    stacked, _ = fitted_model(synthetic_flows, SEED)

    for forest in stacked.clfs_:
        assert len(forest.estimators_) == N_ESTIMATORS == 10
        assert forest.max_depth == MAX_DEPTH == 5
        assert forest.max_features == MAX_FEATURES == 28
        assert forest.criterion == "gini"
        assert forest.class_weight is None


def test_predictions_are_class_codes_and_repeat_with_the_same_seed(synthetic_flows):
    stacked, X_test = fitted_model(synthetic_flows, SEED)
    stacked_again, _ = fitted_model(synthetic_flows, SEED)

    predicted = stacked.predict(X_test)

    assert set(predicted) <= {0, 1, 2}
    assert np.array_equal(predicted, stacked_again.predict(X_test))
    assert np.array_equal(stacked.predict_proba(X_test), stacked_again.predict_proba(X_test))


def balanced_train_and_test(flows):
    """Treino normalizado antes e depois do SMOTE do treino inteiro, e o teste normalizado."""
    train, test = stratified_split(flows, SEED)
    scaler = fit_scaler(train)
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    X_balanced, y_balanced = balanced_train(X_train, y_train, SEED)
    return X_train, y_train, X_balanced, y_balanced, scaler.transform(feature_matrix(test))


@pytest.mark.parametrize("name", ["decision_tree", "xgboost", "random_forest"])
def test_baseline_predicts_class_codes_and_three_probabilities(synthetic_flows, name):
    _, _, X_balanced, y_balanced, X_test = balanced_train_and_test(synthetic_flows)

    model = fit_baseline(name, X_balanced, y_balanced, SEED)

    assert set(model.predict(X_test)) <= {0, 1, 2}
    assert model.predict_proba(X_test).shape == (len(X_test), 3)


def test_whole_train_smote_only_adds_synthetic_rows_to_the_train(synthetic_flows):
    X_train, y_train, X_balanced, y_balanced, X_test = balanced_train_and_test(synthetic_flows)
    real_rows = len(X_train)

    # As linhas reais continuam todas, na mesma ordem, e as duas classes
    # menores sobem até o tamanho da maior.
    assert np.array_equal(X_balanced[:real_rows], X_train)
    assert np.array_equal(y_balanced[:real_rows], y_train)
    assert np.bincount(y_balanced).tolist() == [np.bincount(y_train).max()] * 3

    # Nenhuma amostra sintética é linha do teste, e o teste é predito inteiro.
    synthetic = {tuple(row) for row in X_balanced[real_rows:]}
    assert synthetic.isdisjoint({tuple(row) for row in X_test})
    model = fit_baseline("decision_tree", X_balanced, y_balanced, SEED)
    assert len(model.predict(X_test)) == len(synthetic_flows) // 10


def test_baselines_use_the_hyperparameters_of_table_ii(synthetic_flows):
    _, _, X_balanced, y_balanced, _ = balanced_train_and_test(synthetic_flows)

    tree = fit_baseline("decision_tree", X_balanced, y_balanced, SEED)
    forest = fit_baseline("random_forest", X_balanced, y_balanced, SEED)

    assert tree.max_depth == TABLE_II_TREE_DEPTH == 10
    assert len(forest.estimators_) == TABLE_II_FOREST_TREES == 10
