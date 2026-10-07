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

Os datasets não são versionados; ficam em um zip no drive da equipe.

1. Abra o link e baixe o arquivo zip (cerca de 1,5 GB): https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing
2. Mova o zip para a pasta `project/` do repositório.
3. Extraia ali mesmo. O zip contém a pasta `data/` inteira, então a estrutura fica no lugar sem mover nada:

       cd project
       unzip <arquivo-baixado>.zip

4. Confira que as três pastas existem:

       ls data/raw
       # cira  combinado  hkd

5. Apague o zip ou deixe-o onde está: arquivos `.zip` e as pastas de dados estão no `.gitignore` e não entram em commit.

As pastas esperadas estão descritas em [`data/README.md`](data/README.md).

## Como rodar

Lint, formatação e testes (os testes usam dados sintéticos e não precisam dos datasets):

    uv run ruff check .
    uv run ruff format --check .
    uv run pytest

Métricas recalculadas a partir das matrizes de confusão da Fig. 4 do artigo, só com a biblioteca padrão:

    python3 scripts/metricas_fig4.py

Os scripts dos experimentos e a ordem de execução serão listados aqui conforme entrarem no repositório.

Explicabilidade com SHAP sobre os Random Forests base, ao lado das Figs. 5 a 8 do artigo (precisa dos dados e dos resultados da etapa de dados e da reprodução; grava em `results/e5/`):

    uv run python scripts/e5_xai.py

Painel interativo de explicabilidade, como o da Seção VI-C do artigo (precisa dos dados):

    uv run python scripts/painel_xai.py

O script treina o sistema na memória, calcula os valores SHAP de um dos Random Forests base em uma amostra do teste e serve o painel em http://127.0.0.1:8050, só na própria máquina. O endereço responde depois de alguns minutos de treino e cálculo. Nenhum modelo é gravado nem lido do disco, e o painel não grava resultado: é material de demonstração, e os números vêm de `scripts/e5_xai.py`. Para encerrar, Ctrl+C.

## Como contribuir

1. Ative os hooks do Git uma vez por clone, na raiz do repositório:

       git config core.hooksPath .githooks

   O `pre-commit` roda o lint e a conferência de formatação; o `commit-msg` confere a mensagem.

2. Instale o ambiente como em "Instalação", com uv ou com pip.

3. Antes de cada commit, dentro de `project/`:

       uv run ruff check .
       uv run ruff format --check .
       uv run pytest

   Para corrigir: `uv run ruff check --fix .` e `uv run ruff format .`. Não use `--no-verify`.

4. Mensagem de commit: `tipo(escopo): resumo no imperativo`, em português, com até 72 caracteres na primeira linha. Tipos aceitos: `feat`, `fix`, `docs`, `exp`, `refactor`, `test`, `chore`, `ci`. Exemplo: `feat(splits): adiciona split estratificado com seed`. Sem `Co-Authored-By` e sem assinatura de ferramenta.

5. Adicione arquivos pelo nome (`git add caminho/do/arquivo`), nunca `git add -A` nem `git add .`. Dados, modelos serializados (`.pkl`, `.joblib`) e o PDF do artigo não entram em commit.

6. Uma branch por mudança, criada da `main` atualizada, e integração por pull request com o CI verde e a revisão de outro integrante. A descrição do pull request segue o modelo em `.github/pull_request_template.md`: escopo, o que demonstra, como verificar e a verificação com dados reais.

## Licença

Licença: [Preencher]
