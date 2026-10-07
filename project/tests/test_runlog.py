import json

import pytest

from doh_ids import runlog
from doh_ids.runlog import save_run

METRICS = {"accuracy": 0.5, "confusion_matrix": [[1, 0], [0, 1]]}
CONFIG = {"n_estimators": 10}
DATA_SHA256 = "0" * 64
TIMINGS = {"fit_seconds": 1.5}


def save_example_run(results_dir, track="fiel", timings=TIMINGS):
    return save_run("e1", track, "proposto", 42, METRICS, CONFIG, DATA_SHA256, timings, results_dir)


def test_save_run_writes_both_files_in_the_standard_path(tmp_path):
    run_dir = save_example_run(tmp_path)

    assert run_dir == tmp_path / "e1" / "fiel" / "proposto" / "seed42"
    assert (run_dir / "metrics.json").is_file()
    assert (run_dir / "run.json").is_file()


def test_run_json_declares_track_seed_versions_data_hash_commit_and_machine(tmp_path):
    run_dir = save_example_run(tmp_path)

    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert run["track"] == "fiel"
    assert run["seed"] == 42
    assert run["data_sha256"] == DATA_SHA256
    assert run["python"]
    assert set(run["libraries"]) == set(runlog.LIBRARIES)
    assert "commit" in run
    assert isinstance(run["dirty"], bool)
    assert run["hostname"]
    assert run["cpu_count"] >= 1


def test_save_run_rejects_unknown_track(tmp_path):
    with pytest.raises(ValueError, match="Trilha inválida"):
        save_example_run(tmp_path, track="teste")
    assert list(tmp_path.iterdir()) == []


def test_metrics_json_is_identical_across_runs_and_has_no_time(tmp_path):
    first_dir = save_example_run(tmp_path / "a", timings={"fit_seconds": 1.5})
    second_dir = save_example_run(tmp_path / "b", timings={"fit_seconds": 9.0})

    first = (first_dir / "metrics.json").read_bytes()
    assert first == (second_dir / "metrics.json").read_bytes()
    assert json.loads(first) == METRICS
    run = json.loads((first_dir / "run.json").read_text(encoding="utf-8"))
    assert run["timings"] == {"fit_seconds": 1.5}
    assert run["timestamp"]


def test_save_run_outside_git_repository_records_null_commit(tmp_path, monkeypatch):
    monkeypatch.setattr(runlog, "PROJECT_ROOT", tmp_path)

    run_dir = save_example_run(tmp_path / "results")

    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert run["commit"] is None
    assert run["dirty"] is True
