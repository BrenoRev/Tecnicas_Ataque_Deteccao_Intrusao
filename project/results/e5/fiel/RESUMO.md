# E5: explicabilidade com SHAP, fiel (profundidade 5)

Gerado por `scripts/e5_xai.py`. Os números vêm de `proposto/seed42/metrics.json`; os
tempos estão em `proposto/seed42/run.json`. Random Forests base:
profundidade máxima 5 nos submodelos (Seção IV-B). A outra leitura da profundidade está ao lado desta, em
`../RESUMO.md`. Uma única execução, com a seed 42.
Classes na ordem dos códigos: Non-DoH, Benign-DoH, Malicious-DoH.

## Modelo explicado

A explicação principal é a do sistema na leitura de profundidade variável, em `results/e5/variante/`. A leitura de profundidade 5 é explicada ao lado, em `results/e5/fiel/`. O motivo está no resultado da reprodução:

- **variante (profundidade variável):** no teste, o modelo empilhado tem recall de Benign-DoH de 92.91% (`results/e1/variante/`).
- **fiel (profundidade 5):** no teste, o modelo empilhado tem recall de Benign-DoH de 0.00% (`results/e1/fiel/`).

Um sistema que não prediz uma das três classes não sustenta a explicação das decisões dele. Os Random Forests base de profundidade 5, sozinhos, predizem as três classes, e é a eles que os valores SHAP se referem nas duas leituras.

## Amostras

Os valores SHAP são calculados com o `TreeExplainer` em duas amostras
estratificadas, de até 2000 fluxos por classe, sorteadas com a seed
42. O artigo fala em todo o treino (Fig. 5) e em todo o teste (Fig. 6).

| amostra | Non-DoH | Benign-DoH | Malicious-DoH | uso |
| --- | --- | --- | --- | --- |
| treino | 2000 | 2000 | 2000 | importância global (Fig. 5) |
| teste | 2000 | 1975 | 2000 | dependência e explicações locais (Figs. 6 a 8) |

As classes entram em partes iguais. A importância média pesa as três classes
por igual, e não na proporção do tráfego, em que Non-DoH é a maioria.

A tabela `proposto/seed42/importancia.csv` traz a média do valor absoluto de SHAP
por base, classe e atributo. As figuras usam o Random Forest base
1, o do primeiro subconjunto. Valor base (probabilidade média) de cada
classe nesse modelo: 37.29%, 31.35%, 31.36%.

## Importância global ao lado da Fig. 5

A Fig. 5 do artigo é um gráfico de barras com a média do valor absoluto de SHAP
de cada um dos 29 atributos. Ela não diz a classe; a legenda fala do tráfego
malicioso, e a comparação é com o ranking da classe Malicious-DoH.
Figura equivalente: `proposto/seed42/fig5_importancia_malicious-doh.png`; as das
outras duas classes estão na mesma pasta.

| posto | artigo, Fig. 5 | base 1 | base 2 | base 3 |
| --- | --- | --- | --- | --- |
| 1 | Duration | PacketLengthMode | PacketLengthMode | PacketLengthMode |
| 2 | PacketLengthMode | Duration | Duration | Duration |
| 3 | PacketTimeVariance | PacketTimeMedian | PacketTimeMedian | PacketTimeMedian |
| 4 | PacketLengthCoefficientofVariation | PacketLengthMedian | PacketLengthMedian | PacketLengthMedian |
| 5 | PacketLengthVariance | PacketLengthCoefficientofVariation | PacketLengthCoefficientofVariation | PacketLengthCoefficientofVariation |
| 6 | PacketLengthMean | PacketLengthMean | PacketLengthMean | PacketLengthMean |
| 7 | FlowBytesSent | FlowBytesSent | FlowBytesSent | ResponseTimeTimeSkewFromMedian |
| 8 | PacketTimeMean | ResponseTimeTimeSkewFromMedian | ResponseTimeTimeSkewFromMedian | FlowBytesSent |
| 9 | ResponseTimeTimeMedian | PacketTimeCoefficientofVariation | PacketLengthStandardDeviation | PacketTimeCoefficientofVariation |
| 10 | FlowBytesReceived | PacketLengthStandardDeviation | PacketTimeCoefficientofVariation | PacketLengthStandardDeviation |

Posto, em cada base, dos 10 primeiros atributos do artigo:

| atributo | posto no artigo | posto no base 1 | posto no base 2 | posto no base 3 |
| --- | --- | --- | --- | --- |
| Duration | 1 | 2 | 2 | 2 |
| PacketLengthMode | 2 | 1 | 1 | 1 |
| PacketTimeVariance | 3 | 21 | 21 | 22 |
| PacketLengthCoefficientofVariation | 4 | 5 | 5 | 5 |
| PacketLengthVariance | 5 | 16 | 20 | 17 |
| PacketLengthMean | 6 | 6 | 6 | 6 |
| FlowBytesSent | 7 | 7 | 7 | 8 |
| PacketTimeMean | 8 | 23 | 23 | 24 |
| ResponseTimeTimeMedian | 9 | 12 | 12 | 13 |
| FlowBytesReceived | 10 | 14 | 14 | 14 |

- **`Duration` no topo: não confirmado.** O artigo põe `Duration` em primeiro; nos três bases ela fica nos postos 2, 2, 2.
- **Dez primeiros.** Atributos entre os 10 primeiros do artigo que também estão entre os 10 primeiros de cada base: 5, 5, 5.
- **Ranking inteiro.** Correlação de postos de Spearman entre o ranking do artigo e o de cada base, nos 29 atributos: 0.616, 0.590, 0.571.
- **Famílias de atributos nos 10 primeiros** (o artigo cita, depois da duração, comprimento de pacote e variância do tempo de pacote): base 1: 5 de comprimento de pacote, 2 de tempo de pacote, 1 de tempo de resposta, 1 de bytes do fluxo; base 2: 5 de comprimento de pacote, 2 de tempo de pacote, 1 de tempo de resposta, 1 de bytes do fluxo; base 3: 5 de comprimento de pacote, 2 de tempo de pacote, 1 de tempo de resposta, 1 de bytes do fluxo.

## Estabilidade entre os três submodelos

Correlação de postos de Spearman entre os rankings de dois bases, sobre os
atributos que estão entre os 10 primeiros de pelo menos um deles.
O valor 1 quer dizer a mesma ordem.

| classe | bases 1-2 | bases 1-3 | bases 2-3 |
| --- | --- | --- | --- |
| Non-DoH | 0.988 | 1.000 | 0.988 |
| Benign-DoH | 0.988 | 0.976 | 0.952 |
| Malicious-DoH | 0.988 | 0.988 | 0.976 |

## Dependência de `Duration` ao lado da Fig. 6a

Figura equivalente: `proposto/seed42/fig6a_dependencia_duration.png`, com os dados
em `proposto/seed42/fig6_dependencia.csv`. Um ponto por fluxo da amostra do teste;
no eixo horizontal a duração em segundos, depois de desfeita a normalização;
no vertical o valor SHAP de `Duration` para a classe Malicious-DoH.

O artigo lê na Fig. 6a um limiar de 40 segundos: acima dele o valor SHAP de `Duration` para o tráfego malicioso seria positivo.

- Fluxos da amostra com duração acima de 40 s: 1485, dos quais 99.53% têm valor SHAP positivo.
- Fluxos com duração até 40 s: 4490, dos quais 19.40% têm valor SHAP positivo.
- Limiar que melhor separa valor positivo de não positivo nesta amostra: 33.13 s, com 99.75% dos fluxos do lado esperado.
- Menor duração com valor positivo: 0.0229 s; maior duração com valor não positivo: 112.57 s.

Ressalva sobre os dados: a mediana de `Duration` no dataset limpo é
0.31 s em Non-DoH, 4.10 s em Benign-DoH, 34.07 s em Malicious-DoH. A classe maliciosa foi capturada em outras máquinas e em outro
período, de modo que a duração pode separar as classes pelo modo como o tráfego
foi gerado, e não só pelo protocolo.

## Dependência de `FlowBytesSent` ao lado da Fig. 6b

Figura equivalente: `proposto/seed42/fig6b_dependencia_flowbytessent.png`. O artigo
chama a Fig. 6b de gráfico de interação; o que ela mostra é o valor SHAP de
`FlowBytesSent` contra o valor do atributo, com os pontos coloridos por
`FlowBytesReceived`. Os valores de interação de SHAP não foram calculados. Os
eixos estão em escala logarítmica; os do artigo são lineares, até 6.000 bytes.

O artigo aponta um grupo de fluxos com mais bytes recebidos que enviados e o
associa ao tráfego malicioso. Na amostra do teste:

- fluxos com mais bytes recebidos que enviados, por classe real:
  [1557, 988, 1579]; valor SHAP de `FlowBytesSent` positivo em 37.39% deles;
- demais fluxos, por classe real: [443, 987, 421]; valor SHAP positivo em
  84.17% deles.

## Explicações locais ao lado das Figs. 7 e 8

As Figs. 7 e 8 do artigo são telas do painel interativo: probabilidade por
classe, tabela de contribuição e gráfico de contribuição em cascata. As figuras
equivalentes trazem os três elementos. O fluxo explicado é o primeiro da classe
na amostra do teste; o artigo não diz como escolheu os dele. As probabilidades
são as do Random Forest base 1, que é o que os valores SHAP decompõem.

### Equivalente à Fig. 7: fluxo Malicious-DoH do teste

Arquivos `fig7_explicacao_malicious-doh.png` e `fig7_explicacao_malicious-doh.csv`. Classe predita pelo base 1: Malicious-DoH; pelo modelo empilhado: Malicious-DoH.

| medida | artigo, Fig. 7 | aqui |
| --- | --- | --- |
| probabilidade de Malicious-DoH (%) | 76.4 | 100.00 |
| média da população (%) | 33.31 | 31.36 |
| atributo de maior efeito | Duration = 120.817 (+14.68 pp) | PacketLengthMode = 68 (+65.14 pp) |

| motivo | valor no fluxo | efeito (pp) |
| --- | --- | --- |
| Média da população |  | +31.36 |
| PacketLengthMode | 68 | +65.14 |
| Duration | 33.3443 | +4.35 |
| PacketLengthCoefficientofVariation | 1.68327 | +0.49 |
| ResponseTimeTimeSkewFromMedian | -1.71044 | -0.47 |
| PacketTimeMedian | 0.068567 | -0.42 |
| PacketLengthMean | 223.4 | -0.40 |
| PacketTimeCoefficientofVariation | 1.64183 | -0.27 |
| PacketLengthSkewFromMedian | 1.17593 | +0.24 |
| FlowBytesSent | 1807 | -0.19 |
| PacketLengthStandardDeviation | 376.044 | +0.18 |
| Outros atributos somados |  | -0.01 |
| Predição final |  | +100.00 |

### Equivalente à Fig. 8: fluxo Non-DoH do teste

Arquivos `fig8_explicacao_non-doh.png` e `fig8_explicacao_non-doh.csv`. Classe predita pelo base 1: Non-DoH; pelo modelo empilhado: Non-DoH.

| medida | artigo, Fig. 8 | aqui |
| --- | --- | --- |
| probabilidade de Non-DoH (%) | 88.85 | 96.07 |
| média da população (%) | 33.33 | 37.29 |
| atributo de maior efeito | PacketLengthVariance = 468846 (+19.15 pp) | PacketLengthMode = 60 (+25.94 pp) |

| motivo | valor no fluxo | efeito (pp) |
| --- | --- | --- |
| Média da população |  | +37.29 |
| PacketLengthMode | 60 | +25.94 |
| PacketLengthMedian | 57.5 | +25.87 |
| ResponseTimeTimeMean | 0.0255875 | +3.24 |
| PacketLengthMean | 57.1667 | -2.32 |
| ResponseTimeTimeMedian | 0.0255875 | +2.28 |
| PacketTimeMedian | 33.8454 | +2.01 |
| PacketTimeCoefficientofVariation | 0.706704 | +1.89 |
| Duration | 33.8582 | +0.36 |
| PacketLengthCoefficientofVariation | 0.0499045 | -0.31 |
| PacketLengthSkewFromMedian | -0.350524 | +0.30 |
| Outros atributos somados |  | -0.50 |
| Predição final |  | +96.07 |

## Limitação

Os valores SHAP deste experimento explicam os Random Forests base, não a decisão do empilhamento. A linha 8 do Algoritmo 1 do artigo aplica o `TreeExplainer` sem dizer a qual modelo. O `TreeExplainer` recusa o modelo empilhado com o erro: `Model type not yet supported by TreeExplainer: <class 'mlxtend.classifier.stacking_classification.StackingClassifier'>`. A regressão logística que combina os três bases não é um modelo de árvores, e a decisão final do sistema passa por ela.

Na amostra do teste, a classe de maior probabilidade do base 1 é a classe que o modelo empilhado devolve em 69.99% dos fluxos. Predições do modelo empilhado na amostra: 4019 de Non-DoH, 0 de Benign-DoH, 1956 de Malicious-DoH. Onde os dois divergem, a explicação do base não é a explicação da saída do sistema.

## Ressalvas e o que não foi feito

- Nas seis colunas de assimetria o extrator grava -10 quando o desvio padrão é
  zero; 298766 fluxos do dataset limpo têm esse valor em alguma delas. A
  importância dessas colunas mede em parte esse marcador, e não a assimetria.
- Os valores SHAP são calculados em amostras, não no treino e no teste inteiros.
- Não há média entre seeds: uma execução, com a seed 42.
- O painel interativo é um script à parte e não grava resultado.
- Nenhuma seed, amostra ou fluxo foi escolhido para aproximar as figuras do artigo.
