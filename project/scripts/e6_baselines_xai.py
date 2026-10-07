"""E6: modelos de comparação da Tabela II e SHAP no dataset combinado sem réplicas.

Refaz no segundo dataset (data/processed/combinado_sem_replicas.parquet, CIRA +
DoH-Tunnel-Traffic-HKD com cada fluxo do HKD uma única vez) o que
scripts/e2_baselines.py e scripts/e5_xai.py fazem no CIRA-CIC-DoHBrw-2020, com
as mesmas funções, a mesma seed (42) e o mesmo teste de 10% do sistema do
artigo em scripts/e6_dataset2.py:

- árvore de decisão, XGBoost e Random Forest da Tabela II, treinados no treino
  inteiro balanceado com SMOTE e avaliados no teste, com o recall de
  Malicious-DoH por ferramenta de túnel;
- valores SHAP dos três Random Forests base do sistema retreinado no
  combinado, nas duas leituras de profundidade, com as mesmas amostras por
  classe e as mesmas figuras de E5, e a concordância do ranking de importância
  com o do CIRA.

O que o experimento testa: se os modelos de comparação detectam as ferramentas
do HKD (dnstt, tcp-over-dns e tuns) quando elas estão no treino, e se os
atributos que mais pesam nos Random Forests base mudam quando a classe
maliciosa ganha essas ferramentas. Alvo de comparação: os resultados no CIRA
(results/e2/ e results/e5/) e o sistema do artigo no mesmo teste
(results/e6/<trilha>/retreino_sem_replicas/). O artigo não traz número para
este dataset. Contaria como inesperado: um modelo de comparação com recall das
ferramentas do HKD abaixo do intervalo de confiança do sistema de profundidade
variável, ou `Duration` fora dos primeiros atributos de Malicious-DoH, já que
a duração mediana dos fluxos do HKD é maior que a dos maliciosos do CIRA.

Grava metrics.json e run.json em
results/e6/fiel/retreino_sem_replicas-<modelo>/seed42/ (os modelos de
comparação não dependem da leitura de profundidade e ficam na trilha em que
E2 os gravou) e, com a tabela de importância e as figuras, em
results/e6/<trilha>/retreino_sem_replicas-shap/seed42/. Os arquivos RESUMO.md
são escritos por scripts/e6_resumo.py.

Roda como módulo, a partir da pasta do projeto, porque importa os outros scripts.

Uso: uv run python -m scripts.e6_baselines_xai
"""

import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

import scripts.e2_baselines as e2
import scripts.e5_xai as e5
import scripts.e6_dataset2 as e6
from doh_ids.config import (
    CLASS_NAMES,
    FEATURE_COLUMNS,
    RESULTS_DIR,
    SEED_FIEL,
    SHAP_SAMPLE_PER_CLASS,
    SHAP_TOP_FEATURES,
)
from doh_ids.evaluate import recall_by_tool
from doh_ids.explain import rank_agreement
from doh_ids.runlog import save_run

MALICIOUS = CLASS_NAMES.index("Malicious-DoH")

# O dataset principal desta etapa: o combinado sem réplicas, o mesmo do
# retreino do sistema.
SCENARIO = next(
    scenario for scenario in e6.RETRAINS if scenario["slice_name"] == "retreino_sem_replicas"
)
BASELINE_TRACK = "fiel"
SHAP_SLICE = f"{SCENARIO['slice_name']}-shap"

# Resultados com os quais esta execução é conferida e comparada: o retreino do
# sistema no mesmo dataset e a explicação do sistema no CIRA.
SYSTEM_DIR = RESULTS_DIR / "e6" / "variante" / SCENARIO["slice_name"] / f"seed{SEED_FIEL}"
E5_DIR = RESULTS_DIR / "e5"


def baseline_slice(name: str) -> str:
    """Devolve a pasta do resultado do modelo de comparação `name` neste dataset."""
    return f"{SCENARIO['slice_name']}-{name}"


def run_baselines(table: pd.DataFrame, data_sha256: str, results_dir: Path) -> dict:
    """Treina e avalia os três modelos de comparação sobre `table` e grava os resultados.

    `table` tem os atributos do modelo, `label`, `origin` e `tool`. Devolve,
    para cada modelo, o diretório da execução e o dicionário gravado em
    metrics.json.
    """
    assert (table.loc[table["tool"].notna(), "label"] == MALICIOUS).all(), (
        "Ferramenta de túnel em fluxo que não é Malicious-DoH."
    )
    test, evaluated = e2.evaluate_baselines(table)
    # A origem do fluxo malicioso faz o papel da ferramenta: o recall sai
    # separado para as três ferramentas do CIRA juntas e as três do HKD juntas.
    malicious_origin = test["origin"].where(test["label"] == MALICIOUS)
    results = {}
    for name, entry in evaluated.items():
        metrics = {
            **entry["metrics"],
            "dataset": SCENARIO["dataset"],
            "test_recall_by_tool": recall_by_tool(test["tool"], entry["predicted"]),
            "test_recall_by_origin": recall_by_tool(malicious_origin, entry["predicted"]),
        }
        run_dir = save_run(
            experiment="e6",
            track=BASELINE_TRACK,
            slice_name=baseline_slice(name),
            seed=SEED_FIEL,
            metrics=metrics,
            config={**entry["config"], "dataset": SCENARIO["dataset"]},
            data_sha256=data_sha256,
            timings=entry["timings"],
            results_dir=results_dir,
        )
        results[name] = (run_dir, metrics)
    return results


def ranking_scores(ranking: list[str]) -> pd.Series:
    """Devolve, por atributo, uma pontuação que decresce com o posto no ranking."""
    return pd.Series(range(len(ranking), 0, -1), index=ranking)


def cira_comparison(ranking: dict, cira_ranking: dict) -> dict:
    """Mede a concordância do ranking de importância com o do CIRA, por base e classe.

    `ranking` e `cira_ranking` levam cada base e cada classe à lista dos
    atributos, do mais para o menos importante. Devolve a correlação de postos
    de Spearman nos 29 atributos, a concordância nos atributos do topo, quantos
    atributos do topo são comuns e o topo do CIRA.
    """
    # O base de mesmo número não é o mesmo modelo nos dois datasets: cada um
    # foi treinado no seu subconjunto, com outro split. Compara-se o ranking.
    comparison = {}
    for base, by_class in ranking.items():
        comparison[base] = {}
        for class_name, features in by_class.items():
            cira_features = cira_ranking[base][class_name]
            scores, cira_scores = ranking_scores(features), ranking_scores(cira_features)
            correlation = spearmanr(scores[FEATURE_COLUMNS], cira_scores[FEATURE_COLUMNS])
            top, cira_top = features[:SHAP_TOP_FEATURES], cira_features[:SHAP_TOP_FEATURES]
            comparison[base][class_name] = {
                "spearman_all_features": float(correlation.statistic),
                "top_agreement": rank_agreement(scores, cira_scores, SHAP_TOP_FEATURES),
                "top_shared": len(set(top) & set(cira_top)),
                "cira_top": cira_top,
            }
    return comparison


def run_shap(
    table: pd.DataFrame, data_sha256: str, results_dir: Path, reading: dict, cira_ranking: dict
) -> tuple[Path, dict]:
    """Explica os Random Forests base do sistema retreinado sobre `table` e grava o resultado.

    `reading` é uma das leituras de profundidade de scripts/e6_dataset2.py e
    `cira_ranking` o ranking de importância da mesma leitura no CIRA. Devolve o
    diretório da execução e o dicionário gravado em metrics.json.
    """
    metrics, config, timings, artifacts = e5.explain_system(table, reading)
    metrics["dataset"] = SCENARIO["dataset"]
    metrics["cira_comparison"] = cira_comparison(metrics["ranking"], cira_ranking)
    run_dir = save_run(
        experiment="e6",
        track=reading["track"],
        slice_name=SHAP_SLICE,
        seed=SEED_FIEL,
        metrics=metrics,
        config={**config, "dataset": SCENARIO["dataset"]},
        data_sha256=data_sha256,
        timings=timings,
        results_dir=results_dir,
    )
    e5.write_artifacts(run_dir, *artifacts)
    return run_dir, metrics


def main() -> None:
    """Confere o Parquet e roda os modelos de comparação e o SHAP no combinado sem réplicas."""
    data_sha256 = e6.checked_sha256()[SCENARIO["dataset"]]
    # Lidos antes de treinar, para a falta de um resultado anterior parar o
    # script no começo.
    system_split = json.loads((SYSTEM_DIR / "metrics.json").read_text(encoding="utf-8"))["split"]
    # A explicação no CIRA usa, em cada trilha, a mesma pasta da reprodução.
    cira_rankings = {
        reading["track"]: json.loads(
            (
                E5_DIR
                / reading["track"]
                / reading["e1_slice"]
                / f"seed{SEED_FIEL}"
                / "metrics.json"
            ).read_text(encoding="utf-8")
        )["ranking"]
        for reading in e6.READINGS
    }
    table = pd.read_parquet(SCENARIO["path"])

    for name, (run_dir, metrics) in run_baselines(table, data_sha256, RESULTS_DIR).items():
        # Mesmo teste do sistema do artigo neste dataset: o total, as linhas por
        # classe e os fluxos de cada ferramenta são os registrados no retreino.
        assert metrics["test"]["total"] == system_split["test"]["total"], (
            f"{name}: teste com tamanho diferente do registrado no retreino do sistema."
        )
        assert metrics["test_rows"] == system_split["test"]["rows"]
        tools = {tool: entry["n"] for tool, entry in metrics["test_recall_by_tool"].items()}
        assert tools == system_split["test"]["rows_by_tool"]
        e6.print_run(e2.BASELINES[name]["label"], run_dir)
        print(e6.matrix_table(metrics["test"]["confusion_matrix"]))
        print(e6.recall_table(metrics["test_recall_by_tool"]))

    for reading in e6.READINGS:
        run_dir, metrics = run_shap(
            table, data_sha256, RESULTS_DIR, reading, cira_rankings[reading["track"]]
        )
        assert max(metrics["test_sample_rows"]) <= SHAP_SAMPLE_PER_CLASS
        e6.print_run(f"SHAP, {reading['label']}", run_dir)
        print(f"Amostra do treino: {metrics['train_sample_rows']}")
        print(f"Amostra do teste: {metrics['test_sample_rows']}")
        print(e5.stability_table(metrics))
    print("\nPara escrever os arquivos RESUMO.md: uv run python -m scripts.e6_resumo")


if __name__ == "__main__":
    main()
