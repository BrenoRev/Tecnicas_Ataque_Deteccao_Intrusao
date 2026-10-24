"""E4: protocolo corrigido, com variância em dez seeds e comparação pareada entre modelos.

O artigo sustenta a vantagem do modelo proposto com uma execução e contra um
Random Forest de outros hiperparâmetros (Tabela II). Este script repete a
avaliação em dez seeds, com as configurações fixadas antes em
`config.CORRIGIDA_MODELS` e sem busca de hiperparâmetros:

- A: o sistema empilhado do artigo, com árvores sem limite de profundidade;
- B: um Random Forest único com os mesmos hiperparâmetros de A e SMOTE;
- C: o Random Forest da Tabela II e SMOTE;
- A-prof5 e B-prof5: A e B com profundidade máxima 5, ao lado.

Cada seed refaz o split 90/10 estratificado, o normalizador, os subconjuntos,
o SMOTE e os modelos, e todos os modelos da seed são avaliados no mesmo teste,
inteiro e sem as linhas cujo vetor de atributos existe no treino. Depois das
dez seeds, o modelo A é avaliado deixando máquinas inteiras de fora, em quatro
dobras.

Lê data/processed/cira.parquet. Grava metrics.json e run.json em
results/e4/corrigida/<modelo>/seed<k>/ e em
results/e4/corrigida/A-fold<k>/seed<s>/, e a agregação em
results/e4/corrigida/summary.json e RESUMO.md.

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
    HYPOTHETICAL_PREVALENCES,
    N_JOBS,
    N_SUBSETS,
    PAIRED_COMPARISONS,
    PAIRED_METRICS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    SEEDS_CORRIGIDA,
    TEST_SIZE,
    smote_seed,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.evaluate import aggregate_seeds, base_rate, evaluate, paired_comparison
from doh_ids.models import base_forests, fit_baseline
from doh_ids.runlog import save_run
from doh_ids.splits import balanced_train, fit_scaler, seen_in_train, stratified_split
from doh_ids.summary import markdown_table
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

# Métricas que `evaluate` devolve no primeiro nível, com o nome da média.
TOP_LEVEL_METRICS = [
    "accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1",
    "weighted_precision",
    "weighted_recall",
    "weighted_f1",
    "roc_auc_ovr_macro",
]
PER_CLASS_METRICS = ["precision", "recall", "f1", "pr_auc"]

PAIRED_METHOD = (
    "comparação pareada por seed: diferença média (primeiro menos segundo), número de seeds em "
    "que cada modelo vence e teste de postos sinalizados de Wilcoxon bilateral "
    "(scipy.stats.wilcoxon com os parâmetros padrão: diferenças nulas descartadas)"
)
PAIRED_CAVEAT = (
    "os conjuntos de teste das seeds se sobrepõem e são sorteados da mesma tabela: os pares "
    "não são independentes, o p-valor é indicativo e não sustenta sozinho a palavra "
    "significativo"
)


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
        # de B são os de A por construção, e só a arquitetura muda.
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


def flat_metrics(evaluated: dict) -> dict:
    """Põe em um nível só as métricas numéricas que `evaluate` devolve.

    As chaves do primeiro nível ficam como estão; as de cada classe ganham o
    nome da classe na frente (`benign_doh_recall`), e o FPR de Malicious-DoH
    contra o resto vira `malicious_fpr`.
    """
    flat = {key: evaluated[key] for key in TOP_LEVEL_METRICS}
    if "roc_auc_ovr_macro_base_mean" in evaluated:
        flat["roc_auc_ovr_macro_base_mean"] = evaluated["roc_auc_ovr_macro_base_mean"]
    for name in CLASS_NAMES:
        for metric in PER_CLASS_METRICS:
            flat[f"{class_key(name)}_{metric}"] = evaluated["per_class"][name][metric]
    flat["malicious_fpr"] = evaluated["malicious_vs_rest"]["fpr"]
    return flat


def class_key(name: str) -> str:
    """Devolve o nome da classe como prefixo de chave: `Benign-DoH` vira `benign_doh`."""
    return name.lower().replace("-", "_")


def model_summary(runs: list[dict]) -> dict:
    """Agrega as execuções de um modelo, uma por seed, em média e desvio padrão.

    Devolve a agregação de cada métrica nos dois conjuntos de `SCOPES`, a
    fração do teste com vetor repetido do treino, os falsos positivos de
    Malicious-DoH somados nas seeds e a conta de taxa base.
    """
    summary = {
        scope: aggregate_seeds([flat_metrics(run[scope]) for run in runs]) for scope in SCOPES
    }
    summary["test_seen_in_train_fraction"] = aggregate_seeds(
        [{"fraction": run["test_seen_in_train"]["fraction"]} for run in runs]
    )["fraction"]
    binary = [run["test"]["malicious_vs_rest"] for run in runs]
    summary["false_positives_total"] = sum(entry["false_positives"] for entry in binary)
    summary["negatives_total"] = sum(entry["negatives"] for entry in binary)
    # A taxa base usa o FPR e o recall médios de Malicious-DoH no teste inteiro.
    # A prevalência é hipotética: o conjunto de dados não a mede.
    fpr = summary["test"]["malicious_fpr"]["mean"]
    recall = summary["test"]["malicious_doh_recall"]["mean"]
    summary["base_rate"] = [
        base_rate(fpr, recall, prevalence) for prevalence in HYPOTHETICAL_PREVALENCES
    ]
    return summary


def paired_rows(results: dict, seeds: list[int]) -> list[dict]:
    """Compara, seed a seed, cada par de `PAIRED_COMPARISONS` em cada métrica e conjunto."""
    rows = []
    for first, second in PAIRED_COMPARISONS:
        for scope in SCOPES:
            for metric in PAIRED_METRICS:
                values = [
                    [flat_metrics(results[name][seed][scope])[metric] for seed in seeds]
                    for name in (first, second)
                ]
                rows.append(
                    {
                        "first": first,
                        "second": second,
                        "scope": scope,
                        "metric": metric,
                        **paired_comparison(*values),
                    }
                )
    return rows


def summary_content(results: dict) -> dict:
    """Monta o conteúdo de summary.json a partir do que `run_experiment` devolve."""
    seeds = list(next(iter(results.values())))
    summary = {
        "experiment": EXPERIMENT,
        "track": TRACK,
        "seeds": seeds,
        "std": "desvio padrão amostral entre as seeds, com n - 1 no denominador",
        "scopes": SCOPES,
        "models": {
            name: {
                "config": CORRIGIDA_MODELS[name],
                **model_summary([runs[seed] for seed in seeds]),
            }
            for name, runs in results.items()
        },
        "paired": {
            "method": PAIRED_METHOD,
            "caveat": PAIRED_CAVEAT,
            "comparisons": paired_rows(results, seeds),
        },
    }
    for name, model in summary["models"].items():
        assert model["test"]["accuracy"]["n"] == len(seeds), f"{name}: falta seed."
    return summary


def group_summary(folds: list[dict]) -> dict:
    """Resume a avaliação por máquina: as métricas de cada dobra e a média entre elas."""
    rows = [flat_metrics(fold["test"]) for fold in folds]
    return {
        "model": GROUP_FOLD_MODEL,
        "seed": GROUP_FOLD_SEED,
        "folds": [
            {
                "held_out_groups": fold["held_out_groups"],
                "train_rows": fold["train_rows"],
                "test_rows": fold["test_rows"],
                **row,
            }
            for fold, row in zip(folds, rows, strict=True)
        ],
        "across_folds": aggregate_seeds(rows),
    }


def mean_std(entry: dict, digits: int = 3) -> str:
    """Escreve média e desvio padrão de uma fração, em percentual."""
    return f"{100 * entry['mean']:.{digits}f} ± {100 * entry['std']:.{digits}f}"


def aggregate_table(models: dict, scope: str) -> str:
    """Escreve a tabela das métricas agregadas de cada modelo, com o nome de cada média."""
    columns = {
        "accuracy": "acurácia",
        "macro_precision": "precisão macro",
        "macro_recall": "recall macro",
        "macro_f1": "F1 macro",
        "weighted_f1": "F1 ponderado",
        "roc_auc_ovr_macro": "AUC-ROC one-vs-rest macro",
    }
    rows = [
        [name, *(mean_std(model[scope][key]) for key in columns)] for name, model in models.items()
    ]
    return markdown_table(["modelo", *columns.values()], rows)


def per_class_table(models: dict, scope: str) -> str:
    """Escreve precisão, recall, F1 e AUC-PR de cada classe, com Benign-DoH em negrito."""
    rows = []
    for name, model in models.items():
        for class_name in CLASS_NAMES:
            cells = [
                mean_std(model[scope][f"{class_key(class_name)}_{metric}"])
                for metric in PER_CLASS_METRICS
            ]
            row = [name, class_name, *cells]
            if class_name == "Benign-DoH":
                row = [f"**{cell}**" for cell in row]
            rows.append(row)
    return markdown_table(["modelo", "classe", "precisão", "recall", "F1", "AUC-PR"], rows)


def malicious_table(models: dict, scope: str) -> str:
    """Escreve o FPR e o recall de Malicious-DoH contra o resto, por modelo."""
    rows = [
        [
            name,
            mean_std(model[scope]["malicious_fpr"], 4),
            mean_std(model[scope]["malicious_doh_recall"]),
        ]
        for name, model in models.items()
    ]
    return markdown_table(["modelo", "FPR de Malicious-DoH", "recall de Malicious-DoH"], rows)


def paired_table(comparisons: list[dict]) -> str:
    """Escreve a tabela da comparação pareada: diferença média, vitórias e Wilcoxon."""
    rows = []
    for row in comparisons:
        tested = row["wilcoxon_statistic"] is not None
        rows.append(
            [
                f"{row['first']} contra {row['second']}",
                SCOPES[row["scope"]],
                row["metric"],
                f"{100 * row['mean_difference']:+.4f}",
                row["first_wins"],
                row["second_wins"],
                row["ties"],
                f"{row['wilcoxon_statistic']:g}" if tested else "sem diferença a ordenar",
                f"{row['wilcoxon_p_value']:.4f}" if tested else "",
            ]
        )
    columns = [
        "par",
        "conjunto",
        "métrica",
        "diferença média (pp)",
        "seeds em que o primeiro vence",
        "seeds em que o segundo vence",
        "empates",
        "estatística de Wilcoxon",
        "p-valor",
    ]
    return markdown_table(columns, rows)


def base_rate_table(models: dict) -> str:
    """Escreve a precisão operacional de cada modelo em cada prevalência hipotética."""
    rows = [
        [
            name,
            f"{entry['prevalence']:g}",
            f"{entry['operational_precision']:.2%}",
            f"{entry['false_alarms_per_10_million']:.0f}",
        ]
        for name, model in models.items()
        for entry in model["base_rate"]
    ]
    columns = [
        "modelo",
        "prevalência hipotética",
        "precisão operacional",
        "alarmes falsos a cada dez milhões de fluxos",
    ]
    return markdown_table(columns, rows)


def false_positive_table(models: dict) -> str:
    """Escreve os falsos positivos de Malicious-DoH somados nas seeds, por modelo."""
    rows = [
        [name, model["false_positives_total"], model["negatives_total"]]
        for name, model in models.items()
    ]
    columns = ["modelo", "falsos positivos somados", "fluxos não maliciosos somados"]
    return markdown_table(columns, rows)


def models_table() -> str:
    """Escreve a configuração fixada de cada modelo."""
    rows = [
        [
            name,
            "empilhado, três subconjuntos" if spec["stacked"] else "Random Forest único",
            spec["n_estimators"],
            "sem limite" if spec["max_depth"] is None else spec["max_depth"],
            spec["max_features"],
            "SMOTE por subconjunto" if spec["stacked"] else "SMOTE no treino inteiro",
        ]
        for name, spec in CORRIGIDA_MODELS.items()
    ]
    columns = [
        "modelo",
        "arquitetura",
        "árvores",
        "profundidade máxima",
        "atributos por divisão",
        "balanceamento",
    ]
    return markdown_table(columns, rows)


def summary_text(summary: dict) -> str:
    """Monta o texto do RESUMO.md a partir do conteúdo de summary.json."""
    models = summary["models"]
    seeds = summary["seeds"]
    seen = next(iter(models.values()))["test_seen_in_train_fraction"]
    pairs = ", ".join(f"{first} contra {second}" for first, second in PAIRED_COMPARISONS)
    return f"""# E4: protocolo corrigido, variância entre seeds e comparação pareada

Gerado por `scripts/e4_corrigido.py`. Trilha `corrigida`. Os números de cada
execução estão em `<modelo>/seed<k>/metrics.json`; a configuração, os tempos e
o commit, em `<modelo>/seed<k>/run.json`; as médias e a comparação pareada, sem
arredondamento, em `summary.json`.

## Protocolo

{len(seeds)} seeds ({seeds[0]} a {seeds[-1]}). Cada seed refaz o split 90/10 estratificado, o
normalizador (ajustado só no treino), os subconjuntos, o SMOTE (só no treino) e
os modelos. Todos os modelos de uma seed são ajustados nas mesmas linhas de
treino e avaliados nas mesmas linhas de teste: o script confere a igualdade, e
cada `metrics.json` traz o resumo dos índices em `split_index_sha256`. Não há
busca de hiperparâmetros nem escolha de seed: as configurações abaixo, os pares
comparados, as métricas da comparação e o teste estatístico foram fixados
antes da primeira execução.

{models_table()}

A contra B isola o efeito da arquitetura, porque os dois têm os mesmos
hiperparâmetros. A contra C é a comparação que o artigo faz na Tabela II. Os
modelos com `-prof5` repetem A e B com a profundidade máxima 5 da Seção IV-B do
artigo. O meta-classificador dos modelos empilhados é treinado como na
reprodução do artigo: este protocolo corrige a avaliação, não o desenho do
empilhamento.

Todo valor abaixo é média ± desvio padrão entre as seeds, em percentual. O
desvio padrão é o amostral. Uma seed controla o split, a reamostragem e os
modelos: o desvio mistura as três fontes de variação e não separa nenhuma.

## Teste inteiro

{aggregate_table(models, "test")}

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

{per_class_table(models, "test")}

Malicious-DoH contra o resto:

{malicious_table(models, "test")}

Nos modelos empilhados, a AUC-ROC e a AUC-PR são calculadas com a saída do
meta-classificador, que só tem as combinações de rótulos dos três bases. A
AUC-ROC calculada com a média das probabilidades dos bases está em
`summary.json`, na chave `roc_auc_ovr_macro_base_mean`. As AUC dos empilhados
e as dos Random Forests únicos não medem a mesma coisa e não devem ser
comparadas diretamente.

## Teste sem vetores repetidos do treino

Em média, {mean_std(seen, 2)}% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

{aggregate_table(models, "test_unseen")}

{per_class_table(models, "test_unseen")}

{malicious_table(models, "test_unseen")}

## Comparação pareada

Pares: {pairs}. Método: {PAIRED_METHOD}. A diferença é a do primeiro modelo
menos a do segundo, em pontos percentuais (pp).

{paired_table(summary["paired"]["comparisons"])}

Ressalva: {PAIRED_CAVEAT}. Diferença média menor que o desvio padrão entre
seeds das tabelas acima não distingue os dois modelos.

## Taxa base

Precisão operacional de Malicious-DoH: a fração dos alertas que seria ataque
se a fração de fluxos maliciosos no tráfego fosse a prevalência indicada. As
prevalências são hipotéticas: o conjunto de dados não mede a prevalência
real. A conta usa o FPR e o recall médios do teste inteiro.

{base_rate_table(models)}

Falsos positivos de Malicious-DoH somados nas {len(seeds)} seeds. Os testes se sobrepõem, e o
mesmo fluxo pode ser contado em mais de uma seed. Com zero falsos positivos, o
FPR médio é zero e a precisão operacional sai 100% em qualquer prevalência: o
que a amostra permite afirmar é o limite superior do intervalo de confiança do
FPR, gravado em cada `metrics.json`.

{false_positive_table(models)}

## Limitações

- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o tráfego das outras duas classes. Nenhum split
  dentro do conjunto remove essa diferença: um modelo pode separar as classes
  pela captura, e não pelo ataque.
- Os {len(seeds)} conjuntos de teste são sorteados da mesma tabela e se sobrepõem. O
  desvio padrão entre seeds mede a variação entre sorteios desta tabela, não a
  variação entre redes ou entre capturas.
- Não houve seleção de hiperparâmetros. As configurações são as do artigo e as
  da biblioteca; um modelo de comparação ajustado poderia ter outro resultado.
- Fluxos da mesma sessão podem cair no treino e no teste. A avaliação sem
  vetores repetidos só remove as linhas idênticas, não as parecidas.
"""


def group_text(group: dict) -> str:
    """Monta a seção do RESUMO.md com a avaliação por máquina."""
    rows = [
        [
            index,
            ", ".join(fold["held_out_groups"]),
            fold["test_rows"],
            f"{fold['accuracy']:.3%}",
            f"{fold['macro_f1']:.3%}",
            f"**{fold['benign_doh_recall']:.3%}**",
            f"**{fold['benign_doh_precision']:.3%}**",
            f"{fold['malicious_doh_recall']:.3%}",
            f"{fold['malicious_fpr']:.4%}",
        ]
        for index, fold in enumerate(group["folds"])
    ]
    across = group["across_folds"]
    rows.append(
        [
            "média ± desvio padrão",
            "",
            "",
            mean_std(across["accuracy"]),
            mean_std(across["macro_f1"]),
            f"**{mean_std(across['benign_doh_recall'])}**",
            f"**{mean_std(across['benign_doh_precision'])}**",
            mean_std(across["malicious_doh_recall"]),
            mean_std(across["malicious_fpr"], 4),
        ]
    )
    columns = [
        "dobra",
        "máquinas no teste",
        "linhas do teste por classe",
        "acurácia",
        "F1 macro",
        "**recall Benign-DoH**",
        "**precisão Benign-DoH**",
        "recall Malicious-DoH",
        "FPR Malicious-DoH",
    ]
    return f"""
## Avaliação por máquina

Modelo {group["model"]}, {len(group["folds"])} dobras, seed {group["seed"]} nos sorteios do modelo.
Resultados em `{group["model"]}-fold<k>/seed{group["seed"]}/`. Em cada dobra ficam no
teste todos os fluxos de uma das máquinas que geraram Non-DoH e Benign-DoH e de
uma parte das que geraram Malicious-DoH, nas duas listas pela ordem do endereço. Nenhuma
máquina aparece no treino e no teste da mesma dobra; normalizador,
subconjuntos, SMOTE e modelos são refeitos em cada dobra. As linhas por classe
estão na ordem Non-DoH, Benign-DoH, Malicious-DoH.

{markdown_table(columns, rows)}

As dobras têm tamanhos e proporções de classe muito diferentes, porque as
máquinas geraram quantidades diferentes de tráfego: a média entre dobras pesa
cada dobra por igual e não é comparável à média entre seeds das seções acima.
Nenhuma máquina gerou tráfego legítimo e malicioso, então esta avaliação
também não separa o ataque da captura. Há uma execução por dobra, com uma seed:
não há medida de variação entre seeds aqui.
"""


def write_summary(results: dict, folds: list[dict], results_dir: Path) -> dict:
    """Grava summary.json e RESUMO.md na pasta da trilha e devolve a agregação das seeds."""
    summary = summary_content(results)
    group = group_summary(folds)
    track_dir = results_dir / EXPERIMENT / TRACK
    content = {**summary, "group_folds": group}
    text = json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False)
    (track_dir / "summary.json").write_text(text + "\n", encoding="utf-8")
    (track_dir / "RESUMO.md").write_text(
        summary_text(summary) + group_text(group), encoding="utf-8"
    )
    return summary


def main() -> None:
    """Confere o Parquet, roda as seeds e as dobras por máquina e grava a agregação."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )
    table = pd.read_parquet(CIRA_PARQUET_PATH)

    results = run_experiment(table, data_sha256, RESULTS_DIR, SEEDS_CORRIGIDA)
    folds = run_group_folds(table, data_sha256, RESULTS_DIR)
    summary = write_summary(results, folds, RESULTS_DIR)

    track_dir = RESULTS_DIR / EXPERIMENT / TRACK
    for run_file in sorted(track_dir.glob("*/seed*/run.json")):
        run = json.loads(run_file.read_text(encoding="utf-8"))
        assert run["track"] == TRACK, f"{run_file}: trilha {run['track']}."
    print(paired_table(summary["paired"]["comparisons"]))
    print(f"Resultados em {track_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
