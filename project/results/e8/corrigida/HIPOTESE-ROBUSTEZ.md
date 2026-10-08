# E8: hipótese da robustez à manipulação da duração do fluxo

Escrita antes da primeira execução de `scripts/e8_robustez.py`. Trilha
`corrigida`. Este arquivo não é alterado depois que os resultados existem; a
leitura dos números fica em `RESUMO-ROBUSTEZ.md`. A hipótese da modificação
proposta está em `HIPOTESE.md` e não muda.

## O que o experimento testa

O artigo publica que a duração do fluxo é o atributo de maior importância
para a classe maliciosa (Fig. 5) e que acima de cerca de 40 segundos ela
empurra a predição para Malicious-DoH (Fig. 6a e Seção VI-B). Ele não avalia
um atacante que conheça essa explicação. O experimento mede duas coisas:

- **Parte A, ablação.** Quanto do desempenho em dados sem perturbação depende
  da duração e dos atributos calculados a partir dela: cada modelo é ajustado
  de novo sem `Duration`, e sem `Duration`, `FlowSentRate` e
  `FlowReceivedRate`.
- **Parte B, fragmentação.** Quanto o recall de Malicious-DoH cai quando os
  fluxos maliciosos do teste são trocados por fluxos mais curtos, como os que
  o túnel produziria se a sessão fosse cortada em várias conexões.

Alvo de comparação: o próprio modelo no teste sem perturbação (fator 1) e, na
ablação, o modelo com todos os atributos. O modelo proposto pela equipe é
comparado com o sistema do artigo em cada ponto.

**A parte B é uma perturbação no espaço de atributos, não um ataque
reproduzido em rede.** Nenhum tráfego é gerado, nenhum PCAP é reprocessado, e
o resultado é um limite aproximado do efeito de encurtar os fluxos.

## Modelo de ameaça desta avaliação

- **Objetivo do atacante:** evasão. Um fluxo de túnel DoH deve ser
  classificado como Non-DoH ou como Benign-DoH.
- **O que ele controla:** o cliente e o servidor do túnel, e portanto quando a
  conexão HTTPS que carrega o túnel é encerrada e reaberta. O extrator agrupa
  os pacotes em fluxos por conexão: encerrar a conexão antes encurta o fluxo e
  reduz os bytes que ele carrega.
- **O que ele sabe:** o que o artigo publicou, isto é, que a duração pesa na
  decisão e em que sentido. Ele não conhece os parâmetros do modelo, não
  consulta o detector e não ajusta a perturbação pela resposta dele: é um
  atacante informado pela explicação publicada, não um atacante adaptativo com
  acesso ao modelo.
- **O que ele não controla:** o modelo, os dados de treino, o normalizador, o
  extrator de atributos e o tráfego das outras duas classes. O treino não é
  alterado (não há envenenamento), e os fluxos Non-DoH e Benign-DoH do teste
  ficam como estão.
- **O que fica de fora do modelo de ameaça:** preenchimento de pacotes,
  inserção de atraso entre pacotes e qualquer mudança no conteúdo do túnel. O
  custo da fragmentação para o atacante (menor vazão, um handshake TCP e TLS
  a mais por conexão) não é medido.

## Modelos e colunas, fixados antes de rodar

As configurações estão em `ROBUSTNESS_MODELS`, `ROBUSTNESS_COLUMN_SETS`,
`FRAGMENTED_COLUMNS` e `FRAGMENTATION_FACTORS`, em `src/doh_ids/config.py`.

| modelo | o que é |
| --- | --- |
| A | o sistema empilhado do artigo, com os Random Forests base sem limite de profundidade ("variable tree depth", linha 3 do Algoritmo 1). É o "original" |
| M1M2 | o modelo proposto pela equipe: Random Forest único, sem SMOTE, com peso de classe. É a "modificação" |
| A-prof5 | o sistema do artigo com profundidade máxima 5 (Seção IV-B), ao lado |

| colunas | atributos retirados | atributos que ficam |
| --- | --- | --- |
| `todos` | nenhum | 29 |
| `sem_duration` | `Duration` | 28 |
| `sem_duration_taxas` | `Duration`, `FlowSentRate`, `FlowReceivedRate` | 26 |

Cada modelo é ajustado uma vez por seed e por conjunto de colunas, e esse
mesmo modelo é avaliado em todos os fatores de fragmentação. Os recortes são
`results/e8/corrigida/robustez-<modelo>-<colunas>/seed<k>/`.

Hiperparâmetros de M1M2: os escolhidos pela seleção já gravada em
`results/e8/corrigida/M1M2-cira/`, no treino da mesma seed e com os 29
atributos. A seleção não é refeita sem as colunas retiradas; é uma
simplificação, pelo custo, e o modelo sem colunas pode não ter a combinação
que venceria se a seleção fosse refeita.

Com 28 ou 26 colunas, os 28 atributos por divisão de A e de A-prof5
(Seção IV-A do artigo) passam a ser todos os atributos disponíveis: o sorteio
de atributos em cada divisão deixa de existir nesses modelos.

## A perturbação, fixada antes de rodar

Uma sessão de túnel cortada em `k` conexões de mesma duração vira `k` fluxos.
Cada fluxo malicioso do teste é trocado por um desses fragmentos:

- `Duration`, `FlowBytesSent` e `FlowBytesReceived` são divididos por `k`;
- `FlowSentRate` e `FlowReceivedRate` não mudam, porque são os bytes divididos
  pela duração;
- os outros 24 atributos (estatísticas de comprimento de pacote, de tempo de
  pacote e de tempo de resposta) ficam como estão.

Fatores: 1 (sem perturbação), 2, 4, 8 e 16. O normalizador é o do treino. Os
valores que a perturbação leva para fora da faixa do treino são contados.

Só os fluxos Malicious-DoH do teste são alterados. Como os `k` fragmentos de
um fluxo ficam com o mesmo vetor de atributos, o recall por fragmento é o
recall medido com um fragmento por fluxo.

Simplificações, declaradas antes de rodar:

1. **As estatísticas por pacote ficam fixas.** Em um fluxo fragmentado de
   verdade elas mudariam. A mais direta: o extrator mede o tempo de cada
   pacote a partir do início do fluxo, de modo que média, mediana e moda do
   tempo de pacote não passam da duração, e um fragmento mais curto teria
   estatísticas de tempo de pacote menores. Aqui elas não encolhem, e o vetor
   perturbado pode ter tempo médio de pacote maior que a duração, o que nenhum
   fluxo real tem. O script conta quantos vetores ficam assim em cada fator.
2. **O custo de abrir conexões não entra.** Cada conexão nova traz pacotes de
   handshake, que mudam os bytes e as estatísticas de comprimento de pacote.
3. **Os bytes divididos deixam de ser inteiros.** Não há arredondamento.
4. **Todos os fragmentos são iguais.** Um corte real produziria fragmentos de
   durações e bytes diferentes.

Efeito provável das simplificações: o resultado não mede um ataque real. A
queda de recall pode estar subestimada, porque as estatísticas de tempo de
pacote, que também mudariam, ficam com o valor do fluxo inteiro; ou
superestimada, porque parte dos vetores perturbados é incoerente e cai em
regiões do espaço de atributos que nenhum fluxo ocupa. Uma avaliação fiel
exigiria gerar o tráfego de novo ou reprocessar os PCAPs com o extrator.

## Protocolo, fixado antes de rodar

- Dados: `data/processed/cira.parquet`. Dez seeds, de 0 a 9; cada seed refaz o
  split 90/10 estratificado, que é o mesmo de `results/e4/corrigida/` e de
  `results/e8/corrigida/M1M2-cira/`, conferido pelo resumo dos índices.
- O teste é separado antes de qualquer ajuste. O normalizador, os
  subconjuntos, o SMOTE e os modelos só veem o treino, sem perturbação.
- Com todos os atributos, cada modelo é o mesmo já medido: o script confere
  que a matriz de confusão no teste sem perturbação é a gravada em
  `results/e4/corrigida/` (A e A-prof5) e em `results/e8/corrigida/M1M2-cira/`.
- Métricas: no teste sem perturbação, as de sempre; em cada fator, o recall de
  Malicious-DoH e a classe para onde vão os fluxos não detectados. Média e
  desvio padrão amostral entre as seeds.
- Comparação pareada por seed do recall de Malicious-DoH: M1M2 menos A, com as
  mesmas colunas, em cada fator; cada modelo sem colunas menos ele mesmo com
  todas, em cada fator; e, na parte A, a mesma comparação sem colunas contra
  todas em F1 macro e recall de Benign-DoH no teste sem perturbação.
- Corte por custo: a seed 0 é medida e o total projetado. Se a projeção passar
  de quatro horas, A-prof5 sai da execução, e isso é declarado no resumo. A e
  M1M2 não saem.

## Regra de leitura, fixada antes de rodar

A mesma da modificação proposta: uma diferença pareada **conta** quando a
média é, em módulo, maior que o desvio padrão das diferenças entre as seeds;
caso contrário os dois lados **não se distinguem**.

- Um modelo **degrada** em um fator quando o recall de Malicious-DoH nesse
  fator, menos o do fator 1, é negativo e conta pela regra.
- Um modelo **resiste melhor** que outro em um fator quando a diferença de
  recall entre os dois, nesse fator, é positiva e conta pela regra.

## O que já se sabia antes de rodar

Esta hipótese não foi escrita às cegas.

- `results/e5/variante/`, valores SHAP dos três Random Forests base do
  sistema do artigo sem limite de profundidade, seed 42. Para a classe
  Malicious-DoH, `PacketLengthMode` é o atributo de maior importância nos três
  bases, `PacketLengthMedian` o segundo e `Duration` o terceiro; no artigo
  `Duration` é o primeiro. `FlowBytesSent` e `FlowBytesReceived` ficam entre o
  8º e o 10º posto. O sinal do valor SHAP de `Duration` para Malicious-DoH
  troca perto de 33 s (corte medido de 33,13 s, contra os 40 s que o artigo
  lê): acima do corte a duração empurra para a classe maliciosa.
- A mesma fonte registra a mediana de `Duration` por classe no conjunto
  limpo: 0,31 s em Non-DoH, 4,10 s em Benign-DoH e 34,07 s em Malicious-DoH.
- `results/e4/corrigida/` e `results/e8/corrigida/`: no teste sem perturbação
  o recall de Malicious-DoH de A e de M1M2 passa de 99,9% em todas as seeds, e
  o de A-prof5 fica entre 95,5% e 97,9%.
- Conferências feitas na tabela limpa inteira antes de escrever a
  perturbação, sem nenhum modelo: as duas taxas são exatamente os bytes
  divididos pela duração, e média, mediana e moda do tempo de pacote não
  passam da duração em nenhuma linha. A primeira é asserção do script. Com a
  mediana de 34 s, dividir a duração por 2 já leva a maior parte dos fluxos
  maliciosos para baixo do corte de 33 s, e por 4 ou mais, quase todos; a
  contagem de cada seed é gravada pelo script.

Nenhuma predição em dado perturbado e nenhum modelo sem `Duration` foi visto
antes desta hipótese.

## O que se espera

1. **Parte A, A.** Sem `Duration`, e sem `Duration` e as taxas, o F1 macro e
   o recall de Malicious-DoH de A no teste sem perturbação não se distinguem
   dos de A com todos os atributos, ou caem menos de 1 ponto percentual: os
   atributos de comprimento de pacote sustentam a decisão.
2. **Parte A, M1M2.** O mesmo do item 1.
3. **Parte B, A com todos os atributos.** A degrada em todos os fatores a
   partir de 2, e o recall não aumenta de um fator para o seguinte. Não há
   previsão de tamanho: `Duration` é o terceiro atributo, não o primeiro, e a
   queda pode ser pequena.
4. **Parte B, M1M2 com todos os atributos.** M1M2 também degrada, e resiste
   melhor que A nos fatores a partir de 2: com cinco atributos sorteados por
   divisão e cem árvores, a decisão depende menos de um atributo só. É a
   expectativa em que a equipe tem menos confiança.
5. **Parte B, modelos sem colunas.** Os modelos sem `Duration` resistem
   melhor que o mesmo modelo com todos os atributos, mas não ficam imunes: os
   bytes do fluxo continuam no modelo e também são divididos pelo fator.
6. Os fluxos maliciosos que deixam de ser detectados vão mais para Non-DoH do
   que para Benign-DoH, porque duração curta e poucos bytes são o perfil de
   Non-DoH.

Não há expectativa declarada para A-prof5: ele é medido e reportado.

## O que contaria como resultado inesperado

- A ou M1M2 perder mais de 1 ponto percentual de F1 macro sem `Duration` no
  teste sem perturbação.
- Nenhum modelo degradar em nenhum fator: indicaria que a duração, apesar da
  importância publicada, não é manipulável com proveito por este caminho.
- O recall de um modelo subir de um fator para o seguinte.
- M1M2 resistir pior que A.
- Um modelo sem `Duration` resistir pior que o mesmo modelo com todos os
  atributos.
- A maior parte dos fluxos não detectados ir para Benign-DoH.

Qualquer um desses resultados é reportado como saiu.

## Riscos declarados

- A parte B não é um ataque medido; ver as simplificações acima. Nenhuma frase
  do resumo a apresenta como ataque sem essa ressalva.
- Valores perturbados podem cair fora da faixa do treino. Random Forest não
  extrapola: um valor abaixo do mínimo do treino é tratado como o menor valor
  visto. A contagem desses valores é gravada.
- Retirar `Duration` não tira a informação de duração do modelo: as
  estatísticas de tempo de pacote são medidas desde o início do fluxo e
  carregam a duração de forma indireta. A ablação mede a dependência da
  coluna, não da grandeza.
- O conjunto `sem_duration_taxas` mantém os bytes do fluxo, que a perturbação
  altera. Nenhum dos três conjuntos de colunas é imune por construção.
- Os dez conjuntos de teste se sobrepõem; os pares não são independentes, e o
  p-valor do teste de Wilcoxon é só indicativo.
- O tráfego malicioso do CIRA-CIC-DoHBrw-2020 foi capturado em outras máquinas
  e em outro período que o das outras classes. A duração pode separar as
  classes pelo modo como o tráfego foi gerado, e a perturbação herda isso.

## O que fica de fora

- Perturbação das estatísticas por pacote, preenchimento de pacotes e
  inserção de atraso.
- Atacante com acesso ao modelo (busca do menor fator que evade, por fluxo).
- O combinado CIRA + HKD: a avaliação é só no CIRA-CIC-DoHBrw-2020.
- O teste sem os vetores repetidos do treino: com colunas retiradas, o que é
  vetor repetido muda de um conjunto de colunas para outro, e a avaliação é
  feita só no teste inteiro.
- Treino com fluxos fragmentados (treino adversarial).
