# 13 · segundo dataset · aquisição e compatibilidade

**Onde:** `data/README.md`, `data/manifest.json`, `data/verify.py`, `src/doh_ids/data.py`, `src/doh_ids/config.py`, `scripts/e6_dados.py`, `tests/test_data.py`, `results/e6/dados/`
**Objetivo:** o segundo dataset carregado no mesmo formato do CIRA, com a compatibilidade de colunas conferida e a justificativa da escolha pronta para o relatório.
**Depende de:** — para o download e o registro (passos 2 e 3, onda 0); 04 para a carga e a limpeza (passos 4 a 8)
**Demonstra:** `results/e6/dados/`: compatibilidade de colunas, contagens por classe, origem e ferramenta, e o parágrafo de justificativa. P2 e seção 6.

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- **Q4 respondida em 07/10/2026 (`docs/07-pendencias.md`); efeito na decisão 47.** P2 refaz no segundo dataset tudo o que P1 produz no CIRA. O dataset em que isso é feito é o **combinado sem réplicas**, o único com as três classes; o combinado como publicado e o HKD (transferência) ficam como análises ao lado. O passo 1 e o risco "Q4 respondida com não" deixam de valer como condicionais: não há troca de fonte prevista.
- O professor não comentou as duas ressalvas enviadas (Non-DoH e Benign-DoH do combinado são os do CIRA; réplicas do HKD). A justificativa do passo 8 declara as duas, e declara que o HKD sozinho só tem a classe maliciosa e por isso não permite treinar o sistema.
- **"Contagens por classe" do segundo dataset (decisão 47) saem daqui:** `results/e6/dados/combinado_sem_replicas/seed42/` é o equivalente, para P2, da reconciliação com a Tabela I. A tabela por conjunto (treino, folds, teste) é da tarefa 14.
- `sha256_of` está em `doh_ids.data` desde `f1eba42`; `data/verify.py` e `scripts/e0_dados.py` importam de lá.
- A carga do segundo dataset não cria `group`: o teste correspondente é o T13-7 do plano de testes (era a segunda metade do T04-9), e o T13-1 confere o esquema da decisão 40, sem `group`.
- A tarefa 21 lê `data/raw/cira/MaliciousDoH-CSVs.zip`, que já está no manifesto; a carga desse arquivo é da 21, não desta tarefa.
- Execução com dados reais na própria sessão (decisão 44). Custo: não medido; a tarefa não treina modelo.

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- **`load_cira` não serve para o segundo dataset.** Ela lê os membros de `CIRA_ZIP_MEMBERS` de um zip, mapeia o rótulo com `LABEL_ENCODING` e levanta `ValueError` com rótulo fora do mapa ou com fluxo sem endereço `192.168.20.x`, que é o caso de todo o HKD. A carga do segundo dataset é função nova em `data.py`; reutiliza `feature_matrix`, `class_counts` e `clean_flows`.
- "A mesma função de limpeza da tarefa 04" (passo 6) é `clean_flows(flows, drop_nan=True, drop_inf=False, duplicate_columns=None)`, que devolve `(fluxos que ficaram, removidas por classe)`. O nome da regra adotada mora em `scripts/e0_dados.py` (`ADOPTED_RULE`), não no pacote: o script novo passa os mesmos três argumentos.
- **Teste herdado da tarefa 04:** a segunda metade do T04-9, "a carga do segundo dataset não cria `group`", não foi escrita, porque a carga não existia. É escrita aqui, em `tests/test_data.py`, junto com o T13-1.
- `data/manifest.json` tem o formato `{"files": [{"path", "size_bytes", "sha256", "required", "rows"}]}`, com `path` relativo a `data/raw/` e `rows` como dicionário arquivo → linhas. `data/verify.py` lê o manifesto de forma genérica: confirmado que nada muda no script ao acrescentar entradas.
- `data/README.md` tem hoje a seção do CIRA; as seções do HKD e do combinado são desta tarefa.
- Resultado: `save_run(experiment="e6", track="dados", slice_name=<hkd | combinado | combinado_sem_replicas>, seed=SEED_FIEL, ...)`, com o SHA-256 do arquivo bruto lido do manifesto, como o script de E0 faz em `read_manifest_entry`.
- As 8.028 linhas com NaN do bloco abaixo estão confirmadas em `results/e0/dados/cira/seed42/metrics.json`, chave `nan_by_column`; a mediana de 34,1 s de `Duration` do malicioso do CIRA, em `estatisticas_descritivas.csv`.
- Em `tests/test_data.py` já existe o auxiliar `write_cira_zip`, que grava a fixture `synthetic_raw_csv` no formato do zip.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **Os passos 2 e 3 estão feitos.** Arquivos em `project/data/raw/hkd/` e `project/data/raw/combinado/`; tamanhos e SHA-256 na seção 1 de `docs/08-inventario-dados.md`.
- **Compatibilidade confirmada:** HKD e combinado têm as mesmas 35 colunas do CIRA, com os mesmos nomes e na mesma ordem. Sem NaN no HKD.
- **Leitura:** os CSVs do HKD e do combinado têm BOM (`encoding="utf-8-sig"`), `TimeStamp` no formato `2020/1/14 15:49` e números arredondados para 8 casas. Os atributos são lidos como numéricos sem conversão.
- **Resposta ao passo 5: o arquivo "aumentado" é replicação.** `Total-48h-Augmentation.csv` tem 5.258 linhas distintas, cada uma repetida exatamente 20 vezes. O HKD usado é `hkd/DoH-CSVs/DoH-CSVs-48h/Total-48h.csv`: 5.258 fluxos (dnstt 2.304, tcp-over-dns 1.502, tuns 1.452). As 5.258 distintas do aumentado são as do `Total-48h.csv` (confirmado: diferença máxima de 5 × 10⁻⁸); o script repete a conferência como asserção com tolerância.
- **Resposta ao passo 4:** as três classes do combinado saem de: linhas `NonDoH` de `l1` (897.493); linhas `Benign` de `l2` (19.807); todas as linhas de `l3` (354.996), que já trazem a ferramenta. Não é preciso alinhar `l2` com `l3`, e a ordem das linhas difere entre os arquivos. Origem: dns2tcp, dnscat2 e iodine são do CIRA; dnstt, tcp-over-dns e tuns, do HKD.
- **O combinado traz o HKD replicado 20 vezes** (105.160 linhas, 5.258 distintas). A carga grava três Parquets (decisões 36 e 40): `hkd.parquet`, `combinado.parquet`, como publicado, e `combinado_sem_replicas.parquet`, com cada fluxo do HKD uma vez (Malicious-DoH passa de 354.996 para 255.094 antes da limpeza).
- A mesma limpeza da tarefa 04 remove do combinado as mesmas 8.028 linhas do CIRA; nenhuma do HKD.
- Passo 7, já medido como referência (medianas, HKD contra malicioso do CIRA): `Duration` 120,1 s contra 34,1 s; `FlowBytesSent` 21.375 contra 1.807; `FlowBytesReceived` 21.724 contra 4.896; `PacketLengthMean` 148,6 contra 223,4.
- O HKD tem só duas máquinas (`192.168.11.12` e `.16`), capturas de 27/10 a 04/11/2021.
- `group` não se aplica ao HKD: todas as 5.258 linhas têm as duas máquinas locais, uma na origem e outra no destino (medido em 07/10/2026). O esquema do segundo dataset não tem `group` nem `time_window` (decisão 40).
- A justificativa da escolha (passo 8) precisa dizer que o combinado, como publicado, replica o HKD e por que a equipe avalia também sem as réplicas.
- Cluster, opcional (decisão 42): se a execução for no Apuana, os arquivos são copiados à mão para o Apuana e conferidos lá com `data/verify.py`; o `data/README.md` diz onde ficam no servidor `[Preencher: caminho]`.

## Arquivos

- `data/raw/hkd/`, `data/raw/combinado/` — arquivos baixados, fora do Git.
- `data/manifest.json` e `data/README.md` — acrescentar os novos arquivos (hashes no manifesto; origem e citação no README).
- `data/verify.py` — nada muda se ele lê o manifesto; conferir.
- `src/doh_ids/config.py` — nomes dos arquivos do segundo dataset e o mapa ferramenta → origem.
- `src/doh_ids/data.py` — acrescentar a carga do segundo dataset, reutilizando limpeza e seleção de atributos.
- `scripts/e6_dados.py` — novo: relatório de compatibilidade e contagens.
- `tests/test_data.py` — acrescentar T13-1, T13-2, T13-5 e T13-6.
- `docs/04-dados.md:82-115` — atualizado pelo agente `cin0114-doc-sync` no fechamento.

## O que fazer

1. (Download feito em 07/10/2026.) A carga e a tarefa 14 seguem assumindo a decisão 11 (decisão 39). Só a justificativa final (passo 8) e o texto do relatório esperam a resposta do professor a Q4. Se o combinado não for aceito como outro conjunto de dados, esta tarefa troca a fonte, a 14 roda de novo e a decisão 11 é reaberta com o usuário.
2. Baixar do repositório da Universidade de Hokkaido (`https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/88092`) o arquivo do HKD e o do combinado. Registrar nome, tamanho, SHA-256, condições de uso e a citação exigida, com a referência completa conferida na fonte (feito: está em `docs/04-dados.md`, seção do HKD).
3. Listar os CSVs de cada pacote e seus cabeçalhos. Comparar coluna a coluna com as 29 de `config.py`: nome, tipo e faixa de valores. Registrar diferenças.
4. Identificar no combinado quais linhas são do CIRA e quais são do HKD, e como as três classes se formam a partir dos arquivos de nível 1, 2 e 3. Conferir as contagens contra o README do dataset: Non-DoH 897.493, DoH normal 19.807, DoH suspeito 354.996; por ferramenta, dnstt 46.080, tcp-over-dns 30.040, tuns 29.040.
5. Verificar se o CSV aumentado (`Total-48h-Augmentation.csv`) é o que alimenta o combinado. Decidir e registrar qual arquivo do HKD será usado e por quê; se for o aumentado, isso vai para o relatório.
6. Carregar com a mesma função de limpeza da tarefa 04 e gravar `data/processed/hkd.parquet`, `data/processed/combinado.parquet` e `data/processed/combinado_sem_replicas.parquet`, todos com as 29 colunas, `label`, `origin` (CIRA ou HKD) e `tool` (decisão 40).
7. Comparar as distribuições dos principais atributos (duração, bytes, comprimento de pacote) entre os maliciosos do CIRA e os do HKD. Serve para interpretar o resultado da tarefa 14.
8. Escrever o parágrafo de justificativa da escolha, respondendo às perguntas da seção 6 da especificação: quais dados, por que escolhidos, o que representam.

## Por quê

Objetivo P2 e decisão 11. A especificação exige que a escolha do segundo dataset seja justificada no relatório, e a seção 6 pede as mesmas informações dos dois datasets. Sem conferir as colunas antes, o modelo pode rodar sobre atributos trocados sem acusar erro (risco R6).

## Evidência — verificada no baseline

- `docs/04-dados.md:84-98` — HKD: ferramentas, contagens, limitações.
- `docs/04-dados.md:100-104` — combinado: arquivos e contagens.
- `docs/04-dados.md:106-115` — avaliação dos dois e desenho proposto.
- `planejamento/MEMORY/01-discovery-stack.md`, "Downloads" — página do eprints lista arquivos de 209 MB e 485 MB e a nota "rights Reserved"; os repositórios GitHub só têm README.
- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:29` e `:93-94` — exigência de justificativa e de descrição do segundo dataset.

## Risco

- Q4 respondida com não: a tarefa muda de fonte. O resto (carga, conferência de colunas, justificativa) continua igual.
- Colunas com nomes ou unidades diferentes: mapear explicitamente em `config.py`; se faltar atributo, parar e reportar.
- O combinado inclui o CIRA sem a limpeza da tarefa 04: as contagens do README (897.493 / 19.807) são as brutas. Aplicar a mesma limpeza e registrar as contagens resultantes.
- Condições de uso pouco claras ("rights Reserved"): dados fora do Git e citação obrigatória; em dúvida, perguntar ao professor.

## Critério de aceite

- [ ] `data/README.md` e o manifesto cobrem os novos arquivos; `uv run python data/verify.py` passa.
- [ ] Relatório de compatibilidade em `results/e6/dados/<dataset>/seed42/` (um por Parquet): 29 colunas presentes, diferenças registradas; justificativa em `results/e6/dados/RESUMO.md`.
- [ ] Contagens por classe, por origem e por ferramenta gravadas e comparadas com o README do dataset.
- [ ] Os três Parquets existem e passam pelas asserções de 29 colunas, sem NaN, sem infinito e `label` em {0, 1, 2}; o esquema é 29 atributos + `label` + `origin` + `tool`.
- [ ] Parágrafo de justificativa escrito, sem afirmar nada que não esteja nos arquivos de resultado ou nas fontes citadas.
- [ ] `docs/04-dados.md` atualizado pelo `cin0114-doc-sync` no fechamento, sem `[A verificar]` nos itens resolvidos.

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script roda na própria sessão de implementação, nesta máquina, quando a tarefa chega ao ponto de executar (decisão 44); não se espera um integrante designado. O Apuana continua sendo opção (decisão 42). A evidência é a mesma: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e6_dados.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). A execução é feita com a árvore limpa (o plano em commit antes de rodar, porque `dirty` mede o repositório inteiro) e o resultado entra em commit `exp`. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão.

## Testes

Seção "Tarefa 13" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de dados: G1–G10, com G5 = `uv run python scripts/e6_dados.py`.
