# VERIFICAÇÃO — gate de "pronto" por tarefa

> **Onde fica o código (decisão 43):** o repositório Git é a raiz; o código fica em `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`) é relativo a `project/`, e os comandos `uv` rodam dentro dela. `.github/` e `.githooks/` ficam na raiz do repositório, porque o GitHub e o Git só os leem ali.

Regra: a tarefa só é "pronta" com tudo verde. Vermelho → conserta e repete. Não conseguiu → reporta com a saída do comando, sem maquiar.

## Gate universal

Executado de dentro de `project/`. A raiz do repositório fica um nível acima (decisão 43); os comandos `git` funcionam dos dois lugares.

| # | Verificação | Esperado |
| --- | --- | --- |
| G1 | Ambiente sincronizado | sem alterações no `uv.lock` |
| G2 | Lint | 0 erros |
| G3 | Formatação | nenhum arquivo a reformatar |
| G4 | Testes | suíte inteira verde, sem regressão; os testes da tarefa em [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md) existem; no pull request, CI verde |
| G5 | Script da tarefa | termina com código 0 e grava em `results/`; roda com a árvore limpa e o código já commitado, e o `run.json` versionado tem `dirty: false` (ordem: commit do código, execução, commit `exp` do resultado) |
| G6 | Determinismo | duas execuções seguidas produzem o mesmo `metrics.json` |
| G7 | Higiene | nenhum caminho absoluto de máquina; nenhuma referência a documento interno, tarefa, decisão ou identificador de ambiguidade no código, no README ou em `results/` |
| G8 | Critérios da tarefa | diff relido contra "Critério de aceite", item a item |
| G9 | Revisão automática | agente `revisor-metodologico` (código e experimento) ou `revisor-de-texto` (texto): nenhum achado bloqueante em aberto |
| G10 | Revisão humana | pull request lido e aprovado por outro integrante. **Não se aplica desde 08/10/2026 (decisão 55f):** a versão final foi para a `main` por avanço direto; a leitura do relatório pelos integrantes continua de pessoa |

Comandos:

```bash
uv sync --locked                                   # G1
uv run ruff check .                                # G2
uv run ruff format --check .                       # G3
uv run pytest                                      # G4
uv run python scripts/<script>.py                  # G5, script que não importa outro script
uv run python -m scripts.<script>                  # G5, script que importa outro script (lista abaixo)
uv run python -m scripts.<exp>_resumo              # resumo e agregado, onde o treino não os escreve
# G6: a segunda execução grava fora de results/ e é comparada com o versionado
# (.claude/rules/experimentos.md, regra 6); para tudo de uma vez, a execução limpa:
bash scripts/execucao_limpa.sh <diretório de logs>
uv run python scripts/comparar_resultados.py <results versionado> <results regenerado> --report <report versionado> <report regenerado>
# G7: nenhum dos dois pode devolver linha
grep -rnE "/Users/|/home/|[A-Z]:\\\\" --include="*.py" src scripts tests data
grep -rnE "docs/|planejamento/|\.claude/|[Dd]ecis[ãa]o [0-9]|[Tt]arefa [0-9]|\b[AQ][0-9]{1,2}\b" --include="*.py" --include="*.md" --include="*.json" src scripts tests data README.md results
```

Para G6 funcionar, `metrics.json` não contém nada que varie entre execuções: tempos de treino, data e hora ficam no `run.json`. Também por causa do G6, todo Random Forest prediz com `n_jobs=1` depois de ajustado (`base_forests`, em `models.py`): em paralelo, a soma das probabilidades das árvores depende da ordem das threads e difere na última casa. Modelo novo com `predict_proba` em paralelo segue o mesmo cuidado.

**Comando real do G5 em cada tarefa (conferido nas docstrings e nas importações em `759ec29`).** Pelo caminho do arquivo: `e0_dados.py` (04, 05), `e1_reproducao.py` (08), `e2_baselines.py` (09), `e3_sensibilidade.py` (10), `e4_corrigido.py` (11), `e5_xai.py` (12), `e6_dados.py` (13), `e6_dataset2.py` (14a), `e7_ferramenta.py` (21), `make_report_assets.py` (17). Como módulo, porque importam outros scripts: `scripts.e6_baselines_xai` (14b), `scripts.e8_modificacao` (15), `scripts.e8_robustez` (16) e os seis de resumo, `scripts.e3_resumo`, `scripts.e4_resumo`, `scripts.e6_resumo`, `scripts.e7_resumo`, `scripts.e8_resumo` e `scripts.e8_robustez_resumo`. Os de resumo não treinam: leem os `metrics.json` e os `run.json` gravados e escrevem `RESUMO.md`, `summary*.json` e `comparacao.csv`. A ordem entre todos, com o que cada um lê, está na tarefa 19.

**G6 e os agregados.** O G6 vale para `metrics.json`. `results/e4/corrigida/summary.json` também repete entre execuções. `results/e8/corrigida/summary.json` e `summary-robustez.json` guardam tempos de treino (`train_seconds`, `selection_seconds`, `time_checks`, `fit_seconds`) e não repetem: comparam-se sem essas chaves.

**G5 em execução longa.** `scripts.e8_modificacao` e `scripts.e8_robustez` pulam a execução já gravada pelo commit atual com a árvore limpa. Um commit novo entre duas partes da execução, mesmo de documentação, faz tudo ser refeito.

`dirty` mede o repositório inteiro, menos `project/results/`: edição não commitada em `docs/` ou em `planejamento/` também grava `dirty: true`. O plano e a documentação vão para commit antes de qualquer execução do G5.

G2 e G3 também rodam no hook `pre-commit`, em todo commit. G1 a G4 e G7 rodam no CI do GitHub, em todo pull request. Os testes de G4 usam dados sintéticos; o que depende dos datasets é o nível N2 do plano de testes e entra em G5.

G1 a G4 e G7 existem desde a tarefa 01 (commit `5e11d56`): rodaram verdes em 07/10/2026 na árvore de trabalho e em um clone descartável. No CI, cada checagem do G7 é um passo próprio, e a de arquivo proibido roda na raiz do repositório.

G5 e G6 das tarefas 03 a 16 e da 21 rodaram na própria sessão de implementação, nesta máquina (decisão 44); o cluster Apuana não se aplica, porque não foi usado. A comparação do G6 é entre duas execuções na mesma máquina, no mesmo commit. Script que grava mais de um recorte (o de E1 grava as duas leituras de profundidade) tem o G6 conferido em cada `metrics.json`. Resultado gerado em máquinas diferentes pode divergir em casas decimais (versão de BLAS, número de threads); por isso os resultados versionados e a execução limpa da tarefa 19 saem do mesmo ambiente.

## Quais itens valem por tipo de tarefa

O rodapé de cada tarefa repete a linha correspondente desta tabela.

| Tipo | Tarefas | Gate |
| --- | --- | --- |
| Fundação | 01, 02 | G1–G4, G7, G8, G10 |
| Biblioteca (função e teste, sem script novo) | 06, 07 | G1–G4, G7–G10 |
| Dados (dependem de arquivos fora do Git) | 03, 04 (e o complemento da Fig. 2), 05, 13 | G1–G5, G7–G10; G6 em 04, 05 e 13 |
| Experimento | 08 a 12, 14 (o gate vale para a 14a e para a 14b, cada uma), 15, 16, 21 (obrigatória desde a decisão 49) | G1–G10 |
| Artefatos do relatório | 17 | G1–G5, G8, G10 |
| Texto | 18, 20, 24 | G8, G9 (`revisor-de-texto`), G10; na 24, também G2, G3, G4 e G7, porque ela traz `scripts/make_slides.py`, e o gate de texto abaixo |
| Entrega | 19 | G1–G4, G7–G10 e a execução limpa abaixo |
| Organização | 22, 23 | G8, G10 |

## Gate de texto (tarefas 18, 20 e 24)

Executado de dentro de `project/`. Vale para o relatório e para a apresentação.

| # | Verificação | Comando ou procedimento | Esperado |
| --- | --- | --- | --- |
| X1 | Tabelas e figuras atualizadas | `uv run python scripts/make_report_assets.py`; `git status --short report/tables report/INDICE.md` | nenhuma diferença nos `.tex`, nos `.csv` e no índice |
| X2 | Relatório compila | `tectonic relatorio.tex`, dentro de `report/` (XeLaTeX também serve) | sem erro e sem referência indefinida; até 8 páginas (decisão 53) |
| X3 | Apresentação montada por script | `uv run --group slides python scripts/make_slides.py` | `report/apresentacao.pptx` com 12 a 14 slides e `report/roteiro.md` com soma de tempos de até 13 minutos |
| X4 | Nenhum número digitado | tabelas por `\input` de `report/tables/`; nos slides, células lidas de `report/tables/*.csv`; cada número em frase conferido contra a origem | lista número → arquivo no relato |
| X5 | Só o que os resultados sustentam | conferir o texto contra a lista "O que o relatório pode e não pode afirmar" da tarefa 24 | nenhuma frase da lista "não pode afirmar" |
| X6 | As duas leituras de profundidade lado a lado | onde a reprodução é citada | as duas aparecem, nomeadas |
| X7 | Revisão automática | agente `revisor-de-texto` nos dois documentos | nenhum achado grave em aberto |
| X8 | Páginas e slides olhados um a um | renderizar o PDF em imagem; exportar os slides | sem tabela cortada, figura ilegível ou texto fora da caixa |
| X9 | De pessoa | leitura do relatório pelos integrantes; ensaio cronometrado. Fechados por Breno em 08/10/2026: `.pptx` no Google Slides, template do Overleaf e DOI das referências | registrado em `docs/07-pendencias.md` (o registro no pull request não se aplica: decisão 55f) |

Conferido em `759ec29`, em 08/10/2026: X1 (executado em diretório temporário, tabelas, índice e `.png` idênticos aos versionados) e X2 (executado: compila em 1,5 s, sem erro e sem referência indefinida; o PDF versionado tem 8 páginas). X3 lido: 14 slides e 11 min 55 s. X4 a X8 informados pela sessão principal, sem artefato para conferir. X9 aberto.

Fechamento em `5999c1b`, em 08/10/2026: X1 a X3 repetidos na execução limpa (passos 20 a 22), com `report/tables/`, o índice e o `relatorio.tex` idênticos. X4 e X5 fechados pela revisão final (`REVISAO-FINAL.md`, V2 e V8): 115 afirmações numéricas recalculadas, as inexatas corrigidas em `3725f27` e `c74fc3f`; nenhuma frase da lista "não pode afirmar". X6 e X8 vistos no PDF, página a página, neste fechamento (os slides não foram vistos em imagem; a conferência deles é a de Breno no Google Slides). X7 fechado: achados do `revisor-de-texto` tratados. X9: restam a leitura do relatório pelos integrantes e o ensaio.

## Invariantes do domínio

Valem para toda tarefa que toca dados ou modelo. Cada um tem teste automatizado ou asserção dentro do script.

| # | Invariante | Onde é checado |
| --- | --- | --- |
| I1 | Treino e teste não compartilham nenhuma linha (por índice); a fração do teste cujo vetor de atributos também existe no treino é medida e reportada | teste de `stratified_split`; `split_counts.json` (tarefa 05) |
| I2 | O scaler é ajustado só com o treino; em validação cruzada, só com os folds de treino | teste de `fit_scaler`; scaler dentro do laço de folds (tarefa 08, T08-5; a tarefa 14 reutiliza o mesmo laço no combinado sem réplicas) e como primeiro passo do `Pipeline` (tarefa 15) |
| I3 | Nenhuma amostra sintética em validação ou teste | teste de `balanced_subsets`; asserção de contagem na avaliação |
| I4 | `SourceIP`, `DestinationIP`, `SourcePort`, `DestinationPort`, `TimeStamp` nunca chegam ao modelo | testes de `load_cira` e de `feature_matrix` (T04-1, T04-2), e os das cargas novas (T13-1, T21-1); asserção de 29 colunas antes de todo ajuste (em `fit_system`, tarefa 08) |
| I5 | O teste só é lido na avaliação final; nenhuma escolha (seed, hiperparâmetro, arquitetura, teste estatístico) é feita olhando para ele | escolhas travadas em decisão e em `config.py` antes de rodar; revisão G9 |
| I6 | Todo resultado declara a trilha, a seed, as versões, o hash dos dados e o commit | teste de `save_run` |
| I7 | Métrica agregada sempre com o nome da média | teste de `evaluate` |
| I8 | As métricas calculadas a partir da matriz da Fig. 4b são as de `scripts/metricas_fig4.py` | teste de `metrics_from_confusion` |

Valores de trilha aceitos: `fiel`, `corrigida`, `variante` e `dados` (E0 e a preparação do segundo dataset, que não treinam modelo). `variante` cobre as leituras alternativas da tarefa 10 e, desde a decisão 45, a leitura de profundidade variável dos Random Forests base (`results/e1/variante/profundidade_variavel/`). Na trilha `fiel` a profundidade máxima é 5. As duas leituras são medidas no mesmo protocolo, e nenhuma tabela as junta sem a coluna que as identifica.

## Execução limpa (tarefa 19)

Roda na sessão de implementação (decisão 44), em um clone novo, fora do repositório. Em um diretório novo, sem a pasta de trabalho por perto: `git clone` → `cd project` → `uv sync --locked` → extrair o zip da equipe dentro de `project/`, conforme o `README.md` → os 22 passos da tarefa 19, na ordem (conferência dos dados, treinos, resumos, `make_report_assets.py`, `make_slides.py` com `--group slides`, `tectonic relatorio.tex`) → comparar com o versionado: os 229 `metrics.json` e o `summary.json` de E4, byte a byte; os dois agregados de E8, fora das chaves de tempo; `report/tables/` e `report/INDICE.md`, sem diferença. Os `run.json`, os PDFs e o `.pptx` mudam e não entram na comparação. Os dois agregados de E8 são comparados também sem o campo `commits` (`47cdabe`); das 30 tabelas, as três que citam tempo de treino são só informadas. Os 22 passos estão em `scripts/execucao_limpa.sh` e a comparação em `scripts/comparar_resultados.py`. **Feita em 08/10/2026:** 7 h 30 min, no commit `e2379b7`, 260 de 260 arquivos de `results/` e 56 de 56 de `report/` (`REVISAO-FINAL.md`, "Execução limpa").

A execução limpa foi feita em 08/10/2026, antes do limite de 10/11. Os commits posteriores a `e2379b7` só acrescentaram asserções, testes e texto, e regravaram os dois `metrics.json` de SHAP com o que ela gerou; se algum script de treino mudar daqui em diante, ela é repetida nos scripts afetados.

O painel da tarefa 12 (decisão 50) não entra na comparação de `metrics.json`: não grava resultado. Nenhum modelo serializado está versionado (executado). Que o comando do README sobe o painel com os dados reais não tem registro versionado: é o único item aberto que não é de pessoa (tarefa 12, T12-7). (T12-7 fechado em 08/10/2026: painel no ar com os dados reais, HTTP 200 em `127.0.0.1:8050` após 162 s, processo encerrado e árvore limpa.)

## Situação do gate no fechamento (08/10/2026, commit `5999c1b`)

Executado neste fechamento, sem treino: `uv run ruff check .` (G2, sem erro), `uv run ruff format --check .` (G3, 74 arquivos formatados), `uv run pytest` (G4, 118 testes verdes em 44 s), `python3 scripts/metricas_fig4.py` (código 0), os dois greps do G7 e o filtro de arquivo proibido (nenhuma linha), `gh run list --branch main` (CI verde em `378f170`) e a instalação com pip em um clone descartável (118 testes verdes). Não executados: G1 (`uv sync --locked`, que o CI roda) e qualquer script de treino.

| Gate | Situação | Evidência |
| --- | --- | --- |
| G1 a G4, G7 | verdes | execução acima; CI verde na `main` em `378f170`; `REVISAO-FINAL.md`, V9: os comandos do CI verdes em clone limpo |
| G5 | fechado em todas as tarefas de dados e de experimento | 229 `run.json` com `dirty: false` e a trilha do caminho (`REVISAO-FINAL.md`, V1); os 229 regenerados na execução limpa também |
| G6 | **fechado pela execução limpa**, inclusive o de E1, que não tinha registro | 260 de 260 arquivos de `results/`; nenhum valor não determinístico nos `metrics.json` (`REVISAO-FINAL.md`, V5) |
| G8 | fechado | critério de aceite de cada tarefa conferido item a item neste fechamento, com a evidência ao lado |
| G9 | **fechado pela revisão final** | `REVISAO-FINAL.md`: nenhum achado bloqueante; cinco importantes e nove menores, todos tratados (seção "Tratamento") |
| G10 | não se aplica como escrito (decisão 55f) | a `main` avançou sem pull request por tarefa; o histórico com uma identidade foi aceito (decisão 55d) |
| Gate de texto | X1 a X8 fechados; X9 com dois itens de pessoa | parágrafo de fechamento da seção "Gate de texto" |

Aberto: o registro de que o painel sobe com os dados reais (tarefa 12, T12-7) e o que é de pessoa, listado em `00-README.md`, "O que resta". O CI do commit entregue é conferido no envio dos commits finais. (T12-7 fechado em 08/10/2026: painel no ar com os dados reais, HTTP 200 em `127.0.0.1:8050` após 162 s, processo encerrado e árvore limpa.)

### Registro anterior (08/10/2026, commit `759ec29`)

Executado nesta reconciliação, sem treino em andamento: `uv run ruff check .` (G2, sem erro), `uv run ruff format --check .` (G3, 72 arquivos formatados), `uv run pytest` (G4, 110 testes verdes em 41 s), `python3 scripts/metricas_fig4.py` (código 0), `uv run python data/verify.py` (8 de 8 arquivos), `make_report_assets` em diretório temporário e `tectonic relatorio.tex`. Não executados: G1 (`uv sync --locked`), os dois greps do G7 e qualquer script de treino.

| Tarefa | Conferido nesta reconciliação | Em aberto |
| --- | --- | --- |
| 04, complemento | G5 lido: `run.json` com `18f0024` e `dirty: false`; G6: `metrics.json` e `split_counts.json` sem mudança desde `360c3d3` (`git diff --stat`) | G10 |
| 08 | `results/e1/` sem mudança desde `360c3d3`, depois de `fit_system` ir para o pacote | **G6 sem registro de fechamento**; a execução limpa da 19 o cobre; G10 |
| 09 a 12, 14 a 16 | G4 executado; G5 lido: todos os `run.json` com `dirty: false` e a trilha do caminho | G6 sem registro versionado de segunda execução; G9 informado pela sessão principal; G10 |
| 13 | G5 e G6 lidos: no commit `38809c1` a etapa de dados foi rodada de novo e só os `run.json` mudaram | G10 |
| 21 | G5 e G6 dos dois modelos lidos: em `38809c1` só os `run.json` mudaram; o `metrics.json` da Fig. 9 mudou ali por mudança de código (`d86b0b5`) | G9 informado; G10 |
| 17 | G4 e G5 executados; saída idêntica à versionada | amostragem de três números por tabela; G10 |
| 24 | gate de texto: X1 e X2 executados, X3 lido | X4 a X8 informados; X9 e G10 |

A execução limpa da tarefa 19 fecha de uma vez o G6 que falta: é a segunda execução de todos os scripts, no mesmo ambiente.

### Registro anterior (07/10/2026, commit `360c3d3`)

| Tarefa | Conferido nesta reconciliação | Em aberto |
| --- | --- | --- |
| 06 | G4 da tarefa: `tests/test_evaluate.py` executado, verde; G7: os dois greps executados, sem linha | G10 |
| 07 | G4 da tarefa: `tests/test_splits.py` executado, verde | G10 |
| 08 | G5: `run.json` das duas leituras com o commit `b00e471` e `dirty: false` (lido); G7 executado, sem linha, inclusive em `results/e1/` | **G6 das duas leituras** (segunda execução rodando); G9 informado pela sessão principal, sem artefato para conferir; G10 |

Não executados nesta reconciliação, porque havia um treino em andamento na máquina: a suíte inteira (`tests/test_models.py` e `tests/test_pipeline.py` treinam modelo), `uv sync --locked`, o lint e qualquer script de experimento. Executados, pelo Python do ambiente do projeto e sem `uv run`: `test_evaluate.py`, `test_splits.py`, `test_config.py`, `test_data.py`, `test_runlog.py` e `test_verify.py`, 44 funções, todas verdes.
