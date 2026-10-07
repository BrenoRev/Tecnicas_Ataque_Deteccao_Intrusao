## Escopo
Uma frase: o que esta mudança entrega.

## O que demonstra
Caminho do artefato em `results/` ou `report/`, ou o comportamento novo e como vê-lo.

## Como verificar
    uv run pytest
    uv run python scripts/<script>.py

## Verificação com dados reais
Saída das asserções do script na máquina de quem tem os dados, ou "não se aplica".

## Checklist
- [ ] lint, formatação e testes verdes
- [ ] nenhum dado, modelo serializado ou PDF adicionado
- [ ] mensagens de commit no padrão, sem coautoria
- [ ] resultado em `results/` gerado por script, com `run.json` e árvore limpa
