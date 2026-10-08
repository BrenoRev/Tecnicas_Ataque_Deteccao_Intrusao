# Plano de testes por tarefa

> **Onde fica o código (decisão 43):** o repositório Git é a raiz; o código fica em `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`) é relativo a `project/`, e os comandos `uv` rodam dentro dela. `.github/` e `.githooks/` ficam na raiz do repositório, porque o GitHub e o Git só os leem ali.

Diz, para cada tarefa, o que precisa estar verde antes de passar para a seguinte. As regras de escrita dos testes estão em `.claude/rules/testes.md`; o gate geral, em [VERIFICACAO.md](VERIFICACAO.md).

## Três níveis

| Nível | O que é | Onde roda | Quem confere |
| --- | --- | --- | --- |
| **N1 automático** | `pytest` com dados sintéticos | máquina de quem implementa e CI do GitHub | implementador; CI |
| **N2 local com dados reais** | o script da tarefa, com asserções embutidas, e a conferência do arquivo gerado em `results/` | a própria sessão de implementação, nesta máquina (decisão 44) | implementador; saída colada no pull request |
| **N3 revisão** | agente revisor e leitura de outro integrante | — | revisor; integrante |

O CI não tem os datasets: eles ficam fora do Git e o download do CIRA é manual. Por isso nenhum teste N1 lê `data/`, e tudo o que depende de contagem ou métrica real é N2.

O N2 das tarefas 03 a 16 e da 21 roda na própria sessão de implementação, sem esperar um integrante designado (decisão 44); o cluster Apuana continua opção (decisão 42). Nos dois casos a saída vai para o pull request e o `run.json` registra a máquina.

**Regra de passagem:** a tarefa só fecha com N1 verde no CI, N2 executado (quando a tarefa tem) e N3 sem achado bloqueante. A cada tarefa roda a suíte inteira.

## Base comum dos testes

Criada na tarefa 02 e reutilizada por todas as seguintes.

- `tests/conftest.py`, duas fixtures. `synthetic_flows`: DataFrame com as 29 colunas de atributo de `config.py` e `label` inteiro em {0, 1, 2}, já limpo, com 2.340 linhas (1.800 / 60 / 480). `synthetic_raw_csv`: as 35 colunas do CSV real (5 identificadores, 29 atributos e `Label` em texto), com a máquina local `192.168.20.x` ora em `SourceIP` ora em `DestinationIP`, `TimeStamp` no formato `2020-01-14 15:49:11` e NaN só em `ResponseTimeTimeMedian` e `ResponseTimeTimeSkewFromMedian`, gravada em `tmp_path` quando o teste precisa de arquivo. Três classes desbalanceadas na mesma ordem de grandeza relativa do CIRA (muito Non-DoH, pouco Benign-DoH, Malicious-DoH intermediário), poucas centenas a poucos milhares de linhas, médias deslocadas por classe para os modelos terem o que aprender, gerador `numpy` com seed fixa.
- Tamanhos escolhidos para a suíte inteira rodar em menos de um minuto.
- Nenhum teste exige desempenho mínimo de modelo.

## CI

Workflow único, criado na tarefa 01, em `push` na `main` e em todo pull request:

| Passo | Comando | Falha quando |
| --- | --- | --- |
| Ambiente | `uv sync --locked` | o lock não corresponde ao `pyproject.toml` |
| Lint | `uv run ruff check .` | qualquer erro |
| Formatação | `uv run ruff format --check .` | arquivo a reformatar |
| Testes | `uv run pytest` | teste vermelho ou nenhum teste coletado |
| Script sem dependência | `python3 scripts/metricas_fig4.py` | o script deixar de rodar só com a biblioteca padrão |
| Caminho absoluto | `grep -rnE` de `/Users/`, `/home/` e letra de unidade, com `--include="*.py"`, em `src scripts tests data` (comando exato na tarefa 01, passo 4b) | qualquer ocorrência |
| Referência interna | `grep -rnE` de `docs/`, `planejamento/`, `.claude/`, "decisão N", "tarefa N" e dos identificadores `A1` a `A18` e `Q1` a `Q11`, nos `.py`, `.md` e `.json` de `src scripts tests data README.md results` (comando exato na tarefa 01, passo 4b) | qualquer ocorrência: código, README e resultados não citam documento interno |
| Arquivo proibido | `git ls-files`, na raiz do repositório (`working-directory: .`), filtrado por `.pkl`, `.joblib`, `.pcap`, `.parquet`, `.zip`, `project/data/raw/`, `project/data/processed/`, PDF em `docs/referencias/` | qualquer ocorrência |

Como ficou no commit `5e11d56` (sem mudança até `360c3d3`: `.github/` não foi tocado desde então): o job roda com `working-directory: project`; cada uma das três checagens de higiene é um passo próprio; actions `actions/checkout@v7` e `astral-sh/setup-uv@v10.2.0`. O workflow ainda não rodou no GitHub (T01-5 aberto). Em `759ec29` nada mudou em `.github/`, e o T01-5 segue aberto: nenhuma branch foi enviada como pull request.

**Situação da suíte em `759ec29` (executado em 08/10/2026):** `uv run pytest`, 110 testes verdes em 41 s, 101 funções em doze arquivos; `ruff check` e `ruff format --check` sem erro; `python3 scripts/metricas_fig4.py` com código 0. Os testes que existem e não estavam previstos estão listados na seção de cada tarefa, com identificador novo.

---

## Tarefa 01 · repositório e ambiente

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T01-1 | N1 | `test_smoke.py`: o pacote `doh_ids` importa | Ambiente instalado; o `pytest` não termina com código 5 |
| T01-2 | N1 | Passo do CI: `python3 scripts/metricas_fig4.py` termina com código 0 | O script continua independente do pacote |
| T01-3 | N2 | Em um clone novo: `uv sync --locked`, lint, formatação e testes verdes | Ambiente reprodutível em outra máquina |
| T01-4 | N2 | Três commits de prova em repositório descartável: mensagem fora do padrão, trailer de coautoria e arquivo fora do lint são barrados pelos hooks | Os hooks funcionam |
| T01-5 | N2 | Primeiro pull request de prova: o CI roda e fica verde | O workflow funciona antes de ser necessário |

**Só avança se:** o CI ficou verde pelo menos uma vez e os hooks barraram os três casos.

## Tarefa 02 · configuração e registro de execução

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T02-1 | N1 | `config` tem 29 atributos e 5 identificadores, sem repetição e sem interseção | Base do invariante I4 |
| T02-2 | N1 | `save_run` cria `metrics.json` e `run.json` com trilha, seed, versões, hash dos dados, commit, nome da máquina e número de núcleos | I6 |
| T02-3 | N1 | Trilha fora de `fiel`, `corrigida`, `variante`, `dados` levanta erro | As trilhas não se misturam |
| T02-4 | N1 | Duas chamadas com as mesmas métricas geram `metrics.json` idêntico byte a byte; tempo e data só aparecem no `run.json` | Base do gate G6 |
| T02-5 | N1 | Fora de um repositório Git, o commit é gravado como nulo e a função não falha | Execução limpa em diretório sem Git |
| T02-6 | N1 | `git_state` devolve `dirty` falso com a árvore limpa, verdadeiro com um arquivo de código modificado, e ignora arquivo novo na pasta de resultados (escrito em `ac360ba`) | O `dirty: false` do G5 significa o que diz; gravar várias seeds não suja a execução seguinte |

**Só avança se:** as duas fixtures existem e usam os nomes de `config.py`.

## Tarefa 03 · aquisição do CIRA

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T03-1 | N1 | Com arquivos temporários e um manifesto: a conferência passa quando os hashes batem | `data/verify.py` funciona |
| T03-2 | N1 | A conferência falha, com mensagem que nomeia o arquivo, quando um arquivo é alterado e quando falta um obrigatório; opcional ausente só avisa | Erro de dado não passa calado |
| T03-3 | N2 | `uv run python data/verify.py` com os CSVs reais termina com código 0 | Os dados de quem roda são os registrados |
| T03-4 | N2 | `git status` não mostra nada de `data/raw/` | Dado fora do Git |

**Só avança se:** o cabeçalho real dos CSVs e a coluna de rótulo estão registrados em `data/README.md`. A tarefa 04 depende disso.

## Tarefa 04 · carga e limpeza (E0)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T04-1 | N1 | CSVs sintéticos com identificadores: a carga devolve as 29 colunas e `label` em {0, 1, 2}; a matriz de atributos não tem nenhuma coluna identificadora | I4 |
| T04-2 | N1 | A matriz de atributos é montada por nome: uma coluna extra desconhecida no CSV não entra | I4, contra "tudo menos o rótulo" |
| T04-3 | N1 | Linhas com NaN, com infinito e duplicadas são removidas conforme a regra pedida, e a contagem removida por classe é devolvida | A limpeza faz o que declara |
| T04-4 | N1 | A carga não remove duplicatas: duas linhas idênticas no mesmo arquivo continuam duas, e o total carregado é a soma dos três membros | A limpeza é só a dos NaN (decisão 34); uma deduplicação genérica apagaria as réplicas do combinado publicado |
| T04-5 | N2 | `scripts/e0_dados.py`: asserções de 29 colunas, sem NaN e sem infinito; total bruto 1.167.136; total limpo 889.809 / 19.746 / 249.553 | Dados reais íntegros; Tabela I reproduzida |
| T04-6 | N2 | `results/e0/dados/cira/seed42/` traz a tabela de combinações de limpeza ao lado de 889.809 / 19.746 / 249.553, com a diferença | Reconciliação com a Tabela I |
| T04-7 | N2 | Duas execuções geram Parquet com o mesmo hash | G6 |
| T04-8 | N1 | A carga lê os três membros configurados do zip e não lê `l1-doh.csv` (zip sintético com os quatro membros) | Sem DoH em dobro |
| T04-9 | N1 | No CIRA, `group` é o endereço local `192.168.20.x` que aparece na origem ou no destino, inclusive quando `SourceIP` é o resolvedor. (A segunda metade, sobre o segundo dataset, virou o T13-7.) | Grupo correto para a avaliação por máquina |

Como ficou (conferido em `360c3d3`): a carga é `load_cira`; não existe `load_dataset`. T04-1 a T04-4, T04-8 e T04-9 estão em `tests/test_data.py`, um teste por linha.

Complemento da decisão 46 (Fig. 2): sem teste N1 novo, porque a figura não entra em nenhum ajuste nem em nenhum número. N2: rodar `scripts/e0_dados.py` de novo e conferir que `metrics.json`, `split_counts.json` e `parquet_sha256` saem idênticos aos versionados e que a figura existe. N3: conferência visual, eixos e unidade.

**Só avança se:** a combinação de limpeza adotada está registrada com a diferença para a Tabela I, seja ela zero ou não.

## Tarefa 05 · split e normalização

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T05-1 | N1 | Índices de treino e teste disjuntos e cobrindo todas as linhas | I1 |
| T05-2 | N1 | Proporção por classe preservada nos dois conjuntos; teste com 10% | Split estratificado 90/10 |
| T05-3 | N1 | Mesma seed, mesmo split; seed diferente, split diferente | Reprodutibilidade |
| T05-4 | N1 | Com um valor extremo só no teste, o mínimo e o máximo do scaler são os do treino | I2 |
| T05-5 | N1 | A função que mede a fração do teste repetida no treino acha uma linha duplicada plantada | A medida de duplicatas é correta |
| T05-6 | N2 | `results/e0/dados/cira/seed42/split_counts.json` com treino e teste por classe ao lado de 800.829 / 17.771 / 224.598 e 88.980 / 1.975 / 24.955, tamanho dos 10 folds e fração duplicada (em `test_seen_in_train`, desde `c262b2b`, também as linhas com o mesmo rótulo, com outro rótulo e com os dois: `same_label_rows`, `other_label_rows`, `both_labels_rows`). Esperado: treino 800.828 / 17.771 / 224.598, teste 88.981 / 1.975 / 24.955, cerca de 13,7% do teste repetido no treino | Tabela que a seção 6 do relatório exige |

**Só avança se:** T05-1 e T05-4 estão verdes. São os dois testes que protegem contra vazamento em todo o resto.

## Tarefa 06 · métricas

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T06-1 | N1 | `metrics_from_confusion` na matriz da Fig. 4b: acurácia 99,78%, recall de Benign-DoH 90,23%, macro 99,01 / 96,72 / 97,82, FPR malicioso 3 em 90.955, até a quarta casa | I8 |
| T06-2 | N1 | As matrizes da Fig. 4 em `config.py` são iguais às de `scripts/metricas_fig4.py` depois de permutar a ordem das classes (o script usa Benign, Malicious, Non-DoH; o projeto, 0 = Non-DoH, 1 = Benign, 2 = Malicious) | Uma fonte só para o alvo |
| T06-3 | N1 | Toda chave de métrica agregada contém `macro` ou `weighted` | I7 |
| T06-4 | N1 | Matriz perfeita dá 1,0 em tudo; zero falsos positivos não divide por zero no intervalo de confiança | Casos de borda |
| T06-5 | N1 | `evaluate` recusa rótulos no lugar de probabilidades; a função de taxa base falha sem prevalência | Erro silencioso de AUC; número hipotético não vira medido |
| T06-6 | N1 | A comparação célula a célula de uma matriz com ela mesma dá zero; com uma célula trocada, dá a diferença esperada; com totais diferentes, devolve também a diferença de total | Medida de distância ao artigo, com o teste de 115.911 contra 115.910 |
| T06-7 | N1 | A Fig. 4b montada a partir de rótulos na ordem do projeto (0, 1, 2) comparada com o alvo de `config.py` dá distância zero; comparada com a matriz do script sem permutar, não dá | A ordem das classes do alvo é a da codificação do projeto |
| T06-8 | N1 | O dicionário devolvido por `evaluate`, com as duas AUC, passa por `json.dumps` e volta igual (escrito em `21171f4`) | Contrato com `save_run`, que grava sem conversor |
| T06-9 | N1 | A taxa base calculada para a Fig. 4b é a de `scripts/metricas_fig4.py` (escrito em `21171f4`) | I8 também na conta de taxa base |

Situação em `360c3d3`: os nove existem em `tests/test_evaluate.py` (14 funções) e rodaram verdes em 07/10/2026.

**Só avança se:** T06-1 está verde. É o único teste que amarra o código aos números publicados.

## Tarefa 07 · subconjuntos balanceados

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T07-1 | N1 | As três partes de Non-DoH são disjuntas, cobrem todo o Non-DoH do treino e diferem em no máximo uma amostra | Divisão do artigo (Seção III-B) |
| T07-2 | N1 | Os maliciosos são os mesmos nos três subconjuntos e nenhum é sintético | I3 |
| T07-3 | N1 | Todos os benignos reais estão presentes; a classe benigna termina com o mesmo número de amostras da maliciosa | Alvo do SMOTE |
| T07-4 | N1 | Nenhuma amostra sintética em Non-DoH | I3 |
| T07-5 | N1 | Mesma seed, mesmos subconjuntos | Reprodutibilidade |

Situação em `360c3d3`: os cinco existem em `tests/test_splits.py` e rodaram verdes em 07/10/2026; o T07-5 confere também que outra seed dá outros subconjuntos.

**Só avança se:** o resumo devolve contagem por classe, razão obtida e fração de benignos sintéticos. A tarefa 08 grava esses valores.

## Tarefa 08 · Balanced Stacked Random Forest (E1)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T08-1 | N1 | O modelo empilhado tem três bases e o meta-classificador tem três entradas | Arquitetura do artigo com `use_probas=False` |
| T08-2 | N1 | Os bases usam os hiperparâmetros de `config.py` (10, 5, 28, Gini, sem `class_weight`) quando a profundidade pedida é `MAX_DEPTH` | Trilha fiel |
| T08-3 | N1 | Predições em {0, 1, 2}; mesma seed, mesmas predições | Reprodutibilidade |
| T08-4 | N1 | `test_pipeline.py`, ponta a ponta com dados sintéticos: split, scaler, subconjuntos, bases, meta, avaliação e registro; os dois arquivos de resultado existem, a matriz soma o tamanho do teste e duas execuções dão `metrics.json` idêntico. Parametrizado nas duas leituras de profundidade; confere que a trilha e a profundidade gravadas no `run.json` são as da leitura pedida | O caminho inteiro funciona; I1, I2, I3, I6 juntos; a variante não sai igual à fiel por um argumento ignorado |
| T08-5 | N1 | Na validação cruzada, o scaler e os subconjuntos de cada fold são ajustados só com os folds de treino: a matriz acumulada soma o treino e não tem amostra sintética, e um valor extremo plantado em uma linha só aparece no máximo do scaler nas rodadas em que a linha está nos folds de treino (dois testes, em `tests/test_pipeline.py`) | I2 e I3 dentro do laço |
| T08-6 | N2 | `scripts/e1_reproducao.py`: asserções de 29 colunas, total do teste igual ao de `split_counts.json`, nenhuma amostra sintética na avaliação | Avaliação real íntegra |
| T08-7 | N2 | `results/e1/fiel/proposto/seed42/` e `results/e1/variante/profundidade_variavel/seed42/` com as duas matrizes, as duas AUC nomeadas, a tabela de decisão do meta, os bases isolados e a comparação com a Fig. 4a, a Fig. 4b e a Tabela II; `results/e1/RESUMO.md` com as duas leituras lado a lado | Entrega central de P1, nas duas leituras (decisão 45) |
| T08-8 | N2 | Duas execuções com `metrics.json` idêntico, nas duas leituras | G6 |
| T08-9 | N3 | `revisor-metodologico` sem bloqueante | Vazamento e fidelidade |

Situação em `360c3d3`: T08-1 a T08-3 em `tests/test_models.py`, T08-4 e T08-5 em `tests/test_pipeline.py`; T08-6 e T08-7 conferidos em `results/e1/` (`798ecd3`); **T08-8 em aberto**, com a segunda execução rodando em 07/10/2026; T08-9 informado pela sessão principal.

**Só avança se:** T08-4 está verde no CI. Resultado longe da Fig. 4b não bloqueia: registra-se a distância.

## Tarefa 09 · baselines (E2)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T09-1 | N1 | Cada um dos três baselines treina nos dados sintéticos e devolve predições em {0, 1, 2} e probabilidades de três colunas (um teste parametrizado) | Os construtores funcionam |
| T09-2 | N1 | O SMOTE dos baselines só aumenta o treino: o teste mantém o tamanho e nenhuma amostra sintética chega à avaliação | I3 |
| T09-3 | N1 | Árvore com profundidade 10 e Random Forest com 10 árvores, lidos de `config.py` | Tabela II |
| T09-4 | N2 | `scripts/e2_baselines.py`: o total da matriz de cada baseline é igual ao de `split_counts.json` | Mesmo teste do modelo proposto |
| T09-5 | N2 | Três diretórios em `results/e2/fiel/`, cada um com a diferença para a sua linha da Tabela II | Metade superior da Tabela II |
| T09-6 | N3 | A metade inferior da Tabela II em `config.py` (oito linhas, com a referência de cada uma) conferida contra o artigo por dois integrantes, célula a célula, inclusive as ausentes e a linha impressa em escala percentual | Número de referência do artigo copiado sem erro (decisão 46) |

**Só avança se:** os três baselines foram avaliados no mesmo teste da tarefa 08. O T09-6 bloqueia o fechamento da tarefa, não o início.

Como ficou (`759ec29`): T09-1 é `test_baseline_predicts_class_codes_and_three_probabilities` (parametrizado nos três modelos), T09-2 é `test_whole_train_smote_only_adds_synthetic_rows_to_the_train` e T09-3 é `test_baselines_use_the_hyperparameters_of_table_ii`, em `tests/test_models.py`. T09-4 e T09-5 conferidos em `results/e2/fiel/`. **T09-6 aberto, de pessoa.**

## Tarefa 10 · sensibilidade (E3)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T10-1 | N1 | Cada variante do núcleo treina e prevê nos dados sintéticos (um teste parametrizado) | As quatro variantes rodam |
| T10-2 | N1 | A variante `use_probas` tem meta com nove entradas; `rf_unico` não gera amostra sintética | Cada variante muda o ponto que declara |
| T10-3 | N1 | Cada variante do núcleo difere da configuração fiel em exatamente um ponto, exceto `rf_unico` (e a opcional `stacking_cv`), que reproduzem configurações inteiras e são testadas pelo que declaram: `rf_unico` é um modelo só, sem SMOTE, com `class_weight` e `max_features` no padrão | "Um ponto por vez", com as exceções declaradas |
| T10-4 | N2 | `scripts/e3_sensibilidade.py`: todas as variantes avaliadas no mesmo teste (asserção de total); tabela comparativa gerada por `python -m scripts.e3_resumo` | Comparação justa |
| T10-5 | N1 | Existe e não estava previsto: `test_meta_on_subsets_changes_the_meta_classifier_and_keeps_the_bases`, em `tests/test_models.py` | A variante `meta_uniao`, que era opcional e foi feita, muda só o meta |

**Só avança se:** a lista de variantes rodadas é a lista fechada da tarefa. Variante opcional não feita aparece como não feita.

Como ficou (`759ec29`): T10-1 a T10-3 em `tests/test_models.py` (`test_variant_fits_and_predicts_class_codes_and_three_probabilities`, parametrizado; `test_use_probas_variant_gives_the_meta_classifier_nine_inputs`; `test_single_forest_variant_is_fitted_without_synthetic_rows`; `test_stacked_variant_differs_from_the_fiel_configuration_in_one_point`, parametrizado; `test_single_forest_variant_is_the_configuration_of_the_public_script`). As variantes partem das duas leituras de profundidade (decisão 51d).

## Tarefa 11 · protocolo corrigido (E4)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T11-1 | N1 | Para uma seed, os três modelos recebem os mesmos índices de treino e de teste | Comparação pareada válida |
| T11-2 | N1 | A comparação pareada, em um exemplo feito à mão, devolve a diferença média, a contagem de vitórias e a estatística de Wilcoxon esperadas | O método travado está implementado certo |
| T11-3 | N1 | O filtro "sem duplicatas" remove do teste exatamente as linhas plantadas que existem no treino | Métrica sem duplicatas |
| T11-4 | N1 | A agregação por seed devolve média e desvio corretos em um exemplo pequeno | `summary.json` confiável |
| T11-5 | N2 | `scripts/e4_corrigido.py`: asserção de igualdade dos índices por seed; `summary.json` com dez seeds para A, B e C; trilha `corrigida` em todo `run.json`; a leitura de profundidade de A (decisão 45) dita no `run.json` e no caminho | Variância e comparação justa |
| T11-6 | N3 | `revisor-metodologico`, com atenção ao invariante I5 | Nenhuma escolha feita olhando o teste |
| T11-7 | N1 | Existe e não estava previsto: `test_paired_comparison_of_equal_values_reports_ties_and_no_statistic`, em `tests/test_evaluate.py` | Par empatado em todas as seeds não gera estatística de Wilcoxon inventada |
| T11-8 | N1 | Existe e não estava previsto: `test_paired_verdict_needs_a_mean_difference_larger_than_the_deviation`, em `tests/test_evaluate.py` | A regra de leitura fixada antes da execução (média maior que o desvio das diferenças) é a que o resumo aplica; serve também à tarefa 15 |
| T11-9 | N1 | Existe e não estava previsto: `test_corrected_run_registers_the_track_and_the_depth_reading`, em `tests/test_pipeline.py` | Trilha `corrigida` e leitura de profundidade no `run.json` (o que o T11-5 confere com dados reais) |
| T11-10 | N1 | Existe e não estava previsto: `test_corrected_summary_is_rebuilt_from_the_saved_files_without_training`, em `tests/test_pipeline.py` | O resumo sai dos arquivos gravados, sem treinar |
| T11-11 | N1 | Existe e não estava previsto: `test_group_folds_keep_machines_apart_and_put_every_row_in_one_test`, em `tests/test_splits.py` (importa `scripts.e4_corrigido`) | Nenhuma máquina em treino e teste da mesma dobra; I1 na avaliação por grupo |

O T11-3 cobre só o que for novo: o filtro é `seen_in_train`, já testado pelo T05-5.

**Só avança se:** as configurações estavam em `config.py` em commit anterior ao da primeira execução (`git log` confere). Os dois ⚠️ REVISAR foram resolvidos pela decisão 52.

Como ficou (`759ec29`): T11-1 é `test_every_model_of_a_seed_gets_the_same_train_and_test_rows`; T11-2, `test_paired_comparison_matches_a_hand_made_example`; T11-3, `test_unseen_scope_drops_exactly_the_planted_test_rows_that_exist_in_train`; T11-4, `test_aggregate_seeds_gives_mean_and_sample_standard_deviation`. T11-5 conferido em `results/e4/corrigida/`: `db56052` (configurações) é anterior ao commit `5165fd3` dos `run.json`; o agregado sai de `python -m scripts.e4_resumo`.

## Tarefa 12 · SHAP (E5)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T12-1 | N1 | Os valores SHAP de um Random Forest pequeno têm a forma (amostras, 29, 3) e a classe é indexada pelo último eixo | Erro de indexação do formato antigo |
| T12-2 | N1 | A importância global devolve uma linha por atributo e por classe, ordenada | Tabela de importância |
| T12-3 | N1 | A conversão de `Duration` normalizada para segundos desfaz o scaler em valores conhecidos | Limiar de 40 s discutido na unidade certa |
| T12-4 | N1 | A medida de estabilidade dá 1,0 para rankings iguais e valor menor para rankings trocados | Estabilidade entre submodelos |
| T12-5 | N2 | `scripts/e5_xai.py` gera as figuras equivalentes a todas as figuras SHAP do artigo (Figs. 5, 6a, 6b, 7 e 8) e a tabela de importância em `results/e5/variante/profundidade_variavel/seed42/`; em `results/e5/fiel/proposto/seed42/`, onde o custo permitir | Explicabilidade reproduzida (decisões 45 e 46) |
| T12-6 | N3 | Conferência visual das figuras: eixos rotulados, unidade, `Duration` em segundos | Figura utilizável no relatório |
| T12-7 | N2 | Painel (decisão 50): `uv sync --locked` verde com `explainerdashboard==0.5.8`; o script sobe o painel e a página responde em `localhost`; depois de rodar, `git status` está limpo e não há `.pkl` nem `.joblib` no disco | O painel funciona sem modelo serializado |
| T12-8 | N1 | Existe e não estava previsto: `test_stratified_sample_takes_the_requested_rows_of_each_class_and_follows_the_seed`, em `tests/test_explain.py` | A amostra do SHAP tem o tamanho pedido por classe e repete com a seed |
| T12-9 | N1 | Existe e não estava previsto: `test_dashboard_is_built_in_memory_without_writing_any_file`, em `tests/test_explain.py` (importa `scripts.painel_xai`) | O painel não grava modelo serializado; cobre em N1 metade do T12-7 |

O plano dizia que o painel não teria teste N1; o T12-9 existe e protege a regra de segurança (nenhum modelo serializado), não a biblioteca. Subir o painel e abrir a página continua sendo o T12-7, de pessoa.

Como ficou (`759ec29`): T12-1 a T12-4 em `tests/test_explain.py` (`test_shap_values_have_samples_features_classes_shape`, `test_global_importance_has_one_ordered_row_per_feature_and_class`, `test_original_units_turns_normalized_duration_back_into_seconds`, `test_rank_agreement_is_one_for_equal_rankings_and_lower_when_swapped`). T12-5 conferido nos dois diretórios de `results/e5/`. T12-6 e T12-7 abertos, de pessoa.

**Só avança se:** o tamanho das amostras usadas no SHAP está registrado no resultado.

## Tarefa 13 · segundo dataset: aquisição

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T13-1 | N1 | A carga do segundo dataset, em CSV sintético, devolve as 29 colunas de atributo, `label` em {0, 1, 2}, `origin` e `tool`, sem nenhum identificador (decisão 40) | Mesmo formato dos atributos; I4 |
| T13-2 | N1 | A conferência de colunas acusa coluna ausente e coluna com nome diferente | Relatório de compatibilidade confiável |
| T13-5 | N1 | Um CSV sintético com BOM e `TimeStamp` no formato `2020/1/14 15:49` é lido com a primeira coluna chamada `SourceIP` | Formato real do HKD e do combinado |
| T13-6 | N1 | A remoção de réplicas deixa uma linha de cada fluxo do HKD repetido e não toca nas linhas do CIRA | `combinado_sem_replicas` correto |
| T13-7 | N1 | A carga do segundo dataset não cria `group` nem `time_window` (era a segunda metade do T04-9) | A regra de grupo do CIRA não é aplicada onde não vale (decisão 40) |
| T13-3 | N2 | `uv run python data/verify.py` cobre os novos arquivos | Integridade |
| T13-4 | N2 | `scripts/e6_dados.py`: 29 colunas presentes; contagens por classe, origem e ferramenta ao lado das do README do dataset; HKD com 5.258 fluxos; réplicas contadas (20 por fluxo) | Compatibilidade real |

**Só avança se:** os três Parquets passam nas asserções. Q4 foi respondida em 07/10/2026 (decisão 47): o combinado sem réplicas é o dataset em que P1 é refeito.

Como ficou (`759ec29`): T13-1, T13-2 e T13-5 a T13-7 em `tests/test_data.py`, um teste por linha. T13-3 executado em 08/10/2026: 8 de 8 arquivos do manifesto. T13-4 conferido em `results/e6/dados/`.

## Tarefa 14 · segundo dataset: avaliação (E6)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T14-1 | N1 | A avaliação do recorte só de maliciosos não devolve precisão, FPR nem acurácia | Métrica sem negativos não é reportada |
| T14-2 | N1 | O recall por ferramenta, em um exemplo feito à mão, é o esperado | Recall por ferramenta |
| T14-3 | N1 | A contagem de valores fora de [0, 1] por atributo acha os valores plantados | Medida de mudança de faixa |
| T14-4 | N1 | Na transferência, o scaler aplicado ao segundo dataset é o ajustado no treino do CIRA | I2 entre datasets |
| T14-5 | N2 | 14a, `scripts/e6_dataset2.py`: transferência, retreino publicado e retreino sem réplicas completos, com a tabela de amostras por classe em treino, por fold e no teste, o recall por ferramenta com `n` e intervalo, e a asserção de que nenhum vetor do HKD está em treino e teste na versão sem réplicas | Entrega de P2, sem memorização disfarçada |
| T14-7 | N2 | 14a, no combinado sem réplicas: o sistema nas duas leituras de profundidade, com a matriz de teste e a de validação cruzada de 10 folds; asserções de que a matriz de validação soma o treino e de que a de teste soma o teste | P1 refeito no segundo dataset (decisão 47); I3 na validação |
| T14-8 | N2 | 14b, no combinado sem réplicas: três baselines avaliados no mesmo teste da 14a (asserção de total); figuras SHAP e tabela de importância dos bases treinados no combinado, com o tamanho da amostra registrado | Tabela II e explicabilidade refeitas no segundo dataset |
| T14-6 | N3 | `revisor-metodologico` sem bloqueante, em cada parte | Vazamento entre datasets |

A validação cruzada no combinado reutiliza `cross_validated_confusion`, coberta pelo T08-5; os baselines e o SHAP reutilizam o que T09-1 a T09-3 e T12-1 a T12-4 cobrem. Por isso a 14 não ganha teste N1 novo além de T14-1 a T14-4.

**Só avança se:** a tabela comparativa dos quatro cenários e a tabela final de P2 (CIRA ao lado do combinado sem réplicas) foram geradas por script. A 14a fecha com T14-1 a T14-5 e T14-7; a 14b, com T14-8.

Como ficou (`759ec29`): T14-1 a T14-3 em `tests/test_evaluate.py` (`test_malicious_only_evaluation_reports_no_precision_fpr_or_accuracy`, `test_recall_by_tool_matches_a_hand_made_example`, `test_outside_unit_interval_finds_the_planted_values`); T14-4 é `test_transfer_scales_the_second_dataset_with_the_scaler_of_the_first_train`, em `tests/test_pipeline.py`. N2: 14a por `scripts/e6_dataset2.py`, 14b por `python -m scripts.e6_baselines_xai`, resumos e tabela final por `python -m scripts.e6_resumo`. T14-5, T14-7 e T14-8 conferidos em `results/e6/`.

## Tarefa 15 · modificação M1 + M2 (E8)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T15-1 | N1 | O modelo modificado é um `Pipeline` com o scaler como primeiro passo e um Random Forest com `class_weight='balanced'` | Scaler reajustado em cada fold |
| T15-2 | N1 | O treino do modelo modificado tem o mesmo número de linhas do treino original | Nenhuma amostra sintética |
| T15-3 | N1 | A seleção de hiperparâmetros recebe só os índices de treino da seed | I5 |
| T15-4 | N1 | A grade declarada em `config.py` tem no máximo oito combinações e inclui a do artigo (10, 5, 28) | Grade travada |
| T15-5 | N2 | `python -m scripts.e8_modificacao` e `python -m scripts.e8_resumo`: `summary.json` com A, M1 e M1+M2 no CIRA e A e M1+M2 no combinado, dez seeds, com métricas com e sem duplicatas; hiperparâmetros selecionados por seed gravados | P3 medido |
| T15-6 | N3 | `revisor-metodologico`: o texto não afirma melhora que os números não mostram | Honestidade do resultado |

**Só avança se:** a hipótese e a grade estão em commit anterior ao da primeira execução.

Como ficou (`759ec29`): T15-1 é `test_modified_model_is_a_pipeline_with_the_scaler_first_and_a_class_weighted_forest`; T15-2, `test_modified_model_is_fitted_on_the_rows_of_the_original_train`; T15-3, `test_hyperparameter_selection_only_receives_train_rows_of_the_seed`; T15-4, `test_selection_grid_has_at_most_eight_combinations_and_the_one_of_the_article`; todos em `tests/test_models.py`. A grade tem oito combinações e inclui também (10, sem limite, 28) (decisão 54b). T15-5 conferido em `results/e8/corrigida/`. O `summary.json` guarda tempos de treino e não serve à comparação byte a byte do G6.

## Tarefa 16 · robustez à duração (cortável)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T16-1 | N1 | A ablação remove exatamente as colunas pedidas e mantém as demais na ordem | Parte A |
| T16-2 | N1 | A transformação de fragmentação reduz `Duration` e os bytes na proporção pedida e mantém as taxas | Parte B |
| T16-3 | N1 | A transformação é aplicada só aos maliciosos do teste | O treino não é alterado |
| T16-4 | N2 | `python -m scripts.e8_robustez` e `python -m scripts.e8_robustez_resumo`: métricas com e sem os atributos, dez seeds; curva de recall ou dispensa registrada | M3 medido |
| T16-5 | N1 | Existe e não estava previsto: `test_robustness_seed_fits_the_scaler_on_train_and_perturbs_only_test_malicious`, em `tests/test_robustness.py` (importa `scripts.e8_robustez`) | I2 e a regra do T16-3 dentro da execução de uma seed inteira |

Como ficou (`759ec29`): T16-1 a T16-3 em `tests/test_robustness.py` (`test_drop_features_removes_only_the_requested_columns_and_keeps_the_order`, `test_fragmentation_divides_duration_and_bytes_and_keeps_the_rates`, `test_fragmentation_changes_only_malicious_flows_of_the_test`). T16-4 conferido em `results/e8/corrigida/`: partes A e B feitas.

## Tarefa 17 · tabelas e figuras do relatório

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T17-1 | N1 | Com uma árvore `results/` de mentira em `tmp_path`, o gerador produz os arquivos `.tex` e o número escrito na tabela é o do `metrics.json` | Nenhum número digitado à mão |
| T17-2 | N1 | Faltando resultado de tarefa obrigatória (08, 09, 12, 14 e 21), o gerador falha; faltando opcional, lista como "não gerado" | Tabela incompleta não passa calada |
| T17-3 | N1 | Duas execuções geram `.tex` idênticos | Determinismo |
| T17-4 | N1 | Toda tabela de resultado de modelo traz a trilha e o nome da média na legenda; tabela que junta as duas leituras de profundidade tem a coluna que as identifica | I7 no relatório; as duas leituras não se misturam (decisão 45) |
| T17-5 | N2 | `scripts/make_report_assets.py` com o `results/` real; três números de cada tabela conferidos contra a origem; cada tabela e gráfico de resultado do artigo (lista da tarefa 17) tem o seu equivalente em `report/` | Rastreio; alvo de P1 completo (decisão 46) |

Como ficou (`759ec29`): seis funções em `tests/test_report_assets.py`. T17-1 é `test_number_in_table_is_the_one_in_metrics_json`; T17-2 são duas, `test_missing_required_result_fails` e `test_missing_optional_result_is_listed_as_not_generated`; T17-3 é `test_two_runs_write_identical_tex_and_csv` (cobre também os `.csv`); T17-4 são duas, `test_model_tables_name_track_seed_and_average_in_caption` e `test_tables_with_both_depth_readings_identify_each_one`. T17-5 executado em 08/10/2026 com saída em diretório temporário: 30 `.tex`, 30 `.csv`, `INDICE.md` e 13 `.png` idênticos aos versionados; a amostragem de três números por tabela é de pessoa.

## Tarefa 18 · relatório

Sem teste automático. N3: agente `revisor-de-texto` contra a especificação (nove seções, IEEE, contagens por classe dos dois datasets) e conferência de cada número contra `results/`. O PDF compila no Overleaf sem erro.

Cumprida pela tarefa 24. Executado em 08/10/2026: `tectonic relatorio.tex` compila sem erro e sem referência indefinida. De pessoa: a compilação no Overleaf com XeLaTeX e a leitura cruzada.

## Tarefa 19 · README e execução limpa

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T19-1 | N1 | CI verde na `main` no commit entregue | Estado final íntegro |
| T19-2 | N2 | Execução limpa em clone e diretório novos, fora do repositório, na sessão de implementação (decisão 44), pelos 22 passos da tarefa 19; os 229 `metrics.json` e o `summary.json` de E4 iguais aos versionados; os dois agregados de E8 iguais fora das chaves de tempo; `report/tables/` sem diferença | Um clone limpo regenera os resultados. Não testa outra pessoa nem outra máquina, e o relato diz isso |
| T19-3 | N2 | Instalação pelo `requirements.txt` com `pip` e a suíte verde | Caminho de quem não usa uv |
| T19-4 | N2 | Checagens de higiene do critério de aceite sem nenhuma linha devolvida | Nada proibido no repositório |
| T19-5 | N3 | Skill `checklist-entrega projeto` sem item exigido pendente | Entrega completa |

## Tarefa 20 · slides do projeto

Sem teste automático. N3: `revisor-de-texto`; todo número do slide confere com `results/`; ensaio cronometrado em 15 minutos.

Cumprida pela tarefa 24: `scripts/make_slides.py` monta as tabelas com as células de `report/tables/*.csv` e não tem teste N1. De pessoa: o ensaio e a conferência no Google Slides.

## Tarefa 21 · ferramenta de túnel (E7)

Obrigatória desde a decisão 49.

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T21-1 | N1 | Em `tests/test_data.py`, com um zip sintético: a carga por ferramenta mantém só as linhas com `DoH` verdadeiro, dá a cada uma a ferramenta da sua pasta e não devolve identificador | Conjunto só de maliciosos com rótulo de ferramenta válido; I4 |
| T21-2 | N2 | `scripts/e7_ferramenta.py`: total depois da limpeza conferido por asserção; treino e teste disjuntos; métricas por ferramenta ao lado dos três valores da Seção VI-D; figura equivalente à Fig. 9 | Seção VI-D e Fig. 9 reproduzidas |
| T21-3 | N3 | `revisor-metodologico` sem bloqueante; o resumo declara que o método é leitura da equipe | Vazamento e fidelidade |
| T21-4 | N1 | Existe; era condicional: `test_metrics_are_keyed_by_the_class_names_given`, em `tests/test_evaluate.py` | `evaluate` recebe os nomes das classes (decisão 51e) e as chaves por classe são os nomes passados |
| T21-5 | N1 | Existe e não estava previsto: `test_tool_roles_follow_the_train_counts_and_codes_are_mapped_by_name`, em `tests/test_splits.py` (importa `scripts.e7_ferramenta`) | O papel de cada ferramenta nos subconjuntos sai das contagens do treino, e os códigos, do nome |

Como ficou (`759ec29`): T21-1 é `test_tool_load_keeps_only_doh_rows_with_the_tool_of_the_folder`. T21-2 conferido em `results/e7/`; o resumo sai de `python -m scripts.e7_resumo`.

**Só avança se:** os pontos sem valor declarado da tarefa estão decididos antes da primeira execução (decisão 51).

## Tarefas 22 e 23 · padronização e acompanhamento

Sem teste automático. N3: critério de aceite conferido por outro integrante.

## Tarefa 24 · relatório em PDF e apresentação em PPTX

Sem teste automático: `scripts/make_slides.py` e `report/relatorio.tex` não têm teste N1. N2: `uv run --group slides python scripts/make_slides.py` e `tectonic relatorio.tex`, dentro de `report/`, sem erro. N3: `revisor-de-texto` nos dois documentos; páginas e slides olhados um a um; de pessoa, o `.pptx` no Google Slides.

---

## Resumo: testes N1 por arquivo

| Arquivo | Criado na tarefa | Testes |
| --- | --- | --- |
| `tests/test_smoke.py` | 01 | T01-1 |
| `tests/conftest.py` | 02 | fixtures `synthetic_flows` e `synthetic_raw_csv` |
| `tests/test_config.py`, `tests/test_runlog.py` | 02 | T02-1 a T02-6 |
| `tests/test_verify.py` | 03 | T03-1, T03-2 |
| `tests/test_data.py` (12 funções) | 04, 13, 21 | T04-1 a T04-4, T04-8, T04-9, T13-1, T13-2, T13-5 a T13-7, T21-1 |
| `tests/test_splits.py` (12) | 05, 07, 11, 21 | T05-1 a T05-5, T07-1 a T07-5, T11-11, T21-5 |
| `tests/test_evaluate.py` (23) | 06, 11, 14, 21 | T06-1 a T06-9, T11-2 a T11-4, T11-7, T11-8, T14-1 a T14-3, T21-4 |
| `tests/test_models.py` (16) | 08, 09, 10, 15 | T08-1 a T08-3, T09-1 a T09-3, T10-1 a T10-3, T10-5, T15-1 a T15-4 |
| `tests/test_pipeline.py` (7) | 08, 11, 14 | T08-4, T08-5, T11-1, T11-9, T11-10, T14-4 |
| `tests/test_explain.py` (6) | 12 | T12-1 a T12-4, T12-8, T12-9 |
| `tests/test_robustness.py` (4) | 16 | T16-1 a T16-3, T16-5 |
| `tests/test_report_assets.py` (6) | 17 | T17-1 a T17-4 |

Em `759ec29`, com as tarefas 01 a 17, 21 e 24 prontas, a suíte tem 101 funções de teste em doze arquivos e 110 casos com as parametrizações, todos verdes em 41 s (executado em 08/10/2026). Os testes importam nove scripts como módulo (`e1_reproducao`, `e3_sensibilidade`, `e4_corrigido`, `e4_resumo`, `e6_dataset2`, `e7_ferramenta`, `e8_modificacao`, `e8_robustez`, `painel_xai`, além de `make_report_assets` e `metricas_fig4`): renomear um deles quebra a suíte. Em `360c3d3`, com as tarefas 01 a 08, eram 51 funções em nove arquivos. Onde uma função nova da implementação tornar um destes testes sem sentido, o implementador relata e o plano é ajustado; o teste não é escrito por obrigação.
