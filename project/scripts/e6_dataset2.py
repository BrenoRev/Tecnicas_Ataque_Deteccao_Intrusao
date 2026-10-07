"""E6: o sistema do artigo no segundo dataset, nas duas leituras de profundidade.

Três cenários, todos com a seed 42 e o mesmo protocolo da reprodução no
CIRA-CIC-DoHBrw-2020 (E1):

- transferência: o sistema ajustado no treino do CIRA prediz os fluxos do
  DoH-Tunnel-Traffic-HKD (data/processed/hkd.parquet), normalizados com o
  scaler do treino do CIRA. O HKD só tem a classe maliciosa: mede-se o recall,
  total e por ferramenta, e para que classe vão os erros;
- retreino no combinado sem réplicas (data/processed/combinado_sem_replicas.parquet):
  split 90/10 estratificado, sistema inteiro refeito, teste e validação
  cruzada de 10 folds;
- retreino no combinado como publicado (data/processed/combinado.parquet), em
  que cada fluxo do HKD aparece 20 vezes: o mesmo, sem a validação cruzada.

O sistema é treinado com os Random Forests base sem limite de profundidade
("variable tree depth", linha 3 do Algoritmo 1), que é o sistema base desta
etapa, e com profundidade máxima 5 (Seção IV-B), ao lado.

Grava metrics.json e run.json em results/e6/<trilha>/<cenário>/seed42/, com a
trilha `variante` para a profundidade variável e `fiel` para a profundidade 5.
Os arquivos RESUMO.md de results/e6/ são escritos por scripts/e6_resumo.py, a
partir dos metrics.json, com as funções de texto deste arquivo.

Uso: uv run python scripts/e6_dataset2.py
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.classifier import StackingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    COMBINED_PARQUET_PATH,
    COMBINED_UNIQUE_PARQUET_PATH,
    CV_FOLDS,
    CV_SHUFFLE,
    FEATURE_COLUMNS,
    FIEL_READINGS,
    HKD_PARQUET_PATH,
    HKD_REPLICAS,
    MAX_DEPTH,
    MAX_DEPTH_VARIABLE,
    MAX_FEATURES,
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
from doh_ids.evaluate import (
    evaluate,
    malicious_only_metrics,
    metrics_from_confusion,
    outside_unit_interval,
    recall_by_tool,
)
from doh_ids.runlog import save_run
from doh_ids.splits import seen_in_train, stratified_split
from doh_ids.system import cross_validated_confusion, fit_system

LABELS = list(range(len(CLASS_NAMES)))
MALICIOUS = CLASS_NAMES.index("Malicious-DoH")

# Resultados das etapas anteriores, com os quais esta execução é conferida.
E0_DIR = RESULTS_DIR / "e0" / "dados" / "cira" / f"seed{SEED_FIEL}"
E1_DIR = RESULTS_DIR / "e1"
E6_DATA_DIR = RESULTS_DIR / "e6" / "dados"

# As duas leituras da profundidade dos Random Forests base. A de profundidade
# variável vem primeiro porque é o sistema base desta etapa: na reprodução, o
# sistema de profundidade 5 não prediz Benign-DoH em nenhuma linha do teste.
# `e1_slice` é a pasta do resultado da mesma leitura no CIRA.
READINGS = [
    {
        "track": "variante",
        "e1_slice": "profundidade_variavel",
        "max_depth": MAX_DEPTH_VARIABLE,
        "label": "variante (profundidade variável)",
        "base_depth": 'sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1)',
    },
    {
        "track": "fiel",
        "e1_slice": "proposto",
        "max_depth": MAX_DEPTH,
        "label": f"fiel (profundidade {MAX_DEPTH})",
        "base_depth": f"profundidade máxima {MAX_DEPTH} nos submodelos (Seção IV-B)",
    },
]

TRANSFER_SLICE = "transferencia"

# Os dois retreinos. O combinado sem réplicas é o dataset principal e recebe a
# validação cruzada; o combinado como publicado é análise ao lado, e nele só o
# tamanho dos folds é gerado, sem treinar.
RETRAINS = [
    {
        "slice_name": "retreino_sem_replicas",
        "dataset": "combinado_sem_replicas",
        "title": "combinado sem réplicas",
        "path": COMBINED_UNIQUE_PARQUET_PATH,
        "hkd_replicas": False,
        "cross_validation": True,
    },
    {
        "slice_name": "retreino_publicado",
        "dataset": "combinado",
        "title": "combinado como publicado",
        "path": COMBINED_PARQUET_PATH,
        "hkd_replicas": True,
        "cross_validation": False,
    },
]


def base_mean_proba(stacked: StackingClassifier, X: np.ndarray) -> np.ndarray:
    """Devolve a média das probabilidades por classe dos Random Forests base."""
    return np.mean([forest.predict_proba(X) for forest in stacked.clfs_], axis=0)


def tool_counts(flows: pd.DataFrame) -> dict:
    """Conta os fluxos de cada ferramenta de túnel presente, pelo nome."""
    counts = flows["tool"].value_counts().sort_index()
    return {name: int(count) for name, count in counts.items()}


def validation_fold_rows(train: pd.DataFrame) -> list[list[int]]:
    """Conta as amostras por classe do fold de validação de cada rodada."""
    # Os folds são os mesmos da validação cruzada do sistema: sorteados só
    # dentro do treino, com a mesma seed. A contagem usa só os índices.
    folds = StratifiedKFold(n_splits=CV_FOLDS, shuffle=CV_SHUFFLE, random_state=SEED_FIEL)
    return [
        class_counts(train.iloc[validation]) for _, validation in folds.split(train, train["label"])
    ]


def split_table(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Conta as amostras por classe no treino, em cada fold de validação e no teste."""
    train_rows = class_counts(train)
    validation_rows = validation_fold_rows(train)
    return {
        "test_size": TEST_SIZE,
        "train": {"rows": train_rows, "total": len(train), "rows_by_tool": tool_counts(train)},
        "test": {"rows": class_counts(test), "total": len(test), "rows_by_tool": tool_counts(test)},
        "validation_folds": {
            "n_folds": CV_FOLDS,
            "shuffle": CV_SHUFFLE,
            "validation_rows": validation_rows,
            "train_rows": np.subtract(train_rows, validation_rows).tolist(),
        },
    }


def run_config(stacked: StackingClassifier, reading: dict, datasets: dict) -> dict:
    """Monta a configuração gravada em run.json: hiperparâmetros, leituras e datasets."""
    return {
        "n_estimators": N_ESTIMATORS,
        # A profundidade é lida do modelo ajustado, para o registro dizer o que
        # foi treinado e não o que foi pedido.
        "max_depth": stacked.clfs_[0].max_depth,
        "max_features": MAX_FEATURES,
        "criterion": stacked.clfs_[0].criterion,
        "n_subsets": N_SUBSETS,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "cv_shuffle": CV_SHUFFLE,
        "n_jobs": N_JOBS,
        "smote_seeds": [smote_seed(SEED_FIEL, index) for index in range(N_SUBSETS)],
        "readings": {**FIEL_READINGS, "base_depth": reading["base_depth"]},
        **datasets,
    }


def run_transfer(
    cira: pd.DataFrame, hkd: pd.DataFrame, sha256: dict, results_dir: Path, reading: dict
) -> tuple[Path, dict]:
    """Ajusta o sistema no treino do CIRA, prediz os fluxos do HKD e grava o resultado.

    `cira` e `hkd` têm os atributos do modelo e `label`; `hkd` tem também
    `tool`, e todos os fluxos dele são Malicious-DoH. `sha256` leva `cira` e
    `hkd` ao hash de cada tabela. Neste cenário o HKD inteiro é teste: nenhum
    fluxo dele entra em ajuste algum. Devolve o diretório da execução e o
    dicionário gravado em metrics.json.
    """
    start = time.perf_counter()
    assert (hkd["label"] == MALICIOUS).all(), "O HKD só tem fluxos de túnel."
    train, test = stratified_split(cira, SEED_FIEL)
    scaler, stacked, _, timings = fit_system(train, SEED_FIEL, reading["max_depth"])

    # O scaler aplicado ao HKD é o do treino do CIRA: ajustado também com o
    # HKD, ele vazaria o mínimo e o máximo do conjunto avaliado e esconderia a
    # mudança de faixa que a contagem abaixo mede.
    train_features = feature_matrix(train)
    assert scaler.n_samples_seen_ == len(train), "O scaler viu linhas fora do treino do CIRA."
    assert np.array_equal(scaler.data_min_, train_features.min()), "Mínimo de outro conjunto."
    assert np.array_equal(scaler.data_max_, train_features.max()), "Máximo de outro conjunto."

    X_hkd = scaler.transform(feature_matrix(hkd))
    X_test = scaler.transform(feature_matrix(test))
    metrics = {
        "classes": CLASS_NAMES,
        "train_dataset": "cira",
        "evaluated_dataset": "hkd",
        "train_rows": class_counts(train),
        "hkd_rows": len(hkd),
        "hkd_rows_by_tool": tool_counts(hkd),
        "hkd": malicious_only_metrics(hkd["tool"], stacked.predict(X_hkd)),
        "hkd_outside_unit_interval": outside_unit_interval(X_hkd),
        # O teste do CIRA entra só como referência: a contagem fora da faixa ao
        # lado da do HKD, e a matriz, que confere que o sistema transferido é
        # o mesmo da reprodução.
        "cira_test_outside_unit_interval": outside_unit_interval(X_test),
        "cira_test_confusion_matrix": confusion_matrix(
            test["label"], stacked.predict(X_test), labels=LABELS
        ).tolist(),
    }
    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    datasets = {
        "train_dataset": "cira",
        "evaluated_dataset": "hkd",
        "evaluated_data_sha256": sha256["hkd"],
        "cross_validation": False,
    }
    run_dir = save_run(
        experiment="e6",
        track=reading["track"],
        slice_name=TRANSFER_SLICE,
        seed=SEED_FIEL,
        metrics=metrics,
        config=run_config(stacked, reading, datasets),
        data_sha256=sha256["cira"],
        timings=timings,
        results_dir=results_dir,
    )
    return run_dir, metrics


def run_retrain(
    table: pd.DataFrame, data_sha256: str, results_dir: Path, reading: dict, scenario: dict
) -> tuple[Path, dict]:
    """Refaz o sistema inteiro sobre o dataset combinado e grava o resultado.

    `table` tem os atributos do modelo, `label`, `origin` e `tool`; `scenario`
    é uma das entradas de `RETRAINS`. Devolve o diretório da execução e o
    dicionário gravado em metrics.json.
    """
    start = time.perf_counter()
    assert (table.loc[table["tool"].notna(), "label"] == MALICIOUS).all(), (
        "Ferramenta de túnel em fluxo que não é Malicious-DoH."
    )
    # O teste é separado antes de qualquer ajuste e só volta na avaliação final.
    train, test = stratified_split(table, SEED_FIEL)
    assert train.index.intersection(test.index).empty, "Linha no treino e no teste."

    # Fluxo do HKD no teste com os mesmos 29 atributos de um fluxo do HKD no
    # treino já foi visto pelo modelo: o recall dele mede memorização. Sem as
    # réplicas isso não pode acontecer.
    test_hkd = test[test["origin"] == "HKD"]
    hkd_seen = int(seen_in_train(train[train["origin"] == "HKD"], test_hkd).sum())
    if not scenario["hkd_replicas"]:
        assert hkd_seen == 0, f"{hkd_seen} vetores do HKD no treino e no teste ao mesmo tempo."

    scaler, stacked, summary, timings = fit_system(train, SEED_FIEL, reading["max_depth"])
    X_test = scaler.transform(feature_matrix(test))
    predicted = stacked.predict(X_test)
    test_metrics = evaluate(
        test["label"].to_numpy(),
        predicted,
        stacked.predict_proba(X_test),
        base_mean_proba(stacked, X_test),
    )
    # Amostra sintética só existe dentro dos subconjuntos de treino: a matriz
    # do teste tem, por classe, exatamente as linhas reais do teste.
    assert [sum(row) for row in test_metrics["confusion_matrix"]] == class_counts(test)

    # A origem do fluxo malicioso faz o papel da ferramenta: o recall sai
    # separado para as três ferramentas do CIRA juntas e as três do HKD juntas.
    malicious_origin = test["origin"].where(test["label"] == MALICIOUS)
    metrics = {
        "classes": CLASS_NAMES,
        "dataset": scenario["dataset"],
        "split": split_table(train, test),
        "hkd_test_rows": len(test_hkd),
        "hkd_test_rows_seen_in_train": hkd_seen,
        "test": test_metrics,
        "test_recall_by_tool": recall_by_tool(test["tool"], predicted),
        "test_recall_by_origin": recall_by_tool(malicious_origin, predicted),
        "subsets": summary,
    }
    if scenario["cross_validation"]:
        cv_start = time.perf_counter()
        cv_confusion = cross_validated_confusion(train, SEED_FIEL, reading["max_depth"])
        timings["cross_validation_seconds"] = round(time.perf_counter() - cv_start, 1)
        # Cada linha real do treino é predita uma vez, e nenhuma sintética.
        assert [sum(row) for row in cv_confusion] == class_counts(train), (
            "A matriz de validação não soma o treino."
        )
        metrics["cross_validation"] = metrics_from_confusion(cv_confusion)

    timings["total_seconds"] = round(time.perf_counter() - start, 1)
    datasets = {"dataset": scenario["dataset"], "cross_validation": scenario["cross_validation"]}
    run_dir = save_run(
        experiment="e6",
        track=reading["track"],
        slice_name=scenario["slice_name"],
        seed=SEED_FIEL,
        metrics=metrics,
        config=run_config(stacked, reading, datasets),
        data_sha256=data_sha256,
        timings=timings,
        results_dir=results_dir,
    )
    return run_dir, metrics


def markdown_table(columns: list[str], rows: list[list]) -> str:
    """Escreve uma tabela em Markdown."""
    lines = [" | ".join(columns), " | ".join("---" for _ in columns)]
    lines += [" | ".join(str(value) for value in row) for row in rows]
    return "\n".join(f"| {line} |" for line in lines)


def matrix_table(confusion: list[list[int]]) -> str:
    """Escreve uma matriz de confusão em Markdown, com o nome das classes."""
    rows = [[name, *row] for name, row in zip(CLASS_NAMES, confusion, strict=True)]
    return markdown_table(["real \\ predito", *CLASS_NAMES], rows)


def recall_row(name: str, entry: dict) -> list:
    """Monta a linha de uma tabela de recall: fluxos, detectados, recall, intervalo e erros."""
    return [
        name,
        entry["n"],
        entry["detected"],
        f"{entry['recall']:.2%}",
        f"{entry['recall_ci_low']:.2%} a {entry['recall_ci_high']:.2%}",
        entry["predicted_as"]["Non-DoH"],
        entry["predicted_as"]["Benign-DoH"],
    ]


def recall_table(entries: dict) -> str:
    """Escreve o recall de Malicious-DoH de cada grupo de fluxos, com `n` e intervalo."""
    columns = [
        "fluxos de túnel",
        "n",
        "detectados",
        "recall",
        "intervalo de confiança de 95%",
        "erros para Non-DoH",
        "erros para Benign-DoH",
    ]
    return markdown_table(columns, [recall_row(name, entry) for name, entry in entries.items()])


def class_metrics_table(metrics: dict) -> str:
    """Escreve suporte, precisão, recall e F1 de cada classe e as médias macro e ponderada."""
    # As classes entram pela ordem dos códigos, e não pela ordem das chaves:
    # lido de metrics.json, o dicionário vem em ordem alfabética.
    rows = [
        [
            name,
            metrics["per_class"][name]["support"],
            f"{metrics['per_class'][name]['precision']:.4%}",
            f"{metrics['per_class'][name]['recall']:.4%}",
            f"{metrics['per_class'][name]['f1']:.4%}",
        ]
        for name in CLASS_NAMES
    ]
    for average, title in [("macro", "média macro"), ("weighted", "média ponderada")]:
        values = [f"{metrics[f'{average}_{key}']:.4%}" for key in ("precision", "recall", "f1")]
        rows.append([title, metrics["total"], *values])
    return markdown_table(["classe", "fluxos", "precisão", "recall", "F1"], rows)


def never_predicted_text(confusion: list[list[int]]) -> str:
    """Escreve o aviso sobre as classes que o modelo não prediz em nenhuma linha.

    Devolve texto vazio quando todas as classes são preditas ao menos uma vez.
    """
    never = [name for index, name in enumerate(CLASS_NAMES) if not any(r[index] for r in confusion)]
    if not never:
        return ""
    return (
        f"O modelo não prediz {' nem '.join(never)} em nenhuma linha. A precisão de uma "
        "classe sem predição é indefinida: ela entra como 0 na precisão macro e no F1 macro."
    )


def relation(value: float, reference: float) -> str:
    """Diz, em palavras, se `value` é menor, igual ou maior que `reference`."""
    if value == reference:
        return "igual ao"
    return "menor que o" if value < reference else "maior que o"


def outside_text(outside: dict) -> str:
    """Escreve a contagem de valores normalizados fora do intervalo de 0 a 1."""
    by_column = ", ".join(f"`{name}` {count}" for name, count in outside["by_column"].items())
    return f"{outside['values']} valores em {outside['rows']} fluxos" + (
        f" ({by_column})" if by_column else ""
    )


def transfer_section(transfer: dict, e1_test: dict) -> str:
    """Escreve a seção da transferência do CIRA para o HKD."""
    total, outside = transfer["hkd"]["malicious"], transfer["hkd_outside_unit_interval"]
    missed = total["n"] - total["detected"]
    e1_recall = e1_test["per_class"]["Malicious-DoH"]["recall"]
    if outside["values"]:
        range_text = (
            "Nesses atributos há fluxos do HKD além do mínimo ou do máximo do treino do CIRA."
        )
    else:
        range_text = (
            "Nenhum atributo do HKD sai da faixa do treino do CIRA: a diferença entre os dois "
            "conjuntos é de posição dentro da faixa (medianas em "
            "`../dados/hkd/seed42/medianas_malicioso.csv`), e não de faixa. A contagem não "
            "aponta atributo que explique os erros."
        )
    return f"""## Transferência: treino no CIRA, avaliação no HKD

O sistema é ajustado só com o treino do CIRA ({sum(transfer["train_rows"])} fluxos) e
prediz os {transfer["hkd_rows"]} fluxos do HKD, normalizados com o scaler do treino do
CIRA. O HKD só tem a classe maliciosa e não permite treinar o sistema: neste
cenário tudo é teste, não há treino nem validação com fluxos do HKD.

Sem fluxo legítimo no conjunto não há falso positivo: precisão, FPR e acurácia
não são calculados. A medida é o recall de Malicious-DoH.

{recall_table({"HKD, as três ferramentas": total, **transfer["hkd"]["by_tool"]})}

- **Recall de Malicious-DoH no HKD: {total["recall"]:.2%}.** De {total["n"]} túneis de
  ferramentas que o sistema nunca viu, {missed} passam sem alerta. É
  {relation(total["recall"], e1_recall)} recall de Malicious-DoH no teste do CIRA na mesma
  leitura ({e1_recall:.2%}, em `results/e1/`).
- **Destino dos erros: {total["predicted_as"]["Non-DoH"]} para Non-DoH e
  {total["predicted_as"]["Benign-DoH"]} para Benign-DoH.** O erro para Non-DoH trata o túnel como
  HTTPS comum; o erro para Benign-DoH, como DoH legítimo. Nos dois o operador
  não recebe alerta.
- **Valores normalizados fora de [0, 1] no HKD: {outside_text(outside)}.** No teste do
  CIRA, com o mesmo scaler: {outside_text(transfer["cira_test_outside_unit_interval"])}.
  {range_text}
"""


def samples_table(split: dict) -> str:
    """Escreve as amostras por classe no treino, em cada fold de validação e no teste."""
    folds = split["validation_folds"]["validation_rows"]
    rows = [["treino", *split["train"]["rows"], split["train"]["total"]]]
    rows += [
        [f"validação, fold {number}", *fold, sum(fold)] for number, fold in enumerate(folds, 1)
    ]
    rows.append(["teste", *split["test"]["rows"], split["test"]["total"]])
    return markdown_table(["conjunto", *CLASS_NAMES, "total"], rows)


def tools_table(split: dict) -> str:
    """Escreve os fluxos de cada ferramenta de túnel no treino e no teste."""
    train, test = split["train"]["rows_by_tool"], split["test"]["rows_by_tool"]
    rows = [[name, train[name], test.get(name, 0)] for name in train]
    return markdown_table(["ferramenta", "treino", "teste"], rows)


def validation_text(metrics: dict, e1: dict) -> str:
    """Escreve a validação cruzada do retreino, ou o motivo de ela não ter sido feita."""
    if "cross_validation" not in metrics:
        return (
            "Neste cenário a validação cruzada não é executada: ele é análise ao lado do "
            "combinado sem réplicas. A tabela de amostras por fold acima vem só dos índices."
        )
    validation = metrics["cross_validation"]
    e1_accuracy = e1["cross_validation"]["accuracy"]
    return f"""{CV_FOLDS} folds estratificados sobre o treino. Em cada rodada o scaler, os
subconjuntos, o SMOTE, os bases e o meta são refeitos com os nove folds de
treino; o fold deixado de fora só é predito. A matriz soma o treino original,
sem amostra sintética.

{matrix_table(validation["confusion_matrix"])}

{class_metrics_table(validation)}

Acurácia de {validation["accuracy"]:.4%} e F1 macro de {validation["macro_f1"]:.4%}; na
validação cruzada do CIRA, na mesma leitura, a acurácia é {e1_accuracy:.4%}
(`results/e1/`).

{never_predicted_text(validation["confusion_matrix"])}"""


def retrain_section(metrics: dict, scenario: dict, e1: dict) -> str:
    """Escreve a seção de um retreino: amostras por conjunto, teste e validação cruzada."""
    test, split = metrics["test"], metrics["split"]
    binary, hkd = test["malicious_vs_rest"], metrics["test_recall_by_origin"]["HKD"]
    benign = test["per_class"]["Benign-DoH"]
    seen, hkd_rows = metrics["hkd_test_rows_seen_in_train"], metrics["hkd_test_rows"]
    if scenario["hkd_replicas"]:
        seen_text = (
            f"{seen} dos {hkd_rows} fluxos do HKD no teste ({seen / hkd_rows:.2%}) têm os mesmos "
            f"{len(FEATURE_COLUMNS)} atributos de um fluxo do HKD no treino: são cópias, e o "
            "recall delas mede memorização."
        )
    else:
        seen_text = (
            f"Nenhum dos {hkd_rows} fluxos do HKD no teste tem os mesmos {len(FEATURE_COLUMNS)} "
            "atributos de um fluxo do HKD no treino (conferido por asserção no script)."
        )
    return f"""## Retreino no {scenario["title"]}

Split 90/10 estratificado pelas três classes, scaler ajustado no treino do
combinado, três subconjuntos, três bases e meta, como em E1.

### Amostras por classe em cada conjunto

{samples_table(split)}

Fluxos de túnel por ferramenta:

{tools_table(split)}

{seen_text}

### Teste

{matrix_table(test["confusion_matrix"])}

{class_metrics_table(test)}

- **Acurácia {test["accuracy"]:.4%}.** No teste do CIRA, na mesma leitura:
  {e1["test"]["accuracy"]:.4%}. A maior parte do teste é Non-DoH e são as mesmas linhas do
  CIRA: a acurácia não diz se as ferramentas novas são detectadas.
- **Recall de Malicious-DoH {test["per_class"]["Malicious-DoH"]["recall"]:.4%}.** Soma as seis
  ferramentas; as três do CIRA têm {metrics["test_recall_by_origin"]["CIRA"]["n"]} dos
  {test["per_class"]["Malicious-DoH"]["support"]} fluxos de túnel do teste.
- **Recall das ferramentas do HKD {hkd["recall"]:.2%}.** {hkd["detected"]} de {hkd["n"]} túneis
  detectados; intervalo de confiança de 95%: de {hkd["recall_ci_low"]:.2%} a
  {hkd["recall_ci_high"]:.2%}. São os túneis das ferramentas que o artigo não avaliou.
- **FPR de Malicious-DoH contra o resto {binary["fpr"]:.4%}.** {binary["false_positives"]} de
  {binary["negatives"]} fluxos legítimos classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de 95%: de
  {binary["fpr_ci_low"]:.4%} a {binary["fpr_ci_high"]:.4%}.
- **Recall de Benign-DoH {benign["recall"]:.4%} e F1 macro {test["macro_f1"]:.4%}.** No teste do
  CIRA: {e1["test"]["per_class"]["Benign-DoH"]["recall"]:.4%} e {e1["test"]["macro_f1"]:.4%}.
- **AUC-ROC one-vs-rest macro: {test["roc_auc_ovr_macro"]:.6f} pela saída do
  meta-classificador e {test["roc_auc_ovr_macro_base_mean"]:.6f} pela média das
  probabilidades dos bases.**

{never_predicted_text(test["confusion_matrix"])}

Recall de Malicious-DoH por ferramenta no teste:

{recall_table(metrics["test_recall_by_tool"])}

### Validação cruzada

{validation_text(metrics, e1)}
"""


def memorization_table(result: dict) -> str:
    """Põe lado a lado o recall das ferramentas do HKD nos três cenários."""
    tools = result[TRANSFER_SLICE]["hkd"]["by_tool"]
    columns = ["ferramenta", "transferência (HKD inteiro)"]
    columns += [f"retreino no {scenario['title']} (teste)" for scenario in RETRAINS]
    rows = []
    for name in tools:
        entries = [tools[name]]
        entries += [
            result[scenario["slice_name"]]["test_recall_by_tool"][name] for scenario in RETRAINS
        ]
        rows.append(
            [name]
            + [
                f"{entry['recall']:.2%} ({entry['detected']}/{entry['n']}; "
                f"{entry['recall_ci_low']:.2%} a {entry['recall_ci_high']:.2%})"
                for entry in entries
            ]
        )
    return markdown_table(columns, rows)


def copies_text(result: dict) -> str:
    """Escreve o que as cópias do HKD no teste permitem e não permitem concluir."""
    unique, published = result["retreino_sem_replicas"], result["retreino_publicado"]
    tools = result[TRANSFER_SLICE]["hkd"]["by_tool"]
    unique_train, published_train = (
        sum(metrics["split"]["train"]["rows_by_tool"][name] for name in tools)
        for metrics in (unique, published)
    )
    seen = published["hkd_test_rows_seen_in_train"]
    return f"""O que foi medido: no retreino publicado, {seen} dos
{published["hkd_test_rows"]} fluxos do HKD no teste têm cópia idêntica no treino; no retreino
sem réplicas, {unique["hkd_test_rows_seen_in_train"]} dos {unique["hkd_test_rows"]}.

- **O que isso permite concluir.** No publicado, o recall das ferramentas do HKD
  é medido em fluxos que o modelo já recebeu no treino: ele não mede a detecção
  de fluxo novo dessas ferramentas. A coluna que mede isso é a do retreino sem
  réplicas.
- **O que isso não permite concluir.** A diferença de recall entre as duas
  colunas de retreino não é a medida do efeito das cópias. Os dois retreinos
  diferem também no split (as tabelas são diferentes, e treino e teste não têm
  as mesmas linhas), no número de fluxos do HKD no treino ({published_train} contra
  {unique_train}) e no teste ({published["hkd_test_rows"]} contra {unique["hkd_test_rows"]}). Nenhum
  desses fatores foi isolado.

A coluna da transferência não é comparável em tamanho: é o HKD inteiro, e o
sistema não viu nenhuma das três ferramentas."""


def summary_text(reading: dict, result: dict) -> str:
    """Monta o texto do sistema em uma leitura a partir das métricas de cada cenário.

    `result` leva o nome de cada cenário às métricas dele e `e1` às métricas da
    reprodução no CIRA na mesma leitura.
    """
    e1 = result["e1"]
    retrains = "\n".join(
        retrain_section(result[scenario["slice_name"]], scenario, e1) for scenario in RETRAINS
    )
    return f"""# E6: o sistema do artigo no segundo dataset, {reading["label"]}

Gerado por `scripts/e6_resumo.py`. Os números vêm dos arquivos `metrics.json`
de `transferencia/seed{SEED_FIEL}/`, `retreino_sem_replicas/seed{SEED_FIEL}/` e
`retreino_publicado/seed{SEED_FIEL}/`; os tempos estão nos `run.json`.
Random Forests base: {reading["base_depth"]}. Os cenários das duas leituras
estão lado a lado, com o CIRA, em `../RESUMO.md`; a hipótese escrita antes da
execução, em `../fiel/HIPOTESE.md`.
Uma única execução de cada cenário, com a seed {SEED_FIEL}: não há média nem desvio
padrão. Classes na ordem dos códigos: {", ".join(CLASS_NAMES)}.

## O que cada cenário usa

- O DoH-Tunnel-Traffic-HKD sozinho só tem a classe maliciosa (dnstt,
  tcp-over-dns e tuns): não permite treinar o sistema de três classes. Ele
  entra de duas formas: como teste, na transferência, e dentro do dataset
  combinado CIRA + HKD, nos retreinos.
- No combinado, Non-DoH e Benign-DoH são os fluxos do CIRA. O "outro dataset"
  só é novo na classe maliciosa: métricas gerais perto das do CIRA são
  esperadas e não medem generalização.
- No combinado como publicado, cada fluxo do HKD aparece {HKD_REPLICAS} vezes. O dataset
  principal desta etapa é o combinado sem réplicas, com cada fluxo do HKD uma
  única vez; o publicado vai ao lado.

{transfer_section(result[TRANSFER_SLICE], e1["test"])}
{retrains}
## Ferramentas do HKD nos três cenários

Recall de Malicious-DoH, com detectados sobre `n` e o intervalo de confiança
de 95% entre parênteses.

{memorization_table(result)}

{copies_text(result)}

## O que não foi feito

- O recall por ferramenta no retreino sem réplicas vem de uma única divisão,
  com a seed {SEED_FIEL}: é uma estimativa, com o intervalo ao lado. Não há média
  de várias seeds aqui.
- No combinado como publicado não há validação cruzada; só o tamanho dos folds.
- A validação cruzada grava só a matriz de confusão: não há recall por
  ferramenta nem AUC nos folds.
- Fluxos do HKD da mesma sessão de túnel podem cair um no treino e outro no
  teste sem serem cópias exatas. Isso não é medido, e o recall do retreino sem
  réplicas pode incluir esse efeito.
- Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada depois de ver
  os resultados.
"""


def scenario_row(scenario: str, reading: dict, evaluated: str, metrics: dict, hkd: str) -> list:
    """Monta a linha de um cenário avaliado com as três classes."""
    per_class = metrics["per_class"]
    return [
        scenario,
        reading["label"],
        evaluated,
        metrics["total"],
        f"{metrics['accuracy']:.4%}",
        f"{metrics['macro_f1']:.4%}",
        f"{per_class['Non-DoH']['recall']:.4%}",
        f"{per_class['Benign-DoH']['recall']:.4%}",
        f"{per_class['Malicious-DoH']['recall']:.4%}",
        f"{per_class['Malicious-DoH']['precision']:.4%}",
        f"{metrics['malicious_vs_rest']['fpr']:.4%}",
        hkd,
    ]


def scenario_rows(reading: dict, result: dict) -> list[list]:
    """Monta as linhas dos cenários de uma leitura: CIRA, transferência e os dois retreinos."""
    no_hkd, undefined = "sem fluxos do HKD", "não definido"
    transfer = result[TRANSFER_SLICE]["hkd"]["malicious"]
    rows = [
        scenario_row("CIRA (E1)", reading, "teste", result["e1"]["test"], no_hkd),
        scenario_row(
            "CIRA (E1)", reading, "validação cruzada", result["e1"]["cross_validation"], no_hkd
        ),
        [
            "transferência",
            reading["label"],
            "HKD inteiro",
            transfer["n"],
            *[undefined] * 4,
            f"{transfer['recall']:.4%}",
            *[undefined] * 2,
            f"{transfer['recall']:.2%}",
        ],
    ]
    for scenario in RETRAINS:
        metrics = result[scenario["slice_name"]]
        name = f"retreino no {scenario['title']}"
        rows.append(
            scenario_row(
                name,
                reading,
                "teste",
                metrics["test"],
                f"{metrics['test_recall_by_origin']['HKD']['recall']:.2%}",
            )
        )
        if "cross_validation" in metrics:
            rows.append(
                scenario_row(
                    name, reading, "validação cruzada", metrics["cross_validation"], "não medido"
                )
            )
    return rows


def hypothesis_lines(reading: dict, result: dict) -> str:
    """Põe os números de uma leitura ao lado de cada hipótese escrita antes da execução."""
    transfer, e1_test = result[TRANSFER_SLICE], result["e1"]["test"]
    recall = transfer["hkd"]["malicious"]["recall"]
    e1_recall = e1_test["per_class"]["Malicious-DoH"]["recall"]
    unique, published = result["retreino_sem_replicas"], result["retreino_publicado"]
    unique_hkd = unique["test_recall_by_origin"]["HKD"]
    published_hkd = published["test_recall_by_origin"]["HKD"]
    unique_test, published_test = unique["test"], published["test"]
    benign = {
        name: metrics["per_class"]["Benign-DoH"]["recall"]
        for name, metrics in [
            ("e1", e1_test),
            ("unique", unique_test),
            ("published", published_test),
        ]
    }
    return f"""### {reading["label"]}

1. Valores fora de [0, 1] na transferência:
   {outside_text(transfer["hkd_outside_unit_interval"])}; no teste do CIRA,
   {outside_text(transfer["cira_test_outside_unit_interval"])}.
2. Recall na transferência: {recall:.2%}, {relation(recall, e1_recall)} do teste do CIRA
   ({e1_recall:.2%}).
3. Recall das ferramentas do HKD no teste: {published_hkd["recall"]:.2%} no retreino publicado
   (intervalo de {published_hkd["recall_ci_low"]:.2%} a {published_hkd["recall_ci_high"]:.2%},
   n = {published_hkd["n"]}) e {unique_hkd["recall"]:.2%} no retreino sem réplicas (intervalo de
   {unique_hkd["recall_ci_low"]:.2%} a {unique_hkd["recall_ci_high"]:.2%}, n = {unique_hkd["n"]}).
4. Acurácia no teste: {e1_test["accuracy"]:.4%} no CIRA, {unique_test["accuracy"]:.4%} no combinado
   sem réplicas e {published_test["accuracy"]:.4%} no publicado.
5. Recall de Benign-DoH no teste: {benign["e1"]:.2%} no CIRA, {benign["unique"]:.2%} no combinado
   sem réplicas e {benign["published"]:.2%} no publicado."""


def checked_sha256() -> dict:
    """Confere o hash de cada tabela contra o registrado pela etapa de dados e os devolve."""
    sources = {
        "cira": (CIRA_PARQUET_PATH, E0_DIR),
        "hkd": (HKD_PARQUET_PATH, E6_DATA_DIR / "hkd" / f"seed{SEED_FIEL}"),
    }
    for scenario in RETRAINS:
        data_dir = E6_DATA_DIR / scenario["dataset"] / f"seed{SEED_FIEL}"
        sources[scenario["dataset"]] = (scenario["path"], data_dir)
    sha256 = {}
    for name, (path, data_dir) in sources.items():
        recorded = json.loads((data_dir / "metrics.json").read_text(encoding="utf-8"))
        sha256[name] = sha256_of(path)
        if sha256[name] != recorded["parquet_sha256"]:
            raise SystemExit(
                f"SHA-256 de {path.name} difere do registrado pela etapa de dados: "
                f"encontrado {sha256[name]}. Rode o script da etapa de dados de novo."
            )
    return sha256


def print_run(title: str, run_dir: Path) -> None:
    """Imprime os tempos e o destino de uma execução."""
    timings = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["timings"]
    print(f"\n== {title} ==", flush=True)
    print(f"Tempos, em segundos: {timings}")
    print(f"Resultados em {run_dir.relative_to(PROJECT_ROOT)}", flush=True)


def run_reading(reading: dict, sha256: dict, cira: pd.DataFrame, hkd: pd.DataFrame) -> None:
    """Roda os três cenários de uma leitura, conferindo o sistema do CIRA com o de E1."""
    e1_dir = E1_DIR / reading["track"] / reading["e1_slice"] / f"seed{SEED_FIEL}"
    e1 = json.loads((e1_dir / "metrics.json").read_text(encoding="utf-8"))
    cira_counts = json.loads((E0_DIR / "split_counts.json").read_text(encoding="utf-8"))

    run_dir, transfer = run_transfer(cira, hkd, sha256, RESULTS_DIR, reading)
    # O sistema transferido é o da reprodução: mesma matriz no teste do CIRA.
    assert transfer["cira_test_confusion_matrix"] == e1["test"]["confusion_matrix"], (
        "O sistema ajustado no CIRA difere do registrado em E1."
    )
    assert transfer["cira_test_outside_unit_interval"] == cira_counts["test_outside_unit_interval"]
    print_run(f"{reading['label']}: transferência", run_dir)
    print(recall_table(transfer["hkd"]["by_tool"]))

    for scenario in RETRAINS:
        table = pd.read_parquet(scenario["path"])
        run_dir, metrics = run_retrain(
            table, sha256[scenario["dataset"]], RESULTS_DIR, reading, scenario
        )
        print_run(f"{reading['label']}: retreino no {scenario['title']}", run_dir)
        print(matrix_table(metrics["test"]["confusion_matrix"]))
        print(recall_table(metrics["test_recall_by_tool"]))
        print(
            f"Fluxos do HKD no teste já vistos no treino: {metrics['hkd_test_rows_seen_in_train']}"
        )


def main() -> None:
    """Confere os Parquets e roda os cenários nas duas leituras."""
    sha256 = checked_sha256()
    cira = pd.read_parquet(CIRA_PARQUET_PATH)
    hkd = pd.read_parquet(HKD_PARQUET_PATH)
    for reading in READINGS:
        run_reading(reading, sha256, cira, hkd)
    print("\nPara escrever os arquivos RESUMO.md: uv run python -m scripts.e6_resumo")


if __name__ == "__main__":
    main()
