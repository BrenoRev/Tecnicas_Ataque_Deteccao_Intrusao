# 04 · dados · carga, limpeza e reconciliação com a Tabela I (E0)

> **Situação (07/10/2026, reconciliação no commit `0ae2d49`): pronta e executada em `9e7563f`** (branch `tarefa/04-carga-limpeza`, nascida de `tarefa/03-dados-cira`; código em `407dffc` e `0dd87bb`, resultado em `9e7563f`). **Concluída.** Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f). O ⚠️ REVISAR de `5e11d56` foi resolvido em 07/10/2026: `Total_CSVs.zip` está em `data/raw/cira/` e a decisão 34 vale como escrita.
>
> A tarefa 05 rodou o mesmo script de novo: os arquivos versionados hoje são os da execução de `0ae2d49`, com `run.json` apontando o commit `121cde9` e `dirty: false`.

## Complemento aberto pela decisão 46: a Fig. 2 (07/10/2026, reconciliação no commit `360c3d3`)

A tarefa continua pronta e executada no que já fazia. A decisão 46 põe a Fig. 2 do artigo entre os alvos de P1; o passo 7 a tratava como opcional e ela **não foi feita** (conferido: `results/e0/dados/cira/seed42/` só tem `.json` e `.csv`).

- **Onde a Fig. 2 é gerada: aqui, em `scripts/e0_dados.py`.** É o script que lê os dados; a tarefa 17 só lê `results/` e não tem como calcular densidade. O script grava a figura como arquivo auxiliar em `results/e0/dados/cira/seed42/`, e a tarefa 17 a leva para `report/figures/`.
- **O que a figura mostra, conferido na legenda do manuscrito:** densidade, por classe, de (a) `FlowBytesReceived`, (b) média e (c) variância do comprimento de pacote; o passo 7 já nomeava `PacketLengthMean` e `PacketLengthVariance`. Só a legenda foi lida; a escala dos eixos e o recorte de faixa da figura do artigo são conferidos no PDF por quem implementar.
- A figura sai do conjunto limpo, antes do split e sem normalizar: é descrição dos dados, não entra em nenhum ajuste. Eixos rotulados, com unidade.
- **Ciclo próprio**, em branch nova nascida da ponta da fila, porque as branches 04 a 08 estão encadeadas e nenhuma foi integrada. Não depende de modelo; cabe logo depois da tarefa 09 e precisa estar fechada antes da 17.
- Rodar E0 de novo regenera `metrics.json`, `split_counts.json` e o Parquet: os três têm de sair idênticos aos versionados (o Parquet, pelo `parquet_sha256`), e o `run.json` passa a apontar o commit novo. O script de E0 mudou depois da última execução versionada (o `run.json` aponta `4746c22`; depois disso `f1eba42` mexeu no script e `21171f4`, `2732d0a` e `b00e471` em `config.py`), então essa comparação também confirma que essas mudanças não alteraram o resultado de E0.
- Custo: a última execução de E0 levou 38,3 s (`run.json`, chave `timings`); o tempo da figura não foi medido.

**Como ficou (conferido em `759ec29`, 08/10/2026): complemento pronto e executado.** Código em `d45251e`, figura em `377e331`; `44798f9` passou a gerar o veredito de cada afirmação do artigo sobre a Fig. 2, registrado em `39a7007`. Comando: `uv run python scripts/e0_dados.py` (43,6 s no `run.json`, commit `18f0024`, `dirty: false`). Arquivos novos em `results/e0/dados/cira/seed42/`: `fig2_densidade.png`, `fig2_densidade.csv` (as curvas, que a tarefa 17 redesenha) e `fig2_faixa.csv`. Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f).

Critério de aceite do complemento:

- [x] Figura equivalente à Fig. 2 (três painéis, três classes) em `results/e0/dados/cira/seed42/`, gerada por `scripts/e0_dados.py`, com eixos e unidade. Figura aberta nesta reconciliação: três painéis, três classes, eixos em bytes, bytes² (escala logarítmica) e densidade.
- [x] `metrics.json`, `split_counts.json` e `parquet_sha256` idênticos aos da execução anterior. Executado: `git diff --stat 360c3d3..759ec29 -- project/results/e0` só lista o `RESUMO.md`, o `run.json` e os três arquivos da figura.
- [x] `results/e0/dados/RESUMO.md` diz o que a figura mostra ao lado do que o artigo afirma sobre a Fig. 2. Lido: seção "Fig. 2: densidade por classe", linha 157 em diante, com o que o artigo afirma na linha 195.

## Como ficou (conferido no código em `0ae2d49`)

- `data.py`: `load_cira(zip_path=CIRA_ZIP_PATH)` devolve os 5 identificadores, os 29 atributos, `label` inteiro e `group`, sem limpar; levanta `ValueError` com rótulo fora de `LABEL_ENCODING` ou fluxo sem endereço `192.168.20.x`. `local_machine(flows)`, `feature_matrix(flows)` (só as 29 colunas, por nome), `class_counts(flows)` (lista na ordem dos códigos) e `clean_flows(flows, drop_nan, drop_inf, duplicate_columns)`, que devolve `(fluxos que ficaram, removidas por classe)`.
- Não existe `load_dataset`: a carga do CIRA é `load_cira`. Não há função que leia o Parquet; quem consome usa `pd.read_parquet(CIRA_PARQUET_PATH)`.
- A regra adotada é `clean_flows(raw, drop_nan=True, drop_inf=False, duplicate_columns=None)`. O nome `"NaN"`, a lista `CLEANING_RULES` e `ADOPTED_RULE` moram em `scripts/e0_dados.py`, não no pacote.
- `data/processed/cira.parquet`: 1.159.108 linhas, colunas `FEATURE_COLUMNS + ["label", "group"]`, índice de 0 a n − 1, `label` inteiro e `group` em texto (`192.168.20.111`). SHA-256 em `metrics.json`, chave `parquet_sha256`.
- `results/e0/dados/cira/seed42/`: `metrics.json`, `run.json`, `limpeza_combinacoes.csv`, `maquina_por_classe.csv`, `periodo_por_classe.csv`, `estatisticas_descritivas.csv` (uma linha por classe e atributo, com `count`, `mean`, `std`, `min`, `25%`, `50%`, `75%`, `max`) e, da tarefa 05, `split_counts.json`. Leitura dos números em `results/e0/dados/RESUMO.md`.
- Chaves de `metrics.json`: `classes`, `raw_rows`, `nan_by_column`, `cleaning_rules`, `adopted_rule`, `table_i`, `clean_rows`, `repeated_vectors_by_class`, `vectors_in_more_than_one_class`, `skew_sentinel`, `machines_shared_with_malicious`, `days_shared_with_malicious`, `capture_by_class`, `parquet_columns`, `parquet_sha256`.
- O `data_sha256` do `run.json` de E0 é o do zip; o do Parquet está em `metrics.json`.

**Correção de premissa, medida em `limpeza_combinacoes.csv`:** não é verdade que só uma regra reproduz a Tabela I. Quatro regras empatam com diferença zero: "NaN", "NaN e infinito", "NaN e duplicatas exatas" e "NaN, infinito e duplicatas exatas". Empatam porque não há infinito nem duplicata exata nos dados, então as quatro removem as mesmas 8.028 linhas. A adotada é "NaN", a mais simples, como manda a decisão 34. O relatório diz "a regra mais simples entre as que reproduzem", não "a única".

**Onde:** `src/doh_ids/data.py`, `scripts/e0_dados.py`, `tests/test_data.py`, `results/e0/dados/cira/seed42/`
**Objetivo:** um único conjunto de dados limpo, de três classes e 29 atributos, cujas contagens estão explicadas em relação à Tabela I do artigo.
**Depende de:** 02, 03
**Demonstra:** `results/e0/dados/cira/seed42/`: contagens brutas e limpas ao lado da Tabela I, diferença zero; tabela máquina × classe e período. Seção 6 (dados do artigo) e seção 8 (limitações).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **Fonte:** três membros de `data/raw/cira/Total_CSVs.zip`, lidos direto do zip: `l1-nondoh.csv`, `l2-benign.csv`, `l2-malicious.csv`. **Não ler `l1-doh.csv`**: ele é exatamente a união dos dois `l2` e contaria o DoH em dobro. A asserção de total bruto é 1.167.136 (897.493 + 19.807 + 249.836).
- **Limpeza adotada (decisão 34): remover as linhas com NaN.** Reproduz a Tabela I exatamente: 889.809 / 19.746 / 249.553. Os NaN estão só em `ResponseTimeTimeMedian` e `ResponseTimeTimeSkewFromMedian`, 8.028 linhas. Não há infinito nem duplicata exata nas 35 colunas.
- O passo 4 continua valendo como registro: o script grava a tabela de combinações, para o relatório mostrar quais regras reproduzem o artigo (são quatro, equivalentes nestes dados; ver "Correção de premissa" acima). Remover duplicatas nos 29 atributos, além dos NaN, derruba o Non-DoH para 750.456 e não é adotado.
- Depois da limpeza ficam 139.353 linhas de Non-DoH, 949 de Benign-DoH e 15 de Malicious-DoH com vetor de 29 atributos repetido, e 326 vetores que aparecem em mais de uma classe. O script grava esses números; eles não são removidos na trilha fiel.
- **`group` é a máquina local**, não o `SourceIP`: o endereço `192.168.20.x` que aparece na origem ou no destino (os fluxos são bidirecionais e `SourceIP` às vezes é o resolvedor). Non-DoH e Benign-DoH vêm de quatro máquinas (`.111`, `.112`, `.113`, `.191`); Malicious-DoH, de dez (`.144`, `.204` a `.212`).
- **O dia da captura é usado só na tabela de período por classe e não vai para o Parquet** (decisão 37). Non-DoH e Benign-DoH: 09/12/2019 a 14/01/2020. Malicious-DoH: 18/03 a 01/04/2020. Não há máquina nem dia em comum entre o malicioso e as outras duas classes; o script grava a tabela máquina × classe e o período por classe, que vão para as seções 6 e 8 do relatório.
- `TimeStamp` tem o formato `2020-01-14 15:49:11`.
- As colunas de assimetria têm o valor `-10` em 298.766 linhas. É o valor sentinela que o DoHLyzer devolve quando o desvio padrão é zero (confirmado no código do extrator, métodos `get_skew` e `get_skew2` de `meter/features/packet_length.py` e `response_time.py`, e nos dados; é fonte pública, citável no código). O script conta por coluna e por classe.
- Memória: o conjunto carrega sem tipos explícitos.

## Arquivos

- `src/doh_ids/data.py` — novo: carga dos CSVs, rótulo de três classes, remoção de identificadores, limpeza.
- `scripts/e0_dados.py` — novo: roda a carga, testa as combinações de limpeza, grava o Parquet e o relatório de contagens.
- `tests/test_data.py` — novo.
- `data/processed/cira.parquet` — gerado, fora do Git.
- `results/e0/dados/cira/seed42/` — contagens e estatísticas, no Git; `results/e0/dados/RESUMO.md` com a leitura dos números.
- `docs/04-dados.md:24-35` — atualizado pelo agente `cin0114-doc-sync` no fechamento, com o resultado da reconciliação (o implementador não edita `docs/`).

## O que fazer

1. Carregar os CSVs registrados na tarefa 03 e derivar o rótulo de três classes segundo `config.py`. Como o dataset vem em duas camadas, cada linha de Non-DoH, Benign-DoH e Malicious-DoH deve entrar uma única vez: conferir se os arquivos de DoH da camada 1 repetem as linhas da camada 2 e não contar em dobro.
2. Separar as cinco colunas identificadoras logo após a carga. A matriz de atributos é sempre montada selecionando por nome as 29 colunas de `config.py`, nunca por "todas menos o rótulo". O Parquet guarda, além dos 29 atributos e de `label`, uma coluna auxiliar, `group` (a máquina local, conforme o bloco acima), usada só pela avaliação por grupo opcional da tarefa 11.
3. Contar por classe: total, linhas com NaN, com infinito, duplicadas exatas, duplicadas depois de remover os identificadores.
4. Testar as combinações de limpeza (remover NaN; remover infinitos; remover duplicatas com e sem identificadores; combinações) e registrar a contagem por classe de cada uma ao lado do alvo 889.809 / 19.746 / 249.553.
5. Adotar a combinação que reproduz a Tabela I. Se nenhuma reproduzir exatamente, adotar a mais próxima e registrar a diferença por classe. Não ajustar regra de limpeza para forçar o número.
6. Gravar o resultado limpo em `data/processed/cira.parquet` e seu SHA-256 em `results/e0/dados/cira/seed42/`.
7. Gerar estatísticas descritivas por classe. (Desde a decisão 46 os gráficos são obrigatórios: ver o complemento no topo.) Opcional, se sobrar tempo: os gráficos de densidade de `FlowBytesReceived`, `PacketLengthMean` e `PacketLengthVariance`, para comparar com a Fig. 2 do artigo; só valem o esforço se forem para o relatório.
8. Contar quantas máquinas locais (`group`) e quantos dias de captura existem por classe **antes** de descartar os identificadores, e gravar em `results/e0/dados/cira/seed42/`, junto com a tabela máquina × classe e o período por classe. Esse número diz se o split por grupo da tarefa 11 é viável.

## Por quê

Ambiguidade A1 e decisão 08. Reproduzir as contagens da Tabela I é o primeiro marco verificável do projeto: se os dados de partida já diferem, toda diferença posterior fica sem explicação. A especificação exige descrever os dados e a formação dos conjuntos na seção 6 do relatório.

## Evidência — verificada no baseline

- `docs/04-dados.md:26-31` — Tabela I contra contagens brutas, diferença de 8.028 fluxos.
- `docs/02-artigo.md:87` — A1: o artigo não descreve limpeza.
- `docs/04-dados.md:66-69` — por que identificadores não entram.
- `docs/05-plano-experimental.md:30-38` — escopo de E0.

## Risco

- Nenhuma limpeza reproduzir a Tabela I. Mitigação: reportar a mais próxima; a diferença esperada é pequena (0,7% do total) e dificilmente muda as métricas.
- Estouro de memória ao carregar tudo de uma vez: 1,17 milhão de linhas por 34 colunas cabe em memória; se não couber, ler com tipos explícitos.
- Contagem em dobro por causa das duas camadas (passo 1): coberto por asserção de que o total bruto bate com o da tarefa 03.

## Critério de aceite

Conferido em 07/10/2026 no commit `0ae2d49`. O script de E0 não foi rodado nesta reconciliação: os itens de dados reais foram confirmados pelos arquivos versionados em `results/`.

- [x] As contagens por classe depois da limpeza são 889.809 / 19.746 / 249.553 (asserção no script). Lido: asserção em `scripts/e0_dados.py:347`; `clean_rows` de `metrics.json` traz os três números.
- [x] O Parquet tem exatamente as 29 colunas de `config.py`, `label` e `group`; a função que monta a matriz de atributos devolve só as 29 (teste e asserção; invariante I4). Executado: esquema do `cira.parquet` do disco lido com `pyarrow` e igual a `FEATURE_COLUMNS + ["label", "group"]`; testes `test_load_returns_features_and_integer_label_without_identifiers` e `test_feature_matrix_is_selected_by_name`. Lido: asserções em `e0_dados.py:354-356`.
- [x] Sem NaN e sem infinitos na saída (asserção). Lido: `e0_dados.py:357`; o script só grava resultado se a asserção passa.
- [x] `results/e0/dados/cira/seed42/` contém a tabela de combinações de limpeza com a contagem por classe e a diferença para a Tabela I. Lido: `limpeza_combinacoes.csv`, dez regras.
- [x] A combinação adotada está registrada com a justificativa em `results/e0/dados/RESUMO.md`; `docs/04-dados.md` é atualizado pelo `cin0114-doc-sync` no fechamento. Primeira metade lida em `RESUMO.md`. **Fechado em 08/10/2026:** `docs/04-dados.md` foi reconciliado pelo `cin0114-doc-sync` em `0ca5dcf` e `3da178e` (lido no histórico); a linha 3 do documento diz que o medido em `docs/08-inventario-dados.md` prevalece, e o único `[A verificar]` que resta (linha 152) é de um dataset alternativo que não foi usado.
- [x] A contagem de máquinas e de dias por classe e a tabela máquina × classe (passo 8) estão gravadas. Lido: `periodo_por_classe.csv` (4 máquinas e 13 dias em Non-DoH e Benign-DoH; 10 máquinas e 15 dias em Malicious-DoH) e `maquina_por_classe.csv`; `machines_shared_with_malicious` e `days_shared_with_malicious` iguais a zero.
- [x] Rodar o script duas vezes gera Parquet com o mesmo hash. Confirmado pelo histórico: as execuções de `9e7563f` (03:09) e de `0ae2d49` (03:14) gravaram o mesmo `parquet_sha256` e `git diff 9e7563f 0ae2d49` não toca `metrics.json`. O Parquet do disco tem esse hash (`shasum -a 256` executado).

## Testes

Seção "Tarefa 04" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de dados: G1–G10, com G5 = `uv run python scripts/e0_dados.py`.
