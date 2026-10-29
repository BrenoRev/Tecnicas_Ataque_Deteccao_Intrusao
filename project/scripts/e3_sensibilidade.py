"""E3: sensibilidade do sistema às leituras que o artigo deixa em aberto.

O artigo não especifica vários pontos do Balanced Stacked Random Forest. A
reprodução adota uma leitura em cada um; este script troca uma leitura de cada
vez por outra que o texto também admite e mede o efeito no mesmo teste.

Cada leitura alternativa parte das duas leituras da profundidade das árvores
que a reprodução já mede: sem limite ("variable tree depth", linha 3 do
Algoritmo 1) e profundidade máxima 5 (Seção IV-B). O recorte gravado leva o
nome da leitura alternativa; quando a partida é a profundidade 5, o nome
termina em `-prof5`. A profundidade em si não é repetida aqui: as duas
configurações de partida são lidas de results/e1/.

Lê data/processed/cira.parquet, separa 10% para teste com a seed 42 e avalia
todas as configurações nesse mesmo teste. Grava metrics.json e run.json em
results/e3/variante/<recorte>/seed42/. Este script só treina, avalia e grava os
arquivos de cada execução: a tabela comparativa (comparacao.csv) e a leitura
dos números (RESUMO.md) são feitas por scripts/e3_resumo.py, a partir desses
arquivos e sem retreinar.

Uso: uv run python scripts/e3_sensibilidade.py
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    FIEL_READINGS,
    FIG4B_CONFUSION,
    MAX_DEPTH,
    MAX_DEPTH_VARIABLE,
    N_JOBS,
    N_SUBSETS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    TEST_SIZE,
    smote_seed,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.evaluate import compare_confusion, evaluate, metrics_from_confusion
from doh_ids.models import base_forests
from doh_ids.runlog import save_run
from doh_ids.splits import fit_scaler, stratified_split
from doh_ids.system import fit_system

# Resultados da etapa de dados, com os quais esta execução é conferida.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"

LABELS = list(range(len(CLASS_NAMES)))

# As duas configurações de partida: o sistema da reprodução em cada leitura da
# profundidade. `e1_run` é a execução da reprodução que mede a partida, sem
# nenhuma leitura trocada.
STARTS = [
    {
        "suffix": "",
        "max_depth": MAX_DEPTH_VARIABLE,
        "label": "profundidade variável",
        "base_depth": 'sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1)',
        "e1_run": Path("e1") / "variante" / "profundidade_variavel" / f"seed{SEED_FIEL}",
    },
    {
        "suffix": "-prof5",
        "max_depth": MAX_DEPTH,
        "label": f"profundidade {MAX_DEPTH}",
        "base_depth": f"profundidade máxima {MAX_DEPTH} nos submodelos (Seção IV-B)",
        "e1_run": Path("e1") / "fiel" / "proposto" / f"seed{SEED_FIEL}",
    },
]

# Nome da leitura que não empilha: um Random Forest só.
SINGLE_FOREST = "rf_unico"
# O que o script publicado pelos autores passa ao Random Forest e o artigo não
# descreve: peso de classe "balanced" e atributos por divisão no padrão da
# biblioteca, que no scikit-learn é a raiz quadrada do número de atributos.
PUBLIC_SCRIPT_CLASS_WEIGHT = "balanced"
LIBRARY_MAX_FEATURES = "sqrt"

# Lista fechada das leituras alternativas. `point` é o ponto que o artigo deixa
# em aberto, `reading` a leitura alternativa, `changes` os argumentos de
# `fit_system` que ela troca e `readings` as entradas do registro de leituras
# que ela substitui. Toda leitura troca um ponto só, menos a do Random Forest
# único, que reproduz de propósito a configuração inteira do script publicado.
VARIANTS = {
    "class_weight": {
        "point": "peso de classe nos Random Forests base",
        "reading": "class_weight='balanced' nos três bases, como no script publicado pelos autores",
        "changes": {"class_weight": PUBLIC_SCRIPT_CLASS_WEIGHT},
        "readings": {"class_weight": "balanced, como no script publicado pelos autores"},
    },
    "use_probas": {
        "point": "entrada do meta-classificador",
        "reading": "probabilidades por classe de cada base (use_probas=True), nove entradas",
        "changes": {"use_probas": True},
        "readings": {"meta_input": "probabilidades de cada base (use_probas=True), nove entradas"},
    },
    "max_features_padrao": {
        "point": "atributos candidatos em cada divisão das árvores",
        "reading": f"padrão da biblioteca (max_features='{LIBRARY_MAX_FEATURES}') em vez de 28",
        "changes": {"max_features": LIBRARY_MAX_FEATURES},
        "readings": {"max_features": f"padrão do scikit-learn ('{LIBRARY_MAX_FEATURES}')"},
    },
    "meta_uniao": {
        "point": "dados de treino do meta-classificador",
        "reading": "predições dos bases na união dos três subconjuntos balanceados",
        "changes": {"meta_on_subsets": True},
        "readings": {
            "meta_training_data": (
                "predições dos bases na união dos três subconjuntos balanceados, com as "
                "amostras sintéticas; Benign-DoH e Malicious-DoH reais entram três vezes"
            )
        },
    },
    SINGLE_FOREST: {
        "point": "sistema inteiro: a configuração do script publicado pelos autores",
        "reading": (
            "um Random Forest só, com class_weight='balanced', max_features no padrão da "
            "biblioteca, sem subconjuntos, sem SMOTE e sem meta-classificador"
        ),
        "changes": {},
        "readings": {
            "base_estimators": "um Random Forest só, treinado no treino original normalizado",
            "meta_training_data": "não há meta-classificador",
            "meta_input": "não há meta-classificador",
            "meta_parameters": "não há meta-classificador",
            "smote_target": "SMOTE não aplicado",
            "smote_parameters": "SMOTE não aplicado",
            "class_weight": "balanced, como no script publicado pelos autores",
            "max_features": f"padrão do scikit-learn ('{LIBRARY_MAX_FEATURES}')",
        },
    },
}


def fit_single_forest(
    train: pd.DataFrame, seed: int, max_depth: int | None
) -> tuple[MinMaxScaler, RandomForestClassifier, list[dict], dict]:
    """Ajusta um Random Forest só no treino original, como o script publicado pelos autores.

    Não há subconjuntos, SMOTE nem meta-classificador. Devolve o mesmo que
    `fit_system`: o normalizador, o modelo, o resumo dos conjuntos de ajuste
    (aqui um só, o treino) e os tempos.
    """
    scaler = fit_scaler(train)
    X_train = scaler.transform(feature_matrix(train))
    y_train = train["label"].to_numpy()
    start = time.perf_counter()
    # O script publicado não normaliza os atributos, e a divisão de uma árvore
    # não depende da escala: o normalizador fica só para o modelo receber a
    # mesma matriz das outras configurações.
    forest = base_forests(
        [(X_train, y_train)], seed, max_depth, PUBLIC_SCRIPT_CLASS_WEIGHT, LIBRARY_MAX_FEATURES
    )[0]
    timings = {"base_fit_seconds": round(time.perf_counter() - start, 1)}
    summary = [{"class_counts": np.bincount(y_train, minlength=len(CLASS_NAMES)).tolist()}]
    return scaler, forest, summary, timings


def fit_variant(
    train: pd.DataFrame, seed: int, max_depth: int | None, name: str
) -> tuple[MinMaxScaler, StackingClassifier | RandomForestClassifier, list[dict], dict]:
    """Ajusta, só com `train`, o sistema com a leitura alternativa `name` de `VARIANTS`.

    `max_depth` é a profundidade da configuração de partida. Devolve o
    normalizador, o modelo, o resumo dos conjuntos em que os Random Forests
    foram ajustados e os tempos, em segundos.
    """
    if name == SINGLE_FOREST:
        return fit_single_forest(train, seed, max_depth)
    return fit_system(train, seed, max_depth, **VARIANTS[name]["changes"])


def variant_metrics(
    scaler: MinMaxScaler,
    model: StackingClassifier | RandomForestClassifier,
    summary: list[dict],
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> dict:
    """Avalia o modelo ajustado no teste e monta o dicionário gravado em metrics.json."""
    X_test = scaler.transform(feature_matrix(test))
    y_test = test["label"].to_numpy()
    test_metrics = evaluate(y_test, model.predict(X_test), model.predict_proba(X_test))

    # Amostra sintética só existe nos conjuntos de ajuste: a matriz tem, por
    # classe, exatamente as linhas reais do teste.
    assert [sum(row) for row in test_metrics["confusion_matrix"]] == class_counts(test)

    metrics = {
        "classes": CLASS_NAMES,
        "train_rows": class_counts(train),
        "test_rows": class_counts(test),
        "fit_sets": summary,
        "test": test_metrics,
        "fig4b_comparison": {
            "fig4b": FIG4B_CONFUSION,
            **compare_confusion(test_metrics["confusion_matrix"], FIG4B_CONFUSION),
        },
    }
    if isinstance(model, StackingClassifier):
        # Cada base avaliado sozinho: a diferença entre eles e o modelo
        # empilhado é o que o meta-classificador faz com as predições.
        metrics["base_models_test"] = [
            metrics_from_confusion(confusion_matrix(y_test, forest.predict(X_test), labels=LABELS))
            for forest in model.clfs_
        ]
    return metrics


def run_config(model: StackingClassifier | RandomForestClassifier, name: str, start: dict) -> dict:
    """Monta a configuração gravada em run.json: partida, ponto trocado e hiperparâmetros."""
    stacked = isinstance(model, StackingClassifier)
    # Os hiperparâmetros são lidos do modelo ajustado, para o registro dizer o
    # que foi treinado e não o que foi pedido.
    forest = model.clfs_[0] if stacked else model
    variant = VARIANTS[name]
    return {
        "variant": name,
        "changed_point": variant["point"],
        "alternative_reading": variant["reading"],
        "start": start["label"],
        "start_run": start["e1_run"].as_posix(),
        "changed_arguments": variant["changes"],
        "n_estimators": forest.n_estimators,
        "max_depth": forest.max_depth,
        "max_features": forest.max_features,
        "class_weight": forest.class_weight,
        "criterion": forest.criterion,
        "n_base_models": len(model.clfs_) if stacked else 1,
        "use_probas": model.use_probas if stacked else None,
        "meta_on_subsets": variant["changes"].get("meta_on_subsets", False) if stacked else None,
        "test_size": TEST_SIZE,
        "n_jobs": N_JOBS,
        "smote_seeds": [smote_seed(SEED_FIEL, i) for i in range(N_SUBSETS)] if stacked else [],
        "readings": {**FIEL_READINGS, "base_depth": start["base_depth"], **variant["readings"]},
    }


def run_experiment(table: pd.DataFrame, data_sha256: str, results_dir: Path) -> dict:
    """Treina e avalia cada leitura alternativa, a partir de cada configuração de partida.

    `table` tem os atributos do modelo e `label`. Devolve, para cada recorte
    gravado em `results_dir`, o diretório da execução e o dicionário de
    metrics.json.
    """
    # O teste é separado uma vez, antes de qualquer ajuste, e é o mesmo para
    # todas as configurações.
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."

    results = {}
    for start in STARTS:
        for name in VARIANTS:
            begin = time.perf_counter()
            scaler, model, summary, timings = fit_variant(
                train, SEED_FIEL, start["max_depth"], name
            )
            metrics = variant_metrics(scaler, model, summary, train, test)
            timings["total_seconds"] = round(time.perf_counter() - begin, 1)
            slice_name = name + start["suffix"]
            run_dir = save_run(
                experiment="e3",
                track="variante",
                slice_name=slice_name,
                seed=SEED_FIEL,
                metrics=metrics,
                config=run_config(model, name, start),
                data_sha256=data_sha256,
                timings=timings,
                results_dir=results_dir,
            )
            results[slice_name] = (run_dir, metrics)
            print(f"{slice_name}: {timings}", flush=True)
    return results


def main() -> None:
    """Confere o Parquet, roda as leituras alternativas e grava cada execução."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    counts = json.loads((E0_DIR / "split_counts.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )

    results = run_experiment(pd.read_parquet(CIRA_PARQUET_PATH), data_sha256, RESULTS_DIR)
    # Mesmo teste em todas as configurações: o total é o registrado pela etapa de dados.
    for name, (_, metrics) in results.items():
        assert metrics["test"]["total"] == counts["test"]["total"], (
            f"{name}: teste com tamanho diferente."
        )

    variant_dir = RESULTS_DIR / "e3" / "variante"
    print(f"Resultados em {variant_dir.relative_to(PROJECT_ROOT)}")
    print("Tabela comparativa e resumo: uv run python -m scripts.e3_resumo")


if __name__ == "__main__":
    main()
