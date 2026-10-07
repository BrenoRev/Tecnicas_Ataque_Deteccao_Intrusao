"""E1: reprodução do Balanced Stacked Random Forest do artigo, nas duas leituras de profundidade.

Lê data/processed/cira.parquet, separa 10% para teste com a seed 42, ajusta o
normalizador no treino, monta os três subconjuntos balanceados, treina um
Random Forest em cada um e empilha os três sob uma regressão logística. Avalia
no teste, ao lado da Fig. 4b e da Tabela II do artigo, e em validação cruzada
de 10 folds sobre o treino, ao lado da Fig. 4a.

O artigo traz duas passagens sobre a profundidade das árvores, e o sistema é
treinado e avaliado uma vez com cada uma, no mesmo protocolo: profundidade
máxima 5 (Seção IV-B), na trilha fiel, e sem limite ("variable tree depth",
linha 3 do Algoritmo 1), como variante.

Grava metrics.json e run.json em results/e1/fiel/proposto/seed42/ e em
results/e1/variante/profundidade_variavel/seed42/, a leitura dos números de
cada execução no RESUMO.md da pasta da trilha e as duas lado a lado em
results/e1/RESUMO.md.

Uso: uv run python scripts/e1_reproducao.py
"""

import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import (
    ARTICLE_SUBSET_RATIO,
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    CV_FOLDS,
    CV_SHUFFLE,
    FEATURE_COLUMNS,
    FIEL_READINGS,
    FIG4A_CONFUSION,
    FIG4B_CONFUSION,
    MAX_DEPTH,
    MAX_DEPTH_VARIABLE,
    MAX_FEATURES,
    N_ESTIMATORS,
    N_JOBS,
    N_SUBSETS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    TABLE_II,
    TEST_SIZE,
    smote_seed,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.evaluate import compare_confusion, evaluate, metrics_from_confusion
from doh_ids.runlog import save_run
from doh_ids.splits import stratified_split
from doh_ids.system import cross_validated_confusion, fit_system

# Resultados da etapa de dados, com os quais esta execução é conferida.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"

LABELS = list(range(len(CLASS_NAMES)))
NON_DOH = CLASS_NAMES.index("Non-DoH")
BENIGN = CLASS_NAMES.index("Benign-DoH")
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")

# As duas leituras da profundidade dos Random Forests base. Tudo o mais é
# igual nas duas: dados, seed, split, subconjuntos, SMOTE e meta-classificador.
READINGS = [
    {
        "track": "fiel",
        "slice_name": "proposto",
        "max_depth": MAX_DEPTH,
        "label": f"fiel (profundidade {MAX_DEPTH})",
        "base_depth": f"profundidade máxima {MAX_DEPTH} nos submodelos (Seção IV-B)",
    },
    {
        "track": "variante",
        "slice_name": "profundidade_variavel",
        "max_depth": MAX_DEPTH_VARIABLE,
        "label": "variante (profundidade variável)",
        "base_depth": 'sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1)',
    },
]


def base_mean_proba(stacked: StackingClassifier, X: np.ndarray) -> np.ndarray:
    """Devolve a média das probabilidades por classe dos Random Forests base."""
    return np.mean([forest.predict_proba(X) for forest in stacked.clfs_], axis=0)


def base_models_test(stacked: StackingClassifier, X_test: np.ndarray, y_test: np.ndarray) -> list:
    """Avalia cada Random Forest base sozinho no teste, na ordem dos subconjuntos.

    Devolve, para cada base, as métricas de `metrics_from_confusion`.
    """
    return [
        metrics_from_confusion(confusion_matrix(y_test, forest.predict(X_test), labels=LABELS))
        for forest in stacked.clfs_
    ]


def meta_decision_table(
    stacked: StackingClassifier, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray
) -> list[dict]:
    """Lista a classe que o meta-classificador devolve para cada combinação de rótulos dos bases.

    São as 27 combinações dos rótulos dos três bases. Cada uma traz as linhas
    do treino original em que ocorre, por classe real, que é o que o
    meta-classificador vê ao ser ajustado, e o número de linhas do teste.
    """
    combinations = np.array(list(itertools.product(LABELS, repeat=N_SUBSETS)))
    meta_labels = stacked.meta_clf_.predict(combinations)
    train_labels = stacked.predict_meta_features(X_train)
    test_labels = stacked.predict_meta_features(X_test)
    table = []
    for combination, meta_label in zip(combinations, meta_labels, strict=True):
        in_train = (train_labels == combination).all(axis=1)
        table.append(
            {
                "base_labels": combination.tolist(),
                "meta_label": int(meta_label),
                "train_rows_by_class": np.bincount(
                    y_train[in_train], minlength=len(CLASS_NAMES)
                ).tolist(),
                "test_rows": int((test_labels == combination).all(axis=1).sum()),
            }
        )
    return table


def subset_summary(summary: list[dict]) -> list[dict]:
    """Acrescenta a cada subconjunto a razão entre as classes na escala do artigo."""
    # O artigo declara 15:12:12 (Seção III-B) e não informa o alvo do SMOTE. A
    # classe benigna é igualada à maliciosa, e a razão obtida é escrita com a
    # classe maliciosa valendo o mesmo que na razão declarada, para ficar ao
    # lado dela.
    scale = ARTICLE_SUBSET_RATIO[MALICIOUS]
    return [
        {
            **entry,
            "ratio_article_scale": [scale * value for value in entry["ratio"]],
            "article_ratio": ARTICLE_SUBSET_RATIO,
        }
        for entry in summary
    ]


def table_ii_comparison(test_metrics: dict) -> dict:
    """Põe a linha do modelo proposto da Tabela II ao lado das métricas do teste.

    Devolve, para cada métrica da tabela, o valor do artigo, os valores obtidos
    e a diferença de cada um para o artigo, em pontos percentuais.
    """
    # A Tabela II não diz que média usa nem como calcula a AUC com três classes.
    # Cada valor do artigo é comparado com a nossa média macro e com a
    # ponderada, e a AUC com as duas formas de calculá-la, todas com o nome.
    obtained = {
        "auc": ["roc_auc_ovr_macro", "roc_auc_ovr_macro_base_mean"],
        "accuracy": ["accuracy"],
        "f1": ["macro_f1", "weighted_f1"],
        "precision": ["macro_precision", "weighted_precision"],
        "recall": ["macro_recall", "weighted_recall"],
    }
    comparison = {}
    for metric, target in TABLE_II["balanced_stacked_rf"].items():
        values = {name: test_metrics[name] for name in obtained[metric]}
        comparison[metric] = {
            "table_ii": target,
            "obtained": values,
            "difference_pp": {name: 100 * (value - target) for name, value in values.items()},
        }
    return comparison


def experiment_metrics(
    scaler: MinMaxScaler,
    stacked: StackingClassifier,
    summary: list[dict],
    train: pd.DataFrame,
    test: pd.DataFrame,
    cv_confusion: list[list[int]],
) -> dict:
    """Avalia o sistema ajustado e monta o dicionário gravado em metrics.json."""
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    X_test = scaler.transform(feature_matrix(test))
    y_test = test["label"].to_numpy()
    test_metrics = evaluate(
        y_test,
        stacked.predict(X_test),
        stacked.predict_proba(X_test),
        base_mean_proba(stacked, X_test),
    )

    # Amostra sintética só existe dentro dos subconjuntos de treino: cada matriz
    # tem, por classe, exatamente as linhas reais do conjunto avaliado.
    test_rows, train_rows = class_counts(test), class_counts(train)
    assert [sum(row) for row in test_metrics["confusion_matrix"]] == test_rows
    assert [sum(row) for row in cv_confusion] == train_rows

    decision_table = meta_decision_table(stacked, X_train, y_train, X_test)
    disagreement = sum(
        entry["test_rows"] for entry in decision_table if len(set(entry["base_labels"])) > 1
    )
    return {
        "classes": CLASS_NAMES,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "test": test_metrics,
        "cross_validation": metrics_from_confusion(cv_confusion),
        "fig4b_comparison": {
            "fig4b": FIG4B_CONFUSION,
            **compare_confusion(test_metrics["confusion_matrix"], FIG4B_CONFUSION),
        },
        "fig4a_comparison": {
            "fig4a": FIG4A_CONFUSION,
            **compare_confusion(cv_confusion, FIG4A_CONFUSION),
        },
        "table_ii_comparison": table_ii_comparison(test_metrics),
        "subsets": subset_summary(summary),
        "base_models_test": base_models_test(stacked, X_test, y_test),
        "meta_decision_table": decision_table,
        "base_disagreement_test_rows": disagreement,
        "base_disagreement_test_fraction": disagreement / len(test),
    }


def run_config(stacked: StackingClassifier, reading: dict) -> dict:
    """Monta a configuração gravada em run.json: hiperparâmetros e leituras adotadas."""
    return {
        "n_estimators": N_ESTIMATORS,
        # A profundidade é lida do modelo ajustado, para o registro dizer o que
        # foi treinado e não o que foi pedido.
        "max_depth": stacked.clfs_[0].max_depth,
        "max_features": MAX_FEATURES,
        "criterion": stacked.clfs_[0].criterion,
        "n_subsets": N_SUBSETS,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "cv_shuffle": CV_SHUFFLE,
        "n_jobs": N_JOBS,
        "smote_seeds": [smote_seed(SEED_FIEL, index) for index in range(N_SUBSETS)],
        "readings": {**FIEL_READINGS, "base_depth": reading["base_depth"]},
    }


def run_experiment(
    table: pd.DataFrame, data_sha256: str, results_dir: Path, reading: dict
) -> tuple[Path, dict]:
    """Treina e avalia o sistema sobre `table` e grava o resultado em `results_dir`.

    `table` tem os atributos do modelo e `label`; `reading` é uma das entradas
    de `READINGS` e diz a profundidade dos bases, a trilha e a pasta do
    resultado. Devolve o diretório da execução e o dicionário de métricas
    gravado em metrics.json.
    """
    start = time.perf_counter()
    # O teste é separado antes de qualquer ajuste e só volta na avaliação final.
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."

    scaler, stacked, summary, timings = fit_system(train, SEED_FIEL, reading["max_depth"])

    cv_start = time.perf_counter()
    cv_confusion = cross_validated_confusion(train, SEED_FIEL, reading["max_depth"])
    timings["cross_validation_seconds"] = round(time.perf_counter() - cv_start, 1)

    metrics = experiment_metrics(scaler, stacked, summary, train, test, cv_confusion)
    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    run_dir = save_run(
        experiment="e1",
        track=reading["track"],
        slice_name=reading["slice_name"],
        seed=SEED_FIEL,
        metrics=metrics,
        config=run_config(stacked, reading),
        data_sha256=data_sha256,
        timings=timings,
        results_dir=results_dir,
    )
    return run_dir, metrics


def markdown_table(frame: pd.DataFrame) -> str:
    """Escreve a tabela, com o índice na primeira coluna, em Markdown."""
    frame = frame.reset_index()
    lines = [" | ".join(frame.columns), " | ".join("---" for _ in frame.columns)]
    lines += [" | ".join(str(value) for value in row) for row in frame.itertuples(index=False)]
    return "\n".join(f"| {line} |" for line in lines)


def matrix_table(confusion: list[list[int]]) -> str:
    """Escreve uma matriz de confusão em Markdown, com o nome das classes."""
    index = pd.Index(CLASS_NAMES, name="real \\ predito")
    return markdown_table(pd.DataFrame(confusion, index=index, columns=CLASS_NAMES))


def confusion_tables(obtained: list[list[int]], target: list[list[int]], figure: str) -> str:
    """Escreve a matriz obtida, a da figura do artigo e a diferença, célula a célula."""
    blocks = [
        ("Reprodução", obtained),
        (f"Artigo, {figure}", target),
        ("Diferença (reprodução menos artigo)", np.subtract(obtained, target).tolist()),
    ]
    return "\n\n".join(f"{title}:\n\n{matrix_table(matrix)}" for title, matrix in blocks)


def distance_text(comparison: dict, obtained_total: int) -> str:
    """Escreve a distância entre a matriz obtida e a do artigo, em contagens e em métricas."""
    difference = comparison["metric_difference_pp"]
    return (
        f"Soma das diferenças absolutas: {comparison['absolute_difference_sum']}. "
        f"Diferença de total: {comparison['total_difference']} (a matriz obtida soma "
        f"{obtained_total} fluxos; essa parte da distância vem do tamanho do conjunto). "
        f"Diferença em pontos percentuais: acurácia {difference['accuracy']:+.4f}, "
        f"precisão macro {difference['macro_precision']:+.4f}, "
        f"recall macro {difference['macro_recall']:+.4f}, "
        f"F1 macro {difference['macro_f1']:+.4f}."
    )


def never_predicted_text(confusion: list[list[int]]) -> str:
    """Escreve o aviso sobre as classes que o modelo não prediz em nenhuma linha.

    Devolve texto vazio quando todas as classes são preditas ao menos uma vez.
    """
    never = [name for index, name in enumerate(CLASS_NAMES) if not any(r[index] for r in confusion)]
    if not never:
        return ""
    return (
        f"O modelo não prediz {' nem '.join(never)} em nenhuma linha. A precisão de uma "
        "classe sem predição é indefinida: ela entra como 0 na precisão macro e no F1 "
        "macro, em vez de a classe sair da média."
    )


def metric_lines(test: dict) -> str:
    """Escreve uma linha de interpretação para cada métrica principal do teste."""
    per_class, binary = test["per_class"], test["malicious_vs_rest"]
    malicious, benign = per_class["Malicious-DoH"], per_class["Benign-DoH"]
    confusion = test["confusion_matrix"]
    missed = malicious["support"] - confusion[MALICIOUS][MALICIOUS]
    benign_missed = benign["support"] - confusion[BENIGN][BENIGN]
    non_doh_share = per_class["Non-DoH"]["support"] / test["total"]
    return f"""- **Acurácia {test["accuracy"]:.4%}.** Fração dos fluxos do teste com a classe certa.
  {non_doh_share:.1%} do teste é Non-DoH, então a acurácia mede sobretudo essa
  classe e, sozinha, não diz se o túnel é detectado.
- **Recall de Malicious-DoH {malicious["recall"]:.4%}.** Fluxos de túnel no teste:
  {malicious["support"]}; classificados em outra classe: {missed}. São os túneis que
  passam sem alerta.
- **Precisão de Malicious-DoH {malicious["precision"]:.4%}.** Fração dos alertas de túnel
  que são túnel de fato, na proporção de classes deste teste; em uma rede com
  menos tráfego malicioso a precisão é menor.
- **FPR de Malicious-DoH contra o resto {binary["fpr"]:.4%}.** {binary["false_positives"]} de
  {binary["negatives"]} fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de
  {binary["fpr_ci_level"]:.0%}: de {binary["fpr_ci_low"]:.4%} a {binary["fpr_ci_high"]:.4%}.
- **Recall de Benign-DoH {benign["recall"]:.4%}.** Fluxos de DoH legítimo no
  teste: {benign["support"]}; classificados em outra classe: {benign_missed}. É a classe
  menor; o erro troca DoH legítimo por outra classe e só vira alarme falso
  quando a classe atribuída é Malicious-DoH.
- **F1 macro {test["macro_f1"]:.4%}, precisão macro {test["macro_precision"]:.4%}, recall
  macro {test["macro_recall"]:.4%}.** A média macro pesa as três classes por igual, e
  por isso mostra o erro em Benign-DoH que a média ponderada
  (F1 ponderado {test["weighted_f1"]:.4%}) esconde.
- **AUC-ROC one-vs-rest macro: {test["roc_auc_ovr_macro"]:.6f} pela saída do
  meta-classificador e {test["roc_auc_ovr_macro_base_mean"]:.6f} pela média das
  probabilidades dos bases.** A primeira ordena os fluxos só pelas combinações
  de rótulos dos três bases; a segunda mede a capacidade de ordenação dos
  Random Forests. Nenhuma das duas depende do limiar de decisão."""


def base_models_table(base_models: list[dict]) -> str:
    """Escreve a matriz de confusão e o recall e a precisão de Benign-DoH de cada base no teste."""
    blocks = []
    for number, base in enumerate(base_models, start=1):
        benign = base["per_class"]["Benign-DoH"]
        blocks.append(
            f"Base {number}: recall de Benign-DoH {benign['recall']:.4%}, precisão de "
            f"Benign-DoH {benign['precision']:.4%}, acurácia {base['accuracy']:.4%}.\n\n"
            f"{matrix_table(base['confusion_matrix'])}"
        )
    return "\n\n".join(blocks)


def table_ii_table(comparison: dict) -> str:
    """Escreve a linha do modelo proposto da Tabela II ao lado das métricas obtidas."""
    rows = [
        [metric, entry["table_ii"], name, f"{value:.6f}", f"{entry['difference_pp'][name]:+.4f}"]
        for metric, entry in comparison.items()
        for name, value in entry["obtained"].items()
    ]
    columns = ["métrica da Tabela II", "artigo", "métrica obtida", "valor", "diferença (pp)"]
    return markdown_table(pd.DataFrame(rows, columns=columns).set_index(columns[0]))


def subsets_table(subsets: list[dict]) -> str:
    """Escreve as contagens, a razão obtida e a fração sintética de cada subconjunto."""
    rows = [
        [
            entry["class_counts"],
            ":".join(f"{value:.1f}" for value in entry["ratio_article_scale"]),
            f"{entry['synthetic_benign_fraction']:.2%}",
        ]
        for entry in subsets
    ]
    columns = ["amostras por classe", "razão obtida", "Benign-DoH sintético"]
    index = pd.RangeIndex(1, len(subsets) + 1, name="subconjunto")
    return markdown_table(pd.DataFrame(rows, columns=columns, index=index))


def decisions_table(decision_table: list[dict]) -> str:
    """Escreve a decisão do meta-classificador para cada combinação de rótulos dos bases."""
    rows = [
        [
            str(entry["base_labels"]),
            entry["meta_label"],
            entry["train_rows_by_class"],
            entry["test_rows"],
        ]
        for entry in decision_table
    ]
    columns = [
        "rótulos dos três bases",
        "classe do meta",
        "linhas do treino por classe real",
        "linhas do teste",
    ]
    return markdown_table(pd.DataFrame(rows, columns=columns).set_index(columns[0]))


def meta_text(metrics: dict) -> str:
    """Escreve o que o meta-classificador recebe e onde ele contraria os bases."""
    decision_table = metrics["meta_decision_table"]
    outside = [entry for entry in decision_table if entry["meta_label"] not in entry["base_labels"]]
    return (
        "O meta-classificador recebe o rótulo predito por cada base, como número. Ele é "
        "ajustado no treino original, sobre as predições de bases que já viram essas "
        "linhas ao serem treinados: todo o Benign-DoH e todo o Malicious-DoH estão nos três "
        "subconjuntos, e cada linha de Non-DoH em um deles. O artigo não descreve esse "
        "passo; a alternativa, com predições fora da amostra, não foi medida aqui.\n\n"
        f"Os bases discordam em {metrics['base_disagreement_test_rows']} linhas do teste "
        f"({metrics['base_disagreement_test_fraction']:.4%}); nas demais os três dão o mesmo "
        "rótulo. Combinações em que o meta devolve uma classe que nenhum base predisse: "
        f"{len(outside)} de {len(decision_table)}, com "
        f"{sum(entry['test_rows'] for entry in outside)} linhas do teste."
    )


def difference_text(metrics: dict) -> str:
    """Escreve, com os números medidos, onde se forma o erro em Benign-DoH."""
    benign = [base["per_class"]["Benign-DoH"] for base in metrics["base_models_test"]]
    recalls = ", ".join(f"{entry['recall']:.2%}" for entry in benign)
    precisions = ", ".join(f"{entry['precision']:.2%}" for entry in benign)
    unanimous = next(
        entry
        for entry in metrics["meta_decision_table"]
        if entry["base_labels"] == [BENIGN] * N_SUBSETS
    )
    by_class = unanimous["train_rows_by_class"]
    composition = ", ".join(
        f"{count} de {name}" for name, count in zip(CLASS_NAMES, by_class, strict=True)
    )
    return (
        f"Sozinhos, no teste, os três bases têm recall de Benign-DoH de {recalls} e "
        f"precisão de Benign-DoH de {precisions}. O modelo empilhado tem recall "
        f"{metrics['test']['per_class']['Benign-DoH']['recall']:.2%} e precisão "
        f"{metrics['test']['per_class']['Benign-DoH']['precision']:.2%} nessa classe.\n\n"
        "A combinação em que os três bases dizem Benign-DoH ocorre em "
        f"{sum(by_class)} linhas do treino original, que é o que o meta-classificador vê: "
        f"{composition}. A classe real mais frequente nela é "
        f"{CLASS_NAMES[int(np.argmax(by_class))]}, e o meta devolve "
        f"{CLASS_NAMES[unanimous['meta_label']]} para ela. No teste a combinação ocorre em "
        f"{unanimous['test_rows']} linhas."
    )


def summary_text(metrics: dict, seen: dict, reading: dict) -> str:
    """Monta o texto do RESUMO.md de uma leitura a partir dos números medidos na execução."""
    test, validation = metrics["test"], metrics["cross_validation"]
    fig4b, fig4a = metrics["fig4b_comparison"], metrics["fig4a_comparison"]
    run_dir = f"{reading['slice_name']}/seed{SEED_FIEL}"
    never_predicted = never_predicted_text(test["confusion_matrix"])
    return f"""# E1: reprodução do Balanced Stacked Random Forest, {reading["label"]}

Gerado por `scripts/e1_reproducao.py`. Os números vêm de
`{run_dir}/metrics.json`; os tempos de treino estão em `{run_dir}/run.json`.
Random Forests base: {reading["base_depth"]}. A outra leitura da profundidade
está ao lado desta em `../RESUMO.md`.
Uma única execução, com a seed {SEED_FIEL}: não há média nem desvio padrão.
Classes na ordem dos códigos: {", ".join(CLASS_NAMES)}.

## Teste ao lado da Fig. 4b

{confusion_tables(test["confusion_matrix"], fig4b["fig4b"], "Fig. 4b")}

{distance_text(fig4b, test["total"])}

## Métricas do teste

{metric_lines(test)}

{never_predicted}

{seen["total"]} das {test["total"]} linhas do teste ({seen["fraction_total"]:.2%}) têm
vetor de {len(FEATURE_COLUMNS)} atributos idêntico ao de alguma linha do treino; em Non-DoH são
{seen["fraction"][NON_DOH]:.2%}. Para o modelo essas linhas já foram vistas, e as
métricas acima as incluem.

## Validação cruzada ao lado da Fig. 4a

{CV_FOLDS} folds estratificados sobre o treino. Em cada rodada o normalizador,
os subconjuntos, o SMOTE, os bases e o meta são refeitos com os nove folds de
treino; o fold deixado de fora só é predito. A matriz soma o treino original,
sem amostra sintética.

{confusion_tables(validation["confusion_matrix"], fig4a["fig4a"], "Fig. 4a")}

{distance_text(fig4a, validation["total"])}

## Teste ao lado da Tabela II

A Tabela II não diz que média usa nem como calcula a AUC com três classes. Cada
valor do artigo aparece ao lado da nossa média macro e da ponderada.

{table_ii_table(metrics["table_ii_comparison"])}

## Subconjuntos de treino

O artigo declara a razão {":".join(map(str, ARTICLE_SUBSET_RATIO))} em cada subconjunto. A razão
obtida está escrita com Malicious-DoH valendo {ARTICLE_SUBSET_RATIO[MALICIOUS]}.

{subsets_table(metrics["subsets"])}

## Bases isolados no teste

Cada Random Forest base avaliado sozinho, antes do empilhamento.

{base_models_table(metrics["base_models_test"])}

## Meta-classificador

{meta_text(metrics)}

{decisions_table(metrics["meta_decision_table"])}

## O que não foi feito

- A busca de hiperparâmetros do artigo não é refeita: a grade não foi
  publicada, e os valores usados são os finais do artigo.
- One-sided selection não é aplicada: o artigo a cita sem descrever.
- A validação cruzada grava só a matriz de confusão; a AUC é calculada só no teste.

## Onde a matriz difere da do artigo

{difference_text(metrics)}

O artigo não informa a seed, a lista dos {len(FEATURE_COLUMNS)} atributos, a limpeza, o alvo e os
parâmetros do SMOTE, como o Non-DoH é dividido em três partes nem com que dados
o meta-classificador é treinado; as versões das bibliotecas são outras. Nenhuma
seed, hiperparâmetro ou regra de limpeza foi ajustada para aproximar o resultado.
"""


def side_by_side(target: list[list[int]], figure: str, obtained: dict) -> str:
    """Põe a matriz do artigo e as de cada leitura lado a lado, com as métricas por classe.

    `obtained` leva o nome de cada leitura à matriz de confusão dela.
    """
    matrices = {f"Artigo, {figure}": target, **obtained}
    columns = {name: metrics_from_confusion(matrix) for name, matrix in matrices.items()}
    rows = {
        "soma das diferenças absolutas": [
            compare_confusion(matrix, target)["absolute_difference_sum"]
            for matrix in matrices.values()
        ],
        "acurácia": [f"{column['accuracy']:.4%}" for column in columns.values()],
    }
    for name in CLASS_NAMES:
        for key, title in [("precision", "precisão"), ("recall", "recall"), ("f1", "F1")]:
            rows[f"{title} de {name}"] = [
                f"{column['per_class'][name][key]:.4%}" for column in columns.values()
            ]
    for key, title in [("precision", "precisão"), ("recall", "recall"), ("f1", "F1")]:
        rows[f"{title} macro"] = [f"{column[f'macro_{key}']:.4%}" for column in columns.values()]
    rows["FPR de Malicious-DoH contra o resto"] = [
        f"{column['malicious_vs_rest']['fpr']:.4%}" for column in columns.values()
    ]
    frame = pd.DataFrame.from_dict(rows, orient="index", columns=list(matrices))
    frame.index.name = "medida"
    blocks = [f"{name}:\n\n{matrix_table(matrix)}" for name, matrix in matrices.items()]
    return "\n\n".join([*blocks, markdown_table(frame)])


def comparison_text(results: list[tuple[dict, dict]]) -> str:
    """Monta o RESUMO.md que põe as leituras da profundidade lado a lado contra o artigo.

    `results` tem um par (leitura, métricas) por execução.
    """
    test = {reading["label"]: metrics["test"] for reading, metrics in results}
    validation = {
        reading["label"]: metrics["cross_validation"]["confusion_matrix"]
        for reading, metrics in results
    }
    readings = "\n".join(
        f"- **{reading['label']}:** {reading['base_depth']}. Detalhe em "
        f"`{reading['track']}/RESUMO.md`."
        for reading, _ in results
    )
    bases = "\n".join(
        f"- **{reading['label']}:** recall de Benign-DoH "
        + ", ".join(
            f"{b['per_class']['Benign-DoH']['recall']:.2%}" for b in metrics["base_models_test"]
        )
        + "; precisão de Benign-DoH "
        + ", ".join(
            f"{b['per_class']['Benign-DoH']['precision']:.2%}" for b in metrics["base_models_test"]
        )
        + "."
        for reading, metrics in results
    )
    warnings = "\n".join(
        f"- **{label}:** {never_predicted_text(entry['confusion_matrix'])}"
        for label, entry in test.items()
        if never_predicted_text(entry["confusion_matrix"])
    )
    first = results[0][1]["test"]
    benign_support = first["per_class"]["Benign-DoH"]["support"]
    return f"""# E1: as duas leituras da profundidade ao lado do artigo

Gerado por `scripts/e1_reproducao.py`. O artigo traz duas passagens sobre a
profundidade das árvores dos Random Forests base, e o sistema foi treinado e
avaliado uma vez com cada uma. Dados, seed ({SEED_FIEL}), split, subconjuntos,
SMOTE e meta-classificador são os mesmos nas duas.

{readings}

Uma única execução de cada leitura: não há média nem desvio padrão.
Classes na ordem dos códigos: {", ".join(CLASS_NAMES)}.

## Teste ao lado da Fig. 4b

{side_by_side(FIG4B_CONFUSION, "Fig. 4b", {k: v["confusion_matrix"] for k, v in test.items()})}

## Validação cruzada de {CV_FOLDS} folds ao lado da Fig. 4a

{side_by_side(FIG4A_CONFUSION, "Fig. 4a", validation)}

## Bases isolados no teste

Os três Random Forests base de cada leitura, avaliados sozinhos:

{bases}

## Como ler a comparação

A soma das diferenças absolutas conta linhas, e Benign-DoH tem {benign_support} das
{first["total"]} linhas do teste ({benign_support / first["total"]:.2%}). Um modelo que nunca prediz
essa classe erra no máximo essas linhas, e a soma quase não registra a perda de
uma classe inteira. As métricas por classe e as médias macro, que pesam as três
classes por igual, registram. Por isso as duas medidas vão lado a lado e
nenhuma leitura é declarada a mais próxima do artigo por um número só.

{warnings}

As duas leituras têm apoio no texto do artigo e as duas são reportadas como
saíram. Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada para
aproximar o resultado.
"""


def main() -> None:
    """Confere o Parquet, roda o experimento nas duas leituras e grava os resumos."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    counts = json.loads((E0_DIR / "split_counts.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )

    table = pd.read_parquet(CIRA_PARQUET_PATH)
    results = []
    for reading in READINGS:
        run_dir, metrics = run_experiment(table, data_sha256, RESULTS_DIR, reading)
        test, validation = metrics["test"], metrics["cross_validation"]
        assert test["total"] == counts["test"]["total"], (
            "Teste com tamanho diferente do registrado."
        )
        assert validation["total"] == counts["train"]["total"], "Validação não soma o treino."

        summary = summary_text(metrics, counts["test_seen_in_train"], reading)
        (run_dir.parents[1] / "RESUMO.md").write_text(summary, encoding="utf-8")
        results.append((reading, metrics))

        print(f"\n== {reading['label']} ==")
        print(confusion_tables(test["confusion_matrix"], FIG4B_CONFUSION, "Fig. 4b"))
        print(distance_text(metrics["fig4b_comparison"], test["total"]))
        print(metric_lines(test))
        print(confusion_tables(validation["confusion_matrix"], FIG4A_CONFUSION, "Fig. 4a"))
        print(distance_text(metrics["fig4a_comparison"], validation["total"]))
        timings = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["timings"]
        print(f"Tempos, em segundos: {timings}")
        print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}")

    (RESULTS_DIR / "e1" / "RESUMO.md").write_text(comparison_text(results), encoding="utf-8")


if __name__ == "__main__":
    main()
