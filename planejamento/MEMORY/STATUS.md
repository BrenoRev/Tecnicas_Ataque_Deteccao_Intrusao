# STATUS — plano de implementação do projeto CIN0114

Tier: médio · Tipo de entrega: análise implementável · Atualizado: 08/10/2026, no commit `759ec29` (branch `tarefa/24-entregaveis`)

## Fase atual

Implementação concluída e executada; falta integrar, conferir e entregar. Todos os experimentos (E0 a E8) rodaram com os dados reais em 07 e 08/10/2026, nesta máquina (decisão 44), e o relatório e a apresentação foram gerados (tarefa 24). Nada está na `main`: `origin/main` e a `main` local estão em `6bf80bd`, e cada tarefa está na própria branch, encadeada na anterior, à espera de pull request. O que resta é quase todo de pessoa.

## Coberto

Planejamento:

- [x] Intake, regras, stack, domínio, síntese, red-team e segunda revisão independente → `MEMORY/`
- [x] Decisões 01 a 54 → `MEMORY/00-decisoes-travadas.md` (43 a 54 tomadas durante a implementação)
- [x] Plano com 24 tarefas, gate, plano de testes e mapa de entregas → `plan/`
- [x] Regras de código, commit, teste e fluxo → `.claude/rules/`; agentes e skills em `.claude/`

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
- [x] Relatório e apresentação → `project/report/relatorio.tex`, `relatorio.pdf` (8 páginas), `apresentacao.pptx` (14 slides), `roteiro.md` (24, que cumpre a 18 e a 20)
- [x] Respostas do professor a Q1 a Q6 registradas em `docs/07-pendencias.md` (07/10/2026)
- [x] `docs/` e `MEMORY/` reconciliados com o código em 08/10/2026 (`SYNC-BASELINE.md`)

## Faltando

Tarefas do plano:

- [ ] **19** — README de `project/` com a ordem dos scripts e a tabela resultado → script → arquivo (hoje ele diz que os scripts "serão listados"), execução limpa por quem não escreveu o código, instalação por `requirements.txt` testada, checklist de entrega
- [ ] **22** — padrões que nasceram na implementação, registrados ou dispensados com justificativa
- [ ] **23** — acompanhamentos de 10/11 e 17/11 com o professor

De pessoa (lista com detalhe em `docs/07-pendencias.md`, seção "O que resta de pessoa", e em `POS-IMPLEMENTACAO.md`):

- [ ] `push` das branches que faltam e pull requests na ordem das tarefas, com revisão de outro integrante e CI verde
- [ ] Conferência por dois integrantes das transcrições em `config.py`: metade inferior da Tabela II, `FIG5_RANKING`, `FIG7_MALICIOUS`, `FIG8_NON_DOH`
- [ ] Licença do repositório
- [ ] DOI e conferência das referências, incluindo a citação do dataset CIRA (diverge entre `docs/04-dados.md` e a lista do artigo)
- [ ] Conferir o PPTX no Google Slides; ensaio cronometrado; confirmar a divisão da fala
- [ ] Relatório no Overleaf, compilado com XeLaTeX, conferido contra o template do professor
- [ ] Conversa com o professor: duas leituras de profundidade; o combinado como "outro dataset"; Q5
- [ ] Respostas a Q9, Q10 e à parte em aberto de Q7
- [ ] Dono, revisor e integrador de cada pull request (D5): os 137 commits até `759ec29` são de uma só identidade Git

## ⚠️ REVISAR: fatos da execução que não batem com o texto de uma decisão travada

Nenhuma decisão foi reescrita. Os três pontos abaixo ficam para o usuário.

| Decisão | O que ela diz | O que foi medido ou feito | Fonte |
| --- | --- | --- | --- |
| 23 e 52 | "A contra B isola a arquitetura" | A e B diferem também no balanceamento: em A cada base vê um terço do Non-DoH e só Benign-DoH é aumentada; em B o SMOTE iguala as duas classes menores ao Non-DoH inteiro. A diferença mede as duas coisas juntas | `project/results/e4/corrigida/RESUMO.md`, "Protocolo" e "Hipótese ao lado do resultado"; comentário de `CORRIGIDA_MODELS` em `config.py` |
| 38 | Hipótese de cada experimento em `HIPOTESE.md`, em commit anterior à primeira execução; interpretação em `results/<experimento>/<trilha>/RESUMO.md` | E3 e E7 rodaram sem `HIPOTESE.md`, e os resumos declaram isso. E7 tem um só `RESUMO.md`, no nível do experimento; E8 tem dois pares no mesmo nível (`HIPOTESE.md`/`RESUMO.md` e `HIPOTESE-ROBUSTEZ.md`/`RESUMO-ROBUSTEZ.md`) | `project/results/e3/variante/RESUMO.md`, `project/results/e7/RESUMO.md`, `project/results/e8/corrigida/` |
| 10, 19, 20 | Alvo principal Fig. 4b; painel só se o professor exigir; ferramenta de túnel fora | Superadas pelas decisões 46, 50 e 49, do usuário, depois das respostas a Q2, Q6 e Q5. O texto das três continua como estava | `MEMORY/00-decisoes-travadas.md`, tabela "Pendentes de terceiros" |

## Achados da execução que mudam o que se pode afirmar

Só ponteiros; os números estão nos resumos.

- Com profundidade máxima 5 (Seção IV-B), o modelo empilhado não prediz Benign-DoH no teste; sem limite de profundidade (Algoritmo 1), fica perto da Fig. 4b sem igualá-la. As duas leituras são reportadas (`project/results/e1/RESUMO.md`).
- A árvore de decisão reproduzida fica muito acima da linha dela na Tabela II (`project/results/e2/fiel/RESUMO.md`).
- A transferência do CIRA para o HKD tem recall perto de zero, sem nenhum valor fora da faixa do normalizador; `PacketLengthMode` separa as duas capturas (`project/results/e6/RESUMO.md`).
- No retreino sem réplicas, os fluxos do HKD do teste estão muito próximos de fluxos do HKD do treino: o recall não estima a detecção de uma sessão de túnel que o treino não tenha (`project/results/e6/dados/RESUMO.md`).
- Nas dobras por máquina, o recall de Benign-DoH do modelo A cai para cerca de um terço do medido no split aleatório (`project/results/e4/corrigida/RESUMO.md`, "Avaliação por máquina").
- A legenda da Fig. 9 só é reproduzida com os arquivos por ferramenta sem a limpeza: indício de que a Seção VI-D usou outros dados (`project/results/e7/RESUMO.md`).
- A robustez de E8 é perturbação no espaço de atributos, com vetores incoerentes em fração crescente; não é medição de ataque (`project/results/e8/corrigida/RESUMO-ROBUSTEZ.md`).

## Não feito, por decisão ou declarado

- Cluster Apuana: não usado; a pasta `jobs/` não existe (decisão 44).
- One-sided selection, meta com predições fora da amostra, modelo com 28 atributos no total: não medidos (`project/results/e3/variante/RESUMO.md`).
- Explicabilidade do modelo modificado: fora (decisão 54, item f).
- Estimativa de horas e cards em ferramenta de gestão: não pedidos.

## Lacunas

- Citação do dataset CIRA: duas formas registradas, nenhuma conferida na fonte (`docs/04-dados.md`).
- Template Overleaf do professor: o relatório foi feito sobre `geracao_latex_and_pdf/template.tex` (decisão 53); idioma e limite de páginas seguem sem resposta (Q9).
- Segunda execução com `metrics.json` idêntico (gate G6): não conferida nesta sincronização.
- Python 3.14: não testado; o projeto fixa 3.12.

## Próximo passo

1. Equipe: `push` e pull requests na ordem das tarefas, cada um lido por outro integrante.
2. Equipe: conferir as transcrições de `config.py` e a citação do CIRA; escolher a licença.
3. `/implementar 19` (README e execução limpa), depois a 22.
4. Levar ao acompanhamento de 10/11 as duas leituras de profundidade, a ressalva do combinado e Q5.

## Baseline

ver `SYNC-BASELINE.md` e `plan/SYNC-BASELINE-PLAN.md`
