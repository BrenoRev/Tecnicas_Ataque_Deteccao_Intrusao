"""E8: robustez do sistema do artigo e da modificação à manipulação da duração do fluxo.

O artigo publica que a duração do fluxo pesa na decisão (Fig. 5 e Fig. 6a) e
não avalia um atacante que a mude. Este script mede duas coisas, em dez seeds,
no CIRA-CIC-DoHBrw-2020:

- ablação: cada modelo de `ROBUSTNESS_MODELS` é ajustado com todos os
  atributos, sem `Duration` e sem `Duration` e as duas taxas de bytes por
  segundo (`ROBUSTNESS_COLUMN_SETS`), e avaliado no teste sem perturbação;
- fragmentação: cada um desses modelos, sem novo ajuste, prediz os fluxos
  Malicious-DoH do teste depois de a duração e os bytes serem divididos por
  cada fator de `FRAGMENTATION_FACTORS`.

A fragmentação é uma perturbação no espaço de atributos, não um ataque
reproduzido em rede: as estatísticas por pacote ficam com o valor do fluxo
inteiro. Só o teste é perturbado, e só a classe maliciosa; o normalizador e os
modelos são ajustados no treino sem perturbação.

Com todos os atributos, cada modelo é o que já foi medido: o script confere
que a matriz de confusão no teste é a gravada por scripts/e4_corrigido.py (A e
A-prof5) e por scripts/e8_modificacao.py (o modelo proposto). Os
hiperparâmetros do modelo proposto são os que a seleção gravada escolheu no
treino da mesma seed, com os 29 atributos; a seleção não é refeita aqui.

Lê data/processed/cira.parquet. Grava metrics.json e run.json em
results/e8/corrigida/robustez-<modelo>-<colunas>/seed<k>/, uma execução por
vez. A execução já gravada pelo mesmo commit, com a árvore limpa, não é
refeita: o script pode ser interrompido e retomado. A agregação e a leitura
dos números são feitas por scripts/e8_robustez_resumo.py, sem treinar.

Roda como módulo, a partir da pasta do projeto, porque importa outros scripts.

Uso: uv run python -m scripts.e8_robustez
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

import scripts.e4_corrigido as e4
import scripts.e8_modificacao as e8
from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    CORRIGIDA_MODELS,
    FRAGMENTATION_FACTORS,
    FRAGMENTED_COLUMNS,
    MODIFIED_SELECTED_MODEL,
    PROJECT_ROOT,
    RESULTS_DIR,
    ROBUSTNESS_COLUMN_SETS,
    ROBUSTNESS_MODELS,
    SEEDS_CORRIGIDA,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.evaluate import evaluate, outside_unit_interval
from doh_ids.models import base_forests, fit_modified_forest, stacked_forest
from doh_ids.robustness import drop_features, fragment_malicious, kept_features
from doh_ids.runlog import git_state, save_run
from doh_ids.splits import balanced_subsets, fit_scaler, stratified_split

EXPERIMENT = e8.EXPERIMENT
TRACK = e8.TRACK
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")
SLICE_NAME = "robustez-{model}-{columns}"

# Execuções já gravadas de cada modelo com todos os atributos, nas mesmas seeds
# e nos mesmos splits: A e A-prof5 pelo protocolo corrigido, o modelo proposto
# pelo script da modificação.
REFERENCE_DIRS = {
    "A": e8.E4_DIR / "A",
    "A-prof5": e8.E4_DIR / "A-prof5",
    MODIFIED_SELECTED_MODEL: RESULTS_DIR / EXPERIMENT / TRACK / f"{MODIFIED_SELECTED_MODEL}-cira",
}

# Taxa de bytes por segundo e a coluna de bytes de que o extrator a calcula.
RATE_OF_BYTES = {"FlowSentRate": "FlowBytesSent", "FlowReceivedRate": "FlowBytesReceived"}


def reference_metrics(model: str, seed: int) -> dict:
    """Lê o metrics.json já gravado de `model` com todos os atributos, na seed dada."""
    path = REFERENCE_DIRS[model] / f"seed{seed}" / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def fit_original(
    train: pd.DataFrame, scaler: MinMaxScaler, seed: int, max_depth: int | None, dropped: list[str]
) -> tuple[StackingClassifier, list[list[int]], dict]:
    """Ajusta o sistema do artigo, só com `train`, sem os atributos `dropped`.

    `scaler` é o normalizador ajustado em `train`. Devolve o modelo empilhado,
    as amostras por classe de cada subconjunto e os tempos, em segundos.
    """
    # As colunas saem da matriz já normalizada, antes dos subconjuntos e do
    # SMOTE: nenhuma etapa do ajuste enxerga um atributo retirado. O resto é o
    # ajuste do sistema do artigo, passo a passo.
    X_train = drop_features(scaler.transform(feature_matrix(train)), dropped)
    y_train = train["label"].to_numpy()
    start = time.perf_counter()
    subsets, summary = balanced_subsets(X_train, y_train, seed)
    forests = base_forests(subsets, seed, max_depth)
    model = stacked_forest(forests, X_train, y_train, seed)
    timings = {"fit_seconds": round(time.perf_counter() - start, 1)}
    return model, [entry["class_counts"] for entry in summary], timings


def fit_modification(
    train: pd.DataFrame, scaler: MinMaxScaler, seed: int, dropped: list[str]
) -> tuple[RandomForestClassifier, list[list[int]], dict]:
    """Ajusta o modelo proposto, só com `train`, sem os atributos `dropped`.

    Os hiperparâmetros são os que a seleção já gravada escolheu no treino desta
    seed. Devolve o Random Forest, as amostras por classe do treino e os tempos.
    """
    combination = reference_metrics(MODIFIED_SELECTED_MODEL, seed)["selection"]["selected"]
    kept = kept_features(dropped)
    start = time.perf_counter()
    pipeline = fit_modified_forest(
        feature_matrix(train)[kept], train["label"].to_numpy(), seed, **combination
    )
    timings = {"fit_seconds": round(time.perf_counter() - start, 1)}
    # O normalizador trata cada coluna em separado: o do Pipeline, ajustado só
    # nas colunas que ficam, é o do treino inteiro sem as colunas retiradas.
    # Por isso o Random Forest pode predizer a matriz normalizada por `scaler`.
    fitted_scaler = pipeline.named_steps["scaler"]
    assert np.array_equal(fitted_scaler.scale_, drop_features(scaler.scale_[None, :], dropped)[0])
    assert np.array_equal(fitted_scaler.min_, drop_features(scaler.min_[None, :], dropped)[0])
    return pipeline.named_steps["forest"], [class_counts(train)], timings


def fit_model(
    name: str, train: pd.DataFrame, scaler: MinMaxScaler, seed: int, dropped: list[str]
) -> tuple[StackingClassifier | RandomForestClassifier, list[list[int]], dict, dict]:
    """Ajusta o modelo `name` de `ROBUSTNESS_MODELS` sem os atributos `dropped`.

    Devolve o modelo, as amostras por classe de cada conjunto de ajuste, a
    configuração gravada em run.json e os tempos.
    """
    if name == MODIFIED_SELECTED_MODEL:
        model, fit_rows, timings = fit_modification(train, scaler, seed, dropped)
        forest = model
        config = e8.modification_config(name, model)
        config["hyperparameter_search"] = (
            "nenhuma nesta execução: combinação escolhida pela seleção já gravada, no treino "
            "da mesma seed e com os 29 atributos"
        )
    else:
        max_depth = CORRIGIDA_MODELS[name]["max_depth"]
        model, fit_rows, timings = fit_original(train, scaler, seed, max_depth, dropped)
        forest = model.clfs_[0]
        config = e4.run_config(name, model, seed)
    config["dropped_features"] = dropped
    config["n_features"] = forest.n_features_in_
    # Com menos colunas que os atributos por divisão pedidos, toda divisão
    # examina todas as colunas: o valor gravado é o que a árvore de fato usa.
    config["features_examined_per_split"] = min(
        forest.estimators_[0].max_features_, forest.n_features_in_
    )
    return model, fit_rows, config, timings


def perturbation_summary(scaler: MinMaxScaler, fragmented: pd.DataFrame) -> dict:
    """Descreve os fluxos Malicious-DoH do teste depois da fragmentação.

    `fragmented` é o teste já perturbado e `scaler` o normalizador do treino.
    Devolve o número de fluxos, a mediana da duração, quantos valores e linhas
    caem fora da faixa do treino e quantos vetores ficam com tempo médio de
    pacote maior que a duração.
    """
    malicious = fragmented[fragmented["label"] == MALICIOUS]
    outside = outside_unit_interval(scaler.transform(feature_matrix(malicious)))
    # O extrator mede o tempo de cada pacote desde o início do fluxo: em um
    # fluxo real a média não passa da duração. Como as estatísticas por pacote
    # não são recalculadas, o vetor perturbado pode violar isso.
    incoherent = int((malicious["PacketTimeMean"] > malicious["Duration"]).sum())
    return {
        "rows": len(malicious),
        "median_duration_seconds": float(malicious["Duration"].median()),
        "outside_train_range": {**outside, "row_fraction": outside["rows"] / len(malicious)},
        "packet_time_mean_above_duration": {
            "rows": incoherent,
            "row_fraction": incoherent / len(malicious),
        },
    }


def malicious_predictions(predicted: np.ndarray) -> dict:
    """Resume as predições de fluxos que são todos Malicious-DoH.

    Devolve o número de fluxos, os detectados, o recall e, em `predicted_as`,
    quantos fluxos foram para cada classe, pelo nome.
    """
    counts = np.bincount(predicted, minlength=len(CLASS_NAMES))
    return {
        "n": len(predicted),
        "detected": int(counts[MALICIOUS]),
        "recall": float(counts[MALICIOUS] / len(predicted)),
        "predicted_as": dict(zip(CLASS_NAMES, counts.tolist(), strict=True)),
    }


def model_metrics(
    model: StackingClassifier | RandomForestClassifier,
    dropped: list[str],
    y_test: np.ndarray,
    X_by_factor: dict[int, np.ndarray],
    perturbation: dict[int, dict],
) -> dict:
    """Avalia um modelo no teste sem perturbação e em cada fator de fragmentação.

    `X_by_factor[k]` é o teste com os maliciosos fragmentados pelo fator `k`,
    já normalizado, com os 29 atributos. Devolve a avaliação completa do teste
    sem perturbação (`test`) e, por fator, as predições dos fluxos
    Malicious-DoH e a descrição da perturbação (`fragmentation`).
    """
    X_test = drop_features(X_by_factor[1], dropped)
    predicted = model.predict(X_test)
    proba = model.predict_proba(X_test)
    base_mean = None
    if isinstance(model, StackingClassifier):
        base_mean = np.mean([forest.predict_proba(X_test) for forest in model.clfs_], axis=0)

    malicious = y_test == MALICIOUS
    fragmentation = {}
    for factor, X in X_by_factor.items():
        # Só os fluxos maliciosos mudam com o fator: as predições das outras
        # duas classes são as do teste sem perturbação.
        fragmentation[str(factor)] = {
            "malicious": malicious_predictions(model.predict(drop_features(X[malicious], dropped))),
            "perturbation": perturbation[factor],
        }
    clean = evaluate(y_test, predicted, proba, base_mean)
    # O fator 1 é o teste sem perturbação: o recall é o da avaliação completa.
    assert (
        fragmentation["1"]["malicious"]["detected"]
        == clean["confusion_matrix"][MALICIOUS][MALICIOUS]
    )
    return {"test": clean, "fragmentation": fragmentation}


def run_seed(
    table: pd.DataFrame,
    seed: int,
    pending: list[tuple[str, str]],
    data_sha256: str,
    results_dir: Path,
) -> None:
    """Ajusta, avalia e grava, na seed dada, os pares de modelo e colunas de `pending`."""
    # O teste é separado antes de qualquer ajuste. O split é feito uma vez por
    # seed: todos os modelos recebem o mesmo treino e o mesmo teste.
    train, test = stratified_split(table, seed)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."
    split = {"train": e4.index_sha256(train), "test": e4.index_sha256(test)}
    # O normalizador é ajustado só no treino, sem perturbação. A fragmentação é
    # aplicada ao teste, e o teste perturbado só é transformado e predito.
    scaler = fit_scaler(train)
    y_test = test["label"].to_numpy()
    X_by_factor, perturbation = {}, {}
    for factor in FRAGMENTATION_FACTORS:
        fragmented = fragment_malicious(test, factor)
        assert fragmented.loc[y_test != MALICIOUS, FRAGMENTED_COLUMNS].equals(
            test.loc[y_test != MALICIOUS, FRAGMENTED_COLUMNS].astype(float)
        ), "Fluxo de outra classe alterado pela fragmentação."
        X_by_factor[factor] = scaler.transform(feature_matrix(fragmented))
        perturbation[factor] = perturbation_summary(scaler, fragmented)
    assert np.array_equal(X_by_factor[1], scaler.transform(feature_matrix(test)))

    for name, columns in pending:
        dropped = ROBUSTNESS_COLUMN_SETS[columns]
        reference = reference_metrics(name, seed)
        # A comparação entre modelos só vale se todos forem ajustados e
        # avaliados nas mesmas linhas das execuções já gravadas.
        assert reference["split_index_sha256"] == split, f"{name}, seed {seed}: outro split."
        start = time.perf_counter()
        model, fit_rows, config, timings = fit_model(name, train, scaler, seed, dropped)
        evaluation_start = time.perf_counter()
        metrics = {
            "classes": CLASS_NAMES,
            "train_rows": class_counts(train),
            "test_rows": class_counts(test),
            "split_index_sha256": split,
            "fit_rows": fit_rows,
            "dropped_features": dropped,
            "n_features": config["n_features"],
            **model_metrics(model, dropped, y_test, X_by_factor, perturbation),
        }
        if not dropped:
            # Com todos os atributos o modelo é o que já foi medido.
            assert metrics["test"]["confusion_matrix"] == reference["test"]["confusion_matrix"], (
                f"{name}, seed {seed}: matriz diferente da execução já gravada."
            )
        timings["evaluation_seconds"] = round(time.perf_counter() - evaluation_start, 1)
        timings["total_seconds"] = round(time.perf_counter() - start, 1)
        config["columns"] = columns
        config["dataset"] = "cira"
        config["fragmentation_factors"] = FRAGMENTATION_FACTORS
        config["fragmented_columns"] = FRAGMENTED_COLUMNS
        slice_name = SLICE_NAME.format(model=name, columns=columns)
        save_run(
            EXPERIMENT, TRACK, slice_name, seed, metrics, config, data_sha256, timings, results_dir
        )
        print(f"seed {seed}, {name}, {columns}: {timings}", flush=True)


def run_experiment(
    table: pd.DataFrame, data_sha256: str, results_dir: Path, seeds: list[int], models: list[str]
) -> None:
    """Roda os modelos `models` em cada seed e conjunto de colunas e grava cada execução.

    `table` tem os atributos do modelo e `label`. A execução já gravada em
    `results_dir` pelo commit atual, com a árvore limpa, é pulada.
    """
    commit, _ = git_state(PROJECT_ROOT)
    track_dir = results_dir / EXPERIMENT / TRACK
    for seed in seeds:
        pending = [
            (name, columns)
            for name in models
            for columns in ROBUSTNESS_COLUMN_SETS
            if not e8.already_run(
                track_dir / SLICE_NAME.format(model=name, columns=columns) / f"seed{seed}", commit
            )
        ]
        if not pending:
            print(f"seed {seed}: já gravada por este commit", flush=True)
            continue
        run_seed(table, seed, pending, data_sha256, results_dir)


def main() -> None:
    """Confere os dados, roda as seeds e grava cada execução."""
    recorded = json.loads((e4.E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != recorded["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )
    table = pd.read_parquet(CIRA_PARQUET_PATH)
    for rate, total in RATE_OF_BYTES.items():
        # A fragmentação mantém as taxas porque elas são os bytes divididos
        # pela duração. Se a tabela não confirmar a relação, a perturbação
        # deixa de ser coerente e o script para.
        assert np.allclose(table[rate], table[total] / table["Duration"], rtol=1e-9, atol=0), (
            f"{rate} não é {total} dividido por Duration."
        )

    run_experiment(table, data_sha256, RESULTS_DIR, SEEDS_CORRIGIDA, ROBUSTNESS_MODELS)

    track_dir = RESULTS_DIR / EXPERIMENT / TRACK
    print(f"Resultados em {track_dir.relative_to(PROJECT_ROOT)}")
    print("Agregação e resumo: uv run python -m scripts.e8_robustez_resumo")


if __name__ == "__main__":
    main()
