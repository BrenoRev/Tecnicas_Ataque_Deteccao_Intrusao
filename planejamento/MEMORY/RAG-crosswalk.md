# RAG-crosswalk — arquivo → tarefa → doc

Mapa usado pelos agentes de sincronização para saber o que revisar quando um arquivo muda. As linhas ficam válidas à medida que as tarefas são implementadas; a coluna "Existe desde" diz o que já está no repositório.

Atualizado em 08/10/2026 no commit `5999c1b` (branch `tarefa/19-readme-execucao-limpa`): as 25 tarefas concluídas; decisão 55 levada às linhas; entraram os arquivos da tarefa 19 (`scripts/execucao_limpa.sh`, `scripts/comparar_resultados.py`, `tests/test_comparar_resultados.py`), `LICENSE`, `entregaveis-apresentacao/`, `.claude/rules/experimentos.md`, `docs/09-acompanhamento-professor.md` e `plan/REVISAO-FINAL.md`. Todo arquivo listado abaixo existe, salvo `jobs/`. Atualizações anteriores: 08/10/2026, `759ec29`; 07/10/2026, `360c3d3`.

## Código e dados

O repositório Git é a raiz (decisão 43). Caminhos relativos a `project/`, salvo os marcados com "(raiz)". No `git diff --name-only`, os de `project/` aparecem com o prefixo `project/`.

| Arquivo | Criado na tarefa | Usado nas tarefas | Docs e decisões ligados | Existe desde |
| --- | --- | --- | --- | --- |
| `pyproject.toml`, `uv.lock`, `requirements.txt` | 01; 12 (`explainerdashboard==0.5.8`); 24 (grupo `slides`, com `python-pptx==1.0.2`, fora do `requirements.txt`) | todas | decisões 03, 50, 53; `MEMORY/01-discovery-stack.md`; `docs/06-padroes.md` | `5347ed3`; painel em `e827c0a`; grupo `slides` em `7dd89c0` |
| `src/doh_ids/__init__.py`, `tests/test_smoke.py`, `results/.gitkeep`, `report/.gitkeep` | 01 | todas | decisão 07; `plan/PLANO-DE-TESTES.md` (T01-1) | `5347ed3` |
| `.gitignore` (raiz) e `.gitignore` de `project/` | 01 | todas | decisões 17, 43 | anterior à tarefa 01 |
| `.githooks/pre-commit`, `.githooks/commit-msg` (raiz) | 01 | todas | decisões 29, 43; `.claude/rules/commits.md` | `15ff958` |
| `.github/workflows/ci.yml`, `.github/pull_request_template.md` (raiz) | 01 | todas | decisões 29, 31, 43; `.claude/rules/testes.md`; `plan/PLANO-DE-TESTES.md` (CI); `plan/VERIFICACAO.md` (G7) | `7a41d90` |
| `README.md` (raiz) | 01; 19 (página de apresentação do projeto) | 19, 25 (achado I3 da revisão final: três afirmações ajustadas) | decisões 43, 55; `plan/REVISAO-FINAL.md` | `6bf80bd`; `b6bcbcc`, `7813020`, `3da178e`, `3e42795` |
| `tests/conftest.py`, `tests/test_config.py` | 02 | todas | decisão 31; `plan/PLANO-DE-TESTES.md` (T02-1) | `412c097` |
| `tests/test_runlog.py` | 02 | 04–16, 21 | `plan/PLANO-DE-TESTES.md` (T02-2 a T02-6) | `b1434ab`; `dirty` em `ac360ba` |
| `tests/test_verify.py` | 03 | 13 | `plan/PLANO-DE-TESTES.md` (T03-1, T03-2) | `c2b69e0` |
| `tests/test_data.py` | 04; 13 e 21 acrescentam | — | `plan/PLANO-DE-TESTES.md` (T04, T13, T13-8, T21-1); importa `scripts.e6_dados` | `407dffc`; `89e3914`; `6624612`; `80111aa` |
| `tests/test_splits.py` | 05, 07; 11 e 21 acrescentam | importa `scripts.e4_corrigido` e `scripts.e7_ferramenta` | `plan/PLANO-DE-TESTES.md` (T05, T07, T11-11, T21-5) | `56db5fb`, `a4ba0e5`; `b133df1` |
| `tests/test_evaluate.py` | 06; 11, 14 e 21 acrescentam | importa `scripts.e4_corrigido` e `scripts.metricas_fig4` | `plan/PLANO-DE-TESTES.md` (T06-1 a T06-9, T11-2 a T11-4, T11-7, T11-8, T14-1 a T14-3, T21-4) | `21171f4`; `e858fc3`, `679ed89`, `db56052`, `f9f9b26` |
| `tests/test_models.py` | 08; 09, 10 e 15 acrescentam | importa `scripts.e3_sensibilidade` e `scripts.e8_modificacao` | `plan/PLANO-DE-TESTES.md` (T08-1 a T08-3, T09-1 a T09-3, T10-1 a T10-3, T10-5, T15-1 a T15-4, T15-7, T15-8) | `0a94b10`; `4277e33`, `ceb6ea0`, `7902322`; `2be47e9` |
| `tests/test_pipeline.py` | 08; 11 e 14 acrescentam | importa `scripts.e1_reproducao`, `scripts.e2_baselines`, `scripts.e4_corrigido`, `scripts.e4_resumo` e `scripts.e6_dataset2` | `plan/PLANO-DE-TESTES.md` (T08-4, T08-5, T08-10, T09-7, T11-1, T11-9, T11-10, T14-4) | `2732d0a`, `b00e471`; `472bb79`, `887774c`, `8cf9dc5`; `bf19a11` |
| `tests/test_explain.py` | 12 | importa `scripts.painel_xai` | `plan/PLANO-DE-TESTES.md` (T12-1 a T12-4, T12-8, T12-9) | `f5cdf50`; `b4f1256`, `e4544af` |
| `tests/test_robustness.py` | 16 | importa `scripts.e4_corrigido` e `scripts.e8_robustez` | `plan/PLANO-DE-TESTES.md` (T16-1 a T16-3, T16-5) | `5be854b`; `5fed0ac` |
| `tests/test_report_assets.py` | 17 | importa `scripts.make_report_assets` | `plan/PLANO-DE-TESTES.md` (T17-1 a T17-4) | `ef6ffce`; comentário sobre a fixture em `2622ea3` (achado M6) |
| `tests/test_comparar_resultados.py` | 19 | importa `scripts.comparar_resultados` | `plan/PLANO-DE-TESTES.md` (T19-6) | `53f1ca4` |
| `src/doh_ids/config.py` | 02; acrescida em 04, 05, 06, 08, 09, 11, 12, 13, 15, 16 | todas as de código | decisões 08, 12, 15, 41, 45, 46, 51, 52, 54; `docs/04-dados.md` (colunas); `docs/02-artigo.md` (pipeline, alvos). Alvos do artigo (`FIG4A_CONFUSION`, `FIG4B_CONFUSION`, `TABLE_II`, `TABLE_II_LITERATURE`); as duas profundidades; `SHAP_SAMPLE_PER_CLASS`, `DASHBOARD_*`; `TOOL_ORIGIN`, `README_TOOL_ROWS`; `CORRIGIDA_MODELS`, `HYPOTHETICAL_PREVALENCES`, `GROUP_FOLDS`; `MODIFIED_GRID`, `MODIFIED_SELECTION_FRACTION`, `MODIFIED_RUNS`; `ROBUSTNESS_MODELS`, `FRAGMENTATION_FACTORS` | `412c097`; última mudança de configuração de experimento em `2a5fce5` |
| `src/doh_ids/runlog.py` | 02 | 04–16, 17, 21 | decisões 06, 18, 38, 51a, 52 (a dobra entra no nome do recorte; o layout não mudou) | `b1434ab`, `ac360ba`; versões de scipy, matplotlib e do painel em `8f1d864` |
| `data/README.md` | 01 (tutorial de download), 03 (origem, citação, manifesto) | 13, 19 | decisões 17, 43; `docs/04-dados.md` | `6bf80bd`, tutorial em `5e11d56`, origem e cabeçalho do CIRA em `acc297a` |
| `data/manifest.json`, `data/verify.py` | 03; 13 acrescenta o HKD e o combinado | 13, 19, 21 (`e7_ferramenta.py` lê o manifesto) | decisões 17, 34; `docs/04-dados.md`; `docs/08-inventario-dados.md`, seção 1 | `c2b69e0`; `f1eba42`; `c12f66f`. Executado em `759ec29`: 8 de 8 arquivos |
| `src/doh_ids/data.py` | 04; 13 e 21 acrescentam | 05–16, 21 | decisões 08, 34, 37, 40, 49; A1, A2; `docs/04-dados.md`. Funções: `load_cira`, `local_machine`, `feature_matrix`, `class_counts`, `clean_flows`, `sha256_of`; da 13, `load_hkd`, `load_combined`, `without_replicas`, `column_differences`, `read_header`, `read_flow_csv`; da 21, `load_malicious_by_tool` | `407dffc`; `f1eba42`; `89e3914`; `6624612` |
| `src/doh_ids/splits.py` | 05, 07; 09 acrescenta | 08–16, 21 | decisões 12, 13, 14, 35, 41, 51c; A3, A4, A6; `docs/02-artigo.md`, seção 4. Funções: `stratified_split`, `fit_scaler`, `seen_in_train`, `balanced_subsets`, `balanced_train` (SMOTE do treino inteiro) | `56db5fb`, `a4ba0e5`; `4277e33` |
| `src/doh_ids/evaluate.py` | 06; 11, 14 e 21 acrescentam | 08–16, 21 | decisões 10, 16, 24, 46, 51e; A11, A12; `scripts/metricas_fig4.py`. Funções: `metrics_from_confusion`, `evaluate` (recebe os nomes das classes), `malicious_vs_rest`, `base_rate`, `compare_confusion`; da 14, `recall_by_tool`, `malicious_only_metrics`, `outside_unit_interval`; da 11, `aggregate_seeds`, `paired_comparison`, `paired_verdict` | `21171f4`, `fdbdeb9`; `e858fc3`; `679ed89`; `ed7ded1`, `f9f9b26` |
| `src/doh_ids/models.py` | 08; 09, 10 e 15 acrescentam | 09–16, 21 | decisões 09, 13, 15, 25, 45, 54; A8, A9, A10, A14. Funções: `base_forests`, `stacked_forest` (com os pontos em aberto como argumentos), `fit_baseline`, `fit_modified_forest` | `0a94b10`, `b00e471`; `4277e33`; `ceb6ea0`; `7902322` |
| `src/doh_ids/system.py` | **novo, sem tarefa própria:** saiu de `scripts/e1_reproducao.py` na preparação da 12 e da 14a (decisão 51b) | 08, 10, 11, 12, 14, 15, 16, 21 | decisões 09, 45, 51b; invariantes I2, I3 e I4. Funções: `fit_system`, `cross_validated_confusion` | `472bb79` |
| `src/doh_ids/summary.py` | **novo, sem tarefa própria:** tabela Markdown e constantes levadas dos scripts para o pacote | scripts de E2 a E8 e os de resumo; 17 | regra de código (três chamadores). Funções: `markdown_table`, `frame_markdown_table`, `one_feature_rule_text` | `32f587e` |
| `src/doh_ids/explain.py` | 12 | 14 (14b); `scripts/painel_xai.py` | decisões 19, 45, 46; A15. Funções: `stratified_sample`, `forest_shap_values`, `global_importance`, `original_units`, `rank_agreement` | `f5cdf50`; `6b8abeb` |
| `scripts/painel_xai.py` | 12 | 19 (comando no README, já presente), 20 e 24 (demonstração); `tests/test_explain.py` | decisão 50; Q6. Serve em `127.0.0.1:8050`; não grava resultado | `b4f1256`, `6b8abeb` |
| `src/doh_ids/robustness.py` | 16 | `scripts/e8_robustez.py` | decisão 02; `docs/05-plano-experimental.md`, M3. Funções: `kept_features`, `drop_features`, `fragment_malicious` | `5be854b` |
| `jobs/*.sh` | não criados; não se aplica: nada rodou no Apuana (decisão 44) | — | decisões 42, 44 | — (pasta não existe) |
| `scripts/e0_dados.py` | 04, 05; complemento da 04 (Fig. 2) | 17; todo script de treino lê `results/e0/` (hash do Parquet e total do teste) | `docs/05-plano-experimental.md`, E0; decisões 34, 35, 46 | `0dd87bb`, `121cde9`, `4746c22`, `f1eba42`; Fig. 2 em `d45251e`, `44798f9` |
| `scripts/e1_reproducao.py` | 08 | `tests/test_pipeline.py`. `fit_system` e `cross_validated_confusion` saíram daqui para `src/doh_ids/system.py` | E1; decisões 09, 45, 51b | `2732d0a`, `b00e471`; `472bb79`; asserção do scaler da avaliação em `2686b80` |
| `scripts/e2_baselines.py` | 09 | `scripts/e6_baselines_xai.py` e `scripts/e6_resumo.py` o importam; `tests/test_pipeline.py` (desde `bf19a11`); lê `results/e1/` para o resumo | E2; decisões 46, 51c | `00e50b6`; `3c4611f`, `18f0024` |
| `scripts/e3_sensibilidade.py` (treino) e `scripts/e3_resumo.py` (tabela e resumo; roda como módulo; lê `results/e1/` e `results/e4/corrigida/A/`) | 10 | `tests/test_models.py`; 17 lê `comparacao.csv` | E3; decisão 51d | `d774223`; `320a2a5`, `c64832b` |
| `scripts/e4_corrigido.py` (treino) e `scripts/e4_resumo.py` (agregado e resumo; roda como módulo) | 11 | `scripts/e8_modificacao.py`, `scripts/e8_robustez.py`, `scripts/e8_resumo.py` e `scripts/e8_robustez_resumo.py` os importam; `scripts/e3_resumo.py` lê `results/e4/`; quatro arquivos de teste | E4; decisões 23, 24, 52 | `e1fc0ab`; `8cf9dc5`, `ed7ded1`; asserção do scaler e do SMOTE do treino inteiro em `7200be7` |
| `scripts/e5_xai.py` | 12 | `scripts/e6_baselines_xai.py` e `scripts/e6_resumo.py` o importam; lê `results/e1/` e `results/e6/dados/hkd/` | E5; decisões 45, 46 | `de54fe7`; `a7b94a3`, `e9836b3` |
| `scripts/e6_dados.py` | 13 | `e5_xai.py`, `e6_dataset2.py` e `e7_ferramenta.py` leem `results/e6/dados/` | E6; decisões 11, 36, 40, 47 | `c7503f4`; `fd253d9`, `15ca118`; asserção do combinado sem réplicas em `80111aa`; `tests/test_data.py` o importa |
| `scripts/e6_dataset2.py` (14a), `scripts/e6_baselines_xai.py` (14b; roda como módulo), `scripts/e6_resumo.py` (resumos e tabela final; roda como módulo) | 14 | `scripts/e8_modificacao.py` importa o da 14a; `scripts/e8_resumo.py` lê `results/e6/variante/transferencia/`; `tests/test_pipeline.py` | E6; decisões 36, 47, 51a | `887774c`; `bf593ad`, `3e5aac5`; `883faca`; `ff039fa` |
| `scripts/e7_ferramenta.py` (treino e Fig. 9) e `scripts/e7_resumo.py` (roda como módulo) | 21 | 17; `tests/test_splits.py` | E7; decisões 20, 46, 49, 51e | `b459e2a`; `d86b0b5` |
| `scripts/e8_modificacao.py` (15) e `scripts/e8_resumo.py`; `scripts/e8_robustez.py` (16) e `scripts/e8_robustez_resumo.py`; os quatro rodam como módulo | 15, 16 | 17; `tests/test_models.py`, `tests/test_robustness.py`. `e8_robustez` lê `results/e8/corrigida/M1M2-cira/`; `e8_resumo` lê os recortes `robustez-<modelo>-todos` | E8; decisões 02, 25, 52, 54 | `3ccd1c5`, `a1fb756`, `b6ccf81`; `1529734`, `7cb7158`, `ad9a6f4` |
| `scripts/make_report_assets.py` | 17 | 24 (o relatório e os slides leem o que ele gera); `tests/test_report_assets.py` | decisões 18, 45, 46, 47 | `ef6ffce`; `81a2928`, `30a7985` |
| `scripts/make_slides.py` | 24 | 19 (execução limpa); roda com `uv run --group slides` | decisão 53; lê `geracao_latex_and_pdf/` (raiz), `report/figures/*.png` e `report/tables/*.csv` | `ae38e76`; `dc5fb1c`; fala entre três integrantes em `378f170`; `c74fc3f` |
| `scripts/execucao_limpa.sh` | 19 | roda os 22 passos do README na ordem, com um log por passo, e para no primeiro erro; chama todos os scripts de experimento, `make_report_assets.py`, `make_slides.py` e `tectonic` | decisão 44; `plan/19-entrega-readme-execucao-limpa.md`; `plan/VERIFICACAO.md` (execução limpa); `.claude/rules/experimentos.md`, regra 6 | `88c0e88` |
| `scripts/comparar_resultados.py` | 19 | compara duas árvores `results/` e, com `--report`, duas `report/`; ignora `run.json`, tempos e `commits` dos dois agregados de E8; `tests/test_comparar_resultados.py` | `plan/REVISAO-FINAL.md` (execução limpa); `plan/VERIFICACAO.md` (G6); `.claude/rules/experimentos.md`, regras 2 e 6 | `53f1ca4`; `47cdabe` |
| `results/e0/dados/**` | 04, 05; Fig. 2 no complemento da 04 | todos os scripts de treino (hash e totais), 17 | decisões 18, 34, 35, 38, 46 | `9e7563f`, `0ae2d49`, `c262b2b`; Fig. 2 em `377e331`, `39a7007` |
| `results/e1/fiel/**`, `results/e1/variante/**`, `results/e1/RESUMO.md` | 08 | 09 (comparação), 10, 11, 17, 18, 23 | decisões 10, 38, 45 | `753dea0`; as duas leituras em `798ecd3` |
| `results/e2/fiel/**` | 09 | 14b, 17 | decisões 38, 46 | `c7190e7`, `076fbe1` |
| `results/e3/variante/**` (dez recortes, `comparacao.csv`, `RESUMO.md`) | 10 | 17 | decisões 26, 38, 51d | `7b3ddaf`; `2313597` |
| `results/e4/corrigida/**` (cinco modelos, `A-fold<k>`, `summary.json`, `RESUMO.md`, `HIPOTESE.md`) | 11 | 10 (resumo), 15, 16, 17 | decisões 23, 24, 38, 52 | `5165fd3`, `2a76a84`; `38809c1` |
| `results/e5/**` | 12 | 14b, 17 | decisões 19, 45, 46 | `26b2ed6`, `a0d853a`; `38809c1` |
| `results/e6/dados/**` | 13 | 12, 14, 21, 17 | decisões 36, 40, 47 | `fa320d6`, `4253571`; `38809c1` |
| `results/e6/fiel/**`, `results/e6/variante/**`, `results/e6/RESUMO.md` | 14 | 15 (resumo), 17 | decisões 36, 38, 47, 51a | `c2cb4fc`, `bc5e510`, `b32e4f8`; `38809c1`; os dois `metrics.json` de `retreino_sem_replicas-shap` regravados em `97b2c8c` (achado I5) |
| `results/e7/**` | 21 | 17 | decisões 46, 49, 51e | `1a0e041`; `38809c1` |
| `results/e8/corrigida/**` (`<modelo>-<dados>`, `robustez-<modelo>-<colunas>`, `summary.json`, `summary-robustez.json`, dois resumos e duas hipóteses) | 15, 16 | 17 | decisões 02, 25, 38, 52, 54. Os dois agregados guardam tempos de treino | `1728539`, `713e650`; `a544624`, `df16ca5`; `2313597` |
| `report/tables/**` (30 tabelas, `.tex` e `.csv`), `report/figures/**` (13 figuras, `.pdf` e `.png`), `report/INDICE.md` | 17 | 19, 24 | decisão 18; `docs/01-requisitos.md` | `9aeda1d`; `65062da`, `b2a54de`, `16b7f39` |
| `report/relatorio.tex`, `report/relatorio.pdf`, `report/apresentacao.pptx`, `report/roteiro.md` | 24 (cumpre 18 e 20) | 19 | decisão 53; `plan/24-entrega-pdfs-finais.md`, "pode e não pode afirmar" | `2c6e3da`, `938de1c`; `17a278b`, `759ec29`; `378f170`; correções da revisão final em `3725f27` e `c74fc3f` |
| `entregaveis-apresentacao/relatorio.pdf`, `apresentacao.pptx`, `roteiro.md` (raiz) | 24 (cópia dos três entregáveis, para quem não vai rodar nada) | 19, 20; quem muda `report/` recopia | decisão 53; idênticos aos de `project/report/` em `5999c1b` (`cmp`). O `roteiro-pdf.pdf` da pasta não é rastreado | `f2aedd6` |
| `geracao_latex_and_pdf/template.tex`, `geracao_latex_and_pdf/Apresentação Padrão CIn-UFPE.pptx` (raiz) | entrada da 24 | `scripts/make_slides.py` lê o `.pptx` | decisão 53 | `e40bdc4` |
| `README.md` | 01, 12 (painel e `e5_xai.py`), 19 (completo: instalação com uv e pip, os 22 passos, execução limpa, "Do relatório ao arquivo", limitações, licença) | 17 e 24 (a tabela "Do relatório ao arquivo" segue `report/INDICE.md` e a numeração do relatório); `scripts/execucao_limpa.sh` (mesma ordem) | `docs/06-padroes.md`, seção 1; decisões 46, 50, 55c | `6bf80bd`, `5adf3c5`, `5e11d56`; `eb74170`; `7657501`, `b82a82f`, `7813020`, `3da178e` |
| `LICENSE` (raiz) | 01 (previsto), criado no fechamento da 19 | 19; `README.md`, seção "Licença" | decisão 55c: MIT, os quatro integrantes como titulares | `7813020` |

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
| `docs/07-pendencias.md` | Perguntas e cronograma; Q1 a Q6 respondidas em 07/10/2026; seção "O que resta de pessoa", a lista única que `plan/00-README.md` aponta | `plan/00-README.md` (bloqueios); tarefas 09, 12, 13, 14, 17, 18, 19, 21, 23; decisões 46 a 50 |
| `docs/09-acompanhamento-professor.md` | Página de status para os encontros de 10/11 e 17/11, com a execução limpa (novo em `ba9ddc4`; `4de9ab2`, `5999c1b`) | tarefa 23; decisão 55a; todo número vem de `project/results/` |
| `.claude/rules/*.md` | Regras de código, commit, teste, fluxo e, desde `e2e0015`, experimento (`experimentos.md`: seis regras, saída da tarefa 22) | todas; tarefa 22; `docs/06-padroes.md` (resumo) |
| `.claude/agents/implementador.md`, `.claude/skills/implementar/SKILL.md` | Quem implementa e como o ciclo corre | todas |
| `.claude/agents/gerador-entregaveis.md` | Quem gera o relatório e a apresentação (novo em `e40bdc4`) | tarefa 24; decisão 53 |
| `planejamento/plan/PLANO-DE-TESTES.md` | Testes por tarefa e CI | todas; `plan/VERIFICACAO.md` (G4) |
| `planejamento/plan/REVISAO-FINAL.md` | Resultado da tarefa 25: veredito de V1 a V9, achados, mutações, tratamento e execução limpa (novo em `3e42795`; `5999c1b`) | tarefas 08 a 21, 24 e 25 (fecha o G9 e o G6); `plan/VERIFICACAO.md`; `docs/07-pendencias.md` |
| `.claude/agents/revisor-metodologico.md` | Gate G9 de código | tarefas 04–16, 21 |
| `.claude/agents/revisor-de-texto.md` | Gate G9 de texto | tarefas 18, 19, 20, 24 |
| `.claude/skills/experimento/SKILL.md` | Procedimento de experimento | tarefas 04, 08–16, 21 |
| `.claude/skills/checklist-entrega/SKILL.md` | Checklist final | tarefas 18, 19, 20; rodar na entrega de 18/11 é de pessoa |

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
