# E1: reprodução do Balanced Stacked Random Forest, fiel (profundidade 5)

Gerado por `scripts/e1_reproducao.py`. Os números vêm de
`proposto/seed42/metrics.json`; os tempos de treino estão em `proposto/seed42/run.json`.
Random Forests base: profundidade máxima 5 nos submodelos (Seção IV-B). A outra leitura da profundidade
está ao lado desta em `../RESUMO.md`.
Uma única execução, com a seed 42: não há média nem desvio padrão.
Classes na ordem dos códigos: Non-DoH, Benign-DoH, Malicious-DoH.

## Teste ao lado da Fig. 4b

Reprodução:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88922 | 0 | 59 |
| Benign-DoH | 1975 | 0 | 0 |
| Malicious-DoH | 522 | 0 | 24433 |

Artigo, Fig. 4b:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88928 | 50 | 2 |
| Benign-DoH | 192 | 1782 | 1 |
| Malicious-DoH | 6 | 0 | 24949 |

Diferença (reprodução menos artigo):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | -6 | -50 | 57 |
| Benign-DoH | 1783 | -1782 | -1 |
| Malicious-DoH | 516 | 0 | -516 |

Soma das diferenças absolutas: 4711. Diferença de total: 1 (a matriz obtida soma 115911 fluxos; essa parte da distância vem do tamanho do conjunto). Diferença em pontos percentuais: acurácia -1.9886, precisão macro -33.3363, recall macro -30.7678, F1 macro -32.0168.

## Métricas do teste

- **Acurácia 97.7949%.** Fração dos fluxos do teste com a classe certa.
  76.8% do teste é Non-DoH, então a acurácia mede sobretudo essa
  classe e, sozinha, não diz se o túnel é detectado.
- **Recall de Malicious-DoH 97.9082%.** Fluxos de túnel no teste:
  24955; classificados em outra classe: 522. São os túneis que
  passam sem alerta.
- **Precisão de Malicious-DoH 99.7591%.** Fração dos alertas de túnel
  que são túnel de fato, na proporção de classes deste teste; em uma rede com
  menos tráfego malicioso a precisão é menor.
- **FPR de Malicious-DoH contra o resto 0.0649%.** 59 de
  90956 fluxos legítimos são classificados como túnel: é o alarme
  falso que o operador recebe. Intervalo de confiança de
  95%: de 0.0494% a 0.0837%.
- **Recall de Benign-DoH 0.0000%.** Fluxos de DoH legítimo no
  teste: 1975; classificados em outra classe: 1975. É a classe
  menor; o erro troca DoH legítimo por outra classe e só vira alarme falso
  quando a classe atribuída é Malicious-DoH.
- **F1 macro 65.8027%, precisão macro 65.6759%, recall
  macro 65.9473%.** A média macro pesa as três classes por igual, e
  por isso mostra o erro em Benign-DoH que a média ponderada
  (F1 ponderado 96.9555%) esconde.
- **AUC-ROC one-vs-rest macro: 0.961172 pela saída do
  meta-classificador e 0.988858 pela média das
  probabilidades dos bases.** A primeira ordena os fluxos só pelas combinações
  de rótulos dos três bases; a segunda mede a capacidade de ordenação dos
  Random Forests. Nenhuma das duas depende do limiar de decisão.

O modelo não prediz Benign-DoH em nenhuma linha. A precisão de uma classe sem predição é indefinida: ela entra como 0 na precisão macro e no F1 macro, em vez de a classe sair da média.

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
| Non-DoH | 800080 | 67 | 681 |
| Benign-DoH | 17747 | 1 | 23 |
| Malicious-DoH | 5093 | 30 | 219475 |

Artigo, Fig. 4a:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 800316 | 503 | 10 |
| Benign-DoH | 1816 | 15946 | 9 |
| Malicious-DoH | 93 | 9 | 224496 |

Diferença (reprodução menos artigo):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | -236 | -436 | 671 |
| Benign-DoH | 15931 | -15945 | 14 |
| Malicious-DoH | 5000 | 21 | -5021 |

Soma das diferenças absolutas: 43275. Diferença de total: -1 (a matriz obtida soma 1043197 fluxos; essa parte da distância vem do tamanho do conjunto). Diferença em pontos percentuais: acurácia -2.0323, precisão macro -32.9058, recall macro -30.6632, F1 macro -31.9153.

## Teste ao lado da Tabela II

A Tabela II não diz que média usa nem como calcula a AUC com três classes. Cada
valor do artigo aparece ao lado da nossa média macro e da ponderada.

| métrica da Tabela II | artigo | métrica obtida | valor | diferença (pp) |
| --- | --- | --- | --- | --- |
| auc | 0.9999 | roc_auc_ovr_macro | 0.961172 | -3.8728 |
| auc | 0.9999 | roc_auc_ovr_macro_base_mean | 0.988858 | -1.1042 |
| accuracy | 0.9998 | accuracy | 0.977949 | -2.1851 |
| f1 | 0.9991 | macro_f1 | 0.658027 | -34.1073 |
| f1 | 0.9991 | weighted_f1 | 0.969555 | -2.9545 |
| precision | 0.9991 | macro_precision | 0.656759 | -34.2341 |
| precision | 0.9991 | weighted_precision | 0.961475 | -3.7625 |
| recall | 0.9992 | macro_recall | 0.659473 | -33.9727 |
| recall | 0.9992 | weighted_recall | 0.977949 | -2.1251 |

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

Base 1: recall de Benign-DoH 85.1646%, precisão de Benign-DoH 29.8916%, acurácia 96.1272%.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 85312 | 3630 | 39 |
| Benign-DoH | 293 | 1682 | 0 |
| Malicious-DoH | 212 | 315 | 24428 |

Base 2: recall de Benign-DoH 85.9747%, precisão de Benign-DoH 30.0584%, acurácia 96.1108%.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 85291 | 3625 | 65 |
| Benign-DoH | 277 | 1698 | 0 |
| Malicious-DoH | 215 | 326 | 24414 |

Base 3: recall de Benign-DoH 85.1646%, precisão de Benign-DoH 27.8892%, acurácia 95.7511%.

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 85392 | 3557 | 32 |
| Benign-DoH | 293 | 1682 | 0 |
| Malicious-DoH | 251 | 792 | 23912 |

## Meta-classificador

O meta-classificador recebe o rótulo predito por cada base, como número. Ele é ajustado no treino original, sobre as predições de bases que já viram essas linhas ao serem treinados: todo o Benign-DoH e todo o Malicious-DoH estão nos três subconjuntos, e cada linha de Non-DoH em um deles. O artigo não descreve esse passo; a alternativa, com predições fora da amostra, não foi medida aqui.

Os bases discordam em 829 linhas do teste (0.7152%); nas demais os três dão o mesmo rótulo. Combinações em que o meta devolve uma classe que nenhum base predisse: 2 de 27, com 5473 linhas do teste.

| rótulos dos três bases | classe do meta | linhas do treino por classe real | linhas do teste |
| --- | --- | --- | --- |
| [0, 0, 0] | 0 | [767396, 2118, 1971] | 85685 |
| [0, 0, 1] | 0 | [99, 43, 0] | 20 |
| [0, 0, 2] | 0 | [106, 3, 22] | 14 |
| [0, 1, 0] | 0 | [575, 216, 8] | 74 |
| [0, 1, 1] | 0 | [122, 0, 1] | 9 |
| [0, 1, 2] | 0 | [30, 0, 0] | 2 |
| [0, 2, 0] | 0 | [134, 0, 1] | 13 |
| [0, 2, 1] | 0 | [0, 0, 0] | 0 |
| [0, 2, 2] | 1 | [1, 0, 11] | 0 |
| [1, 0, 0] | 0 | [463, 15, 18] | 62 |
| [1, 0, 1] | 0 | [59, 0, 0] | 2 |
| [1, 0, 2] | 0 | [0, 0, 0] | 0 |
| [1, 1, 0] | 0 | [330, 17, 121] | 65 |
| [1, 1, 1] | 0 | [31025, 15357, 2865] | 5473 |
| [1, 1, 2] | 1 | [0, 0, 0] | 0 |
| [1, 2, 0] | 0 | [0, 0, 0] | 0 |
| [1, 2, 1] | 2 | [244, 0, 39] | 25 |
| [1, 2, 2] | 2 | [0, 0, 0] | 0 |
| [2, 0, 0] | 0 | [2, 0, 0] | 0 |
| [2, 0, 1] | 2 | [0, 0, 0] | 0 |
| [2, 0, 2] | 2 | [1, 0, 1] | 0 |
| [2, 1, 0] | 2 | [0, 0, 193] | 19 |
| [2, 1, 1] | 2 | [17, 0, 1] | 3 |
| [2, 1, 2] | 2 | [27, 0, 6] | 4 |
| [2, 2, 0] | 2 | [118, 0, 3] | 18 |
| [2, 2, 1] | 2 | [0, 0, 4114] | 499 |
| [2, 2, 2] | 2 | [79, 2, 215223] | 23924 |

## O que não foi feito

- A busca de hiperparâmetros do artigo não é refeita: a grade não foi
  publicada, e os valores usados são os finais do artigo.
- One-sided selection não é aplicada: o artigo a cita sem descrever.
- A validação cruzada grava só a matriz de confusão; a AUC é calculada só no teste.

## Onde a matriz difere da do artigo

Sozinhos, no teste, os três bases têm recall de Benign-DoH de 85.16%, 85.97%, 85.16% e precisão de Benign-DoH de 29.89%, 30.06%, 27.89%. O modelo empilhado tem recall 0.00% e precisão 0.00% nessa classe.

A combinação em que os três bases dizem Benign-DoH ocorre em 49247 linhas do treino original, que é o que o meta-classificador vê: 31025 de Non-DoH, 15357 de Benign-DoH, 2865 de Malicious-DoH. A classe real mais frequente nela é Non-DoH, e o meta devolve Non-DoH para ela. No teste a combinação ocorre em 5473 linhas.

O artigo não informa a seed, a lista dos 29 atributos, a limpeza, o alvo e os
parâmetros do SMOTE, como o Non-DoH é dividido em três partes nem com que dados
o meta-classificador é treinado; as versões das bibliotecas são outras. Nenhuma
seed, hiperparâmetro ou regra de limpeza foi ajustada para aproximar o resultado.
