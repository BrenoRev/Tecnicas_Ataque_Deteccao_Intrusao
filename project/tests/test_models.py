import numpy as np

from doh_ids.config import MAX_DEPTH, MAX_FEATURES, N_ESTIMATORS
from doh_ids.data import feature_matrix
from doh_ids.models import base_forests, stacked_forest
from doh_ids.splits import balanced_subsets, fit_scaler, stratified_split

SEED = 42


def fitted_model(flows, seed):
    """Modelo empilhado ajustado no treino sintético e o teste normalizado."""
    train, test = stratified_split(flows, SEED)
    scaler = fit_scaler(train)
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    subsets, _ = balanced_subsets(X_train, y_train, seed)
    stacked = stacked_forest(base_forests(subsets, seed), X_train, y_train, seed)
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
