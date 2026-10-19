# RAG-crosswalk — arquivo → tarefa → doc

Mapa usado pelos agentes de sincronização para saber o que revisar quando um arquivo muda. As linhas ficam válidas à medida que as tarefas são implementadas; a coluna "Existe desde" diz o que já está no repositório.

Atualizado em 07/10/2026 no commit `360c3d3` (branch `tarefa/08-stacked-rf`): tarefas 01 a 08 prontas; decisões 44 a 50 levadas às linhas.

## Código e dados

O repositório Git é a raiz (decisão 43). Caminhos relativos a `project/`, salvo os marcados com "(raiz)". No `git diff --name-only`, os de `project/` aparecem com o prefixo `project/`.

| Arquivo | Criado na tarefa | Usado nas tarefas | Docs e decisões ligados | Existe desde |
| --- | --- | --- | --- | --- |
| `pyproject.toml`, `uv.lock`, `requirements.txt` | 01; 12 (acrescenta `explainerdashboard==0.5.8`) | todas | decisões 03, 50; `MEMORY/01-discovery-stack.md`; `docs/06-padroes.md` | `5347ed3`; a dependência do painel ainda não entrou |
| `src/doh_ids/__init__.py`, `tests/test_smoke.py`, `results/.gitkeep`, `report/.gitkeep` | 01 | todas | decisão 07; `plan/PLANO-DE-TESTES.md` (T01-1) | `5347ed3` |
| `.gitignore` (raiz) e `.gitignore` de `project/` | 01 | todas | decisões 17, 43 | anterior à tarefa 01 |
| `.githooks/pre-commit`, `.githooks/commit-msg` (raiz) | 01 | todas | decisões 29, 43; `.claude/rules/commits.md` | `15ff958` |
| `.github/workflows/ci.yml`, `.github/pull_request_template.md` (raiz) | 01 | todas | decisões 29, 31, 43; `.claude/rules/testes.md`; `plan/PLANO-DE-TESTES.md` (CI); `plan/VERIFICACAO.md` (G7) | `7a41d90` |
| `README.md` (raiz) | 01 | 19 | decisão 43 | `6bf80bd` |
| `tests/conftest.py`, `tests/test_config.py` | 02 | todas | decisão 31; `plan/PLANO-DE-TESTES.md` (T02-1) | `412c097` |
| `tests/test_runlog.py` | 02 | 04–16, 21 | `plan/PLANO-DE-TESTES.md` (T02-2 a T02-6) | `b1434ab`; `dirty` em `ac360ba` |
| `tests/test_verify.py` | 03 | 13 | `plan/PLANO-DE-TESTES.md` (T03-1, T03-2) | `c2b69e0` |
| `tests/test_data.py` | 04 | 13, 21 | `plan/PLANO-DE-TESTES.md` (T04, T13, T21-1) | `407dffc` |
| `tests/test_splits.py` | 05, 07 | 09 | `plan/PLANO-DE-TESTES.md` (T05, T07) | `56db5fb`, `a4ba0e5` |
| `tests/test_evaluate.py` | 06 | 11, 14 | `plan/PLANO-DE-TESTES.md` (T06-1 a T06-9) | `21171f4` |
| `tests/test_models.py` | 08 | 09, 10, 15 | `plan/PLANO-DE-TESTES.md` (T08-1 a T08-3) | `0a94b10` |
| `tests/test_pipeline.py` | 08 | 11, 14; importa `scripts.e1_reproducao` | `plan/PLANO-DE-TESTES.md` (T08-4, T08-5) | `2732d0a`, `b00e471` |
| `tests/test_explain.py`, `tests/test_robustness.py`, `tests/test_report_assets.py` | 12, 16, 17 | — | `plan/PLANO-DE-TESTES.md` | — |
| `src/doh_ids/config.py` | 02; acrescida em 04, 05, 06, 08 | 04–17, 21 | decisões 08, 12, 15, 41, 45; `docs/04-dados.md` (colunas); `docs/02-artigo.md` (pipeline, alvos). Alvos do artigo (`FIG4A_CONFUSION`, `FIG4B_CONFUSION`, `TABLE_II`, só a metade superior) e as duas profundidades (`MAX_DEPTH`, `MAX_DEPTH_VARIABLE`) | `412c097`; última mudança em `b00e471` |
| `src/doh_ids/runlog.py` | 02 | 04–16, 17, 21 | decisões 06, 18, 38; skill `experimento`; ⚠️ REVISAR da tarefa 11 (caminho `fold<k>`) | `b1434ab`, `ac360ba` |
| `data/README.md` | 01 (tutorial de download), 03 (origem, citação, manifesto) | 13, 19 | decisões 17, 43; `docs/04-dados.md` | `6bf80bd`, tutorial em `5e11d56`, origem e cabeçalho do CIRA em `acc297a` |
| `data/manifest.json`, `data/verify.py` | 03 | 13, 19, 21 | decisões 17, 34; `docs/04-dados.md`; `docs/08-inventario-dados.md`, seção 1. O ⚠️ REVISAR das tarefas 03 e 04 foi resolvido | `c2b69e0`; `verify.py` importa `sha256_of` do pacote desde `f1eba42` |
| `src/doh_ids/data.py` | 04 | 05–16; cargas novas em 13 e 21 | decisões 08, 34, 37, 40; A1, A2; `docs/04-dados.md`. Funções: `load_cira`, `local_machine`, `feature_matrix`, `class_counts`, `clean_flows`, `sha256_of` | `407dffc`; `sha256_of` em `f1eba42` |
| `src/doh_ids/splits.py` | 05, 07; 09 acrescenta o SMOTE do treino inteiro | 08–16, 21 | decisões 12, 13, 14, 35, 41; A3, A4, A6; `docs/02-artigo.md`, seção 4. Funções: `stratified_split`, `fit_scaler`, `seen_in_train`, `balanced_subsets` | `56db5fb`, `a4ba0e5` |
| `src/doh_ids/evaluate.py` | 06; 11 e 14 acrescentam | 08–16, 21 | decisões 10, 16, 46; A11, A12; `scripts/metricas_fig4.py`. Funções: `metrics_from_confusion`, `evaluate`, `malicious_vs_rest`, `base_rate`, `compare_confusion`. Nomeia as classes por `CLASS_NAMES`: ver a tarefa 21 | `21171f4`, `fdbdeb9` |
| `src/doh_ids/models.py` | 08 | 09, 10, 11, 12, 14, 15, 16, 21 | decisões 09, 13, 15, 45; A8, A9, A10, A14. Funções: `base_forests(subsets, seed, max_depth)`, `stacked_forest` | `0a94b10`, `b00e471` |
| `src/doh_ids/explain.py` | 12 | 14 (14b), 15, 16 | decisões 19, 45, 46; A15 | — |
| script do painel (nome a confirmar; proposta `scripts/painel_xai.py`) | 12 | 19 (comando no README), 20 | decisão 50; Q6 | — |
| `src/doh_ids/robustness.py` | 16 | — | decisão 02; `docs/05-plano-experimental.md`, M3 | — |
| `jobs/*.sh` | 08 a 16, só se a execução for no Apuana | 19 | decisão 42 | — (pasta não criada) |
| `scripts/e0_dados.py` | 04, 05; complemento da 04 (Fig. 2) | 17 | `docs/05-plano-experimental.md`, E0; decisões 34, 35, 46 | `0dd87bb`, `121cde9`, `4746c22`, `f1eba42` |
| `scripts/e1_reproducao.py` | 08 | `tests/test_pipeline.py`; 10, 11, 12, 14, 15, 16 e 21 precisam de `fit_system` e `cross_validated_confusion`, que moram aqui | E1; decisões 09, 45 | `2732d0a`, `b00e471` |
| `scripts/e2_baselines.py` | 09 | 14 (14b) | E2; decisão 46 (Tabela II inteira) | — |
| `scripts/e3_sensibilidade.py` | 10 | — | E3 | — |
| `scripts/e4_corrigido.py` | 11 | 15 | E4 | — |
| `scripts/e5_xai.py` | 12 | 14 (14b) | E5; decisões 45, 46 | — |
| `scripts/e6_dados.py`, `scripts/e6_dataset2.py` (14a) e os scripts dos baselines e do SHAP no combinado (14b, nomes a confirmar) | 13, 14 | 15 | E6; decisões 11, 36, 40, 47 | — |
| `scripts/e7_ferramenta.py` | 21 | 17 | E7; decisões 20, 46, 49 (a tarefa deixou de ser condicional) | — |
| `scripts/e8_modificacao.py`, `scripts/e8_robustez.py` | 15, 16 | — | E8; decisão 02 | — |
| `scripts/make_report_assets.py` | 17 | 18, 20 | decisões 18, 45, 46, 47 | — |
| `results/e0/dados/**` | 04, 05 | 08 (confere hash e totais), 11, 12, 14, 17, 18 | decisões 18, 34, 35, 38 | `9e7563f`, `0ae2d49`, `c262b2b` |
| `results/e1/fiel/**`, `results/e1/variante/**`, `results/e1/RESUMO.md` | 08 | 09 (comparação), 10, 11, 17, 18, 23 | decisões 10, 38, 45 | `753dea0`; as duas leituras em `798ecd3` |
| `results/e2/**` a `results/e8/**` | 09–16, 21 | 17, 18 | decisões 06, 18, 38; nomes de recorte em aberto (`plan/00-README.md`, "Pendências abertas pela decisão 45") | — |
| `report/**` | 17, 18, 20 | 19 | `docs/01-requisitos.md` | — |
| `README.md` | 01, 19 | — | `docs/06-padroes.md`, seção 1; decisão 50 (comando do painel) | `6bf80bd`, `5adf3c5`, `5e11d56` |
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
| `docs/07-pendencias.md` | Perguntas e cronograma; Q1 a Q6 respondidas em 07/10/2026 | `plan/00-README.md` (bloqueios); tarefas 09, 12, 13, 14, 17, 18, 19, 21, 23; decisões 46 a 50 |
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
| A15 modelo explicado | 19, 45, 50 | 12 |
| A16 ferramenta | 20, 49 (a tarefa deixou de ser condicional) | 21 |
| A17 tempo | 22 | 08, 09 |
| A18 versões | 03 | 01 |
| Profundidade dos Random Forests base: 5 (Seção IV-B) ou variável (Algoritmo 1, linha 3); sem identificador na tabela de ambiguidades de `docs/02-artigo.md` | 45 | 08; base de 09, 11, 12, 14, 15, 16 |
