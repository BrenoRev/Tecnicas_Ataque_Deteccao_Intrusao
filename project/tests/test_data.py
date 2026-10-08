import codecs
import zipfile

import numpy as np
import pandas as pd
import pytest

import scripts.e6_dados as e6_dados
from doh_ids.config import (
    CIRA_LOCAL_PREFIX,
    CIRA_TOOLS,
    CIRA_ZIP_MEMBERS,
    DOH_COLUMN,
    FEATURE_COLUMNS,
    ID_COLUMNS,
    LABEL_COLUMN,
    MALICIOUS_ZIP_MEMBER,
    SECOND_DATASET_COLUMNS,
    TOOL_ORIGIN,
)
from doh_ids.data import (
    clean_flows,
    column_differences,
    feature_matrix,
    load_cira,
    load_combined,
    load_hkd,
    load_malicious_by_tool,
    read_flow_csv,
    read_header,
    without_replicas,
)

# Rótulo em texto de cada membro do zip, na ordem de CIRA_ZIP_MEMBERS.
MEMBER_LABELS = ["NonDoH", "Benign", "Malicious"]

# Vezes que cada fluxo do HKD aparece no combinado sintético.
SYNTHETIC_REPLICAS = 3


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


def write_bom_csv(frame, path):
    """Grava o CSV como os do HKD: com BOM e `TimeStamp` sem segundos nem zero à esquerda."""
    moment = pd.to_datetime(frame["TimeStamp"])
    date = moment.dt.year.astype(str) + "/" + moment.dt.month.astype(str)
    date += "/" + moment.dt.day.astype(str)
    short = date + " " + moment.dt.hour.astype(str) + ":" + moment.dt.strftime("%M")
    frame.assign(TimeStamp=short).to_csv(path, index=False, encoding="utf-8-sig")
    return path


@pytest.fixture
def second_dataset_paths(synthetic_raw_csv, tmp_path):
    """Grava o HKD e os três níveis do combinado; devolve o caminho do HKD e a lista dos níveis.

    Os fluxos maliciosos sintéticos são repartidos entre as seis ferramentas. Os
    das três ferramentas do HKD formam o arquivo do HKD e entram no combinado
    repetidos `SYNTHETIC_REPLICAS` vezes.
    """
    raw = synthetic_raw_csv
    non_doh = raw[raw[LABEL_COLUMN] == "NonDoH"]
    benign = raw[raw[LABEL_COLUMN] == "Benign"]
    malicious = raw[raw[LABEL_COLUMN] == "Malicious"]
    tunnels = malicious.assign(**{LABEL_COLUMN: np.resize(list(TOOL_ORIGIN), len(malicious))})
    from_hkd = tunnels[LABEL_COLUMN].map(TOOL_ORIGIN) == "HKD"
    hkd = tunnels[from_hkd]
    level3 = pd.concat([tunnels[~from_hkd]] + [hkd] * SYNTHETIC_REPLICAS)
    # Como nos arquivos reais, o nível 1 repete os fluxos DoH e o nível 2 os maliciosos.
    level2 = pd.concat([benign, level3.assign(**{LABEL_COLUMN: "Malicious"})])
    level1 = pd.concat([level2.assign(**{LABEL_COLUMN: "DoH"}), non_doh])
    levels = [
        write_bom_csv(level, tmp_path / f"l{number}.csv")
        for number, level in enumerate([level1, level2, level3], start=1)
    ]
    return write_bom_csv(hkd, tmp_path / "hkd.csv"), levels


def test_second_dataset_load_returns_features_label_origin_and_tool_without_identifiers(
    synthetic_raw_csv, second_dataset_paths
):
    hkd_path, level_paths = second_dataset_paths
    hkd = load_hkd(hkd_path)
    combined = load_combined(level_paths)

    for flows in [hkd, combined]:
        assert list(flows.columns) == SECOND_DATASET_COLUMNS
        assert list(feature_matrix(flows).columns) == FEATURE_COLUMNS
        assert not set(ID_COLUMNS) & set(flows.columns)
        assert (flows["origin"] == flows["tool"].map(TOOL_ORIGIN).fillna("CIRA")).all()
    assert set(hkd["label"]) == {2}
    assert set(hkd["origin"]) == {"HKD"}
    assert set(combined["label"]) == {0, 1, 2}
    malicious = combined["label"] == 2
    assert set(combined.loc[malicious, "tool"]) == set(TOOL_ORIGIN)
    assert combined.loc[~malicious, "tool"].isna().all()
    # Cada fluxo entra uma vez: as linhas DoH do nível 1 e Malicious do nível 2
    # repetem o nível 3 e não são somadas.
    assert len(combined) == len(synthetic_raw_csv) + (SYNTHETIC_REPLICAS - 1) * len(hkd)


def test_column_differences_reports_missing_and_renamed_columns(synthetic_raw_csv):
    header = list(synthetic_raw_csv.columns)
    without_duration = [column for column in header if column != "Duration"]
    renamed = ["duration" if column == "Duration" else column for column in header]

    assert column_differences(header) == {"missing": [], "unexpected": []}
    assert column_differences(without_duration) == {"missing": ["Duration"], "unexpected": []}
    assert column_differences(renamed) == {"missing": ["Duration"], "unexpected": ["duration"]}


def test_csv_with_bom_and_short_timestamp_is_read_with_source_ip_first(synthetic_raw_csv, tmp_path):
    path = write_bom_csv(synthetic_raw_csv, tmp_path / "hkd.csv")
    assert path.read_bytes().startswith(codecs.BOM_UTF8)

    flows = read_flow_csv(path)

    assert read_header(path)[0] == "SourceIP"
    assert flows.columns[0] == "SourceIP"
    assert flows["TimeStamp"].iloc[0] == "2020/1/14 15:49"
    assert all(pd.api.types.is_numeric_dtype(flows[column]) for column in FEATURE_COLUMNS)


def test_without_replicas_keeps_one_row_per_hkd_flow_and_all_cira_rows(second_dataset_paths):
    hkd_path, level_paths = second_dataset_paths
    combined = load_combined(level_paths)
    # Uma linha do CIRA repetida: ela não é réplica do HKD e precisa ficar.
    combined = pd.concat([combined, combined.iloc[[0]]], ignore_index=True)
    from_hkd = combined["origin"] == "HKD"

    unique = without_replicas(combined)

    unique_hkd = unique[unique["origin"] == "HKD"]
    assert len(unique_hkd) == len(load_hkd(hkd_path))
    assert len(unique_hkd) * SYNTHETIC_REPLICAS == from_hkd.sum()
    assert not unique_hkd.duplicated(subset=FEATURE_COLUMNS + ["tool"]).any()
    pd.testing.assert_frame_equal(unique[unique["origin"] == "CIRA"], combined[~from_hkd])


def test_script_table_without_replicas_has_each_hkd_flow_once(second_dataset_paths, monkeypatch):
    hkd_path, level_paths = second_dataset_paths
    # Nos arquivos reais nenhum fluxo do HKD tem valor ausente, e a conferência
    # das réplicas conta com isso: as linhas sintéticas com ausente ficam de fora.
    hkd = load_hkd(hkd_path).dropna(subset=FEATURE_COLUMNS)
    combined = load_combined(level_paths).dropna(subset=FEATURE_COLUMNS)

    def synthetic_hkd(path=None):
        # Com caminho, o script pede o arquivo replicado do HKD.
        return hkd if path is None else pd.concat([hkd] * SYNTHETIC_REPLICAS, ignore_index=True)

    # O script lê os arquivos de data/raw/ pelos caminhos padrão: aqui ele
    # recebe as tabelas sintéticas e o número de cópias delas.
    monkeypatch.setattr(e6_dados, "load_hkd", synthetic_hkd)
    monkeypatch.setattr(e6_dados, "load_combined", lambda: combined)
    monkeypatch.setattr(e6_dados, "HKD_REPLICAS", SYNTHETIC_REPLICAS)
    tables, _ = e6_dados.load_checked_sources()

    unique = tables["combinado_sem_replicas"]
    unique_hkd = unique[unique["origin"] == "HKD"]
    assert len(unique_hkd) == len(hkd)
    assert not unique_hkd.duplicated(subset=FEATURE_COLUMNS + ["tool"]).any()
    assert len(tables["combinado"]) == len(unique) + (SYNTHETIC_REPLICAS - 1) * len(hkd)


def test_second_dataset_load_does_not_create_group_or_time_window(second_dataset_paths):
    hkd_path, level_paths = second_dataset_paths

    for flows in [load_hkd(hkd_path), load_combined(level_paths)]:
        assert "group" not in flows.columns
        assert "time_window" not in flows.columns


def test_tool_load_keeps_only_doh_rows_with_the_tool_of_the_folder(synthetic_raw_csv, tmp_path):
    # Como nos arquivos reais: sem a coluna Label, com a coluna DoH booleana e
    # algumas linhas em que ela é falsa.
    raw = synthetic_raw_csv.drop(columns=LABEL_COLUMN)
    parts = [raw.iloc[start :: len(CIRA_TOOLS)] for start in range(len(CIRA_TOOLS))]
    not_doh_rows = 3
    with zipfile.ZipFile(tmp_path / "malicious.zip", "w") as archive:
        for tool, part in zip(CIRA_TOOLS, parts, strict=True):
            is_doh = np.arange(len(part)) >= not_doh_rows
            member = MALICIOUS_ZIP_MEMBER.format(tool=tool)
            archive.writestr(member, part.assign(**{DOH_COLUMN: is_doh}).to_csv(index=False))

    flows = load_malicious_by_tool(tmp_path / "malicious.zip")

    assert list(flows.columns) == FEATURE_COLUMNS + ["tool"]
    assert not set(ID_COLUMNS) & set(flows.columns)
    for tool, part in zip(CIRA_TOOLS, parts, strict=True):
        expected = part.iloc[not_doh_rows:]
        loaded = flows[flows["tool"] == tool]
        assert len(loaded) == len(expected)
        # Duration identifica a linha: cada ferramenta recebe as linhas da sua pasta.
        assert np.allclose(loaded["Duration"], expected["Duration"])
