"""Compara os resultados versionados com os regenerados por uma execução limpa.

Recebe dois diretórios results/ (o versionado e o regenerado) e, se pedido, os
dois diretórios report/. Não treina nada e não altera nenhum arquivo.

O que é comparado, por arquivo de mesmo caminho nas duas árvores:

- metrics.json, split_counts.json, o summary.json do protocolo corrigido, os
  CSV, os .tex e o INDICE.md: byte a byte.
- os dois agregados da modificação (summary.json e summary-robustez.json):
  depois de lidos, sem os valores de tempo, que mudam a cada execução.

O que só é informado, sem contar como diferença: os RESUMO*.md e as tabelas do
relatório que citam tempo de treino. Fora da comparação: run.json (commit, data
e tempos), PNG, PDF e os demais arquivos.

Sai com código 1 se algum arquivo comparado diferir ou faltar em uma das árvores.

Uso: uv run python scripts/comparar_resultados.py <results versionado> <results regenerado>
     [--report <report versionado> <report regenerado>]
"""

import argparse
import json
import sys
from pathlib import Path

# Chaves dos agregados da modificação que mudam entre execuções sem que o
# resultado mude: tempo de execução e o commit que gerou cada execução.
TIME_KEYS = {"train_seconds", "selection_seconds", "time_checks", "fit_seconds", "commits"}

# Agregados que trazem tempo ao lado das métricas: comparados sem as chaves acima.
TIME_AGGREGATES = {"e8/corrigida/summary.json", "e8/corrigida/summary-robustez.json"}

# Tabelas do relatório com coluna ou linha de tempo de treino. As demais células
# delas vêm dos agregados, que já são comparados fora do tempo.
TIME_TABLES = {"tempos_treino", "modificacao_metricas_dupla", "modificacao_pareada_dupla"}

EXACT, WITHOUT_TIME, INFORMATIVE, IGNORED = "exato", "sem tempo", "informativo", "ignorado"


def comparison_kind(relative: Path) -> str:
    """Diz como um arquivo é comparado, a partir do caminho relativo à árvore."""
    name, suffix = relative.name, relative.suffix
    if name == "run.json":
        return IGNORED
    if name.startswith("RESUMO") and suffix == ".md":
        return INFORMATIVE
    if suffix in {".tex", ".csv"} and relative.stem in TIME_TABLES:
        return INFORMATIVE
    if relative.as_posix() in TIME_AGGREGATES:
        return WITHOUT_TIME
    if suffix in {".json", ".csv", ".tex"} or name == "INDICE.md":
        return EXACT
    return IGNORED


def is_time_entry(value) -> bool:
    """Diz se o valor é uma comparação pareada cuja métrica é um tempo."""
    return isinstance(value, dict) and value.get("metric") in TIME_KEYS


def first_dict_difference(first: dict, second: dict, ignore_time: bool, path: str) -> str | None:
    """Primeira chave em que dois objetos JSON diferem, ou None."""
    for key in sorted(first.keys() | second.keys()):
        if ignore_time and key in TIME_KEYS:
            continue
        here = f"{path}.{key}" if path else key
        if key not in first or key not in second:
            return f"{here} (só existe em uma das árvores)"
        found = first_json_difference(first[key], second[key], ignore_time, here)
        if found:
            return found
    return None


def first_list_difference(first: list, second: list, ignore_time: bool, path: str) -> str | None:
    """Primeiro item em que duas listas JSON diferem, ou None."""
    if len(first) != len(second):
        return f"{path} (listas de {len(first)} e {len(second)} itens)"
    for index, (left, right) in enumerate(zip(first, second, strict=True)):
        if ignore_time and is_time_entry(left) and is_time_entry(right):
            continue
        found = first_json_difference(left, right, ignore_time, f"{path}[{index}]")
        if found:
            return found
    return None


def first_json_difference(first, second, ignore_time: bool, path: str = "") -> str | None:
    """Devolve o caminho da primeira chave em que dois JSON diferem, ou None se são iguais."""
    if isinstance(first, dict) and isinstance(second, dict):
        return first_dict_difference(first, second, ignore_time, path)
    if isinstance(first, list) and isinstance(second, list):
        return first_list_difference(first, second, ignore_time, path)
    return None if first == second else (path or "raiz")


def first_line_difference(first: bytes, second: bytes) -> str:
    """Devolve o número da primeira linha em que dois arquivos de texto diferem."""
    left, right = first.splitlines(), second.splitlines()
    for number, (a, b) in enumerate(zip(left, right, strict=False), start=1):
        if a != b:
            return f"linha {number}"
    return f"linha {min(len(left), len(right)) + 1} (um dos arquivos termina antes)"


def file_difference(reference: Path, regenerated: Path, kind: str) -> str | None:
    """Compara um arquivo das duas árvores; devolve onde diferem, ou None se são iguais."""
    first, second = reference.read_bytes(), regenerated.read_bytes()
    if kind == WITHOUT_TIME:
        return first_json_difference(json.loads(first), json.loads(second), ignore_time=True)
    if first == second:
        return None
    if reference.suffix == ".json":
        key = first_json_difference(json.loads(first), json.loads(second), ignore_time=False)
        return key or "mesmo conteúdo, formatação diferente"
    return first_line_difference(first, second)


def relative_files(root: Path) -> set[Path]:
    """Caminhos, relativos à raiz, de todos os arquivos da árvore."""
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}


def compare_trees(reference: Path, regenerated: Path) -> dict[str, list]:
    """Compara duas árvores de mesmo desenho.

    Devolve os caminhos iguais, os diferentes (com a primeira diferença) e os
    informativos que diferem, que não contam como falha.
    """
    result = {"equal": [], "different": [], "informative": []}
    for relative in sorted(relative_files(reference) | relative_files(regenerated)):
        kind = comparison_kind(relative)
        if kind == IGNORED:
            continue
        failures = result["informative"] if kind == INFORMATIVE else result["different"]
        first, second = reference / relative, regenerated / relative
        if not first.is_file() or not second.is_file():
            failures.append(
                (relative, f"só existe em {reference if first.is_file() else regenerated}")
            )
            continue
        difference = file_difference(first, second, kind)
        if difference is None:
            result["equal"].append(relative)
        else:
            failures.append((relative, difference))
    return result


def print_summary(title: str, result: dict[str, list]) -> None:
    """Imprime quantos arquivos foram comparados e onde está cada diferença."""
    exact = [path for path in result["equal"] if comparison_kind(path) != INFORMATIVE]
    different = len(result["different"])
    total = len(exact) + different
    print(f"{title}: {total} comparados, {len(exact)} iguais, {different} diferentes")
    for relative, difference in result["different"]:
        print(f"  DIFERENTE {relative.as_posix()}: {difference}")
    for relative, difference in result["informative"]:
        print(f"  cita tempo, não conta: {relative.as_posix()}: {difference}")


def main(arguments: list[str] | None = None) -> int:
    """Compara as árvores pedidas, imprime o resumo e devolve o código de saída."""
    parser = argparse.ArgumentParser(description="Compara results/ versionado e regenerado.")
    parser.add_argument("reference", type=Path, help="results/ versionado")
    parser.add_argument("regenerated", type=Path, help="results/ regenerado")
    parser.add_argument(
        "--report",
        type=Path,
        nargs=2,
        metavar=("VERSIONADO", "REGENERADO"),
        help="os dois diretórios report/, para comparar tables/ e INDICE.md",
    )
    options = parser.parse_args(arguments)
    pairs = [("results", options.reference, options.regenerated)]
    if options.report:
        pairs.append(("report", *options.report))
    different = 0
    for title, reference, regenerated in pairs:
        for directory in (reference, regenerated):
            if not directory.is_dir():
                raise ValueError(f"{directory} não é um diretório")
        result = compare_trees(reference, regenerated)
        print_summary(title, result)
        different += len(result["different"])
    print("Resultado: " + ("nenhuma diferença" if different == 0 else f"{different} diferenças"))
    return 1 if different else 0


if __name__ == "__main__":
    sys.exit(main())
