# Plano de testes por tarefa

> **Onde fica o código:** o repositório Git do projeto é a pasta `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`, `.githooks/`, `.github/`) é relativo a `project/`, e todo comando `uv` e `git` roda lá dentro. `docs/`, `planejamento/`, `.claude/` e `CLAUDE.md` ficam na pasta de trabalho, fora do repositório, e não são versionados.

Diz, para cada tarefa, o que precisa estar verde antes de passar para a seguinte. As regras de escrita dos testes estão em `.claude/rules/testes.md`; o gate geral, em [VERIFICACAO.md](VERIFICACAO.md).

## Três níveis

| Nível | O que é | Onde roda | Quem confere |
| --- | --- | --- | --- |
| **N1 automático** | `pytest` com dados sintéticos | máquina de quem implementa e CI do GitHub | implementador; CI |
| **N2 local com dados reais** | o script da tarefa, com asserções embutidas, e a conferência do arquivo gerado em `results/` | máquina de quem tem os datasets | implementador ou integrante; saída colada no pull request |
| **N3 revisão** | agente revisor e leitura de outro integrante | — | revisor; integrante |

O CI não tem os datasets: eles ficam fora do Git e o download do CIRA é manual. Por isso nenhum teste N1 lê `data/`, e tudo o que depende de contagem ou métrica real é N2.

**Regra de passagem:** a tarefa só fecha com N1 verde no CI, N2 executado (quando a tarefa tem) e N3 sem achado bloqueante. A cada tarefa roda a suíte inteira.

## Base comum dos testes

Criada na tarefa 02 e reutilizada por todas as seguintes.

- `tests/conftest.py`, duas fixtures. `synthetic_flows`: DataFrame com as 29 colunas de atributo de `config.py` e `label` inteiro em {0, 1, 2}, já limpo. `synthetic_raw_csv`: as 35 colunas do CSV real (5 identificadores, 29 atributos e `Label` em texto), com a máquina local `192.168.20.x` ora em `SourceIP` ora em `DestinationIP`, `TimeStamp` no formato `2020-01-14 15:49:11` e NaN só em `ResponseTimeTimeMedian` e `ResponseTimeTimeSkewFromMedian`, gravada em `tmp_path` quando o teste precisa de arquivo. Três classes desbalanceadas na mesma ordem de grandeza relativa do CIRA (muito Non-DoH, pouco Benign-DoH, Malicious-DoH intermediário), poucas centenas a poucos milhares de linhas, médias deslocadas por classe para os modelos terem o que aprender, gerador `numpy` com seed fixa.
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
| Arquivo proibido | `git ls-files` filtrado por `.pkl`, `.joblib`, `.pcap`, `.parquet`, `data/raw/`, `data/processed/`, PDF em `referencias/` | qualquer ocorrência |

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
| T02-2 | N1 | `save_run` cria `metrics.json` e `run.json` com trilha, seed, versões, hash dos dados e commit | I6 |
| T02-3 | N1 | Trilha fora de `fiel`, `corrigida`, `variante`, `dados` levanta erro | As trilhas não se misturam |
| T02-4 | N1 | Duas chamadas com as mesmas métricas geram `metrics.json` idêntico byte a byte; tempo e data só aparecem no `run.json` | Base do gate G6 |
| T02-5 | N1 | Fora de um repositório Git, o commit é gravado como nulo e a função não falha | Execução limpa em diretório sem Git |

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
| T04-9 | N1 | No CIRA, `group` é o endereço local `192.168.20.x` que aparece na origem ou no destino, inclusive quando `SourceIP` é o resolvedor; a carga do segundo dataset não cria `group` | Grupo correto para a avaliação por máquina |

**Só avança se:** a combinação de limpeza adotada está registrada com a diferença para a Tabela I, seja ela zero ou não.

## Tarefa 05 · split e normalização

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T05-1 | N1 | Índices de treino e teste disjuntos e cobrindo todas as linhas | I1 |
| T05-2 | N1 | Proporção por classe preservada nos dois conjuntos; teste com 10% | Split estratificado 90/10 |
| T05-3 | N1 | Mesma seed, mesmo split; seed diferente, split diferente | Reprodutibilidade |
| T05-4 | N1 | Com um valor extremo só no teste, o mínimo e o máximo do scaler são os do treino | I2 |
| T05-5 | N1 | A função que mede a fração do teste repetida no treino acha uma linha duplicada plantada | A medida de duplicatas é correta |
| T05-6 | N2 | `results/e0/dados/cira/seed42/split_counts.json` com treino e teste por classe ao lado de 800.829 / 17.771 / 224.598 e 88.980 / 1.975 / 24.955, tamanho dos 10 folds e fração duplicada. Esperado: treino 800.828 / 17.771 / 224.598, teste 88.981 / 1.975 / 24.955, cerca de 13,7% do teste repetido no treino | Tabela que a seção 6 do relatório exige |

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

**Só avança se:** T06-1 está verde. É o único teste que amarra o código aos números publicados.

## Tarefa 07 · subconjuntos balanceados

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T07-1 | N1 | As três partes de Non-DoH são disjuntas, cobrem todo o Non-DoH do treino e diferem em no máximo uma amostra | Divisão do artigo (Seção III-B) |
| T07-2 | N1 | Os maliciosos são os mesmos nos três subconjuntos e nenhum é sintético | I3 |
| T07-3 | N1 | Todos os benignos reais estão presentes; a classe benigna termina com o mesmo número de amostras da maliciosa | Alvo do SMOTE |
| T07-4 | N1 | Nenhuma amostra sintética em Non-DoH | I3 |
| T07-5 | N1 | Mesma seed, mesmos subconjuntos | Reprodutibilidade |

**Só avança se:** o resumo devolve contagem por classe, razão obtida e fração de benignos sintéticos. A tarefa 08 grava esses valores.

## Tarefa 08 · Balanced Stacked Random Forest (E1)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T08-1 | N1 | O modelo empilhado tem três bases e o meta-classificador tem três entradas | Arquitetura do artigo com `use_probas=False` |
| T08-2 | N1 | Os bases usam os hiperparâmetros de `config.py` (10, 5, 28, Gini, sem `class_weight`) | Trilha fiel |
| T08-3 | N1 | Predições em {0, 1, 2}; mesma seed, mesmas predições | Reprodutibilidade |
| T08-4 | N1 | `test_pipeline.py`, ponta a ponta com dados sintéticos: split, scaler, subconjuntos, bases, meta, avaliação e registro; os dois arquivos de resultado existem, a matriz soma o tamanho do teste e duas execuções dão `metrics.json` idêntico | O caminho inteiro funciona; I1, I2, I3, I6 juntos |
| T08-5 | N1 | Na validação cruzada, o scaler e os subconjuntos de cada fold são ajustados só com os folds de treino (a matriz acumulada soma o treino e não tem amostra sintética) | I2 e I3 dentro do laço |
| T08-6 | N2 | `scripts/e1_reproducao.py`: asserções de 29 colunas, total do teste igual ao de `split_counts.json`, nenhuma amostra sintética na avaliação | Avaliação real íntegra |
| T08-7 | N2 | `results/e1/fiel/proposto/seed42/` com as duas matrizes, as duas AUC nomeadas, a tabela de decisão do meta e a comparação com a Fig. 4a, a Fig. 4b e a Tabela II | Entrega central de P1 |
| T08-8 | N2 | Duas execuções com `metrics.json` idêntico | G6 |
| T08-9 | N3 | `revisor-metodologico` sem bloqueante | Vazamento e fidelidade |

**Só avança se:** T08-4 está verde no CI. Resultado longe da Fig. 4b não bloqueia: registra-se a distância.

## Tarefa 09 · baselines (E2)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T09-1 | N1 | Cada um dos três baselines treina nos dados sintéticos e devolve predições em {0, 1, 2} e probabilidades de três colunas (um teste parametrizado) | Os construtores funcionam |
| T09-2 | N1 | O SMOTE dos baselines só aumenta o treino: o teste mantém o tamanho e nenhuma amostra sintética chega à avaliação | I3 |
| T09-3 | N1 | Árvore com profundidade 10 e Random Forest com 10 árvores, lidos de `config.py` | Tabela II |
| T09-4 | N2 | `scripts/e2_baselines.py`: o total da matriz de cada baseline é igual ao de `split_counts.json` | Mesmo teste do modelo proposto |
| T09-5 | N2 | Três diretórios em `results/e2/fiel/`, cada um com a diferença para a sua linha da Tabela II | Metade da Tabela II |

**Só avança se:** os três baselines foram avaliados no mesmo teste da tarefa 08.

## Tarefa 10 · sensibilidade (E3)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T10-1 | N1 | Cada variante do núcleo treina e prevê nos dados sintéticos (um teste parametrizado) | As quatro variantes rodam |
| T10-2 | N1 | A variante `use_probas` tem meta com nove entradas; `rf_unico` não gera amostra sintética | Cada variante muda o ponto que declara |
| T10-3 | N1 | Cada variante do núcleo difere da configuração fiel em exatamente um ponto, exceto `rf_unico` (e a opcional `stacking_cv`), que reproduzem configurações inteiras e são testadas pelo que declaram: `rf_unico` é um modelo só, sem SMOTE, com `class_weight` e `max_features` no padrão | "Um ponto por vez", com as exceções declaradas |
| T10-4 | N2 | `scripts/e3_sensibilidade.py`: todas as variantes avaliadas no mesmo teste (asserção de total); tabela comparativa gerada | Comparação justa |

**Só avança se:** a lista de variantes rodadas é a lista fechada da tarefa. Variante opcional não feita aparece como não feita.

## Tarefa 11 · protocolo corrigido (E4)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T11-1 | N1 | Para uma seed, os três modelos recebem os mesmos índices de treino e de teste | Comparação pareada válida |
| T11-2 | N1 | A comparação pareada, em um exemplo feito à mão, devolve a diferença média, a contagem de vitórias e a estatística de Wilcoxon esperadas | O método travado está implementado certo |
| T11-3 | N1 | O filtro "sem duplicatas" remove do teste exatamente as linhas plantadas que existem no treino | Métrica sem duplicatas |
| T11-4 | N1 | A agregação por seed devolve média e desvio corretos em um exemplo pequeno | `summary.json` confiável |
| T11-5 | N2 | `scripts/e4_corrigido.py`: asserção de igualdade dos índices por seed; `summary.json` com dez seeds para A, B e C; trilha `corrigida` em todo `run.json` | Variância e comparação justa |
| T11-6 | N3 | `revisor-metodologico`, com atenção ao invariante I5 | Nenhuma escolha feita olhando o teste |

**Só avança se:** as três configurações estavam em `config.py` em commit anterior ao da primeira execução (`git log` confere).

## Tarefa 12 · SHAP (E5)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T12-1 | N1 | Os valores SHAP de um Random Forest pequeno têm a forma (amostras, 29, 3) e a classe é indexada pelo último eixo | Erro de indexação do formato antigo |
| T12-2 | N1 | A importância global devolve uma linha por atributo e por classe, ordenada | Tabela de importância |
| T12-3 | N1 | A conversão de `Duration` normalizada para segundos desfaz o scaler em valores conhecidos | Limiar de 40 s discutido na unidade certa |
| T12-4 | N1 | A medida de estabilidade dá 1,0 para rankings iguais e valor menor para rankings trocados | Estabilidade entre submodelos |
| T12-5 | N2 | `scripts/e5_xai.py` gera as figuras equivalentes às Figs. 5, 6a, 6b, 7 e 8 e a tabela de importância em `results/e5/fiel/` | Explicabilidade reproduzida |
| T12-6 | N3 | Conferência visual das figuras: eixos rotulados, unidade, `Duration` em segundos | Figura utilizável no relatório |

**Só avança se:** o tamanho das amostras usadas no SHAP está registrado no resultado.

## Tarefa 13 · segundo dataset: aquisição

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T13-1 | N1 | A carga do segundo dataset, em CSV sintético, devolve o mesmo esquema da carga do CIRA mais as colunas de origem e de ferramenta | Mesmo formato; I4 |
| T13-2 | N1 | A conferência de colunas acusa coluna ausente e coluna com nome diferente | Relatório de compatibilidade confiável |
| T13-5 | N1 | Um CSV sintético com BOM e `TimeStamp` no formato `2020/1/14 15:49` é lido com a primeira coluna chamada `SourceIP` | Formato real do HKD e do combinado |
| T13-6 | N1 | A remoção de réplicas deixa uma linha de cada fluxo do HKD repetido e não toca nas linhas do CIRA | `combinado_sem_replicas` correto |
| T13-3 | N2 | `uv run python data/verify.py` cobre os novos arquivos | Integridade |
| T13-4 | N2 | `scripts/e6_dados.py`: 29 colunas presentes; contagens por classe, origem e ferramenta ao lado das do README do dataset; HKD com 5.258 fluxos; réplicas contadas (20 por fluxo) | Compatibilidade real |

**Só avança se:** os três Parquets passam nas asserções. A resposta do professor sobre o dataset combinado (Q4) condiciona só a justificativa final e o texto do relatório; a carga e a tarefa 14 seguem assumindo a decisão 11 (decisão 39).

## Tarefa 14 · segundo dataset: avaliação (E6)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T14-1 | N1 | A avaliação do recorte só de maliciosos não devolve precisão, FPR nem acurácia | Métrica sem negativos não é reportada |
| T14-2 | N1 | O recall por ferramenta, em um exemplo feito à mão, é o esperado | Recall por ferramenta |
| T14-3 | N1 | A contagem de valores fora de [0, 1] por atributo acha os valores plantados | Medida de mudança de faixa |
| T14-4 | N1 | Na transferência, o scaler aplicado ao segundo dataset é o ajustado no treino do CIRA | I2 entre datasets |
| T14-5 | N2 | `scripts/e6_dataset2.py`: `results/e6/fiel/transferencia/seed42/`, `retreino_publicado/seed42/` e `retreino_sem_replicas/seed42/` completos, com a tabela de amostras por classe em treino, por fold e no teste, o recall por ferramenta com `n` e intervalo, e a asserção de que nenhum vetor do HKD está em treino e teste na versão sem réplicas | Entrega de P2, sem memorização disfarçada |
| T14-6 | N3 | `revisor-metodologico` sem bloqueante | Vazamento entre datasets |

**Só avança se:** a tabela comparativa dos quatro cenários foi gerada por script.

## Tarefa 15 · modificação M1 + M2 (E8)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T15-1 | N1 | O modelo modificado é um `Pipeline` com o scaler como primeiro passo e um Random Forest com `class_weight='balanced'` | Scaler reajustado em cada fold |
| T15-2 | N1 | O treino do modelo modificado tem o mesmo número de linhas do treino original | Nenhuma amostra sintética |
| T15-3 | N1 | A seleção de hiperparâmetros recebe só os índices de treino da seed | I5 |
| T15-4 | N1 | A grade declarada em `config.py` tem no máximo oito combinações e inclui a do artigo (10, 5, 28) | Grade travada |
| T15-5 | N2 | `scripts/e8_modificacao.py`: `summary.json` com A, M1 e M1+M2 no CIRA e A e M1+M2 no combinado, dez seeds, com métricas com e sem duplicatas; hiperparâmetros selecionados por seed gravados | P3 medido |
| T15-6 | N3 | `revisor-metodologico`: o texto não afirma melhora que os números não mostram | Honestidade do resultado |

**Só avança se:** a hipótese e a grade estão em commit anterior ao da primeira execução.

## Tarefa 16 · robustez à duração (cortável)

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T16-1 | N1 | A ablação remove exatamente as colunas pedidas e mantém as demais na ordem | Parte A |
| T16-2 | N1 | A transformação de fragmentação reduz `Duration` e os bytes na proporção pedida e mantém as taxas | Parte B |
| T16-3 | N1 | A transformação é aplicada só aos maliciosos do teste | O treino não é alterado |
| T16-4 | N2 | `scripts/e8_robustez.py`: métricas com e sem os atributos, dez seeds; curva de recall ou dispensa registrada | M3 medido |

## Tarefa 17 · tabelas e figuras do relatório

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T17-1 | N1 | Com uma árvore `results/` de mentira em `tmp_path`, o gerador produz os arquivos `.tex` e o número escrito na tabela é o do `metrics.json` | Nenhum número digitado à mão |
| T17-2 | N1 | Faltando resultado de tarefa obrigatória, o gerador falha; faltando opcional, lista como "não gerado" | Tabela incompleta não passa calada |
| T17-3 | N1 | Duas execuções geram `.tex` idênticos | Determinismo |
| T17-4 | N1 | Toda tabela de resultado de modelo traz a trilha e o nome da média na legenda | I7 no relatório |
| T17-5 | N2 | `scripts/make_report_assets.py` com o `results/` real; três números de cada tabela conferidos contra a origem | Rastreio |

## Tarefa 18 · relatório

Sem teste automático. N3: agente `revisor-de-texto` contra a especificação (nove seções, IEEE, contagens por classe dos dois datasets) e conferência de cada número contra `results/`. O PDF compila no Overleaf sem erro.

## Tarefa 19 · README e execução limpa

| ID | Nível | Teste | Garante |
| --- | --- | --- | --- |
| T19-1 | N1 | CI verde na `main` no commit entregue | Estado final íntegro |
| T19-2 | N2 | Execução limpa em diretório novo, por quem não escreveu o código; `metrics.json` gerados iguais aos versionados | Reprodução de verdade |
| T19-3 | N2 | Instalação pelo `requirements.txt` com `pip` e a suíte verde | Caminho de quem não usa uv |
| T19-4 | N2 | Checagens de higiene do critério de aceite sem nenhuma linha devolvida | Nada proibido no repositório |
| T19-5 | N3 | Skill `checklist-entrega projeto` sem item exigido pendente | Entrega completa |

## Tarefa 20 · slides do projeto

Sem teste automático. N3: `revisor-de-texto`; todo número do slide confere com `results/`; ensaio cronometrado em 15 minutos.

## Tarefa 21 · ferramenta de túnel (condicional)

Só se o professor exigir. T21-1 (N1, em `tests/test_data.py`): a montagem do conjunto mantém apenas fluxos maliciosos com rótulo de ferramenta válido. T21-2 (N2): `scripts/e7_ferramenta.py` com as métricas por ferramenta ao lado dos valores do artigo.

## Tarefas 22 e 23 · padronização e acompanhamento

Sem teste automático. N3: critério de aceite conferido por outro integrante.

---

## Resumo: testes N1 por arquivo

| Arquivo | Criado na tarefa | Testes |
| --- | --- | --- |
| `tests/test_smoke.py` | 01 | T01-1 |
| `tests/conftest.py` | 02 | fixture `synthetic_flows` |
| `tests/test_config.py`, `tests/test_runlog.py` | 02 | T02-1 a T02-5 |
| `tests/test_verify.py` | 03 | T03-1, T03-2 |
| `tests/test_data.py` | 04, 13, 21 | T04-1 a T04-4, T04-8, T04-9, T13-1, T13-2, T13-5, T13-6, T21-1 |
| `tests/test_splits.py` | 05, 07 | T05-1 a T05-5, T07-1 a T07-5 |
| `tests/test_evaluate.py` | 06, 11, 14 | T06-1 a T06-7, T11-2 a T11-4, T14-1 a T14-3 |
| `tests/test_models.py` | 08, 09, 10, 15 | T08-1 a T08-3, T08-5, T09-1 a T09-3, T10-1 a T10-3, T15-1 a T15-4 |
| `tests/test_pipeline.py` | 08, 11, 14 | T08-4, T11-1, T14-4 |
| `tests/test_explain.py` | 12 | T12-1 a T12-4 |
| `tests/test_robustness.py` | 16 | T16-1 a T16-3 |
| `tests/test_report_assets.py` | 17 | T17-1 a T17-4 |

Cerca de setenta testes ao fim do projeto, dos quais trinta e cinco até a tarefa 08. Onde uma função nova da implementação tornar um destes testes sem sentido, o implementador relata e o plano é ajustado; o teste não é escrito por obrigação.
