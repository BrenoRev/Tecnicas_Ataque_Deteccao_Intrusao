# E8: hipótese do tempo de inferência

Escrita antes da primeira execução de `scripts/e8_inferencia.py`. Trilha
`corrigida`. Este arquivo não é alterado depois que os resultados existem; a
leitura dos números fica em `RESUMO-INFERENCIA.md`. As hipóteses da modificação
(`HIPOTESE.md`) e da robustez (`HIPOTESE-ROBUSTEZ.md`) não mudam.

## O que o experimento testa

O artigo afirma uma redução de três vezes no tempo de **treino** (introdução,
Seção III-B e Seção VI) e não a mede. Sobre a **predição**, diz uma só coisa: as
árvores dos Random Forests têm profundidade máxima 5 "to keep the computation
fast enough during the prediction stage" (Seção IV-B). Nenhum tempo de
inferência é publicado, de modo que não há alvo numérico do artigo.

A modificação da equipe (M1M2) usa 100 árvores sem limite de profundidade, o
oposto da escolha que o artigo justifica pela predição. O experimento mede
quanto isso custa e confere a justificativa do artigo (A-prof5 contra A).

O tempo medido é o de normalizar e predizer, com um núcleo, em dois regimes:

- **lote:** o teste inteiro de uma vez, repetido 5 vezes depois de uma
  repetição de aquecimento; vale a mediana das 5;
- **fluxo a fluxo:** 1000 fluxos do teste, sorteados com a seed, preditos um
  por chamada, como um detector que classifica cada fluxo ao terminar; vale a
  mediana das 1000 chamadas, e o percentil 95 fica ao lado.

Ao lado do tempo, que depende da máquina, há uma medida determinística: os nós
de árvore percorridos por fluxo no teste, somados em todas as árvores. O
meta-classificador de A (uma regressão logística sobre três rótulos) não entra
nessa contagem.

## Modelos e pares, fixados antes de rodar

As configurações estão em `INFERENCE_MODELS`, `INFERENCE_COMPARISONS`,
`INFERENCE_BATCH_REPEATS` e `INFERENCE_SINGLE_FLOWS`, em `src/doh_ids/config.py`.

| conjunto | modelos | pares (primeiro contra segundo) |
| --- | --- | --- |
| CIRA-CIC-DoHBrw-2020 | A, A-prof5, M1, M1M2 | M1M2 e A; M1 e A; A-prof5 e A |
| combinado sem réplicas | A, M1M2 | M1M2 e A |

Cada modelo é ajustado de novo nas mesmas dez seeds e nos mesmos splits das
execuções já gravadas. O script para se a matriz de confusão no teste diferir
da gravada. M1M2 usa os hiperparâmetros que a seleção já gravada escolheu no
treino da mesma seed.

## O que se espera

1. **Nós por fluxo.** M1M2 percorre mais de duas vezes os nós de A, nos dois
   conjuntos: são 100 árvores contra 30. M1, com 10 árvores, percorre menos
   que A. A-prof5 percorre menos que A, porque nenhum caminho passa de 6 nós.
2. **Lote.** M1M2 é mais lento que A nos dois conjuntos; M1 e A-prof5 são mais
   rápidos que A no CIRA. A ordem dos tempos segue a ordem dos nós por fluxo.
3. **Fluxo a fluxo.** M1M2 é mais lento que A nos dois conjuntos. Em uma chamada
   de um fluxo, o custo fixo por árvore pesa mais que a profundidade: M1 é mais
   rápido que A, e A-prof5 não se distingue de A.

## Regra de leitura

A mesma das outras comparações pareadas de E8 (`paired_comparison` e
`paired_verdict`, em `src/doh_ids/evaluate.py`): por par e por regime, a
diferença seed a seed (primeiro menos segundo) conta quando a média é, em
módulo, maior que o desvio padrão das diferenças; caso contrário, os dois não
se distinguem. O valor de cada seed é a mediana do regime. A razão média entre
os tempos (primeiro sobre segundo) é informada ao lado, sem veredito próprio.

## O que seria inesperado

- M1M2 não ser mais lento que A em algum regime ou conjunto.
- A-prof5 não ser mais rápido que A em lote: a justificativa do artigo para a
  profundidade 5 não se sustentaria nesta implementação.
- No regime em lote, a razão de tempo de um par ficar fora do intervalo entre
  metade e o dobro da razão de nós por fluxo.

## Limitações, declaradas antes de rodar

- Uma máquina, um núcleo, sem isolamento de outros processos. As repetições e
  os modelos são intercalados para que uma variação de carga atinja todos, mas
  o tempo absoluto não se transfere para outra máquina; a medida que se
  transfere é a de nós por fluxo.
- O tempo é o da implementação usada (scikit-learn e mlxtend), não o do
  algoritmo: o empilhamento do mlxtend tem custo próprio de chamada.
- Não mede a extração de atributos do tráfego nem a espera pelo fim do fluxo.
  Num detector real, as duas vêm antes da predição e não dependem do modelo.
- Não há tempo de inferência no artigo para comparar.
