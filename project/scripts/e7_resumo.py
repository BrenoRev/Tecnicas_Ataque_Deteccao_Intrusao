"""E7: resumo da identificação da ferramenta de túnel, a partir dos metrics.json.

Não treina nada. Lê os metrics.json e os run.json gravados por
scripts/e7_ferramenta.py em results/e7/variante/, results/e7/fiel/ e
results/e7/dados/fig9/ e escreve results/e7/RESUMO.md.

Roda como módulo, a partir da pasta do projeto, porque importa o script de treino.

Uso: uv run python -m scripts.e7_resumo
"""

import json
from pathlib import Path

import pandas as pd

import scripts.e7_ferramenta as e7
from doh_ids.config import (
    FEATURE_COLUMNS,
    FIG9_BINS,
    FIG9_PANELS,
    MAX_DEPTH,
    N_ESTIMATORS,
    N_SUBSETS,
    PROJECT_ROOT,
    RESULTS_DIR,
    SECTION_VI_D_ACCURACY,
    SEED_FIEL,
    SKEW_SENTINEL,
    TEST_SIZE,
)
from doh_ids.summary import frame_markdown_table

E7_DIR = RESULTS_DIR / "e7"


def matrix_table(confusion: list[list[int]], roles: list[str]) -> str:
    """Escreve uma matriz de confusão em Markdown, com o nome das ferramentas."""
    index = pd.Index(roles, name="real \\ predito")
    return frame_markdown_table(pd.DataFrame(confusion, index=index, columns=roles))


def comparison_table(comparison: dict) -> str:
    """Escreve o valor do artigo de cada ferramenta ao lado das métricas obtidas no teste."""
    rows = []
    # Na ordem em que o artigo lista as ferramentas: lido de metrics.json, o
    # dicionário vem em ordem alfabética.
    for tool in SECTION_VI_D_ACCURACY:
        entry = comparison[tool]
        row = [tool, f"{entry['article_accuracy']:.1%}", entry["support"]]
        for metric, _ in e7.METRIC_TITLES:
            row += [f"{entry[metric]:.2%}", f"{entry['difference_pp'][metric]:+.2f}"]
        rows.append(row)
    columns = ["ferramenta", 'artigo ("accuracy")', "fluxos no teste"]
    for _, title in e7.METRIC_TITLES:
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

    Devolve texto vazio quando todas são preditas ao menos uma vez; o aviso
    já vem com a linha em branco que o separa do parágrafo seguinte.
    """
    never = [name for code, name in enumerate(roles) if not any(row[code] for row in confusion)]
    if not never:
        return ""
    return (
        f"\nO modelo não prediz {' nem '.join(never)} em nenhuma linha do teste. A precisão de "
        "uma classe sem predição é indefinida e entra como 0 na média macro.\n"
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
    run_dir = f"{reading['track']}/{e7.SCENARIO}/seed{SEED_FIEL}"
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


def legend_matches(statistics: pd.DataFrame) -> int:
    """Conta as estatísticas iguais às da legenda da Fig. 9 nos seis algarismos que ela imprime."""
    pairs = [("média", "média no artigo"), ("desvio padrão", "desvio padrão no artigo")]
    return sum(
        f"{row[obtained]:.6g}" == f"{row[article]:.6g}"
        for _, row in statistics.iterrows()
        for obtained, article in pairs
    )


def legend_text(fig9: dict, statistics: pd.DataFrame) -> str:
    """Escreve o que a medida nos arquivos como publicados mostra sobre a legenda da Fig. 9."""
    by_version = {
        version: statistics[statistics["versão"] == version]
        for version in (e7.FIG9_ARTICLE_VERSION, e7.FIG9_CLEAN_VERSION)
    }
    published, clean = by_version.values()
    total = 2 * len(published)
    rows = sum(fig9["published_rows_by_tool"].values())
    doh = sum(fig9["raw_rows_by_tool"].values())
    return (
        f"A legenda da Fig. 9 foi medida de duas formas. Com todas as {rows} linhas dos três "
        f"arquivos `all.csv` do zip, sem o filtro da coluna `DoH` e sem a limpeza, e com o desvio "
        f"padrão populacional, {legend_matches(published)} das {total} médias e desvios padrão "
        f"saem iguais aos da legenda nos seis algarismos que ela imprime. Com os {fig9['flows']} "
        f"fluxos limpos da reprodução e o desvio padrão amostral, {legend_matches(clean)} das "
        f"{total}. Isso é indício, e não demonstração, de que a Seção VI-D do artigo usou os "
        f"arquivos por ferramenta como publicados, sem a limpeza que leva à Tabela I: os "
        f"arquivos têm {rows} linhas, {doh} delas com `DoH` verdadeiro, e a Tabela I traz "
        f"{fig9['flows']} fluxos Malicious-DoH. O artigo não diz que dados a figura usa."
    )


def fig9_text(fig9: dict) -> str:
    """Monta a seção do RESUMO.md sobre a figura equivalente à Fig. 9."""
    # Lido de metrics.json, cada registro vem com as chaves em ordem alfabética.
    statistics = pd.DataFrame(fig9["fig9_statistics"])[e7.FIG9_COLUMNS]
    clean = statistics[statistics["versão"] == e7.FIG9_CLEAN_VERSION]
    panels = "\n".join(
        f"- ({letter}) `{column}` ({unit}), eixo de {low} a {high}."
        for letter, (column, unit, low, high) in zip("ab", FIG9_PANELS, strict=True)
    )
    lowest = "\n".join(
        f"- `{column}`: o menor desvio padrão é o de "
        f"{panel.loc[panel['desvio padrão'].idxmin(), 'ferramenta']}."
        for column, panel in clean.groupby("atributo", sort=False)
    )
    sentinel = clean.dropna(subset="fração com -10")
    marker = ", ".join(
        f"{row['ferramenta']} {row['fração com -10']:.2%}" for _, row in sentinel.iterrows()
    )
    table = statistics.copy()
    for column in ["fração no eixo", "fração com -10"]:
        table[column] = table[column].map(lambda value: "–" if pd.isna(value) else f"{value:.2%}")
    for column in ["média", "desvio padrão", "média menos artigo", "desvio padrão menos artigo"]:
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

{legend_text(fig9, statistics)}

{frame_markdown_table(table.set_index("versão"))}

O artigo afirma que o dns2tcp tem desvio padrão menor nos dois atributos. Medido
nos dados limpos:

{lowest}

`{sentinel["atributo"].iloc[0]}` é uma coluna de assimetria, em que o extrator grava
{SKEW_SENTINEL} quando o desvio padrão do fluxo é zero. Fração dos fluxos limpos com esse
marcador: {marker}. O marcador entra na média e no desvio padrão da tabela,
como qualquer outro valor.
"""


def declaration_text(runs: list[dict]) -> str:
    """Escreve o que foi fixado antes da execução e que não houve hipótese escrita."""
    commits = sorted({run["commit"][:7] for run in runs})
    tree = (
        "com a árvore limpa"
        if not any(run["dirty"] for run in runs)
        else "e ao menos uma execução tinha a árvore alterada"
    )
    return (
        "O método e a regra que dá o papel de cada ferramenta nos subconjuntos foram fixados no "
        f"código em commit anterior à execução: os `run.json` registram o commit "
        f"{' e '.join(f'`{commit}`' for commit in commits)}, {tree}. Não houve hipótese escrita "
        "antes de rodar, e isso não se conserta depois: nenhum número desta pasta foi "
        "confrontado com uma expectativa declarada antes de ser visto."
    )


def summary_text(results: list[tuple[dict, dict]], fig9: dict, runs: list[dict]) -> str:
    """Monta o RESUMO.md a partir dos arquivos gravados pela execução.

    `results` tem um par (leitura, métricas) por execução, `fig9` é o
    dicionário gravado pela etapa da figura e `runs` os run.json das leituras.
    """
    first = results[0][1]
    roles = first["roles"]
    counts = {key: fig9[key] for key in ("raw_rows_by_tool", "clean_rows_by_tool")}
    rows = pd.DataFrame(counts).rename(
        columns={"raw_rows_by_tool": "fluxos no zip", "clean_rows_by_tool": "depois da limpeza"}
    )
    rows["treino"] = pd.Series(first["train_rows"], index=first["classes"])
    rows["teste"] = pd.Series(first["test_rows"], index=first["classes"])
    rows.index.name = "ferramenta"
    readings = "\n".join(reading_text(reading, metrics) for reading, metrics in results)
    article = ", ".join(f"{tool} {value:.1%}" for tool, value in SECTION_VI_D_ACCURACY.items())
    return f"""# E7: identificação da ferramenta de túnel (Seção VI-D e Fig. 9 do artigo)

Gerado por `scripts/e7_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e7_ferramenta.py`. Uma única execução de cada leitura, com a seed {SEED_FIEL}:
não há média nem desvio padrão.

{declaration_text(runs)}

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

As três acurácias da Seção VI-D: o artigo não informa o modelo, os dados de
treino, o split, a seed nem a definição de "accuracy" por ferramenta; as
versões das bibliotecas são outras. Qualquer um desses pontos pode explicar a
diferença nas acurácias, e os dados não permitem dizer qual.

A média e o desvio padrão da Fig. 9: a diferença para os dados limpos tem
explicação medida, descrita na seção da figura. Se o modelo da Seção VI-D
também usou os arquivos sem a limpeza, os dados dele não são os desta
reprodução; isso é hipótese, e nada aqui a testa.

Nenhuma seed, hiperparâmetro, papel de ferramenta ou regra de limpeza foi
ajustado para aproximar o resultado.
"""


def load_json(run_dir: Path, name: str) -> dict:
    """Lê um dos dois arquivos gravados na pasta de uma execução."""
    return json.loads((run_dir / name).read_text(encoding="utf-8"))


def main() -> None:
    """Lê as execuções gravadas de E7 e escreve o resumo."""
    run_dirs = [
        E7_DIR / reading["track"] / e7.SCENARIO / f"seed{SEED_FIEL}" for reading in e7.READINGS
    ]
    results = [
        (reading, load_json(run_dir, "metrics.json"))
        for reading, run_dir in zip(e7.READINGS, run_dirs, strict=True)
    ]
    runs = [load_json(run_dir, "run.json") for run_dir in run_dirs]
    fig9 = load_json(E7_DIR / "dados" / "fig9" / f"seed{SEED_FIEL}", "metrics.json")
    path = E7_DIR / "RESUMO.md"
    path.write_text(summary_text(results, fig9, runs), encoding="utf-8")
    print(f"Escrito {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
