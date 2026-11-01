import csv
import json
import shutil

import pytest

from doh_ids.config import RESULTS_DIR
from scripts.make_report_assets import (
    READINGS,
    Table,
    build_assets,
    make_assets,
    write_table,
)

# Acurácia plantada na árvore de mentira: um valor que nenhum experimento produz.
PLANTED_ACCURACY = 0.123456
PLANTED_RUN = "e1/variante/profundidade_variavel/seed42/metrics.json"
OPTIONAL_SUMMARY = "e8/corrigida/summary-robustez.json"
REQUIRED_RUN = "e7/fiel/ferramenta/seed42/metrics.json"


def copy_results(target):
    """Copia os arquivos de dados de results/ versionados, sem as imagens e os resumos."""
    shutil.copytree(RESULTS_DIR, target, ignore=shutil.ignore_patterns("*.png", "*.md"))
    return target


@pytest.fixture(scope="module")
def fake_results(tmp_path_factory):
    """Árvore results/ de mentira: a versionada, com a acurácia de uma execução trocada."""
    results = copy_results(tmp_path_factory.mktemp("fake") / "results")
    path = results / PLANTED_RUN
    metrics = json.loads(path.read_text(encoding="utf-8"))
    metrics["test"]["accuracy"] = PLANTED_ACCURACY
    path.write_text(json.dumps(metrics), encoding="utf-8")
    return results


@pytest.fixture(scope="module")
def tables(fake_results):
    assets, _ = build_assets(fake_results)
    return [asset for asset in assets if isinstance(asset, Table)]


def write_tables(tables, folder):
    folder.mkdir()
    for table in tables:
        write_table(table, folder)
    return {path.name: path.read_bytes() for path in folder.iterdir()}


def test_number_in_table_is_the_one_in_metrics_json(fake_results, tmp_path):
    report = tmp_path / "report"

    make_assets(fake_results, report)

    with (report / "tables" / "reproducao_metricas.csv").open(encoding="utf-8") as file:
        rows = {row["Métrica"]: row for row in csv.DictReader(file)}
    assert rows["Acurácia"]["Prof. var."] == f"{100 * PLANTED_ACCURACY:.2f}"
    tex = (report / "tables" / "reproducao_metricas.tex").read_text(encoding="utf-8")
    assert f"{100 * PLANTED_ACCURACY:.2f}".replace(".", ",") in tex
    # Cada tabela sai nos dois formatos e cada figura também; o índice lista todas.
    index = (report / "INDICE.md").read_text(encoding="utf-8")
    for folder, suffixes in [("tables", {".tex", ".csv"}), ("figures", {".pdf", ".png"})]:
        files = list((report / folder).iterdir())
        assert files
        for path in files:
            assert path.suffix in suffixes
            assert all(path.with_suffix(suffix).exists() for suffix in suffixes)
            assert f"{folder}/{path.stem}`" in index


def test_missing_required_result_fails(tmp_path):
    results = copy_results(tmp_path / "results")
    (results / REQUIRED_RUN).unlink()

    with pytest.raises(FileNotFoundError, match="ferramenta"):
        build_assets(results)


def test_missing_optional_result_is_listed_as_not_generated(tmp_path):
    results = copy_results(tmp_path / "results")
    (results / OPTIONAL_SUMMARY).unlink()

    assets, skipped = build_assets(results)

    assert len(skipped) == 1
    assert "robustez" in skipped[0]
    assert OPTIONAL_SUMMARY in skipped[0]
    assert not [asset.name for asset in assets if asset.name.startswith("robustez")]


def test_two_runs_write_identical_tex_and_csv(fake_results, tables, tmp_path):
    first = write_tables(tables, tmp_path / "first")
    again, _ = build_assets(fake_results)

    second = write_tables(
        [asset for asset in again if isinstance(asset, Table)], tmp_path / "second"
    )

    assert first == second
    assert {name.rsplit(".", 1)[1] for name in first} == {"tex", "csv"}


def test_model_tables_name_track_seed_and_average_in_caption(tables):
    model_tables = [table for table in tables if table.tracks]
    assert model_tables
    for table in model_tables:
        assert "Trilha" in table.caption, table.name
        assert all(track in table.caption for track in table.tracks), table.name
        assert "seed" in table.caption, table.name
        assert any(
            average in table.caption for average in ["macro", "ponderada", "sem média agregada"]
        ), table.name
    # Sem trilha, só tabela de contagem de dados ou de literatura.
    for table in tables:
        if not table.tracks:
            assert table.name.startswith("dados_") or table.name == "tabela2_literatura"


def test_tables_with_both_depth_readings_identify_each_one(tables):
    both = [table for table in tables if set(READINGS) <= set(table.tracks)]
    assert both
    for table in both:
        cells = [*table.header, *(cell for row in table.rows if row for cell in row)]
        text = " ".join(str(cell) for cell in cells).lower()
        assert "prof. 5" in text, table.name
        assert "prof. var" in text, table.name
