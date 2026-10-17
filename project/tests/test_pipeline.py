import json

import pytest

import scripts.e1_reproducao as e1
from doh_ids.config import FEATURE_COLUMNS, MAX_DEPTH
from doh_ids.data import class_counts
from doh_ids.splits import stratified_split

SEED = 42
DATA_SHA256 = "0" * 64


@pytest.mark.parametrize("reading", e1.READINGS, ids=lambda reading: reading["track"])
def test_end_to_end_run_writes_both_files_and_repeats_identically(
    synthetic_flows, tmp_path, reading
):
    first_dir, _ = e1.run_experiment(synthetic_flows, DATA_SHA256, tmp_path / "first", reading)
    second_dir, _ = e1.run_experiment(synthetic_flows, DATA_SHA256, tmp_path / "second", reading)

    expected = tmp_path / "first" / "e1" / reading["track"] / reading["slice_name"] / "seed42"
    assert first_dir == expected
    assert (first_dir / "run.json").is_file()
    first_text = (first_dir / "metrics.json").read_text(encoding="utf-8")
    assert first_text == (second_dir / "metrics.json").read_text(encoding="utf-8")

    # O teste é um décimo dos fluxos, e a matriz conta cada linha dele uma vez.
    _, test = stratified_split(synthetic_flows, SEED)
    confusion = json.loads(first_text)["test"]["confusion_matrix"]
    assert [sum(row) for row in confusion] == class_counts(test)

    # A profundidade registrada é a do modelo ajustado: se o argumento fosse
    # ignorado, a variante sairia igual à trilha fiel sem erro aparente.
    run = json.loads((first_dir / "run.json").read_text(encoding="utf-8"))
    assert run["track"] == reading["track"]
    assert run["config"]["max_depth"] == reading["max_depth"]
    assert run["seed"] == SEED


def test_cross_validation_predicts_each_real_train_row_once(synthetic_flows):
    train, _ = stratified_split(synthetic_flows, SEED)

    confusion = e1.cross_validated_confusion(train, SEED, MAX_DEPTH)

    # O SMOTE de cada rodada cria amostras benignas: se alguma chegasse ao fold
    # de validação, a linha de Benign-DoH somaria mais que os benignos reais.
    assert [sum(row) for row in confusion] == class_counts(train)


def test_cross_validation_scaler_never_sees_the_held_out_fold(synthetic_flows, monkeypatch):
    train, _ = stratified_split(synthetic_flows, SEED)
    # Um valor extremo em uma única linha: o máximo do normalizador só pode ser
    # esse valor nas rodadas em que a linha está nos folds de treino.
    planted_row, planted_value = train.index[0], 1e6
    train.loc[planted_row, FEATURE_COLUMNS[0]] = planted_value
    seen = []

    def recording_fit_system(fold_train, seed, max_depth):
        fitted = fit_system(fold_train, seed, max_depth)
        seen.append((planted_row in fold_train.index, fitted[0].data_max_[0]))
        return fitted

    fit_system = e1.fit_system
    monkeypatch.setattr(e1, "fit_system", recording_fit_system)
    e1.cross_validated_confusion(train, SEED, MAX_DEPTH)

    assert [in_fit for in_fit, _ in seen].count(False) == 1
    for in_fit, scaler_maximum in seen:
        assert (scaler_maximum == planted_value) == in_fit
