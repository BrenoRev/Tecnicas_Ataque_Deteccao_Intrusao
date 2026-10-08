"""E8: a modificação proposta pela equipe, ao lado do sistema do artigo, em dez seeds.

A modificação troca o sistema empilhado do artigo (três Random Forests em
subconjuntos balanceados com SMOTE e um meta-classificador) por um Random
Forest único, sem SMOTE, com peso de classe e o normalizador dentro de um
`Pipeline`. Os modelos, a grade e os pares comparados estão em `config.py`,
fixados antes da primeira execução:

- M1 e M1-prof5: o Random Forest único com os hiperparâmetros dos bases de A e
  de A-prof5;
- M1M2: o mesmo, com os hiperparâmetros escolhidos em `MODIFIED_GRID` por
  validação cruzada de 5 folds em uma subamostra estratificada do treino da
  seed. O teste não participa da escolha.

Dois conjuntos de dados, dez seeds cada, com o split 90/10 estratificado
refeito em cada seed:

- data/processed/cira.parquet: M1, M1-prof5 e M1M2. A e A-prof5 não são
  ajustados de novo: foram medidos nas mesmas seeds e nos mesmos splits por
  scripts/e4_corrigido.py, e o script confere a igualdade dos splits. M1M2
  também prediz os fluxos de data/processed/hkd.parquet, que não entram em
  nenhum ajuste;
- data/processed/combinado_sem_replicas.parquet: A e M1M2, com o recall de
  Malicious-DoH por ferramenta de túnel.

Grava metrics.json e run.json em results/e8/corrigida/<modelo>-<dados>/seed<k>/,
uma execução por vez. A execução que já está gravada pelo mesmo commit, com a
árvore limpa, não é refeita: o script pode ser interrompido e retomado. A
agregação (summary.json) e a leitura dos números (RESUMO.md) são feitas por
scripts/e8_resumo.py, a partir desses arquivos e sem treinar.

Roda como módulo, a partir da pasta do projeto, porque importa outros scripts.

Uso: uv run python -m scripts.e8_modificacao
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

import scripts.e4_corrigido as e4
import scripts.e6_dataset2 as e6
from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    COMBINED_UNIQUE_PARQUET_PATH,
    CORRIGIDA_MODELS,
    HKD_PARQUET_PATH,
    MODIFIED_CV_FOLDS,
    MODIFIED_GRID,
    MODIFIED_MODELS,
    MODIFIED_RUNS,
    MODIFIED_SELECTED_MODEL,
    MODIFIED_SELECTION_FRACTION,
    N_JOBS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEEDS_CORRIGIDA,
    TEST_SIZE,
)
from doh_ids.data import class_counts, feature_matrix
from doh_ids.evaluate import malicious_only_metrics, recall_by_tool
from doh_ids.models import fit_modified_forest
from doh_ids.runlog import git_state, save_run
from doh_ids.splits import seen_in_train, stratified_split

EXPERIMENT = "e8"
TRACK = "corrigida"
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")

# Resultados do protocolo corrigido no CIRA, de onde vêm A e A-prof5.
E4_DIR = RESULTS_DIR / e4.EXPERIMENT / e4.TRACK

# Tabela de cada conjunto de dados de `MODIFIED_RUNS`.
DATASET_PATHS = {
    "cira": CIRA_PARQUET_PATH,
    "combinado_sem_replicas": COMBINED_UNIQUE_PARQUET_PATH,
}


def selection_sample(train: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Sorteia do treino a subamostra estratificada em que os hiperparâmetros são escolhidos."""
    sample, _ = train_test_split(
        train,
        train_size=MODIFIED_SELECTION_FRACTION,
        stratify=train["label"],
        random_state=seed,
    )
    return sample


def select_hyperparameters(sample: pd.DataFrame, seed: int) -> tuple[dict, list[dict]]:
    """Escolhe em `MODIFIED_GRID` a combinação de maior F1 macro médio na validação cruzada.

    `sample` são linhas do treino. Devolve a combinação escolhida e, para cada
    combinação da grade, o F1 macro de cada fold e a média.
    """
    X, y = feature_matrix(sample), sample["label"].to_numpy()
    folds = StratifiedKFold(n_splits=MODIFIED_CV_FOLDS, shuffle=True, random_state=seed)
    # Os folds são sorteados uma vez: todas as combinações são avaliadas nas
    # mesmas linhas.
    fold_rows = list(folds.split(X, y))
    scores = []
    for combination in MODIFIED_GRID:
        fold_scores = []
        for fit_rows, validation_rows in fold_rows:
            # O Pipeline é ajustado de novo em cada fold: o normalizador só vê
            # as linhas de ajuste, e o fold de validação só é transformado e predito.
            model = fit_modified_forest(X.iloc[fit_rows], y[fit_rows], seed, **combination)
            predicted = model.predict(X.iloc[validation_rows])
            # Classe que o modelo não prediz no fold entra com F1 zero, a mesma
            # convenção da avaliação final.
            score = f1_score(y[validation_rows], predicted, average="macro", zero_division=0)
            fold_scores.append(float(score))
        scores.append(
            {
                **combination,
                "fold_macro_f1": fold_scores,
                "mean_macro_f1": float(np.mean(fold_scores)),
            }
        )
    # No empate, `argmax` devolve a primeira: a combinação que vem antes na grade.
    best = int(np.argmax([entry["mean_macro_f1"] for entry in scores]))
    return MODIFIED_GRID[best], scores


def fit_modification(
    name: str, train: pd.DataFrame, seed: int
) -> tuple[Pipeline, dict | None, dict]:
    """Ajusta, só com `train`, o modelo modificado `name`.

    `name` é uma chave de `MODIFIED_MODELS` ou `MODIFIED_SELECTED_MODEL`; neste
    caso os hiperparâmetros são escolhidos antes, em uma subamostra de `train`.
    Devolve o `Pipeline` ajustado no treino inteiro, o registro da seleção
    (`None` nos modelos de hiperparâmetros fixos) e os tempos, em segundos.
    """
    selection, timings = None, {}
    if name == MODIFIED_SELECTED_MODEL:
        start = time.perf_counter()
        sample = selection_sample(train, seed)
        assert sample.index.isin(train.index).all(), "Linha de fora do treino na seleção."
        combination, scores = select_hyperparameters(sample, seed)
        selection = {
            "sample_rows": class_counts(sample),
            "folds": MODIFIED_CV_FOLDS,
            "scores": scores,
            "selected": combination,
        }
        timings["selection_seconds"] = round(time.perf_counter() - start, 1)
    else:
        combination = MODIFIED_MODELS[name]

    start = time.perf_counter()
    model = fit_modified_forest(
        feature_matrix(train), train["label"].to_numpy(), seed, **combination
    )
    timings["fit_seconds"] = round(time.perf_counter() - start, 1)
    # Sem SMOTE e sem subconjuntos: o modelo foi ajustado em exatamente as
    # linhas reais do treino.
    assert model.named_steps["scaler"].n_samples_seen_ == len(train), "Treino de outro tamanho."
    forest = model.named_steps["forest"]
    fitted = {key: getattr(forest, key) for key in combination}
    assert fitted == combination, f"{name}: modelo fora da configuração."
    return model, selection, timings


def modification_config(name: str, forest: RandomForestClassifier) -> dict:
    """Monta a configuração gravada em run.json de um modelo modificado já ajustado."""
    search = "nenhuma: configuração fixada antes da execução"
    if name == MODIFIED_SELECTED_MODEL:
        search = (
            f"validação cruzada estratificada de {MODIFIED_CV_FOLDS} folds em subamostra "
            f"estratificada de {MODIFIED_SELECTION_FRACTION:.0%} do treino da seed; F1 macro "
            f"médio; grade de {len(MODIFIED_GRID)} combinações (MODIFIED_GRID); ajuste final "
            "no treino inteiro"
        )
    return {
        "model": name,
        "stacked": False,
        "n_estimators": forest.n_estimators,
        "max_depth": forest.max_depth,
        "max_features": forest.max_features,
        "criterion": forest.criterion,
        "class_weight": forest.class_weight,
        "n_base_models": 1,
        "balancing": "peso de classe no Random Forest; sem SMOTE e sem subconjuntos",
        "scaler": "MinMaxScaler como primeiro passo do Pipeline, ajustado com o Random Forest",
        "hyperparameter_search": search,
        "test_size": TEST_SIZE,
        "n_jobs": N_JOBS,
    }


def split_metrics(
    scaler: MinMaxScaler,
    model: StackingClassifier | RandomForestClassifier,
    fit_rows: list[list[int]],
    train: pd.DataFrame,
    test: pd.DataFrame,
    seen: np.ndarray,
) -> dict:
    """Monta o metrics.json de um modelo ajustado: contagens, resumo do split e avaliação.

    `fit_rows` são as amostras por classe de cada conjunto em que um Random
    Forest foi ajustado e `seen` marca as linhas de `test` cujo vetor de
    atributos existe em `train`. Se `test` traz a ferramenta de túnel, entra o
    recall de Malicious-DoH por ferramenta.
    """
    seen_by_class = np.bincount(test["label"].to_numpy()[seen], minlength=len(CLASS_NAMES))
    metrics = {
        "classes": CLASS_NAMES,
        "train_rows": class_counts(train),
        "test_rows": class_counts(test),
        # Modelos com o mesmo resumo dos índices foram ajustados nas mesmas
        # linhas de treino e avaliados nas mesmas linhas de teste.
        "split_index_sha256": {"train": e4.index_sha256(train), "test": e4.index_sha256(test)},
        "fit_rows": fit_rows,
        "test_seen_in_train": {
            "rows": int(seen.sum()),
            "fraction": float(seen.mean()),
            "by_class": seen_by_class.tolist(),
        },
        **e4.model_metrics(scaler, model, test, seen),
    }
    if "tool" in test.columns:
        predicted = model.predict(scaler.transform(feature_matrix(test)))
        metrics["test_recall_by_tool"] = recall_by_tool(test["tool"], predicted)
    return metrics


def run_model(
    name: str, train: pd.DataFrame, test: pd.DataFrame, seed: int, hkd: pd.DataFrame | None
) -> tuple[dict, dict, dict]:
    """Ajusta o modelo `name` em `train` e o avalia em `test`.

    `name` é A, um modelo de `MODIFIED_MODELS` ou `MODIFIED_SELECTED_MODEL`.
    Com `hkd`, o modelo selecionado também prediz esses fluxos, todos
    Malicious-DoH e de fora do treino. Devolve o dicionário de metrics.json, a
    configuração e os tempos gravados em run.json.
    """
    start = time.perf_counter()
    seen = seen_in_train(train, test)
    selection = None
    if name in CORRIGIDA_MODELS:
        scaler, model, fit_rows, timings = e4.fit_model(name, train, seed, None)
        config = e4.run_config(name, model, seed)
    else:
        pipeline, selection, timings = fit_modification(name, train, seed)
        scaler, model = pipeline.named_steps["scaler"], pipeline.named_steps["forest"]
        fit_rows = [class_counts(train)]
        config = modification_config(name, model)

    evaluation_start = time.perf_counter()
    metrics = split_metrics(scaler, model, fit_rows, train, test, seen)
    if selection is not None:
        metrics["selection"] = selection
        if hkd is not None:
            # O normalizador é o do treino: o HKD só é transformado e predito.
            predicted = model.predict(scaler.transform(feature_matrix(hkd)))
            metrics["hkd_transfer"] = malicious_only_metrics(hkd["tool"], predicted)
    timings["evaluation_seconds"] = round(time.perf_counter() - evaluation_start, 1)
    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    return metrics, config, timings


def already_run(run_dir: Path, commit: str | None) -> bool:
    """Diz se a execução de `run_dir` já foi gravada pelo commit atual, com a árvore limpa."""
    run_file = run_dir / "run.json"
    if not run_file.exists() or not (run_dir / "metrics.json").exists():
        return False
    run = json.loads(run_file.read_text(encoding="utf-8"))
    return run["commit"] == commit and not run["dirty"]


def run_dataset(
    dataset: str,
    table: pd.DataFrame,
    sha256: dict,
    results_dir: Path,
    seeds: list[int],
    hkd: pd.DataFrame | None = None,
) -> None:
    """Roda os modelos de `MODIFIED_RUNS[dataset]` em cada seed e grava cada execução.

    `table` tem os atributos do modelo e `label`; `sha256` leva o nome de cada
    tabela ao hash dela. `hkd`, quando dado, são os fluxos do HKD que o modelo
    selecionado prediz depois de ajustado em `table`.
    """
    commit, _ = git_state(PROJECT_ROOT)
    for seed in seeds:
        slices = {name: f"{name}-{dataset}" for name in MODIFIED_RUNS[dataset]}
        pending = [
            name
            for name, slice_name in slices.items()
            if not already_run(
                results_dir / EXPERIMENT / TRACK / slice_name / f"seed{seed}", commit
            )
        ]
        if not pending:
            print(f"{dataset}, seed {seed}: já gravada por este commit", flush=True)
            continue
        # O teste é separado antes de qualquer ajuste. O split é feito uma vez
        # por seed: todos os modelos da seed recebem o mesmo treino e o mesmo
        # teste, e a seleção de hiperparâmetros só recebe o treino.
        train, test = stratified_split(table, seed)
        assert train.index.intersection(test.index).empty, "Linha no treino e no teste."
        for name in pending:
            metrics, config, timings = run_model(name, train, test, seed, hkd)
            assert metrics["test"]["total"] == len(test)
            config["dataset"] = dataset
            if "hkd_transfer" in metrics:
                config["evaluated_data_sha256"] = sha256["hkd"]
            save_run(
                EXPERIMENT,
                TRACK,
                slices[name],
                seed,
                metrics,
                config,
                sha256[dataset],
                timings,
                results_dir,
            )
            print(f"{dataset}, seed {seed}, {name}: {timings}", flush=True)


def assert_splits_of_e4(table: pd.DataFrame, seeds: list[int]) -> None:
    """Confere que o split de cada seed é o das execuções gravadas do protocolo corrigido."""
    for seed in seeds:
        train, test = stratified_split(table, seed)
        split = {"train": e4.index_sha256(train), "test": e4.index_sha256(test)}
        for name in ("A", "A-prof5"):
            metrics_file = E4_DIR / name / f"seed{seed}" / "metrics.json"
            recorded = json.loads(metrics_file.read_text(encoding="utf-8"))
            # A comparação pareada com A só vale se a modificação for ajustada
            # e avaliada nas mesmas linhas em que A foi.
            assert recorded["split_index_sha256"] == split, f"{name}, seed {seed}: outro split."


def main() -> None:
    """Confere os dados, roda as seeds nos dois conjuntos e grava cada execução."""
    sha256 = e6.checked_sha256()
    hkd = pd.read_parquet(HKD_PARQUET_PATH)
    assert (hkd["label"] == MALICIOUS).all(), "O HKD só tem fluxos de túnel."

    for dataset, path in DATASET_PATHS.items():
        table = pd.read_parquet(path)
        if dataset == "cira":
            assert_splits_of_e4(table, SEEDS_CORRIGIDA)
            run_dataset(dataset, table, sha256, RESULTS_DIR, SEEDS_CORRIGIDA, hkd)
        else:
            assert (table.loc[table["tool"].notna(), "label"] == MALICIOUS).all(), (
                "Ferramenta de túnel em fluxo que não é Malicious-DoH."
            )
            run_dataset(dataset, table, sha256, RESULTS_DIR, SEEDS_CORRIGIDA)

    track_dir = RESULTS_DIR / EXPERIMENT / TRACK
    for run_file in sorted(track_dir.glob("*/seed*/run.json")):
        run = json.loads(run_file.read_text(encoding="utf-8"))
        assert run["track"] == TRACK, f"{run_file}: trilha {run['track']}."
    print(f"Resultados em {track_dir.relative_to(PROJECT_ROOT)}")
    print("Agregação e resumo: uv run python -m scripts.e8_resumo")


if __name__ == "__main__":
    main()
