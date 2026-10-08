import json

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

import scripts.e3_sensibilidade as e3
import scripts.e8_modificacao as e8
from doh_ids.config import (
    FEATURE_COLUMNS,
    MAX_DEPTH,
    MAX_FEATURES,
    MODIFIED_GRID,
    MODIFIED_MODELS,
    MODIFIED_SELECTED_MODEL,
    MODIFIED_SELECTION_FRACTION,
    N_ESTIMATORS,
    TABLE_II_FOREST_TREES,
    TABLE_II_TREE_DEPTH,
)
from doh_ids.data import class_counts, feature_matrix
from doh_ids.models import base_forests, fit_baseline, fit_modified_forest, stacked_forest
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


def test_selection_grid_has_at_most_eight_combinations_and_the_one_of_the_article():
    assert len(MODIFIED_GRID) <= 8
    assert {"n_estimators": 10, "max_depth": 5, "max_features": 28} in MODIFIED_GRID
    # Combinação repetida seria avaliada duas vezes sem mudar a escolha.
    assert len({tuple(combination.items()) for combination in MODIFIED_GRID}) == len(MODIFIED_GRID)


def test_modified_model_is_a_pipeline_with_the_scaler_first_and_a_class_weighted_forest(
    synthetic_flows,
):
    train, _ = stratified_split(synthetic_flows, SEED)

    model = fit_modified_forest(
        feature_matrix(train), train["label"].to_numpy(), SEED, **MODIFIED_MODELS["M1"]
    )

    assert isinstance(model, Pipeline)
    assert isinstance(model.steps[0][1], MinMaxScaler)
    forest = model.steps[-1][1]
    assert isinstance(forest, RandomForestClassifier)
    assert forest.class_weight == "balanced"


def test_modified_model_is_fitted_on_the_rows_of_the_original_train(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    model, _, _ = e8.fit_modification("M1", train, SEED)

    # O normalizador é ajustado junto com o Random Forest, nas mesmas linhas:
    # com SMOTE ou subconjuntos ele veria outro número de linhas.
    assert model.named_steps["scaler"].n_samples_seen_ == len(train)


def test_hyperparameter_selection_only_receives_train_rows_of_the_seed(
    synthetic_flows, tmp_path, monkeypatch
):
    seed = 1
    samples = []
    select = e8.select_hyperparameters

    def recording_select(sample, seed):
        samples.append(sample)
        return select(sample, seed)

    monkeypatch.setattr(e8, "select_hyperparameters", recording_select)
    e8.run_dataset("cira", synthetic_flows, {"cira": "0" * 64}, tmp_path, [seed])

    train, test = stratified_split(synthetic_flows, seed)
    assert len(samples) == 1
    assert samples[0].index.isin(train.index).all()
    assert samples[0].index.intersection(test.index).empty
    assert len(samples[0]) == int(MODIFIED_SELECTION_FRACTION * len(train))
    # A combinação escolhida fica gravada no resultado da seed.
    run_dir = tmp_path / "e8" / "corrigida" / f"{MODIFIED_SELECTED_MODEL}-cira" / f"seed{seed}"
    selected = json.loads((run_dir / "metrics.json").read_text())["selection"]["selected"]
    assert selected in MODIFIED_GRID


def test_selection_sample_is_the_same_for_a_seed_and_changes_with_the_seed(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    first = e8.selection_sample(train, SEED)

    # Sem a seed no sorteio, a seleção de hiperparâmetros não se repetiria.
    assert list(first.index) == list(e8.selection_sample(train, SEED).index)
    assert list(first.index) != list(e8.selection_sample(train, SEED + 1).index)


def test_selection_scaler_is_fitted_inside_each_fold_on_the_fit_rows_only(
    synthetic_flows, monkeypatch
):
    train, _ = stratified_split(synthetic_flows, SEED)
    sample = e8.selection_sample(train, SEED)
    # Um valor extremo em uma única linha: o máximo do normalizador só pode ser
    # esse valor nos ajustes em que a linha está nos folds de ajuste. Com a
    # subamostra normalizada antes dos folds, o máximo seria sempre 1.
    planted_row, planted_value = sample.index[0], 1e6
    sample.loc[planted_row, FEATURE_COLUMNS[0]] = planted_value
    seen = []

    def recording_fit(X, y, seed, **combination):
        model = fit_modified_forest(X, y, seed, **combination)
        assert isinstance(model.steps[0][1], MinMaxScaler)
        seen.append((planted_row in X.index, model.steps[0][1].data_max_[0]))
        return model

    monkeypatch.setattr(e8, "fit_modified_forest", recording_fit)
    # Uma combinação basta: todas passam pelo mesmo laço de folds.
    monkeypatch.setattr(e8, "MODIFIED_GRID", MODIFIED_GRID[:1])
    e8.select_hyperparameters(sample, SEED)

    assert [in_fit for in_fit, _ in seen].count(False) == 1
    for in_fit, scaler_maximum in seen:
        assert (scaler_maximum == planted_value) == in_fit
