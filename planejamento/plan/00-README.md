# Plano de implementação — índice

> **Onde fica o código (decisão 43):** o repositório Git é a raiz; o código fica em `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`) é relativo a `project/`, e os comandos `uv` rodam dentro dela. `.github/` e `.githooks/` ficam na raiz do repositório, porque o GitHub e o Git só os leem ali.

> **Validação (06/10/2026):** plano revisto por um agente independente em três passes (correção metodológica, implementabilidade, excesso de engenharia). Dezenove achados, nenhum crítico, seis altos; todos tratados e registrados em [../MEMORY/04-red-team.md](../MEMORY/04-red-team.md). Vinte e seis referências `arquivo:linha` conferidas, quatro corrigidas. Grafo sem ciclos.

> **Revisão de 07/10/2026:** segunda revisão independente (27 achados: 4 altos, 17 médios, 6 baixos) mais revisão de cobertura dos requisitos do professor e de demonstrabilidade por entrega; 31 referências `arquivo:linha` corrigidas. Decisões 38 a 41 registradas. O mapa requisito do professor → tarefa → artefato está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md).

> **Reconciliação de 07/10/2026, commit `360c3d3`:** tarefas 06, 07 e 08 prontas; respostas do professor a Q1 a Q6 e decisões 44 a 50 levadas às tarefas.

> **Reconciliação de 08/10/2026, commit `759ec29` (branch `tarefa/24-entregaveis`):** tarefas 09 a 17, 21 e 24 prontas e executadas com dados reais, e o complemento da 04 (Fig. 2); com a 24, as tarefas 18 e 20 estão cumpridas. Decisões 51 a 54 levadas às tarefas: os ⚠️ REVISAR das tarefas 11 e 15 e as pendências abertas pela decisão 45 estão resolvidos. **Nenhum ⚠️ REVISAR aberto.** Faltam: 19 (README e execução limpa), 22 (padrões) e 23 (acompanhamento), mais o que depende de pessoa, listado em "Bloqueios". Conferido nesta reconciliação: suíte inteira (110 testes verdes), lint, formatação, `data/verify.py`, `make_report_assets.py` em diretório temporário (tabelas idênticas às versionadas) e a compilação do relatório; nenhum experimento foi rodado de novo.

24 tarefas, organizadas por fluxo. Cada arquivo traz: onde, objetivo, dependências, **o que demonstra**, arquivos, o que fazer, por quê, evidência, risco, critério de aceite e verificação. As tarefas implementadas trazem um bloco "Como ficou", que prevalece sobre o resto do arquivo.

Antes de implementar qualquer tarefa: ler [../MEMORY/00-decisoes-travadas.md](../MEMORY/00-decisoes-travadas.md), [VERIFICACAO.md](VERIFICACAO.md) e a seção da tarefa em [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md). As regras de código, commit, teste e fluxo estão em `.claude/rules/`.

## Tarefas

"Pronta e executada" quer dizer: código, testes e revisão automática feitos, e o script rodado com os dados reais, com `run.json` de `dirty: false`. **Nenhuma tarefa foi integrada:** a `main` local e a `origin/main` estão em `6bf80bd`, e todo o trabalho está na cadeia de branches que termina em `tarefa/24-entregaveis`. A integração (G10) é de pessoa. O commit citado é o último que fechou a tarefa.

| # | Fluxo | Tarefa | Objetivo da especificação | Depende de | Situação |
| --- | --- | --- | --- | --- | --- |
| [01](01-fundacao-repositorio-ambiente.md) | Fundação | Repositório e ambiente | — | — | pronta em `5e11d56`; de pessoa: `push`, pull request de prova, CI verde no GitHub, proteção da `main`; licença pendente |
| [02](02-fundacao-config-runlog.md) | Fundação | Configuração e registro de execução | — | 01 | pronta em `b1434ab` (`dirty` em `ac360ba`; `N_JOBS` em `4746c22`; versões de scipy, matplotlib e do painel no `run.json` em `8f1d864`) |
| [03](03-dados-aquisicao-cira.md) | Dados | Aquisição do CIRA-CIC-DoHBrw-2020 | P1 | — (script: 01) | pronta e executada em `acc297a`; `data/verify.py` executado de novo em `759ec29`: 8 de 8 arquivos |
| [04](04-dados-carga-limpeza.md) | Dados | Carga, limpeza e reconciliação com a Tabela I (E0); Fig. 2 | P1 | 02, 03 | pronta e executada em `9e7563f`; **complemento da Fig. 2 pronto e executado em `39a7007`** (código `d45251e`, `44798f9`) |
| [05](05-dados-split-scaler.md) | Dados | Split, normalização e contagens | P1 | 04 | pronta e executada em `c262b2b` |
| [06](06-avaliacao-metricas.md) | Avaliação | Métricas e comparação com o artigo | P1 | 02 | pronta em `21171f4`; acrescida pelas tarefas 11, 14 e 21 |
| [07](07-reproducao-subconjuntos.md) | Reprodução | Três subconjuntos balanceados | P1 | 05 | pronta em `a4ba0e5`, executada dentro da 08 |
| [08](08-reproducao-stacked-rf.md) | Reprodução | Balanced Stacked Random Forest (E1), nas duas leituras de profundidade | P1 | 06, 07 | pronta e executada em `798ecd3`; `fit_system` e `cross_validated_confusion` foram para `src/doh_ids/system.py` em `472bb79`, sem mudar `results/e1/`; o G6 não tem registro de fechamento: a execução limpa da 19 o cobre |
| [09](09-reproducao-baselines.md) | Reprodução | Tabela II inteira: baselines (E2) e metade inferior | P1 | 05, 06, 08 | pronta e executada em `076fbe1`; metade inferior transcrita em `config.py`; **de pessoa: conferência por dois integrantes** |
| [10](10-reproducao-sensibilidade.md) | Reprodução | Sensibilidade às ambiguidades (E3) | P1 | 08 (o resumo lê a 11) | pronta e executada em `7b3ddaf`; resumo separado em `320a2a5`, refeito em `2313597`; `stacking_cv` e `oss` não feitas, declaradas |
| [11](11-corrigido-protocolo.md) | Protocolo corrigido | Variância e comparação justa (E4) | P1, base de P3 | 08, 09 | pronta e executada em `2a76a84`, dez seeds e quatro dobras por máquina; agregado refeito em `38809c1`; avisos de revisão resolvidos pela decisão 52 |
| [12](12-xai-shap.md) | Explicabilidade | SHAP sobre os modelos base (E5) e painel interativo | P1 | 08 (o script lê a etapa de dados da 13) | pronta e executada em `a0d853a`, refeita em `38809c1`; de pessoa: subir o painel na demonstração |
| [13](13-dataset2-aquisicao.md) | Segundo dataset | Aquisição e compatibilidade | P2 | — (carga: 04) | pronta e executada em `fa320d6`, refeita em `4253571` e `38809c1` |
| [14](14-dataset2-avaliacao.md) | Segundo dataset | P1 refeito no combinado sem réplicas; transferência e combinado publicado ao lado (E6) | P2 | 14a: 08, 13; 14b: 09, 12, 14a | 14a pronta e executada em `bc5e510`; 14b em `b32e4f8`; resumos refeitos em `38809c1` |
| [15](15-p3-modificacao-m1-m2.md) | P3 | Modificação M1 + M2 (E8) | P3 | 11, 12, 14 (basta a 14a) | pronta e executada em `713e650`, dez seeds nos dois datasets; análise posterior em `2313597`; passo de explicabilidade não feito, declarado (decisão 54f); aviso de revisão resolvido pelas decisões 52 e 54 |
| [16](16-p3-robustez-duracao.md) | P3 | Robustez à duração, M3 | P3 | 12, 15 | pronta e executada em `df16ca5`, partes A e B, dez seeds; leitura descritiva posterior em `2313597` |
| [17](17-entrega-tabelas-figuras.md) | Entrega | Tabelas e figuras por script | relatório | 08 a 16, 21 e a Fig. 2 | pronta e executada em `16b7f39`: 30 tabelas, 13 figuras e `report/INDICE.md` |
| [18](18-entrega-relatorio.md) | Entrega | Relatório | relatório | 17 | **cumprida pela 24**; resta, de pessoa: leitura cruzada, lista de conferência, DOI das referências, template no Overleaf com XeLaTeX |
| [19](19-entrega-readme-execucao-limpa.md) | Entrega | README, execução limpa, checklist | GitHub | 17 (envio: 24) | **a fazer; é a próxima.** Tarefa reescrita em `759ec29` com a ordem real dos 22 passos e os tempos medidos; execução limpa estimada em cerca de 9 horas |
| [20](20-entrega-slides-projeto.md) | Entrega | Slides do projeto | apresentação | 15, 17 | **cumprida pela 24**; resta, de pessoa: conferir no Google Slides, confirmar a divisão da fala, ensaio |
| [21](21-condicional-ferramenta-tunel.md) | Reprodução | Ferramenta de túnel (E7), Seção VI-D e Fig. 9 | P1 | 08, 13 (lê a etapa de dados da 13) | pronta e executada em `1a0e041`; resumo separado em `d86b0b5`, refeito em `38809c1` |
| [22](22-padronizacao-doc-padrao.md) | Padronização | Registrar padrões (anti-recorrência) | — | 08, 11 | concluída em 08/10/2026: sete padrões registrados em `.claude/rules/experimentos.md`, dois dispensados com motivo |
| [23](23-acompanhamento-professor.md) | Acompanhamento | Perguntas ao professor e material de 10/11 e 17/11 | — | — (material: 08) | página de status pronta em `docs/09-acompanhamento-professor.md` (08/10/2026); falta preencher a execução limpa e registrar o retorno dos encontros de 10/11 e 17/11, que são de pessoa |
| [24](24-entrega-pdfs-finais.md) | Entrega | Relatório em PDF e apresentação em PPTX, pelos modelos de `geracao_latex_and_pdf/` | relatório e slides | 17 | executada em `759ec29` pelo agente `gerador-entregaveis`: `relatorio.pdf` (8 páginas), `apresentacao.pptx` (14 slides), `roteiro.md` (11 min 55 s); revista pelo `revisor-de-texto` |
| [25](25-revisao-final-em-codigo.md) | Fechamento | Revisão final em código: rastro, recomputação, mutação e leitura, sem treinar | todos | 19 | a fazer; começa quando a execução limpa terminar |

## Grafo de dependência

Cada linha lê-se "X depende de Y". As arestas marcadas com "lê" foram acrescentadas em `759ec29`: são dependências de arquivo de `results/` que o código tem e o plano não previa.

```
01
02 ← 01
03                      (download: nada; script de conferência: 01)
04 ← 02, 03             (Fig. 2: só a 04)
05 ← 04
06 ← 02
07 ← 05
08 ← 06, 07
09 ← 05, 06, 08          (o resumo de E2 lê results/e1/)
10 ← 08                 (o resumo de E3 lê results/e4/corrigida/A/: roda depois da 11)
11 ← 08, 09
12 ← 08                 (e5_xai.py lê results/e6/dados/hkd/: roda depois da etapa de dados da 13)
13                      (download: nada; carga: 04)
14 ← 08, 13             (14a: 08, 13; 14b: 09, 12, 14a)
15 ← 11, 12, 14         (da 14, basta a 14a; o resumo de E8 lê os recortes "todos" da 16)
16 ← 12, 15
17 ← 08, 09, 10, 11, 12, 14, 15, 16, 21 e a Fig. 2
18 ← 17                 (cumprida pela 24)
19 ← 17                 (envio final: 24)
20 ← 15, 17             (cumprida pela 24)
21 ← 08, 13             (e7_ferramenta.py lê results/e6/dados/combinado_sem_replicas/)
22 ← 08, 11
23                      (material de 10/11: 08)
24 ← 17
```

Sem ciclos: as arestas novas vão de script de resumo para resultado de treino (10 → 11; 15 → 16) ou de treino para etapa de dados (12 → 13; 21 → 13), e nenhum treino lê resumo. A ordem de execução que respeita todas elas está na tarefa [19](19-entrega-readme-execucao-limpa.md), "Ordem real dos scripts".

## Ordem de execução

Cada tarefa tem um dono `[Preencher: integrante]`. A tabela de ondas abaixo é a proposta original; as datas em negrito são fixas ou marcos de corte e não mudaram.

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

Em 08/10/2026 as ondas 0 a 7 estão implementadas, antes das janelas: P3 foi feito (15 e 16), e a decisão de 09/11 já não tem o que cortar. As datas fixas seguem valendo como limite para o que resta.

### Ordem do que falta (08/10/2026)

| Ordem | Tarefa | Por que nesta posição | Antes de começar |
| --- | --- | --- | --- |
| 1 | 19 — README completo e execução limpa | todas as dependências prontas; a execução limpa é a primeira conferência de que o código atual regenera os resultados versionados (vários foram gerados antes de refatorações) | decidir, com o usuário, como comparar os dois agregados de E8, que guardam tempos (tarefa 19, "O que a execução limpa compara"); reservar cerca de 9 horas de máquina |
| 2 | 22 — padrões | depende de 08 e 11, prontas; faz mais sentido depois da 19, porque a execução limpa pode mostrar padrão que faltou | — |
| 3 | 23 — acompanhamento | corre em paralelo; os encontros são em 10/11 e 17/11 | página de status; o que levar ao professor está na tarefa |
| — | integração das branches (G10) | de pessoa; os pull requests entram na ordem das branches, da 01 à 24 | CI verde no GitHub (T01-5 ainda aberto) |

Se a execução limpa mostrar diferença em algum `metrics.json`, a fila para ali: é defeito da tarefa dona do script, corrigido no ciclo dela, e as tabelas, o relatório e os slides são regenerados depois.

## Onde roda (decisões 42 e 44)

Desenvolvimento e testes N1: máquina de quem implementa e CI. Execução com dados reais das tarefas 03 a 16 e da 21, e a execução limpa da 19: **na própria sessão de implementação, nesta máquina (decisão 44)**. O cluster Apuana continua sendo opção (decisão 42) e não foi usado: os 229 `run.json` versionados trazem a mesma máquina, com 10 núcleos. A evidência é a mesma: `results/`, `run.json` com a máquina e `dirty: false`, saída no pull request.

Custo medido, pela chave `timings` dos `run.json` (detalhe por script na tarefa 19): E1, 56 minutos; E4, 1 h 59 min; modificação de E8, 1 h 59 min; robustez de E8, 1 h 57 min; E6, 42 minutos (14a) e 31 minutos (14b); os demais, menos de 10 minutos cada. Soma de todos os treinos: 8 h 27 min. Nada foi cortado por custo; a seleção de hiperparâmetros de E8 usa 25% do treino de cada seed (decisão 54a), e isso é declarado.

## O que cortar, e em que ordem, se o prazo apertar

A lista original (parte B da 16; variantes opcionais da 10; avaliação por grupo da 11; 15, 16 e 20; 11) perdeu o objeto: tudo isso foi feito, salvo as variantes `stacking_cv` e `oss` da tarefa 10 e o passo de explicabilidade da tarefa 15, declarados como não feitos nos resumos.

Para o que resta, se o prazo apertar: (1) a tarefa 22 pode fechar com dispensa justificada de cada padrão; (2) a execução limpa pode ser repetida só nos scripts que mudarem depois da primeira. O que não se corta: a execução limpa completa pelo menos uma vez, o README com a ordem dos scripts e os itens de pessoa da entrega. Nenhum corte remove proteção contra vazamento de dados.

## Bloqueios

### O que depende de pessoa

| Item | Trava | Onde está descrito |
| --- | --- | --- |
| Integração das branches 01 a 24: `push`, pull requests na ordem, CI verde no GitHub, aprovação por outro integrante | "integrada" de todas as tarefas; T01-5 e T19-1 | `.claude/rules/fluxo-implementacao.md`, passo 6 |
| Metade inferior da Tabela II: conferência contra o artigo por dois integrantes | fechamento da 09 (T09-6); a tabela `tabela2_literatura` já está no relatório | tarefa 09 |
| Relatório: leitura cruzada; lista de conferência pergunta → seção; DOI de cada referência; template no Overleaf com XeLaTeX | envio da 19 | tarefas 18 e 24 |
| Apresentação: abrir o `.pptx` no Google Slides; confirmar a divisão da fala proposta em `roteiro.md`; ensaio cronometrado | 19/11 | tarefas 20 e 24 |
| Licença do repositório | `LICENSE` e a linha do README | tarefa 19; "Pendentes da equipe" |
| Commits dos quatro integrantes no histórico (`git shortlog -sn` mostra um autor em `759ec29`) | critério da 19 | tarefa 19 |
| Dono de cada tarefa | tabela de ondas | "Pendentes da equipe" |
| Painel: subir e abrir a página na demonstração | T12-7 | tarefa 12 |
| Amostragem de três números por tabela, no pull request da 17 | critério da 17 | tarefa 17 |

### Externos

| Bloqueio | Trava | Situação |
| --- | --- | --- |
| Q1: reimplementação aceita como reprodução? | — | respondida em 07/10/2026: sim, com o cuidado de a reprodução ser a mais fiel possível |
| Q2: alvo e tolerância | — | respondida; decisão 46. Não disse qual referência vale entre Tabela II e Fig. 4b: seguem as duas |
| Q3: requisito adicional | — | respondida; decisão 48: nenhum por ora |
| Q4: combinado conta como outro dataset? | — | respondida; decisão 47. As duas ressalvas (classes Non-DoH e benigna iguais às do CIRA; réplicas) não foram comentadas e vão ao acompanhamento (tarefa 23) |
| Q5: ferramenta de túnel | — | respondida com pedido de conversa; decisão 49: feita (tarefa 21). O método adotado vai ao acompanhamento |
| Q6: painel | — | respondida: não é necessário; decisão 50: implementado na tarefa 12 |
| Q7: política de IA | frase no README e no relatório, só se pedida | uso aprovado; a frase de declaração segue a confirmar |
| Q9: idioma e limite de páginas | — | sem resposta; a decisão 53 fixou português, alvo de 6 páginas e teto de 8. O relatório tem 8 |
| Q10: repositório público ou privado | envio da 19 | sem resposta; o repositório está público (decisão 43) |

## Pendências abertas pela decisão 45: resolvidas

Todas fechadas em 07/10/2026, pelas decisões 51, 52 e 54, e conferidas no código em `759ec29`. A seção fica como registro; nenhuma linha está aberta.

| Pendência | Resolvida por | Como ficou no código |
| --- | --- | --- |
| Como o caminho de `results/` nomeia a leitura de profundidade fora de E1 | decisão 51a | nas trilhas `fiel` e `variante`, a trilha nomeia a leitura (E5, E6, E7); na `corrigida`, o sufixo `-prof5` no recorte (E4, E8); em E3, sob `variante`, também o sufixo `-prof5` |
| O que o modelo B passa a ser | decisão 52 | `CORRIGIDA_MODELS`: A, A-prof5, B, B-prof5 e C |
| M1 e a grade de M2 | decisões 52 e 54 | `MODIFIED_GRID` com oito combinações; `M1` e `M1-prof5` |
| De que configuração partem as variantes de E3 | decisão 51d | das duas leituras: dez recortes |
| Leitura de profundidade, papéis das ferramentas e nomes de classe em E7 | decisão 51e | as duas leituras; papéis pelas contagens do treino; `evaluate` recebe os nomes das classes |
| Mover `fit_system` e `cross_validated_confusion` para o pacote | decisão 51b | `src/doh_ids/system.py`, em `472bb79` |
| Seed do embaralhamento do Non-DoH e do SMOTE do treino inteiro | decisão 51c | a seed da execução; `smote_seed(seed, N_SUBSETS)` |

## Como usar

- Uma tarefa por vez, pelo ciclo de `.claude/rules/fluxo-implementacao.md`: implementa, testa, revisa, integra. A skill `implementar NN` conduz o ciclo e chama o agente `implementador`.
- O que cada tarefa demonstra e como os requisitos do professor se distribuem está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md); a descrição de cada pull request segue o modelo criado na tarefa 01.
- Ao pegar uma tarefa: ler o arquivo inteiro e a seção dela no plano de testes, conferir que as dependências estão concluídas, seguir a skill `experimento` se for de E0 a E8.
- Script que importa outro script roda como módulo: `uv run python -m scripts.<nome>`. O comando de cada um está na docstring do script e na tarefa 19.
- Ao concluir: passar pelo gate de `VERIFICACAO.md`, marcar a situação nesta tabela e pedir ao agente `cin0114-plan-sync` que reconcilie as tarefas seguintes com o que foi implementado.
- A tarefa seguinte não começa com a anterior vermelha (teste, lint ou achado bloqueante).
- Mudança de decisão travada: só com o usuário; registrar em `../MEMORY/00-decisoes-travadas.md`.
