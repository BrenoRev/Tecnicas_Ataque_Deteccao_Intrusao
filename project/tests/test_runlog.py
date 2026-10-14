import json
import re
import subprocess

import pytest

from doh_ids import runlog
from doh_ids.runlog import git_state, save_run

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
    # Os testes rodam dentro do repositório: o commit é o hash completo.
    assert re.fullmatch(r"[0-9a-f]{40}", run["commit"])
    assert isinstance(run["dirty"], bool)
    assert run["hostname"]
    assert run["cpu_count"] >= 1


@pytest.fixture
def project_dir(tmp_path):
    """Repositório Git com um commit; devolve a pasta do projeto, um nível abaixo da raiz."""
    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    (project / "src" / "model.py").write_text("x = 1\n", encoding="utf-8")
    identity = ["-c", "user.name=teste", "-c", "user.email=teste@example.com"]
    for args in (
        ["init", "--quiet"],
        ["add", "project/src/model.py"],
        [*identity, "-c", "commit.gpgsign=false", "commit", "--quiet", "--message", "inicial"],
    ):
        subprocess.run(["git", *args], cwd=tmp_path, check=True)
    return project


def test_git_state_is_not_dirty_with_clean_tree(project_dir):
    commit, dirty = git_state(project_dir)

    assert re.fullmatch(r"[0-9a-f]{40}", commit)
    assert dirty is False


def test_git_state_is_dirty_when_a_code_file_is_modified(project_dir):
    (project_dir / "src" / "model.py").write_text("x = 2\n", encoding="utf-8")

    assert git_state(project_dir)[1] is True


def test_git_state_ignores_new_file_in_results_dir(project_dir):
    results = project_dir / runlog.RESULTS_DIR.name
    results.mkdir()
    (results / "metrics.json").write_text("{}\n", encoding="utf-8")

    assert git_state(project_dir)[1] is False


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
