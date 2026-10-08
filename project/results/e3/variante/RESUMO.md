# E3: sensibilidade às leituras que o artigo deixa em aberto

Gerado por `scripts/e3_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e3_sensibilidade.py`. Os números de cada recorte vêm de
`<recorte>/seed42/metrics.json`; a configuração e os tempos, de
`<recorte>/seed42/run.json`; a tabela abaixo, sem arredondamento, está em
`comparacao.csv`. Uma única execução de cada recorte, com a seed 42: não há
média nem desvio padrão, e diferença pequena entre recortes não distingue
leitura de variação entre seeds. Todos os recortes são avaliados no mesmo
teste, de 115911 fluxos. Não há validação cruzada aqui.

A lista das leituras alternativas e as duas configurações de partida foram fixadas no código em commit anterior à execução: os `run.json` registram o commit `d774223`, com a árvore limpa. Não houve hipótese escrita antes de rodar, e isso não se conserta depois: nenhum número desta pasta foi confrontado com uma expectativa declarada antes de ser visto.

## O que foi variado

O artigo não especifica os pontos abaixo. A reprodução adota uma leitura em
cada um; cada recorte troca uma leitura só e mantém todo o resto da
configuração de partida. A exceção é `rf_unico`, que troca vários pontos de
uma vez, de propósito: é a configuração do script publicado pelos autores, que
não empilha.

| ponto em aberto no artigo | leitura alternativa | recortes |
| --- | --- | --- |
| peso de classe nos Random Forests base | class_weight='balanced' nos três bases, como no script publicado pelos autores | `class_weight`, `class_weight-prof5` |
| entrada do meta-classificador | probabilidades por classe de cada base (use_probas=True), nove entradas | `use_probas`, `use_probas-prof5` |
| atributos candidatos em cada divisão das árvores | padrão da biblioteca (max_features='sqrt') em vez de 28 | `max_features_padrao`, `max_features_padrao-prof5` |
| dados de treino do meta-classificador | predições dos bases na união dos três subconjuntos balanceados | `meta_uniao`, `meta_uniao-prof5` |
| sistema inteiro: a configuração do script publicado pelos autores | um Random Forest só, com class_weight='balanced', max_features no padrão da biblioteca, sem subconjuntos, sem SMOTE e sem meta-classificador | `rf_unico`, `rf_unico-prof5` |

Configurações de partida, as duas leituras da profundidade das árvores:

- **profundidade variável:** sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Medida em `results/e1/variante/profundidade_variavel/seed42/`; recortes desta partida sem sufixo.
- **profundidade 5:** profundidade máxima 5 nos submodelos (Seção IV-B). Medida em `results/e1/fiel/proposto/seed42/`; recortes desta partida com o sufixo `-prof5`.

O script publicado pelos autores usa profundidade máxima 5: dos dois recortes de
`rf_unico`, o que corresponde a ele é `rf_unico-prof5`.

## Teste ao lado da Fig. 4b

As colunas de Benign-DoH estão em negrito: é a classe menor, e é nela que as
leituras mais diferem. FPR de Malicious-DoH é o de Malicious-DoH contra o resto.

| configuração | partida | acurácia | recall Non-DoH | **recall Benign-DoH** | **precisão Benign-DoH** | **F1 Benign-DoH** | recall Malicious-DoH | precisão Malicious-DoH | FPR Malicious-DoH | F1 macro | soma das diferenças absolutas para a Fig. 4b |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Artigo, Fig. 4b |  | 99.78% | 99.94% | **90.23%** | **97.27%** | **93.62%** | 99.98% | 99.99% | 0.0033% | 97.82% | 0 |
| partida (profundidade variável) | profundidade variável | 99.64% | 99.69% | **92.91%** | **87.13%** | **89.93%** | 99.96% | 99.99% | 0.0033% | 96.56% | 553 |
| class_weight | profundidade variável | 99.62% | 99.67% | **93.06%** | **85.97%** | **89.38%** | 99.96% | 100.00% | 0.0011% | 96.37% | 611 |
| use_probas | profundidade variável | 99.66% | 99.72% | **92.76%** | **88.42%** | **90.54%** | 99.97% | 99.98% | 0.0066% | 96.76% | 489 |
| max_features_padrao | profundidade variável | 99.56% | 99.60% | **93.11%** | **83.44%** | **88.01%** | 99.94% | 100.00% | 0.0000% | 95.90% | 749 |
| meta_uniao | profundidade variável | 99.47% | 99.44% | **94.43%** | **78.96%** | **86.00%** | 99.96% | 99.99% | 0.0033% | 95.21% | 1061 |
| rf_unico | profundidade variável | 99.65% | 99.73% | **92.20%** | **88.31%** | **90.22%** | 99.96% | 99.99% | 0.0022% | 96.65% | 469 |
| partida (profundidade 5) | profundidade 5 | 97.79% | 99.93% | **0.00%** | **0.00%** | **0.00%** | 97.91% | 99.76% | 0.0649% | 65.80% | 4711 |
| class_weight-prof5 | profundidade 5 | 97.71% | 99.85% | **0.00%** | **0.00%** | **0.00%** | 97.80% | 99.50% | 0.1352% | 65.72% | 4895 |
| use_probas-prof5 | profundidade 5 | 97.69% | 99.77% | **0.00%** | **0.00%** | **0.00%** | 97.97% | 99.11% | 0.2408% | 65.69% | 4963 |
| max_features_padrao-prof5 | profundidade 5 | 97.42% | 99.44% | **0.00%** | **0.00%** | **0.00%** | 97.92% | 97.55% | 0.6751% | 65.38% | 5579 |
| meta_uniao-prof5 | profundidade 5 | 96.11% | 95.84% | **85.97%** | **29.92%** | **44.39%** | 97.89% | 99.84% | 0.0429% | 80.28% | 8511 |
| rf_unico-prof5 | profundidade 5 | 93.24% | 91.93% | **89.52%** | **19.89%** | **32.54%** | 98.20% | 98.23% | 0.4848% | 75.47% | 15287 |

## O que cada ponto muda, e quanto

Diferença de cada recorte para a sua configuração de partida, em pontos
percentuais (pp).

- **`class_weight`**, sobre a partida de profundidade variável: recall de Benign-DoH de 92.91% para 93.06% (+0.15 pp); precisão de Benign-DoH de 87.13% para 85.97% (-1.16 pp); recall de Malicious-DoH +0.00 pp; FPR de Malicious-DoH -0.0022 pp; acurácia -0.02 pp; F1 macro -0.19 pp; soma das diferenças absolutas de 553 para 611.
- **`use_probas`**, sobre a partida de profundidade variável: recall de Benign-DoH de 92.91% para 92.76% (-0.15 pp); precisão de Benign-DoH de 87.13% para 88.42% (+1.28 pp); recall de Malicious-DoH +0.01 pp; FPR de Malicious-DoH +0.0033 pp; acurácia +0.02 pp; F1 macro +0.21 pp; soma das diferenças absolutas de 553 para 489.
- **`max_features_padrao`**, sobre a partida de profundidade variável: recall de Benign-DoH de 92.91% para 93.11% (+0.20 pp); precisão de Benign-DoH de 87.13% para 83.44% (-3.69 pp); recall de Malicious-DoH -0.02 pp; FPR de Malicious-DoH -0.0033 pp; acurácia -0.08 pp; F1 macro -0.66 pp; soma das diferenças absolutas de 553 para 749.
- **`meta_uniao`**, sobre a partida de profundidade variável: recall de Benign-DoH de 92.91% para 94.43% (+1.52 pp); precisão de Benign-DoH de 87.13% para 78.96% (-8.17 pp); recall de Malicious-DoH +0.00 pp; FPR de Malicious-DoH +0.0000 pp; acurácia -0.17 pp; F1 macro -1.34 pp; soma das diferenças absolutas de 553 para 1061.
- **`rf_unico`**, sobre a partida de profundidade variável: recall de Benign-DoH de 92.91% para 92.20% (-0.71 pp); precisão de Benign-DoH de 87.13% para 88.31% (+1.18 pp); recall de Malicious-DoH -0.00 pp; FPR de Malicious-DoH -0.0011 pp; acurácia +0.01 pp; F1 macro +0.10 pp; soma das diferenças absolutas de 553 para 469.
- **`class_weight-prof5`**, sobre a partida de profundidade 5: recall de Benign-DoH de 0.00% para 0.00% (+0.00 pp); precisão de Benign-DoH de 0.00% para 0.00% (+0.00 pp); recall de Malicious-DoH -0.11 pp; FPR de Malicious-DoH +0.0704 pp; acurácia -0.09 pp; F1 macro -0.08 pp; soma das diferenças absolutas de 4711 para 4895.
- **`use_probas-prof5`**, sobre a partida de profundidade 5: recall de Benign-DoH de 0.00% para 0.00% (+0.00 pp); precisão de Benign-DoH de 0.00% para 0.00% (+0.00 pp); recall de Malicious-DoH +0.06 pp; FPR de Malicious-DoH +0.1759 pp; acurácia -0.11 pp; F1 macro -0.12 pp; soma das diferenças absolutas de 4711 para 4963.
- **`max_features_padrao-prof5`**, sobre a partida de profundidade 5: recall de Benign-DoH de 0.00% para 0.00% (+0.00 pp); precisão de Benign-DoH de 0.00% para 0.00% (+0.00 pp); recall de Malicious-DoH +0.01 pp; FPR de Malicious-DoH +0.6102 pp; acurácia -0.38 pp; F1 macro -0.42 pp; soma das diferenças absolutas de 4711 para 5579.
- **`meta_uniao-prof5`**, sobre a partida de profundidade 5: recall de Benign-DoH de 0.00% para 85.97% (+85.97 pp); precisão de Benign-DoH de 0.00% para 29.92% (+29.92 pp); recall de Malicious-DoH -0.02 pp; FPR de Malicious-DoH -0.0220 pp; acurácia -1.68 pp; F1 macro +14.48 pp; soma das diferenças absolutas de 4711 para 8511.
- **`rf_unico-prof5`**, sobre a partida de profundidade 5: recall de Benign-DoH de 0.00% para 89.52% (+89.52 pp); precisão de Benign-DoH de 0.00% para 19.89% (+19.89 pp); recall de Malicious-DoH +0.29 pp; FPR de Malicious-DoH +0.4200 pp; acurácia -4.56 pp; F1 macro +9.66 pp; soma das diferenças absolutas de 4711 para 15287.

## Bases isolados e modelo empilhado

Recall de Benign-DoH de cada Random Forest base avaliado sozinho no teste, ao
lado do recall do modelo empilhado. Quando os bases acertam a classe e o modelo
empilhado não, a perda acontece no meta-classificador.

- **`class_weight`:** bases 94.28%, 94.28%, 94.38%; modelo empilhado 93.06%.
- **`use_probas`:** bases 94.33%, 94.38%, 94.13%; modelo empilhado 92.76%.
- **`max_features_padrao`:** bases 93.87%, 94.48%, 94.78%; modelo empilhado 93.11%.
- **`meta_uniao`:** bases 94.33%, 94.38%, 94.13%; modelo empilhado 94.43%.
- **`class_weight-prof5`:** bases 87.90%, 88.25%, 88.25%; modelo empilhado 0.00%.
- **`use_probas-prof5`:** bases 85.16%, 85.97%, 85.16%; modelo empilhado 0.00%.
- **`max_features_padrao-prof5`:** bases 85.82%, 86.73%, 89.42%; modelo empilhado 0.00%.
- **`meta_uniao-prof5`:** bases 85.16%, 85.97%, 85.16%; modelo empilhado 85.97%.

## Como ler a comparação

A soma das diferenças absolutas conta linhas, e Benign-DoH tem 1975 das
115911 linhas do teste (1.70%). Um modelo que nunca prediz
essa classe erra no máximo essas linhas, e a soma quase não registra a perda de
uma classe inteira. Por isso a soma vai ao lado das métricas por classe, e
nenhuma leitura é declarada a mais próxima do artigo por um número só.

Nos recortes de profundidade variável, a soma das diferenças absolutas vai de 469 a 1061; a da partida, com a seed 42, é 553. O mesmo modelo de partida, nas 10 seeds de `results/e4/corrigida/A/`, tem soma de 509 a 653: só a troca do split e dos sorteios move a soma em até 144 linhas. Diferença entre recortes menor que essa não ordena as leituras, e nenhum recorte é apontado como o mais próximo da Fig. 4b. O recorte que corresponde ao script publicado pelos autores, `rf_unico-prof5`, tem a maior soma entre os 10 recortes medidos (15287; a maior é 15287).

Não predizem Benign-DoH em nenhuma linha do teste: `use_probas-prof5`, `max_features_padrao-prof5`. Nesses recortes a precisão da classe é indefinida e entra como 0 no F1 macro.

## Medido e hipótese

Medido: as matrizes de confusão de cada recorte no teste, as métricas derivadas
delas e a distância de cada uma à Fig. 4b. Tudo o que está nas seções acima.

Hipótese, não demonstrada por estes números:

- Que a Fig. 4b tenha sido gerada com alguma das leituras medidas. Uma soma
  pequena é compatível com a leitura e não a identifica: leituras diferentes
  podem dar matrizes parecidas, o artigo não informa a seed, e há uma execução
  só de cada recorte.
- Que os números publicados tenham vindo do script publicado, com um Random
  Forest só, e não do sistema descrito no texto. O que se mediu é o resultado de
  `rf_unico-prof5` nos nossos dados. O arquivo que aquele script lê não foi
  publicado, e não se sabe com que limpeza e com que atributos ele foi gerado:
  a distância medida aqui não confirma nem descarta a hipótese.

A reprodução do artigo continua sendo a de `results/e1/`, nas duas leituras da
profundidade. Os recortes desta pasta informam a discussão das ambiguidades e
não substituem a reprodução. Nenhuma seed, hiperparâmetro ou regra de limpeza
foi ajustada para aproximar o resultado.

## O que não foi medido

- **Meta-classificador com predições fora da amostra** (`StackingCVClassifier`
  do mlxtend). Não feita: essa classe ajusta todos os bases no mesmo conjunto e
  não reproduz um subconjunto por base. Efeito: não se sabe quanto do
  resultado depende de o meta-classificador ver predições de bases sobre linhas
  que eles já viram no treino.
- **One-sided selection antes do SMOTE.** Não feita: o artigo cita a técnica uma
  vez (Seção III-B) e não a descreve. Efeito: os subconjuntos de todos os
  recortes têm todo o Non-DoH da sua parte, sem seleção.
- **Um modelo com 28 atributos no total**, a outra leitura de "selected at
  random from 28 features" (Seção IV-A). Não feita: o artigo não diz qual
  atributo sairia, e escolher um seria arbitrário.
- **Duas leituras trocadas ao mesmo tempo** no sistema empilhado, por exemplo
  probabilidades na entrada do meta-classificador ajustado na união dos
  subconjuntos. Cada recorte troca um ponto; o efeito conjunto não é a soma dos
  efeitos separados.
- **Validação cruzada e outras seeds.** Cada recorte tem uma execução, só no teste.
- **A profundidade das árvores** não é repetida: as duas leituras estão em
  `results/e1/` e entram na tabela como as configurações de partida.
