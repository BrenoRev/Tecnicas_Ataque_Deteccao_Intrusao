---
name: implementar
description: Conduz o ciclo completo de uma tarefa do plano do projeto CIN0114 - preparar, implementar, testar, revisar, corrigir e sincronizar o plano. Use quando pedirem "implementar a tarefa NN", "vamos para a próxima tarefa" ou "/implementar NN". Argumento - número da tarefa; sem argumento, a próxima tarefa liberada.
---

# Implementar uma tarefa

Argumento: número da tarefa (`01` a `23`). Sem argumento, escolha a de menor número com a situação "a fazer" e todas as dependências concluídas em `planejamento/plan/00-README.md`.

Uma tarefa por execução. As regras do ciclo estão em `.claude/rules/fluxo-implementacao.md`.

O repositório Git é `project/`. Todos os comandos `git` e `uv` abaixo rodam dentro dessa pasta; os arquivos de plano e de regras são lidos da pasta de trabalho, fora do repositório.

## 1. Preparar

1. Leia a tarefa, a seção dela em `planejamento/plan/PLANO-DE-TESTES.md` e a linha dela em `planejamento/plan/00-README.md`.
2. Confira as dependências: todas com a situação "concluída". Confira os bloqueios externos da mesma página. Dependência aberta ou bloqueio que trava a tarefa: pare e diga o que falta.
3. `git -C project status`: a árvore precisa estar limpa. Se não estiver, pare e mostre o que há. Exceção da tarefa 01: `project/` já existe com `git init` feito e sem commits, e `.gitignore` e `scripts/metricas_fig4.py` aparecem como não rastreados até o primeiro commit; `data/` não pode aparecer.
4. Branch: na tarefa 01, fique na `main`. Nas demais, crie `tarefa/NN-nome-curto` a partir da `main`. Se o usuário pediu para seguir sem esperar a integração da anterior, crie a branch a partir da branch da tarefa anterior e diga isso no relato: os pull requests são integrados na ordem.
5. Se a tarefa usa datasets, confira se os arquivos existem em `project/data/raw/` ou `project/data/processed/`. Se não existem, avise que a verificação local ficará pendente.
6. Tarefa só de texto ou organização (18, 20, 22, 23) não passa pelo agente implementador: siga o arquivo da tarefa e vá direto à revisão.
7. Itens que só uma pessoa faz (repositório remoto, `push`, pull request, proteção da `main`, acesso dos integrantes) ficam listados no relato como pendentes da pessoa; a tarefa não é dada como integrada sem eles.

## 2. Implementar e testar

Chame o agente `implementador` com: o número e o caminho da tarefa, a branch, e a situação dos dados. Não repita no pedido o conteúdo da tarefa: ele lê os arquivos.

Ao receber o relato, confira você mesmo, sem confiar no texto:

```bash
cd project
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
git log --oneline main..HEAD
git log main..HEAD --format=%B | grep -ci "co-authored-by\|generated with"
```

O último comando deve devolver 0. Qualquer vermelho volta para o implementador com a saída do comando.

## 3. Revisar

- Tarefa com código de dados, modelo ou experimento: agente `revisor-metodologico`, apontando o diff da branch (`git diff main...HEAD`).
- Tarefa de texto: agente `revisor-de-texto`.
- Tarefa de fundação sem experimento (01, 02): revise você o diff contra `.claude/rules/codigo.md`.

Entregue ao revisor o diff e os arquivos, não a sua opinião sobre eles.

## 4. Corrigir

Achado bloqueante ou importante volta para o agente `implementador`, com o texto do achado. Depois da correção, repita o passo 2 e peça nova revisão só dos pontos corrigidos. No máximo três rodadas; na terceira com bloqueante aberto, pare e leve ao usuário.

## 5. Fechar

1. Confira o critério de aceite item a item contra o código e os arquivos gerados.
2. Chame o agente `cin0114-plan-sync` para marcar a tarefa e reconciliar as seguintes.
3. Chame o agente `cin0114-doc-sync` quando a implementação mudou algo que `docs/` afirma (nome de coluna, contagem, leitura de ambiguidade) e sempre que a tarefa pede atualização em `docs/` (03, 04, 08, 13): o implementador não edita `docs/`.
4. Não faça `push` nem abra pull request sem pedido explícito.

## 6. Relatar

Em poucas linhas: situação da tarefa; critério de aceite com o que ficou pendente; resultado do gate; achados da revisão e como foram tratados; o que depende de dados reais ou de uma pessoa; a próxima tarefa liberada.

A tarefa está **pronta** quando o gate está verde e a revisão não tem bloqueante. Está **integrada** só depois do pull request aprovado por outro integrante com o CI verde. Não comece a tarefa seguinte antes disso, a menos que o usuário peça para empilhar branches.
