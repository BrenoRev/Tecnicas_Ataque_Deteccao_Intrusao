# STATUS — plano de implementação do projeto CIN0114

Tier: médio · Tipo de entrega: análise implementável · Atualizado: 07/10/2026

## Fase atual

plano revisado em 07/10/2026 (segunda revisão independente, cobertura dos requisitos do professor e demonstrabilidade por entrega) e pronto para implementar a partir da tarefa 01. `project/` tem Git inicializado, `.gitignore` e `scripts/metricas_fig4.py`; nenhum commit ainda.

## Coberto

- [x] Intake: escopo P1 + P2 + P3, workspace em `planejamento/`, sem estimativa, sem ferramenta de gestão
- [x] Regras do projeto → `MEMORY/regras-projeto.md`
- [x] Stack verificada em ambiente descartável → `MEMORY/01-discovery-stack.md`
- [x] Domínio (ponteiros para `docs/`) → `MEMORY/02-discovery-dominio.md`
- [x] Síntese: riscos e arquitetura-alvo → `MEMORY/03-sintese.md`
- [x] Decisões 01 a 41 travadas, e a tabela "Pendentes da equipe" → `MEMORY/00-decisoes-travadas.md`
- [x] Plano: 23 tarefas, grafo, ordem, gate → `plan/`
- [x] Red-team (19 achados, 6 altos, todos tratados) e cortes → `MEMORY/04-red-team.md`
- [x] Agentes de sincronização → `.claude/agents/cin0114-plan-sync.md`, `cin0114-doc-sync.md`
- [x] Regras de código, commit, teste e fluxo → `.claude/rules/` (decisões 28 a 31)
- [x] Plano de testes por tarefa → `plan/PLANO-DE-TESTES.md`
- [x] Agente `implementador` e skill `implementar`
- [x] Lint, `pytest` e hooks de commit validados em repositório descartável (07/10/2026); conteúdo na tarefa 01
- [x] Segunda revisão independente do plano (07/10/2026): 27 achados e 31 referências corrigidos; `plan/ENTREGAS-DEMONSTRAVEIS.md` criado; `[build-system]`, `scipy` e `matplotlib` fixados; `metricas_fig4.py` ajustado ao lint e movido para `project/scripts/`; `project/.gitignore` criado

## Faltando

- [x] Perguntas enviadas ao professor em 07/10/2026 (cópia em `docs/07-pendencias.md`)
- [ ] Respostas do professor a Q1–Q6 e Q9, Q10 e a parte em aberto de Q7 (`docs/07-pendencias.md`); Q7 resolvida em 07/10/2026 (uso de IA aprovado)
- [ ] Itens de "Pendentes da equipe" em `MEMORY/00-decisoes-travadas.md`: licença, visibilidade, dono por tarefa, drive e `.git` da raiz antes da tarefa 01; Tabela II (literatura) antes da 06; prevalências, amostra do SHAP, grade de M2, fração e fatores antes das tarefas 11, 12, 15 e 16
- [x] Decisão 42 (07/10/2026): execução com dados reais local ou no Apuana, as duas valem; o importante é treinar e gerar a evidência. Acesso ao cluster só é pedido se a equipe for usá-lo
- [ ] Template Overleaf lido (tarefa 18, passo 1): o formato das tabelas da tarefa 17 depende dele

## Mudança de 07/10/2026

O repositório Git passa a ser `project/` (decisão 32). O Git vazio da pasta de trabalho foi removido. Os documentos internos não entram no repositório.

## Não feito, por decisão

- Código e commits: ainda não começaram; passam a ser feitos pelo ciclo da decisão 28, a partir da tarefa 01.
- Workflow do GitHub Actions: descrito na tarefa 01, não validado em execução (não há remoto). É conferido no primeiro pull request (teste T01-5).
- Estimativa de horas: não pedida.
- Cards em ferramenta de gestão: não pedidos.
- Artefatos online de gestão e de QA: não gerados; o projeto não tem card nem público de gestão. Disponível sob pedido.

## Dados (07/10/2026)

Os três datasets estão em `project/data/raw/` e foram inventariados (`docs/08-inventario-dados.md`). Decisões 34 a 37. Achados principais: remover NaN reproduz a Tabela I; o teste tem uma amostra a mais que a Fig. 4b; 13,7% do teste repete o treino; o malicioso vem de outras máquinas e de outro período; o HKD "aumentado" é replicação de 20 vezes.

## Lacunas declaradas do discovery

- Resolvidas em 07/10/2026: nomes, tamanhos e cabeçalhos do CIRA; colunas do HKD e do combinado.
- Resolvidas em 07/10/2026: o `-10` é sentinela do DoHLyzer para desvio padrão zero; as 5.258 linhas distintas do HKD aumentado são as do `Total-48h.csv`; citação do HKD conferida.
- Template Overleaf do relatório: não lido (tarefa 18, passo 1).
- Python 3.14: não testado; o plano fixa 3.12.

## Próximo passo

1. Equipe: fechar os itens de "Pendentes da equipe" que vêm antes da tarefa 01 (licença, visibilidade, dono por tarefa, `.git` da raiz) e decidir os demais antes das tarefas que os usam.
2. Ler o template Overleaf (tarefa 18, passo 1), de preferência antes de 14/10, porque o formato das tabelas da tarefa 17 depende dele.
3. `/implementar 01`.

A segunda rodada independente foi feita em 07/10/2026, depois das mudanças de layout e de dados. Se o plano for alterado de novo antes da implementação, vale rodar outra.

## Baseline

ver `SYNC-BASELINE.md` e `plan/SYNC-BASELINE-PLAN.md`
