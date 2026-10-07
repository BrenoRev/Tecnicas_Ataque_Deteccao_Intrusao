# 06 · avaliação · métricas e comparação com os alvos do artigo

**Onde:** `src/doh_ids/evaluate.py`, `tests/test_evaluate.py`
**Objetivo:** uma única função de avaliação, usada por todos os experimentos, que devolve as métricas certas para dados desbalanceados e a distância até os números do artigo.
**Depende de:** 02
**Demonstra:** testes que recalculam as métricas da Fig. 4b (acurácia 99,78%, recall de Benign-DoH 90,23%) a partir da matriz publicada. Define o alvo de P1.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- O nosso teste tem 115.911 amostras e o da Fig. 4b, 115.910. A função de comparação célula a célula aceita matrizes com totais diferentes e devolve também a diferença de total, para a distância mínima de 1 ficar explícita e não ser lida como erro de modelo.

## Arquivos

- `src/doh_ids/evaluate.py` — novo.
- `tests/test_evaluate.py` — novo.
- `src/doh_ids/config.py` — acrescentar os alvos do artigo: matrizes da Fig. 4a e 4b e linhas da Tabela II.
- `scripts/metricas_fig4.py:13-24` — fonte das contagens das matrizes. O script não muda de números (foi ajustado ao lint em 07/10/2026) e continua rodando só com a biblioteca padrão; um teste confere que as matrizes em `config.py` são iguais às dele depois de permutar a ordem das classes.

## O que fazer

1. Duas funções. `metrics_from_confusion` recebe só a matriz de confusão e devolve precisão, recall e F1 por classe, médias macro e ponderada (com esses nomes nas chaves) e acurácia; é a que se aplica às matrizes do artigo. `evaluate` recebe rótulos reais, preditos e probabilidades por classe, monta a matriz, chama a primeira e acrescenta AUC-ROC one-vs-rest macro e AUC-PR por classe.
   - Para o modelo empilhado, `evaluate` aceita um segundo conjunto de probabilidades: a média das probabilidades dos três Random Forests base. Com `use_probas=False`, o meta-classificador só vê 27 combinações de rótulos e produz no máximo 27 vetores de probabilidade distintos; a AUC calculada a partir deles mede essa discretização, não a capacidade de ordenação do modelo (verificado em teste sintético: 0,800 contra 0,861 do Random Forest base). Reportar as duas AUC, nomeadas, e a ressalva.
2. Visão "malicioso contra o resto": falsos positivos, FPR com intervalo de confiança binomial exato, recall da classe maliciosa.
3. Função de taxa base: dada uma prevalência, devolve a precisão operacional e os alarmes falsos por dez milhões de fluxos. A prevalência é parâmetro obrigatório, sem valor padrão, para ninguém tratar um número hipotético como medido.
4. Função de comparação: recebe a matriz obtida e a do artigo e devolve a diferença célula a célula, a soma das diferenças absolutas e a diferença em pontos percentuais de cada métrica.
5. Registrar em `config.py` os alvos: as duas matrizes da Fig. 4 e as quatro linhas da Tabela II, com comentário indicando figura e tabela. As matrizes ficam na ordem da codificação do projeto (0 = Non-DoH, 1 = Benign-DoH, 2 = Malicious-DoH), que difere da ordem do script (`Benign-DoH, Malicious-DoH, Non-DoH`): o teste T06-2 permuta antes de comparar, porque uma comparação célula a célula sem essa permutação daria distâncias erradas sem nenhum erro aparente. Registrar também as linhas de outros trabalhos da metade inferior da Tabela II, copiadas do manuscrito com a referência de cada uma `[Preencher: copiar do PDF, conferido por dois integrantes]`, para a tabela de comparação com a literatura da tarefa 17.
6. Testes: aplicada à matriz da Fig. 4b, `metrics_from_confusion` devolve acurácia 99,78%, recall de Benign-DoH 90,23%, macro 99,01 / 96,72 / 97,82 e FPR de 3 em 90.955; matriz perfeita dá 1,0 em tudo; as chaves de média contêm "macro" ou "weighted"; a Fig. 4b montada a partir de rótulos na ordem 0, 1, 2 comparada com o alvo de `config.py` dá distância zero.

## Por quê

Decisões 10 e 16, ambiguidades A11 e A12. O artigo reporta médias sem nome e chama precisão de acurácia; se cada script calcular métricas do seu jeito, repetimos o problema que criticamos. A comparação célula a célula é a forma proposta de medir "resultados próximos o suficiente" enquanto o professor não define tolerância.

## Evidência — verificada no baseline

- `scripts/metricas_fig4.py:13-24` — contagens das duas matrizes.
- Saída de `python3 scripts/metricas_fig4.py` — valores esperados usados nos testes.
- `docs/02-artigo.md:58-65` — Tabela II.
- `docs/05-plano-experimental.md:133-143` — métricas e quando cada uma engana.

## Risco

- AUC a partir de rótulos em vez de probabilidades dá número errado sem erro: a função exige probabilidades e valida a forma.
- Intervalo de confiança com zero falsos positivos: tratar o caso sem dividir por zero (teste dedicado).

## Critério de aceite

- [ ] Teste do invariante I8 verde: os valores batem com `scripts/metricas_fig4.py` até a quarta casa.
- [ ] Teste do invariante I7 verde.
- [ ] Teste confirma que as matrizes em `config.py` são idênticas às de `scripts/metricas_fig4.py`, e `python3 scripts/metricas_fig4.py` continua rodando sem o pacote instalado.
- [ ] A função de taxa base falha se chamada sem prevalência.

## Testes

Seção "Tarefa 06" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de biblioteca: G1–G4, G7–G10.
