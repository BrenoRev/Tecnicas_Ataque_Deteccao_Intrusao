# 01 · fundação · repositório e ambiente

**Onde:** `project/` — a pasta já existe, com `git init -b main` feito (sem commits) e os datasets em `data/raw/`. Os caminhos abaixo são relativos a ela
**Objetivo:** qualquer integrante clona, roda um comando e tem o mesmo ambiente, com lint e testes funcionando.
**Depende de:** —
**Demonstra:** repositório no GitHub com CI verde em um pull request de prova e hooks barrando commit fora do padrão. Base do entregável "link do GitHub".

## Situação em 08/10/2026: concluída; resta de pessoa a proteção da `main` e o acesso de escrita

Fechamento conferido em `5999c1b`. Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f). O CI rodou e ficou verde na `main` do GitHub (`gh run list --branch main`, executado em 08/10/2026: quatro execuções, todas `success`; a última no commit `378f170`). `LICENSE` (MIT) na raiz desde `7813020` (decisão 55c). Instalação com pip conferida em `5999c1b` (critério de aceite). O pull request de prova não se aplica (decisão 55f). Os quatro caixas vazias dentro do bloco de código do passo 4c são o conteúdo do modelo de pull request, não pendência do plano.

### Registro de 07/10/2026

Reconciliada com o commit `5e11d56` (branch `tarefa/01-prova-ci`). **Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- Commits: `5347ed3` (ambiente), `15ff958` (hooks), `7a41d90` (CI) e `6bf80bd` (README) na `main`; `5adf3c5` e `5e11d56` (README: "Como contribuir" e tutorial dos dados) na branch de prova.
- Remoto: `origin/main` está em `7a41d90`; a `main` local está um commit à frente (`6bf80bd`) e nenhum atrás. A divergência citada no bloco da decisão 43 não existe mais. A branch de prova não está no remoto.
- (Superado em 08/10/2026.) O `push` foi feito e a `main` avançou sem pull request (decisão 55f); o CI ficou verde na `main`. Resta, de pessoa: proteção da `main` e acesso de escrita dos integrantes.
- (Superado em 08/10/2026.) Licença MIT, arquivo `LICENSE` na raiz (`7813020`, decisão 55c); `project/README.md` tem a seção "Licença".

Como ficou, onde difere do texto abaixo:

| Previsto | Implementado |
| --- | --- |
| Passo 1: `show-toplevel` devolve `project/`; `git init` | Superado pela decisão 43: `show-toplevel` devolve a raiz; não houve `git init` |
| Passo 4b: checagens de higiene em um bloco `run` | Um passo do CI por checagem, porque o resultado do passo é o do último comando e um `! grep` no meio do bloco não o reprovaria |
| Passo 4b: `git ls-files` filtrado por `^data/(raw\|processed)/` e `referencias/.*\.pdf$` | Passo com `working-directory: .` e o filtro `^project/data/(raw\|processed)/`, `\.(pkl\|joblib\|pcap\|parquet\|zip)$`, `^docs/referencias/.*\.pdf$` |
| Passo 4b: versão principal das actions | `actions/checkout@v7` e `astral-sh/setup-uv@v10.2.0`, com `working-directory: project` e cache pelo `uv.lock` |
| Passo 4a: `pre-commit` roda o ruff direto | O hook faz `cd project` antes, porque o Git o roda na raiz |
| `LICENSE` | Criado na raiz em `7813020` (MIT, decisão 55c) |
| `data/README.md` como esqueleto | Já traz o tutorial de download e extração; o manifesto de hashes ficou para a tarefa 03, que o criou em `c2b69e0` (`data/manifest.json`) |
| Passo 7: só entra o que está em `project/` | Superado pela decisão 43: `docs/`, `planejamento/`, `.claude/` e `CLAUDE.md` são versionados; `README.md` curto na raiz |
| `jobs/` | Não criada; não se aplica: nada rodou no Apuana (decisão 44) |

## Dependência nova prevista (decisão 50, registrada em 07/10/2026 no commit `360c3d3`)

- O conjunto de dependências fixado por esta tarefa ganha uma: `explainerdashboard==0.5.8`, para o painel interativo. Ela **não está** no `pyproject.toml` (conferido em `360c3d3`: dez dependências, de `scikit-learn` a `scipy`); entra na tarefa 12, com `uv.lock` e `requirements.txt` regenerados no mesmo commit.
- Não verificado: se a 0.5.8 resolve junto com as versões já fixadas. Se não resolver, a tarefa 12 para e relata; nenhuma outra versão é trocada sem o usuário.
- O README ganha o comando que sobe o painel localmente; isso é da tarefa 19.

## Estrutura do repositório (decisão 43, 07/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- O repositório Git é a raiz, acima de `project/`, com remoto `origin` no GitHub (público) e três commits anteriores a esta tarefa. `git rev-parse --show-toplevel` devolve a raiz, não `project/`. Não há `git init` nem primeiro commit a fazer.
- Ficam em `project/`: `pyproject.toml`, `uv.lock`, `requirements.txt`, `src/`, `tests/`, `scripts/`, `data/`, `results/`, `report/`, `README.md`, `LICENSE`. Os comandos `uv` rodam dentro de `project/`.
- Ficam na raiz do repositório: `.github/workflows/ci.yml`, `.github/pull_request_template.md`, `.githooks/` e um `README.md` curto (o que é o repositório, integrantes, e que o código e as instruções estão em `project/README.md`).
- CI: `defaults: run: working-directory: project` no job; a action do uv e o cache apontam para `project/uv.lock`. A checagem de arquivo proibido usa `git ls-files` com os caminhos a partir da raiz (`^project/data/(raw|processed)/`, `\.(pkl|joblib|pcap|parquet|zip)$`, `\.pdf$` em `docs/referencias/`). A checagem de referência interna continua valendo só para o conteúdo de `project/`.
- Hooks: rodam a partir da raiz; o `pre-commit` faz `cd project` antes do `uv run --locked ruff`. Ativação, na raiz: `git config core.hooksPath .githooks`. Valem também para commit de documentação.
- Dados: fora do Git. `project/data/raw/` e `project/data/processed/` estão nos dois `.gitignore` (raiz e `project/`). O zip dos datasets está no drive da equipe: https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing. O link entra em `project/README.md` e em `project/data/README.md`, com a instrução de extrair em `project/data/raw/`.
- Os dois commits que versionavam os dados foram desfeitos em 07/10/2026. Estado conferido no commit `5e11d56`: `origin/main` é ancestral da `main` local (um commit atrás), sem divergência; o `push` que falta é comum, sem `--force`.
- As duas `.gitignore` estão commitadas; a da raiz ignora também `*.zip`.
- Branch de prova: `tarefa/01-prova-ci`, como no passo 7.

## Estado verificado em 07/10/2026 (anterior à decisão 43)

**Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- `project/.git` existe: branch `main`, nenhum commit, nenhum remoto, hooks padrão. A árvore tem `.gitignore` e `scripts/metricas_fig4.py` ainda não rastreados; `data/` está ignorado.
- `project/.gitignore` já foi escrito em 07/10/2026 a partir do da pasta de trabalho, sem a linha do manuscrito e com `*.parquet`; cobre `data/raw/`, `data/processed/`, `*.pkl`, `*.joblib`, `*.pcap`, `.venv/`, `.DS_Store`. Motivo da pressa: em 07/10/2026 os arquivos de `data/raw/` (cerca de 2,4 GB) apareceram adicionados ao índice do Git por engano; foram removidos do índice com `git rm -r --cached data`, sem apagar nada do disco. Conferir com `git status` que `data/` não aparece.
- `scripts/metricas_fig4.py` já está em `project/scripts/`, movido da pasta de trabalho e ajustado ao lint desta tarefa (docstrings nas duas funções, `l` → `linha`, quebra da linha longa, `ruff format`), com a saída conferida idêntica por `diff`. As matrizes continuam nas linhas 13 a 24.
- Sem `[build-system]` no `pyproject.toml`, o uv trata o projeto como virtual e não instala `doh_ids`: `import doh_ids` falha e o teste T01-1 não passa (verificado em 07/10/2026). O bloco do passo 2 é obrigatório.
- Versões resolvidas por `uv lock` em 07/10/2026 para o que o plano não fixava: matplotlib 3.11.2 e scipy 1.18.1. O scipy é usado no intervalo de confiança binomial da tarefa 06 e no teste de Wilcoxon da 11; fica declarado para o `pyproject.toml` ser o conjunto fechado.
- Itens que só uma pessoa faz, porque o agente implementador não faz `push`: criar o repositório no GitHub e ligar o remoto, dar acesso aos quatro integrantes, proteger a `main`, abrir e integrar o pull request de prova. O relato do agente lista o que ficou para a pessoa.
- Cluster, opcional (decisão 42): se a equipe for usar o Apuana, conferir nele se há Python 3.12 e uv. Se não houver uv, o caminho é ambiente virtual com `pip install -r requirements.txt` e `pip install -e .`; o README descreve os dois caminhos. Não verificado em 07/10/2026: versão do Python, partições e limites do cluster.

## Arquivos

- `.gitignore` — já existe (ver bloco); entra no primeiro commit.
- `pyproject.toml` — novo: metadados, Python 3.12, dependências fixadas, `[build-system]`, configuração do ruff e do pytest, pacote `doh_ids` em `src/`.
- `uv.lock` — novo, gerado.
- `requirements.txt` — novo, exportado do lock.
- `src/doh_ids/__init__.py` — novo, vazio.
- `tests/test_smoke.py` — novo: um teste mínimo que importa o pacote. Sem nenhum teste, o pytest termina com código 5 e o gate nunca passa.
- `data/README.md`, `results/.gitkeep`, `report/.gitkeep` — novos.
- `README.md` — novo, esqueleto (objetivo, setup, como rodar, "Como contribuir"; o resto vem na tarefa 19).
- `LICENSE` — criado na raiz do repositório em `7813020`: MIT, com os quatro integrantes como titulares (decisão 55c). A nota de que a licença não cobre o artigo, os datasets nem o material da disciplina está na seção "Licença" de `README.md`.
- `.githooks/pre-commit`, `.githooks/commit-msg` — novos: barram commit fora do lint e mensagem fora do padrão.
- `.github/workflows/ci.yml` — novo: verificação automática em `push` na `main` e em pull request.
- `.github/pull_request_template.md` — novo: modelo de descrição de pull request, para toda tarefa mostrar o que demonstra.
- `scripts/metricas_fig4.py` — já no lugar; entra no primeiro commit.

## O que fazer

1. (Superado pela decisão 43.) Conferir, na raiz: `git rev-parse --show-toplevel` devolve a raiz do repositório, acima de `project/`; `git status` não mostra nada de `project/data/`. Não há pasta a criar nem `git init` a fazer.
2. Escrever o `pyproject.toml` com `requires-python = "==3.12.*"` e as versões exatas de `planejamento/MEMORY/01-discovery-stack.md`: scikit-learn 1.9.1, imbalanced-learn 0.14.2, mlxtend 0.25.0, xgboost 3.4.1, shap 0.52.0, pandas 3.0.6, numpy 2.3.5, pyarrow 25.0.1, matplotlib 3.11.2, scipy 1.18.1; em grupo de desenvolvimento, pytest 9.1.1 e ruff 0.16.10. `explainerdashboard` 0.5.8 só entra se Q6 exigir o painel. Com o bloco de instalação do pacote:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/doh_ids"]
```

3. Rodar `uv sync` para gerar o lock e `uv export --no-emit-project --no-hashes -o requirements.txt` para gerar o `requirements.txt`. Quem usa pip instala com `pip install -r requirements.txt` e depois `pip install -e .`; isso vai para o README.
4. Configurar o ruff (lint e formatação) e o pytest no `pyproject.toml`. Configuração validada em repositório descartável em 07/10/2026, com ruff 0.16.10 e pytest 9.1.1, mais o `pythonpath` que permite aos testes importar funções de `scripts/` e de `data/` (sem `__init__.py`, como pacotes de namespace):

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP", "SIM", "C90", "ERA", "PT", "D1"]
ignore = ["D104"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D1"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"
pythonpath = ["."]
```

   `D1` exige docstring em módulo e função pública; `C90` barra função com complexidade acima de 10; `ERA` barra código comentado, inclusive comentário na forma `nome=valor` (por isso os comentários de origem dos hiperparâmetros são em prosa). São as três regras que sustentam "funções bem descritas" e "sem excesso de engenharia" sem depender de revisão.
4a. Criar os hooks em `.githooks/` e torná-los executáveis (`chmod +x`). Conteúdo validado no mesmo repositório descartável; a única mudança posterior é aceitar a primeira linha `Merge ` de um commit de merge local (conferida com `grep` em 07/10/2026):

```sh
#!/bin/sh
# .githooks/pre-commit
# Barra o commit quando o lint ou a formatação falham.
set -e
uv run --locked ruff check .
uv run --locked ruff format --check .
```

```sh
#!/bin/sh
# .githooks/commit-msg
# Confere o formato da mensagem e barra trailers de coautoria.
primeira=$(head -n 1 "$1")
if ! printf '%s\n' "$primeira" | grep -Eq '^(Merge |(feat|fix|docs|exp|refactor|test|chore|ci)(\([a-z0-9-]+\))?: .+)'; then
    echo "Mensagem fora do padrão. Use: tipo(escopo): resumo. Tipos: feat fix docs exp refactor test chore ci." >&2
    exit 1
fi
if [ "${#primeira}" -gt 72 ]; then
    echo "Primeira linha com mais de 72 caracteres." >&2
    exit 1
fi
if grep -Eiq '^co-authored-by:|generated with' "$1"; then
    echo "Commit sem trailer de coautoria nem assinatura de ferramenta." >&2
    exit 1
fi
```

   Em `dash` (Linux), `${#primeira}` conta bytes, então cada acento conta dois: deixar folga no limite. Cada integrante ativa uma vez por clone: `git config core.hooksPath .githooks`. A instrução vai para o README.
4b. Criar `.github/workflows/ci.yml` com um job só, em `ubuntu-latest`, disparado por `push` na `main` e por `pull_request`: checkout; instalação do uv pela action oficial `astral-sh/setup-uv`; depois os passos da tabela "CI" de `PLANO-DE-TESTES.md`, na ordem, em blocos `run: |`:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
python3 scripts/metricas_fig4.py
! grep -rnE "/Users/|/home/|[A-Z]:\\\\" --include="*.py" src scripts tests data
! grep -rnE "docs/|planejamento/|\.claude/|[Dd]ecis[ãa]o [0-9]|[Tt]arefa [0-9]|\b[AQ][0-9]{1,2}\b" --include="*.py" --include="*.md" --include="*.json" src scripts tests data README.md results
! git ls-files | grep -E "\.(pkl|joblib|pcap|parquet)$|^data/(raw|processed)/|referencias/.*\.pdf$"
```

   Fixar a versão principal de cada action na que estiver vigente no dia e conferir na página da action; não copiar número de versão de memória. O `--include` evita erro do `grep` enquanto ainda não há `.py` em `data/`.
4c. Criar `.github/pull_request_template.md`, em português e sem referência a arquivo interno:

```markdown
## Escopo
Uma frase: o que esta mudança entrega.

## O que demonstra
Caminho do artefato em `results/` ou `report/`, ou o comportamento novo e como vê-lo.

## Como verificar
    uv run pytest
    uv run python scripts/<script>.py

## Verificação com dados reais
Saída das asserções do script na máquina de quem tem os dados, ou "não se aplica".

## Checklist
- [ ] lint, formatação e testes verdes
- [ ] nenhum dado, modelo serializado ou PDF adicionado
- [ ] mensagens de commit no padrão, sem coautoria
- [ ] resultado em `results/` gerado por script, com `run.json` e árvore limpa
```

5. Criar as pastas da estrutura de `docs/06-padroes.md:22-31`.
6. `scripts/metricas_fig4.py` continua rodando só com a biblioteca padrão (`python3 scripts/metricas_fig4.py`).
7. Fazer os primeiros commits na `main`, no padrão de `.claude/rules/commits.md`, sem trailer de coautoria (`chore:` para o ambiente, `ci:` para o workflow e o modelo de pull request). Os arquivos entram pelo nome; `docs/`, `planejamento/`, `.claude/` e `CLAUDE.md` são versionados no mesmo repositório (decisão 43, que substitui a 32), em commits próprios. O último commit da tarefa, com a seção "Como contribuir" do README, sai em uma branch `tarefa/01-prova-ci`, para o CI rodar em um pull request de prova.
7a. No esqueleto do `README.md`, uma seção curta "Como contribuir": ativar os hooks, padrão de mensagem de commit, comandos de lint e de teste, instalação com uv e com pip, modelo de pull request. É o que o integrante sem o assistente precisa, já que as regras completas ficam fora do repositório.
8. **Pessoa:** criar o repositório no GitHub com os quatro integrantes, ligar o remoto, fazer o `push` da `main` e da branch de prova, abrir o pull request de prova, conferir o CI verde, integrar e proteger a `main` (integração só por pull request). Visibilidade conforme Q10; até a resposta, privado com acesso para o professor.

## Por quê

Reprodutibilidade é requisito da equipe (`CLAUDE.md`, regra 5) e a especificação pede link do GitHub com o código. Sem ambiente fixado, o gate das outras tarefas não existe. Decisões 03, 04 e 05.

## Evidência — verificada no baseline

- `planejamento/MEMORY/01-discovery-stack.md` — tabela de versões que instalam juntas em Python 3.12.
- `docs/06-padroes.md:37` — versões do Python e das bibliotecas, preenchidas em 07/10/2026; a fonte passa a ser o `pyproject.toml`.
- 07/10/2026 — `project/` existe com Git inicializado e sem commits; `project/.gitignore` e `project/scripts/metricas_fig4.py` prontos; sem `[build-system]` o pacote não importa; `uv lock` resolve matplotlib 3.11.2 e scipy 1.18.1.

## Risco

- Um colega em Windows ou sem uv: mitigado pelo `requirements.txt` exportado e por instruções no README.
- Versão nova de uma biblioteca quebrar a instalação daqui a semanas: mitigado pelo lock.
- `git add` por engano em `data/`: já aconteceu uma vez (ver bloco); o `.gitignore` é o primeiro arquivo e o CI barra arquivo proibido.
- (Superado pela decisão 43.) O repositório é a raiz e os documentos internos são versionados de propósito. O risco que resta é o código de `project/` citar documento interno; a checagem de referência interna do CI cobre isso.

## Critério de aceite

Conferido pelo agente `cin0114-plan-sync` em 07/10/2026, no commit `5e11d56`. "Executado" é comando rodado na reconciliação; "lido" é conferência do arquivo.

- [x] `uv sync --locked` em clone limpo instala sem erro e `uv run python -c "import doh_ids"` funciona. Executado em um clone descartável da branch de prova, na mesma máquina.
- [x] `uv run ruff check .`, `uv run ruff format --check .` e `uv run pytest` terminam com código 0 (o pytest, graças ao teste mínimo). Executado na árvore de trabalho e no clone: lint sem erro, 5 arquivos formatados, 1 teste verde.
- [x] `uv run python scripts/metricas_fig4.py` imprime as duas matrizes. Executado com `python3`, código 0.
- [x] Os hooks barram, em teste manual: mensagem fora do padrão, trailer `Co-Authored-By` e arquivo fora do lint. Executado no clone descartável com `core.hooksPath .githooks`: as três tentativas de commit foram barradas e o `HEAD` não mudou.
- [x] `git log --format=%B | grep -ci "co-authored-by"` devolve 0. Executado.
- [x] `requirements.txt` corresponde ao lock (gerado por `uv export`, não editado à mão), e a instalação com pip seguida de `pip install -e .` passa no teste mínimo. Primeira metade confirmada em `5e11d56`. **Fechado em 08/10/2026:** executado pelo `cin0114-plan-sync` em um clone descartável do commit `5999c1b`, fora do repositório, com um `venv` de Python 3.12.13 e pip 25.0.1: `pip install -r requirements.txt` e `pip install -e .` com código 0; `python -m pytest`, 118 testes verdes em 47 s. (Em uma cópia sem `.git` um teste de `test_runlog.py` falha porque não há commit a registrar; não é defeito da instalação.)
- [x] `git ls-files` não lista nada de `project/data/raw/` nem de `project/data/processed/`, nenhum zip, modelo serializado ou Parquet e nenhum PDF do artigo. (Texto ajustado à decisão 43: `docs/`, `planejamento/` e `.claude/` são versionados.) Executado com o filtro do CI: nenhuma linha.
- [x] `git rev-parse --show-toplevel` devolve a raiz do repositório, acima de `project/`. (Texto ajustado à decisão 43.) Executado.
- [x] `.github/pull_request_template.md` existe, com o conteúdo do passo 4c (lido). O pull request de prova que o usaria: não se aplica (decisão 55f: a versão final foi para a `main` por avanço direto).
- [x] Repositório remoto existe e o CI rodou e ficou verde. **Fechado em 08/10/2026:** `origin/main` em `378f170`; `gh run list --branch main` (executado) mostra quatro execuções do workflow `CI`, todas `success`, a última em `378f170`. O "pull request de prova" não se aplica (decisão 55f). Os 15 commits de `378f170` a `5999c1b` ainda não foram enviados: o CI do commit entregue é conferido no envio (item 1 de `docs/07-pendencias.md`, "O que resta de pessoa").
- [ ] **Pessoa:** os integrantes têm acesso de escrita no GitHub e a `main` está protegida, se a equipe quiser (item 8 de `docs/07-pendencias.md`, "O que resta de pessoa").
- [x] Licença decidida e `LICENSE` criado. **Fechado em 08/10/2026:** `LICENSE` na raiz, MIT, em `7813020` (lido); decisão 55c: proposta aplicada, sem escolha explícita de Breno, e a troca é de um arquivo.

## Testes

Seção "Tarefa 01" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de fundação em `VERIFICACAO.md`: G1–G4, G7, G8, G10.
