#!/usr/bin/env bash
# Execução limpa: roda os 22 passos do README, na ordem, e para no primeiro erro.
#
# Uso, dentro de project/, com o ambiente instalado (uv sync --locked) e os
# dados extraídos em data/raw/:
#
#     bash scripts/execucao_limpa.sh <diretório de logs>
#
# A saída de cada passo vai para <diretório de logs>/passo-NN.log. O diretório
# de logs fica fora do repositório: um arquivo novo dentro dele deixaria a
# árvore suja, e o run.json de cada execução registra esse estado.
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "uso: bash scripts/execucao_limpa.sh <diretório de logs>" >&2
    exit 2
fi

mkdir -p "$1"
LOGS="$(cd "$1" && pwd)"
cd "$(dirname "$0")/.."

agora() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Roda um passo com a saída no log dele e imprime a hora de início e de fim.
passo() {
    local numero="$1"
    shift
    echo "[$(agora)] início do passo $numero: $*"
    if ! "$@" > "$LOGS/passo-$numero.log" 2>&1; then
        echo "[$(agora)] o passo $numero falhou; veja $LOGS/passo-$numero.log" >&2
        exit 1
    fi
    echo "[$(agora)] fim do passo $numero"
}

passo 01 uv run python data/verify.py
passo 02 uv run python scripts/e0_dados.py
passo 03 uv run python scripts/e6_dados.py
passo 04 uv run python scripts/e1_reproducao.py
passo 05 uv run python scripts/e2_baselines.py
passo 06 uv run python scripts/e5_xai.py
passo 07 uv run python scripts/e6_dataset2.py
passo 08 uv run python -m scripts.e6_baselines_xai
passo 09 uv run python -m scripts.e6_resumo
passo 10 uv run python scripts/e7_ferramenta.py
passo 11 uv run python -m scripts.e7_resumo
passo 12 uv run python scripts/e3_sensibilidade.py
passo 13 uv run python scripts/e4_corrigido.py
passo 14 uv run python -m scripts.e4_resumo
passo 15 uv run python -m scripts.e3_resumo
passo 16 uv run python -m scripts.e8_modificacao
passo 17 uv run python -m scripts.e8_robustez
passo 18 uv run python -m scripts.e8_resumo
passo 19 uv run python -m scripts.e8_robustez_resumo
passo 20 uv run python scripts/make_report_assets.py
passo 21 uv run --group slides python scripts/make_slides.py
cd report
passo 22 tectonic relatorio.tex

echo "[$(agora)] execução limpa concluída; logs em $LOGS"
