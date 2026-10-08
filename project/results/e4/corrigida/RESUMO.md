# E4: protocolo corrigido, variância entre seeds e comparação pareada

Gerado por `scripts/e4_corrigido.py`. Trilha `corrigida`. Os números de cada
execução estão em `<modelo>/seed<k>/metrics.json`; a configuração, os tempos e
o commit, em `<modelo>/seed<k>/run.json`; as médias e a comparação pareada, sem
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

A contra B isola o efeito da arquitetura, porque os dois têm os mesmos
hiperparâmetros. A contra C é a comparação que o artigo faz na Tabela II. Os
modelos com `-prof5` repetem A e B com a profundidade máxima 5 da Seção IV-B do
artigo. O meta-classificador dos modelos empilhados é treinado como na
reprodução do artigo: este protocolo corrige a avaliação, não o desenho do
empilhamento.

Todo valor abaixo é média ± desvio padrão entre as seeds, em percentual. O
desvio padrão é o amostral. Uma seed controla o split, a reamostragem e os
modelos: o desvio mistura as três fontes de variação e não separa nenhuma.

## Teste inteiro

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro |
| --- | --- | --- | --- | --- | --- | --- |
| A | 99.637 ± 0.014 | 95.611 ± 0.219 | 97.570 ± 0.171 | 96.556 ± 0.120 | 99.643 ± 0.013 | 99.254 ± 0.175 |
| B | 99.533 ± 0.020 | 93.961 ± 0.268 | 97.723 ± 0.139 | 95.714 ± 0.175 | 99.548 ± 0.018 | 99.501 ± 0.045 |
| C | 99.421 ± 0.033 | 92.351 ± 0.398 | 97.949 ± 0.105 | 94.857 ± 0.258 | 99.449 ± 0.029 | 99.725 ± 0.037 |
| A-prof5 | 97.659 ± 0.133 | 65.571 ± 0.054 | 65.795 ± 0.231 | 65.673 ± 0.136 | 96.826 ± 0.135 | 96.381 ± 0.257 |
| B-prof5 | 95.168 ± 0.557 | 74.892 ± 0.891 | 93.118 ± 0.310 | 78.499 ± 1.034 | 96.310 ± 0.400 | 98.538 ± 0.291 |

Por classe. Benign-DoH, a classe menor, está em negrito. A classe que um modelo
não prediz em nenhuma linha do teste de uma seed entra com precisão 0 nessa seed.

| modelo | classe | precisão | recall | F1 | AUC-PR |
| --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.837 ± 0.012 | 99.698 ± 0.020 | 99.768 ± 0.010 | 99.898 ± 0.006 |
| **A** | **Benign-DoH** | **87.001 ± 0.663** | **93.073 ± 0.522** | **89.932 ± 0.352** | **83.626 ± 0.676** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.939 ± 0.019 | 99.967 ± 0.010 | 99.979 ± 0.010 |
| B | Non-DoH | 99.854 ± 0.010 | 99.543 ± 0.023 | 99.698 ± 0.013 | 99.918 ± 0.007 |
| **B** | **Benign-DoH** | **82.060 ± 0.810** | **93.666 ± 0.416** | **87.478 ± 0.516** | **90.590 ± 0.730** |
| B | Malicious-DoH | 99.970 ± 0.013 | 99.961 ± 0.015 | 99.965 ± 0.008 | 99.991 ± 0.006 |
| C | Non-DoH | 99.868 ± 0.007 | 99.380 ± 0.042 | 99.623 ± 0.022 | 99.964 ± 0.005 |
| **C** | **Benign-DoH** | **77.199 ± 1.192** | **94.511 ± 0.313** | **84.978 ± 0.753** | **94.476 ± 0.412** |
| C | Malicious-DoH | 99.987 ± 0.007 | 99.955 ± 0.023 | 99.971 ± 0.011 | 99.997 ± 0.003 |
| A-prof5 | Non-DoH | 97.173 ± 0.194 | 99.866 ± 0.055 | 98.501 ± 0.086 | 99.353 ± 0.051 |
| **A-prof5** | **Benign-DoH** | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.000 ± 0.000** | **27.208 ± 1.035** |
| A-prof5 | Malicious-DoH | 99.539 ± 0.193 | 97.519 ± 0.728 | 98.517 ± 0.323 | 98.887 ± 0.195 |
| B-prof5 | Non-DoH | 99.449 ± 0.039 | 94.704 ± 0.681 | 97.017 ± 0.343 | 99.712 ± 0.091 |
| **B-prof5** | **Benign-DoH** | **26.211 ± 2.139** | **87.195 ± 1.169** | **40.252 ± 2.393** | **43.243 ± 7.354** |
| B-prof5 | Malicious-DoH | 99.017 ± 1.004 | 97.456 ± 0.357 | 98.228 ± 0.517 | 99.434 ± 0.356 |

Malicious-DoH contra o resto:

| modelo | FPR de Malicious-DoH | recall de Malicious-DoH |
| --- | --- | --- |
| A | 0.0015 ± 0.0011 | 99.939 ± 0.019 |
| B | 0.0084 ± 0.0036 | 99.961 ± 0.015 |
| C | 0.0036 ± 0.0018 | 99.955 ± 0.023 |
| A-prof5 | 0.1241 ± 0.0522 | 97.519 ± 0.728 |
| B-prof5 | 0.2680 ± 0.2751 | 97.456 ± 0.357 |

Nos modelos empilhados, a AUC-ROC e a AUC-PR são calculadas com a saída do
meta-classificador, que só tem as combinações de rótulos dos três bases. A
AUC-ROC calculada com a média das probabilidades dos bases está em
`summary.json`, na chave `roc_auc_ovr_macro_base_mean`. As AUC dos empilhados
e as dos Random Forests únicos não medem a mesma coisa e não devem ser
comparadas diretamente.

## Teste sem vetores repetidos do treino

Em média, 13.64 ± 0.08% das linhas do teste têm os mesmos 29 atributos
de alguma linha do treino da mesma seed. As tabelas abaixo repetem a avaliação
sem essas linhas.

| modelo | acurácia | precisão macro | recall macro | F1 macro | F1 ponderado | AUC-ROC one-vs-rest macro |
| --- | --- | --- | --- | --- | --- | --- |
| A | 99.624 ± 0.016 | 95.620 ± 0.246 | 97.988 ± 0.146 | 96.754 ± 0.136 | 99.631 ± 0.015 | 99.505 ± 0.117 |
| B | 99.506 ± 0.024 | 93.943 ± 0.308 | 98.138 ± 0.110 | 95.881 ± 0.199 | 99.523 ± 0.022 | 99.564 ± 0.030 |
| C | 99.390 ± 0.039 | 92.436 ± 0.390 | 98.357 ± 0.104 | 95.070 ± 0.271 | 99.421 ± 0.036 | 99.777 ± 0.033 |
| A-prof5 | 97.400 ± 0.154 | 65.423 ± 0.062 | 65.787 ± 0.229 | 65.592 ± 0.142 | 96.492 ± 0.156 | 96.415 ± 0.280 |
| B-prof5 | 94.578 ± 0.639 | 74.752 ± 0.878 | 93.091 ± 0.290 | 78.216 ± 1.045 | 95.865 ± 0.460 | 98.618 ± 0.282 |

| modelo | classe | precisão | recall | F1 | AUC-PR |
| --- | --- | --- | --- | --- | --- |
| A | Non-DoH | 99.846 ± 0.012 | 99.650 ± 0.025 | 99.748 ± 0.012 | 99.919 ± 0.006 |
| **A** | **Benign-DoH** | **87.021 ± 0.741** | **94.374 ± 0.447** | **90.546 ± 0.400** | **84.878 ± 0.758** |
| A | Malicious-DoH | 99.994 ± 0.004 | 99.939 ± 0.019 | 99.967 ± 0.010 | 99.980 ± 0.009 |
| B | Non-DoH | 99.866 ± 0.010 | 99.466 ± 0.030 | 99.666 ± 0.016 | 99.911 ± 0.007 |
| **B** | **Benign-DoH** | **81.993 ± 0.929** | **94.987 ± 0.326** | **88.010 ± 0.584** | **91.614 ± 0.752** |
| B | Malicious-DoH | 99.970 ± 0.013 | 99.961 ± 0.015 | 99.965 ± 0.008 | 99.991 ± 0.005 |
| C | Non-DoH | 99.882 ± 0.008 | 99.288 ± 0.049 | 99.584 ± 0.027 | 99.965 ± 0.005 |
| **C** | **Benign-DoH** | **77.439 ± 1.163** | **95.829 ± 0.291** | **85.655 ± 0.786** | **95.658 ± 0.406** |
| C | Malicious-DoH | 99.987 ± 0.007 | 99.955 ± 0.023 | 99.971 ± 0.011 | 99.997 ± 0.003 |
| A-prof5 | Non-DoH | 96.729 ± 0.234 | 99.837 ± 0.067 | 98.258 ± 0.103 | 99.236 ± 0.064 |
| **A-prof5** | **Benign-DoH** | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.000 ± 0.000** | **26.830 ± 1.079** |
| A-prof5 | Malicious-DoH | 99.539 ± 0.193 | 97.523 ± 0.729 | 98.519 ± 0.323 | 98.927 ± 0.192 |
| B-prof5 | Non-DoH | 99.370 ± 0.048 | 93.763 ± 0.823 | 96.483 ± 0.416 | 99.665 ± 0.102 |
| **B-prof5** | **Benign-DoH** | **25.867 ± 2.082** | **88.050 ± 1.245** | **39.934 ± 2.343** | **42.762 ± 7.733** |
| B-prof5 | Malicious-DoH | 99.019 ± 1.002 | 97.460 ± 0.358 | 98.231 ± 0.515 | 99.454 ± 0.338 |

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

| par | conjunto | métrica | diferença média (pp) | seeds em que o primeiro vence | seeds em que o segundo vence | empates | estatística de Wilcoxon | p-valor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A contra B | teste inteiro | macro_f1 | +0.8416 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra B | teste inteiro | benign_doh_recall | -0.5924 | 0 | 10 | 0 | 0 | 0.0020 |
| A contra B | teste sem vetores repetidos do treino | macro_f1 | +0.8731 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra B | teste sem vetores repetidos do treino | benign_doh_recall | -0.6127 | 0 | 10 | 0 | 0 | 0.0020 |
| A contra C | teste inteiro | macro_f1 | +1.6981 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra C | teste inteiro | benign_doh_recall | -1.4380 | 0 | 10 | 0 | 0 | 0.0020 |
| A contra C | teste sem vetores repetidos do treino | macro_f1 | +1.6837 | 10 | 0 | 0 | 0 | 0.0020 |
| A contra C | teste sem vetores repetidos do treino | benign_doh_recall | -1.4546 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste inteiro | macro_f1 | -12.8263 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste inteiro | benign_doh_recall | -87.1949 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste sem vetores repetidos do treino | macro_f1 | -12.6235 | 0 | 10 | 0 | 0 | 0.0020 |
| A-prof5 contra B-prof5 | teste sem vetores repetidos do treino | benign_doh_recall | -88.0499 | 0 | 10 | 0 | 0 | 0.0020 |

Ressalva: os conjuntos de teste das seeds se sobrepõem e são sorteados da mesma tabela: os pares não são independentes, o p-valor é indicativo e não sustenta sozinho a palavra significativo. Diferença média menor que o desvio padrão entre
seeds das tabelas acima não distingue os dois modelos.

## Taxa base

Precisão operacional de Malicious-DoH: a fração dos alertas que seria ataque
se a fração de fluxos maliciosos no tráfego fosse a prevalência indicada. As
prevalências são hipotéticas: o conjunto de dados não mede a prevalência
real. A conta usa o FPR e o recall médios do teste inteiro.

| modelo | prevalência hipotética | precisão operacional | alarmes falsos a cada dez milhões de fluxos |
| --- | --- | --- | --- |
| A | 0.001 | 98.48% | 154 |
| A | 0.0001 | 86.66% | 154 |
| A | 1e-05 | 39.37% | 154 |
| B | 0.001 | 92.29% | 835 |
| B | 0.0001 | 54.47% | 835 |
| B | 1e-05 | 10.69% | 836 |
| C | 0.001 | 96.50% | 362 |
| C | 0.0001 | 73.37% | 363 |
| C | 1e-05 | 21.60% | 363 |
| A-prof5 | 0.001 | 44.02% | 12400 |
| A-prof5 | 0.0001 | 7.28% | 12411 |
| A-prof5 | 1e-05 | 0.78% | 12412 |
| B-prof5 | 0.001 | 26.68% | 26777 |
| B-prof5 | 0.0001 | 3.51% | 26801 |
| B-prof5 | 1e-05 | 0.36% | 26804 |

Falsos positivos de Malicious-DoH somados nas 10 seeds. Os testes se sobrepõem, e o
mesmo fluxo pode ser contado em mais de uma seed. Com zero falsos positivos, o
FPR médio é zero e a precisão operacional sai 100% em qualquer prevalência: o
que a amostra permite afirmar é o limite superior do intervalo de confiança do
FPR, gravado em cada `metrics.json`.

| modelo | falsos positivos somados | fluxos não maliciosos somados |
| --- | --- | --- |
| A | 14 | 909560 |
| B | 76 | 909560 |
| C | 33 | 909560 |
| A-prof5 | 1129 | 909560 |
| B-prof5 | 2438 | 909560 |

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
Nenhuma máquina gerou tráfego legítimo e malicioso, então esta avaliação
também não separa o ataque da captura. Há uma execução por dobra, com uma seed:
não há medida de variação entre seeds aqui.
