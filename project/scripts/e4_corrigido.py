"""E4: protocolo corrigido, com variância em dez seeds e comparação pareada entre modelos.

O artigo sustenta a vantagem do modelo proposto com uma execução e contra um
Random Forest de outros hiperparâmetros (Tabela II). Este script repete a
avaliação em dez seeds, com as configurações fixadas antes em
`config.CORRIGIDA_MODELS` e sem busca de hiperparâmetros:

- A: o sistema empilhado do artigo, com árvores sem limite de profundidade;
- B: um Random Forest único com os mesmos hiperparâmetros de A e SMOTE no
  treino inteiro;
- C: o Random Forest da Tabela II e SMOTE;
- A-prof5 e B-prof5: A e B com profundidade máxima 5, ao lado.

Cada seed refaz o split 90/10 estratificado, o normalizador, os subconjuntos,
o SMOTE e os modelos, e todos os modelos da seed são avaliados no mesmo teste,
inteiro e sem as linhas cujo vetor de atributos existe no treino. Depois das
dez seeds, o modelo A é avaliado deixando máquinas inteiras de fora, em quatro
dobras.

Lê data/processed/cira.parquet. Grava metrics.json e run.json em
results/e4/corrigida/<modelo>/seed<k>/ e em
results/e4/corrigida/A-fold<k>/seed<s>/. Este script só treina, avalia e grava
os arquivos de cada execução: a agregação (summary.json) e a leitura dos
números (RESUMO.md) são feitas por scripts/e4_resumo.py, a partir desses
arquivos e sem retreinar.

Uso: uv run python scripts/e4_corrigido.py
"""

import hashlib
import ipaddress
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    CORRIGIDA_MODELS,
    GROUP_FOLD_SEED,
    GROUP_FOLDS,
    N_JOBS,
    N_SUBSETS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    SEEDS_CORRIGIDA,
    TEST_SIZE,
    smote_seed,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.evaluate import evaluate
from doh_ids.models import base_forests, fit_baseline
from doh_ids.runlog import save_run
from doh_ids.splits import balanced_train, fit_scaler, seen_in_train, stratified_split
from doh_ids.system import fit_system

# Resultados da etapa de dados, com os quais o arquivo lido é conferido.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"

EXPERIMENT = "e4"
TRACK = "corrigida"
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")
# Modelo da avaliação por máquina: o sistema do artigo.
GROUP_FOLD_MODEL = "A"

# Os dois conjuntos em que cada modelo é avaliado: o teste inteiro e o teste
# sem as linhas cujo vetor de atributos existe no treino da mesma seed.
SCOPES = {"test": "teste inteiro", "test_unseen": "teste sem vetores repetidos do treino"}


def index_sha256(flows: pd.DataFrame) -> str:
    """Devolve o SHA-256 do índice das linhas de `flows`, na ordem em que estão."""
    return hashlib.sha256(flows.index.to_numpy().tobytes()).hexdigest()


def fit_model(
    name: str, train: pd.DataFrame, seed: int, balanced: tuple[np.ndarray, np.ndarray] | None
) -> tuple[MinMaxScaler, StackingClassifier | RandomForestClassifier, list[list[int]], dict]:
    """Ajusta, só com `train`, o modelo `name` de `CORRIGIDA_MODELS`.

    `balanced` é o treino normalizado e balanceado com SMOTE, usado pelos
    modelos que não empilham; o empilhado monta os próprios subconjuntos.
    Devolve o normalizador, o modelo, as amostras por classe de cada conjunto
    em que um Random Forest foi ajustado e os tempos, em segundos.
    """
    spec = CORRIGIDA_MODELS[name]
    if spec["stacked"]:
        # O meta-classificador é treinado como na reprodução do artigo, sobre
        # as predições dos bases no treino original. O protocolo corrigido
        # conserta a avaliação, não o desenho do empilhamento.
        scaler, model, subsets, timings = fit_system(train, seed, spec["max_depth"])
        return scaler, model, [entry["class_counts"] for entry in subsets], timings

    start = time.perf_counter()
    if name == "C":
        model = fit_baseline("random_forest", *balanced, seed)
    else:
        # A mesma função que treina os bases do empilhado: os hiperparâmetros
        # de B são os de A por construção. O conjunto de ajuste não é o mesmo:
        # B recebe o treino inteiro balanceado, e cada base de A um subconjunto.
        model = base_forests([balanced], seed, spec["max_depth"])[0]
    timings = {"fit_seconds": round(time.perf_counter() - start, 1)}
    fit_rows = [np.bincount(balanced[1], minlength=len(CLASS_NAMES)).tolist()]
    return fit_scaler(train), model, fit_rows, timings


def model_metrics(
    scaler: MinMaxScaler,
    model: StackingClassifier | RandomForestClassifier,
    test: pd.DataFrame,
    seen: np.ndarray,
) -> dict:
    """Avalia o modelo no teste inteiro e no teste sem os vetores que existem no treino.

    `seen` marca as linhas de `test` cujo vetor de atributos existe no treino.
    Devolve as métricas dos dois conjuntos, nas chaves de `SCOPES`.
    """
    X_test = scaler.transform(feature_matrix(test))
    y_test = test["label"].to_numpy()
    predicted = model.predict(X_test)
    proba = model.predict_proba(X_test)
    # No empilhado, a saída do meta-classificador só tem as combinações de
    # rótulos dos três bases; a média das probabilidades dos bases entra ao
    # lado, para a AUC não medir só essa discretização.
    base_mean = None
    if isinstance(model, StackingClassifier):
        base_mean = np.mean([forest.predict_proba(X_test) for forest in model.clfs_], axis=0)

    full = evaluate(y_test, predicted, proba, base_mean)
    # Amostra sintética só existe nos conjuntos de ajuste: a matriz tem, por
    # classe, exatamente as linhas reais do teste.
    assert [sum(row) for row in full["confusion_matrix"]] == class_counts(test)

    unseen = evaluate(
        y_test[~seen],
        predicted[~seen],
        proba[~seen],
        None if base_mean is None else base_mean[~seen],
    )
    assert unseen["total"] == len(test) - int(seen.sum()), "Filtro de vetores repetidos errado."
    return {"test": full, "test_unseen": unseen}


def run_config(name: str, model: StackingClassifier | RandomForestClassifier, seed: int) -> dict:
    """Monta a configuração gravada em run.json, com os hiperparâmetros do modelo ajustado."""
    spec = CORRIGIDA_MODELS[name]
    forest = model.clfs_[0] if spec["stacked"] else model
    # Os hiperparâmetros são lidos do modelo ajustado e conferidos com a
    # configuração fixada: o registro diz o que foi treinado, não o que foi pedido.
    # A asserção protege a construção de B e de C, que são montados por funções
    # que não recebem as árvores nem os atributos por divisão da configuração.
    fitted = {key: getattr(forest, key) for key in ("n_estimators", "max_depth", "max_features")}
    assert fitted == {key: spec[key] for key in fitted}, f"{name}: modelo fora da configuração."
    depth = spec["max_depth"]
    return {
        "model": name,
        "stacked": spec["stacked"],
        **fitted,
        "criterion": forest.criterion,
        "class_weight": forest.class_weight,
        "depth_reading": (
            "sem limite de profundidade" if depth is None else f"profundidade máxima {depth}"
        ),
        "n_base_models": N_SUBSETS if spec["stacked"] else 1,
        "balancing": (
            "SMOTE em cada subconjunto: Benign-DoH aumentada até o tamanho de Malicious-DoH"
            if spec["stacked"]
            else "SMOTE no treino inteiro: as duas classes menores aumentadas até Non-DoH"
        ),
        "smote_seeds": (
            [smote_seed(seed, index) for index in range(N_SUBSETS)]
            if spec["stacked"]
            else [smote_seed(seed, N_SUBSETS)]
        ),
        "hyperparameter_search": "nenhuma: configuração fixada antes da execução",
        "test_size": TEST_SIZE,
        "n_jobs": N_JOBS,
    }


def evaluate_split(
    names: list[str], train: pd.DataFrame, test: pd.DataFrame, seed: int
) -> tuple[dict, dict]:
    """Ajusta os modelos `names` no mesmo treino e os avalia no mesmo teste.

    Devolve, para cada modelo, o dicionário gravado em metrics.json, e para
    cada modelo o par de configuração e tempos gravado em run.json.
    """
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."
    seen = seen_in_train(train, test)
    seen_by_class = np.bincount(test["label"].to_numpy()[seen], minlength=len(CLASS_NAMES))

    # O SMOTE do treino inteiro só enxerga o treino e é feito uma vez por seed:
    # os Random Forests únicos da mesma seed recebem o mesmo treino balanceado.
    balanced, smote_seconds = None, None
    if any(not CORRIGIDA_MODELS[name]["stacked"] for name in names):
        start = time.perf_counter()
        X_train = fit_scaler(train).transform(feature_matrix(train))
        balanced = balanced_train(X_train, train["label"].to_numpy(), seed)
        smote_seconds = round(time.perf_counter() - start, 1)

    metrics, records = {}, {}
    for name in names:
        start = time.perf_counter()
        scaler, model, fit_rows, timings = fit_model(name, train, seed, balanced)
        evaluation_start = time.perf_counter()
        metrics[name] = {
            "classes": CLASS_NAMES,
            "train_rows": class_counts(train),
            "test_rows": class_counts(test),
            # Resumo das linhas de treino e de teste, pelo índice na tabela:
            # modelos com o mesmo resumo foram avaliados nas mesmas linhas.
            "split_index_sha256": {"train": index_sha256(train), "test": index_sha256(test)},
            "fit_rows": fit_rows,
            "test_seen_in_train": {
                "rows": int(seen.sum()),
                "fraction": float(seen.mean()),
                "by_class": seen_by_class.tolist(),
            },
            **model_metrics(scaler, model, test, seen),
        }
        timings["evaluation_seconds"] = round(time.perf_counter() - evaluation_start, 1)
        timings["total_seconds"] = round(time.perf_counter() - start, 1)
        if not CORRIGIDA_MODELS[name]["stacked"]:
            timings["shared_smote_seconds"] = smote_seconds
        records[name] = (run_config(name, model, seed), timings)
        print(f"seed {seed}, {name}: {timings}", flush=True)
    return metrics, records


def run_experiment(
    table: pd.DataFrame, data_sha256: str, results_dir: Path, seeds: list[int]
) -> dict:
    """Roda todos os modelos de `CORRIGIDA_MODELS` em cada seed e grava cada execução.

    `table` tem os atributos do modelo e `label`. Devolve, para cada modelo, as
    métricas de cada seed: `results[modelo][seed]` é o dicionário de metrics.json.
    """
    names = list(CORRIGIDA_MODELS)
    results = {name: {} for name in names}
    for seed in seeds:
        # O teste é separado antes de qualquer ajuste. O split é feito uma vez
        # por seed, e todos os modelos da seed recebem o mesmo treino e o mesmo teste.
        train, test = stratified_split(table, seed)
        metrics, records = evaluate_split(names, train, test, seed)
        for name in names:
            # A comparação pareada só vale com todos os modelos da seed
            # ajustados nas mesmas linhas de treino e avaliados nas mesmas de teste.
            assert metrics[name]["split_index_sha256"] == metrics[names[0]]["split_index_sha256"]
            assert metrics[name]["test"]["total"] == len(test)
            config, timings = records[name]
            save_run(
                EXPERIMENT,
                TRACK,
                name,
                seed,
                metrics[name],
                config,
                data_sha256,
                timings,
                results_dir,
            )
            results[name][seed] = metrics[name]
    return results


def group_folds(table: pd.DataFrame) -> list[tuple[list[str], pd.DataFrame, pd.DataFrame]]:
    """Separa treino e teste por máquina, em `GROUP_FOLDS` dobras.

    `table` traz em `group` o endereço da máquina local de cada fluxo. Em cada
    dobra ficam no teste uma das máquinas que geraram Non-DoH e Benign-DoH e
    uma parte das que geraram Malicious-DoH, nas duas listas pela ordem do
    endereço. Devolve, por dobra, as máquinas deixadas de fora, o treino e o teste.
    """
    malicious = table["label"] == MALICIOUS
    legitimate_machines = sorted(table.loc[~malicious, "group"].unique(), key=ipaddress.ip_address)
    malicious_machines = sorted(table.loc[malicious, "group"].unique(), key=ipaddress.ip_address)
    # No CIRA-CIC-DoHBrw-2020 nenhuma máquina gerou tráfego legítimo e
    # malicioso: por isso cada dobra precisa tirar máquinas das duas listas.
    assert len(legitimate_machines) == GROUP_FOLDS, "Esperada uma máquina legítima por dobra."
    assert set(legitimate_machines).isdisjoint(malicious_machines)

    folds = []
    malicious_parts = np.array_split(malicious_machines, GROUP_FOLDS)
    for machine, part in zip(legitimate_machines, malicious_parts, strict=True):
        held_out = [machine, *part.tolist()]
        in_test = table["group"].isin(held_out)
        folds.append((held_out, table[~in_test], table[in_test]))
    return folds


def run_group_folds(table: pd.DataFrame, data_sha256: str, results_dir: Path) -> list[dict]:
    """Avalia o modelo A deixando máquinas inteiras de fora e grava cada dobra.

    Normalizador, subconjuntos, SMOTE e modelos são refeitos com o treino de
    cada dobra. Devolve o dicionário de metrics.json de cada dobra.
    """
    folds = []
    for fold, (held_out, train, test) in enumerate(group_folds(table)):
        assert set(train["group"]).isdisjoint(test["group"]), "Máquina no treino e no teste."
        metrics, records = evaluate_split([GROUP_FOLD_MODEL], train, test, GROUP_FOLD_SEED)
        fold_metrics = {"held_out_groups": held_out, **metrics[GROUP_FOLD_MODEL]}
        config, timings = records[GROUP_FOLD_MODEL]
        save_run(
            EXPERIMENT,
            TRACK,
            f"{GROUP_FOLD_MODEL}-fold{fold}",
            GROUP_FOLD_SEED,
            fold_metrics,
            {**config, "split": "por máquina", "held_out_groups": held_out},
            data_sha256,
            timings,
            results_dir,
        )
        folds.append(fold_metrics)
    return folds


def main() -> None:
    """Confere o Parquet, roda as seeds e as dobras por máquina e grava cada execução."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )
    table = pd.read_parquet(CIRA_PARQUET_PATH)

    run_experiment(table, data_sha256, RESULTS_DIR, SEEDS_CORRIGIDA)
    run_group_folds(table, data_sha256, RESULTS_DIR)

    track_dir = RESULTS_DIR / EXPERIMENT / TRACK
    for run_file in sorted(track_dir.glob("*/seed*/run.json")):
        run = json.loads(run_file.read_text(encoding="utf-8"))
        assert run["track"] == TRACK, f"{run_file}: trilha {run['track']}."
    print(f"Resultados em {track_dir.relative_to(PROJECT_ROOT)}")
    print("Agregação e resumo: uv run python -m scripts.e4_resumo")


if __name__ == "__main__":
    main()
