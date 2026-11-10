"""E8: agregação e resumo do tempo de inferência.

Não treina nada. Lê os metrics.json e os run.json gravados por
scripts/e8_inferencia.py em results/e8/corrigida/inferencia-<dados>/seed<k>/ e
escreve em results/e8/corrigida/:

- summary-inferencia.json: por conjunto de dados e modelo, média e desvio
  padrão entre as seeds dos nós percorridos por fluxo e dos tempos, e as
  comparações pareadas de `INFERENCE_COMPARISONS`;
- RESUMO-INFERENCIA.md: a leitura dos números, ao lado da hipótese escrita
  antes da primeira execução (HIPOTESE-INFERENCIA.md, que este script não altera).

Roda como módulo, a partir da pasta do projeto, porque importa outros scripts.

Uso: uv run python -m scripts.e8_inferencia_resumo
"""

import json
from pathlib import Path

import numpy as np

import scripts.e8_inferencia as inf
from doh_ids.config import (
    INFERENCE_COMPARISONS,
    INFERENCE_MODELS,
    INFERENCE_NODE_RATIO_BAND,
    MODIFIED_SELECTED_MODEL,
    PROJECT_ROOT,
    RESULTS_DIR,
    SEEDS_CORRIGIDA,
)
from doh_ids.evaluate import HIGHER, LOWER, SAME, aggregate_seeds, paired_comparison, paired_verdict
from doh_ids.summary import markdown_table

E8_DIR = RESULTS_DIR / inf.EXPERIMENT / inf.TRACK
DATASET_NAMES = {"cira": "CIRA-CIC-DoHBrw-2020", "combinado_sem_replicas": "combinado sem réplicas"}
# Métricas comparadas nos pares: a determinística e os dois regimes de tempo.
PAIRED = {
    "nodes_per_flow": "nós por fluxo",
    "batch_seconds": "tempo em lote",
    "single_seconds": "tempo fluxo a fluxo",
}
VERDICT_TEXT = {HIGHER: "maior", LOWER: "menor", SAME: "não se distinguem"}


def seed_values(metrics: dict, run: dict, name: str) -> dict:
    """Extrai de uma execução os valores de um modelo: um número por chave."""
    timings = run["timings"][name]
    model = metrics["models"][name]
    return {
        "trees": model["trees"],
        "nodes_per_flow": model["nodes_per_flow"],
        "batch_seconds": float(np.median(timings["batch_seconds"])),
        "single_seconds": timings["single_median_seconds"],
        "single_p95_seconds": timings["single_p95_seconds"],
    }


def load_dataset(e8_dir: Path, dataset: str, seeds: list[int]) -> dict:
    """Lê as execuções de um conjunto e devolve, por modelo, a lista de valores por seed."""
    values = {name: [] for name in INFERENCE_MODELS[dataset]}
    runs = []
    for seed in seeds:
        run_dir = e8_dir / inf.SLICE_NAME.format(dataset=dataset) / f"seed{seed}"
        metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        assert run["track"] == inf.TRACK, f"{run_dir}: trilha {run['track']}."
        assert not run["dirty"], f"{run_dir}: gravada com a árvore suja."
        runs.append(run)
        for name in values:
            values[name].append(seed_values(metrics, run, name))
    test_rows = sum(metrics["test_rows"])
    machine = sorted({(run["hostname"], run["cpu_count"]) for run in runs})
    commits = sorted({run["commit"] for run in runs})
    return {"values": values, "test_rows": test_rows, "machine": machine, "commits": commits}


def pair_rows(values: dict, first: str, second: str) -> list[dict]:
    """Compara dois modelos seed a seed em cada métrica de `PAIRED`, com a razão média."""
    rows = []
    for metric in PAIRED:
        a = [seed[metric] for seed in values[first]]
        b = [seed[metric] for seed in values[second]]
        comparison = paired_comparison(a, b)
        ratios = np.divide(a, b)
        rows.append(
            {
                "first": first,
                "second": second,
                "metric": metric,
                **comparison,
                "mean_ratio": float(np.mean(ratios)),
                "min_ratio": float(np.min(ratios)),
                "max_ratio": float(np.max(ratios)),
                "verdict": paired_verdict(comparison),
            }
        )
    return rows


def summary_content(e8_dir: Path, seeds: list[int]) -> tuple[dict, dict]:
    """Monta o summary-inferencia.json; devolve também as máquinas e os commits das execuções."""
    datasets, machines, commits = {}, set(), set()
    for dataset in INFERENCE_MODELS:
        loaded = load_dataset(e8_dir, dataset, seeds)
        machines.update(tuple(entry) for entry in loaded["machine"])
        commits.update(loaded["commits"])
        datasets[dataset] = {
            "test_rows": loaded["test_rows"],
            "models": {name: aggregate_seeds(v) for name, v in loaded["values"].items()},
            "pairs": [
                row
                for first, second in INFERENCE_COMPARISONS[dataset]
                for row in pair_rows(loaded["values"], first, second)
            ],
        }
    meta = {"machine": sorted(machines), "commits": sorted(commits)}
    return {"seeds": seeds, "datasets": datasets}, meta


def find_pair(summary: dict, dataset: str, first: str, second: str, metric: str) -> dict:
    """Devolve a comparação de um par em uma métrica."""
    pairs = summary["datasets"][dataset]["pairs"]
    return next(
        row
        for row in pairs
        if (row["first"], row["second"], row["metric"]) == (first, second, metric)
    )


def mean_std(entry: dict, scale: float = 1.0, digits: int = 2) -> str:
    """Escreve média ± desvio padrão entre as seeds, multiplicados por `scale`."""
    return f"{scale * entry['mean']:.{digits}f} ± {scale * entry['std']:.{digits}f}"


def models_table(dataset_summary: dict) -> str:
    """Tabela por modelo: árvores, nós por fluxo e os dois regimes de tempo."""
    per_flow = 1e6 / dataset_summary["test_rows"]
    rows = [
        [
            name,
            int(entry["trees"]["mean"]),
            mean_std(entry["nodes_per_flow"], digits=1),
            mean_std(entry["batch_seconds"], 1000),
            mean_std(entry["batch_seconds"], per_flow),
            mean_std(entry["single_seconds"], 1000, 3),
            mean_std(entry["single_p95_seconds"], 1000, 3),
        ]
        for name, entry in dataset_summary["models"].items()
    ]
    columns = [
        "modelo",
        "árvores",
        "nós por fluxo",
        "lote, teste inteiro (ms)",
        "lote, por fluxo (µs)",
        "fluxo a fluxo, mediana (ms)",
        "fluxo a fluxo, p95 (ms)",
    ]
    return markdown_table(columns, rows)


def pairs_table(dataset_summary: dict) -> str:
    """Tabela das comparações pareadas, com a razão média e o veredito da regra."""
    rows = []
    for row in dataset_summary["pairs"]:
        scale, unit = (1.0, "nós") if row["metric"] == "nodes_per_flow" else (1000.0, "ms")
        rows.append(
            [
                f"{row['first']} contra {row['second']}",
                PAIRED[row["metric"]],
                f"{row['mean_ratio']:.2f}",
                f"{scale * row['mean_difference']:+.3f} {unit}",
                f"{scale * row['std_difference']:.3f} {unit}",
                f"{row['first_wins']} de {row['first_wins'] + row['second_wins'] + row['ties']}",
                VERDICT_TEXT[row["verdict"]],
            ]
        )
    columns = [
        "par",
        "métrica",
        "razão média (primeiro / segundo)",
        "diferença média",
        "desvio padrão das diferenças",
        "seeds em que o primeiro é maior",
        "veredito para o primeiro",
    ]
    return markdown_table(columns, rows)


def occurred(happened: bool) -> str:
    """Escreve se uma expectativa ocorreu, em negrito quando sim."""
    return "**ocorreu**" if happened else "não ocorreu"


def verdict(summary: dict, dataset: str, first: str, metric: str) -> str:
    """Veredito de `first` contra A em uma métrica."""
    return find_pair(summary, dataset, first, "A", metric)["verdict"]


def ratio(summary: dict, dataset: str, first: str, metric: str) -> float:
    """Razão média de `first` sobre A em uma métrica."""
    return find_pair(summary, dataset, first, "A", metric)["mean_ratio"]


def time_order_follows_nodes(dataset_summary: dict) -> bool:
    """Diz se a ordem dos modelos pelo tempo em lote é a ordem pelos nós por fluxo."""
    models = dataset_summary["models"]
    by_nodes = sorted(models, key=lambda name: models[name]["nodes_per_flow"]["mean"])
    by_time = sorted(models, key=lambda name: models[name]["batch_seconds"]["mean"])
    return by_nodes == by_time


def expected_lines(summary: dict) -> list[str]:
    """As três expectativas da hipótese, cada uma com o resultado ao lado."""
    both, s = list(INFERENCE_MODELS), summary
    m1m2 = MODIFIED_SELECTED_MODEL
    nodes = [f"{ratio(s, ds, m1m2, 'nodes_per_flow'):.2f}" for ds in both]
    batch = [f"{ratio(s, ds, m1m2, 'batch_seconds'):.2f}" for ds in both]
    single = [f"{ratio(s, ds, m1m2, 'single_seconds'):.2f}" for ds in both]
    return [
        "1. Nós por fluxo. M1M2 percorre mais de duas vezes os nós de A nos dois conjuntos: "
        f"{occurred(all(ratio(s, ds, m1m2, 'nodes_per_flow') > 2 for ds in both))} (razão "
        f"média {nodes[0]} no CIRA e {nodes[1]} no combinado); M1 percorre menos que A: "
        f"{occurred(verdict(s, 'cira', 'M1', 'nodes_per_flow') == LOWER)}; A-prof5 percorre "
        f"menos que A: {occurred(verdict(s, 'cira', 'A-prof5', 'nodes_per_flow') == LOWER)}.",
        "2. Lote. M1M2 mais lento que A nos dois conjuntos: "
        f"{occurred(all(verdict(s, ds, m1m2, 'batch_seconds') == HIGHER for ds in both))} "
        f"(razão média {batch[0]} no CIRA e {batch[1]} no combinado); M1 mais rápido que A: "
        f"{occurred(verdict(s, 'cira', 'M1', 'batch_seconds') == LOWER)}; A-prof5 mais rápido "
        f"que A: {occurred(verdict(s, 'cira', 'A-prof5', 'batch_seconds') == LOWER)}; a ordem "
        "dos tempos no CIRA segue a dos nós por fluxo: "
        f"{occurred(time_order_follows_nodes(s['datasets']['cira']))}.",
        "3. Fluxo a fluxo. M1M2 mais lento que A nos dois conjuntos: "
        f"{occurred(all(verdict(s, ds, m1m2, 'single_seconds') == HIGHER for ds in both))} "
        f"(razão média {single[0]} no CIRA e {single[1]} no combinado); M1 mais rápido que A: "
        f"{occurred(verdict(s, 'cira', 'M1', 'single_seconds') == LOWER)}; A-prof5 não se "
        f"distingue de A: {occurred(verdict(s, 'cira', 'A-prof5', 'single_seconds') == SAME)}.",
    ]


def outside_band(summary: dict) -> list[str]:
    """Pares cuja razão de tempo em lote sai da faixa em torno da razão de nós por fluxo."""
    low, high = INFERENCE_NODE_RATIO_BAND
    found = []
    for dataset, pairs in INFERENCE_COMPARISONS.items():
        for first, second in pairs:
            nodes = find_pair(summary, dataset, first, second, "nodes_per_flow")["mean_ratio"]
            batch = find_pair(summary, dataset, first, second, "batch_seconds")["mean_ratio"]
            if not low * nodes <= batch <= high * nodes:
                found.append(f"{first} contra {second} ({dataset}): {batch:.2f} e {nodes:.2f}")
    return found


def unexpected_lines(summary: dict) -> list[str]:
    """Os resultados que a hipótese declarou inesperados, cada um com o que ocorreu."""
    s = summary
    m1m2_not_slower = any(
        verdict(s, ds, MODIFIED_SELECTED_MODEL, metric) != HIGHER
        for ds in INFERENCE_MODELS
        for metric in ("batch_seconds", "single_seconds")
    )
    band = outside_band(s)
    return [
        "- M1M2 não ser mais lento que A em algum regime ou conjunto: "
        f"{occurred(m1m2_not_slower)}.",
        "- A-prof5 não ser mais rápido que A em lote: "
        f"{occurred(verdict(s, 'cira', 'A-prof5', 'batch_seconds') != LOWER)}.",
        "- Razão de tempo em lote fora do intervalo entre metade e o dobro da razão de nós por "
        f"fluxo: {occurred(bool(band))}" + (f" ({'; '.join(band)})." if band else "."),
    ]


def throughput_lines(summary: dict) -> list[str]:
    """Traduz os tempos médios em fluxos por segundo, nesta máquina e com uma thread."""
    lines = []
    for dataset, content in summary["datasets"].items():
        models = content["models"]
        batch = ", ".join(
            f"{name} {content['test_rows'] / entry['batch_seconds']['mean'] / 1000:.0f} mil"
            for name, entry in models.items()
        )
        single = ", ".join(
            f"{name} {1 / entry['single_seconds']['mean']:.0f}" for name, entry in models.items()
        )
        lines.append(
            f"- {DATASET_NAMES[dataset]}: em lote, fluxos por segundo: {batch}. Um fluxo por "
            f"chamada, fluxos por segundo: {single}."
        )
    return [
        "Fluxos por segundo equivalentes aos tempos médios, só da etapa de normalizar e "
        "predizer, com uma thread, nesta máquina e no estado de carga de cada seed. Não são a "
        "capacidade de um detector: ficam de fora a extração de atributos, a espera pelo fim do "
        "fluxo e o uso de mais threads. O que se compara entre modelos são as razões das tabelas "
        "de pares.",
        "",
        *lines,
    ]


def spread(entry: dict) -> float:
    """Coeficiente de variação entre as seeds: desvio padrão sobre a média."""
    return entry["std"] / entry["mean"]


def posterior_lines(summary: dict) -> list[str]:
    """Leitura acrescentada depois de ver os números; não altera regra nem vereditos."""
    s, cira = summary, summary["datasets"]["cira"]
    single = find_pair(s, "cira", "A-prof5", "A", "single_seconds")
    excess = abs(single["mean_difference"]) / single["std_difference"] - 1
    p95 = mean_std(cira["models"]["A"]["single_p95_seconds"], 1000, 1)
    variation = [
        f"{DATASET_NAMES[ds]}: {100 * spread(c['models']['A']['nodes_per_flow']):.1f}% nos nós "
        f"por fluxo, {100 * spread(c['models']['A']['batch_seconds']):.0f}% no tempo em lote e "
        f"{100 * spread(c['models']['A']['single_seconds']):.0f}% no fluxo a fluxo"
        for ds, c in s["datasets"].items()
    ]
    return [
        "- **Profundidade 5, lote contra fluxo a fluxo.** A razão de tempo de A-prof5 sobre A é "
        f"{ratio(s, 'cira', 'A-prof5', 'batch_seconds'):.2f} em lote e "
        f"{ratio(s, 'cira', 'A-prof5', 'single_seconds'):.2f} fluxo a fluxo, com razão de nós "
        f"por fluxo {ratio(s, 'cira', 'A-prof5', 'nodes_per_flow'):.2f}. Numa chamada de um "
        "fluxo, a parte do tempo que não depende da profundidade das árvores domina; não se mediu "
        "qual é essa parte.",
        f"- **A-prof5 contra A fluxo a fluxo, no limite da regra.** O módulo da diferença média "
        f"supera o desvio padrão das diferenças em {100 * excess:.1f}%. A-prof5 é mais rápido em "
        f"{single['second_wins']} de 10 seeds, com razão por seed entre "
        f"{single['min_ratio']:.3f} e {single['max_ratio']:.3f}. O veredito da regra fica como "
        "está; a frase que os números sustentam é que A-prof5 é cerca de "
        f"{100 * (1 - single['mean_ratio']):.0f}% mais rápido por fluxo, em todas as seeds.",
        "- **Variação entre seeds.** Coeficiente de variação de A entre as seeds: "
        + "; ".join(variation)
        + ". Os nós por fluxo quase não variam, e o tempo varia muito: a variação vem do estado "
        "da máquina em cada seed, não do modelo. Por isso os tempos absolutos e os p95 não se "
        f"citam sozinhos; as razões pareadas e os nós por fluxo, sim. No {DATASET_NAMES['cira']}, "
        f"o p95 fluxo a fluxo de A foi {p95} ms.",
    ]


LIMITATIONS = [
    "- Uma máquina, uma thread de predição sem núcleo fixo, sem isolamento de outros processos. "
    "O sistema operacional não permite fixar a thread em um núcleo; a máquina tem núcleos de "
    "tipos diferentes e pode reduzir a frequência com a temperatura, e as threads da biblioteca "
    "de álgebra linear não foram limitadas. As repetições e os modelos foram intercalados, o que "
    "protege as razões pareadas, mas o tempo absoluto não se transfere para outra máquina; as "
    "medidas citáveis são as razões pareadas e os nós por fluxo.",
    "- O tempo é o da implementação (scikit-learn e mlxtend), não o do algoritmo: o empilhamento "
    "do mlxtend faz três predições de Random Forest e uma da regressão logística por chamada.",
    "- Não mede a extração de atributos do tráfego nem a espera pelo fim do fluxo, que vêm antes "
    "da predição num detector real e não dependem do modelo.",
    "- O artigo não publica tempo de inferência: não há alvo para comparar.",
    "- Antes do commit da hipótese, as funções de medição rodaram uma vez em uma amostra de 40 mil "
    "fluxos do CIRA, com A, A-prof5 e M1 ajustados nessa amostra e sem M1M2, para conferir que "
    "funcionavam. Esse teste exibiu os nós por fluxo e os tempos em lote e fluxo a fluxo dos três "
    "modelos. A hipótese já estava escrita e não mudou depois dele, mas a ordem dos commits não "
    "comprova isso: as expectativas 2 e 3 sobre A, A-prof5 e M1 devem ser citadas como "
    "registradas depois de um teste de funcionamento. As expectativas sobre M1M2 não são "
    "afetadas.",
]


def resumo_markdown(summary: dict, loaded_meta: dict) -> str:
    """Escreve o RESUMO-INFERENCIA.md a partir do agregado."""
    parts = [
        "# E8: tempo de inferência",
        "",
        "Gerado por `scripts/e8_inferencia_resumo.py` a partir de "
        "`results/e8/corrigida/inferencia-<dados>/seed<k>/`. Hipótese, regra de leitura e o que "
        "seria inesperado: `HIPOTESE-INFERENCIA.md`, escrita antes da execução completa (ver, nas "
        "limitações, o teste de funcionamento anterior ao commit dela).",
        "",
        f"Seeds: {', '.join(str(seed) for seed in summary['seeds'])}. Tempo de normalizar e "
        "predizer, com uma thread. Lote: mediana de 5 repetições do teste inteiro. Fluxo a fluxo: "
        "mediana e percentil 95 de 1000 fluxos do teste preditos um por chamada. Média ± desvio "
        "padrão amostral entre as seeds. Nós por fluxo: nós de árvore percorridos por um fluxo, "
        "somados em todas as árvores, sem o meta-classificador de A.",
        "",
        f"Máquina (nome, núcleos): {loaded_meta['machine']}. Commits: {loaded_meta['commits']}.",
    ]
    for dataset, content in summary["datasets"].items():
        parts += [
            "",
            f"## {DATASET_NAMES[dataset]}",
            "",
            f"Teste: {content['test_rows']} fluxos.",
            "",
            models_table(content),
            "",
            pairs_table(content),
        ]
    parts += ["", "## Hipótese ao lado do resultado", "", *expected_lines(summary)]
    parts += ["", "Resultados que a hipótese declarou como inesperados:", ""]
    parts += unexpected_lines(summary)
    parts += ["", "## Leitura posterior", ""]
    parts += [
        "Acrescentada depois de ver os números. Não muda a regra de leitura nem os vereditos "
        "acima.",
        "",
        *posterior_lines(summary),
    ]
    parts += ["", "## Fluxos por segundo nesta máquina (posterior)", "", *throughput_lines(summary)]
    parts += ["", "## Limitações", "", *LIMITATIONS]
    return "\n".join(parts) + "\n"


def main() -> None:
    """Agrega as execuções gravadas e escreve o summary-inferencia.json e o RESUMO-INFERENCIA.md."""
    summary, meta = summary_content(E8_DIR, SEEDS_CORRIGIDA)
    (E8_DIR / "summary-inferencia.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (E8_DIR / "RESUMO-INFERENCIA.md").write_text(resumo_markdown(summary, meta), encoding="utf-8")
    print(f"Resumo em {(E8_DIR / 'RESUMO-INFERENCIA.md').relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
