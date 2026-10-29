"""E5: explicabilidade com SHAP sobre os Random Forests base, ao lado das Figs. 5 a 8 do artigo.

Lê data/processed/cira.parquet, separa 10% para teste com a seed 42 e ajusta o
sistema do artigo. Calcula os valores SHAP dos três Random Forests base em uma
amostra estratificada do treino (importância global, Fig. 5) e os do primeiro
base em uma amostra do teste (dependência e explicações locais, Figs. 6 a 8).

O sistema é explicado nas duas leituras de profundidade das árvores: sem
limite ("variable tree depth", linha 3 do Algoritmo 1), que é a explicação
principal, e profundidade máxima 5 (Seção IV-B), ao lado.

Grava em results/e5/variante/profundidade_variavel/seed42/ e em
results/e5/fiel/proposto/seed42/: metrics.json, run.json, a tabela de
importância, as figuras e os dados de cada figura em CSV. A leitura dos números
vai para o RESUMO.md da pasta de cada trilha e as duas lado a lado para
results/e5/RESUMO.md.

Uso: uv run python scripts/e5_xai.py
"""

import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from mlxtend.classifier import StackingClassifier
from scipy.stats import spearmanr

from doh_ids.config import (
    ADDITIVITY_TOLERANCE,
    ARTICLE_DURATION_THRESHOLD_SECONDS,
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    EXPLAINED_BASE,
    FEATURE_COLUMNS,
    FIG5_RANKING,
    FIG7_MALICIOUS,
    FIG8_NON_DOH,
    LOCAL_TABLE_FEATURES,
    MAX_DEPTH,
    MAX_DEPTH_VARIABLE,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    SHAP_SAMPLE_PER_CLASS,
    SHAP_TOP_FEATURES,
    SKEW_COLUMNS,
    SKEW_SENTINEL,
)
from doh_ids.data import class_counts, feature_matrix, sha256_of
from doh_ids.explain import (
    forest_shap_values,
    global_importance,
    original_units,
    rank_agreement,
    stratified_sample,
)
from doh_ids.runlog import save_run
from doh_ids.splits import stratified_split
from doh_ids.summary import markdown_table, one_feature_rule_text
from doh_ids.system import fit_system

# Resultados da etapa de dados e da reprodução, com os quais esta execução é conferida.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"
E1_DIR = RESULTS_DIR / "e1"
# Medidas da etapa de dados do segundo dataset, citadas na ressalva de um atributo.
HKD_DATA_PATH = RESULTS_DIR / "e6" / "dados" / "hkd" / f"seed{SEED_FIEL}" / "metrics.json"

NON_DOH = CLASS_NAMES.index("Non-DoH")
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")
EXPLAINED_BASE_NUMBER = EXPLAINED_BASE + 1

# As duas leituras da profundidade dos Random Forests base. A de profundidade
# variável vem primeiro porque é a explicação principal.
READINGS = [
    {
        "track": "variante",
        "slice_name": "profundidade_variavel",
        "max_depth": MAX_DEPTH_VARIABLE,
        "label": "variante (profundidade variável)",
        "base_depth": 'sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1)',
    },
    {
        "track": "fiel",
        "slice_name": "proposto",
        "max_depth": MAX_DEPTH,
        "label": f"fiel (profundidade {MAX_DEPTH})",
        "base_depth": f"profundidade máxima {MAX_DEPTH} nos submodelos (Seção IV-B)",
    },
]

# Explicações locais: a figura do artigo, o arquivo gravado e os números lidos da figura.
LOCAL_FIGURES = [
    ("Fig. 7", "fig7_explicacao_malicious-doh", FIG7_MALICIOUS),
    ("Fig. 8", "fig8_explicacao_non-doh", FIG8_NON_DOH),
]


def base_importance(forests: list, X: np.ndarray) -> tuple[pd.DataFrame, list[list[float]]]:
    """Calcula a importância global de cada Random Forest base nas linhas de `X`.

    Devolve a tabela com uma linha por base, classe e atributo, e o valor base
    de cada classe em cada base.
    """
    tables, base_values = [], []
    for number, forest in enumerate(forests, start=1):
        values, base = forest_shap_values(forest, X)
        table = global_importance(values)
        table.insert(0, "base", number)
        tables.append(table)
        base_values.append(base.tolist())
    return pd.concat(tables, ignore_index=True), base_values


def importance_series(importance: pd.DataFrame, base: int, class_name: str) -> pd.Series:
    """Devolve a importância de cada atributo para um base e uma classe, já ordenada."""
    rows = importance[(importance["base"] == base) & (importance["class_name"] == class_name)]
    return rows.set_index("feature")["mean_abs_shap"]


def ranking_stability(importance: pd.DataFrame) -> dict:
    """Mede, por classe, a concordância do ranking entre cada par de bases."""
    bases = sorted(importance["base"].unique().tolist())
    return {
        class_name: {
            f"{first}-{second}": rank_agreement(
                importance_series(importance, first, class_name),
                importance_series(importance, second, class_name),
                SHAP_TOP_FEATURES,
            )
            for first, second in itertools.combinations(bases, 2)
        }
        for class_name in CLASS_NAMES
    }


def article_comparison(importance: pd.DataFrame) -> list[dict]:
    """Compara o ranking de Malicious-DoH de cada base com o da Fig. 5 do artigo."""
    # A Fig. 5 não diz a classe do "predicted label". A legenda fala do tráfego
    # malicioso, e a comparação é feita com o ranking da classe Malicious-DoH.
    article_rank = pd.Series(range(1, len(FIG5_RANKING) + 1), index=FIG5_RANKING)
    article_top = FIG5_RANKING[:SHAP_TOP_FEATURES]
    comparison = []
    for base in sorted(importance["base"].unique().tolist()):
        ranking = importance_series(importance, base, CLASS_NAMES[MALICIOUS]).index.tolist()
        obtained_rank = pd.Series(range(1, len(ranking) + 1), index=ranking)
        correlation = spearmanr(article_rank[FEATURE_COLUMNS], obtained_rank[FEATURE_COLUMNS])
        comparison.append(
            {
                "base": base,
                "spearman_all_features": float(correlation.statistic),
                "top_obtained": ranking[:SHAP_TOP_FEATURES],
                "top_shared_with_article": len(set(ranking[:SHAP_TOP_FEATURES]) & set(article_top)),
                "obtained_rank_of_article_top": {
                    feature: int(obtained_rank[feature]) for feature in article_top
                },
            }
        )
    return comparison


def positive_share(positive: np.ndarray) -> float | None:
    """Devolve a fração de valores positivos, ou None quando não há fluxo."""
    return float(positive.mean()) if len(positive) else None


def duration_by_class(
    positive: np.ndarray, above: np.ndarray, between: np.ndarray, labels: np.ndarray
) -> dict:
    """Separa por classe real as contagens da análise do limiar de `Duration`.

    `positive` marca os fluxos com valor SHAP positivo, `above` os de duração
    acima do limiar do artigo e `between` os que ficam entre o limiar do artigo
    e o corte medido.
    """
    by_class = {}
    for code, name in enumerate(CLASS_NAMES):
        of_class = labels == code
        by_class[name] = {
            "rows_up_to_article_threshold": int((of_class & ~above).sum()),
            "positive_fraction_up_to_article_threshold": positive_share(
                positive[of_class & ~above]
            ),
            "rows_above_article_threshold": int((of_class & above).sum()),
            "positive_fraction_above_article_threshold": positive_share(positive[of_class & above]),
            "rows_between_cuts": int((of_class & between).sum()),
            "fraction_between_cuts": float(between[of_class].mean()),
        }
    return by_class


def duration_threshold(duration: np.ndarray, shap_duration: np.ndarray, labels: np.ndarray) -> dict:
    """Mede onde o valor SHAP de `Duration` para Malicious-DoH troca de sinal.

    `duration` está em segundos e `labels` é a classe real de cada fluxo.
    Devolve a fração de valores positivos acima e abaixo do limiar do artigo,
    no total e por classe, o corte que melhor separa os dois sinais e os
    fluxos que ficam entre esse corte e o limiar do artigo.
    """
    positive = shap_duration > 0
    above = duration > ARTICLE_DURATION_THRESHOLD_SECONDS
    # Corte que melhor separa: os fluxos são ordenados pela duração e, para
    # cada ponto de corte, contam-se os negativos até ele e os positivos depois
    # dele. O corte com a maior contagem é o corte medido.
    order = np.argsort(duration, kind="stable")
    agreeing = np.cumsum(~positive[order]) + positive.sum() - np.cumsum(positive[order])
    best = int(np.argmax(agreeing))
    best_seconds = float(duration[order][best])

    # Fluxos que o corte medido e o limiar do artigo põem em lados diferentes.
    # O corte medido é, por construção, o que mais concorda com o sinal: ele
    # não serve de critério para confirmar ou negar o limiar do artigo, e os
    # dois cortes são só reportados lado a lado.
    low, high = sorted([best_seconds, float(ARTICLE_DURATION_THRESHOLD_SECONDS)])
    between = (duration > low) & (duration <= high)
    return {
        "article_threshold_seconds": ARTICLE_DURATION_THRESHOLD_SECONDS,
        "rows_above_article_threshold": int(above.sum()),
        "positive_fraction_above_article_threshold": float(positive[above].mean()),
        "rows_up_to_article_threshold": int((~above).sum()),
        "positive_fraction_up_to_article_threshold": float(positive[~above].mean()),
        "article_threshold_agreement": float((positive == above).mean()),
        "best_threshold_seconds": best_seconds,
        "best_threshold_agreement": float(agreeing[best] / len(duration)),
        "rows_between_cuts": int(between.sum()),
        "positive_fraction_between_cuts": positive_share(positive[between]),
        "by_class": duration_by_class(positive, above, between, labels),
        "shortest_positive_seconds": float(duration[positive].min()),
        "longest_non_positive_seconds": float(duration[~positive].max()),
    }


def received_over_sent(dependence: pd.DataFrame) -> dict:
    """Conta os fluxos com mais bytes recebidos que enviados e o sinal do valor SHAP neles."""
    more_received = dependence["FlowBytesReceived"] > dependence["FlowBytesSent"]
    positive = dependence["shap_FlowBytesSent"] > 0
    labels = dependence.loc[more_received, "label"].to_numpy()
    return {
        "rows_by_class": np.bincount(labels, minlength=len(CLASS_NAMES)).tolist(),
        "positive_fraction": float(positive[more_received].mean()),
        "rows_others_by_class": np.bincount(
            dependence.loc[~more_received, "label"].to_numpy(), minlength=len(CLASS_NAMES)
        ).tolist(),
        "positive_fraction_others": float(positive[~more_received].mean()),
    }


def local_explanation(
    position: int,
    flows: pd.DataFrame,
    values: np.ndarray,
    base_values: np.ndarray,
    base_proba: np.ndarray,
    stacked_labels: np.ndarray,
) -> dict:
    """Monta a explicação do fluxo de posição `position` na amostra do teste.

    A classe explicada é a classe real do fluxo. As contribuições estão em
    pontos percentuais de probabilidade, como na tabela das Figs. 7 e 8 do
    artigo: média da população, os atributos de maior efeito, a soma dos demais
    e a predição final.
    """
    class_index = int(flows["label"].iloc[position])
    effects = pd.Series(100 * values[position, :, class_index], index=FEATURE_COLUMNS)
    top = effects.abs().sort_values(ascending=False, kind="stable").index[:LOCAL_TABLE_FEATURES]
    population = 100 * float(base_values[class_index])
    rows = [{"item": "Média da população", "value": None, "effect_pp": population}]
    rows += [
        {"item": feature, "value": float(flows[feature].iloc[position]), "effect_pp": effect}
        for feature, effect in effects[top].items()
    ]
    others = float(effects.drop(top).sum())
    rows.append({"item": "Outros atributos somados", "value": None, "effect_pp": others})
    final = population + float(effects.sum())
    rows.append({"item": "Predição final", "value": None, "effect_pp": final})
    return {
        "explained_class": CLASS_NAMES[class_index],
        "base_probabilities_percent": (100 * base_proba[position]).tolist(),
        "base_predicted_class": CLASS_NAMES[int(np.argmax(base_proba[position]))],
        "stacked_predicted_class": CLASS_NAMES[int(stacked_labels[position])],
        "contributions": rows,
    }


def stacked_explainer_error(stacked: StackingClassifier) -> str | None:
    """Devolve a mensagem com que o TreeExplainer recusa o modelo empilhado, ou None."""
    # O erro que a biblioteca levanta para modelo que não é de árvores é uma
    # subclasse de ValueError.
    try:
        shap.TreeExplainer(stacked)
    except ValueError as error:
        return str(error)
    return None


def draw_fig5(importance: pd.Series, class_name: str) -> Figure:
    """Desenha as barras de importância global de uma classe, como a Fig. 5 do artigo."""
    # A figura é criada sem a interface pyplot, que abriria uma janela: assim o
    # script roda em máquina sem tela.
    figure = Figure(figsize=(9, 8), layout="constrained")
    axis = figure.subplots()
    labels = [f"{rank}. {feature}" for rank, feature in enumerate(importance.index, start=1)]
    axis.barh(labels, importance.to_numpy(), color="dimgray")
    axis.invert_yaxis()
    axis.set_xlabel(
        f"Média do valor absoluto de SHAP (probabilidade de {class_name})\n"
        f"Random Forest base {EXPLAINED_BASE_NUMBER}, amostra do treino"
    )
    axis.set_ylabel("Atributo, do mais para o menos importante")
    return figure


def draw_dependence(dependence: pd.DataFrame, column: str, unit: str, style: dict) -> Figure:
    """Desenha o valor SHAP de `column` contra o valor do atributo, um ponto por fluxo.

    `style` diz a coluna que colore os pontos (`color`), a unidade dela
    (`color_unit`) e se a escala é logarítmica (`log`), no eixo horizontal e
    nas cores. Com `threshold`, traça a linha vertical do limiar do artigo.
    """
    figure = Figure(figsize=(8, 5), layout="constrained")
    axis = figure.subplots()
    norm = LogNorm() if style["log"] else None
    points = axis.scatter(
        dependence[column],
        dependence[f"shap_{column}"],
        c=dependence[style["color"]],
        cmap="coolwarm",
        norm=norm,
        s=6,
        rasterized=True,
    )
    scale = ", escala logarítmica" if style["log"] else ""
    if style["log"]:
        axis.set_xscale("log")
    axis.axhline(0, color="black", linewidth=0.8)
    if style.get("threshold"):
        axis.axvline(style["threshold"], color="black", linestyle="--", linewidth=0.8)
        axis.annotate(
            f"{style['threshold']} s (limiar do artigo)",
            (style["threshold"], axis.get_ylim()[0]),
            textcoords="offset points",
            xytext=(4, 4),
        )
    axis.set_xlabel(f"{column} ({unit}{scale})")
    axis.set_ylabel(
        f"Valor SHAP de {column}\n(efeito na probabilidade de {CLASS_NAMES[MALICIOUS]})"
    )
    figure.colorbar(points, ax=axis, label=f"{style['color']} ({style['color_unit']}{scale})")
    return figure


def draw_local(explanation: dict, title: str) -> Figure:
    """Desenha a explicação de um fluxo: probabilidades, cascata e tabela de contribuição.

    São os três elementos das Figs. 7 e 8 do artigo, que são telas do painel.
    """
    figure = Figure(figsize=(16, 8), layout="constrained")
    grid = figure.add_gridspec(2, 2, height_ratios=[1, 2.4])
    figure.suptitle(title)

    # No lugar do gráfico de pizza do painel, barras: a leitura do valor é direta.
    proba_axis = figure.add_subplot(grid[0, 0])
    marked = [
        f"{name}*" if name == explanation["explained_class"] else name for name in CLASS_NAMES
    ]
    bars = proba_axis.barh(marked, explanation["base_probabilities_percent"], color="steelblue")
    proba_axis.bar_label(bars, fmt="%.1f%%", padding=3)
    proba_axis.invert_yaxis()
    proba_axis.set_xlim(0, 115)
    proba_axis.set_xlabel(
        f"Probabilidade predita pelo Random Forest base {EXPLAINED_BASE_NUMBER} (%)\n"
        "* classe real do fluxo, que é a classe explicada"
    )

    rows = explanation["contributions"]
    effects = [row["effect_pp"] for row in rows]
    # Cascata: a primeira e a última barra partem do zero; cada contribuição
    # parte de onde a anterior terminou.
    bottoms = [0.0, *np.cumsum(effects[:-2]).tolist(), 0.0]
    colors = ["goldenrod"]
    colors += ["tab:green" if effect >= 0 else "tab:red" for effect in effects[1:-1]]
    colors += ["steelblue"]
    waterfall_axis = figure.add_subplot(grid[1, 0])
    waterfall_axis.bar(range(len(rows)), effects, bottom=bottoms, color=colors)
    waterfall_axis.set_xticks(range(len(rows)), [row["item"] for row in rows])
    waterfall_axis.tick_params(axis="x", labelrotation=45)
    for label in waterfall_axis.get_xticklabels():
        label.set_horizontalalignment("right")
    waterfall_axis.set_ylabel(
        f"Probabilidade de {explanation['explained_class']} (%)\n"
        "verde: contribuição positiva; vermelho: negativa"
    )

    table_axis = figure.add_subplot(grid[:, 1])
    table_axis.axis("off")
    cells = [
        [
            row["item"] if row["value"] is None else f"{row['item']} = {row['value']:.6g}",
            f"{row['effect_pp']:.2f}%"
            if row["value"] is None and row["item"] != "Outros atributos somados"
            else f"{row['effect_pp']:+.2f}%",
        ]
        for row in rows
    ]
    table = table_axis.table(
        cellText=cells,
        colLabels=["Motivo (atributo = valor no fluxo)", "Efeito"],
        colWidths=[0.75, 0.2],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    return figure


def save_figure(figure: Figure, path: Path) -> None:
    """Grava a figura em PNG, sem o campo com a versão da biblioteca."""
    # A imagem depende da versão da biblioteca e das fontes da máquina. Os dados
    # de cada figura vão também em CSV: é esse arquivo que duas execuções comparam.
    figure.savefig(path, dpi=150, metadata={"Software": None})


def write_artifacts(
    run_dir: Path, importance: pd.DataFrame, dependence: pd.DataFrame, local: dict
) -> None:
    """Grava em `run_dir` a tabela de importância, as figuras e os dados de cada figura."""
    importance.to_csv(run_dir / "importancia.csv", index=False, float_format="%.6g")
    for class_name in CLASS_NAMES:
        series = importance_series(importance, EXPLAINED_BASE_NUMBER, class_name)
        save_figure(
            draw_fig5(series, class_name),
            run_dir / f"fig5_importancia_{class_name.lower()}.png",
        )

    dependence.to_csv(run_dir / "fig6_dependencia.csv", index=False, float_format="%.6g")
    duration_style = {
        "color": "Duration",
        "color_unit": "s",
        "log": False,
        "threshold": ARTICLE_DURATION_THRESHOLD_SECONDS,
    }
    save_figure(
        draw_dependence(dependence, "Duration", "s", duration_style),
        run_dir / "fig6a_dependencia_duration.png",
    )
    # Na Fig. 6b do artigo o eixo vai até 6.000 bytes, em escala linear. Aqui os
    # dois atributos cobrem várias ordens de grandeza, e a escala é logarítmica.
    bytes_style = {"color": "FlowBytesReceived", "color_unit": "bytes", "log": True}
    save_figure(
        draw_dependence(dependence, "FlowBytesSent", "bytes", bytes_style),
        run_dir / "fig6b_dependencia_flowbytessent.png",
    )

    for figure_name, file_name, _ in LOCAL_FIGURES:
        explanation = local[figure_name]
        table = pd.DataFrame(explanation["contributions"])
        table.to_csv(run_dir / f"{file_name}.csv", index=False, float_format="%.6g")
        title = (
            f"Explicação de um fluxo {explanation['explained_class']} do teste "
            f"(equivalente à {figure_name} do artigo)"
        )
        save_figure(draw_local(explanation, title), run_dir / f"{file_name}.png")


def explain_test_sample(
    scaler, stacked: StackingClassifier, test_sample: pd.DataFrame
) -> tuple[pd.DataFrame, dict, dict]:
    """Explica a amostra do teste com o Random Forest base escolhido.

    Devolve os dados das figuras de dependência, as explicações locais e as
    medidas tiradas da amostra.
    """
    forest = stacked.clfs_[EXPLAINED_BASE]
    X = scaler.transform(feature_matrix(test_sample))
    values, base_values = forest_shap_values(forest, X)
    base_proba, stacked_labels = forest.predict_proba(X), stacked.predict(X)
    explained = base_values + values.sum(axis=1)
    assert np.abs(explained - base_proba).max() < ADDITIVITY_TOLERANCE, (
        "O valor base mais os valores SHAP não reproduz a probabilidade do modelo."
    )

    # O modelo recebe os atributos normalizados. Os eixos das figuras e o limiar
    # de duração são lidos na unidade do dataset, desfazendo a normalização.
    units = original_units(scaler, X)
    assert np.allclose(units, feature_matrix(test_sample)), "A conversão de unidade não confere."
    dependence = pd.DataFrame(
        {
            "label": test_sample["label"].to_numpy(),
            "Duration": units["Duration"],
            "FlowBytesSent": units["FlowBytesSent"],
            "FlowBytesReceived": units["FlowBytesReceived"],
            "shap_Duration": values[:, FEATURE_COLUMNS.index("Duration"), MALICIOUS],
            "shap_FlowBytesSent": values[:, FEATURE_COLUMNS.index("FlowBytesSent"), MALICIOUS],
        }
    )

    # O artigo não diz como escolheu os fluxos das Figs. 7 e 8. Aqui é o
    # primeiro fluxo de cada classe na amostra do teste, que depende só da seed.
    labels = test_sample["label"].to_numpy()
    local = {}
    for figure_name, _, article in LOCAL_FIGURES:
        position = int(np.flatnonzero(labels == CLASS_NAMES.index(article["class_name"]))[0])
        local[figure_name] = local_explanation(
            position, test_sample, values, base_values, base_proba, stacked_labels
        )

    measures = {
        "duration_threshold": duration_threshold(
            dependence["Duration"].to_numpy(), dependence["shap_Duration"].to_numpy(), labels
        ),
        "received_over_sent": received_over_sent(dependence),
        "base_agrees_with_stacked_fraction": float(
            (base_proba.argmax(axis=1) == stacked_labels).mean()
        ),
        "stacked_predictions_by_class": np.bincount(
            stacked_labels, minlength=len(CLASS_NAMES)
        ).tolist(),
    }
    return dependence, local, measures


def explain_system(table: pd.DataFrame, reading: dict) -> tuple[dict, dict, dict, tuple]:
    """Ajusta o sistema sobre `table` e calcula os valores SHAP, sem gravar nada.

    `table` tem os atributos do modelo e `label`; `reading` é uma das entradas
    de `READINGS`. Devolve as métricas, a configuração, os tempos e os dados
    das figuras: a tabela de importância, os dados de dependência e as
    explicações locais.
    """
    start = time.perf_counter()
    # O teste é separado antes de qualquer ajuste. Ele só é lido aqui para ser
    # explicado: nenhum ajuste e nenhuma escolha dependem dele.
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."
    scaler, stacked, _, timings = fit_system(train, SEED_FIEL, reading["max_depth"])

    train_sample = stratified_sample(train, SHAP_SAMPLE_PER_CLASS, SEED_FIEL)
    test_sample = stratified_sample(test, SHAP_SAMPLE_PER_CLASS, SEED_FIEL)

    # Importância global na amostra do treino, como a Fig. 5 do artigo
    # ("global feature importance values obtained from the training data").
    shap_start = time.perf_counter()
    importance, base_values = base_importance(
        stacked.clfs_, scaler.transform(feature_matrix(train_sample))
    )
    timings["shap_train_sample_seconds"] = round(time.perf_counter() - shap_start, 1)

    # Dependência e explicações locais na amostra do teste, como as Figs. 6 a 8.
    shap_start = time.perf_counter()
    dependence, local, measures = explain_test_sample(scaler, stacked, test_sample)
    timings["shap_test_sample_seconds"] = round(time.perf_counter() - shap_start, 1)

    metrics = {
        "classes": CLASS_NAMES,
        "explained_base": EXPLAINED_BASE_NUMBER,
        "sample_per_class_requested": SHAP_SAMPLE_PER_CLASS,
        "train_sample_rows": class_counts(train_sample),
        "test_sample_rows": class_counts(test_sample),
        "base_values": base_values,
        "ranking": {
            f"base_{base}": {
                name: importance_series(importance, base, name).index.tolist()
                for name in CLASS_NAMES
            }
            for base in sorted(importance["base"].unique().tolist())
        },
        "stability_top_features": SHAP_TOP_FEATURES,
        "stability": ranking_stability(importance),
        "local": local,
        "stacked_explainer_error": stacked_explainer_error(stacked),
        **measures,
    }
    config = {
        "max_depth": stacked.clfs_[0].max_depth,
        "shap_sample_per_class": SHAP_SAMPLE_PER_CLASS,
        "shap_sample_seed": SEED_FIEL,
        "explained_base": EXPLAINED_BASE_NUMBER,
        "explainer": "shap.TreeExplainer, sem dados de referência, saída em probabilidade",
        "base_depth": reading["base_depth"],
    }
    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    return metrics, config, timings, (importance, dependence, local)


def run_experiment(
    table: pd.DataFrame, data_sha256: str, results_dir: Path, reading: dict
) -> tuple[Path, dict]:
    """Ajusta o sistema, calcula os valores SHAP e grava o resultado em `results_dir`.

    `table` tem os atributos do modelo e `label`; `reading` é uma das entradas
    de `READINGS`. Devolve o diretório da execução e o dicionário gravado em
    metrics.json.
    """
    metrics, config, timings, artifacts = explain_system(table, reading)
    # A Fig. 5 é do dataset do artigo: a comparação com ela só entra aqui.
    metrics["fig5_comparison"] = article_comparison(artifacts[0])
    run_dir = save_run(
        experiment="e5",
        track=reading["track"],
        slice_name=reading["slice_name"],
        seed=SEED_FIEL,
        metrics=metrics,
        config=config,
        data_sha256=data_sha256,
        timings=timings,
        results_dir=results_dir,
    )
    write_artifacts(run_dir, *artifacts)
    return run_dir, metrics


def ranking_table(metrics: dict) -> str:
    """Põe os primeiros atributos da Fig. 5 ao lado dos de cada base, para Malicious-DoH."""
    comparison = metrics["fig5_comparison"]
    columns = ["posto", "artigo, Fig. 5"] + [f"base {entry['base']}" for entry in comparison]
    rows = [
        [rank + 1, FIG5_RANKING[rank], *[entry["top_obtained"][rank] for entry in comparison]]
        for rank in range(SHAP_TOP_FEATURES)
    ]
    return markdown_table(columns, rows)


def article_top_table(metrics: dict) -> str:
    """Escreve o posto que cada atributo do topo da Fig. 5 ocupa em cada base."""
    comparison = metrics["fig5_comparison"]
    columns = ["atributo", "posto no artigo"] + [
        f"posto no base {entry['base']}" for entry in comparison
    ]
    rows = [
        [
            feature,
            rank,
            *[entry["obtained_rank_of_article_top"][feature] for entry in comparison],
        ]
        for rank, feature in enumerate(FIG5_RANKING[:SHAP_TOP_FEATURES], start=1)
    ]
    return markdown_table(columns, rows)


def ranking_text(metrics: dict) -> str:
    """Escreve o que a comparação com a Fig. 5 confirma e o que não confirma."""
    comparison = metrics["fig5_comparison"]
    duration = [entry["obtained_rank_of_article_top"]["Duration"] for entry in comparison]
    confirmed = "confirmado" if all(rank == 1 for rank in duration) else "não confirmado"
    correlations = ", ".join(f"{entry['spearman_all_features']:.3f}" for entry in comparison)
    shared = ", ".join(str(entry["top_shared_with_article"]) for entry in comparison)
    families = []
    for entry in comparison:
        top = entry["top_obtained"]
        families.append(
            f"base {entry['base']}: {sum(name.startswith('PacketLength') for name in top)} de "
            f"comprimento de pacote, {sum(name.startswith('PacketTime') for name in top)} de tempo "
            f"de pacote, {sum(name.startswith('ResponseTime') for name in top)} de tempo de "
            f"resposta, {sum(name.startswith('Flow') for name in top)} de bytes do fluxo"
        )
    return (
        f"- **`Duration` no topo: {confirmed}.** O artigo põe `Duration` em primeiro; nos três "
        f"bases ela fica nos postos {', '.join(map(str, duration))}.\n"
        f"- **Dez primeiros.** Atributos entre os {SHAP_TOP_FEATURES} primeiros do artigo que "
        f"também estão entre os {SHAP_TOP_FEATURES} primeiros de cada base: {shared}.\n"
        f"- **Ranking inteiro.** Correlação de postos de Spearman entre o ranking do artigo e o "
        f"de cada base, nos {len(FEATURE_COLUMNS)} atributos: {correlations}.\n"
        f"- **Famílias de atributos nos {SHAP_TOP_FEATURES} primeiros** (o artigo cita, depois "
        "da duração, comprimento de pacote e variância do tempo de pacote): "
        + "; ".join(families)
        + "."
    )


def share_text(fraction: float | None) -> str:
    """Escreve uma fração em percentual, ou um traço quando não há fluxo."""
    return "–" if fraction is None else f"{fraction:.2%}"


def threshold_class_table(threshold: dict) -> str:
    """Escreve, por classe real, os fluxos de cada lado do limiar do artigo e o sinal do SHAP."""
    seconds = threshold["article_threshold_seconds"]
    rows = [
        [
            name,
            entry["rows_up_to_article_threshold"],
            share_text(entry["positive_fraction_up_to_article_threshold"]),
            entry["rows_above_article_threshold"],
            share_text(entry["positive_fraction_above_article_threshold"]),
            entry["rows_between_cuts"],
            f"{entry['fraction_between_cuts']:.2%}",
        ]
        for name, entry in threshold["by_class"].items()
    ]
    columns = [
        "classe real",
        f"fluxos até {seconds} s",
        "com SHAP positivo",
        f"fluxos acima de {seconds} s",
        "com SHAP positivo",
        "fluxos entre os dois cortes",
        "fração da classe na amostra",
    ]
    return markdown_table(columns, rows)


def threshold_facts(threshold: dict) -> str:
    """Escreve os dois fatos medidos sobre o limiar de 40 segundos que o artigo lê na Fig. 6a."""
    seconds = threshold["article_threshold_seconds"]
    malicious = threshold["by_class"][CLASS_NAMES[MALICIOUS]]
    above = threshold["positive_fraction_above_article_threshold"]
    up_to = threshold["positive_fraction_up_to_article_threshold"]
    best = threshold["best_threshold_seconds"]
    observed = "é observada" if above > 0.5 > up_to else "não é observada"
    return (
        f"**Dois fatos medidos nesta amostra.** Primeiro, a direção que o artigo descreve "
        f"{observed}: acima de {seconds} s, {above:.2%} dos fluxos têm valor SHAP positivo; até "
        f"{seconds} s, {up_to:.2%}. Segundo, o ponto em que o sinal troca na amostra é "
        f"{best:.2f} s, e o artigo lê {seconds} s: o corte em {best:.2f} s deixa "
        f"{threshold['best_threshold_agreement']:.2%} dos fluxos do lado esperado, e o corte em "
        f"{seconds} s, {threshold['article_threshold_agreement']:.2%}. Entre os dois cortes "
        f"ficam {threshold['rows_between_cuts']} fluxos, {malicious['rows_between_cuts']} deles "
        f"{CLASS_NAMES[MALICIOUS]} ({malicious['fraction_between_cuts']:.2%} dos maliciosos da "
        f"amostra), e {share_text(threshold['positive_fraction_between_cuts'])} têm valor SHAP "
        "positivo. O artigo lê o limiar a olho na figura e não informa a amostra; a diferença "
        "não é atribuível. O corte medido é o que mais concorda com o sinal nesta amostra, por "
        "construção, e por isso não confirma nem nega o limiar do artigo. A amostra tem as três "
        "classes em partes iguais, e os percentuais não são os do tráfego."
    )


def threshold_text(threshold: dict) -> str:
    """Escreve o que a amostra do teste mostra sobre o limiar de 40 segundos."""
    return (
        f"O artigo lê na Fig. 6a um limiar de {threshold['article_threshold_seconds']} segundos: "
        "acima dele o valor SHAP de `Duration` para o tráfego malicioso seria positivo.\n\n"
        f"- Fluxos da amostra com duração acima de {threshold['article_threshold_seconds']} s: "
        f"{threshold['rows_above_article_threshold']}, dos quais "
        f"{threshold['positive_fraction_above_article_threshold']:.2%} têm valor SHAP positivo.\n"
        f"- Fluxos com duração até {threshold['article_threshold_seconds']} s: "
        f"{threshold['rows_up_to_article_threshold']}, dos quais "
        f"{threshold['positive_fraction_up_to_article_threshold']:.2%} têm valor SHAP positivo.\n"
        f"- Corte que melhor separa valor positivo de não positivo nesta amostra: "
        f"{threshold['best_threshold_seconds']:.2f} s, com "
        f"{threshold['best_threshold_agreement']:.2%} dos fluxos do lado esperado.\n"
        f"- Menor duração com valor positivo: {threshold['shortest_positive_seconds']:.4f} s; "
        f"maior duração com valor não positivo: {threshold['longest_non_positive_seconds']:.2f} s."
        '\n\nPor classe real. "Entre os dois cortes" são os fluxos com duração entre o corte '
        f"medido e os {threshold['article_threshold_seconds']} s do artigo:\n\n"
        f"{threshold_class_table(threshold)}\n\n{threshold_facts(threshold)}"
    )


def local_text(metrics: dict) -> str:
    """Escreve as duas explicações locais ao lado dos números das Figs. 7 e 8 do artigo."""
    blocks = []
    for figure_name, file_name, article in LOCAL_FIGURES:
        explanation = metrics["local"][figure_name]
        rows = explanation["contributions"]
        population, top, final = rows[0], rows[1], rows[-1]
        table = markdown_table(
            ["motivo", "valor no fluxo", "efeito (pp)"],
            [
                [
                    row["item"],
                    "" if row["value"] is None else f"{row['value']:.6g}",
                    f"{row['effect_pp']:+.2f}",
                ]
                for row in rows
            ],
        )
        blocks.append(
            f"### Equivalente à {figure_name}: fluxo {explanation['explained_class']} do teste\n\n"
            f"Arquivos `{file_name}.png` e `{file_name}.csv`. Classe predita pelo base "
            f"{metrics['explained_base']}: {explanation['base_predicted_class']}; pelo modelo "
            f"empilhado: {explanation['stacked_predicted_class']}.\n\n"
            + markdown_table(
                ["medida", f"artigo, {figure_name}", "aqui"],
                [
                    [
                        f"probabilidade de {article['class_name']} (%)",
                        article["prediction"],
                        f"{final['effect_pp']:.2f}",
                    ],
                    [
                        "média da população (%)",
                        article["population_average"],
                        f"{population['effect_pp']:.2f}",
                    ],
                    [
                        "atributo de maior efeito",
                        f"{article['top_feature']} = {article['top_value']:.6g} "
                        f"({article['top_effect']:+.2f} pp)",
                        f"{top['item']} = {top['value']:.6g} ({top['effect_pp']:+.2f} pp)",
                    ],
                ],
            )
            + f"\n\n{table}"
        )
    return "\n\n".join(blocks)


def stability_table(metrics: dict) -> str:
    """Escreve a concordância do ranking entre cada par de bases, por classe."""
    pairs = list(metrics["stability"][CLASS_NAMES[0]])
    rows = [
        [name, *[f"{metrics['stability'][name][pair]:.3f}" for pair in pairs]]
        for name in CLASS_NAMES
    ]
    return markdown_table(["classe", *[f"bases {pair}" for pair in pairs]], rows)


def limitation_text(metrics: dict) -> str:
    """Escreve o que a explicação cobre e o que ela deixa de fora."""
    error = metrics["stacked_explainer_error"]
    refusal = (
        f"O `TreeExplainer` recusa o modelo empilhado com o erro: `{error}`"
        if error
        else "Nesta execução o `TreeExplainer` não recusou o modelo empilhado"
    )
    predictions = ", ".join(
        f"{count} de {name}"
        for name, count in zip(CLASS_NAMES, metrics["stacked_predictions_by_class"], strict=True)
    )
    return (
        "Os valores SHAP deste experimento explicam os Random Forests base, não a decisão do "
        "empilhamento. A linha 8 do Algoritmo 1 do artigo aplica o `TreeExplainer` sem dizer a "
        f"qual modelo. {refusal}. A regressão logística que combina os três bases não é um "
        "modelo de árvores, e a decisão final do sistema passa por ela.\n\n"
        f"Na amostra do teste, com as classes em partes iguais, a classe de maior "
        f"probabilidade do base "
        f"{metrics['explained_base']} é a classe que o modelo empilhado devolve em "
        f"{metrics['base_agrees_with_stacked_fraction']:.2%} dos fluxos. Predições do modelo "
        f"empilhado na amostra: {predictions}. Onde os dois divergem, a explicação do base não "
        "é a explicação da saída do sistema."
    )


def explained_model_text(e1_tests: dict) -> str:
    """Escreve qual leitura de profundidade é a explicação principal e por quê."""
    lines = []
    for reading in READINGS:
        benign = e1_tests[reading["track"]]["per_class"]["Benign-DoH"]
        lines.append(
            f"- **{reading['label']}:** no teste, o modelo empilhado tem recall de Benign-DoH "
            f"de {benign['recall']:.2%} (`results/e1/{reading['track']}/`)."
        )
    return (
        "A explicação principal é a do sistema na leitura de profundidade variável, em "
        "`results/e5/variante/`. A leitura de profundidade 5 é explicada ao lado, em "
        "`results/e5/fiel/`. O motivo está no resultado da reprodução:\n\n"
        + "\n".join(lines)
        + "\n\nUm sistema que não prediz uma das três classes não sustenta a explicação das "
        "decisões dele. Os Random Forests base de profundidade 5, sozinhos, predizem as três "
        "classes, e é a eles que os valores SHAP se referem nas duas leituras."
    )


def summary_text(metrics: dict, reading: dict, context: dict) -> str:
    """Monta o RESUMO.md de uma leitura a partir dos números medidos na execução."""
    run_dir = f"{reading['slice_name']}/seed{SEED_FIEL}"
    base_values = ", ".join(
        f"{100 * value:.2f}%" for value in metrics["base_values"][metrics["explained_base"] - 1]
    )
    medians = ", ".join(
        f"{value:.2f} s em {name}"
        for name, value in zip(CLASS_NAMES, context["duration_medians"], strict=True)
    )
    over = metrics["received_over_sent"]
    mode = context["packet_length_mode"]
    malicious_ranking = metrics["ranking"][f"base_{metrics['explained_base']}"][
        CLASS_NAMES[MALICIOUS]
    ]
    mode_rank = malicious_ranking.index(mode["column"]) + 1
    return f"""# E5: explicabilidade com SHAP, {reading["label"]}

Gerado por `scripts/e5_xai.py`. Os números vêm de `{run_dir}/metrics.json`; os
tempos estão em `{run_dir}/run.json`. Random Forests base:
{reading["base_depth"]}. A outra leitura da profundidade está ao lado desta, em
`../RESUMO.md`. Uma única execução, com a seed {SEED_FIEL}.
Classes na ordem dos códigos: {", ".join(CLASS_NAMES)}.

## Modelo explicado

{explained_model_text(context["e1_tests"])}

## Amostras

Os valores SHAP são calculados com o `TreeExplainer` em duas amostras
estratificadas, de até {
        metrics["sample_per_class_requested"]
    } fluxos por classe, sorteadas com a seed
{SEED_FIEL}. O artigo fala em todo o treino (Fig. 5) e em todo o teste (Fig. 6).

{
        markdown_table(
            ["amostra", *CLASS_NAMES, "uso"],
            [
                ["treino", *metrics["train_sample_rows"], "importância global (Fig. 5)"],
                [
                    "teste",
                    *metrics["test_sample_rows"],
                    "dependência e explicações locais (Figs. 6 a 8)",
                ],
            ],
        )
    }

As classes entram em partes iguais. A importância média pesa as três classes
por igual, e não na proporção do tráfego, em que Non-DoH é a maioria.

A tabela `{run_dir}/importancia.csv` traz a média do valor absoluto de SHAP
por base, classe e atributo. As figuras usam o Random Forest base
{metrics["explained_base"]}, o do primeiro subconjunto. Valor base (probabilidade média) de cada
classe nesse modelo: {base_values}.

## Importância global ao lado da Fig. 5

A Fig. 5 do artigo é um gráfico de barras com a média do valor absoluto de SHAP
de cada um dos {len(FEATURE_COLUMNS)} atributos. Ela não diz a classe; a legenda fala do tráfego
malicioso, e a comparação é com o ranking da classe {CLASS_NAMES[MALICIOUS]}.
Figura equivalente: `{run_dir}/fig5_importancia_malicious-doh.png`; as das
outras duas classes estão na mesma pasta.

{ranking_table(metrics)}

Posto, em cada base, dos {SHAP_TOP_FEATURES} primeiros atributos do artigo:

{article_top_table(metrics)}

{ranking_text(metrics)}

## Estabilidade entre os três submodelos

Correlação de postos de Spearman entre os rankings de dois bases, sobre os
atributos que estão entre os {metrics["stability_top_features"]} primeiros de pelo menos um deles.
O valor 1 quer dizer a mesma ordem.

{stability_table(metrics)}

## Dependência de `Duration` ao lado da Fig. 6a

Figura equivalente: `{run_dir}/fig6a_dependencia_duration.png`, com os dados
em `{run_dir}/fig6_dependencia.csv`. Um ponto por fluxo da amostra do teste;
no eixo horizontal a duração em segundos, depois de desfeita a normalização;
no vertical o valor SHAP de `Duration` para a classe {CLASS_NAMES[MALICIOUS]}.

{threshold_text(metrics["duration_threshold"])}

Ressalva sobre os dados: a mediana de `Duration` no dataset limpo é
{medians}. A classe maliciosa foi capturada em outras máquinas e em outro
período, de modo que a duração pode separar as classes pelo modo como o tráfego
foi gerado, e não só pelo protocolo.

Ressalva sobre `{mode["column"]}`, atributo de posto {mode_rank} no ranking de
{CLASS_NAMES[MALICIOUS]} do base {metrics["explained_base"]} e de posto
{FIG5_RANKING.index(mode["column"]) + 1} na Fig. 5 do artigo.
{one_feature_rule_text(mode)}
Os números vêm de `results/e6/dados/hkd/seed{SEED_FIEL}/metrics.json`, gravado por
`scripts/e6_dados.py`. Como a duração, esse atributo pode separar as classes
pelo modo como o tráfego do CIRA foi capturado, e não só pelo protocolo: a
importância dele aqui não diz que ele detecta túnel de outra captura.

## Dependência de `FlowBytesSent` ao lado da Fig. 6b

Figura equivalente: `{run_dir}/fig6b_dependencia_flowbytessent.png`. O artigo
chama a Fig. 6b de gráfico de interação; o que ela mostra é o valor SHAP de
`FlowBytesSent` contra o valor do atributo, com os pontos coloridos por
`FlowBytesReceived`. Os valores de interação de SHAP não foram calculados. Os
eixos estão em escala logarítmica; os do artigo são lineares, até 6.000 bytes.

O artigo aponta um grupo de fluxos com mais bytes recebidos que enviados e o
associa ao tráfego malicioso. Na amostra do teste:

- fluxos com mais bytes recebidos que enviados, por classe real:
  {over["rows_by_class"]}; valor SHAP de `FlowBytesSent` positivo em {
        over["positive_fraction"]:.2%} deles;
- demais fluxos, por classe real: {over["rows_others_by_class"]}; valor SHAP positivo em
  {over["positive_fraction_others"]:.2%} deles.

## Explicações locais ao lado das Figs. 7 e 8

As Figs. 7 e 8 do artigo são telas do painel interativo: probabilidade por
classe, tabela de contribuição e gráfico de contribuição em cascata. As figuras
equivalentes trazem os três elementos. O fluxo explicado é o primeiro da classe
na amostra do teste; o artigo não diz como escolheu os dele. As probabilidades
são as do Random Forest base {metrics["explained_base"]}, que é o que os valores SHAP decompõem.

{local_text(metrics)}

## Limitação

{limitation_text(metrics)}

## Ressalvas e o que não foi feito

- Nas seis colunas de assimetria o extrator grava {SKEW_SENTINEL} quando o desvio padrão é
  zero; {context["sentinel_rows"]} fluxos do dataset limpo têm esse valor em alguma delas. A
  importância dessas colunas mede em parte esse marcador, e não a assimetria.
- Os valores SHAP são calculados em amostras, não no treino e no teste inteiros.
- Não há média entre seeds: uma execução, com a seed {SEED_FIEL}.
- O painel interativo é um script à parte e não grava resultado.
- Nenhuma seed, amostra ou fluxo foi escolhido para aproximar as figuras do artigo.
"""


def comparison_text(results: list[tuple[dict, dict]], e1_tests: dict) -> str:
    """Monta o RESUMO.md que põe os rankings das duas leituras lado a lado com o artigo."""
    columns = ["posto", "artigo, Fig. 5"] + [reading["label"] for reading, _ in results]
    tops = [metrics["fig5_comparison"][EXPLAINED_BASE]["top_obtained"] for _, metrics in results]
    rows = [
        [rank + 1, FIG5_RANKING[rank], *[top[rank] for top in tops]]
        for rank in range(SHAP_TOP_FEATURES)
    ]
    measures = [
        [
            reading["label"],
            f"{metrics['fig5_comparison'][EXPLAINED_BASE]['spearman_all_features']:.3f}",
            metrics["fig5_comparison"][EXPLAINED_BASE]["top_shared_with_article"],
            f"{metrics['duration_threshold']['best_threshold_seconds']:.2f}",
            metrics["duration_threshold"]["rows_between_cuts"],
            f"{metrics['duration_threshold']['positive_fraction_above_article_threshold']:.2%}",
            f"{metrics['duration_threshold']['positive_fraction_up_to_article_threshold']:.2%}",
            f"{metrics['base_agrees_with_stacked_fraction']:.2%}",
        ]
        for reading, metrics in results
    ]
    readings = "\n".join(
        f"- **{reading['label']}:** {reading['base_depth']}. Detalhe em "
        f"`{reading['track']}/RESUMO.md`."
        for reading, _ in results
    )
    return f"""# E5: explicabilidade nas duas leituras da profundidade, ao lado do artigo

Gerado por `scripts/e5_xai.py`. Dados, seed ({SEED_FIEL}), split, subconjuntos, SMOTE,
meta-classificador e amostras do SHAP são os mesmos nas duas leituras.

{readings}

{explained_model_text(e1_tests)}

## Ranking de {CLASS_NAMES[MALICIOUS]} ao lado da Fig. 5

Random Forest base {EXPLAINED_BASE_NUMBER} de cada leitura, na amostra do treino.

{markdown_table(columns, rows)}

## Medidas lado a lado

{
        markdown_table(
            [
                "leitura",
                f"Spearman com a Fig. 5 ({len(FEATURE_COLUMNS)} atributos)",
                f"atributos em comum nos {SHAP_TOP_FEATURES} primeiros",
                "corte que melhor separa o sinal do SHAP (s), amostra com classes em partes iguais",
                f"fluxos entre o corte medido e {ARTICLE_DURATION_THRESHOLD_SECONDS} s",
                f"SHAP positivo acima de {ARTICLE_DURATION_THRESHOLD_SECONDS} s",
                f"SHAP positivo até {ARTICLE_DURATION_THRESHOLD_SECONDS} s",
                "base concorda com o empilhado",
            ],
            measures,
        )
    }

As medidas são do Random Forest base {EXPLAINED_BASE_NUMBER}, na amostra do teste com as classes
em partes iguais. O corte medido é o ponto em que o sinal do valor SHAP de
`Duration` troca na amostra; o artigo lê {
        ARTICLE_DURATION_THRESHOLD_SECONDS
    } s a olho na Fig. 6a e não informa a
amostra, e a diferença entre os dois não é atribuível. O detalhe por classe está
no resumo de cada trilha. A última coluna diz em que fração da amostra a classe
mais provável do base é a classe que o modelo empilhado devolve: é o alcance da
explicação do base como explicação do sistema.
"""


def main() -> None:
    """Confere o Parquet, explica o sistema nas duas leituras e grava os resumos."""
    assert sorted(FIG5_RANKING) == sorted(FEATURE_COLUMNS), "Ranking da Fig. 5 incompleto."
    e0_metrics = json.loads((E0_DIR / "metrics.json").read_text(encoding="utf-8"))
    data_sha256 = sha256_of(CIRA_PARQUET_PATH)
    if data_sha256 != e0_metrics["parquet_sha256"]:
        raise SystemExit(
            f"SHA-256 de {CIRA_PARQUET_PATH.name} difere do registrado pela etapa de dados: "
            f"encontrado {data_sha256}. Rode scripts/e0_dados.py de novo."
        )
    e1_tests = {
        reading["track"]: json.loads(
            (
                E1_DIR / reading["track"] / reading["slice_name"] / f"seed{SEED_FIEL}/metrics.json"
            ).read_text(encoding="utf-8")
        )["test"]
        for reading in READINGS
    }

    if not HKD_DATA_PATH.exists():
        raise SystemExit(
            f"Falta {HKD_DATA_PATH.relative_to(PROJECT_ROOT)}. Rode scripts/e6_dados.py antes."
        )
    hkd_data = json.loads(HKD_DATA_PATH.read_text(encoding="utf-8"))

    table = pd.read_parquet(CIRA_PARQUET_PATH)
    context = {
        "e1_tests": e1_tests,
        "packet_length_mode": hkd_data["packet_length_mode"],
        "duration_medians": table.groupby("label")["Duration"].median().tolist(),
        "sentinel_rows": int((table[SKEW_COLUMNS] == SKEW_SENTINEL).any(axis=1).sum()),
    }
    results = []
    for reading in READINGS:
        run_dir, metrics = run_experiment(table, data_sha256, RESULTS_DIR, reading)
        assert max(metrics["test_sample_rows"]) <= SHAP_SAMPLE_PER_CLASS
        summary = summary_text(metrics, reading, context)
        (run_dir.parents[1] / "RESUMO.md").write_text(summary, encoding="utf-8")
        results.append((reading, metrics))

        print(f"\n== {reading['label']} ==")
        print(f"Amostra do treino: {metrics['train_sample_rows']}")
        print(f"Amostra do teste: {metrics['test_sample_rows']}")
        print(ranking_table(metrics))
        print(ranking_text(metrics))
        print(stability_table(metrics))
        print(threshold_text(metrics["duration_threshold"]))
        timings = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["timings"]
        print(f"Tempos, em segundos: {timings}")
        print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}")

    (RESULTS_DIR / "e5" / "RESUMO.md").write_text(
        comparison_text(results, e1_tests), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
