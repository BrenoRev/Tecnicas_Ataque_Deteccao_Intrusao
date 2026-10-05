# 10 · reprodução · sensibilidade às ambiguidades (E3)

**Onde:** `scripts/e3_sensibilidade.py`, `tests/test_models.py`, `results/e3/variante/`
**Objetivo:** saber quanto o resultado da reprodução depende de cada ponto que o artigo deixou em aberto, e qual leitura fica mais perto da Fig. 4b.
**Depende de:** 08
**Demonstra:** `results/e3/variante/`: distância à Fig. 4b por leitura alternativa. Seção 7: discussão das ambiguidades.

## Arquivos

- `scripts/e3_sensibilidade.py` — novo.
- `src/doh_ids/models.py`, `src/doh_ids/splits.py` — parâmetros para as variantes do núcleo; código novo só se uma opcional for feita.
- `tests/test_models.py` — acrescentar T10-1 a T10-3.
- `results/e3/variante/<variante>/seed42/` — gerado.
- `results/e3/variante/RESUMO.md` — interpretação (passo 5).

## O que fazer

1. Rodar a skill `experimento` para E3. As variantes abaixo são a lista fechada: não se acrescenta variante depois de ver resultado.
2. A partir da configuração da tarefa 08, mudar um ponto por vez:

| Variante | O que muda | Ambiguidade | Prioridade |
| --- | --- | --- | --- |
| `class_weight` | `class_weight='balanced'` nos bases, como no script dos autores | A14 | núcleo |
| `use_probas` | Meta recebe probabilidades (9 entradas) | A10 | núcleo |
| `max_features_padrao` | `max_features` no padrão da biblioteca | crítica 5 do seminário | núcleo |
| `rf_unico` | Um Random Forest só, com `class_weight='balanced'`, `max_features` no padrão da biblioteca e sem SMOTE: o que o código público faz. Muda mais de um ponto de uma vez, de propósito | auditoria | núcleo |
| `meta_uniao` | Meta treinado na união dos três subconjuntos balanceados | A8 | opcional |
| `stacking_cv` | `StackingCVClassifier`: meta com predições out-of-fold, bases no treino inteiro com SMOTE | A8, A9 | opcional |
| `oss` | One-sided selection (Kubat e Matwin) antes do SMOTE | A3 | opcional, primeira a cortar |

   As quatro do núcleo são obrigatórias. As opcionais só entram com as do núcleo fechadas. Sobre `oss`: no artigo, "one-sided selection" aparece na mesma frase que descreve dividir só o Non-DoH, e pode ser apenas o nome que os autores deram a subamostrar um lado; nesse caso a variante testa algo que eles não fizeram. É cara (vizinho mais próximo sobre centenas de milhares de amostras) e a menos informativa.
3. Avaliar cada variante no mesmo teste, com a mesma função, e calcular a distância até a Fig. 4b.
4. Gerar uma tabela: variante, soma das diferenças absolutas para a Fig. 4b, recall de Benign-DoH, F1 macro, acurácia.
5. Escrever a interpretação: qual variante fica mais perto, e o que isso sugere sobre o que os autores rodaram. Sugerir não é concluir.

## Por quê

Risco R2. Como o artigo não especifica vários pontos, "a reprodução" é uma família de modelos. Medir a família é a forma honesta de reportar, e a variante `rf_unico` testa a hipótese de que os números publicados vieram do código público e não do sistema descrito.

## Evidência — verificada no baseline

- `docs/02-artigo.md:81-104` — tabela de ambiguidades.
- `docs/05-plano-experimental.md:63-75` — escopo de E3.
- `docs/03-auditoria-repositorio.md`, "O script de modelagem" — configuração do Random Forest único.
- `planejamento/MEMORY/01-discovery-stack.md` — `StackingCVClassifier` e `OneSidedSelection` existem e executam; `use_probas=True` dá 9 entradas.

## Risco

- Escolher, depois de ver os números, a variante que mais se parece com o artigo e chamá-la de reprodução (risco R3). A trilha fiel continua sendo a da tarefa 08; esta tarefa só informa a discussão.
- One-sided selection usa vizinho mais próximo sobre centenas de milhares de amostras e pode ser lenta. Se passar de um tempo razoável, medir em um subconjunto e declarar.
- `stacking_cv` não reproduz "um subconjunto por base"; isso fica dito na descrição da variante.

## Critério de aceite

- [ ] Um diretório de resultado para cada variante do núcleo (quatro) e para cada opcional feita, com `run.json` de trilha `variante` nomeando a variante e o ponto que ela muda. Opcional não feita está listada como não feita no resumo.
- [ ] Tabela comparativa gerada por script em `results/e3/variante/`.
- [ ] Todas as variantes avaliadas no mesmo teste (asserção de total).
- [ ] Texto de interpretação em `RESUMO.md` separa o que foi medido do que é hipótese.
- [ ] Revisor metodológico sem achado bloqueante.

## Execução com dados reais: local ou Apuana (decisão 42)

O script roda na máquina de quem tem os dados ou no cluster Apuana; as duas formas valem. O que importa é treinar e deixar a evidência: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e3.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). Quem executa roda com a árvore limpa e faz o commit `exp`. A tarefa fica "pronta" sem isso e "executada" com isso.

## Testes

Seção "Tarefa 10" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e3_sensibilidade.py`.
