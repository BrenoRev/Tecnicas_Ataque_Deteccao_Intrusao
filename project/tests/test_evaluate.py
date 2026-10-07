import json

import numpy as np
import pytest

from doh_ids.config import CLASS_NAMES, FEATURE_COLUMNS, FIG4A_CONFUSION, FIG4B_CONFUSION
from doh_ids.evaluate import (
    base_rate,
    compare_confusion,
    evaluate,
    malicious_only_metrics,
    metrics_from_confusion,
    outside_unit_interval,
    recall_by_tool,
)
from scripts import metricas_fig4

# O script da Fig. 4 só imprime porcentagens com duas casas: 5e-5 é meia
# unidade da quarta casa decimal da fração.
FOURTH_DECIMAL = 5e-5


def in_project_order(script_matrix):
    """Reordena linhas e colunas de uma matriz do script para a ordem de `CLASS_NAMES`."""
    order = [metricas_fig4.CLASSES.index(name) for name in CLASS_NAMES]
    return [[script_matrix[row][column] for column in order] for row in order]


def labels_from_confusion(confusion):
    """Devolve rótulos reais e preditos que reproduzem a matriz de confusão."""
    y_true, y_pred = [], []
    for real, row in enumerate(confusion):
        for predicted, count in enumerate(row):
            y_true += [real] * count
            y_pred += [predicted] * count
    return np.array(y_true), np.array(y_pred)


def one_hot(labels):
    """Probabilidade 1 na classe indicada, como a de um modelo sem dúvida."""
    return np.eye(len(CLASS_NAMES))[labels]


def test_fig4b_metrics_match_the_published_matrix():
    metrics = metrics_from_confusion(FIG4B_CONFUSION)

    assert metrics["total"] == 115910
    assert metrics["accuracy"] == pytest.approx(0.9978, abs=FOURTH_DECIMAL)
    assert metrics["per_class"]["Benign-DoH"]["recall"] == pytest.approx(0.9023, abs=FOURTH_DECIMAL)
    assert metrics["macro_precision"] == pytest.approx(0.9901, abs=FOURTH_DECIMAL)
    assert metrics["macro_recall"] == pytest.approx(0.9672, abs=FOURTH_DECIMAL)
    assert metrics["macro_f1"] == pytest.approx(0.9782, abs=FOURTH_DECIMAL)
    assert metrics["malicious_vs_rest"]["false_positives"] == 3
    assert metrics["malicious_vs_rest"]["negatives"] == 90955


def test_fig4b_metrics_match_the_reference_script_per_class():
    script_matrix = metricas_fig4.MATRIZES["Fig. 4b (teste)"]
    _, script_rows = metricas_fig4.metricas_por_classe(script_matrix)

    per_class = metrics_from_confusion(FIG4B_CONFUSION)["per_class"]

    for name, support, precision, recall, f1 in script_rows:
        assert per_class[name]["support"] == support
        assert per_class[name]["precision"] == pytest.approx(precision, abs=1e-12)
        assert per_class[name]["recall"] == pytest.approx(recall, abs=1e-12)
        assert per_class[name]["f1"] == pytest.approx(f1, abs=1e-12)


def test_config_matrices_equal_the_script_matrices_after_reordering_classes():
    assert in_project_order(metricas_fig4.MATRIZES["Fig. 4a (treino, CV 10 folds)"]) == (
        FIG4A_CONFUSION
    )
    assert in_project_order(metricas_fig4.MATRIZES["Fig. 4b (teste)"]) == FIG4B_CONFUSION


def test_every_aggregated_metric_key_names_its_average():
    y_true, y_pred = labels_from_confusion([[5, 1, 0], [1, 4, 1], [0, 1, 5]])

    metrics = evaluate(y_true, y_pred, one_hot(y_pred), base_mean_proba=one_hot(y_pred))

    # Só a acurácia e os totais não são média entre classes.
    not_averaged = {"confusion_matrix", "total", "accuracy", "per_class", "malicious_vs_rest"}
    aggregated = set(metrics) - not_averaged
    assert len(aggregated) == 8
    assert all("macro" in key or "weighted" in key for key in aggregated)


def test_perfect_matrix_gives_one_in_every_metric():
    y_true, y_pred = labels_from_confusion([[6, 0, 0], [0, 3, 0], [0, 0, 4]])

    metrics = evaluate(y_true, y_pred, one_hot(y_pred))

    assert metrics["accuracy"] == 1.0
    assert metrics["roc_auc_ovr_macro"] == 1.0
    for average in ("macro", "weighted"):
        for metric in ("precision", "recall", "f1"):
            assert metrics[f"{average}_{metric}"] == 1.0
    for name in CLASS_NAMES:
        assert metrics["per_class"][name]["f1"] == 1.0
        assert metrics["per_class"][name]["pr_auc"] == 1.0
    assert metrics["malicious_vs_rest"]["recall"] == 1.0


def test_zero_false_positives_gives_interval_from_zero_to_positive_upper_bound():
    malicious = metrics_from_confusion([[6, 0, 0], [0, 3, 0], [0, 0, 4]])["malicious_vs_rest"]

    assert malicious["false_positives"] == 0
    assert malicious["fpr"] == 0.0
    assert malicious["fpr_ci_low"] == 0.0
    assert 0.0 < malicious["fpr_ci_high"] < 1.0


def test_evaluate_refuses_labels_in_place_of_probabilities():
    y_true, y_pred = labels_from_confusion([[5, 1, 0], [1, 4, 1], [0, 1, 5]])

    with pytest.raises(ValueError, match="probabilidades"):
        evaluate(y_true, y_pred, y_pred)
    with pytest.raises(ValueError, match="probabilidades"):
        evaluate(y_true, y_pred, one_hot(y_pred), base_mean_proba=y_pred)


def test_base_rate_fails_without_prevalence():
    with pytest.raises(TypeError, match="prevalence"):
        base_rate(fpr=0.01, recall=0.99)


def test_base_rate_matches_the_reference_script_for_fig4b():
    malicious = metrics_from_confusion(FIG4B_CONFUSION)["malicious_vs_rest"]

    result = base_rate(malicious["fpr"], malicious["recall"], metricas_fig4.PREVALENCIA_HIPOTETICA)

    # Valores impressos pelo script: precisão de 75,2% e 330 alarmes falsos.
    assert result["operational_precision"] == pytest.approx(0.752, abs=5e-4)
    assert result["false_alarms_per_10_million"] == pytest.approx(330, abs=0.5)


def test_comparing_a_matrix_with_itself_gives_zero():
    comparison = compare_confusion(FIG4B_CONFUSION, FIG4B_CONFUSION)

    assert comparison["absolute_difference_sum"] == 0
    assert comparison["total_difference"] == 0
    assert comparison["metric_difference_pp"]["accuracy"] == 0.0


def test_moving_samples_between_cells_gives_the_expected_difference():
    target = [[10, 0, 0], [0, 10, 0], [0, 0, 10]]
    obtained = [[10, 0, 0], [3, 7, 0], [0, 0, 10]]

    comparison = compare_confusion(obtained, target)

    assert comparison["cell_difference"] == [[0, 0, 0], [3, -3, 0], [0, 0, 0]]
    assert comparison["absolute_difference_sum"] == 6
    assert comparison["total_difference"] == 0
    assert comparison["metric_difference_pp"]["accuracy"] == pytest.approx(-10.0)
    benign = comparison["metric_difference_pp"]["per_class"]["Benign-DoH"]
    assert benign["recall"] == pytest.approx(-30.0)


def test_matrices_with_different_totals_also_report_the_total_difference():
    # O teste do projeto tem um fluxo a mais que o da Fig. 4b.
    obtained = [list(row) for row in FIG4B_CONFUSION]
    obtained[0][0] += 1

    comparison = compare_confusion(obtained, FIG4B_CONFUSION)

    assert comparison["total_difference"] == 1
    assert comparison["absolute_difference_sum"] == 1


def test_fig4b_built_from_labels_in_project_order_has_zero_distance_to_the_target():
    y_true, y_pred = labels_from_confusion(FIG4B_CONFUSION)

    obtained = evaluate(y_true, y_pred, one_hot(y_pred))["confusion_matrix"]

    assert compare_confusion(obtained, FIG4B_CONFUSION)["absolute_difference_sum"] == 0
    script_matrix = metricas_fig4.MATRIZES["Fig. 4b (teste)"]
    assert compare_confusion(obtained, script_matrix)["absolute_difference_sum"] > 0


def test_evaluate_result_is_json_serializable():
    y_true, y_pred = labels_from_confusion([[5, 1, 0], [1, 4, 1], [0, 1, 5]])

    metrics = evaluate(y_true, y_pred, one_hot(y_pred), base_mean_proba=one_hot(y_pred))

    assert json.loads(json.dumps(metrics)) == metrics


def keys_in(result):
    """Devolve todas as chaves de um dicionário aninhado."""
    if not isinstance(result, dict):
        return set()
    return set(result).union(*(keys_in(value) for value in result.values()))


def test_malicious_only_evaluation_reports_no_precision_fpr_or_accuracy():
    tool = ["dnstt", "dnstt", "tuns", "tuns"]
    y_pred = np.array([2, 0, 2, 1])

    result = malicious_only_metrics(tool, y_pred)

    assert result["negatives"] == 0
    assert result["malicious"]["recall"] == 0.5
    assert result["malicious"]["predicted_as"] == {
        "Non-DoH": 1,
        "Benign-DoH": 1,
        "Malicious-DoH": 2,
    }
    forbidden = ("precision", "fpr", "accuracy", "f1")
    assert not [key for key in keys_in(result) if any(word in key for word in forbidden)]
    assert json.loads(json.dumps(result)) == result


def test_recall_by_tool_matches_a_hand_made_example():
    # Quatro fluxos de dnstt, três detectados; dois de tuns, nenhum detectado.
    # As duas linhas sem ferramenta não são de túnel e não entram na conta,
    # nem a que foi classificada como maliciosa.
    tool = ["dnstt", "dnstt", "dnstt", "dnstt", "tuns", "tuns", None, None]
    y_pred = np.array([2, 2, 2, 0, 1, 0, 2, 0])

    result = recall_by_tool(tool, y_pred)

    assert list(result) == ["dnstt", "tuns"]
    assert (result["dnstt"]["n"], result["dnstt"]["detected"]) == (4, 3)
    assert result["dnstt"]["recall"] == 0.75
    assert result["dnstt"]["predicted_as"]["Non-DoH"] == 1
    assert (result["tuns"]["n"], result["tuns"]["recall"]) == (2, 0.0)
    assert result["tuns"]["predicted_as"] == {"Non-DoH": 1, "Benign-DoH": 1, "Malicious-DoH": 0}
    # Com dois fluxos, o intervalo exato de um recall zero ainda vai longe.
    assert result["tuns"]["recall_ci_low"] == 0.0
    assert 0.5 < result["tuns"]["recall_ci_high"] < 1.0


def test_outside_unit_interval_finds_the_planted_values():
    X_scaled = np.full((5, len(FEATURE_COLUMNS)), 0.5)
    # Os extremos 0 e 1 pertencem ao intervalo.
    X_scaled[0, 0], X_scaled[1, 0] = 0.0, 1.0
    X_scaled[2, 0], X_scaled[3, 0] = 1.5, -0.1
    X_scaled[3, 4] = 7.0

    result = outside_unit_interval(X_scaled)

    assert result["values"] == 3
    assert result["rows"] == 2
    assert result["by_column"] == {FEATURE_COLUMNS[0]: 2, FEATURE_COLUMNS[4]: 1}


def test_metrics_are_keyed_by_the_class_names_given():
    tools = ["dns2tcp", "dnscat2", "iodine"]
    confusion = [[5, 1, 0], [1, 4, 1], [0, 1, 5]]
    y_true, y_pred = labels_from_confusion(confusion)

    metrics = evaluate(y_true, y_pred, one_hot(y_pred), one_hot(y_pred), class_names=tools)

    assert list(metrics["per_class"]) == tools
    assert set(metrics["per_class"]["dnscat2"]) == {
        "support",
        "precision",
        "recall",
        "f1",
        "pr_auc",
        "pr_auc_base_mean",
    }
    # Entre ferramentas não há tráfego legítimo: a visão binária não é devolvida.
    assert "malicious_vs_rest" not in metrics
    # Só os nomes mudam: os números são os da mesma matriz com os nomes padrão.
    default = metrics_from_confusion(confusion)
    assert metrics["accuracy"] == default["accuracy"]
    assert metrics["macro_f1"] == default["macro_f1"]
    assert metrics["per_class"]["dnscat2"]["recall"] == default["per_class"]["Benign-DoH"]["recall"]
