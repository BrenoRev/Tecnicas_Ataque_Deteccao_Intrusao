# Plano de implementação — índice

> **Onde fica o código (decisão 43):** o repositório Git é a raiz; o código fica em `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`) é relativo a `project/`, e os comandos `uv` rodam dentro dela. `.github/` e `.githooks/` ficam na raiz do repositório, porque o GitHub e o Git só os leem ali.

> **Validação (06/10/2026):** plano revisto por um agente independente em três passes (correção metodológica, implementabilidade, excesso de engenharia). Dezenove achados, nenhum crítico, seis altos; todos tratados e registrados em [../MEMORY/04-red-team.md](../MEMORY/04-red-team.md). Vinte e seis referências `arquivo:linha` conferidas, quatro corrigidas. Grafo sem ciclos.

> **Revisão de 07/10/2026:** segunda revisão independente (27 achados: 4 altos, 17 médios, 6 baixos) mais revisão de cobertura dos requisitos do professor e de demonstrabilidade por entrega; 31 referências `arquivo:linha` corrigidas. Decisões 38 a 41 registradas. O mapa requisito do professor → tarefa → artefato está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md).

> **Reconciliação de 07/10/2026, commit `360c3d3`:** tarefas 06, 07 e 08 prontas; respostas do professor a Q1 a Q6 e decisões 44 a 50 levadas às tarefas.

> **Reconciliação de 08/10/2026, commit `759ec29` (branch `tarefa/24-entregaveis`):** tarefas 09 a 17, 21 e 24 prontas e executadas com dados reais, e o complemento da 04 (Fig. 2); com a 24, as tarefas 18 e 20 estão cumpridas. Decisões 51 a 54 levadas às tarefas: os ⚠️ REVISAR das tarefas 11 e 15 e as pendências abertas pela decisão 45 estão resolvidos. **Nenhum ⚠️ REVISAR aberto.** Faltam: 19 (README e execução limpa), 22 (padrões) e 23 (acompanhamento), mais o que depende de pessoa, listado então em "Bloqueios" (hoje, "O que resta"). Conferido nesta reconciliação: suíte inteira (110 testes verdes), lint, formatação, `data/verify.py`, `make_report_assets.py` em diretório temporário (tabelas idênticas às versionadas) e a compilação do relatório; nenhum experimento foi rodado de novo.

> **Fechamento de 08/10/2026, commit `5999c1b` (branch `tarefa/19-readme-execucao-limpa`):** as 25 tarefas estão concluídas. Depois de `759ec29` vieram a 19 (README, `scripts/execucao_limpa.sh`, `scripts/comparar_resultados.py` e a execução limpa de 08/10/2026: 7 h 30 min, 22 passos, 260 de 260 arquivos de `results/` e 56 de 56 de `report/` conferem), a 22 (`.claude/rules/experimentos.md`), a 23 (página `docs/09-acompanhamento-professor.md`) e a 25 (revisão final em código, em [REVISAO-FINAL.md](REVISAO-FINAL.md): nenhum achado bloqueante, cinco importantes e nove menores, todos tratados). A decisão 55 fechou as pendências de pessoa que dependiam de conversa ou de conferência, e a versão final foi para a `main` por avanço direto, sem pull request por tarefa (55f). **Nenhum ⚠️ REVISAR aberto.** Conferido neste fechamento: suíte inteira (118 testes verdes em 44 s), lint, formatação, `scripts/metricas_fig4.py`, os greps de higiene, o CI verde na `main` do GitHub e a instalação com pip em um clone descartável; nenhum experimento foi rodado. O que resta é de pessoa e está em "O que resta", abaixo.

25 tarefas, organizadas por fluxo. Cada arquivo traz: onde, objetivo, dependências, **o que demonstra**, arquivos, o que fazer, por quê, evidência, risco, critério de aceite e verificação. As tarefas implementadas trazem um bloco "Como ficou" ou "Situação", que prevalece sobre o resto do arquivo.

Antes de implementar qualquer tarefa: ler [../MEMORY/00-decisoes-travadas.md](../MEMORY/00-decisoes-travadas.md), [VERIFICACAO.md](VERIFICACAO.md) e a seção da tarefa em [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md). As regras de código, commit, teste e fluxo estão em `.claude/rules/`.

## Tarefas

"Concluída" quer dizer: código, testes e revisão feitos; o script rodado com os dados reais, com `run.json` de `dirty: false`; o resultado regenerado igual na execução limpa de 08/10/2026; e o commit na `main`. A versão final foi para a `main` por avanço direto, sem pull request por tarefa (decisão 55f): `origin/main` está em `378f170`, com o CI verde, e os 15 commits de `378f170` a `5999c1b` (correções da revisão final, registro da execução limpa) estão na branch local e são enviados em seguida. O commit citado é o que fechou a tarefa. "Resta de pessoa" é o que só a equipe faz.

| # | Fluxo | Tarefa | Objetivo da especificação | Depende de | Situação |
| --- | --- | --- | --- | --- | --- |
| [01](01-fundacao-repositorio-ambiente.md) | Fundação | Repositório e ambiente | — | — | concluída em `5e11d56`; `LICENSE` (MIT) em `7813020`; CI verde na `main` do GitHub; instalação com pip conferida em `5999c1b`; resta de pessoa: proteção da `main` e acesso de escrita dos integrantes |
| [02](02-fundacao-config-runlog.md) | Fundação | Configuração e registro de execução | — | 01 | concluída em `b1434ab` (`dirty` em `ac360ba`; `N_JOBS` em `4746c22`; versões de scipy, matplotlib e do painel no `run.json` em `8f1d864`) |
| [03](03-dados-aquisicao-cira.md) | Dados | Aquisição do CIRA-CIC-DoHBrw-2020 | P1 | — (script: 01) | concluída em `acc297a`; `data/verify.py`: 8 de 8 arquivos |
| [04](04-dados-carga-limpeza.md) | Dados | Carga, limpeza e reconciliação com a Tabela I (E0); Fig. 2 | P1 | 02, 03 | concluída em `9e7563f`; complemento da Fig. 2 em `39a7007` (código `d45251e`, `44798f9`) |
| [05](05-dados-split-scaler.md) | Dados | Split, normalização e contagens | P1 | 04 | concluída em `c262b2b` |
| [06](06-avaliacao-metricas.md) | Avaliação | Métricas e comparação com o artigo | P1 | 02 | concluída em `21171f4`; acrescida pelas tarefas 11, 14 e 21 |
| [07](07-reproducao-subconjuntos.md) | Reprodução | Três subconjuntos balanceados | P1 | 05 | concluída em `a4ba0e5`, executada dentro da 08 |
| [08](08-reproducao-stacked-rf.md) | Reprodução | Balanced Stacked Random Forest (E1), nas duas leituras de profundidade | P1 | 06, 07 | concluída em `798ecd3`; `fit_system` e `cross_validated_confusion` no pacote desde `472bb79`; G6 fechado pela execução limpa; asserção do scaler em `2686b80` |
| [09](09-reproducao-baselines.md) | Reprodução | Tabela II inteira: baselines (E2) e metade inferior | P1 | 05, 06, 08 | concluída em `076fbe1`; metade inferior da Tabela II conferida pelo assistente em duas passagens, não por dois integrantes (decisão 55b); teste do scaler de E2 em `bf19a11` |
| [10](10-reproducao-sensibilidade.md) | Reprodução | Sensibilidade às ambiguidades (E3) | P1 | 08 (o resumo lê a 11) | concluída em `7b3ddaf`; resumo em `320a2a5`, refeito em `2313597`; `stacking_cv` e `oss` não feitas, declaradas |
| [11](11-corrigido-protocolo.md) | Protocolo corrigido | Variância e comparação justa (E4) | P1, base de P3 | 08, 09 | concluída em `2a76a84`, dez seeds e quatro dobras por máquina; agregado refeito em `38809c1`; asserção do scaler e do SMOTE em `7200be7` |
| [12](12-xai-shap.md) | Explicabilidade | SHAP sobre os modelos base (E5) e painel interativo | P1 | 08 (o script lê a etapa de dados da 13) | concluída em `a0d853a`, refeita em `38809c1`; painel conferido no ar com os dados reais em 08/10/2026 |
| [13](13-dataset2-aquisicao.md) | Segundo dataset | Aquisição e compatibilidade | P2 | — (carga: 04) | concluída em `fa320d6`, refeita em `4253571` e `38809c1`; asserção do combinado sem réplicas em `80111aa` |
| [14](14-dataset2-avaliacao.md) | Segundo dataset | P1 refeito no combinado sem réplicas; transferência e combinado publicado ao lado (E6) | P2 | 14a: 08, 13; 14b: 09, 12, 14a | concluída: 14a em `bc5e510`, 14b em `b32e4f8`; resumos refeitos em `38809c1`; dois `metrics.json` de SHAP regravados em `97b2c8c` |
| [15](15-p3-modificacao-m1-m2.md) | P3 | Modificação M1 + M2 (E8) | P3 | 11, 12, 14 (basta a 14a) | concluída em `713e650`, dez seeds nos dois datasets; análise posterior em `2313597`; testes da seleção em `2be47e9`; passo de explicabilidade não feito, declarado (decisão 54f) |
| [16](16-p3-robustez-duracao.md) | P3 | Robustez à duração, M3 | P3 | 12, 15 | concluída em `df16ca5`, partes A e B, dez seeds; leitura descritiva posterior em `2313597` |
| [17](17-entrega-tabelas-figuras.md) | Entrega | Tabelas e figuras por script | relatório | 08 a 16, 21 e a Fig. 2 | concluída em `16b7f39`: 30 tabelas, 13 figuras e `report/INDICE.md`; regeneradas idênticas na execução limpa |
| [18](18-entrega-relatorio.md) | Entrega | Relatório | relatório | 17 | concluída pela 24 (`3725f27`); resta de pessoa: leitura do relatório pelos integrantes, com a lista de conferência pergunta → seção |
| [19](19-entrega-readme-execucao-limpa.md) | Entrega | README, execução limpa, checklist | GitHub | 17 (envio: 24) | concluída em `5999c1b`: README em `7657501`, `execucao_limpa.sh` em `88c0e88`, `comparar_resultados.py` em `53f1ca4` e `47cdabe`; execução limpa em 08/10/2026; resta de pessoa: enviar os commits finais e a entrega de 18/11, com a checklist e o comprovante |
| [20](20-entrega-slides-projeto.md) | Entrega | Slides do projeto | apresentação | 15, 17 | concluída pela 24 (`c74fc3f`); resta de pessoa: ensaio cronometrado; apresentação em 19/11 e arguição |
| [21](21-condicional-ferramenta-tunel.md) | Reprodução | Ferramenta de túnel (E7), Seção VI-D e Fig. 9 | P1 | 08, 13 (lê a etapa de dados da 13) | concluída em `1a0e041`; resumo em `d86b0b5`, refeito em `38809c1` |
| [22](22-padronizacao-doc-padrao.md) | Padronização | Registrar padrões (anti-recorrência) | — | 08, 11 | concluída em `e2e0015`: seis regras em `.claude/rules/experimentos.md` (sete padrões registrados), dois padrões dispensados com motivo |
| [23](23-acompanhamento-professor.md) | Acompanhamento | Perguntas ao professor e material de 10/11 e 17/11 | — | — (material: 08) | concluída: página `docs/09-acompanhamento-professor.md` em `ba9ddc4` e `4de9ab2`, com a execução limpa em `5999c1b`; resta de pessoa: encontros de 10/11 e 17/11 e o registro do retorno |
| [24](24-entrega-pdfs-finais.md) | Entrega | Relatório em PDF e apresentação em PPTX, pelos modelos de `geracao_latex_and_pdf/` | relatório e slides | 17 | concluída em `c74fc3f`: `relatorio.pdf` (8 páginas), `apresentacao.pptx` (14 slides), `roteiro.md` (11 min 55 s, três apresentadores); cópia em `entregaveis-apresentacao/` (`f2aedd6`) |
| [25](25-revisao-final-em-codigo.md) | Fechamento | Revisão final em código: rastro, recomputação, mutação e leitura, sem treinar | todos | 19 | concluída em `5999c1b`: revisão em `3e42795`, achados tratados em `2686b80`, `7200be7`, `bf19a11`, `2be47e9`, `80111aa`, `2622ea3`, `97b2c8c`, `3725f27` e `c74fc3f` |

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
25 ← 19
```

Sem ciclos: as arestas novas vão de script de resumo para resultado de treino (10 → 11; 15 → 16) ou de treino para etapa de dados (12 → 13; 21 → 13), e nenhum treino lê resumo. A ordem de execução que respeita todas elas está na tarefa [19](19-entrega-readme-execucao-limpa.md), "Ordem real dos scripts".

## Ordem de execução

A tabela de ondas abaixo é a proposta original; as datas em negrito são fixas ou marcos de corte e não mudaram. O dono por tarefa não se aplica: a execução ficou na sessão de implementação (decisão 44) e o histórico com uma só identidade Git foi aceito (decisão 55d).

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

Em 08/10/2026 as ondas 0 a 8 estão implementadas, antes das janelas: P3 foi feito (15 e 16), a decisão de 09/11 já não tem o que cortar, e a execução limpa foi feita. As datas fixas seguem valendo para o que é de pessoa: os encontros de 10/11 e 17/11, a entrega de 18/11 e a apresentação de 19/11.

## Onde roda (decisões 42 e 44)

Desenvolvimento e testes N1: máquina de quem implementa e CI. A execução com dados reais das tarefas 03 a 16 e da 21, e a execução limpa da 19, foram feitas na própria sessão de implementação, nesta máquina (decisão 44). O cluster Apuana não se aplica: não foi usado, e a pasta `jobs/` não existe. Os 229 `run.json` versionados trazem a mesma máquina, com 10 núcleos. A evidência é `results/`, o `run.json` com a máquina e `dirty: false`, e a execução limpa; a saída colada no pull request não se aplica (decisão 55f).

Custo medido, pela chave `timings` dos `run.json` (detalhe por script na tarefa 19): E1, 56 minutos; E4, 1 h 59 min; modificação de E8, 1 h 59 min; robustez de E8, 1 h 57 min; E6, 42 minutos (14a) e 31 minutos (14b); os demais, menos de 10 minutos cada. Soma de todos os treinos: 8 h 27 min. A execução limpa inteira levou 7 h 30 min. Nada foi cortado por custo; a seleção de hiperparâmetros de E8 usa 25% do treino de cada seed (decisão 54a), e isso é declarado.

## O que foi cortado

Nada foi cortado por prazo. Não foram feitos, e estão declarados como não feitos nos resumos: as variantes `stacking_cv` e `oss` da tarefa 10 e o passo de explicabilidade da tarefa 15 (decisão 54f). Nenhum corte removeu proteção contra vazamento de dados.

## O que resta

A lista única, com o detalhe e a evidência de cada item, é a seção "O que resta de pessoa" de [`docs/07-pendencias.md`](../../docs/07-pendencias.md). Aqui fica só o que tem caixa aberta em arquivo de tarefa.

### De pessoa

| Item | Tarefa | Data |
| --- | --- | --- |
| Enviar os commits finais (de `378f170` em diante) e conferir o CI verde no commit entregue | 19 | antes de 18/11 |
| Slides e apresentação do seminário (fora das tarefas deste plano) | — | 14/10; 15 ou 20/10 |
| Encontros com o professor e registro do retorno de cada um | 23 | 10/11 e 17/11 |
| Leitura do relatório pelos integrantes, com a lista de conferência pergunta → seção e parágrafo | 18, 24 | antes de 18/11 |
| Ensaio cronometrado da apresentação, pelos três que apresentam | 20 | antes de 19/11 |
| Entrega: checklist de entrega, PDF e link do GitHub, com o comprovante | 19 | 18/11 |
| Apresentação e arguição | 20 | 19/11 |
| Proteção da `main` e acesso de escrita dos integrantes no GitHub, se a equipe quiser | 01 | — |

### Aberto que não é de pessoa

| Item | Tarefa | Por que ficou aberto |
| --- | --- | --- |
| Registro de que o painel sobe e a página responde com os dados reais | 12 (T12-7) | Fechado: conferido em 08/10/2026 na sessão: `uv run python scripts/painel_xai.py` com os dados reais, HTTP 200 em `127.0.0.1:8050` e em `/_dash-layout` após 162 s; processo encerrado, porta livre, `git status` limpo |

### Perguntas ao professor

Q1 a Q6 foram respondidas em 07/10/2026 (decisões 46 a 50). Q7 (frase de declaração do uso de IA), Q9 (idioma e limite de páginas) e Q10 (repositório público ou privado) ficaram sem resposta e foram fechadas pela equipe em 08/10/2026: sem frase, português com até 8 páginas, repositório público (decisão 55a). O mesmo vale para os pontos que pediam conversa: as duas leituras de profundidade, as ressalvas de Q4 sobre o combinado e o método de Q5. Nenhum desses é resposta do professor; continuam na página `docs/09-acompanhamento-professor.md`, e uma resposta dele que contrarie uma decisão vira `⚠️ REVISAR` na tarefa afetada.

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

- O plano está fechado: não há tarefa a implementar. O que resta é de pessoa e está em "O que resta".
- O que cada tarefa demonstra e como os requisitos do professor se distribuem está em [ENTREGAS-DEMONSTRAVEIS.md](ENTREGAS-DEMONSTRAVEIS.md).
- Para regenerar tudo: `scripts/execucao_limpa.sh` e `scripts/comparar_resultados.py`, descritos na tarefa 19 e no `README.md` de `project/`. Script que importa outro script roda como módulo: `uv run python -m scripts.<nome>`.
- Se uma correção futura tocar código: ciclo de `.claude/rules/fluxo-implementacao.md` (implementa, testa, revisa), gate de `VERIFICACAO.md`, e o agente `cin0114-plan-sync` reconcilia o plano depois.
- Mudança de decisão travada: só com o usuário; registrar em `../MEMORY/00-decisoes-travadas.md`.
