import numpy as np
import pandas as pd

import scripts.e4_corrigido as e4
import scripts.e8_robustez as rob
from doh_ids.config import FEATURE_COLUMNS, FRAGMENTED_COLUMNS, ROBUSTNESS_COLUMN_SETS
from doh_ids.data import feature_matrix
from doh_ids.robustness import MALICIOUS, drop_features, fragment_malicious, kept_features
from doh_ids.splits import stratified_split

SEED = 42
FACTOR = 4
RATE_COLUMNS = ["FlowSentRate", "FlowReceivedRate"]


def test_drop_features_removes_only_the_requested_columns_and_keeps_the_order(synthetic_flows):
    X = feature_matrix(synthetic_flows).to_numpy()
    dropped = ROBUSTNESS_COLUMN_SETS["sem_duration_taxas"]

    reduced = drop_features(X, dropped)

    kept = kept_features(dropped)
    assert dropped == ["Duration", "FlowSentRate", "FlowReceivedRate"]
    assert kept == [name for name in FEATURE_COLUMNS if name not in dropped]
    assert reduced.shape == (len(X), len(FEATURE_COLUMNS) - 3)
    assert np.array_equal(reduced, synthetic_flows[kept].to_numpy())
    assert np.array_equal(drop_features(X, []), X)


def test_fragmentation_divides_duration_and_bytes_and_keeps_the_rates(synthetic_flows):
    fragmented = fragment_malicious(synthetic_flows, FACTOR)

    malicious = synthetic_flows["label"] == MALICIOUS
    before, after = synthetic_flows[malicious], fragmented[malicious]
    assert np.allclose(after[FRAGMENTED_COLUMNS], before[FRAGMENTED_COLUMNS] / FACTOR)
    assert FRAGMENTED_COLUMNS == ["Duration", "FlowBytesSent", "FlowBytesReceived"]
    unchanged = [name for name in FEATURE_COLUMNS if name not in FRAGMENTED_COLUMNS]
    assert set(RATE_COLUMNS) <= set(unchanged)
    pd.testing.assert_frame_equal(after[unchanged], before[unchanged])


def test_fragmentation_changes_only_malicious_flows_of_the_test(synthetic_flows):
    train, test = stratified_split(synthetic_flows, SEED)
    train_before, test_before = train.copy(), test.copy()

    fragmented = fragment_malicious(test, FACTOR)

    other = test["label"] != MALICIOUS
    assert other.any()
    assert not other.all()
    pd.testing.assert_frame_equal(
        fragmented.loc[other, FEATURE_COLUMNS], test.loc[other, FEATURE_COLUMNS]
    )
    assert fragmented["label"].equals(test["label"])
    assert fragmented.index.equals(test.index)
    # A função devolve uma cópia: o teste original e o treino ficam intactos.
    pd.testing.assert_frame_equal(test, test_before)
    pd.testing.assert_frame_equal(train, train_before)


def test_robustness_seed_fits_the_scaler_on_train_and_perturbs_only_test_malicious(
    synthetic_flows, monkeypatch, tmp_path
):
    train, test = stratified_split(synthetic_flows, SEED)
    split = {"train": e4.index_sha256(train), "test": e4.index_sha256(test)}
    # As execuções de referência só existem com os dados reais: no lugar delas
    # entra o split desta seed, que é o que a função da seed confere.
    monkeypatch.setattr(rob, "reference_metrics", lambda name, seed: {"split_index_sha256": split})
    seen = {}
    fit_model, model_metrics = rob.fit_model, rob.model_metrics

    def fit_model_seen(name, train, scaler, seed, dropped):
        seen["train"], seen["scaler"] = train.copy(), scaler
        return fit_model(name, train, scaler, seed, dropped)

    def model_metrics_seen(model, dropped, y_test, X_by_factor, perturbation):
        seen["X_by_factor"] = X_by_factor
        return model_metrics(model, dropped, y_test, X_by_factor, perturbation)

    monkeypatch.setattr(rob, "fit_model", fit_model_seen)
    monkeypatch.setattr(rob, "model_metrics", model_metrics_seen)

    rob.run_seed(synthetic_flows, SEED, [("A-prof5", "sem_duration")], "0" * 64, tmp_path)

    # O normalizador tem o mínimo e o máximo do treino, que não são os da
    # tabela inteira: ajustado com o teste junto, ele teria os da tabela.
    scaler = seen["scaler"]
    assert np.array_equal(scaler.data_min_, feature_matrix(train).min())
    assert np.array_equal(scaler.data_max_, feature_matrix(train).max())
    everything = feature_matrix(synthetic_flows)
    assert not (
        np.array_equal(scaler.data_min_, everything.min())
        and np.array_equal(scaler.data_max_, everything.max())
    )
    pd.testing.assert_frame_equal(seen["train"], train)

    malicious = test["label"].to_numpy() == MALICIOUS
    clean = scaler.transform(feature_matrix(test))
    fragmented = [FEATURE_COLUMNS.index(name) for name in FRAGMENTED_COLUMNS]
    for factor, X in seen["X_by_factor"].items():
        assert np.array_equal(X[~malicious], clean[~malicious])
        changed = X[malicious] != clean[malicious]
        assert not np.delete(changed, fragmented, axis=1).any()
        assert changed[:, fragmented].all() == (factor != 1)
