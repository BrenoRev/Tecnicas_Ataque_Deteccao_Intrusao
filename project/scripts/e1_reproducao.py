"""E1: reprodução do Balanced Stacked Random Forest do artigo, na trilha fiel.

Lê data/processed/cira.parquet, separa 10% para teste com a seed 42, ajusta o
normalizador no treino, monta os três subconjuntos balanceados, treina um
Random Forest em cada um e empilha os três sob uma regressão logística. Avalia
no teste, ao lado da Fig. 4b e da Tabela II do artigo, e em validação cruzada
de 10 folds sobre o treino, ao lado da Fig. 4a.

Grava metrics.json e run.json em results/e1/fiel/proposto/seed42/ e a leitura
dos números em results/e1/fiel/RESUMO.md.

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
from sklearn.model_selection import StratifiedKFold
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
from doh_ids.models import base_forests, stacked_forest
from doh_ids.runlog import save_run
from doh_ids.splits import balanced_subsets, fit_scaler, stratified_split

# Resultados da etapa de dados, com os quais esta execução é conferida.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"

LABELS = list(range(len(CLASS_NAMES)))
NON_DOH = CLASS_NAMES.index("Non-DoH")
BENIGN = CLASS_NAMES.index("Benign-DoH")
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")


def fit_system(
    train: pd.DataFrame, seed: int
) -> tuple[MinMaxScaler, StackingClassifier, list[dict], dict]:
    """Ajusta o sistema inteiro só com `train`: normalizador, subconjuntos, bases e meta.

    Devolve o normalizador, o modelo empilhado, o resumo dos subconjuntos e os
    tempos de cada etapa, em segundos.
    """
    scaler = fit_scaler(train)
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    assert X_train.shape[1] == len(FEATURE_COLUMNS) == 29, "O modelo espera os 29 atributos."

    # O artigo cita "one-sided selection with SMOTE" uma única vez (Seção III-B)
    # e não descreve a seleção: ela não é aplicada. O Non-DoH só é dividido em
    # três partes.
    start = time.perf_counter()
    subsets, summary = balanced_subsets(X_train, y_train, seed)
    subsets_seconds = time.perf_counter() - start

    start = time.perf_counter()
    forests = base_forests(subsets, seed)
    base_seconds = time.perf_counter() - start

    start = time.perf_counter()
    stacked = stacked_forest(forests, X_train, y_train, seed)
    meta_seconds = time.perf_counter() - start

    timings = {
        "subsets_seconds": round(subsets_seconds, 1),
        "base_fit_seconds": round(base_seconds, 1),
        "meta_fit_seconds": round(meta_seconds, 1),
    }
    return scaler, stacked, summary, timings


def cross_validated_confusion(train: pd.DataFrame, seed: int) -> list[list[int]]:
    """Soma as matrizes de confusão dos folds de validação, para comparar com a Fig. 4a.

    Cada linha do treino é predita uma vez, pelo sistema ajustado nos outros
    nove folds. A matriz tem a classe real na linha e a predita na coluna.
    """
    # A legenda da Fig. 4a diz que a matriz do treino vem de validação cruzada
    # de 10 folds e não detalha o procedimento. A figura soma o treino original,
    # sem amostra sintética: por isso o normalizador, os subconjuntos, o SMOTE,
    # os bases e o meta são refeitos com os nove folds de treino, e o fold
    # deixado de fora só é transformado e predito.
    folds = StratifiedKFold(n_splits=CV_FOLDS, shuffle=CV_SHUFFLE, random_state=seed)
    total = np.zeros((len(LABELS), len(LABELS)), dtype=int)
    for fit_rows, held_out_rows in folds.split(train, train["label"]):
        scaler, stacked, _, _ = fit_system(train.iloc[fit_rows], seed)
        held_out = train.iloc[held_out_rows]
        predicted = stacked.predict(scaler.transform(feature_matrix(held_out)))
        total += confusion_matrix(held_out["label"], predicted, labels=LABELS)
    return total.tolist()


def base_mean_proba(stacked: StackingClassifier, X: np.ndarray) -> np.ndarray:
    """Devolve a média das probabilidades por classe dos Random Forests base."""
    return np.mean([forest.predict_proba(X) for forest in stacked.clfs_], axis=0)


def meta_decision_table(stacked: StackingClassifier, X_test: np.ndarray) -> list[dict]:
    """Lista a classe que o meta-classificador devolve para cada combinação de rótulos dos bases.

    São as 27 combinações dos rótulos dos três bases, cada uma com o número de
    linhas do teste em que ela ocorre.
    """
    combinations = np.array(list(itertools.product(LABELS, repeat=N_SUBSETS)))
    meta_labels = stacked.meta_clf_.predict(combinations)
    base_labels = stacked.predict_meta_features(X_test)
    return [
        {
            "base_labels": combination.tolist(),
            "meta_label": int(meta_label),
            "test_rows": int((base_labels == combination).all(axis=1).sum()),
        }
        for combination, meta_label in zip(combinations, meta_labels, strict=True)
    ]


def subset_summary(summary: list[dict]) -> list[dict]:
    """Acrescenta a cada subconjunto a razão entre as classes na escala do artigo."""
    # O artigo declara 15:12:12 (Seção III-B) e não informa o alvo do SMOTE. A
    # classe benigna é igualada à maliciosa, e a razão obtida é escrita com a
    # classe maliciosa valendo 12, para ficar ao lado da declarada.
    scale = ARTICLE_SUBSET_RATIO[MALICIOUS]
    return [
        {
            **entry,
            "ratio_malicious_as_12": [scale * value for value in entry["ratio"]],
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


def run_experiment(table: pd.DataFrame, data_sha256: str, results_dir: Path) -> tuple[Path, dict]:
    """Treina e avalia o sistema sobre `table` e grava o resultado em `results_dir`.

    `table` tem os 29 atributos e `label`. Devolve o diretório da execução e o
    dicionário de métricas gravado em metrics.json.
    """
    start = time.perf_counter()
    # O teste é separado antes de qualquer ajuste e só volta na avaliação final.
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."

    scaler, stacked, summary, timings = fit_system(train, SEED_FIEL)

    cv_start = time.perf_counter()
    cv_confusion = cross_validated_confusion(train, SEED_FIEL)
    timings["cross_validation_seconds"] = round(time.perf_counter() - cv_start, 1)

    X_test = scaler.transform(feature_matrix(test))
    test_metrics = evaluate(
        test["label"],
        stacked.predict(X_test),
        stacked.predict_proba(X_test),
        base_mean_proba(stacked, X_test),
    )
    cv_metrics = metrics_from_confusion(cv_confusion)

    # Amostra sintética só existe dentro dos subconjuntos de treino: cada matriz
    # tem, por classe, exatamente as linhas reais do conjunto avaliado.
    test_rows, train_rows = class_counts(test), class_counts(train)
    assert [sum(row) for row in test_metrics["confusion_matrix"]] == test_rows
    assert [sum(row) for row in cv_confusion] == train_rows

    decision_table = meta_decision_table(stacked, X_test)
    disagreement = sum(
        entry["test_rows"] for entry in decision_table if len(set(entry["base_labels"])) > 1
    )
    metrics = {
        "classes": CLASS_NAMES,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "test": test_metrics,
        "cross_validation": cv_metrics,
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
        "meta_decision_table": decision_table,
        "base_disagreement_test_rows": disagreement,
        "base_disagreement_test_fraction": disagreement / len(test),
    }
    config = {
        "n_estimators": N_ESTIMATORS,
        "max_depth": MAX_DEPTH,
        "max_features": MAX_FEATURES,
        "criterion": stacked.clfs_[0].criterion,
        "n_subsets": N_SUBSETS,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "cv_shuffle": CV_SHUFFLE,
        "n_jobs": N_JOBS,
        "smote_seeds": [smote_seed(SEED_FIEL, index) for index in range(N_SUBSETS)],
        "readings": FIEL_READINGS,
    }
    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    run_dir = save_run(
        experiment="e1",
        track="fiel",
        slice_name="proposto",
        seed=SEED_FIEL,
        metrics=metrics,
        config=config,
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


def confusion_tables(obtained: list[list[int]], target: list[list[int]], figure: str) -> str:
    """Escreve a matriz obtida, a da figura do artigo e a diferença, célula a célula."""
    index = pd.Index(CLASS_NAMES, name="real \\ predito")
    difference = np.subtract(obtained, target)
    blocks = [
        ("Reprodução", obtained),
        (f"Artigo, {figure}", target),
        ("Diferença (reprodução menos artigo)", difference),
    ]
    return "\n\n".join(
        f"{title}:\n\n{markdown_table(pd.DataFrame(matrix, index=index, columns=CLASS_NAMES))}"
        for title, matrix in blocks
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


def summary_text(metrics: dict, seen: dict) -> str:
    """Monta o texto de RESUMO.md a partir dos números medidos nesta execução."""
    test, fig4b, fig4a = metrics["test"], metrics["fig4b_comparison"], metrics["fig4a_comparison"]
    table_ii = pd.DataFrame(
        [
            [
                metric,
                entry["table_ii"],
                name,
                f"{value:.6f}",
                f"{entry['difference_pp'][name]:+.4f}",
            ]
            for metric, entry in metrics["table_ii_comparison"].items()
            for name, value in entry["obtained"].items()
        ],
        columns=["métrica da Tabela II", "artigo", "métrica obtida", "valor", "diferença (pp)"],
    ).set_index("métrica da Tabela II")
    subsets = pd.DataFrame(
        [
            [
                entry["class_counts"],
                ":".join(f"{value:.1f}" for value in entry["ratio_malicious_as_12"]),
                f"{entry['synthetic_benign_fraction']:.2%}",
            ]
            for entry in metrics["subsets"]
        ],
        columns=["amostras por classe", "razão obtida", "Benign-DoH sintético"],
        index=pd.RangeIndex(1, N_SUBSETS + 1, name="subconjunto"),
    )
    decisions = pd.DataFrame(
        [
            [str(entry["base_labels"]), entry["meta_label"], entry["test_rows"]]
            for entry in metrics["meta_decision_table"]
        ],
        columns=["rótulos dos três bases", "classe do meta", "linhas do teste"],
    ).set_index("rótulos dos três bases")
    outside = [
        entry
        for entry in metrics["meta_decision_table"]
        if entry["meta_label"] not in entry["base_labels"]
    ]
    return f"""# E1: reprodução do Balanced Stacked Random Forest, trilha fiel

Gerado por `scripts/e1_reproducao.py`. Os números vêm de
`proposto/seed{SEED_FIEL}/metrics.json`; os tempos de treino estão em
`proposto/seed{SEED_FIEL}/run.json`.
Uma única execução, com a seed {SEED_FIEL}: não há média nem desvio padrão.
Classes na ordem dos códigos: {", ".join(CLASS_NAMES)}.

## Teste ao lado da Fig. 4b

{confusion_tables(test["confusion_matrix"], fig4b["fig4b"], "Fig. 4b")}

Soma das diferenças absolutas: {fig4b["absolute_difference_sum"]}. Diferença de
total: {fig4b["total_difference"]} (o teste tem {test["total"]} fluxos e a
Fig. 4b soma {sum(map(sum, fig4b["fig4b"]))}; essa parte da distância vem do
tamanho do conjunto). Diferença em pontos percentuais: acurácia
{fig4b["metric_difference_pp"]["accuracy"]:+.4f}, precisão macro
{fig4b["metric_difference_pp"]["macro_precision"]:+.4f}, recall macro
{fig4b["metric_difference_pp"]["macro_recall"]:+.4f}, F1 macro
{fig4b["metric_difference_pp"]["macro_f1"]:+.4f}.

## Métricas do teste

{metric_lines(test)}

{seen["total"]} das {test["total"]} linhas do teste ({seen["fraction_total"]:.2%}) têm
vetor de 29 atributos idêntico ao de alguma linha do treino; em Non-DoH são
{seen["fraction"][NON_DOH]:.2%}. Para o modelo essas linhas já foram vistas, e as
métricas acima as incluem.

## Validação cruzada ao lado da Fig. 4a

{CV_FOLDS} folds estratificados sobre o treino. Em cada rodada o normalizador,
os subconjuntos, o SMOTE, os bases e o meta são refeitos com os nove folds de
treino; o fold deixado de fora só é predito. A matriz soma o treino original,
sem amostra sintética.

{confusion_tables(metrics["cross_validation"]["confusion_matrix"], fig4a["fig4a"], "Fig. 4a")}

Soma das diferenças absolutas: {fig4a["absolute_difference_sum"]}. Diferença de
total: {fig4a["total_difference"]}. Diferença em pontos percentuais: acurácia
{fig4a["metric_difference_pp"]["accuracy"]:+.4f}, precisão macro
{fig4a["metric_difference_pp"]["macro_precision"]:+.4f}, recall macro
{fig4a["metric_difference_pp"]["macro_recall"]:+.4f}, F1 macro
{fig4a["metric_difference_pp"]["macro_f1"]:+.4f}.

## Teste ao lado da Tabela II

A Tabela II não diz que média usa nem como calcula a AUC com três classes. Cada
valor do artigo aparece ao lado da nossa média macro e da ponderada.

{markdown_table(table_ii)}

## Subconjuntos de treino

O artigo declara a razão {":".join(map(str, ARTICLE_SUBSET_RATIO))} em cada subconjunto. A razão
obtida está escrita com Malicious-DoH valendo {ARTICLE_SUBSET_RATIO[MALICIOUS]}.

{markdown_table(subsets)}

## Meta-classificador

O meta-classificador recebe o rótulo predito por cada base, como número. Os
bases discordam em {metrics["base_disagreement_test_rows"]} linhas do teste
({metrics["base_disagreement_test_fraction"]:.4%}); nas demais os três dão o mesmo
rótulo. Combinações em que o meta devolve uma classe que nenhum base predisse:
{len(outside)} de {len(metrics["meta_decision_table"])}, com
{sum(entry["test_rows"] for entry in outside)} linhas do teste.

{markdown_table(decisions)}

## O que não foi feito

- A busca de hiperparâmetros do artigo não é refeita: a grade não foi
  publicada, e os valores usados são os finais do artigo.
- One-sided selection não é aplicada: o artigo a cita sem descrever.
- A validação cruzada grava só a matriz de confusão; a AUC é calculada só no teste.

## Se a matriz difere da do artigo

Causas possíveis, sem evidência para escolher uma: a seed do artigo não é
informada; o artigo não lista os 29 atributos nem descreve a limpeza; o alvo e
os parâmetros do SMOTE, a divisão do Non-DoH em três partes e os dados de
treino do meta-classificador não estão no texto; as versões das bibliotecas
são outras. Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada para
aproximar o resultado.
"""


def main() -> None:
    """Confere o Parquet, roda o experimento e grava o resumo."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    counts = json.loads((E0_DIR / "split_counts.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )

    table = pd.read_parquet(CIRA_PARQUET_PATH)
    run_dir, metrics = run_experiment(table, data_sha256, RESULTS_DIR)
    test, validation = metrics["test"], metrics["cross_validation"]
    assert test["total"] == counts["test"]["total"], "Teste com tamanho diferente do registrado."
    assert validation["total"] == counts["train"]["total"], "Validação não soma o treino."

    summary = summary_text(metrics, counts["test_seen_in_train"])
    (run_dir.parents[1] / "RESUMO.md").write_text(summary, encoding="utf-8")

    print(confusion_tables(test["confusion_matrix"], FIG4B_CONFUSION, "Fig. 4b"))
    print(
        f"Soma das diferenças absolutas: {metrics['fig4b_comparison']['absolute_difference_sum']}"
    )
    print(metric_lines(test))
    print(confusion_tables(validation["confusion_matrix"], FIG4A_CONFUSION, "Fig. 4a"))
    print(
        f"Soma das diferenças absolutas: {metrics['fig4a_comparison']['absolute_difference_sum']}"
    )
    timings = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["timings"]
    print(f"Tempos, em segundos: {timings}")
    print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
