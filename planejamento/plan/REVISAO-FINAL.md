# Revisão final em código — resultado

Saída da tarefa [25](25-revisao-final-em-codigo.md). Executada em 08/10/2026 pelo agente `revisor-metodologico`, sobre o commit `3da178e`. Nenhum modelo foi treinado com dados reais e nada foi escrito no repositório durante a revisão. Os scripts de recomputação são independentes do pacote `doh_ids` (numpy e scipy).

**Resumo:** nenhum achado bloqueante. Cinco achados importantes e nove menores. Os números gravados estão certos e coerentes de ponta a ponta; os achados são três frases inexatas no relatório, três afirmações fortes demais no README, oito pontos de vazamento protegidos só por leitura de código, e dois arquivos de métricas que o código atual regenera com chaves a mais.

A situação de cada achado (corrigido, registrado ou aberto) está na seção "Tratamento", no fim.

## Veredito por verificação

| # | Verificação | Veredito | Evidência |
| --- | --- | --- | --- |
| V1 | Rastro de cada resultado até o código | Achado I5; fecha pela execução limpa | 229 `metrics.json` com `run.json` ao lado, `dirty: false`, trilha igual ao caminho; 12 commits, todos ancestrais da referência; hash dos quatro Parquets igual ao gravado |
| V2 | Recomputação em cadeia | OK nos números; achados de texto I1, I2, M1, M2 | 362 matrizes e 11.266 métricas recalculadas, 0 divergências; 2.377 conferências de totais, 0; 2.811 valores dos três agregados, 0; 60 tabelas, 26 figuras e o índice regenerados idênticos; 115 afirmações numéricas do relatório, 112 conferem |
| V3 | Invariantes de vazamento | Achado I4 | por leitura, os oito invariantes estão garantidos; por mutação, 23 aplicadas, 15 pegas por teste, 8 sobrevivem |
| V4 | Fidelidade ao artigo | OK, com M5 | hiperparâmetros e passos conferidos contra o manuscrito; nenhuma correção de protocolo na trilha fiel |
| V5 | Sorteios e determinismo | OK | 13 fontes de sorteio, todas com seed vinda de `config.py`; nenhum valor não determinístico nos 229 `metrics.json` |
| V6 | Coerência entre experimentos | OK | 432 conferências, 0 divergências: mesmo split por seed entre E4, E8 e robustez; mesmo modelo, mesma matriz em experimentos diferentes |
| V7 | Testes | Achados I4, M6, M7 | 113 testes verdes; nenhum `skip`, `xfail` ou teste sem asserção; nenhum lê dados reais |
| V8 | Texto contra a lista do que se pode afirmar | Achados I1, I2, I3, M1 a M4 | os nove itens "pode afirmar" conferem com os dados; nenhuma frase proibida aparece como afirmação no relatório nem nos slides |
| V9 | Higiene do repositório | OK, com M9 | os comandos do CI verdes em clone limpo; nenhum arquivo proibido; nenhum commit com coautoria; `LICENSE` presente |

## Achados importantes

**I1. Relatório: "não prediz Benign-DoH nas dez seeds" é falso em 8 delas.** `project/report/relatorio.tex`, parágrafo da reprodução com profundidade 5. O recall de Benign-DoH é 0 nas dez seeds, mas em 8 delas o modelo chega a predizer a classe, sempre errado (147 fluxos no total). A conclusão não muda; a frase sim. Não exige treino.

**I2. Mesma inexatidão no retreino do segundo conjunto.** "continua sem predizer Benign-DoH": a matriz tem 13 fluxos preditos como Benign-DoH, nenhum certo. Redação certa: "continua com recall 0 em Benign-DoH". Não exige treino.

**I3. README da raiz afirma mais do que os resultados sustentam.** "medimos tudo em dez seeds" (só E4 e E8 têm dez seeds); "mostramos que o detector aprende um artefato da captura" (o relatório diz "é compatível com"); título "O que explica a queda" (causa não medida). Não exige treino.

**I4. Oito mutações de vazamento ou de sorteio não derrubam nenhum teste.** O ponto em que o scaler e o SMOTE do treino inteiro são ajustados dentro dos scripts de E1, E2 e E4, o fold de fora da validação cruzada, a normalização na seleção de hiperparâmetros, a seed da subamostra da seleção e a gravação do combinado sem réplicas estão protegidos só por leitura. Evidência, por outro caminho, de que os resultados gravados não têm esse vazamento: `fit_rows` de B, C e B-prof5 é 3 × 800.828 nas 30 execuções (com o teste junto seria 889.809); E2 tem asserção do balanceamento; o retreino afirma zero fluxos do HKD repetidos; no Parquet sem réplicas há 0 duplicatas do HKD; o hash do split recalculado do Parquet é o gravado. Correção sem treino: asserções nos scripts e testes novos.

**I5. Dois `metrics.json` não são regenerados idênticos pelo código atual.** `project/results/e6/{fiel,variante}/retreino_sem_replicas-shap/seed42/metrics.json` foram gerados antes de a análise do limiar de `Duration` ganhar quatro chaves. As chaves comuns não mudam. Correção: versionar os dois arquivos que a execução limpa gerar, depois de conferir as chaves antigas.

## Achados menores

- **M1.** "2,3 vezes o tempo de treino (265,1 contra 117,8 s)" no combinado: a razão é 2,25. No CIRA, 2,3 está certo.
- **M2.** Resumo do relatório: "0,5 ponto percentual nos dois conjuntos"; é 0,50 e 0,57.
- **M3.** "regra fixada antes da execução": vale para a modificação e a robustez; no protocolo corrigido a regra com o desvio das diferenças pareadas entrou depois, sem mudar nenhum veredito.
- **M4.** "o recall de 100% mede memorização": o experimento não separa cópia no teste de peso maior no treino; usar "não mede a detecção de fluxo novo".
- **M5.** Três leituras adotadas não aparecem no relatório: parâmetros padrão da regressão logística; alvo do SMOTE dos modelos de comparação; ausência de peso de classe na trilha fiel.
- **M6.** `tests/test_report_assets.py` copia a pasta `results/` versionada, e não uma árvore sintética. Roda no CI porque `results/` é versionado; quebra se o formato mudar.
- **M7.** O resumo do plano de testes não lista `tests/test_comparar_resultados.py`.
- **M8.** A tabela de pendentes das decisões ainda dizia que não havia `LICENSE`.
- **M9.** Três commits iniciais fora do formato e cinco com assunto de 73 ou 74 caracteres. Histórico publicado não se reescreve.

## Mutações

| Invariante | Mutação | Teste que pegou |
| --- | --- | --- |
| Teste antes do ajuste | scaler reajustado na tabela inteira em E1 | **nenhum** |
| Teste antes do ajuste | scaler do SMOTE compartilhado ajustado em treino e teste em E4 | **nenhum** |
| Teste antes do ajuste | `fit_scaler(table)` em E2 | **nenhum** |
| Scaler só no treino | `fit_scaler` ajusta em dados alterados | `test_scaler_is_fitted_on_train_only` |
| Scaler dentro do fold | treino normalizado antes do laço de folds | `test_cross_validation_scaler_never_sees_the_held_out_fold` |
| Scaler dentro do fold | fold de fora transformado com scaler do treino inteiro | **nenhum** |
| Scaler dentro do fold, seleção | subamostra normalizada antes dos folds | **nenhum** |
| SMOTE só no treino | SMOTE antes do split em E1 | teste de ponta a ponta de E1 |
| SMOTE só no treino | SMOTE antes do split em E4 | `test_every_model_of_a_seed_gets_the_same_train_and_test_rows` |
| Sintético só na classe prevista | SMOTE em todas as classes menores nos subconjuntos | `test_malicious_rows_are_the_same_real_rows_in_every_subset` |
| SMOTE só no treino | `balanced_train` de E4 recebe treino e teste | **nenhum** |
| Matriz por nome | "tudo menos o rótulo" | `test_load_returns_features_and_integer_label_without_identifiers` |
| Identificadores fora | porta de origem entre os atributos | `test_feature_and_id_columns_are_29_and_5_without_repetition_or_overlap` |
| Seleção só com o treino | seleção com treino e teste | `test_hyperparameter_selection_only_receives_train_rows_of_the_seed` |
| Seleção, seed | subamostra sem seed | **nenhum** |
| Transferência | scaler reajustado com o HKD (antes e depois das asserções) | `test_transfer_scales_the_second_dataset_with_the_scaler_of_the_first_train` |
| Perturbação só no teste | treino fragmentado | `test_robustness_seed_fits_the_scaler_on_train_and_perturbs_only_test_malicious` |
| Perturbação só nos maliciosos | todas as classes fragmentadas | `test_fragmentation_changes_only_malicious_flows_of_the_test` |
| Scaler do treino na robustez | scaler na tabela inteira; scaler com o teste perturbado | o mesmo teste da robustez |
| Combinado sem réplicas | a função devolve tudo | `test_without_replicas_keeps_one_row_per_hkd_flow_and_all_cira_rows` |
| Combinado sem réplicas | o script grava sem chamar a função | **nenhum** (só a asserção do retreino, com dados reais) |

## O que a revisão não verificou, e por quê

1. Fechamento de V1: depende da execução limpa.
2. `RESUMO.md` escritos por scripts de treino (E0, E1, E2, E5, etapa de dados de E6): não se regeneram sem treinar. Todo número deles citado no relatório foi recalculado dos `metrics.json` ou dos Parquets.
3. Valores SHAP (ranking, Spearman, corte de 33,13 s): conferidos só contra os `metrics.json`; recalcular exige ajustar o modelo.
4. AUC-ROC e AUC-PR: dependem das probabilidades, que não são gravadas; conferidas só na agregação e na coerência entre experimentos.
5. Suíte em menos de um minuto: a máquina estava carregada (220 s); com a máquina livre o registro é de cerca de 40 s.
6. Tabela II e Figs. 5, 7 e 8 contra o manuscrito: conferidas no mesmo dia, em passagem separada, sem divergência (decisão 55).
7. Apresentação no Google Slides, DOI das referências e forma das curvas da Fig. 2: de pessoa.

## Tratamento

Preenchido depois da revisão, à medida que cada achado é tratado.

| Achado | Situação |
| --- | --- |
| I1, I2 | **Corrigido** em `3725f27`: as duas frases do relatório dizem "recall 0" e a primeira traz os 147 fluxos preditos e errados em 8 seeds; PDF recompilado, 8 páginas |
| I3 | **Corrigido** em `3e42795`: README da raiz diz "medimos a variância em dez seeds", "resultado compatível com" e "um indício do porquê" |
| I4 | **Corrigido** em `2686b80`, `7200be7`, `bf19a11`, `2be47e9`, `80111aa`: asserções nos scripts de E1, E2, E4 e E6 e cinco testes novos; as oito mutações agora derrubam um teste (provado aplicando cada uma). Suíte com 118 testes. As asserções novas só rodaram com dados sintéticos; a lógica numérica não mudou |
| I5 | **Corrigido** em `97b2c8c`: os dois `metrics.json` de SHAP do segundo conjunto foram trocados pelos da execução limpa, depois de conferir que as 521 chaves comuns saíram iguais |
| M1 a M5 | **Corrigido** em `3725f27` e `c74fc3f`: 2,2 vezes no combinado; "cerca de meio ponto"; regra "fixada antes da execução da modificação e da robustez, e aplicada do mesmo modo ao protocolo corrigido"; "não mede a detecção de fluxo novo"; as três leituras que faltavam entraram no parágrafo de leituras adotadas |
| M6 | **Registrado** em `2622ea3`: comentário no teste explica por que a fixture copia a pasta `results/` versionada |
| M7, M8 | **Corrigido** na reconciliação final do plano e de `docs/` |
| M9 | registrado; histórico publicado não se reescreve |
| V1 | **Fechado pela execução limpa** (ver abaixo) |

## Execução limpa (tarefa 19)

Rodada em 08/10/2026, de 04:54 a 12:24 (7 h 30 min), em um clone novo fora do repositório, no commit `e2379b7`, com os dados extraídos do zip da equipe e a árvore limpa: os 22 passos de `scripts/execucao_limpa.sh`, sem erro. Os 229 `run.json` regenerados registram `dirty: false`.

Comparação com `scripts/comparar_resultados.py` contra o repositório:

- `results/`: 260 arquivos comparados (229 `metrics.json`, `split_counts.json`, 3 agregados e 27 CSV). 256 saíram idênticos na primeira comparação. Os quatro restantes:
  - dois `metrics.json` de SHAP do segundo conjunto, com 21 chaves novas e as 521 chaves comuns iguais (achado I5, corrigido);
  - os dois agregados de E8, diferentes só no campo `commits`, que registra o commit de cada execução, e nas entradas de tempo. O script passou a ignorar `commits` (`47cdabe`).
- `report/`: 56 arquivos (27 tabelas em `.tex` e `.csv`, o índice e o `relatorio.tex`), todos idênticos.
- Depois das duas correções, a comparação dá 260 de 260 e 56 de 56, com código de saída 0.

Com isso, todo número versionado foi regenerado do zero pelo código da `main` daquele commit. Os commits posteriores só acrescentaram asserções, testes e texto.
