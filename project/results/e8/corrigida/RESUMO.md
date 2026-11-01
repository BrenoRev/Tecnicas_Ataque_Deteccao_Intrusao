# E8: a modificação proposta pela equipe ao lado do sistema do artigo

Gerado por `scripts/e8_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e8_modificacao.py` e, para A e A-prof5 no CIRA, por
`scripts/e4_corrigido.py`. Trilha `corrigida`. Os números de cada execução
estão em `<modelo>-<dados>/seed<k>/metrics.json`; a configuração, os tempos e o
commit, em `<modelo>-<dados>/seed<k>/run.json`; as médias e a comparação
pareada, sem arredondamento, em `summary.json`.

## Protocolo

10 seeds (0 a 9). Cada seed refaz o split 90/10 estratificado e
todos os ajustes. Os dois modelos de cada par são ajustados nas mesmas linhas de treino
e avaliados nas mesmas linhas de teste: o script confere a igualdade pelo
resumo dos índices (`split_index_sha256`) de cada `metrics.json`. No CIRA, A e
A-prof5 são os de `results/e4/corrigida/`, sem novo ajuste.

A modificação é um Random Forest único, sem SMOTE e sem empilhamento, com peso
de classe (`class_weight='balanced'`) e o normalizador como primeiro passo de
um `Pipeline`. M1 e M1-prof5 têm os hiperparâmetros dos bases de A e de
A-prof5. M1M2, o modelo proposto, tem os hiperparâmetros escolhidos em cada
seed e em cada conjunto de dados: subamostra estratificada de
25% do treino da seed, validação cruzada estratificada de
5 folds dentro dela, com o normalizador reajustado em cada fold, e
escolha pelo maior F1 macro médio; o modelo final é ajustado no treino
inteiro. O teste não participa da seleção. Grade (árvores, profundidade
máxima, atributos por divisão): (10, 5, sqrt), (100, 5, sqrt), (10, 10, sqrt), (100, 10, sqrt), (10, sem limite, sqrt), (100, sem limite, sqrt), (10, 5, 28), (10, sem limite, 28).

Modelos, grade, pares, métricas da comparação e regra de leitura foram fixados
antes da primeira execução. Commit e estado da árvore de cada grupo de
execuções:

- CIRA-CIC-DoHBrw-2020, A: commit `5165fd3`; execuções com a árvore suja: 0.
- CIRA-CIC-DoHBrw-2020, A-prof5: commit `5165fd3`; execuções com a árvore suja: 0.
- CIRA-CIC-DoHBrw-2020, M1: commit `3ccd1c5`; execuções com a árvore suja: 0.
- CIRA-CIC-DoHBrw-2020, M1-prof5: commit `3ccd1c5`; execuções com a árvore suja: 0.
- CIRA-CIC-DoHBrw-2020, M1M2: commit `3ccd1c5`; execuções com a árvore suja: 0.
- combinado CIRA + HKD sem réplicas, A: commit `3ccd1c5`; execuções com a árvore suja: 0.
- combinado CIRA + HKD sem réplicas, M1M2: commit `3ccd1c5`; execuções com a árvore suja: 0.

Todo valor abaixo é média ± desvio padrão entre as seeds, em percentual, salvo
onde a tabela diz outra unidade. O desvio padrão é o amostral. Uma seed
controla o split, a subamostra da seleção, os folds, a reamostragem e os
modelos: o desvio mistura essas fontes.

Comparação pareada. Método: comparação pareada por seed: diferença média (a modificação menos o modelo de referência), desvio padrão das diferenças, número de seeds em que cada modelo tem o valor maior e teste de postos sinalizados de Wilcoxon bilateral (scipy.stats.wilcoxon com os parâmetros padrão: diferenças nulas descartadas). As diferenças de métrica estão em
pontos percentuais (pp) e as de tempo, em segundos. Regra de leitura:
a modificação melhora a métrica quando a diferença média tem o sinal favorável (positivo em recall e F1, negativo em FPR e tempo) e é, em módulo, maior que o desvio padrão das diferenças pareadas; piora quando tem o sinal desfavorável e passa do mesmo desvio; nos outros casos os dois modelos não se distinguem. Ressalva: os conjuntos de teste das seeds se sobrepõem e são sorteados da mesma tabela: os pares não são independentes, o p-valor é indicativo e não sustenta sozinho a palavra significativo.

## CIRA-CIC-DoHBrw-2020

Modelos e amostras em que cada um foi ajustado. O treino da primeira seed tem
[800828, 17771, 224598] fluxos reais por classe (Non-DoH, Benign-DoH, Malicious-DoH): o que passa disso em
uma classe é amostra sintética.

| modelo | arquitetura | balanceamento | árvores, profundidade máxima, atributos por divisão | amostras por classe em cada conjunto de ajuste, primeira seed (Non-DoH, Benign-DoH, Malicious-DoH) |
| --- | --- | --- | --- | --- |
| A | empilhado, três subconjuntos | SMOTE por subconjunto | (10, sem limite, 28) | [266943, 224598, 224598], [266943, 224598, 224598], [266942, 224598, 224598] |
| A-prof5 | empilhado, três subconjuntos | SMOTE por subconjunto | (10, 5, 28) | [266943, 224598, 224598], [266943, 224598, 224598], [266942, 224598, 224598] |
| M1 | Random Forest único | peso de classe, sem SMOTE | (10, sem limite, 28) | [800828, 17771, 224598] |
| M1-prof5 | Random Forest único | peso de classe, sem SMOTE | (10, 5, 28) | [800828, 17771, 224598] |
| M1M2 | Random Forest único | peso de classe, sem SMOTE | selecionados em cada seed | [800828, 17771, 224598] |

### Teste inteiro

Aviso sobre as AUC. Nos modelos empilhados (A e A-prof5), a saída do modelo é a do meta-classificador, que só tem as combinações de rótulos dos três bases: a AUC dela mede essa discretização e não deve ser comparada com a dos Random Forests únicos. A coluna da média das probabilidades dos bases é a que pode ficar ao lado da AUC de um Random Forest único; ela não é a saída com que o sistema decide.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro, saída do modelo | AUC-ROC one-vs-rest macro, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 99.637 ± 0.014 | 95.611 ± 0.219 | 97.570 ± 0.171 | 96.556 ± 0.120 | 99.643 ± 0.013 | 99.254 ± 0.175 | 99.758 ± 0.035 |
| A-prof5 | 97.659 ± 0.133 | 65.571 ± 0.054 | 65.795 ± 0.231 | 65.673 ± 0.136 | 96.826 ± 0.135 | 96.381 ± 0.257 | 98.741 ± 0.248 |
| M1 | 99.701 ± 0.012 | 96.840 ± 0.173 | 97.440 ± 0.170 | 97.136 ± 0.119 | 99.703 ± 0.012 | 99.551 ± 0.053 | não se aplica |
| M1-prof5 | 95.279 ± 0.271 | 75.084 ± 0.383 | 93.331 ± 0.348 | 78.659 ± 0.502 | 96.418 ± 0.171 | 98.739 ± 0.236 | não se aplica |
| M1M2 | 99.692 ± 0.016 | 96.347 ± 0.233 | 97.796 ± 0.161 | 97.053 ± 0.155 | 99.696 ± 0.015 | 99.819 ± 0.021 | não se aplica |

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

| modelo | classe | precisão | recall | F1 | AUC-PR, saída do modelo | AUC-PR, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.837 ± 0.012 | 99.698 ± 0.020 | 99.768 ± 0.010 | 99.898 ± 0.006 | 99.964 ± 0.005 |
| **A** | **Benign-DoH** | **87.001 ± 0.663** | **93.073 ± 0.522** | **89.932 ± 0.352** | **83.626 ± 0.676** | **94.346 ± 0.362** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.939 ± 0.019 | 99.967 ± 0.010 | 99.979 ± 0.010 | 99.996 ± 0.002 |
| A-prof5 | Non-DoH | 97.173 ± 0.194 | 99.866 ± 0.055 | 98.501 ± 0.086 | 99.353 ± 0.051 | 99.755 ± 0.059 |
| **A-prof5** | **Benign-DoH** | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.000 ± 0.000** | **27.208 ± 1.035** | **44.240 ± 6.446** |
| A-prof5 | Malicious-DoH | 99.539 ± 0.193 | 97.519 ± 0.728 | 98.517 ± 0.323 | 98.887 ± 0.195 | 99.409 ± 0.358 |
| M1 | Non-DoH | 99.826 ± 0.011 | 99.786 ± 0.013 | 99.806 ± 0.008 | 99.937 ± 0.007 | não se aplica |
| **M1** | **Benign-DoH** | **90.710 ± 0.521** | **92.572 ± 0.514** | **91.630 ± 0.349** | **93.845 ± 0.465** | **não se aplica** |
| M1 | Malicious-DoH | 99.982 ± 0.010 | 99.962 ± 0.008 | 99.972 ± 0.007 | 99.994 ± 0.004 | não se aplica |
| M1-prof5 | Non-DoH | 99.418 ± 0.055 | 94.815 ± 0.311 | 97.061 ± 0.148 | 99.761 ± 0.059 | não se aplica |
| **M1-prof5** | **Benign-DoH** | **26.228 ± 1.098** | **87.641 ± 1.362** | **40.355 ± 1.209** | **43.535 ± 7.398** | **não se aplica** |
| M1-prof5 | Malicious-DoH | 99.607 ± 0.352 | 97.538 ± 0.273 | 98.561 ± 0.217 | 99.462 ± 0.336 | não se aplica |
| M1M2 | Non-DoH | 99.851 ± 0.012 | 99.748 ± 0.018 | 99.799 ± 0.010 | 99.979 ± 0.003 | não se aplica |
| **M1M2** | **Benign-DoH** | **89.191 ± 0.699** | **93.671 ± 0.479** | **91.375 ± 0.457** | **95.646 ± 0.267** | **não se aplica** |
| M1M2 | Malicious-DoH | 99.999 ± 0.002 | 99.970 ± 0.016 | 99.985 ± 0.008 | 100.000 ± 0.000 | não se aplica |

Malicious-DoH contra o resto:

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0015 ± 0.0011 | 99.939 ± 0.019 |
| A-prof5 | 0.1241 ± 0.0522 | 97.519 ± 0.728 |
| M1 | 0.0048 ± 0.0027 | 99.962 ± 0.008 |
| M1-prof5 | 0.1059 ± 0.0951 | 97.538 ± 0.273 |
| M1M2 | 0.0002 ± 0.0005 | 99.970 ± 0.016 |

### Os dois erros de Benign-DoH

Média ± desvio padrão entre as seeds do número de fluxos do teste, lido das
matrizes de confusão: Non-DoH predito como Benign-DoH baixa a precisão de
Benign-DoH; Benign-DoH predito como Non-DoH baixa o recall.

| modelo | Non-DoH predito como Benign-DoH | Benign-DoH predito como Non-DoH |
| --- | --- | --- |
| A | 267.5 ± 18.0 | 136.6 ± 10.2 |
| A-prof5 | 10.7 ± 19.9 | 1970.7 ± 1.8 |
| M1 | 186.5 ± 11.9 | 145.9 ± 10.2 |
| M1-prof5 | 4520.5 ± 264.9 | 241.4 ± 26.8 |
| M1M2 | 224.2 ± 16.2 | 125.0 ± 9.5 |

- M1 contra A: Non-DoH predito como Benign-DoH, 186.5 contra 267.5 fluxos por teste; Benign-DoH predito como Non-DoH, 145.9 contra 136.6. Leitura: os dois trocam um erro pelo outro: quem erra menos em um sentido erra mais no outro.
- M1-prof5 contra A-prof5: Non-DoH predito como Benign-DoH, 4520.5 contra 10.7 fluxos por teste; Benign-DoH predito como Non-DoH, 241.4 contra 1970.7. Leitura: os dois trocam um erro pelo outro: quem erra menos em um sentido erra mais no outro.
- M1M2 contra A: Non-DoH predito como Benign-DoH, 224.2 contra 267.5 fluxos por teste; Benign-DoH predito como Non-DoH, 125.0 contra 136.6. Leitura: não há troca: o mesmo modelo erra menos nos dois sentidos, ou há empate.

### Teste sem vetores repetidos do treino

Em média, 13.64 ± 0.08% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro, saída do modelo | AUC-ROC one-vs-rest macro, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 99.624 ± 0.016 | 95.620 ± 0.246 | 97.988 ± 0.146 | 96.754 ± 0.136 | 99.631 ± 0.015 | 99.505 ± 0.117 | 99.819 ± 0.035 |
| A-prof5 | 97.400 ± 0.154 | 65.423 ± 0.062 | 65.787 ± 0.229 | 65.592 ± 0.142 | 96.492 ± 0.156 | 96.415 ± 0.280 | 98.861 ± 0.219 |
| M1 | 99.702 ± 0.012 | 96.961 ± 0.200 | 97.862 ± 0.145 | 97.404 ± 0.112 | 99.704 ± 0.012 | 99.614 ± 0.041 | não se aplica |
| M1-prof5 | 94.704 ± 0.313 | 74.940 ± 0.366 | 93.320 ± 0.323 | 78.378 ± 0.496 | 95.989 ± 0.200 | 98.871 ± 0.218 | não se aplica |
| M1M2 | 99.699 ± 0.016 | 96.577 ± 0.234 | 98.214 ± 0.131 | 97.372 ± 0.145 | 99.703 ± 0.015 | 99.884 ± 0.019 | não se aplica |

| modelo | classe | precisão | recall | F1 | AUC-PR, saída do modelo | AUC-PR, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.846 ± 0.012 | 99.650 ± 0.025 | 99.748 ± 0.012 | 99.919 ± 0.006 | 99.965 ± 0.006 |
| **A** | **Benign-DoH** | **87.021 ± 0.741** | **94.374 ± 0.447** | **90.546 ± 0.400** | **84.878 ± 0.758** | **95.543 ± 0.367** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.939 ± 0.019 | 99.967 ± 0.010 | 99.980 ± 0.009 | 99.996 ± 0.002 |
| A-prof5 | Non-DoH | 96.729 ± 0.234 | 99.837 ± 0.067 | 98.258 ± 0.103 | 99.236 ± 0.064 | 99.725 ± 0.063 |
| **A-prof5** | **Benign-DoH** | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.000 ± 0.000** | **26.830 ± 1.079** | **44.768 ± 6.667** |
| A-prof5 | Malicious-DoH | 99.539 ± 0.193 | 97.523 ± 0.729 | 98.519 ± 0.323 | 98.927 ± 0.192 | 99.507 ± 0.270 |
| M1 | Non-DoH | 99.833 ± 0.012 | 99.762 ± 0.017 | 99.797 ± 0.009 | 99.937 ± 0.006 | não se aplica |
| **M1** | **Benign-DoH** | **91.067 ± 0.605** | **93.860 ± 0.439** | **92.441 ± 0.328** | **95.181 ± 0.357** | **não se aplica** |
| M1 | Malicious-DoH | 99.982 ± 0.010 | 99.962 ± 0.008 | 99.972 ± 0.007 | 99.995 ± 0.003 | não se aplica |
| M1-prof5 | Non-DoH | 99.332 ± 0.064 | 93.895 ± 0.374 | 96.536 ± 0.181 | 99.738 ± 0.065 | não se aplica |
| **M1-prof5** | **Benign-DoH** | **25.881 ± 1.045** | **88.521 ± 1.349** | **40.035 ± 1.163** | **43.730 ± 7.617** | **não se aplica** |
| M1-prof5 | Malicious-DoH | 99.607 ± 0.352 | 97.543 ± 0.275 | 98.564 ± 0.217 | 99.541 ± 0.260 | não se aplica |
| M1M2 | Non-DoH | 99.861 ± 0.012 | 99.727 ± 0.021 | 99.794 ± 0.011 | 99.984 ± 0.003 | não se aplica |
| **M1M2** | **Benign-DoH** | **89.871 ± 0.703** | **94.945 ± 0.390** | **92.337 ± 0.428** | **97.248 ± 0.160** | **não se aplica** |
| M1M2 | Malicious-DoH | 99.999 ± 0.002 | 99.970 ± 0.016 | 99.985 ± 0.008 | 100.000 ± 0.000 | não se aplica |

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0019 ± 0.0013 | 99.939 ± 0.019 |
| A-prof5 | 0.1502 ± 0.0633 | 97.523 ± 0.729 |
| M1 | 0.0059 ± 0.0032 | 99.962 ± 0.008 |
| M1-prof5 | 0.1281 ± 0.1151 | 97.543 ± 0.275 |
| M1M2 | 0.0003 ± 0.0006 | 99.970 ± 0.016 |

### M1M2 ajustado no CIRA, avaliado nos fluxos do HKD

Os fluxos do HKD são todos Malicious-DoH e não entram em nenhum ajuste; são
normalizados com o normalizador do treino do CIRA. Sem fluxo legítimo, só o
recall é definido. O mínimo e o máximo entre as seeds foram acrescentados
depois da execução.

| fluxos do HKD | fluxos | recall, M1M2 ajustado no CIRA, média ± desvio padrão entre as seeds (%) | menor recall entre as seeds (%) | maior recall entre as seeds (%) | seeds sem nenhum fluxo detectado |
| --- | --- | --- | --- | --- | --- |
| as três ferramentas | 5258 | 22.779 ± 12.102 | 2.130 | 42.963 | 0 |
| dnstt | 2304 | 1.016 ± 3.212 | 0.000 | 10.156 | 9 |
| tcp-over-dns | 1502 | 26.305 ± 26.968 | 0.333 | 66.911 | 0 |
| tuns | 1452 | 53.664 ± 35.495 | 7.369 | 95.110 | 0 |

Sem nenhum fluxo detectado em alguma seed: dnstt, em 9 das 10 seeds. Nas 10 seeds, M1M2 deixa passar de 57.04% a 97.87% dos fluxos do HKD.

O sistema do artigo ajustado no CIRA foi avaliado no HKD em uma execução só, com a seed 42 (`results/e6/variante/transferencia/`): recall de 1.807% (dnstt 0.000%, tcp-over-dns 0.333%, tuns 6.198%), ou 98.19% dos fluxos sem detecção. Esse número não é das mesmas seeds, por isso fica fora da tabela, e não há comparação pareada. Nenhum dos dois sistemas transfere.

### Hiperparâmetros selecionados

Combinação escolhida em cada seed (árvores, profundidade máxima, atributos por
divisão): seed 0: (100, sem limite, sqrt); seed 1: (100, sem limite, sqrt); seed 2: (100, sem limite, sqrt); seed 3: (100, sem limite, sqrt); seed 4: (100, sem limite, sqrt); seed 5: (100, sem limite, sqrt); seed 6: (100, sem limite, sqrt); seed 7: (100, sem limite, sqrt); seed 8: (100, sem limite, sqrt); seed 9: (100, sem limite, sqrt).

A subamostra da seleção da primeira seed tem [200207, 4443, 56149] fluxos por classe
(Non-DoH, Benign-DoH, Malicious-DoH). O F1 macro de validação vem só de linhas do treino.

| árvores, profundidade máxima, atributos por divisão | seeds em que foi escolhida | F1 macro de validação, média ± desvio padrão entre as seeds (%) |
| --- | --- | --- |
| (10, 5, sqrt) | 0 | 75.426 ± 0.801 |
| (100, 5, sqrt) | 0 | 76.852 ± 0.293 |
| (10, 10, sqrt) | 0 | 86.527 ± 0.426 |
| (100, 10, sqrt) | 0 | 87.107 ± 0.377 |
| (10, sem limite, sqrt) | 0 | 96.595 ± 0.179 |
| (100, sem limite, sqrt) | 10 | 96.930 ± 0.156 |
| (10, 5, 28) | 0 | 77.015 ± 1.057 |
| (10, sem limite, 28) | 0 | 96.062 ± 0.168 |

### Tempo de treino

Média ± desvio padrão entre as seeds, em segundos: a soma das etapas de ajuste
de cada modelo (subconjuntos com SMOTE, Random Forests base e meta-classificador
no empilhado; seleção de hiperparâmetros e ajuste do `Pipeline` na
modificação). Split, busca de vetores repetidos e avaliação ficam de fora. O
tempo depende da carga da máquina e não é reprodutível como as métricas.

| modelo | tempo de treino (s) | parte que é seleção de hiperparâmetros (s) |
| --- | --- | --- |
| A | 161.0 ± 57.3 |  |
| A-prof5 | 63.5 ± 30.9 |  |
| M1 | 31.1 ± 1.3 |  |
| M1-prof5 | 15.0 ± 0.9 |  |
| M1M2 | 263.2 ± 7.2 | 178.2 ± 4.8 |

A definição de tempo de treino acima foi ajustada depois da execução: antes era o total da execução menos a avaliação. Com a definição anterior, os vereditos de tempo são os mesmos.

Os tempos dos modelos que vêm de `results/e4/corrigida/` foram medidos em outra execução, com outra carga na máquina. Os mesmos modelos foram reajustados nas mesmas seeds pelo script da robustez (`robustez-<modelo>-todos/`): A, 112.5 ± 3.4 s reajustado contra 161.0 ± 57.3 s na tabela; A-prof5, 39.2 ± 1.3 s reajustado contra 63.5 ± 30.9 s na tabela. Com o tempo reajustado no lugar, os vereditos de tempo são os mesmos.

### Comparação pareada

| par | conjunto | métrica | melhor é o valor | diferença média | desvio padrão das diferenças | seeds em que o primeiro tem o valor maior | seeds em que o segundo tem o valor maior | empates | p-valor de Wilcoxon | veredito para a modificação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1 contra A | teste inteiro | recall de Benign-DoH | maior | -0.5013 pp | 0.2908 pp | 0 | 10 | 0 | 0.0020 | **piora** |
| M1 contra A | teste inteiro | F1 macro | maior | +0.5808 pp | 0.1212 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1 contra A | teste inteiro | FPR de Malicious-DoH | menor | +0.0033 pp | 0.0026 pp | 8 | 1 | 1 | 0.0078 | **piora** |
| M1 contra A | teste sem vetores repetidos do treino | recall de Benign-DoH | maior | -0.5141 pp | 0.3065 pp | 0 | 9 | 1 | 0.0039 | **piora** |
| M1 contra A | teste sem vetores repetidos do treino | F1 macro | maior | +0.6499 pp | 0.1265 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1 contra A | teste sem vetores repetidos do treino | FPR de Malicious-DoH | menor | +0.0040 pp | 0.0031 pp | 8 | 1 | 1 | 0.0078 | **piora** |
| M1 contra A | uma medida por execução | tempo de treino | menor | -129.9 s | 57.8 s | 0 | 10 | 0 | 0.0020 | **melhora** |
| M1-prof5 contra A-prof5 | teste inteiro | recall de Benign-DoH | maior | +87.6405 pp | 1.3623 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1-prof5 contra A-prof5 | teste inteiro | F1 macro | maior | +12.9865 pp | 0.5717 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1-prof5 contra A-prof5 | teste inteiro | FPR de Malicious-DoH | menor | -0.0183 pp | 0.1079 pp | 5 | 5 | 0 | 0.5566 | **não se distinguem** |
| M1-prof5 contra A-prof5 | teste sem vetores repetidos do treino | recall de Benign-DoH | maior | +88.5213 pp | 1.3486 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1-prof5 contra A-prof5 | teste sem vetores repetidos do treino | F1 macro | maior | +12.7859 pp | 0.5728 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1-prof5 contra A-prof5 | teste sem vetores repetidos do treino | FPR de Malicious-DoH | menor | -0.0222 pp | 0.1306 pp | 5 | 5 | 0 | 0.5566 | **não se distinguem** |
| M1-prof5 contra A-prof5 | uma medida por execução | tempo de treino | menor | -48.5 s | 31.2 s | 0 | 10 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste inteiro | recall de Benign-DoH | maior | +0.5975 pp | 0.5458 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste inteiro | F1 macro | maior | +0.4973 pp | 0.1677 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste inteiro | FPR de Malicious-DoH | menor | -0.0013 pp | 0.0011 pp | 0 | 7 | 3 | 0.0156 | **melhora** |
| M1M2 contra A | teste sem vetores repetidos do treino | recall de Benign-DoH | maior | +0.5701 pp | 0.4958 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste sem vetores repetidos do treino | F1 macro | maior | +0.6181 pp | 0.1509 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste sem vetores repetidos do treino | FPR de Malicious-DoH | menor | -0.0016 pp | 0.0014 pp | 0 | 7 | 3 | 0.0156 | **melhora** |
| M1M2 contra A | uma medida por execução | tempo de treino | menor | +102.2 s | 59.9 s | 9 | 1 | 0 | 0.0039 | **piora** |

### Análise acrescentada depois da execução, fora dos pares pré-registrados

Este bloco é análise acrescentada depois da execução, fora dos pares pré-registrados: o par ou a métrica não estavam na hipótese, e a regra de leitura é aplicada do mesmo modo. Não entra na condição que a hipótese fixou para
dizer que o modelo proposto é melhor que A.

| par | conjunto | métrica | melhor é o valor | diferença média | desvio padrão das diferenças | seeds em que o primeiro tem o valor maior | seeds em que o segundo tem o valor maior | empates | p-valor de Wilcoxon | veredito para a modificação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1M2 contra A | teste inteiro | precisão de Benign-DoH | maior | +2.1907 pp | 0.5368 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste sem vetores repetidos do treino | precisão de Benign-DoH | maior | +2.8499 pp | 0.5010 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra M1 | teste inteiro | F1 macro | maior | -0.0835 pp | 0.1545 pp | 3 | 7 | 0 | 0.1309 | **não se distinguem** |
| M1M2 contra M1 | teste inteiro | recall de Benign-DoH | maior | +1.0987 pp | 0.4863 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra M1 | teste inteiro | precisão de Benign-DoH | maior | -1.5192 pp | 0.5833 pp | 0 | 10 | 0 | 0.0020 | **piora** |
| M1M2 contra M1 | teste inteiro | FPR de Malicious-DoH | menor | -0.0046 pp | 0.0027 pp | 0 | 10 | 0 | 0.0020 | **melhora** |
| M1M2 contra M1 | teste sem vetores repetidos do treino | F1 macro | maior | -0.0318 pp | 0.1410 pp | 3 | 7 | 0 | 0.3223 | **não se distinguem** |
| M1M2 contra M1 | teste sem vetores repetidos do treino | recall de Benign-DoH | maior | +1.0842 pp | 0.4467 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra M1 | teste sem vetores repetidos do treino | precisão de Benign-DoH | maior | -1.1962 pp | 0.5447 pp | 0 | 10 | 0 | 0.0020 | **piora** |
| M1M2 contra M1 | teste sem vetores repetidos do treino | FPR de Malicious-DoH | menor | -0.0056 pp | 0.0032 pp | 0 | 10 | 0 | 0.0020 | **melhora** |

Falsos positivos de Malicious-DoH somados nas seeds: teste inteiro, A 14, M1 44, M1M2 2, em 909560 fluxos não maliciosos; teste sem vetores repetidos do treino, A 14, M1 44, M1M2 2, em 751516 fluxos não maliciosos.

Pela regra, no teste inteiro, de M1 para M1M2: F1 macro, não se distinguem; recall de Benign-DoH, melhora; precisão de Benign-DoH, piora; FPR de Malicious-DoH, melhora. A seleção de hiperparâmetros troca precisão por recall de Benign-DoH; reduz os falsos positivos de Malicious-DoH; não aumenta o F1 macro. O ganho de F1 macro de M1M2 sobre A já está em M1.

| modelo | árvores, profundidade máxima, atributos por divisão | F1 macro de validação, subamostra de 25% do treino (%) | F1 macro no teste inteiro (%) |
| --- | --- | --- | --- |
| M1 | (10, sem limite, 28) | 96.062 ± 0.168 | 97.136 ± 0.119 |
| M1M2 | a escolhida em cada seed | 96.930 ± 0.156 | 97.053 ± 0.155 |

A combinação de M1 é a 3ª das 8 da grade pela média de validação. Na validação, a combinação escolhida fica acima da de M1 em 10 das 10 seeds (diferença média de +0.868 pp); no teste, M1M2 fica acima de M1 em 3 seeds e abaixo em 7 (diferença média de -0.084 pp). A validação mede modelos ajustados em quatro quintos da subamostra; o teste, modelos ajustados no treino inteiro. A ordem que a validação dá às duas combinações não se repete no teste: é evidência da limitação da subamostra, registrada em Limitações.

## combinado CIRA + HKD sem réplicas

Modelos e amostras em que cada um foi ajustado. O treino da primeira seed tem
[800828, 17771, 229330] fluxos reais por classe (Non-DoH, Benign-DoH, Malicious-DoH): o que passa disso em
uma classe é amostra sintética.

| modelo | arquitetura | balanceamento | árvores, profundidade máxima, atributos por divisão | amostras por classe em cada conjunto de ajuste, primeira seed (Non-DoH, Benign-DoH, Malicious-DoH) |
| --- | --- | --- | --- | --- |
| A | empilhado, três subconjuntos | SMOTE por subconjunto | (10, sem limite, 28) | [266943, 229330, 229330], [266943, 229330, 229330], [266942, 229330, 229330] |
| M1M2 | Random Forest único | peso de classe, sem SMOTE | selecionados em cada seed | [800828, 17771, 229330] |

### Teste inteiro

Aviso sobre as AUC. Nos modelos empilhados (A), a saída do modelo é a do meta-classificador, que só tem as combinações de rótulos dos três bases: a AUC dela mede essa discretização e não deve ser comparada com a dos Random Forests únicos. A coluna da média das probabilidades dos bases é a que pode ficar ao lado da AUC de um Random Forest único; ela não é a saída com que o sistema decide.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro, saída do modelo | AUC-ROC one-vs-rest macro, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 99.636 ± 0.021 | 95.528 ± 0.279 | 97.607 ± 0.179 | 96.529 ± 0.188 | 99.643 ± 0.020 | 99.060 ± 0.062 | 99.759 ± 0.031 |
| M1M2 | 99.700 ± 0.015 | 96.440 ± 0.170 | 97.793 ± 0.138 | 97.101 ± 0.142 | 99.704 ± 0.015 | 99.825 ± 0.022 | não se aplica |

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

| modelo | classe | precisão | recall | F1 | AUC-PR, saída do modelo | AUC-PR, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.842 ± 0.013 | 99.691 ± 0.023 | 99.766 ± 0.014 | 99.897 ± 0.007 | 99.964 ± 0.004 |
| **A** | **Benign-DoH** | **86.748 ± 0.835** | **93.185 ± 0.532** | **89.849 ± 0.549** | **83.361 ± 0.927** | **94.260 ± 0.356** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.947 ± 0.013 | 99.970 ± 0.008 | 99.983 ± 0.005 | 99.997 ± 0.003 |
| M1M2 | Non-DoH | 99.853 ± 0.011 | 99.755 ± 0.013 | 99.804 ± 0.010 | 99.980 ± 0.003 | não se aplica |
| **M1M2** | **Benign-DoH** | **89.470 ± 0.503** | **93.646 ± 0.400** | **91.510 ± 0.414** | **95.658 ± 0.304** | **não se aplica** |
| M1M2 | Malicious-DoH | 99.998 ± 0.003 | 99.978 ± 0.007 | 99.988 ± 0.004 | 100.000 ± 0.000 | não se aplica |

Malicious-DoH contra o resto:

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0016 ± 0.0011 | 99.947 ± 0.013 |
| M1M2 | 0.0005 ± 0.0008 | 99.978 ± 0.007 |

### Os dois erros de Benign-DoH

Média ± desvio padrão entre as seeds do número de fluxos do teste, lido das
matrizes de confusão: Non-DoH predito como Benign-DoH baixa a precisão de
Benign-DoH; Benign-DoH predito como Non-DoH baixa o recall.

| modelo | Non-DoH predito como Benign-DoH | Benign-DoH predito como Non-DoH |
| --- | --- | --- |
| A | 274.2 ± 20.5 | 134.1 ± 10.8 |
| M1M2 | 217.5 ± 11.0 | 125.4 ± 7.9 |

- M1M2 contra A: Non-DoH predito como Benign-DoH, 217.5 contra 274.2 fluxos por teste; Benign-DoH predito como Non-DoH, 125.4 contra 134.1. Leitura: não há troca: o mesmo modelo erra menos nos dois sentidos, ou há empate.

### Teste sem vetores repetidos do treino

Em média, 13.55 ± 0.08% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro, saída do modelo | AUC-ROC one-vs-rest macro, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 99.593 ± 0.024 | 95.455 ± 0.299 | 97.616 ± 0.192 | 96.493 ± 0.206 | 99.601 ± 0.023 | 99.075 ± 0.064 | 99.797 ± 0.032 |
| M1M2 | 99.678 ± 0.016 | 96.573 ± 0.167 | 97.819 ± 0.136 | 97.182 ± 0.138 | 99.682 ± 0.016 | 99.887 ± 0.025 | não se aplica |

| modelo | classe | precisão | recall | F1 | AUC-PR, saída do modelo | AUC-PR, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.818 ± 0.015 | 99.634 ± 0.027 | 99.726 ± 0.017 | 99.884 ± 0.008 | 99.961 ± 0.005 |
| **A** | **Benign-DoH** | **86.553 ± 0.891** | **93.267 ± 0.569** | **89.782 ± 0.600** | **83.352 ± 0.992** | **94.714 ± 0.363** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.947 ± 0.013 | 99.970 ± 0.008 | 99.983 ± 0.005 | 99.998 ± 0.003 |
| M1M2 | Non-DoH | 99.831 ± 0.012 | 99.727 ± 0.014 | 99.779 ± 0.011 | 99.984 ± 0.004 | não se aplica |
| **M1M2** | **Benign-DoH** | **89.891 ± 0.493** | **93.750 ± 0.394** | **91.779 ± 0.400** | **96.786 ± 0.245** | **não se aplica** |
| M1M2 | Malicious-DoH | 99.998 ± 0.003 | 99.978 ± 0.007 | 99.988 ± 0.004 | 100.000 ± 0.000 | não se aplica |

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0020 ± 0.0013 | 99.947 ± 0.013 |
| M1M2 | 0.0007 ± 0.0009 | 99.978 ± 0.007 |

### Recall de Malicious-DoH por ferramenta de túnel

Teste inteiro, média ± desvio padrão entre as seeds. dns2tcp, dnscat2 e iodine
vêm do CIRA; dnstt, tcp-over-dns e tuns, do HKD.

| ferramenta | fluxos no teste, média entre as seeds | recall, A (%) | recall, M1M2 (%) |
| --- | --- | --- | --- |
| dns2tcp | 16776.0 | 99.983 ± 0.009 | 99.992 ± 0.003 |
| dnscat2 | 3543.6 | 99.909 ± 0.071 | 99.983 ± 0.015 |
| dnstt | 233.5 | 99.878 ± 0.274 | 100.000 ± 0.000 |
| iodine | 4630.0 | 99.857 ± 0.051 | 99.927 ± 0.032 |
| tcp-over-dns | 149.0 | 99.792 ± 0.335 | 99.936 ± 0.203 |
| tuns | 148.9 | 99.738 ± 0.339 | 99.874 ± 0.265 |

### Hiperparâmetros selecionados

Combinação escolhida em cada seed (árvores, profundidade máxima, atributos por
divisão): seed 0: (100, sem limite, sqrt); seed 1: (100, sem limite, sqrt); seed 2: (100, sem limite, sqrt); seed 3: (100, sem limite, sqrt); seed 4: (100, sem limite, sqrt); seed 5: (100, sem limite, sqrt); seed 6: (100, sem limite, sqrt); seed 7: (100, sem limite, sqrt); seed 8: (100, sem limite, sqrt); seed 9: (100, sem limite, sqrt).

A subamostra da seleção da primeira seed tem [200207, 4443, 57332] fluxos por classe
(Non-DoH, Benign-DoH, Malicious-DoH). O F1 macro de validação vem só de linhas do treino.

| árvores, profundidade máxima, atributos por divisão | seeds em que foi escolhida | F1 macro de validação, média ± desvio padrão entre as seeds (%) |
| --- | --- | --- |
| (10, 5, sqrt) | 0 | 75.125 ± 0.529 |
| (100, 5, sqrt) | 0 | 76.615 ± 0.322 |
| (10, 10, sqrt) | 0 | 86.178 ± 0.499 |
| (100, 10, sqrt) | 0 | 86.831 ± 0.316 |
| (10, sem limite, sqrt) | 0 | 96.597 ± 0.115 |
| (100, sem limite, sqrt) | 10 | 96.856 ± 0.116 |
| (10, 5, 28) | 0 | 76.468 ± 0.689 |
| (10, sem limite, 28) | 0 | 95.993 ± 0.133 |

### Tempo de treino

Média ± desvio padrão entre as seeds, em segundos: a soma das etapas de ajuste
de cada modelo (subconjuntos com SMOTE, Random Forests base e meta-classificador
no empilhado; seleção de hiperparâmetros e ajuste do `Pipeline` na
modificação). Split, busca de vetores repetidos e avaliação ficam de fora. O
tempo depende da carga da máquina e não é reprodutível como as métricas.

| modelo | tempo de treino (s) | parte que é seleção de hiperparâmetros (s) |
| --- | --- | --- |
| A | 117.8 ± 2.0 |  |
| M1M2 | 265.1 ± 1.4 | 180.0 ± 1.4 |

A definição de tempo de treino acima foi ajustada depois da execução: antes era o total da execução menos a avaliação. Com a definição anterior, os vereditos de tempo são os mesmos.

### Comparação pareada

| par | conjunto | métrica | melhor é o valor | diferença média | desvio padrão das diferenças | seeds em que o primeiro tem o valor maior | seeds em que o segundo tem o valor maior | empates | p-valor de Wilcoxon | veredito para a modificação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1M2 contra A | teste inteiro | recall de Benign-DoH | maior | +0.4608 pp | 0.4746 pp | 8 | 1 | 1 | 0.0078 | **não se distinguem** |
| M1M2 contra A | teste inteiro | F1 macro | maior | +0.5720 pp | 0.2008 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste inteiro | FPR de Malicious-DoH | menor | -0.0011 pp | 0.0012 pp | 0 | 6 | 4 | 0.0312 | **não se distinguem** |
| M1M2 contra A | teste sem vetores repetidos do treino | recall de Benign-DoH | maior | +0.4829 pp | 0.5001 pp | 8 | 1 | 1 | 0.0078 | **não se distinguem** |
| M1M2 contra A | teste sem vetores repetidos do treino | F1 macro | maior | +0.6894 pp | 0.2031 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste sem vetores repetidos do treino | FPR de Malicious-DoH | menor | -0.0013 pp | 0.0014 pp | 0 | 6 | 4 | 0.0312 | **não se distinguem** |
| M1M2 contra A | uma medida por execução | tempo de treino | menor | +147.2 s | 1.8 s | 10 | 0 | 0 | 0.0020 | **piora** |

### Análise acrescentada depois da execução, fora dos pares pré-registrados

Este bloco é análise acrescentada depois da execução, fora dos pares pré-registrados: o par ou a métrica não estavam na hipótese, e a regra de leitura é aplicada do mesmo modo. Não entra na condição que a hipótese fixou para
dizer que o modelo proposto é melhor que A.

| par | conjunto | métrica | melhor é o valor | diferença média | desvio padrão das diferenças | seeds em que o primeiro tem o valor maior | seeds em que o segundo tem o valor maior | empates | p-valor de Wilcoxon | veredito para a modificação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1M2 contra A | teste inteiro | precisão de Benign-DoH | maior | +2.7219 pp | 0.8061 pp | 10 | 0 | 0 | 0.0020 | **melhora** |
| M1M2 contra A | teste sem vetores repetidos do treino | precisão de Benign-DoH | maior | +3.3376 pp | 0.7796 pp | 10 | 0 | 0 | 0.0020 | **melhora** |

Falsos positivos de Malicious-DoH somados nas seeds: teste inteiro, A 15, M1M2 5, em 909560 fluxos não maliciosos; teste sem vetores repetidos do treino, A 15, M1M2 5, em 751844 fluxos não maliciosos.

## Hipótese ao lado do resultado

A hipótese está em `HIPOTESE.md`, escrita antes da primeira execução e não
alterada depois. Os itens abaixo seguem a ordem do arquivo. Regra de leitura,
fixada na hipótese: a modificação melhora a métrica quando a diferença média tem o sinal favorável (positivo em recall e F1, negativo em FPR e tempo) e é, em módulo, maior que o desvio padrão das diferenças pareadas; piora quando tem o sinal desfavorável e passa do mesmo desvio; nos outros casos os dois modelos não se distinguem.

### O que se esperava

1. M1 contra A, CIRA, teste inteiro:
   - Esperado: os dois não se distinguem em F1 macro nem em recall de Benign-DoH. F1 macro: diferença média de +0.5808 pp, desvio padrão das diferenças de 0.1212 pp, veredito **melhora**; recall de Benign-DoH: diferença média de -0.5013 pp, desvio padrão das diferenças de 0.2908 pp, veredito **piora**: não ocorreu.
   - Esperado: M1 treina em menos tempo que A. tempo de treino: diferença média de -129.9 s, desvio padrão das diferenças de 57.8 s, veredito **melhora**: **ocorreu**.
2. M1-prof5 contra A-prof5, CIRA, teste inteiro:
   - Esperado: recall de Benign-DoH maior que zero em todas as seeds. Menor recall de M1-prof5 entre as seeds: 85.165%: **ocorreu**.
   - Esperado: melhora do F1 macro. F1 macro: diferença média de +12.9865 pp, desvio padrão das diferenças de 0.5717 pp, veredito **melhora**: **ocorreu**.
   - Esperado: piora do FPR de Malicious-DoH. FPR de Malicious-DoH: diferença média de -0.0183 pp, desvio padrão das diferenças de 0.1079 pp, veredito **não se distinguem**: não ocorreu.
3. Seleção. Esperado: uma combinação sem limite de profundidade em todas as seeds e (100, sem limite, sqrt) como a mais frequente.
   - CIRA-CIC-DoHBrw-2020: sem limite de profundidade em 10 das 10 seeds: **ocorreu**; (100, sem limite, sqrt) escolhida em 10 seeds, a mais frequente: **ocorreu**.
   - combinado CIRA + HKD sem réplicas: sem limite de profundidade em 10 das 10 seeds: **ocorreu**; (100, sem limite, sqrt) escolhida em 10 seeds, a mais frequente: **ocorreu**.
4. M1M2 contra A, CIRA-CIC-DoHBrw-2020, teste inteiro:
   - Esperado: melhora do F1 macro. F1 macro: diferença média de +0.4973 pp, desvio padrão das diferenças de 0.1677 pp, veredito **melhora**: **ocorreu**.
   - Esperado: diferença de F1 macro abaixo de 1 pp: **ocorreu**.
   - Esperado: sem melhora no recall de Benign-DoH. recall de Benign-DoH: diferença média de +0.5975 pp, desvio padrão das diferenças de 0.5458 pp, veredito **melhora**: não ocorreu. Em fluxos (contagem acrescentada depois da execução): M1M2 acerta em média +11.8 fluxos Benign-DoH por teste em relação a A, de 1975 no teste da primeira seed.
   - Esperado: o ganho, se houver, vem de menos fluxos Non-DoH preditos como Benign-DoH. Média por teste de 224.2 em M1M2 contra 267.5 em A: **ocorreu**.
   - Esperado: os dois não se distinguem no FPR de Malicious-DoH. FPR de Malicious-DoH: diferença média de -0.0013 pp, desvio padrão das diferenças de 0.0011 pp, veredito **melhora**: não ocorreu. Em fluxos (contagem acrescentada depois da execução): 2 falsos positivos de Malicious-DoH somados nas 10 seeds em M1M2 contra 14 em A, em 909560 fluxos não maliciosos somados.
5. M1M2 contra A, combinado CIRA + HKD sem réplicas, teste inteiro:
   - Esperado: melhora do F1 macro. F1 macro: diferença média de +0.5720 pp, desvio padrão das diferenças de 0.2008 pp, veredito **melhora**: **ocorreu**.
   - Esperado: diferença de F1 macro abaixo de 1 pp: **ocorreu**.
   - Esperado: sem melhora no recall de Benign-DoH. recall de Benign-DoH: diferença média de +0.4608 pp, desvio padrão das diferenças de 0.4746 pp, veredito **não se distinguem**: **ocorreu**. Em fluxos (contagem acrescentada depois da execução): M1M2 acerta em média +9.1 fluxos Benign-DoH por teste em relação a A, de 1975 no teste da primeira seed.
   - Esperado: o ganho, se houver, vem de menos fluxos Non-DoH preditos como Benign-DoH. Média por teste de 217.5 em M1M2 contra 274.2 em A: **ocorreu**.
   - Esperado: os dois não se distinguem no FPR de Malicious-DoH. FPR de Malicious-DoH: diferença média de -0.0011 pp, desvio padrão das diferenças de 0.0012 pp, veredito **não se distinguem**: **ocorreu**. Em fluxos (contagem acrescentada depois da execução): 5 falsos positivos de Malicious-DoH somados nas 10 seeds em M1M2 contra 15 em A, em 909560 fluxos não maliciosos somados.
6. Esperado: os vereditos de M1M2 contra A são os mesmos no teste inteiro e no teste sem vetores repetidos.
   - CIRA-CIC-DoHBrw-2020: recall de Benign-DoH, melhora e melhora; F1 macro, melhora e melhora; FPR de Malicious-DoH, melhora e melhora: **ocorreu**.
   - combinado CIRA + HKD sem réplicas: recall de Benign-DoH, não se distinguem e não se distinguem; F1 macro, melhora e melhora; FPR de Malicious-DoH, não se distinguem e não se distinguem: **ocorreu**.
7. Esperado: M1M2 leva mais tempo de treino que A, por causa da seleção.
   - CIRA-CIC-DoHBrw-2020: tempo de treino: diferença média de +102.2 s, desvio padrão das diferenças de 59.9 s, veredito **piora**: **ocorreu**.
   - combinado CIRA + HKD sem réplicas: tempo de treino: diferença média de +147.2 s, desvio padrão das diferenças de 1.8 s, veredito **piora**: **ocorreu**.

### O modelo proposto é melhor que A?

A hipótese fixou a condição: melhorar o F1 macro pela regra no teste inteiro e
no teste sem vetores repetidos, sem piorar o recall de Benign-DoH nem o FPR de
Malicious-DoH.

- CIRA-CIC-DoHBrw-2020: recall de Benign-DoH, melhora no teste inteiro e melhora no teste sem vetores repetidos do treino; F1 macro, melhora no teste inteiro e melhora no teste sem vetores repetidos do treino; FPR de Malicious-DoH, melhora no teste inteiro e melhora no teste sem vetores repetidos do treino. Pela regra, M1M2 **é dito melhor que A**.
- combinado CIRA + HKD sem réplicas: recall de Benign-DoH, não se distinguem no teste inteiro e não se distinguem no teste sem vetores repetidos do treino; F1 macro, melhora no teste inteiro e melhora no teste sem vetores repetidos do treino; FPR de Malicious-DoH, não se distinguem no teste inteiro e não se distinguem no teste sem vetores repetidos do treino. Pela regra, M1M2 **é dito melhor que A**.

Leitura acrescentada depois da execução. Pela regra, no teste inteiro, o veredito de melhora de M1M2 sobre A se repete em todos os conjuntos de dados em: F1 macro, precisão de Benign-DoH. Não se repete em: recall de Benign-DoH (só em CIRA-CIC-DoHBrw-2020), FPR de Malicious-DoH (só em CIRA-CIC-DoHBrw-2020). A precisão de Benign-DoH não estava entre as métricas da hipótese e entra aqui como análise posterior. Os conjuntos não são independentes: o segundo tem 0.45% de fluxos a mais que o primeiro (+0 Non-DoH, +0 Benign-DoH, +5258 Malicious-DoH). É o primeiro mais os fluxos do HKD, e o resultado nele não é uma réplica independente do resultado no primeiro.

M1M2 difere de A em três coisas ao mesmo tempo: a arquitetura (um Random
Forest em vez de três e um meta-classificador), o balanceamento (peso de
classe em vez de SMOTE) e os hiperparâmetros. A diferença entre os dois não
pode ser atribuída a nenhuma das três em separado. M1 contra A, no CIRA, mede
a arquitetura e o balanceamento juntos, com os hiperparâmetros iguais. M1
contra M1M2 não estava entre os pares da hipótese: a comparação seed a seed
foi acrescentada depois da execução e está na seção do CIRA. Médias dos dois
no teste inteiro do CIRA: F1 macro de 97.136 ± 0.119% em M1 e de
97.053 ± 0.155% em M1M2; recall de Benign-DoH de
92.572 ± 0.514% e de 93.671 ± 0.479%; precisão de
Benign-DoH de 90.710 ± 0.521% e de 89.191 ± 0.699%.

### O que a hipótese listava como resultado inesperado

- M1 piorar o F1 macro ou o recall de Benign-DoH em relação a A, no teste inteiro: **ocorreu**.
- M1-prof5 com recall de Benign-DoH igual a zero em alguma seed: não ocorreu.
- CIRA-CIC-DoHBrw-2020: a seleção escolher profundidade 5 ou 10 em alguma seed: não ocorreu (0 de 10 seeds).
- CIRA-CIC-DoHBrw-2020: M1M2 abaixo de A em F1 macro em todas as seeds: não ocorreu (abaixo em 0 de 10).
- CIRA-CIC-DoHBrw-2020: M1M2 piorar o recall de Benign-DoH ou o FPR de Malicious-DoH, no teste inteiro: não ocorreu.
- CIRA-CIC-DoHBrw-2020: veredito de melhora no teste inteiro que não se repete no teste sem vetores repetidos: não ocorreu.
- combinado CIRA + HKD sem réplicas: a seleção escolher profundidade 5 ou 10 em alguma seed: não ocorreu (0 de 10 seeds).
- combinado CIRA + HKD sem réplicas: M1M2 abaixo de A em F1 macro em todas as seeds: não ocorreu (abaixo em 0 de 10).
- combinado CIRA + HKD sem réplicas: M1M2 piorar o recall de Benign-DoH ou o FPR de Malicious-DoH, no teste inteiro: não ocorreu.
- combinado CIRA + HKD sem réplicas: veredito de melhora no teste inteiro que não se repete no teste sem vetores repetidos: não ocorreu.

## O que não foi feito

- A explicabilidade do modelo proposto (importância global com `TreeExplainer`
  sobre M1M2) não foi feita nesta execução.
- Não há ajuste de limiar de decisão nem variante que mantenha o SMOTE e só
  selecione hiperparâmetros.
- No combinado sem réplicas, M1, M1-prof5 e A-prof5 não foram rodados: só A e
  M1M2.
- O recall de M1M2 nos fluxos do HKD não tem par nas mesmas seeds: o sistema
  do artigo só foi avaliado no HKD com a seed 42.

## Limitações

- A seleção de hiperparâmetros usa 25% do treino, pelo custo. A
  combinação escolhida pode não ser a que venceria no treino inteiro.
- Há vetores de atributos repetidos dentro do treino. Na validação cruzada da
  seleção o mesmo vetor pode cair no fold de ajuste e no de validação, o que
  favorece árvores mais profundas; a avaliação no teste sem vetores repetidos
  só remove as linhas idênticas, não as parecidas.
- Os 10 conjuntos de teste são sorteados da mesma tabela e se sobrepõem. O
  desvio padrão entre seeds mede a variação entre sorteios desta tabela, não a
  variação entre redes ou entre capturas.
- O tempo de treino de A no CIRA foi medido em outra execução, a do protocolo
  corrigido, com outra carga na máquina. A comparação de tempo é indicativa; a
  seção de tempo de treino do CIRA mostra o mesmo modelo reajustado.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o tráfego das outras duas classes. Nenhum split
  dentro do conjunto remove essa diferença.
