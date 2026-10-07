# RAG-crosswalk — arquivo → tarefa → doc

Mapa usado pelos agentes de sincronização para saber o que revisar quando um arquivo muda. As linhas ficam válidas à medida que as tarefas são implementadas; a coluna "Existe desde" diz o que já está no repositório.

## Código e dados

O repositório Git é a raiz (decisão 43). Caminhos relativos a `project/`, salvo os marcados com "(raiz)". No `git diff --name-only`, os de `project/` aparecem com o prefixo `project/`.

| Arquivo | Criado na tarefa | Usado nas tarefas | Docs e decisões ligados | Existe desde |
| --- | --- | --- | --- | --- |
| `pyproject.toml`, `uv.lock`, `requirements.txt` | 01 | todas | decisão 03; `MEMORY/01-discovery-stack.md`; `docs/06-padroes.md` | `5347ed3` |
| `src/doh_ids/__init__.py`, `tests/test_smoke.py`, `results/.gitkeep`, `report/.gitkeep` | 01 | todas | decisão 07; `plan/PLANO-DE-TESTES.md` (T01-1) | `5347ed3` |
| `.gitignore` (raiz) e `.gitignore` de `project/` | 01 | todas | decisões 17, 43 | anterior à tarefa 01 |
| `.githooks/pre-commit`, `.githooks/commit-msg` (raiz) | 01 | todas | decisões 29, 43; `.claude/rules/commits.md` | `15ff958` |
| `.github/workflows/ci.yml`, `.github/pull_request_template.md` (raiz) | 01 | todas | decisões 29, 31, 43; `.claude/rules/testes.md`; `plan/PLANO-DE-TESTES.md` (CI); `plan/VERIFICACAO.md` (G7) | `7a41d90` |
| `README.md` (raiz) | 01 | 19 | decisão 43 | `6bf80bd` |
| `tests/conftest.py` e `tests/test_*.py` | 02–17 | todas | decisão 31; `plan/PLANO-DE-TESTES.md` | — |
| `src/doh_ids/config.py` | 02 | 04–16 | decisões 08, 12, 15; `docs/04-dados.md` (colunas); `docs/02-artigo.md` (pipeline, alvos) | — |
| `src/doh_ids/runlog.py` | 02 | 04–16, 17 | decisões 06, 18; skill `experimento` | — |
| `data/README.md` | 01 (tutorial de download), 03 (origem, citação, manifesto) | 13, 19 | decisões 17, 43; `docs/04-dados.md` | `6bf80bd`, tutorial em `5e11d56` |
| `data/manifest.json`, `data/verify.py` | 03 | 13, 19 | decisões 17, 34; `docs/04-dados.md`; `docs/08-inventario-dados.md`, seção 1. ⚠️ REVISAR aberto nas tarefas 03 e 04 | — |
| `src/doh_ids/data.py` | 04 | 13 | decisão 08; A1, A2; `docs/04-dados.md` | — |
| `src/doh_ids/splits.py` | 05, 07 | 08–16 | decisões 12, 13, 14; A3, A4, A6; `docs/02-artigo.md`, seção 4 | — |
| `src/doh_ids/evaluate.py` | 06 | 08–16, 21 | decisões 10, 16; A11, A12; `scripts/metricas_fig4.py` | — |
| `src/doh_ids/models.py` | 08 | 09, 10, 11, 15 | decisões 09, 13, 15; A8, A9, A10, A14 | — |
| `src/doh_ids/explain.py` | 12 | 15, 16 | decisão 19; A15 | — |
| `src/doh_ids/robustness.py` | 16 | — | decisão 02; `docs/05-plano-experimental.md`, M3 | — |
| `jobs/*.sh` | 08 a 16, só se a execução for no Apuana | 19 | decisão 42 | — (pasta não criada) |
| `scripts/e0_dados.py` | 04 | 05 | `docs/05-plano-experimental.md`, E0 | — |
| `scripts/e1_reproducao.py` | 08 | — | E1 | — |
| `scripts/e2_baselines.py` | 09 | — | E2 | — |
| `scripts/e3_sensibilidade.py` | 10 | — | E3 | — |
| `scripts/e4_corrigido.py` | 11 | 15 | E4 | — |
| `scripts/e5_xai.py` | 12 | — | E5 | — |
| `scripts/e6_dados.py`, `scripts/e6_dataset2.py` | 13, 14 | 15 | E6; decisão 11 | — |
| `scripts/e7_ferramenta.py` | 21 | — | E7; decisão 20 | — |
| `scripts/e8_modificacao.py`, `scripts/e8_robustez.py` | 15, 16 | — | E8; decisão 02 | — |
| `scripts/make_report_assets.py` | 17 | 18, 20 | decisão 18 | — |
| `results/**` | 04–16 | 17, 18 | decisões 06, 18 | — |
| `report/**` | 17, 18, 20 | 19 | `docs/01-requisitos.md` | — |
| `README.md` | 01, 19 | — | `docs/06-padroes.md`, seção 1 | `6bf80bd`, `5adf3c5`, `5e11d56` |
| `LICENSE` | pendente da equipe (previsto na 01) | 19 | "Pendentes da equipe" em `MEMORY/00-decisoes-travadas.md` | — |

## Arquivos que já existem

| Arquivo | O que é | Quem depende |
| --- | --- | --- |
| `project/scripts/metricas_fig4.py` | Recalcula métricas das matrizes da Fig. 4; roda no CI só com a biblioteca padrão | tarefa 06 (valores esperados nos testes); `docs/02-artigo.md`, seção 3 |
| `CLAUDE.md` | Regras do projeto | todas; `MEMORY/regras-projeto.md` |
| `docs/01-requisitos.md` | O que é cobrado | tarefas 17, 18, 19, 20 |
| `docs/02-artigo.md` | Especificação do sistema e ambiguidades | tarefas 04–12, 18, 21 |
| `docs/03-auditoria-repositorio.md` | Código dos autores | tarefas 02, 10 |
| `docs/04-dados.md` | Dados | tarefas 03, 04, 05, 13, 14 |
| `docs/08-inventario-dados.md` | O que foi medido nos arquivos baixados | tarefas 02–08, 11–15, 21; decisões 34–37 |
| `docs/05-plano-experimental.md` | E0 a E8 | tarefas 04–16, 21 |
| `docs/06-padroes.md` | Padrões | todas; tarefa 22 |
| `docs/07-pendencias.md` | Perguntas e cronograma | `plan/00-README.md` (bloqueios); tarefas 13, 18, 19, 21, 23 |
| `.claude/rules/*.md` | Regras de código, commit, teste e fluxo | todas; tarefa 22; `docs/06-padroes.md` (resumo) |
| `.claude/agents/implementador.md`, `.claude/skills/implementar/SKILL.md` | Quem implementa e como o ciclo corre | todas |
| `planejamento/plan/PLANO-DE-TESTES.md` | Testes por tarefa e CI | todas; `plan/VERIFICACAO.md` (G4) |
| `.claude/agents/revisor-metodologico.md` | Gate G9 de código | tarefas 04–16, 21 |
| `.claude/agents/revisor-de-texto.md` | Gate G9 de texto | tarefas 18, 19, 20 |
| `.claude/skills/experimento/SKILL.md` | Procedimento de experimento | tarefas 04, 08–16, 21 |
| `.claude/skills/checklist-entrega/SKILL.md` | Checklist final | tarefas 18, 19, 20 |

## Ambiguidade → tarefa que a resolve

| Ambiguidade | Decisão | Tarefa |
| --- | --- | --- |
| A1 limpeza | — (empírica) | 04 |
| A2 atributos | 08 | 02, 04 |
| A3 one-sided selection | 13 | 07, 10 |
| A4, A6 SMOTE | 14 | 07 |
| A5 SMOTE e folds | 15, 25 | 15 |
| A7 grade | 15, 25 | 15 |
| A8, A9, A10 empilhamento | 09 | 08, 10 |
| A11, A12 médias e AUC | 16 | 06 |
| A13 seed | 12 | 02 |
| A14 `class_weight` | 13 | 08, 10 |
| A15 modelo explicado | 19 | 12 |
| A16 ferramenta | 20 | 21 |
| A17 tempo | 22 | 08, 09 |
| A18 versões | 03 | 01 |
