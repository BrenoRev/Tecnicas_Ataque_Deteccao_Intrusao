# E6: o segundo dataset ao lado do CIRA

Gerado por `scripts/e6_resumo.py`, a partir dos `metrics.json` de `results/e6/`
(gravados por `scripts/e6_dataset2.py` e `scripts/e6_baselines_xai.py`) e dos de
`results/e1/`, `results/e2/` e `results/e5/`. Seed 42, uma execução de cada
modelo e de cada cenário: não há média nem desvio padrão.

- **variante (profundidade variável):** sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Detalhe em `variante/RESUMO.md`.
- **fiel (profundidade 5):** profundidade máxima 5 nos submodelos (Seção IV-B). Detalhe em `fiel/RESUMO.md`.

O sistema base desta etapa é o de profundidade variável; o de profundidade 5
vai ao lado. O artigo não traz figura nem tabela para o segundo dataset: o que
fica lado a lado é o resultado no CIRA e o do segundo dataset.

- **Combinado sem réplicas:** dataset combinado CIRA + DoH-Tunnel-Traffic-HKD
  com cada fluxo do HKD uma única vez. É o dataset principal: nele são refeitos
  o sistema nas duas leituras, a validação cruzada, os três modelos de
  comparação da Tabela II e o SHAP.
- **Combinado como publicado:** o mesmo, com as 20 cópias de cada fluxo do
  HKD, que deixam cópias idênticas no treino e no teste. Análise ao lado.
- **Transferência:** treino no CIRA, avaliação nos fluxos do HKD. O HKD só tem
  a classe maliciosa e não permite treinar o sistema: não há precisão, FPR nem
  acurácia, e neste cenário tudo é teste. Análise ao lado.

No combinado, Non-DoH e Benign-DoH são os fluxos do CIRA; só a classe maliciosa
ganha fluxos novos. Métricas gerais perto das do CIRA são esperadas e não medem
generalização: a leitura útil é o recall das ferramentas do HKD.

## Tabela final: CIRA ao lado do combinado sem réplicas

Os modelos de comparação são os da Tabela II do artigo e não dependem da
leitura de profundidade. Os resultados no CIRA vêm de `results/e1/` (sistema) e
de `results/e2/` (modelos de comparação).

| modelo | dataset | avaliado em | fluxos avaliados | acurácia | F1 macro | F1 ponderado | recall de Non-DoH | recall de Benign-DoH | recall de Malicious-DoH | precisão de Malicious-DoH | FPR de Malicious-DoH contra o resto | AUC-ROC one-vs-rest macro | recall das ferramentas do HKD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sistema do artigo, variante (profundidade variável) | CIRA | teste | 115911 | 99.6359% | 96.5556% | 99.6415% | 99.6943% | 92.9114% | 99.9599% | 99.9880% | 0.0033% | 0.993010 | sem fluxos do HKD |
| Sistema do artigo, variante (profundidade variável) | combinado sem réplicas | teste | 116437 | 99.6247% | 96.4190% | 99.6320% | 99.6752% | 93.3165% | 99.9372% | 99.9921% | 0.0022% | 0.988927 | 99.42% (510/513; 98.30% a 99.88%) |
| Sistema do artigo, variante (profundidade variável) | CIRA | validação cruzada | 1043197 | 99.6386% | 96.5701% | 99.6445% | 99.6972% | 93.1630% | 99.9421% | 99.9955% | 0.0012% | não medido | sem fluxos do HKD |
| Sistema do artigo, variante (profundidade variável) | combinado sem réplicas | validação cruzada | 1047929 | 99.6362% | 96.5517% | 99.6423% | 99.6947% | 93.1686% | 99.9333% | 99.9891% | 0.0031% | não medido | não medido |
| Sistema do artigo, fiel (profundidade 5) | CIRA | teste | 115911 | 97.7949% | 65.8027% | 96.9555% | 99.9337% | 0.0000% | 97.9082% | 99.7591% | 0.0649% | 0.961172 | sem fluxos do HKD |
| Sistema do artigo, fiel (profundidade 5) | combinado sem réplicas | teste | 116437 | 97.5592% | 65.5661% | 96.7294% | 99.8258% | 0.0000% | 97.2058% | 99.3383% | 0.1814% | 0.963208 | 73.29% (376/513; 69.24% a 77.08%) |
| Sistema do artigo, fiel (profundidade 5) | CIRA | validação cruzada | 1043197 | 97.7338% | 65.7495% | 96.8994% | 99.9066% | 0.0056% | 97.7190% | 99.6803% | 0.0860% | não medido | sem fluxos do HKD |
| Sistema do artigo, fiel (profundidade 5) | combinado sem réplicas | validação cruzada | 1047929 | 97.5840% | 65.5892% | 96.7526% | 99.8871% | 0.0000% | 97.1033% | 99.5587% | 0.1206% | não medido | não medido |
| Árvore de decisão | CIRA | teste | 115911 | 97.2306% | 84.2075% | 97.7452% | 96.7487% | 93.2152% | 99.2667% | 99.7022% | 0.0814% | 0.992682 | sem fluxos do HKD |
| Árvore de decisão | combinado sem réplicas | teste | 116437 | 97.1641% | 83.8258% | 97.7122% | 96.6543% | 92.8608% | 99.2779% | 99.7988% | 0.0561% | 0.992473 | 98.64% (506/513; 97.21% a 99.45%) |
| XGBoost | CIRA | teste | 115911 | 99.3090% | 93.9987% | 99.3531% | 99.2144% | 94.9367% | 99.9920% | 99.9960% | 0.0011% | 0.998613 | sem fluxos do HKD |
| XGBoost | combinado sem réplicas | teste | 116437 | 99.3353% | 94.1789% | 99.3758% | 99.2470% | 94.9367% | 99.9843% | 99.9961% | 0.0011% | 0.998576 | 100.00% (513/513; 99.28% a 100.00%) |
| Random Forest | CIRA | teste | 115911 | 99.4194% | 94.8025% | 99.4467% | 99.3886% | 93.9747% | 99.9599% | 99.9960% | 0.0011% | 0.996580 | sem fluxos do HKD |
| Random Forest | combinado sem réplicas | teste | 116437 | 99.3902% | 94.5820% | 99.4204% | 99.3504% | 93.8734% | 99.9568% | 99.9764% | 0.0066% | 0.996537 | 100.00% (513/513; 99.28% a 100.00%) |

- As duas linhas de um modelo não usam o mesmo teste: cada dataset tem o seu
  split, com a mesma seed. A diferença entre elas não isola o efeito das
  ferramentas novas.
- No sistema, a AUC é a da saída do meta-classificador; a da média das
  probabilidades dos bases está no resumo de cada trilha. A validação cruzada
  grava só a matriz de confusão: não há AUC nem recall por ferramenta nos
  folds. Os modelos de comparação não têm validação cruzada, como no CIRA.
- A última coluna é o recall de Malicious-DoH só nos fluxos de dnstt,
  tcp-over-dns e tuns, com os detectados sobre `n` e o intervalo de confiança
  de 95%.

Leitura em termos de detecção, no teste do combinado sem réplicas:

- **Sistema do artigo, variante (profundidade variável).** Recall das ferramentas do HKD de 99.42%: de 513 túneis de dnstt, tcp-over-dns e tuns no teste, 3 passam sem alerta (intervalo de confiança de 95%: de 98.30% a 99.88%). FPR de Malicious-DoH contra o resto de 0.0022%: 2 de 90956 fluxos legítimos viram alarme falso. Recall de Benign-DoH de 93.32%.
- **Sistema do artigo, fiel (profundidade 5).** Recall das ferramentas do HKD de 73.29%: de 513 túneis de dnstt, tcp-over-dns e tuns no teste, 137 passam sem alerta (intervalo de confiança de 95%: de 69.24% a 77.08%). FPR de Malicious-DoH contra o resto de 0.1814%: 165 de 90956 fluxos legítimos viram alarme falso. Recall de Benign-DoH de 0.00%.
- **Árvore de decisão.** Recall das ferramentas do HKD de 98.64%: de 513 túneis de dnstt, tcp-over-dns e tuns no teste, 7 passam sem alerta (intervalo de confiança de 95%: de 97.21% a 99.45%). FPR de Malicious-DoH contra o resto de 0.0561%: 51 de 90956 fluxos legítimos viram alarme falso. Recall de Benign-DoH de 92.86%.
- **XGBoost.** Recall das ferramentas do HKD de 100.00%: de 513 túneis de dnstt, tcp-over-dns e tuns no teste, 0 passam sem alerta (intervalo de confiança de 95%: de 99.28% a 100.00%). FPR de Malicious-DoH contra o resto de 0.0011%: 1 de 90956 fluxos legítimos viram alarme falso. Recall de Benign-DoH de 94.94%.
- **Random Forest.** Recall das ferramentas do HKD de 100.00%: de 513 túneis de dnstt, tcp-over-dns e tuns no teste, 0 passam sem alerta (intervalo de confiança de 95%: de 99.28% a 100.00%). FPR de Malicious-DoH contra o resto de 0.0066%: 6 de 90956 fluxos legítimos viram alarme falso. Recall de Benign-DoH de 93.87%.

## Recall por ferramenta no teste do combinado sem réplicas

Recall de Malicious-DoH, com detectados sobre `n` e o intervalo de confiança de
95% entre parênteses. O teste é o mesmo para os cinco modelos. dns2tcp, dnscat2
e iodine são as ferramentas do CIRA; dnstt, tcp-over-dns e tuns, as do HKD.

| ferramenta | Sistema do artigo, variante (profundidade variável) | Sistema do artigo, fiel (profundidade 5) | Árvore de decisão | XGBoost | Random Forest |
| --- | --- | --- | --- | --- | --- |
| dns2tcp | 99.98% (16715/16718; 99.95% a 100.00%) | 99.41% (16620/16718; 99.29% a 99.52%) | 99.75% (16677/16718; 99.67% a 99.82%) | 99.99% (16717/16718; 99.97% a 100.00%) | 99.98% (16715/16718; 99.95% a 100.00%) |
| dnscat2 | 99.86% (3669/3674; 99.68% a 99.96%) | 93.69% (3442/3674; 92.85% a 94.45%) | 98.67% (3625/3674; 98.24% a 99.01%) | 99.97% (3673/3674; 99.85% a 100.00%) | 99.95% (3672/3674; 99.80% a 99.99%) |
| dnstt | 99.57% (231/232; 97.62% a 99.99%) | 49.14% (114/232; 42.54% a 55.76%) | 99.57% (231/232; 97.62% a 99.99%) | 100.00% (232/232; 98.42% a 100.00%) | 100.00% (232/232; 98.42% a 100.00%) |
| iodine | 99.89% (4571/4576; 99.75% a 99.96%) | 94.65% (4331/4576; 93.95% a 95.28%) | 98.10% (4489/4576; 97.66% a 98.47%) | 99.96% (4574/4576; 99.84% a 99.99%) | 99.87% (4570/4576; 99.71% a 99.95%) |
| tcp-over-dns | 98.59% (140/142; 95.00% a 99.83%) | 87.32% (124/142; 80.71% a 92.31%) | 95.77% (136/142; 91.03% a 98.43%) | 100.00% (142/142; 97.44% a 100.00%) | 100.00% (142/142; 97.44% a 100.00%) |
| tuns | 100.00% (139/139; 97.38% a 100.00%) | 99.28% (138/139; 96.06% a 99.98%) | 100.00% (139/139; 97.38% a 100.00%) | 100.00% (139/139; 97.38% a 100.00%) | 100.00% (139/139; 97.38% a 100.00%) |
| ferramentas do CIRA juntas | 99.95% (24955/24968; 99.91% a 99.97%) | 97.70% (24393/24968; 97.50% a 97.88%) | 99.29% (24791/24968; 99.18% a 99.39%) | 99.98% (24964/24968; 99.96% a 100.00%) | 99.96% (24957/24968; 99.92% a 99.98%) |
| ferramentas do HKD juntas | 99.42% (510/513; 98.30% a 99.88%) | 73.29% (376/513; 69.24% a 77.08%) | 98.64% (506/513; 97.21% a 99.45%) | 100.00% (513/513; 99.28% a 100.00%) | 100.00% (513/513; 99.28% a 100.00%) |

## SHAP no combinado sem réplicas ao lado do CIRA

Valores SHAP dos Random Forests base do sistema retreinado no combinado sem
réplicas, nas mesmas amostras por classe da explicação no CIRA (E5). Fluxos por
classe nas amostras: variante (profundidade variável): treino [2000, 2000, 2000], teste [2000, 1975, 2000]; fiel (profundidade 5): treino [2000, 2000, 2000], teste [2000, 1975, 2000].

Primeiros atributos de Malicious-DoH, Random Forest base 1:

| posto | CIRA, variante (profundidade variável) | combinado sem réplicas, variante (profundidade variável) | CIRA, fiel (profundidade 5) | combinado sem réplicas, fiel (profundidade 5) |
| --- | --- | --- | --- | --- |
| 1 | PacketLengthMode | PacketLengthMode | PacketLengthMode | PacketLengthMode |
| 2 | PacketLengthMedian | Duration | Duration | Duration |
| 3 | Duration | PacketLengthMedian | PacketTimeMedian | PacketTimeMedian |
| 4 | PacketTimeMedian | PacketTimeMedian | PacketLengthMedian | PacketLengthMedian |
| 5 | PacketLengthSkewFromMode | ResponseTimeTimeMedian | PacketLengthCoefficientofVariation | PacketLengthMean |
| 6 | PacketLengthCoefficientofVariation | PacketLengthMean | PacketLengthMean | PacketLengthCoefficientofVariation |
| 7 | ResponseTimeTimeMedian | PacketLengthCoefficientofVariation | FlowBytesSent | FlowBytesSent |
| 8 | PacketLengthMean | FlowBytesSent | ResponseTimeTimeSkewFromMedian | PacketTimeCoefficientofVariation |
| 9 | FlowBytesSent | FlowBytesReceived | PacketTimeCoefficientofVariation | PacketLengthStandardDeviation |
| 10 | FlowBytesReceived | ResponseTimeTimeMean | PacketLengthStandardDeviation | ResponseTimeTimeMedian |

Concordância do ranking no combinado sem réplicas com o do CIRA:

| leitura | base | classe | Spearman nos 29 atributos | Spearman na união dos 10 primeiros | atributos em comum nos 10 primeiros |
| --- | --- | --- | --- | --- | --- |
| variante (profundidade variável) | base 1 | Non-DoH | 0.958 | 0.991 | 9 |
| variante (profundidade variável) | base 1 | Benign-DoH | 0.966 | 0.945 | 9 |
| variante (profundidade variável) | base 1 | Malicious-DoH | 0.863 | 0.773 | 9 |
| variante (profundidade variável) | base 2 | Non-DoH | 0.992 | 0.988 | 10 |
| variante (profundidade variável) | base 2 | Benign-DoH | 0.983 | 0.964 | 9 |
| variante (profundidade variável) | base 2 | Malicious-DoH | 0.910 | 0.955 | 9 |
| variante (profundidade variável) | base 3 | Non-DoH | 0.959 | 0.891 | 10 |
| variante (profundidade variável) | base 3 | Benign-DoH | 0.959 | 0.945 | 9 |
| variante (profundidade variável) | base 3 | Malicious-DoH | 0.878 | 0.945 | 9 |
| fiel (profundidade 5) | base 1 | Non-DoH | 0.980 | 0.991 | 9 |
| fiel (profundidade 5) | base 1 | Benign-DoH | 0.975 | 0.976 | 10 |
| fiel (profundidade 5) | base 1 | Malicious-DoH | 0.974 | 0.936 | 9 |
| fiel (profundidade 5) | base 2 | Non-DoH | 0.967 | 0.982 | 9 |
| fiel (profundidade 5) | base 2 | Benign-DoH | 0.967 | 0.976 | 10 |
| fiel (profundidade 5) | base 2 | Malicious-DoH | 0.952 | 0.873 | 9 |
| fiel (profundidade 5) | base 3 | Non-DoH | 0.988 | 1.000 | 10 |
| fiel (profundidade 5) | base 3 | Benign-DoH | 0.965 | 0.955 | 9 |
| fiel (profundidade 5) | base 3 | Malicious-DoH | 0.934 | 0.873 | 9 |

Correlação de postos de Spearman entre o ranking de importância no combinado sem réplicas e o do base de mesmo número no CIRA; o valor 1 quer dizer a mesma ordem. O base de mesmo número não é o mesmo modelo nos dois datasets: cada um foi treinado no seu subconjunto, depois de outro split.

## Ao lado do que foi declarado antes de rodar os modelos de comparação e o SHAP

O cabeçalho de `scripts/e6_baselines_xai.py` declara, antes da execução, o que
contaria como resultado inesperado. Os números:

1. Recall das ferramentas do HKD dos modelos de comparação ao lado do intervalo de confiança do sistema na leitura variante (profundidade variável) (de 98.30% a 99.88%):
   - Árvore de decisão: 98.64%, dentro ou acima do intervalo.
   - XGBoost: 100.00%, dentro ou acima do intervalo.
   - Random Forest: 100.00%, dentro ou acima do intervalo.
2. Posto de `Duration` no ranking de Malicious-DoH dos três bases treinados no combinado sem réplicas:
   - variante (profundidade variável): 2, 2, 2.
   - fiel (profundidade 5): 2, 2, 2.

## Análises ao lado: combinado como publicado e transferência

Os quatro cenários do sistema do artigo, nas duas leituras: CIRA,
transferência, retreino no combinado sem réplicas e retreino no combinado como
publicado.

| cenário | leitura | avaliado em | fluxos avaliados | acurácia | F1 macro | recall de Non-DoH | recall de Benign-DoH | recall de Malicious-DoH | precisão de Malicious-DoH | FPR de Malicious-DoH contra o resto | recall das ferramentas do HKD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CIRA (E1) | variante (profundidade variável) | teste | 115911 | 99.6359% | 96.5556% | 99.6943% | 92.9114% | 99.9599% | 99.9880% | 0.0033% | sem fluxos do HKD |
| CIRA (E1) | variante (profundidade variável) | validação cruzada | 1043197 | 99.6386% | 96.5701% | 99.6972% | 93.1630% | 99.9421% | 99.9955% | 0.0012% | sem fluxos do HKD |
| transferência | variante (profundidade variável) | HKD inteiro | 5258 | não definido | não definido | não definido | não definido | 1.8068% | não definido | não definido | 1.81% |
| retreino no combinado sem réplicas | variante (profundidade variável) | teste | 116437 | 99.6247% | 96.4190% | 99.6752% | 93.3165% | 99.9372% | 99.9921% | 0.0022% | 99.42% |
| retreino no combinado sem réplicas | variante (profundidade variável) | validação cruzada | 1047929 | 99.6362% | 96.5517% | 99.6947% | 93.1686% | 99.9333% | 99.9891% | 0.0031% | não medido |
| retreino no combinado como publicado | variante (profundidade variável) | teste | 126427 | 99.6259% | 96.1758% | 99.6460% | 92.9114% | 99.9493% | 99.9859% | 0.0055% | 100.00% |
| CIRA (E1) | fiel (profundidade 5) | teste | 115911 | 97.7949% | 65.8027% | 99.9337% | 0.0000% | 97.9082% | 99.7591% | 0.0649% | sem fluxos do HKD |
| CIRA (E1) | fiel (profundidade 5) | validação cruzada | 1043197 | 97.7338% | 65.7495% | 99.9066% | 0.0056% | 97.7190% | 99.6803% | 0.0860% | sem fluxos do HKD |
| transferência | fiel (profundidade 5) | HKD inteiro | 5258 | não definido | não definido | não definido | não definido | 1.7117% | não definido | não definido | 1.71% |
| retreino no combinado sem réplicas | fiel (profundidade 5) | teste | 116437 | 97.5592% | 65.5661% | 99.8258% | 0.0000% | 97.2058% | 99.3383% | 0.1814% | 73.29% |
| retreino no combinado sem réplicas | fiel (profundidade 5) | validação cruzada | 1047929 | 97.5840% | 65.5892% | 99.8871% | 0.0000% | 97.1033% | 99.5587% | 0.1206% | não medido |
| retreino no combinado como publicado | fiel (profundidade 5) | teste | 126427 | 96.7721% | 64.8783% | 99.0065% | 0.0000% | 96.5549% | 97.0887% | 1.1291% | 99.49% |

A última coluna é o recall de Malicious-DoH só nos fluxos de dnstt, tcp-over-dns
e tuns. Na validação cruzada ela não é medida, porque só a matriz de confusão
é gravada.

Recall por ferramenta do HKD nos três cenários, com detectados sobre `n` e
intervalo de confiança de 95% entre parênteses.

variante (profundidade variável):

| ferramenta | transferência (HKD inteiro) | retreino no combinado sem réplicas (teste) | retreino no combinado como publicado (teste) |
| --- | --- | --- | --- |
| dnstt | 0.00% (0/2304; 0.00% a 0.16%) | 99.57% (231/232; 97.62% a 99.99%) | 100.00% (4696/4696; 99.92% a 100.00%) |
| tcp-over-dns | 0.33% (5/1502; 0.11% a 0.78%) | 98.59% (140/142; 95.00% a 99.83%) | 100.00% (2935/2935; 99.87% a 100.00%) |
| tuns | 6.20% (90/1452; 5.01% a 7.56%) | 100.00% (139/139; 97.38% a 100.00%) | 100.00% (2859/2859; 99.87% a 100.00%) |

fiel (profundidade 5):

| ferramenta | transferência (HKD inteiro) | retreino no combinado sem réplicas (teste) | retreino no combinado como publicado (teste) |
| --- | --- | --- | --- |
| dnstt | 0.00% (0/2304; 0.00% a 0.16%) | 49.14% (114/232; 42.54% a 55.76%) | 100.00% (4696/4696; 99.92% a 100.00%) |
| tcp-over-dns | 0.00% (0/1502; 0.00% a 0.25%) | 87.32% (124/142; 80.71% a 92.31%) | 98.23% (2883/2935; 97.68% a 98.67%) |
| tuns | 6.20% (90/1452; 5.01% a 7.56%) | 99.28% (138/139; 96.06% a 99.98%) | 99.97% (2858/2859; 99.81% a 100.00%) |

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

**Proximidade ao treino.** No retreino sem réplicas, o recall das ferramentas do HKD (99.42%, 510 de 513) é de fluxos muito próximos de fluxos do treino. Nos 29 atributos normalizados, a mediana da distância de um fluxo do HKD no teste ao fluxo do HKD mais próximo no treino é 0.002571; ao fluxo Malicious-DoH do CIRA mais próximo no treino, 0.051449. Em 505 dos 513 fluxos (98.44%), o vizinho do HKD está mais perto que qualquer malicioso do CIRA. Nenhum deles é cópia exata, mas o recall não estima a detecção de uma sessão de túnel que o treino não tenha. Medida em `dados/combinado_sem_replicas/seed42/metrics.json`, com a tabela em `dados/RESUMO.md`. O recall citado é o da leitura
variante (profundidade variável).

## `PacketLengthMode` e a queda na transferência

Medido pela etapa de dados nos conjuntos limpos inteiros
(`dados/hkd/seed42/metrics.json`, com a tabela em `dados/RESUMO.md`).
No CIRA limpo inteiro, os valores {56, 62, 68, 87} de `PacketLengthMode` cobrem 99.84% dos 249553 fluxos Malicious-DoH e ocorrem em 1 dos 909555 fluxos legítimos (Non-DoH e Benign-DoH). A regra de um só atributo que chama de malicioso o fluxo com `PacketLengthMode` nesse conjunto tem, no mesmo CIRA de onde os valores foram tirados, recall de 99.84% e 1 falso positivo em 909555 (FPR de 0.0001%). Nos 5258 fluxos do HKD ela detecta 0 (0.00%): 0.00% dos fluxos do HKD têm um valor de `PacketLengthMode` que ocorre no Malicious-DoH do CIRA. O valor mais frequente no HKD, 66 (99.90% dos fluxos), é, no CIRA, o de 28.09% dos fluxos Non-DoH, 50.70% dos fluxos Benign-DoH, 0.00% dos fluxos Malicious-DoH.

O recall do sistema na transferência, nas duas leituras, está na tabela de
cenários acima. O que não foi medido: quanto da decisão do sistema nos fluxos
do HKD vem desse atributo, e a causa da diferença entre as capturas. Hipótese,
não medida: a moda do comprimento do pacote depende de como cada captura gravou
os pacotes (por exemplo, o cabeçalho de enlace ou as opções do TCP), e não só
da ferramenta de túnel.

## Números ao lado das hipóteses

As hipóteses estão em `fiel/HIPOTESE.md`, na mesma ordem, e não foram alteradas
depois da execução.

### variante (profundidade variável)

1. Valores fora de [0, 1] na transferência:
   0 valores em 0 fluxos; no teste do CIRA,
   3 valores em 3 fluxos (`FlowSentRate` 1, `PacketLengthMean` 1, `ResponseTimeTimeCoefficientofVariation` 1).
2. Recall na transferência: 1.81%, menor que o do teste do CIRA
   (99.96%).
3. Recall das ferramentas do HKD no teste: 100.00% no retreino publicado
   (intervalo de 99.96% a 100.00%,
   n = 10490) e 99.42% no retreino sem réplicas (intervalo de
   98.30% a 99.88%, n = 513).
4. Acurácia no teste: 99.6359% no CIRA, 99.6247% no combinado
   sem réplicas e 99.6259% no publicado.
5. Recall de Benign-DoH no teste: 92.91% no CIRA, 93.32% no combinado
   sem réplicas e 92.91% no publicado.

### fiel (profundidade 5)

1. Valores fora de [0, 1] na transferência:
   0 valores em 0 fluxos; no teste do CIRA,
   3 valores em 3 fluxos (`FlowSentRate` 1, `PacketLengthMean` 1, `ResponseTimeTimeCoefficientofVariation` 1).
2. Recall na transferência: 1.71%, menor que o do teste do CIRA
   (97.91%).
3. Recall das ferramentas do HKD no teste: 99.49% no retreino publicado
   (intervalo de 99.34% a 99.62%,
   n = 10490) e 73.29% no retreino sem réplicas (intervalo de
   69.24% a 77.08%, n = 513).
4. Acurácia no teste: 97.7949% no CIRA, 97.5592% no combinado
   sem réplicas e 96.7721% no publicado.
5. Recall de Benign-DoH no teste: 0.00% no CIRA, 0.00% no combinado
   sem réplicas e 0.00% no publicado.

## Resultados que a hipótese listava como inesperados

A lista é a de `fiel/HIPOTESE.md`, na mesma ordem.

### variante (profundidade variável)

- Recall na transferência igual ou maior que o do teste do CIRA:
  não ocorreu (1.81% contra 99.96%).
- Recall na transferência perto de zero em alguma ferramenta:
  **ocorreu** em dnstt e tcp-over-dns. Por
  ferramenta: dnstt 0.00% (0/2304); tcp-over-dns 0.33% (5/1502); tuns 6.20% (90/1452). "Perto de zero" é recall de até 1%, limite nosso.
- Muitos valores fora de [0, 1] na transferência: não ocorreu
  (0 valores).
- Recall das ferramentas do HKD maior no retreino sem réplicas que no
  publicado, além do intervalo de confiança: não ocorreu
  (99.42%, de 98.30% a
  99.88%, contra 100.00%, de
  99.96% a 100.00%).
- Métricas de Non-DoH ou de Benign-DoH no retreino longe das de E1: a hipótese
  não fixa a distância, e não há veredito. Recall no teste do combinado sem
  réplicas contra o do CIRA: Non-DoH 99.6752% contra 99.6943%; Benign-DoH 93.3165% contra 92.9114%.

### fiel (profundidade 5)

- Recall na transferência igual ou maior que o do teste do CIRA:
  não ocorreu (1.71% contra 97.91%).
- Recall na transferência perto de zero em alguma ferramenta:
  **ocorreu** em dnstt e tcp-over-dns. Por
  ferramenta: dnstt 0.00% (0/2304); tcp-over-dns 0.00% (0/1502); tuns 6.20% (90/1452). "Perto de zero" é recall de até 1%, limite nosso.
- Muitos valores fora de [0, 1] na transferência: não ocorreu
  (0 valores).
- Recall das ferramentas do HKD maior no retreino sem réplicas que no
  publicado, além do intervalo de confiança: não ocorreu
  (73.29%, de 69.24% a
  77.08%, contra 99.49%, de
  99.34% a 99.62%).
- Métricas de Non-DoH ou de Benign-DoH no retreino longe das de E1: a hipótese
  não fixa a distância, e não há veredito. Recall no teste do combinado sem
  réplicas contra o do CIRA: Non-DoH 99.8258% contra 99.9337%; Benign-DoH 0.0000% contra 0.0000%.
