"""E3: tabela comparativa e resumo da sensibilidade, a partir dos metrics.json.

Não treina nada. Lê os metrics.json e os run.json gravados por
scripts/e3_sensibilidade.py em results/e3/variante/<recorte>/seed42/, os das
duas configurações de partida em results/e1/ e, para a variação entre seeds do
modelo de partida, os de results/e4/corrigida/A/. Escreve
results/e3/variante/comparacao.csv e results/e3/variante/RESUMO.md.

Roda como módulo, a partir da pasta do projeto, porque importa o script de treino.

Uso: uv run python -m scripts.e3_resumo
"""

import json
from pathlib import Path

import pandas as pd

import scripts.e3_sensibilidade as e3
from doh_ids.config import (
    CLASS_NAMES,
    FIG4B_CONFUSION,
    MAX_DEPTH,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEED_FIEL,
    SEEDS_CORRIGIDA,
)
from doh_ids.evaluate import compare_confusion, metrics_from_confusion
from doh_ids.summary import markdown_table

VARIANT_DIR = RESULTS_DIR / "e3" / "variante"
# Execuções do modelo de partida de profundidade variável em dez seeds, feitas
# pelo protocolo corrigido.
SEEDS_RUN_DIR = RESULTS_DIR / "e4" / "corrigida" / "A"

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

    `results` leva cada recorte ao metrics.json dele; `start_tests` leva o
    rótulo de cada configuração de partida às métricas dela no teste.
    """
    rows = [comparison_row("Artigo, Fig. 4b", "", "", metrics_from_confusion(FIG4B_CONFUSION))]
    for start in e3.STARTS:
        rows.append(
            comparison_row(
                f"partida ({start['label']})",
                start["label"],
                "nenhum: reprodução",
                start_tests[start["label"]],
            )
        )
        for name, variant in e3.VARIANTS.items():
            slice_name = name + start["suffix"]
            rows.append(
                comparison_row(
                    slice_name, start["label"], variant["point"], results[slice_name]["test"]
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
            ", ".join(f"`{name}{start['suffix']}`" for start in e3.STARTS),
        ]
        for name, variant in e3.VARIANTS.items()
    ]
    return markdown_table(["ponto em aberto no artigo", "leitura alternativa", "recortes"], rows)


def effect_lines(frame: pd.DataFrame) -> str:
    """Escreve, para cada recorte, quanto ele se afasta da própria configuração de partida."""
    rows = frame.set_index("configuration")
    lines = []
    for start in e3.STARTS:
        origin = rows.loc[f"partida ({start['label']})"]
        for name in e3.VARIANTS:
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
    for slice_name, metrics in results.items():
        if "base_models_test" not in metrics:
            continue
        recalls = ", ".join(
            f"{base['per_class']['Benign-DoH']['recall']:.2%}"
            for base in metrics["base_models_test"]
        )
        stacked = metrics["test"]["per_class"]["Benign-DoH"]["recall"]
        lines.append(f"- **`{slice_name}`:** bases {recalls}; modelo empilhado {stacked:.2%}.")
    return "\n".join(lines)


def fig4b_sum(confusion: list[list[int]]) -> int:
    """Devolve a soma das diferenças absolutas entre uma matriz de confusão e a da Fig. 4b."""
    return compare_confusion(confusion, FIG4B_CONFUSION)["absolute_difference_sum"]


def start_sums_across_seeds() -> list[int]:
    """Calcula a soma para a Fig. 4b do modelo de partida em cada seed do protocolo corrigido.

    O modelo A daquele protocolo é o sistema da partida de profundidade
    variável, com outro split e outros sorteios em cada seed.
    """
    sums = []
    for seed in SEEDS_CORRIGIDA:
        path = SEEDS_RUN_DIR / f"seed{seed}" / "metrics.json"
        metrics = json.loads(path.read_text(encoding="utf-8"))
        sums.append(fig4b_sum(metrics["test"]["confusion_matrix"]))
    return sums


def distance_reading_text(frame: pd.DataFrame, results: dict, seed_sums: list[int]) -> str:
    """Põe as somas para a Fig. 4b ao lado da variação entre seeds do modelo de partida.

    `seed_sums` é a soma do modelo de partida de profundidade variável em cada
    seed do protocolo corrigido. O texto diz também qual recorte tem a maior
    soma e quais nunca predizem Benign-DoH.
    """
    start = e3.STARTS[0]
    measured = frame[frame["changed_point"].isin([v["point"] for v in e3.VARIANTS.values()])]
    sums = measured.set_index("configuration")["fig4b_absolute_difference_sum"]
    variable = measured.loc[measured["start"] == start["label"], "fig4b_absolute_difference_sum"]
    origin = frame.set_index("configuration").loc[
        f"partida ({start['label']})", "fig4b_absolute_difference_sum"
    ]
    spread = max(seed_sums) - min(seed_sums)
    public = f"{e3.SINGLE_FOREST}{e3.STARTS[1]['suffix']}"
    if sums[public] == sums.max():
        position, values = "tem a maior soma", f"{sums[public]}"
    else:
        position, values = "não tem a maior soma", f"{sums[public]}; a maior é {sums.max()}"
    benign = CLASS_NAMES.index("Benign-DoH")
    never = [
        f"`{slice_name}`"
        for slice_name, metrics in results.items()
        if not any(row[benign] for row in metrics["test"]["confusion_matrix"])
    ]
    text = (
        f"Nos recortes de {start['label']}, a soma das diferenças absolutas vai de "
        f"{variable.min()} a {variable.max()}; a da partida, com a seed {SEED_FIEL}, é {origin}. "
        f"O mesmo modelo de partida, nas {len(seed_sums)} seeds de "
        f"`results/{SEEDS_RUN_DIR.relative_to(RESULTS_DIR).as_posix()}/`, tem soma de "
        f"{min(seed_sums)} a {max(seed_sums)}: só a troca do split e dos sorteios move a soma em "
        f"até {spread} linhas. Diferença entre recortes menor que essa não ordena as leituras, "
        f"e nenhum recorte é apontado como o mais próximo da Fig. 4b. O recorte que corresponde "
        f"ao script publicado pelos autores, `{public}`, {position} entre os {len(measured)} "
        f"recortes medidos ({values}).\n\n"
    )
    if never:
        text += (
            f"Não predizem Benign-DoH em nenhuma linha do teste: {', '.join(never)}. Nesses "
            "recortes a precisão da classe é indefinida e entra como 0 no F1 macro."
        )
    else:
        text += "Todos os recortes predizem Benign-DoH em alguma linha do teste."
    return text


def declaration_text(runs: list[dict]) -> str:
    """Escreve o que foi fixado antes da execução e que não houve hipótese escrita."""
    commits = sorted({run["commit"][:7] for run in runs})
    tree = (
        "com a árvore limpa"
        if not any(run["dirty"] for run in runs)
        else "e ao menos uma execução tinha a árvore alterada"
    )
    return (
        "A lista das leituras alternativas e as duas configurações de partida foram fixadas no "
        f"código em commit anterior à execução: os `run.json` registram o commit "
        f"{' e '.join(f'`{commit}`' for commit in commits)}, {tree}. Não houve hipótese escrita "
        "antes de rodar, e isso não se conserta depois: nenhum número desta pasta foi "
        "confrontado com uma expectativa declarada antes de ser visto."
    )


def summary_text(results: dict, start_tests: dict, seed_sums: list[int], runs: list[dict]) -> str:
    """Monta o texto do RESUMO.md a partir dos arquivos gravados pela execução.

    `results` leva cada recorte ao metrics.json dele, `start_tests` o rótulo de
    cada partida às métricas dela no teste, `seed_sums` é o que
    `start_sums_across_seeds` devolve e `runs` os run.json dos recortes.
    """
    frame = comparison_frame(results, start_tests)
    test = next(iter(results.values()))["test"]
    benign_support = test["per_class"]["Benign-DoH"]["support"]
    starts = "\n".join(
        f"- **{start['label']}:** {start['base_depth']}. Medida em "
        f"`results/{start['e1_run'].as_posix()}/`; recortes desta partida "
        + (f"com o sufixo `{start['suffix']}`." if start["suffix"] else "sem sufixo.")
        for start in e3.STARTS
    )
    return f"""# E3: sensibilidade às leituras que o artigo deixa em aberto

Gerado por `scripts/e3_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e3_sensibilidade.py`. Os números de cada recorte vêm de
`<recorte>/seed{SEED_FIEL}/metrics.json`; a configuração e os tempos, de
`<recorte>/seed{SEED_FIEL}/run.json`; a tabela abaixo, sem arredondamento, está em
`comparacao.csv`. Uma única execução de cada recorte, com a seed {SEED_FIEL}: não há
média nem desvio padrão, e diferença pequena entre recortes não distingue
leitura de variação entre seeds. Todos os recortes são avaliados no mesmo
teste, de {test["total"]} fluxos. Não há validação cruzada aqui.

{declaration_text(runs)}

## O que foi variado

O artigo não especifica os pontos abaixo. A reprodução adota uma leitura em
cada um; cada recorte troca uma leitura só e mantém todo o resto da
configuração de partida. A exceção é `{e3.SINGLE_FOREST}`, que troca vários pontos de
uma vez, de propósito: é a configuração do script publicado pelos autores, que
não empilha.

{readings_table()}

Configurações de partida, as duas leituras da profundidade das árvores:

{starts}

O script publicado pelos autores usa profundidade máxima {MAX_DEPTH}: dos dois recortes de
`{e3.SINGLE_FOREST}`, o que corresponde a ele é `{e3.SINGLE_FOREST}-prof5`.

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

{distance_reading_text(frame, results, seed_sums)}

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
  `{e3.SINGLE_FOREST}-prof5` nos nossos dados. O arquivo que aquele script lê não foi
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


def load_json(run_dir: Path, name: str) -> dict:
    """Lê um dos dois arquivos gravados na pasta de uma execução."""
    return json.loads((run_dir / name).read_text(encoding="utf-8"))


def main() -> None:
    """Lê as execuções gravadas de E3 e escreve a tabela comparativa e o resumo."""
    slices = [name + start["suffix"] for start in e3.STARTS for name in e3.VARIANTS]
    run_dirs = {name: VARIANT_DIR / name / f"seed{SEED_FIEL}" for name in slices}
    results = {name: load_json(run_dir, "metrics.json") for name, run_dir in run_dirs.items()}
    runs = [load_json(run_dir, "run.json") for run_dir in run_dirs.values()]
    start_tests = {
        start["label"]: load_json(RESULTS_DIR / start["e1_run"], "metrics.json")["test"]
        for start in e3.STARTS
    }
    # Mesmo teste em todas as configurações, inclusive nas duas de partida.
    totals = {metrics["test"]["total"] for metrics in results.values()}
    totals |= {test["total"] for test in start_tests.values()}
    assert len(totals) == 1, f"Configurações avaliadas em testes de tamanhos diferentes: {totals}."

    frame = comparison_frame(results, start_tests)
    frame.to_csv(VARIANT_DIR / "comparacao.csv", index=False)
    text = summary_text(results, start_tests, start_sums_across_seeds(), runs)
    (VARIANT_DIR / "RESUMO.md").write_text(text, encoding="utf-8")
    print(comparison_table(frame))
    print(f"Escritos comparacao.csv e RESUMO.md em {VARIANT_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
