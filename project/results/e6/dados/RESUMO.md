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
sistema é aplicado sem mudar a entrada. Segundo, o HKD traz tráfego de túnel de
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
