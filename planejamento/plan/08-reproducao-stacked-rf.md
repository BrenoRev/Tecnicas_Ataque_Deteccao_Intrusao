# 08 · reprodução · Balanced Stacked Random Forest (E1)

**Onde:** `src/doh_ids/models.py`, `scripts/e1_reproducao.py`, `tests/test_models.py`, `tests/test_pipeline.py`, `results/e1/fiel/proposto/seed42/`
**Objetivo:** o sistema proposto pelo artigo, treinado e avaliado como o texto descreve, com o resultado posto ao lado da Fig. 4 e da Tabela II. É a entrega central de P1.
**Depende de:** 06, 07
**Demonstra:** `results/e1/fiel/proposto/seed42/`: matriz de confusão da reprodução ao lado da Fig. 4b, célula a célula, com a diferença. Evidência central de P1 (seção 7.1).

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

- [ ] `results/e1/fiel/proposto/seed42/metrics.json` contém as duas matrizes, métricas por classe, macro e ponderada, as duas AUC nomeadas, a tabela de decisão do meta e a fração de desacordo entre bases.
- [ ] O mesmo diretório contém a comparação com a Fig. 4a, a Fig. 4b e a Tabela II, com as diferenças.
- [ ] `run.json` registra trilha `fiel`, seed 42 e, por nome, as leituras adotadas nos pontos omissos (dados de treino do meta, `use_probas`, alvo e parâmetros do SMOTE, origem dos hiperparâmetros). Correspondem às decisões 09, 13, 14 e 15, mas o arquivo não cita número de decisão.
- [ ] Duas execuções produzem métricas idênticas.
- [ ] Cada escolha em ponto omisso do artigo (A3, A4, A6, A8, A9, A10, A13, A14) tem comentário com a decisão, o motivo e a seção do artigo, sem identificador interno. Conferido um a um na revisão; no fechamento, o agente `cin0114-doc-sync` acrescenta à tabela de ambiguidades de `docs/02-artigo.md` uma coluna "onde no código" e a preenche.
- [ ] Uma linha de interpretação por métrica principal está escrita em `results/e1/fiel/RESUMO.md` (o que significa para a detecção).
- [ ] Revisor metodológico sem achado bloqueante.

## Execução com dados reais: local ou Apuana (decisão 42)

O script roda na máquina de quem tem os dados ou no cluster Apuana; as duas formas valem. O que importa é treinar e deixar a evidência: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e1.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). Quem executa roda com a árvore limpa e faz o commit `exp`. A tarefa fica "pronta" sem isso e "executada" com isso.

## Testes

Seção "Tarefa 08" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e1_reproducao.py`.
