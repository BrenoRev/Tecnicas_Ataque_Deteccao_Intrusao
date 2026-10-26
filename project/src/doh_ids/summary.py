"""Tabelas em Markdown dos arquivos RESUMO.md gravados em results/."""

from collections.abc import Iterable

import pandas as pd

from doh_ids.config import CLASS_NAMES


def markdown_table(columns: list[str], rows: Iterable[Iterable]) -> str:
    """Escreve uma tabela em Markdown a partir dos nomes das colunas e das linhas."""
    lines = [" | ".join(columns), " | ".join("---" for _ in columns)]
    lines += [" | ".join(str(value) for value in row) for row in rows]
    return "\n".join(f"| {line} |" for line in lines)


def frame_markdown_table(frame: pd.DataFrame) -> str:
    """Escreve um DataFrame em Markdown, com o índice na primeira coluna."""
    frame = frame.reset_index()
    return markdown_table(list(frame.columns), frame.itertuples(index=False))


def one_feature_rule_text(measure: dict) -> str:
    """Escreve o que a regra de um só atributo mede no CIRA e no HKD.

    `measure` é o dicionário que a etapa de dados do segundo dataset grava para
    o atributo: os valores da regra, o desempenho dela nos dois conjuntos e o
    valor mais frequente no HKD.
    """
    rule, column = measure["rule"], measure["column"]
    values = "{" + ", ".join(f"{value:g}" for value in rule["values"]) + "}"
    malicious, legitimate, hkd = rule["cira_malicious"], rule["cira_legitimate"], rule["hkd"]
    frequent = measure["hkd_most_frequent_value"]
    by_group = frequent["fraction_by_group"]
    # As classes entram pela ordem dos códigos: lido de metrics.json, o
    # dicionário vem em ordem alfabética.
    cira_groups = ", ".join(
        f"{by_group[f'CIRA, {name}']:.2%} dos fluxos {name}" for name in CLASS_NAMES
    )
    return (
        f"No CIRA limpo inteiro, os valores {values} de `{column}` cobrem "
        f"{malicious['recall']:.2%} dos {malicious['n']} fluxos Malicious-DoH e ocorrem em "
        f"{legitimate['false_positives']} dos {legitimate['n']} fluxos legítimos (Non-DoH e "
        f"Benign-DoH). A regra de um só atributo que chama de malicioso o fluxo com `{column}` "
        f"nesse conjunto tem, no mesmo CIRA de onde os valores foram tirados, recall de "
        f"{malicious['recall']:.2%} e {legitimate['false_positives']} falso positivo em "
        f"{legitimate['n']} (FPR de {legitimate['fpr']:.4%}). Nos {hkd['n']} fluxos do HKD ela "
        f"detecta {hkd['detected']} ({hkd['recall']:.2%}): "
        f"{measure['hkd_fraction_with_cira_malicious_value']:.2%} dos fluxos do HKD têm um valor "
        f"de `{column}` que ocorre no Malicious-DoH do CIRA. O valor mais frequente no HKD, "
        f"{frequent['value']:g} ({by_group['HKD, Malicious-DoH']:.2%} dos fluxos), é, no CIRA, o "
        f"de {cira_groups}."
    )
