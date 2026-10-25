import json

import pytest

import scripts.e1_reproducao as e1
import scripts.e4_corrigido as e4
import scripts.e4_resumo as e4_resumo
import scripts.e6_dataset2 as e6
from doh_ids import system
from doh_ids.config import CLASS_NAMES, CORRIGIDA_MODELS, FEATURE_COLUMNS, MAX_DEPTH
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

    confusion = system.cross_validated_confusion(train, SEED, MAX_DEPTH)

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

    fit_system = system.fit_system
    monkeypatch.setattr(system, "fit_system", recording_fit_system)
    system.cross_validated_confusion(train, SEED, MAX_DEPTH)

    assert [in_fit for in_fit, _ in seen].count(False) == 1
    for in_fit, scaler_maximum in seen:
        assert (scaler_maximum == planted_value) == in_fit


def test_transfer_scales_the_second_dataset_with_the_scaler_of_the_first_train(
    synthetic_flows, tmp_path
):
    malicious = CLASS_NAMES.index("Malicious-DoH")
    second = synthetic_flows[synthetic_flows["label"] == malicious].head(30).copy()
    second["tool"] = ["dnstt", "tcp-over-dns", "tuns"] * 10
    # Todo fluxo do segundo dataset fica muito acima do máximo do primeiro em
    # um atributo. Com o scaler do treino do primeiro, todos saem do intervalo
    # de 0 a 1; um scaler que tivesse visto o segundo dataset os traria de volta.
    second[FEATURE_COLUMNS[0]] += 1e6
    sha256 = {"cira": DATA_SHA256, "hkd": "1" * 64}

    run_dir, metrics = e6.run_transfer(synthetic_flows, second, sha256, tmp_path, e6.READINGS[1])

    outside = metrics["hkd_outside_unit_interval"]
    assert outside["rows"] == len(second)
    assert outside["by_column"][FEATURE_COLUMNS[0]] == len(second)
    train, _ = stratified_split(synthetic_flows, SEED)
    assert metrics["train_rows"] == class_counts(train)
    assert metrics["hkd"]["malicious"]["n"] == len(second)
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert run_dir == tmp_path / "e6" / "fiel" / "transferencia" / "seed42"
    assert run["config"]["train_dataset"] == "cira"
    assert run["config"]["max_depth"] == MAX_DEPTH


def test_every_model_of_a_seed_gets_the_same_train_and_test_rows(
    synthetic_flows, tmp_path, monkeypatch
):
    seeds = [0, 1]
    fitted, evaluated = [], []

    def recording_fit_model(name, train, seed, balanced):
        fitted.append((seed, list(train.index)))
        return fit_model(name, train, seed, balanced)

    def recording_model_metrics(scaler, model, test, seen):
        evaluated.append(list(test.index))
        return model_metrics(scaler, model, test, seen)

    fit_model, model_metrics = e4.fit_model, e4.model_metrics
    monkeypatch.setattr(e4, "fit_model", recording_fit_model)
    monkeypatch.setattr(e4, "model_metrics", recording_model_metrics)
    e4.run_experiment(synthetic_flows, DATA_SHA256, tmp_path, seeds)

    n_models = len(CORRIGIDA_MODELS)
    assert len(fitted) == len(evaluated) == n_models * len(seeds)
    for position, seed in enumerate(seeds):
        calls = slice(position * n_models, (position + 1) * n_models)
        train, test = stratified_split(synthetic_flows, seed)
        assert fitted[calls] == [(seed, list(train.index))] * n_models
        assert evaluated[calls] == [list(test.index)] * n_models
    # Seeds diferentes dão splits diferentes: sem isso as dez execuções seriam uma só.
    assert evaluated[0] != evaluated[n_models]


@pytest.fixture
def e4_run(synthetic_flows, tmp_path):
    """Roda o protocolo corrigido em duas seeds e devolve as seeds e o que ficou em memória."""
    seeds = [0, 1]
    return seeds, e4.run_experiment(synthetic_flows, DATA_SHA256, tmp_path, seeds)


def test_corrected_run_registers_the_track_and_the_depth_reading(e4_run, tmp_path):
    for name, spec in CORRIGIDA_MODELS.items():
        run_file = tmp_path / "e4" / "corrigida" / name / "seed1" / "run.json"
        run = json.loads(run_file.read_text(encoding="utf-8"))
        assert run["track"] == "corrigida"
        assert run["config"]["max_depth"] == spec["max_depth"]


def test_corrected_summary_is_rebuilt_from_the_saved_files_without_training(e4_run, tmp_path):
    seeds, in_memory = e4_run

    saved = e4_resumo.load_results(tmp_path / "e4" / "corrigida", seeds)
    summary = e4_resumo.summary_content(saved)

    # O que o resumo lê do disco é o que o treino avaliou: a agregação não depende de retreinar.
    assert saved == in_memory
    assert set(summary["models"]) == set(CORRIGIDA_MODELS)
    assert all(model["test"]["macro_f1"]["n"] == len(seeds) for model in summary["models"].values())
    assert "## Hipótese ao lado do resultado" in e4_resumo.summary_text(summary, saved)
