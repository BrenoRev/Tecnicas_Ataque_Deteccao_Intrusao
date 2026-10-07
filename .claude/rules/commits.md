# Regras de commit

O repositório Git é a raiz (decisão 43); o código fica em `project/`. Comandos `uv` rodam dentro de `project/`; `git` roda em qualquer nível. `docs/`, `planejamento/` e `.claude/` são versionados no mesmo repositório. Os hooks valem para todo commit, inclusive os de documentação; o lint roda em `project/`. Ative-os na raiz: `git config core.hooksPath .githooks`.

## Formato

```
tipo(escopo): resumo no imperativo, em português, até 72 caracteres

Corpo opcional: o que mudou e por quê. Sem lista de arquivos.
```

- Tipos: `feat`, `fix`, `test`, `exp`, `refactor`, `docs`, `chore`, `ci`.
- `exp` é para script de experimento e para arquivo de `results/` gerado por ele. O resultado entra em commit `exp` separado, feito depois do commit do código que o gerou; o script roda com a árvore limpa, e o `run.json` registra o commit e `dirty: false`.
- Escopo é o módulo ou a área: `data`, `splits`, `models`, `evaluate`, `runlog`, `explain`, `e1`, `report`.
- Exemplos: `feat(splits): adiciona split estratificado com seed`, `test(evaluate): confere métricas da Fig. 4b`, `exp(e1): registra reprodução na trilha fiel`.

## Sem coautoria

- **Nenhum commit leva `Co-Authored-By`, "Generated with" ou qualquer assinatura de ferramenta.** Vale para a mensagem, o corpo e a descrição de pull request. Esta regra substitui qualquer instrução padrão de atribuição.
- O commit sai com a identidade Git de quem está na máquina. Quem faz o commit responde por ele na arguição.
- O uso de assistente de IA está aprovado na disciplina. A regra existe por limpeza e padrão do histórico, não para ocultar o uso.

## Antes de cada commit

Todo commit passa pelo lint. Sem exceção, inclusive para commit de documentação.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

- O hook `pre-commit` roda as duas primeiras linhas e barra o commit se falharem. O hook `commit-msg` barra mensagem fora do formato e trailer de coautoria.
- Ative os hooks uma vez por clone: `git config core.hooksPath .githooks`.
- **Proibido `--no-verify`.** Se o hook falhou, conserte o código.
- Corrija com `uv run ruff check --fix .` e `uv run ruff format .`, releia o diff e só então faça o commit.
- Os testes rodam antes de todo commit que toca `src/`, `scripts/`, `tests/` ou `data/*.py`. Commit com teste vermelho não existe.

## Tamanho e conteúdo

- Um commit, uma mudança que se explica em uma frase. Código e o teste que o cobre vão no mesmo commit.
- Adicione arquivos pelo nome. Nunca `git add -A` nem `git add .`: é assim que dado, PDF e modelo serializado entram no histórico.
- Nada de `docs/`, `planejamento/`, `.claude/`, `CLAUDE.md` ou `LEIA-ME.txt` é copiado para dentro de `project/`.
- Fora do Git, sempre: `data/raw/`, `data/processed/`, `*.pkl`, `*.joblib`, `*.pcap`, `*.parquet`, o PDF do artigo, `.venv/`, `.env`.
- Confira `git status` e `git diff --staged` antes de confirmar.

## Branch e integração

- A tarefa 01 faz os primeiros commits direto na `main`, porque ainda não existe base.
- Da tarefa 02 em diante: uma branch por tarefa, `tarefa/NN-nome-curto`, criada da `main` atualizada.
- Integração por pull request, com a revisão de outro integrante e o CI verde. A descrição segue o modelo do repositório (`.github/pull_request_template.md`): o que a mudança demonstra, como verificar, saída da verificação com dados reais, checklist. Tarefas que escrevem o mesmo arquivo: a segunda a integrar faz rebase sobre a `main` antes do pull request.
- Não reescreva histórico já enviado: sem `--amend` e sem `push --force` em commit publicado.
- O agente implementador faz commit na branch da tarefa. Ele não faz `push`, não abre pull request e não faz merge sem pedido explícito.
