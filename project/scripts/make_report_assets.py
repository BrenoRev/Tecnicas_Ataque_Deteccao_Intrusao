r"""Tabelas e figuras do relatório e dos slides, geradas a partir de results/.

Não treina nada e não altera results/. Lê os metrics.json, run.json e
summary.json e os CSV das figuras gravados pelos scripts dos experimentos, mais
os valores do artigo transcritos em config.py, e escreve:

- report/tables/<nome>.tex: ambiente tabular, sem o table em volta, para \input
  no IEEEtran; números com vírgula decimal e linhas com \hline.
- report/tables/<nome>.csv: as mesmas células, com ponto decimal.
- report/figures/<nome>.pdf (vetorial, para o LaTeX) e <nome>.png (para os slides).
- report/INDICE.md: cada arquivo, os resultados de onde veio e a legenda sugerida.

O sufixo _dupla no nome marca a tabela ou figura que precisa da largura da
página (table* ou figure*); as outras cabem em uma coluna.

Nenhum número é digitado aqui. O script falha se faltar resultado obrigatório
(dados, reprodução, modelos de comparação, explicabilidade, segundo dataset e
ferramenta de túnel). Sensibilidade, protocolo corrigido, modificação e robustez
são opcionais: o que faltar é listado na saída como "não gerado".

Uso: uv run python scripts/make_report_assets.py
"""

import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure

from doh_ids.config import (
    ARTICLE_DURATION_THRESHOLD_SECONDS,
    BASE_RATE_FLOWS,
    CLASS_NAMES,
    CORRIGIDA_MODELS,
    CV_FOLDS,
    FIG2_PANELS,
    FIG4A_CONFUSION,
    FIG4B_CONFUSION,
    FIG5_RANKING,
    FIG9_PANELS,
    MAX_DEPTH,
    MODIFIED_SELECTED_MODEL,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    SHAP_TOP_FEATURES,
    TABLE_II_LITERATURE,
    TOOL_ORIGIN,
)
from doh_ids.evaluate import metrics_from_confusion

REPORT_DIR = PROJECT_ROOT / "report"

# As duas leituras da profundidade dos Random Forests base: a trilha fiel usa a
# profundidade máxima 5 (Seção IV-B do artigo) e a trilha variante, a
# profundidade variável (linha 3 do Algoritmo 1). O rótulo identifica a leitura
# em toda tabela e figura que mostra as duas.
READINGS = {"fiel": "prof. 5", "variante": "prof. variável"}
# Forma curta, para o cabeçalho das colunas.
READING_HEADERS = {"fiel": "Prof. 5", "variante": "Prof. var."}
# Recorte da reprodução e da explicabilidade em cada trilha.
SYSTEM_SLICES = {"fiel": "proposto", "variante": "profundidade_variavel"}
BASELINES = {
    "decision_tree": "Decision Tree",
    "xgboost": "XGBoost",
    "random_forest": "Random Forest",
}
SECOND_DATASET = "Combinado sem réplicas"
CV_TITLE = f"na validação cruzada de {CV_FOLDS} folds sobre o treino"
DATASET_TITLES = {"cira": "CIRA", "combinado_sem_replicas": SECOND_DATASET}

# Linhas das tabelas de métricas: as três métricas de cada classe primeiro, com
# Benign-DoH (a classe menor) à frente, e as médias depois, cada uma com o nome.
CLASS_ORDER = ["Benign-DoH", "Malicious-DoH", "Non-DoH"]
CLASS_METRICS = {"precision": "precisão", "recall": "recall", "f1": "F1"}
AVERAGES = {
    "accuracy": "Acurácia",
    "macro_precision": "Precisão macro",
    "macro_recall": "Recall macro",
    "macro_f1": "F1 macro",
    "weighted_f1": "F1 ponderado",
}
FPR_LABEL = "Malicious-DoH: FPR"
# Chave de cada linha nos resumos de dez seeds, que achatam classe e métrica.
SUMMARY_KEYS = {
    f"{name}: {label}": f"{name.lower().replace('-', '_')}_{key}"
    for name in CLASS_ORDER
    for key, label in CLASS_METRICS.items()
}
SUMMARY_KEYS[FPR_LABEL] = "malicious_fpr"
SUMMARY_KEYS.update({label: key for key, label in AVERAGES.items()})
KEY_LABELS = {key: label for label, key in SUMMARY_KEYS.items()}
# Subconjunto usado nas tabelas que comparam muitos modelos lado a lado.
KEY_METRICS = [
    "Benign-DoH: precisão",
    "Benign-DoH: recall",
    "Benign-DoH: F1",
    "Malicious-DoH: recall",
    FPR_LABEL,
    "F1 macro",
]

# Casas decimais. Os percentuais levam duas; a taxa de falsos positivos leva
# quatro, porque com duas os valores medidos, da ordem de 0,001%, viram zero.
DECIMALS = 2
FPR_DECIMALS = 4
# A metade inferior da Tabela II é copiada como impressa, com até quatro casas
# em percentual, sem zeros à direita.
LITERATURE_DECIMALS = 4
MISSING = "–"

MACRO_NAMED = "médias macro e ponderada nomeadas na tabela"
NO_AVERAGE = "sem média agregada"

# Largura de uma coluna e da página do IEEEtran, em polegadas.
COLUMN_WIDTH = 3.46
PAGE_WIDTH = 7.16
PNG_DPI = 300
FIGURE_STYLE = {
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "lines.linewidth": 1.2,
}
# Sem a data de criação, o mesmo resultado gera o mesmo arquivo.
FIGURE_METADATA = {"pdf": {"CreationDate": None}, "png": {"Software": None}}
# Paleta de Okabe e Ito, distinguível por quem tem daltonismo.
CLASS_COLORS = {"Non-DoH": "#0072B2", "Benign-DoH": "#009E73", "Malicious-DoH": "#D55E00"}
SERIES_COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]

# Símbolos trocados no .tex, que não carrega pacote além dos do template.
TEX_SYMBOLS = {
    "&": r"\&",
    "%": r"\%",
    "_": r"\_",
    "±": r"$\pm$",
    "–": "--",
    "−": "$-$",
    "Σ": r"$\Sigma$",
    "|": "$|$",
    "→": r"$\rightarrow$",
    "²": "$^2$",
}


class Num(str):
    """Célula numérica: texto com ponto decimal, que no .tex vira vírgula."""


@dataclass
class Table:
    """Tabela do relatório: células, legenda sugerida e arquivos de origem.

    `rows` aceita `None` para uma linha horizontal entre blocos. `groups` é a
    linha de cima de um cabeçalho de dois níveis: rótulo e número de colunas.
    `tracks` lista as trilhas dos modelos da tabela; vazio em tabela de dados
    ou de literatura.
    """

    name: str
    header: list[str]
    rows: list[list[str] | None]
    caption: str
    source: str
    tracks: tuple[str, ...] = ()
    groups: list[tuple[str, int]] | None = None


@dataclass
class Plot:
    """Figura do relatório: o desenho, a legenda sugerida e os arquivos de origem."""

    name: str
    figure: Figure
    caption: str
    source: str


# Células.


def num(value: float, decimals: int = DECIMALS) -> Num:
    """Escreve um número com casas fixas."""
    # Somar zero troca o zero negativo que o arredondamento produz por zero.
    return Num(f"{round(value, decimals) + 0.0:.{decimals}f}")


def count(value: float) -> Num:
    """Escreve uma contagem."""
    return Num(str(int(value)))


def signed(value: float, decimals: int = DECIMALS) -> Num:
    """Escreve uma diferença, com o sinal; a diferença nula sai sem sinal."""
    rounded = round(value, decimals)
    return num(rounded, decimals) if rounded == 0 else Num(f"{rounded:+.{decimals}f}")


def decimals_for(label: str) -> int:
    """Casas decimais da métrica da linha: quatro na taxa de falsos positivos."""
    return FPR_DECIMALS if "FPR" in label else DECIMALS


def percent(label: str, fraction: float) -> Num:
    """Escreve em percentual uma métrica que é fração entre 0 e 1."""
    return num(100 * fraction, decimals_for(label))


def percent_points(label: str, obtained: float, reference: float) -> Num:
    """Escreve a diferença entre duas frações em pontos percentuais."""
    return signed(100 * (obtained - reference), decimals_for(label))


def mean_std(statistic: dict, scale: float = 100.0, decimals: int = DECIMALS) -> Num:
    """Escreve média ± desvio padrão de um resumo de seeds."""
    mean, std = num(scale * statistic["mean"], decimals), num(scale * statistic["std"], decimals)
    return Num(f"{mean} ± {std}")


def count_row(label: str, counts: list[int]) -> list[str]:
    """Linha de contagens por classe, com o total na última coluna."""
    return [label, *map(count, counts), count(sum(counts))]


# Leitura de results/.


def read_json(path: Path) -> dict:
    """Lê um arquivo JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def run_dir(results_dir: Path, experiment: str, track: str, run_slice: str, seed: int) -> Path:
    """Pasta de uma execução, no layout experimento/trilha/recorte/seed."""
    return results_dir / experiment / track / run_slice / f"seed{seed}"


def load_log(
    results_dir: Path, experiment: str, track: str, run_slice: str, seed: int = SEED_FIEL
) -> dict:
    """Lê o run.json de uma execução e confere que a trilha gravada é a pedida."""
    log = read_json(run_dir(results_dir, experiment, track, run_slice, seed) / "run.json")
    # Trilhas diferentes só aparecem juntas em tabela que as identifica: a
    # execução lida tem de ser da trilha que a tabela vai nomear.
    if log["track"] != track:
        raise ValueError(
            f"{experiment}/{track}/{run_slice}: o run.json registra a trilha {log['track']}"
        )
    return log


def load_run(
    results_dir: Path, experiment: str, track: str, run_slice: str, seed: int = SEED_FIEL
) -> dict:
    """Lê o metrics.json de uma execução, depois de conferir a trilha."""
    load_log(results_dir, experiment, track, run_slice, seed)
    return read_json(run_dir(results_dir, experiment, track, run_slice, seed) / "metrics.json")


def both_readings(results_dir: Path, experiment: str, slices: dict[str, str] | str) -> dict:
    """Lê a mesma execução nas duas leituras de profundidade, pela trilha.

    `slices` é o recorte de cada trilha, ou um só nome quando é o mesmo nas duas.
    """
    if isinstance(slices, str):
        slices = dict.fromkeys(READINGS, slices)
    return {track: load_run(results_dir, experiment, track, slices[track]) for track in READINGS}


def metric_values(evaluation: dict) -> dict[str, float]:
    """Métricas de uma avaliação pelo rótulo da linha: por classe e depois as médias."""
    values = {
        f"{name}: {label}": evaluation["per_class"][name][key]
        for name in CLASS_ORDER
        for key, label in CLASS_METRICS.items()
    }
    values[FPR_LABEL] = evaluation["malicious_vs_rest"]["fpr"]
    values.update({label: evaluation[key] for key, label in AVERAGES.items()})
    return values


def tool_recalls(metrics: dict) -> dict:
    """Recall de Malicious-DoH por ferramenta de túnel, na transferência ou no retreino."""
    return metrics["hkd"]["by_tool"] if "hkd" in metrics else metrics["test_recall_by_tool"]


def model_caption(text: str, tracks: tuple[str, ...], seeds: str, average: str) -> str:
    """Legenda de tabela de modelo: o texto, a trilha, as seeds e o nome da média."""
    plural = "s" if len(tracks) > 1 else ""
    return f"{text} Trilha{plural} {' e '.join(tracks)}; {seeds}; {average}."


def ten_seeds(seeds: list[int]) -> str:
    """Descreve as seeds de um resumo, para a legenda."""
    return f"{len(seeds)} seeds ({seeds[0]} a {seeds[-1]}), média ± desvio padrão amostral"


def model_description(name: str, config: dict) -> str:
    """Descreve um modelo do protocolo corrigido pelos hiperparâmetros gravados no resumo."""
    kind = "empilhado de três Random Forests" if config["stacked"] else "Random Forest único"
    if "n_estimators" not in config:
        return f"{name}: {kind}, hiperparâmetros {config['hyperparameters']}"
    depth = "variável" if config["max_depth"] is None else config["max_depth"]
    return (
        f"{name}: {kind}, {config['n_estimators']} árvores, profundidade {depth}, "
        f"{config['max_features']} atributos por divisão"
    )


# Tabelas de dados.

SINGLE_SEED = f"seed {SEED_FIEL}"
E0_RUN = Path("e0") / "dados" / "cira" / f"seed{SEED_FIEL}"


def split_rows(prefix: str, split: dict) -> list[list[str]]:
    """Linhas de treino, fold de validação e teste de um split gravado em results/."""
    folds = split["validation_folds"]["validation_rows"]
    # Os folds diferem em poucos fluxos: a linha mostra o menor de cada coluna.
    columns = [*zip(*folds, strict=True), [sum(fold) for fold in folds]]
    return [
        count_row(f"{prefix}treino", split["train"]["rows"]),
        [f"{prefix}validação", *(count(min(column)) for column in columns)],
        count_row(f"{prefix}teste", split["test"]["rows"]),
    ]


def folds_text(split: dict) -> str:
    """Descreve os folds de validação e quanto o tamanho deles varia, para a legenda."""
    folds = split["validation_folds"]
    spread = max(
        max(column) - min(column) for column in zip(*folds["validation_rows"], strict=True)
    )
    return (
        f"A linha de validação é o menor dos {folds['n_folds']} folds da validação cruzada "
        f"sobre o treino, que diferem em no máximo {spread} fluxo por classe."
    )


def cira_counts_table(results_dir: Path) -> list[Table]:
    """Fluxos por classe do CIRA: bruto, limpo, Tabela I, treino, folds e teste."""
    data = read_json(results_dir / E0_RUN / "metrics.json")
    split = read_json(results_dir / E0_RUN / "split_counts.json")
    difference = [
        ours - article for ours, article in zip(data["clean_rows"], data["table_i"], strict=True)
    ]
    rows = [
        count_row("Bruto", data["raw_rows"]),
        count_row("Limpo", data["clean_rows"]),
        count_row("Tabela I", data["table_i"]),
        ["Limpo − Tabela I", *(signed(value, 0) for value in [*difference, sum(difference)])],
        None,
        *split_rows("Reprodução: ", split),
        None,
        count_row("Artigo: treino", split["train"]["fig4a"]),
        count_row("Artigo: teste", split["test"]["fig4b"]),
    ]
    caption = (
        "Fluxos por classe do CIRA-CIC-DoHBrw-2020. A limpeza remove as linhas com "
        f"valor ausente (regra {data['adopted_rule']}). Split estratificado com "
        f"{split['test_size']:.0%} para teste, seed {split['seed']}. {folds_text(split)} As "
        "contagens do artigo são as somas das linhas das matrizes da Fig. 4a (treino) e da "
        "Fig. 4b (teste)."
    )
    source = f"results/{E0_RUN}/metrics.json, split_counts.json"
    return [
        Table("dados_cira_contagens", ["Conjunto", *CLASS_NAMES, "Total"], rows, caption, source)
    ]


def capture_table(results_dir: Path) -> list[Table]:
    """Máquinas e período de captura de cada classe do CIRA."""
    data = read_json(results_dir / E0_RUN / "metrics.json")
    rows = [
        [
            entry["classe"],
            count(entry["máquinas"]),
            count(entry["dias"]),
            entry["primeiro dia"],
            entry["último dia"],
        ]
        for entry in data["capture_by_class"]
    ]
    caption = (
        "Máquinas e período de captura de cada classe do CIRA-CIC-DoHBrw-2020. Máquinas em "
        f"comum entre Malicious-DoH e as outras classes: {data['machines_shared_with_malicious']}; "
        f"dias em comum: {data['days_shared_with_malicious']}."
    )
    header = ["Classe", "Máquinas", "Dias", "Primeiro dia", "Último dia"]
    source = f"results/{E0_RUN}/metrics.json"
    return [Table("dados_cira_captura", header, rows, caption, source)]


E6_DATA_SOURCE = (
    "results/e6/dados/{combinado,combinado_sem_replicas,hkd}/seed42/metrics.json; "
    "results/e6/fiel/retreino_{publicado,sem_replicas}/seed42/metrics.json"
)
# As duas formas do combinado: nome do dataset, cenário de retreino e título.
COMBINED_FORMS = [
    ("combinado", "retreino_publicado", "Publicado"),
    ("combinado_sem_replicas", "retreino_sem_replicas", "Sem réplicas"),
]


def second_dataset_counts_table(results_dir: Path) -> list[Table]:
    """Fluxos por classe do segundo dataset, nas duas formas do combinado e no HKD isolado."""
    rows = []
    for name, scenario, title in COMBINED_FORMS:
        data = load_run(results_dir, "e6", "dados", name)
        split = load_run(results_dir, "e6", "fiel", scenario)["split"]
        rows += [
            count_row(f"{title}: limpo", data["clean_rows"]),
            count_row(f"{title}: só HKD", data["clean_rows_by_origin"]["HKD"]),
            *split_rows(f"{title}: ", split),
            None,
        ]
    hkd = load_run(results_dir, "e6", "dados", "hkd")
    rows.append(count_row("HKD isolado: teste", hkd["clean_rows"]))
    unique = load_run(results_dir, "e6", "dados", "combinado_sem_replicas")
    caption = (
        "Fluxos por classe do segundo dataset: o combinado CIRA + DoH-Tunnel-Traffic-HKD como "
        f"publicado, em que cada fluxo do HKD aparece {hkd['augmented_file']['copies_per_flow']} "
        f"vezes, e sem as réplicas ({unique['replicas_removed']} linhas removidas). Non-DoH e "
        f"Benign-DoH são os do CIRA. Split estratificado, seed {SEED_FIEL}. {folds_text(split)} "
        "O HKD isolado só tem a classe maliciosa e serve apenas de teste na transferência."
    )
    header = ["Conjunto", *CLASS_NAMES, "Total"]
    return [Table("dados_segundo_contagens", header, rows, caption, E6_DATA_SOURCE)]


def second_dataset_tools_table(results_dir: Path) -> list[Table]:
    """Fluxos Malicious-DoH por ferramenta de túnel no segundo dataset."""
    published = load_run(results_dir, "e6", "dados", "combinado")["clean_rows_by_tool"]
    unique = load_run(results_dir, "e6", "dados", "combinado_sem_replicas")["clean_rows_by_tool"]
    hkd = load_run(results_dir, "e6", "dados", "hkd")["clean_rows_by_tool"]
    split = load_run(results_dir, "e6", "fiel", "retreino_sem_replicas")["split"]
    rows = [
        [tool, origin, count(published[tool]), count(unique[tool])]
        + [count(split[part]["rows_by_tool"][tool]) for part in ["train", "test"]]
        + [count(hkd[tool])]
        for tool, origin in TOOL_ORIGIN.items()
    ]
    caption = (
        "Fluxos Malicious-DoH por ferramenta de túnel, depois da limpeza: no combinado "
        "publicado, no combinado sem réplicas (total, treino e teste) e no HKD isolado, que é "
        "o conjunto de teste da transferência."
    )
    header = ["Ferramenta", "Origem", "Publicado", "Limpo", "Treino", "Teste", "HKD isolado"]
    table = Table("dados_segundo_ferramentas", header, rows, caption, E6_DATA_SOURCE)
    table.groups = [("", 2), ("", 1), ("Sem réplicas", 3), ("Transferência", 1)]
    return [table]


# Reprodução.


E1_SOURCE = "results/e1/{fiel/proposto,variante/profundidade_variavel}/seed42/metrics.json"
# Cabeçalho de dois níveis das matrizes de confusão: as colunas são a classe predita.
PREDICTED_GROUPS = [("", 2), ("Classe predita", len(CLASS_NAMES))]


def confusion_block(label: str, matrix: list[list[int]], cell=count) -> list[list[str]]:
    """Três linhas de uma matriz de confusão: a fonte, a classe real e as contagens."""
    return [[label, name, *map(cell, row)] for name, row in zip(CLASS_NAMES, matrix, strict=True)]


def confusion_table(results_dir: Path, name: str, figure_key: str, title: str) -> Table:
    """Matriz de confusão do artigo ao lado das duas leituras, com a diferença por célula.

    `figure_key` é `fig4a` (validação cruzada) ou `fig4b` (teste), como nas
    chaves de comparação gravadas pela reprodução.
    """
    runs = both_readings(results_dir, "e1", SYSTEM_SLICES)
    first = next(iter(runs.values()))[f"{figure_key}_comparison"]
    article = f"Artigo (Fig. 4{figure_key[-1]})"
    rows = confusion_block(article, first[figure_key])
    sums = []
    for track, metrics in runs.items():
        comparison = metrics[f"{figure_key}_comparison"]
        evaluation = metrics["cross_validation" if figure_key == "fig4a" else "test"]
        reading = READING_HEADERS[track]
        rows.append(None)
        rows += confusion_block(reading, evaluation["confusion_matrix"])
        rows += confusion_block(
            f"{reading} − artigo", comparison["cell_difference"], lambda v: signed(v, 0)
        )
        sums.append(f"{comparison['absolute_difference_sum']} ({READINGS[track]})")
    caption = model_caption(
        f"Matriz de confusão {title}: artigo, reprodução nas duas leituras de profundidade dos "
        "Random Forests base e diferença célula a célula. Linha é a classe real e coluna a "
        f"classe predita. Soma das diferenças absolutas: {' e '.join(sums)}.",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    table = Table(name, ["Fonte", "Classe real", *CLASS_NAMES], rows, caption, E1_SOURCE)
    table.tracks, table.groups = tuple(READINGS), PREDICTED_GROUPS
    return table


def confusion_tables(results_dir: Path) -> list[Table]:
    """Tabelas equivalentes à Fig. 4b (teste) e à Fig. 4a (validação cruzada)."""
    return [
        confusion_table(results_dir, "reproducao_matriz_teste", "fig4b", "no teste"),
        confusion_table(
            results_dir,
            "reproducao_matriz_validacao",
            "fig4a",
            CV_TITLE,
        ),
    ]


def reproduction_metrics_table(results_dir: Path) -> list[Table]:
    """Métricas por classe e médias no teste: Fig. 4b do artigo e as duas leituras."""
    runs = both_readings(results_dir, "e1", SYSTEM_SLICES)
    article = metric_values(metrics_from_confusion(FIG4B_CONFUSION))
    ours = {track: metric_values(metrics["test"]) for track, metrics in runs.items()}
    rows = []
    for label, reference in article.items():
        if label == AVERAGES["accuracy"]:
            rows.append(None)
        row = [label, percent(label, reference)]
        for track in READINGS:
            row += [
                percent(label, ours[track][label]),
                percent_points(label, ours[track][label], reference),
            ]
        rows.append(row)
    header = ["Métrica", "Artigo"]
    for reading in READING_HEADERS.values():
        header += [reading, "Dif."]
    caption = model_caption(
        "Métricas no teste do CIRA-CIC-DoHBrw-2020, em %: valores calculados da matriz da "
        "Fig. 4b do artigo, reprodução nas duas leituras de profundidade e diferença em pontos "
        "percentuais. FPR é a taxa de falsos positivos de Malicious-DoH contra o resto.",
        tuple(READINGS),
        SINGLE_SEED,
        MACRO_NAMED,
    )
    source = E1_SOURCE
    return [Table("reproducao_metricas", header, rows, caption, source, tuple(READINGS))]


def table_ii_rows(results_dir: Path) -> list[tuple[str, dict]]:
    """Modelos da metade superior da Tabela II, com a comparação gravada em results/."""
    rows = [
        (title, load_run(results_dir, "e2", "fiel", model)["table_ii_comparison"])
        for model, title in BASELINES.items()
    ]
    runs = both_readings(results_dir, "e1", SYSTEM_SLICES)
    rows += [
        (f"Proposto, {READINGS[track]}", metrics["table_ii_comparison"])
        for track, metrics in runs.items()
    ]
    return rows


def table_ii_table(results_dir: Path, average: str, average_title: str, short_title: str) -> Table:
    """Metade superior da Tabela II: artigo, reprodução e diferença, com uma média nomeada.

    `average` é o prefixo da média nas chaves de results/; `average_title` e
    `short_title` são o nome dela na legenda e no cabeçalho da coluna.
    """
    obtained_key = {
        "auc": "roc_auc_ovr_macro",
        "accuracy": "accuracy",
        "f1": f"{average}_f1",
        "precision": f"{average}_precision",
        "recall": f"{average}_recall",
    }
    titles = {
        "auc": "AUC",
        "accuracy": "Acurácia",
        "f1": "F1",
        "precision": "Precisão",
        "recall": "Recall",
    }
    rows = []
    for title, comparison in table_ii_rows(results_dir):
        row = [title]
        for metric, key in obtained_key.items():
            entry = comparison[metric]
            row += [
                num(100 * entry["table_ii"]),
                num(100 * entry["obtained"][key]),
                signed(entry["difference_pp"][key]),
            ]
        rows.append(row)
    caption = model_caption(
        f"Metade superior da Tabela II do artigo ao lado da reprodução, em %, com a média "
        f"{average_title} em F1, precisão e recall (o artigo não diz que média usa) e a "
        "diferença em pontos percentuais. A AUC reproduzida é a um-contra-o-resto com média "
        "macro. O modelo proposto aparece nas duas leituras de profundidade; os três modelos "
        "de comparação são da trilha fiel.",
        tuple(READINGS),
        SINGLE_SEED,
        f"média {average_title}",
    )
    source = (
        "results/e2/fiel/{decision_tree,xgboost,random_forest}/seed42/metrics.json; "
        "results/e1/{fiel/proposto,variante/profundidade_variavel}/seed42/metrics.json"
    )
    # Na coluna reproduzida, AUC e acurácia não têm média; as outras levam o nome dela.
    header = ["Modelo"]
    for metric in titles:
        named = metric in ("f1", "precision", "recall")
        header += ["Art.", short_title if named else "Rep.", "Dif."]
    table = Table(
        f"tabela2_superior_{average_title}_dupla", header, rows, caption, source, tuple(READINGS)
    )
    table.groups = [("", 1), *((title, 3) for title in titles.values())]
    return table


def table_ii_tables(results_dir: Path) -> list[Table]:
    """Metade superior da Tabela II com a média macro e com a ponderada."""
    return [
        table_ii_table(results_dir, "macro", "macro", "Macro"),
        table_ii_table(results_dir, "weighted", "ponderada", "Pond."),
    ]


def literature_cell(entry: dict, metric: str) -> str:
    """Valor de uma linha da literatura em percentual, como o artigo o imprime."""
    if entry[metric] is None:
        return MISSING
    value = entry[metric] if entry["percent"] else 100 * entry[metric]
    return Num(f"{round(value, LITERATURE_DECIMALS):g}")


def literature_table(results_dir: Path) -> list[Table]:
    """Metade inferior da Tabela II: resultados de outros trabalhos, transcritos do artigo."""
    metrics = ["auc", "accuracy", "f1", "precision", "recall"]
    rows = [
        [entry["model"], entry["reference"], *(literature_cell(entry, key) for key in metrics)]
        for entry in TABLE_II_LITERATURE
    ]
    caption = (
        "Metade inferior da Tabela II do artigo: resultados de outros trabalhos no mesmo "
        "dataset, em %, transcritos como o artigo os imprime; a referência é a da lista do "
        "artigo e o traço marca a célula que ele deixa vazia. O artigo declara que o método "
        "experimental desses trabalhos não é diretamente comparável ao dele (Seção V), e não "
        "diz que média usam."
    )
    header = ["Modelo", "Ref.", "AUC", "Acurácia", "F1", "Precisão", "Recall"]
    return [Table("tabela2_literatura", header, rows, caption, "config.py, TABLE_II_LITERATURE")]


def timings_table(results_dir: Path) -> list[Table]:
    """Tempos de treino medidos na reprodução e nos modelos de comparação, em segundos."""
    rows = []
    for model, title in BASELINES.items():
        timings = load_log(results_dir, "e2", "fiel", model)["timings"]
        rows.append(
            [title, num(timings["smote_seconds"], 1), num(timings["fit_seconds"], 1)]
            + [MISSING, MISSING]
        )
    cpus = set()
    for track, reading in READINGS.items():
        log = load_log(results_dir, "e1", track, SYSTEM_SLICES[track])
        timings = log["timings"]
        cpus.add(log["cpu_count"])
        rows.append(
            [f"Proposto, {reading}"]
            + [
                num(timings[key], 1)
                for key in [
                    "subsets_seconds",
                    "base_fit_seconds",
                    "meta_fit_seconds",
                    "cross_validation_seconds",
                ]
            ]
        )
    caption = model_caption(
        "Tempos medidos em uma execução, em segundos: reamostragem (SMOTE; no modelo proposto, "
        "a montagem dos três subconjuntos), ajuste do modelo ou dos três Random Forests base, "
        f"ajuste do meta-classificador e validação cruzada de {CV_FOLDS} folds. Máquina com "
        f"{' ou '.join(str(value) for value in sorted(cpus))} núcleos; o tempo varia entre "
        "execuções e não entra na comparação com o artigo, que não o reporta.",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    header = ["Modelo", "Reamostragem", "Ajuste", "Meta", "Valid. cruzada"]
    source = (
        "results/e2/fiel/*/seed42/run.json; "
        "results/e1/{fiel/proposto,variante/profundidade_variavel}/seed42/run.json"
    )
    return [Table("tempos_treino", header, rows, caption, source, tuple(READINGS))]


def meta_decision_table(results_dir: Path) -> list[Table]:
    """Decisão do meta-classificador quando os bases concordam e fluxos em que discordam."""
    rows = []
    for track, metrics in both_readings(results_dir, "e1", SYSTEM_SLICES).items():
        reading = READING_HEADERS[track]
        for entry in metrics["meta_decision_table"]:
            labels = set(entry["base_labels"])
            if len(labels) == 1 and entry["test_rows"] > 0:
                bases, meta = CLASS_NAMES[labels.pop()], CLASS_NAMES[entry["meta_label"]]
                rows.append([reading, bases, meta, count(entry["test_rows"]), MISSING])
        fraction = num(100 * metrics["base_disagreement_test_fraction"])
        rows.append(
            [reading, "em desacordo", "varia", count(metrics["base_disagreement_test_rows"])]
            + [fraction]
        )
        rows.append(None)
    caption = model_caption(
        "Saída do meta-classificador (regressão logística sobre os rótulos preditos pelos três "
        "Random Forests base) nos fluxos do teste em que os bases são unânimes, e número de "
        "fluxos em que eles discordam, com a fração do teste em %.",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    header = ["Leitura", "Bases unânimes em", "Saída do meta", "Fluxos", "% do teste"]
    source = E1_SOURCE
    return [Table("reproducao_meta", header, rows[:-1], caption, source, tuple(READINGS))]


# Explicabilidade.

SHAP_RUNS = {
    "cira": ("e5", SYSTEM_SLICES, "CIRA"),
    "segundo": ("e6", "retreino_sem_replicas-shap", SECOND_DATASET),
}
SHAP_SOURCE = (
    "results/e5/{fiel/proposto,variante/profundidade_variavel}/seed42/; "
    "results/e6/{fiel,variante}/retreino_sem_replicas-shap/seed42/"
)
MALICIOUS = CLASS_NAMES[2]


def shap_runs(results_dir: Path) -> dict[tuple[str, str], dict]:
    """Métricas de explicabilidade por (dataset, trilha), nos dois datasets e nas duas leituras."""
    return {
        (dataset, track): metrics
        for dataset, (experiment, slices, _) in SHAP_RUNS.items()
        for track, metrics in both_readings(results_dir, experiment, slices).items()
    }


def shap_header(runs: dict) -> tuple[list[str], list[tuple[str, int]]]:
    """Colunas das tabelas de explicabilidade: uma por leitura, agrupadas por dataset."""
    header = [READING_HEADERS[track] for _, track in runs]
    # No cabeçalho, o combinado sem réplicas vai só como "Combinado"; a legenda diz qual é.
    return header, [(title.split()[0], len(READINGS)) for _, _, title in SHAP_RUNS.values()]


def article_ranking_cells(metrics: dict) -> list[str]:
    """Spearman com a Fig. 5 e atributos em comum no topo, onde a comparação foi gravada."""
    for entry in metrics.get("fig5_comparison", []):
        if entry["base"] == metrics["explained_base"]:
            return [num(entry["spearman_all_features"]), count(entry["top_shared_with_article"])]
    return [MISSING, MISSING]


def shap_ranking_table(results_dir: Path) -> list[Table]:
    """Posição dos atributos do topo da Fig. 5 no ranking de importância obtido."""
    runs = shap_runs(results_dir)
    rankings = [
        metrics["ranking"][f"base_{metrics['explained_base']}"][MALICIOUS]
        for metrics in runs.values()
    ]
    rows = [
        [feature, count(position), *(count(ranking.index(feature) + 1) for ranking in rankings)]
        for position, feature in enumerate(FIG5_RANKING[:SHAP_TOP_FEATURES], start=1)
    ]
    spearman, shared = zip(*map(article_ranking_cells, runs.values()), strict=True)
    rows += [
        None,
        ["Spearman com a Fig. 5", MISSING, *spearman],
        [f"Em comum nos {SHAP_TOP_FEATURES} primeiros", MISSING, *shared],
    ]
    first = next(iter(runs.values()))
    caption = model_caption(
        f"Os {SHAP_TOP_FEATURES} atributos mais importantes da Fig. 5 do artigo e a posição de "
        "cada um no ranking de importância global (média do valor absoluto de SHAP) da classe "
        f"{MALICIOUS}, no Random Forest base {first['explained_base']}, nos dois datasets e nas "
        f"duas leituras de profundidade. Amostra de {first['sample_per_class_requested']} "
        f"fluxos por classe. A correlação de Spearman usa os {len(FIG5_RANKING)} atributos e "
        "só é calculada contra o artigo no CIRA.",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    header, groups = shap_header(runs)
    table = Table("shap_ranking", ["Atributo", "Artigo", *header], rows, caption, SHAP_SOURCE)
    table.tracks, table.groups = tuple(READINGS), [("", 2), *groups]
    return [table]


def shap_stability_table(results_dir: Path) -> list[Table]:
    """Estabilidade do ranking SHAP entre os três Random Forests base, por classe."""
    runs = shap_runs(results_dir)
    rows = [
        [name, *(num(min(metrics["stability"][name].values())) for metrics in runs.values())]
        for name in CLASS_ORDER
    ]
    first = next(iter(runs.values()))
    caption = model_caption(
        "Estabilidade do ranking SHAP entre os três Random Forests base: menor correlação de "
        "Spearman entre os pares de bases, calculada sobre os atributos que estão entre os "
        f"{first['stability_top_features']} primeiros de pelo menos um dos dois (1 = mesma "
        "ordem).",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    header, groups = shap_header(runs)
    table = Table("shap_estabilidade", ["Classe", *header], rows, caption, SHAP_SOURCE)
    table.tracks, table.groups = tuple(READINGS), [("", 1), *groups]
    return [table]


# Segundo dataset.

E6_SOURCE = "results/e6/{fiel,variante}/<cenário>/seed42/metrics.json"


def second_dataset_metrics_table(results_dir: Path) -> list[Table]:
    """Métricas no teste do sistema nas duas leituras: CIRA ao lado do combinado sem réplicas."""
    cira = both_readings(results_dir, "e1", SYSTEM_SLICES)
    combined = both_readings(results_dir, "e6", "retreino_sem_replicas")
    columns = [metric_values(metrics["test"]) for metrics in [*cira.values(), *combined.values()]]
    rows = []
    for label in columns[0]:
        if label == AVERAGES["accuracy"]:
            rows.append(None)
        rows.append([label, *(percent(label, column[label]) for column in columns)])
    caption = model_caption(
        "Sistema do artigo retreinado e avaliado no segundo dataset (combinado CIRA + HKD sem "
        "réplicas), ao lado do CIRA: métricas no teste, em %, nas duas leituras de "
        "profundidade. Non-DoH e Benign-DoH do combinado são os do CIRA.",
        tuple(READINGS),
        SINGLE_SEED,
        MACRO_NAMED,
    )
    header = ["Métrica", *READING_HEADERS.values(), *READING_HEADERS.values()]
    source = (
        "results/e1/{fiel/proposto,variante/profundidade_variavel}/seed42/metrics.json; "
        "results/e6/{fiel,variante}/retreino_sem_replicas/seed42/metrics.json"
    )
    table = Table("segundo_metricas", header, rows, caption, source, tuple(READINGS))
    table.groups = [("", 1), ("CIRA", len(READINGS)), (SECOND_DATASET, len(READINGS))]
    return [table]


def second_dataset_baselines_table(results_dir: Path) -> list[Table]:
    """Modelos de comparação e sistema proposto no teste, nos dois datasets."""
    metrics = ["F1 macro", "Benign-DoH: recall", "Malicious-DoH: recall", FPR_LABEL]
    models = {
        title: (
            load_run(results_dir, "e2", "fiel", model),
            load_run(results_dir, "e6", "fiel", f"retreino_sem_replicas-{model}"),
        )
        for model, title in BASELINES.items()
    }
    cira = both_readings(results_dir, "e1", SYSTEM_SLICES)
    combined = both_readings(results_dir, "e6", "retreino_sem_replicas")
    for track, reading in READINGS.items():
        models[f"Proposto, {reading}"] = (cira[track], combined[track])
    rows = []
    for title, runs in models.items():
        row = [title]
        for run in runs:
            values = metric_values(run["test"])
            row += [percent(label, values[label]) for label in metrics]
        rows.append(row)
    caption = model_caption(
        "Modelos de comparação da Tabela II e sistema proposto, nas duas leituras de "
        "profundidade, no teste do CIRA e do combinado sem réplicas, em %. Os modelos de "
        "comparação são da trilha fiel.",
        tuple(READINGS),
        SINGLE_SEED,
        "média macro",
    )
    short = ["F1 macro", "Benign rec.", "Malic. rec.", "Malic. FPR"]
    source = (
        "results/e2/fiel/*/seed42/metrics.json; results/e1/*/*/seed42/metrics.json; "
        "results/e6/fiel/retreino_sem_replicas-*/seed42/metrics.json; "
        "results/e6/{fiel,variante}/retreino_sem_replicas/seed42/metrics.json"
    )
    table = Table(
        "segundo_baselines_dupla", ["Modelo", *short * 2], rows, caption, source, tuple(READINGS)
    )
    table.groups = [("", 1), ("CIRA", len(short)), (SECOND_DATASET, len(short))]
    return [table]


def second_dataset_confusion_table(results_dir: Path) -> list[Table]:
    """Matrizes de confusão no combinado sem réplicas: teste e validação cruzada."""
    runs = both_readings(results_dir, "e6", "retreino_sem_replicas")
    rows = []
    for key, title in [("test", "teste"), ("cross_validation", "validação")]:
        for track, metrics in runs.items():
            label = f"{READING_HEADERS[track]}, {title}"
            rows += [*confusion_block(label, metrics[key]["confusion_matrix"]), None]
    caption = model_caption(
        "Matrizes de confusão do sistema do artigo no combinado sem réplicas, no teste e na "
        f"validação cruzada de {CV_FOLDS} folds sobre o treino, nas duas leituras de "
        "profundidade. Linha é a classe real e coluna a classe predita.",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    header = ["Avaliação", "Classe real", *CLASS_NAMES]
    source = "results/e6/{fiel,variante}/retreino_sem_replicas/seed42/metrics.json"
    table = Table("segundo_matrizes", header, rows[:-1], caption, source, tuple(READINGS))
    table.groups = PREDICTED_GROUPS
    return [table]


SCENARIOS = {
    "transferencia": "Transferência",
    "retreino_publicado": "Retreino, publicado",
    "retreino_sem_replicas": "Retreino, sem réplicas",
}


def tool_recall_table(results_dir: Path) -> list[Table]:
    """Recall de Malicious-DoH por ferramenta na transferência e nos dois retreinos."""
    rows = []
    for scenario, title in SCENARIOS.items():
        runs = both_readings(results_dir, "e6", scenario)
        by_tool = {track: tool_recalls(metrics) for track, metrics in runs.items()}
        for tool in TOOL_ORIGIN:
            if tool in by_tool["fiel"]:
                rows.append(
                    [title, tool, count(by_tool["fiel"][tool]["n"])]
                    + [num(100 * by_tool[track][tool]["recall"]) for track in READINGS]
                )
        rows.append(None)
    caption = model_caption(
        "Recall de Malicious-DoH por ferramenta de túnel, em %, no segundo dataset: "
        "transferência (modelo treinado no CIRA e avaliado no HKD inteiro, sem retreino), "
        "retreino no combinado como publicado e retreino no combinado sem réplicas. n é o "
        "número de fluxos da ferramenta no conjunto de teste do cenário. dns2tcp, dnscat2 e "
        "iodine são do CIRA; dnstt, tcp-over-dns e tuns, do HKD.",
        tuple(READINGS),
        SINGLE_SEED,
        NO_AVERAGE,
    )
    header = [
        "Cenário",
        "Ferramenta",
        "n",
        *READING_HEADERS.values(),
    ]
    return [
        Table("segundo_recall_ferramenta", header, rows[:-1], caption, E6_SOURCE, tuple(READINGS))
    ]


def replicas_table(results_dir: Path) -> list[Table]:
    """Retreino no combinado publicado contra o combinado sem réplicas."""
    runs = {
        (scenario, track): metrics
        for scenario in ["retreino_publicado", "retreino_sem_replicas"]
        for track, metrics in both_readings(results_dir, "e6", scenario).items()
    }
    rows = [
        [label, *(percent(label, metric_values(run["test"])[label]) for run in runs.values())]
        for label in KEY_METRICS
    ]
    rows.append(None)
    rows.append(
        ["Recall nos fluxos do HKD"]
        + [num(100 * run["test_recall_by_origin"]["HKD"]["recall"]) for run in runs.values()]
    )
    rows.append(["Fluxos do HKD no teste", *(count(run["hkd_test_rows"]) for run in runs.values())])
    rows.append(
        ["dos quais repetidos no treino"]
        + [count(run["hkd_test_rows_seen_in_train"]) for run in runs.values()]
    )
    caption = model_caption(
        "Retreino do sistema do artigo no combinado como publicado e no combinado sem réplicas: "
        "métricas no teste, em %, e contagem dos fluxos do HKD do teste cujo vetor de atributos "
        "também está no treino. No publicado, as cópias de cada fluxo caem dos dois lados do "
        "split, e o recall no HKD mede memorização.",
        tuple(READINGS),
        SINGLE_SEED,
        "média macro",
    )
    header = ["Métrica", *READING_HEADERS.values(), *READING_HEADERS.values()]
    table = Table("segundo_replicas", header, rows, caption, E6_SOURCE, tuple(READINGS))
    table.groups = [("", 1), ("Publicado", len(READINGS)), ("Sem réplicas", len(READINGS))]
    return [table]


# Ferramenta de túnel.


def tunnel_tool_table(results_dir: Path) -> list[Table]:
    """Métricas por ferramenta de túnel ao lado dos valores da Seção VI-D do artigo."""
    rows, overall = [], []
    for track, metrics in both_readings(results_dir, "e7", "ferramenta").items():
        for tool, entry in metrics["article_comparison"].items():
            values = [entry["article_accuracy"], entry["precision"], entry["recall"], entry["f1"]]
            rows.append(
                [READING_HEADERS[track], tool, count(entry["support"])]
                + [num(100 * value) for value in values]
                + [signed(entry["difference_pp"]["recall"])]
            )
        rows.append(None)
        test = metrics["test"]
        overall.append(
            f"{READINGS[track]}: acurácia {tex_cell(num(100 * test['accuracy']))}% e F1 macro "
            f"{tex_cell(num(100 * test['macro_f1']))}%"
        )
    caption = model_caption(
        "Identificação da ferramenta de túnel nos fluxos Malicious-DoH do CIRA, em %, ao lado "
        "dos três valores que a Seção VI-D do artigo chama de acurácia. O artigo não descreve "
        "o método: aqui o mesmo sistema empilhado é treinado com as três ferramentas como "
        "classes, o que é leitura da equipe, e o recall por ferramenta é a métrica comparada "
        "ao valor do artigo (Dif., em pontos percentuais). No conjunto das três ferramentas, "
        f"{'; '.join(overall)}.",
        tuple(READINGS),
        SINGLE_SEED,
        "média macro",
    )
    header = ["Leitura", "Ferramenta", "n", "Artigo", "Precisão", "Recall", "F1", "Dif."]
    source = "results/e7/{fiel,variante}/ferramenta/seed42/metrics.json"
    return [Table("ferramenta_metricas", header, rows[:-1], caption, source, tuple(READINGS))]


# Opcionais: sensibilidade, protocolo corrigido, modificação e robustez.


def sensitivity_table(results_dir: Path) -> list[Table]:
    """Sensibilidade às leituras alternativas do artigo, a partir da tabela comparativa."""
    comparison = pd.read_csv(results_dir / "e3" / "variante" / "comparacao.csv")
    columns = {
        "accuracy": "Acurácia",
        "benign_precision": "Benign-DoH: precisão",
        "benign_recall": "Benign-DoH: recall",
        "malicious_recall": "Malicious-DoH: recall",
        "malicious_fpr": FPR_LABEL,
        "macro_f1": "F1 macro",
    }
    rows = []
    for _, entry in comparison.iterrows():
        # Linha horizontal antes de cada uma das duas reproduções de partida.
        if pd.notna(entry["start"]) and entry["changed_point"].startswith("nenhum"):
            rows.append(None)
        rows.append(
            [entry["configuration"]]
            + [percent(label, entry[key]) for key, label in columns.items()]
            + [count(entry["fig4b_absolute_difference_sum"])]
        )
    caption = model_caption(
        "Sensibilidade às leituras alternativas dos pontos que o artigo deixa em aberto, no "
        "teste do CIRA, em %. Cada configuração muda um ponto a partir de uma das duas "
        "reproduções (profundidade variável ou, com o sufixo prof5, profundidade 5). A última "
        "coluna é a soma das diferenças absolutas, célula a célula, para a matriz da Fig. 4b.",
        ("variante",),
        SINGLE_SEED,
        "média macro",
    )
    header = ["Configuração", "Acurácia", "Benign prec.", "Benign rec.", "Malic. rec."]
    header += ["Malic. FPR", "F1 macro", "Σ |dif.| Fig. 4b"]
    source = "results/e3/variante/comparacao.csv"
    return [Table("sensibilidade_dupla", header, rows, caption, source, ("variante",))]


E4_SOURCE = "results/e4/corrigida/summary.json"
E8_SOURCE = "results/e8/corrigida/summary.json"
ROBUSTNESS_SOURCE = "results/e8/corrigida/summary-robustez.json"


def load_summary(results_dir: Path, source: str) -> tuple[dict, tuple[str, ...], str]:
    """Lê um resumo de seeds; devolve o resumo, a trilha e a descrição das seeds."""
    summary = read_json(results_dir / Path(source).relative_to("results"))
    return summary, (summary["track"],), ten_seeds(summary["seeds"])


def summary_cells(statistics: dict, labels: list[str]) -> list[Num]:
    """Média ± desvio de cada métrica pedida, a partir de um resumo de seeds."""
    return [
        mean_std(statistics[SUMMARY_KEYS[label]], decimals=decimals_for(label)) for label in labels
    ]


def corrected_metrics_table(results_dir: Path) -> list[Table]:
    """Protocolo corrigido: métricas no teste de cada modelo, em dez seeds."""
    summary, tracks, seeds = load_summary(results_dir, E4_SOURCE)
    models = summary["models"]
    columns = [summary_cells(model["test"], list(SUMMARY_KEYS)) for model in models.values()]
    rows = [[label, *cells] for label, *cells in zip(SUMMARY_KEYS, *columns, strict=True)]
    rows.insert(list(SUMMARY_KEYS).index(AVERAGES["accuracy"]), None)
    described = "; ".join(
        model_description(name, model["config"]) for name, model in models.items()
    )
    caption = model_caption(
        f"Protocolo corrigido no CIRA: métricas no teste, em %. {described}. Todos com SMOTE "
        "ajustado só no treino.",
        tracks,
        seeds,
        MACRO_NAMED,
    )
    header = ["Métrica", *models]
    return [Table("corrigido_metricas_dupla", header, rows, caption, E4_SOURCE, tracks)]


def duplicates_table(results_dir: Path) -> list[Table]:
    """Protocolo corrigido: métricas com e sem as linhas do teste repetidas no treino."""
    summary, tracks, seeds = load_summary(results_dir, E4_SOURCE)
    labels = ["F1 macro", "Benign-DoH: recall"]
    rows = [
        [name, mean_std(model["test_seen_in_train_fraction"])]
        + [cell for scope in summary["scopes"] for cell in summary_cells(model[scope], labels)]
        for name, model in summary["models"].items()
    ]
    caption = model_caption(
        "Efeito das linhas do teste cujo vetor de atributos também está no treino: fração do "
        "teste que se repete e métricas, em %, no teste inteiro e no teste sem essas linhas.",
        tracks,
        seeds,
        "média macro",
    )
    header = ["Modelo", "Teste repetido no treino", *labels * len(summary["scopes"])]
    table = Table("corrigido_repetidos_dupla", header, rows, caption, E4_SOURCE, tracks)
    table.groups = [
        ("", 2),
        *((title.capitalize(), len(labels)) for title in summary["scopes"].values()),
    ]
    return [table]


def base_rate_table(results_dir: Path) -> list[Table]:
    """Protocolo corrigido: precisão operacional sob prevalências hipotéticas."""
    summary, tracks, seeds = load_summary(results_dir, E4_SOURCE)
    models = summary["models"]
    prevalences = [entry["prevalence"] for entry in next(iter(models.values()))["base_rate"]]
    rows = [
        [name, count(model["false_positives_total"]), count(model["negatives_total"])]
        + [num(100 * entry["operational_precision"]) for entry in model["base_rate"]]
        + [num(model["base_rate"][-1]["false_alarms_per_10_million"], 0)]
        for name, model in models.items()
    ]
    caption = model_caption(
        "Taxa base: precisão operacional de Malicious-DoH, em %, sob prevalências hipotéticas "
        "de tráfego malicioso (o dataset não mede a prevalência real), calculada com o FPR e o "
        "recall médios das seeds, e alarmes falsos esperados em "
        f"{BASE_RATE_FLOWS // 10**6} milhões de fluxos na menor prevalência. FP e Negativos são "
        "os falsos positivos e os fluxos não maliciosos somados nas seeds.",
        tracks,
        seeds,
        NO_AVERAGE,
    )
    header = ["Modelo", "FP", "Negativos"]
    header += [f"1 em {round(1 / prevalence)}" for prevalence in prevalences] + ["Alarmes"]
    table = Table("corrigido_taxa_base", header, rows, caption, E4_SOURCE, tracks)
    table.groups = [("", 3), ("Precisão, prevalência", len(prevalences)), ("", 1)]
    return [table]


def group_folds_table(results_dir: Path) -> list[Table]:
    """Protocolo corrigido: split aleatório contra folds por máquina de origem, se medidos."""
    summary, tracks, seeds = load_summary(results_dir, E4_SOURCE)
    if "group_folds" not in summary:
        return []
    groups = summary["group_folds"]
    columns = [summary["models"][groups["model"]]["test"], groups["across_folds"]]
    cells = [summary_cells(column, KEY_METRICS) for column in columns]
    rows = [list(row) for row in zip(KEY_METRICS, *cells, strict=True)]
    caption = model_caption(
        f"Modelo {groups['model']} avaliado com split aleatório estratificado ({seeds}) e com "
        f"folds por máquina de origem do fluxo ({len(groups['folds'])} folds, seed "
        f"{groups['seed']}, média ± desvio padrão amostral entre os folds), em %. Nos folds por "
        "máquina, nenhuma máquina do teste aparece no treino.",
        tracks,
        seeds,
        "média macro",
    )
    header = ["Métrica", "Split aleatório", "Por máquina"]
    return [Table("corrigido_grupos", header, rows, caption, E4_SOURCE, tracks)]


def modification_metrics_table(results_dir: Path) -> list[Table]:
    """Modificação da equipe e sistema do artigo no teste, nos dois datasets, em dez seeds."""
    summary, tracks, seeds = load_summary(results_dir, E8_SOURCE)
    rows, descriptions = [], {}
    for key, dataset in summary["datasets"].items():
        for name, model in dataset["models"].items():
            descriptions[name] = model_description(name, model["config"])
            rows.append(
                [DATASET_TITLES[key], name, *summary_cells(model["test"], KEY_METRICS)]
                + [mean_std(model["train_seconds"], scale=1, decimals=1)]
            )
        rows.append(None)
    selection = summary["selection"]
    caption = model_caption(
        "Modificação proposta pela equipe contra o sistema do artigo (A), no teste, em %, com o "
        f"tempo de treino em segundos. {MODIFIED_SELECTED_MODEL} é a modificação: Random Forest "
        "único, sem SMOTE, com peso de classe balanceado e hiperparâmetros escolhidos em cada "
        f"seed por validação cruzada de {selection['folds']} folds em "
        f"{selection['train_fraction']:.0%} do treino ({selection['metric']}); M1 só troca o "
        f"SMOTE pelo peso de classe. {'; '.join(descriptions.values())}.",
        tracks,
        seeds,
        "média macro",
    )
    header = ["Dataset", "Modelo", "Benign prec.", "Benign rec.", "Benign F1", "Malic. rec."]
    header += ["Malic. FPR", "F1 macro", "Treino (s)"]
    return [Table("modificacao_metricas_dupla", header, rows[:-1], caption, E8_SOURCE, tracks)]


def paired_row(dataset: str, entry: dict) -> list[str]:
    """Linha de uma comparação pareada: diferença média, desvio, vitórias e leitura."""
    seconds = entry["metric"] == "train_seconds"
    label = "Tempo de treino (s)" if seconds else KEY_LABELS[entry["metric"]]
    scale, decimals = (1, 1) if seconds else (100, decimals_for(label))
    return [
        dataset,
        f"{entry['first']} − {entry['second']}",
        label,
        signed(scale * entry["mean_difference"], decimals),
        num(scale * entry["std_difference"], decimals),
        Num(f"{entry['first_wins']}–{entry['second_wins']}"),
        entry["verdict"],
    ]


def modification_paired_table(results_dir: Path) -> list[Table]:
    """Comparação pareada por seed entre a modificação e o modelo de referência."""
    summary, tracks, seeds = load_summary(results_dir, E8_SOURCE)
    rows = []
    for key, dataset in summary["datasets"].items():
        # Só o teste inteiro; o tempo de treino não tem recorte do teste.
        rows += [
            paired_row(DATASET_TITLES[key], entry)
            for entry in dataset["paired"]
            if entry["scope"] in ("test", None)
        ]
        rows.append(None)
    caption = model_caption(
        "Comparação pareada por seed entre a modificação e o modelo de referência: diferença "
        "média (primeiro menos segundo) e desvio padrão das diferenças, em pontos percentuais "
        "(em segundos no tempo de treino), e número de seeds em que cada um tem o valor maior. "
        "A leitura segue a regra fixada antes da execução: há diferença quando a média, em "
        "módulo, passa do desvio. Os conjuntos de teste das seeds se sobrepõem, e os pares não "
        "são independentes.",
        tracks,
        seeds,
        "média macro",
    )
    header = ["Dataset", "Comparação", "Métrica", "Dif. média", "Desvio", "Seeds a favor"]
    header += ["Leitura"]
    return [Table("modificacao_pareada_dupla", header, rows[:-1], caption, E8_SOURCE, tracks)]


def modification_transfer_table(results_dir: Path) -> list[Table]:
    """Transferência da modificação treinada no CIRA para os fluxos do HKD."""
    summary, tracks, seeds = load_summary(results_dir, E8_SOURCE)
    transfer = summary["datasets"]["cira"]["hkd_transfer"]
    rows = [
        [tool, count(entry["rows_mean"]), mean_std(entry["recall"])]
        for tool, entry in transfer.items()
    ]
    caption = model_caption(
        f"Transferência da modificação ({MODIFIED_SELECTED_MODEL}) treinada no CIRA para os "
        "fluxos do HKD, sem retreino: recall de Malicious-DoH por ferramenta, em %.",
        tracks,
        seeds,
        NO_AVERAGE,
    )
    header = ["Ferramenta do HKD", "n", "Recall"]
    return [Table("modificacao_transferencia", header, rows, caption, E8_SOURCE, tracks)]


def fragmentation_text(summary: dict) -> str:
    """Descreve a perturbação de fragmentação, para a legenda da tabela e da figura."""
    return (
        "Cada fluxo Malicious-DoH do teste é dividido em k fluxos iguais: "
        f"{', '.join(summary['fragmented_columns'])} são divididos por k e as taxas e as "
        "estatísticas de pacote ficam como estão. É uma perturbação no espaço de atributos, "
        "não tráfego gerado, e o modelo não é retreinado com fluxos fragmentados."
    )


def column_sets(summary: dict) -> list[tuple[str, list[str]]]:
    """Conjuntos de atributos da robustez, do completo para o mais reduzido."""
    return sorted(summary["column_sets"].items(), key=lambda item: len(item[1]))


def robustness_table(results_dir: Path) -> list[Table]:
    """Recall de Malicious-DoH sob fragmentação do fluxo, por conjunto de atributos e fator."""
    summary, tracks, seeds = load_summary(results_dir, ROBUSTNESS_SOURCE)
    models = summary["models"]
    rows = []
    for name, dropped in column_sets(summary):
        for factor in map(str, summary["factors"]):
            duration = summary["perturbation"][factor]["median_duration_seconds"]["mean"]
            rows.append(
                ["sem " + ", ".join(dropped) if dropped else "todos", count(factor)]
                + [num(duration, 1)]
                + [
                    mean_std(model[name]["fragmentation"][factor]["recall"])
                    for model in models.values()
                ]
            )
        rows.append(None)
    caption = model_caption(
        "Recall de Malicious-DoH, em %, sob fragmentação do fluxo, no CIRA. "
        f"{fragmentation_text(summary)} A duração mediana é a dos fluxos maliciosos do teste "
        "depois da divisão.",
        tracks,
        seeds,
        NO_AVERAGE,
    )
    header = ["Atributos do modelo", "k", "Duração mediana (s)", *models]
    name = "robustez_fragmentacao_dupla"
    return [Table(name, header, rows[:-1], caption, ROBUSTNESS_SOURCE, tracks)]


def robustness_figure(results_dir: Path) -> list[Plot]:
    """Recall de Malicious-DoH contra o fator de fragmentação, com todos os atributos."""
    summary, tracks, seeds = load_summary(results_dir, ROBUSTNESS_SOURCE)
    all_features = column_sets(summary)[0][0]
    figure = Figure(figsize=(COLUMN_WIDTH, 2.4), layout="constrained")
    axis = figure.subplots()
    for (name, model), color in zip(summary["models"].items(), SERIES_COLORS, strict=False):
        recall = [
            model[all_features]["fragmentation"][str(factor)]["recall"]
            for factor in summary["factors"]
        ]
        axis.errorbar(
            summary["factors"],
            [100 * entry["mean"] for entry in recall],
            yerr=[100 * entry["std"] for entry in recall],
            color=color,
            marker="o",
            markersize=3,
            capsize=2,
            label=name,
        )
    axis.set_xscale("log", base=2)
    axis.set_xticks(summary["factors"], labels=summary["factors"])
    axis.set_xlabel("Fator de fragmentação k (fluxos por fluxo original)")
    axis.set_ylabel("Recall de Malicious-DoH (%)")
    axis.legend(title="Modelo")
    caption = (
        "Recall de Malicious-DoH sob fragmentação do fluxo, no CIRA, com todos os atributos. "
        f"{fragmentation_text(summary)} Trilha {tracks[0]}; {seeds}."
    )
    return [Plot("robustez_fragmentacao", figure, caption, ROBUSTNESS_SOURCE)]


# Figuras.


def density_figure(results_dir: Path) -> list[Plot]:
    """Densidade por classe dos três atributos da Fig. 2 do artigo."""
    curves = pd.read_csv(results_dir / E0_RUN / "fig2_densidade.csv")
    figure = Figure(figsize=(PAGE_WIDTH, 2.1), layout="constrained")
    axes = figure.subplots(1, len(FIG2_PANELS))
    for axis, letter, (column, unit, _, _, log_scale) in zip(axes, "abc", FIG2_PANELS, strict=True):
        panel = curves[curves["atributo"] == column]
        for name in CLASS_NAMES:
            curve = panel[panel["classe"] == name]
            axis.plot(curve["x"], curve["densidade"], color=CLASS_COLORS[name], label=name)
        if log_scale:
            axis.set_xscale("log")
        axis.set_xlabel(f"({letter}) {column} ({unit})")
        axis.set_ylabel("Densidade (1/década)" if log_scale else f"Densidade (1/{unit})")
        axis.set_ylim(bottom=0)
    axes[0].legend()
    caption = (
        "Densidade estimada por classe de três atributos do CIRA-CIC-DoHBrw-2020 limpo, nas "
        "faixas de eixo da Fig. 2 do artigo: (a) FlowBytesReceived, (b) PacketLengthMean e "
        "(c) PacketLengthVariance, este em escala logarítmica."
    )
    source = f"results/{E0_RUN}/fig2_densidade.csv"
    return [Plot("fig2_densidades_dupla", figure, caption, source)]


def draw_confusion(axis, matrix: list[list[int]], difference: list[list[int]] | None) -> None:
    """Desenha uma matriz de confusão, colorida pela fração da classe real."""
    counts = np.array(matrix)
    fractions = counts / counts.sum(axis=1, keepdims=True)
    axis.imshow(fractions, cmap="Blues", vmin=0, vmax=1)
    for row in range(len(CLASS_NAMES)):
        for column in range(len(CLASS_NAMES)):
            text = str(counts[row, column])
            if difference is not None:
                text += f"\n({signed(difference[row][column], 0)})"
            # Acima da metade da escala o fundo é escuro e o texto vai em branco.
            color = "white" if fractions[row, column] > 0.5 else "black"
            axis.text(column, row, text, ha="center", va="center", color=color, fontsize=7)
    axis.set_xticks(range(len(CLASS_NAMES)), labels=CLASS_NAMES)
    axis.set_yticks(range(len(CLASS_NAMES)), labels=CLASS_NAMES, rotation=90, va="center")
    axis.set_xlabel("Classe predita")


def confusion_figures(results_dir: Path) -> list[Plot]:
    """Matrizes de confusão lado a lado: artigo e as duas leituras, no teste e na validação."""
    runs = both_readings(results_dir, "e1", SYSTEM_SLICES)
    plots = []
    for name, key, article, evaluation, title in [
        ("matriz_confusao_teste_dupla", "fig4b", FIG4B_CONFUSION, "test", "no teste"),
        (
            "matriz_confusao_validacao_dupla",
            "fig4a",
            FIG4A_CONFUSION,
            "cross_validation",
            CV_TITLE,
        ),
    ]:
        figure = Figure(figsize=(PAGE_WIDTH, 2.6), layout="constrained")
        axes = figure.subplots(1, 1 + len(READINGS))
        draw_confusion(axes[0], article, None)
        axes[0].set_title(f"Artigo (Fig. 4{key[-1]})")
        axes[0].set_ylabel("Classe real")
        for axis, (track, metrics) in zip(axes[1:], runs.items(), strict=True):
            difference = metrics[f"{key}_comparison"]["cell_difference"]
            draw_confusion(axis, metrics[evaluation]["confusion_matrix"], difference)
            axis.set_title(f"{READINGS[track].capitalize()} (trilha {track})")
        caption = (
            f"Matrizes de confusão {title}: artigo e reprodução nas duas leituras de "
            "profundidade dos Random Forests base. Em cada célula, o número de fluxos e, entre "
            "parênteses, a diferença para o artigo; a cor é a fração da classe real. "
            f"Seed {SEED_FIEL}."
        )
        source = E1_SOURCE
        plots.append(Plot(name, figure, caption, source))
    return plots


def shap_run_dir(results_dir: Path, dataset: str, track: str) -> Path:
    """Pasta da execução de explicabilidade de um dataset em uma trilha."""
    experiment, slices, _ = SHAP_RUNS[dataset]
    run_slice = slices if isinstance(slices, str) else slices[track]
    return run_dir(results_dir, experiment, track, run_slice, SEED_FIEL)


def importance_figure(results_dir: Path, dataset: str, runs: dict) -> Plot:
    """Importância global de Malicious-DoH (equivalente à Fig. 5), nas duas leituras."""
    figure = Figure(figsize=(COLUMN_WIDTH, 4.6), layout="constrained")
    axes = figure.subplots(len(READINGS), 1)
    for axis, track in zip(axes, READINGS, strict=True):
        metrics = runs[dataset, track]
        importance = pd.read_csv(shap_run_dir(results_dir, dataset, track) / "importancia.csv")
        top = importance[
            (importance["base"] == metrics["explained_base"])
            & (importance["class_name"] == MALICIOUS)
        ].nsmallest(SHAP_TOP_FEATURES, "rank")
        axis.barh(top["feature"], top["mean_abs_shap"], color=CLASS_COLORS[MALICIOUS])
        axis.invert_yaxis()
        # Título alinhado à direita: os nomes dos atributos estreitam o painel.
        axis.set_title(f"{READINGS[track].capitalize()} (trilha {track})", loc="right")
    axes[-1].set_xlabel("Média do valor absoluto de SHAP")
    first = runs[dataset, "fiel"]
    caption = (
        f"Importância global dos {SHAP_TOP_FEATURES} atributos de maior média do valor "
        f"absoluto de SHAP para a classe {MALICIOUS}, equivalente à Fig. 5 do artigo, no "
        f"Random Forest base {first['explained_base']}, dataset {SHAP_RUNS[dataset][2]}, nas "
        f"duas leituras de profundidade. Amostra de {first['sample_per_class_requested']} "
        f"fluxos por classe do treino; seed {SEED_FIEL}."
    )
    return Plot(f"shap_importancia_{dataset}", figure, caption, SHAP_SOURCE)


def dependence_figure(results_dir: Path, dataset: str, runs: dict) -> Plot:
    """Dependência do valor SHAP de Duration e de FlowBytesSent (equivalente à Fig. 6)."""
    # Painel (a): Duration, com o limiar que o artigo lê na figura. Painel (b):
    # FlowBytesSent colorido por FlowBytesReceived, em escala logarítmica, porque
    # os dois atributos cobrem várias ordens de grandeza.
    panels = [
        ("Duration", "s", "Duration", "s", False),
        ("FlowBytesSent", "bytes", "FlowBytesReceived", "bytes", True),
    ]
    figure = Figure(figsize=(PAGE_WIDTH, 4.4), layout="constrained")
    axes = figure.subplots(len(READINGS), len(panels))
    for row_axes, track in zip(axes, READINGS, strict=True):
        points = pd.read_csv(shap_run_dir(results_dir, dataset, track) / "fig6_dependencia.csv")
        for axis, letter, (column, unit, color, color_unit, log_scale) in zip(
            row_axes, "ab", panels, strict=True
        ):
            drawn = axis.scatter(
                points[column],
                points[f"shap_{column}"],
                c=points[color],
                cmap="coolwarm",
                norm=LogNorm() if log_scale else None,
                s=2,
                rasterized=True,
            )
            axis.axhline(0, color="black", linewidth=0.6)
            if log_scale:
                axis.set_xscale("log")
            else:
                axis.axvline(
                    ARTICLE_DURATION_THRESHOLD_SECONDS, color="black", linestyle="--", linewidth=0.6
                )
            scale = ", escala logarítmica" if log_scale else ""
            axis.set_xlabel(f"({letter}) {column} ({unit}{scale})")
            axis.set_ylabel(f"SHAP de {column}")
            axis.set_title(f"{READINGS[track].capitalize()} (trilha {track})")
            figure.colorbar(drawn, ax=axis, label=f"{color} ({color_unit})")
    first = runs[dataset, "fiel"]
    caption = (
        "Dependência do valor SHAP, equivalente à Fig. 6 do artigo: efeito de (a) Duration e "
        f"de (b) FlowBytesSent na probabilidade de {MALICIOUS}, um ponto por fluxo da amostra "
        f"do teste, no Random Forest base {first['explained_base']}, dataset "
        f"{SHAP_RUNS[dataset][2]}, nas duas leituras de profundidade. A linha tracejada marca "
        f"os {ARTICLE_DURATION_THRESHOLD_SECONDS} s que o artigo aponta como limiar. "
        f"Seed {SEED_FIEL}."
    )
    return Plot(f"shap_dependencia_{dataset}_dupla", figure, caption, SHAP_SOURCE)


def local_figure(dataset: str, runs: dict) -> Plot:
    """Explicação de um fluxo malicioso e de um Non-DoH (equivalentes às Figs. 7 e 8)."""
    figure = Figure(figsize=(PAGE_WIDTH, 5.0), layout="constrained")
    explained = list(runs[dataset, "fiel"]["local"])
    axes = figure.subplots(len(READINGS), len(explained))
    for row_axes, track in zip(axes, READINGS, strict=True):
        for axis, key in zip(row_axes, explained, strict=True):
            explanation = runs[dataset, track]["local"][key]
            start, *features, end = explanation["contributions"]
            labels = [
                entry["item"]
                if entry["value"] is None
                else f"{entry['item']} = {entry['value']:.4g}"
                for entry in features
            ]
            effects = [entry["effect_pp"] for entry in features]
            colors = [SERIES_COLORS[0] if effect >= 0 else SERIES_COLORS[1] for effect in effects]
            axis.barh(labels, effects, color=colors)
            axis.invert_yaxis()
            axis.axvline(0, color="black", linewidth=0.6)
            axis.tick_params(axis="y", labelsize=6)
            # Título alinhado à direita: os rótulos longos do eixo estreitam o painel.
            axis.set_title(
                f"{key}, {READINGS[track]}: {explanation['explained_class']}\n"
                f"média {start['effect_pp']:.1f}% → predição {end['effect_pp']:.1f}%",
                loc="right",
            )
            axis.set_xlabel("Contribuição (pontos percentuais)")
    first = runs[dataset, "fiel"]
    caption = (
        "Explicação local de dois fluxos do teste, equivalentes às Figs. 7 e 8 do artigo: "
        "contribuição de cada atributo (com o valor dele no fluxo) para a probabilidade da "
        f"classe explicada, no Random Forest base {first['explained_base']}, dataset "
        f"{SHAP_RUNS[dataset][2]}, nas duas leituras de profundidade. A contribuição soma-se à "
        "média da população para dar a probabilidade predita, indicadas no título de cada "
        f"painel. Azul aumenta a probabilidade e laranja a reduz. Seed {SEED_FIEL}."
    )
    return Plot(f"shap_local_{dataset}_dupla", figure, caption, SHAP_SOURCE)


def shap_figures(results_dir: Path) -> list[Plot]:
    """Figuras de explicabilidade nos dois datasets: importância, dependência e explicação local."""
    runs = shap_runs(results_dir)
    plots = []
    for dataset in SHAP_RUNS:
        plots += [
            importance_figure(results_dir, dataset, runs),
            dependence_figure(results_dir, dataset, runs),
            local_figure(dataset, runs),
        ]
    return plots


def tunnel_tool_figure(results_dir: Path) -> list[Plot]:
    """Distribuição por ferramenta dos dois atributos da Fig. 9 do artigo."""
    folder = run_dir(results_dir, "e7", "dados", "fig9", SEED_FIEL)
    curves = pd.read_csv(folder / "fig9_curvas.csv")
    kinds = {
        "densidade_normal": "Curva normal com a média e o desvio medidos",
        "densidade_histograma": "Histograma dos fluxos",
    }
    figure = Figure(figsize=(PAGE_WIDTH, 3.8), layout="constrained")
    axes = figure.subplots(len(kinds), len(FIG9_PANELS))
    for row_axes, (key, title) in zip(axes, kinds.items(), strict=True):
        for axis, letter, (column, unit, _, _) in zip(row_axes, "ab", FIG9_PANELS, strict=True):
            panel = curves[curves["atributo"] == column]
            for (tool, curve), color in zip(
                panel.groupby("ferramenta"), SERIES_COLORS, strict=False
            ):
                axis.plot(curve["x"], curve[key], color=color, label=tool)
            axis.set_title(title)
            axis.set_xlabel(f"({letter}) {column} ({unit})")
            axis.set_ylabel("Densidade" if unit == "sem unidade" else f"Densidade (1/{unit})")
            axis.set_ylim(bottom=0)
    axes[0][0].legend(title="Ferramenta")
    caption = (
        "Distribuição de (a) ResponseTimeTimeSkewFromMode e (b) PacketTimeVariance por "
        "ferramenta de túnel, equivalente à Fig. 9 do artigo. Em cima, a curva normal com a "
        "média e o desvio padrão medidos, que é o tipo de gráfico do artigo; embaixo, o "
        "histograma dos mesmos fluxos, que a curva normal resume."
    )
    return [
        Plot(
            "fig9_ferramentas_dupla",
            figure,
            caption,
            f"results/{folder.relative_to(results_dir)}/fig9_curvas.csv",
        )
    ]


def tool_recall_figure(results_dir: Path) -> list[Plot]:
    """Recall por ferramenta na transferência e nos retreinos, nas duas leituras."""
    figure = Figure(figsize=(COLUMN_WIDTH, 4.2), layout="constrained")
    axis = figure.subplots()
    tools = list(TOOL_ORIGIN)
    bars = [(scenario, track) for scenario in SCENARIOS for track in READINGS]
    height = 0.8 / len(bars)
    for index, (scenario, track) in enumerate(bars):
        by_tool = tool_recalls(load_run(results_dir, "e6", track, scenario))
        present = [tool for tool in tools if tool in by_tool]
        recall = np.array([100 * by_tool[tool]["recall"] for tool in present])
        low = np.array([100 * by_tool[tool]["recall_ci_low"] for tool in present])
        high = np.array([100 * by_tool[tool]["recall_ci_high"] for tool in present])
        axis.barh(
            [tools.index(tool) + (index - (len(bars) - 1) / 2) * height for tool in present],
            recall,
            height=height,
            xerr=[recall - low, high - recall],
            color=SERIES_COLORS[list(SCENARIOS).index(scenario)],
            # A leitura de profundidade 5 vai em tom claro e a variável, em tom cheio.
            alpha=0.45 if track == "fiel" else 1.0,
            error_kw={"linewidth": 0.6},
            label=f"{SCENARIOS[scenario]}, {READINGS[track]}",
        )
    axis.set_yticks(range(len(tools)), labels=[f"{tool}\n({TOOL_ORIGIN[tool]})" for tool in tools])
    axis.invert_yaxis()
    axis.set_xlabel("Recall de Malicious-DoH (%)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=1)
    level = tool_recalls(load_run(results_dir, "e6", "fiel", "transferencia"))
    level = next(iter(level.values()))["recall_ci_level"]
    caption = (
        "Recall de Malicious-DoH por ferramenta de túnel no segundo dataset: transferência do "
        "modelo treinado no CIRA para o HKD (só as três ferramentas do HKD), retreino no "
        "combinado como publicado e retreino no combinado sem réplicas, nas duas leituras de "
        f"profundidade. As barras de erro são o intervalo de confiança de {level:.0%}. "
        f"Trilhas fiel e variante; seed {SEED_FIEL}."
    )
    return [Plot("segundo_recall_ferramenta", figure, caption, E6_SOURCE)]


def seed_distribution_figure(results_dir: Path) -> list[Plot]:
    """Distribuição por seed do recall de Benign-DoH e do F1 macro, no protocolo corrigido."""
    summary = read_json(results_dir / "e4" / "corrigida" / "summary.json")
    track, seeds = summary["track"], summary["seeds"]
    # Só os modelos de profundidade variável: os de profundidade 5 têm recall de
    # Benign-DoH perto de zero e achatariam a escala.
    slices = {
        name: ("e4", name)
        for name, config in CORRIGIDA_MODELS.items()
        if config["max_depth"] != MAX_DEPTH
    }
    modified = f"{MODIFIED_SELECTED_MODEL}-cira"
    if (results_dir / "e8" / track / modified).exists():
        slices[MODIFIED_SELECTED_MODEL] = ("e8", modified)
    panels = {"Recall de Benign-DoH (%)": [], "F1 macro (%)": []}
    for experiment, run_slice in slices.values():
        tests = [
            load_run(results_dir, experiment, track, run_slice, seed)["test"] for seed in seeds
        ]
        panels["Recall de Benign-DoH (%)"].append(
            [100 * test["per_class"]["Benign-DoH"]["recall"] for test in tests]
        )
        panels["F1 macro (%)"].append([100 * test["macro_f1"] for test in tests])
    figure = Figure(figsize=(COLUMN_WIDTH, 2.4), layout="constrained")
    axes = figure.subplots(1, len(panels))
    offsets = np.linspace(-0.2, 0.2, len(seeds))
    for axis, (label, values) in zip(axes, panels.items(), strict=True):
        for position, (model_values, color) in enumerate(zip(values, SERIES_COLORS, strict=False)):
            axis.scatter(position + offsets, model_values, s=8, color=color)
            axis.hlines(
                np.mean(model_values), position - 0.3, position + 0.3, color="black", linewidth=0.8
            )
        axis.set_xticks(range(len(slices)), labels=list(slices))
        axis.set_xlabel("Modelo")
        axis.set_ylabel(label)
    caption = (
        "Distribuição por seed do recall de Benign-DoH e do F1 macro no teste do CIRA, nos "
        f"modelos de profundidade variável do protocolo corrigido ({', '.join(slices)}): um "
        f"ponto por seed ({len(seeds)} seeds) e a média em traço. Trilha {track}."
    )
    source = "results/e4/corrigida/<modelo>/seed<k>/metrics.json; results/e8/corrigida/M1M2-cira/"
    return [Plot("corrigido_seeds", figure, caption, source)]


# Escrita.


def tex_cell(cell: str) -> str:
    """Escreve uma célula em LaTeX: vírgula decimal nos números e símbolos trocados."""
    text = str(cell)
    if isinstance(cell, Num):
        text = text.replace(".", ",").replace("-", "−")
    for symbol, replacement in TEX_SYMBOLS.items():
        text = text.replace(symbol, replacement)
    return text


def tex_lines(table: Table) -> list[str]:
    """Linhas do ambiente tabular de uma tabela, com \\hline como no template."""
    rows = [row for row in table.rows if row is not None]
    # Coluna só de números (ou de traço de célula vazia) alinha à direita.
    align = "".join(
        "r" if all(isinstance(row[index], Num) or row[index] == MISSING for row in rows) else "l"
        for index in range(len(table.header))
    )
    lines = [f"\\begin{{tabular}}{{{align}}}", "\\hline"]
    if table.groups:
        cells = [
            f"\\multicolumn{{{span}}}{{c}}{{\\textbf{{{tex_cell(label)}}}}}"
            for label, span in table.groups
        ]
        lines.append(" & ".join(cells) + " \\\\")
    header = " & ".join(f"\\textbf{{{tex_cell(name)}}}" for name in table.header)
    lines.append(header + " \\\\ \\hline")
    for row in table.rows:
        lines.append("\\hline" if row is None else " & ".join(map(tex_cell, row)) + " \\\\")
    return [*lines, "\\hline", "\\end{tabular}"]


def csv_header(table: Table) -> list[str]:
    """Cabeçalho do CSV: o nome da coluna, precedido do grupo quando há dois níveis."""
    if not table.groups:
        return table.header
    prefixes = [label for label, span in table.groups for _ in range(span)]
    return [f"{prefix} {name}".strip() for prefix, name in zip(prefixes, table.header, strict=True)]


def write_table(table: Table, tables_dir: Path) -> None:
    """Grava a tabela em .tex e em .csv, com as mesmas células."""
    assert all(row is None or len(row) == len(table.header) for row in table.rows), table.name
    (tables_dir / f"{table.name}.tex").write_text(
        "\n".join(tex_lines(table)) + "\n", encoding="utf-8"
    )
    with (tables_dir / f"{table.name}.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(csv_header(table))
        writer.writerows(row for row in table.rows if row is not None)


def write_plot(plot: Plot, figures_dir: Path) -> None:
    """Grava a figura em PDF vetorial e em PNG."""
    for suffix, metadata in FIGURE_METADATA.items():
        plot.figure.savefig(figures_dir / f"{plot.name}.{suffix}", dpi=PNG_DPI, metadata=metadata)


def index_text(assets: list[Table | Plot], skipped: list[str]) -> str:
    """Escreve o índice: arquivo, origem em results/ e legenda sugerida de cada item."""
    lines = [
        "# Índice das tabelas e figuras",
        "",
        "Gerado por `scripts/make_report_assets.py` a partir de `results/` e de `config.py`. Não "
        "edite à mão: rode o script de novo.",
        "",
        "Cada tabela tem um `.tex` (ambiente `tabular`, para `\\input` dentro de `table` ou de "
        "`table*`) e um `.csv` com as mesmas células; cada figura, um `.pdf` e um `.png`. O "
        "sufixo `_dupla` marca o que precisa da largura da página (`table*` ou `figure*`). A "
        "legenda sugerida diz o que o item mostra, a trilha, a seed e o nome da média.",
        "",
        "As tabelas foram dimensionadas para `\\footnotesize` com `\\tabcolsep` de 3pt. As que "
        "ainda passam da largura cabem com `\\resizebox{\\columnwidth}{!}{...}` em volta do "
        "`\\input` (`\\textwidth` nas de sufixo `_dupla`); o `graphicx` já está no template. "
        "Nos `.tex` o separador decimal é a vírgula; nos `.csv` e nos eixos das figuras, o ponto.",
        "",
        "| Arquivo | Origem | Legenda sugerida |",
        "| --- | --- | --- |",
    ]
    for asset in assets:
        folder, suffixes = (
            ("tables", "tex, csv") if isinstance(asset, Table) else ("figures", "pdf, png")
        )
        caption = asset.caption.replace("|", "\\|")
        lines.append(f"| `{folder}/{asset.name}` ({suffixes}) | `{asset.source}` | {caption} |")
    if skipped:
        lines += ["", "## Não gerado", "", *(f"- {item}" for item in skipped)]
    return "\n".join(lines) + "\n"


# Resultados obrigatórios: execuções (experimento, trilha, recorte) e arquivos de figura.
REQUIRED_RUNS = (
    [("e0", "dados", "cira"), ("e7", "dados", "fig9")]
    + [("e1", track, run_slice) for track, run_slice in SYSTEM_SLICES.items()]
    + [("e5", track, run_slice) for track, run_slice in SYSTEM_SLICES.items()]
    + [("e2", "fiel", model) for model in BASELINES]
    + [("e6", "fiel", f"retreino_sem_replicas-{model}") for model in BASELINES]
    + [("e6", "dados", name) for name in ["hkd", "combinado", "combinado_sem_replicas"]]
    + [
        ("e6", track, scenario)
        for track in READINGS
        for scenario in [*SCENARIOS, "retreino_sem_replicas-shap"]
    ]
    + [("e7", track, "ferramenta") for track in READINGS]
)
REQUIRED_FILES = [
    E0_RUN / "split_counts.json",
    E0_RUN / "fig2_densidade.csv",
    Path("e7") / "dados" / "fig9" / f"seed{SEED_FIEL}" / "fig9_curvas.csv",
]
REQUIRED_BUILDERS = [
    cira_counts_table,
    capture_table,
    second_dataset_counts_table,
    second_dataset_tools_table,
    confusion_tables,
    reproduction_metrics_table,
    table_ii_tables,
    literature_table,
    timings_table,
    meta_decision_table,
    shap_ranking_table,
    shap_stability_table,
    second_dataset_metrics_table,
    second_dataset_baselines_table,
    second_dataset_confusion_table,
    tool_recall_table,
    replicas_table,
    tunnel_tool_table,
    density_figure,
    confusion_figures,
    shap_figures,
    tunnel_tool_figure,
    tool_recall_figure,
]
# Opcionais: o arquivo de que dependem, o que são e as funções que os geram.
OPTIONAL_BUILDERS = [
    (
        Path("e3") / "variante" / "comparacao.csv",
        "sensibilidade às leituras alternativas",
        [sensitivity_table],
    ),
    (
        Path("e4") / "corrigida" / "summary.json",
        "protocolo corrigido em dez seeds, taxa base e avaliação por máquina",
        [
            corrected_metrics_table,
            duplicates_table,
            base_rate_table,
            group_folds_table,
            seed_distribution_figure,
        ],
    ),
    (
        Path("e8") / "corrigida" / "summary.json",
        "modificação proposta pela equipe",
        [modification_metrics_table, modification_paired_table, modification_transfer_table],
    ),
    (
        Path("e8") / "corrigida" / "summary-robustez.json",
        "robustez à fragmentação dos fluxos",
        [robustness_table, robustness_figure],
    ),
]


def check_required(results_dir: Path) -> None:
    """Falha, com a lista do que falta, se algum resultado obrigatório não existe."""
    paths = [
        run_dir(results_dir, experiment, track, run_slice, SEED_FIEL) / "metrics.json"
        for experiment, track, run_slice in REQUIRED_RUNS
    ] + [results_dir / relative for relative in REQUIRED_FILES]
    missing = [str(path.relative_to(results_dir)) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltam resultados obrigatórios em results/: " + ", ".join(missing))


def build_assets(results_dir: Path) -> tuple[list[Table | Plot], list[str]]:
    """Monta as tabelas e as figuras; devolve também os itens opcionais não gerados."""
    check_required(results_dir)
    builders, skipped = list(REQUIRED_BUILDERS), []
    for relative, description, optional in OPTIONAL_BUILDERS:
        if (results_dir / relative).exists():
            builders += optional
        else:
            skipped.append(f"{description} (falta results/{relative.as_posix()})")
    assets = []
    with matplotlib.rc_context(FIGURE_STYLE):
        for builder in builders:
            assets += builder(results_dir)
    return assets, skipped


def make_assets(results_dir: Path = RESULTS_DIR, report_dir: Path = REPORT_DIR) -> list[str]:
    """Grava as tabelas, as figuras e o índice; devolve os itens opcionais não gerados."""
    assets, skipped = build_assets(results_dir)
    tables_dir, figures_dir = report_dir / "tables", report_dir / "figures"
    # As duas pastas só têm arquivo gerado: são refeitas do zero, para não
    # sobrar tabela de um resultado que deixou de existir.
    for folder in [tables_dir, figures_dir]:
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
    # O estilo vale também na gravação, que é quando a figura é desenhada.
    with matplotlib.rc_context(FIGURE_STYLE):
        for asset in assets:
            if isinstance(asset, Table):
                write_table(asset, tables_dir)
            else:
                write_plot(asset, figures_dir)
    (report_dir / "INDICE.md").write_text(index_text(assets, skipped), encoding="utf-8")
    return skipped


def main() -> None:
    """Gera os artefatos do relatório e lista o que foi gravado e o que não foi gerado."""
    skipped = make_assets()
    for folder in ["tables", "figures"]:
        files = sorted(path.name for path in (REPORT_DIR / folder).iterdir())
        print(f"report/{folder}: {len(files)} arquivos")
        for name in files:
            print(f"  {name}")
    for item in skipped:
        print(f"não gerado: {item}")


if __name__ == "__main__":
    main()
