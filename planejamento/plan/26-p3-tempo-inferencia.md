# 26 · P3 · tempo de inferência do sistema do artigo e da modificação (E8)

**Onde:** `src/doh_ids/config.py` (constantes `INFERENCE_*`), `scripts/e8_inferencia.py`, `scripts/e8_inferencia_resumo.py`, `results/e8/corrigida/inferencia-<dados>/`
**Objetivo:** medir quanto custa, na predição, a modificação da equipe (100 árvores sem limite de profundidade) diante do sistema do artigo, e conferir a justificativa que o artigo dá para a profundidade 5 ("to keep the computation fast enough during the prediction stage", Seção IV-B), que ele não mede.
**Depende de:** 11 (execuções gravadas de A e A-prof5, com o hash do split), 13 (Parquet do combinado sem réplicas), 15 (execuções gravadas de M1, M1M2 e A no combinado, com os hiperparâmetros selecionados por seed)
**Demonstra:** `results/e8/corrigida/summary-inferencia.json` e `RESUMO-INFERENCIA.md`, com a hipótese anterior em `HIPOTESE-INFERENCIA.md`: nós de árvore percorridos por fluxo (determinístico) e tempo de normalizar e predizer, em lote e fluxo a fluxo, com um núcleo, dez seeds, nos dois datasets. Extra de P3 (seções 5 e 7); **não está no relatório nem nos slides**.

> **Tarefa acrescentada depois do fechamento do plano**, a pedido do usuário, em 10/11/2026. Não estava nas 25 tarefas nem na ordem de execução. Foi implementada e executada na branch `tarefa/26-tempo-inferencia`, criada da `main` em `9885358`; o registro abaixo foi escrito depois da implementação, a partir do código e de `results/`.

## Como ficou (conferido no código e em `results/` em `f1bdc37`, 10/11/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Executado em `f1bdc37`, dentro de `project/`: `uv run ruff check .` (sem erro), `uv run ruff format --check .` (78 arquivos formatados), `uv run pytest` (118 verdes em 44 s; nenhum teste novo), `python3 scripts/metricas_fig4.py` (código 0) e os dois greps do G7 (nenhuma linha). Nenhum treino nem medição foi rodado de novo.

- **Situação: pronta e executada**, na branch `tarefa/26-tempo-inferencia`; **não está na `main`** e **não passou pela execução limpa** de 08/10/2026, que é anterior a ela. Hipótese e constantes em `527efde`; scripts de medição e de resumo, com os passos no `execucao_limpa.sh` e as chaves novas no `comparar_resultados.py`, em `4e5b1df`; resultados das dez seeds em `51b8683`; resumo em `9ae169c`; README e `docs/05-plano-experimental.md` em `1c57621`; achados da revisão metodológica tratados em `9c4f4df` (código) e `f1bdc37` (resumo regenerado).
- **Execução com dados reais:** 10/11/2026, commit `4e5b1df`, `dirty: false` nos 20 `run.json`, máquina `MacBook-Air-de-Breno-2.local`, 10 núcleos (executado: leitura dos 20 `run.json` por script). Tempo de relógio informado pela sessão e no README: 2 h 27 min; os `timestamp` dos `run.json` vão de 15:31:05 a 17:50:56 (lido). A soma de `fit_seconds` dos 20 `run.json` é 6.462,5 s (executado).
- **Arquivos:** `src/doh_ids/config.py` (`INFERENCE_MODELS`, `INFERENCE_COMPARISONS`, `INFERENCE_BATCH_REPEATS`, `INFERENCE_SINGLE_FLOWS`, `INFERENCE_SINGLE_WARMUP`, `INFERENCE_NODE_RATIO_BAND`); `scripts/e8_inferencia.py` (funções `reference_metrics`, `fit_model`, `forests_of`, `tree_cost`, `rotated`, `time_batch`, `time_single`, `measure`, `run_seed`, `run_dataset`); `scripts/e8_inferencia_resumo.py` (não treina; `summary_content(e8_dir, seeds)` recebe o diretório de leitura). A medição grava por `run_dataset(..., results_dir, seeds)`, que recebe o diretório de saída (regra 6); `scripts/comparar_resultados.py` (`batch_seconds`, `single_seconds`, `single_p95_seconds` em `TIME_KEYS`; `summary-inferencia.json` em `TIME_AGGREGATES`); `scripts/execucao_limpa.sh` e `README.md` (passos 19a e 19b).
- **Comando real:** `uv run python -m scripts.e8_inferencia` e, depois, `uv run python -m scripts.e8_inferencia_resumo`. A medição importa `scripts.e4_corrigido`, `scripts.e6_dataset2` e `scripts.e8_modificacao`; lê `data/processed/cira.parquet`, `data/processed/combinado_sem_replicas.parquet`, `results/e4/corrigida/{A,A-prof5}/` e `results/e8/corrigida/{M1-cira,M1M2-cira,A-combinado_sem_replicas,M1M2-combinado_sem_replicas}/`. Pula a seed já gravada pelo mesmo commit com a árvore limpa (`e8.already_run`).
- **Resultados:** `results/e8/corrigida/inferencia-cira/seed<0..9>/` (A, A-prof5, M1, M1M2) e `inferencia-combinado_sem_replicas/seed<0..9>/` (A, M1M2), com `metrics.json` e `run.json`; `summary-inferencia.json`, `RESUMO-INFERENCIA.md` e `HIPOTESE-INFERENCIA.md` no nível da trilha. Os números estão no `RESUMO-INFERENCIA.md` e no agregado; este registro não os repete.
- **Onde ficam os tempos:** só no `run.json` (`timings`: `batch_seconds`, `single_median_seconds`, `single_p95_seconds`, `fit_seconds`) e no agregado, em chaves com `seconds` no nome. O `metrics.json` tem matriz de confusão, `trees`, `nodes`, `nodes_per_flow`, contagens do teste, hash do split e a amostra de fluxo a fluxo por classe.
- **Mudança de código depois da execução (`9c4f4df`), classificada:** `SINGLE_WARMUP = 10` saiu do script para `config.INFERENCE_SINGLE_WARMUP`, com o mesmo valor; `INFERENCE_NODE_RATIO_BAND` entrou em `config.py` com a faixa que a hipótese já fixava (metade ao dobro); um comentário de `tree_cost` foi reescrito; e entrou a asserção de `n_jobs == 1`. Nada disso toca a lógica numérica da medição (lido: `git diff 4e5b1df..9c4f4df`). Consequência: os `run.json` trazem `4e5b1df`, e relançar o script no commit atual refaz as 20 execuções.
- **A asserção de `n_jobs == 1` não rodou com os dados reais.** Ela foi acrescentada em `9c4f4df`, depois da execução. Na execução gravada, a predição com um núcleo vinha da construção dos modelos: `base_forests` faz `set_params(n_jobs=1)` depois do ajuste (`src/doh_ids/models.py:60`) e `fit_modified_forest` faz o mesmo na floresta do `Pipeline` (`:172`); `models.py` não mudou no delta (lido). As demais asserções existiam em `4e5b1df` (lido: `git show 4e5b1df:project/scripts/e8_inferencia.py`).
- **`summary-inferencia.json` traz tempos e pares de tempo:** não repete entre execuções. A comparação da execução limpa o lê sem as chaves de tempo e sem os pares cuja `metric` é de tempo (`is_time_entry`).
- **Concluída como pronta e executada (10/11/2026).** Integração na `main` pendente: decisão da equipe.

## Arquivos

- `src/doh_ids/config.py` — acrescida: as constantes `INFERENCE_*`, fixadas antes da execução (as quatro primeiras no commit da hipótese).
- `scripts/e8_inferencia.py` — novo: ajusta de novo cada modelo nas mesmas seeds e splits, mede e grava.
- `scripts/e8_inferencia_resumo.py` — novo: agrega, compara por par e escreve o resumo, sem treinar.
- `scripts/comparar_resultados.py`, `scripts/execucao_limpa.sh`, `README.md` — acrescidos.
- `results/e8/corrigida/inferencia-<dados>/seed<k>/`, `summary-inferencia.json`, `RESUMO-INFERENCIA.md`, `HIPOTESE-INFERENCIA.md` — gerados (a hipótese, escrita à mão antes).
- Nenhum arquivo em `tests/` (ver "Testes").

## O que foi feito

1. Hipótese escrita antes da execução, com modelos, pares, regimes, regra de leitura, o que seria inesperado e as limitações (`HIPOTESE-INFERENCIA.md`, `527efde`).
2. Para cada seed de 0 a 9 e cada conjunto, o split é refeito com a seed e conferido contra o hash gravado na execução de referência; cada modelo de `INFERENCE_MODELS` é ajustado só com o treino; M1M2 usa os hiperparâmetros que a seleção gravada escolheu na mesma seed, sem nova seleção.
3. Medida determinística: nós de árvore percorridos por fluxo no teste, somados em todas as árvores dos Random Forests (`tree_cost`, por `decision_path`; o meta-classificador de A não entra).
4. Tempo de normalizar e predizer, com o coletor de lixo desligado durante a medida e a ordem dos modelos girada a cada repetição: em lote (teste inteiro, uma predição de aquecimento e `INFERENCE_BATCH_REPEATS` repetições) e fluxo a fluxo (`INFERENCE_SINGLE_FLOWS` fluxos sorteados com a seed, depois de `INFERENCE_SINGLE_WARMUP` predições de aquecimento).
5. Conferências por asserção, dentro do script: treino e teste disjuntos; hash do split igual ao da execução de referência; matriz de confusão no teste igual à gravada; rótulo de cada fluxo predito sozinho igual ao do lote; e, desde `9c4f4df`, `n_jobs == 1` em todas as florestas.
6. Resumo: média e desvio entre seeds; por par de `INFERENCE_COMPARISONS` e por métrica, a comparação pareada de `paired_comparison` e o veredito de `paired_verdict`, com a razão média ao lado; a hipótese ao lado do resultado; leitura posterior e fluxos por segundo marcados como "posterior".

## Por quê

O artigo justifica a profundidade 5 pela velocidade de predição (Seção IV-B) e afirma uma redução de três vezes no tempo de treino que não mede (decisão 22). A modificação de P3 (tarefa 15) troca o empilhado por um Random Forest único de 100 árvores sem limite de profundidade, o oposto do que o artigo justifica pela predição. Sem medir, o relatório não pode dizer quanto a modificação custa na predição nem se a justificativa do artigo se sustenta. A medida de nós por fluxo existe porque o tempo absoluto não se transfere entre máquinas; as razões pareadas e os nós por fluxo, sim.

## Evidência — verificada em `f1bdc37`

- `results/e8/corrigida/HIPOTESE-INFERENCIA.md`, seção "O que o experimento testa": a frase da Seção IV-B citada e a ausência de tempo de inferência no artigo.
- `docs/05-plano-experimental.md`, linha "E8, inferência" (`1c57621`).
- Decisão 22 (tempo de treino medido, sem comparação com a redução de três vezes); decisão 38 (layout `results/<experimento>/<trilha>/<recorte>/seed<k>/`, que o recorte `inferencia-<dados>` segue); decisões 52 e 54 (A, A-prof5, M1 e M1M2).

## Risco

- Citar tempo absoluto ou p95 como propriedade do modelo. A variação entre seeds vem do estado da máquina; o resumo o mede e diz que só as razões pareadas e os nós por fluxo se citam (`RESUMO-INFERENCIA.md`, "Leitura posterior" e "Limitações").
- Ler os fluxos por segundo como capacidade de um detector. Ficam de fora a extração de atributos, a espera pelo fim do fluxo e o uso de mais threads; o resumo diz isso na própria seção.
- Ordem hipótese → execução: um teste de funcionamento em amostra de 40 mil fluxos rodou antes do commit da hipótese e exibiu tempos de A, A-prof5 e M1. O resumo declara que as expectativas 2 e 3 sobre esses três modelos devem ser citadas como registradas depois desse teste; as sobre M1M2 não são afetadas.
- Veredito no limite: A-prof5 contra A, fluxo a fluxo, passa a regra por 0,4%; o resumo o registra como leitura posterior, sem mudar o veredito.

## Critério de aceite

- [x] Hipótese, modelos e pares fixados antes da primeira execução. Lido: `527efde` (15:22:10) traz `HIPOTESE-INFERENCIA.md` e as quatro primeiras constantes `INFERENCE_*`; os 20 `run.json` trazem `4e5b1df` (15:23:28), posterior. O teste de funcionamento anterior está declarado em `RESUMO-INFERENCIA.md`, "Limitações".
- [x] Medição e resumo em scripts separados (regra 1 de `.claude/rules/experimentos.md`). Lido: docstrings dos dois scripts; o de resumo importa de `scripts.e8_inferencia` só `EXPERIMENT`, `TRACK` e `SLICE_NAME`, não chama função de ajuste e lê `metrics.json` e `run.json`.
- [x] Nenhum tempo em `metrics.json` (regra 2). Executado: varredura das chaves dos 20 `metrics.json` por `second`, `time`, `ms` e `_us`, sem ocorrência; os tempos estão em `run.json`, chave `timings`.
- [x] Dez seeds, nos dois conjuntos, com os modelos de `INFERENCE_MODELS`. Executado: 20 `run.json` (`inferencia-cira` e `inferencia-combinado_sem_replicas`, `seed0` a `seed9`); `summary-inferencia.json`, chave `seeds` de 0 a 9; quatro modelos no CIRA e dois no combinado.
- [x] Cada modelo medido é o mesmo da execução já avaliada. Lido: asserções de hash do split (`scripts/e8_inferencia.py:213`) e de matriz de confusão (`:222`), presentes em `4e5b1df`; `save_run` só é chamado depois de `run_seed`, que as executa, de modo que cada um dos 20 `run.json` gravados prova que elas passaram naquela seed.
- [x] Predição de um fluxo igual à predição em lote. Lido: asserção em `scripts/e8_inferencia.py:190`, presente em `4e5b1df`; mesmo argumento do item anterior.
- [x] Predição com um núcleo em todas as florestas. Lido: na execução gravada, por construção (`src/doh_ids/models.py:60` e `:172`); a asserção que o confere (`scripts/e8_inferencia.py:169`) entrou em `9c4f4df`, depois da execução, e **não rodou com os dados reais**.
- [x] `run.json` com o commit e `dirty: false`. Executado: os 20 trazem `4e5b1df` e `dirty: false`.
- [x] Resumo com a hipótese ao lado do resultado e o acrescentado depois marcado como posterior (regra 3). Lido: `RESUMO-INFERENCIA.md`, seções "Hipótese ao lado do resultado", "Leitura posterior" e "Fluxos por segundo nesta máquina (posterior)".
- [x] A comparação da execução limpa ignora os tempos do agregado novo e acusa mudança na medida determinística. Executado: `scripts/comparar_resultados.py` sobre cópias de `summary-inferencia.json` no diretório temporário da sessão; com os tempos dobrados e os vereditos dos pares de tempo trocados, código 0; com `nodes_per_flow` de A alterado, código 1, nomeando `datasets.cira.models.A.nodes_per_flow.mean`.
- [x] O relatório gerado não muda. Executado: `make_assets` com saída em diretório temporário; `report/tables/` e `report/INDICE.md` idênticos aos versionados (`diff -rq`).
- [x] README e `execucao_limpa.sh` com os passos novos. Lido: passos 19a e 19b nos dois, com o tempo de relógio e a observação sobre os três agregados de E8. Resta uma frase desatualizada: `README.md:111` ainda diz "Os 22 passos abaixo", e a tabela tem 24 linhas de passo; levado ao usuário.
- [x] Revisão metodológica sem achado bloqueante. Informado pela sessão principal; achados tratados em `9c4f4df` e `f1bdc37` (mensagens de commit lidas). Não há arquivo de revisão versionado para conferir.
- [ ] Determinismo (G6): uma segunda execução gravada fora de `results/` com os mesmos `metrics.json`. **Não feita.** O que existe: a asserção de matriz de confusão mostra que os modelos são os das execuções gravadas, que a execução limpa de 08/10/2026 já regenerou iguais; `nodes_per_flow` depende só do modelo e do teste; a amostra de fluxo a fluxo vem de gerador com a seed. Isso torna provável, e não comprova, que os `metrics.json` repetem. Custo de comprovar: cerca de 2 h 30 min.

## Execução com dados reais: na sessão de implementação (decisão 44)

O script rodou na própria sessão, nesta máquina, em 10/11/2026, com a árvore limpa e o código já commitado (`4e5b1df`). **Não se aplica:** o Apuana (decisão 44); a saída colada no pull request (não houve pull request). A evidência é a versionada: os 20 `run.json` com a máquina, os núcleos, as versões, o hash dos dados, o commit e `dirty: false`.

## Testes

Seção "Tarefa 26" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md). Nenhum teste N1 novo: as conferências que protegem o resultado estão dentro do script, como asserções que dependem dos dados reais. Fica em aberto, para a equipe, se `tree_cost` merece um teste com dados sintéticos.

## Verificação ao concluir

Gate de experimento: G1–G10, com G5 = `uv run python -m scripts.e8_inferencia` e, depois, `uv run python -m scripts.e8_inferencia_resumo`. Situação em `f1bdc37`: G2, G3, G4 e G7 executados, verdes; G1 não executado; G5 lido nos `run.json`; **G6 não feito** (critério acima); G8 neste registro; G9 informado pela sessão principal; G10 não se aplica (decisão 55f), e a integração na `main` é da equipe.
