# 02 · fundação · configuração e registro de execução

**Onde:** `src/doh_ids/config.py`, `src/doh_ids/runlog.py`, `tests/`
**Objetivo:** todo experimento lê as mesmas constantes e grava o resultado no mesmo formato, com tudo o que é preciso para regenerá-lo.
**Depende de:** 01
**Demonstra:** `config.py` com cada hiperparâmetro e a seção do artigo de origem; formato único de resultado em `results/`. Base da seção 4 do relatório e da rastreabilidade de todo número.

> **Situação (07/10/2026, reconciliação no commit `0ae2d49`): pronta em `b1434ab`** (branch `tarefa/02-config-runlog`, nascida de `tarefa/01-prova-ci`; commits `412c097` e `b1434ab`). Aguarda integração por pessoa (G10). **Passo 5a fechado em 07/10/2026 (reconciliação no commit `360c3d3`):** `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45.

## Como ficou (conferido no código em `0ae2d49`)

Nomes públicos que as tarefas seguintes consomem.

- `config.py`: `CLASS_NAMES` (a posição é o código da classe), `LABEL_COLUMN`, `LABEL_ENCODING`, `ID_COLUMNS`, `FEATURE_COLUMNS`, `NAN_COLUMNS`, `SKEW_COLUMNS`, `SKEW_SENTINEL`, `TABLE_I_COUNTS`, `CIRA_ZIP_MEMBERS`, `CIRA_LOCAL_PREFIX`, `TEST_SIZE`, `N_SUBSETS`, `N_ESTIMATORS`, `MAX_FEATURES`, `MAX_DEPTH`, `SEED_FIEL`, `SEEDS_CORRIGIDA`, `TRACKS`, `PROJECT_ROOT`, `DATA_RAW_DIR`, `DATA_PROCESSED_DIR`, `RESULTS_DIR`, `CIRA_ZIP_PATH`, `CIRA_PARQUET_PATH`. As constantes de `SKEW_COLUMNS` a `CIRA_LOCAL_PREFIX` e os dois caminhos do CIRA entraram com as tarefas 03 e 04.
- A seed derivada é a função `smote_seed(seed, subset_index)`, que devolve `seed * 100 + subset_index`; não há constante.
- `runlog.py`: `save_run(experiment, track, slice_name, seed, metrics, config, data_sha256, timings, results_dir=RESULTS_DIR)` devolve o diretório `<results_dir>/<experiment>/<track>/<slice_name>/seed<seed>/`. `git_state(repo_dir)` devolve `(commit, dirty)`.
- `metrics.json` recebe só o dicionário `metrics`, gravado com `json.dumps` sem conversor: os valores precisam ser tipos nativos do Python (`int`, `float`, `list`, `dict` com chave em texto). Um `numpy.int64` ou um array levanta `TypeError`; o script de E0 converte com `.tolist()`.
- `run.json` tem as chaves `experiment`, `track`, `slice`, `seed`, `config`, `data_sha256`, `timings`, `timestamp`, `python`, `libraries`, `commit`, `dirty`, `hostname`, `cpu_count`. O recorte aparece como `slice`. O que a tarefa quiser registrar por nome (leitura adotada, variante, ponto que muda) entra pelo dicionário `config`; tempos, por `timings`.
- `dirty` mede o repositório inteiro menos `project/results/` (`runlog.py:38-44`). Documento de `docs/` ou de `planejamento/` editado e não commitado marca `dirty: true`; arquivo de `results/` alterado não marca. Consequência prática: toda edição do plano precisa estar em commit antes de rodar um experimento.
- `tests/conftest.py`: fixtures `synthetic_flows` (2.340 linhas: 1.800 / 60 / 480, seed 0, 29 atributos e `label`) e `synthetic_raw_csv` (as 35 colunas, NaN nas duas colunas de `NAN_COLUMNS` em uma linha a cada vinte).

## Reconciliado com a tarefa 01 (07/10/2026, commit `5e11d56`)

- Dependência: a 01 está pronta e ainda não integrada. A branch desta tarefa nasce da `main` depois da integração ou, em execução encadeada, de `tarefa/01-prova-ci`, com isso dito no relato.
- O que a 01 deixou e esta tarefa usa, conferido no código: pacote `doh_ids` instalável (`src/doh_ids/__init__.py`), `pythonpath = ["."]` no pytest, lint com `D1`, `ERA` e `C90`, `tests/test_smoke.py`. `tests/conftest.py`, `config.py` e `runlog.py` não existem: são desta tarefa.
- O repositório é a raiz (decisão 43): o hash do commit é lido com o Git a partir de `project/` sem mudança, mas `dirty` passa a refletir a árvore inteira, inclusive `docs/` e `planejamento/`. Um documento editado e não commitado marca `dirty: true`; o resultado versionado exige árvore limpa (decisão 38).
- `jobs/` não existe (passo 5a): só é criada se a equipe executar no Apuana. `N_JOBS = -1` foi declarado em `4746c22` (decisão 45).
- A constante dos membros de `Total_CSVs.zip` (bloco abaixo) é `CIRA_ZIP_MEMBERS`. O ⚠️ REVISAR das tarefas 03 e 04 foi resolvido em 07/10/2026: os zips originais foram repostos em `project/data/raw/cira/` e a decisão 34 vale como escrita.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- Os nomes das 35 colunas dos CSVs são exatamente os previstos: 5 identificadores, 29 atributos e `Label`. Não há ajuste a fazer na lista.
- O rótulo vem em texto. `config.py` declara o mapa `{"NonDoH": 0, "Benign": 1, "Malicious": 2}`.
- `config.py` declara também os membros lidos de `Total_CSVs.zip` (`l1-nondoh.csv`, `l2-benign.csv`, `l2-malicious.csv`) e as duas colunas em que há NaN (`ResponseTimeTimeMedian`, `ResponseTimeTimeSkewFromMedian`), usadas na fixture de teste.
- Duas fixtures em `tests/conftest.py`: `synthetic_flows` (29 atributos e `label` inteiro, já limpo) e `synthetic_raw_csv` (as 35 colunas do CSV, `Label` em texto, máquina local `192.168.20.x` ora em `SourceIP` ora em `DestinationIP`, `TimeStamp` com segundos e NaN só nessas duas colunas), gravada em `tmp_path` quando o teste precisa de arquivo.

## Arquivos

- `src/doh_ids/config.py` — novo: nomes das classes e sua codificação, lista dos 29 atributos, lista dos 5 identificadores, hiperparâmetros da trilha fiel, seeds, caminhos relativos.
- `src/doh_ids/runlog.py` — novo: função que grava métricas e metadados em `results/<experimento>/<trilha>/<recorte>/seed<k>/` (decisão 38).
- `tests/test_config.py`, `tests/test_runlog.py` — novos.
- `tests/conftest.py` — novo: fixtures `synthetic_flows` e `synthetic_raw_csv`, base de todos os testes seguintes (ver `PLANO-DE-TESTES.md`).

## O que fazer

1. Em `config.py`, declarar a codificação `0 = Non-DoH, 1 = Benign-DoH, 2 = Malicious-DoH` (a do script dos autores) e os nomes das 29 colunas de atributo e das 5 de identificação, copiados de `docs/04-dados.md:54-62`.
2. Declarar os hiperparâmetros da trilha fiel, cada um com um comentário dizendo a seção do artigo de onde vem: 10 árvores e `max_features` 28 (IV-A), profundidade 5 (IV-B), split de 10% (III-B), 3 subconjuntos (III-B). O que for escolha nossa leva um comentário dizendo que o artigo é omisso naquele ponto e qual leitura foi adotada, sem citar arquivo interno, número de decisão nem identificador de ambiguidade (`.claude/rules/codigo.md`). Os comentários são em prosa (`# 10 árvores, Seção IV-A do artigo`), nunca na forma `nome=valor`: a regra `ERA` do lint barra comentário que pareça código (verificado com ruff 0.16.10 em 07/10/2026).
3. Declarar as seeds: 42 para a trilha fiel, 0 a 9 para a corrigida (decisão 12). Declarar também a seed derivada: o SMOTE do subconjunto `i` usa `seed * 100 + i`; os Random Forests e o meta-classificador usam `seed` (decisão 41).
4. Em `runlog.py`, escrever a função de registro `save_run`: recebe nome do experimento, trilha, recorte (modelo, variante ou cenário), seed, dicionário de métricas, dicionário de configuração, SHA-256 do arquivo de dados e dicionário de tempos; monta o caminho `results/<experimento>/<trilha>/<recorte>/seed<k>/` e grava ali `metrics.json` e `run.json` (decisão 38). Arquivos auxiliares nomeados (por exemplo `split_counts.json`) ficam no mesmo diretório. O texto de interpretação de cada experimento fica em `results/<experimento>/<trilha>/RESUMO.md`; a hipótese escrita antes de rodar, quando a tarefa pede, em `HIPOTESE.md` no mesmo nível. O `metrics.json` só contém valores determinísticos; tempos de execução vão para o `run.json`, para que duas execuções possam ser comparadas com `diff`.
5. O `run.json` contém: trilha, seed, data e hora, tempos de treino, versão do Python e das bibliotecas principais, SHA-256 do arquivo de dados usado, hash do commit e indicação de árvore de trabalho suja. Grava também o nome da máquina e o número de núcleos usados: é a evidência, no repositório, de onde o resultado foi gerado (decisão 42).
5a. Declarar em `config.py` a constante `N_JOBS`, usada por todo estimador que aceita `n_jobs`, com o mesmo valor do `--cpus-per-task` dos scripts de `jobs/` (`[Decidir: valor]`). O resultado do Random Forest não depende de `n_jobs` quando a seed é fixa.
6. A função recusa trilha fora de `fiel`, `corrigida`, `variante` e `dados`. `variante` é das leituras alternativas da tarefa 10; `dados` é de E0 e da preparação do segundo dataset, que não treinam modelo.
7. Testar: os dois arquivos são criados, os campos obrigatórios existem, trilha inválida levanta erro.

## Por quê

Decisões 07, 12 e 18. Sem um formato único de resultado, a tarefa 17 não consegue gerar as tabelas do relatório por script, e a mistura de trilhas (risco R7) fica possível.

## Evidência — verificada no baseline

- `docs/04-dados.md:54-62` — grupos de colunas lidos do código do DoHLyzer.
- `docs/03-auditoria-repositorio.md`, seção "O que o código acrescenta" — ordem dos rótulos e seed 42.
- `docs/02-artigo.md:11-27` — origem de cada hiperparâmetro.
- `.claude/skills/experimento/SKILL.md`, seção "Ao registrar" — o que cada execução precisa gravar.

## Risco

- Os nomes de coluna vêm do código do extrator, não do CSV. Se o CSV divergir, a tarefa 04 corrige `config.py`; por isso a lista fica em um só lugar.
- Hash do commit indisponível fora de um repositório Git: gravar `null` e marcar como árvore suja, sem falhar.

## Critério de aceite

Conferido em 07/10/2026 no commit `0ae2d49`. "Executado" quer dizer `uv run pytest` rodado nesta reconciliação (23 testes verdes); "lido" quer dizer conferido no arquivo, sem execução.

- [x] `config.py` tem exatamente 29 nomes de atributo e 5 de identificador, sem interseção (teste). Executado: `test_feature_and_id_columns_are_29_and_5_without_repetition_or_overlap`.
- [x] Todo hiperparâmetro tem comentário de origem: a seção do artigo, ou a frase "o artigo não informa" seguida da leitura adotada. Conferido na revisão do pull request, constante por constante; não há grep que prove isso. Lido em `config.py:79-100`: `TEST_SIZE`, `N_SUBSETS`, `N_ESTIMATORS`, `MAX_FEATURES`, `MAX_DEPTH` e as seeds têm o comentário. A conferência humana no pull request continua devida.
- [x] `run.json` contém trilha, seed, versões, hash dos dados e commit (teste; invariante I6). Executado: `test_run_json_declares_track_seed_versions_data_hash_commit_and_machine`. Lido no arquivo real `results/e0/dados/cira/seed42/run.json`.
- [x] Trilha inválida é rejeitada (teste). Executado: `test_save_run_rejects_unknown_track`.
- [x] `save_run` monta o caminho `results/<experimento>/<trilha>/<recorte>/seed<k>/` (teste). Executado: `test_save_run_writes_both_files_in_the_standard_path`; o caminho real `results/e0/dados/cira/seed42/` existe.
- [x] Passo 5a, fora da lista original de critérios: `N_JOBS` em `config.py`. Lido em `360c3d3`: `N_JOBS = -1`, com o comentário de que cada árvore recebe a própria seed e o valor só muda o tempo; valor confirmado pela decisão 45.

## Testes

Seção "Tarefa 02" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de fundação: G1–G4, G7, G8, G10.
