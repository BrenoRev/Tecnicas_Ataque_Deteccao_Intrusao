# 09 · reprodução · baselines do artigo (E2)

**Onde:** `src/doh_ids/models.py`, `scripts/e2_baselines.py`, `results/e2/fiel/`
**Objetivo:** a Tabela II inteira (decisão 46): os três modelos de comparação da metade superior, no mesmo split e no mesmo teste do modelo proposto, e a metade inferior, com os resultados da literatura que o artigo cita, registrada para a tabela de comparação.
**Depende de:** 05, 06, 08 (a 08 cria `models.py`; esta tarefa pode começar da branch da 08)
**Demonstra:** `results/e2/fiel/<modelo>/seed42/`: três baselines ao lado das linhas da Tabela II; a metade inferior da Tabela II em `config.py`, com a referência de cada linha. Seção 7: comparação com outros trabalhos.

## Como ficou (conferido no código e em `results/` em `759ec29`, 08/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Suíte inteira executada em `759ec29`: 110 testes verdes em 41 s; `ruff check` e `ruff format --check` sem erro.

- **Situação: pronta e executada.** Código em `4277e33` e `00e50b6`; `3c4611f` separou treino e avaliação da gravação (a função `evaluate_baselines` passou a ser usada também pela 14b); `18f0024` corrigiu o resumo. Resultados em `c7190e7`, refeitos em `076fbe1`: os três `run.json` trazem o commit `18f0024` e `dirty: false` (lido).
- **Arquivos:** `src/doh_ids/models.py` (`fit_baseline`), `src/doh_ids/splits.py` (`balanced_train`, o SMOTE do treino inteiro), `src/doh_ids/config.py` (`TABLE_II_LITERATURE`, a metade inferior), `scripts/e2_baselines.py`, `tests/test_models.py`.
- **Comando real:** `uv run python scripts/e2_baselines.py`. Lê `data/processed/cira.parquet`, `results/e0/` (hash do Parquet e total do teste) e `results/e1/` (o modelo proposto nas duas leituras, só para o resumo): roda depois de `e0_dados.py` e de `e1_reproducao.py`. Tempo medido (`timings` dos `run.json`): SMOTE 45,9 s, uma vez; ajuste 61,7 s (árvore), 38,9 s (Random Forest) e 24,2 s (XGBoost); cerca de 3 minutos no total.
- **Resultados:** `results/e2/fiel/{decision_tree,xgboost,random_forest}/seed42/` e `results/e2/fiel/RESUMO.md`. Aqui o resumo é escrito pelo próprio script; não existe `e2_resumo`.
- **Desvios que ficaram:** a seed do SMOTE do treino inteiro é `smote_seed(seed, N_SUBSETS)`, 4203 com a seed 42 (decisão 51c; lido no `run.json`). O resumo destaca a árvore de decisão muito acima da linha da Tabela II, sem ajuste (`18f0024`, `076fbe1`). O script lê `results/e1/` para o resumo, ao contrário do passo 6, que deixava a leitura para a tarefa 17: a tabela inteira aparece nos dois lugares.
- **Concluída (08/10/2026).** A conferência da metade inferior da Tabela II foi feita pelo assistente em duas passagens independentes, a pedido de Breno, e não por dois integrantes (decisão 55b; T09-6). Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- Dependências 05, 06 e 08 prontas (a 08 executada em `798ecd3`), nenhuma integrada: em execução encadeada, a branch nasce de `tarefa/08-stacked-rf`.
- **Tabela II inteira (decisão 46).** A metade inferior deixa de ser opcional. `config.py` só tem a metade superior (`TABLE_II`, chaves `decision_tree`, `xgboost`, `random_forest`, `balanced_stacked_rf`). A metade inferior tem oito linhas no manuscrito, das referências [10], [12] e [22]; várias células são "–", e a última linha está impressa em escala percentual (99.5 / 99.4 / 99.6) enquanto as outras estão entre 0 e 1. Os valores são copiados do artigo como impressos, com a referência de cada linha, e conferidos (copiados na sessão de implementação; conferidos pelo assistente em 08/10/2026, em duas passagens independentes contra a camada de texto da página 7 do manuscrito, sem divergência, e não por dois integrantes: decisão 55b). Era bloqueio para fechar a tarefa, não para começar: o código e a execução dos três baselines não dependem dela.
- **As duas leituras de profundidade (decisão 45) não mudam os baselines.** Árvore, XGBoost e Random Forest seguem a Tabela II e ficam na trilha `fiel`. O que muda é a comparação: o modelo proposto aparece ao lado deles nas duas leituras, lidas de `results/e1/fiel/` e de `results/e1/variante/` pela tarefa 17. Esta tarefa continua sem ler resultado da 08.
- Recortes: usar como `slice_name` as chaves de `TABLE_II` (`decision_tree`, `xgboost`, `random_forest`), para a linha do artigo de cada modelo ser `TABLE_II[slice_name]`.
- `table_ii_comparison(test_metrics)` existe em `scripts/e1_reproducao.py`, fixa na linha `balanced_stacked_rf`. Este script é o segundo chamador da mesma conta com outra linha; dois scripts parecidos são aceitos pela regra de código, e mexer no de E1 sai da lista de arquivos desta tarefa.
- `N_JOBS` existe. O Random Forest da Tabela II precisa do mesmo cuidado de `base_forests`: `n_jobs=1` depois do ajuste, para `predict_proba` repetir entre execuções. O determinismo do XGBoost com `n_jobs` maior que um não foi verificado: conferir no G6 antes de fechar.
- **Continua sem valor declarado:** a seed do SMOTE do treino inteiro (item do bloco abaixo). Confirmar com o usuário.
- **Custo: não medido.** O SMOTE do treino inteiro gera 2.402.484 linhas. Única referência disponível: os três Random Forests base sem limite de profundidade, cada um em cerca de 716 mil linhas, levaram 187 s juntos na tarefa 08, com a máquina carregada. Cronometrar o primeiro baseline antes de lançar os três e registrar o tempo no `run.json`.
- Execução com dados reais na própria sessão (decisão 44).

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- `splits.py` já existe, com `stratified_split`, `fit_scaler` e `seen_in_train`; o SMOTE do treino inteiro é acrescentado ali. Carga, split e normalização como na tarefa 08: `pd.read_parquet(CIRA_PARQUET_PATH)`, `stratified_split(table, SEED_FIEL)`, `fit_scaler(train)`.
- Asserção do critério de aceite, com a chave real: total da matriz igual a `split_counts.json["test"]["total"]`, 115.911.
- As contagens do risco (783.057 e 576.230 sintéticas; 2.402.484 linhas) conferem com `split_counts.json["train"]["rows"]`, 800.828 / 17.771 / 224.598.
- `save_run(..., slice_name=<modelo>, ...)`: tempo de treino em `timings`; `metrics.json` só com tipos nativos.
- `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45; não altera resultado, só o tempo.
- **Ponto sem valor declarado:** `smote_seed(seed, subset_index)` é a seed do SMOTE de cada subconjunto do modelo proposto (decisão 41). A seed do SMOTE do treino inteiro dos baselines não está em nenhuma decisão. Confirmar com o usuário; o implementador não escolhe.

## Arquivos

- `src/doh_ids/models.py` — acrescentar os construtores dos baselines.
- `src/doh_ids/splits.py` — acrescentar o SMOTE do treino inteiro (iguala as duas classes minoritárias à majoritária).
- `src/doh_ids/config.py` — profundidade 10 da árvore e 10 árvores do Random Forest, com a origem (Tabela II).
- `scripts/e2_baselines.py` — novo.
- `tests/test_models.py` — acrescentar T09-1 a T09-3.
- `results/e2/fiel/<modelo>/seed42/` e `results/e2/fiel/RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento` para E2, trilha fiel.
2. Preparar o treino dos baselines: treino normalizado completo, com SMOTE aplicado para igualar as classes minoritárias à majoritária. O artigo só diz "SMOTE balanced"; a estratégia exata é escolha nossa e leva comentário dizendo isso (ambiguidade A6, sem citar o identificador no código).
3. Árvore de decisão com profundidade máxima 10 (Tabela II); XGBoost; Random Forest com 10 árvores (Tabela II). Os demais hiperparâmetros ficam no padrão das bibliotecas, com comentário dizendo que o artigo não os informa.
4. Avaliar os três no mesmo teste da tarefa 08, com a mesma função de avaliação.
5. Gravar métricas, tempo de treino e a comparação com as três linhas correspondentes da Tabela II.
6. O resumo dos quatro modelos lado a lado (os três baselines e o proposto) é montado na tarefa 17, a partir de `results/e1/` e `results/e2/`. Aqui não se lê resultado da tarefa 08, para as duas poderem andar em paralelo.

## Por quê

P1: a Tabela II é metade dos resultados do artigo. A comparação que o artigo usa para justificar o modelo proposto é contra o Random Forest com SMOTE, por 0,0004 em F1; sem reproduzir o baseline não dá para discutir essa afirmação.

## Evidência — verificada no baseline

- `docs/02-artigo.md:58-65` — Tabela II.
- `docs/05-plano-experimental.md:57-61` — escopo de E2.
- `planejamento/MEMORY/01-discovery-stack.md` — `XGBClassifier` treina no ambiente fixado.

## Risco

- SMOTE sobre o treino inteiro cria 783.057 amostras sintéticas de Benign-DoH e 576.230 de Malicious-DoH (cada classe sobe para 800.828); o treino passa a 2.402.484 linhas. Pela medição cabe em memória e em minutos; se não couber, registrar e reduzir declaradamente.
- A linha da árvore de decisão no artigo (recall 0,7120) é muito pior que as outras. Se a nossa sair muito melhor, é indício de que os autores usaram outra configuração; reportar, não ajustar.
- Rótulos inteiros 0, 1, 2 são exigidos pelo XGBoost: já é a codificação de `config.py`.

## Critério de aceite

- [x] Três diretórios de resultado, um por baseline, com métricas e `run.json`. Lido: `results/e2/fiel/{decision_tree,xgboost,random_forest}/seed42/`, trilha `fiel` e `dirty: false` nos três.
- [x] Todos avaliados sobre o mesmo teste: o total da matriz é igual ao de `results/e0/dados/cira/seed42/split_counts.json` (asserção). Lido: a matriz de teste soma 115.911 nos três `metrics.json`, igual a `split_counts.json["test"]["total"]`.
- [x] Cada baseline tem métricas macro e ponderada nomeadas e a diferença para a sua linha da Tabela II. Lido: chaves `macro_*`, `weighted_*`, `roc_auc_ovr_macro` e `table_ii_comparison` nos três.
- [x] Hiperparâmetros não informados pelo artigo estão comentados como padrão da biblioteca. Lido: `models.py:95` e `models.py:118`; a mesma declaração em `config.readings` dos `run.json`.
- [x] Metade inferior da Tabela II em `config.py`: oito linhas copiadas do artigo como impressas, com a referência de cada uma e as células ausentes marcadas como ausentes, conferidas (decisão 46). Lido: `TABLE_II_LITERATURE` tem oito entradas, cada uma com `reference`. **Fechado em 08/10/2026:** decisão 55b: as 60 células da Tabela II, nas duas metades, conferidas pelo assistente em duas passagens independentes contra a página 7 do manuscrito, sem divergência. **Não foi por dois integrantes**, como o critério pedia; a equipe aceitou assim. `REVISAO-FINAL.md`, item 6 de "O que a revisão não verificou", registra a mesma conferência.
- [x] Revisor metodológico sem achado bloqueante. **Fechado em 08/10/2026:** `REVISAO-FINAL.md`: nenhum achado bloqueante; V3 a V6. O ponto do achado I4 que tocava E2 (`fit_scaler` do script) ganhou teste em `bf19a11`. Commits de correção anteriores: `3c4611f`, `18f0024`, `076fbe1`.

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script rodou na própria sessão de implementação, nesta máquina (decisão 44). **Não se aplica:** o Apuana e o script de submissão em `jobs/` (decisão 44: nada rodou no cluster, a pasta não existe); a saída colada no pull request (decisão 55f: não houve pull request por tarefa). A evidência é a que está versionada: resultados em `results/`, `run.json` com a máquina, os núcleos, as versões, o commit e `dirty: false`, e a execução limpa de 08/10/2026, que regenerou os mesmos `metrics.json` em um clone novo (`REVISAO-FINAL.md`, "Execução limpa"). Os dois fechamentos, "pronta" e "executada", aconteceram na mesma sessão.

## Testes

Seção "Tarefa 09" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e2_baselines.py`.
