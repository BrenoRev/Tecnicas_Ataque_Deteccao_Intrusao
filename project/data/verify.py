"""Confere os arquivos de data/raw/ contra o manifesto data/manifest.json.

Recalcula o SHA-256 de cada arquivo listado. Termina com código 1 se faltar um
arquivo obrigatório ou se algum hash divergir; arquivo opcional ausente gera
só um aviso.

Uso: uv run python data/verify.py
"""

import json
import sys
from pathlib import Path

from doh_ids.config import DATA_RAW_DIR, PROJECT_ROOT
from doh_ids.data import sha256_of

MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"


def check_files(manifest: dict, raw_dir: Path) -> tuple[list[str], list[str]]:
    """Confere cada arquivo do manifesto dentro de `raw_dir`.

    Devolve duas listas de mensagens, erros e avisos. É erro o arquivo
    obrigatório ausente e qualquer arquivo presente com hash diferente do
    registrado; é aviso o arquivo opcional ausente. Toda mensagem traz o
    caminho do arquivo.
    """
    errors = []
    warnings = []
    for entry in manifest["files"]:
        path = raw_dir / entry["path"]
        if not path.is_file():
            if entry["required"]:
                errors.append(f"Arquivo obrigatório ausente: {entry['path']}")
            else:
                warnings.append(f"Arquivo opcional ausente: {entry['path']}")
            continue
        found = sha256_of(path)
        if found != entry["sha256"]:
            errors.append(
                f"SHA-256 divergente: {entry['path']} "
                f"(esperado {entry['sha256']}, encontrado {found})"
            )
    return errors, warnings


def main() -> None:
    """Confere data/raw/ contra o manifesto e encerra com erro se algo divergir."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    errors, warnings = check_files(manifest, DATA_RAW_DIR)
    for message in warnings:
        print(f"AVISO: {message}")
    for message in errors:
        print(f"ERRO: {message}", file=sys.stderr)
    if errors:
        sys.exit(1)
    present = len(manifest["files"]) - len(warnings)
    print(f"OK: {present} de {len(manifest['files'])} arquivos do manifesto conferidos.")


if __name__ == "__main__":
    main()
