import numpy as np
import pandas as pd

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
