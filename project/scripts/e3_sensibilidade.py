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
results/e3/variante/<recorte>/seed42/, a tabela comparativa em
results/e3/variante/comparacao.csv e a leitura dos números em
results/e3/variante/RESUMO.md.

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
    N_ESTIMATORS,
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
from doh_ids.summary import markdown_table
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

# Colunas da tabela comparativa que são fração entre 0 e 1.
FRACTION_COLUMNS = [
    "accuracy",
    "non_doh_recall",
    "benign_precision",
    "benign_recall",
    "benign_f1",
    "malicious_precision",
    "malicious_recall",
    "malicious_fpr",
    "macro_f1",
]


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
        "n_estimators": N_ESTIMATORS,
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


def comparison_row(configuration: str, start: str, point: str, test: dict) -> dict:
    """Monta a linha de uma configuração na tabela comparativa, a partir das métricas do teste."""
    per_class = test["per_class"]
    benign, malicious = per_class["Benign-DoH"], per_class["Malicious-DoH"]
    confusion = test["confusion_matrix"]
    return {
        "configuration": configuration,
        "start": start,
        "changed_point": point,
        "accuracy": test["accuracy"],
        "non_doh_recall": per_class["Non-DoH"]["recall"],
        "benign_precision": benign["precision"],
        "benign_recall": benign["recall"],
        "benign_f1": benign["f1"],
        "malicious_precision": malicious["precision"],
        "malicious_recall": malicious["recall"],
        "malicious_fpr": test["malicious_vs_rest"]["fpr"],
        "macro_f1": test["macro_f1"],
        "fig4b_absolute_difference_sum": compare_confusion(confusion, FIG4B_CONFUSION)[
            "absolute_difference_sum"
        ],
    }


def comparison_frame(results: dict, start_tests: dict) -> pd.DataFrame:
    """Monta a tabela comparativa: o artigo, as duas partidas e cada leitura alternativa.

    `results` é o que `run_experiment` devolve; `start_tests` leva o rótulo de
    cada configuração de partida às métricas dela no teste.
    """
    rows = [comparison_row("Artigo, Fig. 4b", "", "", metrics_from_confusion(FIG4B_CONFUSION))]
    for start in STARTS:
        rows.append(
            comparison_row(
                f"partida ({start['label']})",
                start["label"],
                "nenhum: reprodução",
                start_tests[start["label"]],
            )
        )
        for name, variant in VARIANTS.items():
            slice_name = name + start["suffix"]
            rows.append(
                comparison_row(
                    slice_name, start["label"], variant["point"], results[slice_name][1]["test"]
                )
            )
    return pd.DataFrame(rows)


def comparison_table(frame: pd.DataFrame) -> str:
    """Escreve a tabela comparativa em Markdown, com as frações em percentual."""
    columns = [
        "configuração",
        "partida",
        "acurácia",
        "recall Non-DoH",
        "**recall Benign-DoH**",
        "**precisão Benign-DoH**",
        "**F1 Benign-DoH**",
        "recall Malicious-DoH",
        "precisão Malicious-DoH",
        "FPR Malicious-DoH",
        "F1 macro",
        "soma das diferenças absolutas para a Fig. 4b",
    ]
    rows = [
        [
            row.configuration,
            row.start,
            f"{row.accuracy:.2%}",
            f"{row.non_doh_recall:.2%}",
            f"**{row.benign_recall:.2%}**",
            f"**{row.benign_precision:.2%}**",
            f"**{row.benign_f1:.2%}**",
            f"{row.malicious_recall:.2%}",
            f"{row.malicious_precision:.2%}",
            f"{row.malicious_fpr:.4%}",
            f"{row.macro_f1:.2%}",
            row.fig4b_absolute_difference_sum,
        ]
        for row in frame.itertuples(index=False)
    ]
    return markdown_table(columns, rows)


def readings_table() -> str:
    """Escreve a lista das leituras alternativas: o ponto, a leitura e os recortes gravados."""
    rows = [
        [
            variant["point"],
            variant["reading"],
            ", ".join(f"`{name}{start['suffix']}`" for start in STARTS),
        ]
        for name, variant in VARIANTS.items()
    ]
    return markdown_table(["ponto em aberto no artigo", "leitura alternativa", "recortes"], rows)


def effect_lines(frame: pd.DataFrame) -> str:
    """Escreve, para cada recorte, quanto ele se afasta da própria configuração de partida."""
    rows = frame.set_index("configuration")
    lines = []
    for start in STARTS:
        origin = rows.loc[f"partida ({start['label']})"]
        for name in VARIANTS:
            row = rows.loc[name + start["suffix"]]
            difference = {
                column: 100 * (row[column] - origin[column]) for column in FRACTION_COLUMNS
            }
            distance = int(row["fig4b_absolute_difference_sum"])
            origin_distance = int(origin["fig4b_absolute_difference_sum"])
            lines.append(
                f"- **`{row.name}`**, sobre a partida de {start['label']}: recall de Benign-DoH "
                f"de {origin['benign_recall']:.2%} para {row['benign_recall']:.2%} "
                f"({difference['benign_recall']:+.2f} pp); precisão de Benign-DoH de "
                f"{origin['benign_precision']:.2%} para {row['benign_precision']:.2%} "
                f"({difference['benign_precision']:+.2f} pp); recall de Malicious-DoH "
                f"{difference['malicious_recall']:+.2f} pp; FPR de Malicious-DoH "
                f"{difference['malicious_fpr']:+.4f} pp; acurácia "
                f"{difference['accuracy']:+.2f} pp; F1 macro {difference['macro_f1']:+.2f} pp; "
                f"soma das diferenças absolutas de {origin_distance} para {distance}."
            )
    return "\n".join(lines)


def bases_lines(results: dict) -> str:
    """Escreve o recall de Benign-DoH dos bases isolados ao lado do modelo empilhado."""
    lines = []
    for slice_name, (_, metrics) in results.items():
        if "base_models_test" not in metrics:
            continue
        recalls = ", ".join(
            f"{base['per_class']['Benign-DoH']['recall']:.2%}"
            for base in metrics["base_models_test"]
        )
        stacked = metrics["test"]["per_class"]["Benign-DoH"]["recall"]
        lines.append(f"- **`{slice_name}`:** bases {recalls}; modelo empilhado {stacked:.2%}.")
    return "\n".join(lines)


def distance_reading_text(frame: pd.DataFrame, results: dict) -> str:
    """Põe a menor soma para a Fig. 4b ao lado de Benign-DoH e lista quem nunca prediz a classe."""
    benign = CLASS_NAMES.index("Benign-DoH")
    never = [
        f"`{slice_name}`"
        for slice_name, (_, metrics) in results.items()
        if not any(row[benign] for row in metrics["test"]["confusion_matrix"])
    ]
    measured = frame[frame["changed_point"].isin([v["point"] for v in VARIANTS.values()])]
    closest = measured.loc[measured["fig4b_absolute_difference_sum"].idxmin()]
    text = (
        f"Entre os {len(measured)} recortes medidos aqui, o de menor soma das diferenças "
        f"absolutas é `{closest['configuration']}` "
        f"({closest['fig4b_absolute_difference_sum']}), com recall de Benign-DoH de "
        f"{closest['benign_recall']:.2%} e precisão de Benign-DoH de "
        f"{closest['benign_precision']:.2%}. "
    )
    if never:
        text += (
            f"Não predizem Benign-DoH em nenhuma linha do teste: {', '.join(never)}. Nesses "
            "recortes a precisão da classe é indefinida e entra como 0 no F1 macro."
        )
    else:
        text += "Todos os recortes predizem Benign-DoH em alguma linha do teste."
    return text


def summary_text(results: dict, start_tests: dict) -> str:
    """Monta o texto do RESUMO.md a partir dos números medidos na execução."""
    frame = comparison_frame(results, start_tests)
    test = next(iter(results.values()))[1]["test"]
    benign_support = test["per_class"]["Benign-DoH"]["support"]
    starts = "\n".join(
        f"- **{start['label']}:** {start['base_depth']}. Medida em "
        f"`results/{start['e1_run'].as_posix()}/`; recortes desta partida "
        + (f"com o sufixo `{start['suffix']}`." if start["suffix"] else "sem sufixo.")
        for start in STARTS
    )
    return f"""# E3: sensibilidade às leituras que o artigo deixa em aberto

Gerado por `scripts/e3_sensibilidade.py`. Os números de cada recorte vêm de
`<recorte>/seed{SEED_FIEL}/metrics.json`; a configuração e os tempos, de
`<recorte>/seed{SEED_FIEL}/run.json`; a tabela abaixo, sem arredondamento, está em
`comparacao.csv`. Uma única execução de cada recorte, com a seed {SEED_FIEL}: não há
média nem desvio padrão, e diferença pequena entre recortes não distingue
leitura de variação entre seeds. Todos os recortes são avaliados no mesmo
teste, de {test["total"]} fluxos. Não há validação cruzada aqui.

## O que foi variado

O artigo não especifica os pontos abaixo. A reprodução adota uma leitura em
cada um; cada recorte troca uma leitura só e mantém todo o resto da
configuração de partida. A exceção é `{SINGLE_FOREST}`, que troca vários pontos de
uma vez, de propósito: é a configuração do script publicado pelos autores, que
não empilha.

{readings_table()}

Configurações de partida, as duas leituras da profundidade das árvores:

{starts}

O script publicado pelos autores usa profundidade máxima {MAX_DEPTH}: dos dois recortes de
`{SINGLE_FOREST}`, o que corresponde a ele é `{SINGLE_FOREST}-prof5`.

## Teste ao lado da Fig. 4b

As colunas de Benign-DoH estão em negrito: é a classe menor, e é nela que as
leituras mais diferem. FPR de Malicious-DoH é o de Malicious-DoH contra o resto.

{comparison_table(frame)}

## O que cada ponto muda, e quanto

Diferença de cada recorte para a sua configuração de partida, em pontos
percentuais (pp).

{effect_lines(frame)}

## Bases isolados e modelo empilhado

Recall de Benign-DoH de cada Random Forest base avaliado sozinho no teste, ao
lado do recall do modelo empilhado. Quando os bases acertam a classe e o modelo
empilhado não, a perda acontece no meta-classificador.

{bases_lines(results)}

## Como ler a comparação

A soma das diferenças absolutas conta linhas, e Benign-DoH tem {benign_support} das
{test["total"]} linhas do teste ({benign_support / test["total"]:.2%}). Um modelo que nunca prediz
essa classe erra no máximo essas linhas, e a soma quase não registra a perda de
uma classe inteira. Por isso a soma vai ao lado das métricas por classe, e
nenhuma leitura é declarada a mais próxima do artigo por um número só.

{distance_reading_text(frame, results)}

## Medido e hipótese

Medido: as matrizes de confusão de cada recorte no teste, as métricas derivadas
delas e a distância de cada uma à Fig. 4b. Tudo o que está nas seções acima.

Hipótese, não demonstrada por estes números:

- Que a Fig. 4b tenha sido gerada com alguma das leituras medidas. Uma soma
  pequena é compatível com a leitura e não a identifica: leituras diferentes
  podem dar matrizes parecidas, o artigo não informa a seed, e há uma execução
  só de cada recorte.
- Que os números publicados tenham vindo do script publicado, com um Random
  Forest só, e não do sistema descrito no texto. O que se mediu é o resultado de
  `{SINGLE_FOREST}-prof5` nos nossos dados. O arquivo que aquele script lê não foi
  publicado, e não se sabe com que limpeza e com que atributos ele foi gerado:
  a distância medida aqui não confirma nem descarta a hipótese.

A reprodução do artigo continua sendo a de `results/e1/`, nas duas leituras da
profundidade. Os recortes desta pasta informam a discussão das ambiguidades e
não substituem a reprodução. Nenhuma seed, hiperparâmetro ou regra de limpeza
foi ajustada para aproximar o resultado.

## O que não foi medido

- **Meta-classificador com predições fora da amostra** (`StackingCVClassifier`
  do mlxtend). Não feita: essa classe ajusta todos os bases no mesmo conjunto e
  não reproduz um subconjunto por base. Efeito: não se sabe quanto do
  resultado depende de o meta-classificador ver predições de bases sobre linhas
  que eles já viram no treino.
- **One-sided selection antes do SMOTE.** Não feita: o artigo cita a técnica uma
  vez (Seção III-B) e não a descreve. Efeito: os subconjuntos de todos os
  recortes têm todo o Non-DoH da sua parte, sem seleção.
- **Um modelo com 28 atributos no total**, a outra leitura de "selected at
  random from 28 features" (Seção IV-A). Não feita: o artigo não diz qual
  atributo sairia, e escolher um seria arbitrário.
- **Duas leituras trocadas ao mesmo tempo** no sistema empilhado, por exemplo
  probabilidades na entrada do meta-classificador ajustado na união dos
  subconjuntos. Cada recorte troca um ponto; o efeito conjunto não é a soma dos
  efeitos separados.
- **Validação cruzada e outras seeds.** Cada recorte tem uma execução, só no teste.
- **A profundidade das árvores** não é repetida: as duas leituras estão em
  `results/e1/` e entram na tabela como as configurações de partida.
"""


def main() -> None:
    """Confere o Parquet, roda as leituras alternativas e grava a tabela e o resumo."""
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    counts = json.loads((E0_DIR / "split_counts.json").read_text(encoding="utf-8"))
    # Lido antes de treinar, para a falta do resultado de uma partida parar o
    # script no começo.
    start_tests = {
        start["label"]: json.loads(
            (RESULTS_DIR / start["e1_run"] / "metrics.json").read_text(encoding="utf-8")
        )["test"]
        for start in STARTS
    }
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )

    results = run_experiment(pd.read_parquet(CIRA_PARQUET_PATH), data_sha256, RESULTS_DIR)
    # Mesmo teste em todas as configurações, inclusive nas duas de partida: o
    # total é o registrado pela etapa de dados.
    totals = {name: metrics["test"]["total"] for name, (_, metrics) in results.items()}
    totals.update({label: test["total"] for label, test in start_tests.items()})
    for name, total in totals.items():
        assert total == counts["test"]["total"], f"{name}: teste com tamanho diferente."

    variant_dir = RESULTS_DIR / "e3" / "variante"
    comparison_frame(results, start_tests).to_csv(variant_dir / "comparacao.csv", index=False)
    (variant_dir / "RESUMO.md").write_text(summary_text(results, start_tests), encoding="utf-8")
    print(comparison_table(comparison_frame(results, start_tests)))
    print(f"Resultados em {variant_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
