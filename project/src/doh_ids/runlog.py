"""Registro de execução: grava as métricas e os metadados de um resultado."""

import json
import os
import platform
import subprocess
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from doh_ids.config import PROJECT_ROOT, RESULTS_DIR, TRACKS

# Bibliotecas cuja versão pode mudar um resultado numérico.
LIBRARIES = [
    "scikit-learn",
    "imbalanced-learn",
    "mlxtend",
    "xgboost",
    "shap",
    "pandas",
    "numpy",
    "scipy",
    "pyarrow",
    "matplotlib",
    "explainerdashboard",
]


def _git_output(args: list[str], repo_dir: Path) -> str | None:
    """Roda um comando do Git e devolve a saída, ou None se o Git não responder."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=repo_dir, capture_output=True, text=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip()


def git_state(repo_dir: Path) -> tuple[str | None, bool]:
    """Devolve o hash do commit atual e se a árvore de trabalho está suja.

    `repo_dir` é a pasta do projeto, a que contém a pasta de resultados.
    Fora de um repositório Git devolve `(None, True)`: sem commit não há como
    regenerar o resultado, então ele é tratado como não reprodutível.
    """
    commit = _git_output(["rev-parse", "HEAD"], repo_dir)
    if commit is None:
        return None, True
    # A árvore é a do repositório inteiro, não só a da pasta do código: o commit
    # registrado só reproduz o resultado se nada do que ele versiona foi alterado.
    # A pasta de resultados fica de fora porque é saída, não entrada: um script
    # que grava várias seeds marcaria como suja toda execução depois da primeira.
    status = _git_output(
        ["status", "--porcelain", "--", ":(top)", f":(exclude){RESULTS_DIR.name}"], repo_dir
    )
    return commit, status != ""


def _write_json(path: Path, content: dict) -> None:
    """Grava um dicionário em JSON com chaves ordenadas, para o arquivo ser comparável."""
    text = json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")


def save_run(
    experiment: str,
    track: str,
    slice_name: str,
    seed: int,
    metrics: dict,
    config: dict,
    data_sha256: str,
    timings: dict,
    results_dir: Path = RESULTS_DIR,
) -> Path:
    """Grava `metrics.json` e `run.json` de uma execução e devolve o diretório.

    O diretório é `<results_dir>/<experiment>/<track>/<slice_name>/seed<seed>/`,
    em que `slice_name` é o modelo, a variante ou o cenário. `metrics.json`
    recebe só `metrics`, que deve ter apenas valores determinísticos; tempos,
    data e ambiente vão para o `run.json`, para que duas execuções possam ser
    comparadas com `diff`.

    Levanta `ValueError` se `track` não for uma das trilhas de `config.TRACKS`.
    """
    if track not in TRACKS:
        raise ValueError(f"Trilha inválida: {track!r}. Use uma de {TRACKS}.")

    run_dir = results_dir / experiment / track / slice_name / f"seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    commit, dirty = git_state(PROJECT_ROOT)
    run = {
        "experiment": experiment,
        "track": track,
        "slice": slice_name,
        "seed": seed,
        "config": config,
        "data_sha256": data_sha256,
        "timings": timings,
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "libraries": {name: version(name) for name in LIBRARIES},
        "commit": commit,
        "dirty": dirty,
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
    }
    _write_json(run_dir / "metrics.json", metrics)
    _write_json(run_dir / "run.json", run)
    return run_dir
