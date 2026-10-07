# IDS explicável para ataques DNS over HTTPS: reprodução

Projeto da disciplina CIN0114, Técnicas de Ataque e Detecção de Intrusão (CIn/UFPE, 2026.2).

## Objetivo

Reproduzir o sistema de detecção de intrusão proposto em:

> T. Zebin, S. Rezvy and Y. Luo, "An Explainable AI-Based Intrusion Detection System for DNS Over HTTPS (DoH) Attacks," IEEE Trans. Inf. Forensics Security, vol. 17, pp. 2339-2349, 2022, doi: 10.1109/TIFS.2022.3183390.

O sistema é o Balanced Stacked Random Forest: três Random Forests treinados em subconjuntos balanceados do CIRA-CIC-DoHBrw-2020, combinados por um meta-classificador de regressão logística, com explicações SHAP sobre os modelos base. O projeto tem três partes:

1. reproduzir o sistema do artigo;
2. avaliar o mesmo sistema em um segundo dataset;
3. modificação proposta pela equipe (opcional).

O repositório dos autores não contém o sistema, que é reimplementado aqui a partir do texto do artigo.

## Estrutura

Este diretório (`project/`) contém o código. Os comandos abaixo rodam dentro dele.

```
├── pyproject.toml       # dependências com versão fixada
├── uv.lock              # versões resolvidas, usadas por uv sync --locked
├── requirements.txt     # exportado do uv.lock, para instalação com pip
├── data/                # instruções de download; os dados ficam fora do Git
├── src/doh_ids/         # código reutilizável
├── scripts/             # um script por experimento
├── tests/               # testes com dados sintéticos
├── results/             # métricas e figuras geradas por script
└── report/              # relatório
```

## Instalação

O projeto usa Python 3.12, com as versões das bibliotecas fixadas no `pyproject.toml` e no `uv.lock`.

Com [uv](https://docs.astral.sh/uv/):

    cd project
    uv sync --locked

Com pip, em um ambiente virtual com Python 3.12:

    cd project
    python3.12 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -e .

O `requirements.txt` é gerado por `uv export --no-emit-project --no-hashes -o requirements.txt` e não é editado à mão. Com pip, os comandos deste README rodam sem o prefixo `uv run`.

## Dados

Os datasets não são versionados. Baixe o arquivo zip do drive da equipe e extraia o conteúdo em `project/data/raw/`:

https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing

As pastas esperadas estão descritas em [`data/README.md`](data/README.md).

## Como rodar

Lint, formatação e testes (os testes usam dados sintéticos e não precisam dos datasets):

    uv run ruff check .
    uv run ruff format --check .
    uv run pytest

Métricas recalculadas a partir das matrizes de confusão da Fig. 4 do artigo, só com a biblioteca padrão:

    python3 scripts/metricas_fig4.py

Os scripts dos experimentos e a ordem de execução serão listados aqui conforme entrarem no repositório.

## Licença

Licença: [Preencher]
