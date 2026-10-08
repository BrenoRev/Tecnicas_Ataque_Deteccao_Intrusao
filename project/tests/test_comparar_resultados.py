import json
import shutil

import pytest

from scripts.comparar_resultados import main

METRICS = "e1/fiel/proposto/seed42/metrics.json"
AGGREGATE = "e8/corrigida/summary.json"


def write_json(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")


@pytest.fixture
def trees(tmp_path):
    """Duas árvores results/ pequenas e iguais: uma execução, um agregado e um resumo."""
    reference = tmp_path / "versionado"
    write_json(reference / METRICS, {"test": {"accuracy": 0.9779, "f1_macro": 0.6575}})
    write_json(
        reference / AGGREGATE,
        {
            "models": {"A": {"f1_macro": {"mean": 0.9656}, "train_seconds": {"mean": 161.0}}},
            "paired": [
                {"metric": "f1_macro", "mean_difference": 0.005},
                {"metric": "train_seconds", "mean_difference": 102.2},
            ],
        },
    )
    (reference / "e1/RESUMO.md").write_text("ajuste em 902 s\n", encoding="utf-8")
    regenerated = tmp_path / "regenerado"
    shutil.copytree(reference, regenerated)
    return reference, regenerated


def test_equal_trees_exit_with_zero(trees, capsys):
    reference, regenerated = trees

    assert main([str(reference), str(regenerated)]) == 0
    assert "2 comparados, 2 iguais, 0 diferentes" in capsys.readouterr().out


def test_changed_metric_exits_with_one_and_names_the_key(trees, capsys):
    reference, regenerated = trees
    write_json(regenerated / METRICS, {"test": {"accuracy": 0.9779, "f1_macro": 0.6576}})

    assert main([str(reference), str(regenerated)]) == 1
    output = capsys.readouterr().out
    assert f"DIFERENTE {METRICS}: test.f1_macro" in output
    assert "2 comparados, 1 iguais, 1 diferentes" in output


def test_difference_only_in_time_is_not_a_failure(trees, capsys):
    reference, regenerated = trees
    aggregate = json.loads((regenerated / AGGREGATE).read_text(encoding="utf-8"))
    aggregate["models"]["A"]["train_seconds"]["mean"] = 112.5
    aggregate["paired"][1]["mean_difference"] = 150.7
    write_json(regenerated / AGGREGATE, aggregate)
    (regenerated / "e1/RESUMO.md").write_text("ajuste em 850 s\n", encoding="utf-8")

    assert main([str(reference), str(regenerated)]) == 0
    assert "cita tempo, não conta: e1/RESUMO.md: linha 1" in capsys.readouterr().out
