# 16 · P3 · robustez à manipulação de duração: M3 (extra, cortável)

**Onde:** `src/doh_ids/robustness.py`, `scripts/e8_robustez.py`, `tests/test_robustness.py`, `results/e8/corrigida/robustez-<variante>/`
**Objetivo:** medir quanto o detector degrada quando o atacante encurta os fluxos do túnel, e se uma versão sem os atributos manipuláveis resiste melhor.
**Depende de:** 12, 15
**Demonstra:** ablação sem `Duration` e curva de recall por fator de fragmentação. Extra de P3 (seções 5, 7 e 8).

> **Tarefa cortável.** É a primeira a sair se o prazo apertar (decisão 02). Só começa com a 15 fechada e o rascunho do relatório em andamento.

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- Os três atributos da ablação têm estes nomes em `FEATURE_COLUMNS`: `Duration`, `FlowSentRate`, `FlowReceivedRate`.
- `feature_matrix` devolve sempre as 29 colunas e `fit_scaler` ajusta nas 29. A ablação (T16-1) seleciona o subconjunto de colunas depois; como o `MinMaxScaler` normaliza cada coluna em separado, ajustar nas 29 e descartar colunas dá o mesmo resultado que ajustar só nas que ficam.
- A matriz normalizada é um array sem nomes: a posição de cada coluna é a de `FEATURE_COLUMNS`.
- `save_run(experiment="e8", track="corrigida", slice_name="robustez-<variante>", seed=k, ...)`.
- `N_JOBS` não existe em `config.py` (pendência da equipe; ver o bloqueio no topo da tarefa 08).

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

- [ ] Modelo de ameaça da avaliação escrito antes dos resultados.
- [ ] Parte A: métricas com e sem os atributos manipuláveis, dez seeds, original e modificado.
- [ ] Parte B: curva de recall por fator de fragmentação, ou dispensa registrada com o motivo.
- [ ] A simplificação está declarada no arquivo de resultado.
- [ ] Nenhuma frase do resumo chama a parte B de ataque adversarial sem a ressalva (revisor metodológico).

## Execução com dados reais: local ou Apuana (decisão 42)

O script roda na máquina de quem tem os dados ou no cluster Apuana; as duas formas valem. O que importa é treinar e deixar a evidência: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e8_robustez.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). Quem executa roda com a árvore limpa e faz o commit `exp`. A tarefa fica "pronta" sem isso e "executada" com isso.

## Testes

Seção "Tarefa 16" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e8_robustez.py`.
