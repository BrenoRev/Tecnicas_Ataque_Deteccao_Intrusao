"""Avaliação: métricas por classe, médias nomeadas e distância até o artigo.

Todos os experimentos avaliam por aqui. As matrizes de confusão têm a classe
real na linha e a classe predita na coluna, as duas na ordem de `CLASS_NAMES`.
Os dicionários devolvidos só têm tipos nativos, para serem gravados em JSON.
"""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy.stats import binomtest, wilcoxon
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score

from doh_ids.config import BASE_RATE_FLOWS, CLASS_NAMES, CONFIDENCE_LEVEL, FEATURE_COLUMNS

MALICIOUS = CLASS_NAMES.index("Malicious-DoH")
CLASS_METRICS = ["precision", "recall", "f1"]


def _ratio(numerator: float, denominator: float) -> float:
    """Divide, devolvendo 0.0 quando o denominador é zero."""
    # Classe que o modelo nunca prediz não tem precisão definida. Zero é a
    # convenção que penaliza o modelo, em vez de tirar a classe da média.
    return numerator / denominator if denominator else 0.0


def malicious_vs_rest(confusion: list[list[int]]) -> dict:
    """Resume a matriz na visão binária "Malicious-DoH contra o resto".

    Devolve os falsos positivos (fluxos não maliciosos classificados como
    maliciosos), o total de fluxos não maliciosos, o FPR com intervalo de
    confiança binomial exato (Clopper-Pearson) e o recall da classe maliciosa.
    """
    total = sum(map(sum, confusion))
    malicious_rows = sum(confusion[MALICIOUS])
    negatives = total - malicious_rows
    false_positives = sum(row[MALICIOUS] for row in confusion) - confusion[MALICIOUS][MALICIOUS]
    # O intervalo exato vale também com zero falsos positivos: o limite
    # inferior é zero e o superior continua informando o que a amostra permite afirmar.
    interval = binomtest(false_positives, negatives).proportion_ci(
        confidence_level=CONFIDENCE_LEVEL, method="exact"
    )
    return {
        "false_positives": false_positives,
        "negatives": negatives,
        "fpr": false_positives / negatives,
        "fpr_ci_level": CONFIDENCE_LEVEL,
        "fpr_ci_low": float(interval.low),
        "fpr_ci_high": float(interval.high),
        "recall": _ratio(confusion[MALICIOUS][MALICIOUS], malicious_rows),
    }


def metrics_from_confusion(
    confusion: list[list[int]], class_names: list[str] = CLASS_NAMES
) -> dict:
    """Calcula as métricas a partir só da matriz de confusão.

    Devolve a matriz, o total, a acurácia, suporte, precisão, recall e F1 de
    cada classe (em `per_class`, pelo nome da classe), as médias macro e
    ponderada de cada uma (chaves `macro_*` e `weighted_*`) e a visão
    "Malicious-DoH contra o resto" (em `malicious_vs_rest`).

    `class_names` dá o nome de cada código de classe, na ordem da matriz. Com
    nomes que não são os de `CLASS_NAMES`, a visão "Malicious-DoH contra o
    resto" não é devolvida.
    """
    confusion = [[int(cell) for cell in row] for row in confusion]
    total = sum(map(sum, confusion))
    per_class = {}
    for index, name in enumerate(class_names):
        hits = confusion[index][index]
        support = sum(confusion[index])
        predicted = sum(row[index] for row in confusion)
        precision = _ratio(hits, predicted)
        recall = _ratio(hits, support)
        per_class[name] = {
            "support": support,
            "precision": precision,
            "recall": recall,
            "f1": _ratio(2 * precision * recall, precision + recall),
        }

    metrics = {
        "confusion_matrix": confusion,
        "total": total,
        "accuracy": sum(confusion[index][index] for index in range(len(class_names))) / total,
        "per_class": per_class,
    }
    # A visão binária separa o tráfego malicioso do legítimo. Entre classes que
    # são todas maliciosas, como as ferramentas de túnel, ela não existe.
    if class_names == CLASS_NAMES:
        metrics["malicious_vs_rest"] = malicious_vs_rest(confusion)
    # O artigo reporta médias sem dizer qual (Tabela II). Aqui toda média leva
    # o nome: a macro pesa as três classes por igual; a ponderada pesa pelo
    # suporte e por isso esconde a classe benigna, a menor.
    for metric in CLASS_METRICS:
        values = [per_class[name][metric] for name in class_names]
        supports = [per_class[name]["support"] for name in class_names]
        metrics[f"macro_{metric}"] = sum(values) / len(values)
        metrics[f"weighted_{metric}"] = (
            sum(value * support for value, support in zip(values, supports, strict=True)) / total
        )
    return metrics


def _check_proba(proba: np.ndarray, n_samples: int) -> None:
    """Levanta `ValueError` se `proba` não for uma probabilidade por classe e por amostra."""
    expected = (n_samples, len(CLASS_NAMES))
    if proba.shape != expected:
        raise ValueError(
            f"Esperadas probabilidades com forma {expected}, recebida {proba.shape}. "
            "A AUC é calculada com as probabilidades de cada classe, não com os rótulos preditos."
        )
    if not np.allclose(proba.sum(axis=1), 1.0):
        raise ValueError("Cada linha das probabilidades deve somar 1.")


def _ranking_metrics(
    y_true: np.ndarray, proba: np.ndarray, class_names: list[str]
) -> tuple[float, dict]:
    """Devolve a AUC-ROC one-vs-rest macro e a AUC-PR de cada classe, pelo nome."""
    labels = list(range(len(class_names)))
    roc_auc = roc_auc_score(y_true, proba, multi_class="ovr", average="macro", labels=labels)
    pr_auc = {
        name: float(average_precision_score(y_true == index, proba[:, index]))
        for index, name in enumerate(class_names)
    }
    return float(roc_auc), pr_auc


def evaluate(
    y_true: ArrayLike,
    y_pred: ArrayLike,
    proba: ArrayLike,
    base_mean_proba: ArrayLike | None = None,
    class_names: list[str] = CLASS_NAMES,
) -> dict:
    """Avalia um modelo pelos rótulos reais, os preditos e as probabilidades por classe.

    Devolve o dicionário de `metrics_from_confusion` acrescido de
    `roc_auc_ovr_macro` e, em cada classe de `per_class`, de `pr_auc`.

    `base_mean_proba` é só para o modelo empilhado: a média das probabilidades
    dos Random Forests base. Com ela entram também `roc_auc_ovr_macro_base_mean`
    e `pr_auc_base_mean`. As duas AUC medem coisas diferentes: o
    meta-classificador que recebe rótulos só enxerga as 27 combinações de
    rótulos dos três bases e devolve no máximo 27 vetores de probabilidade
    distintos, de modo que a AUC da saída dele mede essa discretização, não a
    capacidade de ordenação do modelo.

    `class_names` dá o nome de cada código de classe, como em
    `metrics_from_confusion`; o número de classes é sempre o de `CLASS_NAMES`.

    Levanta `ValueError` se as probabilidades não tiverem uma coluna por classe
    e uma linha por amostra, que é o que acontece ao passar rótulos no lugar.
    """
    y_true = np.asarray(y_true)
    proba = np.asarray(proba)
    _check_proba(proba, len(y_true))

    labels = list(range(len(class_names)))
    metrics = metrics_from_confusion(
        confusion_matrix(y_true, y_pred, labels=labels).tolist(), class_names
    )
    metrics["roc_auc_ovr_macro"], pr_auc = _ranking_metrics(y_true, proba, class_names)
    for name in class_names:
        metrics["per_class"][name]["pr_auc"] = pr_auc[name]

    if base_mean_proba is not None:
        base_mean_proba = np.asarray(base_mean_proba)
        _check_proba(base_mean_proba, len(y_true))
        metrics["roc_auc_ovr_macro_base_mean"], pr_auc = _ranking_metrics(
            y_true, base_mean_proba, class_names
        )
        for name in class_names:
            metrics["per_class"][name]["pr_auc_base_mean"] = pr_auc[name]
    return metrics


def _malicious_recall(y_pred: np.ndarray) -> dict:
    """Resume as predições de fluxos que são todos Malicious-DoH.

    Devolve o número de fluxos, os detectados, o recall com intervalo de
    confiança binomial exato (Clopper-Pearson) e, em `predicted_as`, quantos
    fluxos foram para cada classe, pelo nome.
    """
    predicted = np.bincount(y_pred, minlength=len(CLASS_NAMES))
    n, detected = len(y_pred), int(predicted[MALICIOUS])
    interval = binomtest(detected, n).proportion_ci(
        confidence_level=CONFIDENCE_LEVEL, method="exact"
    )
    return {
        "n": n,
        "detected": detected,
        "recall": detected / n,
        "recall_ci_level": CONFIDENCE_LEVEL,
        "recall_ci_low": float(interval.low),
        "recall_ci_high": float(interval.high),
        "predicted_as": dict(zip(CLASS_NAMES, predicted.tolist(), strict=True)),
    }


def recall_by_tool(tool: ArrayLike, y_pred: ArrayLike) -> dict:
    """Calcula o recall de Malicious-DoH de cada ferramenta de túnel.

    `tool` traz a ferramenta de cada fluxo e fica vazia fora da classe
    maliciosa; as linhas sem ferramenta não entram. Devolve, para cada
    ferramenta presente, o número de fluxos (`n`), os detectados, o recall com
    intervalo de confiança binomial exato e a classe atribuída a cada fluxo.
    """
    tool = pd.Series(np.asarray(tool, dtype=object))
    y_pred = np.asarray(y_pred)
    return {
        name: _malicious_recall(y_pred[(tool == name).to_numpy()])
        for name in sorted(tool.dropna().unique())
    }


def malicious_only_metrics(tool: ArrayLike, y_pred: ArrayLike) -> dict:
    """Avalia um conjunto em que todos os fluxos são Malicious-DoH.

    `tool` é a ferramenta de túnel de cada fluxo. Devolve o recall da classe
    maliciosa no conjunto todo (`malicious`) e por ferramenta (`by_tool`), cada
    um com `n`, intervalo de confiança e a classe para onde foram os erros.
    """
    # Sem fluxo legítimo no conjunto não existe falso positivo: precisão e FPR
    # não são definidos, e a acurácia repetiria o recall. Nenhum dos três é
    # devolvido, para não entrar em tabela ao lado de conjunto com três classes.
    y_pred = np.asarray(y_pred)
    return {
        "negatives": 0,
        "malicious": _malicious_recall(y_pred),
        "by_tool": recall_by_tool(tool, y_pred),
    }


def outside_unit_interval(X_scaled: ArrayLike) -> dict:
    """Conta os valores normalizados que caem fora do intervalo de 0 a 1.

    `X_scaled` tem os 29 atributos, na ordem de `FEATURE_COLUMNS`, já
    transformados pelo normalizador. Devolve o total de valores fora do
    intervalo (`values`), o número de linhas com ao menos um (`rows`) e a
    contagem de cada atributo que tem algum (`by_column`).
    """
    # O normalizador conhece só o treino: valor abaixo do mínimo ou acima do
    # máximo do treino sai do intervalo, e a contagem mede mudança de faixa.
    X_scaled = np.asarray(X_scaled)
    outside = pd.DataFrame((X_scaled < 0) | (X_scaled > 1), columns=FEATURE_COLUMNS)
    by_column = outside.sum()
    return {
        "values": int(by_column.sum()),
        "rows": int(outside.any(axis=1).sum()),
        "by_column": {name: int(count) for name, count in by_column.items() if count > 0},
    }


def base_rate(fpr: float, recall: float, prevalence: float) -> dict:
    """Aplica a taxa base a um detector com o FPR e o recall dados.

    `prevalence` é a fração de fluxos maliciosos no tráfego. É obrigatória e
    não tem valor padrão: o conjunto de dados não a mede, então quem chama
    declara o valor hipotético que está usando.

    Devolve a prevalência, a precisão operacional (fração dos alertas que são
    ataque, pelo teorema de Bayes) e os alarmes falsos a cada dez milhões de fluxos.
    """
    true_alerts = prevalence * recall
    false_alerts = (1 - prevalence) * fpr
    return {
        "prevalence": prevalence,
        "operational_precision": _ratio(true_alerts, true_alerts + false_alerts),
        "false_alarms_per_10_million": BASE_RATE_FLOWS * false_alerts,
    }


def aggregate_seeds(runs: list[dict]) -> dict:
    """Resume uma métrica por seed em média e desvio padrão.

    `runs` tem um dicionário por seed, todos com as mesmas chaves e um número
    em cada uma. Devolve, para cada chave, a média (`mean`), o desvio padrão
    amostral (`std`) e o número de seeds (`n`).
    """
    # Desvio padrão amostral, com n - 1 no denominador: as seeds são uma
    # amostra das execuções possíveis, não todas elas.
    return {
        key: {
            "mean": float(np.mean([run[key] for run in runs])),
            "std": float(np.std([run[key] for run in runs], ddof=1)),
            "n": len(runs),
        }
        for key in runs[0]
    }


def paired_comparison(first: ArrayLike, second: ArrayLike) -> dict:
    """Compara dois modelos pela mesma métrica, seed a seed.

    `first` e `second` trazem o valor da métrica de cada modelo, na mesma ordem
    de seeds; vence a seed quem tem o valor maior. Devolve a diferença média
    (primeiro menos segundo), o desvio padrão amostral das diferenças, o
    número de seeds em que cada um vence, os empates e a estatística e o
    p-valor do teste de postos sinalizados de Wilcoxon, bilateral.
    """
    difference = np.asarray(first, dtype=float) - np.asarray(second, dtype=float)
    result = {
        "mean_difference": float(difference.mean()),
        # Desvio das diferenças seed a seed, e não o de cada modelo entre as
        # seeds: no par, o que varia de um split para outro se cancela.
        "std_difference": float(difference.std(ddof=1)),
        "first_wins": int((difference > 0).sum()),
        "second_wins": int((difference < 0).sum()),
        "ties": int((difference == 0).sum()),
        "wilcoxon_statistic": None,
        "wilcoxon_p_value": None,
    }
    # O teste ordena as diferenças não nulas. Com todas nulas não há o que
    # ordenar, e a estatística fica vazia em vez de sugerir um resultado.
    if np.any(difference != 0):
        test = wilcoxon(difference)
        result["wilcoxon_statistic"] = float(test.statistic)
        result["wilcoxon_p_value"] = float(test.pvalue)
    return result


def _difference_pp(obtained: dict, target: dict) -> dict:
    """Devolve, em pontos percentuais, a diferença de cada métrica entre dois resultados."""
    aggregated = ["accuracy"] + [
        f"{average}_{metric}" for average in ("macro", "weighted") for metric in CLASS_METRICS
    ]
    difference = {key: 100 * (obtained[key] - target[key]) for key in aggregated}
    difference["per_class"] = {
        name: {
            metric: 100 * (obtained["per_class"][name][metric] - target["per_class"][name][metric])
            for metric in CLASS_METRICS
        }
        for name in CLASS_NAMES
    }
    return difference


def compare_confusion(obtained: list[list[int]], target: list[list[int]]) -> dict:
    """Mede a distância entre a matriz obtida e a matriz alvo, as duas na ordem de `CLASS_NAMES`.

    Devolve a diferença célula a célula (obtida menos alvo), a soma das
    diferenças absolutas, a diferença de total e a diferença de cada métrica
    em pontos percentuais.

    As matrizes podem ter totais diferentes. Nesse caso a soma das diferenças
    absolutas nunca é menor que a diferença de total, e essa parte da distância
    vem do tamanho dos conjuntos, não de erro do modelo.
    """
    cell_difference = [
        [int(cell) - int(target_cell) for cell, target_cell in zip(row, target_row, strict=True)]
        for row, target_row in zip(obtained, target, strict=True)
    ]
    return {
        "cell_difference": cell_difference,
        "absolute_difference_sum": sum(abs(cell) for row in cell_difference for cell in row),
        "total_difference": sum(map(sum, cell_difference)),
        "metric_difference_pp": _difference_pp(
            metrics_from_confusion(obtained), metrics_from_confusion(target)
        ),
    }
