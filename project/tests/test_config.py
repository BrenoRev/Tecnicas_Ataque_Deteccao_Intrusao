from doh_ids.config import FEATURE_COLUMNS, ID_COLUMNS


def test_feature_and_id_columns_are_29_and_5_without_repetition_or_overlap():
    assert len(FEATURE_COLUMNS) == 29
    assert len(ID_COLUMNS) == 5
    assert len(set(FEATURE_COLUMNS)) == 29
    assert len(set(ID_COLUMNS)) == 5
    assert set(FEATURE_COLUMNS).isdisjoint(ID_COLUMNS)


def test_fixtures_use_the_column_names_of_config(synthetic_flows, synthetic_raw_csv):
    assert list(synthetic_flows.columns) == FEATURE_COLUMNS + ["label"]
    assert list(synthetic_raw_csv.columns) == ID_COLUMNS + FEATURE_COLUMNS + ["Label"]
