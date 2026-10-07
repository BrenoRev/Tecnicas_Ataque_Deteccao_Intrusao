# E1: as duas leituras da profundidade ao lado do artigo

Gerado por `scripts/e1_reproducao.py`. O artigo traz duas passagens sobre a
profundidade das árvores dos Random Forests base, e o sistema foi treinado e
avaliado uma vez com cada uma. Dados, seed (42), split, subconjuntos,
SMOTE e meta-classificador são os mesmos nas duas.

- **fiel (profundidade 5):** profundidade máxima 5 nos submodelos (Seção IV-B). Detalhe em `fiel/RESUMO.md`.
- **variante (profundidade variável):** sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). Detalhe em `variante/RESUMO.md`.

Uma única execução de cada leitura: não há média nem desvio padrão.
Classes na ordem dos códigos: Non-DoH, Benign-DoH, Malicious-DoH.

## Teste ao lado da Fig. 4b

Artigo, Fig. 4b:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88928 | 50 | 2 |
| Benign-DoH | 192 | 1782 | 1 |
| Malicious-DoH | 6 | 0 | 24949 |

fiel (profundidade 5):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88922 | 0 | 59 |
| Benign-DoH | 1975 | 0 | 0 |
| Malicious-DoH | 522 | 0 | 24433 |

variante (profundidade variável):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 88709 | 269 | 3 |
| Benign-DoH | 140 | 1835 | 0 |
| Malicious-DoH | 8 | 2 | 24945 |

| medida | Artigo, Fig. 4b | fiel (profundidade 5) | variante (profundidade variável) |
| --- | --- | --- | --- |
| soma das diferenças absolutas | 0 | 4711 | 553 |
| acurácia | 99.7835% | 97.7949% | 99.6359% |
| precisão de Non-DoH | 99.7778% | 97.2686% | 99.8334% |
| recall de Non-DoH | 99.9416% | 99.9337% | 99.6943% |
| F1 de Non-DoH | 99.8596% | 98.5831% | 99.7638% |
| precisão de Benign-DoH | 97.2707% | 0.0000% | 87.1320% |
| recall de Benign-DoH | 90.2278% | 0.0000% | 92.9114% |
| F1 de Benign-DoH | 93.6170% | 0.0000% | 89.9289% |
| precisão de Malicious-DoH | 99.9880% | 99.7591% | 99.9880% |
| recall de Malicious-DoH | 99.9760% | 97.9082% | 99.9599% |
| F1 de Malicious-DoH | 99.9820% | 98.8250% | 99.9739% |
| precisão macro | 99.0122% | 65.6759% | 95.6511% |
| recall macro | 96.7151% | 65.9473% | 97.5219% |
| F1 macro | 97.8195% | 65.8027% | 96.5556% |
| FPR de Malicious-DoH contra o resto | 0.0033% | 0.0649% | 0.0033% |

## Validação cruzada de 10 folds ao lado da Fig. 4a

Artigo, Fig. 4a:

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 800316 | 503 | 10 |
| Benign-DoH | 1816 | 15946 | 9 |
| Malicious-DoH | 93 | 9 | 224496 |

fiel (profundidade 5):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 800080 | 67 | 681 |
| Benign-DoH | 17747 | 1 | 23 |
| Malicious-DoH | 5093 | 30 | 219475 |

variante (profundidade variável):

| real \ predito | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Non-DoH | 798403 | 2416 | 9 |
| Benign-DoH | 1214 | 16556 | 1 |
| Malicious-DoH | 71 | 59 | 224468 |

| medida | Artigo, Fig. 4a | fiel (profundidade 5) | variante (profundidade variável) |
| --- | --- | --- | --- |
| soma das diferenças absolutas | 0 | 43275 | 5147 |
| acurácia | 99.7661% | 97.7338% | 99.6386% |
| precisão de Non-DoH | 99.7620% | 97.2245% | 99.8393% |
| recall de Non-DoH | 99.9359% | 99.9066% | 99.6972% |
| F1 de Non-DoH | 99.8489% | 98.5473% | 99.7682% |
| precisão de Benign-DoH | 96.8891% | 1.0204% | 86.9949% |
| recall de Benign-DoH | 89.7305% | 0.0056% | 93.1630% |
| F1 de Benign-DoH | 93.1725% | 0.0112% | 89.9734% |
| precisão de Malicious-DoH | 99.9915% | 99.6803% | 99.9955% |
| recall de Malicious-DoH | 99.9546% | 97.7190% | 99.9421% |
| F1 de Malicious-DoH | 99.9731% | 98.6899% | 99.9688% |
| precisão macro | 98.8809% | 65.9751% | 95.6099% |
| recall macro | 96.5403% | 65.8771% | 97.6008% |
| F1 macro | 97.6648% | 65.7495% | 96.5701% |
| FPR de Malicious-DoH contra o resto | 0.0023% | 0.0860% | 0.0012% |

## Bases isolados no teste

Os três Random Forests base de cada leitura, avaliados sozinhos:

- **fiel (profundidade 5):** recall de Benign-DoH 85.16%, 85.97%, 85.16%; precisão de Benign-DoH 29.89%, 30.06%, 27.89%.
- **variante (profundidade variável):** recall de Benign-DoH 94.33%, 94.38%, 94.13%; precisão de Benign-DoH 77.69%, 76.80%, 77.17%.

## Como ler a comparação

A soma das diferenças absolutas conta linhas, e Benign-DoH tem 1975 das
115911 linhas do teste (1.70%). Um modelo que nunca prediz
essa classe erra no máximo essas linhas, e a soma quase não registra a perda de
uma classe inteira. As métricas por classe e as médias macro, que pesam as três
classes por igual, registram. Por isso as duas medidas vão lado a lado e
nenhuma leitura é declarada a mais próxima do artigo por um número só.

- **fiel (profundidade 5):** O modelo não prediz Benign-DoH em nenhuma linha. A precisão de uma classe sem predição é indefinida: ela entra como 0 na precisão macro e no F1 macro, em vez de a classe sair da média.

As duas leituras têm apoio no texto do artigo e as duas são reportadas como
saíram. Nenhuma seed, hiperparâmetro ou regra de limpeza foi ajustada para
aproximar o resultado.
