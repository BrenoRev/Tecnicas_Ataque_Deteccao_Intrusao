# Fluxo de implementação

Uma tarefa por vez: desenvolve, testa, revisa, integra. Só então a próxima.

## Ciclo de uma tarefa

| Passo | Quem | O que acontece | Só avança se |
| --- | --- | --- | --- |
| 1. Preparar | sessão principal | Dentro de `project/`: confere as dependências em `planejamento/plan/00-README.md` e os bloqueios externos; cria a branch `tarefa/NN-nome` | Dependências concluídas e integradas; nenhum bloqueio aberto que trave a tarefa |
| 2. Implementar | agente `implementador` | Lê a tarefa e a seção dela no plano de testes; escreve o código e os testes previstos; commits pequenos | Critério de aceite coberto |
| 3. Testar | agente `implementador` | Roda o gate automático e, se a tarefa usa dados reais, a verificação local | Tudo verde, com a saída dos comandos no relato |
| 4. Revisar | agente `revisor-metodologico` ou `revisor-de-texto` | Revisão independente do diff | Nenhum achado bloqueante |
| 5. Corrigir | agente `implementador` | Trata os achados e repete o passo 3 | Verde de novo |
| 6. Integrar | integrante da equipe | Lê o pull request (descrição no modelo do repositório: o que demonstra, como verificar, verificação com dados reais), confere o CI e aprova | CI verde e aprovação humana |
| 7. Sincronizar | agente `cin0114-plan-sync` | Marca a tarefa como concluída e reconcilia as seguintes | Plano atualizado |

A skill `implementar` conduz os passos 1 a 5 e o 7. O passo 6 é sempre de uma pessoa.

## Regras do ciclo

- **Não se começa a tarefa seguinte com a anterior vermelha.** Teste falhando, lint falhando ou achado bloqueante em aberto param a fila.
- A cada tarefa roda a suíte inteira, não só os testes novos. Regressão em teste antigo é defeito da tarefa atual.
- Teste que falha é consertado no código. Não se apaga teste, não se afrouxa asserção e não se marca `skip` para passar.
- Se o critério de aceite não pode ser cumprido como escrito, o implementador para e relata. Ele não reinterpreta a tarefa.
- Resultado longe do artigo não é falha de teste. Registra-se a distância e segue-se o plano.
- Tarefa de dados e de experimento só fecha com a verificação local executada por quem tem os datasets, com a saída colada no pull request.
- Execução encadeada: quando o usuário pede para seguir sem esperar a integração, a branch da tarefa seguinte nasce da branch da anterior, isso fica dito no relato, e os pull requests são integrados na ordem.
- Cada tarefa tem um dono, que roda o ciclo na própria máquina com a própria identidade Git.

## Quando parar e chamar o usuário

- Dependência não concluída ou bloqueio externo sem resposta.
- A implementação exigiria contrariar uma decisão travada.
- Falta uma informação que a tarefa não traz: nome real de coluna, arquivo de dados, resposta do professor.
- O gate continua vermelho depois de três tentativas de correção.
- O trabalho pede mudança fora dos arquivos listados na tarefa.

## Dois fechamentos em tarefa de experimento (decisão 42)

Vale para as tarefas 08 a 16.

- **Pronta:** código, testes N1 e revisão sem bloqueante.
- **Executada:** o script rodou com os dados reais, na máquina local ou no cluster Apuana. As duas formas valem; o importante é treinar e gerar a evidência: resultados em commit `exp` de quem rodou, com a árvore limpa, `run.json` com a máquina e a saída no pull request.
- A tarefa seguinte pode começar com a anterior "pronta", desde que não dependa de resultado real. Dependem de resultado real: a 05 (saída da 04), a 11 (resultados da 08 e da 09), a 15 (`results/e4/`) e a 17 (todos).
- "Pronta" sem "executada" não vira número no relatório.

## O que é "pronto"

1. Critério de aceite da tarefa conferido item a item.
2. Testes da seção correspondente do plano de testes escritos e verdes.
3. Gate de `planejamento/plan/VERIFICACAO.md` verde para o tipo da tarefa.
4. Revisão automática sem achado bloqueante.
5. Commits no padrão, na branch da tarefa.

"Integrada" é o passo seguinte: pull request aprovado por outro integrante, com o CI verde.
