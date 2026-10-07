# Planejamento do projeto CIN0114 — mapa-mestre

**Objetivo:** plano em tarefas implementáveis para o projeto da disciplina: reproduzir o IDS para DoH de Zebin et al. (P1), avaliá-lo em outro dataset (P2) e implementar a modificação opcional (P3).

**Tipo de entrega:** análise implementável. **Tier:** médio. **Estimativa de horas:** não pedida. **Gestão:** só os `.md` do plano.

**Repositório:** a raiz desta pasta (decisão 43), com remoto público no GitHub; o código fica em `project/` e este plano é versionado junto. A fase de plano está encerrada; a implementação segue o ciclo de `.claude/rules/fluxo-implementacao.md`, uma tarefa por vez.

## Índice

| Preciso de | Arquivo |
| --- | --- |
| Em que fase está e o que fazer ao retomar | [MEMORY/STATUS.md](MEMORY/STATUS.md) |
| Decisões travadas (fonte única) | [MEMORY/00-decisoes-travadas.md](MEMORY/00-decisoes-travadas.md) |
| Regras do projeto, agentes e skills a reutilizar | [MEMORY/regras-projeto.md](MEMORY/regras-projeto.md) |
| Stack verificada (versões, APIs, custo) | [MEMORY/01-discovery-stack.md](MEMORY/01-discovery-stack.md) |
| Ponteiros para o discovery de domínio | [MEMORY/02-discovery-dominio.md](MEMORY/02-discovery-dominio.md) |
| Riscos priorizados e arquitetura-alvo | [MEMORY/03-sintese.md](MEMORY/03-sintese.md) |
| Resultado do red-team e cortes | [MEMORY/04-red-team.md](MEMORY/04-red-team.md) |
| Arquivo → tarefa → doc | [MEMORY/RAG-crosswalk.md](MEMORY/RAG-crosswalk.md) |
| Tarefas, grafo e ordem | [plan/00-README.md](plan/00-README.md) |
| Gate de "pronto" | [plan/VERIFICACAO.md](plan/VERIFICACAO.md) |
| Testes de cada tarefa e CI | [plan/PLANO-DE-TESTES.md](plan/PLANO-DE-TESTES.md) |
| Requisito do professor → tarefa → artefato | [plan/ENTREGAS-DEMONSTRAVEIS.md](plan/ENTREGAS-DEMONSTRAVEIS.md) |

O conhecimento de domínio (requisitos, artigo, dados, plano experimental, padrões, pendências) vive em [../docs/](../docs/README.md) e não é duplicado aqui.

## Regras deste workspace

- Decisão travada só muda com o usuário. Fato novo que a contradiga vira `⚠️ REVISAR`, não reescrita.
- Toda afirmação aponta para a fonte: `arquivo:linha` no repositório, seção/figura do artigo, ou comando executado.
- Ao implementar uma tarefa, seguem valendo o [../CLAUDE.md](../CLAUDE.md), a skill `experimento` e o gate em `plan/VERIFICACAO.md`.
