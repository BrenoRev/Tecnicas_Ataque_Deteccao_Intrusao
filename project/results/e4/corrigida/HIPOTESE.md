# E4: hipótese do protocolo corrigido

Escrita antes da primeira execução de `scripts/e4_corrigido.py`. Trilha
`corrigida`. Este arquivo não é alterado depois que os resultados existem; a
leitura dos números fica em `RESUMO.md`.

## O que o experimento testa

Se o empilhamento de três Random Forests em subconjuntos balanceados, que é o
sistema do artigo, classifica melhor que um Random Forest único com os mesmos
hiperparâmetros, e quanto o resultado varia de um split para outro.

Alvo de comparação: a Tabela II do artigo, em que o modelo proposto tem F1 de
0,9991 e o Random Forest com SMOTE tem 0,9987. A diferença é de 0,0004, medida
em uma execução, contra um Random Forest de outros hiperparâmetros, e a tabela
não diz que média usa.

## Modelos, fixados antes de rodar

As configurações estão em `CORRIGIDA_MODELS`, em `src/doh_ids/config.py`. Não
há busca de hiperparâmetros.

| modelo | arquitetura | árvores | profundidade máxima | atributos por divisão | balanceamento |
| --- | --- | --- | --- | --- | --- |
| A | empilhado, três subconjuntos | 10 | sem limite | 28 | SMOTE por subconjunto |
| B | Random Forest único | 10 | sem limite | 28 | SMOTE no treino inteiro |
| C | Random Forest único, como na Tabela II | 10 | sem limite (padrão da biblioteca) | padrão da biblioteca | SMOTE no treino inteiro |
| A-prof5 | empilhado, três subconjuntos | 10 | 5 | 28 | SMOTE por subconjunto |
| B-prof5 | Random Forest único | 10 | 5 | 28 | SMOTE no treino inteiro |

O modelo A usa a leitura "variable tree depth" da linha 3 do Algoritmo 1 do
artigo; A-prof5 usa a profundidade máxima 5 da Seção IV-B. A contra B, e
A-prof5 contra B-prof5, isolam a arquitetura. A contra C é a comparação que o
artigo faz.

## Protocolo, fixado antes de rodar

- Dez seeds, de 0 a 9. Cada seed refaz o split 90/10 estratificado, o
  normalizador, os subconjuntos, o SMOTE e os modelos. Nenhuma seed é
  escolhida nem descartada.
- Todos os modelos de uma seed usam o mesmo treino e o mesmo teste.
- O meta-classificador dos modelos empilhados é treinado como na reprodução
  do artigo, nas predições dos bases sobre o treino original. A trilha
  corrigida conserta a avaliação, não o desenho do empilhamento.
- Cada métrica é reportada como média e desvio padrão amostral entre as seeds,
  com o nome da média (macro ou ponderada), no teste inteiro e no teste sem as
  linhas cujo vetor de 29 atributos existe no treino da mesma seed.
- Comparação pareada por seed em F1 macro e em recall de Benign-DoH: diferença
  média, número de seeds em que cada modelo vence e teste de postos
  sinalizados de Wilcoxon, bilateral.
- Taxa base com as prevalências hipotéticas de `HYPOTHETICAL_PREVALENCES`.
- Avaliação por máquina com o modelo A, em quatro dobras e com a seed 0 nos
  sorteios do modelo.

## O que se espera

- Que a diferença entre A e B seja da ordem do desvio padrão entre seeds ou
  menor: os dois veem os mesmos fluxos reais de Benign-DoH e de Malicious-DoH,
  e a diferença de 0,0004 da Tabela II é pequena para uma execução só.
- Que os modelos de profundidade 5 tenham recall de Benign-DoH mais baixo que
  os sem limite de profundidade, como já se mediu com a seed 42 em
  `results/e1/`.

## O que contaria como resultado inesperado

- A vencer B em todas as seeds, com diferença média maior que o desvio padrão
  entre seeds: seria evidência a favor do empilhamento que a Tabela II não dá.
- B ou C vencer A em todas as seeds.
- Desvio padrão entre seeds maior que a diferença entre a leitura de
  profundidade variável e a de profundidade 5.
- Queda grande das métricas no teste sem vetores repetidos, que indicaria que
  parte do resultado vem de linhas que o modelo já viu.

## Riscos declarados

- Os dez conjuntos de teste se sobrepõem. Os pares da comparação não são
  independentes, e o p-valor do teste de Wilcoxon é só indicativo.
- Uma seed controla o split, a reamostragem e os modelos: o desvio padrão
  mistura as três fontes.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o das outras classes. Nenhum split dentro do conjunto
  remove essa diferença, nem a avaliação por máquina, porque nenhuma máquina
  gerou as duas coisas.
- As prevalências da taxa base são hipotéticas: o conjunto não as mede.
