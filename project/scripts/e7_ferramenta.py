"""E7: identificação da ferramenta de túnel (Seção VI-D e Fig. 9 do artigo).

O artigo diz que o sistema identifica a ferramenta que gerou o tráfego
malicioso e dá um valor por ferramenta, sem descrever o método. Leitura adotada
aqui: o mesmo sistema da reprodução (split de 10% para teste, normalizador
ajustado no treino, três subconjuntos balanceados, três Random Forests e
regressão logística), aplicado só aos fluxos maliciosos do
CIRA-CIC-DoHBrw-2020, com dns2tcp, dnscat2 e iodine como as três classes.

Lê data/raw/cira/MaliciousDoH-CSVs.zip, que traz a ferramenta de cada fluxo.
O sistema é treinado nas duas leituras de profundidade do artigo: sem limite,
na trilha variante, que é a principal, e profundidade máxima 5, na trilha fiel.

Grava metrics.json e run.json em results/e7/variante/ferramenta/seed42/ e em
results/e7/fiel/ferramenta/seed42/, a figura equivalente à Fig. 9 e os dados
dela em results/e7/dados/fig9/seed42/ e a leitura dos números em
results/e7/RESUMO.md.

Uso: uv run python scripts/e7_ferramenta.py
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from mlxtend.classifier import StackingClassifier
from scipy.stats import norm
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler

from doh_ids.config import (
    CIRA_TOOLS,
    CLASS_NAMES,
    DATA_RAW_DIR,
    FEATURE_COLUMNS,
    FIEL_READINGS,
    FIG9_BINS,
    FIG9_MEAN_STD,
    FIG9_PANELS,
    MALICIOUS_ZIP_PATH,
    MAX_DEPTH,
    MAX_DEPTH_VARIABLE,
    MAX_FEATURES,
    N_ESTIMATORS,
    N_JOBS,
    N_SUBSETS,
    PROJECT_ROOT,
    README_TOOL_ROWS,
    RESULTS_DIR,
    SECTION_VI_D_ACCURACY,
    SEED_FIEL,
    SKEW_COLUMNS,
    SKEW_SENTINEL,
    TABLE_I_COUNTS,
    TEST_SIZE,
    smote_seed,
)
from doh_ids.data import clean_flows, feature_matrix, load_malicious_by_tool, sha256_of
from doh_ids.evaluate import evaluate, metrics_from_confusion
from doh_ids.runlog import save_run
from doh_ids.splits import seen_in_train, stratified_split
from doh_ids.summary import frame_markdown_table
from doh_ids.system import fit_system

MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"

# Contagens por ferramenta que a etapa de dados do segundo dataset registrou,
# lidas de outro arquivo (o combinado), com as quais esta carga é conferida.
E6_DATA_METRICS = (
    RESULTS_DIR / "e6" / "dados" / "combinado_sem_replicas" / f"seed{SEED_FIEL}" / "metrics.json"
)

# A mesma regra de limpeza da reprodução: saem as linhas com valor ausente em
# algum atributo, e nada mais.
CLEANING = {"drop_nan": True, "drop_inf": False, "duplicate_columns": None}

# O sistema do artigo dá um papel a cada código de classe: a classe de código 0
# (Non-DoH, a maior) é dividida em três partes, a de código 1 (Benign-DoH, a
# menor) é aumentada com SMOTE até o tamanho da de código 2 (Malicious-DoH),
# que entra inteira em cada subconjunto (Seção III-B). Entre ferramentas, os
# mesmos papéis vão para a maior, a menor e a terceira.
SPLIT_ROLE = CLASS_NAMES.index("Non-DoH")
RESAMPLED_ROLE = CLASS_NAMES.index("Benign-DoH")
REFERENCE_ROLE = CLASS_NAMES.index("Malicious-DoH")

SCENARIO = "ferramenta"

# As duas leituras da profundidade dos Random Forests base, a principal
# primeiro. Tudo o mais é igual nas duas: dados, seed, split, subconjuntos,
# SMOTE e meta-classificador.
READINGS = [
    {
        "track": "variante",
        "max_depth": MAX_DEPTH_VARIABLE,
        "label": "variante (profundidade variável)",
        "base_depth": 'sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1)',
    },
    {
        "track": "fiel",
        "max_depth": MAX_DEPTH,
        "label": f"fiel (profundidade {MAX_DEPTH})",
        "base_depth": f"profundidade máxima {MAX_DEPTH} nos submodelos (Seção IV-B)",
    },
]

# Leituras próprias deste experimento, gravadas no registro de cada execução.
E7_READINGS = {
    "method": "sistema da reprodução aplicado só aos fluxos maliciosos, uma classe por ferramenta",
    "subset_roles": "a ferramenta com mais fluxos no treino é dividida em três partes; a com "
    "menos é aumentada com SMOTE até o tamanho da terceira",
    "smote_target": "só a ferramenta com menos fluxos no treino",
    "cross_validation": "não executada: o artigo não mostra matriz para a Seção VI-D",
}

# Cores das ferramentas na Fig. 9 do artigo.
FIG9_COLORS = {"iodine": "tab:blue", "dnscat2": "tab:red", "dns2tcp": "yellowgreen"}

METRIC_TITLES = [("recall", "recall"), ("precision", "precisão"), ("f1", "F1")]


def checked_sha256() -> str:
    """Devolve o SHA-256 do zip dos fluxos maliciosos, depois de conferi-lo com o manifesto."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    zip_name = MALICIOUS_ZIP_PATH.relative_to(DATA_RAW_DIR).as_posix()
    entry = next(item for item in manifest["files"] if item["path"] == zip_name)
    found = sha256_of(MALICIOUS_ZIP_PATH)
    if found != entry["sha256"]:
        raise SystemExit(f"SHA-256 de {zip_name} difere do manifesto: encontrado {found}.")
    return found


def load_clean_flows() -> tuple[pd.DataFrame, dict]:
    """Lê os fluxos maliciosos por ferramenta, limpa e confere as contagens.

    Devolve a tabela limpa, com os atributos, `tool` e `label`, e as contagens
    por ferramenta antes e depois da limpeza. O `label` daqui é o código da
    ferramenta na ordem de `CIRA_TOOLS` e só serve para contar e estratificar.
    """
    raw = load_malicious_by_tool()
    raw["label"] = raw["tool"].map(CIRA_TOOLS.index)
    flows, _ = clean_flows(raw, **CLEANING)
    counts = {
        "raw_rows_by_tool": raw["tool"].value_counts().sort_index().to_dict(),
        "clean_rows_by_tool": flows["tool"].value_counts().sort_index().to_dict(),
    }

    # O conjunto tem de ser a classe Malicious-DoH da reprodução, só que com a
    # ferramenta: as contagens são conferidas com as que o dataset publica, com
    # a Tabela I do artigo e com as que a etapa de dados mediu em outro arquivo.
    registered = json.loads(E6_DATA_METRICS.read_text(encoding="utf-8"))["clean_rows_by_tool"]
    for tool in CIRA_TOOLS:
        assert counts["raw_rows_by_tool"][tool] == README_TOOL_ROWS[tool], (
            f"Fluxos de {tool} no zip diferem do que o dataset informa."
        )
        assert counts["clean_rows_by_tool"][tool] == registered[tool], (
            f"Fluxos de {tool} depois da limpeza diferem dos registrados pela etapa de dados."
        )
    assert len(flows) == TABLE_I_COUNTS[CLASS_NAMES.index("Malicious-DoH")], (
        "Total depois da limpeza difere do Malicious-DoH da Tabela I do artigo."
    )
    assert set(flows.columns) == set(FEATURE_COLUMNS) | {"tool", "label"}
    return flows, counts


def tool_roles(train_tools: pd.Series) -> list[str]:
    """Devolve as ferramentas na ordem dos códigos de classe que o sistema espera.

    A posição na lista é o código: a ferramenta com mais fluxos no treino
    recebe o código da classe dividida em três partes, a com menos o da classe
    aumentada com SMOTE e a terceira o da classe de referência.
    """
    counts = train_tools.value_counts()
    assert len(counts) == len(CLASS_NAMES), "O sistema espera exatamente três ferramentas."
    assert counts.is_unique, "Duas ferramentas com a mesma contagem: papel indefinido."
    largest, middle, smallest = counts.index
    roles = [""] * len(CLASS_NAMES)
    roles[SPLIT_ROLE] = largest
    roles[RESAMPLED_ROLE] = smallest
    roles[REFERENCE_ROLE] = middle
    return roles


def base_mean_proba(stacked: StackingClassifier, X: np.ndarray) -> np.ndarray:
    """Devolve a média das probabilidades por classe dos Random Forests base."""
    return np.mean([forest.predict_proba(X) for forest in stacked.clfs_], axis=0)


def article_comparison(test_metrics: dict) -> dict:
    """Põe o valor da Seção VI-D de cada ferramenta ao lado das métricas dela no teste.

    Devolve, por ferramenta, o valor do artigo, o suporte, o recall, a precisão
    e o F1 obtidos e a diferença de cada um para o artigo, em pontos percentuais.
    """
    # O artigo chama os três valores de "accuracy" e não diz como os calculou.
    # A medida que responde "quantos fluxos desta ferramenta foram atribuídos a
    # ela" é o recall; a precisão e o F1 vão ao lado, porque o valor do artigo
    # também pode ser um deles.
    comparison = {}
    for tool, target in SECTION_VI_D_ACCURACY.items():
        obtained = test_metrics["per_class"][tool]
        comparison[tool] = {
            "article_accuracy": target,
            "support": obtained["support"],
            **{metric: obtained[metric] for metric, _ in METRIC_TITLES},
            "difference_pp": {
                metric: 100 * (obtained[metric] - target) for metric, _ in METRIC_TITLES
            },
        }
    return comparison


def experiment_metrics(
    scaler: MinMaxScaler,
    stacked: StackingClassifier,
    summary: list[dict],
    train: pd.DataFrame,
    test: pd.DataFrame,
    roles: list[str],
) -> dict:
    """Avalia o sistema ajustado no teste e monta o dicionário gravado em metrics.json.

    `roles` são as ferramentas na ordem dos códigos de classe.
    """
    X_test = scaler.transform(feature_matrix(test))
    y_test = test["label"].to_numpy()
    test_metrics = evaluate(
        y_test,
        stacked.predict(X_test),
        stacked.predict_proba(X_test),
        base_mean_proba(stacked, X_test),
        class_names=roles,
    )
    labels = list(range(len(roles)))
    train_rows = np.bincount(train["label"], minlength=len(roles)).tolist()
    test_rows = np.bincount(y_test, minlength=len(roles)).tolist()
    # Amostra sintética só existe dentro dos subconjuntos de treino: a matriz
    # tem, por ferramenta, exatamente as linhas reais do teste.
    assert [sum(row) for row in test_metrics["confusion_matrix"]] == test_rows

    seen = seen_in_train(train, test)
    return {
        "classes": roles,
        "roles": {
            "split_in_three": roles[SPLIT_ROLE],
            "resampled": roles[RESAMPLED_ROLE],
            "reference": roles[REFERENCE_ROLE],
        },
        "train_rows": train_rows,
        "test_rows": test_rows,
        "test": test_metrics,
        "article_comparison": article_comparison(test_metrics),
        "subsets": [
            {
                "class_counts": entry["class_counts"],
                "synthetic_fraction_of_resampled": entry["synthetic_benign_fraction"],
            }
            for entry in summary
        ],
        "base_models_test": [
            metrics_from_confusion(
                confusion_matrix(y_test, forest.predict(X_test), labels=labels), roles
            )
            for forest in stacked.clfs_
        ],
        "test_seen_in_train": {
            "total": int(seen.sum()),
            "fraction_total": float(seen.mean()),
            "fraction": [float(seen[y_test == code].mean()) for code in labels],
        },
    }


def run_config(stacked: StackingClassifier, reading: dict, roles: list[str]) -> dict:
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
        "n_jobs": N_JOBS,
        "smote_seeds": [smote_seed(SEED_FIEL, index) for index in range(N_SUBSETS)],
        "cleaning": CLEANING,
        "classes": roles,
        "readings": {**FIEL_READINGS, **E7_READINGS, "base_depth": reading["base_depth"]},
    }


def run_experiment(
    flows: pd.DataFrame, data_sha256: str, results_dir: Path, reading: dict
) -> tuple[Path, dict]:
    """Treina e avalia o sistema sobre `flows` e grava o resultado em `results_dir`.

    `flows` tem os atributos, `tool` e um `label` que distingue as ferramentas;
    `reading` é uma das entradas de `READINGS`. Devolve o diretório da execução
    e o dicionário de métricas gravado em metrics.json.
    """
    start = time.perf_counter()
    # O teste é separado antes de qualquer ajuste, com a mesma proporção de
    # ferramentas do conjunto todo, e só volta na avaliação final.
    train, test = stratified_split(flows, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."

    # O papel de cada ferramenta vem só das contagens do treino. O código de
    # classe definitivo é a posição da ferramenta nessa ordem.
    roles = tool_roles(train["tool"])
    train = train.assign(label=train["tool"].map(roles.index))
    test = test.assign(label=test["tool"].map(roles.index))

    scaler, stacked, summary, timings = fit_system(train, SEED_FIEL, reading["max_depth"])
    metrics = experiment_metrics(scaler, stacked, summary, train, test, roles)
    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    run_dir = save_run(
        experiment="e7",
        track=reading["track"],
        slice_name=SCENARIO,
        seed=SEED_FIEL,
        metrics=metrics,
        config=run_config(stacked, reading, roles),
        data_sha256=data_sha256,
        timings=timings,
        results_dir=results_dir,
    )
    return run_dir, metrics


def fig9_data(flows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula o que a figura equivalente à Fig. 9 desenha.

    Devolve as curvas (atributo, ferramenta, ponto do eixo, densidade da curva
    normal e densidade do histograma) e as estatísticas (por atributo e
    ferramenta: fluxos, média e desvio padrão obtidos e os do artigo, fração
    dos fluxos dentro do eixo da figura e fração com o marcador -10).
    """
    curves, statistics = [], []
    for column, _, low, high in FIG9_PANELS:
        edges = np.linspace(low, high, FIG9_BINS + 1)
        centers = (edges[:-1] + edges[1:]) / 2
        for tool in CIRA_TOOLS:
            values = flows.loc[flows["tool"] == tool, column]
            mean, std = values.mean(), values.std()
            inside, _ = np.histogram(values, bins=edges)
            curves.append(
                pd.DataFrame(
                    {
                        "atributo": column,
                        "ferramenta": tool,
                        "x": centers,
                        # A Fig. 9 do artigo desenha, para cada ferramenta, a
                        # curva normal com a média e o desvio padrão da legenda.
                        "densidade_normal": norm.pdf(centers, mean, std),
                        # O histograma é dividido por todos os fluxos da
                        # ferramenta: o que cai fora do eixo falta na área.
                        "densidade_histograma": inside / (len(values) * (edges[1] - edges[0])),
                    }
                )
            )
            article_mean, article_std = FIG9_MEAN_STD[column][tool]
            # Nas colunas de assimetria o extrator grava -10 quando o desvio
            # padrão do fluxo é zero: o valor entra na média como se fosse medida.
            sentinel = (values == SKEW_SENTINEL).mean() if column in SKEW_COLUMNS else None
            statistics.append(
                [column, tool, len(values), mean, std, article_mean, article_std]
                + [inside.sum() / len(values), sentinel]
            )
    columns = ["atributo", "ferramenta", "fluxos", "média", "desvio padrão"]
    columns += ["média no artigo", "desvio padrão no artigo", "fração no eixo", "fração com -10"]
    return pd.concat(curves, ignore_index=True), pd.DataFrame(statistics, columns=columns)


def draw_fig9(curves: pd.DataFrame, statistics: pd.DataFrame) -> Figure:
    """Desenha a figura equivalente à Fig. 9: curva normal e histograma por ferramenta.

    A linha de cima repete o tipo de gráfico do artigo, uma curva normal por
    ferramenta com a média e o desvio padrão na legenda. A de baixo mostra o
    histograma dos mesmos fluxos, que a curva normal resume.
    """
    # A figura é criada sem a interface pyplot, que abriria uma janela: assim o
    # script roda em máquina sem tela.
    figure = Figure(figsize=(13, 8), layout="constrained")
    axes = figure.subplots(2, len(FIG9_PANELS))
    rows = [
        ("densidade_normal", "Curva normal com a média e o desvio padrão medidos"),
        ("densidade_histograma", "Histograma dos fluxos"),
    ]
    for (key, title), row_axes in zip(rows, axes, strict=True):
        for axis, letter, (column, unit, _, _) in zip(row_axes, "ab", FIG9_PANELS, strict=True):
            for tool, color in FIG9_COLORS.items():
                curve = curves[(curves["atributo"] == column) & (curves["ferramenta"] == tool)]
                measured = statistics[
                    (statistics["atributo"] == column) & (statistics["ferramenta"] == tool)
                ].iloc[0]
                label = f"{tool} (μ={measured['média']:.6g}, σ={measured['desvio padrão']:.6g})"
                axis.plot(curve["x"], curve[key], color=color, label=label)
            axis.set_title(title)
            axis.set_xlabel(f"({letter}) {column} ({unit})")
            axis.set_ylabel("Densidade" if unit == "sem unidade" else f"Densidade (1/{unit})")
            axis.set_ylim(bottom=0)
            axis.legend(title="Ferramenta")
    return figure


def run_fig9(flows: pd.DataFrame, data_sha256: str, results_dir: Path) -> tuple[Path, dict]:
    """Grava em `results_dir` a figura equivalente à Fig. 9, os dados dela e o registro.

    Devolve o diretório da execução e o dicionário gravado em metrics.json.
    """
    start = time.perf_counter()
    curves, statistics = fig9_data(flows)
    # O valor que não se aplica é gravado como nulo: NaN não é JSON válido.
    records = statistics.astype(object).where(statistics.notna(), None).to_dict(orient="records")
    metrics = {"fig9_statistics": records, "flows": len(flows)}
    run_dir = save_run(
        experiment="e7",
        track="dados",
        slice_name="fig9",
        seed=SEED_FIEL,
        metrics=metrics,
        config={"cleaning": CLEANING, "bins": FIG9_BINS, "panels": FIG9_PANELS},
        data_sha256=data_sha256,
        timings={"total_seconds": round(time.perf_counter() - start, 1)},
        results_dir=results_dir,
    )
    # A imagem depende da versão da biblioteca e das fontes da máquina. As
    # curvas vão também em CSV, com seis algarismos significativos: é esse
    # arquivo que duas execuções comparam.
    curves.to_csv(run_dir / "fig9_curvas.csv", index=False, float_format="%.6g")
    statistics.to_csv(run_dir / "fig9_estatisticas.csv", index=False, float_format="%.6g")
    # Sem o campo com a versão da biblioteca, a imagem só muda se o desenho mudar.
    figure = draw_fig9(curves, statistics)
    figure.savefig(run_dir / "fig9_distribuicao.png", dpi=150, metadata={"Software": None})
    return run_dir, metrics


def matrix_table(confusion: list[list[int]], roles: list[str]) -> str:
    """Escreve uma matriz de confusão em Markdown, com o nome das ferramentas."""
    index = pd.Index(roles, name="real \\ predito")
    return frame_markdown_table(pd.DataFrame(confusion, index=index, columns=roles))


def comparison_table(comparison: dict) -> str:
    """Escreve o valor do artigo de cada ferramenta ao lado das métricas obtidas no teste."""
    rows = []
    for tool, entry in comparison.items():
        row = [tool, f"{entry['article_accuracy']:.1%}", entry["support"]]
        for metric, _ in METRIC_TITLES:
            row += [f"{entry[metric]:.2%}", f"{entry['difference_pp'][metric]:+.2f}"]
        rows.append(row)
    columns = ["ferramenta", 'artigo ("accuracy")', "fluxos no teste"]
    for _, title in METRIC_TITLES:
        columns += [title, f"{title} menos artigo (pp)"]
    return frame_markdown_table(pd.DataFrame(rows, columns=columns).set_index(columns[0]))


def tool_lines(test: dict, roles: list[str]) -> str:
    """Escreve, para cada ferramenta, quantos fluxos do teste foram para outra e para qual."""
    lines = []
    for code, tool in enumerate(roles):
        row = test["confusion_matrix"][code]
        others = {roles[other]: count for other, count in enumerate(row) if other != code}
        missed = ", ".join(f"{count} a {name}" for name, count in others.items())
        entry = test["per_class"][tool]
        lines.append(
            f"- **{tool}: recall {entry['recall']:.2%}, precisão {entry['precision']:.2%}.** "
            f"Fluxos de {tool} no teste: {entry['support']}; atribuídos a outra ferramenta: "
            f"{sum(others.values())} ({missed})."
        )
    lines.append(
        "\nO erro aqui é de atribuição: quem investiga o alerta parte da ferramenta errada. "
        "A detecção do túnel não é medida, porque todos os fluxos do conjunto são maliciosos."
    )
    return "\n".join(lines)


def never_predicted_text(confusion: list[list[int]], roles: list[str]) -> str:
    """Escreve o aviso sobre as ferramentas que o modelo não prediz em nenhuma linha.

    Devolve texto vazio quando todas são preditas ao menos uma vez.
    """
    never = [name for code, name in enumerate(roles) if not any(row[code] for row in confusion)]
    if not never:
        return ""
    return (
        f"O modelo não prediz {' nem '.join(never)} em nenhuma linha do teste. A precisão de "
        "uma classe sem predição é indefinida e entra como 0 na média macro."
    )


def subsets_table(metrics: dict) -> str:
    """Escreve as contagens por ferramenta e a fração sintética de cada subconjunto."""
    rows = [
        [entry["class_counts"], f"{entry['synthetic_fraction_of_resampled']:.2%}"]
        for entry in metrics["subsets"]
    ]
    resampled = metrics["roles"]["resampled"]
    columns = ["amostras por ferramenta", f"{resampled} sintético"]
    index = pd.RangeIndex(1, len(rows) + 1, name="subconjunto")
    return frame_markdown_table(pd.DataFrame(rows, columns=columns, index=index))


def reading_text(reading: dict, metrics: dict) -> str:
    """Monta a seção do RESUMO.md de uma leitura de profundidade."""
    test, roles = metrics["test"], metrics["classes"]
    seen = metrics["test_seen_in_train"]
    bases = "; ".join(
        ", ".join(f"{tool} {base['per_class'][tool]['recall']:.2%}" for tool in roles)
        for base in metrics["base_models_test"]
    )
    run_dir = f"{reading['track']}/{SCENARIO}/seed{SEED_FIEL}"
    return f"""## Leitura {reading["label"]}

Random Forests base: {reading["base_depth"]}. Números em `{run_dir}/metrics.json`;
tempos em `{run_dir}/run.json`.

Matriz de confusão no teste ({test["total"]} fluxos; linha é a ferramenta real):

{matrix_table(test["confusion_matrix"], roles)}

Ao lado da Seção VI-D do artigo:

{comparison_table(metrics["article_comparison"])}

Acurácia no teste: {test["accuracy"]:.2%}. Recall macro {test["macro_recall"]:.2%}, precisão
macro {test["macro_precision"]:.2%}, F1 macro {test["macro_f1"]:.2%}; F1 ponderado
{test["weighted_f1"]:.2%}. AUC-ROC one-vs-rest macro: {test["roc_auc_ovr_macro"]:.6f} pela saída do
meta-classificador e {test["roc_auc_ovr_macro_base_mean"]:.6f} pela média das probabilidades
dos bases.

{tool_lines(test, roles)}

{never_predicted_text(test["confusion_matrix"], roles)}

Recall de cada Random Forest base sozinho no teste, na ordem dos subconjuntos:
{bases}.

Subconjuntos de treino (ferramentas na ordem {", ".join(roles)}):

{subsets_table(metrics)}

{seen["total"]} das {test["total"]} linhas do teste ({seen["fraction_total"]:.2%}) têm vetor de
{len(FEATURE_COLUMNS)} atributos idêntico ao de alguma linha do treino. Para o modelo essas
linhas já foram vistas, e as métricas acima as incluem.
"""


def fig9_text(fig9: dict) -> str:
    """Monta a seção do RESUMO.md sobre a figura equivalente à Fig. 9."""
    statistics = pd.DataFrame(fig9["fig9_statistics"])
    panels = "\n".join(
        f"- ({letter}) `{column}` ({unit}), eixo de {low} a {high}."
        for letter, (column, unit, low, high) in zip("ab", FIG9_PANELS, strict=True)
    )
    lowest = "\n".join(
        f"- `{column}`: o menor desvio padrão é o de "
        f"{panel.loc[panel['desvio padrão'].idxmin(), 'ferramenta']}."
        for column, panel in statistics.groupby("atributo", sort=False)
    )
    sentinel = statistics.dropna(subset="fração com -10")
    marker = ", ".join(
        f"{row['ferramenta']} {row['fração com -10']:.2%}" for _, row in sentinel.iterrows()
    )
    table = statistics.copy()
    for column in ["fração no eixo", "fração com -10"]:
        table[column] = table[column].map(lambda value: "–" if pd.isna(value) else f"{value:.2%}")
    for column in ["média", "desvio padrão"]:
        table[column] = table[column].map(lambda value: f"{value:.6g}")
    run_dir = f"dados/fig9/seed{SEED_FIEL}"
    return f"""## Figura equivalente à Fig. 9

`{run_dir}/fig9_distribuicao.png`, com os dados em `{run_dir}/fig9_curvas.csv` e
`{run_dir}/fig9_estatisticas.csv`. Os mesmos dois atributos da figura do artigo:

{panels}

A Fig. 9 do artigo desenha, para cada ferramenta, uma curva normal com a média e
o desvio padrão escritos na legenda. A linha de cima da nossa figura repete esse
tipo de gráfico com a média e o desvio padrão medidos; a de baixo mostra o
histograma dos mesmos fluxos, em {FIG9_BINS} intervalos. O eixo vertical do artigo é
"Frequency", sem dizer a escala; o nosso é densidade, e a altura das curvas não
é comparável à do artigo. A figura descreve os dados e usa todos os
{fig9["flows"]} fluxos limpos, do treino e do teste; nenhum modelo é ajustado com ela.

{frame_markdown_table(table.set_index("atributo"))}

O artigo afirma que o dns2tcp tem desvio padrão menor nos dois atributos. Medido:

{lowest}

`{sentinel["atributo"].iloc[0]}` é uma coluna de assimetria, em que o extrator grava
{SKEW_SENTINEL} quando o desvio padrão do fluxo é zero. Fração dos fluxos com esse marcador:
{marker}. O marcador entra na média e no desvio padrão da tabela, como
qualquer outro valor.
"""


def summary_text(counts: dict, results: list[tuple[dict, dict]], fig9: dict) -> str:
    """Monta o RESUMO.md a partir dos números medidos na execução.

    `results` tem um par (leitura, métricas) por execução; `fig9` é o
    dicionário gravado pela etapa da figura.
    """
    first = results[0][1]
    roles = first["roles"]
    rows = pd.DataFrame(counts).rename(
        columns={"raw_rows_by_tool": "fluxos no zip", "clean_rows_by_tool": "depois da limpeza"}
    )
    rows["treino"] = pd.Series(first["train_rows"], index=first["classes"])
    rows["teste"] = pd.Series(first["test_rows"], index=first["classes"])
    rows.index.name = "ferramenta"
    readings = "\n".join(reading_text(reading, metrics) for reading, metrics in results)
    article = ", ".join(f"{tool} {value:.1%}" for tool, value in SECTION_VI_D_ACCURACY.items())
    return f"""# E7: identificação da ferramenta de túnel (Seção VI-D e Fig. 9 do artigo)

Gerado por `scripts/e7_ferramenta.py`. Uma única execução de cada leitura, com a
seed {SEED_FIEL}: não há média nem desvio padrão.

## O método é leitura nossa

A Seção VI-D do artigo diz que o sistema identificou a ferramenta de túnel que
gerou o tráfego malicioso e dá um valor por ferramenta, que chama de
"accuracy": {article}. O artigo não diz que modelo produziu esses valores, com
que dados foi treinado, como o teste foi separado nem como a "accuracy" de uma
ferramenta foi calculada. Sem método descrito, o que se faz aqui é uma leitura:

- o mesmo sistema da reprodução ({1 - TEST_SIZE:.0%} para treino e {TEST_SIZE:.0%} para teste, com a
  mesma proporção de ferramentas; normalizador ajustado só no treino; {N_SUBSETS}
  subconjuntos; {N_SUBSETS} Random Forests de {N_ESTIMATORS} árvores; regressão logística),
  aplicado só aos fluxos maliciosos, com as três ferramentas como classes;
- nos subconjuntos, a ferramenta com mais fluxos no treino ({roles["split_in_three"]}) é
  dividida em {N_SUBSETS} partes, a com menos ({roles["resampled"]}) é aumentada com SMOTE até o
  tamanho da terceira ({roles["reference"]}), que entra inteira em cada subconjunto. É o
  que o sistema do artigo faz com Non-DoH, Benign-DoH e Malicious-DoH;
- o valor do artigo de cada ferramenta fica ao lado do recall, da precisão e do
  F1 dela, porque não se sabe a qual deles a "accuracy" corresponde. As classes
  são desbalanceadas, e a acurácia do conjunto sozinha mediria sobretudo o
  {roles["split_in_three"]}.

O sistema é treinado nas duas leituras de profundidade do artigo. A principal
é a de profundidade variável (linha 3 do Algoritmo 1); a de profundidade máxima
{MAX_DEPTH} (Seção IV-B) vai ao lado.

## Dados

Fluxos de `MaliciousDoH-CSVs.zip` com a coluna `DoH` verdadeira; a ferramenta é
a pasta do arquivo. Limpeza: saem as linhas com valor ausente em algum
atributo, como na reprodução. O total depois da limpeza é o Malicious-DoH da
Tabela I do artigo ({fig9["flows"]}).

{frame_markdown_table(rows)}

{readings}
{fig9_text(fig9)}
## O que não foi feito

- Validação cruzada: o artigo não mostra matriz de confusão para a Seção VI-D,
  e as métricas acima vêm só do teste.
- Outro classificador ou outro split: só a leitura descrita acima foi medida.
- Detecção: o conjunto só tem tráfego malicioso, então nada aqui mede falso
  positivo sobre tráfego legítimo.

## Onde os valores diferem dos do artigo

O artigo não informa o modelo, os dados de treino, o split, a seed nem a
definição de "accuracy" por ferramenta; as versões das bibliotecas são outras.
Qualquer um desses pontos pode explicar a diferença, e os dados não permitem
dizer qual. Nenhuma seed, hiperparâmetro, papel de ferramenta ou regra de
limpeza foi ajustado para aproximar o resultado.
"""


def main() -> None:
    """Confere os dados, roda as duas leituras e a figura e grava o resumo."""
    data_sha256 = checked_sha256()
    flows, counts = load_clean_flows()

    results = []
    for reading in READINGS:
        run_dir, metrics = run_experiment(flows, data_sha256, RESULTS_DIR, reading)
        results.append((reading, metrics))
        print(f"\n== {reading['label']} ==")
        print(matrix_table(metrics["test"]["confusion_matrix"], metrics["classes"]))
        print(comparison_table(metrics["article_comparison"]))
        print(f"Acurácia no teste: {metrics['test']['accuracy']:.4%}")
        timings = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["timings"]
        print(f"Tempos, em segundos: {timings}")
        print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}")

    run_dir, fig9 = run_fig9(flows, data_sha256, RESULTS_DIR)
    print(f"\nFigura equivalente à Fig. 9 em {run_dir.relative_to(PROJECT_ROOT)}")
    summary = summary_text(counts, results, fig9)
    (RESULTS_DIR / "e7" / "RESUMO.md").write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
