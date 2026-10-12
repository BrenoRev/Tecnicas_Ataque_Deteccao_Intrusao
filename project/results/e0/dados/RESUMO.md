# E0: dados do CIRA-CIC-DoHBrw-2020

Gerado por `scripts/e0_dados.py`. Os números vêm de `cira/seed42/metrics.json`
e dos arquivos CSV da mesma pasta.

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
