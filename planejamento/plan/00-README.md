# Plano de implementação — índice

> **Onde fica o código:** o repositório Git do projeto é a pasta `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`, `.githooks/`, `.github/`) é relativo a `project/`, e todo comando `uv` e `git` roda lá dentro. `docs/`, `planejamento/`, `.claude/` e `CLAUDE.md` ficam na pasta de trabalho, fora do repositório, e não são versionados.

> **Validação (06/10/2026):** plano revisto por um agente independente em três passes (correção metodológica, implementabilidade, excesso de engenharia). Dezenove achados, nenhum crítico, seis altos; todos tratados e registrados em [../MEMORY/04-red-team.md](../MEMORY/04-red-team.md). Vinte e seis referências `arquivo:linha` conferidas, quatro corrigidas. Grafo sem ciclos. **Pronto para implementar**, com os bloqueios externos listados abaixo.

> **Revisão de 07/10/2026:** segunda revisão independente (27 achados: 4 altos, 17 médios, 6 baixos) mais revisão de cobertura dos requisitos do professor e de demonstrabilidade por entrega; 31 referências `arquivo:linha` corrigidas. Correções aplicadas nas tarefas, no plano de testes, no gate, nas regras e nos agentes; decisões 38 a 41 registradas; o que depende da equipe está em "Pendentes da equipe" de [../MEMORY/00-decisoes-travadas.md](../MEMORY/00-decisoes-travadas.md). O mapa requisito do professor → tarefa → artefato está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md). **Pronto para implementar a partir da tarefa 01.**

23 tarefas, organizadas por fluxo. Cada arquivo traz: onde, objetivo, dependências, **o que demonstra**, arquivos, o que fazer, por quê, evidência, risco, critério de aceite e verificação.

Os dados já foram baixados e inventariados: cada tarefa que os usa traz um bloco "Verificado nos dados", que prevalece sobre os passos escritos antes do download.

Antes de implementar qualquer tarefa: ler [../MEMORY/00-decisoes-travadas.md](../MEMORY/00-decisoes-travadas.md), [VERIFICACAO.md](VERIFICACAO.md) e a seção da tarefa em [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md). As regras de código, commit, teste e fluxo estão em `.claude/rules/`.

## Tarefas

| # | Fluxo | Tarefa | Objetivo da especificação | Depende de | Situação |
| --- | --- | --- | --- | --- | --- |
| [01](01-fundacao-repositorio-ambiente.md) | Fundação | Repositório e ambiente | — | — | a fazer |
| [02](02-fundacao-config-runlog.md) | Fundação | Configuração e registro de execução | — | 01 | a fazer |
| [03](03-dados-aquisicao-cira.md) | Dados | Aquisição do CIRA-CIC-DoHBrw-2020 | P1 | — (script: 01) | a fazer |
| [04](04-dados-carga-limpeza.md) | Dados | Carga, limpeza e reconciliação com a Tabela I (E0) | P1 | 02, 03 | a fazer |
| [05](05-dados-split-scaler.md) | Dados | Split, normalização e contagens | P1 | 04 | a fazer |
| [06](06-avaliacao-metricas.md) | Avaliação | Métricas e comparação com o artigo | P1 | 02 | a fazer |
| [07](07-reproducao-subconjuntos.md) | Reprodução | Três subconjuntos balanceados | P1 | 05 | a fazer |
| [08](08-reproducao-stacked-rf.md) | Reprodução | Balanced Stacked Random Forest (E1) | P1 | 06, 07 | a fazer |
| [09](09-reproducao-baselines.md) | Reprodução | Baselines do artigo (E2) | P1 | 05, 06, 08 | a fazer |
| [10](10-reproducao-sensibilidade.md) | Reprodução | Sensibilidade às ambiguidades (E3) | P1 | 08 | a fazer |
| [11](11-corrigido-protocolo.md) | Protocolo corrigido | Variância e comparação justa (E4) | P1, base de P3 | 08, 09 | a fazer |
| [12](12-xai-shap.md) | Explicabilidade | SHAP sobre os modelos base (E5) | P1 | 08 | a fazer |
| [13](13-dataset2-aquisicao.md) | Segundo dataset | Aquisição e compatibilidade | P2 | — (carga: 04) | a fazer |
| [14](14-dataset2-avaliacao.md) | Segundo dataset | Transferência e retreino (E6) | P2 | 08, 13 | a fazer |
| [15](15-p3-modificacao-m1-m2.md) | P3 | Modificação M1 + M2 (E8) | P3 | 11, 12, 14 | a fazer |
| [16](16-p3-robustez-duracao.md) | P3 | Robustez à duração, M3 — **cortável** | P3 | 12, 15 | a fazer |
| [17](17-entrega-tabelas-figuras.md) | Entrega | Tabelas e figuras por script | relatório | 08, 09, 12, 14 (10, 11, 15, 16 se feitas) | a fazer |
| [18](18-entrega-relatorio.md) | Entrega | Relatório | relatório | 17 (seções 1 a 4: nenhuma) | a fazer |
| [19](19-entrega-readme-execucao-limpa.md) | Entrega | README, execução limpa, checklist | GitHub | 17 (envio: 18) | a fazer |
| [20](20-entrega-slides-projeto.md) | Entrega | Slides do projeto — **só com P3** | apresentação | 15, 17 | a fazer |
| [21](21-condicional-ferramenta-tunel.md) | Condicional | Ferramenta de túnel (E7) — **só se Q5** | P1 | 08, 13 | bloqueada por Q5 |
| [22](22-padronizacao-doc-padrao.md) | Padronização | Registrar padrões (anti-recorrência) | — | 08, 11 | a fazer |
| [23](23-acompanhamento-professor.md) | Acompanhamento | Perguntas ao professor e material de 10/11 e 17/11 | — | — (material: 08) | a fazer |

## Grafo de dependência

Cada linha lê-se "X depende de Y".

```
01
02 ← 01
03                      (download: nada; script de conferência: 01)
04 ← 02, 03
05 ← 04
06 ← 02
07 ← 05
08 ← 06, 07
09 ← 05, 06, 08          (a 08 cria models.py)
10 ← 08
11 ← 08, 09
12 ← 08
13                      (download: nada; carga: 04)
14 ← 08, 13
15 ← 11, 12, 14
16 ← 12, 15
17 ← 08, 09, 12, 14     (opcionais: 10, 11, 15, 16)
18 ← 17                 (seções 1 a 4: nada)
19 ← 17                 (envio final: 18)
20 ← 15, 17
21 ← 08, 13             (e resposta a Q5)
22 ← 08, 11
23                      (material de 10/11: 08)
```

Sem ciclos. Caminho crítico do obrigatório: 01 → 02 → 04 → 05 → 07 → 08 → 14 → 17 → 18 → 19 (a parte de download de 03 e 13 já está feita). Com P3: … → 08 → 11 → 15 → 17 → 18 → 19. Tarefas que escrevem o mesmo arquivo (04 e 06 em `config.py`; 08 e 09 em `models.py`): a segunda a integrar faz rebase sobre a `main` antes do pull request.

## Ordem de execução

Dentro de uma onda as tarefas são independentes e podem ser divididas entre integrantes. Cada tarefa tem um dono `[Preencher: integrante]`, que roda o ciclo na própria máquina, com a própria identidade Git: é assim que o histórico fica com commits dos quatro (critério da tarefa 19).

| Onda | Tarefas | Janela proposta | Marco |
| --- | --- | --- | --- |
| 0 | 03 e 13 (só download e registro); 18 passo 1 (ler o template); 23 passo 1 (perguntas) | já, em paralelo com o seminário; perguntas até 13/10 | Dados na máquina; perguntas enviadas |
| 1 | 01 | até 21/10 | Ambiente reprodutível e primeiro commit |
| 2 | 02 e 03 (passos 2, 5 e 6), depois 04 e 06 em paralelo; 18 (seções 1 a 4) começa | 21/10 a 24/10 | Contagens reconciliadas com a Tabela I |
| 3 | 05, 07, 13 (carga) | 24/10 a 27/10 | Split conferido com a Fig. 4; segundo dataset carregado |
| 4 | 08, depois 09 (pode partir da branch da 08) | 27/10 a 30/10 | Primeira matriz de confusão ao lado da Fig. 4b |
| 5 | 10 (núcleo), 11, 12, 14 em paralelo | 30/10 a 09/11 | Reprodução fechada; P2 fechado |
| — | **09/11: decidir se P3 continua** | | |
| — | **10/11: acompanhamento com o professor**; primeira execução limpa | | Status de uma página e tabela de resultados |
| 6 | 15, 22; 17 começa | 10/11 a 13/11 | P3 medido |
| — | **13/11: experimentos congelados** | | Só correções a partir daqui |
| 7 | 16 parte A (se couber), 17, 18 (seções 5 a 8), 20 | 13/11 a 17/11 | Rascunho completo do relatório |
| — | **17/11: acompanhamento com o professor** | | |
| 8 | 19 (execução limpa final começa em 16/11) | até 18/11 | **Entrega: PDF e link do GitHub** |
| — | **19/11: apresentação (com P3)** | | |

As janelas são proposta; as datas em negrito são fixas ou marcos de corte. A janela mais apertada é a de 10/11 a 17/11: é ali que P3 e o relatório competem, e por isso a decisão de 09/11 existe.

## Onde roda (decisão 42)

Desenvolvimento e testes N1: máquina de cada integrante e CI. Execução com dados reais das tarefas 08 a 16 e execução limpa da 19: máquina local ou cluster Apuana, as duas valem; o importante é treinar e gerar a evidência (`results/`, `run.json` com a máquina, saída no pull request). Cada tarefa de experimento tem dois fechamentos, "pronta" e "executada" `[Preencher: quem desenvolve e quem executa, por tarefa]`.

## O que cortar, e em que ordem, se o prazo apertar

1. Parte B da tarefa 16; depois a 16 inteira.
2. Variantes opcionais da tarefa 10 (`oss`, `stacking_cv`, `meta_uniao`).
3. Avaliação por grupo da tarefa 11; gráficos de densidade da tarefa 04.
4. Tarefa 15 e, com ela, a 16 e a 20: P3 é opcional. Decisão em 09/11.
5. Tarefa 11, se P3 já tiver saído: a reprodução fecha sem ela, mas o relatório perde a discussão de variância.

O que não se corta: 01 a 09, 12, 13, 14, 17, 18, 19, 23. São P1, P2 e os entregáveis obrigatórios. Nenhum corte remove proteção contra vazamento de dados.

## Bloqueios externos

| Bloqueio | Trava | Enquanto não resolve |
| --- | --- | --- |
| Q1: reimplementação aceita como reprodução? | premissa do plano | seguir; as tarefas 01 a 07 valem em qualquer resposta |
| Q2: alvo e tolerância | texto da tarefa 18 | assumir Fig. 4b (decisão 10) |
| Q4: combinado conta como outro dataset? | justificativa da 13; texto da 14 no relatório | seguir assumindo a decisão 11: carregar (13) e rodar a 14; só a justificativa final e o texto do relatório esperam a resposta. Se for "não", a 13 troca a fonte e a 14 roda de novo (decisão 39) |
| Q5: ferramenta de túnel | 21 | não iniciar |
| Q6: painel | passo 9 da 12 | não construir |
| Q7: política de IA | — | **resolvido em 07/10/2026:** uso aprovado. Se o relatório precisa de uma frase de declaração, confirmar com o professor |
| Q9: idioma e limite de páginas | lista de tabelas da 17; texto da 18 | ler o template na onda 0 |
| Download do CIRA (formulário) | — | **resolvido em 07/10/2026:** os três datasets estão em `project/data/raw/`, inventariados em `docs/08-inventario-dados.md` |

## Como usar

- Uma tarefa por vez, pelo ciclo de `.claude/rules/fluxo-implementacao.md`: implementa, testa, revisa, integra. A skill `implementar NN` conduz o ciclo e chama o agente `implementador`.
- O que cada tarefa demonstra e como os requisitos do professor se distribuem está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md); a descrição de cada pull request segue o modelo criado na tarefa 01.
- Ao pegar uma tarefa: ler o arquivo inteiro e a seção dela no plano de testes, conferir que as dependências estão concluídas, seguir a skill `experimento` se for de E0 a E8.
- Ao concluir: passar pelo gate de `VERIFICACAO.md`, marcar a situação nesta tabela e pedir ao agente `cin0114-plan-sync` que reconcilie as tarefas seguintes com o que foi implementado.
- A tarefa seguinte não começa com a anterior vermelha (teste, lint ou achado bloqueante).
- Mudança de decisão travada: só com o usuário; registrar em `../MEMORY/00-decisoes-travadas.md`.
