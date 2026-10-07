# 15 · P3 · modificação proposta: M1 + M2 (E8)

**Onde:** `src/doh_ids/models.py`, `src/doh_ids/config.py`, `scripts/e8_modificacao.py`, `tests/test_models.py`, `results/e8/corrigida/`
**Objetivo:** uma versão do sistema que ataca as fraquezas apontadas no seminário, avaliada contra o original nos dois datasets. É o item opcional que vale ponto extra.
**Depende de:** 11, 12, 14
**Demonstra:** `results/e8/corrigida/summary.json`: original contra modificado nos dois datasets, dez seeds, com `HIPOTESE.md` anterior aos números. P3 (seções 5 e 7).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- No segundo dataset (passo 6), as dez seeds rodam sobre o combinado **sem réplicas**. No combinado como publicado, o HKD replicado 20 vezes tornaria a comparação entre A e M1+M2 uma comparação de memorização.

## Arquivos

- `src/doh_ids/models.py` — acrescentar o construtor do modelo modificado.
- `src/doh_ids/config.py` — a grade de M2, em commit anterior à primeira execução.
- `scripts/e8_modificacao.py` — novo.
- `tests/test_models.py` — acrescentar T15-1 a T15-4.
- `results/e8/corrigida/HIPOTESE.md` — escrita antes de rodar, em commit anterior.
- `results/e8/corrigida/<modelo>-<dataset>/seed<k>/`, `summary.json` e `RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento` para E8, trilha corrigida. Escrever a hipótese em `results/e8/corrigida/HIPOTESE.md` antes de rodar, em commit anterior à primeira execução: o que se espera melhorar e o que contaria como não ter melhorado.
2. **Modelo modificado, fixado antes de qualquer resultado (decisão 25):** um Random Forest único, sem SMOTE, com `class_weight='balanced'` (M1) e hiperparâmetros selecionados por validação cruzada dentro do treino (M2). A divisão em três subconjuntos existe no artigo para repartir o custo do SMOTE; sem SMOTE ela perde a razão de ser, e por isso o modelo modificado não a mantém. Essa escolha de arquitetura não depende dos resultados da tarefa 11.
3. **Seleção de hiperparâmetros (M2), aninhada por seed.** Grade pequena, declarada em `config.py` antes de rodar, com no máximo oito combinações de profundidade, número de árvores e `max_features`, incluindo os valores do artigo (5, 10, 28) (`[Decidir: a grade; proposta em "Pendentes da equipe"]`). Validação cruzada estratificada de 5 folds dentro do treino da seed, com um `Pipeline` cujo primeiro passo é o `MinMaxScaler`, de modo que o scaler é reajustado em cada fold. Métrica de seleção: F1 macro. O teste da seed não participa.
4. Antes de lançar tudo, cronometrar uma combinação em uma seed e estimar o total. Se passar do que cabe em uma noite, fazer a seleção em uma subamostra estratificada do treino, de fração declarada em `config.py` (`[Decidir: fração; proposta em "Pendentes da equipe"]`), e dizer isso no relatório.
5. Modelos avaliados, dez seeds, mesmos splits da tarefa 11:

| Modelo | O que é | Para que serve |
| --- | --- | --- |
| A (original) | Empilhado com os valores do artigo; lido de `results/e4/` | Referência |
| M1 | Random Forest único, `class_weight`, hiperparâmetros do artigo (10, 5, 28) | Efeito de tirar o SMOTE |
| M1+M2 | Random Forest único, `class_weight`, hiperparâmetros selecionados | O modelo proposto pela equipe |

6. **Segundo dataset, dez seeds.** Rodar A e M1+M2 no combinado: split 90/10 por seed, scaler e seleção de hiperparâmetros refeitos dentro do treino do combinado (não se reaproveita o que foi selecionado no CIRA, porque as linhas do CIRA estão dentro do combinado). Para o CIRA, medir também a transferência ao HKD com M1+M2.
7. Comparação pareada por seed com o modelo A, pelo método da decisão 24: recall de Benign-DoH, F1 macro, FPR da classe maliciosa, tempo de treino. Mesma ressalva de dependência entre os pares.
7a. Métricas com e sem as linhas do teste duplicadas no treino, em toda seed, e a comparação pareada nas duas versões, como na tarefa 11: com 13,7% do teste repetido no treino, um modelo mais profundo pode vencer por memorizar duplicatas, e a seleção por validação cruzada também vê duplicatas entre folds. Declarar isso no `RESUMO.md`.
8. Explicabilidade do modelo M1+M2: importância global com `TreeExplainer`, como na tarefa 12, e se o ranking mudou. Aqui a explicação é do modelo que decide, sem a limitação do empilhamento.
9. Escrever o resultado como está. Se não melhorar, a seção 5 do relatório relata a tentativa e a análise do porquê.

## Por quê

Objetivo P3 e decisões 02 e 25. M1 responde à crítica de que cerca de 92% da classe benigna de treino é sintética. M2 responde à crítica de que `max_features` de 28 em 29 anula a aleatorização do Random Forest, e ao recall de 90% na classe benigna, que os números de treino indicam ser viés. Um modelo único também pode ser explicado diretamente pelo `TreeExplainer`, o que o empilhamento não permite.

## Evidência — verificada no baseline

- `docs/05-plano-experimental.md:110-121` — candidatas M1 a M4 e recomendação.
- `docs/02-artigo.md:77` — recall de Benign-DoH de 89,7% no treino e 90,2% no teste.
- `docs/04-dados.md:48` — estimativa de 92% de benignos sintéticos.
- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:30` e `:83-87` — o item opcional e as perguntas da seção 5 do relatório.
- Mesma especificação, `:35` — modificação obriga slides e apresentação em 19/11.
- `planejamento/MEMORY/04-red-team.md`, achados F1 a F5 — por que a arquitetura é fixada antes, a seleção é aninhada e o ajuste de limiar foi retirado.

## Risco

- A modificação não melhorar, ou melhorar dentro do desvio. É resultado reportável; o ponto extra é pela proposta implementada e avaliada.
- Custo da seleção aninhada: sem SMOTE, cada ajuste é um Random Forest sobre o treino; o passo 4 mede antes de lançar.
- Escopo crescer: a tabela do passo 5 é fechada. A variante "só M2" (SMOTE com hiperparâmetros selecionados) e o ajuste de limiar ficaram de fora de propósito.
- Prazo: se a tarefa 11 não estiver fechada em 09/11, cortar esta tarefa e a 20.

## Critério de aceite

- [ ] Hipótese e grade em commit anterior ao da primeira execução.
- [ ] A seleção de hiperparâmetros de cada seed usa só o treino daquela seed (revisão; asserção de que os índices do teste não entram no ajuste).
- [ ] `summary.json` com média e desvio de A, M1 e M1+M2 no CIRA, e de A e M1+M2 no combinado, em dez seeds.
- [ ] Hiperparâmetros selecionados em cada seed gravados, com a frequência de cada combinação.
- [ ] Comparação pareada com A gravada, com método e ressalva.
- [ ] Nenhuma amostra sintética no treino de M1 e M1+M2 (asserção de tamanho).
- [ ] Métricas com e sem duplicatas em toda seed, nos dois datasets.
- [ ] Texto de resultado não afirma melhora que os números não mostram (revisor metodológico).

## Execução com dados reais: local ou Apuana (decisão 42)

O script roda na máquina de quem tem os dados ou no cluster Apuana; as duas formas valem. O que importa é treinar e deixar a evidência: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e8.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). As dez seeds podem ser um job por seed, em paralelo; para isso o script aceita a seed como argumento e a agregação do `summary.json` roda depois, em um passo próprio. Quem executa roda com a árvore limpa e faz o commit `exp`. A tarefa fica "pronta" sem isso e "executada" com isso.

## Testes

Seção "Tarefa 15" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e8_modificacao.py`.
