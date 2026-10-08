"""E8: agregação e resumo da robustez à manipulação da duração do fluxo.

Não treina nada. Lê os metrics.json e os run.json gravados por
scripts/e8_robustez.py em results/e8/corrigida/robustez-<modelo>-<colunas>/seed<k>/
e escreve em results/e8/corrigida/:

- summary-robustez.json: média e desvio padrão entre as seeds de cada modelo
  em cada conjunto de colunas, no teste sem perturbação e em cada fator de
  fragmentação, a descrição da perturbação e as comparações pareadas;
- RESUMO-ROBUSTEZ.md: a leitura dos números, ao lado da hipótese escrita antes
  da primeira execução (HIPOTESE-ROBUSTEZ.md, que este script não altera).

Roda como módulo, a partir da pasta do projeto, porque importa outros scripts.

Uso: uv run python -m scripts.e8_robustez_resumo
"""

import json
from itertools import combinations
from pathlib import Path

import numpy as np

import scripts.e4_resumo as e4r
import scripts.e8_robustez as rob
from doh_ids.config import (
    CLASS_NAMES,
    FEATURE_COLUMNS,
    FRAGMENTATION_FACTORS,
    FRAGMENTED_COLUMNS,
    PROJECT_ROOT,
    RESULTS_DIR,
    ROBUSTNESS_COLLAPSE_RECALL,
    ROBUSTNESS_COLUMN_PAIRS,
    ROBUSTNESS_COLUMN_SETS,
    ROBUSTNESS_INCOHERENT_FRACTION,
    ROBUSTNESS_MODEL_PAIR,
    ROBUSTNESS_MODELS,
    SEEDS_CORRIGIDA,
)
from doh_ids.evaluate import HIGHER, LOWER, aggregate_seeds, paired_comparison, paired_verdict
from doh_ids.summary import markdown_table

E8_DIR = RESULTS_DIR / rob.EXPERIMENT / rob.TRACK
RECALL = "malicious_doh_recall"
# Métricas do teste sem perturbação mostradas e comparadas na ablação.
CLEAN_METRICS = {
    "macro_f1": "F1 macro",
    "benign_doh_recall": "recall de Benign-DoH",
    RECALL: "recall de Malicious-DoH",
    "malicious_fpr": "FPR de Malicious-DoH",
}
# Fatores que perturbam o teste: todos menos o 1.
PERTURBED = [factor for factor in FRAGMENTATION_FACTORS if factor != 1]
# Modelos com expectativa declarada na hipótese.
MAIN_MODELS = list(ROBUSTNESS_MODEL_PAIR)[::-1]
# Queda de F1 macro, em fração, que a hipótese declara como inesperada na ablação.
UNEXPECTED_F1_DROP = 0.01

READING_RULE = (
    "uma diferença pareada conta quando a média é, em módulo, maior que o desvio padrão das "
    "diferenças entre as seeds; caso contrário os dois lados não se distinguem"
)
DESCRIPTIVE_NOTE = (
    "leitura descritiva acrescentada depois da execução: não faz parte da hipótese, não muda "
    "a regra de leitura nem os vereditos dela, e os limiares que usa foram escolhidos com os "
    "resultados à vista"
)


def slice_dir(e8_dir: Path, model: str, columns: str) -> Path:
    """Devolve o diretório das execuções de um modelo em um conjunto de colunas."""
    return e8_dir / rob.SLICE_NAME.format(model=model, columns=columns)


def load_runs(e8_dir: Path, seeds: list[int]) -> dict:
    """Lê as execuções gravadas: `{(modelo, colunas): {seed: (metrics, run)}}`.

    Modelo de `ROBUSTNESS_MODELS` sem nenhuma execução gravada fica de fora.
    """
    loaded = {}
    for model in ROBUSTNESS_MODELS:
        for columns in ROBUSTNESS_COLUMN_SETS:
            directory = slice_dir(e8_dir, model, columns)
            if not directory.exists():
                continue
            loaded[(model, columns)] = {
                seed: tuple(
                    json.loads((directory / f"seed{seed}" / name).read_text(encoding="utf-8"))
                    for name in ("metrics.json", "run.json")
                )
                for seed in seeds
            }
    return loaded


def recall_by_seed(runs: dict, factor: int) -> list[float]:
    """Devolve o recall de Malicious-DoH de cada seed em um fator de fragmentação."""
    return [
        metrics["fragmentation"][str(factor)]["malicious"]["recall"] for metrics, _ in runs.values()
    ]


def clean_by_seed(runs: dict, metric: str) -> list[float]:
    """Devolve uma métrica do teste sem perturbação em cada seed."""
    return [e4r.flat_metrics(metrics["test"])[metric] for metrics, _ in runs.values()]


def paired(values: list[float], reference: list[float], **labels) -> dict:
    """Compara dois lados seed a seed (`values` menos `reference`) e junta rótulos e veredito."""
    comparison = paired_comparison(values, reference)
    return {**labels, **comparison, "verdict": paired_verdict(comparison)}


def slice_summary(runs: dict) -> dict:
    """Resume as execuções de um modelo em um conjunto de colunas."""
    all_metrics = [metrics for metrics, _ in runs.values()]
    all_runs = [run for _, run in runs.values()]
    fragmentation = {}
    for factor in FRAGMENTATION_FACTORS:
        entries = [metrics["fragmentation"][str(factor)]["malicious"] for metrics in all_metrics]
        fragmentation[str(factor)] = {
            "recall": aggregate_seeds([{"recall": entry["recall"]} for entry in entries])["recall"],
            # O menor recall entre as seeds fica ao lado da média: uma seed em
            # que o modelo cede muito mais que nas outras some na média.
            "recall_min": min(entry["recall"] for entry in entries),
            "rows": aggregate_seeds([{"n": entry["n"]} for entry in entries])["n"],
            "predicted_as": aggregate_seeds([entry["predicted_as"] for entry in entries]),
        }
    config = all_runs[0]["config"]
    return {
        "n_features": config["n_features"],
        "features_examined_per_split": config["features_examined_per_split"],
        "dropped_features": config["dropped_features"],
        "clean": aggregate_seeds(
            [
                {key: e4r.flat_metrics(metrics["test"])[key] for key in CLEAN_METRICS}
                for metrics in all_metrics
            ]
        ),
        "fragmentation": fragmentation,
        "fit_seconds": aggregate_seeds(
            [{"fit": run["timings"]["fit_seconds"]} for run in all_runs]
        )["fit"],
        "commits": sorted({run["commit"] for run in all_runs}),
        "dirty_runs": sum(run["dirty"] for run in all_runs),
    }


def perturbation_summary(runs: dict) -> dict:
    """Resume, por fator, a descrição da perturbação gravada em cada seed."""
    summary = {}
    for factor in FRAGMENTATION_FACTORS:
        entries = [
            metrics["fragmentation"][str(factor)]["perturbation"] for metrics, _ in runs.values()
        ]
        columns = sorted(
            {name for entry in entries for name in entry["outside_train_range"]["by_column"]}
        )
        summary[str(factor)] = {
            **aggregate_seeds(
                [
                    {
                        "rows": entry["rows"],
                        "median_duration_seconds": entry["median_duration_seconds"],
                        "outside_row_fraction": entry["outside_train_range"]["row_fraction"],
                        "outside_value_fraction": entry["outside_train_range"]["values"]
                        / (entry["rows"] * len(FEATURE_COLUMNS)),
                        "incoherent_row_fraction": entry["packet_time_mean_above_duration"][
                            "row_fraction"
                        ],
                    }
                    for entry in entries
                ]
            ),
            # Média entre as seeds do número de fluxos com o atributo fora da
            # faixa do treino; atributo sem nenhum caso em nenhuma seed não entra.
            "outside_rows_by_column": {
                name: float(
                    np.mean(
                        [
                            entry["outside_train_range"]["by_column"].get(name, 0)
                            for entry in entries
                        ]
                    )
                )
                for name in columns
            },
        }
    return summary


def paired_rows(loaded: dict) -> dict:
    """Monta as comparações pareadas da ablação e da fragmentação."""
    models = sorted({model for model, _ in loaded}, key=ROBUSTNESS_MODELS.index)
    ablation, degradation, between_columns, between_models = [], [], [], []
    for model in models:
        for columns, reference in ROBUSTNESS_COLUMN_PAIRS:
            first, second = loaded[(model, columns)], loaded[(model, reference)]
            ablation += [
                paired(
                    clean_by_seed(first, metric),
                    clean_by_seed(second, metric),
                    model=model,
                    first=columns,
                    second=reference,
                    metric=metric,
                )
                for metric in CLEAN_METRICS
            ]
            between_columns += [
                paired(
                    recall_by_seed(first, factor),
                    recall_by_seed(second, factor),
                    model=model,
                    first=columns,
                    second=reference,
                    factor=factor,
                )
                for factor in PERTURBED
            ]
        for columns in ROBUSTNESS_COLUMN_SETS:
            runs = loaded[(model, columns)]
            degradation += [
                paired(
                    recall_by_seed(runs, factor),
                    recall_by_seed(runs, 1),
                    model=model,
                    columns=columns,
                    factor=factor,
                )
                for factor in PERTURBED
            ]
    first_model, second_model = ROBUSTNESS_MODEL_PAIR
    for columns in ROBUSTNESS_COLUMN_SETS:
        between_models += [
            paired(
                recall_by_seed(loaded[(first_model, columns)], factor),
                recall_by_seed(loaded[(second_model, columns)], factor),
                first=first_model,
                second=second_model,
                columns=columns,
                factor=factor,
            )
            for factor in FRAGMENTATION_FACTORS
        ]
    return {
        "ablation": ablation,
        "degradation": degradation,
        "between_columns": between_columns,
        "between_models": between_models,
    }


def collapse_by_factor(recalls: dict, seeds: list[int]) -> dict:
    """Conta, em cada fator perturbado, as seeds com recall abaixo do limiar de colapso.

    `recalls[fator]` tem o recall de cada seed, na ordem de `seeds`. Devolve,
    por fator, as seeds abaixo do limiar e o menor e o maior recall das demais.
    """
    summary = {}
    for factor in PERTURBED:
        values = recalls[str(factor)]
        others = [value for value in values if value >= ROBUSTNESS_COLLAPSE_RECALL]
        summary[str(factor)] = {
            "seeds_below": [
                seed
                for seed, value in zip(seeds, values, strict=True)
                if value < ROBUSTNESS_COLLAPSE_RECALL
            ],
            "others_min": min(others, default=None),
            "others_max": max(others, default=None),
        }
    return summary


def seed_rises(recalls: dict, seeds: list[int]) -> list[dict]:
    """Lista as vezes em que o recall de uma seed sobe de um fator para o seguinte."""
    rises = []
    for index, seed in enumerate(seeds):
        for before, after in zip(FRAGMENTATION_FACTORS, FRAGMENTATION_FACTORS[1:], strict=False):
            difference = recalls[str(after)][index] - recalls[str(before)][index]
            if difference > 0:
                rises.append({"seed": seed, "from": before, "to": after, "difference": difference})
    return rises


def column_effect(loaded: dict, models: list[str]) -> list[dict]:
    """Mede, por modelo e fator, o efeito de retirar colunas no recall sob fragmentação.

    Para cada par de `ROBUSTNESS_COLUMN_PAIRS`, devolve a diferença média de
    recall (sem as colunas menos com todas), em quantas seeds ela é positiva e
    negativa e a menor e a maior diferença entre as seeds.
    """
    rows = []
    for model in models:
        for columns, reference in ROBUSTNESS_COLUMN_PAIRS:
            for factor in PERTURBED:
                difference = np.subtract(
                    recall_by_seed(loaded[(model, columns)], factor),
                    recall_by_seed(loaded[(model, reference)], factor),
                )
                rows.append(
                    {
                        "model": model,
                        "first": columns,
                        "second": reference,
                        "factor": factor,
                        "mean_difference": float(difference.mean()),
                        "seeds_higher": int((difference > 0).sum()),
                        "seeds_lower": int((difference < 0).sum()),
                        "min_difference": float(difference.min()),
                        "max_difference": float(difference.max()),
                    }
                )
    return rows


def identical_clean_matrices(loaded: dict, models: list[str]) -> list[dict]:
    """Lista os pares de conjuntos de colunas com a mesma matriz no teste sem perturbação.

    Só entra o par em que as matrizes de confusão são iguais em todas as
    seeds. Devolve também em quantas seeds as predições dos fluxos
    fragmentados diferem: matriz igual não quer dizer modelo igual.
    """
    rows = []
    for model in models:
        for first, second in combinations(ROBUSTNESS_COLUMN_SETS, 2):
            pairs = [
                (one, other)
                for (one, _), (other, _) in zip(
                    loaded[(model, first)].values(), loaded[(model, second)].values(), strict=True
                )
            ]
            if all(
                one["test"]["confusion_matrix"] == other["test"]["confusion_matrix"]
                for one, other in pairs
            ):
                differing = sum(
                    any(
                        one["fragmentation"][str(factor)]["malicious"]
                        != other["fragmentation"][str(factor)]["malicious"]
                        for factor in PERTURBED
                    )
                    for one, other in pairs
                )
                rows.append(
                    {
                        "model": model,
                        "first": first,
                        "second": second,
                        "seeds_with_other_fragmented_predictions": differing,
                    }
                )
    return rows


def descriptive_findings(loaded: dict, seeds: list[int]) -> dict:
    """Calcula a leitura descritiva acrescentada depois da execução.

    Devolve o recall de cada seed em cada fator, as seeds abaixo do limiar de
    colapso, as subidas de recall por seed, o efeito de retirar colunas por
    modelo e os pares de conjuntos de colunas com a mesma matriz no teste.
    """
    models = sorted({model for model, _ in loaded}, key=ROBUSTNESS_MODELS.index)
    recalls = {
        model: {
            columns: {
                str(factor): recall_by_seed(loaded[(model, columns)], factor)
                for factor in FRAGMENTATION_FACTORS
            }
            for columns in ROBUSTNESS_COLUMN_SETS
        }
        for model in models
    }
    return {
        "note": DESCRIPTIVE_NOTE,
        "collapse_recall": ROBUSTNESS_COLLAPSE_RECALL,
        "incoherent_fraction": ROBUSTNESS_INCOHERENT_FRACTION,
        "recall_by_seed": recalls,
        "collapse": {
            model: {columns: collapse_by_factor(entry, seeds) for columns, entry in by.items()}
            for model, by in recalls.items()
        },
        "rises_by_seed": {
            model: {columns: seed_rises(entry, seeds) for columns, entry in by.items()}
            for model, by in recalls.items()
        },
        "column_effect": column_effect(loaded, models),
        "identical_clean_matrices": identical_clean_matrices(loaded, models),
    }


def summary_content(loaded: dict, seeds: list[int]) -> dict:
    """Monta o conteúdo de summary-robustez.json a partir das execuções lidas."""
    for runs in loaded.values():
        for seed, (metrics, _) in runs.items():
            reference = loaded[(ROBUSTNESS_MODEL_PAIR[1], "todos")][seed][0]
            # A comparação pareada só vale com todos os modelos da seed
            # avaliados nas mesmas linhas, com a mesma perturbação.
            assert metrics["split_index_sha256"] == reference["split_index_sha256"]
            for factor in FRAGMENTATION_FACTORS:
                assert (
                    metrics["fragmentation"][str(factor)]["perturbation"]
                    == reference["fragmentation"][str(factor)]["perturbation"]
                )
    models = {}
    for (model, columns), runs in loaded.items():
        models.setdefault(model, {})[columns] = slice_summary(runs)
    paired_all = paired_rows(loaded)
    return {
        "experiment": rob.EXPERIMENT,
        "track": rob.TRACK,
        "dataset": "cira",
        "seeds": seeds,
        "factors": FRAGMENTATION_FACTORS,
        "fragmented_columns": FRAGMENTED_COLUMNS,
        "column_sets": ROBUSTNESS_COLUMN_SETS,
        "models_not_run": [name for name in ROBUSTNESS_MODELS if name not in models],
        "models": models,
        "perturbation": perturbation_summary(loaded[(ROBUSTNESS_MODEL_PAIR[1], "todos")]),
        "reading_rule": READING_RULE,
        "paired_method": e4r.PAIRED_METHOD,
        "paired_caveat": e4r.PAIRED_CAVEAT,
        "paired": paired_all,
        "hypothesis": hypothesis_findings(models, paired_all),
        "descriptive": descriptive_findings(loaded, seeds),
    }


def slices(summary: dict) -> list[tuple[str, str, dict]]:
    """Lista os pares de modelo e colunas do resumo, na ordem da configuração."""
    return [
        (model, columns, entry)
        for model, by_columns in summary["models"].items()
        for columns, entry in by_columns.items()
    ]


def clean_table(summary: dict) -> str:
    """Escreve a tabela da ablação: cada modelo e conjunto de colunas no teste sem perturbação."""
    rows = [
        [
            model,
            f"`{columns}`",
            entry["n_features"],
            entry["features_examined_per_split"],
            *[e4r.mean_std(entry["clean"][metric], 4) for metric in CLEAN_METRICS],
            f"{entry['fit_seconds']['mean']:.1f}",
        ]
        for model, columns, entry in slices(summary)
    ]
    columns = [
        "modelo",
        "colunas",
        "atributos",
        "atributos examinados por divisão",
        *CLEAN_METRICS.values(),
        "ajuste (s, média)",
    ]
    return markdown_table(columns, rows)


def paired_cells(row: dict) -> list:
    """Escreve as células comuns a toda linha de comparação pareada."""
    tested = row["wilcoxon_p_value"] is not None
    return [
        f"{100 * row['mean_difference']:+.4f} pp",
        f"{100 * row['std_difference']:.4f} pp",
        row["first_wins"],
        row["second_wins"],
        row["ties"],
        f"{row['wilcoxon_p_value']:.4f}" if tested else "sem diferença a ordenar",
        f"**{row['verdict']}**",
    ]


PAIRED_COLUMNS = [
    "diferença média",
    "desvio padrão das diferenças",
    "seeds com o primeiro maior",
    "seeds com o segundo maior",
    "empates",
    "p-valor de Wilcoxon",
    "o primeiro é",
]


def ablation_table(rows: list[dict]) -> str:
    """Escreve a comparação pareada da ablação, no teste sem perturbação."""
    lines = [
        [
            row["model"],
            f"`{row['first']}` menos `{row['second']}`",
            CLEAN_METRICS[row["metric"]],
            *paired_cells(row),
        ]
        for row in rows
    ]
    return markdown_table(["modelo", "par", "métrica", *PAIRED_COLUMNS], lines)


def recall_table(summary: dict) -> str:
    """Escreve o recall de Malicious-DoH de cada modelo em cada fator de fragmentação."""
    rows = []
    for model, columns, entry in slices(summary):
        cells = []
        for factor in FRAGMENTATION_FACTORS:
            fragment = entry["fragmentation"][str(factor)]
            cells.append(
                f"{e4r.mean_std(fragment['recall'])} (mín. {100 * fragment['recall_min']:.3f})"
            )
        rows.append([model, f"`{columns}`", *cells])
    factors = ["fator 1 (sem perturbação)", *[f"fator {factor}" for factor in PERTURBED]]
    return markdown_table(["modelo", "colunas", *factors], rows)


def missed_table(summary: dict) -> str:
    """Escreve para que classe vão os fluxos Malicious-DoH não detectados, por fator."""
    rows = []
    for model, columns, entry in slices(summary):
        for factor in FRAGMENTATION_FACTORS:
            fragment = entry["fragmentation"][str(factor)]
            rows.append(
                [
                    model,
                    f"`{columns}`",
                    factor,
                    f"{fragment['rows']['mean']:.1f}",
                    *[
                        f"{fragment['predicted_as'][name]['mean']:.1f} ± "
                        f"{fragment['predicted_as'][name]['std']:.1f}"
                        for name in CLASS_NAMES
                    ],
                ]
            )
    columns = [
        "modelo",
        "colunas",
        "fator",
        "fluxos Malicious-DoH no teste",
        *[f"preditos como {name}" for name in CLASS_NAMES],
    ]
    return markdown_table(columns, rows)


def perturbation_table(perturbation: dict) -> str:
    """Escreve a descrição da perturbação em cada fator."""
    rows = []
    for factor in FRAGMENTATION_FACTORS:
        entry = perturbation[str(factor)]
        by_column = ", ".join(
            f"`{name}` {rows_mean:.1f}"
            for name, rows_mean in entry["outside_rows_by_column"].items()
        )
        rows.append(
            [
                factor,
                f"{entry['median_duration_seconds']['mean']:.2f}",
                e4r.mean_std(entry["outside_row_fraction"]),
                e4r.mean_std(entry["outside_value_fraction"], 4),
                by_column or "nenhum",
                e4r.mean_std(entry["incoherent_row_fraction"]),
            ]
        )
    columns = [
        "fator",
        "mediana da duração dos maliciosos (s)",
        "fluxos maliciosos com algum valor fora da faixa do treino (%)",
        "valores fora da faixa, entre todos os valores dos fluxos maliciosos (%)",
        "fluxos fora da faixa, por atributo",
        "fluxos com tempo médio de pacote maior que a duração (%)",
    ]
    return markdown_table(columns, rows)


def factor_table(rows: list[dict], label_columns: list[str], labels) -> str:
    """Escreve uma comparação pareada de recall por fator; `labels` monta os rótulos da linha."""
    lines = [[*labels(row), row["factor"], *paired_cells(row)] for row in rows]
    return markdown_table([*label_columns, "fator", *PAIRED_COLUMNS], lines)


def select(rows: list[dict], **labels) -> list[dict]:
    """Devolve as comparações cujos rótulos são os dados."""
    return [row for row in rows if all(row[key] == value for key, value in labels.items())]


def recall_rises(entry: dict) -> bool:
    """Diz se o recall médio de um modelo sobe de algum fator para o seguinte."""
    means = [
        entry["fragmentation"][str(factor)]["recall"]["mean"] for factor in FRAGMENTATION_FACTORS
    ]
    return bool((np.diff(means) > 0).any())


def factors_with(rows: list[dict], wanted: str) -> list[int]:
    """Devolve os fatores perturbados em que a comparação tem o veredito `wanted`."""
    return [row["factor"] for row in rows if row["factor"] != 1 and row["verdict"] == wanted]


def in_factors(factors: list[int]) -> str:
    """Escreve em que fatores algo ocorre: "nos fatores 2, 4", "no fator 2" ou "em nenhum fator"."""
    if not factors:
        return "em nenhum fator"
    if len(factors) == 1:
        return f"no fator {factors[0]}"
    return "nos fatores " + ", ".join(str(factor) for factor in factors)


def hypothesis_findings(models: dict, paired_all: dict) -> dict:
    """Calcula o que cada expectativa da hipótese precisa para ser conferida.

    `models` e `paired_all` são as agregações por modelo e as comparações
    pareadas. As expectativas só falam do sistema do artigo e do modelo proposto.
    """
    ablation = {}
    for model in MAIN_MODELS:
        rows = [
            row
            for row in select(paired_all["ablation"], model=model)
            if row["metric"] in ("macro_f1", RECALL)
        ]
        ablation[model] = {
            "small_or_no_loss": all(
                row["verdict"] != LOWER or abs(row["mean_difference"]) < UNEXPECTED_F1_DROP
                for row in rows
            ),
            "largest_macro_f1_drop": min(
                row["mean_difference"] for row in rows if row["metric"] == "macro_f1"
            ),
        }

    between_models = select(paired_all["between_models"], columns="todos")
    column_rows = [row for row in paired_all["between_columns"] if row["model"] in MAIN_MODELS]
    reduced = [
        row
        for row in paired_all["degradation"]
        if row["model"] in MAIN_MODELS and row["columns"] != "todos"
    ]
    # Fluxos maliciosos não detectados, por classe atribuída: soma, nos
    # modelos com todos os atributos e nos fatores perturbados, da média por seed.
    missed = {
        name: sum(
            models[model]["todos"]["fragmentation"][str(factor)]["predicted_as"][name]["mean"]
            for model in MAIN_MODELS
            for factor in PERTURBED
        )
        for name in ("Non-DoH", "Benign-DoH")
    }
    return {
        "ablation": ablation,
        "degrades_in_factors": {
            model: factors_with(
                select(paired_all["degradation"], model=model, columns="todos"), LOWER
            )
            for model in MAIN_MODELS
        },
        "recall_rises": {model: recall_rises(models[model]["todos"]) for model in MAIN_MODELS},
        "modification_higher_in_factors": factors_with(between_models, HIGHER),
        "modification_lower_in_factors": factors_with(between_models, LOWER),
        "column_comparisons": len(column_rows),
        "reduced_columns_higher": sum(row["verdict"] == HIGHER for row in column_rows),
        "reduced_columns_lower": sum(row["verdict"] == LOWER for row in column_rows),
        "reduced_models_degrading": sum(row["verdict"] == LOWER for row in reduced),
        "reduced_model_comparisons": len(reduced),
        "missed_mean_rows": missed,
        "any_model_degrades": any(row["verdict"] == LOWER for row in paired_all["degradation"]),
        "slices_with_rising_recall": [
            f"{model} `{columns}`"
            for model, by_columns in models.items()
            for columns, entry in by_columns.items()
            if recall_rises(entry)
        ],
    }


def expected_lines(found: dict) -> list[str]:
    """Escreve cada expectativa da hipótese ao lado do que ocorreu."""
    first_model, second_model = ROBUSTNESS_MODEL_PAIR
    lines = []
    for number, model in enumerate(MAIN_MODELS, start=1):
        entry = found["ablation"][model]
        lines.append(
            f"{number}. Parte A, {model}: sem as colunas, F1 macro e recall de Malicious-DoH "
            f"não se distinguem dos do modelo com todos os atributos ou caem menos de 1 pp: "
            f"{e4r.occurred(entry['small_or_no_loss'])}. Menor diferença média de F1 macro, "
            f"sem as colunas menos com todas: {100 * entry['largest_macro_f1_drop']:+.4f} pp."
        )
    degrades = found["degrades_in_factors"]
    higher, lower = found["modification_higher_in_factors"], found["modification_lower_in_factors"]
    missed = found["missed_mean_rows"]
    lines += [
        f"3. Parte B, {second_model} com todos os atributos degrada em todos os fatores a partir "
        f"de 2: {e4r.occurred(degrades[second_model] == PERTURBED)} (degrada "
        f"{in_factors(degrades[second_model])}); o recall não aumenta de um fator para o "
        f"seguinte: {e4r.occurred(not found['recall_rises'][second_model])}.",
        f"4. Parte B, {first_model} com todos os atributos degrada em todos os fatores a partir "
        f"de 2: {e4r.occurred(degrades[first_model] == PERTURBED)} (pela regra, degrada "
        f"{in_factors(degrades[first_model])}); resiste melhor que {second_model} em todos "
        f"eles: {e4r.occurred(higher == PERTURBED)} (recall maior {in_factors(higher)}, menor "
        f"{in_factors(lower)}). Estes são os vereditos da regra de leitura; o recall de "
        f"{first_model} em cada seed e a contagem das quedas estão na leitura descritiva, abaixo.",
        f"5. Parte B, os modelos sem `Duration` resistem melhor que o mesmo modelo com todos os "
        f"atributos: "
        f"{e4r.occurred(found['reduced_columns_higher'] == found['column_comparisons'])} "
        f"(recall maior em {found['reduced_columns_higher']} das "
        f"{found['column_comparisons']} comparações de {' e '.join(MAIN_MODELS)}, menor em "
        f"{found['reduced_columns_lower']}); e não ficam imunes: "
        f"{e4r.occurred(found['reduced_models_degrading'] > 0)} (degradam em "
        f"{found['reduced_models_degrading']} das {found['reduced_model_comparisons']} "
        f"combinações de modelo, colunas e fator). A-prof5 fica fora dessas contagens, porque a "
        f"hipótese só declara expectativa para {' e '.join(MAIN_MODELS)}; os três modelos "
        f"estão, em separado, na leitura descritiva, abaixo.",
        f"6. Os fluxos não detectados vão mais para Non-DoH do que para Benign-DoH: "
        f"{e4r.occurred(missed['Non-DoH'] > missed['Benign-DoH'])}. Somando "
        f"{' e '.join(MAIN_MODELS)} com todos os atributos nos fatores a partir de 2, a média "
        f"por seed é de {missed['Non-DoH']:.1f} fluxos preditos como Non-DoH e "
        f"{missed['Benign-DoH']:.1f} como Benign-DoH.",
    ]
    return lines


def rises_text(rises_by_seed: dict) -> str:
    """Escreve as vezes em que o recall de uma seed sobe de um fator para o seguinte."""
    cells = [
        f"{model} `{columns}`, seed {rise['seed']}, do fator {rise['from']} para o {rise['to']} "
        f"({100 * rise['difference']:+.2f} pp)"
        for model, by_columns in rises_by_seed.items()
        for columns, rises in by_columns.items()
        for rise in rises
    ]
    return "; ".join(cells) or "em nenhuma seed"


def unexpected_lines(found: dict, descriptive: dict) -> list[str]:
    """Escreve cada resultado que a hipótese declarou como inesperado e se ele ocorreu."""
    first_model, second_model = ROBUSTNESS_MODEL_PAIR
    rising, lower = found["slices_with_rising_recall"], found["modification_lower_in_factors"]
    missed = found["missed_mean_rows"]
    # A regra só diz "pior" ou "melhor" quando a média passa do desvio: sem
    # veredito de "menor" em nenhum fator e sem "maior" em todos, ela não
    # sustenta nenhuma das duas direções.
    undecided = not lower and found["modification_higher_in_factors"] != PERTURBED
    f1_lines = []
    for model in MAIN_MODELS:
        lost = found["ablation"][model]["largest_macro_f1_drop"] < -UNEXPECTED_F1_DROP
        f1_lines.append(
            f"- {model} perder mais de 1 pp de F1 macro sem `Duration` no teste sem "
            f"perturbação: {e4r.occurred(lost)}."
        )
    return [
        *f1_lines,
        f"- Nenhum modelo degradar em nenhum fator: "
        f"{e4r.occurred(not found['any_model_degrades'])}.",
        f"- O recall médio de um modelo subir de um fator para o seguinte: "
        f"{e4r.occurred(bool(rising))}"
        + (f" ({', '.join(rising)})." if rising else ".")
        + " O item fala da média. Olhando cada seed, na leitura descritiva acrescentada depois "
        f"da execução, o recall sobe em: {rises_text(descriptive['rises_by_seed'])}.",
        f"- {first_model} resistir pior que {second_model}: {e4r.occurred(bool(lower))}"
        + (f" ({in_factors(lower)})." if lower else ".")
        + (
            " É o veredito da regra; pela leitura descritiva, abaixo, nenhuma direção é sustentada."
            if undecided
            else ""
        ),
        f"- Um modelo sem `Duration` resistir pior que o mesmo modelo com todos os atributos: "
        f"{e4r.occurred(found['reduced_columns_lower'] > 0)} "
        f"({found['reduced_columns_lower']} das {found['column_comparisons']} comparações).",
        f"- A maior parte dos fluxos não detectados ir para Benign-DoH: "
        f"{e4r.occurred(missed['Benign-DoH'] > missed['Non-DoH'])}.",
    ]


def hypothesis_text(found: dict, descriptive: dict) -> str:
    """Escreve a seção que põe a hipótese ao lado do resultado."""
    lines = [
        "## Hipótese ao lado do resultado",
        "",
        "Expectativas de `HIPOTESE-ROBUSTEZ.md`:",
        "",
        *expected_lines(found),
        "",
        "Resultados que a hipótese declarou como inesperados:",
        "",
        *unexpected_lines(found, descriptive),
    ]
    return "\n".join(lines) + "\n"


def seed_recall_table(recalls: dict, seeds: list[int]) -> str:
    """Escreve o recall de Malicious-DoH de um modelo em cada seed e fator, em percentual."""
    rows = [
        [seed, *[f"{100 * recalls[str(factor)][index]:.2f}" for factor in FRAGMENTATION_FACTORS]]
        for index, seed in enumerate(seeds)
    ]
    return markdown_table(["seed", *[f"fator {factor}" for factor in FRAGMENTATION_FACTORS]], rows)


def collapse_lines(summary: dict, model: str) -> list[str]:
    """Escreve, por fator, em quantas seeds o recall de `model` cai e em quantas colapsa."""
    seeds, limit = summary["seeds"], summary["descriptive"]["collapse_recall"]
    lines = []
    for row in select(summary["paired"]["degradation"], model=model, columns="todos"):
        entry = summary["descriptive"]["collapse"][model]["todos"][str(row["factor"])]
        below = entry["seeds_below"]
        line = (
            f"- Fator {row['factor']}: o recall é menor que o do fator 1 em {row['second_wins']} "
            f"das {len(seeds)} seeds; fica abaixo de {limit:.0%} em {len(below)}"
        )
        if below:
            line += f" (seeds {', '.join(str(seed) for seed in below)})"
        if entry["others_min"] is not None:
            line += (
                f"; nas {'demais' if below else len(seeds)}, vai de "
                f"{100 * entry['others_min']:.2f}% a {100 * entry['others_max']:.2f}%"
            )
        lines.append(line + ".")
    return lines


def direction_text(summary: dict) -> str:
    """Escreve o que se pode dizer da direção da diferença entre a modificação e o original."""
    first_model, second_model = ROBUSTNESS_MODEL_PAIR
    found = summary["hypothesis"]
    higher, lower = found["modification_higher_in_factors"], found["modification_lower_in_factors"]
    rows = select(summary["paired"]["between_models"], columns="todos")
    wins = "; ".join(
        f"fator {row['factor']}, acima em {row['first_wins']} seeds e abaixo em "
        f"{row['second_wins']}"
        for row in rows
        if row["factor"] != 1
    )
    text = (
        f"{first_model} contra {second_model}, com todos os atributos: pela regra, o recall de "
        f"{first_model} é maior {in_factors(higher)} e menor {in_factors(lower)}. Seed a seed, "
        f"{first_model} fica acima ou abaixo de {second_model} assim: {wins}."
    )
    if higher != PERTURBED and lower != PERTURBED:
        text += (
            " Nenhuma direção é sustentada: a modificação não é nem mais robusta, nem menos, "
            "que o original."
        )
    return text


def column_effect_table(rows: list[dict]) -> str:
    """Escreve o efeito de retirar colunas no recall sob fragmentação, por modelo e fator."""
    lines = [
        [
            row["model"],
            f"`{row['first']}` menos `{row['second']}`",
            row["factor"],
            f"{100 * row['mean_difference']:+.4f} pp",
            row["seeds_higher"],
            row["seeds_lower"],
            f"{100 * row['min_difference']:+.4f} pp",
            f"{100 * row['max_difference']:+.4f} pp",
        ]
        for row in rows
    ]
    columns = [
        "modelo",
        "par",
        "fator",
        "diferença média",
        "seeds com recall maior sem as colunas",
        "seeds com recall menor sem as colunas",
        "menor diferença entre as seeds",
        "maior diferença entre as seeds",
    ]
    return markdown_table(columns, lines)


def seed_range(counts: list[int]) -> str:
    """Escreve a faixa de uma contagem de seeds: "9 a 10", ou só "10" quando não varia."""
    low, high = min(counts), max(counts)
    return str(low) if low == high else f"{low} a {high}"


def column_effect_lines(summary: dict) -> list[str]:
    """Escreve, modelo a modelo, se retirar colunas ajuda ou piora o recall sob fragmentação."""
    rows, n_seeds = summary["descriptive"]["column_effect"], len(summary["seeds"])
    lines, helped, hurt = [], [], []
    for model in summary["models"]:
        own = select(rows, model=model)
        means = [row["mean_difference"] for row in own]
        positive = sum(mean > 0 for mean in means)
        if positive == len(own):
            helped.append(model)
        elif positive == 0:
            hurt.append(model)
        verdicts = [
            row["verdict"] for row in select(summary["paired"]["between_columns"], model=model)
        ]
        higher = [row["seeds_higher"] for row in own]
        lines.append(
            f"- {model}: diferença média positiva em {positive} das {len(own)} comparações (de "
            f"{100 * min(means):+.2f} a {100 * max(means):+.2f} pp); recall maior sem as colunas "
            f"em {seed_range(higher)} das {n_seeds} seeds, conforme a comparação; menor "
            f"diferença em uma seed, {100 * min(row['min_difference'] for row in own):+.2f} pp. "
            f"Vereditos da regra: maior em {verdicts.count(HIGHER)}, menor em "
            f"{verdicts.count(LOWER)}, não se distinguem em "
            f"{len(verdicts) - verdicts.count(HIGHER) - verdicts.count(LOWER)}."
        )
    if helped and hurt:
        lines.append(
            "\nO efeito tem sinais opostos: retirar as colunas aumenta o recall sob fragmentação "
            f"em {' e '.join(helped)} e diminui em {' e '.join(hurt)}. A causa não foi "
            "investigada."
        )
    return lines


def incoherence_text(summary: dict) -> str:
    """Liga a fração de vetores incoerentes de cada fator ao que se pode ler do recall."""
    first_model, _ = ROBUSTNESS_MODEL_PAIR
    limit = summary["descriptive"]["incoherent_fraction"]
    fraction = {
        factor: summary["perturbation"][str(factor)]["incoherent_row_fraction"]
        for factor in PERTURBED
    }
    by_factor = "; ".join(
        f"fator {factor}, {100 * entry['mean']:.2f}%" for factor, entry in fraction.items()
    )
    coherent = [factor for factor, entry in fraction.items() if entry["mean"] < 0.5]
    outside = [factor for factor, entry in fraction.items() if entry["mean"] > limit]
    drops = "; ".join(
        f"{model}, fator {row['factor']}, {100 * row['mean_difference']:+.2f} pp"
        for model in MAIN_MODELS
        for row in select(summary["paired"]["degradation"], model=model, columns="todos")
        if row["factor"] in coherent
    )
    recall_std = max(
        summary["models"][first_model]["todos"]["fragmentation"][str(factor)]["recall"]["std"]
        for factor in PERTURBED
    )
    fraction_std = max(entry["std"] for entry in fraction.values())
    return (
        "Fração dos vetores Malicious-DoH do teste com tempo médio de pacote maior que a "
        f"duração, média entre as seeds: {by_factor}. A maioria dos vetores continua coerente só "
        f"{in_factors(coherent)}; aí, a diferença de recall para o fator 1, com todos os "
        f"atributos, é: {drops or 'nenhuma a mostrar'}. Com mais de {limit:.0%} dos vetores "
        f"incoerentes, o que ocorre {in_factors(outside)}, o recall descreve o modelo fora da "
        "região de fluxos possíveis, e não a resposta dele a fluxos fragmentados.\n\n"
        f"A relação entre a incoerência e o colapso de {first_model} em algumas seeds não foi "
        "investigada. A fração incoerente é quase a mesma em todas as seeds (desvio padrão de "
        f"no máximo {100 * fraction_std:.2f} pp), e o recall de {first_model} com todos os "
        f"atributos tem desvio padrão de até {100 * recall_std:.2f} pp: o que muda de uma seed "
        "para outra é o split e o modelo ajustado, não a proporção de vetores incoerentes."
    )


def missed_by_factor_text(summary: dict) -> str:
    """Escreve, por modelo e fator, para que classe vão os fluxos não detectados."""
    cells, benign_first = [], []
    for model in MAIN_MODELS:
        for factor in PERTURBED:
            predicted = summary["models"][model]["todos"]["fragmentation"][str(factor)][
                "predicted_as"
            ]
            non_doh, benign = predicted["Non-DoH"]["mean"], predicted["Benign-DoH"]["mean"]
            cells.append(f"{model}, fator {factor}, {non_doh:.1f} e {benign:.1f}")
            if benign > non_doh:
                benign_first.append(f"{model} no fator {factor}")
    return (
        "O item 6 da hipótese soma os fatores. Por fator, com todos os atributos, a média por "
        f"seed de fluxos preditos como Non-DoH e como Benign-DoH é: {'; '.join(cells)}. Vão "
        "mais fluxos para Benign-DoH do que para Non-DoH em: "
        f"{', '.join(benign_first) or 'nenhum caso'}."
    )


def identical_text(summary: dict) -> str:
    """Escreve a frase sobre conjuntos de colunas com a mesma matriz no teste, se houver."""
    lines = [
        f"{row['model']}: `{row['first']}` e `{row['second']}` têm a mesma matriz de confusão "
        f"no teste sem perturbação nas {len(summary['seeds'])} seeds, e por isso as linhas dos "
        "dois são iguais nas tabelas desta parte. Os dois modelos não são o mesmo: as predições "
        f"dos fluxos fragmentados diferem em {row['seeds_with_other_fragmented_predictions']} "
        "seeds."
        for row in summary["descriptive"]["identical_clean_matrices"]
    ]
    if not lines:
        return ""
    return "Nota acrescentada depois da execução. " + " ".join(lines) + "\n\n"


def descriptive_text(summary: dict) -> str:
    """Escreve a seção da leitura descritiva acrescentada depois da execução."""
    first_model, _ = ROBUSTNESS_MODEL_PAIR
    descriptive, seeds = summary["descriptive"], summary["seeds"]
    return f"""## Leitura descritiva acrescentada depois da execução

Tudo nesta seção é {DESCRIPTIVE_NOTE}. Os números saem dos mesmos
`metrics.json`; nenhuma execução foi refeita. O mínimo entre as seeds e a nota
de leitura da tabela de recall por fator também foram acrescentados depois da
execução, sem mudar a regra nem os vereditos.

### Recall de {first_model} com todos os atributos, em cada seed

Em percentual. A regra de leitura diz "não se distinguem" quando a média não
passa do desvio; a tabela mostra o que há por trás da média.

{seed_recall_table(descriptive["recall_by_seed"][first_model]["todos"], seeds)}

{chr(10).join(collapse_lines(summary, first_model))}

O limiar de {descriptive["collapse_recall"]:.0%} é descritivo e foi escolhido depois de ver os
resultados: com outro limiar, a contagem muda.

{direction_text(summary)}

### Retirar `Duration`, modelo a modelo

Recall de Malicious-DoH sem as colunas menos o do mesmo modelo com todas, em
cada fator. A hipótese só fala de {" e ".join(MAIN_MODELS)}; aqui estão os três modelos.

{column_effect_table(descriptive["column_effect"])}

{chr(10).join(column_effect_lines(summary))}

### A incoerência dos vetores e o que se pode ler

{incoherence_text(summary)}

### Destino dos fluxos não detectados, por fator

{missed_by_factor_text(summary)}
"""


def provenance_text(summary: dict) -> str:
    """Escreve o commit e o estado da árvore com que cada grupo de execuções foi gravado."""
    return "\n".join(
        f"- {model}, `{columns}`: commit "
        f"{', '.join(f'`{commit[:7]}`' for commit in entry['commits'])}; execuções com a árvore "
        f"suja: {entry['dirty_runs']}."
        for model, columns, entry in slices(summary)
    )


def summary_text(summary: dict) -> str:
    """Escreve o RESUMO-ROBUSTEZ.md a partir da agregação."""
    seeds, paired_all = summary["seeds"], summary["paired"]
    first_model, second_model = ROBUSTNESS_MODEL_PAIR
    fragmented = ", ".join(f"`{name}`" for name in FRAGMENTED_COLUMNS)
    not_run = summary["models_not_run"]
    not_run_text = (
        f"- Modelos de `ROBUSTNESS_MODELS` sem execução gravada: {', '.join(not_run)}.\n"
        if not_run
        else ""
    )
    return f"""# E8: robustez à manipulação da duração do fluxo

Gerado por `scripts/e8_robustez_resumo.py` a partir dos arquivos gravados por
`scripts/e8_robustez.py`. Trilha `corrigida`. Dados: CIRA-CIC-DoHBrw-2020,
{len(seeds)} seeds ({seeds[0]} a {seeds[-1]}), split 90/10 estratificado refeito em cada seed.
A hipótese, o modelo de ameaça e as simplificações foram escritos antes da
primeira execução, em `HIPOTESE-ROBUSTEZ.md`.

**Como ler este arquivo.** A parte B é uma perturbação no espaço de atributos,
não um ataque reproduzido em rede. Nenhum tráfego foi gerado e nenhum PCAP foi
reprocessado: os fluxos Malicious-DoH do teste tiveram {fragmented} divididos
por um fator, e os outros atributos ficaram como estavam. Os números da parte
B são um limite aproximado do efeito de encurtar os fluxos, não a medição de
um ataque.

## O que foi medido

- **Modelos.** {second_model} é o sistema empilhado do artigo com os Random Forests base
  sem limite de profundidade (o original); {first_model} é o modelo proposto pela equipe,
  um Random Forest único com peso de classe (a modificação); A-prof5, quando
  presente, é o sistema do artigo com profundidade máxima 5, ao lado.
- **Parte A, ablação.** Cada modelo ajustado com todos os atributos (`todos`),
  sem `Duration` (`sem_duration`) e sem `Duration`, `FlowSentRate` e
  `FlowReceivedRate` (`sem_duration_taxas`), avaliado no teste sem perturbação.
- **Parte B, fragmentação.** Os mesmos modelos, sem novo ajuste, predizem os
  fluxos Malicious-DoH do teste com {fragmented} divididos pelos fatores
  {", ".join(str(factor) for factor in PERTURBED)}. As duas taxas de bytes por segundo não mudam,
  porque são os bytes divididos pela duração; o script confere essa relação
  na tabela inteira antes de rodar. O fator 1 é o teste sem perturbação.
- **O que não é tocado.** O treino, o normalizador (ajustado só no treino) e
  os fluxos Non-DoH e Benign-DoH do teste. O FPR não muda com o fator.
- **Hiperparâmetros de {first_model}.** Os escolhidos pela seleção já gravada em
  `{first_model}-cira/`, no treino da mesma seed e com os 29 atributos. A seleção não
  foi refeita sem as colunas retiradas.
- **Conferência.** Com todos os atributos, a matriz de confusão de cada modelo
  no teste sem perturbação é igual à já gravada para a mesma seed
  (`results/e4/corrigida/` e `{first_model}-cira/`); o script para se não for.

Commit e estado da árvore de cada grupo de execuções:

{provenance_text(summary)}

Todo valor é média ± desvio padrão amostral entre as seeds, em percentual,
salvo onde a tabela diz outra unidade. Comparação pareada: {summary["paired_method"]}.
Regra de leitura: {READING_RULE}. Ressalva: {summary["paired_caveat"]}.

## Parte A: ablação no teste sem perturbação

{clean_table(summary)}

"Atributos examinados por divisão" é o que a árvore de fato usa: com 28 ou 26
colunas, os 28 atributos por divisão do artigo (Seção IV-A) passam a ser todas
as colunas, e o sorteio de atributos em cada divisão deixa de existir.

Cada conjunto de colunas contra `todos`, no mesmo modelo, seed a seed:

{ablation_table(paired_all["ablation"])}

{identical_text(summary)}## Parte B: a perturbação

Descrição dos fluxos Malicious-DoH do teste depois da fragmentação. Não
depende do modelo. A faixa do treino é a do normalizador: valor abaixo do
mínimo ou acima do máximo que o atributo tem no treino da seed.

{perturbation_table(summary["perturbation"])}

A última coluna mede a incoerência que a simplificação cria. Nos fluxos do
conjunto de dados o tempo médio de pacote não passa da duração. Isso é
observação dos dados, não leitura do código do extrator: no fator 1, que é o
teste sem perturbação, a coluna é {
        e4r.mean_std(summary["perturbation"]["1"]["incoherent_row_fraction"])
    }%;
e, em conferência feita à parte na tabela limpa do CIRA, que não é gravada em
`results/`, em nenhuma linha a média, a mediana ou a moda do tempo de pacote
passa da duração. Como as estatísticas por pacote não foram recalculadas, o
vetor perturbado deixa de respeitar isso.

## Parte B: recall de Malicious-DoH por fator de fragmentação

Média ± desvio padrão entre as seeds e, entre parênteses, o menor valor entre
as seeds. O mínimo e esta nota de leitura foram acrescentados depois da
execução, sem mudar a regra nem os vereditos. Onde o mínimo fica longe da
média, o modelo cede em algumas seeds
muito mais que nas outras, e a regra de leitura, que compara a média com o
desvio, pode dizer "não se distinguem" para uma queda que existe em todas as
seeds: as colunas de contagem de seeds das tabelas pareadas mostram isso.

{recall_table(summary)}

Para onde vão os fluxos Malicious-DoH, em número de fluxos por seed:

{missed_table(summary)}

Cada fator contra o fator 1, no mesmo modelo (o primeiro lado é o fator
perturbado; "menor" quer dizer que o modelo degrada nesse fator):

{
        factor_table(
            paired_all["degradation"],
            ["modelo", "colunas"],
            lambda row: [row["model"], f"`{row['columns']}`"],
        )
    }

{first_model} menos {second_model}, com as mesmas colunas, em cada fator:

{
        factor_table(
            paired_all["between_models"],
            ["par", "colunas"],
            lambda row: [f"{row['first']} menos {row['second']}", f"`{row['columns']}`"],
        )
    }

Cada conjunto de colunas contra `todos`, no mesmo modelo, em cada fator:

{
        factor_table(
            paired_all["between_columns"],
            ["modelo", "par"],
            lambda row: [row["model"], f"`{row['first']}` menos `{row['second']}`"],
        )
    }

{hypothesis_text(summary["hypothesis"], summary["descriptive"])}
{descriptive_text(summary)}
## Relação com a explicação do modelo

Os valores SHAP de `results/e5/variante/` põem `Duration` como o terceiro
atributo em importância para Malicious-DoH nos três Random Forests base, atrás
de `PacketLengthMode` e `PacketLengthMedian`, e mostram que o sinal do valor
SHAP de `Duration` troca perto de 33 s. A tabela da perturbação mostra a
mediana da duração dos fluxos maliciosos em cada fator: é contra esse corte
que ela deve ser lida. A importância SHAP diz quanto o atributo pesa na
saída do modelo; a parte B mede o que acontece com a predição quando o
atributo e os bytes do fluxo mudam juntos. As duas medidas não são a mesma
coisa, e a parte B não isola o efeito de `Duration` do efeito dos bytes.

## Simplificações e o efeito delas

- **As estatísticas por pacote ficam fixas.** Em um fluxo fragmentado de
  verdade, as estatísticas de tempo de pacote encolheriam com a duração e as
  de comprimento de pacote mudariam com os pacotes de handshake de cada
  conexão nova. Aqui os 24 atributos que não são {fragmented} nem as
  duas taxas ficam com o valor do fluxo inteiro. A coluna de incoerência da
  tabela da perturbação conta os vetores com uma relação entre tempo de pacote
  e duração que nenhum fluxo do conjunto de dados tem.
- **Efeito no resultado.** A queda de recall pode estar subestimada, porque
  atributos que também mudariam ficam com o valor original, ou superestimada,
  porque vetores incoerentes caem em regiões do espaço de atributos em que o
  modelo não viu nenhum fluxo. O experimento não diz qual das duas.
- **Valores fora da faixa do treino.** Random Forest não extrapola: um valor
  abaixo do mínimo do treino segue o mesmo caminho na árvore que o menor
  valor visto. A contagem está na tabela da perturbação.
- **Bytes fracionários e fragmentos iguais.** Os bytes divididos não são
  arredondados, e todos os fragmentos de um fluxo têm o mesmo vetor: o recall
  por fragmento é o recall medido com um fragmento por fluxo.
- **Retirar a coluna não retira a grandeza.** As estatísticas de tempo de
  pacote carregam a duração de forma indireta, e `sem_duration_taxas` mantém
  os bytes do fluxo, que a perturbação altera. Nenhum dos três conjuntos de
  colunas é imune por construção.
- **A seleção de hiperparâmetros de {first_model} não foi refeita** para os modelos
  sem colunas: eles podem não ter a combinação que venceria.

Uma avaliação fiel exigiria gerar o tráfego de novo com o túnel configurado
para reabrir a conexão, ou reprocessar os PCAPs com o extrator.

## O que não foi feito

{not_run_text}- Perturbação das estatísticas por pacote, preenchimento de pacotes e inserção
  de atraso.
- Atacante com acesso ao modelo, que busca por fluxo o menor fator que evade.
- Avaliação no combinado CIRA + HKD.
- Avaliação no teste sem os vetores repetidos do treino: com colunas
  retiradas, o que é vetor repetido muda de um conjunto de colunas para outro.
- Treino com fluxos fragmentados.
- Custo da fragmentação para o atacante (vazão do túnel, handshakes).

## Limitações

- Os {len(seeds)} conjuntos de teste são sorteados da mesma tabela e se sobrepõem; o
  desvio padrão mede a variação entre sorteios desta tabela.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o das outras classes. A duração pode separar as
  classes pelo modo como o tráfego foi gerado, e a perturbação herda isso.
- O tempo de ajuste depende da carga da máquina e é só indicativo.
"""


def write_summary(e8_dir: Path, seeds: list[int]) -> dict:
    """Lê as execuções, grava summary-robustez.json e RESUMO-ROBUSTEZ.md e devolve a agregação."""
    summary = summary_content(load_runs(e8_dir, seeds), seeds)
    text = json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False)
    (e8_dir / "summary-robustez.json").write_text(text + "\n", encoding="utf-8")
    (e8_dir / "RESUMO-ROBUSTEZ.md").write_text(summary_text(summary), encoding="utf-8")
    return summary


def main() -> None:
    """Agrega as execuções gravadas e escreve summary-robustez.json e RESUMO-ROBUSTEZ.md."""
    summary = write_summary(E8_DIR, SEEDS_CORRIGIDA)
    print(recall_table(summary))
    print(
        f"Escritos summary-robustez.json e RESUMO-ROBUSTEZ.md em {E8_DIR.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()
