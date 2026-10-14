# 07 · reprodução · três subconjuntos balanceados

**Onde:** `src/doh_ids/splits.py`, `tests/test_splits.py`
**Objetivo:** os três subconjuntos de treino descritos na seção III-B do artigo, construídos de forma determinística e conferível.
**Depende de:** 05
**Demonstra:** resumo dos três subconjuntos: contagens, razão obtida contra 15:12:12, fração sintética (gravado pela tarefa 08). Seções 4 e 6.

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

- [ ] Testes do invariante I3 e dos itens do passo 7 verdes.
- [ ] Com os dados reais e seed 42, o resumo mostra três subconjuntos com o mesmo conjunto de maliciosos e partes de Non-DoH disjuntas (asserção no script da tarefa 08).
- [ ] O resumo registra a razão obtida e a fração sintética, para o relatório.

## Testes

Seção "Tarefa 07" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de biblioteca: G1–G4, G7–G10. A execução com dados reais acontece na tarefa 08.
