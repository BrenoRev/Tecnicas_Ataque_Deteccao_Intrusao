# STATUS — plano de implementação do projeto CIN0114

Tier: médio · Tipo de entrega: análise implementável · Atualizado: 08/10/2026, no commit `5999c1b` (branch `tarefa/19-readme-execucao-limpa`)

## Fase atual

Concluído; resta o que é de pessoa. O projeto está implementado, executado com os dados reais em 07 e 08/10/2026, nesta máquina (decisão 44), regenerado do zero pela execução limpa e revisado em código, sem achado bloqueante. Os entregáveis estão em `project/report/`, com cópia em `entregaveis-apresentacao/`.

A integração foi por avanço direto da `main`, sem pull request por tarefa (decisão 55f). `main` e `origin/main` estão em `378f170`; os 15 commits seguintes, até `5999c1b` (revisão final, tratamento dos achados e registro da execução limpa), estão na branch local e ainda não foram enviados ao GitHub.

## Coberto

Planejamento:

- [x] Intake, regras, stack, domínio, síntese, red-team e segunda revisão independente → `MEMORY/`
- [x] Decisões 01 a 55 → `MEMORY/00-decisoes-travadas.md` (43 a 55 tomadas durante a implementação)
- [x] Plano com 25 tarefas, gate, plano de testes e mapa de entregas → `plan/`
- [x] Regras de código, commit, teste, fluxo e experimento → `.claude/rules/`; agentes e skills em `.claude/`

Implementação (situação por tarefa em `plan/00-README.md`, mantido pelo agente `cin0114-plan-sync`):

- [x] Fundação: ambiente com `uv`, hooks, CI, `config.py`, `runlog.py` (tarefas 01 e 02)
- [x] Dados do CIRA: manifesto, carga, limpeza, split, Fig. 2 → `project/results/e0/dados/RESUMO.md` (03 a 05)
- [x] Métricas e subconjuntos balanceados (06, 07)
- [x] E1, reprodução nas duas leituras de profundidade → `project/results/e1/RESUMO.md` (08)
- [x] E2, Tabela II inteira → `project/results/e2/fiel/RESUMO.md` (09)
- [x] E3, sensibilidade, dez recortes → `project/results/e3/variante/RESUMO.md` (10)
- [x] E4, protocolo corrigido em dez seeds e avaliação por máquina → `project/results/e4/corrigida/RESUMO.md` (11)
- [x] E5, SHAP e painel interativo → `project/results/e5/RESUMO.md`, `project/scripts/painel_xai.py` (12)
- [x] E6, segundo dataset → `project/results/e6/RESUMO.md`, `project/results/e6/dados/RESUMO.md` (13, 14)
- [x] E7, ferramenta de túnel e Fig. 9 → `project/results/e7/RESUMO.md` (21)
- [x] E8, modificação M1 + M2 e robustez à duração → `project/results/e8/corrigida/RESUMO.md` e `RESUMO-ROBUSTEZ.md` (15, 16)
- [x] Tabelas e figuras por script → `project/report/tables/`, `project/report/figures/`, `project/report/INDICE.md` (17)
- [x] Relatório e apresentação → `project/report/relatorio.tex`, `relatorio.pdf` (8 páginas), `apresentacao.pptx` (14 slides), `roteiro.md` (11 min 55 s; apresentam Amanda, Antonio e João) (24, que cumpre a 18 e a 20)
- [x] README e execução limpa → `project/README.md` (22 passos), `README.md` da raiz, `LICENSE`; execução limpa em 08/10/2026, em clone novo, 7 h 30 min, 260 de 260 arquivos de `results/` e 56 de 56 de `report/` (`plan/REVISAO-FINAL.md`, "Execução limpa") (19)
- [x] Padrões que nasceram na implementação → `.claude/rules/experimentos.md` (22)
- [x] Página de status para os encontros com o professor → `docs/09-acompanhamento-professor.md` (23; os encontros são de pessoa)
- [x] Revisão final em código: nenhum bloqueante; cinco achados importantes e nove menores, todos tratados; suíte com 118 testes → `plan/REVISAO-FINAL.md` (25)
- [x] Respostas do professor a Q1 a Q6 registradas em `docs/07-pendencias.md` (07/10/2026); Q9, Q10 e a parte aberta de Q7 fechadas pela equipe, sem resposta dele (decisão 55a)
- [x] `docs/` e `MEMORY/` reconciliados com o repositório em `5999c1b` (`SYNC-BASELINE.md`)

## O que resta

Não há lista aqui. A lista única e viva é a seção "O que resta de pessoa" de `docs/07-pendencias.md`, com doze itens em `5999c1b`: envio dos commits finais e avanço da `main`; ensaio; seminário (com Q8 e Q11); encontros de 10/11 e 17/11; entrega em 18/11; apresentação em 19/11 e arguição; leitura do relatório pelos quatro; proteção da `main` e acessos no GitHub; os dois `[Preencher]` da mensagem ao professor; D6; a citação do dataset CIRA; e a instalação por `requirements.txt` com pip, que é o único item que não é de pessoa.

## ⚠️ REVISAR: situação

Nenhum aberto. Nenhuma decisão foi reescrita.

| Decisão | O que ela diz | O que foi medido ou feito | Situação |
| --- | --- | --- | --- |
| 23 e 52 | "A contra B isola a arquitetura" | A e B diferem também no balanceamento: em A cada base vê um terço do Non-DoH e só Benign-DoH é aumentada; em B o SMOTE iguala as duas classes menores ao Non-DoH inteiro. A diferença mede as duas coisas juntas (`project/results/e4/corrigida/RESUMO.md`, "Protocolo" e "Hipótese ao lado do resultado") | **Resolvido** (decisão 55e, o usuário manteve as decisões): o texto das decisões fica como registro histórico; o relatório e `project/results/e4/corrigida/RESUMO.md` trazem a formulação correta |
| 38 | Hipótese de cada experimento em `HIPOTESE.md`, em commit anterior à primeira execução; interpretação em `results/<experimento>/<trilha>/RESUMO.md` | E3 e E7 rodaram sem `HIPOTESE.md`; E7 tem um só `RESUMO.md`, no nível do experimento; E8 tem dois pares no mesmo nível, com o sufixo `-ROBUSTEZ` | **Resolvido**: declarados nos resumos (`project/results/e3/variante/RESUMO.md`, `project/results/e7/RESUMO.md`) e registrados em `.claude/rules/experimentos.md`, regra 3, que fixa a hipótese em commit anterior e o sufixo no nome para o segundo experimento da mesma pasta |
| 10, 19, 20 | Alvo principal Fig. 4b; painel só se o professor exigir; ferramenta de túnel fora | Superadas pelas decisões 46, 50 e 49, do usuário, depois das respostas a Q2, Q6 e Q5 | **Resolvido**: não há contradição em vigor; as decisões novas são do usuário e o texto das três antigas fica como registro histórico (`MEMORY/00-decisoes-travadas.md`, tabela "Pendentes de terceiros") |

## Achados da execução que mudam o que se pode afirmar

Só ponteiros; os números estão nos resumos.

- Com profundidade máxima 5 (Seção IV-B), o modelo empilhado tem recall 0 em Benign-DoH no teste; sem limite de profundidade (Algoritmo 1), fica perto da Fig. 4b sem igualá-la. As duas leituras são reportadas (`project/results/e1/RESUMO.md`).
- A árvore de decisão reproduzida fica muito acima da linha dela na Tabela II (`project/results/e2/fiel/RESUMO.md`).
- A transferência do CIRA para o HKD tem recall perto de zero, sem nenhum valor fora da faixa do normalizador; `PacketLengthMode` separa as duas capturas (`project/results/e6/RESUMO.md`).
- No retreino sem réplicas, os fluxos do HKD do teste estão muito próximos de fluxos do HKD do treino: o recall não estima a detecção de uma sessão de túnel que o treino não tenha (`project/results/e6/dados/RESUMO.md`).
- Nas dobras por máquina, o recall de Benign-DoH do modelo A cai para cerca de um terço do medido no split aleatório (`project/results/e4/corrigida/RESUMO.md`, "Avaliação por máquina").
- A legenda da Fig. 9 só é reproduzida com os arquivos por ferramenta sem a limpeza: indício de que a Seção VI-D usou outros dados (`project/results/e7/RESUMO.md`).
- A robustez de E8 é perturbação no espaço de atributos, com vetores incoerentes em fração crescente; não é medição de ataque (`project/results/e8/corrigida/RESUMO-ROBUSTEZ.md`).

## Não feito, por decisão ou declarado

- Cluster Apuana: não usado; a pasta `jobs/` não existe (decisão 44).
- Pull request por tarefa, revisão por outro integrante e quatro autores no histórico: não feitos (decisões 55d e 55f).
- Execução limpa por quem não escreveu o código ou em outra máquina: não feita; rodou na sessão de implementação, em clone novo (decisões 44 e 55d).
- One-sided selection, meta com predições fora da amostra, modelo com 28 atributos no total: não medidos (`project/results/e3/variante/RESUMO.md`).
- Explicabilidade do modelo modificado: fora (decisão 54, item f).
- Estimativa de horas e cards em ferramenta de gestão: não pedidos.

## Lacunas

O que a revisão final declara não ter verificado está em `plan/REVISAO-FINAL.md`, "O que a revisão não verificou, e por quê". Além disso:

- Citação do dataset CIRA: duas formas registradas, nenhuma conferida na fonte (`docs/04-dados.md`; item 11 da lista única).
- Instalação por `requirements.txt` com pip: sem registro de teste (item 12 da lista única).
- Dataset alternativo com tráfego benigno próprio: não avaliado (`docs/04-dados.md`).
- Python 3.14: não testado; o projeto fixa 3.12.

## Próximo passo

1. Enviar os commits finais e avançar a `main`; conferir o CI no commit final.
2. Seminário: ajustes do material, slides em 14/10, apresentação em 15 ou 20/10.
3. Encontros com o professor em 10/11 e 17/11, com a página `docs/09-acompanhamento-professor.md`; registrar o retorno.
4. Entrega em 18/11 (checklist, envio e comprovante) e apresentação em 19/11.

## Baseline

ver `SYNC-BASELINE.md` e `plan/SYNC-BASELINE-PLAN.md`
