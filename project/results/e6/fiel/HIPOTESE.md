# E6: hipótese do sistema do artigo no segundo dataset

Escrita antes da primeira execução de `scripts/e6_dataset2.py`. Vale para as
duas leituras da profundidade dos Random Forests base: sem limite ("variable
tree depth", linha 3 do Algoritmo 1), em `results/e6/variante/`, que é o
sistema base desta etapa, e profundidade máxima 5 (Seção IV-B), em
`results/e6/fiel/`. Este arquivo não é alterado depois que os resultados
existem; a leitura dos números fica nos arquivos `RESUMO.md`.

## O que o experimento testa

Se o Balanced Stacked Random Forest do artigo, com os hiperparâmetros e o
protocolo da reprodução no CIRA-CIC-DoHBrw-2020 (E1), detecta túneis DoH de
ferramentas que o artigo não avaliou (dnstt, tcp-over-dns e tuns, do
DoH-Tunnel-Traffic-HKD). Três cenários, todos com a seed 42:

- **Transferência:** o sistema treinado só no treino do CIRA prediz os 5.258
  fluxos do HKD, normalizados com o scaler do treino do CIRA. O HKD só tem a
  classe maliciosa: a medida é o recall de Malicious-DoH, total e por
  ferramenta. Sem negativos, não há precisão, FPR nem acurácia.
- **Retreino no combinado sem réplicas:** o sistema inteiro é refeito no
  dataset combinado CIRA + HKD com cada fluxo do HKD uma única vez, com split
  90/10 estratificado, teste e validação cruzada de 10 folds. É o dataset
  principal desta etapa.
- **Retreino no combinado como publicado:** o mesmo, com o dataset de terceiros
  tal como distribuído, em que cada fluxo do HKD aparece 20 vezes.

Alvo de comparação: os resultados de E1 no CIRA, em `results/e1/`. O artigo não
traz figura nem tabela para o segundo dataset.

## O que se sabia antes de rodar

Dos arquivos de `results/e6/dados/` e de `results/e1/`, já versionados:

- Medianas dos fluxos do HKD ao lado das dos maliciosos do CIRA: `Duration`
  120,06 s contra 34,07 s; `FlowBytesSent` 21.375 contra 1.807;
  `FlowBytesReceived` 21.723,5 contra 4.896; `PacketLengthMean` 148,56 contra
  223,43.
- **Nenhum fluxo do HKD tem valor abaixo do mínimo ou acima do máximo do CIRA
  limpo inteiro, em nenhum dos 29 atributos** (`hkd/seed42/faixa_por_atributo.csv`).
  A faixa do CIRA ali é a das três classes juntas, treino e teste.
- No teste do CIRA, três valores normalizados ficam fora de [0, 1]
  (`results/e0/dados/cira/seed42/split_counts.json`).
- No combinado, Non-DoH e Benign-DoH são as mesmas linhas do CIRA; só a classe
  maliciosa ganha fluxos: 5.258 sem réplicas, 105.160 como publicado.
- Em E1, o sistema de profundidade variável tem, no teste do CIRA, recall de
  Malicious-DoH de 99,96% e de Benign-DoH de 92,91%; o de profundidade 5 tem
  recall de Malicious-DoH de 97,91% e não prediz Benign-DoH em nenhuma linha.

## Hipóteses

1. **Valores fora de [0, 1] na transferência.** A hipótese do planejamento,
   formulada só com as medianas, era: como os fluxos do HKD têm duração mediana
   de 120 s e bytes cerca de dez vezes maiores que os maliciosos do CIRA, parte
   dos valores normalizados cairá fora de [0, 1]. A medição de faixa listada
   acima, feita depois e antes desta execução, contraria essa expectativa: a
   mudança é de posição dentro da faixa do CIRA, não de faixa. O scaler é
   ajustado só no treino do CIRA (90% das linhas), então a contagem esperada é
   zero ou muito pequena; só haverá valor fora de [0, 1] onde o extremo do CIRA
   em um atributo ficou no teste e algum fluxo do HKD passa do extremo do
   treino. A hipótese original fica registrada como estava, com o fato medido
   ao lado.
2. **Recall na transferência.** O recall de Malicious-DoH nos fluxos do HKD é
   menor que o do teste do CIRA em E1, na mesma leitura de profundidade, porque
   as três ferramentas não estão no treino e as medianas de duração, bytes e
   tamanho de pacote mudam. Não há expectativa escrita sobre qual ferramenta
   cai mais nem para que classe vão os erros.
3. **Memorização no combinado publicado.** O recall das ferramentas do HKD no
   teste do retreino publicado é maior ou igual ao do retreino sem réplicas:
   com 20 cópias de cada fluxo, o split aleatório põe cópias idênticas em
   treino e teste. A diferença entre os dois mede o que é memorização.
4. **Métricas gerais do retreino.** Acurácia e métricas de Non-DoH e Benign-DoH
   ficam perto das de E1, porque essas duas classes são as mesmas linhas. Isso
   não mede generalização; a leitura útil é o recall por ferramenta.
5. **Leitura de profundidade 5.** Como em E1, o sistema de profundidade 5 não
   prediz Benign-DoH, ou quase não prediz, também no combinado.

## O que contaria como resultado inesperado

- Recall na transferência igual ou maior que o do teste do CIRA, ou perto de
  zero em alguma ferramenta.
- Muitos valores fora de [0, 1] na transferência, o que contrariaria a medição
  de faixa.
- Recall das ferramentas do HKD maior no retreino sem réplicas que no
  publicado, além do que o intervalo de confiança explica.
- Métricas de Non-DoH ou de Benign-DoH no retreino longe das de E1.

Qualquer desses resultados é reportado como saiu. Nenhuma seed, hiperparâmetro
ou regra de limpeza é ajustado depois de ver os números.

## Riscos de método declarados antes de rodar

- **Vazamento entre datasets:** ajustar o scaler com fluxos do HKD na
  transferência mudaria a pergunta. O script confere que o scaler é o do
  treino do CIRA.
- **Réplicas:** no combinado publicado, o recall das ferramentas do HKD inclui
  fluxos idênticos aos do treino. O script mede quantos e, na versão sem
  réplicas, confere que nenhum vetor de 29 atributos do HKD está em treino e
  teste ao mesmo tempo.
- **Quase-duplicatas:** os fluxos do HKD vêm de duas máquinas e de sessões
  longas, com duração mediana colada em 120 s. Fluxos da mesma sessão podem
  cair um em cada conjunto mesmo sem réplica exata; isso não é medido aqui.
- **Uma seed:** o teste do combinado sem réplicas tem cerca de 526 fluxos do
  HKD. O recall por ferramenta vem com `n` e intervalo de confiança binomial
  exato e é uma estimativa de uma única divisão.
- **Dois terços do dataset são o CIRA:** métricas gerais parecidas com as de E1
  são esperadas e não provam nada sobre as ferramentas novas.
