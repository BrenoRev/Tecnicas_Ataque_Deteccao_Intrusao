# E7: identificação da ferramenta de túnel (Seção VI-D e Fig. 9 do artigo)

Gerado por `scripts/e7_ferramenta.py`. Uma única execução de cada leitura, com a
seed 42: não há média nem desvio padrão.

## O método é leitura nossa

A Seção VI-D do artigo diz que o sistema identificou a ferramenta de túnel que
gerou o tráfego malicioso e dá um valor por ferramenta, que chama de
"accuracy": dns2tcp 99.2%, iodine 92.9%, dnscat2 91.3%. O artigo não diz que modelo produziu esses valores, com
que dados foi treinado, como o teste foi separado nem como a "accuracy" de uma
ferramenta foi calculada. Sem método descrito, o que se faz aqui é uma leitura:

- o mesmo sistema da reprodução (90% para treino e 10% para teste, com a
  mesma proporção de ferramentas; normalizador ajustado só no treino; 3
  subconjuntos; 3 Random Forests de 10 árvores; regressão logística),
  aplicado só aos fluxos maliciosos, com as três ferramentas como classes;
- nos subconjuntos, a ferramenta com mais fluxos no treino (dns2tcp) é
  dividida em 3 partes, a com menos (dnscat2) é aumentada com SMOTE até o
  tamanho da terceira (iodine), que entra inteira em cada subconjunto. É o
  que o sistema do artigo faz com Non-DoH, Benign-DoH e Malicious-DoH;
- o valor do artigo de cada ferramenta fica ao lado do recall, da precisão e do
  F1 dela, porque não se sabe a qual deles a "accuracy" corresponde. As classes
  são desbalanceadas, e a acurácia do conjunto sozinha mediria sobretudo o
  dns2tcp.

O sistema é treinado nas duas leituras de profundidade do artigo. A principal
é a de profundidade variável (linha 3 do Algoritmo 1); a de profundidade máxima
5 (Seção IV-B) vai ao lado.

## Dados

Fluxos de `MaliciousDoH-CSVs.zip` com a coluna `DoH` verdadeira; a ferramenta é
a pasta do arquivo. Limpeza: saem as linhas com valor ausente em algum
atributo, como na reprodução. O total depois da limpeza é o Malicious-DoH da
Tabela I do artigo (249553).

| ferramenta | fluxos no zip | depois da limpeza | treino | teste |
| --- | --- | --- | --- | --- |
| dns2tcp | 167486 | 167287 | 150558 | 16729 |
| dnscat2 | 35770 | 35742 | 32168 | 3574 |
| iodine | 46580 | 46524 | 41871 | 4653 |

## Leitura variante (profundidade variável)

Random Forests base: sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Números em `variante/ferramenta/seed42/metrics.json`;
tempos em `variante/ferramenta/seed42/run.json`.

Matriz de confusão no teste (24956 fluxos; linha é a ferramenta real):

| real \ predito | dns2tcp | dnscat2 | iodine |
| --- | --- | --- | --- |
| dns2tcp | 16444 | 188 | 97 |
| dnscat2 | 48 | 3325 | 201 |
| iodine | 21 | 319 | 4313 |

Ao lado da Seção VI-D do artigo:

| ferramenta | artigo ("accuracy") | fluxos no teste | recall | recall menos artigo (pp) | precisão | precisão menos artigo (pp) | F1 | F1 menos artigo (pp) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dns2tcp | 99.2% | 16729 | 98.30% | -0.90 | 99.58% | +0.38 | 98.94% | -0.26 |
| iodine | 92.9% | 4653 | 92.69% | -0.21 | 93.54% | +0.64 | 93.11% | +0.21 |
| dnscat2 | 91.3% | 3574 | 93.03% | +1.73 | 86.77% | -4.53 | 89.79% | -1.51 |

Acurácia no teste: 96.50%. Recall macro 94.67%, precisão
macro 93.30%, F1 macro 93.95%; F1 ponderado
96.54%. AUC-ROC one-vs-rest macro: 0.989360 pela saída do
meta-classificador e 0.996376 pela média das probabilidades
dos bases.

- **dns2tcp: recall 98.30%, precisão 99.58%.** Fluxos de dns2tcp no teste: 16729; atribuídos a outra ferramenta: 285 (188 a dnscat2, 97 a iodine).
- **dnscat2: recall 93.03%, precisão 86.77%.** Fluxos de dnscat2 no teste: 3574; atribuídos a outra ferramenta: 249 (48 a dns2tcp, 201 a iodine).
- **iodine: recall 92.69%, precisão 93.54%.** Fluxos de iodine no teste: 4653; atribuídos a outra ferramenta: 340 (21 a dns2tcp, 319 a dnscat2).

O erro aqui é de atribuição: quem investiga o alerta parte da ferramenta errada. A detecção do túnel não é medida, porque todos os fluxos do conjunto são maliciosos.



Recall de cada Random Forest base sozinho no teste, na ordem dos subconjuntos:
dns2tcp 98.06%, dnscat2 93.06%, iodine 92.84%; dns2tcp 98.13%, dnscat2 93.65%, iodine 92.86%; dns2tcp 98.04%, dnscat2 93.76%, iodine 92.99%.

Subconjuntos de treino (ferramentas na ordem dns2tcp, dnscat2, iodine):

| subconjunto | amostras por ferramenta | dnscat2 sintético |
| --- | --- | --- |
| 1 | [50186, 41871, 41871] | 23.17% |
| 2 | [50186, 41871, 41871] | 23.17% |
| 3 | [50186, 41871, 41871] | 23.17% |

5 das 24956 linhas do teste (0.02%) têm vetor de
29 atributos idêntico ao de alguma linha do treino. Para o modelo essas
linhas já foram vistas, e as métricas acima as incluem.

## Leitura fiel (profundidade 5)

Random Forests base: profundidade máxima 5 nos submodelos (Seção IV-B). Números em `fiel/ferramenta/seed42/metrics.json`;
tempos em `fiel/ferramenta/seed42/run.json`.

Matriz de confusão no teste (24956 fluxos; linha é a ferramenta real):

| real \ predito | dns2tcp | dnscat2 | iodine |
| --- | --- | --- | --- |
| dns2tcp | 15298 | 1299 | 132 |
| dnscat2 | 6 | 3467 | 101 |
| iodine | 25 | 1249 | 3379 |

Ao lado da Seção VI-D do artigo:

| ferramenta | artigo ("accuracy") | fluxos no teste | recall | recall menos artigo (pp) | precisão | precisão menos artigo (pp) | F1 | F1 menos artigo (pp) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dns2tcp | 99.2% | 16729 | 91.45% | -7.75 | 99.80% | +0.60 | 95.44% | -3.76 |
| iodine | 92.9% | 4653 | 72.62% | -20.28 | 93.55% | +0.65 | 81.77% | -11.13 |
| dnscat2 | 91.3% | 3574 | 97.01% | +5.71 | 57.64% | -33.66 | 72.31% | -18.99 |

Acurácia no teste: 88.73%. Recall macro 87.02%, precisão
macro 83.66%, F1 macro 83.17%; F1 ponderado
89.58%. AUC-ROC one-vs-rest macro: 0.954993 pela saída do
meta-classificador e 0.974931 pela média das probabilidades
dos bases.

- **dns2tcp: recall 91.45%, precisão 99.80%.** Fluxos de dns2tcp no teste: 16729; atribuídos a outra ferramenta: 1431 (1299 a dnscat2, 132 a iodine).
- **dnscat2: recall 97.01%, precisão 57.64%.** Fluxos de dnscat2 no teste: 3574; atribuídos a outra ferramenta: 107 (6 a dns2tcp, 101 a iodine).
- **iodine: recall 72.62%, precisão 93.55%.** Fluxos de iodine no teste: 4653; atribuídos a outra ferramenta: 1274 (25 a dns2tcp, 1249 a dnscat2).

O erro aqui é de atribuição: quem investiga o alerta parte da ferramenta errada. A detecção do túnel não é medida, porque todos os fluxos do conjunto são maliciosos.



Recall de cada Random Forest base sozinho no teste, na ordem dos subconjuntos:
dns2tcp 91.38%, dnscat2 97.17%, iodine 72.53%; dns2tcp 91.40%, dnscat2 97.23%, iodine 72.23%; dns2tcp 91.37%, dnscat2 97.17%, iodine 72.15%.

Subconjuntos de treino (ferramentas na ordem dns2tcp, dnscat2, iodine):

| subconjunto | amostras por ferramenta | dnscat2 sintético |
| --- | --- | --- |
| 1 | [50186, 41871, 41871] | 23.17% |
| 2 | [50186, 41871, 41871] | 23.17% |
| 3 | [50186, 41871, 41871] | 23.17% |

5 das 24956 linhas do teste (0.02%) têm vetor de
29 atributos idêntico ao de alguma linha do treino. Para o modelo essas
linhas já foram vistas, e as métricas acima as incluem.

## Figura equivalente à Fig. 9

`dados/fig9/seed42/fig9_distribuicao.png`, com os dados em `dados/fig9/seed42/fig9_curvas.csv` e
`dados/fig9/seed42/fig9_estatisticas.csv`. Os mesmos dois atributos da figura do artigo:

- (a) `ResponseTimeTimeSkewFromMode` (sem unidade), eixo de -10 a 10.
- (b) `PacketTimeVariance` (s²), eixo de 0 a 3000.

A Fig. 9 do artigo desenha, para cada ferramenta, uma curva normal com a média e
o desvio padrão escritos na legenda. A linha de cima da nossa figura repete esse
tipo de gráfico com a média e o desvio padrão medidos; a de baixo mostra o
histograma dos mesmos fluxos, em 100 intervalos. O eixo vertical do artigo é
"Frequency", sem dizer a escala; o nosso é densidade, e a altura das curvas não
é comparável à do artigo. A figura descreve os dados e usa todos os
249553 fluxos limpos, do treino e do teste; nenhum modelo é ajustado com ela.

| atributo | ferramenta | fluxos | média | desvio padrão | média no artigo | desvio padrão no artigo | fração no eixo | fração com -10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ResponseTimeTimeSkewFromMode | dns2tcp | 167287 | 1.09866 | 0.607149 | 1.09728 | 0.607949 | 100.00% | 0.10% |
| ResponseTimeTimeSkewFromMode | dnscat2 | 35742 | 0.504119 | 1.13847 | 0.504178 | 1.13836 | 100.00% | 0.75% |
| ResponseTimeTimeSkewFromMode | iodine | 46524 | 0.521273 | 1.08435 | 0.520797 | 1.08367 | 100.00% | 0.78% |
| PacketTimeVariance | dns2tcp | 167287 | 197.603 | 290.947 | 197.345 | 290.832 | 100.00% | – |
| PacketTimeVariance | dnscat2 | 35742 | 857.581 | 432.252 | 854.902 | 434.215 | 100.00% | – |
| PacketTimeVariance | iodine | 46524 | 880.865 | 429.092 | 879.466 | 430.179 | 100.00% | – |

O artigo afirma que o dns2tcp tem desvio padrão menor nos dois atributos. Medido:

- `ResponseTimeTimeSkewFromMode`: o menor desvio padrão é o de dns2tcp.
- `PacketTimeVariance`: o menor desvio padrão é o de dns2tcp.

`ResponseTimeTimeSkewFromMode` é uma coluna de assimetria, em que o extrator grava
-10 quando o desvio padrão do fluxo é zero. Fração dos fluxos com esse marcador:
dns2tcp 0.10%, dnscat2 0.75%, iodine 0.78%. O marcador entra na média e no desvio padrão da tabela, como
qualquer outro valor.

## O que não foi feito

- Validação cruzada: o artigo não mostra matriz de confusão para a Seção VI-D,
  e as métricas acima vêm só do teste.
- Outro classificador ou outro split: só a leitura descrita acima foi medida.
- Detecção: o conjunto só tem tráfego malicioso, então nada aqui mede falso
  positivo sobre tráfego legítimo.

## Onde os valores diferem dos do artigo

O artigo não informa o modelo, os dados de treino, o split, a seed nem a
definição de "accuracy" por ferramenta; as versões das bibliotecas são outras.
Qualquer um desses pontos pode explicar a diferença, e os dados não permitem
dizer qual. Nenhuma seed, hiperparâmetro, papel de ferramenta ou regra de
limpeza foi ajustado para aproximar o resultado.
