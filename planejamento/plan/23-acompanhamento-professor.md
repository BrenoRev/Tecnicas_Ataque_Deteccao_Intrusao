# 23 · acompanhamento · perguntas ao professor e material de 10/11 e 17/11

**Onde:** `docs/07-pendencias.md`; uma página de status em `planejamento/`
**Objetivo:** as respostas que podem mudar o plano chegam cedo, e os dois encontros de acompanhamento são usados para corrigir rumo com material concreto.
**Depende de:** — para as perguntas (onda 0); 08 para o material de 10/11
**Demonstra:** respostas do professor registradas com data; página de status e tabela de resultados para 10/11; rascunho para 17/11.

## Reconciliado com as respostas do professor (07/10/2026, commit `360c3d3`)

- Q1 a Q6 respondidas em 07/10/2026 e registradas em `docs/07-pendencias.md`, com o efeito de cada uma: Q1, reimplementação aceita; Q2, decisão 46; Q3, decisão 48 (sem requisito adicional: o passo 3 não se aplica por ora); Q4, decisão 47; Q5, decisão 49; Q6, decisão 50. As tarefas afetadas foram atualizadas nesta reconciliação.
- Q9 (idioma e limite de páginas), Q10 (repositório público ou privado) e a parte em aberto de Q7 (frase de declaração do uso de IA) ficaram sem resposta do professor e foram fechadas pela equipe em 08/10/2026 (decisão 55a): português, até 8 páginas; repositório público; sem frase. Não são respostas dele.
- **Para levar ao professor, porque ele não comentou ou pediu conversa:** (1) as duas ressalvas de Q4: Non-DoH e Benign-DoH do combinado são os do CIRA, e o combinado publicado replica o HKD; (2) Q5: ele pediu que a equipe explicasse melhor depois da aula; a equipe decidiu fazer (decisão 49) e leva o método adotado; (3) Q2: ele não disse qual referência vale entre a Tabela II e a Fig. 4b nem deu margem; (4) as duas leituras de profundidade (decisão 45) e o resultado da leitura de profundidade 5.
- Material de 10/11: a página `docs/09-acompanhamento-professor.md` (`ba9ddc4`, `4de9ab2`), com a seção "Execução limpa" preenchida em `5999c1b`.
- **Situação em 08/10/2026: concluída; resta de pessoa** levar a página aos encontros de 10/11 e 17/11 e registrar o retorno de cada um. Os quatro pontos acima foram fechados pela equipe sem resposta do professor (decisão 55a) e continuam na página, para o caso de ele dizer outra coisa.

## O que fazer

1. (Feito em 07/10/2026.) Enviar ao professor, por escrito, as perguntas de `docs/07-pendencias.md:11-21`: foram Q1 a Q6, Q9, Q10 e a parte em aberto de Q7, em uma mensagem só.
2. Registrar cada resposta em `docs/07-pendencias.md`, com a data. Para cada resposta, conferir a tabela "Pendentes de terceiros" de `planejamento/MEMORY/00-decisoes-travadas.md`: se a resposta contraria a premissa assumida, marcar `⚠️ REVISAR` na tarefa afetada e levar a decisão ao grupo.
3. Se o professor informar requisito adicional para este artigo (Q3), propor a tarefa nova e sua posição no grafo antes de implementar.
4. **Para 10/11:** uma página com o que funciona, o que falta e o que travou; a tabela de resultados que existir (reprodução ao lado da Fig. 4b, segundo dataset); a lista de decisões que dependem dele; e o resultado da primeira execução limpa (tarefa 19).
5. **Para 17/11:** o rascunho do relatório e as dúvidas que restarem.
5a. Não se aplica (decisão 44): nada rodou no Apuana.
6. Depois de cada encontro, registrar o retorno recebido e convertê-lo em ajuste de tarefa.

## Por quê

Sete perguntas em aberto podem mudar o escopo: se a reimplementação vale como reprodução (Q1), qual é o alvo (Q2), se o segundo dataset é aceito (Q4). Uma resposta negativa a Q4 em novembro não deixa tempo para trocar de dataset. A especificação também avisa que pode haver requisito adicional por artigo.

## Evidência — verificada no baseline

- `docs/07-pendencias.md:11-21` — perguntas Q1 a Q11.
- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:32` — "requisitos adicionais podem ser exigidos especificamente para cada artigo escolhido".
- `planejamento/MEMORY/00-decisoes-travadas.md`, "Pendentes de terceiros" — qual decisão cada resposta pode mudar.
- Calendário da disciplina: acompanhamento de projeto em 10/11 e 17/11.

## Risco

- O professor não responder por escrito: levar as perguntas impressas à aula seguinte e registrar a resposta oral, com a data e quem ouviu.
- Resposta que invalida uma premissa: o plano isola o impacto (seção "O que resta" de `00-README.md`); nenhuma resposta desfaz as tarefas 01 a 07.

## Critério de aceite

- [x] Mensagem enviada em 07/10/2026, com Q1 a Q6, Q9, Q10 e a parte em aberto de Q7; cópia em `docs/07-pendencias.md`.
- [x] Cada resposta registrada com data, e as tarefas afetadas atualizadas ou marcadas. **Fechado em 08/10/2026:** Q1 a Q6 registradas com data em `docs/07-pendencias.md` (lido) e levadas às tarefas em `360c3d3`; Q9, Q10 e a parte em aberto de Q7 não tiveram resposta e foram fechadas pela equipe (decisão 55a), com isso dito em cada tarefa afetada (18, 19, 21).
- [x] Página de status e tabela de resultados prontas na véspera de 10/11. **Fechado em 08/10/2026:** `docs/09-acompanhamento-professor.md` existe desde `ba9ddc4`, com a seção "Execução limpa" preenchida em `5999c1b` (lido: 22 passos, 7 h 30 min). A própria página pede para conferir os números de novo na véspera.
- [ ] **Pessoa:** encontros com o professor em 10/11 e 17/11, com o retorno de cada um registrado em `docs/07-pendencias.md` e convertido em ajuste (item 4 de "O que resta de pessoa").

## Testes

Sem teste automático. Critério de aceite conferido por outro integrante.

## Verificação ao concluir

Gate de organização: G8, G10.
