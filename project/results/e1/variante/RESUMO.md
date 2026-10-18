# E1: reprodução do Balanced Stacked Random Forest, variante (profundidade variável)

Gerado por `scripts/e1_reproducao.py`. Os números vêm de
`profundidade_variavel/seed42/metrics.json`; os tempos de treino estão em `profundidade_variavel/seed42/run.json`.
Random Forests base: sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). A outra leitura da profundidade
está ao lado desta em `../RESUMO.md`.
Uma única execução, com a seed 42: não há média nem desvio padrão.
Classes na ordem dos códigos: Non-DoH, Benign-DoH, Malicious-DoH.

## Teste ao lado da Fig. 4b

Reprodução:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88709 | 269 | 3 |
| Benign-DoH | 140 | 1835 | 0 |
| Malicious-DoH | 8 | 2 | 24945 |

Artigo, Fig. 4b:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88928 | 50 | 2 |
| Benign-DoH | 192 | 1782 | 1 |
| Malicious-DoH | 6 | 0 | 24949 |

Diferença (reprodução menos artigo):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | -219 | 219 | 1 |
| Benign-DoH | -52 | 53 | -1 |
| Malicious-DoH | 2 | 2 | -4 |

Soma das diferenças absolutas: 553. Diferença de total: 1 (a matriz obtida soma 115911 fluxos; essa parte da distância vem do tamanho do conjunto). Diferença em pontos percentuais: acurácia -0.1475, precisão macro -3.3610, recall macro +0.8068, F1 macro -1.2640.

## Métricas do teste

- **Acurácia 99.6359%.** Fração dos fluxos do teste com a classe certa.
  76.8% do teste é Non-DoH, então a acurácia mede sobretudo essa
  classe e, sozinha, não diz se o túnel é detectado.
- **Recall de Malicious-DoH 99.9599%.** Fluxos de túnel no teste:
  24955; classificados em outra classe: 10. São os túneis que
  passam sem alerta.
- **Precisão de Malicious-DoH 99.9880%.** Fração dos alertas de túnel
  que são túnel de fato, na proporção de classes deste teste; em uma rede com
  menos tráfego malicioso a precisão é menor.
- **FPR de Malicious-DoH contra o resto 0.0033%.** 3 de
  90956 fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de
  95%: de 0.0007% a 0.0096%.
- **Recall de Benign-DoH 92.9114%.** Fluxos de DoH legítimo no
  teste: 1975; classificados em outra classe: 140. É a classe
  menor; o erro troca DoH legítimo por outra classe e só vira alarme falso
  quando a classe atribuída é Malicious-DoH.
- **F1 macro 96.5556%, precisão macro 95.6511%, recall
  macro 97.5219%.** A média macro pesa as três classes por igual, e
  por isso mostra o erro em Benign-DoH que a média ponderada
  (F1 ponderado 99.6415%) esconde.
- **AUC-ROC one-vs-rest macro: 0.993010 pela saída do
  meta-classificador e 0.997276 pela média das
  probabilidades dos bases.** A primeira ordena os fluxos só pelas combinações
  de rótulos dos três bases; a segunda mede a capacidade de ordenação dos
  Random Forests. Nenhuma das duas depende do limiar de decisão.



15842 das 115911 linhas do teste (13.67%) têm
vetor de 29 atributos idêntico ao de alguma linha do treino; em Non-DoH são
17.68%. Para o modelo essas linhas já foram vistas, e as
métricas acima as incluem.

## Validação cruzada ao lado da Fig. 4a

10 folds estratificados sobre o treino. Em cada rodada o normalizador,
os subconjuntos, o SMOTE, os bases e o meta são refeitos com os nove folds de
treino; o fold deixado de fora só é predito. A matriz soma o treino original,
sem amostra sintética.

Reprodução:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 798403 | 2416 | 9 |
| Benign-DoH | 1214 | 16556 | 1 |
| Malicious-DoH | 71 | 59 | 224468 |

Artigo, Fig. 4a:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 800316 | 503 | 10 |
| Benign-DoH | 1816 | 15946 | 9 |
| Malicious-DoH | 93 | 9 | 224496 |

Diferença (reprodução menos artigo):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | -1913 | 1913 | -1 |
| Benign-DoH | -602 | 610 | -8 |
| Malicious-DoH | -22 | 50 | -28 |

Soma das diferenças absolutas: 5147. Diferença de total: -1 (a matriz obtida soma 1043197 fluxos; essa parte da distância vem do tamanho do conjunto). Diferença em pontos percentuais: acurácia -0.1275, precisão macro -3.2710, recall macro +1.0604, F1 macro -1.0947.

## Teste ao lado da Tabela II

A Tabela II não diz que média usa nem como calcula a AUC com três classes. Cada
valor do artigo aparece ao lado da nossa média macro e da ponderada.

| métrica da Tabela II | artigo | métrica obtida | valor | diferença (pp) |
| --- | --- | --- | --- | --- |
| auc | 0.9999 | roc_auc_ovr_macro | 0.993010 | -0.6890 |
| auc | 0.9999 | roc_auc_ovr_macro_base_mean | 0.997276 | -0.2624 |
| accuracy | 0.9998 | accuracy | 0.996359 | -0.3441 |
| f1 | 0.9991 | macro_f1 | 0.965556 | -3.3544 |
| f1 | 0.9991 | weighted_f1 | 0.996415 | -0.2685 |
| precision | 0.9991 | macro_precision | 0.956511 | -4.2589 |
| precision | 0.9991 | weighted_precision | 0.996503 | -0.2597 |
| recall | 0.9992 | macro_recall | 0.975219 | -2.3981 |
| recall | 0.9992 | weighted_recall | 0.996359 | -0.2841 |

## Subconjuntos de treino

O artigo declara a razão 15:12:12 em cada subconjunto. A razão
obtida está escrita com Malicious-DoH valendo 12.

| subconjunto | amostras por classe | razão obtida | Benign-DoH sintético |
| --- | --- | --- | --- |
| 1 | [266943, 224598, 224598] | 14.3:12.0:12.0 | 92.09% |
| 2 | [266943, 224598, 224598] | 14.3:12.0:12.0 | 92.09% |
| 3 | [266942, 224598, 224598] | 14.3:12.0:12.0 | 92.09% |

## Bases isolados no teste

Cada Random Forest base avaliado sozinho, antes do empilhamento.

Base 1: recall de Benign-DoH 94.3291%, precisão de Benign-DoH 77.6897%, acurácia 99.4306%.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88442 | 533 | 6 |
| Benign-DoH | 112 | 1863 | 0 |
| Malicious-DoH | 7 | 2 | 24946 |

Base 2: recall de Benign-DoH 94.3797%, precisão de Benign-DoH 76.8026%, acurácia 99.4030%.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88408 | 562 | 11 |
| Benign-DoH | 111 | 1864 | 0 |
| Malicious-DoH | 7 | 1 | 24947 |

Base 3: recall de Benign-DoH 94.1266%, precisão de Benign-DoH 77.1689%, acurácia 99.4142%.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88430 | 544 | 7 |
| Benign-DoH | 116 | 1859 | 0 |
| Malicious-DoH | 6 | 6 | 24943 |

## Meta-classificador

O meta-classificador recebe o rótulo predito por cada base, como número. Ele é ajustado no treino original, sobre as predições de bases que já viram essas linhas ao serem treinados: todo o Benign-DoH e todo o Malicious-DoH estão nos três subconjuntos, e cada linha de Non-DoH em um deles. O artigo não descreve esse passo; a alternativa, com predições fora da amostra, não foi medida aqui.

Os bases discordam em 698 linhas do teste (0.6022%); nas demais os três dão o mesmo rótulo. Combinações em que o meta devolve uma classe que nenhum base predisse: 3 de 27, com 3 linhas do teste.

| rótulos dos três bases | classe do meta | linhas do treino por classe real | linhas do teste |
| --- | --- | --- | --- |
| [0, 0, 0] | 0 | [793893, 274, 2] | 88165 |
| [0, 0, 1] | 0 | [1238, 14, 0] | 148 |
| [0, 0, 2] | 0 | [28, 0, 2] | 3 |
| [0, 1, 0] | 0 | [1213, 0, 0] | 153 |
| [0, 1, 1] | 0 | [864, 18, 0] | 83 |
| [0, 1, 2] | 1 | [2, 0, 0] | 0 |
| [0, 2, 0] | 0 | [32, 0, 1] | 7 |
| [0, 2, 1] | 1 | [0, 0, 0] | 0 |
| [0, 2, 2] | 1 | [12, 0, 1] | 2 |
| [1, 0, 0] | 0 | [1192, 2, 0] | 135 |
| [1, 0, 1] | 0 | [850, 13, 0] | 72 |
| [1, 0, 2] | 1 | [1, 0, 0] | 0 |
| [1, 1, 0] | 0 | [868, 30, 0] | 88 |
| [1, 1, 1] | 1 | [600, 17420, 0] | 2103 |
| [1, 1, 2] | 1 | [0, 0, 1] | 0 |
| [1, 2, 0] | 1 | [2, 0, 0] | 0 |
| [1, 2, 1] | 1 | [0, 0, 0] | 0 |
| [1, 2, 2] | 2 | [0, 0, 1] | 0 |
| [2, 0, 0] | 0 | [20, 0, 0] | 3 |
| [2, 0, 1] | 1 | [0, 0, 0] | 0 |
| [2, 0, 2] | 1 | [3, 0, 1] | 0 |
| [2, 1, 0] | 1 | [0, 0, 0] | 0 |
| [2, 1, 1] | 1 | [0, 0, 0] | 0 |
| [2, 1, 2] | 2 | [0, 0, 1] | 0 |
| [2, 2, 0] | 1 | [9, 0, 6] | 1 |
| [2, 2, 1] | 2 | [0, 0, 1] | 3 |
| [2, 2, 2] | 2 | [1, 0, 224581] | 24945 |

## O que não foi feito

- A busca de hiperparâmetros do artigo não é refeita: a grade não foi
  publicada, e os valores usados são os finais do artigo.
- One-sided selection não é aplicada: o artigo a cita sem descrever.
- A validação cruzada grava só a matriz de confusão; a AUC é calculada só no teste.

## Onde a matriz difere da do artigo

Sozinhos, no teste, os três bases têm recall de Benign-DoH de 94.33%, 94.38%, 94.13% e precisão de Benign-DoH de 77.69%, 76.80%, 77.17%. O modelo empilhado tem recall 92.91% e precisão 87.13% nessa classe.

A combinação em que os três bases dizem Benign-DoH ocorre em 18020 linhas do treino original, que é o que o meta-classificador vê: 600 de Non-DoH, 17420 de Benign-DoH, 0 de Malicious-DoH. A classe real mais frequente nela é Benign-DoH, e o meta devolve Benign-DoH para ela. No teste a combinação ocorre em 2103 linhas.

O artigo não informa a seed, a lista dos 29 atributos, a limpeza, o alvo e os
parâmetros do SMOTE, como o Non-DoH é dividido em três partes nem com que dados
o meta-classificador é treinado; as versões das bibliotecas são outras. Nenhuma
seed, hiperparâmetro ou regra de limpeza foi ajustada para aproximar o resultado.
