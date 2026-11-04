# 08 · reprodução · Balanced Stacked Random Forest (E1)

**Onde:** `src/doh_ids/models.py`, `scripts/e1_reproducao.py`, `tests/test_models.py`, `tests/test_pipeline.py`, `results/e1/fiel/proposto/seed42/`, `results/e1/variante/profundidade_variavel/seed42/`
**Objetivo:** o sistema proposto pelo artigo, treinado e avaliado como o texto descreve, com o resultado posto ao lado da Fig. 4 e da Tabela II. É a entrega central de P1.
**Depende de:** 06, 07
**Demonstra:** `results/e1/fiel/proposto/seed42/` e `results/e1/variante/profundidade_variavel/seed42/`: matriz de confusão da reprodução ao lado da Fig. 4b e da Fig. 4a, célula a célula, com a diferença, nas duas leituras de profundidade (decisão 45); `results/e1/RESUMO.md` com as duas lado a lado. Evidência central de P1 (seção 7.1).

> **Situação (07/10/2026, reconciliação no commit `360c3d3`): pronta e executada em `798ecd3`** (branch `tarefa/08-stacked-rf`, nascida de `tarefa/07-subconjuntos`; código em `f1eba42`, `0a94b10`, `2732d0a`, `fdbdeb9` e `b00e471`; resultado em `798ecd3`, que substitui o de `753dea0`, só da trilha fiel). **Concluída (08/10/2026, conferido em `5999c1b`).** O G6 foi fechado pela execução limpa: os `metrics.json` das duas leituras saíram idênticos em um clone novo (`REVISAO-FINAL.md`, "Execução limpa"). Revisão sem achado bloqueante: `REVISAO-FINAL.md`, V3 a V5; o ponto do achado I4 que tocava este script foi corrigido em `2686b80`. Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f).

## Como ficou (conferido no código e em `results/` em `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- **Duas leituras de profundidade, uma execução de cada (decisão 45).** O script roda as duas entradas de `READINGS`: trilha `fiel`, recorte `proposto`, `MAX_DEPTH = 5` (Seção IV-B); trilha `variante`, recorte `profundidade_variavel`, `MAX_DEPTH_VARIABLE = None` (linha 3 do Algoritmo 1). Dados, seed, split, subconjuntos, SMOTE e meta são os mesmos nas duas.
- `models.py`: `base_forests(subsets, seed, max_depth)`, com `max_depth` obrigatório, e `stacked_forest(forests, X_train, y_train, seed)`. Depois do ajuste, cada Random Forest fica com `n_jobs=1`: na predição em paralelo a soma das probabilidades depende da ordem das threads, e o G6 falharia na última casa. Todo modelo novo com `predict_proba` em paralelo (tarefas 09 e 15) precisa do mesmo cuidado.
- `scripts/e1_reproducao.py`: `fit_system(train, seed, max_depth)` devolve `(scaler, stacked, summary, timings)`; `cross_validated_confusion(train, seed, max_depth)` refaz o sistema em cada fold e devolve a matriz somada; `run_experiment(table, data_sha256, results_dir, reading)` grava pelo `save_run`; `table_ii_comparison(test_metrics)` compara com a linha `balanced_stacked_rf`. **Essas funções moram no script, não no pacote.** As tarefas 10, 11, 12, 14, 15, 16 e 21 também ajustam o sistema inteiro: pela regra de código, o terceiro chamador leva `fit_system` (e, para a 14 e a 21, `cross_validated_confusion`) para `src/doh_ids/models.py`. Isso toca `scripts/e1_reproducao.py` e `tests/test_pipeline.py` (o T08-5 troca `e1.fit_system` por `monkeypatch`), fora da lista de arquivos da tarefa que fizer: combinar com o usuário na primeira que precisar.
- `config.py` ganhou `CV_FOLDS`, `CV_SHUFFLE` e `N_JOBS` em `4746c22` (ainda na branch da 05), `ARTICLE_SUBSET_RATIO` e `FIEL_READINGS` em `2732d0a` e `MAX_DEPTH_VARIABLE` em `b00e471`. `sha256_of` foi para `doh_ids.data` (`f1eba42`), com `data/verify.py` e `scripts/e0_dados.py` importando de lá. As três propostas do bloco abaixo que tocavam arquivos fora da lista (`CV_FOLDS` em `config.py`, `sha256_of` no pacote, `N_JOBS`) foram feitas.
- `metrics.json`, chaves: `classes`, `train_rows`, `test_rows`, `test` (saída de `evaluate`, com as duas AUC), `cross_validation` (só da matriz; a AUC é calculada só no teste), `fig4b_comparison`, `fig4a_comparison`, `table_ii_comparison`, `subsets`, `base_models_test` (cada base sozinho no teste), `meta_decision_table` (27 combinações, com `base_labels`, `meta_label`, `train_rows_by_class`, `test_rows`), `base_disagreement_test_rows` e `base_disagreement_test_fraction`.
- `run.json`: `config` com `n_estimators`, `max_depth` (lido do modelo ajustado), `max_features`, `criterion`, `n_subsets`, `test_size`, `cv_folds`, `cv_shuffle`, `n_jobs`, `smote_seeds` e `readings` (as leituras de `FIEL_READINGS` mais `base_depth`). `data_sha256` é o do Parquet, conferido contra `parquet_sha256` de E0 antes de rodar.
- Resumos: `results/e1/fiel/RESUMO.md` e `results/e1/variante/RESUMO.md`, um por trilha como manda a decisão 38, e `results/e1/RESUMO.md`, arquivo a mais, com as duas leituras lado a lado.

Resultado com a seed 42, lido em `results/e1/` (uma execução de cada leitura; sem média nem desvio):

| Medida no teste | Artigo, Fig. 4b | fiel (profundidade 5) | variante (profundidade variável) |
| --- | --- | --- | --- |
| Soma das diferenças absolutas para a Fig. 4b | 0 | 4.711 | 553 |
| Acurácia | 99,78% | 97,79% | 99,64% |
| Recall de Benign-DoH | 90,23% | 0,00% | 92,91% |
| Precisão de Benign-DoH | 97,27% | 0,00% (classe nunca predita) | 87,13% |
| F1 macro | 97,82% | 65,80% | 96,56% |
| FPR de Malicious-DoH contra o resto | 0,0033% | 0,0649% | 0,0033% |

- Na trilha fiel o modelo não prediz Benign-DoH em nenhuma linha do teste; na validação cruzada prediz a classe em 98 linhas e acerta uma. Os três bases isolados têm recall de Benign-DoH de 85% a 86% e precisão de 28% a 30%: a perda da classe acontece no meta. É esse o motivo, dado na decisão 45, de as tarefas seguintes usarem a variante como sistema base.
- Validação cruzada ao lado da Fig. 4a: soma das diferenças absolutas 43.275 (fiel) e 5.147 (variante); as duas matrizes somam 1.043.197.
- **Custo medido** (`run.json`, chave `timings`; 10 núcleos; a máquina estava carregada na execução da variante): um ajuste do sistema inteiro leva 112 s na fiel (4,3 de subconjuntos, 103,1 de bases, 4,9 de meta) e 194 s na variante (2,0 + 187,3 + 4,3); a validação cruzada de 10 folds, 785 s na fiel e 2.270 s na variante; o script inteiro, 902 s + 2.473 s, cerca de 56 minutos. O "são minutos" do item de risco abaixo e os "25 s" da evidência estão superados por estes números.

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- (Resolvido em `4746c22`: `N_JOBS = -1`; ver o bloco acima.) **Bloqueio antes de começar: `N_JOBS` não existe em `config.py`.** O passo 5a da tarefa 02 não foi feito porque o valor é pendência da equipe ("Pendentes da equipe" de `00-decisoes-travadas.md`). Esta tarefa para nesse ponto até a equipe decidir; o implementador não escolhe o valor.
- **Folds da validação cruzada (passo 5): usar a mesma construção de E0.** `StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED_FIEL)` sobre `train` e `train["label"]`, como em `scripts/e0_dados.py:189-195`. A tabela por fold de `split_counts.json`, que vai para a seção 6 do relatório, foi gerada com essa construção; folds montados de outro jeito deixam a tabela descrevendo uma validação que não foi a rodada.
- `CV_FOLDS = 10` é constante local de `scripts/e0_dados.py:80`. Proposta, a confirmar com o usuário porque toca um arquivo fora da lista desta tarefa: subir `CV_FOLDS` para `config.py` aqui, com o script de E0 passando a importá-la, e rodar E0 de novo para mostrar que `metrics.json` e `split_counts.json` não mudam. A alternativa, repetir o número no script novo, cria duas fontes.
- Carga (passo 4): não há função que leia o Parquet. `pd.read_parquet(CIRA_PARQUET_PATH)` devolve `FEATURE_COLUMNS + ["label", "group"]` com índice de 0 a n − 1. Depois `stratified_split(table, SEED_FIEL)`, `fit_scaler(train)` e `scaler.transform(feature_matrix(...))`.
- `save_run(experiment, track, slice_name, seed, metrics, config, data_sha256, timings, results_dir=RESULTS_DIR)`. As leituras adotadas nos pontos omissos entram no dicionário `config`; os tempos dos bases e do meta, em `timings`. `hostname` e `cpu_count` são gravados sem o script pedir. O recorte aparece no `run.json` como `slice`.
- `metrics.json` recebe só o dicionário de métricas, com tipos nativos do Python. A tabela de decisão do meta e as matrizes vão como listas.
- `data_sha256`: o arquivo que este script lê é o Parquet. O hash de referência está em `results/e0/dados/cira/seed42/metrics.json`, chave `parquet_sha256`. `sha256_of` existe em `data/verify.py` e em `scripts/e0_dados.py`; este script seria o terceiro chamador, o que pela regra de código leva a função para `src/`. Isso também toca arquivos fora da lista: combinar com o usuário.
- `dirty` mede o repositório inteiro menos `project/results/`. Edição não commitada em `docs/` ou em `planejamento/` marca `dirty: true`: o plano precisa estar em commit antes de rodar.
- Asserções do passo 7, com as chaves reais: total do teste igual a `split_counts.json["test"]["total"]` (115.911); soma da matriz da validação cruzada igual a `["train"]["total"]` (1.043.197); 29 colunas conferidas em `feature_matrix(...)`.
- A fração de 13,7% do bloco abaixo é `split_counts.json["test_seen_in_train"]["fraction_total"]`.
- No teste de ponta a ponta (T08-4), `save_run` recebe `results_dir=tmp_path`.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- Total do teste: 115.911, uma amostra de Non-DoH a mais que na Fig. 4b. A soma das diferenças absolutas para a Fig. 4b tem, por isso, mínimo de 1. A matriz da validação cruzada soma 1.043.197, contra 1.043.198 da Fig. 4a.
- 13,7% do teste tem vetor idêntico no treino (17,7% do Non-DoH). O resumo do experimento declara isso ao lado das métricas da trilha fiel.

## Arquivos

- `src/doh_ids/models.py` — novo: construção dos Random Forests base e do empilhamento.
- `scripts/e1_reproducao.py` — novo.
- `tests/test_models.py` — novo.
- `tests/test_pipeline.py` — novo: teste de ponta a ponta com dados sintéticos (T08-4).
- `src/doh_ids/config.py` — acrescentar constantes novas, se houver (os nomes das leituras adotadas gravados no `run.json`).
- `results/e1/fiel/proposto/seed42/` — gerado.
- `results/e1/fiel/RESUMO.md` — interpretação dos números, uma linha por métrica principal.

## O que fazer

1. Antes de escrever, rodar a skill `experimento` para E1, trilha fiel.
2. Função dos modelos base: um `RandomForestClassifier` por subconjunto, com 10 árvores, profundidade máxima 5, `max_features` 28, critério Gini, sem `class_weight`, seed da execução.
3. Função do empilhamento: `mlxtend.classifier.StackingClassifier` com os três bases já treinados, `fit_base_estimators=False`, regressão logística como meta-classificador, `use_probas=False`. O meta é ajustado com o treino original normalizado (decisão 09).
4. Script: carregar o Parquet, split com seed 42, normalizar, construir os subconjuntos, treinar os bases, treinar o meta, avaliar no teste.
5. Avaliação de treino comparável à Fig. 4a: validação cruzada de 10 folds estratificada sobre o treino original, refazendo dentro de cada fold o scaler, os subconjuntos, o SMOTE, os bases e o meta com os nove folds de treino, e prevendo o fold deixado de fora. A legenda interna da Fig. 4a diz que os resultados foram obtidos "in a 10-fold cross-validation process", sem detalhar o procedimento; esta é a leitura em que a matriz tem só amostras reais e soma o treino original, como a figura mostra. A ambiguidade A5 (SMOTE antes ou dentro dos folds) afeta a seleção de hiperparâmetros, que a trilha fiel não refaz (decisão 15); por isso não há uma versão "com vazamento" a reproduzir aqui.
6. Gravar: matriz de confusão do teste e da validação cruzada, métricas completas, comparação célula a célula com a Fig. 4b e a 4a, comparação com a linha "Proposed model" da Tabela II, resumo dos subconjuntos. Os tempos de treino dos bases e do meta vão para o `run.json`.
   - AUC do modelo empilhado calculada das duas formas previstas na tarefa 06 (saída do meta e média das probabilidades dos bases), cada uma com seu nome.
   - Tabela de decisão do meta-classificador: para cada uma das 27 combinações de rótulos dos três bases, a classe que o meta devolve; e a fração das amostras de teste em que os bases discordam. Com `use_probas=False` a regressão logística recebe os rótulos 0, 1, 2 como número, e a codificação põe Benign-DoH entre Non-DoH e Malicious-DoH: um desacordo entre Non-DoH e Malicious-DoH pode ser resolvido como Benign-DoH (verificado em teste sintético). É o comportamento da biblioteca que o artigo cita, então fica na trilha fiel, mas precisa estar medido e declarado no relatório.
7. Asserções no script: 29 colunas antes de todo ajuste; total do teste igual ao de `split_counts.json`; nenhuma amostra sintética na avaliação.
8. Testes com dados sintéticos: o modelo empilhado tem três bases e o meta tem três entradas; as predições estão em {0, 1, 2}; mesma seed, mesmas predições.
9. Pedir revisão ao agente `revisor-metodologico`.

## Por quê

Objetivo P1 da especificação. O repositório dos autores não contém este modelo, então ele sai do texto. As decisões 09, 13, 14 e 15 fixam uma leitura para cada ponto omisso, antes de olhar para qualquer resultado.

## Evidência — verificada no baseline

- `docs/02-artigo.md:11-27` — pipeline declarado e seções de origem.
- `docs/02-artigo.md:33-49` — matrizes da Fig. 4.
- `docs/02-artigo.md:94-96` — A8, A9, A10.
- Manuscrito em `docs/referencias/`, Algoritmo 1, linha 5 ("Calculate the labels for each sample xn of the training dataset X") — apoio para treinar o meta sobre as predições no treino original.
- `planejamento/MEMORY/01-discovery-stack.md` — `fit_base_estimators=False` aceita bases pré-treinados; meta recebe 3 atributos com `use_probas=False`; Random Forest em 717 mil linhas leva cerca de 25 s.
- `docs/03-auditoria-repositorio.md`, "Artigo contra código" — o que falta no código público.

## Risco

- Resultado longe da Fig. 4b (risco R2). Não mexer em seed nem em hiperparâmetro: registrar a distância e seguir para a tarefa 10, que mede as leituras alternativas.
- A validação cruzada do passo 5 treina o sistema 10 vezes. Pela medição, são minutos; se passar disso, reduzir a paralelização dos folds, não o número de folds.
- O meta é treinado sobre predições que os bases fizeram em dados que já viram. Não envolve o teste, mas tende a deixar o meta confiante demais nos bases. Fica assim nas duas trilhas, declarado (decisões 09 e 23); a variante out-of-fold é opcional na tarefa 10.

## Critério de aceite

Conferido em 07/10/2026 no commit `360c3d3`. Nesta reconciliação não se rodou o script nem os testes que treinam modelo (`tests/test_models.py`, `tests/test_pipeline.py`), porque havia um treino em andamento na máquina; os itens abaixo foram confirmados pela leitura do código e dos arquivos versionados em `results/`, salvo onde se diz "executado".

- [x] `results/e1/fiel/proposto/seed42/metrics.json` contém as duas matrizes, métricas por classe, macro e ponderada, as duas AUC nomeadas, a tabela de decisão do meta e a fração de desacordo entre bases. Lido: chaves `test`, `cross_validation`, `roc_auc_ovr_macro`, `roc_auc_ovr_macro_base_mean`, `meta_decision_table` e `base_disagreement_test_fraction`, nas duas leituras (`fiel/proposto` e `variante/profundidade_variavel`).
- [x] O mesmo diretório contém a comparação com a Fig. 4a, a Fig. 4b e a Tabela II, com as diferenças. Lido: `fig4a_comparison`, `fig4b_comparison` e `table_ii_comparison`, nas duas leituras.
- [x] `run.json` registra trilha `fiel`, seed 42 e, por nome, as leituras adotadas nos pontos omissos (dados de treino do meta, `use_probas`, alvo e parâmetros do SMOTE, origem dos hiperparâmetros). Correspondem às decisões 09, 13, 14 e 15, mas o arquivo não cita número de decisão. Lido: `track`, `seed`, `config.readings` (onze entradas, entre elas `meta_training_data`, `meta_input`, `smote_target`, `smote_parameters`, `hyperparameter_source` e `base_depth`), `commit` `b00e471` e `dirty: false`; o da variante tem `track: variante` e `max_depth` nulo. Executado: o grep do G7 sobre `src scripts tests data README.md results` não devolve linha.
- [x] Duas execuções produzem métricas idênticas. **Fechado em 08/10/2026:** a execução limpa (clone novo, commit `e2379b7`, 22 passos) regenerou os 229 `metrics.json`; os dois de `results/e1/` saíram idênticos byte a byte aos versionados, gerados em `b00e471` (`REVISAO-FINAL.md`, "Execução limpa": 256 de 260 idênticos na primeira comparação, e nenhum dos quatro restantes é de E1; lido). N1 correspondente executado em `5999c1b`: `test_end_to_end_run_writes_both_files_and_repeats_identically`, nas duas leituras, verde.
- [x] Cada escolha em ponto omisso do artigo (A3, A4, A6, A8, A9, A10, A13, A14) tem comentário com a decisão, o motivo e a seção do artigo, sem identificador interno. Primeira metade lida em `360c3d3`. **Fechado em 08/10/2026:** `docs/02-artigo.md` tem a coluna "Onde no código" nas duas tabelas de leituras (linhas 91 e 116, lido); o grep de referência interna em `project/` não devolve linha (executado em `5999c1b`); `REVISAO-FINAL.md`, V4: hiperparâmetros e passos conferidos contra o manuscrito.
- [x] Uma linha de interpretação por métrica principal está escrita em `results/e1/fiel/RESUMO.md` (o que significa para a detecção). Lido: seção "Métricas do teste" (acurácia, recall e precisão de Malicious-DoH, FPR com intervalo, recall de Benign-DoH, médias macro), com a mesma estrutura em `results/e1/variante/RESUMO.md`.
- [x] Revisor metodológico sem achado bloqueante. **Fechado em 08/10/2026:** `REVISAO-FINAL.md`: nenhum achado bloqueante; V3 (vazamento), V4 (fidelidade) e V5 (sorteios). O achado importante I4 que tocava E1 (scaler da avaliação) foi corrigido em `2686b80`; as oito mutações passaram a derrubar um teste (`REVISAO-FINAL.md`, "Tratamento").

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script rodou na própria sessão de implementação, nesta máquina (decisão 44). **Não se aplica:** o Apuana e o script de submissão em `jobs/` (decisão 44: nada rodou no cluster, a pasta não existe); a saída colada no pull request (decisão 55f: não houve pull request por tarefa). A evidência é a que está versionada: resultados em `results/`, `run.json` com a máquina, os núcleos, as versões, o commit e `dirty: false`, e a execução limpa de 08/10/2026, que regenerou os mesmos `metrics.json` em um clone novo (`REVISAO-FINAL.md`, "Execução limpa"). Os dois fechamentos, "pronta" e "executada", aconteceram na mesma sessão.

## Testes

Seção "Tarefa 08" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e1_reproducao.py`.
