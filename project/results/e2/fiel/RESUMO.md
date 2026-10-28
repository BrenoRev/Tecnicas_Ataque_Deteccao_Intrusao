# E2: modelos de comparação da Tabela II do artigo, trilha fiel

Gerado por `scripts/e2_baselines.py`. Os números dos três modelos de comparação
vêm de `<modelo>/seed42/metrics.json` e os tempos de treino de
`<modelo>/seed42/run.json`. Os do modelo proposto são lidos dos resultados
de `scripts/e1_reproducao.py`, sem treinar de novo.
Uma única execução, com a seed 42: não há média nem desvio padrão.
Classes na ordem dos códigos: Non-DoH, Benign-DoH, Malicious-DoH.

## Protocolo

Mesmo split e mesmo teste do modelo proposto: 115911 fluxos, por classe
[88981, 1975, 24955]. O normalizador é ajustado no treino. O treino inteiro é
balanceado com SMOTE: de [800828, 17771, 224598] fluxos por classe passa a
[800828, 800828, 800828], com [0, 783057, 576230] amostras sintéticas. A Tabela II
só diz "SMOTE balanced"; igualar as duas classes menores à maior é leitura nossa.
A tabela informa a profundidade máxima 10 da árvore de decisão e as
10 árvores do Random Forest; todos os outros hiperparâmetros ficam no
padrão do scikit-learn e do XGBoost.

## Tabela II, metade superior: artigo e reprodução

A Tabela II não diz que média usa nem como calcula a AUC com três classes. Cada
valor do artigo aparece ao lado da nossa média macro e da ponderada. A
diferença é o valor obtido menos o do artigo, em pontos percentuais. O modelo
proposto aparece nas duas leituras da profundidade dos Random Forests base;
nele, `roc_auc_ovr_macro` é a AUC da saída do meta-classificador e
`roc_auc_ovr_macro_base_mean` a da média das probabilidades dos bases.

| modelo | métrica da Tabela II | artigo | métrica obtida | valor | dif. (pp) |
| --- | --- | --- | --- | --- | --- |
| Árvore de decisão | auc | 0.8617 | roc_auc_ovr_macro | 0.992682 | +13.0982 |
| Árvore de decisão | accuracy | 0.977 | accuracy | 0.972306 | -0.4694 |
| Árvore de decisão | f1 | 0.8197 | macro_f1 | 0.842075 | +2.2375 |
| Árvore de decisão | f1 | 0.8197 | weighted_f1 | 0.977452 | +15.7752 |
| Árvore de decisão | precision | 0.9658 | macro_precision | 0.794507 | -17.1293 |
| Árvore de decisão | precision | 0.9658 | weighted_precision | 0.986741 | +2.0941 |
| Árvore de decisão | recall | 0.712 | macro_recall | 0.964102 | +25.2102 |
| Árvore de decisão | recall | 0.712 | weighted_recall | 0.972306 | +26.0306 |
| XGBoost | auc | 0.9986 | roc_auc_ovr_macro | 0.998613 | +0.0013 |
| XGBoost | accuracy | 0.9927 | accuracy | 0.993090 | +0.0390 |
| XGBoost | f1 | 0.9843 | macro_f1 | 0.939987 | -4.4313 |
| XGBoost | f1 | 0.9843 | weighted_f1 | 0.993531 | +0.9231 |
| XGBoost | precision | 0.9956 | macro_precision | 0.909176 | -8.6424 |
| XGBoost | precision | 0.9956 | weighted_precision | 0.994483 | -0.1117 |
| XGBoost | recall | 0.9732 | macro_recall | 0.980477 | +0.7277 |
| XGBoost | recall | 0.9732 | weighted_recall | 0.993090 | +1.9890 |
| Random Forest | auc | 0.9999 | roc_auc_ovr_macro | 0.996580 | -0.3320 |
| Random Forest | accuracy | 0.9998 | accuracy | 0.994194 | -0.5606 |
| Random Forest | f1 | 0.9987 | macro_f1 | 0.948025 | -5.0675 |
| Random Forest | f1 | 0.9987 | weighted_f1 | 0.994467 | -0.4233 |
| Random Forest | precision | 0.9989 | macro_precision | 0.923742 | -7.5158 |
| Random Forest | precision | 0.9989 | weighted_precision | 0.995026 | -0.3874 |
| Random Forest | recall | 0.9985 | macro_recall | 0.977744 | -2.0756 |
| Random Forest | recall | 0.9985 | weighted_recall | 0.994194 | -0.4306 |
| Modelo proposto, fiel (profundidade 5) | auc | 0.9999 | roc_auc_ovr_macro | 0.961172 | -3.8728 |
| Modelo proposto, fiel (profundidade 5) | auc | 0.9999 | roc_auc_ovr_macro_base_mean | 0.988858 | -1.1042 |
| Modelo proposto, fiel (profundidade 5) | accuracy | 0.9998 | accuracy | 0.977949 | -2.1851 |
| Modelo proposto, fiel (profundidade 5) | f1 | 0.9991 | macro_f1 | 0.658027 | -34.1073 |
| Modelo proposto, fiel (profundidade 5) | f1 | 0.9991 | weighted_f1 | 0.969555 | -2.9545 |
| Modelo proposto, fiel (profundidade 5) | precision | 0.9991 | macro_precision | 0.656759 | -34.2341 |
| Modelo proposto, fiel (profundidade 5) | precision | 0.9991 | weighted_precision | 0.961475 | -3.7625 |
| Modelo proposto, fiel (profundidade 5) | recall | 0.9992 | macro_recall | 0.659473 | -33.9727 |
| Modelo proposto, fiel (profundidade 5) | recall | 0.9992 | weighted_recall | 0.977949 | -2.1251 |
| Modelo proposto, variante (profundidade variável) | auc | 0.9999 | roc_auc_ovr_macro | 0.993010 | -0.6890 |
| Modelo proposto, variante (profundidade variável) | auc | 0.9999 | roc_auc_ovr_macro_base_mean | 0.997276 | -0.2624 |
| Modelo proposto, variante (profundidade variável) | accuracy | 0.9998 | accuracy | 0.996359 | -0.3441 |
| Modelo proposto, variante (profundidade variável) | f1 | 0.9991 | macro_f1 | 0.965556 | -3.3544 |
| Modelo proposto, variante (profundidade variável) | f1 | 0.9991 | weighted_f1 | 0.996415 | -0.2685 |
| Modelo proposto, variante (profundidade variável) | precision | 0.9991 | macro_precision | 0.956511 | -4.2589 |
| Modelo proposto, variante (profundidade variável) | precision | 0.9991 | weighted_precision | 0.996503 | -0.2597 |
| Modelo proposto, variante (profundidade variável) | recall | 0.9992 | macro_recall | 0.975219 | -2.3981 |
| Modelo proposto, variante (profundidade variável) | recall | 0.9992 | weighted_recall | 0.996359 | -0.2841 |

Modelos de comparação mais de 5 pontos percentuais acima da sua linha na Tabela II (o limite é escolha nossa):

- **Árvore de decisão:** `roc_auc_ovr_macro` 0.9927 contra 0.8617 no artigo (+13.10 pp); `weighted_f1` 0.9775 contra 0.8197 no artigo (+15.78 pp); `macro_recall` 0.9641 contra 0.712 no artigo (+25.21 pp); `weighted_recall` 0.9723 contra 0.712 no artigo (+26.03 pp).

Uma diferença desse tamanho, para cima, é indício de que o modelo do artigo foi treinado com uma configuração diferente da que a Tabela II informa. Qual é a diferença não foi medido, e a configuração daqui não foi ajustada para aproximar o resultado.

## Tabela II, metade inferior: resultados da literatura

Valores copiados do artigo como impressos, com a referência que ele cita em
cada linha; "–" é célula que o artigo deixa vazia. A última linha está impressa
em percentual e as outras em fração. O artigo declara que o método experimental
desses trabalhos não é diretamente comparável ao dele (Seção V); eles não foram
reproduzidos aqui.

| modelo | AUC | acurácia | F1 | precisão | recall | escala |
| --- | --- | --- | --- | --- | --- | --- |
| Decision Tree [10] | 0.998 | 0.998 | 0.998 | 0.998 | 0.999 | fração |
| Gradient Boosting(XGB) [10] | 1 | 0.999 | 1 | 1 | 1 | fração |
| Random Forest [10] | 1 | 0.998 | 0.997 | 0.999 | 0.998 | fração |
| Decision Tree [12] | – | 0.999715 | – | – | – | fração |
| Random Forest [12] | – | 0.999802 | – | – | – | fração |
| Decision Tree [22] | – | 0.993 | – | 0.992 | 0.993 | fração |
| Gradient Boosting(XGB) [22] | – | 0.951 | – | 0.957 | 0.951 | fração |
| Random Forest [22] | – | 99.5 | – | 99.4 | 99.6 | percentual |

## Cada modelo de comparação no teste

### Árvore de decisão

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 86088 | 2824 | 69 |
| Benign-DoH | 129 | 1841 | 5 |
| Malicious-DoH | 120 | 63 | 24772 |

- **Recall de Malicious-DoH 99.2667%.** De 24955 fluxos de
  túnel no teste, 183 são classificados em outra classe: passam sem alerta.
- **FPR de Malicious-DoH contra o resto 0.0814%.** 74 de
  90956 fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de 95%:
  de 0.0639% a 0.1021%.
- **Recall de Benign-DoH 93.2152% e precisão 38.9382%.** É a
  classe menor, com 1975 fluxos no teste; o erro nela quase não
  aparece na acurácia (97.2306%) nem na média ponderada.
- **F1 macro 84.2075% e F1 ponderado 97.7452%.** A média
  macro pesa as três classes por igual; a ponderada pesa pelo suporte.
- **AUC-ROC one-vs-rest macro 0.992682.** Não depende do limiar
  de decisão.

### XGBoost

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88282 | 698 | 1 |
| Benign-DoH | 100 | 1875 | 0 |
| Malicious-DoH | 2 | 0 | 24953 |

- **Recall de Malicious-DoH 99.9920%.** De 24955 fluxos de
  túnel no teste, 2 são classificados em outra classe: passam sem alerta.
- **FPR de Malicious-DoH contra o resto 0.0011%.** 1 de
  90956 fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de 95%:
  de 0.0000% a 0.0061%.
- **Recall de Benign-DoH 94.9367% e precisão 72.8721%.** É a
  classe menor, com 1975 fluxos no teste; o erro nela quase não
  aparece na acurácia (99.3090%) nem na média ponderada.
- **F1 macro 93.9987% e F1 ponderado 99.3531%.** A média
  macro pesa as três classes por igual; a ponderada pesa pelo suporte.
- **AUC-ROC one-vs-rest macro 0.998613.** Não depende do limiar
  de decisão.

### Random Forest

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88437 | 544 | 0 |
| Benign-DoH | 118 | 1856 | 1 |
| Malicious-DoH | 8 | 2 | 24945 |

- **Recall de Malicious-DoH 99.9599%.** De 24955 fluxos de
  túnel no teste, 10 são classificados em outra classe: passam sem alerta.
- **FPR de Malicious-DoH contra o resto 0.0011%.** 1 de
  90956 fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de 95%:
  de 0.0000% a 0.0061%.
- **Recall de Benign-DoH 93.9747% e precisão 77.2689%.** É a
  classe menor, com 1975 fluxos no teste; o erro nela quase não
  aparece na acurácia (99.4194%) nem na média ponderada.
- **F1 macro 94.8025% e F1 ponderado 99.4467%.** A média
  macro pesa as três classes por igual; a ponderada pesa pelo suporte.
- **AUC-ROC one-vs-rest macro 0.996580.** Não depende do limiar
  de decisão.

## O que não foi feito

- Nenhuma busca de hiperparâmetros: o artigo não a descreve para estes modelos.
- Não há validação cruzada dos modelos de comparação: a Tabela II só traz o teste.
- Os trabalhos da metade inferior da tabela não foram reproduzidos.
- Uma execução por modelo: a diferença entre o Random Forest e o modelo
  proposto não tem variância medida aqui.

## Onde os números diferem dos do artigo

O artigo não informa a seed, a lista dos atributos, a limpeza, o alvo e os
parâmetros do SMOTE, os hiperparâmetros além dos dois da Tabela II, a média das
métricas nem o cálculo da AUC; as versões das bibliotecas são outras. Qualquer
um desses pontos pode explicar uma diferença, e nenhum foi isolado aqui.
Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada para aproximar o
resultado.
