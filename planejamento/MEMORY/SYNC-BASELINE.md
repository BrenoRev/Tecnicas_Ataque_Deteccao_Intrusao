# SYNC-BASELINE — último estado do repositório refletido nos docs

> O agente `cin0114-doc-sync` lê este arquivo, calcula o que mudou desde o commit registrado, reconcilia `docs/` e `planejamento/MEMORY/` e avança a coluna.

| Repositório | Branch | Commit analisado | Analisado em |
| --- | --- | --- | --- |
| `project/` | `main` | — (repositório inicializado, sem commits) | 07/10/2026 |

A pasta `project/` tem `git init` feito (`main`), sem commits nem remoto; dentro dela já estão `data/raw/` (ignorado), `.gitignore` e `scripts/metricas_fig4.py`. O primeiro baseline real é o primeiro commit, feito na tarefa 01.

## Histórico

| Quando | Delta relevante | Docs tocados / ⚠️ REVISAR |
| --- | --- | --- |
| 06/10/2026 | Estado inicial: `docs/`, `CLAUDE.md`, `.claude/`, `scripts/metricas_fig4.py`, `planejamento/` | — |
| 07/10/2026 | `scripts/metricas_fig4.py` movido para `project/scripts/` e ajustado ao lint; `project/.gitignore` criado; dados inventariados | `docs/04`, `06`, `07`, `08`; plano |
