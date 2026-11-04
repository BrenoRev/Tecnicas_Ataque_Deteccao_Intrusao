"""E2: os três modelos de comparação da Tabela II do artigo, na trilha fiel.

Lê data/processed/cira.parquet, separa o mesmo teste de 10% do modelo proposto
(seed 42), ajusta o normalizador no treino e balanceia o treino inteiro com
SMOTE. Treina a árvore de decisão, o XGBoost e o Random Forest da Tabela II e
avalia cada um no teste, ao lado da sua linha da tabela.

Grava metrics.json e run.json em results/e2/fiel/<modelo>/seed42/ e a Tabela II
inteira em results/e2/fiel/RESUMO.md: os três modelos de comparação, o modelo
proposto (lido dos resultados de scripts/e1_reproducao.py, sem treinar de novo)
e a metade inferior, com os resultados da literatura que o artigo cita.

Uso: uv run python scripts/e2_baselines.py
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    N_JOBS,
    N_SUBSETS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    TABLE_II,
    TABLE_II_FAR_ABOVE_PP,
    TABLE_II_FOREST_TREES,
    TABLE_II_LITERATURE,
    TABLE_II_TREE_DEPTH,
    TEST_SIZE,
    smote_seed,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.evaluate import evaluate
from doh_ids.models import fit_baseline
from doh_ids.runlog import save_run
from doh_ids.splits import balanced_train, fit_scaler, stratified_split
from doh_ids.summary import markdown_table

# Resultados da etapa de dados, com os quais esta execução é conferida.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"

# Resultados do modelo proposto, nas duas leituras da profundidade dos Random
# Forests base. Só entram no resumo, para a Tabela II ficar inteira.
E1_DIR = RESULTS_DIR / "e1"
PROPOSED_RUNS = {
    "Modelo proposto, fiel (profundidade 5)": E1_DIR / "fiel" / "proposto",
    "Modelo proposto, variante (profundidade variável)": E1_DIR
    / "variante"
    / "profundidade_variavel",
}

MALICIOUS = CLASS_NAMES.index("Malicious-DoH")

# Os três modelos de comparação, com o nome da linha na Tabela II e os únicos
# hiperparâmetros que a tabela informa.
BASELINES = {
    "decision_tree": {
        "label": "Árvore de decisão",
        "table_ii_hyperparameters": {"max_depth": TABLE_II_TREE_DEPTH},
    },
    "xgboost": {"label": "XGBoost", "table_ii_hyperparameters": {}},
    "random_forest": {
        "label": "Random Forest",
        "table_ii_hyperparameters": {"n_estimators": TABLE_II_FOREST_TREES},
    },
}

# Métrica da Tabela II e as métricas nossas postas ao lado dela. A tabela não
# diz que média usa nem como calcula a AUC com três classes: cada valor do
# artigo é comparado com a nossa média macro e com a ponderada, as duas com o nome.
OBTAINED = {
    "auc": ["roc_auc_ovr_macro"],
    "accuracy": ["accuracy"],
    "f1": ["macro_f1", "weighted_f1"],
    "precision": ["macro_precision", "weighted_precision"],
    "recall": ["macro_recall", "weighted_recall"],
}

# Leitura adotada em cada ponto que a Tabela II deixa em aberto, gravada no
# registro de cada execução.
BASELINE_READINGS = {
    "smote_target": "treino inteiro: as duas classes menores aumentadas até o tamanho de Non-DoH",
    "smote_parameters": "padrão do imbalanced-learn",
    "other_hyperparameters": "padrão do scikit-learn e do XGBoost: o artigo não os informa",
    "class_weight": "nenhum: o artigo não menciona",
    "hyperparameter_source": "Tabela II do artigo, sem busca",
}


def table_ii_comparison(test_metrics: dict, name: str) -> dict:
    """Põe a linha `name` da Tabela II ao lado das métricas do teste.

    Devolve, para cada métrica da tabela, o valor do artigo, os valores obtidos
    e a diferença de cada um para o artigo, em pontos percentuais.
    """
    comparison = {}
    for metric, target in TABLE_II[name].items():
        values = {key: test_metrics[key] for key in OBTAINED[metric]}
        comparison[metric] = {
            "table_ii": target,
            "obtained": values,
            "difference_pp": {key: 100 * (value - target) for key, value in values.items()},
        }
    return comparison


def run_baseline(
    name: str,
    balanced: tuple[np.ndarray, np.ndarray],
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> tuple[dict, np.ndarray, int | None, dict]:
    """Treina o modelo `name` no treino balanceado e o avalia no teste.

    Devolve as métricas do teste, a classe predita para cada linha do teste, a
    profundidade máxima do modelo ajustado e os tempos de treino e de
    avaliação, em segundos.
    """
    start = time.perf_counter()
    model = fit_baseline(name, *balanced, SEED_FIEL)
    fit_seconds = round(time.perf_counter() - start, 1)
    print(f"{BASELINES[name]['label']}: treino em {fit_seconds} s")

    start = time.perf_counter()
    predicted = model.predict(X_test)
    test_metrics = evaluate(y_test, predicted, model.predict_proba(X_test))
    evaluation_seconds = round(time.perf_counter() - start, 1)
    timings = {"fit_seconds": fit_seconds, "evaluation_seconds": evaluation_seconds}
    return test_metrics, predicted, model.max_depth, timings


def evaluate_baselines(table: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Treina e avalia os três modelos de comparação sobre `table`, sem gravar nada.

    `table` tem os atributos do modelo e `label`. Devolve o teste e, para cada
    modelo, um dicionário com as métricas (`metrics`), a configuração
    (`config`), os tempos (`timings`) e a classe predita para cada linha do
    teste (`predicted`).
    """
    # O teste é separado antes de qualquer ajuste e só volta na avaliação final.
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."

    scaler = fit_scaler(train)
    # O normalizador que transforma o teste é o ajustado só com o treino:
    # ajustado com a tabela inteira, ele levaria o mínimo e o máximo do teste
    # para o treino e para a avaliação dos três modelos.
    train_features = feature_matrix(train)
    assert scaler.n_samples_seen_ == len(train), "O scaler viu linhas fora do treino."
    assert np.array_equal(scaler.data_min_, train_features.min()), "Mínimo de outro conjunto."
    assert np.array_equal(scaler.data_max_, train_features.max()), "Máximo de outro conjunto."
    X_train = scaler.transform(train_features)
    X_test = scaler.transform(feature_matrix(test))

    # O SMOTE só enxerga o treino. As amostras sintéticas ficam no treino dos
    # três modelos; o teste é o mesmo do modelo proposto, só com linhas reais.
    start = time.perf_counter()
    balanced = balanced_train(X_train, train["label"].to_numpy(), SEED_FIEL)
    smote_seconds = round(time.perf_counter() - start, 1)
    train_rows, test_rows = class_counts(train), class_counts(test)
    balanced_rows = np.bincount(balanced[1], minlength=len(CLASS_NAMES)).tolist()
    assert balanced_rows == [max(train_rows)] * len(CLASS_NAMES), "Treino não ficou balanceado."
    print(f"SMOTE do treino inteiro: {smote_seconds} s; amostras por classe {balanced_rows}")

    evaluated = {}
    for name, baseline in BASELINES.items():
        test_metrics, predicted, max_depth, timings = run_baseline(
            name, balanced, X_test, test["label"].to_numpy()
        )
        # Cada matriz tem, por classe, exatamente as linhas reais do teste:
        # nenhuma amostra sintética chega à avaliação.
        assert [sum(row) for row in test_metrics["confusion_matrix"]] == test_rows

        metrics = {
            "classes": CLASS_NAMES,
            "train_rows": train_rows,
            "balanced_train_rows": balanced_rows,
            "synthetic_train_rows": np.subtract(balanced_rows, train_rows).tolist(),
            "test_rows": test_rows,
            "test": test_metrics,
        }
        config = {
            "model": name,
            "table_ii_hyperparameters": baseline["table_ii_hyperparameters"],
            # Lida do modelo ajustado. Vazio quer dizer o padrão da biblioteca:
            # sem limite no Random Forest, e o valor padrão do XGBoost.
            "max_depth": max_depth,
            "test_size": TEST_SIZE,
            "n_jobs": N_JOBS,
            "smote_seed": smote_seed(SEED_FIEL, N_SUBSETS),
            "readings": BASELINE_READINGS,
        }
        evaluated[name] = {
            "metrics": metrics,
            "config": config,
            "timings": {"smote_seconds": smote_seconds, **timings},
            "predicted": predicted,
        }
    return test, evaluated


def run_experiment(table: pd.DataFrame, data_sha256: str, results_dir: Path) -> dict:
    """Treina e avalia os três modelos de comparação sobre `table` e grava os resultados.

    `table` tem os atributos do modelo e `label`. Devolve, para cada modelo, o
    diretório da execução e o dicionário gravado em metrics.json.
    """
    _, evaluated = evaluate_baselines(table)
    results = {}
    for name, entry in evaluated.items():
        metrics = {
            **entry["metrics"],
            "table_ii_comparison": table_ii_comparison(entry["metrics"]["test"], name),
        }
        run_dir = save_run(
            experiment="e2",
            track="fiel",
            slice_name=name,
            seed=SEED_FIEL,
            metrics=metrics,
            config=entry["config"],
            data_sha256=data_sha256,
            timings=entry["timings"],
            results_dir=results_dir,
        )
        results[name] = (run_dir, metrics)
    return results


def comparison_table(comparisons: dict) -> str:
    """Escreve a metade superior da Tabela II: artigo, valor obtido e diferença.

    `comparisons` leva o nome de cada modelo à sua comparação com a Tabela II.
    """
    rows = [
        [
            label,
            metric,
            comparison[metric]["table_ii"],
            key,
            f"{value:.6f}",
            f"{comparison[metric]['difference_pp'][key]:+.4f}",
        ]
        for label, comparison in comparisons.items()
        for metric in OBTAINED
        for key, value in comparison[metric]["obtained"].items()
    ]
    columns = ["modelo", "métrica da Tabela II", "artigo", "métrica obtida", "valor", "dif. (pp)"]
    return markdown_table(columns, rows)


def far_above_text(comparisons: dict) -> str:
    """Destaca os modelos de comparação que saem muito acima da sua linha na Tabela II.

    `comparisons` leva o nome de cada modelo de comparação à sua comparação com
    a Tabela II.
    """
    limit = f"{TABLE_II_FAR_ABOVE_PP:g} pontos percentuais"
    lines = []
    for label, comparison in comparisons.items():
        far = [
            f"`{key}` {value:.4f} contra {entry['table_ii']} no artigo "
            f"({entry['difference_pp'][key]:+.2f} pp)"
            for entry in comparison.values()
            for key, value in entry["obtained"].items()
            if entry["difference_pp"][key] > TABLE_II_FAR_ABOVE_PP
        ]
        if far:
            lines.append(f"- **{label}:** " + "; ".join(far) + ".")
    if not lines:
        return f"Nenhum modelo de comparação fica mais de {limit} acima da sua linha na Tabela II."
    return (
        f"Modelos de comparação mais de {limit} acima da sua linha na Tabela II (o limite é "
        "escolha nossa):\n\n" + "\n".join(lines) + "\n\nUma diferença desse tamanho, para "
        "cima, é indício de que o modelo do artigo foi treinado com uma configuração diferente "
        "da que a Tabela II informa. Qual é a diferença não foi medido, e a configuração daqui "
        "não foi ajustada para aproximar o resultado."
    )


def literature_table() -> str:
    """Escreve a metade inferior da Tabela II como o artigo a imprime."""
    rows = [
        [
            f"{row['model']} {row['reference']}",
            *("–" if row[metric] is None else row[metric] for metric in OBTAINED),
            "percentual" if row["percent"] else "fração",
        ]
        for row in TABLE_II_LITERATURE
    ]
    return markdown_table(["modelo", "AUC", "acurácia", "F1", "precisão", "recall", "escala"], rows)


def baseline_text(label: str, test: dict) -> str:
    """Escreve a matriz de confusão de um modelo e a leitura das métricas em termos de detecção."""
    per_class, binary = test["per_class"], test["malicious_vs_rest"]
    malicious, benign = per_class["Malicious-DoH"], per_class["Benign-DoH"]
    confusion = test["confusion_matrix"]
    missed = malicious["support"] - confusion[MALICIOUS][MALICIOUS]
    rows = [[name, *row] for name, row in zip(CLASS_NAMES, confusion, strict=True)]
    return f"""### {label}

{markdown_table(["real \\ predito", *CLASS_NAMES], rows)}

- **Recall de Malicious-DoH {malicious["recall"]:.4%}.** De {malicious["support"]} fluxos de
  túnel no teste, {missed} são classificados em outra classe: passam sem alerta.
- **FPR de Malicious-DoH contra o resto {binary["fpr"]:.4%}.** {binary["false_positives"]} de
  {binary["negatives"]} fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de {binary["fpr_ci_level"]:.0%}:
  de {binary["fpr_ci_low"]:.4%} a {binary["fpr_ci_high"]:.4%}.
- **Recall de Benign-DoH {benign["recall"]:.4%} e precisão {benign["precision"]:.4%}.** É a
  classe menor, com {benign["support"]} fluxos no teste; o erro nela quase não
  aparece na acurácia ({test["accuracy"]:.4%}) nem na média ponderada.
- **F1 macro {test["macro_f1"]:.4%} e F1 ponderado {test["weighted_f1"]:.4%}.** A média
  macro pesa as três classes por igual; a ponderada pesa pelo suporte.
- **AUC-ROC one-vs-rest macro {test["roc_auc_ovr_macro"]:.6f}.** Não depende do limiar
  de decisão."""


def summary_text(results: dict, proposed: dict) -> str:
    """Monta o RESUMO.md com a Tabela II inteira a partir dos números medidos.

    `results` é a saída de `run_experiment`; `proposed` leva o nome de cada
    leitura do modelo proposto à sua comparação com a Tabela II.
    """
    metrics = {name: entry[1] for name, entry in results.items()}
    first = next(iter(metrics.values()))
    comparisons = {
        BASELINES[name]["label"]: entry["table_ii_comparison"] for name, entry in metrics.items()
    }
    details = "\n\n".join(
        baseline_text(BASELINES[name]["label"], entry["test"]) for name, entry in metrics.items()
    )
    return f"""# E2: modelos de comparação da Tabela II do artigo, trilha fiel

Gerado por `scripts/e2_baselines.py`. Os números dos três modelos de comparação
vêm de `<modelo>/seed{SEED_FIEL}/metrics.json` e os tempos de treino de
`<modelo>/seed{SEED_FIEL}/run.json`. Os do modelo proposto são lidos dos resultados
de `scripts/e1_reproducao.py`, sem treinar de novo.
Uma única execução, com a seed {SEED_FIEL}: não há média nem desvio padrão.
Classes na ordem dos códigos: {", ".join(CLASS_NAMES)}.

## Protocolo

Mesmo split e mesmo teste do modelo proposto: {first["test"]["total"]} fluxos, por classe
{first["test_rows"]}. O normalizador é ajustado no treino. O treino inteiro é
balanceado com SMOTE: de {first["train_rows"]} fluxos por classe passa a
{first["balanced_train_rows"]}, com {first["synthetic_train_rows"]} amostras sintéticas. A Tabela II
só diz "SMOTE balanced"; igualar as duas classes menores à maior é leitura nossa.
A tabela informa a profundidade máxima {TABLE_II_TREE_DEPTH} da árvore de decisão e as
{TABLE_II_FOREST_TREES} árvores do Random Forest; todos os outros hiperparâmetros ficam no
padrão do scikit-learn e do XGBoost.

## Tabela II, metade superior: artigo e reprodução

A Tabela II não diz que média usa nem como calcula a AUC com três classes. Cada
valor do artigo aparece ao lado da nossa média macro e da ponderada. A
diferença é o valor obtido menos o do artigo, em pontos percentuais. O modelo
proposto aparece nas duas leituras da profundidade dos Random Forests base;
nele, `roc_auc_ovr_macro` é a AUC da saída do meta-classificador e
`roc_auc_ovr_macro_base_mean` a da média das probabilidades dos bases.

{comparison_table({**comparisons, **proposed})}

{far_above_text(comparisons)}

## Tabela II, metade inferior: resultados da literatura

Valores copiados do artigo como impressos, com a referência que ele cita em
cada linha; "–" é célula que o artigo deixa vazia. A última linha está impressa
em percentual e as outras em fração. O artigo declara que o método experimental
desses trabalhos não é diretamente comparável ao dele (Seção V); eles não foram
reproduzidos aqui.

{literature_table()}

## Cada modelo de comparação no teste

{details}

## O que não foi feito

- Nenhuma busca de hiperparâmetros: o artigo não a descreve para estes modelos.
- Não há validação cruzada dos modelos de comparação: a Tabela II só traz o teste.
- Os trabalhos da metade inferior da tabela não foram reproduzidos.
- Uma execução por modelo: a diferença entre o Random Forest e o modelo
  proposto não tem variância medida aqui.

## Onde os números diferem dos do artigo

O artigo não informa a seed, a lista dos atributos, a limpeza, o alvo e os
parâmetros do SMOTE, os hiperparâmetros além dos dois da Tabela II, a média das
métricas nem o cálculo da AUC; as versões das bibliotecas são outras. Qualquer
um desses pontos pode explicar uma diferença, e nenhum foi isolado aqui.
Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada para aproximar o
resultado.
"""


def main() -> None:
    """Confere o Parquet, roda os três modelos de comparação e grava o resumo."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    counts = json.loads((E0_DIR / "split_counts.json").read_text(encoding="utf-8"))
    # Lido antes de treinar, para a falta do resultado do modelo proposto parar
    # o script no começo.
    proposed = {
        label: json.loads((path / f"seed{SEED_FIEL}" / "metrics.json").read_text(encoding="utf-8"))[
            "table_ii_comparison"
        ]
        for label, path in PROPOSED_RUNS.items()
    }
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )

    results = run_experiment(pd.read_parquet(CIRA_PARQUET_PATH), data_sha256, RESULTS_DIR)
    for name, (run_dir, metrics) in results.items():
        # Mesmo teste do modelo proposto: o total é o registrado pela etapa de dados.
        assert metrics["test"]["total"] == counts["test"]["total"], (
            f"{name}: teste com tamanho diferente do registrado."
        )
        print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}")

    summary = summary_text(results, proposed)
    (RESULTS_DIR / "e2" / "fiel" / "RESUMO.md").write_text(summary, encoding="utf-8")
    comparisons = {
        BASELINES[name]["label"]: metrics["table_ii_comparison"]
        for name, (_, metrics) in results.items()
    }
    print(comparison_table({**comparisons, **proposed}))


if __name__ == "__main__":
    main()
