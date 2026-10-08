# 16 · P3 · robustez à manipulação de duração: M3 (extra, cortável)

**Onde:** `src/doh_ids/robustness.py`, `scripts/e8_robustez.py`, `tests/test_robustness.py`, `results/e8/corrigida/robustez-<variante>/`
**Objetivo:** medir quanto o detector degrada quando o atacante encurta os fluxos do túnel, e se uma versão sem os atributos manipuláveis resiste melhor.
**Depende de:** 12, 15
**Demonstra:** ablação sem `Duration` e curva de recall por fator de fragmentação. Extra de P3 (seções 5, 7 e 8).

> **Tarefa cortável.** É a primeira a sair se o prazo apertar (decisão 02). Só começa com a 15 fechada e o rascunho do relatório em andamento.

## Como ficou (conferido no código e em `results/` em `759ec29`, 08/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Suíte inteira executada em `759ec29`: 110 testes verdes em 41 s; `ruff check` e `ruff format --check` sem erro.

- **Situação: pronta e executada, partes A e B.** Hipótese e modelo de ameaça em `a544624`; `robustness.py` em `5be854b`; script em `1529734`; `7cb7158` (resumo); resultados em `df16ca5`; leitura descritiva posterior em `ad9a6f4` e `2313597`; teste em `5fed0ac`. Os 90 `run.json` trazem o commit `1529734` e `dirty: false` (lido).
- **Arquivos:** `src/doh_ids/robustness.py` (`kept_features`, `drop_features`, `fragment_malicious`), `src/doh_ids/config.py` (`ROBUSTNESS_MODELS`, `FRAGMENTATION_FACTORS`), `scripts/e8_robustez.py` (só treina e grava), `scripts/e8_robustez_resumo.py`, `tests/test_robustness.py`.
- **Comando real:** `uv run python -m scripts.e8_robustez` e, depois, `uv run python -m scripts.e8_robustez_resumo`. O treino importa os scripts de E4 e de E8, lê `cira.parquet`, `results/e4/corrigida/{A,A-prof5}/` e **`results/e8/corrigida/M1M2-cira/`** (os hiperparâmetros que a seleção já gravada escolheu em cada seed; não há nova seleção): roda depois de `e8_modificacao`. Confere por asserção que a matriz com todos os atributos é a da execução já gravada. Retomável por commit, como o script da modificação. Tempo medido: A 3.294 s, M1M2 2.552 s e A-prof5 1.154 s nos três conjuntos de colunas; 7.000 s, cerca de 2 horas.
- **Resultados:** `results/e8/corrigida/robustez-{A,A-prof5,M1M2}-{todos,sem_duration,sem_duration_taxas}/seed<0..9>/`, `summary-robustez.json`, `RESUMO-ROBUSTEZ.md` e `HIPOTESE-ROBUSTEZ.md`.
- **Desvios que ficaram:** fatores de fragmentação 1, 2, 4, 8 e 16 (a proposta mais o fator 1, que é o teste sem perturbação); o recorte é `robustez-<modelo>-<colunas>`; hipótese, resumo e agregado são arquivos próprios, com o sufixo `-ROBUSTEZ`, e não uma seção do `RESUMO.md` de E8; o modificado é o M1M2, e M1 não entrou. O resumo declara que nos fatores 8 e 16 a maior parte dos vetores perturbados é fisicamente incoerente.
- **`summary-robustez.json` traz tempos** (`fit_seconds`): não repete entre execuções; a comparação da execução limpa ignora a chave.
- **Pendente de pessoa:** a integração (G10).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- **Sistema base (decisão 45):** o "original" desta tarefa é o empilhado de profundidade variável; o de profundidade 5 entra ao lado onde o custo permitir. O "modificado" é o que sair da tarefa 15, que tem um ⚠️ REVISAR aberto.
- A ablação tira colunas da matriz normalizada antes de `balanced_subsets` e de `base_forests`, que aceitam qualquer número de colunas; a asserção de 29 colunas de `fit_system` (`scripts/e1_reproducao.py:103`) não vale para os modelos da ablação e não pode ser reaproveitada sem ajuste.
- **Custo estimado, sem cortar nada.** Parte A: original e modificado, duas ablações, dez seeds. Só o original são 20 ajustes do sistema inteiro: cerca de 65 minutos na profundidade variável (194 s por ajuste, medido na tarefa 08 com 29 colunas e a máquina carregada; com menos colunas o tempo deve cair, não medido), mais 37 minutos se a profundidade 5 for rodada ao lado. O modificado não foi medido. A parte B não treina modelo novo.
- **Ponto sem valor declarado:** o nome dos recortes `robustez-<variante>` com duas leituras de profundidade. Ver "Pendências abertas pela decisão 45" em `00-README.md`.
- Execução com dados reais na própria sessão (decisão 44).

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- Os três atributos da ablação têm estes nomes em `FEATURE_COLUMNS`: `Duration`, `FlowSentRate`, `FlowReceivedRate`.
- `feature_matrix` devolve sempre as 29 colunas e `fit_scaler` ajusta nas 29. A ablação (T16-1) seleciona o subconjunto de colunas depois; como o `MinMaxScaler` normaliza cada coluna em separado, ajustar nas 29 e descartar colunas dá o mesmo resultado que ajustar só nas que ficam.
- A matriz normalizada é um array sem nomes: a posição de cada coluna é a de `FEATURE_COLUMNS`.
- `save_run(experiment="e8", track="corrigida", slice_name="robustez-<variante>", seed=k, ...)`.
- `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45; não altera resultado, só o tempo.

## Arquivos

- `src/doh_ids/robustness.py` — novo: ablação de colunas e transformação de fragmentação.
- `scripts/e8_robustez.py` — novo.
- `tests/test_robustness.py` — novo (T16-1 a T16-3).
- `results/e8/corrigida/robustez-<variante>/seed<k>/` e a seção de robustez de `results/e8/corrigida/RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento`. Escrever primeiro o modelo de ameaça desta avaliação: o que o atacante controla (quando encerra e reabre a conexão do túnel), o que ele sabe (que a duração pesa na decisão, porque o artigo publicou isso), e o que ele não controla.
2. **Parte A, ablação, sem simular ataque.** Retreinar o original e o modificado sem `Duration`; depois sem `Duration` e sem as duas taxas (`FlowSentRate`, `FlowReceivedRate`), que são calculadas a partir dela. Avaliar em dados limpos, dez seeds. Responde: quanto do desempenho depende de um atributo que o atacante controla? Com 26 ou 24 colunas, `max_features=28` é aceito pelo scikit-learn 1.9.1 e equivale a usar todas as colunas (verificado em 07/10/2026); o resultado registra isso.
3. **Parte B, evasão aproximada — opcional dentro de uma tarefa já cortável.** A parte A responde à pergunta principal e pode ser entregue sozinha.
    Para os fluxos maliciosos do teste, simular a fragmentação de uma sessão em fluxos de duração menor: reduzir `Duration` e os bytes totais na mesma proporção, mantendo as taxas, e deixando as estatísticas por pacote como estão. Variar o fator de fragmentação (`[Decidir: fatores; proposta em "Pendentes da equipe"]`) e medir o recall de Malicious-DoH em cada ponto.
4. Declarar a simplificação da parte B por escrito: as estatísticas de comprimento e de tempo de pacote de um fluxo fragmentado de verdade mudariam, e aqui ficam fixas; o resultado é um limite aproximado, não a medição de um ataque real. Uma avaliação fiel exigiria regenerar o tráfego ou reprocessar os PCAPs com o DoHLyzer.
5. Comparar original e modificado, com e sem os atributos manipuláveis, na curva de recall por fator de fragmentação.
6. Relacionar com a importância SHAP de `Duration` medida na tarefa 12.

## Por quê

A crítica 10 do seminário diz que a explicação publicada indica ao atacante o que manipular, e que o artigo não avalia atacante adaptativo. Esta tarefa transforma a crítica em medida. É a parte do projeto que mais conversa com as aulas de ataques adversariais, e por isso vale como extra de P3.

## Evidência — verificada no baseline

- `docs/05-plano-experimental.md:118` e `:123` — M3 e a ressalva sobre perturbação válida de protocolo.
- `docs/02-artigo.md:120-134` — modelo de ameaça inferido: atacante não adaptativo.
- `docs/04-dados.md:57-58` — `Duration` e as taxas de fluxo como atributos.
- Manuscrito em `docs/referencias/`, legenda da Fig. 6 — limiar aparente de 40 segundos.

## Risco

- Apresentar a parte B como ataque real. A simplificação do passo 4 vai no resultado e no relatório, com essas palavras.
- A relação entre `Duration`, bytes e taxas no extrator pode não ser a que assumimos: conferir as definições no código do DoHLyzer antes de perturbar, e registrar a fonte.
- Consumir o tempo do relatório (risco R9): a parte A sozinha já responde à pergunta principal e pode ser entregue sem a parte B.

## Critério de aceite

- [x] Modelo de ameaça da avaliação escrito antes dos resultados. Lido: seção "Modelo de ameaça desta avaliação" em `HIPOTESE-ROBUSTEZ.md:31`, no commit `a544624`, anterior a `1529734` (commit dos `run.json`) e a `df16ca5`.
- [x] Parte A: métricas com e sem os atributos manipuláveis, dez seeds, original e modificado. Lido: `column_sets` com `todos`, `sem_duration` e `sem_duration_taxas`; `models` com A, A-prof5 e M1M2; `seeds` de 0 a 9; `models_not_run` vazio.
- [x] Parte B: curva de recall por fator de fragmentação, ou dispensa registrada com o motivo. Lido: `factors` e `perturbation` no `summary-robustez.json`; `report/figures/robustez_fragmentacao.pdf`.
- [x] A simplificação está declarada no arquivo de resultado. Lido: `RESUMO-ROBUSTEZ.md:9-13`.
- [ ] Nenhuma frase do resumo chama a parte B de ataque adversarial sem a ressalva (revisor metodológico). Informado pela sessão principal como revisto; sem artefato da revisão para conferir aqui.

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script roda na própria sessão de implementação, nesta máquina, quando a tarefa chega ao ponto de executar (decisão 44); não se espera um integrante designado. O Apuana continua sendo opção (decisão 42). A evidência é a mesma: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e8_robustez.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). A execução é feita com a árvore limpa (o plano em commit antes de rodar, porque `dirty` mede o repositório inteiro) e o resultado entra em commit `exp`. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão.

## Testes

Seção "Tarefa 16" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python -m scripts.e8_robustez` e, depois, `uv run python -m scripts.e8_robustez_resumo`.
