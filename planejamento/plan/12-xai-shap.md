# 12 · explicabilidade · SHAP sobre os modelos base e painel interativo (E5)

**Onde:** `src/doh_ids/explain.py`, `scripts/e5_xai.py`, script do painel, `pyproject.toml`, `tests/test_explain.py`, `results/e5/variante/profundidade_variavel/seed42/` e, ao lado, `results/e5/fiel/proposto/seed42/`
**Objetivo:** as figuras de explicabilidade do artigo reproduzidas com o nosso modelo, e a resposta a duas perguntas: o ranking de atributos se repete, e o limiar de 40 segundos em `Duration` aparece?
**Depende de:** 08
**Demonstra:** `results/e5/variante/profundidade_variavel/seed42/`: figuras equivalentes a todas as figuras SHAP do artigo (Figs. 5, 6a, 6b, 7 e 8) e tabela de importância; o painel `explainerdashboard` no ar, localmente, como material de demonstração. P1: a parte explicável do artigo (seção 7).

## Como ficou (conferido no código e em `results/` em `759ec29`, 08/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Suíte inteira executada em `759ec29`: 110 testes verdes em 41 s; `ruff check` e `ruff format --check` sem erro.

- **Situação: pronta e executada.** Dependência em `e827c0a`; `explain.py` em `f5cdf50`; script em `de54fe7`; painel em `b4f1256` e `6b8abeb`; resultados em `26b2ed6`; `a7b94a3` separou o cálculo da gravação (a 14b reutiliza `explain_system`); `e9836b3` e `a0d853a` trocaram o veredito do limiar de 40 s por dois fatos medidos; `e4544af` acrescentou o teste da amostra; resultados refeitos em `38809c1`. Os `run.json` trazem o commit `ff039fa` e `dirty: false` (lido).
- **Arquivos:** `src/doh_ids/explain.py` (`stratified_sample`, `forest_shap_values`, `global_importance`, `original_units`, `rank_agreement`), `scripts/e5_xai.py`, `scripts/painel_xai.py`, `tests/test_explain.py`, `pyproject.toml`, `uv.lock`, `requirements.txt`.
- **Comando real:** `uv run python scripts/e5_xai.py`. Lê `cira.parquet`, `results/e0/`, `results/e1/` e **`results/e6/dados/hkd/seed42/metrics.json`**: roda depois de `e6_dados.py`, e para com mensagem se o arquivo faltar. Tempo medido: 516 s na profundidade variável (294 s do SHAP na amostra do treino e 97,5 s na do teste) e 43 s na profundidade 5; cerca de 9 minutos. Painel: `uv run python scripts/painel_xai.py`, em `http://127.0.0.1:8050`.
- **Resultados:** `results/e5/variante/profundidade_variavel/seed42/` e `results/e5/fiel/proposto/seed42/`, cada um com `fig5_importancia_<classe>.png`, `fig6a_dependencia_duration.png`, `fig6b_dependencia_flowbytessent.png`, `fig6_dependencia.csv`, `fig7_explicacao_malicious-doh.{png,csv}`, `fig8_explicacao_non-doh.{png,csv}`, `importancia.csv`, `metrics.json` e `run.json`; `RESUMO.md` em cada trilha e `results/e5/RESUMO.md` com as duas lado a lado. Os resumos são escritos pelo próprio script.
- **Desvios que ficaram:** amostra de 2.000 fluxos por classe (`SHAP_SAMPLE_PER_CLASS`), como na proposta; na amostra do teste, Benign-DoH tem 1.975 fluxos, que é a classe inteira. O painel explica o Random Forest base 1 com 333 fluxos por classe (`DASHBOARD_SAMPLE_PER_CLASS`). A Fig. 6b saiu como dependência de `FlowBytesSent`. O painel ganhou um teste N1, de que é montado na memória sem gravar arquivo, ao contrário do que o plano de testes previa.
- **Pendente de pessoa:** subir o painel e abrir a página (T12-7) na demonstração; a conferência visual das figuras (T12-6); a integração (G10).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos) divergirem, vale este bloco.**

- Dependência 08 pronta e executada (`798ecd3`).
- **Modelo explicado (decisão 45): os três Random Forests base da variante de profundidade variável**, `base_forests(subsets, SEED_FIEL, MAX_DEPTH_VARIABLE)`. A trilha fiel não prediz Benign-DoH e não sustenta a explicação; onde o custo permitir, as mesmas figuras são geradas também para os bases de profundidade 5, e o resumo põe os dois rankings lado a lado. Os bases de profundidade 5, isolados, predizem as três classes (recall de Benign-DoH de 85% a 86% no teste, `results/e1/fiel/`): o `TreeExplainer` explica o base, não o meta, e isso continua sendo a limitação do passo 8.
- **Caminhos, pelo mesmo padrão de E1:** `save_run(experiment="e5", track="variante", slice_name="profundidade_variavel", seed=SEED_FIEL, ...)` e, para a profundidade 5, `track="fiel", slice_name="proposto"`. Onde o texto abaixo diz `results/e5/fiel/proposto/seed42/` como destino principal, leia-se `results/e5/variante/profundidade_variavel/seed42/`; `RESUMO.md` em cada trilha.
- **Todas as figuras SHAP do artigo são alvo (decisão 46).** Conferido no manuscrito: Fig. 5 (summary plot, com a lista de atributos), Fig. 6a (dependence plot de `Duration`, sobre o teste), Fig. 6b (interação `FlowBytesSent` × `FlowBytesReceived`), Fig. 7 (explicação de um fluxo malicioso do teste) e Fig. 8 (de um fluxo Non-DoH do teste). As Figs. 7 e 8 do artigo são telas do painel: probabilidade predita por classe, tabela de contribuição de cada atributo e gráfico de contribuição em cascata. A figura estática equivalente traz esses três elementos, gerados pelo script, e é ela a evidência do relatório. A Fig. 9 é da tarefa 21.
- **Painel interativo (decisão 50): o passo 9 deixa de ser condicional.**
  - Dependência nova: `explainerdashboard==0.5.8` em `pyproject.toml`, com `uv.lock` e `requirements.txt` regenerados. É a única dependência nova do plano e está justificada pela decisão 50; esses três arquivos entram na lista desta tarefa.
  - Um script próprio (`[Decidir: nome; proposta: scripts/painel_xai.py]`) lê o Parquet, treina o sistema com a seed 42 na memória, constrói o explicador sobre um dos Random Forests base (`[Decidir: qual dos três; proposta: o do primeiro subconjunto]`) com a amostra do teste do passo 3 e sobe o painel em `localhost`. **Não grava nem lê modelo serializado:** nada de `.pkl`, `.joblib`, `dump`, `to_yaml` ou `from_config`. O painel não passa por `save_run` e não gera arquivo em `results/`.
  - O painel é material de demonstração; as figuras estáticas continuam sendo a evidência. O professor disse que não é necessário (Q6).
  - Não verificado: se `explainerdashboard` 0.5.8 resolve junto com as versões fixadas (pandas 3.0.6, numpy 2.3.5, scikit-learn 1.9.1, shap 0.52.0). `MEMORY/01-discovery-stack.md` registra que `ClassifierExplainer(RandomForest, X_df, y)` constrói na 0.5.8, sem dizer com quais versões das outras. Se `uv lock` não resolver ou o construtor falhar, o implementador para e relata; não troca versão de outra biblioteca por conta própria, porque isso mudaria os resultados já versionados.
  - O comando do painel entra no README pela tarefa 19.
- **Custo: não medido para o SHAP.** O ajuste do sistema é o da tarefa 08: 194 s na profundidade variável e 112 s na profundidade 5. O `TreeExplainer` percorre cada árvore, e árvores sem limite de profundidade são muito maiores que as de profundidade 5: cronometrar o cálculo em uma fração da amostra antes de lançar a amostra inteira, e registrar o tempo no `run.json`. O tamanho da amostra continua pendência da equipe.
- Execução com dados reais na própria sessão (decisão 44).

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- As colunas de assimetria e o valor sentinela estão em `config.py`: `SKEW_COLUMNS` e `SKEW_SENTINEL`. As contagens do bloco abaixo estão confirmadas em `results/e0/dados/cira/seed42/metrics.json`, chave `skew_sentinel`: 298.766 linhas com o valor em alguma coluna; nas duas colunas de `ResponseTimeTimeSkew...`, 290.123 / 3.547 / 804 por classe.
- As medianas de `Duration` do bloco abaixo estão confirmadas em `results/e0/dados/cira/seed42/estatisticas_descritivas.csv`, coluna `50%`: 0,31 s, 4,10 s e 34,07 s. É esse o arquivo "do que a tarefa 04 mostrar" citado em "Risco".
- Conversão de `Duration` para segundos (passo 6, T12-3): o scaler é o de `fit_scaler(train)`; `Duration` é a coluna de índice 0 de `FEATURE_COLUMNS`, e a matriz normalizada é um array sem nomes de coluna.
- Figuras e tabela são arquivos auxiliares no diretório que `save_run(experiment="e5", track="fiel", slice_name="proposto", seed=SEED_FIEL, ...)` devolve. O tamanho das amostras do SHAP entra no dicionário `config` e, se for resultado, em `metrics`.
- `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45; não altera resultado, só o tempo.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- As colunas de assimetria têm o valor `-10` em 298.766 linhas do conjunto limpo. É o valor sentinela do DoHLyzer para desvio padrão zero (confirmado nos métodos `get_skew` e `get_skew2` de `meter/features/packet_length.py` e `response_time.py` do extrator): 294.474 das ocorrências estão em `ResponseTimeTimeSkew...`, das quais 290.123 em Non-DoH e só 804 em Malicious-DoH. A análise de importância de qualquer `...SkewFromMedian` ou `...SkewFromMode` diz que parte do sinal é esse marcador de "fluxo com no máximo um tempo de resposta", e não a assimetria.
- A classe maliciosa vem de outras máquinas e de outro período. A importância de `Duration` é lida com essa ressalva: medianas de `Duration` no CIRA limpo de 34,1 s (malicioso), 4,1 s (benigno) e 0,3 s (Non-DoH), medidas em 07/10/2026 (`docs/08-inventario-dados.md`).

## Arquivos

- `src/doh_ids/explain.py` — novo.
- `scripts/e5_xai.py` — novo.
- `tests/test_explain.py` — novo (T12-1 a T12-4).
- Script do painel — novo (nome no bloco de reconciliação).
- `pyproject.toml`, `uv.lock`, `requirements.txt` — `explainerdashboard==0.5.8` (decisão 50).
- `results/e5/variante/profundidade_variavel/seed42/` — figuras e tabela de importância; `results/e5/fiel/proposto/seed42/`, ao lado, onde o custo permitir.
- `results/e5/variante/RESUMO.md` (e `results/e5/fiel/RESUMO.md`, se a trilha fiel for gerada) — comparação com o artigo e limitação do passo 8.

## O que fazer

1. Rodar a skill `experimento` para E5.
2. Treinar o modelo da tarefa 08 (seed 42) e aplicar `shap.TreeExplainer` a cada um dos três Random Forests base. Os valores vêm em um array de forma (amostras, 29 atributos, 3 classes); indexar a classe pelo último eixo.
3. Calcular os valores sobre duas amostras estratificadas, de tamanho declarado em `config.py` e registrado no resultado (`[Decidir: tamanho; proposta em "Pendentes da equipe"]`): uma do treino, porque a Fig. 5 do artigo diz que a importância global foi obtida "from the training data", e uma do teste, porque a Fig. 6 usa o teste.
4. Importância global (amostra do treino, como na Fig. 5): média do valor absoluto por atributo e por classe; ranking por submodelo.
5. Figuras equivalentes às do artigo: summary plot (Fig. 5), dependence plot de `Duration` para a classe maliciosa (Fig. 6a), interação `FlowBytesSent` × `FlowBytesReceived` (Fig. 6b), e explicação local de um fluxo malicioso e de um Non-DoH do teste (Figs. 7 e 8). Eixos rotulados, com unidade.
6. Comparar o ranking com o que o artigo afirma: duração no topo, depois comprimento de pacote e variância do tempo de pacote. Atenção: os valores estão normalizados em [0, 1]; para discutir o limiar de 40 segundos, converter o eixo de `Duration` de volta para segundos com o scaler.
7. Estabilidade: concordância do ranking entre os três submodelos (correlação de postos dos dez primeiros).
8. Escrever a limitação: isto explica os Random Forests base, não a decisão do empilhamento; o `TreeExplainer` rejeita o modelo empilhado.
9. Painel interativo (decisão 50): acrescentar `explainerdashboard==0.5.8` ao `pyproject.toml`, escrever o script que treina o modelo na memória e sobe o painel localmente sobre um dos Random Forests base, sem modelo serializado, e registrar o comando. Detalhe no bloco de reconciliação.

## Por quê

A explicabilidade é a contribuição que dá nome ao artigo; P1 não fecha sem ela. Decisão 19 e ambiguidade A15: o artigo não diz qual modelo foi explicado, e verificamos que não pode ter sido o empilhamento.

## Evidência — verificada no baseline

- `docs/02-artigo.md:101` — A15.
- `docs/05-plano-experimental.md:86-95` — escopo de E5.
- `planejamento/MEMORY/01-discovery-stack.md` — forma `(n, 29, 3)` de `shap_values`; `InvalidModelError` no modelo empilhado; `ClassifierExplainer` constrói na 0.5.8.
- Manuscrito em `docs/referencias/`, seção VI e legendas das Figs. 5 e 6 — o que o artigo afirma sobre importância e sobre o limiar.

## Risco

- Indexar `shap_values` como lista por classe, como em tutoriais antigos (risco R11): teste que confere a forma do array.
- `Duration` dominante pode ser artefato do testbed (tempo limite do extrator) e não do protocolo. Reportar como ressalva, com o que a tarefa 04 mostrar sobre a distribuição de duração por classe.
- Calcular SHAP sobre o teste inteiro é desnecessário e lento: usar amostra e declarar.

## Critério de aceite

- [x] Figuras equivalentes às Figs. 5, 6a, 6b, 7 e 8 em `results/e5/variante/profundidade_variavel/seed42/`, geradas pelo script; as mesmas em `results/e5/fiel/proposto/seed42/`, ou registro de que o custo não permitiu. Lido: os mesmos nove arquivos de figura e de dados nos dois diretórios. Não conferidas visualmente aqui.
- [x] Tabela de importância por atributo, classe e submodelo em arquivo. Lido: `importancia.csv` nos dois diretórios.
- [x] O dependence plot de `Duration` está em segundos. Lido: `results/e5/variante/RESUMO.md:94`; executado: `test_original_units_turns_normalized_duration_back_into_seconds`. A figura não foi aberta.
- [ ] Texto de comparação com o artigo: ranking e limiar, com o que confirmou e o que não confirmou. O texto existe (`fig5_comparison` e `duration_threshold` em `metrics.json`; seções do resumo); não relido frase a frase.
- [x] Medida de estabilidade entre submodelos registrada. Lido: `stability` e `stability_top_features` em `metrics.json`.
- [x] A limitação do passo 8 está escrita no `RESUMO.md` de cada trilha gerada. Lido: seção "Limitação" na linha 204 dos dois; `stacked_explainer_error` em `metrics.json`.
- [x] O resumo declara que o modelo explicado é o da leitura de profundidade variável e por quê. Lido: `results/e5/variante/RESUMO.md:11-14`.
- [ ] Painel: `explainerdashboard==0.5.8` no `pyproject.toml`, com `uv sync --locked` verde; o script sobe o painel localmente; nenhum arquivo de modelo é gravado nem lido (`git status` limpo depois de rodar e nenhum `.pkl` ou `.joblib` no disco). Lido: `pyproject.toml:17` e `requirements.txt:58`. Executado: `test_dashboard_is_built_in_memory_without_writing_any_file`. **Não executado aqui:** subir o painel e abrir a página.
- [ ] Revisor metodológico sem achado bloqueante. Informado pela sessão principal como feito, com os achados tratados; não há artefato da revisão para conferir aqui. Lido: commits de correção posteriores (`e9836b3`, `a0d853a`, `e4544af`, `38809c1`).

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script roda na própria sessão de implementação, nesta máquina, quando a tarefa chega ao ponto de executar (decisão 44); não se espera um integrante designado. O Apuana continua sendo opção (decisão 42). A evidência é a mesma: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e5.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). A execução é feita com a árvore limpa (o plano em commit antes de rodar, porque `dirty` mede o repositório inteiro) e o resultado entra em commit `exp`. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão.

## Testes

Seção "Tarefa 12" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e5_xai.py`. O script do painel não entra em G5 nem em G6: não grava resultado; é conferido pelo T12-7 do plano de testes.
