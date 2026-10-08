# E5: explicabilidade nas duas leituras da profundidade, ao lado do artigo

Gerado por `scripts/e5_xai.py`. Dados, seed (42), split, subconjuntos, SMOTE,
meta-classificador e amostras do SHAP são os mesmos nas duas leituras.

- **variante (profundidade variável):** sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Detalhe em `variante/RESUMO.md`.
- **fiel (profundidade 5):** profundidade máxima 5 nos submodelos (Seção IV-B). Detalhe em `fiel/RESUMO.md`.

A explicação principal é a do sistema na leitura de profundidade variável, em `results/e5/variante/`. A leitura de profundidade 5 é explicada ao lado, em `results/e5/fiel/`. O motivo está no resultado da reprodução:

- **variante (profundidade variável):** no teste, o modelo empilhado tem recall de Benign-DoH de 92.91% (`results/e1/variante/`).
- **fiel (profundidade 5):** no teste, o modelo empilhado tem recall de Benign-DoH de 0.00% (`results/e1/fiel/`).

Um sistema que não prediz uma das três classes não sustenta a explicação das decisões dele. Os Random Forests base de profundidade 5, sozinhos, predizem as três classes, e é a eles que os valores SHAP se referem nas duas leituras.

## Ranking de Malicious-DoH ao lado da Fig. 5

Random Forest base 1 de cada leitura, na amostra do treino.

| posto | artigo, Fig. 5 | variante (profundidade variável) | fiel (profundidade 5) |
| --- | --- | --- | --- |
| 1 | Duration | PacketLengthMode | PacketLengthMode |
| 2 | PacketLengthMode | PacketLengthMedian | Duration |
| 3 | PacketTimeVariance | Duration | PacketTimeMedian |
| 4 | PacketLengthCoefficientofVariation | PacketTimeMedian | PacketLengthMedian |
| 5 | PacketLengthVariance | PacketLengthSkewFromMode | PacketLengthCoefficientofVariation |
| 6 | PacketLengthMean | PacketLengthCoefficientofVariation | PacketLengthMean |
| 7 | FlowBytesSent | ResponseTimeTimeMedian | FlowBytesSent |
| 8 | PacketTimeMean | PacketLengthMean | ResponseTimeTimeSkewFromMedian |
| 9 | ResponseTimeTimeMedian | FlowBytesSent | PacketTimeCoefficientofVariation |
| 10 | FlowBytesReceived | FlowBytesReceived | PacketLengthStandardDeviation |

## Medidas lado a lado

| leitura | Spearman com a Fig. 5 (29 atributos) | atributos em comum nos 10 primeiros | corte que melhor separa o sinal do SHAP (s), amostra com classes em partes iguais | fluxos entre o corte medido e 40 s | SHAP positivo acima de 40 s | SHAP positivo até 40 s | base concorda com o empilhado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| variante (profundidade variável) | 0.515 | 7 | 33.13 | 869 | 97.37% | 20.51% | 99.50% |
| fiel (profundidade 5) | 0.616 | 5 | 33.13 | 869 | 99.53% | 19.40% | 69.99% |

As medidas são do Random Forest base 1, na amostra do teste com as classes
em partes iguais. O corte medido é o ponto em que o sinal do valor SHAP de
`Duration` troca na amostra; o artigo lê 40 s a olho na Fig. 6a e não informa a
amostra, e a diferença entre os dois não é atribuível. O detalhe por classe está
no resumo de cada trilha. A última coluna diz em que fração da amostra a classe
mais provável do base é a classe que o modelo empilhado devolve: é o alcance da
explicação do base como explicação do sistema.
