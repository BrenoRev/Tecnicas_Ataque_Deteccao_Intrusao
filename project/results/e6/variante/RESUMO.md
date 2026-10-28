# E6: o sistema do artigo no segundo dataset, variante (profundidade variável)

Gerado por `scripts/e6_resumo.py`. Os números vêm dos arquivos `metrics.json`
de `transferencia/seed42/`, `retreino_sem_replicas/seed42/` e
`retreino_publicado/seed42/`; os tempos estão nos `run.json`.
Random Forests base: sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Os cenários das duas leituras
estão lado a lado, com o CIRA, em `../RESUMO.md`; a hipótese escrita antes da
execução, em `../fiel/HIPOTESE.md`.
Uma única execução de cada cenário, com a seed 42: não há média nem desvio
padrão. Classes na ordem dos códigos: Non-DoH, Benign-DoH, Malicious-DoH.

## O que cada cenário usa

- O DoH-Tunnel-Traffic-HKD sozinho só tem a classe maliciosa (dnstt,
  tcp-over-dns e tuns): não permite treinar o sistema de três classes. Ele
  entra de duas formas: como teste, na transferência, e dentro do dataset
  combinado CIRA + HKD, nos retreinos.
- No combinado, Non-DoH e Benign-DoH são os fluxos do CIRA. O "outro dataset"
  só é novo na classe maliciosa: métricas gerais perto das do CIRA são
  esperadas e não medem generalização.
- No combinado como publicado, cada fluxo do HKD aparece 20 vezes. O dataset
  principal desta etapa é o combinado sem réplicas, com cada fluxo do HKD uma
  única vez; o publicado vai ao lado.

## Transferência: treino no CIRA, avaliação no HKD

O sistema é ajustado só com o treino do CIRA (1043197 fluxos) e
prediz os 5258 fluxos do HKD, normalizados com o scaler do treino do
CIRA. O HKD só tem a classe maliciosa e não permite treinar o sistema: neste
cenário tudo é teste, não há treino nem validação com fluxos do HKD.

Sem fluxo legítimo no conjunto não há falso positivo: precisão, FPR e acurácia
não são calculados. A medida é o recall de Malicious-DoH.

| fluxos de túnel | n | detectados | recall | intervalo de confiança de 95% | erros para Non-DoH | erros para Benign-DoH |
| --- | --- | --- | --- | --- | --- | --- |
| HKD, as três ferramentas | 5258 | 95 | 1.81% | 1.46% a 2.20% | 1265 | 3898 |
| dnstt | 2304 | 0 | 0.00% | 0.00% a 0.16% | 575 | 1729 |
| tcp-over-dns | 1502 | 5 | 0.33% | 0.11% a 0.78% | 601 | 896 |
| tuns | 1452 | 90 | 6.20% | 5.01% a 7.56% | 89 | 1273 |

- **Recall de Malicious-DoH no HKD: 1.81%.** De 5258 túneis de
  ferramentas que o sistema nunca viu, 5163 passam sem alerta. É
  menor que o recall de Malicious-DoH no teste do CIRA na mesma
  leitura (99.96%, em `results/e1/`).
- **Destino dos erros: 1265 para Non-DoH e
  3898 para Benign-DoH.** O erro para Non-DoH trata o túnel como
  HTTPS comum; o erro para Benign-DoH, como DoH legítimo. Nos dois o operador
  não recebe alerta.
- **Valores normalizados fora de [0, 1] no HKD: 0 valores em 0 fluxos.** No teste do
  CIRA, com o mesmo scaler: 3 valores em 3 fluxos (`FlowSentRate` 1, `PacketLengthMean` 1, `ResponseTimeTimeCoefficientofVariation` 1).
  Nenhum atributo do HKD sai da faixa do treino do CIRA: a diferença entre os dois conjuntos é de posição dentro da faixa (medianas em `../dados/hkd/seed42/medianas_malicioso.csv`), e não de faixa.

### `PacketLengthMode` nos fluxos do HKD

Medido pela etapa de dados nos conjuntos limpos inteiros
(`../dados/hkd/seed42/metrics.json`, com a tabela em `../dados/RESUMO.md`).
No CIRA limpo inteiro, os valores {56, 62, 68, 87} de `PacketLengthMode` cobrem 99.84% dos 249553 fluxos Malicious-DoH e ocorrem em 1 dos 909555 fluxos legítimos (Non-DoH e Benign-DoH). A regra de um só atributo que chama de malicioso o fluxo com `PacketLengthMode` nesse conjunto tem, no mesmo CIRA de onde os valores foram tirados, recall de 99.84% e 1 falso positivo em 909555 (FPR de 0.0001%). Nos 5258 fluxos do HKD ela detecta 0 (0.00%): 0.00% dos fluxos do HKD têm um valor de `PacketLengthMode` que ocorre no Malicious-DoH do CIRA. O valor mais frequente no HKD, 66 (99.90% dos fluxos), é, no CIRA, o de 28.09% dos fluxos Non-DoH, 50.70% dos fluxos Benign-DoH, 0.00% dos fluxos Malicious-DoH.

- **Ao lado do sistema.** O recall do sistema na transferência é 1.81%; o
  da regra de um só atributo, nos mesmos fluxos, 0.00%.
- **O que não foi medido.** Quanto da decisão do sistema nos fluxos do HKD vem
  de `PacketLengthMode`: não há valor SHAP dos fluxos do HKD neste cenário. A
  causa da diferença entre as capturas também não foi medida. Hipótese, não
  medida: a moda do comprimento do pacote depende de como cada captura gravou
  os pacotes (por exemplo, o cabeçalho de enlace ou as opções do TCP), e não
  só da ferramenta de túnel.

## Retreino no combinado sem réplicas

Split 90/10 estratificado pelas três classes, scaler ajustado no treino do
combinado, três subconjuntos, três bases e meta, como em E1.

### Amostras por classe em cada conjunto

| conjunto | Non-DoH | Benign-DoH | Malicious-DoH | total |
| --- | --- | --- | --- | --- |
| treino | 800828 | 17771 | 229330 | 1047929 |
| validação, fold 1 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 2 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 3 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 4 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 5 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 6 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 7 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 8 | 80083 | 1777 | 22933 | 104793 |
| validação, fold 9 | 80082 | 1778 | 22933 | 104793 |
| validação, fold 10 | 80082 | 1777 | 22933 | 104792 |
| teste | 88981 | 1975 | 25481 | 116437 |

Fluxos de túnel por ferramenta:

| ferramenta | treino | teste |
| --- | --- | --- |
| dns2tcp | 150569 | 16718 |
| dnscat2 | 32068 | 3674 |
| dnstt | 2072 | 232 |
| iodine | 41948 | 4576 |
| tcp-over-dns | 1360 | 142 |
| tuns | 1313 | 139 |

Nenhum dos 513 fluxos do HKD no teste tem os mesmos 29 atributos de um fluxo do HKD no treino (conferido por asserção no script).

### Teste

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88692 | 287 | 2 |
| Benign-DoH | 132 | 1843 | 0 |
| Malicious-DoH | 4 | 12 | 25465 |

| classe | fluxos | precisão | recall | F1 |
| --- | --- | --- | --- | --- |
| Non-DoH | 88981 | 99.8469% | 99.6752% | 99.7610% |
| Benign-DoH | 1975 | 86.0411% | 93.3165% | 89.5312% |
| Malicious-DoH | 25481 | 99.9921% | 99.9372% | 99.9647% |
| média macro | 116437 | 95.2934% | 97.6430% | 96.4190% |
| média ponderada | 116437 | 99.6445% | 99.6247% | 99.6320% |

- **Acurácia 99.6247%.** No teste do CIRA, na mesma leitura:
  99.6359%. A maior parte do teste é Non-DoH e são as mesmas linhas do
  CIRA: a acurácia não diz se as ferramentas novas são detectadas.
- **Recall de Malicious-DoH 99.9372%.** Soma as seis
  ferramentas; as três do CIRA têm 24968 dos
  25481 fluxos de túnel do teste.
- **Recall das ferramentas do HKD 99.42%.** 510 de 513 túneis
  detectados; intervalo de confiança de 95%: de 98.30% a
  99.88%. São os túneis das ferramentas que o artigo não avaliou.
- **FPR de Malicious-DoH contra o resto 0.0022%.** 2 de
  90956 fluxos legítimos classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de 95%: de
  0.0003% a 0.0079%.
- **Recall de Benign-DoH 93.3165% e F1 macro 96.4190%.** No teste do
  CIRA: 92.9114% e 96.5556%.
- **AUC-ROC one-vs-rest macro: 0.988927 pela saída do
  meta-classificador e 0.996972 pela média das
  probabilidades dos bases.**



Recall de Malicious-DoH por ferramenta no teste:

| fluxos de túnel | n | detectados | recall | intervalo de confiança de 95% | erros para Non-DoH | erros para Benign-DoH |
| --- | --- | --- | --- | --- | --- | --- |
| dns2tcp | 16718 | 16715 | 99.98% | 99.95% a 100.00% | 2 | 1 |
| dnscat2 | 3674 | 3669 | 99.86% | 99.68% a 99.96% | 1 | 4 |
| dnstt | 232 | 231 | 99.57% | 97.62% a 99.99% | 0 | 1 |
| iodine | 4576 | 4571 | 99.89% | 99.75% a 99.96% | 1 | 4 |
| tcp-over-dns | 142 | 140 | 98.59% | 95.00% a 99.83% | 0 | 2 |
| tuns | 139 | 139 | 100.00% | 97.38% a 100.00% | 0 | 0 |

### Validação cruzada

10 folds estratificados sobre o treino. Em cada rodada o scaler, os
subconjuntos, o SMOTE, os bases e o meta são refeitos com os nove folds de
treino; o fold deixado de fora só é predito. A matriz soma o treino original,
sem amostra sintética.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 798383 | 2428 | 17 |
| Benign-DoH | 1206 | 16557 | 8 |
| Malicious-DoH | 86 | 67 | 229177 |

| classe | fluxos | precisão | recall | F1 |
| --- | --- | --- | --- | --- |
| Non-DoH | 800828 | 99.8384% | 99.6947% | 99.7665% |
| Benign-DoH | 17771 | 86.9043% | 93.1686% | 89.9275% |
| Malicious-DoH | 229330 | 99.9891% | 99.9333% | 99.9612% |
| média macro | 1047929 | 95.5773% | 97.5989% | 96.5517% |
| média ponderada | 1047929 | 99.6521% | 99.6362% | 99.6423% |

Acurácia de 99.6362% e F1 macro de 96.5517%; na
validação cruzada do CIRA, na mesma leitura, a acurácia é 99.6386%
(`results/e1/`).



## Retreino no combinado como publicado

Split 90/10 estratificado pelas três classes, scaler ajustado no treino do
combinado, três subconjuntos, três bases e meta, como em E1.

### Amostras por classe em cada conjunto

| conjunto | Non-DoH | Benign-DoH | Malicious-DoH | total |
| --- | --- | --- | --- | --- |
| treino | 800828 | 17771 | 319242 | 1137841 |
| validação, fold 1 | 80082 | 1778 | 31925 | 113785 |
| validação, fold 2 | 80082 | 1777 | 31925 | 113784 |
| validação, fold 3 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 4 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 5 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 6 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 7 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 8 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 9 | 80083 | 1777 | 31924 | 113784 |
| validação, fold 10 | 80083 | 1777 | 31924 | 113784 |
| teste | 88981 | 1975 | 35471 | 126427 |

Fluxos de túnel por ferramenta:

| ferramenta | treino | teste |
| --- | --- | --- |
| dns2tcp | 150608 | 16679 |
| dnscat2 | 32007 | 3735 |
| dnstt | 41384 | 4696 |
| iodine | 41957 | 4567 |
| tcp-over-dns | 27105 | 2935 |
| tuns | 26181 | 2859 |

10490 dos 10490 fluxos do HKD no teste (100.00%) têm os mesmos 29 atributos de um fluxo do HKD no treino: são cópias de fluxos do treino. O recall delas não mede detecção de fluxo novo.

### Teste

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88666 | 312 | 3 |
| Benign-DoH | 138 | 1835 | 2 |
| Malicious-DoH | 8 | 10 | 35453 |

| classe | fluxos | precisão | recall | F1 |
| --- | --- | --- | --- | --- |
| Non-DoH | 88981 | 99.8356% | 99.6460% | 99.7407% |
| Benign-DoH | 1975 | 85.0719% | 92.9114% | 88.8190% |
| Malicious-DoH | 35471 | 99.9859% | 99.9493% | 99.9676% |
| média macro | 126427 | 94.9645% | 97.5022% | 96.1758% |
| média ponderada | 126427 | 99.6471% | 99.6259% | 99.6337% |

- **Acurácia 99.6259%.** No teste do CIRA, na mesma leitura:
  99.6359%. A maior parte do teste é Non-DoH e são as mesmas linhas do
  CIRA: a acurácia não diz se as ferramentas novas são detectadas.
- **Recall de Malicious-DoH 99.9493%.** Soma as seis
  ferramentas; as três do CIRA têm 24981 dos
  35471 fluxos de túnel do teste.
- **Recall das ferramentas do HKD 100.00%.** 10490 de 10490 túneis
  detectados; intervalo de confiança de 95%: de 99.96% a
  100.00%. São os túneis das ferramentas que o artigo não avaliou.
- **FPR de Malicious-DoH contra o resto 0.0055%.** 5 de
  90956 fluxos legítimos classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de 95%: de
  0.0018% a 0.0128%.
- **Recall de Benign-DoH 92.9114% e F1 macro 96.1758%.** No teste do
  CIRA: 92.9114% e 96.5556%.
- **AUC-ROC one-vs-rest macro: 0.993053 pela saída do
  meta-classificador e 0.996697 pela média das
  probabilidades dos bases.**



Recall de Malicious-DoH por ferramenta no teste:

| fluxos de túnel | n | detectados | recall | intervalo de confiança de 95% | erros para Non-DoH | erros para Benign-DoH |
| --- | --- | --- | --- | --- | --- | --- |
| dns2tcp | 16679 | 16671 | 99.95% | 99.91% a 99.98% | 3 | 5 |
| dnscat2 | 3735 | 3731 | 99.89% | 99.73% a 99.97% | 2 | 2 |
| dnstt | 4696 | 4696 | 100.00% | 99.92% a 100.00% | 0 | 0 |
| iodine | 4567 | 4561 | 99.87% | 99.71% a 99.95% | 3 | 3 |
| tcp-over-dns | 2935 | 2935 | 100.00% | 99.87% a 100.00% | 0 | 0 |
| tuns | 2859 | 2859 | 100.00% | 99.87% a 100.00% | 0 | 0 |

### Validação cruzada

Neste cenário a validação cruzada não é executada: ele é análise ao lado do combinado sem réplicas. A tabela de amostras por fold acima vem só dos índices.

## Ferramentas do HKD nos três cenários

Recall de Malicious-DoH, com detectados sobre `n` e o intervalo de confiança
de 95% entre parênteses.

| ferramenta | transferência (HKD inteiro) | retreino no combinado sem réplicas (teste) | retreino no combinado como publicado (teste) |
| --- | --- | --- | --- |
| dnstt | 0.00% (0/2304; 0.00% a 0.16%) | 99.57% (231/232; 97.62% a 99.99%) | 100.00% (4696/4696; 99.92% a 100.00%) |
| tcp-over-dns | 0.33% (5/1502; 0.11% a 0.78%) | 98.59% (140/142; 95.00% a 99.83%) | 100.00% (2935/2935; 99.87% a 100.00%) |
| tuns | 6.20% (90/1452; 5.01% a 7.56%) | 100.00% (139/139; 97.38% a 100.00%) | 100.00% (2859/2859; 99.87% a 100.00%) |

O que foi medido: no retreino publicado, 10490 dos
10490 fluxos do HKD no teste têm cópia idêntica no treino; no retreino
sem réplicas, 0 dos 513.

- **O que isso permite concluir.** No publicado, o recall das ferramentas do HKD
  é medido em fluxos que o modelo já recebeu no treino: ele não mede a detecção
  de fluxo novo dessas ferramentas. A coluna que mede isso é a do retreino sem
  réplicas.
- **O que isso não permite concluir.** A diferença entre as duas colunas reúne
  dois efeitos que este experimento não separa: o peso 20 vezes maior do HKD
  no treino (94670 fluxos contra 4745) e a presença, no teste, de cópias
  de fluxos do treino. Os dois testes têm linhas e tamanhos diferentes
  (10490 fluxos do HKD contra 513).

A coluna da transferência não é comparável em tamanho: é o HKD inteiro, e o
sistema não viu nenhuma das três ferramentas.

**Proximidade ao treino.** No retreino sem réplicas, o recall das ferramentas do HKD (99.42%, 510 de 513) é de fluxos muito próximos de fluxos do treino. Nos 29 atributos normalizados, a mediana da distância de um fluxo do HKD no teste ao fluxo do HKD mais próximo no treino é 0.002571; ao fluxo Malicious-DoH do CIRA mais próximo no treino, 0.051449. Em 505 dos 513 fluxos (98.44%), o vizinho do HKD está mais perto que qualquer malicioso do CIRA. Nenhum deles é cópia exata, mas o recall não estima a detecção de uma sessão de túnel que o treino não tenha. Medida em `../dados/combinado_sem_replicas/seed42/metrics.json`, com a tabela em `../dados/RESUMO.md`.

## O que não foi feito

- O recall por ferramenta no retreino sem réplicas vem de uma única divisão,
  com a seed 42: é uma estimativa, com o intervalo ao lado. Não há média
  de várias seeds aqui.
- No combinado como publicado não há validação cruzada; só o tamanho dos folds.
- A validação cruzada grava só a matriz de confusão: não há recall por
  ferramenta nem AUC nos folds.
- Fluxos do HKD da mesma sessão de túnel podem cair um no treino e outro no
  teste sem serem cópias exatas. A sessão não está nas tabelas e não é medida;
  o que foi medido é a distância ao treino, acima.
- Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada depois de ver
  os resultados.

## SHAP dos Random Forests base no combinado sem réplicas

Gerado por `scripts/e6_baselines_xai.py`, com as mesmas funções da explicação
no CIRA (`scripts/e5_xai.py`). Os números vêm de `retreino_sem_replicas-shap/seed42/metrics.json`; os
do CIRA, de `results/e5/variante/`. O sistema explicado é o do retreino
no combinado sem réplicas nesta leitura: mesma seed, mesmo split e mesmos
subconjuntos de `retreino_sem_replicas/`. Não há figura do artigo para este dataset: o
que fica ao lado é a explicação no CIRA.

### Amostras

Duas amostras estratificadas de até 2000 fluxos por classe,
sorteadas com a seed 42, como no CIRA. O sorteio é feito na classe
Malicious-DoH inteira, sem separar por ferramenta, e o número de fluxos de cada
ferramenta na amostra não é gravado. No treino, 4745 dos 229330 fluxos da
classe são do HKD (2.07%): pelo sorteio, a amostra de Malicious-DoH
é quase toda de fluxos das ferramentas do CIRA, e a importância medida reflete
sobretudo esses fluxos.

| amostra | Non-DoH | Benign-DoH | Malicious-DoH | uso |
| --- | --- | --- | --- | --- |
| treino | 2000 | 2000 | 2000 | importância global |
| teste | 2000 | 1975 | 2000 | dependência e explicações locais |

A tabela `retreino_sem_replicas-shap/seed42/importancia.csv` traz a média do valor absoluto de SHAP
por base, classe e atributo. As figuras, na mesma pasta, são as equivalentes às
Figs. 5 a 8 do artigo e usam o Random Forest base 1.

### Ranking de Malicious-DoH ao lado do CIRA

| posto | CIRA, base 1 | combinado, base 1 | combinado, base 2 | combinado, base 3 |
| --- | --- | --- | --- | --- |
| 1 | PacketLengthMode | PacketLengthMode | PacketLengthMode | PacketLengthMode |
| 2 | PacketLengthMedian | Duration | Duration | Duration |
| 3 | Duration | PacketLengthMedian | PacketLengthMedian | PacketLengthMedian |
| 4 | PacketTimeMedian | PacketTimeMedian | PacketTimeMedian | PacketTimeMedian |
| 5 | PacketLengthSkewFromMode | ResponseTimeTimeMedian | ResponseTimeTimeMedian | ResponseTimeTimeMedian |
| 6 | PacketLengthCoefficientofVariation | PacketLengthMean | PacketLengthMean | PacketLengthMean |
| 7 | ResponseTimeTimeMedian | PacketLengthCoefficientofVariation | PacketLengthCoefficientofVariation | PacketLengthCoefficientofVariation |
| 8 | PacketLengthMean | FlowBytesSent | FlowBytesSent | FlowBytesReceived |
| 9 | FlowBytesSent | FlowBytesReceived | FlowBytesReceived | FlowBytesSent |
| 10 | FlowBytesReceived | ResponseTimeTimeMean | ResponseTimeTimeMean | PacketLengthSkewFromMedian |

| base | classe | Spearman nos 29 atributos | Spearman na união dos 10 primeiros | atributos em comum nos 10 primeiros |
| --- | --- | --- | --- | --- |
| base 1 | Non-DoH | 0.958 | 0.991 | 9 |
| base 1 | Benign-DoH | 0.966 | 0.945 | 9 |
| base 1 | Malicious-DoH | 0.863 | 0.773 | 9 |
| base 2 | Non-DoH | 0.992 | 0.988 | 10 |
| base 2 | Benign-DoH | 0.983 | 0.964 | 9 |
| base 2 | Malicious-DoH | 0.910 | 0.955 | 9 |
| base 3 | Non-DoH | 0.959 | 0.891 | 10 |
| base 3 | Benign-DoH | 0.959 | 0.945 | 9 |
| base 3 | Malicious-DoH | 0.878 | 0.945 | 9 |

Correlação de postos de Spearman entre o ranking de importância no combinado sem réplicas e o do base de mesmo número no CIRA; o valor 1 quer dizer a mesma ordem. O base de mesmo número não é o mesmo modelo nos dois datasets: cada um foi treinado no seu subconjunto, depois de outro split.

### Estabilidade entre os três submodelos

Correlação de postos de Spearman entre os rankings de dois bases, sobre os
atributos que estão entre os 10 primeiros de pelo menos um deles.

| classe | bases 1-2 | bases 1-3 | bases 2-3 |
| --- | --- | --- | --- |
| Non-DoH | 0.964 | 0.873 | 0.842 |
| Benign-DoH | 0.964 | 0.900 | 0.891 |
| Malicious-DoH | 1.000 | 0.982 | 0.982 |

### Dependência e explicações locais

Medidas do Random Forest base 1 na amostra do teste. O limiar de
40 segundos é a leitura que o artigo faz da Fig. 6a, no CIRA;
aqui ele é só a linha de referência das figuras.

| medida | CIRA (E5) | combinado sem réplicas |
| --- | --- | --- |
| corte que melhor separa o sinal do SHAP (s), amostra com classes em partes iguais | 33.13 | 33.07 |
| SHAP positivo acima de 40 s | 97.37% | 98.30% |
| SHAP positivo até 40 s | 20.51% | 19.28% |
| base concorda com o empilhado | 99.50% | 99.68% |

Fluxos da amostra com mais bytes recebidos que enviados, por classe real:
[1544, 988, 1614]; o valor SHAP de `FlowBytesSent` para Malicious-DoH é positivo em
30.41% deles e em 24.33% dos demais.

- `fig7_explicacao_malicious-doh.png` e `fig7_explicacao_malicious-doh.csv`: fluxo Malicious-DoH do teste. Probabilidade da classe no base 1: 100.00%, a partir da média da população de 31.61%; atributo de maior efeito: `PacketLengthMode` = 68 (+59.43 pp). Classe predita pelo base: Malicious-DoH; pelo modelo empilhado: Malicious-DoH.
- `fig8_explicacao_non-doh.png` e `fig8_explicacao_non-doh.csv`: fluxo Non-DoH do teste. Probabilidade da classe no base 1: 100.00%, a partir da média da população de 36.81%; atributo de maior efeito: `PacketLengthMode` = 112 (+39.17 pp). Classe predita pelo base: Non-DoH; pelo modelo empilhado: Non-DoH.

### Limitação

Os valores SHAP deste experimento explicam os Random Forests base, não a decisão do empilhamento. A linha 8 do Algoritmo 1 do artigo aplica o `TreeExplainer` sem dizer a qual modelo. O `TreeExplainer` recusa o modelo empilhado com o erro: `Model type not yet supported by TreeExplainer: <class 'mlxtend.classifier.stacking_classification.StackingClassifier'>`. A regressão logística que combina os três bases não é um modelo de árvores, e a decisão final do sistema passa por ela.

Na amostra do teste, com as classes em partes iguais, a classe de maior probabilidade do base 1 é a classe que o modelo empilhado devolve em 99.68% dos fluxos. Predições do modelo empilhado na amostra: 2123 de Non-DoH, 1852 de Benign-DoH, 2000 de Malicious-DoH. Onde os dois divergem, a explicação do base não é a explicação da saída do sistema.

Os valores SHAP são calculados em amostras, com uma seed. O fluxo de cada
explicação local é o primeiro da classe na amostra do teste e pode ser de
qualquer ferramenta.
