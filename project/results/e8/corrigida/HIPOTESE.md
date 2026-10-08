# E8: hipótese da modificação proposta pela equipe

Escrita antes da primeira execução de `scripts/e8_modificacao.py`. Trilha
`corrigida`. Este arquivo não é alterado depois que os resultados existem; a
leitura dos números fica em `RESUMO.md`.

## O que o experimento testa

Se um Random Forest único, sem SMOTE e sem empilhamento, com peso de classe
(`class_weight='balanced'`) e hiperparâmetros selecionados por validação
cruzada dentro do treino, classifica melhor que o sistema empilhado do artigo.
A comparação é feita em dez seeds e em dois conjuntos de dados: o
CIRA-CIC-DoHBrw-2020 e o combinado CIRA + HKD sem réplicas.

Alvo de comparação: o modelo A do protocolo corrigido, que é o sistema do
artigo com os Random Forests base sem limite de profundidade ("variable tree
depth", linha 3 do Algoritmo 1). No CIRA, A e A-prof5 são lidos de
`results/e4/corrigida/`; no combinado sem réplicas, A é ajustado por este
script.

A modificação responde a duas críticas ao sistema do artigo. A primeira: em
cada subconjunto de treino, Benign-DoH é aumentada com SMOTE de 17771 para
224598 fluxos (seed 0 de `results/e4/corrigida/`), de modo que a maior parte
da classe é sintética. A segunda: com 28 atributos candidatos por divisão, de
29, as árvores do Random Forest quase não diferem pelo sorteio de atributos
(Seção IV-A do artigo).

## Modelos, fixados antes de rodar

As configurações estão em `MODIFIED_MODELS`, `MODIFIED_GRID` e `MODIFIED_RUNS`,
em `src/doh_ids/config.py`.

| modelo | arquitetura | balanceamento | árvores, profundidade máxima, atributos por divisão | comparado com |
| --- | --- | --- | --- | --- |
| A | empilhado, três subconjuntos | SMOTE por subconjunto | 10, sem limite, 28 | referência |
| A-prof5 | empilhado, três subconjuntos | SMOTE por subconjunto | 10, 5, 28 | referência, ao lado |
| M1 | Random Forest único | peso de classe, sem SMOTE | 10, sem limite, 28 | A |
| M1-prof5 | Random Forest único | peso de classe, sem SMOTE | 10, 5, 28 | A-prof5 |
| M1M2 | Random Forest único | peso de classe, sem SMOTE | selecionados em cada seed | A |

M1M2 é o modelo proposto. M1 e M1-prof5 existem para separar efeitos: têm os
hiperparâmetros de Random Forest de A e de A-prof5, e diferem deles na
arquitetura (um modelo em vez de três e um meta-classificador) e no
balanceamento (peso de classe em vez de SMOTE), as duas coisas juntas. M1M2
difere de A em arquitetura, balanceamento e hiperparâmetros ao mesmo tempo: a
diferença entre M1M2 e A não isola nenhum dos três.

Grade da seleção, oito combinações de árvores, profundidade máxima e atributos
por divisão: (10, 5, sqrt), (100, 5, sqrt), (10, 10, sqrt), (100, 10, sqrt),
(10, sem limite, sqrt), (100, sem limite, sqrt), (10, 5, 28) e
(10, sem limite, 28). As duas últimas são as configurações do artigo nas duas
leituras de profundidade.

## Protocolo, fixado antes de rodar

- Dez seeds, de 0 a 9. Cada seed refaz o split 90/10 estratificado. No CIRA o
  split de cada seed é o mesmo de `results/e4/corrigida/`, conferido pelo
  resumo dos índices (`split_index_sha256`).
- O normalizador é o primeiro passo de um `Pipeline` e é reajustado em todo
  ajuste do modelo, inclusive em cada fold da seleção.
- Seleção de hiperparâmetros, refeita em cada seed e em cada conjunto de dados:
  subamostra estratificada de 25% do treino da seed, validação cruzada
  estratificada de 5 folds dentro dela, F1 macro médio nos folds; no empate,
  fica a combinação que vem antes na grade. O modelo final é ajustado no
  treino inteiro com a combinação escolhida. O teste da seed não participa da
  seleção e só é lido na avaliação final.
- Nenhuma amostra sintética entra no treino de M1, M1-prof5 e M1M2.
- Métricas no teste inteiro e no teste sem as linhas cujo vetor de 29
  atributos existe no treino da mesma seed, como média e desvio padrão
  amostral entre as seeds.
- Comparação pareada por seed, a modificação menos o modelo de referência, em
  recall de Benign-DoH, F1 macro, FPR de Malicious-DoH contra o resto e tempo
  de treino: diferença média, desvio padrão das diferenças, número de seeds em
  que cada modelo tem o valor maior e teste de postos sinalizados de Wilcoxon
  bilateral.
- No combinado sem réplicas, recall de Malicious-DoH por ferramenta de túnel.
  Com M1M2 ajustado no CIRA, recall nos fluxos do HKD, que não entram em
  nenhum ajuste.

## Regra de leitura, fixada antes de rodar

Para cada par e cada métrica: a modificação **melhora** a métrica quando a
diferença média tem o sinal favorável (positivo em recall e F1, negativo em
FPR e tempo) e é, em módulo, maior que o desvio padrão das diferenças
pareadas; **piora** quando tem o sinal desfavorável e passa do mesmo desvio;
nos outros casos os dois modelos **não se distinguem**.

O modelo proposto só é dito melhor que A em um conjunto de dados se melhorar o
F1 macro por essa regra no teste inteiro e no teste sem vetores repetidos, sem
piorar o recall de Benign-DoH nem o FPR de Malicious-DoH. Qualquer outro
resultado é relatado como não ter melhorado.

## O que já se sabia antes de rodar

Esta hipótese não foi escrita às cegas. Antes dela a equipe já tinha visto:

- `results/e4/corrigida/`, dez seeds no CIRA. A: F1 macro de 96,556 ± 0,120%,
  recall de Benign-DoH de 93,073 ± 0,522% e precisão de Benign-DoH de 87,001 ±
  0,663%. A-prof5: recall de Benign-DoH igual a zero nas dez seeds e F1 macro
  de 65,673 ± 0,136%. B, um Random Forest único com os hiperparâmetros de A e
  SMOTE no treino inteiro: F1 macro de 95,714 ± 0,175%.
- `results/e3/variante/`, uma execução com a seed 42 no CIRA. O recorte
  `rf_unico` é um Random Forest único, sem SMOTE, com peso de classe, 10
  árvores, sem limite de profundidade e atributos por divisão no padrão da
  biblioteca: F1 macro de 96,65%, recall de Benign-DoH de 92,20% e precisão de
  88,31%, contra 96,56%, 92,91% e 87,13% do sistema empilhado na mesma seed. O
  recorte `rf_unico-prof5`, o mesmo com profundidade 5: recall de Benign-DoH de
  89,52%, precisão de 19,89%, F1 macro de 75,47% e FPR de Malicious-DoH de
  0,4848%, contra 0,0649% do empilhado de profundidade 5.
- `results/e6/variante/`, uma execução com a seed 42: o sistema empilhado no
  combinado sem réplicas tem F1 macro de 96,42% e recall de 98,59% a 100% em
  cada ferramenta de túnel; ajustado só no CIRA, detecta 95 dos 5258 fluxos do
  HKD.
- A medição de custo feita antes desta execução. Para estimar o tempo, a grade
  inteira foi ajustada em um fold do treino da seed 0 do CIRA, e a medição
  imprimiu o F1 macro de validação de cada combinação: entre 0,74 e 0,78 nas
  combinações de profundidade 5, entre 0,85 e 0,87 nas de profundidade 10 e
  entre 0,959 e 0,972 nas sem limite de profundidade, com
  (100, sem limite, sqrt) à frente. Esses números vêm só do treino: o teste de
  nenhuma seed foi lido. Eles antecipam o que a seleção deve escolher, e por
  isso a expectativa 3 abaixo não é uma previsão independente.
- A mesma medição deu o custo: 35,9 s para ajustar a grade em um fold da
  subamostra de 25%, contra 231,6 s no treino inteiro. Nas execuções gravadas
  em `results/e4/corrigida/`, o ajuste e a avaliação de A no CIRA levaram de
  111,2 a 317,9 s por seed.

## O que se espera

1. M1 contra A, no CIRA: os dois não se distinguem em F1 macro nem em recall
   de Benign-DoH. Com os mesmos hiperparâmetros, tirar o SMOTE e o
   empilhamento não deve custar desempenho. M1 treina em menos tempo que A.
2. M1-prof5 contra A-prof5, no CIRA: M1-prof5 tem recall de Benign-DoH maior
   que zero em todas as seeds e melhora o F1 macro, mas piora o FPR de
   Malicious-DoH.
3. Seleção: uma combinação sem limite de profundidade é escolhida em todas as
   seeds, nos dois conjuntos de dados, e (100, sem limite, sqrt) é a mais
   frequente.
4. M1M2 contra A, no CIRA: M1M2 melhora o F1 macro, por menos de 1 ponto
   percentual. Não se espera melhora no recall de Benign-DoH: o ganho, se
   houver, vem de menos fluxos Non-DoH preditos como Benign-DoH. No FPR de
   Malicious-DoH os dois não se distinguem.
5. M1M2 contra A, no combinado sem réplicas: o mesmo do item 4.
6. Os vereditos dos itens 4 e 5 são os mesmos no teste inteiro e no teste sem
   vetores repetidos.
7. M1M2 leva mais tempo de treino que A, por causa da seleção.

Não há expectativa declarada para o recall por ferramenta de túnel no
combinado nem para o recall de M1M2 nos fluxos do HKD: os dois são medidos e
reportados.

## O que contaria como resultado inesperado

- M1 piorar o F1 macro ou o recall de Benign-DoH em relação a A.
- M1-prof5 com recall de Benign-DoH igual a zero em alguma seed.
- A seleção escolher profundidade 5 ou 10 em alguma seed.
- M1M2 ficar abaixo de A em F1 macro em todas as seeds.
- M1M2 piorar o recall de Benign-DoH ou o FPR de Malicious-DoH.
- Um veredito de melhora no teste inteiro que não se repete no teste sem
  vetores repetidos: indicaria ganho vindo de linhas que o modelo já viu.

## Riscos declarados

- A seleção é feita em 25% do treino, com cerca de um quarto dos fluxos de
  Benign-DoH. A combinação escolhida pode não ser a que venceria no treino
  inteiro.
- Há vetores de atributos repetidos dentro do treino. Na validação cruzada da
  seleção, o mesmo vetor pode cair no fold de ajuste e no de validação, o que
  favorece as combinações de árvores mais profundas.
- M1M2 difere de A em três coisas ao mesmo tempo. Uma diferença entre os dois
  não pode ser atribuída ao balanceamento, à arquitetura ou aos
  hiperparâmetros em separado.
- Os dez conjuntos de teste se sobrepõem. Os pares da comparação não são
  independentes, e o p-valor do teste de Wilcoxon é só indicativo.
- Uma seed controla o split, a subamostra, os folds e os modelos: o desvio
  padrão mistura essas fontes.
- O tempo de treino depende da carga da máquina. No CIRA, o tempo de A foi
  medido em outra execução, a do protocolo corrigido.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o das outras classes; nenhum split dentro do conjunto
  remove essa diferença.

## O que fica de fora

A explicabilidade do modelo proposto (importância global com `TreeExplainer`
sobre M1M2) não é feita nesta execução. Não há ajuste de limiar de decisão nem
variante que mantenha o SMOTE e só selecione hiperparâmetros.
