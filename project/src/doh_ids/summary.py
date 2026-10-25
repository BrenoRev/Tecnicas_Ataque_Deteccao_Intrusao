"""Tabelas em Markdown dos arquivos RESUMO.md gravados em results/."""

from collections.abc import Iterable

import pandas as pd


def markdown_table(columns: list[str], rows: Iterable[Iterable]) -> str:
    """Escreve uma tabela em Markdown a partir dos nomes das colunas e das linhas."""
    lines = [" | ".join(columns), " | ".join("---" for _ in columns)]
    lines += [" | ".join(str(value) for value in row) for row in rows]
    return "\n".join(f"| {line} |" for line in lines)


def frame_markdown_table(frame: pd.DataFrame) -> str:
    """Escreve um DataFrame em Markdown, com o índice na primeira coluna."""
    frame = frame.reset_index()
    return markdown_table(list(frame.columns), frame.itertuples(index=False))
