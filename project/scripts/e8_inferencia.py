"""E8: tempo de inferência do sistema do artigo e da modificação, em dez seeds.

O artigo limita as árvores dos Random Forests a profundidade 5 para manter o
cálculo rápido na predição (Seção IV-B) e não mede esse tempo; a modificação
usa 100 árvores sem limite de profundidade. Este script mede, em cada modelo de
`INFERENCE_MODELS`, o tempo de normalizar e predizer, com um núcleo:

- em lote: o teste inteiro de uma vez, `INFERENCE_BATCH_REPEATS` vezes, depois
  de uma predição de aquecimento;
- fluxo a fluxo: `INFERENCE_SINGLE_FLOWS` fluxos do teste, sorteados com a
  seed, um por chamada.

Ao lado do tempo, que depende da máquina, grava uma medida determinística do
custo: os nós de árvore percorridos por fluxo no teste, somados em todas as
árvores dos Random Forests.

Cada modelo é ajustado de novo nas mesmas seeds e nos mesmos splits das
execuções já gravadas por scripts/e4_corrigido.py e scripts/e8_modificacao.py,
e o script confere que a matriz de confusão no teste é a gravada. M1M2 usa os
hiperparâmetros que a seleção gravada escolheu no treino da mesma seed; a
seleção não é refeita.

Lê data/processed/cira.parquet e data/processed/combinado_sem_replicas.parquet.
Grava metrics.json (só valores determinísticos) e run.json (os tempos) em
results/e8/corrigida/inferencia-<dados>/seed<k>/. A execução já gravada pelo
mesmo commit, com a árvore limpa, não é refeita. A agregação e a leitura dos
números são feitas por scripts/e8_inferencia_resumo.py, sem treinar.

Roda como módulo, a partir da pasta do projeto, porque importa outros scripts.

Uso: uv run python -m scripts.e8_inferencia
"""

import gc
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler

import scripts.e4_corrigido as e4
import scripts.e6_dataset2 as e6
import scripts.e8_modificacao as e8
from doh_ids.config import (
    CLASS_NAMES,
    CORRIGIDA_MODELS,
    INFERENCE_BATCH_REPEATS,
    INFERENCE_MODELS,
    INFERENCE_SINGLE_FLOWS,
    MODIFIED_MODELS,
    MODIFIED_SELECTED_MODEL,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEEDS_CORRIGIDA,
)
from doh_ids.data import class_counts, feature_matrix
from doh_ids.models import fit_modified_forest
from doh_ids.runlog import git_state, save_run
from doh_ids.splits import stratified_split

EXPERIMENT = e8.EXPERIMENT
TRACK = e8.TRACK
SLICE_NAME = "inferencia-{dataset}"
# Predições de fluxo único feitas antes da medição, para que a primeira chamada
# de cada modelo, mais lenta, não entre na mediana.
SINGLE_WARMUP = 10

Model = StackingClassifier | RandomForestClassifier


def reference_metrics(dataset: str, name: str, seed: int) -> dict:
    """Lê o metrics.json já gravado do modelo `name` no conjunto `dataset`, na seed dada."""
    if dataset == "cira" and name in CORRIGIDA_MODELS:
        run_dir = e8.E4_DIR / name
    else:
        run_dir = RESULTS_DIR / EXPERIMENT / TRACK / f"{name}-{dataset}"
    return json.loads((run_dir / f"seed{seed}" / "metrics.json").read_text(encoding="utf-8"))


def fit_model(
    dataset: str, name: str, train: pd.DataFrame, seed: int
) -> tuple[MinMaxScaler, Model, dict]:
    """Ajusta `name` só com `train`; devolve o normalizador, o modelo e a configuração."""
    if name in CORRIGIDA_MODELS:
        scaler, model, _, _ = e4.fit_model(name, train, seed, None)
        return scaler, model, {"max_depth": CORRIGIDA_MODELS[name]["max_depth"]}
    if name == MODIFIED_SELECTED_MODEL:
        combination = reference_metrics(dataset, name, seed)["selection"]["selected"]
    else:
        combination = MODIFIED_MODELS[name]
    pipeline = fit_modified_forest(
        feature_matrix(train), train["label"].to_numpy(), seed, **combination
    )
    return pipeline.named_steps["scaler"], pipeline.named_steps["forest"], combination


def forests_of(model: Model) -> list[RandomForestClassifier]:
    """Devolve os Random Forests do modelo: os três bases do empilhado ou o único."""
    return list(model.clfs_) if isinstance(model, StackingClassifier) else [model]


def tree_cost(model: Model, X: np.ndarray) -> dict:
    """Conta as árvores, os nós e os nós percorridos por fluxo de `X`, já normalizado."""
    trees = [tree for forest in forests_of(model) for tree in forest.estimators_]
    # Cada fluxo percorre, em cada árvore, um caminho da raiz até uma folha: o
    # número de nós desse caminho é o número de comparações que a predição faz.
    visited = sum(tree.decision_path(X).nnz for tree in trees)
    return {
        "trees": len(trees),
        "nodes": int(sum(tree.tree_.node_count for tree in trees)),
        "nodes_per_flow": visited / len(X),
    }


def rotated(names: list[str], shift: int) -> list[str]:
    """Gira a ordem dos modelos, para que nenhum seja sempre o primeiro a ser medido."""
    shift %= len(names)
    return names[shift:] + names[:shift]


def time_batch(fitted: dict, X_raw: pd.DataFrame) -> dict:
    """Mede, em segundos, cada repetição de normalizar e predizer `X_raw` inteiro."""
    names = list(fitted)
    seconds = {name: [] for name in names}
    for repeat in range(INFERENCE_BATCH_REPEATS):
        for name in rotated(names, repeat):
            scaler, model = fitted[name]
            start = time.perf_counter()
            model.predict(scaler.transform(X_raw))
            seconds[name].append(time.perf_counter() - start)
    return seconds


def time_single(fitted: dict, rows: list[pd.DataFrame]) -> tuple[dict, dict]:
    """Mede, em segundos, a predição de cada fluxo de `rows`, um por chamada.

    Devolve os tempos e os rótulos preditos por modelo, na ordem de `rows`.
    """
    names = list(fitted)
    for name in names:
        scaler, model = fitted[name]
        for row in rows[:SINGLE_WARMUP]:
            model.predict(scaler.transform(row))
    seconds = {name: [] for name in names}
    predicted = {name: [] for name in names}
    for index, row in enumerate(rows):
        for name in rotated(names, index):
            scaler, model = fitted[name]
            start = time.perf_counter()
            label = model.predict(scaler.transform(row))
            seconds[name].append(time.perf_counter() - start)
            predicted[name].append(int(label[0]))
    return seconds, predicted


def measure(fitted: dict, test: pd.DataFrame, seed: int) -> tuple[dict, dict]:
    """Mede os dois regimes e confere as predições; devolve as métricas e os tempos."""
    X_raw = feature_matrix(test)
    y_test = test["label"].to_numpy()
    sample = np.random.default_rng(seed).choice(len(test), INFERENCE_SINGLE_FLOWS, replace=False)
    rows = [X_raw.iloc[[position]] for position in sample]

    metrics, batch_predicted = {}, {}
    for name, (scaler, model) in fitted.items():
        # Predição de aquecimento: também dá os rótulos conferidos abaixo.
        batch_predicted[name] = model.predict(scaler.transform(X_raw))
        metrics[name] = {
            **tree_cost(model, scaler.transform(X_raw)),
            "confusion_matrix": confusion_matrix(
                y_test, batch_predicted[name], labels=range(len(CLASS_NAMES))
            ).tolist(),
        }

    # O coletor de lixo pararia a medição em momento arbitrário; ele é
    # desligado durante as medidas, como faz o módulo timeit da biblioteca padrão.
    gc.collect()
    gc.disable()
    batch_seconds = time_batch(fitted, X_raw)
    single_seconds, single_predicted = time_single(fitted, rows)
    gc.enable()

    timings = {}
    for name in fitted:
        # Um fluxo predito sozinho tem de receber o mesmo rótulo que no lote.
        assert np.array_equal(single_predicted[name], batch_predicted[name][sample]), (
            f"{name}: predição de um fluxo diferente da predição em lote."
        )
        timings[name] = {
            "batch_seconds": batch_seconds[name],
            "single_median_seconds": float(np.median(single_seconds[name])),
            "single_p95_seconds": float(np.percentile(single_seconds[name], 95)),
        }
    sampled = {"rows": INFERENCE_SINGLE_FLOWS, "by_class": class_counts(test.iloc[sample])}
    return {"models": metrics, "single_flow_sample": sampled}, timings


def run_seed(dataset: str, table: pd.DataFrame, seed: int) -> tuple[dict, dict, dict]:
    """Ajusta e mede os modelos na seed dada; devolve métricas, configuração e tempos."""
    # O teste é separado antes de qualquer ajuste, uma vez por seed: todos os
    # modelos recebem o mesmo treino, e o teste só é normalizado e predito.
    train, test = stratified_split(table, seed)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."
    split = {"train": e4.index_sha256(train), "test": e4.index_sha256(test)}

    fitted, config, fit_seconds = {}, {}, {}
    for name in INFERENCE_MODELS[dataset]:
        reference = reference_metrics(dataset, name, seed)
        assert reference["split_index_sha256"] == split, f"{name}, seed {seed}: outro split."
        start = time.perf_counter()
        scaler, model, config[name] = fit_model(dataset, name, train, seed)
        fit_seconds[name] = round(time.perf_counter() - start, 1)
        fitted[name] = (scaler, model)

    measured, timings = measure(fitted, test, seed)
    for name in fitted:
        # O tempo só descreve o modelo já avaliado se o modelo for o mesmo.
        assert (
            measured["models"][name]["confusion_matrix"]
            == reference_metrics(dataset, name, seed)["test"]["confusion_matrix"]
        ), f"{name}, seed {seed}: matriz diferente da execução já gravada."
        timings[name]["fit_seconds"] = fit_seconds[name]

    metrics = {
        "classes": CLASS_NAMES,
        "test_rows": class_counts(test),
        "split_index_sha256": split,
        **measured,
    }
    config = {
        "dataset": dataset,
        "models": config,
        "batch_repeats": INFERENCE_BATCH_REPEATS,
        "single_flows": INFERENCE_SINGLE_FLOWS,
        "predict_n_jobs": 1,
    }
    return metrics, config, timings


def run_dataset(
    dataset: str, table: pd.DataFrame, data_sha256: str, results_dir: Path, seeds: list[int]
) -> None:
    """Roda as seeds de um conjunto de dados e grava cada execução, pulando as já gravadas."""
    commit, _ = git_state(PROJECT_ROOT)
    slice_name = SLICE_NAME.format(dataset=dataset)
    for seed in seeds:
        run_dir = results_dir / EXPERIMENT / TRACK / slice_name / f"seed{seed}"
        if e8.already_run(run_dir, commit):
            print(f"{dataset}, seed {seed}: já gravada por este commit", flush=True)
            continue
        metrics, config, timings = run_seed(dataset, table, seed)
        save_run(
            EXPERIMENT, TRACK, slice_name, seed, metrics, config, data_sha256, timings, results_dir
        )
        medians = {
            name: round(float(np.median(t["batch_seconds"])), 3) for name, t in timings.items()
        }
        print(f"{dataset}, seed {seed}: lote, mediana em segundos {medians}", flush=True)


def main() -> None:
    """Confere os dados, roda as seeds nos dois conjuntos e grava cada execução."""
    sha256 = e6.checked_sha256()
    for dataset, path in e8.DATASET_PATHS.items():
        table = pd.read_parquet(path)
        run_dataset(dataset, table, sha256[dataset], RESULTS_DIR, SEEDS_CORRIGIDA)
    track_dir = RESULTS_DIR / EXPERIMENT / TRACK
    print(f"Resultados em {track_dir.relative_to(PROJECT_ROOT)}/inferencia-*")
    print("Agregação e resumo: uv run python -m scripts.e8_inferencia_resumo")


if __name__ == "__main__":
    main()
