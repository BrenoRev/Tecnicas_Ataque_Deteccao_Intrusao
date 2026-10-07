import numpy as np
import pandas as pd

from doh_ids.config import FEATURE_COLUMNS
from doh_ids.data import class_counts, feature_matrix
from doh_ids.splits import balanced_subsets, fit_scaler, seen_in_train, stratified_split

SEED = 42


def normalized_train(flows):
    """Treino normalizado e rótulos, como `balanced_subsets` os recebe."""
    train, _ = stratified_split(flows, SEED)
    X_train = fit_scaler(train).transform(feature_matrix(train))
    return X_train, train["label"].to_numpy()


def row_set(X):
    """Linhas da matriz como conjunto: os valores sintéticos dos testes não se repetem."""
    return {tuple(row) for row in X}


def test_train_and_test_indices_are_disjoint_and_cover_all_rows(synthetic_flows):
    train, test = stratified_split(synthetic_flows, SEED)

    assert not set(train.index) & set(test.index)
    assert sorted([*train.index, *test.index]) == list(synthetic_flows.index)


def test_split_keeps_class_proportion_with_ten_percent_in_test(synthetic_flows):
    train, test = stratified_split(synthetic_flows, SEED)

    # O teste fica com um décimo de cada classe. Os tamanhos das classes
    # sintéticas são múltiplos de 10, então a divisão inteira é exata.
    total = class_counts(synthetic_flows)
    assert class_counts(test) == [size // 10 for size in total]
    assert class_counts(train) == [size - size // 10 for size in total]


def test_same_seed_gives_same_split_and_other_seed_gives_another(synthetic_flows):
    _, test = stratified_split(synthetic_flows, SEED)
    _, test_again = stratified_split(synthetic_flows, SEED)
    _, test_other_seed = stratified_split(synthetic_flows, SEED + 1)

    assert list(test.index) == list(test_again.index)
    assert list(test.index) != list(test_other_seed.index)


def test_scaler_is_fitted_on_train_only(synthetic_flows):
    train, test = stratified_split(synthetic_flows, SEED)
    test = test.copy()
    extreme = synthetic_flows["Duration"].max() + 1000.0
    test.loc[test.index[0], "Duration"] = extreme

    scaler = fit_scaler(train)

    X_train = feature_matrix(train)
    assert np.array_equal(scaler.data_min_, X_train.min().to_numpy())
    assert np.array_equal(scaler.data_max_, X_train.max().to_numpy())
    whole = pd.concat([train, test])
    assert scaler.data_max_[0] != whole["Duration"].max()
    # O valor extremo do teste, que o scaler não viu, sai do intervalo de 0 a 1.
    assert scaler.transform(feature_matrix(test)).max() > 1.0


def test_seen_in_train_finds_the_planted_duplicate(synthetic_flows):
    train, test = stratified_split(synthetic_flows, SEED)
    test = test.copy()
    assert not seen_in_train(train, test).any()

    planted = 3
    test.loc[test.index[planted], FEATURE_COLUMNS] = train.iloc[0][FEATURE_COLUMNS]
    # O vetor plantado aparece duas vezes no treino: a linha do teste não pode
    # ser contada duas vezes nem deslocar as seguintes.
    train = pd.concat([train, train.iloc[[0]]])

    seen = seen_in_train(train, test)

    assert len(seen) == len(test)
    assert np.flatnonzero(seen).tolist() == [planted]


def test_non_doh_parts_are_disjoint_cover_train_and_differ_by_at_most_one(synthetic_flows):
    X_train, y_train = normalized_train(synthetic_flows)

    subsets, _ = balanced_subsets(X_train, y_train, SEED)

    parts = [row_set(X[y == 0]) for X, y in subsets]
    sizes = [len(part) for part in parts]
    assert len(parts) == 3
    assert sum(sizes) == (y_train == 0).sum()
    assert set.union(*parts) == row_set(X_train[y_train == 0])
    assert max(sizes) - min(sizes) <= 1


def test_malicious_rows_are_the_same_real_rows_in_every_subset(synthetic_flows):
    X_train, y_train = normalized_train(synthetic_flows)

    subsets, _ = balanced_subsets(X_train, y_train, SEED)

    for X, y in subsets:
        assert np.array_equal(X[y == 2], X_train[y_train == 2])


def test_benign_keeps_every_real_row_and_reaches_the_malicious_count(synthetic_flows):
    X_train, y_train = normalized_train(synthetic_flows)
    real_benign = row_set(X_train[y_train == 1])
    n_malicious = int((y_train == 2).sum())

    subsets, summary = balanced_subsets(X_train, y_train, SEED)

    for (X, y), entry in zip(subsets, summary, strict=True):
        assert real_benign <= row_set(X[y == 1])
        assert (y == 1).sum() == n_malicious
        assert entry["class_counts"] == np.bincount(y).tolist()
        assert entry["ratio"] == [count / n_malicious for count in entry["class_counts"]]
        assert entry["synthetic_benign_fraction"] == 1 - len(real_benign) / n_malicious


def test_no_synthetic_sample_in_non_doh(synthetic_flows):
    X_train, y_train = normalized_train(synthetic_flows)
    real_non_doh = row_set(X_train[y_train == 0])

    subsets, _ = balanced_subsets(X_train, y_train, SEED)

    for X, y in subsets:
        assert row_set(X[y == 0]) <= real_non_doh


def test_same_seed_gives_same_subsets_and_other_seed_gives_others(synthetic_flows):
    X_train, y_train = normalized_train(synthetic_flows)

    subsets, _ = balanced_subsets(X_train, y_train, SEED)
    subsets_again, _ = balanced_subsets(X_train, y_train, SEED)
    subsets_other_seed, _ = balanced_subsets(X_train, y_train, SEED + 1)

    for (X, y), (X_again, y_again) in zip(subsets, subsets_again, strict=True):
        assert np.array_equal(X, X_again)
        assert np.array_equal(y, y_again)
    assert not np.array_equal(subsets[0][0], subsets_other_seed[0][0])
