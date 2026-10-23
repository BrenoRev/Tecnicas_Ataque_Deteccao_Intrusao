# Plano de implementação — índice

> **Onde fica o código (decisão 43):** o repositório Git é a raiz; o código fica em `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`) é relativo a `project/`, e os comandos `uv` rodam dentro dela. `.github/` e `.githooks/` ficam na raiz do repositório, porque o GitHub e o Git só os leem ali.

> **Validação (06/10/2026):** plano revisto por um agente independente em três passes (correção metodológica, implementabilidade, excesso de engenharia). Dezenove achados, nenhum crítico, seis altos; todos tratados e registrados em [../MEMORY/04-red-team.md](../MEMORY/04-red-team.md). Vinte e seis referências `arquivo:linha` conferidas, quatro corrigidas. Grafo sem ciclos. **Pronto para implementar**, com os bloqueios externos listados abaixo.

> **Revisão de 07/10/2026:** segunda revisão independente (27 achados: 4 altos, 17 médios, 6 baixos) mais revisão de cobertura dos requisitos do professor e de demonstrabilidade por entrega; 31 referências `arquivo:linha` corrigidas. Correções aplicadas nas tarefas, no plano de testes, no gate, nas regras e nos agentes; decisões 38 a 41 registradas; o que depende da equipe está em "Pendentes da equipe" de [../MEMORY/00-decisoes-travadas.md](../MEMORY/00-decisoes-travadas.md). O mapa requisito do professor → tarefa → artefato está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md). **Pronto para implementar a partir da tarefa 01.**

> **Reconciliação de 07/10/2026, commit `360c3d3`:** tarefas 06, 07 e 08 prontas (a 08 executada com dados reais, nas duas leituras de profundidade); respostas do professor a Q1 a Q6 e decisões 44 a 50 levadas às tarefas. Mudanças de escopo: sistema base das tarefas seguintes é a variante de profundidade variável (45); todas as tabelas e gráficos do artigo são alvo, com a Fig. 2 e a metade inferior da Tabela II obrigatórias (46); P2 refaz P1 no combinado sem réplicas, e a tarefa 14 ganhou as partes 14a e 14b (47); a tarefa 21 deixou de ser condicional (49); a tarefa 12 ganhou o painel (50); os experimentos rodam na sessão de implementação (44). ⚠️ REVISAR abertos: dois na tarefa 11 e um na 15; pontos sem valor declarado em "Pendências abertas pela decisão 45".

23 tarefas, organizadas por fluxo. Cada arquivo traz: onde, objetivo, dependências, **o que demonstra**, arquivos, o que fazer, por quê, evidência, risco, critério de aceite e verificação.

Os dados já foram baixados e inventariados: cada tarefa que os usa traz um bloco "Verificado nos dados", que prevalece sobre os passos escritos antes do download.

Antes de implementar qualquer tarefa: ler [../MEMORY/00-decisoes-travadas.md](../MEMORY/00-decisoes-travadas.md), [VERIFICACAO.md](VERIFICACAO.md) e a seção da tarefa em [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md). As regras de código, commit, teste e fluxo estão em `.claude/rules/`.

## Tarefas

| # | Fluxo | Tarefa | Objetivo da especificação | Depende de | Situação |
| --- | --- | --- | --- | --- | --- |
| [01](01-fundacao-repositorio-ambiente.md) | Fundação | Repositório e ambiente | — | — | pronta em `5e11d56` (branch `tarefa/01-prova-ci`); aguarda integração por pessoa: `push`, pull request de prova, CI verde, proteção da `main`; licença pendente |
| [02](02-fundacao-config-runlog.md) | Fundação | Configuração e registro de execução | — | 01 | pronta em `b1434ab` (branch `tarefa/02-config-runlog`); aguarda integração por pessoa; passo 5a fechado (`N_JOBS = -1` em `4746c22`, decisão 45) |
| [03](03-dados-aquisicao-cira.md) | Dados | Aquisição do CIRA-CIC-DoHBrw-2020 | P1 | — (script: 01) | pronta e executada em `acc297a` (branch `tarefa/03-dados-cira`); aguarda integração por pessoa; ⚠️ REVISAR de `5e11d56` resolvido (zips repostos) |
| [04](04-dados-carga-limpeza.md) | Dados | Carga, limpeza e reconciliação com a Tabela I (E0) | P1 | 02, 03 | pronta e executada em `9e7563f` (branch `tarefa/04-carga-limpeza`); aguarda integração por pessoa; `docs/04-dados.md` a atualizar pelo `cin0114-doc-sync`; **complemento aberto: Fig. 2 (decisão 46)**, a fazer |
| [05](05-dados-split-scaler.md) | Dados | Split, normalização e contagens | P1 | 04 | pronta e executada em `0ae2d49` (branch `tarefa/05-split-scaler`); aguarda integração por pessoa |
| [06](06-avaliacao-metricas.md) | Avaliação | Métricas e comparação com o artigo | P1 | 02 | pronta em `21171f4` (branch `tarefa/06-avaliacao-metricas`); aguarda integração por pessoa; metade inferior da Tabela II passou para a 09 |
| [07](07-reproducao-subconjuntos.md) | Reprodução | Três subconjuntos balanceados | P1 | 05 | pronta em `a4ba0e5` (branch `tarefa/07-subconjuntos`), executada dentro da 08; aguarda integração por pessoa |
| [08](08-reproducao-stacked-rf.md) | Reprodução | Balanced Stacked Random Forest (E1), nas duas leituras de profundidade | P1 | 06, 07 | pronta e executada em `798ecd3` (branch `tarefa/08-stacked-rf`); G6 em aberto (segunda execução rodando em 07/10/2026); aguarda integração por pessoa |
| [09](09-reproducao-baselines.md) | Reprodução | Tabela II inteira: baselines (E2) e metade inferior | P1 | 05, 06, 08 | a fazer; para fechar, a metade inferior copiada do artigo e conferida por dois integrantes |
| [10](10-reproducao-sensibilidade.md) | Reprodução | Sensibilidade às ambiguidades (E3) | P1 | 08 | a fazer; configuração de partida a confirmar com o usuário |
| [11](11-corrigido-protocolo.md) | Protocolo corrigido | Variância e comparação justa (E4) | P1, base de P3 | 08, 09 | a fazer; ⚠️ REVISAR: o caminho `fold<k>` do passo 9 sai do layout de `save_run`, e a decisão 45 muda o modelo A sem dizer o que B passa a ser |
| [12](12-xai-shap.md) | Explicabilidade | SHAP sobre os modelos base (E5) e painel interativo | P1 | 08 | a fazer |
| [13](13-dataset2-aquisicao.md) | Segundo dataset | Aquisição e compatibilidade | P2 | — (carga: 04) | a fazer |
| [14](14-dataset2-avaliacao.md) | Segundo dataset | P1 refeito no combinado sem réplicas; transferência e combinado publicado ao lado (E6) | P2 | 14a: 08, 13; 14b: 09, 12, 14a | a fazer |
| [15](15-p3-modificacao-m1-m2.md) | P3 | Modificação M1 + M2 (E8) | P3 | 11, 12, 14 (basta a 14a) | a fazer; ⚠️ REVISAR: M1 e a grade diante da decisão 45 |
| [16](16-p3-robustez-duracao.md) | P3 | Robustez à duração, M3 — **cortável** | P3 | 12, 15 | a fazer |
| [17](17-entrega-tabelas-figuras.md) | Entrega | Tabelas e figuras por script | relatório | 08, 09, 12, 14, 21, complemento da 04 (10, 11, 15, 16 se feitas) | a fazer |
| [18](18-entrega-relatorio.md) | Entrega | Relatório | relatório | 17 (seções 1 a 4: nenhuma) | a fazer |
| [19](19-entrega-readme-execucao-limpa.md) | Entrega | README, execução limpa, checklist | GitHub | 17 (envio: 18) | a fazer |
| [20](20-entrega-slides-projeto.md) | Entrega | Slides do projeto — **só com P3** | apresentação | 15, 17 | a fazer |
| [21](21-condicional-ferramenta-tunel.md) | Reprodução | Ferramenta de túnel (E7), Seção VI-D e Fig. 9 | P1 | 08, 13 | a fazer; obrigatória desde a decisão 49; três pontos sem valor declarado no arquivo |
| [22](22-padronizacao-doc-padrao.md) | Padronização | Registrar padrões (anti-recorrência) | — | 08, 11 | a fazer |
| [23](23-acompanhamento-professor.md) | Acompanhamento | Perguntas ao professor e material de 10/11 e 17/11 | — | — (material: 08) | em andamento: perguntas enviadas e Q1 a Q6 respondidas em 07/10/2026; Q9, Q10 e parte de Q7 sem resposta |
| [24](24-entrega-pdfs-finais.md) | Entrega | Relatório em PDF e apresentação em PPTX, pelos modelos de `geracao_latex_and_pdf/` | relatório e slides | 17 (e 15, 16 se feitas) | a fazer; última tarefa; executada pelo agente `gerador-entregaveis`; cumpre as tarefas 18 e 20 |

## Grafo de dependência

Cada linha lê-se "X depende de Y".

```
01
02 ← 01
03                      (download: nada; script de conferência: 01)
04 ← 02, 03             (complemento Fig. 2: só a 04; antes da 17)
05 ← 04
06 ← 02
07 ← 05
08 ← 06, 07
09 ← 05, 06, 08          (a 08 cria models.py)
10 ← 08
11 ← 08, 09
12 ← 08
13                      (download: nada; carga: 04)
14 ← 08, 13             (14a: 08, 13; 14b: 09, 12, 14a)
15 ← 11, 12, 14         (da 14, basta a 14a)
16 ← 12, 15
17 ← 08, 09, 12, 14, 21 (e a Fig. 2, complemento da 04; opcionais: 10, 11, 15, 16)
18 ← 17                 (seções 1 a 4: nada)
19 ← 17                 (envio final: 18)
20 ← 15, 17
21 ← 08, 13             (obrigatória, decisão 49; na ordem, depois da 14)
22 ← 08, 11
23                      (material de 10/11: 08)
```

Sem ciclos (conferido de novo em 07/10/2026 com as arestas novas: 14b ← 09, 12, 14a; 17 ← 21). Caminho crítico do obrigatório: 01 → 02 → 04 → 05 → 07 → 08 → 09 → 14 (14a, depois 14b, que também espera a 12) → 21 (depende só de 08 e 13; vem depois da 14 pela ordem) → 17 → 18 → 19 (a parte de download de 03 e 13 já está feita; 01 a 08 prontas). Com P3: … → 09 → 11 → 15 → 17 → 18 → 19. Tarefas que escrevem o mesmo arquivo (04 e 06 em `config.py`; 08 e 09 em `models.py`): a segunda a integrar faz rebase sobre a `main` antes do pull request.

## Ordem de execução

Dentro de uma onda as tarefas são independentes e podem ser divididas entre integrantes. Cada tarefa tem um dono `[Preencher: integrante]`, que roda o ciclo na própria máquina, com a própria identidade Git: é assim que o histórico fica com commits dos quatro (critério da tarefa 19).

| Onda | Tarefas | Janela proposta | Marco |
| --- | --- | --- | --- |
| 0 | 03 e 13 (só download e registro); 18 passo 1 (ler o template); 23 passo 1 (perguntas) | já, em paralelo com o seminário; perguntas até 13/10 | Dados na máquina; perguntas enviadas |
| 1 | 01 | até 21/10 | Ambiente reprodutível e primeiro commit |
| 2 | 02 e 03 (passos 2, 5 e 6), depois 04 e 06 em paralelo; 18 (seções 1 a 4) começa | 21/10 a 24/10 | Contagens reconciliadas com a Tabela I |
| 3 | 05, 07, 13 (carga) | 24/10 a 27/10 | Split conferido com a Fig. 4; segundo dataset carregado |
| 4 | 08, depois 09 (pode partir da branch da 08) | 27/10 a 30/10 | Primeira matriz de confusão ao lado da Fig. 4b |
| 5 | 10 (núcleo), 11, 12, 14 (14a e 14b), depois 21; complemento da 04 (Fig. 2) | 30/10 a 09/11 | Reprodução fechada; P2 fechado |
| — | **09/11: decidir se P3 continua** | | |
| — | **10/11: acompanhamento com o professor**; primeira execução limpa | | Status de uma página e tabela de resultados |
| 6 | 15, 22; 17 começa | 10/11 a 13/11 | P3 medido |
| — | **13/11: experimentos congelados** | | Só correções a partir daqui |
| 7 | 16 parte A (se couber), 17, 18 (seções 5 a 8), 20 | 13/11 a 17/11 | Rascunho completo do relatório |
| — | **17/11: acompanhamento com o professor** | | |
| 8 | 19 (execução limpa final começa em 16/11) | até 18/11 | **Entrega: PDF e link do GitHub** |
| — | **19/11: apresentação (com P3)** | | |

As janelas são proposta; as datas em negrito são fixas ou marcos de corte. A janela mais apertada é a de 10/11 a 17/11: é ali que P3 e o relatório competem, e por isso a decisão de 09/11 existe.

### Ordem das tarefas que faltam (07/10/2026)

Em 07/10/2026 as tarefas 01 a 08 estão prontas, antes da janela proposta. A execução acontece na sessão de implementação, uma tarefa por vez (decisão 44), em branches encadeadas a partir de `tarefa/08-stacked-rf`, porque nenhuma foi integrada. A ordem abaixo respeita o grafo e põe primeiro o que é obrigatório; as datas fixas da tabela acima não mudam.

| Ordem | Tarefa | Por que nesta posição | Antes de começar |
| --- | --- | --- | --- |
| 1 | 09 — Tabela II (baselines) | só depende do que está pronto; a 11 e a 14b esperam por ela | seed do SMOTE do treino inteiro (usuário); a metade inferior só bloqueia o fechamento |
| 2 | 04, complemento — Fig. 2 | não depende de modelo; a 17 espera por ela | — |
| 3 | 13 — segundo dataset, carga | a 14 e a 21 esperam por ela | — |
| 4 | 12 — SHAP e painel | a 14b e a 15 esperam por ela | tamanho da amostra do SHAP; nome do script e base do painel |
| 5 | 14a — sistema no combinado sem réplicas, transferência, publicado | P2 | nome dos recortes de `results/e6/` |
| 6 | 14b — baselines e SHAP no combinado sem réplicas | fecha P2 | o mesmo |
| 7 | 21 — ferramenta de túnel | decisão 49: depois da 14 | papel de cada ferramenta, leitura de profundidade, caminho, avaliação com nomes de classe |
| 8 | 10 — sensibilidade (núcleo) | fecha a reprodução | configuração de partida |
| 9 | 11 — protocolo corrigido | base de P3; depende de resultado real da 08 e da 09 | os dois ⚠️ REVISAR; prevalências |
| — | 09/11: decidir se P3 continua | | |
| 10 | 15 — M1 + M2 | P3 | ⚠️ REVISAR; grade; fração da subamostra |
| 11 | 22 — padrões | depende de 08 e 11 | — |
| 12 | 16 — robustez (cortável) | depende de 12 e 15 | fatores de fragmentação |
| 13 | 17 — tabelas e figuras | depende de 08, 09, 12, 14, 21 e da Fig. 2 | Q9 |
| 14 | 18 — relatório (seções 5 a 8) | depende da 17 | — |
| 15 | 19 — README e execução limpa | depende da 17; envio depois da 18 | licença; Q10 |
| 16 | 20 — slides (só com P3) | depende de 15 e 17 | — |

Em paralelo, sem bloquear a fila: 18 (passo 1 e seções 1 a 4) e 23. A integração por pessoa das tarefas 01 a 08 (G10) também corre em paralelo; os pull requests entram na ordem das branches.

## Onde roda (decisões 42 e 44)

Desenvolvimento e testes N1: máquina de quem implementa e CI. Execução com dados reais das tarefas 03 a 16 e da 21, e a execução limpa da 19: **na própria sessão de implementação, nesta máquina (decisão 44)**; quando a tarefa chega ao ponto de executar, o script roda ali e o resultado entra em commit `exp`, sem esperar um integrante designado. O cluster Apuana continua sendo opção (decisão 42). A evidência é a mesma: `results/`, `run.json` com a máquina e `dirty: false`, saída no pull request. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão. A integração (G10) continua sendo de uma pessoa.

Custo medido até aqui, na tarefa 08 (10 núcleos; máquina carregada na segunda leitura): um ajuste do sistema inteiro leva 112 s com profundidade 5 e 194 s sem limite de profundidade; a validação cruzada de 10 folds, 785 s e 2.270 s. Cada tarefa seguinte traz a estimativa de custo no seu bloco de reconciliação; nada foi cortado por custo.

## O que cortar, e em que ordem, se o prazo apertar

1. Parte B da tarefa 16; depois a 16 inteira.
2. Variantes opcionais da tarefa 10 (`oss`, `stacking_cv`, `meta_uniao`).
3. Avaliação por grupo da tarefa 11. (Os gráficos de densidade da tarefa 04 saíram desta lista: a Fig. 2 é alvo de P1 desde a decisão 46.)
4. Tarefa 15 e, com ela, a 16 e a 20: P3 é opcional. Decisão em 09/11.
5. Tarefa 11, se P3 já tiver saído: a reprodução fecha sem ela, mas o relatório perde a discussão de variância.

O que não se corta: 01 a 09, 12, 13, 14 (14a e 14b), 17, 18, 19, 21, 23 e a Fig. 2 (complemento da 04). São P1, P2 e os entregáveis obrigatórios; a 21 entrou com a decisão 49. O painel da tarefa 12 foi decidido pela equipe (decisão 50) e o professor disse que não é necessário: tirá-lo, se o prazo apertar, é decisão do usuário, não desta lista. Nenhum corte remove proteção contra vazamento de dados.

## Bloqueios externos

| Bloqueio | Trava | Enquanto não resolve |
| --- | --- | --- |
| Q1: reimplementação aceita como reprodução? | — | **respondida em 07/10/2026:** sim, com o cuidado de a reprodução ser a mais fiel possível |
| Q2: alvo e tolerância | — | **respondida em 07/10/2026; decisão 46:** todas as tabelas e gráficos de resultado; pequenas diferenças aceitáveis. Não disse qual referência vale entre Tabela II e Fig. 4b: seguem as duas |
| Q3: requisito adicional | — | **respondida em 07/10/2026; decisão 48:** nenhum por ora |
| Q4: combinado conta como outro dataset? | — | **respondida em 07/10/2026; decisão 47:** refazer tudo no outro dataset; feito no combinado sem réplicas. O professor não comentou as duas ressalvas (classes Non-DoH e benigna iguais às do CIRA; réplicas): ficam declaradas e vão ao acompanhamento (tarefa 23) |
| Q5: ferramenta de túnel | — | **respondida em 07/10/2026** com pedido de conversa; **decisão 49:** a equipe faz sem esperar. A tarefa 21 é obrigatória |
| Q6: painel | — | **respondida em 07/10/2026:** não é necessário; **decisão 50:** a equipe implementa, na tarefa 12 |
| Q7: política de IA | — | **resolvido em 07/10/2026:** uso aprovado. Se o relatório precisa de uma frase de declaração, confirmar com o professor |
| Q9: idioma e limite de páginas | lista de tabelas da 17; texto da 18 | ler o template na onda 0 |
| Q10: repositório público ou privado | envio da 19 | sem resposta; o repositório está público (decisão 43) |
| Metade inferior da Tabela II: copiar do artigo e conferir por dois integrantes | fechamento da 09; tabela da 17 | começar a 09 sem ela |
| Download do CIRA (formulário) | — | **resolvido em 07/10/2026:** os três datasets estão em `project/data/raw/`, inventariados em `docs/08-inventario-dados.md` |

## Pendências abertas pela decisão 45 (07/10/2026)

São do usuário; o implementador não escolhe. Cada uma é resolvida antes da primeira tarefa que precisa dela.

| Pendência | Onde aparece | Precisa estar decidida antes de |
| --- | --- | --- |
| **Como o caminho de `results/` nomeia a leitura de profundidade fora de E1.** Em E1 ficou `fiel/proposto` e `variante/profundidade_variavel`, e a tarefa 12 segue o mesmo padrão. Onde o recorte já nomeia cenário ou modelo (E4: `<modelo>`; E6: `transferencia`, `retreino_publicado`, `retreino_sem_replicas`; E8: `<modelo>-<dataset>`, `robustez-<variante>`), a decisão 38 não diz onde entra a leitura, nem lista recortes para os baselines e o SHAP no combinado (14b) ou para E7. Proposta, a confirmar: em E6 e E7 a trilha diz a leitura (`fiel` para profundidade 5, `variante` para profundidade variável) e o recorte continua nomeando o cenário ou o modelo; em E4 e E8, cuja trilha é `corrigida`, a leitura entra no nome do recorte. A decisão 38 ganha o adendo | 11, 14, 15, 16, 21 | 14a |
| ⚠️ REVISAR: o que o modelo B (decisão 23) passa a ser quando A não tem limite de profundidade | 11 | 11 |
| ⚠️ REVISAR: M1 e a grade de M2 (decisão 25) diante do A de profundidade variável | 15 | 15 |
| De que configuração partem as variantes de E3 | 10 | 10 |
| Leitura de profundidade, papel de cada ferramenta nos subconjuntos e avaliação com nomes de classe próprios em E7 | 21 | 21 |
| Mover `fit_system` e `cross_validated_confusion` de `scripts/e1_reproducao.py` para o pacote, o que toca arquivos fora da lista da tarefa que fizer | 10, 11, 12, 14, 15, 16, 21 | a primeira que ajustar o sistema inteiro (12 ou 14a) |
| Seed do embaralhamento do Non-DoH: o código usa a seed da execução; nenhuma decisão registra | 07 | — (confirmar e registrar) |
| Seed do SMOTE do treino inteiro dos baselines | 09 | 09 |

## Como usar

- Uma tarefa por vez, pelo ciclo de `.claude/rules/fluxo-implementacao.md`: implementa, testa, revisa, integra. A skill `implementar NN` conduz o ciclo e chama o agente `implementador`.
- O que cada tarefa demonstra e como os requisitos do professor se distribuem está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md); a descrição de cada pull request segue o modelo criado na tarefa 01.
- Ao pegar uma tarefa: ler o arquivo inteiro e a seção dela no plano de testes, conferir que as dependências estão concluídas, seguir a skill `experimento` se for de E0 a E8.
- Ao concluir: passar pelo gate de `VERIFICACAO.md`, marcar a situação nesta tabela e pedir ao agente `cin0114-plan-sync` que reconcilie as tarefas seguintes com o que foi implementado.
- A tarefa seguinte não começa com a anterior vermelha (teste, lint ou achado bloqueante).
- Mudança de decisão travada: só com o usuário; registrar em `../MEMORY/00-decisoes-travadas.md`.
