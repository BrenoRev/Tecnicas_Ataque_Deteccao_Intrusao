# 20 · entrega · slides e apresentação do projeto (só com P3)

> **Execução (07/10/2026):** a apresentação é produzida pela tarefa [24](24-entrega-pdfs-finais.md), com o agente `gerador-entregaveis` e os modelos de `geracao_latex_and_pdf/`. Este arquivo continua valendo para o conteúdo exigido e a lista de conferência; em tamanho e formato vale a tarefa 24 (relatório: alvo de 6 páginas, teto de 8; apresentação: 12 a 14 slides em PPTX, para o Google Slides; a apresentação é feita mesmo sem a modificação).

> **Cumprida pela tarefa 24 (08/10/2026, commit `759ec29`):** `report/apresentacao.pptx`, 14 slides, e `report/roteiro.md`, 11 min 55 s, gerados por `scripts/make_slides.py` e revistos pelo `revisor-de-texto`. `report/slides_projeto.pdf` não existe: a entrega é o `.pptx`. **Resta, de pessoa:** abrir no Google Slides e conferir o layout; confirmar a divisão da fala proposta no roteiro; ensaio cronometrado; confirmar com o professor o que a apresentação cobre (passo 1).

**Onde:** modelo de apresentação do CIn (Google Slides); PDF em `report/`
**Objetivo:** apresentação de 15 minutos em 19/11/2026, exigida das equipes que modificaram o artigo original.
**Depende de:** 15, 17
**Demonstra:** slides no modelo do CIn com números vindos de `report/`. Entregável de 19/11, se P3.

> Só existe se a tarefa 15 foi concluída. Se P3 for cortado, esta tarefa sai junto.

## Reconciliado com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

- **Decisão 50:** o painel interativo da tarefa 12 é material de demonstração e pode entrar na apresentação, ao vivo ou em captura de tela. Se entrar ao vivo, o ensaio do passo 5 é feito com o painel já no ar, porque o script treina o modelo antes de subir (cerca de 3 minutos, pelo tempo de ajuste medido na tarefa 08). Os números ditos em sala continuam vindo de `report/`, não do painel.
- **Decisão 45:** o bloco da reprodução mostra as duas leituras de profundidade lado a lado e diz qual foi usada como base e por quê.
- **Decisões 46, 47 e 49:** o roteiro do passo 2 ganha a ferramenta de túnel (Seção VI-D) no bloco da reprodução, e o bloco do segundo dataset passa a ser "P1 refeito no combinado sem réplicas", com transferência e combinado publicado ao lado.

## Arquivos

- Cópia do modelo institucional do CIn (`https://docs.google.com/presentation/d/1lAaS3mgRNcWwQmUez8e8s4JKzim4ZwwWh7RCAwCoNyo/edit`).
- `report/slides_projeto.pdf` — exportado.

## O que fazer

1. Confirmar com o professor o que a apresentação deve cobrir. A especificação diz só "slides de apresentação e apresentação de 15 minutos"; a proposta abaixo assume foco no que é novo em relação ao seminário.
2. Roteiro proposto, com o tempo de cada bloco:
   - o que o artigo propõe, em um slide (a turma já viu o seminário);
   - a reprodução: o que deu para reproduzir, a distância até a Fig. 4b, as ambiguidades que pesaram;
   - o segundo dataset: transferência e retreino, recall por ferramenta;
   - a modificação: hipótese, o que mudou, resultado contra o original nos dois datasets;
   - limitações e o que faríamos em seguida.
3. Só tópicos, bullets e imagens. Gráficos e tabelas vêm da tarefa 17; nenhum número digitado.
4. Dividir a fala entre os quatro e distribuir as perguntas prováveis.
5. Ensaiar cronometrando.
6. Rodar o agente `revisor-de-texto` sobre os slides.

## Por quê

A especificação exige slides e apresentação de quem faz a modificação opcional. É o custo de P3 que não aparece no código.

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:35` — exigência e data.
- Mesma especificação, `:40` — modelo institucional do CIn.
- Mesma especificação, `:54` — tópicos, bullets e imagens; textos longos evitados (regra escrita para o seminário, adotada aqui).

## Risco

- Repetir o seminário e ficar sem tempo para a modificação: um slide para o artigo, no máximo.
- Um dia entre a entrega do relatório e a apresentação: os slides começam quando a tarefa 15 fecha, não em 18/11.

## Critério de aceite

- [ ] Slides no modelo do CIn, exportados em PDF.
- [ ] Todo número e todo gráfico vem de `report/tables/` ou `report/figures/`.
- [ ] Ensaio em até 15 minutos, com a divisão de fala registrada.
- [ ] `revisor-de-texto` sem achado grave em aberto.

## Testes

Sem teste automático. Seção "Tarefa 20" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): revisão N3 pelo `revisor-de-texto`; todo número conferido contra `results/`; ensaio cronometrado.

## Verificação ao concluir

Gate de texto: G8, G9 (`revisor-de-texto`), G10. Itens de apresentação da skill `checklist-entrega projeto`.
