# 22 · padronização · registrar os padrões que nasceram na implementação (anti-recorrência)

> **Fechada em 08/10/2026.** Decisão por padrão levantado na implementação:
>
> | Padrão | Decisão | Onde ou por quê |
> | --- | --- | --- |
> | Resumo separado do treino | REGISTRAR | `.claude/rules/experimentos.md`, regra 1; vale para experimento novo e para o que treina por minutos; os scripts antigos e rápidos não são reescritos |
> | Tempo fora do que se compara (agregados de E8 guardam tempo) | REGISTRAR | `.claude/rules/experimentos.md`, regra 2 |
> | Hipótese antes da execução; nome do segundo arquivo | REGISTRAR | regra 3 (já estava na decisão 38 e na skill `experimento`; a regra acrescenta o sufixo e a imutabilidade) |
> | Análise posterior marcada como tal | REGISTRAR | regra 3; depende só de disciplina |
> | Duas leituras lado a lado | REGISTRAR | regra 4 (decisões 45, 51, 52) |
> | "Pode e não pode afirmar" | REGISTRAR | regra 5 (nasceu na tarefa 24) |
> | Segunda execução em diretório temporário | REGISTRAR | regra 6 |
> | `python -m` para script que importa script | DISPENSAR | o erro de importação é claro e o README traz o comando |
> | Retomada por commit em execução longa | DISPENSAR | dois casos; exigir em todos acrescenta código sem proteger resultado |
>
> `docs/06-padroes.md` e `docs/02-artigo.md` foram atualizados pelo `cin0114-doc-sync` em `0ca5dcf`. O `CLAUDE.md` aponta para `.claude/rules/`, que já inclui o arquivo novo.


**Onde:** raiz do repositório, fora de `project/` (versionados desde a decisão 43) — `.claude/rules/`, `CLAUDE.md`, `docs/06-padroes.md`
**Objetivo:** os padrões que o plano define ficam escritos onde os próximos agentes e integrantes leem, para os erros que eles evitam não voltarem. Ou fica justificado por que não é preciso.
**Depende de:** 08, 11 (as duas prontas e executadas em `759ec29`). Não bloqueia nenhuma outra tarefa. `docs/` é editado pelo agente `cin0114-doc-sync`
**Demonstra:** regras registradas ou dispensa justificada, conferível por `grep`.

## O que fazer

1. **Analisar criticamente se a documentação é necessária.** Para cada padrão abaixo, responder: previne um erro que de fato pode recorrer? Alguém (agente ou integrante) vai ler e aplicar? Já está coberto por regra existente ou por teste automatizado?

| Padrão que o plano introduz | Já coberto por |
| --- | --- |
| Matriz de atributos montada por nome das 29 colunas, nunca "tudo menos o rótulo" | Teste do invariante I4 |
| Trilha (`fiel`, `corrigida`, `variante` ou `dados`) obrigatória em todo resultado | `runlog` recusa outra trilha (tarefa 02) |
| Teste só é lido na avaliação final | Nada automatizado; só revisão |
| Scaler e reamostragem refeitos dentro de cada fold onde há validação cruzada (tarefa 08) ou seleção de hiperparâmetros (tarefa 15) | Testes T08-5 e T15-1 |
| Escolha em ponto omisso do artigo leva comentário com decisão, motivo e seção do artigo, sem identificador interno | `.claude/rules/codigo.md` |
| Commit sem coautoria, com lint verde, uma tarefa por vez | `.claude/rules/commits.md` e `fluxo-implementacao.md`; hooks e CI (tarefa 01) |
| Formato de `shap_values` como array (amostras, atributos, classes) | Teste na tarefa 12 |
| Lista fechada de variantes antes de ver resultado | Skill `experimento` |
| Configurações, arquitetura e teste estatístico travados em `config.py` e em decisão antes de rodar | Nada automatizado; só revisão |
| Tempos e datas fora do `metrics.json` | Gate G6 falha se entrarem |
| Predição de Random Forest com `n_jobs=1` depois do ajuste, para `predict_proba` repetir entre execuções (nasceu na tarefa 08, `models.py`) | Gate G6 falha se faltar; nada o exige em modelo novo |
| Onde o artigo admite duas leituras, as duas são medidas no mesmo protocolo e reportadas lado a lado, cada uma na sua trilha (decisão 45) | Nada automatizado; só revisão |

   **Padrões que nasceram na implementação das tarefas 09 a 17, 21 e 24 (levantados em `759ec29`, 08/10/2026).** Nenhum está em `.claude/rules/` nem em decisão própria; entram na mesma análise crítica, um a um. A coluna "Onde aparece" é o que foi lido no código; a decisão de registrar ou dispensar é desta tarefa.

| Padrão que nasceu na implementação | Onde aparece | Já coberto por | Pergunta para a decisão |
| --- | --- | --- | --- |
| Resumo separado do treino: o script de treino só treina, avalia e grava `metrics.json` e `run.json`; `RESUMO.md`, `summary.json` e tabela comparativa saem de um script de resumo que não treina | `e3_resumo`, `e4_resumo`, `e6_resumo`, `e7_resumo`, `e8_resumo`, `e8_robustez_resumo` (`8cf9dc5`, `320a2a5`, `d86b0b5`, `883faca`) | Um teste só, em E4: `test_corrected_summary_is_rebuilt_from_the_saved_files_without_training` | E0, E1, E2, E5 e a etapa de dados de E6 ainda escrevem o resumo no próprio script. A regra vale só para experimento com agregação entre execuções, ou os cinco são dívida? |
| Script que importa outro script roda como módulo: `python -m scripts.<nome>` | os seis de resumo, `e6_baselines_xai`, `e8_modificacao`, `e8_robustez` (`3e5aac5`) | Nada: rodar pelo caminho do arquivo falha na importação, com erro claro | Basta o README e a docstring de cada script (já dizem o comando), ou vai para `.claude/rules/codigo.md`? |
| Hipótese escrita antes da execução, em commit anterior ao do script que roda | `HIPOTESE.md` de E4, E6 e E8 e `HIPOTESE-ROBUSTEZ.md` (`5165fd3`, `c2cb4fc`, `1728539`, `a544624`) | Decisão 38 e skill `experimento`; a ordem dos commits só se confere no `git log` | Já está registrado. O que falta decidir é o nome do segundo arquivo de hipótese na mesma trilha (`-ROBUSTEZ`), que a decisão 38 não prevê |
| Análise posterior marcada como tal: o que foi acrescentado depois de ver os números fica separado dos pares e das métricas fixados antes, e a legenda diz "(posterior)" | `posterior` em `results/e8/corrigida/summary.json`; `descriptive` em `summary-robustez.json`; tabelas `modificacao_pareada_dupla` e `robustez_seeds` (`b6ccf81`, `ad9a6f4`, `81a2928`) | Nada automatizado; só revisão | É o padrão que mais depende de disciplina e o que protege o invariante I5 no texto. Registrar onde: skill `experimento`, `revisor-metodologico`, ou os dois? |
| Duas leituras lado a lado: onde o artigo admite duas leituras, as duas são medidas no mesmo protocolo e toda tabela traz a coluna que as identifica; na trilha `corrigida`, o sufixo `-prof5` | E1, E3, E5, E6, E7; recortes `-prof5` de E3, E4 e E8; tabelas `_dupla` | Decisões 45, 51 e 52; `test_tables_with_both_depth_readings_identify_each_one` | É a última linha da tabela acima, agora com teste na ponta do relatório. Falta regra para quem escrever experimento novo? |
| "Pode e não pode afirmar": antes do texto, uma lista do que os resultados sustentam e do que não sustentam, cada item com o número e o arquivo de origem | tarefa 24, seção "O que o relatório pode e não pode afirmar" (`c715add`) | Nada: a lista vive em um arquivo de tarefa | Vira passo fixo da skill `checklist-entrega` ou do `revisor-de-texto`, ou fica como prática desta entrega? |
| Retomada por commit em execução longa: a execução já gravada pelo commit atual, com a árvore limpa, não é refeita | `already_run` em `scripts/e8_modificacao.py`, usada também por `scripts/e8_robustez.py` | Nada: a função mora em um script e não tem teste | `e4_corrigido.py` e `e1_reproducao.py`, que levam 2 horas e 56 minutos, não têm. Registrar a partir de que duração a retomada é exigida, ou dispensar por serem só dois casos? |
| Segunda execução em diretório temporário para o determinismo: a conferência do G6 grava a segunda execução fora de `results/` e compara os `metrics.json`, sem sobrescrever o versionado | as funções de execução dos scripts recebem `results_dir` (`run_experiment`, `run_baselines`, `run_group_folds`, `run_dataset`); `make_assets(results_dir, report_dir)`; `test_end_to_end_run_writes_both_files_and_repeats_identically` | O teste de ponta a ponta, só com dados sintéticos. Com dados reais, o `VERIFICACAO.md` ainda manda copiar o `metrics.json` para fora e rodar de novo no lugar | Não há registro versionado de que a segunda execução foi feita em cada experimento. Trocar o procedimento do G6 pelo diretório temporário e dizer onde a evidência fica? |

   Dois fatos do levantamento que pesam na decisão: (1) os agregados `summary.json` de E8 e `summary-robustez.json` guardam tempos de treino, e por isso não repetem entre execuções, ao contrário do `metrics.json`; a regra "tempo só no `run.json`" não diz nada sobre agregado; (2) a função de retomada compara o commit do `run.json` com o atual, então um commit de documentação entre duas partes de uma execução longa faz tudo ser refeito.

2. Para cada um, decidir **REGISTRAR** ou **DISPENSAR**. Padrão já garantido por teste ou por código que falha tende a ser dispensa: a regra escrita seria redundante. Padrão que só depende de disciplina (o do teste, o da lista fechada) tende a ser registro.
3. Se registrar: uma regra curta e imperativa, com o anti-padrão, o padrão correto e um exemplo, em `.claude/rules/<regra>.md` ou em seção do `CLAUDE.md`. Conferir antes que não duplica nem contradiz `docs/06-padroes.md` e o agente `revisor-metodologico`.
4. Atualizar `docs/06-padroes.md` e `docs/02-artigo.md` onde a implementação mudou o que estava previsto (nomes de coluna reais, leituras de ambiguidade confirmadas ou trocadas).
5. Citar a tarefa ou a decisão que originou cada regra.

## Por quê

O projeto é tocado por quatro pessoas e por agentes; padrão que vive só na cabeça de quem implementou a tarefa 08 não chega à tarefa 15. Ao mesmo tempo, regra demais ninguém lê: por isso a análise de necessidade vem antes do registro.

## Critério de aceite

- [x] Para cada padrão da tabela, a decisão está escrita: **REGISTRAR** (com o caminho da regra, conferível por `grep`) ou **DISPENSAR** (com a justificativa). **Fechado em 08/10/2026:** tabela no topo deste arquivo; `.claude/rules/experimentos.md` (`e2e0015`, ajustado em `3da178e`) tem seis regras e a seção "Dispensados, com o motivo", com os dois dispensados (lido).
- [x] Toda regra registrada tem anti-padrão, padrão correto e exemplo. **Fechado em 08/10/2026:** lido: as seis regras de `.claude/rules/experimentos.md` têm os itens "Errado", "Certo" e "Exemplo".
- [x] Nenhuma regra duplica ou contradiz `CLAUDE.md`, `docs/06-padroes.md` ou os agentes existentes. **Fechado em 08/10/2026:** lido contra o `CLAUDE.md` e as outras quatro regras de `.claude/rules/`: as regras 2 e 3 estendem o que já existia (tempo fora do `metrics.json`; hipótese antes da execução) com o caso novo, sem contradizer. `docs/06-padroes.md` não foi relido aqui: é do `cin0114-doc-sync`, que o reconciliou em `0ca5dcf` e `3da178e`.
- [x] `docs/` reflete o que foi de fato implementado. **Fechado em 08/10/2026:** reconciliado pelo `cin0114-doc-sync` em `0ca5dcf`, `3da178e` e `5999c1b` (lido no histórico), e de novo neste fechamento, em paralelo; `docs/02-artigo.md` tem a coluna "Onde no código" (lido).

## Testes

Sem teste automático. Critério de aceite conferido por outro integrante.

## Verificação ao concluir

Gate de organização: G8, G10.
