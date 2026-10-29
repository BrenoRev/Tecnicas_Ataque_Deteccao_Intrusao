"""E4: agregação e resumo do protocolo corrigido, a partir dos metrics.json.

Não treina nada. Lê os metrics.json gravados por scripts/e4_corrigido.py em
results/e4/corrigida/<modelo>/seed<k>/ e em
results/e4/corrigida/A-fold<k>/seed<s>/ e escreve, na pasta da trilha:

- summary.json: média e desvio padrão entre as seeds, a comparação pareada e
  as dobras por máquina. É agregação determinística dos metrics.json;
- RESUMO.md: a leitura dos números, ao lado da hipótese escrita antes da
  primeira execução (HIPOTESE.md, que este script não altera).

Roda como módulo, a partir da pasta do projeto, porque importa o script de treino.

Uso: uv run python -m scripts.e4_resumo
"""

import json
from pathlib import Path

import numpy as np

import scripts.e4_corrigido as e4
from doh_ids.config import (
    CLASS_NAMES,
    CORRIGIDA_MODELS,
    GROUP_FOLD_SEED,
    GROUP_FOLDS,
    HYPOTHETICAL_PREVALENCES,
    PAIRED_COMPARISONS,
    PAIRED_METRICS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEEDS_CORRIGIDA,
)
from doh_ids.evaluate import aggregate_seeds, base_rate, malicious_vs_rest, paired_comparison
from doh_ids.summary import markdown_table

NON_DOH = CLASS_NAMES.index("Non-DoH")
BENIGN = CLASS_NAMES.index("Benign-DoH")
SCOPES = e4.SCOPES
ORDER = ", ".join(CLASS_NAMES)

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
# Nome, no texto, das métricas da comparação pareada.
METRIC_TITLES = {"macro_f1": "F1 macro", "benign_doh_recall": "recall de Benign-DoH"}

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
NOT_APPLICABLE = "não se aplica"


def load_results(track_dir: Path, seeds: list[int]) -> dict:
    """Lê o metrics.json de cada modelo em cada seed: `results[modelo][seed]`."""
    return {
        name: {
            seed: json.loads(
                (track_dir / name / f"seed{seed}" / "metrics.json").read_text(encoding="utf-8")
            )
            for seed in seeds
        }
        for name in CORRIGIDA_MODELS
    }


def load_folds(track_dir: Path) -> list[dict]:
    """Lê o metrics.json de cada dobra da avaliação por máquina, na ordem das dobras."""
    return [
        json.loads(
            (
                track_dir
                / f"{e4.GROUP_FOLD_MODEL}-fold{fold}"
                / f"seed{GROUP_FOLD_SEED}"
                / "metrics.json"
            ).read_text(encoding="utf-8")
        )
        for fold in range(GROUP_FOLDS)
    ]


def class_key(name: str) -> str:
    """Devolve o nome da classe como prefixo de chave: `Benign-DoH` vira `benign_doh`."""
    return name.lower().replace("-", "_")


def flat_metrics(evaluated: dict) -> dict:
    """Põe em um nível só as métricas numéricas que `evaluate` devolve.

    As chaves do primeiro nível ficam como estão; as de cada classe ganham o
    nome da classe na frente (`benign_doh_recall`), e o FPR de Malicious-DoH
    contra o resto vira `malicious_fpr`. Nos modelos empilhados entram também
    as AUC calculadas com a média das probabilidades dos bases, com o sufixo
    `_base_mean`.
    """
    flat = {key: evaluated[key] for key in TOP_LEVEL_METRICS}
    if "roc_auc_ovr_macro_base_mean" in evaluated:
        flat["roc_auc_ovr_macro_base_mean"] = evaluated["roc_auc_ovr_macro_base_mean"]
    for name in CLASS_NAMES:
        per_class = evaluated["per_class"][name]
        for metric in PER_CLASS_METRICS:
            flat[f"{class_key(name)}_{metric}"] = per_class[metric]
        if "pr_auc_base_mean" in per_class:
            flat[f"{class_key(name)}_pr_auc_base_mean"] = per_class["pr_auc_base_mean"]
    flat["malicious_fpr"] = evaluated["malicious_vs_rest"]["fpr"]
    return flat


def model_summary(runs: list[dict]) -> dict:
    """Agrega as execuções de um modelo, uma por seed, em média e desvio padrão.

    Devolve a agregação de cada métrica nos dois conjuntos de `SCOPES`, a
    fração do teste com vetor repetido do treino, os dois erros de Benign-DoH
    em número de fluxos, o FPR de Malicious-DoH entre as seeds e com os falsos
    positivos somados, e a conta de taxa base.
    """
    summary = {
        scope: aggregate_seeds([flat_metrics(run[scope]) for run in runs]) for scope in SCOPES
    }
    summary["test_seen_in_train_fraction"] = aggregate_seeds(
        [{"fraction": run["test_seen_in_train"]["fraction"]} for run in runs]
    )["fraction"]
    confusions = [run["test"]["confusion_matrix"] for run in runs]
    summary["benign_doh_errors"] = aggregate_seeds(
        [
            {
                "non_doh_as_benign_doh": matrix[NON_DOH][BENIGN],
                "benign_doh_as_non_doh": matrix[BENIGN][NON_DOH],
            }
            for matrix in confusions
        ]
    )
    fprs = [run["test"]["malicious_vs_rest"]["fpr"] for run in runs]
    summary["malicious_fpr_range"] = {
        "min": min(fprs),
        "median": float(np.median(fprs)),
        "max": max(fprs),
    }
    # Matrizes das seeds somadas célula a célula: o FPR e o intervalo de
    # confiança saem dos falsos positivos e dos fluxos não maliciosos somados.
    pooled = malicious_vs_rest(np.sum(confusions, axis=0).tolist())
    summary["false_positives_total"] = pooled["false_positives"]
    summary["negatives_total"] = pooled["negatives"]
    summary["pooled_fpr_ci_high"] = pooled["fpr_ci_high"]
    # A taxa base usa o FPR e o recall médios de Malicious-DoH no teste inteiro.
    # A prevalência é hipotética: o conjunto de dados não a mede.
    fpr = summary["test"]["malicious_fpr"]["mean"]
    recall = summary["test"]["malicious_doh_recall"]["mean"]
    summary["base_rate"] = [
        base_rate(fpr, recall, prevalence) for prevalence in HYPOTHETICAL_PREVALENCES
    ]
    # A mesma conta com o limite superior do intervalo do FPR: é o que a
    # amostra permite afirmar quando o FPR medido é zero ou quase zero.
    summary["base_rate_at_fpr_ci_high"] = [
        base_rate(pooled["fpr_ci_high"], recall, prevalence)
        for prevalence in HYPOTHETICAL_PREVALENCES
    ]
    return summary


def paired(results: dict, first: str, second: str, metric: str, scope: str = "test") -> dict:
    """Compara dois modelos seed a seed em uma métrica de `flat_metrics`."""
    values = [
        [flat_metrics(run[scope])[metric] for run in results[name].values()]
        for name in (first, second)
    ]
    return paired_comparison(*values)


def paired_rows(results: dict) -> list[dict]:
    """Compara, seed a seed, cada par de `PAIRED_COMPARISONS` em cada métrica e conjunto."""
    return [
        {
            "first": first,
            "second": second,
            "scope": scope,
            "metric": metric,
            **paired(results, first, second, metric, scope),
        }
        for first, second in PAIRED_COMPARISONS
        for scope in SCOPES
        for metric in PAIRED_METRICS
    ]


def summary_content(results: dict) -> dict:
    """Monta a agregação das seeds a partir do que `load_results` devolve."""
    seeds = list(next(iter(results.values())))
    summary = {
        "experiment": e4.EXPERIMENT,
        "track": e4.TRACK,
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
            "comparisons": paired_rows(results),
        },
    }
    for name, model in summary["models"].items():
        assert model["test"]["accuracy"]["n"] == len(seeds), f"{name}: falta seed."
    return summary


def group_summary(folds: list[dict]) -> dict:
    """Resume a avaliação por máquina: as métricas de cada dobra e a média entre elas."""
    rows = [flat_metrics(fold["test"]) for fold in folds]
    return {
        "model": e4.GROUP_FOLD_MODEL,
        "seed": GROUP_FOLD_SEED,
        "folds": [
            {
                "held_out_groups": fold["held_out_groups"],
                "train_rows": fold["train_rows"],
                "test_rows": fold["test_rows"],
                "fit_rows": fold["fit_rows"],
                "test_seen_in_train_fraction": fold["test_seen_in_train"]["fraction"],
                **row,
            }
            for fold, row in zip(folds, rows, strict=True)
        ],
        "across_folds": aggregate_seeds(rows),
    }


def mean_std(entry: dict, digits: int = 3) -> str:
    """Escreve média e desvio padrão de uma fração, em percentual."""
    return f"{100 * entry['mean']:.{digits}f} ± {100 * entry['std']:.{digits}f}"


def optional_mean_std(metrics: dict, key: str) -> str:
    """Escreve média e desvio padrão de uma métrica que só os modelos empilhados têm."""
    return mean_std(metrics[key]) if key in metrics else NOT_APPLICABLE


def occurred(condition: bool) -> str:
    """Escreve se um resultado esperado ou declarado como inesperado ocorreu."""
    return "**ocorreu**" if condition else "não ocorreu"


def aggregate_table(models: dict, scope: str) -> str:
    """Escreve a tabela das métricas agregadas de cada modelo, com o nome de cada média."""
    columns = {
        "accuracy": "acurácia",
        "macro_precision": "precisão macro",
        "macro_recall": "recall macro",
        "macro_f1": "F1 macro",
        "weighted_f1": "F1 ponderado",
        "roc_auc_ovr_macro": "AUC-ROC one-vs-rest macro, saída do modelo",
    }
    rows = [
        [
            name,
            *(mean_std(model[scope][key]) for key in columns),
            optional_mean_std(model[scope], "roc_auc_ovr_macro_base_mean"),
        ]
        for name, model in models.items()
    ]
    last = "AUC-ROC one-vs-rest macro, média das probabilidades dos bases"
    return markdown_table(["modelo", *columns.values(), last], rows)


def per_class_table(models: dict, scope: str) -> str:
    """Escreve precisão, recall, F1 e as duas AUC-PR de cada classe, com Benign-DoH em negrito."""
    rows = []
    for name, model in models.items():
        for class_name in CLASS_NAMES:
            key = class_key(class_name)
            cells = [mean_std(model[scope][f"{key}_{metric}"]) for metric in PER_CLASS_METRICS]
            cells.append(optional_mean_std(model[scope], f"{key}_pr_auc_base_mean"))
            row = [name, class_name, *cells]
            if class_name == "Benign-DoH":
                row = [f"**{cell}**" for cell in row]
            rows.append(row)
    columns = ["modelo", "classe", "precisão", "recall", "F1"]
    columns += ["AUC-PR, saída do modelo", "AUC-PR, média das probabilidades dos bases"]
    return markdown_table(columns, rows)


def auc_note(models: dict) -> str:
    """Escreve o aviso sobre as duas AUC, que vai junto de cada tabela que as traz."""
    stacked = " e ".join(name for name, model in models.items() if model["config"]["stacked"])
    return (
        f"Aviso sobre as AUC. Nos modelos empilhados ({stacked}), a saída do modelo é a do "
        "meta-classificador, que só tem as combinações de rótulos dos três bases: a AUC dela "
        "mede essa discretização e não deve ser comparada com a dos Random Forests únicos. A "
        "coluna da média das probabilidades dos bases é a que pode ficar ao lado da AUC de um "
        "Random Forest único; ela não é a saída com que o sistema decide."
    )


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


def balancing_text(results: dict) -> str:
    """Escreve em que A e B diferem, com as amostras em que cada um foi ajustado."""
    seed = next(iter(results["A"]))
    first, second = results["A"][seed], results["B"][seed]
    return (
        "A e B têm os mesmos hiperparâmetros de Random Forest. Diferem na arquitetura e no "
        "balanceamento que ela traz: em A cada base vê um terço do Non-DoH e só Benign-DoH é "
        "aumentada; em B o SMOTE iguala Benign-DoH e Malicious-DoH ao Non-DoH inteiro. A "
        "diferença entre A e B mede as duas coisas juntas. Amostras por classe nos conjuntos "
        f"de ajuste da seed {seed}, na ordem {ORDER}: os três bases de A, "
        f"{', '.join(map(str, first['fit_rows']))}; B, "
        f"{', '.join(map(str, second['fit_rows']))}. O treino da seed tem "
        f"{first['train_rows']} fluxos reais: o que passa disso em uma classe é amostra sintética."
    )


def benign_errors_table(models: dict) -> str:
    """Escreve os dois erros de Benign-DoH de cada modelo, em fluxos por teste."""
    rows = [
        [
            name,
            *(
                f"{model['benign_doh_errors'][key]['mean']:.1f} ± "
                f"{model['benign_doh_errors'][key]['std']:.1f}"
                for key in ("non_doh_as_benign_doh", "benign_doh_as_non_doh")
            ),
        ]
        for name, model in models.items()
    ]
    columns = ["modelo", "Non-DoH predito como Benign-DoH", "Benign-DoH predito como Non-DoH"]
    return markdown_table(columns, rows)


def benign_errors_text(models: dict, pairs: list[tuple[str, str]] = PAIRED_COMPARISONS) -> str:
    """Diz, para cada par de `pairs`, se os modelos trocam um erro de Benign-DoH pelo outro."""
    lines = []
    for first, second in pairs:
        errors = [models[name]["benign_doh_errors"] for name in (first, second)]
        false_benign = [entry["non_doh_as_benign_doh"]["mean"] for entry in errors]
        missed_benign = [entry["benign_doh_as_non_doh"]["mean"] for entry in errors]
        trade = (false_benign[0] < false_benign[1]) != (missed_benign[0] < missed_benign[1])
        reading = (
            "os dois trocam um erro pelo outro: quem erra menos em um sentido erra mais no outro"
            if trade
            else "não há troca: o mesmo modelo erra menos nos dois sentidos, ou há empate"
        )
        lines.append(
            f"- {first} contra {second}: Non-DoH predito como Benign-DoH, {false_benign[0]:.1f} "
            f"contra {false_benign[1]:.1f} fluxos por teste; Benign-DoH predito como Non-DoH, "
            f"{missed_benign[0]:.1f} contra {missed_benign[1]:.1f}. Leitura: {reading}."
        )
    return "\n".join(lines)


def paired_table(comparisons: list[dict]) -> str:
    """Escreve a tabela da comparação pareada: diferença, desvio, vitórias e Wilcoxon."""
    rows = []
    for row in comparisons:
        tested = row["wilcoxon_statistic"] is not None
        rows.append(
            [
                f"{row['first']} contra {row['second']}",
                SCOPES[row["scope"]],
                METRIC_TITLES[row["metric"]],
                f"{100 * row['mean_difference']:+.4f}",
                f"{100 * row['std_difference']:.4f}",
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
        "desvio padrão das diferenças (pp)",
        "seeds em que o primeiro vence",
        "seeds em que o segundo vence",
        "empates",
        "estatística de Wilcoxon",
        "p-valor",
    ]
    return markdown_table(columns, rows)


def paired_reading_text(comparisons: list[dict], n_seeds: int) -> str:
    """Escreve o que o p-valor pode dizer e quais comparações não distinguem os modelos."""
    # Com n pares e nenhuma diferença nula, o teste bilateral tem 2 elevado a n
    # combinações de sinais igualmente prováveis, e as duas mais extremas são
    # todos os sinais iguais.
    undistinguished = [
        f"{row['first']} contra {row['second']} em {METRIC_TITLES[row['metric']]} "
        f"({SCOPES[row['scope']]})"
        for row in comparisons
        if abs(row["mean_difference"]) < row["std_difference"]
    ]
    listed = "; ".join(undistinguished) if undistinguished else "nenhuma"
    return (
        f"O p-valor mínimo possível com {n_seeds} pares é 2/{2**n_seeds} "
        f"({2 / 2**n_seeds:.4f}), o de um modelo vencer em todas as seeds: ele repete a contagem "
        "de vitórias e não mede tamanho de efeito. Regra de leitura: diferença média, em "
        "módulo, menor que o desvio padrão das diferenças pareadas não distingue os dois "
        f"modelos. Comparações nessa condição: {listed}."
    )


def fpr_table(models: dict) -> str:
    """Escreve o FPR de Malicious-DoH entre as seeds e com os falsos positivos somados."""
    rows = [
        [
            name,
            *(f"{model['malicious_fpr_range'][key]:.4%}" for key in ("min", "median", "max")),
            model["false_positives_total"],
            model["negatives_total"],
            f"{model['pooled_fpr_ci_high']:.4%}",
        ]
        for name, model in models.items()
    ]
    columns = [
        "modelo",
        "FPR mínimo entre seeds",
        "FPR mediano",
        "FPR máximo",
        "falsos positivos somados",
        "fluxos não maliciosos somados",
        "limite superior do intervalo de confiança do FPR somado",
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
            f"{upper['operational_precision']:.2%}",
            f"{upper['false_alarms_per_10_million']:.0f}",
        ]
        for name, model in models.items()
        for entry, upper in zip(model["base_rate"], model["base_rate_at_fpr_ci_high"], strict=True)
    ]
    columns = [
        "modelo",
        "prevalência hipotética",
        "precisão operacional, FPR médio",
        "alarmes falsos a cada dez milhões de fluxos, FPR médio",
        "precisão operacional, limite superior do FPR",
        "alarmes falsos a cada dez milhões de fluxos, limite superior do FPR",
    ]
    return markdown_table(columns, rows)


def expected_lines(models: dict, results: dict) -> str:
    """Põe os números ao lado das duas expectativas de HIPOTESE.md, na ordem do arquivo."""
    n_seeds = len(results["A"])
    lines = [
        "1. Esperado: diferença entre A e B da ordem do desvio padrão entre seeds ou menor. "
        'A hipótese não fixa o que é "da ordem"; a conta abaixo compara a diferença média, em '
        "módulo, com o maior dos dois desvios padrão entre seeds."
    ]
    for metric, title in METRIC_TITLES.items():
        row = paired(results, "A", "B", metric)
        stds = [models[name]["test"][metric]["std"] for name in ("A", "B")]
        lines.append(
            f"   - {title}: diferença média de {100 * row['mean_difference']:+.4f} pp (A menos "
            f"B); desvio padrão entre seeds de {100 * stds[0]:.4f} pp em A e de "
            f"{100 * stds[1]:.4f} pp em B. Diferença dentro do maior desvio: "
            f"{occurred(abs(row['mean_difference']) <= max(stds))}."
        )
    lines.append(
        "2. Esperado: recall de Benign-DoH mais baixo nos modelos de profundidade 5 que nos sem "
        "limite de profundidade."
    )
    for shallow, deep in (("A-prof5", "A"), ("B-prof5", "B")):
        row = paired(results, shallow, deep, "benign_doh_recall")
        recalls = [mean_std(models[name]["test"]["benign_doh_recall"]) for name in (shallow, deep)]
        lines.append(
            f"   - {shallow} contra {deep}: {recalls[0]}% contra {recalls[1]}%; {shallow} fica "
            f"abaixo em {row['second_wins']} das {n_seeds} seeds: "
            f"{occurred(row['mean_difference'] < 0)}."
        )
    return "\n".join(lines)


def wins_lines(models: dict, results: dict) -> list[str]:
    """Confronta os dois itens da hipótese sobre um modelo vencer o outro em todas as seeds."""
    n_seeds = len(results["A"])
    lines = [
        "1. A vencer B em todas as seeds, com diferença média maior que o desvio padrão entre "
        "seeds (aqui, o maior dos dois):"
    ]
    for metric, title in METRIC_TITLES.items():
        row = paired(results, "A", "B", metric)
        largest = max(models[name]["test"][metric]["std"] for name in ("A", "B"))
        happened = row["first_wins"] == n_seeds and row["mean_difference"] > largest
        lines.append(
            f"   - {title}: A vence em {row['first_wins']} das {n_seeds} seeds; diferença média "
            f"de {100 * row['mean_difference']:+.4f} pp, maior desvio padrão entre seeds de "
            f"{100 * largest:.4f} pp: {occurred(happened)}."
        )
    lines.append("2. B ou C vencer A em todas as seeds:")
    for other in ("B", "C"):
        for metric, title in METRIC_TITLES.items():
            row = paired(results, "A", other, metric)
            lines.append(
                f"   - {other}, {title}: vence A em {row['second_wins']} das {n_seeds} seeds "
                f"(diferença média A menos {other} de {100 * row['mean_difference']:+.4f} pp): "
                f"{occurred(row['second_wins'] == n_seeds)}."
            )
    return lines


def spread_lines(models: dict) -> list[str]:
    """Confronta os dois itens da hipótese sobre a variação entre seeds e os vetores repetidos."""
    lines = [
        "3. Desvio padrão entre seeds maior que a diferença entre a leitura de profundidade "
        "variável e a de profundidade 5:"
    ]
    for deep, shallow in (("A", "A-prof5"), ("B", "B-prof5")):
        for metric, title in METRIC_TITLES.items():
            entries = [models[name]["test"][metric] for name in (deep, shallow)]
            difference = entries[0]["mean"] - entries[1]["mean"]
            largest = max(entry["std"] for entry in entries)
            lines.append(
                f"   - {deep} e {shallow}, {title}: diferença entre as médias de "
                f"{100 * difference:+.4f} pp; maior desvio padrão entre seeds de "
                f"{100 * largest:.4f} pp: {occurred(largest > abs(difference))}."
            )
    lines.append(
        '4. Queda grande das métricas no teste sem vetores repetidos. A hipótese não fixa o que é "'
        'grande", e não há veredito. Médias no teste inteiro e no teste sem vetores repetidos:'
    )
    for name, model in models.items():
        cells = "; ".join(
            f"{title} de {100 * model['test'][metric]['mean']:.3f}% para "
            f"{100 * model['test_unseen'][metric]['mean']:.3f}% "
            f"({100 * (model['test_unseen'][metric]['mean'] - model['test'][metric]['mean']):+.3f}"
            " pp)"
            for metric, title in METRIC_TITLES.items()
        )
        lines.append(f"   - {name}: {cells}.")
    return lines


def hypothesis_text(models: dict, results: dict) -> str:
    """Monta a seção que põe a hipótese escrita antes da execução ao lado do resultado."""
    unexpected = "\n".join(wins_lines(models, results) + spread_lines(models))
    return f"""## Hipótese ao lado do resultado

A hipótese está em `HIPOTESE.md`, escrita antes da primeira execução e não
alterada depois. Os itens abaixo seguem a ordem do arquivo e usam o teste
inteiro. A hipótese diz que A contra B isola a arquitetura; como está na seção
Protocolo, o par difere também no balanceamento, e a diferença mede as duas
coisas juntas.

### O que se esperava

{expected_lines(models, results)}

### O que a hipótese listava como resultado inesperado

{unexpected}
"""


def fold_table(group: dict, model: dict, train_rows: list[int]) -> str:
    """Põe cada dobra por máquina ao lado do split aleatório do mesmo modelo."""
    rows = [
        [
            index,
            f"{fold['benign_doh_recall']:.3%}",
            f"{fold['test_seen_in_train_fraction']:.2%}",
            f"{fold['malicious_doh_recall']:.3%}",
            fold["train_rows"],
            f"{sum(fold['train_rows']) / sum(train_rows):.1%}",
            fold["fit_rows"][0],
        ]
        for index, fold in enumerate(group["folds"])
    ]
    seen = model["test_seen_in_train_fraction"]
    rows.append(
        [
            "split aleatório, média entre seeds",
            f"{model['test']['benign_doh_recall']['mean']:.3%}",
            f"{seen['mean']:.2%}",
            f"{model['test']['malicious_doh_recall']['mean']:.3%}",
            train_rows,
            "100.0%",
            "",
        ]
    )
    columns = [
        "dobra",
        "recall de Benign-DoH",
        "fração do teste com vetor repetido do treino",
        "recall de Malicious-DoH",
        "fluxos do treino por classe",
        "treino em relação ao do split aleatório",
        "amostras por classe no primeiro subconjunto",
    ]
    return markdown_table(columns, rows)


def fold_reading_text(group: dict, model: dict, train_rows: list[int]) -> str:
    """Escreve o que as dobras por máquina medem, o que não medem e a ressalva do treino."""
    sizes = [sum(fold["train_rows"]) / sum(train_rows) for fold in group["folds"]]
    return f"""### O que as dobras medem

Medem se a separação entre Non-DoH e Benign-DoH aprendida em três máquinas vale
na quarta: as duas classes foram geradas pelas mesmas {len(group["folds"])} máquinas, e em cada
dobra uma delas fica inteira no teste.

Não medem a generalização da detecção de Malicious-DoH, porque máquina e classe
se confundem: nenhuma máquina gerou tráfego legítimo e malicioso. Uma máquina
de Malicious-DoH deixada de fora continua diferente das de Non-DoH e Benign-DoH
do treino pela captura, e não só pelo ataque.

Ao lado do split aleatório do modelo {group["model"]} (classes na ordem {ORDER}):

{fold_table(group, model, train_rows)}

Ressalva: o treino muda de tamanho e de composição a cada dobra. Ele tem de
{min(sizes):.1%} a {max(sizes):.1%} dos fluxos do treino do split aleatório, e a proporção entre as
classes não é a mesma, como mostram as contagens da tabela. A diferença de uma
dobra para o split aleatório mistura a máquina nova com o treino de outro
tamanho e de outra composição, e os números não separam as duas causas.
"""


def group_text(group: dict, model: dict, train_rows: list[int]) -> str:
    """Monta a seção do RESUMO.md com a avaliação por máquina.

    `model` é a agregação das seeds do modelo avaliado por máquina e
    `train_rows` os fluxos por classe do treino dele no split aleatório.
    """
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
estão na ordem {ORDER}.

{markdown_table(columns, rows)}

As dobras têm tamanhos e proporções de classe muito diferentes, porque as
máquinas geraram quantidades diferentes de tráfego: a média entre dobras pesa
cada dobra por igual e não é comparável à média entre seeds das seções acima.
Há uma execução por dobra, com uma seed: não há medida de variação entre seeds
aqui.

{fold_reading_text(group, model, train_rows)}"""


def summary_text(summary: dict, results: dict) -> str:
    """Monta o texto do RESUMO.md a partir da agregação e das execuções de cada seed."""
    models = summary["models"]
    seeds = summary["seeds"]
    seen = next(iter(models.values()))["test_seen_in_train_fraction"]
    pairs = ", ".join(f"{first} contra {second}" for first, second in PAIRED_COMPARISONS)
    comparisons = summary["paired"]["comparisons"]
    return f"""# E4: protocolo corrigido, variância entre seeds e comparação pareada

Gerado por `scripts/e4_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e4_corrigido.py`. Trilha `corrigida`. Os números de cada execução
estão em `<modelo>/seed<k>/metrics.json`; a configuração, os tempos e o commit,
em `<modelo>/seed<k>/run.json`; as médias e a comparação pareada, sem
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

{balancing_text(results)}

A contra C é a comparação que o artigo faz na Tabela II. Os modelos com
`-prof5` repetem A e B com a profundidade máxima 5 da Seção IV-B do artigo. O
meta-classificador dos modelos empilhados é treinado como na reprodução do
artigo: este protocolo corrige a avaliação, não o desenho do empilhamento.

Todo valor abaixo é média ± desvio padrão entre as seeds, em percentual, salvo
onde a tabela diz outra unidade. O desvio padrão é o amostral. Uma seed
controla o split, a reamostragem e os modelos: o desvio mistura as três fontes
de variação e não separa nenhuma.

## Teste inteiro

{auc_note(models)}

{aggregate_table(models, "test")}

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

{per_class_table(models, "test")}

Malicious-DoH contra o resto:

{malicious_table(models, "test")}

## Os dois erros de Benign-DoH

Média ± desvio padrão entre as seeds do número de fluxos do teste, lido das
matrizes de confusão: Non-DoH predito como Benign-DoH baixa a precisão de
Benign-DoH; Benign-DoH predito como Non-DoH baixa o recall.

{benign_errors_table(models)}

{benign_errors_text(models)}

## Teste sem vetores repetidos do treino

Em média, {mean_std(seen, 2)}% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

{auc_note(models)}

{aggregate_table(models, "test_unseen")}

{per_class_table(models, "test_unseen")}

{malicious_table(models, "test_unseen")}

## Comparação pareada

Pares: {pairs}. Método: {PAIRED_METHOD}. A diferença é a do primeiro modelo
menos a do segundo, em pontos percentuais (pp).

{paired_table(comparisons)}

Ressalva: {PAIRED_CAVEAT}.

{paired_reading_text(comparisons, len(seeds))}

## Taxa base

FPR de Malicious-DoH contra o resto no teste inteiro: mínimo, mediana e máximo
entre as {len(seeds)} seeds, e os falsos positivos somados nas seeds, com o limite superior
do intervalo de confiança exato de 95% do FPR somado. Os testes das seeds se
sobrepõem, e o mesmo fluxo pode ser contado em mais de uma: as observações
somadas não são independentes, e o intervalo do FPR somado é mais estreito do
que a amostra sustenta. O intervalo de cada seed está em cada `metrics.json`.

{fpr_table(models)}

Precisão operacional de Malicious-DoH: a fração dos alertas que seria ataque
se a fração de fluxos maliciosos no tráfego fosse a prevalência indicada. As
prevalências são hipotéticas: o conjunto de dados não mede a prevalência
real. A conta usa o recall médio do teste inteiro e dois valores de FPR: o
médio entre seeds e o limite superior do intervalo do FPR somado. Com zero
falsos positivos, o FPR médio é zero e a precisão operacional sai 100% em
qualquer prevalência: o que a amostra permite afirmar é a coluna do limite
superior.

{base_rate_table(models)}

{hypothesis_text(models, results)}
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


def write_summary(track_dir: Path, seeds: list[int]) -> dict:
    """Lê as execuções de `track_dir`, grava summary.json e RESUMO.md e devolve a agregação."""
    results = load_results(track_dir, seeds)
    summary = summary_content(results)
    group = group_summary(load_folds(track_dir))
    content = {**summary, "group_folds": group}
    text = json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False)
    (track_dir / "summary.json").write_text(text + "\n", encoding="utf-8")

    model = summary["models"][group["model"]]
    train_rows = results[group["model"]][seeds[0]]["train_rows"]
    (track_dir / "RESUMO.md").write_text(
        summary_text(summary, results) + group_text(group, model, train_rows), encoding="utf-8"
    )
    return summary


def main() -> None:
    """Agrega as execuções gravadas de E4 e escreve summary.json e RESUMO.md."""
    track_dir = RESULTS_DIR / e4.EXPERIMENT / e4.TRACK
    summary = write_summary(track_dir, SEEDS_CORRIGIDA)
    print(paired_table(summary["paired"]["comparisons"]))
    print(f"Escritos summary.json e RESUMO.md em {track_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
