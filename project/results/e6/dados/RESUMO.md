# E6, dados: segundo dataset

Gerado por `scripts/e6_dados.py`. Os números vêm dos arquivos `metrics.json` de
`hkd/seed42/`, `combinado/seed42/` e `combinado_sem_replicas/seed42/` e dos
arquivos CSV de `hkd/seed42/`.

## Fonte

- DoH-Tunnel-Traffic-HKD: `hkd/DoH-CSVs/DoH-CSVs-48h/Total-48h.csv`, com
  5258 fluxos, todos de túnel DoH.
  `hkd/Total-48h-Augmentation.csv` é lido só para a conferência das réplicas.
- Combinado CIRA-CIC-DoHBrw-2020 + DoH-Tunnel-Traffic-HKD: Non-DoH das linhas
  `NonDoH` de `combinado/l1-total-add.csv`, Benign-DoH das linhas `Benign` de
  `combinado/l2-total-add.csv` e Malicious-DoH de todas as linhas de
  `combinado/l3-total-add.csv`, que traz a ferramenta de túnel.

## Compatibilidade de colunas

Cabeçalho de cada arquivo comparado, pelo nome, com as 35
colunas do CIRA-CIC-DoHBrw-2020: 5 identificadores,
29 atributos e o rótulo. `missing` lista as colunas
esperadas que faltam e `unexpected`, as que sobram.

| arquivo | bom | columns | same_order | missing | unexpected |
| --- | --- | --- | --- | --- | --- |
| hkd/DoH-CSVs/DoH-CSVs-48h/Total-48h.csv | True | 35 | True | [] | [] |
| hkd/Total-48h-Augmentation.csv | True | 35 | True | [] | [] |
| combinado/l1-total-add.csv | False | 35 | True | [] | [] |
| combinado/l2-total-add.csv | False | 35 | True | [] | [] |
| combinado/l3-total-add.csv | True | 35 | True | [] | [] |

Diferenças de formato, sem efeito nos atributos:

- `bom` diz se o arquivo começa com a marca de ordem de bytes do UTF-8. A
  leitura a descarta nos arquivos que a têm.
- Em `Total-48h.csv`, os atributos ['FlowBytesSent', 'FlowBytesReceived', 'PacketLengthMode'] só têm
  valores inteiros. A carga converte os 29 atributos para decimal.
- Os identificadores do fluxo não são copiados para as tabelas gravadas.

## Fluxos por classe, origem e ferramenta

"Bruto" é o que a carga lê, "removidas" o que a limpeza tira e "limpo" o que é
gravado. A limpeza é a mesma do CIRA: sai a linha com valor ausente em algum
dos 29 atributos. A coluna do README traz as contagens que o `README.txt` do
dataset combinado informa.

| classe | README do combinado | hkd, bruto | hkd, removidas | hkd, limpo | combinado, bruto | combinado, removidas | combinado, limpo | combinado_sem_replicas, bruto | combinado_sem_replicas, removidas | combinado_sem_replicas, limpo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Non-DoH | 897493 | 0 | 0 | 0 | 897493 | 7684 | 889809 | 897493 | 7684 | 889809 |
| Benign-DoH | 19807 | 0 | 0 | 0 | 19807 | 61 | 19746 | 19807 | 61 | 19746 |
| Malicious-DoH | 354996 | 5258 | 0 | 5258 | 354996 | 283 | 354713 | 255094 | 283 | 254811 |

| ferramenta | origem | README do combinado | hkd, bruto | hkd, limpo | combinado, bruto | combinado, limpo | combinado_sem_replicas, bruto | combinado_sem_replicas, limpo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dns2tcp | CIRA | 167486 | 0 | 0 | 167486 | 167287 | 167486 | 167287 |
| dnscat2 | CIRA | 35770 | 0 | 0 | 35770 | 35742 | 35770 | 35742 |
| iodine | CIRA | 46580 | 0 | 0 | 46580 | 46524 | 46580 | 46524 |
| dnstt | HKD | 46080 | 2304 | 2304 | 46080 | 46080 | 2304 | 2304 |
| tcp-over-dns | HKD | 30040 | 1502 | 1502 | 30040 | 30040 | 1502 | 1502 |
| tuns | HKD | 29040 | 1452 | 1452 | 29040 | 29040 | 1452 | 1452 |

- O combinado bruto tem as contagens do README, por classe e por ferramenta.
- Valores ausentes no combinado, por coluna: {'ResponseTimeTimeMedian': 8028, 'ResponseTimeTimeSkewFromMedian': 8028}. No
  HKD: {}. Valores infinitos: 0
  no combinado e 0 no HKD.
- Todas as linhas removidas são do CIRA. Depois da limpeza, a parte do CIRA
  dentro do combinado tem [889809, 19746, 249553] fluxos por
  classe; a Tabela I do artigo tem [889809, 19746, 249553].

Combinado sem réplicas, limpo, por origem:

| classe | CIRA | HKD |
| --- | --- | --- |
| Non-DoH | 889809 | 0 |
| Benign-DoH | 19746 | 0 |
| Malicious-DoH | 249553 | 5258 |

## Réplicas do HKD

- `Total-48h-Augmentation.csv`: 105160 linhas,
  5258 fluxos distintos, cada um
  exatamente 20 vezes.
- Linhas das ferramentas do HKD em `l3-total-add.csv`: 105160,
  5258 fluxos distintos, cada um exatamente
  20 vezes.
- Nos dois arquivos, os fluxos distintos são os de `Total-48h.csv`: mesma
  ferramenta e maior diferença absoluta em um atributo de
  5.0e-08, que é arredondamento.
- `combinado_sem_replicas` fica com a primeira linha de cada fluxo do HKD:
  saem 99902 linhas, todas da classe Malicious-DoH, que
  passa de 354996 para 255094 fluxos antes
  da limpeza. As linhas do CIRA ficam todas, inclusive as repetidas.

## HKD ao lado do tráfego malicioso do CIRA

Descrição dos conjuntos inteiros, sem separar treino e teste e sem normalizar;
nenhum modelo é ajustado aqui. Os fluxos do CIRA são os do combinado limpo.

- Máquinas do HKD: ['192.168.11.12', '192.168.11.16']. Em
  5258 dos 5258
  fluxos, origem e destino são máquinas diferentes dessa lista. Captura de
  2021-10-27 a 2021-11-04.
- Mediana de quatro atributos; os 29 estão em `hkd/seed42/medianas_malicioso.csv`:

| atributo | CIRA, Malicious-DoH | HKD |
| --- | --- | --- |
| Duration | 34.071709 | 120.0644985 |
| FlowBytesSent | 1807.0 | 21375.0 |
| FlowBytesReceived | 4896.0 | 21723.5 |
| PacketLengthMean | 223.4333333 | 148.56124605 |

- Faixa de valores de cada atributo, em `hkd/seed42/faixa_por_atributo.csv`. A
  faixa do CIRA é a dos fluxos limpos das três classes. Atributos em que algum
  fluxo do HKD fica abaixo do mínimo ou acima do máximo do CIRA:

Nenhum.

## `PacketLengthMode` no CIRA e no HKD

Moda do comprimento dos pacotes de cada fluxo, nos conjuntos limpos inteiros,
sem separar treino e teste e sem normalizar. Os fluxos do CIRA são os do
combinado limpo e os do HKD, os de `Total-48h.csv`.

| origem e classe | fluxos | valores distintos | os 5 valores mais frequentes (fração dos fluxos) |
| --- | --- | --- | --- |
| CIRA, Non-DoH | 889809 | 237 | 54 (33.57%), 66 (28.09%), 55 (22.63%), 1514 (5.56%), 60 (3.18%) |
| CIRA, Benign-DoH | 19746 | 14 | 66 (50.70%), 105 (22.12%), 54 (12.21%), 60 (7.95%), 74 (2.03%) |
| CIRA, Malicious-DoH | 249553 | 20 | 68 (88.09%), 56 (7.56%), 62 (2.20%), 87 (1.99%), 165 (0.10%) |
| HKD, Malicious-DoH | 5258 | 2 | 66 (99.90%), 285 (0.10%) |

No CIRA limpo inteiro, os valores {56, 62, 68, 87} de `PacketLengthMode` cobrem 99.84% dos 249553 fluxos Malicious-DoH e ocorrem em 1 dos 909555 fluxos legítimos (Non-DoH e Benign-DoH). A regra de um só atributo que chama de malicioso o fluxo com `PacketLengthMode` nesse conjunto tem, no mesmo CIRA de onde os valores foram tirados, recall de 99.84% e 1 falso positivo em 909555 (FPR de 0.0001%). Nos 5258 fluxos do HKD ela detecta 0 (0.00%): 0.00% dos fluxos do HKD têm um valor de `PacketLengthMode` que ocorre no Malicious-DoH do CIRA. O valor mais frequente no HKD, 66 (99.90% dos fluxos), é, no CIRA, o de 28.09% dos fluxos Non-DoH, 50.70% dos fluxos Benign-DoH, 0.00% dos fluxos Malicious-DoH.

- **Critério da regra.** Entram os valores que cobrem ao menos
  1% dos fluxos Malicious-DoH do CIRA e no máximo
  0.01% dos fluxos legítimos. Os dois limites são escolha
  nossa; os valores saem dos dados.
- **O que isso mede.** A regra é tirada do CIRA inteiro e medida nele mesmo:
  descreve os dados, não é um modelo avaliado em teste. Ela mostra que, no
  CIRA, um só atributo separa quase todo o tráfego malicioso do legítimo, e
  que essa separação não vale para os fluxos do HKD.
- **O que não foi medido.** A causa da diferença. Hipótese, não medida: a moda
  do comprimento do pacote depende de como cada captura gravou os pacotes (por
  exemplo, o cabeçalho de enlace ou as opções do TCP), e não só da ferramenta
  de túnel. Nenhum arquivo de captura foi examinado.

## Fluxos do HKD no teste do combinado sem réplicas ao lado do treino

Split do retreino do sistema: seed 42, fração de teste
0.1. Para cada um dos 513 fluxos do HKD no teste, a
distância euclidiana, nos 29 atributos normalizados pelo scaler do treino, até
o mais próximo dos 4745 fluxos do HKD no treino e até o mais próximo dos
224585 fluxos Malicious-DoH do CIRA no treino. Cada atributo
normalizado vai de 0 a 1 no treino.

| distância | mínimo | 1º quartil | mediana | 3º quartil | máximo |
| --- | --- | --- | --- | --- | --- |
| ao fluxo do HKD mais próximo no treino | 0.000008 | 0.000978 | 0.002571 | 0.006485 | 0.214349 |
| ao fluxo Malicious-DoH do CIRA mais próximo no treino | 0.017216 | 0.025584 | 0.051449 | 0.070082 | 0.197388 |

| ferramenta | fluxos no teste | mediana ao HKD do treino | mediana ao malicioso do CIRA do treino |
| --- | --- | --- | --- |
| dnstt | 232 | 0.003373 | 0.061047 |
| tcp-over-dns | 142 | 0.007081 | 0.070669 |
| tuns | 139 | 0.000056 | 0.021812 |

Em 505 dos 513 fluxos
(98.44%), o fluxo do HKD mais próximo no treino está
mais perto que qualquer fluxo malicioso do CIRA. A mediana da distância ao HKD do
treino é 5.00% da mediana da distância ao malicioso do CIRA.
Nenhum fluxo do HKD no teste é cópia exata de um do treino; a medida diz o
quanto os que não são cópia ficam perto. Ela não separa fluxos da mesma sessão
de túnel, porque as tabelas não trazem a sessão.

## Justificativa da escolha do segundo dataset

**Quais dados.** O segundo dataset é o combinado CIRA-CIC-DoHBrw-2020 +
DoH-Tunnel-Traffic-HKD, publicado pelos autores do HKD, na forma sem réplicas:
1164366 fluxos depois da limpeza, [889809, 19746, 254811] por
classe (Non-DoH, Benign-DoH, Malicious-DoH). Ao lado dele ficam o combinado como publicado
(1264268 fluxos) e o HKD sozinho
(5258 fluxos).

**Por que foram escolhidos.** Primeiro, os atributos são os mesmos do dataset do
artigo: os cinco arquivos lidos têm as 35 colunas do
CIRA-CIC-DoHBrw-2020, com os mesmos nomes e na mesma ordem, e o `README.txt` do
HKD informa que os atributos foram extraídos das capturas com o DoHLyzer. O
sistema recebe as mesmas 29 colunas. Colunas iguais não garantem valores
comparáveis entre as duas capturas: em `PacketLengthMode`,
0.00% dos fluxos do HKD têm um valor que ocorre no
tráfego malicioso do CIRA (seção `PacketLengthMode` acima). Segundo, o HKD traz tráfego de túnel de
três ferramentas que o CIRA não tem (dnstt, tcp-over-dns, tuns), capturado em
outras máquinas, de 2021-10-27 a 2021-11-04; as máquinas e
o período do CIRA estão em `results/e0/dados/RESUMO.md`. Terceiro, o
combinado é o único dos dois com as três classes: o HKD sozinho só tem a classe
Malicious-DoH e não permite treinar o sistema; ele serve para avaliar, nas
ferramentas novas, o sistema treinado no CIRA.

**O que representam, e as ressalvas.** No combinado sem réplicas, o tráfego novo
são 5258 fluxos do HKD, todos na classe
Malicious-DoH. Os fluxos Non-DoH e Benign-DoH vêm do CIRA, porque o HKD só tem
tráfego de túnel: depois da limpeza, a parte do CIRA dentro do combinado tem as
contagens por classe da Tabela I do artigo. O segundo dataset difere do
primeiro, portanto, só na classe maliciosa. O combinado como publicado repete
cada fluxo do HKD 20 vezes; o `README.txt` do HKD
descreve o arquivo de origem como "augmented assuming 20 client PCs". Com as
réplicas, uma separação aleatória entre treino e teste põe cópias do mesmo fluxo
nos dois lados, e o teste mediria, nas ferramentas novas, fluxos que o modelo já
viu no treino. Por isso o sistema é treinado e avaliado na forma sem réplicas, e
a forma publicada fica ao lado, para comparação.

## Arquivos gerados

Em `data/processed/`, com os 29 atributos, `label`, `origin` e `tool`:

- `hkd.parquet`, SHA-256 `86a363f2f07d7b88130dd2eecc43ae601638a108abe6d2bae2590eddd45a4779`;
- `combinado.parquet`, SHA-256 `fe3acba6240f9a35fa7c8ed4ebf91b9fa1dcea6f62a9c4b4e3d02ebec676754c`;
- `combinado_sem_replicas.parquet`, SHA-256 `624c21216525d5b54075b9442e55b7b3f75aaead8ba4b6f0578c08132648890e`.
