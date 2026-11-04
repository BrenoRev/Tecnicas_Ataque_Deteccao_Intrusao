# 14 · segundo dataset · P1 refeito no combinado sem réplicas, com transferência e combinado publicado ao lado (E6)

**Onde:** `scripts/e6_dataset2.py` (14a), scripts dos baselines e do SHAP no combinado (14b), `src/doh_ids/evaluate.py`, `tests/test_evaluate.py`, `tests/test_pipeline.py`, `results/e6/`
**Objetivo:** refazer no dataset combinado sem réplicas o que P1 produz no CIRA (decisão 47): contagens por classe em cada conjunto, o sistema nas duas leituras de profundidade, a validação cruzada, os baselines da Tabela II e as figuras SHAP. Ao lado, como análises: o retreino no combinado como publicado e a transferência do modelo do CIRA para o HKD. É a entrega de P2.
**Depende de:** 08, 13 (parte 14a); 09, 12 e a 14a (parte 14b)
**Demonstra:** `results/e6/`: no combinado sem réplicas, as matrizes de teste e de validação cruzada do sistema nas duas leituras, os três baselines e as figuras SHAP, com as tabelas de amostras por conjunto e o recall por ferramenta; ao lado, o retreino no combinado publicado e a transferência. Evidência de P2 (seções 6 e 7.2).

## Como ficou (conferido no código e em `results/` em `759ec29`, 08/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Suíte inteira executada em `759ec29`: 110 testes verdes em 41 s; `ruff check` e `ruff format --check` sem erro.

- **Situação: 14a e 14b prontas e executadas.** 14a: hipótese em `c2cb4fc`, funções de avaliação em `e858fc3`, script em `887774c`, resultados em `bc5e510`. 14b: script em `bf593ad` e `3e5aac5` (roda como módulo), resumos e tabela final em `883faca`, fração do HKD na amostra do SHAP em `ac3323e`, resultados em `b32e4f8`. Depois da revisão: `fd253d9`, `15ca118`, `4253571`, `ff039fa` e `38809c1`. Os `run.json` trazem `887774c` (14a) e `3e5aac5` (14b), com `dirty: false` (lido).
- **Arquivos:** `scripts/e6_dataset2.py` (14a), `scripts/e6_baselines_xai.py` (14b), `scripts/e6_resumo.py` (todos os `RESUMO.md` de `results/e6/`, sem treinar), `src/doh_ids/system.py` (`fit_system` e `cross_validated_confusion`, levadas do script de E1 para o pacote em `472bb79`, decisão 51b), `src/doh_ids/evaluate.py` (`recall_by_tool`, `malicious_only_metrics`, `outside_unit_interval`), `tests/test_evaluate.py`, `tests/test_pipeline.py`.
- **Comandos reais, nesta ordem:** `uv run python scripts/e6_dataset2.py`; `uv run python -m scripts.e6_baselines_xai`; `uv run python -m scripts.e6_resumo`. A 14a lê os Parquets, `results/e0/`, `results/e1/` e `results/e6/dados/`. A 14b importa os scripts de E2, E5 e da 14a e lê `results/e6/variante/retreino_sem_replicas/` (o split) e `results/e5/` (o ranking do CIRA). O resumo lê `results/e1/`, `results/e2/`, `results/e5/` e `results/e6/`. Tempo medido: 14a, 2.512 s (42 minutos: 1.488 s e 484 s nos retreinos sem réplicas com validação cruzada, 256 s e 59 s no publicado, 175 s e 50 s na transferência); 14b, 1.839 s (31 minutos: SMOTE 56 s, baselines 610 s, SHAP 1.106 s e 60 s).
- **Resultados:** `results/e6/{fiel,variante}/{transferencia,retreino_publicado,retreino_sem_replicas}/seed42/`; `results/e6/fiel/retreino_sem_replicas-{decision_tree,xgboost,random_forest}/seed42/`; `results/e6/{fiel,variante}/retreino_sem_replicas-shap/seed42/`; `results/e6/RESUMO.md` (tabela final, CIRA ao lado), `results/e6/fiel/RESUMO.md`, `results/e6/variante/RESUMO.md` e `results/e6/fiel/HIPOTESE.md`.
- **Desvios que ficaram:** a trilha nomeia a leitura de profundidade e o recorte, o cenário (decisão 51a); os baselines ficam só na trilha `fiel`, com o modelo no sufixo do recorte; o SHAP, no recorte `-shap`. Não há validação cruzada no publicado nem na transferência. O teste do combinado sem réplicas tem 513 fluxos do HKD (o plano estimava cerca de 526). A hipótese é uma só, em `fiel/`, e vale para as duas trilhas.
- **Pendente de pessoa:** a integração (G10); as duas ressalvas de Q4 seguem para o professor (tarefa 23).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos) divergirem, vale este bloco.**

Q4 foi respondida em 07/10/2026: "devem fazer tudo novamente com outro dataset não usado no trabalho". A decisão 47 traduz isso: o que P1 produz no CIRA é refeito no combinado sem réplicas. A tarefa fica em um arquivo só e é dividida em duas partes, porque a segunda depende de código que as tarefas 09 e 12 ainda vão criar. Não há tarefa nova nem número novo.

| Parte | O que produz | Equivale, no CIRA, a | Depende de |
| --- | --- | --- | --- |
| **14a** | No combinado sem réplicas: contagens por classe em treino, folds e teste; o sistema nas duas leituras de profundidade, avaliado no teste e em validação cruzada de 10 folds; recall por ferramenta. Ao lado: retreino no combinado como publicado e transferência do modelo do CIRA para o HKD | tarefas 05 e 08 (E0 e E1) | 08, 13 |
| **14b** | No combinado sem réplicas: os três baselines da Tabela II e as figuras SHAP dos Random Forests base | tarefas 09 e 12 (E2 e E5) | 09, 12, 14a |

A 14a pode ser fechada e integrada antes da 14b; a tarefa 14 só fica concluída com as duas. A tarefa 15 precisa só da 14a; a 17 precisa das duas.

**O que muda em relação aos passos abaixo:**

- **A validação cruzada passa a ser refeita.** A frase do passo 3, "a validação cruzada de 10 folds da tarefa 08 não é repetida aqui", deixa de valer no combinado sem réplicas: a decisão 47 lista a validação cruzada entre o que é refeito. Usa-se a mesma construção da tarefa 08 (`cross_validated_confusion`: scaler, subconjuntos, SMOTE, bases e meta refeitos em cada fold). No combinado como publicado e na transferência, que são análises ao lado, não há validação cruzada; no publicado continua valendo a tabela de tamanho por fold só com os índices.
- **Duas leituras de profundidade (decisão 45).** No combinado sem réplicas o sistema é treinado com profundidade 5 e sem limite de profundidade, como em E1. Nas análises ao lado, o sistema base é o de profundidade variável; o de profundidade 5 entra onde o custo permitir.
- **Não há figura nem tabela do artigo para o segundo dataset.** `compare_confusion` contra a Fig. 4 e a comparação com a Tabela II não se aplicam; o que vai lado a lado é o resultado do CIRA (tarefas 08, 09 e 12) e o do combinado sem réplicas.
- **O HKD sozinho só tem a classe maliciosa** e não permite treinar o sistema: por isso a transferência é só teste, e isso é declarado no resumo, com as duas ressalvas que o professor não comentou (Non-DoH e Benign-DoH do combinado são os do CIRA; réplicas do HKD no combinado publicado).
- **14b:** os baselines usam os construtores e o SMOTE do treino inteiro criados na tarefa 09; o SHAP usa `explain.py` da tarefa 12, sobre os Random Forests base treinados no combinado sem réplicas. Dois scripts novos e parecidos com os de E2 e E5 são aceitos pela regra de código; a alternativa, os scripts de E2 e de E5 receberem o dataset como argumento, toca arquivos de outras tarefas e é combinada com o usuário.
- **Ponto sem valor declarado: os recortes de `results/e6/`.** A decisão 38 lista três (`transferencia`, `retreino_publicado`, `retreino_sem_replicas`), todos sob a trilha `fiel`. O escopo novo precisa de nome para a leitura de profundidade em cada cenário, para os três baselines no combinado e para o SHAP no combinado. Ver "Pendências abertas pela decisão 45" em `00-README.md`; o implementador não escolhe. Onde os passos e critérios abaixo dizem `results/e6/fiel/<cenário>/seed42/`, isso vale para a profundidade 5.
- Código que já existe e é reutilizado: `stratified_split(table, seed)` estratifica por `label` e serve ao combinado; `fit_scaler`; `balanced_subsets` (as três classes do combinado têm os mesmos papéis das do CIRA); `seen_in_train`; `evaluate` e `metrics_from_confusion`; `malicious_vs_rest` já devolve o FPR com intervalo binomial exato. `fit_system` e `cross_validated_confusion` moram em `scripts/e1_reproducao.py`: ver o bloco "Como ficou" da tarefa 08 sobre levá-las para o pacote.
- `CV_FOLDS` e `CV_SHUFFLE` estão em `config.py` desde `4746c22`. A construção dos folds em `scripts/e0_dados.py` é `validation_fold_rows`, hoje nas linhas 182 a 188.
- **Custo estimado, sem cortar nada** (a partir dos tempos medidos na tarefa 08, com 1.043.197 linhas de treino; o combinado sem réplicas tem cerca de 5 mil fluxos a mais e o publicado, cerca de 105 mil a mais):
  - 14a, combinado sem réplicas, duas leituras com validação cruzada: cerca de 15 minutos na profundidade 5 e 41 na profundidade variável, 56 minutos no total;
  - 14a, combinado publicado: um ajuste por leitura, cerca de 3 minutos na profundidade variável e 2 na profundidade 5;
  - 14a, transferência: o modelo do CIRA não é serializado, então é ajustado de novo: os mesmos 3 e 2 minutos;
  - 14b: não medido; o tempo dos baselines sai da tarefa 09 e o do SHAP, da tarefa 12.
- Execução com dados reais na própria sessão (decisão 44).

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- **Referência da contagem fora de [0, 1] (passo 2):** `results/e0/dados/cira/seed42/split_counts.json`, chave `test_outside_unit_interval`. No teste do CIRA são três valores, em três linhas: um em `FlowSentRate`, um em `PacketLengthMean` e um em `ResponseTimeTimeCoefficientofVariation`.
- A contagem fora de faixa hoje só existe dentro de `scripts/e0_dados.py` (`outside_unit_interval(train, test)`, que ajusta o scaler internamente). A função prevista aqui para `evaluate.py` (T14-3) fica sendo a segunda implementação da mesma conta. Fazer o script de E0 usar a nova toca um arquivo fora da lista desta tarefa: combinar com o usuário.
- **Tabela por fold (passo 3):** a construção é a de `validation_fold_rows` em `scripts/e0_dados.py`, `StratifiedKFold(n_splits=CV_FOLDS, shuffle=CV_SHUFFLE, random_state=SEED_FIEL)` sobre o treino, com as duas constantes em `config.py`. O formato de `split_counts.json` (chaves `train`, `test`, `validation_folds`) serve de modelo para as tabelas dos dois retreinos.
- Scaler da transferência: `fit_scaler(train)` com o treino do CIRA de `stratified_split(table, SEED_FIEL)`; no HKD, `scaler.transform(feature_matrix(hkd))`.
- A asserção da versão sem réplicas pode usar `seen_in_train`, de `splits.py`, restrita às linhas do HKD de cada lado.
- `save_run(experiment="e6", track="fiel", slice_name=<transferencia | retreino_publicado | retreino_sem_replicas>, seed=SEED_FIEL, ...)`; `metrics.json` só com tipos nativos do Python.
- `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45; não altera resultado, só o tempo.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **E6a usa `hkd.parquet` com 5.258 fluxos**, não os 105.160 do arquivo replicado. O recall por ferramenta é o mesmo; o tamanho da amostra reportado é o real. No `Total-48h.csv` não há vetor de 29 atributos repetido nem vetor com dois rótulos (medido em 07/10/2026); o que resta é a quase-duplicata de fluxos da mesma sessão (duas máquinas, mediana de duração colada no tempo limite de 120 s), que o resumo declara.
- **E6b roda duas vezes (decisão 36):** no combinado como publicado, que é o dataset de terceiros tal como distribuído, e no combinado sem réplicas. Resultados em `results/e6/fiel/retreino_publicado/seed42/` e `results/e6/fiel/retreino_sem_replicas/seed42/`. No publicado, cada fluxo do HKD aparece 20 vezes e o split aleatório põe cópias idênticas em treino e teste: o recall das ferramentas novas mede memorização. A versão sem réplicas é a que responde se o sistema detecta as ferramentas novas. As duas vão para a mesma tabela, nomeadas.
- Asserção no script: na versão sem réplicas, nenhum vetor de 29 atributos do HKD aparece em treino e teste ao mesmo tempo. É satisfazível, pelo primeiro item.
- Hipótese a escrever antes de rodar E6a, em `results/e6/fiel/HIPOTESE.md`: os fluxos do HKD têm duração mediana de 120 s e bytes cerca de dez vezes maiores que os maliciosos do CIRA, então parte dos valores normalizados cairá fora de [0, 1].
- Com seed 42 e split 90/10, o teste do combinado sem réplicas tem cerca de 526 fluxos do HKD, perto de 150 por ferramenta. O recall por ferramenta vem com `n` e intervalo de confiança binomial exato, e o resumo declara que é uma estimativa de uma seed. As dez seeds do modelo A no combinado sem réplicas ficam na tarefa 15; se P3 for cortado, essa limitação fica escrita na seção 8 do relatório.

## Arquivos

- `scripts/e6_dataset2.py` — novo (14a).
- Scripts dos baselines e do SHAP no combinado sem réplicas — novos (14b); nomes junto com os recortes, no ponto sem valor declarado do bloco de reconciliação.
- `src/doh_ids/evaluate.py` — acrescentar: recall por ferramenta, contagem de valores fora de [0, 1] por atributo e a avaliação do recorte só de maliciosos (sem precisão, FPR nem acurácia).
- `tests/test_evaluate.py` (T14-1 a T14-3) e `tests/test_pipeline.py` (T14-4) — acrescentar.
- `results/e6/fiel/HIPOTESE.md` — escrita antes de rodar, em commit anterior à primeira execução.
- `results/e6/fiel/transferencia/seed42/`, `results/e6/fiel/retreino_publicado/seed42/`, `results/e6/fiel/retreino_sem_replicas/seed42/` e `results/e6/fiel/RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento` para E6, trilha fiel. Escrever `HIPOTESE.md` antes da primeira execução.
2. **E6a, transferência.** Treinar o sistema da tarefa 08 no CIRA (seed 42). Normalizar os fluxos do HKD com o scaler ajustado no treino do CIRA e prever.
   - Métrica: recall de Malicious-DoH, total e por ferramenta (dnstt, tcp-over-dns, tuns), com `n` e intervalo de confiança binomial exato, e para que classe vão os erros.
   - Contar quantos valores normalizados caem fora de [0, 1], por atributo. Comparar com a contagem da tarefa 05.
   - Não há negativos neste recorte: não calcular precisão, FPR nem acurácia geral, e dizer isso no resultado.
   - Gravar a tabela de contagem do HKD por ferramenta. Neste cenário tudo é teste: não há treino nem validação, e a seção 6 do relatório diz isso com essas palavras.
3. **E6b, retreino.** Pipeline completo da tarefa 08 sobre o combinado, duas vezes (publicado e sem réplicas): split 90/10 estratificado pelas três classes, scaler ajustado no novo treino, três subconjuntos, três bases, meta. Mesma função de avaliação. A validação cruzada de 10 folds da tarefa 08 não é repetida aqui; a tabela de tamanho por classe de cada fold é gerada só com os índices, sem treinar, para a seção 6 responder "treino, validação e teste" também para o segundo dataset.
   - Reportar o recall de Malicious-DoH por ferramenta no teste, usando a coluna `tool`, com `n` e intervalo de confiança.
   - Gerar, para cada retreino, a tabela de amostras por classe em treino, por fold de validação e no teste, que a seção 6 do relatório exige.
   - Na versão sem réplicas, asserção de que nenhum vetor do HKD está em treino e teste ao mesmo tempo.
4. Colocar lado a lado os quatro cenários: CIRA (tarefa 08), transferência, retreino publicado e retreino sem réplicas.
5. Interpretar em `RESUMO.md`, com apoio das distribuições da tarefa 13: se a transferência cair, quais atributos mudaram de faixa; o que a diferença entre os dois retreinos diz sobre memorização.
6. Esta tarefa usa a seed 42. As dez seeds no combinado sem réplicas são feitas na tarefa 15, com a seleção de hiperparâmetros refeita dentro do treino do combinado.
7. **14a, validação cruzada no combinado sem réplicas (decisão 47).** Para cada leitura de profundidade, a matriz somada dos 10 folds sobre o treino do combinado sem réplicas, com o sistema refeito em cada fold, como na tarefa 08. A matriz soma o treino e não tem amostra sintética (asserção).
8. **14b, baselines.** Árvore de decisão, XGBoost e Random Forest da Tabela II, como na tarefa 09, treinados no treino do combinado sem réplicas com SMOTE e avaliados no mesmo teste do passo 3 (asserção de total), com recall por ferramenta.
9. **14b, SHAP.** As figuras da tarefa 12 (equivalentes às Figs. 5, 6a, 6b, 7 e 8) e a tabela de importância para os Random Forests base treinados no combinado sem réplicas, na leitura de profundidade variável; a de profundidade 5 onde o custo permitir. O resumo compara o ranking com o do CIRA.
10. Tabela final de P2, gerada por script: CIRA ao lado do combinado sem réplicas, para o sistema nas duas leituras e para os três baselines; em bloco separado e nomeado, o retreino publicado e a transferência.

## Por quê

Objetivo P2 da especificação. O artigo avalia só com as três ferramentas presentes no treino; a transferência mede o que ele não mede. O retreino cumpre a letra do requisito, com as três classes, e a versão sem réplicas evita que o resultado seja memorização.

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:29` — "obter resultados do sistema proposto no artigo reproduzido em outro conjunto de dados".
- `docs/05-plano-experimental.md:97-104` — desenho de E6a e E6b.
- `docs/04-dados.md:115` — por que os dois cenários.
- Mesma especificação, `:98-103` — a seção 7 pede os resultados do sistema do artigo nos dois conjuntos.
- Mesma especificação, `:93-94` — a seção 6 pede, para o outro dataset, como treino, validação e teste foram formados e quantas amostras há por classe em cada um.

## Risco

- Recall de transferência muito baixo é resultado, não falha. Reportar como está; é a evidência mais forte para a seção de limitações.
- Ajustar o scaler com o HKD em E6a seria vazamento e mudaria a pergunta: asserção de que o scaler usado é o do CIRA.
- No retreino, dois terços das classes são as mesmas linhas do CIRA; métricas gerais parecidas com as da tarefa 08 são esperadas e não provam generalização. A leitura útil é o recall por ferramenta.
- Com uma seed, o recall por ferramenta no retreino sem réplicas tem intervalo largo: reportar `n` e intervalo, não só a taxa.

## Critério de aceite

- [x] `results/e6/fiel/transferencia/seed42/metrics.json` com recall por ferramenta (`n` e intervalo), destino dos erros, contagem de valores fora de faixa e a tabela do HKD por ferramenta. Lido: chaves `hkd.by_tool`, `hkd.malicious`, `hkd_outside_unit_interval`, `hkd_rows_by_tool`; 5.258 fluxos. O mesmo em `variante/`.
- [x] `results/e6/fiel/retreino_publicado/seed42/metrics.json` e `results/e6/fiel/retreino_sem_replicas/seed42/metrics.json` com as métricas completas, o recall por ferramenta e a tabela de amostras por classe em treino, por fold de validação e no teste. Lido: chaves `test`, `test_recall_by_tool`, `test_recall_by_origin`, `split`.
- [x] Nenhuma precisão ou FPR reportada para o recorte só de maliciosos. Executado: `test_malicious_only_evaluation_reports_no_precision_fpr_or_accuracy`. Lido: `hkd.negatives` registra a ausência de negativos.
- [ ] Asserção da versão sem réplicas verde, com a saída colada no pull request. Lido: `hkd_test_rows_seen_in_train` é 0 nas duas trilhas. O pull request é de pessoa.
- [x] Tabela comparativa dos quatro cenários gerada por script. Lido: `results/e6/RESUMO.md`, escrito por `scripts/e6_resumo.py`.
- [x] 14a: no combinado sem réplicas, matriz de teste e matriz de validação cruzada de 10 folds para as duas leituras de profundidade; a de validação soma o treino (asserção). Lido: nas duas trilhas a matriz de validação soma 1.047.929, o treino, e a de teste, 116.437.
- [x] 14a: o resumo declara que o HKD sozinho só tem a classe maliciosa, e as duas ressalvas sobre o combinado. Lido: `results/e6/fiel/RESUMO.md:14` e `:29`; `results/e6/RESUMO.md:25`.
- [x] 14b: três baselines no combinado sem réplicas, avaliados no mesmo teste da 14a (asserção de total), com métricas macro e ponderada nomeadas. Lido: as três matrizes somam 116.437.
- [x] 14b: figuras SHAP e tabela de importância dos Random Forests base treinados no combinado sem réplicas, com o tamanho da amostra registrado. Lido: os nove arquivos nos dois recortes `-shap`; `sample_per_class_requested` 2.000.
- [x] Tabela final de P2 (CIRA ao lado do combinado sem réplicas) gerada por script. Lido: `results/e6/RESUMO.md`.
- [x] Todo resultado diz, no caminho e no `run.json`, a leitura de profundidade e o dataset. Lido: `config.max_depth`, `config.dataset` e `config.readings.base_depth`.
- [ ] `HIPOTESE.md` em commit anterior à primeira execução; interpretação em `RESUMO.md`, com uma linha por número principal. Primeira metade lida no histórico: `c2cb4fc` vem antes de `887774c`, o commit dos `run.json`. A segunda não foi relida.
- [ ] Revisor metodológico sem achado bloqueante. Informado pela sessão principal como feito, com os achados tratados; não há artefato da revisão para conferir aqui. Lido: commits de correção posteriores (`ac3323e`, `fd253d9`, `15ca118`, `ff039fa`, `38809c1`).

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script roda na própria sessão de implementação, nesta máquina, quando a tarefa chega ao ponto de executar (decisão 44); não se espera um integrante designado. O Apuana continua sendo opção (decisão 42). A evidência é a mesma: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e6.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). A execução é feita com a árvore limpa (o plano em commit antes de rodar, porque `dirty` mede o repositório inteiro) e o resultado entra em commit `exp`. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão.

## Testes

Seção "Tarefa 14" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e6_dataset2.py` na 14a e `uv run python -m scripts.e6_baselines_xai` na 14b; os resumos saem de `uv run python -m scripts.e6_resumo`. O gate é aplicado a cada parte.
