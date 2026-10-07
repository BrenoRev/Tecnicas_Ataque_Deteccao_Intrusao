"""E6: resumos do segundo dataset e tabela final, a partir dos metrics.json.

Não treina nada. Lê os metrics.json gravados em results/e6/ por
scripts/e6_dataset2.py (o sistema do artigo) e por scripts/e6_baselines_xai.py
(modelos de comparação e SHAP), e os do CIRA-CIC-DoHBrw-2020 em results/e1/,
results/e2/ e results/e5/. Escreve:

- results/e6/RESUMO.md: a tabela final do segundo dataset, com o CIRA ao lado
  do combinado sem réplicas para o sistema nas duas leituras de profundidade e
  para os três modelos de comparação, o recall por ferramenta, o ranking SHAP
  ao lado do do CIRA e, em bloco separado, o combinado como publicado e a
  transferência;
- results/e6/<trilha>/RESUMO.md: a leitura dos números de cada trilha. Os
  modelos de comparação ficam no da trilha `fiel`, onde estão gravados.

Roda como módulo, a partir da pasta do projeto, porque importa os outros scripts.

Uso: uv run python -m scripts.e6_resumo
"""

import json
from pathlib import Path

import scripts.e2_baselines as e2
import scripts.e5_xai as e5
import scripts.e6_baselines_xai as e6b
import scripts.e6_dataset2 as e6
from doh_ids.config import (
    ARTICLE_DURATION_THRESHOLD_SECONDS,
    CLASS_NAMES,
    FEATURE_COLUMNS,
    HKD_REPLICAS,
    RESULTS_DIR,
    SEED_FIEL,
    SHAP_TOP_FEATURES,
)

E6_DIR = RESULTS_DIR / "e6"
UNIQUE_SLICE = e6b.SCENARIO["slice_name"]
MALICIOUS_NAME = "Malicious-DoH"
CIRA, COMBINED = "CIRA", "combinado sem réplicas"


def load_metrics(slice_dir: Path) -> dict:
    """Lê o metrics.json da seed 42 gravado na pasta de um recorte."""
    path = slice_dir / f"seed{SEED_FIEL}" / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_reading(reading: dict) -> dict:
    """Lê os resultados de uma leitura de profundidade.

    Devolve as métricas de cada cenário do sistema pelo nome do recorte, as do
    SHAP no combinado sem réplicas em `shap` e as do CIRA na mesma leitura em
    `e1` (reprodução) e `e5` (SHAP).
    """
    track_dir = E6_DIR / reading["track"]
    # A explicação no CIRA usa, em cada trilha, a mesma pasta da reprodução.
    result = {
        "e1": load_metrics(e6.E1_DIR / reading["track"] / reading["e1_slice"]),
        "e5": load_metrics(RESULTS_DIR / "e5" / reading["track"] / reading["e1_slice"]),
        e6.TRANSFER_SLICE: load_metrics(track_dir / e6.TRANSFER_SLICE),
        "shap": load_metrics(track_dir / e6b.SHAP_SLICE),
    }
    for scenario in e6.RETRAINS:
        result[scenario["slice_name"]] = load_metrics(track_dir / scenario["slice_name"])
    return result


def load_baselines() -> dict:
    """Lê, para cada modelo de comparação, as métricas no CIRA e no combinado sem réplicas."""
    combined_dir = E6_DIR / e6b.BASELINE_TRACK
    return {
        name: {
            CIRA: load_metrics(RESULTS_DIR / "e2" / "fiel" / name),
            COMBINED: load_metrics(combined_dir / e6b.baseline_slice(name)),
        }
        for name in e2.BASELINES
    }


def recall_cell(entry: dict) -> str:
    """Escreve um recall com os detectados sobre `n` e o intervalo de confiança."""
    return (
        f"{entry['recall']:.2%} ({entry['detected']}/{entry['n']}; "
        f"{entry['recall_ci_low']:.2%} a {entry['recall_ci_high']:.2%})"
    )


def model_row(model: str, dataset: str, evaluated: str, metrics: dict, hkd: str) -> list:
    """Monta a linha da tabela final para um modelo avaliado em um conjunto."""
    per_class = metrics["per_class"]
    # A validação cruzada grava só a matriz de confusão: sem probabilidade, não há AUC.
    auc = f"{metrics['roc_auc_ovr_macro']:.6f}" if "roc_auc_ovr_macro" in metrics else "não medido"
    return [
        model,
        dataset,
        evaluated,
        metrics["total"],
        f"{metrics['accuracy']:.4%}",
        f"{metrics['macro_f1']:.4%}",
        f"{metrics['weighted_f1']:.4%}",
        f"{per_class['Non-DoH']['recall']:.4%}",
        f"{per_class['Benign-DoH']['recall']:.4%}",
        f"{per_class[MALICIOUS_NAME]['recall']:.4%}",
        f"{per_class[MALICIOUS_NAME]['precision']:.4%}",
        f"{metrics['malicious_vs_rest']['fpr']:.4%}",
        auc,
        hkd,
    ]


def system_label(reading: dict) -> str:
    """Devolve o nome do sistema do artigo em uma leitura de profundidade."""
    return f"Sistema do artigo, {reading['label']}"


def final_rows(results: list[tuple[dict, dict]], baselines: dict) -> list[list]:
    """Monta as linhas da tabela final: cada modelo no CIRA e no combinado sem réplicas."""
    no_hkd, not_measured = "sem fluxos do HKD", "não medido"
    rows = []
    for reading, result in results:
        e1, unique, label = result["e1"], result[UNIQUE_SLICE], system_label(reading)
        hkd = recall_cell(unique["test_recall_by_origin"]["HKD"])
        rows += [
            model_row(label, CIRA, "teste", e1["test"], no_hkd),
            model_row(label, COMBINED, "teste", unique["test"], hkd),
            model_row(label, CIRA, "validação cruzada", e1["cross_validation"], no_hkd),
            model_row(
                label, COMBINED, "validação cruzada", unique["cross_validation"], not_measured
            ),
        ]
    for name, metrics in baselines.items():
        label, combined = e2.BASELINES[name]["label"], metrics[COMBINED]
        hkd = recall_cell(combined["test_recall_by_origin"]["HKD"])
        rows += [
            model_row(label, CIRA, "teste", metrics[CIRA]["test"], no_hkd),
            model_row(label, COMBINED, "teste", combined["test"], hkd),
        ]
    return rows


def combined_models(results: list[tuple[dict, dict]], baselines: dict) -> dict:
    """Leva o nome de cada modelo às métricas dele no combinado sem réplicas."""
    models = {system_label(reading): result[UNIQUE_SLICE] for reading, result in results}
    for name, metrics in baselines.items():
        models[e2.BASELINES[name]["label"]] = metrics[COMBINED]
    return models


def tools_table(models: dict) -> str:
    """Escreve o recall de Malicious-DoH por ferramenta no teste, um modelo por coluna."""
    first = next(iter(models.values()))
    rows = [
        [name, *[recall_cell(metrics["test_recall_by_tool"][name]) for metrics in models.values()]]
        for name in first["test_recall_by_tool"]
    ]
    rows += [
        [
            f"ferramentas do {origin} juntas",
            *[recall_cell(metrics["test_recall_by_origin"][origin]) for metrics in models.values()],
        ]
        for origin in first["test_recall_by_origin"]
    ]
    return e6.markdown_table(["ferramenta", *models], rows)


def detection_lines(models: dict) -> str:
    """Escreve, para cada modelo no combinado sem réplicas, a leitura em termos de detecção."""
    lines = []
    for label, metrics in models.items():
        hkd, binary = metrics["test_recall_by_origin"]["HKD"], metrics["test"]["malicious_vs_rest"]
        benign = metrics["test"]["per_class"]["Benign-DoH"]["recall"]
        lines.append(
            f"- **{label}.** Recall das ferramentas do HKD de {hkd['recall']:.2%}: de {hkd['n']} "
            f"túneis de dnstt, tcp-over-dns e tuns no teste, {hkd['n'] - hkd['detected']} passam "
            f"sem alerta (intervalo de confiança de 95%: de {hkd['recall_ci_low']:.2%} a "
            f"{hkd['recall_ci_high']:.2%}). FPR de Malicious-DoH contra o resto de "
            f"{binary['fpr']:.4%}: {binary['false_positives']} de {binary['negatives']} fluxos "
            f"legítimos viram alarme falso. Recall de Benign-DoH de {benign:.2%}."
        )
    return "\n".join(lines)


def duration_ranks(shap: dict) -> list[int]:
    """Devolve o posto de `Duration` no ranking de Malicious-DoH de cada base."""
    return [by_class[MALICIOUS_NAME].index("Duration") + 1 for by_class in shap["ranking"].values()]


def declared_lines(results: list[tuple[dict, dict]], baselines: dict) -> str:
    """Põe os números ao lado do que o script dos modelos de comparação declarou como inesperado."""
    reading, result = results[0]
    system = result[UNIQUE_SLICE]["test_recall_by_origin"]["HKD"]
    lines = [
        f"1. Recall das ferramentas do HKD dos modelos de comparação ao lado do intervalo de "
        f"confiança do sistema na leitura {reading['label']} (de {system['recall_ci_low']:.2%} a "
        f"{system['recall_ci_high']:.2%}):"
    ]
    for name, metrics in baselines.items():
        recall = metrics[COMBINED]["test_recall_by_origin"]["HKD"]["recall"]
        position = "abaixo do" if recall < system["recall_ci_low"] else "dentro ou acima do"
        lines.append(f"   - {e2.BASELINES[name]['label']}: {recall:.2%}, {position} intervalo.")
    lines.append(
        f"2. Posto de `Duration` no ranking de {MALICIOUS_NAME} dos três bases treinados no "
        "combinado sem réplicas:"
    )
    for reading, result in results:
        ranks = ", ".join(map(str, duration_ranks(result["shap"])))
        lines.append(f"   - {reading['label']}: {ranks}.")
    return "\n".join(lines)


def shap_ranking_table(shap: dict, e5_metrics: dict) -> str:
    """Põe os primeiros atributos de Malicious-DoH no CIRA ao lado dos de cada base no combinado."""
    base = f"base_{shap['explained_base']}"
    cira_top = e5_metrics["ranking"][base][MALICIOUS_NAME][:SHAP_TOP_FEATURES]
    columns = ["posto", f"CIRA, base {shap['explained_base']}"]
    columns += [f"combinado, {name.replace('_', ' ')}" for name in shap["ranking"]]
    rows = [
        [rank + 1, cira_top[rank], *[by[MALICIOUS_NAME][rank] for by in shap["ranking"].values()]]
        for rank in range(SHAP_TOP_FEATURES)
    ]
    return e6.markdown_table(columns, rows)


def shap_agreement_rows(shap: dict, prefix: list) -> list[list]:
    """Monta as linhas de concordância com o CIRA, por base e classe, depois de `prefix`."""
    return [
        [
            *prefix,
            base.replace("_", " "),
            class_name,
            f"{by_class[class_name]['spearman_all_features']:.3f}",
            f"{by_class[class_name]['top_agreement']:.3f}",
            by_class[class_name]["top_shared"],
        ]
        for base, by_class in shap["cira_comparison"].items()
        for class_name in CLASS_NAMES
    ]


AGREEMENT_COLUMNS = [
    "base",
    "classe",
    f"Spearman nos {len(FEATURE_COLUMNS)} atributos",
    f"Spearman na união dos {SHAP_TOP_FEATURES} primeiros",
    f"atributos em comum nos {SHAP_TOP_FEATURES} primeiros",
]

AGREEMENT_NOTE = (
    "Correlação de postos de Spearman entre o ranking de importância no combinado sem "
    "réplicas e o do base de mesmo número no CIRA; o valor 1 quer dizer a mesma ordem. O "
    "base de mesmo número não é o mesmo modelo nos dois datasets: cada um foi treinado no seu "
    "subconjunto, depois de outro split."
)


def shap_measures_table(shap: dict, e5_metrics: dict) -> str:
    """Põe as medidas da amostra do teste no combinado ao lado das do CIRA."""
    seconds = ARTICLE_DURATION_THRESHOLD_SECONDS
    measures = [
        ("limiar medido de `Duration` (s)", "best_threshold_seconds", ".2f"),
        (f"SHAP positivo acima de {seconds} s", "positive_fraction_above_article_threshold", ".2%"),
        (f"SHAP positivo até {seconds} s", "positive_fraction_up_to_article_threshold", ".2%"),
    ]
    rows = [
        [
            title,
            *[format(metrics["duration_threshold"][key], spec) for metrics in (e5_metrics, shap)],
        ]
        for title, key, spec in measures
    ]
    rows.append(
        [
            "base concorda com o empilhado",
            *[
                f"{metrics['base_agrees_with_stacked_fraction']:.2%}"
                for metrics in (e5_metrics, shap)
            ],
        ]
    )
    return e6.markdown_table(["medida", "CIRA (E5)", COMBINED], rows)


def local_lines(shap: dict) -> str:
    """Escreve as duas explicações locais gravadas, um fluxo por linha."""
    lines = []
    for figure_name, file_name, _ in e5.LOCAL_FIGURES:
        explanation = shap["local"][figure_name]
        rows = explanation["contributions"]
        population, top, final = rows[0], rows[1], rows[-1]
        lines.append(
            f"- `{file_name}.png` e `{file_name}.csv`: fluxo {explanation['explained_class']} do "
            f"teste. Probabilidade da classe no base {shap['explained_base']}: "
            f"{final['effect_pp']:.2f}%, a partir da média da população de "
            f"{population['effect_pp']:.2f}%; atributo de maior efeito: `{top['item']}` = "
            f"{top['value']:.6g} ({top['effect_pp']:+.2f} pp). Classe predita pelo base: "
            f"{explanation['base_predicted_class']}; pelo modelo empilhado: "
            f"{explanation['stacked_predicted_class']}."
        )
    return "\n".join(lines)


def shap_section(reading: dict, result: dict) -> str:
    """Escreve a seção do SHAP no combinado sem réplicas para uma leitura de profundidade."""
    shap, e5_metrics = result["shap"], result["e5"]
    train = result[UNIQUE_SLICE]["split"]["train"]
    hkd_tools = result[e6.TRANSFER_SLICE]["hkd"]["by_tool"]
    hkd_train = sum(train["rows_by_tool"][name] for name in hkd_tools)
    malicious_train = train["rows"][CLASS_NAMES.index(MALICIOUS_NAME)]
    run_dir = f"{e6b.SHAP_SLICE}/seed{SEED_FIEL}"
    samples = e6.markdown_table(
        ["amostra", *CLASS_NAMES, "uso"],
        [
            ["treino", *shap["train_sample_rows"], "importância global"],
            ["teste", *shap["test_sample_rows"], "dependência e explicações locais"],
        ],
    )
    over = shap["received_over_sent"]
    return f"""## SHAP dos Random Forests base no combinado sem réplicas

Gerado por `scripts/e6_baselines_xai.py`, com as mesmas funções da explicação
no CIRA (`scripts/e5_xai.py`). Os números vêm de `{run_dir}/metrics.json`; os
do CIRA, de `results/e5/{reading["track"]}/`. O sistema explicado é o do retreino
no combinado sem réplicas nesta leitura: mesma seed, mesmo split e mesmos
subconjuntos de `{UNIQUE_SLICE}/`. Não há figura do artigo para este dataset: o
que fica ao lado é a explicação no CIRA.

### Amostras

Duas amostras estratificadas de até {shap["sample_per_class_requested"]} fluxos por classe,
sorteadas com a seed {SEED_FIEL}, como no CIRA. O sorteio é feito na classe
{MALICIOUS_NAME} inteira, sem separar por ferramenta, e o número de fluxos de cada
ferramenta na amostra não é gravado. No treino, {hkd_train} dos {malicious_train} fluxos da
classe são do HKD ({hkd_train / malicious_train:.2%}): pelo sorteio, a amostra de {MALICIOUS_NAME}
é quase toda de fluxos das ferramentas do CIRA, e a importância medida reflete
sobretudo esses fluxos.

{samples}

A tabela `{run_dir}/importancia.csv` traz a média do valor absoluto de SHAP
por base, classe e atributo. As figuras, na mesma pasta, são as equivalentes às
Figs. 5 a 8 do artigo e usam o Random Forest base {shap["explained_base"]}.

### Ranking de {MALICIOUS_NAME} ao lado do CIRA

{shap_ranking_table(shap, e5_metrics)}

{e6.markdown_table(AGREEMENT_COLUMNS, shap_agreement_rows(shap, []))}

{AGREEMENT_NOTE}

### Estabilidade entre os três submodelos

Correlação de postos de Spearman entre os rankings de dois bases, sobre os
atributos que estão entre os {shap["stability_top_features"]} primeiros de pelo menos um deles.

{e5.stability_table(shap)}

### Dependência e explicações locais

Medidas do Random Forest base {shap["explained_base"]} na amostra do teste. O limiar de
{ARTICLE_DURATION_THRESHOLD_SECONDS} segundos é a leitura que o artigo faz da Fig. 6a, no CIRA;
aqui ele é só a linha de referência das figuras.

{shap_measures_table(shap, e5_metrics)}

Fluxos da amostra com mais bytes recebidos que enviados, por classe real:
{over["rows_by_class"]}; o valor SHAP de `FlowBytesSent` para {MALICIOUS_NAME} é positivo em
{over["positive_fraction"]:.2%} deles e em {over["positive_fraction_others"]:.2%} dos demais.

{local_lines(shap)}

### Limitação

{e5.limitation_text(shap)}

Os valores SHAP são calculados em amostras, com uma seed. O fluxo de cada
explicação local é o primeiro da classe na amostra do teste e pode ser de
qualquer ferramenta.
"""


def baselines_section(baselines: dict) -> str:
    """Escreve a seção dos modelos de comparação no combinado sem réplicas."""
    first = next(iter(baselines.values()))[COMBINED]
    details = "\n\n".join(
        e2.baseline_text(e2.BASELINES[name]["label"], metrics[COMBINED]["test"])
        + "\n\nRecall de Malicious-DoH por ferramenta no teste:\n\n"
        + e6.recall_table(metrics[COMBINED]["test_recall_by_tool"])
        for name, metrics in baselines.items()
    )
    return f"""## Modelos de comparação da Tabela II no combinado sem réplicas

Gerado por `scripts/e6_baselines_xai.py`, com as mesmas funções dos modelos de
comparação no CIRA (`scripts/e2_baselines.py`). Os números vêm de
`{e6b.baseline_slice("<modelo>")}/seed{SEED_FIEL}/metrics.json`. Os três modelos não
dependem da leitura de profundidade dos Random Forests base; ficam nesta trilha
porque seguem a Tabela II do artigo, como no CIRA.

Mesmo split e mesmo teste do sistema do artigo em `{UNIQUE_SLICE}/` (conferido
por asserção no script: total, fluxos por classe e fluxos por ferramenta):
{first["test"]["total"]} fluxos, por classe {first["test_rows"]}. O normalizador é ajustado no
treino. O treino inteiro é balanceado com SMOTE: de {first["train_rows"]} fluxos por
classe passa a {first["balanced_train_rows"]}, com {first["synthetic_train_rows"]} amostras
sintéticas. A árvore de decisão tem profundidade máxima {e2.TABLE_II_TREE_DEPTH} e o Random Forest,
{e2.TABLE_II_FOREST_TREES} árvores; os outros hiperparâmetros ficam no padrão do scikit-learn e do
XGBoost. A Tabela II não traz número para este dataset: os mesmos modelos no
CIRA estão ao lado em `../RESUMO.md`.

{details}

Não há validação cruzada nem busca de hiperparâmetros dos modelos de
comparação, como no CIRA. Uma execução por modelo, com a seed {SEED_FIEL}.
"""


def track_text(reading: dict, result: dict, baselines: dict) -> str:
    """Monta o RESUMO.md de uma trilha: o sistema, o SHAP e, na trilha deles, os baselines."""
    text = e6.summary_text(reading, result) + "\n" + shap_section(reading, result)
    if reading["track"] == e6b.BASELINE_TRACK:
        text += "\n" + baselines_section(baselines)
    return text


def final_shap_text(results: list[tuple[dict, dict]]) -> str:
    """Escreve o bloco do SHAP da tabela final: ranking e concordância nas duas leituras."""
    columns = ["posto"]
    tops = []
    for reading, result in results:
        base = f"base_{result['shap']['explained_base']}"
        columns += [f"{CIRA}, {reading['label']}", f"{COMBINED}, {reading['label']}"]
        tops += [result[key]["ranking"][base][MALICIOUS_NAME] for key in ("e5", "shap")]
    rows = [[rank + 1, *[top[rank] for top in tops]] for rank in range(SHAP_TOP_FEATURES)]
    agreement = [
        row
        for reading, result in results
        for row in shap_agreement_rows(result["shap"], [reading["label"]])
    ]
    samples = "; ".join(
        f"{reading['label']}: treino {result['shap']['train_sample_rows']}, teste "
        f"{result['shap']['test_sample_rows']}"
        for reading, result in results
    )
    explained_base = results[0][1]["shap"]["explained_base"]
    return f"""Valores SHAP dos Random Forests base do sistema retreinado no combinado sem
réplicas, nas mesmas amostras por classe da explicação no CIRA (E5). Fluxos por
classe nas amostras: {samples}.

Primeiros atributos de {MALICIOUS_NAME}, Random Forest base {explained_base}:

{e6.markdown_table(columns, rows)}

Concordância do ranking no combinado sem réplicas com o do CIRA:

{e6.markdown_table(["leitura", *AGREEMENT_COLUMNS], agreement)}

{AGREEMENT_NOTE}"""


FINAL_COLUMNS = [
    "modelo",
    "dataset",
    "avaliado em",
    "fluxos avaliados",
    "acurácia",
    "F1 macro",
    "F1 ponderado",
    "recall de Non-DoH",
    "recall de Benign-DoH",
    "recall de Malicious-DoH",
    "precisão de Malicious-DoH",
    "FPR de Malicious-DoH contra o resto",
    "AUC-ROC one-vs-rest macro",
    "recall das ferramentas do HKD",
]

SCENARIO_COLUMNS = [
    "cenário",
    "leitura",
    "avaliado em",
    "fluxos avaliados",
    "acurácia",
    "F1 macro",
    "recall de Non-DoH",
    "recall de Benign-DoH",
    "recall de Malicious-DoH",
    "precisão de Malicious-DoH",
    "FPR de Malicious-DoH contra o resto",
    "recall das ferramentas do HKD",
]


def final_text(results: list[tuple[dict, dict]], baselines: dict) -> str:
    """Monta o RESUMO.md de E6: a tabela final e os cenários ao lado.

    `results` tem um par (leitura, resultados da leitura) por leitura de
    profundidade; `baselines` é a saída de `load_baselines`.
    """
    models = combined_models(results, baselines)
    scenarios = [row for reading, result in results for row in e6.scenario_rows(reading, result)]
    readings = "\n".join(
        f"- **{reading['label']}:** {reading['base_depth']}. Detalhe em "
        f"`{reading['track']}/RESUMO.md`."
        for reading, _ in results
    )
    tools = "\n\n".join(
        f"{reading['label']}:\n\n{e6.memorization_table(result)}" for reading, result in results
    )
    hypotheses = "\n\n".join(e6.hypothesis_lines(reading, result) for reading, result in results)
    return f"""# E6: o segundo dataset ao lado do CIRA

Gerado por `scripts/e6_resumo.py`, a partir dos `metrics.json` de `results/e6/`
(gravados por `scripts/e6_dataset2.py` e `scripts/e6_baselines_xai.py`) e dos de
`results/e1/`, `results/e2/` e `results/e5/`. Seed {SEED_FIEL}, uma execução de cada
modelo e de cada cenário: não há média nem desvio padrão.

{readings}

O sistema base desta etapa é o de profundidade variável; o de profundidade 5
vai ao lado. O artigo não traz figura nem tabela para o segundo dataset: o que
fica lado a lado é o resultado no CIRA e o do segundo dataset.

- **Combinado sem réplicas:** dataset combinado CIRA + DoH-Tunnel-Traffic-HKD
  com cada fluxo do HKD uma única vez. É o dataset principal: nele são refeitos
  o sistema nas duas leituras, a validação cruzada, os três modelos de
  comparação da Tabela II e o SHAP.
- **Combinado como publicado:** o mesmo, com as {HKD_REPLICAS} cópias de cada fluxo do
  HKD, que deixam cópias idênticas no treino e no teste. Análise ao lado.
- **Transferência:** treino no CIRA, avaliação nos fluxos do HKD. O HKD só tem
  a classe maliciosa e não permite treinar o sistema: não há precisão, FPR nem
  acurácia, e neste cenário tudo é teste. Análise ao lado.

No combinado, Non-DoH e Benign-DoH são os fluxos do CIRA; só a classe maliciosa
ganha fluxos novos. Métricas gerais perto das do CIRA são esperadas e não medem
generalização: a leitura útil é o recall das ferramentas do HKD.

## Tabela final: CIRA ao lado do combinado sem réplicas

Os modelos de comparação são os da Tabela II do artigo e não dependem da
leitura de profundidade. Os resultados no CIRA vêm de `results/e1/` (sistema) e
de `results/e2/` (modelos de comparação).

{e6.markdown_table(FINAL_COLUMNS, final_rows(results, baselines))}

- As duas linhas de um modelo não usam o mesmo teste: cada dataset tem o seu
  split, com a mesma seed. A diferença entre elas não isola o efeito das
  ferramentas novas.
- No sistema, a AUC é a da saída do meta-classificador; a da média das
  probabilidades dos bases está no resumo de cada trilha. A validação cruzada
  grava só a matriz de confusão: não há AUC nem recall por ferramenta nos
  folds. Os modelos de comparação não têm validação cruzada, como no CIRA.
- A última coluna é o recall de Malicious-DoH só nos fluxos de dnstt,
  tcp-over-dns e tuns, com os detectados sobre `n` e o intervalo de confiança
  de 95%.

Leitura em termos de detecção, no teste do combinado sem réplicas:

{detection_lines(models)}

## Recall por ferramenta no teste do combinado sem réplicas

Recall de Malicious-DoH, com detectados sobre `n` e o intervalo de confiança de
95% entre parênteses. O teste é o mesmo para os cinco modelos. dns2tcp, dnscat2
e iodine são as ferramentas do CIRA; dnstt, tcp-over-dns e tuns, as do HKD.

{tools_table(models)}

## SHAP no combinado sem réplicas ao lado do CIRA

{final_shap_text(results)}

## Ao lado do que foi declarado antes de rodar os modelos de comparação e o SHAP

O cabeçalho de `scripts/e6_baselines_xai.py` declara, antes da execução, o que
contaria como resultado inesperado. Os números:

{declared_lines(results, baselines)}

## Análises ao lado: combinado como publicado e transferência

Os quatro cenários do sistema do artigo, nas duas leituras: CIRA,
transferência, retreino no combinado sem réplicas e retreino no combinado como
publicado.

{e6.markdown_table(SCENARIO_COLUMNS, scenarios)}

A última coluna é o recall de Malicious-DoH só nos fluxos de dnstt, tcp-over-dns
e tuns. Na validação cruzada ela não é medida, porque só a matriz de confusão
é gravada.

Recall por ferramenta do HKD nos três cenários, com detectados sobre `n` e
intervalo de confiança de 95% entre parênteses.

{tools}

{e6.copies_text(results[0][1])}

## Números ao lado das hipóteses

As hipóteses estão em `fiel/HIPOTESE.md`, na mesma ordem, e não foram alteradas
depois da execução.

{hypotheses}
"""


def main() -> None:
    """Lê os metrics.json de E6 e do CIRA e escreve os três arquivos RESUMO.md."""
    baselines = load_baselines()
    results = [(reading, load_reading(reading)) for reading in e6.READINGS]
    for reading, result in results:
        path = E6_DIR / reading["track"] / "RESUMO.md"
        path.write_text(track_text(reading, result, baselines), encoding="utf-8")
        print(f"Escrito {path.relative_to(RESULTS_DIR.parent)}")
    path = E6_DIR / "RESUMO.md"
    path.write_text(final_text(results, baselines), encoding="utf-8")
    print(f"Escrito {path.relative_to(RESULTS_DIR.parent)}")


if __name__ == "__main__":
    main()
