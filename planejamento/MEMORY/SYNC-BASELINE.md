# SYNC-BASELINE — último estado do repositório refletido nos docs

> O agente `cin0114-doc-sync` lê este arquivo, calcula o que mudou desde o commit registrado, reconcilia `docs/` e `planejamento/MEMORY/` e avança a coluna.

| Repositório | Branch | Commit analisado | Analisado em |
| --- | --- | --- | --- |
| raiz da pasta de trabalho (decisão 43); código em `project/` | `tarefa/24-entregaveis` | `759ec29` | 08/10/2026 |

O repositório Git é a raiz (decisão 43), com remoto público no GitHub. `main` local e `origin/main` estão em `6bf80bd`: nenhuma branch de tarefa foi integrada, e a reconciliação foi feita na branch `tarefa/24-entregaveis`, que contém todas as anteriores. Não houve `pull` na `main`. Próxima sincronização: `git diff --name-only 759ec29..HEAD`.

## Histórico

| Quando | Delta relevante | Docs tocados / ⚠️ REVISAR |
| --- | --- | --- |
| 06/10/2026 | Estado inicial: `docs/`, `CLAUDE.md`, `.claude/`, `scripts/metricas_fig4.py`, `planejamento/` | — |
| 07/10/2026 | `scripts/metricas_fig4.py` movido para `project/scripts/` e ajustado ao lint; `project/.gitignore` criado; dados inventariados | `docs/04`, `06`, `07`, `08`; plano |
| 08/10/2026 | Primeiro baseline com commit: do estado sem commits até `759ec29` (137 commits). Projeto inteiro implementado e executado com dados reais em 07 e 08/10/2026: E0 a E8 em `project/results/`, tabelas, figuras, relatório e apresentação em `project/report/`; decisões 43 a 54 | `docs/README`, `01` (evidência), `02` (leitura adotada e lugar no código de A1 a A18; doze linhas de leituras novas), `04`, `05`, `06`, `07`, `08`; `MEMORY/STATUS.md`, `regras-projeto.md`, `04-red-team.md`, tabelas de pendentes de `00-decisoes-travadas.md`; `POS-IMPLEMENTACAO.md`; `LEIA-ME.txt`. Números corrigidos em `docs/08`: fração do teste repetida no treino de 13,7% para 13,67% (com o detalhe por rótulo); BOM por arquivo (`l1` e `l2` do combinado não têm); hipótese de valores fora da faixa na transferência, não confirmada. ⚠️ REVISAR abertos, em `STATUS.md`: decisões 23 e 52 ("A contra B isola a arquitetura", contra `results/e4/corrigida/RESUMO.md`) e decisão 38 (E3 e E7 sem `HIPOTESE.md`; nomes e nível dos resumos em E7 e E8). Pendência de fonte: citação do dataset CIRA, duas formas, confirmar no IEEE Xplore. `RAG-crosswalk.md` não foi tocado nesta rodada: ficou com o `cin0114-plan-sync`, que rodou em paralelo |
