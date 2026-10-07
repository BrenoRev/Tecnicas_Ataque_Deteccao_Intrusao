# 07 · reprodução · três subconjuntos balanceados

**Onde:** `src/doh_ids/splits.py`, `tests/test_splits.py`
**Objetivo:** os três subconjuntos de treino descritos na seção III-B do artigo, construídos de forma determinística e conferível.
**Depende de:** 05
**Demonstra:** resumo dos três subconjuntos: contagens, razão obtida contra 15:12:12, fração sintética (gravado pela tarefa 08). Seções 4 e 6.

> **Situação (07/10/2026, reconciliação no commit `360c3d3`): pronta em `a4ba0e5`** (branch `tarefa/07-subconjuntos`, nascida de `tarefa/06-avaliacao-metricas`). Executada com os dados reais dentro da tarefa 08 (`798ecd3`). Aguarda integração por pessoa (G10).

## Como ficou (conferido no código em `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- `splits.py`: `balanced_subsets(X_train, y_train, seed)` devolve `(subsets, summary)`. `subsets` é a lista de três pares `(X, y)`, com as linhas reais primeiro (parte de Non-DoH, benignos, maliciosos) e as sintéticas no fim. `summary` tem um dicionário por subconjunto: `class_counts` (posição é o código da classe), `ratio` (contagens divididas pela da classe maliciosa) e `synthetic_benign_fraction`.
- SMOTE: `SMOTE(sampling_strategy={BENIGN: len(malicious)}, random_state=smote_seed(seed, index))`, vizinhos no padrão da biblioteca.
- **O ponto sem valor declarado do bloco abaixo foi resolvido no código:** o Non-DoH é embaralhado com `np.random.default_rng(seed).permutation`, a própria seed da execução, e cortado com `np.array_split`. Nenhuma decisão registra essa escolha; a decisão 41 só fala do SMOTE, dos Random Forests e do meta. Fica para o usuário confirmar se ela entra como adendo da decisão 41.
- **A função fixa o papel de cada classe:** divide a classe 0 em três, repete as classes 1 e 2 e aumenta a classe 1 até o tamanho da 2. Serve para o CIRA e para o combinado. Para a tarefa 21, em que as classes são ferramentas, o papel de cada classe precisa ser declarado antes.
- A tarefa 08 acrescenta ao resumo, no script, `ratio_article_scale` e `article_ratio`, e grava tudo em `metrics.json`, chave `subsets`.
- Medido com a seed 42 (`results/e1/fiel/proposto/seed42/metrics.json`, chave `subsets`): contagens 266.943 / 224.598 / 224.598 nos dois primeiros subconjuntos e 266.942 / 224.598 / 224.598 no terceiro; fração de benignos sintéticos 0,9209; razão na escala do artigo 14,26 : 12 : 12, ao lado de 15 : 12 : 12. Confere com o bloco "Verificado nos dados".

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- Dependência: a 05 está pronta, executada e não integrada. Em execução encadeada, a branch nasce de `tarefa/05-split-scaler`.
- `src/doh_ids/splits.py` e `tests/test_splits.py` já existem. `splits.py` tem `stratified_split(flows, seed)`, que devolve `(train, test)` como DataFrames com o índice original; `fit_scaler(train)`, que devolve o `MinMaxScaler`; e `seen_in_train(train, test)`.
- "Treino já normalizado" (passo 1) é `fit_scaler(train).transform(feature_matrix(train))`: um array de 29 colunas, sem nomes, na ordem de `FEATURE_COLUMNS`. Os rótulos são `train["label"]`. `feature_matrix` vem de `doh_ids.data`.
- A seed do SMOTE do subconjunto `i` é `smote_seed(seed, i)`, função de `config.py`; não se escreve a fórmula no módulo. O número de subconjuntos é `N_SUBSETS`.
- **Ponto sem valor declarado:** a decisão 41 fixa a seed do SMOTE, dos Random Forests e do meta-classificador, mas não a do embaralhamento do Non-DoH (passo 2). Confirmar com o usuário antes de implementar; o implementador não escolhe.
- Contagens do bloco abaixo conferidas contra `split_counts.json`: `train.rows` é 800.828 / 17.771 / 224.598.
- Os testes T07-1 a T07-5 entram em `tests/test_splits.py`, com a fixture `synthetic_flows`.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- Non-DoH de treino: 800.828. As três partes têm 266.943, 266.943 e 266.942 amostras. Maliciosos de treino: 224.598; benignos reais: 17.771. Com o SMOTE até igualar a classe maliciosa, 206.827 benignos de cada subconjunto são sintéticos (92,1%).

## Arquivos

- `src/doh_ids/splits.py` — acrescentar a função de subconjuntos balanceados.
- `tests/test_splits.py` — acrescentar testes.

## O que fazer

1. Receber o treino já normalizado e a seed.
2. Embaralhar o Non-DoH de treino e dividi-lo em três partes disjuntas de tamanho igual (ou diferindo em uma amostra).
3. Montar cada subconjunto com: uma parte do Non-DoH, todos os maliciosos do treino, todos os benignos do treino.
4. Aplicar SMOTE só à classe benigna, até ela ter o mesmo número de amostras da classe maliciosa (decisão 14), com `k_neighbors` no padrão da biblioteca e seed `seed * 100 + i` para o subconjunto `i` (decisão 41).
5. Devolver os três pares (atributos, rótulos) e um resumo: contagem por classe, razão obtida e fração de benignos sintéticos em cada um.
6. Não implementar one-sided selection aqui. Ela só entra se a variante opcional `oss` da tarefa 10 for feita.
7. Testes com dados sintéticos: partes de Non-DoH disjuntas e cobrindo todo o Non-DoH; maliciosos idênticos nos três; nenhuma amostra sintética de Non-DoH ou de malicioso; benignos reais presentes integralmente; mesma seed, mesmo resultado.

## Por quê

É o "balanced" do Balanced Stacked Random Forest. O artigo descreve a construção em uma frase e declara a razão 15:12:12 sem dizer como chegou a ela (A4), nem os parâmetros do SMOTE (A6).

## Evidência — verificada no baseline

- `docs/02-artigo.md:18` — descrição do balanceamento (seção III-B).
- `docs/02-artigo.md:90` — A4: o 15:12:12 do artigo é a razão inicial arredondada 45:1:12 com o Non-DoH dividido por três; com as contagens reais (266.943 de Non-DoH e 224.598 maliciosos) dá 14,3:12.
- `docs/04-dados.md:48` — estimativa de 92% de benignos sintéticos.
- `planejamento/MEMORY/01-discovery-stack.md` — assinatura do `SMOTE`; `sampling_strategy` aceita dicionário; custo de 0,4 s nesse tamanho.

## Risco

- A razão obtida (cerca de 14,3:12:12) não ser exatamente a 15:12:12 do artigo. É esperado e não é divergência: o artigo arredonda a razão inicial para 45:1:12 e divide 45 por três. Reportar as duas com essa explicação.
- SMOTE interpola fluxos e pode gerar combinações impossíveis no protocolo. Não se corrige na trilha fiel; é limitação a declarar e argumento de M1.

## Critério de aceite

Conferido em 07/10/2026 no commit `360c3d3`.

- [x] Testes do invariante I3 e dos itens do passo 7 verdes. Executado: `tests/test_splits.py` inteiro, verde; os cinco testes desta tarefa são `test_non_doh_parts_are_disjoint_cover_train_and_differ_by_at_most_one`, `test_malicious_rows_are_the_same_real_rows_in_every_subset`, `test_benign_keeps_every_real_row_and_reaches_the_malicious_count`, `test_no_synthetic_sample_in_non_doh` e `test_same_seed_gives_same_subsets_and_other_seed_gives_others`.
- [x] Com os dados reais e seed 42, o resumo mostra três subconjuntos com o mesmo conjunto de maliciosos e partes de Non-DoH disjuntas (asserção no script da tarefa 08). Lido: asserções em `scripts/e1_reproducao.py:116-121` (o Non-DoH dos três subconjuntos soma o Non-DoH do treino; cada subconjunto tem a contagem de maliciosos do treino) e as contagens em `metrics.json`. A asserção com dados reais é por contagem; a identidade das linhas é coberta pelos testes sintéticos do item anterior.
- [x] O resumo registra a razão obtida e a fração sintética, para o relatório. Lido: chave `subsets` de `metrics.json` nas duas leituras de profundidade e a seção "Subconjuntos de treino" dos dois `RESUMO.md`.

## Testes

Seção "Tarefa 07" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de biblioteca: G1–G4, G7–G10. A execução com dados reais acontece na tarefa 08.
