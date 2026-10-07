# E6: o sistema do artigo no segundo dataset, ao lado do CIRA

Gerado por `scripts/e6_dataset2.py`, a partir dos `metrics.json` de
`results/e6/` e de `results/e1/`. Seed 42, uma execução de cada cenário:
não há média nem desvio padrão.

- **variante (profundidade variável):** sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Detalhe em `variante/RESUMO.md`.
- **fiel (profundidade 5):** profundidade máxima 5 nos submodelos (Seção IV-B). Detalhe em `fiel/RESUMO.md`.

O sistema base desta etapa é o de profundidade variável; o de profundidade 5
vai ao lado. O artigo não traz figura nem tabela para o segundo dataset: o que
fica lado a lado é o resultado no CIRA (E1) e os três cenários abaixo.

- **CIRA (E1):** treino e teste no CIRA-CIC-DoHBrw-2020.
- **Transferência:** treino no CIRA, avaliação nos fluxos do
  DoH-Tunnel-Traffic-HKD. O HKD só tem a classe maliciosa: não há precisão,
  FPR nem acurácia, e neste cenário tudo é teste.
- **Retreino no combinado sem réplicas:** treino e teste no dataset combinado
  CIRA + HKD com cada fluxo do HKD uma única vez. É o dataset principal.
- **Retreino no combinado como publicado:** o mesmo, com as 20 cópias de
  cada fluxo do HKD, que deixam cópias idênticas no treino e no teste.

No combinado, Non-DoH e Benign-DoH são os fluxos do CIRA; só a classe maliciosa
ganha fluxos novos.

## Cenários lado a lado

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

## Recall por ferramenta do HKD

Detectados sobre `n` e intervalo de confiança de 95% entre parênteses.

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
