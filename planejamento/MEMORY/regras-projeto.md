# Regras do projeto e do Claude

Lido em 06/10/2026. Repositório único: a pasta `project/` (decisão 32). Os comandos abaixo rodam dentro dela.

| Fonte lida | Convenção que o plano DEVE seguir | Agente/skill a reutilizar |
| --- | --- | --- |
| `CLAUDE.md` (raiz) | Especificação oficial decide o que é cobrado; nada inventado; reprodução fiel separada de correção; checklist antes de entrega; a equipe precisa conseguir defender tudo | — |
| `docs/06-padroes.md` | Estrutura `src/ scripts/ tests/ results/ report/ data/`; identificadores em inglês, comentários em português; comentário explica o porquê; ponto omisso do artigo comentado com decisão, motivo e seção do artigo, sem identificador interno; sem número mágico; seeds explícitas; sem abstração antecipada; Conventional Commits em português; PR com revisão de outro integrante | — |
| `.claude/skills/experimento/SKILL.md` | Antes de qualquer script de experimento: declarar o que testa, o alvo e a trilha; resultado em `results/<experimento>/` com config, seed, versões, hash e commit | skill `experimento` em toda tarefa de E0 a E8 |
| `.claude/skills/checklist-entrega/SKILL.md` | Checklist item a item com evidência antes de submeter | skill `checklist-entrega projeto` na tarefa 19 |
| `.claude/agents/revisor-metodologico.md` | Revisão independente de código e protocolo; ordem: vazamento, fidelidade, reprodutibilidade, avaliação, código | agente no gate de toda tarefa com código de experimento |
| `.claude/agents/revisor-de-texto.md` | Revisão de relatório, slides e README contra especificação e fontes | agente no gate das tarefas 18, 19 e 20 |
| `.claude/skills/estudar/SKILL.md` | Modo Ensino; não afeta o plano | — |
| `.gitignore` (pasta de trabalho) | Modelo do `.gitignore` de `project/`, criado em 07/10/2026 | tarefa 01 |
| `.claude/rules/codigo.md` | Solução mais simples; docstring em função pública; comentário só para regra do artigo ou decisão; nenhuma referência a arquivo interno no código | agente `implementador` |
| `.claude/rules/commits.md` | Conventional Commits; sem `Co-Authored-By`; lint e formatação verdes em todo commit; uma branch por tarefa | hooks em `.githooks/` (tarefa 01) |
| `.claude/rules/testes.md` | Testes de funcionalidade macro e de erro silencioso, com dados sintéticos, no CI | `plan/PLANO-DE-TESTES.md` |
| `.claude/rules/fluxo-implementacao.md` | Uma tarefa por vez: implementa, testa, revisa, integra | skill `implementar` |

## Comandos (build/test/lint)

`project/` ainda não tem `pyproject.toml`. Os comandos abaixo passam a existir com a tarefa 01, rodam dentro de `project/` e são os do gate:

| Finalidade | Comando |
| --- | --- |
| Instalar | `uv sync` |
| Lint | `uv run ruff check .` |
| Formatação | `uv run ruff format --check .` |
| Testes | `uv run pytest` |
| Executar experimento | `uv run python scripts/<experimento>.py` |

Hoje só existe um script, sem dependências: `cd project && python3 scripts/metricas_fig4.py`.

## Conflitos entre o plano e as regras

- `docs/06-padroes.md` deixa a versão do Python e das bibliotecas como `[Preencher]`. O plano preenche com as versões verificadas (decisão 03). Não é conflito; a tarefa 01 atualiza o doc.
- A skill `experimento` manda gravar o commit junto do resultado. O repositório não tem commits ainda; a tarefa 01 cria o primeiro. Sem conflito depois disso.
- Nenhuma regra existente contradiz o plano.
