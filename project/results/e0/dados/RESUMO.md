# E0: dados do CIRA-CIC-DoHBrw-2020

Gerado por `scripts/e0_dados.py`. Os números vêm de `cira/seed42/metrics.json`,
de `cira/seed42/split_counts.json` e dos arquivos CSV da mesma pasta.

## Fonte

Membros `l1-nondoh.csv`, `l2-benign.csv`, `l2-malicious.csv` de
`Total_CSVs.zip`, lidos direto do zip. O membro `l1-doh.csv` não é lido: ele
repete os fluxos dos dois arquivos `l2`. Fluxos brutos por classe
(Non-DoH, Benign-DoH, Malicious-DoH): [897493, 19807, 249836], total 1167136.

## Regras de limpeza ao lado da Tabela I

Tabela I do artigo: [889809, 19746, 249553]. As três primeiras colunas numéricas são
os fluxos que ficam; "removidas" são os que saem; "diferença" é o que fica
menos a Tabela I.

| regra | Non-DoH | Benign-DoH | Malicious-DoH | removidas Non-DoH | removidas Benign-DoH | removidas Malicious-DoH | diferença Non-DoH | diferença Benign-DoH | diferença Malicious-DoH |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nenhuma (bruto) | 897493 | 19807 | 249836 | 0 | 0 | 0 | 7684 | 61 | 283 |
| NaN | 889809 | 19746 | 249553 | 7684 | 61 | 283 | 0 | 0 | 0 |
| infinito | 897493 | 19807 | 249836 | 0 | 0 | 0 | 7684 | 61 | 283 |
| duplicatas exatas | 897493 | 19807 | 249836 | 0 | 0 | 0 | 7684 | 61 | 283 |
| duplicatas nos 29 atributos | 753560 | 18804 | 249712 | 143933 | 1003 | 124 | -136249 | -942 | 159 |
| NaN e infinito | 889809 | 19746 | 249553 | 7684 | 61 | 283 | 0 | 0 | 0 |
| NaN e duplicatas exatas | 889809 | 19746 | 249553 | 7684 | 61 | 283 | 0 | 0 | 0 |
| NaN e duplicatas nos 29 atributos | 750456 | 18797 | 249538 | 147037 | 1010 | 298 | -139353 | -949 | -15 |
| NaN, infinito e duplicatas exatas | 889809 | 19746 | 249553 | 7684 | 61 | 283 | 0 | 0 | 0 |
| NaN, infinito e duplicatas nos 29 atributos | 750456 | 18797 | 249538 | 147037 | 1010 | 298 | -139353 | -949 | -15 |

Regra adotada: remover as linhas com `NaN` em algum dos 29 atributos, e só
isso. Diferença para a Tabela I: [0, 0, 0].
Regras com diferença zero nas três classes: ['NaN', 'NaN e infinito', 'NaN e duplicatas exatas', 'NaN, infinito e duplicatas exatas'].
O artigo não descreve a limpeza; a regra adotada é a mais simples entre as que
chegam às contagens publicadas. Valores ausentes por coluna, no bruto:
{'ResponseTimeTimeMedian': 8028, 'ResponseTimeTimeSkewFromMedian': 8028}.

## O que fica no conjunto limpo

- Fluxos por classe: [889809, 19746, 249553], total 1159108.
- Linhas cujo vetor de 29 atributos repete o de uma linha anterior:
  [139353, 949, 15]. Elas não são removidas: removê-las
  é a regra "NaN e duplicatas nos 29 atributos" da tabela acima.
- Vetores de 29 atributos presentes em mais de uma classe:
  326.
- Linhas com o valor -10 em alguma coluna de assimetria:
  298766. O extrator DoHLyzer grava esse
  valor quando o desvio padrão é zero. Por coluna e por classe:

| coluna | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| PacketLengthSkewFromMedian | 312 | 0 | 4616 |
| PacketLengthSkewFromMode | 312 | 0 | 4616 |
| PacketTimeSkewFromMedian | 0 | 0 | 0 |
| PacketTimeSkewFromMode | 0 | 0 | 0 |
| ResponseTimeTimeSkewFromMedian | 290123 | 3547 | 804 |
| ResponseTimeTimeSkewFromMode | 290123 | 3547 | 804 |

## Máquinas e período de captura

Medido no conjunto limpo, antes de os identificadores serem descartados. A
máquina é o endereço da rede local que aparece na origem ou no destino do fluxo.

| classe | máquinas | dias | primeiro dia | último dia |
| --- | --- | --- | --- | --- |
| Non-DoH | 4 | 13 | 2019-12-09 | 2020-01-14 |
| Benign-DoH | 4 | 13 | 2019-12-09 | 2020-01-14 |
| Malicious-DoH | 10 | 15 | 2020-03-18 | 2020-04-01 |

| máquina | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| 192.168.20.111 | 217432 | 12300 | 0 |
| 192.168.20.112 | 88235 | 1335 | 0 |
| 192.168.20.113 | 47457 | 2580 | 0 |
| 192.168.20.144 | 0 | 0 | 73632 |
| 192.168.20.191 | 536685 | 3531 | 0 |
| 192.168.20.204 | 0 | 0 | 28674 |
| 192.168.20.205 | 0 | 0 | 19215 |
| 192.168.20.206 | 0 | 0 | 19037 |
| 192.168.20.207 | 0 | 0 | 18899 |
| 192.168.20.208 | 0 | 0 | 18451 |
| 192.168.20.209 | 0 | 0 | 18376 |
| 192.168.20.210 | 0 | 0 | 17977 |
| 192.168.20.211 | 0 | 0 | 18132 |
| 192.168.20.212 | 0 | 0 | 17160 |

Máquinas em que há fluxo malicioso e também fluxo de outra classe:
0. Dias em que há fluxo malicioso e
também fluxo de outra classe: 0.

## Arquivo gerado

`data/processed/cira.parquet`, com os 29 atributos, `label` e `group`.
SHA-256: `7085c3d27dd67d7c0560b9bc4549168852f390838be7f0e1018bde7b99375de3`.

## Treino, validação e teste

Gerado de `cira/seed42/split_counts.json`. Sorteio estratificado por classe,
seed 42, fração de teste 0.1. Treino:
1043197 fluxos; teste: 115911.

| classe | treino | Fig. 4a | diferença no treino | teste | Fig. 4b | diferença no teste |
| --- | --- | --- | --- | --- | --- | --- |
| Non-DoH | 800828 | 800829 | -1 | 88981 | 88980 | 1 |
| Benign-DoH | 17771 | 17771 | 0 | 1975 | 1975 | 0 |
| Malicious-DoH | 224598 | 224598 | 0 | 24955 | 24955 | 0 |

As matrizes da Fig. 4 somam 1043198 fluxos no treino e
115910 no teste. A fração 0.1 de 1159108
fluxos não é um número inteiro, e a biblioteca arredonda o tamanho do teste
para cima: o teste fica com 115911 fluxos, e o fluxo que passa do
treino para o teste é Non-DoH. O tamanho não é forçado para igualar a figura.

### Validação

O artigo não tem conjunto de validação separado: a validação é cruzada, com
10 folds estratificados sorteados só dentro do treino
(embaralhamento: True, seed 42). O teste não entra
em nenhum fold. Amostras por classe no fold de validação de cada rodada:

| fold | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| 1 | 80083 | 1777 | 22460 |
| 2 | 80083 | 1777 | 22460 |
| 3 | 80083 | 1777 | 22460 |
| 4 | 80083 | 1777 | 22460 |
| 5 | 80083 | 1777 | 22460 |
| 6 | 80083 | 1777 | 22460 |
| 7 | 80083 | 1778 | 22459 |
| 8 | 80083 | 1777 | 22459 |
| 9 | 80082 | 1777 | 22460 |
| 10 | 80082 | 1777 | 22460 |

### Teste com vetor de atributos presente no treino

Linhas do teste cujos 29 atributos são iguais aos de alguma linha do treino:
15842 de 115911 (13.67%). Os índices
de treino e teste são disjuntos; o que se repete é o vetor de atributos, porque
o conjunto limpo mantém as linhas repetidas. "Com o mesmo rótulo" conta a linha
do teste cujo vetor está no treino com a classe dela; "com outro rótulo", a que
tem o vetor no treino com classe diferente; "com os dois", a que está nos dois
casos.

| classe | linhas do teste | vetor presente no treino | fração | com o mesmo rótulo | com outro rótulo | com os dois |
| --- | --- | --- | --- | --- | --- | --- |
| Non-DoH | 88981 | 15733 | 17.68% | 15722 | 2358 | 2347 |
| Benign-DoH | 1975 | 107 | 5.42% | 82 | 48 | 23 |
| Malicious-DoH | 24955 | 2 | 0.01% | 2 | 0 | 0 |

### Teste normalizado

O normalizador é ajustado só no treino. No teste normalizado,
3 valores em 3 linhas ficam fora do
intervalo de 0 a 1, nas colunas {'FlowSentRate': 1, 'PacketLengthMean': 1, 'ResponseTimeTimeCoefficientofVariation': 1}.

## Fig. 2: densidade por classe

Figura em `cira/seed42/fig2_densidade.png`, com as curvas desenhadas em
`cira/seed42/fig2_densidade.csv` e os números desta seção em
`cira/seed42/fig2_faixa.csv`. Medida no conjunto limpo inteiro, antes de separar
treino e teste e sem normalizar. Nenhum fluxo é sorteado.

Como a Fig. 2 do artigo, a figura tem três painéis, um por atributo, e uma curva
por classe, estimada com núcleo gaussiano (KDE) e a largura de banda padrão do
SciPy, em 400 pontos do eixo. Cada classe é estimada sozinha: a
área de cada curva é 1. As faixas dos eixos foram lidas na figura do artigo, que
não diz como recortou os dados nem que largura de banda usou:

| atributo | unidade | faixa do eixo | eixo |
| --- | --- | --- | --- |
| FlowBytesReceived | bytes | 0 a 17500 | linear |
| PacketLengthMean | bytes | 0 a 800 | linear |
| PacketLengthVariance | bytes² | 10 a 1000000 | logarítmico |

A densidade usa só os fluxos dentro da faixa do eixo; "fração na faixa" diz
quantos são. Fluxo com variância zero fica fora do terceiro painel, porque o
eixo é logarítmico. Nesse painel a densidade é estimada sobre o logaritmo de
base 10 da variância. "Pico da densidade" é o valor do atributo em que a curva
da classe é mais alta. Os quartis são do atributo em todos os fluxos da classe,
dentro e fora da faixa.

| atributo | classe | fluxos | fluxos na faixa | fração na faixa | pico da densidade | 1º quartil | mediana | 3º quartil |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FlowBytesReceived | Non-DoH | 889809 | 767716 | 86.28% | 131.579 | 108 | 2839 | 6929 |
| FlowBytesReceived | Benign-DoH | 19746 | 17367 | 87.95% | 263.158 | 327 | 1295 | 5785 |
| FlowBytesReceived | Malicious-DoH | 249553 | 174488 | 69.92% | 4868.42 | 4169 | 4896 | 34055 |
| PacketLengthMean | Non-DoH | 889809 | 805917 | 90.57% | 62.1554 | 60.5 | 227.147 | 393.889 |
| PacketLengthMean | Benign-DoH | 19746 | 19746 | 100.00% | 88.2206 | 87.2222 | 116.522 | 153.78 |
| PacketLengthMean | Malicious-DoH | 249553 | 249553 | 100.00% | 224.561 | 150.158 | 223.433 | 248.864 |
| PacketLengthVariance | Non-DoH | 889809 | 787095 | 88.46% | 29.9358 | 30.25 | 115512 | 399280 |
| PacketLengthVariance | Benign-DoH | 19746 | 19559 | 99.05% | 379.269 | 372.49 | 3741.21 | 20192.3 |
| PacketLengthVariance | Malicious-DoH | 249553 | 237443 | 95.15% | 140563 | 15544.8 | 141409 | 182528 |

O que o artigo afirma (Seção III-A e legenda da Fig. 2), para ler ao lado da
tabela:

- (a) o número de bytes enviados ou recebidos é maior no Malicious-DoH do que no
  Non-DoH e no Benign-DoH. Comparar as linhas de `FlowBytesReceived`.
- (b) e (c) os fluxos DoH têm comprimento de pacote mais regular, com variância
  menor que a dos Non-DoH, o que a figura do artigo mostra como uma curva
  estreita para o Malicious-DoH. Comparar o primeiro e o terceiro quartis de
  `PacketLengthVariance`.
- A variância do Malicious-DoH é sempre relativamente alta, ao contrário da do
  Benign-DoH. Comparar o primeiro quartil de `PacketLengthVariance` das duas
  classes.

### Veredito por afirmação

Cada afirmação é confrontada com a mediana, ou com o primeiro quartil, do
atributo em todos os fluxos de cada classe, lidos da tabela acima. É uma
comparação de dois números, não um teste estatístico, e não olha a forma das
curvas.

- **Afirmação: (a) os bytes recebidos são mais no Malicious-DoH do que no Non-DoH e no Benign-DoH.**
  - mediana de `FlowBytesReceived`: 4896 no Malicious-DoH, maior que 2839 no Non-DoH. O número sustenta a afirmação para o Malicious-DoH diante do Non-DoH.
  - mediana de `FlowBytesReceived`: 4896 no Malicious-DoH, maior que 1295 no Benign-DoH. O número sustenta a afirmação para o Malicious-DoH diante do Benign-DoH.
- **Afirmação: (b) e (c) os fluxos DoH têm variância do comprimento de pacote menor que a dos Non-DoH.**
  - mediana de `PacketLengthVariance`: 3741.21 no Benign-DoH, menor que 115512 no Non-DoH. O número sustenta a afirmação para o Benign-DoH diante do Non-DoH.
  - mediana de `PacketLengthVariance`: 141409 no Malicious-DoH, maior que 115512 no Non-DoH. O número não sustenta a afirmação para o Malicious-DoH diante do Non-DoH.
- **Afirmação: a variância do Malicious-DoH é sempre relativamente alta, ao contrário da do Benign-DoH.**
  - 1º quartil de `PacketLengthVariance`: 15544.8 no Malicious-DoH, maior que 372.49 no Benign-DoH. O número sustenta a afirmação para o Malicious-DoH diante do Benign-DoH.
