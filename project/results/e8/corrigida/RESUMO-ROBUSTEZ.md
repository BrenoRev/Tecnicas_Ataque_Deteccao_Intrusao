# E8: robustez à manipulação da duração do fluxo

Gerado por `scripts/e8_robustez_resumo.py` a partir dos arquivos gravados por
`scripts/e8_robustez.py`. Trilha `corrigida`. Dados: CIRA-CIC-DoHBrw-2020,
10 seeds (0 a 9), split 90/10 estratificado refeito em cada seed.
A hipótese, o modelo de ameaça e as simplificações foram escritos antes da
primeira execução, em `HIPOTESE-ROBUSTEZ.md`.

**Como ler este arquivo.** A parte B é uma perturbação no espaço de atributos,
não um ataque reproduzido em rede. Nenhum tráfego foi gerado e nenhum PCAP foi
reprocessado: os fluxos Malicious-DoH do teste tiveram `Duration`, `FlowBytesSent`, `FlowBytesReceived` divididos
por um fator, e os outros atributos ficaram como estavam. Os números da parte
B são um limite aproximado do efeito de encurtar os fluxos, não a medição de
um ataque.

## O que foi medido

- **Modelos.** A é o sistema empilhado do artigo com os Random Forests base
  sem limite de profundidade (o original); M1M2 é o modelo proposto pela equipe,
  um Random Forest único com peso de classe (a modificação); A-prof5, quando
  presente, é o sistema do artigo com profundidade máxima 5, ao lado.
- **Parte A, ablação.** Cada modelo ajustado com todos os atributos (`todos`),
  sem `Duration` (`sem_duration`) e sem `Duration`, `FlowSentRate` e
  `FlowReceivedRate` (`sem_duration_taxas`), avaliado no teste sem perturbação.
- **Parte B, fragmentação.** Os mesmos modelos, sem novo ajuste, predizem os
  fluxos Malicious-DoH do teste com `Duration`, `FlowBytesSent`, `FlowBytesReceived` divididos pelos fatores
  2, 4, 8, 16. As duas taxas de bytes por segundo não mudam,
  porque são os bytes divididos pela duração; o script confere essa relação
  na tabela inteira antes de rodar. O fator 1 é o teste sem perturbação.
- **O que não é tocado.** O treino, o normalizador (ajustado só no treino) e
  os fluxos Non-DoH e Benign-DoH do teste. O FPR não muda com o fator.
- **Hiperparâmetros de M1M2.** Os escolhidos pela seleção já gravada em
  `M1M2-cira/`, no treino da mesma seed e com os 29 atributos. A seleção não
  foi refeita sem as colunas retiradas.
- **Conferência.** Com todos os atributos, a matriz de confusão de cada modelo
  no teste sem perturbação é igual à já gravada para a mesma seed
  (`results/e4/corrigida/` e `M1M2-cira/`); o script para se não for.

Commit e estado da árvore de cada grupo de execuções:

- A, `todos`: commit `1529734`; execuções com a árvore suja: 0.
- A, `sem_duration`: commit `1529734`; execuções com a árvore suja: 0.
- A, `sem_duration_taxas`: commit `1529734`; execuções com a árvore suja: 0.
- M1M2, `todos`: commit `1529734`; execuções com a árvore suja: 0.
- M1M2, `sem_duration`: commit `1529734`; execuções com a árvore suja: 0.
- M1M2, `sem_duration_taxas`: commit `1529734`; execuções com a árvore suja: 0.
- A-prof5, `todos`: commit `1529734`; execuções com a árvore suja: 0.
- A-prof5, `sem_duration`: commit `1529734`; execuções com a árvore suja: 0.
- A-prof5, `sem_duration_taxas`: commit `1529734`; execuções com a árvore suja: 0.

Todo valor é média ± desvio padrão amostral entre as seeds, em percentual,
salvo onde a tabela diz outra unidade. Comparação pareada: comparação pareada por seed: diferença média (primeiro menos segundo), número de seeds em que cada modelo vence e teste de postos sinalizados de Wilcoxon bilateral (scipy.stats.wilcoxon com os parâmetros padrão: diferenças nulas descartadas).
Regra de leitura: uma diferença pareada conta quando a média é, em módulo, maior que o desvio padrão das diferenças entre as seeds; caso contrário os dois lados não se distinguem. Ressalva: os conjuntos de teste das seeds se sobrepõem e são sorteados da mesma tabela: os pares não são independentes, o p-valor é indicativo e não sustenta sozinho a palavra significativo.

## Parte A: ablação no teste sem perturbação

| modelo | colunas | atributos | atributos examinados por divisão | F1 macro | recall de Benign-DoH | recall de Malicious-DoH | FPR de Malicious-DoH | ajuste (s, média) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | `todos` | 29 | 28 | 96.5555 ± 0.1196 | 93.0734 ± 0.5223 | 99.9391 ± 0.0192 | 0.0015 ± 0.0011 | 112.5 |
| A | `sem_duration` | 28 | 28 | 96.5108 ± 0.1947 | 93.1291 ± 0.4427 | 99.9423 ± 0.0159 | 0.0018 ± 0.0016 | 109.6 |
| A | `sem_duration_taxas` | 26 | 26 | 96.4510 ± 0.1691 | 92.9722 ± 0.4849 | 99.9431 ± 0.0146 | 0.0021 ± 0.0014 | 103.6 |
| M1M2 | `todos` | 29 | 5 | 97.0529 ± 0.1547 | 93.6709 ± 0.4792 | 99.9699 ± 0.0159 | 0.0002 ± 0.0005 | 83.7 |
| M1M2 | `sem_duration` | 28 | 5 | 97.0178 ± 0.1814 | 93.8278 ± 0.3379 | 99.9695 ± 0.0133 | 0.0010 ± 0.0012 | 81.9 |
| M1M2 | `sem_duration_taxas` | 26 | 5 | 97.1386 ± 0.1205 | 93.7215 ± 0.3401 | 99.9715 ± 0.0157 | 0.0005 ± 0.0008 | 80.9 |
| A-prof5 | `todos` | 29 | 28 | 65.6727 ± 0.1358 | 0.0000 ± 0.0000 | 97.5191 ± 0.7284 | 0.1241 ± 0.0522 | 39.2 |
| A-prof5 | `sem_duration` | 28 | 28 | 65.4536 ± 0.1727 | 0.1114 ± 0.3183 | 96.2585 ± 0.9654 | 0.1582 ± 0.0741 | 38.2 |
| A-prof5 | `sem_duration_taxas` | 26 | 26 | 65.4536 ± 0.1727 | 0.1114 ± 0.3183 | 96.2585 ± 0.9654 | 0.1582 ± 0.0741 | 35.8 |

"Atributos examinados por divisão" é o que a árvore de fato usa: com 28 ou 26
colunas, os 28 atributos por divisão do artigo (Seção IV-A) passam a ser todas
as colunas, e o sorteio de atributos em cada divisão deixa de existir.

Cada conjunto de colunas contra `todos`, no mesmo modelo, seed a seed:

| modelo | par | métrica | diferença média | desvio padrão das diferenças | seeds com o primeiro maior | seeds com o segundo maior | empates | p-valor de Wilcoxon | o primeiro é |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | `sem_duration` menos `todos` | F1 macro | -0.0447 pp | 0.1154 pp | 4 | 6 | 0 | 0.2754 | **não se distinguem** |
| A | `sem_duration` menos `todos` | recall de Benign-DoH | +0.0557 pp | 0.2663 pp | 5 | 5 | 0 | 0.7109 | **não se distinguem** |
| A | `sem_duration` menos `todos` | recall de Malicious-DoH | +0.0032 pp | 0.0105 pp | 5 | 4 | 1 | 0.4258 | **não se distinguem** |
| A | `sem_duration` menos `todos` | FPR de Malicious-DoH | +0.0002 pp | 0.0011 pp | 5 | 2 | 3 | 0.6562 | **não se distinguem** |
| A | `sem_duration_taxas` menos `todos` | F1 macro | -0.1045 pp | 0.0896 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` menos `todos` | recall de Benign-DoH | -0.1013 pp | 0.1754 pp | 2 | 8 | 0 | 0.1270 | **não se distinguem** |
| A | `sem_duration_taxas` menos `todos` | recall de Malicious-DoH | +0.0040 pp | 0.0065 pp | 7 | 2 | 1 | 0.1250 | **não se distinguem** |
| A | `sem_duration_taxas` menos `todos` | FPR de Malicious-DoH | +0.0005 pp | 0.0014 pp | 6 | 2 | 2 | 0.2734 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | F1 macro | -0.0351 pp | 0.0689 pp | 4 | 6 | 0 | 0.1934 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | recall de Benign-DoH | +0.1570 pp | 0.1871 pp | 6 | 1 | 3 | 0.0469 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | recall de Malicious-DoH | -0.0004 pp | 0.0044 pp | 4 | 4 | 2 | 1.0000 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | FPR de Malicious-DoH | +0.0008 pp | 0.0009 pp | 5 | 0 | 5 | 0.0625 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | F1 macro | +0.0857 pp | 0.0691 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 | `sem_duration_taxas` menos `todos` | recall de Benign-DoH | +0.0506 pp | 0.2161 pp | 4 | 5 | 1 | 0.8164 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | recall de Malicious-DoH | +0.0016 pp | 0.0043 pp | 3 | 1 | 6 | 0.5000 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | FPR de Malicious-DoH | +0.0003 pp | 0.0005 pp | 3 | 0 | 7 | 0.2500 | **não se distinguem** |
| A-prof5 | `sem_duration` menos `todos` | F1 macro | -0.2190 pp | 0.2187 pp | 1 | 9 | 0 | 0.0098 | **menor** |
| A-prof5 | `sem_duration` menos `todos` | recall de Benign-DoH | +0.1114 pp | 0.3183 pp | 2 | 0 | 8 | 0.5000 | **não se distinguem** |
| A-prof5 | `sem_duration` menos `todos` | recall de Malicious-DoH | -1.2607 pp | 1.2701 pp | 1 | 9 | 0 | 0.0137 | **não se distinguem** |
| A-prof5 | `sem_duration` menos `todos` | FPR de Malicious-DoH | +0.0341 pp | 0.0672 pp | 7 | 3 | 0 | 0.2754 | **não se distinguem** |
| A-prof5 | `sem_duration_taxas` menos `todos` | F1 macro | -0.2190 pp | 0.2187 pp | 1 | 9 | 0 | 0.0098 | **menor** |
| A-prof5 | `sem_duration_taxas` menos `todos` | recall de Benign-DoH | +0.1114 pp | 0.3183 pp | 2 | 0 | 8 | 0.5000 | **não se distinguem** |
| A-prof5 | `sem_duration_taxas` menos `todos` | recall de Malicious-DoH | -1.2607 pp | 1.2701 pp | 1 | 9 | 0 | 0.0137 | **não se distinguem** |
| A-prof5 | `sem_duration_taxas` menos `todos` | FPR de Malicious-DoH | +0.0341 pp | 0.0672 pp | 7 | 3 | 0 | 0.2754 | **não se distinguem** |

Nota acrescentada depois da execução. A-prof5: `sem_duration` e `sem_duration_taxas` têm a mesma matriz de confusão no teste sem perturbação nas 10 seeds, e por isso as linhas dos dois são iguais nas tabelas desta parte. Os dois modelos não são o mesmo: as predições dos fluxos fragmentados diferem em 3 seeds.

## Parte B: a perturbação

Descrição dos fluxos Malicious-DoH do teste depois da fragmentação. Não
depende do modelo. A faixa do treino é a do normalizador: valor abaixo do
mínimo ou acima do máximo que o atributo tem no treino da seed.

| fator | mediana da duração dos maliciosos (s) | fluxos maliciosos com algum valor fora da faixa do treino (%) | valores fora da faixa, entre todos os valores dos fluxos maliciosos (%) | fluxos fora da faixa, por atributo | fluxos com tempo médio de pacote maior que a duração (%) |
| --- | --- | --- | --- | --- | --- |
| 1 | 34.07 | 0.001 ± 0.002 | 0.0000 ± 0.0001 | `PacketTimeMode` 0.1, `ResponseTimeTimeMode` 0.1 | 0.000 ± 0.000 |
| 2 | 17.04 | 0.270 ± 0.020 | 0.0111 ± 0.0011 | `FlowBytesReceived` 67.2, `FlowBytesSent` 12.6, `PacketTimeMode` 0.1, `ResponseTimeTimeMode` 0.1 | 29.668 ± 0.202 |
| 4 | 8.52 | 0.698 ± 0.043 | 0.0449 ± 0.0030 | `FlowBytesReceived` 173.2, `FlowBytesSent` 151.7, `PacketTimeMode` 0.1, `ResponseTimeTimeMode` 0.1 | 69.384 ± 0.253 |
| 8 | 4.26 | 2.319 ± 0.082 | 0.1251 ± 0.0054 | `Duration` 0.1, `FlowBytesReceived` 525.9, `FlowBytesSent` 379.3, `PacketTimeMode` 0.1, `ResponseTimeTimeMode` 0.1 | 96.496 ± 0.070 |
| 16 | 2.13 | 8.906 ± 0.216 | 0.5706 ± 0.0142 | `Duration` 0.4, `FlowBytesReceived` 2166.2, `FlowBytesSent` 1962.3, `PacketTimeMode` 0.1, `ResponseTimeTimeMode` 0.1 | 99.901 ± 0.019 |

A última coluna mede a incoerência que a simplificação cria. Nos fluxos do
conjunto de dados o tempo médio de pacote não passa da duração. Isso é
observação dos dados, não leitura do código do extrator: no fator 1, que é o
teste sem perturbação, a coluna é 0.000 ± 0.000%;
e, em conferência feita à parte na tabela limpa do CIRA, que não é gravada em
`results/`, em nenhuma linha a média, a mediana ou a moda do tempo de pacote
passa da duração. Como as estatísticas por pacote não foram recalculadas, o
vetor perturbado deixa de respeitar isso.

## Parte B: recall de Malicious-DoH por fator de fragmentação

Média ± desvio padrão entre as seeds e, entre parênteses, o menor valor entre
as seeds. O mínimo e esta nota de leitura foram acrescentados depois da
execução, sem mudar a regra nem os vereditos. Onde o mínimo fica longe da
média, o modelo cede em algumas seeds
muito mais que nas outras, e a regra de leitura, que compara a média com o
desvio, pode dizer "não se distinguem" para uma queda que existe em todas as
seeds: as colunas de contagem de seeds das tabelas pareadas mostram isso.

| modelo | colunas | fator 1 (sem perturbação) | fator 2 | fator 4 | fator 8 | fator 16 |
| --- | --- | --- | --- | --- | --- | --- |
| A | `todos` | 99.939 ± 0.019 (mín. 99.908) | 96.753 ± 0.759 (mín. 95.820) | 95.414 ± 0.145 (mín. 95.231) | 95.036 ± 0.150 (mín. 94.859) | 94.704 ± 0.193 (mín. 94.498) |
| A | `sem_duration` | 99.942 ± 0.016 (mín. 99.912) | 95.751 ± 0.761 (mín. 94.819) | 94.144 ± 0.165 (mín. 93.889) | 93.063 ± 0.174 (mín. 92.771) | 92.519 ± 0.151 (mín. 92.246) |
| A | `sem_duration_taxas` | 99.943 ± 0.015 (mín. 99.920) | 95.794 ± 0.698 (mín. 94.887) | 94.103 ± 0.193 (mín. 93.881) | 93.025 ± 0.313 (mín. 92.551) | 92.484 ± 0.417 (mín. 91.745) |
| M1M2 | `todos` | 99.970 ± 0.016 (mín. 99.932) | 99.628 ± 0.349 (mín. 98.918) | 92.749 ± 10.899 (mín. 70.399) | 91.299 ± 10.142 (mín. 72.250) | 90.986 ± 9.674 (mín. 71.813) |
| M1M2 | `sem_duration` | 99.970 ± 0.013 (mín. 99.936) | 99.954 ± 0.018 (mín. 99.916) | 99.196 ± 0.158 (mín. 98.970) | 98.486 ± 0.222 (mín. 98.097) | 97.798 ± 0.806 (mín. 95.660) |
| M1M2 | `sem_duration_taxas` | 99.972 ± 0.016 (mín. 99.932) | 99.948 ± 0.020 (mín. 99.908) | 99.115 ± 0.297 (mín. 98.349) | 97.957 ± 1.457 (mín. 93.929) | 95.764 ± 6.226 (mín. 78.125) |
| A-prof5 | `todos` | 97.519 ± 0.728 (mín. 95.512) | 93.149 ± 0.701 (mín. 91.164) | 92.936 ± 0.886 (mín. 91.008) | 92.936 ± 0.886 (mín. 91.008) | 92.936 ± 0.886 (mín. 91.008) |
| A-prof5 | `sem_duration` | 96.258 ± 0.965 (mín. 94.414) | 96.105 ± 0.990 (mín. 94.194) | 96.106 ± 0.965 (mín. 94.182) | 96.037 ± 0.920 (mín. 94.182) | 95.982 ± 0.892 (mín. 94.182) |
| A-prof5 | `sem_duration_taxas` | 96.258 ± 0.965 (mín. 94.414) | 96.091 ± 0.982 (mín. 94.194) | 96.079 ± 0.979 (mín. 94.182) | 96.013 ± 0.936 (mín. 94.182) | 95.970 ± 0.916 (mín. 94.182) |

Para onde vão os fluxos Malicious-DoH, em número de fluxos por seed:

| modelo | colunas | fator | fluxos Malicious-DoH no teste | preditos como Non-DoH | preditos como Benign-DoH | preditos como Malicious-DoH |
| --- | --- | --- | --- | --- | --- | --- |
| A | `todos` | 1 | 24955.0 | 7.9 ± 3.7 | 7.3 ± 3.5 | 24939.8 ± 4.8 |
| A | `todos` | 2 | 24955.0 | 362.3 ± 132.1 | 448.1 ± 228.2 | 24144.6 ± 189.5 |
| A | `todos` | 4 | 24955.0 | 871.0 ± 135.1 | 273.5 ± 137.1 | 23810.5 ± 36.2 |
| A | `todos` | 8 | 24955.0 | 970.0 ± 169.4 | 268.7 ± 175.3 | 23716.3 ± 37.4 |
| A | `todos` | 16 | 24955.0 | 1082.2 ± 155.5 | 239.5 ± 158.6 | 23633.3 ± 48.1 |
| A | `sem_duration` | 1 | 24955.0 | 8.0 ± 3.0 | 6.4 ± 2.5 | 24940.6 ± 4.0 |
| A | `sem_duration` | 2 | 24955.0 | 753.8 ± 68.7 | 306.5 ± 172.7 | 23894.7 ± 190.0 |
| A | `sem_duration` | 4 | 24955.0 | 1308.4 ± 48.5 | 152.9 ± 50.9 | 23493.7 ± 41.2 |
| A | `sem_duration` | 8 | 24955.0 | 1475.1 ± 63.4 | 256.0 ± 60.2 | 23223.9 ± 43.5 |
| A | `sem_duration` | 16 | 24955.0 | 1613.9 ± 85.0 | 252.9 ± 83.5 | 23088.2 ± 37.6 |
| A | `sem_duration_taxas` | 1 | 24955.0 | 8.6 ± 3.2 | 5.6 ± 1.0 | 24940.8 ± 3.6 |
| A | `sem_duration_taxas` | 2 | 24955.0 | 675.4 ± 129.8 | 374.3 ± 222.2 | 23905.3 ± 174.1 |
| A | `sem_duration_taxas` | 4 | 24955.0 | 1221.9 ± 337.3 | 249.6 ± 326.6 | 23483.5 ± 48.1 |
| A | `sem_duration_taxas` | 8 | 24955.0 | 1393.4 ± 359.7 | 347.2 ± 349.3 | 23214.4 ± 78.2 |
| A | `sem_duration_taxas` | 16 | 24955.0 | 1559.9 ± 371.7 | 315.7 ± 342.4 | 23079.4 ± 104.0 |
| M1M2 | `todos` | 1 | 24955.0 | 7.4 ± 4.0 | 0.1 ± 0.3 | 24947.5 ± 4.0 |
| M1M2 | `todos` | 2 | 24955.0 | 92.8 ± 87.0 | 0.0 ± 0.0 | 24862.2 ± 87.0 |
| M1M2 | `todos` | 4 | 24955.0 | 1809.5 ± 2719.9 | 0.0 ± 0.0 | 23145.5 ± 2719.9 |
| M1M2 | `todos` | 8 | 24955.0 | 2171.3 ± 2530.9 | 0.0 ± 0.0 | 22783.7 ± 2530.9 |
| M1M2 | `todos` | 16 | 24955.0 | 2249.4 ± 2414.2 | 0.0 ± 0.0 | 22705.6 ± 2414.2 |
| M1M2 | `sem_duration` | 1 | 24955.0 | 7.5 ± 3.4 | 0.1 ± 0.3 | 24947.4 ± 3.3 |
| M1M2 | `sem_duration` | 2 | 24955.0 | 11.5 ± 4.6 | 0.0 ± 0.0 | 24943.5 ± 4.6 |
| M1M2 | `sem_duration` | 4 | 24955.0 | 200.7 ± 39.4 | 0.0 ± 0.0 | 24754.3 ± 39.4 |
| M1M2 | `sem_duration` | 8 | 24955.0 | 377.9 ± 55.3 | 0.0 ± 0.0 | 24577.1 ± 55.3 |
| M1M2 | `sem_duration` | 16 | 24955.0 | 549.6 ± 201.2 | 0.0 ± 0.0 | 24405.4 ± 201.2 |
| M1M2 | `sem_duration_taxas` | 1 | 24955.0 | 7.0 ± 4.0 | 0.1 ± 0.3 | 24947.9 ± 3.9 |
| M1M2 | `sem_duration_taxas` | 2 | 24955.0 | 13.0 ± 4.9 | 0.0 ± 0.0 | 24942.0 ± 4.9 |
| M1M2 | `sem_duration_taxas` | 4 | 24955.0 | 220.8 ± 74.2 | 0.0 ± 0.0 | 24734.2 ± 74.2 |
| M1M2 | `sem_duration_taxas` | 8 | 24955.0 | 509.9 ± 363.7 | 0.0 ± 0.0 | 24445.1 ± 363.7 |
| M1M2 | `sem_duration_taxas` | 16 | 24955.0 | 1057.2 ± 1553.7 | 0.0 ± 0.0 | 23897.8 ± 1553.7 |
| A-prof5 | `todos` | 1 | 24955.0 | 615.1 ± 183.7 | 4.0 ± 11.6 | 24335.9 ± 181.8 |
| A-prof5 | `todos` | 2 | 24955.0 | 1699.8 ± 179.3 | 9.8 ± 15.8 | 23245.4 ± 174.9 |
| A-prof5 | `todos` | 4 | 24955.0 | 1752.1 ± 227.1 | 10.6 ± 16.8 | 23192.3 ± 221.1 |
| A-prof5 | `todos` | 8 | 24955.0 | 1752.1 ± 227.1 | 10.6 ± 16.8 | 23192.3 ± 221.1 |
| A-prof5 | `todos` | 16 | 24955.0 | 1752.1 ± 227.1 | 10.6 ± 16.8 | 23192.3 ± 221.1 |
| A-prof5 | `sem_duration` | 1 | 24955.0 | 932.9 ± 241.2 | 0.8 ± 2.5 | 24021.3 ± 240.9 |
| A-prof5 | `sem_duration` | 2 | 24955.0 | 967.8 ± 248.5 | 4.1 ± 13.0 | 23983.1 ± 247.0 |
| A-prof5 | `sem_duration` | 4 | 24955.0 | 967.5 ± 242.5 | 4.3 ± 13.6 | 23983.2 ± 240.9 |
| A-prof5 | `sem_duration` | 8 | 24955.0 | 988.0 ± 229.9 | 1.0 ± 3.2 | 23966.0 ± 229.5 |
| A-prof5 | `sem_duration` | 16 | 24955.0 | 1001.9 ± 223.0 | 0.8 ± 2.5 | 23952.3 ± 222.6 |
| A-prof5 | `sem_duration_taxas` | 1 | 24955.0 | 932.9 ± 241.2 | 0.8 ± 2.5 | 24021.3 ± 240.9 |
| A-prof5 | `sem_duration_taxas` | 2 | 24955.0 | 974.7 ± 245.3 | 0.9 ± 2.8 | 23979.4 ± 245.0 |
| A-prof5 | `sem_duration_taxas` | 4 | 24955.0 | 977.8 ± 244.7 | 0.8 ± 2.5 | 23976.4 ± 244.4 |
| A-prof5 | `sem_duration_taxas` | 8 | 24955.0 | 994.1 ± 233.8 | 0.8 ± 2.5 | 23960.1 ± 233.5 |
| A-prof5 | `sem_duration_taxas` | 16 | 24955.0 | 1005.0 ± 229.1 | 0.8 ± 2.5 | 23949.2 ± 228.7 |

Cada fator contra o fator 1, no mesmo modelo (o primeiro lado é o fator
perturbado; "menor" quer dizer que o modelo degrada nesse fator):

| modelo | colunas | fator | diferença média | desvio padrão das diferenças | seeds com o primeiro maior | seeds com o segundo maior | empates | p-valor de Wilcoxon | o primeiro é |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | `todos` | 2 | -3.1865 pp | 0.7511 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `todos` | 4 | -4.5253 pp | 0.1365 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `todos` | 8 | -4.9028 pp | 0.1435 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `todos` | 16 | -5.2354 pp | 0.1849 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration` | 2 | -4.1911 pp | 0.7565 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration` | 4 | -5.7980 pp | 0.1676 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration` | 8 | -6.8792 pp | 0.1733 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration` | 16 | -7.4230 pp | 0.1523 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` | 2 | -4.1495 pp | 0.6938 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` | 4 | -5.8397 pp | 0.1885 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` | 8 | -6.9181 pp | 0.3105 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` | 16 | -7.4590 pp | 0.4143 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `todos` | 2 | -0.3418 pp | 0.3511 pp | 0 | 10 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `todos` | 4 | -7.2210 pp | 10.9001 pp | 0 | 10 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `todos` | 8 | -8.6708 pp | 10.1445 pp | 0 | 10 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `todos` | 16 | -8.9838 pp | 9.6779 pp | 0 | 10 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `sem_duration` | 2 | -0.0156 pp | 0.0099 pp | 0 | 9 | 1 | 0.0039 | **menor** |
| M1M2 | `sem_duration` | 4 | -0.7738 pp | 0.1613 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration` | 8 | -1.4839 pp | 0.2156 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration` | 16 | -2.1719 pp | 0.8006 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration_taxas` | 2 | -0.0236 pp | 0.0125 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration_taxas` | 4 | -0.8563 pp | 0.3004 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration_taxas` | 8 | -2.0148 pp | 1.4606 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration_taxas` | 16 | -4.2080 pp | 6.2289 pp | 0 | 10 | 0 | 0.0020 | **não se distinguem** |
| A-prof5 | `todos` | 2 | -4.3699 pp | 0.1847 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `todos` | 4 | -4.5826 pp | 0.5796 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `todos` | 8 | -4.5826 pp | 0.5796 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `todos` | 16 | -4.5826 pp | 0.5796 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration` | 2 | -0.1531 pp | 0.0514 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration` | 4 | -0.1527 pp | 0.0659 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration` | 8 | -0.2216 pp | 0.1636 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration` | 16 | -0.2765 pp | 0.2445 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration_taxas` | 2 | -0.1679 pp | 0.0219 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration_taxas` | 4 | -0.1799 pp | 0.0275 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration_taxas` | 8 | -0.2452 pp | 0.1438 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A-prof5 | `sem_duration_taxas` | 16 | -0.2889 pp | 0.2353 pp | 0 | 10 | 0 | 0.0020 | **menor** |

M1M2 menos A, com as mesmas colunas, em cada fator:

| par | colunas | fator | diferença média | desvio padrão das diferenças | seeds com o primeiro maior | seeds com o segundo maior | empates | p-valor de Wilcoxon | o primeiro é |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1M2 menos A | `todos` | 1 | +0.0309 pp | 0.0161 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `todos` | 2 | +2.8756 pp | 0.7249 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `todos` | 4 | -2.6648 pp | 10.8191 pp | 8 | 2 | 0 | 0.4316 | **não se distinguem** |
| M1M2 menos A | `todos` | 8 | -3.7371 pp | 10.0581 pp | 7 | 3 | 0 | 1.0000 | **não se distinguem** |
| M1M2 menos A | `todos` | 16 | -3.7175 pp | 9.6371 pp | 7 | 3 | 0 | 1.0000 | **não se distinguem** |
| M1M2 menos A | `sem_duration` | 1 | +0.0272 pp | 0.0175 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration` | 2 | +4.2028 pp | 0.7624 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration` | 4 | +5.0515 pp | 0.2233 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration` | 8 | +5.4226 pp | 0.2094 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration` | 16 | +5.2783 pp | 0.8678 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration_taxas` | 1 | +0.0285 pp | 0.0108 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration_taxas` | 2 | +4.1543 pp | 0.6983 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration_taxas` | 4 | +5.0118 pp | 0.3370 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration_taxas` | 8 | +4.9317 pp | 1.3158 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| M1M2 menos A | `sem_duration_taxas` | 16 | +3.2795 pp | 5.9783 pp | 9 | 1 | 0 | 0.0840 | **não se distinguem** |

Cada conjunto de colunas contra `todos`, no mesmo modelo, em cada fator:

| modelo | par | fator | diferença média | desvio padrão das diferenças | seeds com o primeiro maior | seeds com o segundo maior | empates | p-valor de Wilcoxon | o primeiro é |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | `sem_duration` menos `todos` | 2 | -1.0014 pp | 0.6953 pp | 1 | 9 | 0 | 0.0039 | **menor** |
| A | `sem_duration` menos `todos` | 4 | -1.2695 pp | 0.1419 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration` menos `todos` | 8 | -1.9732 pp | 0.1509 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration` menos `todos` | 16 | -2.1843 pp | 0.1717 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` menos `todos` | 2 | -0.9589 pp | 0.7428 pp | 1 | 9 | 0 | 0.0098 | **menor** |
| A | `sem_duration_taxas` menos `todos` | 4 | -1.3104 pp | 0.1209 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` menos `todos` | 8 | -2.0112 pp | 0.2606 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| A | `sem_duration_taxas` menos `todos` | 16 | -2.2196 pp | 0.3624 pp | 0 | 10 | 0 | 0.0020 | **menor** |
| M1M2 | `sem_duration` menos `todos` | 2 | +0.3258 pp | 0.3526 pp | 10 | 0 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | 4 | +6.4468 pp | 10.9436 pp | 10 | 0 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | 8 | +7.1865 pp | 10.2383 pp | 10 | 0 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `sem_duration` menos `todos` | 16 | +6.8115 pp | 9.9337 pp | 9 | 1 | 0 | 0.0039 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | 2 | +0.3198 pp | 0.3480 pp | 10 | 0 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | 4 | +6.3663 pp | 10.8944 pp | 10 | 0 | 0 | 0.0020 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | 8 | +6.6576 pp | 10.3501 pp | 9 | 1 | 0 | 0.0371 | **não se distinguem** |
| M1M2 | `sem_duration_taxas` menos `todos` | 16 | +4.7774 pp | 12.1538 pp | 9 | 1 | 0 | 0.0488 | **não se distinguem** |
| A-prof5 | `sem_duration` menos `todos` | 2 | +2.9561 pp | 1.2689 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration` menos `todos` | 4 | +3.1693 pp | 1.0410 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration` menos `todos` | 8 | +3.1004 pp | 1.0252 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration` menos `todos` | 16 | +3.0455 pp | 1.0239 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration_taxas` menos `todos` | 2 | +2.9413 pp | 1.2672 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration_taxas` menos `todos` | 4 | +3.1421 pp | 1.0688 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration_taxas` menos `todos` | 8 | +3.0767 pp | 1.0522 pp | 10 | 0 | 0 | 0.0020 | **maior** |
| A-prof5 | `sem_duration_taxas` menos `todos` | 16 | +3.0331 pp | 1.0514 pp | 10 | 0 | 0 | 0.0020 | **maior** |

## Hipótese ao lado do resultado

Expectativas de `HIPOTESE-ROBUSTEZ.md`:

1. Parte A, A: sem as colunas, F1 macro e recall de Malicious-DoH não se distinguem dos do modelo com todos os atributos ou caem menos de 1 pp: **ocorreu**. Menor diferença média de F1 macro, sem as colunas menos com todas: -0.1045 pp.
2. Parte A, M1M2: sem as colunas, F1 macro e recall de Malicious-DoH não se distinguem dos do modelo com todos os atributos ou caem menos de 1 pp: **ocorreu**. Menor diferença média de F1 macro, sem as colunas menos com todas: -0.0351 pp.
3. Parte B, A com todos os atributos degrada em todos os fatores a partir de 2: **ocorreu** (degrada nos fatores 2, 4, 8, 16); o recall não aumenta de um fator para o seguinte: **ocorreu**.
4. Parte B, M1M2 com todos os atributos degrada em todos os fatores a partir de 2: não ocorreu (pela regra, degrada em nenhum fator); resiste melhor que A em todos eles: não ocorreu (recall maior no fator 2, menor em nenhum fator). Estes são os vereditos da regra de leitura; o recall de M1M2 em cada seed e a contagem das quedas estão na leitura descritiva, abaixo.
5. Parte B, os modelos sem `Duration` resistem melhor que o mesmo modelo com todos os atributos: não ocorreu (recall maior em 0 das 16 comparações de A e M1M2, menor em 8); e não ficam imunes: **ocorreu** (degradam em 15 das 16 combinações de modelo, colunas e fator). A-prof5 fica fora dessas contagens, porque a hipótese só declara expectativa para A e M1M2; os três modelos estão, em separado, na leitura descritiva, abaixo.
6. Os fluxos não detectados vão mais para Non-DoH do que para Benign-DoH: **ocorreu**. Somando A e M1M2 com todos os atributos nos fatores a partir de 2, a média por seed é de 9608.5 fluxos preditos como Non-DoH e 1229.8 como Benign-DoH.

Resultados que a hipótese declarou como inesperados:

- A perder mais de 1 pp de F1 macro sem `Duration` no teste sem perturbação: não ocorreu.
- M1M2 perder mais de 1 pp de F1 macro sem `Duration` no teste sem perturbação: não ocorreu.
- Nenhum modelo degradar em nenhum fator: não ocorreu.
- O recall médio de um modelo subir de um fator para o seguinte: **ocorreu** (A-prof5 `sem_duration`). O item fala da média. Olhando cada seed, na leitura descritiva acrescentada depois da execução, o recall sobe em: M1M2 `todos`, seed 3, do fator 4 para o 8 (+1.31 pp); M1M2 `todos`, seed 9, do fator 4 para o 8 (+1.85 pp); M1M2 `todos`, seed 9, do fator 8 para o 16 (+17.32 pp); A-prof5 `sem_duration`, seed 6, do fator 2 para o 4 (+0.11 pp).
- M1M2 resistir pior que A: não ocorreu. É o veredito da regra; pela leitura descritiva, abaixo, nenhuma direção é sustentada.
- Um modelo sem `Duration` resistir pior que o mesmo modelo com todos os atributos: **ocorreu** (8 das 16 comparações).
- A maior parte dos fluxos não detectados ir para Benign-DoH: não ocorreu.

## Leitura descritiva acrescentada depois da execução

Tudo nesta seção é leitura descritiva acrescentada depois da execução: não faz parte da hipótese, não muda a regra de leitura nem os vereditos dela, e os limiares que usa foram escolhidos com os resultados à vista. Os números saem dos mesmos
`metrics.json`; nenhuma execução foi refeita. O mínimo entre as seeds e a nota
de leitura da tabela de recall por fator também foram acrescentados depois da
execução, sem mudar a regra nem os vereditos.

### Recall de M1M2 com todos os atributos, em cada seed

Em percentual. A regra de leitura diz "não se distinguem" quando a média não
passa do desvio; a tabela mostra o que há por trás da média.

| seed | fator 1 | fator 2 | fator 4 | fator 8 | fator 16 |
| --- | --- | --- | --- | --- | --- |
| 0 | 99.98 | 99.07 | 98.14 | 97.42 | 96.39 |
| 1 | 99.96 | 99.78 | 97.83 | 97.48 | 96.28 |
| 2 | 99.93 | 99.82 | 97.95 | 97.19 | 96.25 |
| 3 | 99.97 | 99.64 | 73.86 | 75.18 | 71.81 |
| 4 | 99.97 | 99.82 | 98.04 | 97.70 | 97.01 |
| 5 | 99.97 | 99.87 | 98.04 | 97.72 | 97.28 |
| 6 | 99.98 | 99.60 | 97.36 | 96.66 | 95.30 |
| 7 | 99.99 | 99.91 | 98.05 | 97.05 | 95.50 |
| 8 | 99.98 | 99.85 | 97.81 | 84.34 | 74.47 |
| 9 | 99.97 | 98.92 | 70.40 | 72.25 | 89.57 |

- Fator 2: o recall é menor que o do fator 1 em 10 das 10 seeds; fica abaixo de 90% em 0; nas 10, vai de 98.92% a 99.91%.
- Fator 4: o recall é menor que o do fator 1 em 10 das 10 seeds; fica abaixo de 90% em 2 (seeds 3, 9); nas demais, vai de 97.36% a 98.14%.
- Fator 8: o recall é menor que o do fator 1 em 10 das 10 seeds; fica abaixo de 90% em 3 (seeds 3, 8, 9); nas demais, vai de 96.66% a 97.72%.
- Fator 16: o recall é menor que o do fator 1 em 10 das 10 seeds; fica abaixo de 90% em 3 (seeds 3, 8, 9); nas demais, vai de 95.30% a 97.28%.

O limiar de 90% é descritivo e foi escolhido depois de ver os
resultados: com outro limiar, a contagem muda.

M1M2 contra A, com todos os atributos: pela regra, o recall de M1M2 é maior no fator 2 e menor em nenhum fator. Seed a seed, M1M2 fica acima ou abaixo de A assim: fator 2, acima em 10 seeds e abaixo em 0; fator 4, acima em 8 seeds e abaixo em 2; fator 8, acima em 7 seeds e abaixo em 3; fator 16, acima em 7 seeds e abaixo em 3. Nenhuma direção é sustentada: a modificação não é nem mais robusta, nem menos, que o original.

### Retirar `Duration`, modelo a modelo

Recall de Malicious-DoH sem as colunas menos o do mesmo modelo com todas, em
cada fator. A hipótese só fala de A e M1M2; aqui estão os três modelos.

| modelo | par | fator | diferença média | seeds com recall maior sem as colunas | seeds com recall menor sem as colunas | menor diferença entre as seeds | maior diferença entre as seeds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `sem_duration` menos `todos` | 2 | -1.0014 pp | 1 | 9 | -2.1118 pp | +0.7053 pp |
| A | `sem_duration` menos `todos` | 4 | -1.2695 pp | 0 | 10 | -1.5388 pp | -1.1380 pp |
| A | `sem_duration` menos `todos` | 8 | -1.9732 pp | 0 | 10 | -2.2200 pp | -1.6951 pp |
| A | `sem_duration` menos `todos` | 16 | -2.1843 pp | 0 | 10 | -2.4444 pp | -1.9074 pp |
| A | `sem_duration_taxas` menos `todos` | 2 | -0.9589 pp | 1 | 9 | -2.0437 pp | +0.3206 pp |
| A | `sem_duration_taxas` menos `todos` | 4 | -1.3104 pp | 0 | 10 | -1.5107 pp | -1.1260 pp |
| A | `sem_duration_taxas` menos `todos` | 8 | -2.0112 pp | 0 | 10 | -2.3643 pp | -1.5508 pp |
| A | `sem_duration_taxas` menos `todos` | 16 | -2.2196 pp | 0 | 10 | -2.7930 pp | -1.5067 pp |
| M1M2 | `sem_duration` menos `todos` | 2 | +0.3258 pp | 10 | 0 | +0.0641 pp | +1.0459 pp |
| M1M2 | `sem_duration` menos `todos` | 4 | +6.4468 pp | 10 | 0 | +0.9978 pp | +29.0683 pp |
| M1M2 | `sem_duration` menos `todos` | 8 | +7.1865 pp | 10 | 0 | +0.6171 pp | +26.4436 pp |
| M1M2 | `sem_duration` menos `todos` | 16 | +6.8115 pp | 9 | 1 | -0.6171 pp | +26.1871 pp |
| M1M2 | `sem_duration_taxas` menos `todos` | 2 | +0.3198 pp | 10 | 0 | +0.0601 pp | +1.0339 pp |
| M1M2 | `sem_duration_taxas` menos `todos` | 4 | +6.3663 pp | 10 | 0 | +0.5410 pp | +28.6235 pp |
| M1M2 | `sem_duration_taxas` menos `todos` | 8 | +6.6576 pp | 9 | 1 | -2.7289 pp | +25.9667 pp |
| M1M2 | `sem_duration_taxas` menos `todos` | 16 | +4.7774 pp | 9 | 1 | -17.1749 pp | +25.9026 pp |
| A-prof5 | `sem_duration` menos `todos` | 2 | +2.9561 pp | 10 | 0 | +0.8375 pp | +5.2014 pp |
| A-prof5 | `sem_duration` menos `todos` | 4 | +3.1693 pp | 10 | 0 | +1.0339 pp | +5.3176 pp |
| A-prof5 | `sem_duration` menos `todos` | 8 | +3.1004 pp | 10 | 0 | +1.0339 pp | +5.3136 pp |
| A-prof5 | `sem_duration` menos `todos` | 16 | +3.0455 pp | 10 | 0 | +1.0339 pp | +5.3136 pp |
| A-prof5 | `sem_duration_taxas` menos `todos` | 2 | +2.9413 pp | 10 | 0 | +0.8375 pp | +5.2014 pp |
| A-prof5 | `sem_duration_taxas` menos `todos` | 4 | +3.1421 pp | 10 | 0 | +0.9096 pp | +5.3176 pp |
| A-prof5 | `sem_duration_taxas` menos `todos` | 8 | +3.0767 pp | 10 | 0 | +0.9096 pp | +5.3136 pp |
| A-prof5 | `sem_duration_taxas` menos `todos` | 16 | +3.0331 pp | 10 | 0 | +0.9096 pp | +5.3136 pp |

- A: diferença média positiva em 0 das 8 comparações (de -2.22 a -0.96 pp); recall maior sem as colunas em 0 a 1 das 10 seeds, conforme a comparação; menor diferença em uma seed, -2.79 pp. Vereditos da regra: maior em 0, menor em 8, não se distinguem em 0.
- M1M2: diferença média positiva em 8 das 8 comparações (de +0.32 a +7.19 pp); recall maior sem as colunas em 9 a 10 das 10 seeds, conforme a comparação; menor diferença em uma seed, -17.17 pp. Vereditos da regra: maior em 0, menor em 0, não se distinguem em 8.
- A-prof5: diferença média positiva em 8 das 8 comparações (de +2.94 a +3.17 pp); recall maior sem as colunas em 10 das 10 seeds, conforme a comparação; menor diferença em uma seed, +0.84 pp. Vereditos da regra: maior em 8, menor em 0, não se distinguem em 0.

O efeito tem sinais opostos: retirar as colunas aumenta o recall sob fragmentação em M1M2 e A-prof5 e diminui em A. A causa não foi investigada.

### A incoerência dos vetores e o que se pode ler

Fração dos vetores Malicious-DoH do teste com tempo médio de pacote maior que a duração, média entre as seeds: fator 2, 29.67%; fator 4, 69.38%; fator 8, 96.50%; fator 16, 99.90%. A maioria dos vetores continua coerente só no fator 2; aí, a diferença de recall para o fator 1, com todos os atributos, é: A, fator 2, -3.19 pp; M1M2, fator 2, -0.34 pp. Com mais de 90% dos vetores incoerentes, o que ocorre nos fatores 8, 16, o recall descreve o modelo fora da região de fluxos possíveis, e não a resposta dele a fluxos fragmentados.

A relação entre a incoerência e o colapso de M1M2 em algumas seeds não foi investigada. A fração incoerente é quase a mesma em todas as seeds (desvio padrão de no máximo 0.25 pp), e o recall de M1M2 com todos os atributos tem desvio padrão de até 10.90 pp: o que muda de uma seed para outra é o split e o modelo ajustado, não a proporção de vetores incoerentes.

### Destino dos fluxos não detectados, por fator

O item 6 da hipótese soma os fatores. Por fator, com todos os atributos, a média por seed de fluxos preditos como Non-DoH e como Benign-DoH é: A, fator 2, 362.3 e 448.1; A, fator 4, 871.0 e 273.5; A, fator 8, 970.0 e 268.7; A, fator 16, 1082.2 e 239.5; M1M2, fator 2, 92.8 e 0.0; M1M2, fator 4, 1809.5 e 0.0; M1M2, fator 8, 2171.3 e 0.0; M1M2, fator 16, 2249.4 e 0.0. Vão mais fluxos para Benign-DoH do que para Non-DoH em: A no fator 2.

## Relação com a explicação do modelo

Os valores SHAP de `results/e5/variante/` põem `Duration` como o terceiro
atributo em importância para Malicious-DoH nos três Random Forests base, atrás
de `PacketLengthMode` e `PacketLengthMedian`, e mostram que o sinal do valor
SHAP de `Duration` troca perto de 33 s. A tabela da perturbação mostra a
mediana da duração dos fluxos maliciosos em cada fator: é contra esse corte
que ela deve ser lida. A importância SHAP diz quanto o atributo pesa na
saída do modelo; a parte B mede o que acontece com a predição quando o
atributo e os bytes do fluxo mudam juntos. As duas medidas não são a mesma
coisa, e a parte B não isola o efeito de `Duration` do efeito dos bytes.

## Simplificações e o efeito delas

- **As estatísticas por pacote ficam fixas.** Em um fluxo fragmentado de
  verdade, as estatísticas de tempo de pacote encolheriam com a duração e as
  de comprimento de pacote mudariam com os pacotes de handshake de cada
  conexão nova. Aqui os 24 atributos que não são `Duration`, `FlowBytesSent`, `FlowBytesReceived` nem as
  duas taxas ficam com o valor do fluxo inteiro. A coluna de incoerência da
  tabela da perturbação conta os vetores com uma relação entre tempo de pacote
  e duração que nenhum fluxo do conjunto de dados tem.
- **Efeito no resultado.** A queda de recall pode estar subestimada, porque
  atributos que também mudariam ficam com o valor original, ou superestimada,
  porque vetores incoerentes caem em regiões do espaço de atributos em que o
  modelo não viu nenhum fluxo. O experimento não diz qual das duas.
- **Valores fora da faixa do treino.** Random Forest não extrapola: um valor
  abaixo do mínimo do treino segue o mesmo caminho na árvore que o menor
  valor visto. A contagem está na tabela da perturbação.
- **Bytes fracionários e fragmentos iguais.** Os bytes divididos não são
  arredondados, e todos os fragmentos de um fluxo têm o mesmo vetor: o recall
  por fragmento é o recall medido com um fragmento por fluxo.
- **Retirar a coluna não retira a grandeza.** As estatísticas de tempo de
  pacote carregam a duração de forma indireta, e `sem_duration_taxas` mantém
  os bytes do fluxo, que a perturbação altera. Nenhum dos três conjuntos de
  colunas é imune por construção.
- **A seleção de hiperparâmetros de M1M2 não foi refeita** para os modelos
  sem colunas: eles podem não ter a combinação que venceria.

Uma avaliação fiel exigiria gerar o tráfego de novo com o túnel configurado
para reabrir a conexão, ou reprocessar os PCAPs com o extrator.

## O que não foi feito

- Perturbação das estatísticas por pacote, preenchimento de pacotes e inserção
  de atraso.
- Atacante com acesso ao modelo, que busca por fluxo o menor fator que evade.
- Avaliação no combinado CIRA + HKD.
- Avaliação no teste sem os vetores repetidos do treino: com colunas
  retiradas, o que é vetor repetido muda de um conjunto de colunas para outro.
- Treino com fluxos fragmentados.
- Custo da fragmentação para o atacante (vazão do túnel, handshakes).

## Limitações

- Os 10 conjuntos de teste são sorteados da mesma tabela e se sobrepõem; o
  desvio padrão mede a variação entre sorteios desta tabela.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o das outras classes. A duração pode separar as
  classes pelo modo como o tráfego foi gerado, e a perturbação herda isso.
- O tempo de ajuste depende da carga da máquina e é só indicativo.
