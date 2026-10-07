import zipfile

import numpy as np
import pandas as pd

from doh_ids.config import (
    CIRA_LOCAL_PREFIX,
    CIRA_ZIP_MEMBERS,
    FEATURE_COLUMNS,
    ID_COLUMNS,
    LABEL_COLUMN,
)
from doh_ids.data import clean_flows, feature_matrix, load_cira

# Rótulo em texto de cada membro do zip, na ordem de CIRA_ZIP_MEMBERS.
MEMBER_LABELS = ["NonDoH", "Benign", "Malicious"]


def write_cira_zip(raw, path):
    """Grava o CSV bruto sintético no formato do zip publicado, com os quatro membros."""
    members = {
        name: raw[raw[LABEL_COLUMN] == label]
        for name, label in zip(CIRA_ZIP_MEMBERS, MEMBER_LABELS, strict=True)
    }
    # Como no zip real, l1-doh.csv repete os fluxos dos dois arquivos l2.
    doh = pd.concat([members["l2-benign.csv"], members["l2-malicious.csv"]])
    members["l1-doh.csv"] = doh.assign(**{LABEL_COLUMN: "DoH"})
    with zipfile.ZipFile(path, "w") as archive:
        for name, frame in members.items():
            archive.writestr(name, frame.to_csv(index=False))
    return path


def test_load_returns_features_and_integer_label_without_identifiers(synthetic_raw_csv, tmp_path):
    flows = load_cira(write_cira_zip(synthetic_raw_csv, tmp_path / "cira.zip"))

    assert set(FEATURE_COLUMNS) <= set(flows.columns)
    assert set(flows["label"]) == {0, 1, 2}
    X = feature_matrix(flows)
    assert list(X.columns) == FEATURE_COLUMNS
    assert not set(ID_COLUMNS) & set(X.columns)


def test_feature_matrix_is_selected_by_name(synthetic_raw_csv, tmp_path):
    raw = synthetic_raw_csv.assign(FlowIndex=range(len(synthetic_raw_csv)))
    flows = load_cira(write_cira_zip(raw, tmp_path / "cira.zip"))

    assert "FlowIndex" not in flows.columns
    assert list(feature_matrix(flows.assign(Unknown=1.0)).columns) == FEATURE_COLUMNS


def test_clean_removes_what_the_rule_asks_and_counts_by_class(synthetic_flows):
    first_of_class = [int(np.flatnonzero(synthetic_flows["label"] == code)[0]) for code in range(3)]
    flows = synthetic_flows.copy()
    flows.loc[first_of_class[0], "Duration"] = np.nan
    flows.loc[first_of_class[1], "Duration"] = np.inf
    repeated = flows.iloc[[first_of_class[2] + 1]]
    flows = pd.concat([flows, repeated, repeated], ignore_index=True)

    _, removed_nan = clean_flows(flows, drop_nan=True, drop_inf=False, duplicate_columns=None)
    _, removed_inf = clean_flows(flows, drop_nan=False, drop_inf=True, duplicate_columns=None)
    _, removed_repeated = clean_flows(
        flows, drop_nan=False, drop_inf=False, duplicate_columns=FEATURE_COLUMNS
    )
    cleaned, removed_all = clean_flows(
        flows, drop_nan=True, drop_inf=True, duplicate_columns=FEATURE_COLUMNS
    )

    assert removed_nan == [1, 0, 0]
    assert removed_inf == [0, 1, 0]
    assert removed_repeated == [0, 0, 2]
    assert removed_all == [1, 1, 2]
    assert len(cleaned) == len(synthetic_flows) - 2
    assert np.isfinite(feature_matrix(cleaned)).all(axis=None)
    assert not cleaned.duplicated(subset=FEATURE_COLUMNS).any()


def test_load_keeps_duplicated_rows(synthetic_raw_csv, tmp_path):
    raw = pd.concat([synthetic_raw_csv, synthetic_raw_csv.iloc[[0]]], ignore_index=True)
    flows = load_cira(write_cira_zip(raw, tmp_path / "cira.zip"))

    assert len(flows) == len(raw)
    assert flows.duplicated().sum() == 1


def test_load_reads_only_the_three_configured_members(synthetic_raw_csv, tmp_path):
    path = write_cira_zip(synthetic_raw_csv, tmp_path / "cira.zip")
    with zipfile.ZipFile(path) as archive:
        assert "l1-doh.csv" in archive.namelist()

    flows = load_cira(path)

    # Lido também, l1-doh.csv somaria os fluxos DoH uma segunda vez; com o rótulo
    # "DoH", que não é uma das três classes, a carga seria interrompida.
    assert len(flows) == len(synthetic_raw_csv)
    assert flows["label"].value_counts().to_dict() == {0: 1800, 2: 480, 1: 60}


def test_group_is_the_local_machine_on_either_side_of_the_flow(synthetic_raw_csv, tmp_path):
    flows = load_cira(write_cira_zip(synthetic_raw_csv, tmp_path / "cira.zip"))

    resolver_is_source = ~flows["SourceIP"].str.startswith(CIRA_LOCAL_PREFIX)
    assert resolver_is_source.any()
    assert (~resolver_is_source).any()
    assert flows["group"].str.startswith(CIRA_LOCAL_PREFIX).all()
    in_destination = flows[resolver_is_source]
    in_source = flows[~resolver_is_source]
    assert (in_destination["group"] == in_destination["DestinationIP"]).all()
    assert (in_source["group"] == in_source["SourceIP"]).all()
