# 05 · dados · split estratificado, normalização e contagens por conjunto

**Onde:** `src/doh_ids/splits.py`, `tests/test_splits.py`, `scripts/e0_dados.py`, `results/e0/dados/cira/seed42/`
**Objetivo:** treino e teste separados uma única vez, de forma reprodutível, com a normalização ajustada só no treino e a tabela de amostras por classe que o relatório exige.
**Depende de:** 04
**Demonstra:** `split_counts.json`: amostras por classe em treino, nos dez folds de validação e no teste, ao lado dos valores da Fig. 4. Seção 6: pergunta explícita da especificação.

> **Situação (07/10/2026, reconciliação no commit `0ae2d49`): pronta e executada em `0ae2d49`** (branch `tarefa/05-split-scaler`, nascida de `tarefa/04-carga-limpeza`; código em `56db5fb` e `121cde9`, resultado em `0ae2d49`). Aguarda integração por pessoa (G10).

## Como ficou (conferido no código em `0ae2d49`)

- `splits.py`: `stratified_split(flows, seed)` recebe a tabela com `label` e devolve `(train, test)`, dois DataFrames com o índice original. `fit_scaler(train)` devolve o `MinMaxScaler` ajustado em `feature_matrix(train)`; a transformação é `scaler.transform(feature_matrix(...))`, que devolve um array sem nomes de coluna, na ordem de `FEATURE_COLUMNS`. `seen_in_train(train, test)` devolve o vetor booleano, na ordem de `test`, das linhas cujo vetor de 29 atributos existe no treino.
- Os folds de validação são `StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED_FIEL)` sobre `train` e `train["label"]`, em `validation_fold_rows` de `scripts/e0_dados.py:189-195`. `CV_FOLDS = 10` é constante local do script (`:80`), não de `config.py`. Também são locais do script `FIG4_TRAIN_COUNTS`, `FIG4_TEST_COUNTS` (somas por linha das matrizes da Fig. 4) e `outside_unit_interval(train, test)`.
- `split_counts.json` é gravado pelo script ao lado do `metrics.json`, sem passar por `save_run`. Chaves: `classes`, `seed`, `test_size`, `train` e `test` (cada um com `rows`, `total`, `difference` e `fig4a` ou `fig4b`), `validation_folds` (`n_folds`, `validation_rows`, `train_rows`), `test_outside_unit_interval` (`values`, `rows`, `by_column`) e `test_seen_in_train` (`rows`, `total`, `fraction`, `fraction_total`).
- Medido e gravado (passo 4): três valores do teste normalizado fora de [0, 1], em três linhas, um em cada coluna: `FlowSentRate`, `PacketLengthMean` e `ResponseTimeTimeCoefficientofVariation`. É a referência da tarefa 14.
- Medido e gravado (passo 6): 15.842 linhas do teste com vetor presente no treino, 13,67% do total; por classe 15.733 / 107 / 2, ou 17,68% / 5,42% / 0,008%. Confere com o bloco abaixo.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- Com a limpeza adotada e `test_size=0.1`, estratificado, seed 42: treino 800.828 / 17.771 / 224.598 (1.043.197) e teste 88.981 / 1.975 / 24.955 (115.911).
- **Uma amostra de Non-DoH de diferença para a Fig. 4** (800.829 no treino e 88.980 no teste). O scikit-learn arredonda o teste para cima; Benign-DoH e Malicious-DoH batem exatamente. O tamanho do teste não é forçado para 115.910 (decisão 35): o script dos autores usa `test_size=0.1`. O critério "contagens idênticas às da Fig. 4" passa a ser "idênticas em Benign-DoH e Malicious-DoH e com uma amostra de diferença em Non-DoH, registrada".
- Fração do teste cujo vetor de 29 atributos existe no treino, medida com seed 42: 13,7% no total; 17,7% em Non-DoH, 5,4% em Benign-DoH, 0,01% em Malicious-DoH. É o valor esperado do passo 6; a tarefa 11 depende dele.
- Os valores acima foram medidos fora do repositório. O que vale para o relatório é o que `scripts/e0_dados.py` gravar; se divergir destes, parar e investigar antes de seguir.

## Arquivos

- `src/doh_ids/splits.py` — novo: split estratificado e ajuste do normalizador.
- `tests/test_splits.py` — novo.
- `scripts/e0_dados.py` — acrescentar a geração da tabela de contagens por conjunto.
- `results/e0/dados/cira/seed42/split_counts.json` — gerado.

## O que fazer

1. Escrever a função de split: 90% treino, 10% teste, estratificado pela classe, com seed. Devolve os dois conjuntos com os índices originais preservados.
2. Escrever a função de normalização: ajusta um `MinMaxScaler` com o treino e devolve o objeto; a transformação do teste usa esse mesmo objeto.
3. No script de E0, com seed 42, gerar a tabela de amostras por classe em treino e teste e gravar ao lado dos valores deduzidos da Fig. 4: treino 800.829 / 17.771 / 224.598, teste 88.980 / 1.975 / 24.955.
4. Contar quantos valores do teste normalizado caem fora de [0, 1] e registrar. É esperado que existam alguns; o número serve de referência para a tarefa 14.
5. Gerar também a tabela de tamanho por classe de cada fold da validação cruzada estratificada de 10 folds sobre o treino (seed 42). A especificação pede contagens de treino, validação e teste; como a validação é cruzada, a resposta é o tamanho por fold.
6. Medir, por classe, a fração das linhas do teste cujo vetor de 29 atributos também existe no treino, e gravar em `split_counts.json`. Índices disjuntos não impedem que linhas idênticas caiam nos dois lados; se a limpeza adotada na tarefa 04 não remover duplicatas, esse número diz quanto do teste é repetição do treino. A trilha fiel não muda por causa dele; a corrigida reporta as métricas também sem essas linhas (tarefa 11).
7. Testes com dados sintéticos: índices de treino e teste disjuntos e cobrindo tudo; proporção por classe preservada; mesmo resultado com a mesma seed e resultado diferente com outra; mínimo e máximo do scaler iguais aos do treino e diferentes dos do conjunto inteiro quando o teste tem um valor extremo.

## Por quê

Decisão 12 e risco R1. A especificação pede, na seção 6 do relatório, como os conjuntos foram formados e quantas amostras há por classe em cada um. O artigo não diz que o split é estratificado, mas as somas da Fig. 4 mostram que é; reproduzir essas contagens confirma que partimos do mesmo ponto.

## Evidência — verificada no baseline

- `docs/04-dados.md:37-46` — split implícito por classe, deduzido da Fig. 4.
- `docs/02-artigo.md:71-77` — o que a Fig. 4a revela: split estratificado.
- `docs/02-artigo.md:17` — normalização ajustada no treino (seção III-C do artigo).
- `docs/03-auditoria-repositorio.md` — o script dos autores usa `stratify=y, test_size=0.1, random_state=42`.

## Risco

- As contagens só batem com a Fig. 4 se a limpeza da tarefa 04 reproduzir a Tabela I. Se não reproduzir, as contagens ficam proporcionais e a diferença é reportada.
- O artigo fala em treino, validação e teste. Não há conjunto de validação separado: a validação é a cruzada de 10 folds dentro do treino. O relatório precisa dizer isso com essas palavras.

## Critério de aceite

Conferido em 07/10/2026 no commit `0ae2d49`. O script de E0 não foi rodado nesta reconciliação: os itens de dados reais foram confirmados pelo arquivo versionado.

- [x] Testes dos invariantes I1 e I2 verdes. Executado: `test_train_and_test_indices_are_disjoint_and_cover_all_rows` e `test_scaler_is_fitted_on_train_only`, na suíte de 23 testes.
- [x] `results/e0/dados/cira/seed42/split_counts.json` traz treino e teste por classe, os valores da Fig. 4 e a diferença, o tamanho por classe de cada fold, e a fração do teste duplicada no treino. Lido no arquivo.
- [x] As contagens são idênticas às da Fig. 4 em Benign-DoH e Malicious-DoH e diferem em uma amostra de Non-DoH (teste com 115.911 contra 115.910), com a diferença registrada. Qualquer outra diferença para a tarefa e é investigada antes de seguir. Lido: `train.difference` é `[-1, 0, 0]` e `test.difference` é `[1, 0, 0]`; as asserções de `e0_dados.py:214-215` interrompem o script com qualquer outro valor.
- [x] Nenhuma função de `splits.py` recebe o teste para ajustar qualquer coisa (revisão). Lido: `fit_scaler` recebe só o treino; `seen_in_train` recebe o teste para comparar, sem ajustar nada. A revisão humana no pull request continua devida.

## Testes

Seção "Tarefa 05" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de dados: G1–G10, com G5 = `uv run python scripts/e0_dados.py`.
