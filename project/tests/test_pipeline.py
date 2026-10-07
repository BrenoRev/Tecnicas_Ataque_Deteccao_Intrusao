import json

from doh_ids.data import class_counts
from doh_ids.splits import stratified_split
from scripts.e1_reproducao import cross_validated_confusion, run_experiment

SEED = 42
DATA_SHA256 = "0" * 64


def test_end_to_end_run_writes_both_files_and_repeats_identically(synthetic_flows, tmp_path):
    first_dir, _ = run_experiment(synthetic_flows, DATA_SHA256, tmp_path / "first")
    second_dir, _ = run_experiment(synthetic_flows, DATA_SHA256, tmp_path / "second")

    assert first_dir == tmp_path / "first" / "e1" / "fiel" / "proposto" / "seed42"
    assert (first_dir / "run.json").is_file()
    first_text = (first_dir / "metrics.json").read_text(encoding="utf-8")
    assert first_text == (second_dir / "metrics.json").read_text(encoding="utf-8")

    # O teste é um décimo dos fluxos, e a matriz conta cada linha dele uma vez.
    _, test = stratified_split(synthetic_flows, SEED)
    confusion = json.loads(first_text)["test"]["confusion_matrix"]
    assert [sum(row) for row in confusion] == class_counts(test)

    run = json.loads((first_dir / "run.json").read_text(encoding="utf-8"))
    assert run["track"] == "fiel"
    assert run["seed"] == SEED


def test_cross_validation_predicts_each_real_train_row_once(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    confusion = cross_validated_confusion(train, SEED)

    # O SMOTE de cada rodada cria amostras benignas: se alguma chegasse ao fold
    # de validação, a linha de Benign-DoH somaria mais que os benignos reais.
    assert [sum(row) for row in confusion] == class_counts(train)
