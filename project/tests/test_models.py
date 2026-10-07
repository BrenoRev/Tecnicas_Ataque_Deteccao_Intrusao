import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

import scripts.e3_sensibilidade as e3
from doh_ids.config import (
    MAX_DEPTH,
    MAX_FEATURES,
    N_ESTIMATORS,
    TABLE_II_FOREST_TREES,
    TABLE_II_TREE_DEPTH,
)
from doh_ids.data import class_counts, feature_matrix
from doh_ids.models import base_forests, fit_baseline, stacked_forest
from doh_ids.splits import balanced_subsets, balanced_train, fit_scaler, stratified_split
from doh_ids.system import fit_system

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


def system_configuration(stacked):
    """Os pontos da configuração do sistema empilhado que uma leitura alternativa pode trocar."""
    forest = stacked.clfs_[0]
    return {
        "n_base_models": len(stacked.clfs_),
        "n_estimators": len(forest.estimators_),
        "max_depth": forest.max_depth,
        "criterion": forest.criterion,
        "class_weight": forest.class_weight,
        "max_features": forest.max_features,
        "use_probas": stacked.use_probas,
    }


@pytest.mark.parametrize("name", e3.VARIANTS)
def test_variant_fits_and_predicts_class_codes_and_three_probabilities(synthetic_flows, name):
    train, test = stratified_split(synthetic_flows, SEED)

    scaler, model, _, _ = e3.fit_variant(train, SEED, MAX_DEPTH, name)
    X_test = scaler.transform(feature_matrix(test))

    assert set(model.predict(X_test)) <= {0, 1, 2}
    assert model.predict_proba(X_test).shape == (len(test), 3)


def test_use_probas_variant_gives_the_meta_classifier_nine_inputs(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    _, stacked, _, _ = e3.fit_variant(train, SEED, MAX_DEPTH, "use_probas")

    assert stacked.meta_clf_.n_features_in_ == 9


def test_single_forest_variant_is_fitted_without_synthetic_rows(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    _, _, single_sets, _ = e3.fit_variant(train, SEED, MAX_DEPTH, "rf_unico")
    _, _, stacked_sets, _ = fit_system(train, SEED, MAX_DEPTH)

    # O Random Forest único é ajustado em um conjunto só, com as linhas reais
    # do treino; os subconjuntos do sistema empilhado têm Benign-DoH sintético.
    benign = 1
    assert [entry["class_counts"] for entry in single_sets] == [class_counts(train)]
    assert all(
        entry["class_counts"][benign] > class_counts(train)[benign] for entry in stacked_sets
    )


@pytest.mark.parametrize(
    ("name", "point"),
    [
        ("class_weight", "class_weight"),
        ("use_probas", "use_probas"),
        ("max_features_padrao", "max_features"),
    ],
)
def test_stacked_variant_differs_from_the_fiel_configuration_in_one_point(
    synthetic_flows, name, point
):
    train, _ = stratified_split(synthetic_flows, SEED)

    fiel = system_configuration(fit_system(train, SEED, MAX_DEPTH)[1])
    variant = system_configuration(e3.fit_variant(train, SEED, MAX_DEPTH, name)[1])

    assert {key for key in fiel if fiel[key] != variant[key]} == {point}


def test_single_forest_variant_is_the_configuration_of_the_public_script(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    _, forest, _, _ = e3.fit_variant(train, SEED, MAX_DEPTH, "rf_unico")

    assert isinstance(forest, RandomForestClassifier)
    assert forest.class_weight == "balanced"
    assert forest.max_features == RandomForestClassifier().max_features
    assert len(forest.estimators_) == N_ESTIMATORS
    assert forest.max_depth == MAX_DEPTH


def test_meta_on_subsets_changes_the_meta_classifier_and_keeps_the_bases(synthetic_flows):
    train, test = stratified_split(synthetic_flows, SEED)

    scaler, fiel, _, _ = fit_system(train, SEED, MAX_DEPTH)
    _, variant, _, _ = e3.fit_variant(train, SEED, MAX_DEPTH, "meta_uniao")
    X_test = scaler.transform(feature_matrix(test))

    # Os bases são os mesmos; só os dados em que o meta é ajustado mudam. Se o
    # argumento fosse ignorado, a variante sairia igual à reprodução sem erro.
    assert system_configuration(fiel) == system_configuration(variant)
    assert np.array_equal(fiel.predict_meta_features(X_test), variant.predict_meta_features(X_test))
    assert not np.array_equal(fiel.meta_clf_.coef_, variant.meta_clf_.coef_)
