"""E8: agregação e resumo da modificação proposta, a partir dos arquivos de cada execução.

Não treina nada. Lê os metrics.json e os run.json gravados por
scripts/e8_modificacao.py em results/e8/corrigida/<modelo>-<dados>/seed<k>/ e,
para os modelos A e A-prof5 no CIRA-CIC-DoHBrw-2020, os gravados por
scripts/e4_corrigido.py em results/e4/corrigida/. Escreve em results/e8/corrigida/:

- summary.json: média e desvio padrão entre as seeds de cada modelo em cada
  conjunto de dados, os hiperparâmetros escolhidos em cada seed, os tempos de
  treino e a comparação pareada com o veredito de cada métrica;
- RESUMO.md: a leitura dos números, ao lado da hipótese escrita antes da
  primeira execução (HIPOTESE.md, que este script não altera).

Roda como módulo, a partir da pasta do projeto, porque importa outros scripts.

Uso: uv run python -m scripts.e8_resumo
"""

import json
from pathlib import Path

import numpy as np

import scripts.e4_resumo as e4r
import scripts.e8_modificacao as e8
import scripts.e8_robustez as rob
from doh_ids.config import (
    CLASS_NAMES,
    CORRIGIDA_MODELS,
    MODIFIED_COMPARISONS,
    MODIFIED_CV_FOLDS,
    MODIFIED_GRID,
    MODIFIED_MODELS,
    MODIFIED_PAIRED_METRICS,
    MODIFIED_RUNS,
    MODIFIED_SELECTED_MODEL,
    MODIFIED_SELECTION_FRACTION,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    SEEDS_CORRIGIDA,
)
from doh_ids.evaluate import HIGHER, SAME, aggregate_seeds, paired_comparison, paired_verdict
from doh_ids.summary import markdown_table

E8_DIR = RESULTS_DIR / e8.EXPERIMENT / e8.TRACK
# O sistema do artigo ajustado no CIRA e avaliado no HKD, uma execução com a
# seed 42: é o número que fica ao lado do recall de M1M2 nos fluxos do HKD.
E6_TRANSFER_FILE = (
    RESULTS_DIR / "e6" / "variante" / "transferencia" / f"seed{SEED_FIEL}" / "metrics.json"
)

SCOPES = e8.e4.SCOPES
ORDER = ", ".join(CLASS_NAMES)
SELECTED = MODIFIED_SELECTED_MODEL
# Linha da transferência que junta os fluxos das três ferramentas do HKD.
TRANSFER_TOTAL = "as três ferramentas"
DATASET_TITLES = {
    "cira": "CIRA-CIC-DoHBrw-2020",
    "combinado_sem_replicas": "combinado CIRA + HKD sem réplicas",
}

BENIGN = CLASS_NAMES.index("Benign-DoH")
TRAIN_SECONDS = "train_seconds"
PRECISION = "benign_doh_precision"
METRIC_TITLES = {
    "benign_doh_recall": "recall de Benign-DoH",
    PRECISION: "precisão de Benign-DoH",
    "macro_f1": "F1 macro",
    "malicious_fpr": "FPR de Malicious-DoH",
    TRAIN_SECONDS: "tempo de treino",
}
# Etapas de ajuste gravadas nos tempos de cada execução; cada modelo tem as suas.
FIT_STEPS = [
    "subsets_seconds",
    "base_fit_seconds",
    "meta_fit_seconds",
    "selection_seconds",
    "fit_seconds",
]
# Métricas em que o valor menor é o melhor.
LOWER_IS_BETTER = ["malicious_fpr", TRAIN_SECONDS]

IMPROVES, WORSENS = "melhora", "piora"
# Combinação que a hipótese diz ser a mais escolhida pela seleção.
EXPECTED_SELECTION = {"n_estimators": 100, "max_depth": None, "max_features": "sqrt"}
READING_RULE = (
    "a modificação melhora a métrica quando a diferença média tem o sinal favorável (positivo "
    "em recall e F1, negativo em FPR e tempo) e é, em módulo, maior que o desvio padrão das "
    "diferenças pareadas; piora quando tem o sinal desfavorável e passa do mesmo desvio; nos "
    "outros casos os dois modelos não se distinguem"
)
# Comparações acrescentadas depois da execução, que a hipótese não previa:
# a precisão de Benign-DoH do modelo proposto contra A, e o modelo proposto
# contra M1, que tem a mesma arquitetura e o mesmo balanceamento e só difere
# nos hiperparâmetros. A regra de leitura é aplicada a elas do mesmo modo.
POSTERIOR_NOTE = (
    "análise acrescentada depois da execução, fora dos pares pré-registrados: o par ou a "
    "métrica não estavam na hipótese, e a regra de leitura é aplicada do mesmo modo"
)
POSTERIOR_METRICS = ["macro_f1", "benign_doh_recall", PRECISION, "malicious_fpr"]
POSTERIOR_COMPARISONS = {
    "cira": [(SELECTED, "A", [PRECISION]), (SELECTED, "M1", POSTERIOR_METRICS)],
    "combinado_sem_replicas": [(SELECTED, "A", [PRECISION])],
}
PAIRED_METHOD = (
    "comparação pareada por seed: diferença média (a modificação menos o modelo de "
    "referência), desvio padrão das diferenças, número de seeds em que cada modelo tem o "
    "valor maior e teste de postos sinalizados de Wilcoxon bilateral (scipy.stats.wilcoxon "
    "com os parâmetros padrão: diferenças nulas descartadas)"
)


def model_names(dataset: str) -> list[str]:
    """Devolve os modelos de um conjunto de dados: os de referência e depois os modificados."""
    pairs = MODIFIED_COMPARISONS[dataset]
    names = [second for _, second in pairs] + [first for first, _ in pairs]
    return list(dict.fromkeys(names))


def slice_dir(dataset: str, name: str, e8_dir: Path, e4_dir: Path) -> Path:
    """Devolve a pasta das execuções de um modelo em um conjunto de dados."""
    # No CIRA, A e A-prof5 não são ajustados de novo: vêm do protocolo corrigido.
    if name in MODIFIED_RUNS[dataset]:
        return e8_dir / f"{name}-{dataset}"
    return e4_dir / name


def load_seeds(directory: Path, seeds: list[int], file_name: str) -> dict:
    """Lê o arquivo `file_name` da execução de cada seed: `{seed: conteúdo}`."""
    return {
        seed: json.loads((directory / f"seed{seed}" / file_name).read_text(encoding="utf-8"))
        for seed in seeds
    }


def load_dataset(dataset: str, e8_dir: Path, e4_dir: Path, seeds: list[int]) -> tuple[dict, dict]:
    """Lê as execuções de um conjunto de dados.

    Devolve `results[modelo][seed]`, o metrics.json, e `runs[modelo][seed]`, o
    run.json. Confere que os dois modelos de cada par foram ajustados e
    avaliados nas mesmas linhas em toda seed.
    """
    results, runs = {}, {}
    for name in model_names(dataset):
        directory = slice_dir(dataset, name, e8_dir, e4_dir)
        results[name] = load_seeds(directory, seeds, "metrics.json")
        runs[name] = load_seeds(directory, seeds, "run.json")
    for first, second in MODIFIED_COMPARISONS[dataset]:
        for seed in seeds:
            assert (
                results[first][seed]["split_index_sha256"]
                == results[second][seed]["split_index_sha256"]
            ), f"{dataset}, seed {seed}: {first} e {second} em splits diferentes."
    return results, runs


def train_seconds(run: dict) -> float:
    """Devolve o tempo de treino de uma execução: a soma das etapas de ajuste.

    No sistema empilhado são os subconjuntos com SMOTE, os Random Forests base
    e o meta-classificador; na modificação, a seleção de hiperparâmetros,
    quando há, e o ajuste do `Pipeline`. Ficam de fora o split, a busca de
    vetores repetidos e a avaliação, que não são do modelo.
    """
    return sum(run["timings"][key] for key in FIT_STEPS if key in run["timings"])


def previous_train_seconds(run: dict) -> float:
    """Devolve o tempo de treino pela definição anterior: o total menos a avaliação.

    Só serve para conferir que a troca de definição, feita depois da
    execução, não muda nenhum veredito de tempo.
    """
    return run["timings"]["total_seconds"] - run["timings"]["evaluation_seconds"]


def model_config(name: str) -> dict:
    """Devolve a configuração fixada de um modelo, como ela vai para o summary.json."""
    if name in CORRIGIDA_MODELS:
        return CORRIGIDA_MODELS[name]
    if name == SELECTED:
        return {"stacked": False, "hyperparameters": "selecionados em cada seed"}
    return {"stacked": False, **MODIFIED_MODELS[name]}


def selection_summary(runs: list[dict]) -> dict:
    """Resume a seleção de hiperparâmetros das seeds de um conjunto de dados.

    Devolve a combinação escolhida em cada execução, na ordem de `runs`, e,
    para cada combinação da grade, em quantas seeds foi escolhida e a média e o
    desvio padrão, entre as seeds, do F1 macro de validação.
    """
    selected = [run["selection"]["selected"] for run in runs]
    grid = []
    for index, combination in enumerate(MODIFIED_GRID):
        scores = [run["selection"]["scores"][index] for run in runs]
        assert all({key: score[key] for key in combination} == combination for score in scores), (
            "Seleção gravada com outra grade."
        )
        validation = aggregate_seeds([{"f1": score["mean_macro_f1"]} for score in scores])["f1"]
        grid.append(
            {
                **combination,
                "seeds_selected": selected.count(combination),
                "validation_macro_f1": validation,
            }
        )
    return {
        "selected_by_seed": selected,
        "sample_rows": runs[0]["selection"]["sample_rows"],
        "grid": grid,
    }


def tool_recall_summary(entries: list[dict]) -> dict:
    """Agrega entre as seeds o recall de Malicious-DoH por ferramenta de túnel.

    `entries` tem, por seed, o dicionário de `recall_by_tool`. Devolve, por
    ferramenta, a média de fluxos avaliados, a média e o desvio padrão do
    recall, o menor e o maior recall entre as seeds e em quantas seeds nenhum
    fluxo foi detectado.
    """
    recall = aggregate_seeds(
        [{tool: entry["recall"] for tool, entry in by_tool.items()} for by_tool in entries]
    )
    rows = aggregate_seeds(
        [{tool: entry["n"] for tool, entry in by_tool.items()} for by_tool in entries]
    )
    summary = {}
    for tool in recall:
        by_seed = [by_tool[tool]["recall"] for by_tool in entries]
        summary[tool] = {
            "rows_mean": rows[tool]["mean"],
            "recall": recall[tool],
            "recall_min": min(by_seed),
            "recall_max": max(by_seed),
            "seeds_none_detected": sum(value == 0 for value in by_seed),
        }
    return summary


def verdict(comparison: dict, metric: str) -> str:
    """Aplica a regra de leitura a uma comparação pareada da modificação com a referência."""
    side = paired_verdict(comparison)
    if side == SAME:
        return SAME
    # O lado favorável à modificação é o menor em FPR e tempo e o maior no resto.
    favourable = (side == HIGHER) != (metric in LOWER_IS_BETTER)
    return IMPROVES if favourable else WORSENS


def metric_rows(results: dict, first: str, second: str, metrics: list[str]) -> list[dict]:
    """Compara dois modelos, seed a seed, em cada métrica pedida, nos dois conjuntos de teste."""
    rows = []
    for scope in SCOPES:
        for metric in metrics:
            comparison = e4r.paired(results, first, second, metric, scope)
            rows.append(
                {
                    "first": first,
                    "second": second,
                    "scope": scope,
                    "metric": metric,
                    **comparison,
                    "verdict": verdict(comparison, metric),
                }
            )
    return rows


def time_row(seconds: dict, first: str, second: str) -> dict:
    """Compara o tempo de treino de dois modelos, seed a seed."""
    comparison = paired_comparison(seconds[first], seconds[second])
    return {
        "first": first,
        "second": second,
        "scope": None,
        "metric": TRAIN_SECONDS,
        **comparison,
        "verdict": verdict(comparison, TRAIN_SECONDS),
    }


def paired_rows(results: dict, seconds: dict, dataset: str) -> list[dict]:
    """Compara, seed a seed, cada par do conjunto de dados em cada métrica e no tempo de treino."""
    rows = []
    for first, second in MODIFIED_COMPARISONS[dataset]:
        rows += metric_rows(results, first, second, MODIFIED_PAIRED_METRICS)
        rows.append(time_row(seconds, first, second))
    return rows


def selection_against_test(results: dict) -> dict:
    """Põe a ordem da validação ao lado da do teste, para M1 e para o modelo proposto.

    Compara, seed a seed, o F1 macro de validação da combinação escolhida com
    o da combinação de M1, na subamostra da seleção, e o F1 macro de teste do
    modelo proposto com o de M1. Devolve as duas comparações e a média de
    validação de cada combinação.
    """
    fixed = combination_text(MODIFIED_MODELS["M1"])
    chosen, reference = [], []
    for run in results[SELECTED].values():
        scores = {
            combination_text(score): score["mean_macro_f1"] for score in run["selection"]["scores"]
        }
        chosen.append(scores[combination_text(run["selection"]["selected"])])
        reference.append(scores[fixed])
    validation = aggregate_seeds(
        [{SELECTED: one, "M1": other} for one, other in zip(chosen, reference, strict=True)]
    )
    return {
        "validation_macro_f1": validation,
        "validation_paired": paired_comparison(chosen, reference),
        "test_paired": e4r.paired(results, SELECTED, "M1", "macro_f1"),
    }


def posterior_summary(dataset: str, results: dict) -> dict:
    """Monta as comparações acrescentadas depois da execução para um conjunto de dados."""
    rows = []
    for first, second, metrics in POSTERIOR_COMPARISONS[dataset]:
        for seed, run in results[first].items():
            assert run["split_index_sha256"] == results[second][seed]["split_index_sha256"]
        rows += metric_rows(results, first, second, metrics)
    summary = {"note": POSTERIOR_NOTE, "paired": rows}
    if "M1" in results:
        summary["selection_against_test"] = selection_against_test(results)
    return summary


def time_checks(runs: dict, seconds: dict, dataset: str, refit_runs: dict) -> dict:
    """Refaz a comparação de tempo de treino de dois outros modos, para conferir os vereditos.

    `previous_definition` usa o total da execução menos a avaliação, a
    definição que valia antes de o resumo somar as etapas de ajuste.
    `refit_reference` troca o tempo dos modelos de `refit_runs`, medido em
    outra execução, pelo do mesmo modelo reajustado nas mesmas seeds.
    """
    pairs = MODIFIED_COMPARISONS[dataset]
    previous = {
        name: [previous_train_seconds(run) for run in by_seed.values()]
        for name, by_seed in runs.items()
    }
    checks = {"previous_definition": [time_row(previous, first, second) for first, second in pairs]}
    if refit_runs:
        refit = {
            name: [run["timings"]["fit_seconds"] for run in by_seed.values()]
            for name, by_seed in refit_runs.items()
        }
        checks["refit_reference"] = {
            "train_seconds": aggregate_seeds(
                [
                    dict(zip(refit, values, strict=True))
                    for values in zip(*refit.values(), strict=True)
                ]
            ),
            "paired": [
                time_row({**seconds, **refit}, first, second)
                for first, second in pairs
                if second in refit
            ],
        }
    return checks


def dataset_summary(dataset: str, results: dict, runs: dict, refit_runs: dict) -> dict:
    """Agrega as execuções de um conjunto de dados a partir do que `load_dataset` devolve.

    `refit_runs` tem o run.json dos modelos de referência reajustados em outra
    execução, por modelo e seed; vazio quando não há.
    """
    seeds = list(results[SELECTED])
    seconds = {name: [train_seconds(runs[name][seed]) for seed in seeds] for name in results}
    models = {}
    for name, by_seed in results.items():
        metrics = [by_seed[seed] for seed in seeds]
        models[name] = {
            "config": model_config(name),
            "train_rows": metrics[0]["train_rows"],
            "test_rows": metrics[0]["test_rows"],
            "fit_rows": metrics[0]["fit_rows"],
            "commits": sorted({runs[name][seed]["commit"] for seed in seeds}),
            "dirty_runs": sum(runs[name][seed]["dirty"] for seed in seeds),
            **e4r.model_summary(metrics),
            "benign_doh_recall_min": min(
                run["test"]["per_class"]["Benign-DoH"]["recall"] for run in metrics
            ),
            TRAIN_SECONDS: aggregate_seeds([{"s": value} for value in seconds[name]])["s"],
            "benign_doh_detected": aggregate_seeds(
                [{"n": run["test"]["confusion_matrix"][BENIGN][BENIGN]} for run in metrics]
            )["n"],
            # Falsos positivos de Malicious-DoH e fluxos não maliciosos, somados nas seeds.
            "false_positives_by_scope": {
                scope: {
                    key: sum(run[scope]["malicious_vs_rest"][key] for run in metrics)
                    for key in ("false_positives", "negatives")
                }
                for scope in SCOPES
            },
        }
        assert models[name]["test"]["accuracy"]["n"] == len(seeds), f"{name}: falta seed."
        if "test_recall_by_tool" in metrics[0]:
            models[name]["test_recall_by_tool"] = tool_recall_summary(
                [run["test_recall_by_tool"] for run in metrics]
            )
    selected_runs = [results[SELECTED][seed] for seed in seeds]
    summary = {
        "title": DATASET_TITLES[dataset],
        "models": models,
        "selection": selection_summary(selected_runs),
        "selection_seconds": aggregate_seeds(
            [{"s": runs[SELECTED][seed]["timings"]["selection_seconds"]} for seed in seeds]
        )["s"],
        "paired": paired_rows(results, seconds, dataset),
        "posterior": posterior_summary(dataset, results),
        "time_checks": time_checks(runs, seconds, dataset, refit_runs),
    }
    if "hkd_transfer" in selected_runs[0]:
        transfer = [run["hkd_transfer"] for run in selected_runs]
        summary["hkd_transfer"] = tool_recall_summary(
            [{TRANSFER_TOTAL: run["malicious"], **run["by_tool"]} for run in transfer]
        )
    return summary


def summary_content(loaded: dict, refit_runs: dict) -> dict:
    """Monta o summary.json a partir das execuções lidas de cada conjunto de dados.

    `refit_runs[dados][modelo][seed]` é o run.json do modelo de referência
    reajustado em outra execução, quando há.
    """
    datasets = {
        dataset: dataset_summary(dataset, results, runs, refit_runs.get(dataset, {}))
        for dataset, (results, runs) in loaded.items()
    }
    first_results, _ = next(iter(loaded.values()))
    return {
        "experiment": e8.EXPERIMENT,
        "track": e8.TRACK,
        "seeds": list(first_results[SELECTED]),
        "std": "desvio padrão amostral entre as seeds, com n - 1 no denominador",
        "scopes": SCOPES,
        "selection": {
            "grid": MODIFIED_GRID,
            "folds": MODIFIED_CV_FOLDS,
            "train_fraction": MODIFIED_SELECTION_FRACTION,
            "metric": "F1 macro médio nos folds",
        },
        "paired": {
            "method": PAIRED_METHOD,
            "caveat": e4r.PAIRED_CAVEAT,
            "reading_rule": READING_RULE,
            "lower_is_better": LOWER_IS_BETTER,
        },
        "datasets": datasets,
    }


def combination_text(combination: dict) -> str:
    """Escreve uma combinação da grade: árvores, profundidade máxima e atributos por divisão."""
    depth = "sem limite" if combination["max_depth"] is None else combination["max_depth"]
    return f"({combination['n_estimators']}, {depth}, {combination['max_features']})"


def models_table(dataset: dict) -> str:
    """Escreve o que é cada modelo de um conjunto de dados e em que amostras foi ajustado."""
    rows = []
    for name, model in dataset["models"].items():
        config = model["config"]
        stacked = config["stacked"]
        rows.append(
            [
                name,
                "empilhado, três subconjuntos" if stacked else "Random Forest único",
                "SMOTE por subconjunto" if stacked else "peso de classe, sem SMOTE",
                combination_text(config) if "max_depth" in config else "selecionados em cada seed",
                ", ".join(map(str, model["fit_rows"])),
            ]
        )
    columns = [
        "modelo",
        "arquitetura",
        "balanceamento",
        "árvores, profundidade máxima, atributos por divisão",
        f"amostras por classe em cada conjunto de ajuste, primeira seed ({ORDER})",
    ]
    return markdown_table(columns, rows)


def selection_text(dataset: dict, seeds: list[int]) -> str:
    """Escreve a combinação escolhida em cada seed e a tabela da grade com a validação."""
    selection = dataset["selection"]
    by_seed = "; ".join(
        f"seed {seed}: {combination_text(combination)}"
        for seed, combination in zip(seeds, selection["selected_by_seed"], strict=True)
    )
    rows = [
        [
            combination_text(entry),
            entry["seeds_selected"],
            e4r.mean_std(entry["validation_macro_f1"]),
        ]
        for entry in selection["grid"]
    ]
    columns = [
        "árvores, profundidade máxima, atributos por divisão",
        "seeds em que foi escolhida",
        "F1 macro de validação, média ± desvio padrão entre as seeds (%)",
    ]
    return f"""Combinação escolhida em cada seed (árvores, profundidade máxima, atributos por
divisão): {by_seed}.

A subamostra da seleção da primeira seed tem {selection["sample_rows"]} fluxos por classe
({ORDER}). O F1 macro de validação vem só de linhas do treino.

{markdown_table(columns, rows)}"""


def seconds_table(dataset: dict) -> str:
    """Escreve o tempo de treino de cada modelo, em segundos."""
    rows = []
    for name, model in dataset["models"].items():
        entry = model[TRAIN_SECONDS]
        part = ""
        if name == SELECTED:
            selection = dataset["selection_seconds"]
            part = f"{selection['mean']:.1f} ± {selection['std']:.1f}"
        rows.append([name, f"{entry['mean']:.1f} ± {entry['std']:.1f}", part])
    columns = ["modelo", "tempo de treino (s)", "parte que é seleção de hiperparâmetros (s)"]
    return markdown_table(columns, rows)


def tool_table(dataset: dict) -> str:
    """Escreve o recall de Malicious-DoH por ferramenta de túnel, um modelo por coluna."""
    by_model = {
        name: model["test_recall_by_tool"]
        for name, model in dataset["models"].items()
        if "test_recall_by_tool" in model
    }
    tools = next(iter(by_model.values()))
    rows = [
        [
            tool,
            f"{tools[tool]['rows_mean']:.1f}",
            *(e4r.mean_std(by_tool[tool]["recall"]) for by_tool in by_model.values()),
        ]
        for tool in tools
    ]
    columns = ["ferramenta", "fluxos no teste, média entre as seeds"]
    columns += [f"recall, {name} (%)" for name in by_model]
    return markdown_table(columns, rows)


def transfer_table(transfer: dict) -> str:
    """Escreve o recall de M1M2 nos fluxos do HKD: média, desvio, mínimo e máximo entre as seeds."""
    rows = [
        [
            name,
            f"{entry['rows_mean']:.0f}",
            e4r.mean_std(entry["recall"]),
            f"{100 * entry['recall_min']:.3f}",
            f"{100 * entry['recall_max']:.3f}",
            entry["seeds_none_detected"],
        ]
        for name, entry in transfer.items()
    ]
    columns = [
        "fluxos do HKD",
        "fluxos",
        f"recall, {SELECTED} ajustado no CIRA, média ± desvio padrão entre as seeds (%)",
        "menor recall entre as seeds (%)",
        "maior recall entre as seeds (%)",
        "seeds sem nenhum fluxo detectado",
    ]
    return markdown_table(columns, rows)


def transfer_text(transfer: dict, e6_transfer: dict, n_seeds: int) -> str:
    """Escreve a leitura da transferência ao HKD, com o sistema do artigo citado à parte."""
    total = transfer[TRANSFER_TOTAL]
    article = e6_transfer["malicious"]["recall"]
    by_tool = ", ".join(
        f"{tool} {entry['recall']:.3%}" for tool, entry in e6_transfer["by_tool"].items()
    )
    none_detected = [
        f"{tool}, em {entry['seeds_none_detected']} das {n_seeds} seeds"
        for tool, entry in transfer.items()
        if entry["seeds_none_detected"]
    ]
    text = (
        f"Sem nenhum fluxo detectado em alguma seed: {'; '.join(none_detected) or 'nenhuma'}. "
        f"Nas {n_seeds} seeds, {SELECTED} deixa passar de {1 - total['recall_max']:.2%} a "
        f"{1 - total['recall_min']:.2%} dos fluxos do HKD.\n\n"
        f"O sistema do artigo ajustado no CIRA foi avaliado no HKD em uma execução só, com a "
        f"seed {SEED_FIEL} (`results/e6/variante/transferencia/`): recall de {article:.3%} "
        f"({by_tool}), ou {1 - article:.2%} dos fluxos sem detecção. Esse número não é das "
        "mesmas seeds, por isso fica fora da tabela, e não há comparação pareada."
    )
    # Um sistema que deixa passar a maioria dos fluxos em toda execução medida
    # não transfere, qualquer que seja a diferença entre os dois.
    if total["recall_max"] < 0.5 and article < 0.5:
        text += " Nenhum dos dois sistemas transfere."
    return text


def difference_text(row: dict) -> tuple[str, str]:
    """Escreve a diferença média e o desvio das diferenças de uma comparação, com a unidade."""
    if row["metric"] == TRAIN_SECONDS:
        return f"{row['mean_difference']:+.1f} s", f"{row['std_difference']:.1f} s"
    return f"{100 * row['mean_difference']:+.4f} pp", f"{100 * row['std_difference']:.4f} pp"


def paired_table(rows: list[dict]) -> str:
    """Escreve a tabela da comparação pareada, com o veredito da regra de leitura."""
    lines = []
    for row in rows:
        tested = row["wilcoxon_statistic"] is not None
        lines.append(
            [
                f"{row['first']} contra {row['second']}",
                SCOPES[row["scope"]] if row["scope"] else "uma medida por execução",
                METRIC_TITLES[row["metric"]],
                "menor" if row["metric"] in LOWER_IS_BETTER else "maior",
                *difference_text(row),
                row["first_wins"],
                row["second_wins"],
                row["ties"],
                f"{row['wilcoxon_p_value']:.4f}" if tested else "sem diferença a ordenar",
                f"**{row['verdict']}**",
            ]
        )
    columns = [
        "par",
        "conjunto",
        "métrica",
        "melhor é o valor",
        "diferença média",
        "desvio padrão das diferenças",
        "seeds em que o primeiro tem o valor maior",
        "seeds em que o segundo tem o valor maior",
        "empates",
        "p-valor de Wilcoxon",
        "veredito para a modificação",
    ]
    return markdown_table(columns, lines)


def find(
    rows: list[dict],
    first: str,
    metric: str,
    scope: str | None = "test",
    second: str | None = None,
) -> dict:
    """Devolve a comparação pareada do modelo `first` com a referência dele em uma métrica.

    `second` só é preciso quando `rows` tem `first` contra mais de um modelo.
    """
    if metric == TRAIN_SECONDS:
        scope = None
    return next(
        row
        for row in rows
        if row["first"] == first
        and row["metric"] == metric
        and row["scope"] == scope
        and second in (None, row["second"])
    )


def verdict_text(rows: list[dict], first: str, metric: str, scope: str | None = "test") -> str:
    """Escreve o veredito de uma comparação, com a diferença média e o desvio das diferenças."""
    row = find(rows, first, metric, scope)
    difference, deviation = difference_text(row)
    return (
        f"{METRIC_TITLES[metric]}: diferença média de {difference}, desvio padrão das "
        f"diferenças de {deviation}, veredito **{row['verdict']}**"
    )


def fixed_models_lines(cira: dict) -> list[str]:
    """Confronta os itens 1 e 2 da hipótese: M1 contra A e M1-prof5 contra A-prof5, no CIRA."""
    rows = cira["paired"]
    same = all(
        find(rows, "M1", metric)["verdict"] == SAME for metric in ("macro_f1", "benign_doh_recall")
    )
    lowest = cira["models"]["M1-prof5"]["benign_doh_recall_min"]
    return [
        "1. M1 contra A, CIRA, teste inteiro:",
        "   - Esperado: os dois não se distinguem em F1 macro nem em recall de Benign-DoH. "
        f"{verdict_text(rows, 'M1', 'macro_f1')}; {verdict_text(rows, 'M1', 'benign_doh_recall')}: "
        f"{e4r.occurred(same)}.",
        "   - Esperado: M1 treina em menos tempo que A. "
        f"{verdict_text(rows, 'M1', TRAIN_SECONDS)}: "
        f"{e4r.occurred(find(rows, 'M1', TRAIN_SECONDS)['verdict'] == IMPROVES)}.",
        "2. M1-prof5 contra A-prof5, CIRA, teste inteiro:",
        "   - Esperado: recall de Benign-DoH maior que zero em todas as seeds. Menor recall "
        f"de M1-prof5 entre as seeds: {lowest:.3%}: {e4r.occurred(lowest > 0)}.",
        f"   - Esperado: melhora do F1 macro. {verdict_text(rows, 'M1-prof5', 'macro_f1')}: "
        f"{e4r.occurred(find(rows, 'M1-prof5', 'macro_f1')['verdict'] == IMPROVES)}.",
        "   - Esperado: piora do FPR de Malicious-DoH. "
        f"{verdict_text(rows, 'M1-prof5', 'malicious_fpr')}: "
        f"{e4r.occurred(find(rows, 'M1-prof5', 'malicious_fpr')['verdict'] == WORSENS)}.",
    ]


def selection_lines(datasets: dict) -> list[str]:
    """Confronta o item 3 da hipótese: o que a seleção escolheu em cada conjunto de dados."""
    lines = [
        "3. Seleção. Esperado: uma combinação sem limite de profundidade em todas as seeds e "
        f"{combination_text(EXPECTED_SELECTION)} como a mais frequente."
    ]
    for dataset in datasets.values():
        selected = dataset["selection"]["selected_by_seed"]
        unlimited = sum(combination["max_depth"] is None for combination in selected)
        expected = selected.count(EXPECTED_SELECTION)
        most_frequent = expected == max(
            entry["seeds_selected"] for entry in dataset["selection"]["grid"]
        )
        lines.append(
            f"   - {dataset['title']}: sem limite de profundidade em {unlimited} das "
            f"{len(selected)} seeds: {e4r.occurred(unlimited == len(selected))}; "
            f"{combination_text(EXPECTED_SELECTION)} escolhida em {expected} seeds, a mais "
            f"frequente: {e4r.occurred(most_frequent)}."
        )
    return lines


def proposed_lines(number: int, dataset: dict) -> list[str]:
    """Confronta com os números o que se esperava de M1M2 contra A em um conjunto de dados."""
    rows, models = dataset["paired"], dataset["models"]
    f1 = find(rows, SELECTED, "macro_f1")
    recall = find(rows, SELECTED, "benign_doh_recall")
    fpr = find(rows, SELECTED, "malicious_fpr")
    false_benign = [
        models[name]["benign_doh_errors"]["non_doh_as_benign_doh"]["mean"]
        for name in (SELECTED, "A")
    ]
    detected = [models[name]["benign_doh_detected"]["mean"] for name in (SELECTED, "A")]
    false_positives = [models[name]["false_positives_by_scope"]["test"] for name in (SELECTED, "A")]
    n_seeds = models[SELECTED]["test"]["accuracy"]["n"]
    return [
        f"{number}. {SELECTED} contra A, {dataset['title']}, teste inteiro:",
        f"   - Esperado: melhora do F1 macro. {verdict_text(rows, SELECTED, 'macro_f1')}: "
        f"{e4r.occurred(f1['verdict'] == IMPROVES)}.",
        "   - Esperado: diferença de F1 macro abaixo de 1 pp: "
        f"{e4r.occurred(abs(100 * f1['mean_difference']) < 1)}.",
        "   - Esperado: sem melhora no recall de Benign-DoH. "
        f"{verdict_text(rows, SELECTED, 'benign_doh_recall')}: "
        f"{e4r.occurred(recall['verdict'] != IMPROVES)}. Em fluxos (contagem acrescentada "
        f"depois da execução): {SELECTED} acerta em média {detected[0] - detected[1]:+.1f} "
        f"fluxos Benign-DoH por teste em relação a A, de "
        f"{models[SELECTED]['test_rows'][BENIGN]} no teste da primeira seed.",
        "   - Esperado: o ganho, se houver, vem de menos fluxos Non-DoH preditos como "
        f"Benign-DoH. Média por teste de {false_benign[0]:.1f} em {SELECTED} contra "
        f"{false_benign[1]:.1f} em A: {e4r.occurred(false_benign[0] < false_benign[1])}.",
        "   - Esperado: os dois não se distinguem no FPR de Malicious-DoH. "
        f"{verdict_text(rows, SELECTED, 'malicious_fpr')}: "
        f"{e4r.occurred(fpr['verdict'] == SAME)}. Em fluxos (contagem acrescentada depois da "
        f"execução): {false_positives[0]['false_positives']} falsos positivos de "
        f"Malicious-DoH somados nas {n_seeds} seeds em {SELECTED} contra "
        f"{false_positives[1]['false_positives']} em A, em "
        f"{false_positives[0]['negatives']} fluxos não maliciosos somados.",
    ]


def scope_and_time_lines(datasets: dict) -> list[str]:
    """Confronta os itens 6 e 7 da hipótese: os dois conjuntos de teste e o tempo de treino."""
    lines = [
        f"6. Esperado: os vereditos de {SELECTED} contra A são os mesmos no teste inteiro e no "
        "teste sem vetores repetidos."
    ]
    for dataset in datasets.values():
        rows = dataset["paired"]
        verdicts = {
            metric: [find(rows, SELECTED, metric, scope)["verdict"] for scope in SCOPES]
            for metric in MODIFIED_PAIRED_METRICS
        }
        cells = "; ".join(
            f"{METRIC_TITLES[metric]}, {pair[0]} e {pair[1]}" for metric, pair in verdicts.items()
        )
        same = all(pair[0] == pair[1] for pair in verdicts.values())
        lines.append(f"   - {dataset['title']}: {cells}: {e4r.occurred(same)}.")
    lines.append(f"7. Esperado: {SELECTED} leva mais tempo de treino que A, por causa da seleção.")
    for dataset in datasets.values():
        rows = dataset["paired"]
        slower = find(rows, SELECTED, TRAIN_SECONDS)["verdict"] == WORSENS
        lines.append(
            f"   - {dataset['title']}: {verdict_text(rows, SELECTED, TRAIN_SECONDS)}: "
            f"{e4r.occurred(slower)}."
        )
    return lines


def proposed_is_better(dataset: dict) -> bool:
    """Diz se o modelo proposto é dito melhor que A pela regra fixada na hipótese."""
    rows = dataset["paired"]
    return all(
        find(rows, SELECTED, "macro_f1", scope)["verdict"] == IMPROVES
        and find(rows, SELECTED, "benign_doh_recall", scope)["verdict"] != WORSENS
        and find(rows, SELECTED, "malicious_fpr", scope)["verdict"] != WORSENS
        for scope in SCOPES
    )


def better_lines(datasets: dict) -> list[str]:
    """Escreve, para cada conjunto de dados, se o modelo proposto é dito melhor que A."""
    lines = []
    for dataset in datasets.values():
        rows = dataset["paired"]
        cells = "; ".join(
            f"{METRIC_TITLES[metric]}, "
            + " e ".join(
                f"{find(rows, SELECTED, metric, scope)['verdict']} no {title}"
                for scope, title in SCOPES.items()
            )
            for metric in MODIFIED_PAIRED_METRICS
        )
        conclusion = (
            f"{SELECTED} **é dito melhor que A**"
            if proposed_is_better(dataset)
            else f"**não se diz que {SELECTED} é melhor que A**"
        )
        lines.append(f"- {dataset['title']}: {cells}. Pela regra, {conclusion}.")
    return lines


def improves_over_reference(dataset: dict, metric: str) -> bool:
    """Diz se o modelo proposto melhora a métrica sobre A, pela regra, no teste inteiro."""
    rows = [*dataset["paired"], *dataset["posterior"]["paired"]]
    return find(rows, SELECTED, metric, second="A")["verdict"] == IMPROVES


def repeated_text(datasets: dict) -> str:
    """Diz que melhoras de M1M2 sobre A se repetem nos conjuntos de dados, no teste inteiro."""
    repeated, single = [], []
    for metric in [*MODIFIED_PAIRED_METRICS, PRECISION]:
        improved = [
            dataset["title"]
            for dataset in datasets.values()
            if improves_over_reference(dataset, metric)
        ]
        if len(improved) == len(datasets):
            repeated.append(METRIC_TITLES[metric])
        elif improved:
            single.append(f"{METRIC_TITLES[metric]} (só em {', '.join(improved)})")
    # Fluxos por classe de cada conjunto, na primeira seed: treino mais teste.
    first, last = (
        np.add(dataset["models"][SELECTED]["train_rows"], dataset["models"][SELECTED]["test_rows"])
        for dataset in (list(datasets.values())[0], list(datasets.values())[-1])
    )
    by_class = ", ".join(
        f"{difference:+d} {name}"
        for name, difference in zip(CLASS_NAMES, last - first, strict=True)
    )
    return (
        "Leitura acrescentada depois da execução. Pela regra, no teste inteiro, o veredito de "
        f"melhora de {SELECTED} sobre A se repete em todos os conjuntos de dados em: "
        f"{', '.join(repeated) or 'nenhuma métrica'}. Não se repete em: "
        f"{', '.join(single) or 'nenhuma métrica'}. A {METRIC_TITLES[PRECISION]} não estava entre "
        "as métricas da hipótese e entra aqui como análise posterior. Os conjuntos não são "
        f"independentes: o segundo tem {last.sum() / first.sum() - 1:.2%} de fluxos a mais que "
        f"o primeiro ({by_class}). É o primeiro mais os fluxos do HKD, e o resultado nele não "
        "é uma réplica independente do resultado no primeiro."
    )


def unexpected_lines(datasets: dict) -> list[str]:
    """Confronta com os números a lista de resultados inesperados da hipótese."""
    cira = datasets["cira"]
    m1_worse = any(
        find(cira["paired"], "M1", metric)["verdict"] == WORSENS
        for metric in ("macro_f1", "benign_doh_recall")
    )
    lowest = cira["models"]["M1-prof5"]["benign_doh_recall_min"]
    lines = [
        "- M1 piorar o F1 macro ou o recall de Benign-DoH em relação a A, no teste inteiro: "
        f"{e4r.occurred(m1_worse)}.",
        "- M1-prof5 com recall de Benign-DoH igual a zero em alguma seed: "
        f"{e4r.occurred(lowest == 0)}.",
    ]
    for dataset in datasets.values():
        rows, title = dataset["paired"], dataset["title"]
        selected = dataset["selection"]["selected_by_seed"]
        limited = sum(combination["max_depth"] is not None for combination in selected)
        below = find(rows, SELECTED, "macro_f1")["second_wins"]
        worse = [
            METRIC_TITLES[metric]
            for metric in ("benign_doh_recall", "malicious_fpr")
            if find(rows, SELECTED, metric)["verdict"] == WORSENS
        ]
        lost = [
            METRIC_TITLES[metric]
            for metric in MODIFIED_PAIRED_METRICS
            if find(rows, SELECTED, metric, "test")["verdict"] == IMPROVES
            and find(rows, SELECTED, metric, "test_unseen")["verdict"] != IMPROVES
        ]
        lines += [
            f"- {title}: a seleção escolher profundidade 5 ou 10 em alguma seed: "
            f"{e4r.occurred(limited > 0)} ({limited} de {len(selected)} seeds).",
            f"- {title}: {SELECTED} abaixo de A em F1 macro em todas as seeds: "
            f"{e4r.occurred(below == len(selected))} (abaixo em {below} de {len(selected)}).",
            f"- {title}: {SELECTED} piorar o recall de Benign-DoH ou o FPR de Malicious-DoH, no "
            f"teste inteiro: {e4r.occurred(bool(worse))}"
            + (f" ({', '.join(worse)})." if worse else "."),
            f"- {title}: veredito de melhora no teste inteiro que não se repete no teste sem "
            f"vetores repetidos: {e4r.occurred(bool(lost))}"
            + (f" ({', '.join(lost)})." if lost else "."),
        ]
    return lines


def hypothesis_text(datasets: dict) -> str:
    """Monta a seção que põe a hipótese escrita antes da execução ao lado do resultado."""
    expected = fixed_models_lines(datasets["cira"]) + selection_lines(datasets)
    for number, dataset in enumerate(datasets.values(), start=4):
        expected += proposed_lines(number, dataset)
    expected += scope_and_time_lines(datasets)
    keys = ("macro_f1", "benign_doh_recall", "benign_doh_precision")
    fixed, selected = (
        {key: e4r.mean_std(datasets["cira"]["models"][name]["test"][key]) for key in keys}
        for name in ("M1", SELECTED)
    )
    return f"""## Hipótese ao lado do resultado

A hipótese está em `HIPOTESE.md`, escrita antes da primeira execução e não
alterada depois. Os itens abaixo seguem a ordem do arquivo. Regra de leitura,
fixada na hipótese: {READING_RULE}.

### O que se esperava

{chr(10).join(expected)}

### O modelo proposto é melhor que A?

A hipótese fixou a condição: melhorar o F1 macro pela regra no teste inteiro e
no teste sem vetores repetidos, sem piorar o recall de Benign-DoH nem o FPR de
Malicious-DoH.

{chr(10).join(better_lines(datasets))}

{repeated_text(datasets)}

{SELECTED} difere de A em três coisas ao mesmo tempo: a arquitetura (um Random
Forest em vez de três e um meta-classificador), o balanceamento (peso de
classe em vez de SMOTE) e os hiperparâmetros. A diferença entre os dois não
pode ser atribuída a nenhuma das três em separado. M1 contra A, no CIRA, mede
a arquitetura e o balanceamento juntos, com os hiperparâmetros iguais. M1
contra {SELECTED} não estava entre os pares da hipótese: a comparação seed a seed
foi acrescentada depois da execução e está na seção do CIRA. Médias dos dois
no teste inteiro do CIRA: F1 macro de {fixed["macro_f1"]}% em M1 e de
{selected["macro_f1"]}% em {SELECTED}; recall de Benign-DoH de
{fixed["benign_doh_recall"]}% e de {selected["benign_doh_recall"]}%; precisão de
Benign-DoH de {fixed["benign_doh_precision"]}% e de {selected["benign_doh_precision"]}%.

### O que a hipótese listava como resultado inesperado

{chr(10).join(unexpected_lines(datasets))}
"""


def dataset_text(key: str, dataset: dict, seeds: list[int], e6_transfer: dict) -> str:
    """Monta a seção do RESUMO.md de um conjunto de dados."""
    models = dataset["models"]
    seen = next(iter(models.values()))["test_seen_in_train_fraction"]
    pairs = [(first, second) for first, second in MODIFIED_COMPARISONS[key]]
    extra = ""
    if "test_recall_by_tool" in models[SELECTED]:
        extra += f"""
### Recall de Malicious-DoH por ferramenta de túnel

Teste inteiro, média ± desvio padrão entre as seeds. dns2tcp, dnscat2 e iodine
vêm do CIRA; dnstt, tcp-over-dns e tuns, do HKD.

{tool_table(dataset)}
"""
    if "hkd_transfer" in dataset:
        extra += f"""
### {SELECTED} ajustado no CIRA, avaliado nos fluxos do HKD

Os fluxos do HKD são todos Malicious-DoH e não entram em nenhum ajuste; são
normalizados com o normalizador do treino do CIRA. Sem fluxo legítimo, só o
recall é definido. O mínimo e o máximo entre as seeds foram acrescentados
depois da execução.

{transfer_table(dataset["hkd_transfer"])}

{transfer_text(dataset["hkd_transfer"], e6_transfer, len(seeds))}
"""
    return f"""## {dataset["title"]}

Modelos e amostras em que cada um foi ajustado. O treino da primeira seed tem
{models[SELECTED]["train_rows"]} fluxos reais por classe ({ORDER}): o que passa disso em
uma classe é amostra sintética.

{models_table(dataset)}

### Teste inteiro

{e4r.auc_note(models)}

{e4r.aggregate_table(models, "test")}

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

{e4r.per_class_table(models, "test")}

Malicious-DoH contra o resto:

{e4r.malicious_table(models, "test")}

### Os dois erros de Benign-DoH

Média ± desvio padrão entre as seeds do número de fluxos do teste, lido das
matrizes de confusão: Non-DoH predito como Benign-DoH baixa a precisão de
Benign-DoH; Benign-DoH predito como Non-DoH baixa o recall.

{e4r.benign_errors_table(models)}

{e4r.benign_errors_text(models, pairs)}

### Teste sem vetores repetidos do treino

Em média, {e4r.mean_std(seen, 2)}% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

{e4r.aggregate_table(models, "test_unseen")}

{e4r.per_class_table(models, "test_unseen")}

{e4r.malicious_table(models, "test_unseen")}
{extra}
### Hiperparâmetros selecionados

{selection_text(dataset, seeds)}

### Tempo de treino

Média ± desvio padrão entre as seeds, em segundos: a soma das etapas de ajuste
de cada modelo (subconjuntos com SMOTE, Random Forests base e meta-classificador
no empilhado; seleção de hiperparâmetros e ajuste do `Pipeline` na
modificação). Split, busca de vetores repetidos e avaliação ficam de fora. O
tempo depende da carga da máquina e não é reprodutível como as métricas.

{seconds_table(dataset)}

{time_text(dataset)}

### Comparação pareada

{paired_table(dataset["paired"])}

{posterior_text(dataset)}"""


def false_positives_text(models: dict, names: list[str]) -> str:
    """Escreve os falsos positivos de Malicious-DoH somados nas seeds, nos dois conjuntos."""
    cells = []
    for scope, title in SCOPES.items():
        counts = [models[name]["false_positives_by_scope"][scope] for name in names]
        by_model = ", ".join(
            f"{name} {entry['false_positives']}" for name, entry in zip(names, counts, strict=True)
        )
        cells.append(f"{title}, {by_model}, em {counts[0]['negatives']} fluxos não maliciosos")
    return "Falsos positivos de Malicious-DoH somados nas seeds: " + "; ".join(cells) + "."


def selection_effect_text(dataset: dict) -> str:
    """Escreve o que a seleção de hiperparâmetros muda, de M1 para o modelo proposto."""
    rows = dataset["posterior"]["paired"]
    verdicts = {
        metric: find(rows, SELECTED, metric, second="M1")["verdict"] for metric in POSTERIOR_METRICS
    }
    parts = []
    if verdicts["benign_doh_recall"] == IMPROVES and verdicts[PRECISION] == WORSENS:
        parts.append("troca precisão por recall de Benign-DoH")
    if verdicts["malicious_fpr"] == IMPROVES:
        parts.append("reduz os falsos positivos de Malicious-DoH")
    if verdicts["macro_f1"] != IMPROVES:
        parts.append("não aumenta o F1 macro")
    text = (
        f"Pela regra, no teste inteiro, de M1 para {SELECTED}: "
        + "; ".join(f"{METRIC_TITLES[metric]}, {value}" for metric, value in verdicts.items())
        + ". "
    )
    if parts:
        text += f"A seleção de hiperparâmetros {'; '.join(parts)}."
    if (
        verdicts["macro_f1"] != IMPROVES
        and find(dataset["paired"], "M1", "macro_f1")["verdict"] == IMPROVES
    ):
        text += f" O ganho de F1 macro de {SELECTED} sobre A já está em M1."
    return text


def selection_against_test_text(dataset: dict) -> str:
    """Escreve a ordem da validação ao lado do F1 macro de teste de M1 e do modelo proposto."""
    against = dataset["posterior"]["selection_against_test"]
    validation, test = against["validation_paired"], against["test_paired"]
    fixed = combination_text(MODIFIED_MODELS["M1"])
    ranking = sorted(
        dataset["selection"]["grid"], key=lambda entry: -entry["validation_macro_f1"]["mean"]
    )
    position = [combination_text(entry) for entry in ranking].index(fixed) + 1
    rows = [
        [
            name,
            combination,
            e4r.mean_std(against["validation_macro_f1"][name]),
            e4r.mean_std(dataset["models"][name]["test"]["macro_f1"]),
        ]
        for name, combination in (("M1", fixed), (SELECTED, "a escolhida em cada seed"))
    ]
    columns = [
        "modelo",
        "árvores, profundidade máxima, atributos por divisão",
        f"F1 macro de validação, subamostra de {MODIFIED_SELECTION_FRACTION:.0%} do treino (%)",
        "F1 macro no teste inteiro (%)",
    ]
    text = (
        f"A combinação de M1 é a {position}ª das {len(ranking)} da grade pela média de "
        f"validação. Na validação, a combinação escolhida fica acima da de M1 em "
        f"{validation['first_wins']} das {dataset['models'][SELECTED]['test']['macro_f1']['n']} "
        f"seeds (diferença média de {100 * validation['mean_difference']:+.3f} pp); no teste, "
        f"{SELECTED} fica acima de M1 em {test['first_wins']} seeds e abaixo em "
        f"{test['second_wins']} (diferença média de {100 * test['mean_difference']:+.3f} pp). "
        "A validação mede modelos ajustados em quatro quintos da subamostra; o teste, modelos "
        "ajustados no treino inteiro."
    )
    if validation["mean_difference"] > 0 and test["mean_difference"] <= 0:
        text += (
            " A ordem que a validação dá às duas combinações não se repete no teste: é "
            "evidência da limitação da subamostra, registrada em Limitações."
        )
    return f"{markdown_table(columns, rows)}\n\n{text}"


def posterior_text(dataset: dict) -> str:
    """Monta o bloco das comparações acrescentadas depois da execução."""
    posterior, models = dataset["posterior"], dataset["models"]
    compared = {name for row in posterior["paired"] for name in (row["first"], row["second"])}
    names = [name for name in models if name in compared]
    text = f"""### Análise acrescentada depois da execução, fora dos pares pré-registrados

Este bloco é {POSTERIOR_NOTE}. Não entra na condição que a hipótese fixou para
dizer que o modelo proposto é melhor que A.

{paired_table(posterior["paired"])}

{false_positives_text(models, names)}
"""
    if "selection_against_test" in posterior:
        text += f"""
{selection_effect_text(dataset)}

{selection_against_test_text(dataset)}
"""
    return text


def time_text(dataset: dict) -> str:
    """Escreve as duas conferências do tempo de treino feitas depois da execução."""
    checks, current = dataset["time_checks"], dataset["paired"]

    def same_verdicts(rows: list[dict]) -> str:
        same = all(
            row["verdict"] == find(current, row["first"], TRAIN_SECONDS)["verdict"] for row in rows
        )
        return "são os mesmos" if same else "**mudam**"

    text = (
        "A definição de tempo de treino acima foi ajustada depois da execução: antes era o "
        "total da execução menos a avaliação. Com a definição anterior, os vereditos de tempo "
        f"{same_verdicts(checks['previous_definition'])}."
    )
    if "refit_reference" in checks:
        refit = checks["refit_reference"]
        cells = "; ".join(
            f"{name}, {entry['mean']:.1f} ± {entry['std']:.1f} s reajustado contra "
            f"{dataset['models'][name][TRAIN_SECONDS]['mean']:.1f} ± "
            f"{dataset['models'][name][TRAIN_SECONDS]['std']:.1f} s na tabela"
            for name, entry in refit["train_seconds"].items()
        )
        text += (
            "\n\nOs tempos dos modelos que vêm de `results/e4/corrigida/` foram medidos em outra "
            "execução, com outra carga na máquina. Os mesmos modelos foram reajustados nas mesmas "
            f"seeds pelo script da robustez (`robustez-<modelo>-todos/`): {cells}. Com o tempo "
            f"reajustado no lugar, os vereditos de tempo {same_verdicts(refit['paired'])}."
        )
    return text


def provenance_text(datasets: dict) -> str:
    """Escreve o commit e o estado da árvore com que cada grupo de execuções foi gravado."""
    lines = []
    for dataset in datasets.values():
        for name, model in dataset["models"].items():
            commits = ", ".join(f"`{commit[:7]}`" for commit in model["commits"])
            lines.append(
                f"- {dataset['title']}, {name}: commit {commits}; execuções com a árvore "
                f"suja: {model['dirty_runs']}."
            )
    return "\n".join(lines)


def summary_text(summary: dict, e6_transfer: dict) -> str:
    """Monta o texto do RESUMO.md a partir da agregação."""
    datasets, seeds = summary["datasets"], summary["seeds"]
    grid = ", ".join(combination_text(combination) for combination in MODIFIED_GRID)
    sections = "\n".join(
        dataset_text(key, dataset, seeds, e6_transfer) for key, dataset in datasets.items()
    )
    return f"""# E8: a modificação proposta pela equipe ao lado do sistema do artigo

Gerado por `scripts/e8_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e8_modificacao.py` e, para A e A-prof5 no CIRA, por
`scripts/e4_corrigido.py`. Trilha `corrigida`. Os números de cada execução
estão em `<modelo>-<dados>/seed<k>/metrics.json`; a configuração, os tempos e o
commit, em `<modelo>-<dados>/seed<k>/run.json`; as médias e a comparação
pareada, sem arredondamento, em `summary.json`.

## Protocolo

{len(seeds)} seeds ({seeds[0]} a {seeds[-1]}). Cada seed refaz o split 90/10 estratificado e
todos os ajustes. Os dois modelos de cada par são ajustados nas mesmas linhas de treino
e avaliados nas mesmas linhas de teste: o script confere a igualdade pelo
resumo dos índices (`split_index_sha256`) de cada `metrics.json`. No CIRA, A e
A-prof5 são os de `results/e4/corrigida/`, sem novo ajuste.

A modificação é um Random Forest único, sem SMOTE e sem empilhamento, com peso
de classe (`class_weight='balanced'`) e o normalizador como primeiro passo de
um `Pipeline`. M1 e M1-prof5 têm os hiperparâmetros dos bases de A e de
A-prof5. {SELECTED}, o modelo proposto, tem os hiperparâmetros escolhidos em cada
seed e em cada conjunto de dados: subamostra estratificada de
{MODIFIED_SELECTION_FRACTION:.0%} do treino da seed, validação cruzada estratificada de
{MODIFIED_CV_FOLDS} folds dentro dela, com o normalizador reajustado em cada fold, e
escolha pelo maior F1 macro médio; o modelo final é ajustado no treino
inteiro. O teste não participa da seleção. Grade (árvores, profundidade
máxima, atributos por divisão): {grid}.

Modelos, grade, pares, métricas da comparação e regra de leitura foram fixados
antes da primeira execução. Commit e estado da árvore de cada grupo de
execuções:

{provenance_text(datasets)}

Todo valor abaixo é média ± desvio padrão entre as seeds, em percentual, salvo
onde a tabela diz outra unidade. O desvio padrão é o amostral. Uma seed
controla o split, a subamostra da seleção, os folds, a reamostragem e os
modelos: o desvio mistura essas fontes.

Comparação pareada. Método: {PAIRED_METHOD}. As diferenças de métrica estão em
pontos percentuais (pp) e as de tempo, em segundos. Regra de leitura:
{READING_RULE}. Ressalva: {e4r.PAIRED_CAVEAT}.

{sections}
{hypothesis_text(datasets)}
## O que não foi feito

- A explicabilidade do modelo proposto (importância global com `TreeExplainer`
  sobre {SELECTED}) não foi feita nesta execução.
- Não há ajuste de limiar de decisão nem variante que mantenha o SMOTE e só
  selecione hiperparâmetros.
- No combinado sem réplicas, M1, M1-prof5 e A-prof5 não foram rodados: só A e
  {SELECTED}.
- O recall de {SELECTED} nos fluxos do HKD não tem par nas mesmas seeds: o sistema
  do artigo só foi avaliado no HKD com a seed {SEED_FIEL}.

## Limitações

- A seleção de hiperparâmetros usa {MODIFIED_SELECTION_FRACTION:.0%} do treino, pelo custo. A
  combinação escolhida pode não ser a que venceria no treino inteiro.
- Há vetores de atributos repetidos dentro do treino. Na validação cruzada da
  seleção o mesmo vetor pode cair no fold de ajuste e no de validação, o que
  favorece árvores mais profundas; a avaliação no teste sem vetores repetidos
  só remove as linhas idênticas, não as parecidas.
- Os {len(seeds)} conjuntos de teste são sorteados da mesma tabela e se sobrepõem. O
  desvio padrão entre seeds mede a variação entre sorteios desta tabela, não a
  variação entre redes ou entre capturas.
- O tempo de treino de A no CIRA foi medido em outra execução, a do protocolo
  corrigido, com outra carga na máquina. A comparação de tempo é indicativa; a
  seção de tempo de treino do CIRA mostra o mesmo modelo reajustado.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o tráfego das outras duas classes. Nenhum split
  dentro do conjunto remove essa diferença.
"""


def load_refit_runs(e8_dir: Path, seeds: list[int]) -> dict:
    """Lê o run.json dos modelos do CIRA que vêm do protocolo corrigido e foram reajustados.

    O script da robustez reajusta esses modelos com todos os atributos, nas
    mesmas seeds e nos mesmos splits. Modelo sem essa execução fica de fora.
    """
    refit = {}
    for name in model_names("cira"):
        directory = e8_dir / rob.SLICE_NAME.format(model=name, columns="todos")
        if name not in MODIFIED_RUNS["cira"] and directory.exists():
            refit[name] = load_seeds(directory, seeds, "run.json")
    return {"cira": refit}


def write_summary(e8_dir: Path, e4_dir: Path, e6_transfer_file: Path, seeds: list[int]) -> dict:
    """Lê as execuções, grava summary.json e RESUMO.md em `e8_dir` e devolve a agregação."""
    loaded = {
        dataset: load_dataset(dataset, e8_dir, e4_dir, seeds) for dataset in MODIFIED_COMPARISONS
    }
    summary = summary_content(loaded, load_refit_runs(e8_dir, seeds))
    text = json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False)
    (e8_dir / "summary.json").write_text(text + "\n", encoding="utf-8")
    e6_transfer = json.loads(e6_transfer_file.read_text(encoding="utf-8"))["hkd"]
    (e8_dir / "RESUMO.md").write_text(summary_text(summary, e6_transfer), encoding="utf-8")
    return summary


def main() -> None:
    """Agrega as execuções gravadas de E8 e escreve summary.json e RESUMO.md."""
    summary = write_summary(E8_DIR, e8.E4_DIR, E6_TRANSFER_FILE, SEEDS_CORRIGIDA)
    for dataset in summary["datasets"].values():
        print(dataset["title"])
        print(paired_table(dataset["paired"]))
    print("\n".join(better_lines(summary["datasets"])))
    print(f"Escritos summary.json e RESUMO.md em {E8_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
