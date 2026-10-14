import numpy as np
import pandas as pd

from doh_ids.config import FEATURE_COLUMNS
from doh_ids.data import class_counts, feature_matrix
from doh_ids.splits import fit_scaler, seen_in_train, stratified_split

SEED = 42


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
