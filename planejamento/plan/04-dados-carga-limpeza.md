# 04 · dados · carga, limpeza e reconciliação com a Tabela I (E0)

> ⚠️ REVISAR (07/10/2026, reconciliação no commit `5e11d56`): a fonte desta tarefa é `data/raw/cira/Total_CSVs.zip`, lido direto do zip (decisão 34; teste T04-8 com zip sintético). Na máquina onde a reconciliação rodou esse zip não existe: há a pasta extraída `data/raw/cira/Total_CSVs/` com os quatro CSVs. O zip da equipe no drive continua trazendo o zip. Motivo e as duas saídas estão no topo da [tarefa 03](03-dados-aquisicao-cira.md); a escolha é do usuário e vem antes desta tarefa. Nada foi mudado nos passos abaixo.

**Onde:** `src/doh_ids/data.py`, `scripts/e0_dados.py`, `tests/test_data.py`, `results/e0/dados/cira/seed42/`
**Objetivo:** um único conjunto de dados limpo, de três classes e 29 atributos, cujas contagens estão explicadas em relação à Tabela I do artigo.
**Depende de:** 02, 03
**Demonstra:** `results/e0/dados/cira/seed42/`: contagens brutas e limpas ao lado da Tabela I, diferença zero; tabela máquina × classe e período. Seção 6 (dados do artigo) e seção 8 (limitações).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **Fonte:** três membros de `data/raw/cira/Total_CSVs.zip`, lidos direto do zip: `l1-nondoh.csv`, `l2-benign.csv`, `l2-malicious.csv`. **Não ler `l1-doh.csv`**: ele é exatamente a união dos dois `l2` e contaria o DoH em dobro. A asserção de total bruto é 1.167.136 (897.493 + 19.807 + 249.836).
- **Limpeza adotada (decisão 34): remover as linhas com NaN.** Reproduz a Tabela I exatamente: 889.809 / 19.746 / 249.553. Os NaN estão só em `ResponseTimeTimeMedian` e `ResponseTimeTimeSkewFromMedian`, 8.028 linhas. Não há infinito nem duplicata exata nas 35 colunas.
- O passo 4 continua valendo como registro: o script grava a tabela de combinações, para o relatório mostrar que só essa regra reproduz o artigo. Remover duplicatas nos 29 atributos derruba o Non-DoH para 750.456 e não é adotado.
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
7. Gerar estatísticas descritivas por classe. Opcional, se sobrar tempo: os gráficos de densidade de `FlowBytesReceived`, `PacketLengthMean` e `PacketLengthVariance`, para comparar com a Fig. 2 do artigo; só valem o esforço se forem para o relatório.
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

- [ ] As contagens por classe depois da limpeza são 889.809 / 19.746 / 249.553 (asserção no script).
- [ ] O Parquet tem exatamente as 29 colunas de `config.py`, `label` e `group`; a função que monta a matriz de atributos devolve só as 29 (teste e asserção; invariante I4).
- [ ] Sem NaN e sem infinitos na saída (asserção).
- [ ] `results/e0/dados/cira/seed42/` contém a tabela de combinações de limpeza com a contagem por classe e a diferença para a Tabela I.
- [ ] A combinação adotada está registrada com a justificativa em `results/e0/dados/RESUMO.md`; `docs/04-dados.md` é atualizado pelo `cin0114-doc-sync` no fechamento.
- [ ] A contagem de máquinas e de dias por classe e a tabela máquina × classe (passo 8) estão gravadas.
- [ ] Rodar o script duas vezes gera Parquet com o mesmo hash.

## Testes

Seção "Tarefa 04" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de dados: G1–G10, com G5 = `uv run python scripts/e0_dados.py`.
