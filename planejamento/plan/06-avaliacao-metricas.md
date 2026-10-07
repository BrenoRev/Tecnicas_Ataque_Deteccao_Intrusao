# 06 · avaliação · métricas e comparação com os alvos do artigo

**Onde:** `src/doh_ids/evaluate.py`, `tests/test_evaluate.py`
**Objetivo:** uma única função de avaliação, usada por todos os experimentos, que devolve as métricas certas para dados desbalanceados e a distância até os números do artigo.
**Depende de:** 02
**Demonstra:** testes que recalculam as métricas da Fig. 4b (acurácia 99,78%, recall de Benign-DoH 90,23%) a partir da matriz publicada. Define o alvo de P1.

> **Situação (07/10/2026, reconciliação no commit `360c3d3`): pronta em `21171f4`** (branch `tarefa/06-avaliacao-metricas`, nascida de `tarefa/05-split-scaler`; tipos anotados em `fdbdeb9`, já na branch da 08). Aguarda integração por pessoa (G10). A metade inferior da Tabela II não foi registrada e passa para a tarefa 09 (decisão 46).

## Como ficou (conferido no código em `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- `evaluate.py`: `metrics_from_confusion(confusion)`, `evaluate(y_true, y_pred, proba, base_mean_proba=None)`, `malicious_vs_rest(confusion)`, `base_rate(fpr, recall, prevalence)` e `compare_confusion(obtained, target)`. Tudo devolve só tipos nativos.
- Chaves de `metrics_from_confusion`: `confusion_matrix`, `total`, `accuracy`, `per_class` (pelo nome da classe: `support`, `precision`, `recall`, `f1`), `malicious_vs_rest` (`false_positives`, `negatives`, `fpr`, `fpr_ci_level`, `fpr_ci_low`, `fpr_ci_high`, `recall`) e `macro_*` e `weighted_*` de `precision`, `recall` e `f1`. `evaluate` acrescenta `roc_auc_ovr_macro` e `pr_auc` por classe; com `base_mean_proba`, também `roc_auc_ovr_macro_base_mean` e `pr_auc_base_mean`.
- `compare_confusion` devolve `cell_difference`, `absolute_difference_sum`, `total_difference` e `metric_difference_pp`. `base_rate` devolve `prevalence`, `operational_precision` e `false_alarms_per_10_million`.
- Classe que o modelo nunca prediz: a precisão entra como 0,0 (`_ratio`), em vez de a classe sair da média macro. É o caso da trilha fiel da tarefa 08, que não prediz Benign-DoH.
- **As funções nomeiam as classes por `CLASS_NAMES` e fixam a classe maliciosa pelo índice.** Servem para qualquer conjunto com as três classes do projeto (CIRA, combinado). Não servem, como estão, para a tarefa 21, em que as classes são as três ferramentas de túnel.
- `config.py` ganhou `FIG4A_CONFUSION`, `FIG4B_CONFUSION`, `FIG4_TRAIN_COUNTS` e `FIG4_TEST_COUNTS` (derivadas das matrizes; `scripts/e0_dados.py` passou a importá-las, e a duplicação apontada no bloco abaixo deixou de existir), `TABLE_II` (só a metade superior, chaves `decision_tree`, `xgboost`, `random_forest` e `balanced_stacked_rf`, cada uma com `auc`, `accuracy`, `f1`, `precision`, `recall`), `CONFIDENCE_LEVEL` e `BASE_RATE_FLOWS`.
- **Não feito: a metade inferior da Tabela II** (final do passo 5). Não há nenhuma linha da literatura em `config.py`. Com a decisão 46 ela é obrigatória; o registro e a conferência por dois integrantes ficam como critério de fechamento da tarefa 09.

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- Dependência: a 02 está pronta e não integrada. Em execução encadeada, a branch nasce de `tarefa/05-split-scaler`, com isso dito no relato. `config.py` já foi escrito pelas tarefas 02, 03 e 04.
- `config.py` já tem `CLASS_NAMES` (a posição na lista é o código da classe; é a ordem das matrizes do alvo) e `TABLE_I_COUNTS`. Os alvos desta tarefa entram no mesmo arquivo.
- As somas por linha das matrizes da Fig. 4 já existem em `scripts/e0_dados.py:75-76`, como `FIG4_TRAIN_COUNTS` e `FIG4_TEST_COUNTS`. Conferido: são iguais às somas por linha das matrizes de `scripts/metricas_fig4.py:13-24` depois de permutar a ordem das classes. Com as matrizes em `config.py`, o mesmo número passa a ter duas fontes. Tirar a duplicação exige editar `scripts/e0_dados.py`, que não está na lista de arquivos desta tarefa: combinar com o usuário antes; a alternativa sem tocar no script é um teste que confere as somas.
- O que `evaluate` e `metrics_from_confusion` devolvem vai direto para `save_run`, que grava com `json.dumps` sem conversor. Só tipos nativos: matriz como lista de listas, contagens como `int`. `numpy.int64` e array levantam `TypeError`.
- `save_run` grava em `metrics.json` só o dicionário de métricas. Tempo, leitura adotada e qualquer valor que varie entre execuções vão pelos argumentos `timings` e `config`.
- Referência do total do teste para a comparação célula a célula: `results/e0/dados/cira/seed42/split_counts.json`, chave `test.total`, 115.911.
- Fixture para os testes: `synthetic_flows`, 2.340 linhas (1.800 / 60 / 480).
- Pendente da equipe antes desta tarefa: a metade inferior da Tabela II, copiada do manuscrito e conferida por dois integrantes.

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

Conferido em 07/10/2026 no commit `360c3d3`. Executado: `tests/test_evaluate.py` inteiro, verde, pelo Python do ambiente do projeto (`-m pytest`), e `python3 scripts/metricas_fig4.py`, código 0.

- [x] Teste do invariante I8 verde: os valores batem com `scripts/metricas_fig4.py` até a quarta casa. Executado: `test_fig4b_metrics_match_the_published_matrix` (tolerância na quarta casa), `test_fig4b_metrics_match_the_reference_script_per_class` (10⁻¹² contra o script) e `test_base_rate_matches_the_reference_script_for_fig4b`.
- [x] Teste do invariante I7 verde. Executado: `test_every_aggregated_metric_key_names_its_average`.
- [x] Teste confirma que as matrizes em `config.py` são idênticas às de `scripts/metricas_fig4.py`, e `python3 scripts/metricas_fig4.py` continua rodando sem o pacote instalado. Executado: `test_config_matrices_equal_the_script_matrices_after_reordering_classes`; o script rodou com o `python3` do sistema, fora do ambiente do projeto.
- [x] A função de taxa base falha se chamada sem prevalência. Executado: `test_base_rate_fails_without_prevalence`.

## Testes

Seção "Tarefa 06" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de biblioteca: G1–G4, G7–G10.
