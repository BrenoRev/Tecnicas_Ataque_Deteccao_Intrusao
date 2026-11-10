# E8: tempo de inferência

Gerado por `scripts/e8_inferencia_resumo.py` a partir de `results/e8/corrigida/inferencia-<dados>/seed<k>/`. Hipótese, regra de leitura e o que seria inesperado: `HIPOTESE-INFERENCIA.md`, escrita antes da execução completa (ver, nas limitações, o teste de funcionamento anterior ao commit dela).

Seeds: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9. Tempo de normalizar e predizer, com uma thread. Lote: mediana de 5 repetições do teste inteiro. Fluxo a fluxo: mediana e percentil 95 de 1000 fluxos do teste preditos um por chamada. Média ± desvio padrão amostral entre as seeds. Nós por fluxo: nós de árvore percorridos por um fluxo, somados em todas as árvores, sem o meta-classificador de A.

Máquina (nome, núcleos): [('MacBook-Air-de-Breno-2.local', 10)]. Commits: ['4e5b1df5ec2577aa2f1ae86500287ea718e845a1'].

## CIRA-CIC-DoHBrw-2020

Teste: 115911 fluxos.

| modelo | árvores | nós por fluxo | lote, teste inteiro (ms) | lote, por fluxo (µs) | fluxo a fluxo, mediana (ms) | fluxo a fluxo, p95 (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| A | 30 | 463.0 ± 5.1 | 422.52 ± 145.50 | 3.65 ± 1.26 | 3.012 ± 1.536 | 7.423 ± 9.128 |
| A-prof5 | 30 | 164.3 ± 1.3 | 161.14 ± 36.72 | 1.39 ± 0.32 | 2.923 ± 1.449 | 7.077 ± 8.479 |
| M1 | 10 | 138.3 ± 1.7 | 117.44 ± 33.20 | 1.01 ± 0.29 | 1.468 ± 0.806 | 3.701 ± 4.701 |
| M1M2 | 100 | 1418.1 ± 7.9 | 1455.41 ± 441.47 | 12.56 ± 3.81 | 5.220 ± 2.198 | 12.117 ± 15.781 |

| par | métrica | razão média (primeiro / segundo) | diferença média | desvio padrão das diferenças | seeds em que o primeiro é maior | veredito para o primeiro |
| --- | --- | --- | --- | --- | --- | --- |
| M1M2 contra A | nós por fluxo | 3.06 | +955.123 nós | 10.407 nós | 10 de 10 | maior |
| M1M2 contra A | tempo em lote | 3.48 | +1032.898 ms | 303.827 ms | 10 de 10 | maior |
| M1M2 contra A | tempo fluxo a fluxo | 1.79 | +2.208 ms | 0.727 ms | 10 de 10 | maior |
| M1 contra A | nós por fluxo | 0.30 | -324.672 nós | 4.603 nós | 0 de 10 | menor |
| M1 contra A | tempo em lote | 0.28 | -305.076 ms | 113.194 ms | 0 de 10 | menor |
| M1 contra A | tempo fluxo a fluxo | 0.48 | -1.544 ms | 0.735 ms | 0 de 10 | menor |
| A-prof5 contra A | nós por fluxo | 0.35 | -298.707 nós | 5.350 nós | 0 de 10 | menor |
| A-prof5 contra A | tempo em lote | 0.39 | -261.376 ms | 111.167 ms | 0 de 10 | menor |
| A-prof5 contra A | tempo fluxo a fluxo | 0.98 | -0.090 ms | 0.089 ms | 0 de 10 | menor |

## combinado sem réplicas

Teste: 116437 fluxos.

| modelo | árvores | nós por fluxo | lote, teste inteiro (ms) | lote, por fluxo (µs) | fluxo a fluxo, mediana (ms) | fluxo a fluxo, p95 (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| A | 30 | 464.5 ± 7.7 | 352.29 ± 67.42 | 3.03 ± 0.58 | 2.139 ± 0.331 | 3.502 ± 2.024 |
| M1M2 | 100 | 1430.5 ± 5.3 | 1256.32 ± 218.63 | 10.79 ± 1.88 | 3.997 ± 0.617 | 6.177 ± 3.513 |

| par | métrica | razão média (primeiro / segundo) | diferença média | desvio padrão das diferenças | seeds em que o primeiro é maior | veredito para o primeiro |
| --- | --- | --- | --- | --- | --- | --- |
| M1M2 contra A | nós por fluxo | 3.08 | +966.024 nós | 12.197 nós | 10 de 10 | maior |
| M1M2 contra A | tempo em lote | 3.58 | +904.023 ms | 151.749 ms | 10 de 10 | maior |
| M1M2 contra A | tempo fluxo a fluxo | 1.87 | +1.857 ms | 0.286 ms | 10 de 10 | maior |

## Hipótese ao lado do resultado

1. Nós por fluxo. M1M2 percorre mais de duas vezes os nós de A nos dois conjuntos: **ocorreu** (razão média 3.06 no CIRA e 3.08 no combinado); M1 percorre menos que A: **ocorreu**; A-prof5 percorre menos que A: **ocorreu**.
2. Lote. M1M2 mais lento que A nos dois conjuntos: **ocorreu** (razão média 3.48 no CIRA e 3.58 no combinado); M1 mais rápido que A: **ocorreu**; A-prof5 mais rápido que A: **ocorreu**; a ordem dos tempos no CIRA segue a dos nós por fluxo: **ocorreu**.
3. Fluxo a fluxo. M1M2 mais lento que A nos dois conjuntos: **ocorreu** (razão média 1.79 no CIRA e 1.87 no combinado); M1 mais rápido que A: **ocorreu**; A-prof5 não se distingue de A: não ocorreu.

Resultados que a hipótese declarou como inesperados:

- M1M2 não ser mais lento que A em algum regime ou conjunto: não ocorreu.
- A-prof5 não ser mais rápido que A em lote: não ocorreu.
- Razão de tempo em lote fora do intervalo entre metade e o dobro da razão de nós por fluxo: não ocorreu.

## Leitura posterior

Acrescentada depois de ver os números. Não muda a regra de leitura nem os vereditos acima.

- **Profundidade 5, lote contra fluxo a fluxo.** A razão de tempo de A-prof5 sobre A é 0.39 em lote e 0.98 fluxo a fluxo, com razão de nós por fluxo 0.35. Numa chamada de um fluxo, a parte do tempo que não depende da profundidade das árvores domina; não se mediu qual é essa parte.
- **A-prof5 contra A fluxo a fluxo, no limite da regra.** O módulo da diferença média supera o desvio padrão das diferenças em 0.4%. A-prof5 é mais rápido em 10 de 10 seeds, com razão por seed entre 0.951 e 0.989. O veredito da regra fica como está; a frase que os números sustentam é que A-prof5 é cerca de 2% mais rápido por fluxo, em todas as seeds.
- **Variação entre seeds.** Coeficiente de variação de A entre as seeds: CIRA-CIC-DoHBrw-2020: 1.1% nos nós por fluxo, 34% no tempo em lote e 51% no fluxo a fluxo; combinado sem réplicas: 1.7% nos nós por fluxo, 19% no tempo em lote e 15% no fluxo a fluxo. Os nós por fluxo quase não variam, e o tempo varia muito: a variação vem do estado da máquina em cada seed, não do modelo. Por isso os tempos absolutos e os p95 não se citam sozinhos; as razões pareadas e os nós por fluxo, sim. No CIRA-CIC-DoHBrw-2020, o p95 fluxo a fluxo de A foi 7.4 ± 9.1 ms.

## Fluxos por segundo nesta máquina (posterior)

Fluxos por segundo equivalentes aos tempos médios, só da etapa de normalizar e predizer, com uma thread, nesta máquina e no estado de carga de cada seed. Não são a capacidade de um detector: ficam de fora a extração de atributos, a espera pelo fim do fluxo e o uso de mais threads. O que se compara entre modelos são as razões das tabelas de pares.

- CIRA-CIC-DoHBrw-2020: em lote, fluxos por segundo: A 274 mil, A-prof5 719 mil, M1 987 mil, M1M2 80 mil. Um fluxo por chamada, fluxos por segundo: A 332, A-prof5 342, M1 681, M1M2 192.
- combinado sem réplicas: em lote, fluxos por segundo: A 331 mil, M1M2 93 mil. Um fluxo por chamada, fluxos por segundo: A 467, M1M2 250.

## Limitações

- Uma máquina, uma thread de predição sem núcleo fixo, sem isolamento de outros processos. O sistema operacional não permite fixar a thread em um núcleo; a máquina tem núcleos de tipos diferentes e pode reduzir a frequência com a temperatura, e as threads da biblioteca de álgebra linear não foram limitadas. As repetições e os modelos foram intercalados, o que protege as razões pareadas, mas o tempo absoluto não se transfere para outra máquina; as medidas citáveis são as razões pareadas e os nós por fluxo.
- O tempo é o da implementação (scikit-learn e mlxtend), não o do algoritmo: o empilhamento do mlxtend faz três predições de Random Forest e uma da regressão logística por chamada.
- Não mede a extração de atributos do tráfego nem a espera pelo fim do fluxo, que vêm antes da predição num detector real e não dependem do modelo.
- O artigo não publica tempo de inferência: não há alvo para comparar.
- Antes do commit da hipótese, as funções de medição rodaram uma vez em uma amostra de 40 mil fluxos do CIRA, com A, A-prof5 e M1 ajustados nessa amostra e sem M1M2, para conferir que funcionavam. Esse teste exibiu os nós por fluxo e os tempos em lote e fluxo a fluxo dos três modelos. A hipótese já estava escrita e não mudou depois dele, mas a ordem dos commits não comprova isso: as expectativas 2 e 3 sobre A, A-prof5 e M1 devem ser citadas como registradas depois de um teste de funcionamento. As expectativas sobre M1M2 não são afetadas.
