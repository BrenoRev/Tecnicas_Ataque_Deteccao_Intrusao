# SYNC-BASELINE-PLAN — último commit analisado no plano

> O agente `cin0114-plan-sync` lê este arquivo, calcula o que mudou desde o commit registrado, reconcilia as tarefas e avança a coluna. Baseline separado do de `MEMORY/SYNC-BASELINE.md`.

| Repositório | Branch | Commit analisado | Analisado em |
| --- | --- | --- | --- |
| raiz da pasta de trabalho (decisão 43); código em `project/` | `tarefa/08-stacked-rf` (dois commits à frente de `origin/tarefa/08-stacked-rf`; `main` local e `origin/main` em `6bf80bd`; nenhuma branch de tarefa integrada) | `360c3d3` | 07/10/2026 |

## Histórico

| Quando | Delta relevante para o plano | Tarefas tocadas / ⚠️ REVISAR |
| --- | --- | --- |
| 06/10/2026 | Plano criado; nenhum código | — |
| 07/10/2026 | Segunda revisão independente e revisão de requisitos; decisões 38 a 41; `ENTREGAS-DEMONSTRAVEIS.md`; tarefas 01 e 14 reescritas; 31 referências corrigidas | todas |
| 07/10/2026 | Tarefa 01 implementada: `c74a393..5e11d56`, 14 arquivos novos (ambiente, pacote, teste mínimo, hooks, CI, modelo de pull request, READMEs). Repositório na raiz (decisão 43). Dados do CIRA extraídos no disco, sem os zips | 01 pronta, aguardando integração por pessoa; 02, 19 e 21 com referências ajustadas; `VERIFICACAO.md` e `PLANO-DE-TESTES.md` (CI) ajustados; ⚠️ REVISAR em 03 e 04 |
| 07/10/2026 | Tarefas 02 a 05 implementadas: `5e11d56..0ae2d49`. Linha registrada depois, a partir do commit `280eca7`, que reconciliou as tarefas sem avançar esta tabela | 02 a 05 prontas (03 a 05 executadas); 06 a 16 e 21 com bloco de reconciliação; ⚠️ REVISAR de 03 e 04 resolvidos; ⚠️ REVISAR aberto na 11 (caminho `fold<k>`). Ficaram por aplicar o crosswalk, o plano de testes e o I4 do gate, aplicados na linha seguinte |
| 07/10/2026 | `0ae2d49..360c3d3`: tarefas 06 (`21171f4`), 07 (`a4ba0e5`) e 08 (`0a94b10`, `2732d0a`, `b00e471`; resultados em `798ecd3`, nas duas leituras de profundidade); ajustes de 02 a 05 (`ac360ba`, `20cd2cd`, `4746c22`, `c262b2b`, `f1eba42`); respostas do professor a Q1 a Q6 e decisões 44 a 50 (`0c5867a`, `360c3d3`). Sem `pull` na `main`: a reconciliação foi feita na branch da tarefa, com um treino em andamento, e a `main` local está igual à `origin/main` | 06, 07 e 08 prontas (08 executada; G6 em aberto). Decisões levadas a 01, 04 (complemento Fig. 2), 09 a 21 e 23; 14 dividida em 14a e 14b; 21 obrigatória; `00-README.md` (situação, grafo, ordem, bloqueios, pendências da decisão 45), `PLANO-DE-TESTES.md`, `VERIFICACAO.md`, `ENTREGAS-DEMONSTRAVEIS.md` e `RAG-crosswalk.md` atualizados. ⚠️ REVISAR abertos: 11 (caminho `fold<k>`; modelo B diante da decisão 45) e 15 (M1 e grade diante da decisão 45) |
