# E4: protocolo corrigido, variância entre seeds e comparação pareada

Gerado por `scripts/e4_resumo.py`, que não treina: lê os arquivos gravados por
`scripts/e4_corrigido.py`. Trilha `corrigida`. Os números de cada execução
estão em `<modelo>/seed<k>/metrics.json`; a configuração, os tempos e o commit,
em `<modelo>/seed<k>/run.json`; as médias e a comparação pareada, sem
arredondamento, em `summary.json`.

## Protocolo

10 seeds (0 a 9). Cada seed refaz o split 90/10 estratificado, o
normalizador (ajustado só no treino), os subconjuntos, o SMOTE (só no treino) e
os modelos. Todos os modelos de uma seed são ajustados nas mesmas linhas de
treino e avaliados nas mesmas linhas de teste: o script confere a igualdade, e
cada `metrics.json` traz o resumo dos índices em `split_index_sha256`. Não há
busca de hiperparâmetros nem escolha de seed: as configurações abaixo, os pares
comparados, as métricas da comparação e o teste estatístico foram fixados
antes da primeira execução.

| modelo | arquitetura | árvores | profundidade máxima | atributos por divisão | balanceamento |
| --- | --- | --- | --- | --- | --- |
| A | empilhado, três subconjuntos | 10 | sem limite | 28 | SMOTE por subconjunto |
| B | Random Forest único | 10 | sem limite | 28 | SMOTE no treino inteiro |
| C | Random Forest único | 10 | sem limite | sqrt | SMOTE no treino inteiro |
| A-prof5 | empilhado, três subconjuntos | 10 | 5 | 28 | SMOTE por subconjunto |
| B-prof5 | Random Forest único | 10 | 5 | 28 | SMOTE no treino inteiro |

A e B têm os mesmos hiperparâmetros de Random Forest. Diferem na arquitetura e no balanceamento que ela traz: em A cada base vê um terço do Non-DoH e só Benign-DoH é aumentada; em B o SMOTE iguala Benign-DoH e Malicious-DoH ao Non-DoH inteiro. A diferença entre A e B mede as duas coisas juntas. Amostras por classe nos conjuntos de ajuste da seed 0, na ordem Non-DoH, Benign-DoH, Malicious-DoH: os três bases de A, [266943, 224598, 224598], [266943, 224598, 224598], [266942, 224598, 224598]; B, [800828, 800828, 800828]. O treino da seed tem [800828, 17771, 224598] fluxos reais: o que passa disso em uma classe é amostra sintética.

A contra C é a comparação que o artigo faz na Tabela II. Os modelos com
`-prof5` repetem A e B com a profundidade máxima 5 da Seção IV-B do artigo. O
meta-classificador dos modelos empilhados é treinado como na reprodução do
artigo: este protocolo corrige a avaliação, não o desenho do empilhamento.

Todo valor abaixo é média ± desvio padrão entre as seeds, em percentual, salvo
onde a tabela diz outra unidade. O desvio padrão é o amostral. Uma seed
controla o split, a reamostragem e os modelos: o desvio mistura as três fontes
de variação e não separa nenhuma.

## Teste inteiro

Aviso sobre as AUC. Nos modelos empilhados (A e A-prof5), a saída do modelo é a do meta-classificador, que só tem as combinações de rótulos dos três bases: a AUC dela mede essa discretização e não deve ser comparada com a dos Random Forests únicos. A coluna da média das probabilidades dos bases é a que pode ficar ao lado da AUC de um Random Forest único; ela não é a saída com que o sistema decide.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro, saída do modelo | AUC-ROC one-vs-rest macro, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 99.637 ± 0.014 | 95.611 ± 0.219 | 97.570 ± 0.171 | 96.556 ± 0.120 | 99.643 ± 0.013 | 99.254 ± 0.175 | 99.758 ± 0.035 |
| B | 99.533 ± 0.020 | 93.961 ± 0.268 | 97.723 ± 0.139 | 95.714 ± 0.175 | 99.548 ± 0.018 | 99.501 ± 0.045 | não se aplica |
| C | 99.421 ± 0.033 | 92.351 ± 0.398 | 97.949 ± 0.105 | 94.857 ± 0.258 | 99.449 ± 0.029 | 99.725 ± 0.037 | não se aplica |
| A-prof5 | 97.659 ± 0.133 | 65.571 ± 0.054 | 65.795 ± 0.231 | 65.673 ± 0.136 | 96.826 ± 0.135 | 96.381 ± 0.257 | 98.741 ± 0.248 |
| B-prof5 | 95.168 ± 0.557 | 74.892 ± 0.891 | 93.118 ± 0.310 | 78.499 ± 1.034 | 96.310 ± 0.400 | 98.538 ± 0.291 | não se aplica |

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

| modelo | classe | precisão | recall | F1 | AUC-PR, saída do modelo | AUC-PR, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.837 ± 0.012 | 99.698 ± 0.020 | 99.768 ± 0.010 | 99.898 ± 0.006 | 99.964 ± 0.005 |
| **A** | **Benign-DoH** | **87.001 ± 0.663** | **93.073 ± 0.522** | **89.932 ± 0.352** | **83.626 ± 0.676** | **94.346 ± 0.362** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.939 ± 0.019 | 99.967 ± 0.010 | 99.979 ± 0.010 | 99.996 ± 0.002 |
| B | Non-DoH | 99.854 ± 0.010 | 99.543 ± 0.023 | 99.698 ± 0.013 | 99.918 ± 0.007 | não se aplica |
| **B** | **Benign-DoH** | **82.060 ± 0.810** | **93.666 ± 0.416** | **87.478 ± 0.516** | **90.590 ± 0.730** | **não se aplica** |
| B | Malicious-DoH | 99.970 ± 0.013 | 99.961 ± 0.015 | 99.965 ± 0.008 | 99.991 ± 0.006 | não se aplica |
| C | Non-DoH | 99.868 ± 0.007 | 99.380 ± 0.042 | 99.623 ± 0.022 | 99.964 ± 0.005 | não se aplica |
| **C** | **Benign-DoH** | **77.199 ± 1.192** | **94.511 ± 0.313** | **84.978 ± 0.753** | **94.476 ± 0.412** | **não se aplica** |
| C | Malicious-DoH | 99.987 ± 0.007 | 99.955 ± 0.023 | 99.971 ± 0.011 | 99.997 ± 0.003 | não se aplica |
| A-prof5 | Non-DoH | 97.173 ± 0.194 | 99.866 ± 0.055 | 98.501 ± 0.086 | 99.353 ± 0.051 | 99.755 ± 0.059 |
| **A-prof5** | **Benign-DoH** | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.000 ± 0.000** | **27.208 ± 1.035** | **44.240 ± 6.446** |
| A-prof5 | Malicious-DoH | 99.539 ± 0.193 | 97.519 ± 0.728 | 98.517 ± 0.323 | 98.887 ± 0.195 | 99.409 ± 0.358 |
| B-prof5 | Non-DoH | 99.449 ± 0.039 | 94.704 ± 0.681 | 97.017 ± 0.343 | 99.712 ± 0.091 | não se aplica |
| **B-prof5** | **Benign-DoH** | **26.211 ± 2.139** | **87.195 ± 1.169** | **40.252 ± 2.393** | **43.243 ± 7.354** | **não se aplica** |
| B-prof5 | Malicious-DoH | 99.017 ± 1.004 | 97.456 ± 0.357 | 98.228 ± 0.517 | 99.434 ± 0.356 | não se aplica |

Malicious-DoH contra o resto:

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0015 ± 0.0011 | 99.939 ± 0.019 |
| B | 0.0084 ± 0.0036 | 99.961 ± 0.015 |
| C | 0.0036 ± 0.0018 | 99.955 ± 0.023 |
| A-prof5 | 0.1241 ± 0.0522 | 97.519 ± 0.728 |
| B-prof5 | 0.2680 ± 0.2751 | 97.456 ± 0.357 |

## Os dois erros de Benign-DoH

Média ± desvio padrão entre as seeds do número de fluxos do teste, lido das
matrizes de confusão: Non-DoH predito como Benign-DoH baixa a precisão de
Benign-DoH; Benign-DoH predito como Non-DoH baixa o recall.

| modelo | Non-DoH predito como Benign-DoH | Benign-DoH predito como Non-DoH |
| --- | --- | --- |
| A | 267.5 ± 18.0 | 136.6 ± 10.2 |
| B | 401.5 ± 21.9 | 122.6 ± 8.0 |
| C | 550.3 ± 36.8 | 106.8 ± 6.1 |
| A-prof5 | 10.7 ± 19.9 | 1970.7 ± 1.8 |
| B-prof5 | 4475.1 ± 466.7 | 246.8 ± 22.8 |

- A contra B: Non-DoH predito como Benign-DoH, 267.5 contra 401.5 fluxos por teste; Benign-DoH predito como Non-DoH, 136.6 contra 122.6. Leitura: os dois trocam um erro pelo outro: quem erra menos em um sentido erra mais no outro.
- A contra C: Non-DoH predito como Benign-DoH, 267.5 contra 550.3 fluxos por teste; Benign-DoH predito como Non-DoH, 136.6 contra 106.8. Leitura: os dois trocam um erro pelo outro: quem erra menos em um sentido erra mais no outro.
- A-prof5 contra B-prof5: Non-DoH predito como Benign-DoH, 10.7 contra 4475.1 fluxos por teste; Benign-DoH predito como Non-DoH, 1970.7 contra 246.8. Leitura: os dois trocam um erro pelo outro: quem erra menos em um sentido erra mais no outro.

## Teste sem vetores repetidos do treino

Em média, 13.64 ± 0.08% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

Aviso sobre as AUC. Nos modelos empilhados (A e A-prof5), a saída do modelo é a do meta-classificador, que só tem as combinações de rótulos dos três bases: a AUC dela mede essa discretização e não deve ser comparada com a dos Random Forests únicos. A coluna da média das probabilidades dos bases é a que pode ficar ao lado da AUC de um Random Forest único; ela não é a saída com que o sistema decide.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro, saída do modelo | AUC-ROC one-vs-rest macro, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 99.624 ± 0.016 | 95.620 ± 0.246 | 97.988 ± 0.146 | 96.754 ± 0.136 | 99.631 ± 0.015 | 99.505 ± 0.117 | 99.819 ± 0.035 |
| B | 99.506 ± 0.024 | 93.943 ± 0.308 | 98.138 ± 0.110 | 95.881 ± 0.199 | 99.523 ± 0.022 | 99.564 ± 0.030 | não se aplica |
| C | 99.390 ± 0.039 | 92.436 ± 0.390 | 98.357 ± 0.104 | 95.070 ± 0.271 | 99.421 ± 0.036 | 99.777 ± 0.033 | não se aplica |
| A-prof5 | 97.400 ± 0.154 | 65.423 ± 0.062 | 65.787 ± 0.229 | 65.592 ± 0.142 | 96.492 ± 0.156 | 96.415 ± 0.280 | 98.861 ± 0.219 |
| B-prof5 | 94.578 ± 0.639 | 74.752 ± 0.878 | 93.091 ± 0.290 | 78.216 ± 1.045 | 95.865 ± 0.460 | 98.618 ± 0.282 | não se aplica |

| modelo | classe | precisão | recall | F1 | AUC-PR, saída do modelo | AUC-PR, média das probabilidades dos bases |
| --- | --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.846 ± 0.012 | 99.650 ± 0.025 | 99.748 ± 0.012 | 99.919 ± 0.006 | 99.965 ± 0.006 |
| **A** | **Benign-DoH** | **87.021 ± 0.741** | **94.374 ± 0.447** | **90.546 ± 0.400** | **84.878 ± 0.758** | **95.543 ± 0.367** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.939 ± 0.019 | 99.967 ± 0.010 | 99.980 ± 0.009 | 99.996 ± 0.002 |
| B | Non-DoH | 99.866 ± 0.010 | 99.466 ± 0.030 | 99.666 ± 0.016 | 99.911 ± 0.007 | não se aplica |
| **B** | **Benign-DoH** | **81.993 ± 0.929** | **94.987 ± 0.326** | **88.010 ± 0.584** | **91.614 ± 0.752** | **não se aplica** |
| B | Malicious-DoH | 99.970 ± 0.013 | 99.961 ± 0.015 | 99.965 ± 0.008 | 99.991 ± 0.005 | não se aplica |
| C | Non-DoH | 99.882 ± 0.008 | 99.288 ± 0.049 | 99.584 ± 0.027 | 99.965 ± 0.005 | não se aplica |
| **C** | **Benign-DoH** | **77.439 ± 1.163** | **95.829 ± 0.291** | **85.655 ± 0.786** | **95.658 ± 0.406** | **não se aplica** |
| C | Malicious-DoH | 99.987 ± 0.007 | 99.955 ± 0.023 | 99.971 ± 0.011 | 99.997 ± 0.003 | não se aplica |
| A-prof5 | Non-DoH | 96.729 ± 0.234 | 99.837 ± 0.067 | 98.258 ± 0.103 | 99.236 ± 0.064 | 99.725 ± 0.063 |
| **A-prof5** | **Benign-DoH** | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.000 ± 0.000** | **26.830 ± 1.079** | **44.768 ± 6.667** |
| A-prof5 | Malicious-DoH | 99.539 ± 0.193 | 97.523 ± 0.729 | 98.519 ± 0.323 | 98.927 ± 0.192 | 99.507 ± 0.270 |
| B-prof5 | Non-DoH | 99.370 ± 0.048 | 93.763 ± 0.823 | 96.483 ± 0.416 | 99.665 ± 0.102 | não se aplica |
| **B-prof5** | **Benign-DoH** | **25.867 ± 2.082** | **88.050 ± 1.245** | **39.934 ± 2.343** | **42.762 ± 7.733** | **não se aplica** |
| B-prof5 | Malicious-DoH | 99.019 ± 1.002 | 97.460 ± 0.358 | 98.231 ± 0.515 | 99.454 ± 0.338 | não se aplica |

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0019 ± 0.0013 | 99.939 ± 0.019 |
| B | 0.0101 ± 0.0044 | 99.961 ± 0.015 |
| C | 0.0044 ± 0.0022 | 99.955 ± 0.023 |
| A-prof5 | 0.1502 ± 0.0633 | 97.523 ± 0.729 |
| B-prof5 | 0.3235 ± 0.3318 | 97.460 ± 0.358 |

## Comparação pareada

Pares: A contra B, A contra C, A-prof5 contra B-prof5. Método: comparação pareada por seed: diferença média (primeiro menos segundo), número de seeds em que cada modelo vence e teste de postos sinalizados de Wilcoxon bilateral (scipy.stats.wilcoxon com os parâmetros padrão: diferenças nulas descartadas). A diferença é a do primeiro modelo
menos a do segundo, em pontos percentuais (pp).

| par | conjunto | métrica | diferença média (pp) | desvio padrão das diferenças (pp) | seeds em que o primeiro vence | seeds em que o segundo vence | empates | estatística de Wilcoxon | p-valor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A contra B | teste inteiro | F1 macro | +0.8416 | 0.0948 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra B | teste inteiro | recall de Benign-DoH | -0.5924 | 0.3229 | 0 | 10 | 0 | 0 | 0.0020 |
| A contra B | teste sem vetores repetidos do treino | F1 macro | +0.8731 | 0.1022 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra B | teste sem vetores repetidos do treino | recall de Benign-DoH | -0.6127 | 0.3245 | 0 | 10 | 0 | 0 | 0.0020 |
| A contra C | teste inteiro | F1 macro | +1.6981 | 0.2846 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra C | teste inteiro | recall de Benign-DoH | -1.4380 | 0.4101 | 0 | 10 | 0 | 0 | 0.0020 |
| A contra C | teste sem vetores repetidos do treino | F1 macro | +1.6837 | 0.2850 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra C | teste sem vetores repetidos do treino | recall de Benign-DoH | -1.4546 | 0.3788 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste inteiro | F1 macro | -12.8263 | 1.0164 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste inteiro | recall de Benign-DoH | -87.1949 | 1.1692 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste sem vetores repetidos do treino | F1 macro | -12.6235 | 1.0266 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste sem vetores repetidos do treino | recall de Benign-DoH | -88.0499 | 1.2449 | 0 | 10 | 0 | 0 | 0.0020 |

Ressalva: os conjuntos de teste das seeds se sobrepõem e são sorteados da mesma tabela: os pares não são independentes, o p-valor é indicativo e não sustenta sozinho a palavra significativo.

O p-valor mínimo possível com 10 pares é 2/1024 (0.0020), o de um modelo vencer em todas as seeds: ele repete a contagem de vitórias e não mede tamanho de efeito. Regra de leitura: diferença média, em módulo, menor que o desvio padrão das diferenças pareadas não distingue os dois modelos. Comparações nessa condição: nenhuma.

## Taxa base

FPR de Malicious-DoH contra o resto no teste inteiro: mínimo, mediana e máximo
entre as 10 seeds, e os falsos positivos somados nas seeds, com o limite superior
do intervalo de confiança exato de 95% do FPR somado. Os testes das seeds se
sobrepõem, e o mesmo fluxo pode ser contado em mais de uma: as observações
somadas não são independentes, e o intervalo do FPR somado é mais estreito do
que a amostra sustenta. O intervalo de cada seed está em cada `metrics.json`.

| modelo | FPR mínimo entre seeds | FPR mediano | FPR máximo | falsos positivos somados | fluxos não maliciosos somados | limite superior do intervalo de confiança do FPR somado |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.0000% | 0.0016% | 0.0033% | 14 | 909560 | 0.0026% |
| B | 0.0044% | 0.0071% | 0.0143% | 76 | 909560 | 0.0105% |
| C | 0.0011% | 0.0033% | 0.0077% | 33 | 909560 | 0.0051% |
| A-prof5 | 0.0253% | 0.1347% | 0.1990% | 1129 | 909560 | 0.1316% |
| B-prof5 | 0.0385% | 0.0720% | 0.6047% | 2438 | 909560 | 0.2789% |

Precisão operacional de Malicious-DoH: a fração dos alertas que seria ataque
se a fração de fluxos maliciosos no tráfego fosse a prevalência indicada. As
prevalências são hipotéticas: o conjunto de dados não mede a prevalência
real. A conta usa o recall médio do teste inteiro e dois valores de FPR: o
médio entre seeds e o limite superior do intervalo do FPR somado. Com zero
falsos positivos, o FPR médio é zero e a precisão operacional sai 100% em
qualquer prevalência: o que a amostra permite afirmar é a coluna do limite
superior.

| modelo | prevalência hipotética | precisão operacional, FPR médio | alarmes falsos a cada dez milhões de fluxos, FPR médio | precisão operacional, limite superior do FPR | alarmes falsos a cada dez milhões de fluxos, limite superior do FPR |
| --- | --- | --- | --- | --- | --- |
| A | 0.001 | 98.48% | 154 | 97.48% | 258 |
| A | 0.0001 | 86.66% | 154 | 79.47% | 258 |
| A | 1e-05 | 39.37% | 154 | 27.90% | 258 |
| B | 0.001 | 92.29% | 835 | 90.54% | 1045 |
| B | 0.0001 | 54.47% | 835 | 48.87% | 1046 |
| B | 1e-05 | 10.69% | 836 | 8.72% | 1046 |
| C | 0.001 | 96.50% | 362 | 95.15% | 509 |
| C | 0.0001 | 73.37% | 363 | 66.24% | 509 |
| C | 1e-05 | 21.60% | 363 | 16.40% | 510 |
| A-prof5 | 0.001 | 44.02% | 12400 | 42.59% | 13145 |
| A-prof5 | 0.0001 | 7.28% | 12411 | 6.90% | 13157 |
| A-prof5 | 1e-05 | 0.78% | 12412 | 0.74% | 13158 |
| B-prof5 | 0.001 | 26.68% | 26777 | 25.92% | 27860 |
| B-prof5 | 0.0001 | 3.51% | 26801 | 3.38% | 27885 |
| B-prof5 | 1e-05 | 0.36% | 26804 | 0.35% | 27888 |

## Hipótese ao lado do resultado

A hipótese está em `HIPOTESE.md`, escrita antes da primeira execução e não
alterada depois. Os itens abaixo seguem a ordem do arquivo e usam o teste
inteiro. A hipótese diz que A contra B isola a arquitetura; como está na seção
Protocolo, o par difere também no balanceamento, e a diferença mede as duas
coisas juntas.

### O que se esperava

1. Esperado: diferença entre A e B da ordem do desvio padrão entre seeds ou menor. A hipótese não fixa o que é "da ordem"; a conta abaixo compara a diferença média, em módulo, com o maior dos dois desvios padrão entre seeds.
   - F1 macro: diferença média de +0.8416 pp (A menos B); desvio padrão entre seeds de 0.1196 pp em A e de 0.1752 pp em B. Diferença dentro do maior desvio: não ocorreu.
   - recall de Benign-DoH: diferença média de -0.5924 pp (A menos B); desvio padrão entre seeds de 0.5223 pp em A e de 0.4165 pp em B. Diferença dentro do maior desvio: não ocorreu.
2. Esperado: recall de Benign-DoH mais baixo nos modelos de profundidade 5 que nos sem limite de profundidade.
   - A-prof5 contra A: 0.000 ± 0.000% contra 93.073 ± 0.522%; A-prof5 fica abaixo em 10 das 10 seeds: **ocorreu**.
   - B-prof5 contra B: 87.195 ± 1.169% contra 93.666 ± 0.416%; B-prof5 fica abaixo em 10 das 10 seeds: **ocorreu**.

### O que a hipótese listava como resultado inesperado

1. A vencer B em todas as seeds, com diferença média maior que o desvio padrão entre seeds (aqui, o maior dos dois):
   - F1 macro: A vence em 10 das 10 seeds; diferença média de +0.8416 pp, maior desvio padrão entre seeds de 0.1752 pp: **ocorreu**.
   - recall de Benign-DoH: A vence em 0 das 10 seeds; diferença média de -0.5924 pp, maior desvio padrão entre seeds de 0.5223 pp: não ocorreu.
2. B ou C vencer A em todas as seeds:
   - B, F1 macro: vence A em 0 das 10 seeds (diferença média A menos B de +0.8416 pp): não ocorreu.
   - B, recall de Benign-DoH: vence A em 10 das 10 seeds (diferença média A menos B de -0.5924 pp): **ocorreu**.
   - C, F1 macro: vence A em 0 das 10 seeds (diferença média A menos C de +1.6981 pp): não ocorreu.
   - C, recall de Benign-DoH: vence A em 10 das 10 seeds (diferença média A menos C de -1.4380 pp): **ocorreu**.
3. Desvio padrão entre seeds maior que a diferença entre a leitura de profundidade variável e a de profundidade 5:
   - A e A-prof5, F1 macro: diferença entre as médias de +30.8829 pp; maior desvio padrão entre seeds de 0.1358 pp: não ocorreu.
   - A e A-prof5, recall de Benign-DoH: diferença entre as médias de +93.0734 pp; maior desvio padrão entre seeds de 0.5223 pp: não ocorreu.
   - B e B-prof5, F1 macro: diferença entre as médias de +17.2150 pp; maior desvio padrão entre seeds de 1.0337 pp: não ocorreu.
   - B e B-prof5, recall de Benign-DoH: diferença entre as médias de +6.4709 pp; maior desvio padrão entre seeds de 1.1692 pp: não ocorreu.
4. Queda grande das métricas no teste sem vetores repetidos. A hipótese não fixa o que é "grande", e não há veredito. Médias no teste inteiro e no teste sem vetores repetidos:
   - A: F1 macro de 96.556% para 96.754% (+0.198 pp); recall de Benign-DoH de 93.073% para 94.374% (+1.301 pp).
   - B: F1 macro de 95.714% para 95.881% (+0.167 pp); recall de Benign-DoH de 93.666% para 94.987% (+1.321 pp).
   - C: F1 macro de 94.857% para 95.070% (+0.212 pp); recall de Benign-DoH de 94.511% para 95.829% (+1.318 pp).
   - A-prof5: F1 macro de 65.673% para 65.592% (-0.080 pp); recall de Benign-DoH de 0.000% para 0.000% (+0.000 pp).
   - B-prof5: F1 macro de 78.499% para 78.216% (-0.283 pp); recall de Benign-DoH de 87.195% para 88.050% (+0.855 pp).

## Limitações

- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o tráfego das outras duas classes. Nenhum split
  dentro do conjunto remove essa diferença: um modelo pode separar as classes
  pela captura, e não pelo ataque.
- Os 10 conjuntos de teste são sorteados da mesma tabela e se sobrepõem. O
  desvio padrão entre seeds mede a variação entre sorteios desta tabela, não a
  variação entre redes ou entre capturas.
- Não houve seleção de hiperparâmetros. As configurações são as do artigo e as
  da biblioteca; um modelo de comparação ajustado poderia ter outro resultado.
- Fluxos da mesma sessão podem cair no treino e no teste. A avaliação sem
  vetores repetidos só remove as linhas idênticas, não as parecidas.

## Avaliação por máquina

Modelo A, 4 dobras, seed 0 nos sorteios do modelo.
Resultados em `A-fold<k>/seed0/`. Em cada dobra ficam no
teste todos os fluxos de uma das máquinas que geraram Non-DoH e Benign-DoH e de
uma parte das que geraram Malicious-DoH, nas duas listas pela ordem do endereço. Nenhuma
máquina aparece no treino e no teste da mesma dobra; normalizador,
subconjuntos, SMOTE e modelos são refeitos em cada dobra. As linhas por classe
estão na ordem Non-DoH, Benign-DoH, Malicious-DoH.

| dobra | máquinas no teste | linhas do teste por classe | acurácia | F1 macro | **recall Benign-DoH** | **precisão Benign-DoH** | recall Malicious-DoH | FPR Malicious-DoH |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 192.168.20.111, 192.168.20.144, 192.168.20.204, 192.168.20.205 | [217432, 12300, 121521] | 96.442% | 79.898% | **32.000%** | **68.859%** | 97.180% | 0.0061% |
| 1 | 192.168.20.112, 192.168.20.206, 192.168.20.207, 192.168.20.208 | [88235, 1335, 56387] | 98.749% | 73.819% | **19.251%** | **27.225%** | 99.865% | 0.0156% |
| 2 | 192.168.20.113, 192.168.20.209, 192.168.20.210 | [47457, 2580, 36353] | 98.163% | 85.433% | **42.287%** | **92.068%** | 99.986% | 0.0060% |
| 3 | 192.168.20.191, 192.168.20.211, 192.168.20.212 | [536685, 3531, 35292] | 98.257% | 72.414% | **30.869%** | **15.164%** | 99.977% | 0.2875% |
| média ± desvio padrão |  |  | 97.903 ± 1.007 | 77.891 ± 5.986 | **31.102 ± 9.424** | **50.829 ± 35.846** | 99.252 ± 1.383 | 0.0788 ± 0.1392 |

As dobras têm tamanhos e proporções de classe muito diferentes, porque as
máquinas geraram quantidades diferentes de tráfego: a média entre dobras pesa
cada dobra por igual e não é comparável à média entre seeds das seções acima.
Há uma execução por dobra, com uma seed: não há medida de variação entre seeds
aqui.

### O que as dobras medem

Medem se a separação entre Non-DoH e Benign-DoH aprendida em três máquinas vale
na quarta: as duas classes foram geradas pelas mesmas 4 máquinas, e em cada
dobra uma delas fica inteira no teste.

Não medem a generalização da detecção de Malicious-DoH, porque máquina e classe
se confundem: nenhuma máquina gerou tráfego legítimo e malicioso. Uma máquina
de Malicious-DoH deixada de fora continua diferente das de Non-DoH e Benign-DoH
do treino pela captura, e não só pelo ataque.

Ao lado do split aleatório do modelo A (classes na ordem Non-DoH, Benign-DoH, Malicious-DoH):

| dobra | recall de Benign-DoH | fração do teste com vetor repetido do treino | recall de Malicious-DoH | fluxos do treino por classe | treino em relação ao do split aleatório | amostras por classe no primeiro subconjunto |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 32.000% | 0.24% | 97.180% | [672377, 7446, 128032] | 77.4% | [224126, 128032, 128032] |
| 1 | 19.251% | 0.41% | 99.865% | [801574, 18411, 193166] | 97.1% | [267192, 193166, 193166] |
| 2 | 42.287% | 0.26% | 99.986% | [842352, 17166, 213200] | 102.8% | [280784, 213200, 213200] |
| 3 | 30.869% | 0.01% | 99.977% | [353124, 16215, 214261] | 55.9% | [117708, 214261, 214261] |
| split aleatório, média entre seeds | 93.073% | 13.64% | 99.939% | [800828, 17771, 224598] | 100.0% |  |

Ressalva: o treino muda de tamanho e de composição a cada dobra. Ele tem de
55.9% a 102.8% dos fluxos do treino do split aleatório, e a proporção entre as
classes não é a mesma, como mostram as contagens da tabela. A diferença de uma
dobra para o split aleatório mistura a máquina nova com o treino de outro
tamanho e de outra composição, e os números não separam as duas causas.
