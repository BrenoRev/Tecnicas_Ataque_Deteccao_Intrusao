# 10 · reprodução · sensibilidade às ambiguidades (E3)

**Onde:** `scripts/e3_sensibilidade.py`, `tests/test_models.py`, `results/e3/variante/`
**Objetivo:** saber quanto o resultado da reprodução depende de cada ponto que o artigo deixou em aberto, e qual leitura fica mais perto da Fig. 4b.
**Depende de:** 08
**Demonstra:** `results/e3/variante/`: distância à Fig. 4b por leitura alternativa. Seção 7: discussão das ambiguidades.

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- Dependência 08 pronta e executada (`798ecd3`).
- **Ponto a confirmar com o usuário: de que configuração as variantes partem.** A tarefa manda mudar um ponto por vez "a partir da configuração da tarefa 08", que era a trilha fiel (profundidade 5). A decisão 45 troca o sistema base das tarefas 09, 11, 12, 14, 15 e 16 pela variante de profundidade variável e não cita esta tarefa. Como está escrito, as variantes partem da fiel, que com a seed 42 não prediz Benign-DoH. O implementador não escolhe: partir da fiel, da profundidade variável ou das duas é decisão do usuário, tomada antes de ver qualquer resultado desta tarefa.
- A leitura de profundidade já está medida em `results/e1/variante/profundidade_variavel/seed42/` (soma das diferenças absolutas para a Fig. 4b de 553, contra 4.711 da fiel). Ela não é rodada de novo aqui; a tabela comparativa do passo 4 pode trazê-la como linha lida de `results/e1/`, se o usuário confirmar.
- `base_forests(subsets, seed, max_depth)` não recebe `class_weight` nem `max_features`: as variantes `class_weight` e `max_features_padrao` pedem esses parâmetros em `models.py`, e `use_probas` pede o seu em `stacked_forest`. Já há um segundo valor em uso para cada um, o que a regra de código exige para criar parâmetro.
- `fit_system` mora em `scripts/e1_reproducao.py`; ver o bloco "Como ficou" da tarefa 08 sobre levá-la para o pacote.
- **Custo estimado, sem cortar nada:** cada variante empilhada é um ajuste do sistema inteiro, 112 s partindo da fiel e 194 s partindo da profundidade variável (medidos na tarefa 08, o segundo com a máquina carregada). As três variantes empilhadas do núcleo dão cerca de 6 minutos em um caso e 10 no outro; `rf_unico` e as opcionais não foram medidas. Esta tarefa não repete a validação cruzada.
- Execução com dados reais na própria sessão (decisão 44).

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- Cada variante é uma chamada `save_run(experiment="e3", track="variante", slice_name=<variante>, seed=SEED_FIEL, ...)`. No `run.json` o nome da variante aparece na chave `slice`; o ponto que ela muda entra no dicionário `config`, que é o que o critério de aceite pede "por nome".
- Asserção de total, com a chave real: `split_counts.json["test"]["total"]`, 115.911.
- `metrics.json` só com tipos nativos do Python; a tabela comparativa é arquivo auxiliar, gravado pelo script em `results/e3/variante/`.
- `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45; não altera resultado, só o tempo.

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

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script roda na própria sessão de implementação, nesta máquina, quando a tarefa chega ao ponto de executar (decisão 44); não se espera um integrante designado. O Apuana continua sendo opção (decisão 42). A evidência é a mesma: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e3.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). A execução é feita com a árvore limpa (o plano em commit antes de rodar, porque `dirty` mede o repositório inteiro) e o resultado entra em commit `exp`. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão.

## Testes

Seção "Tarefa 10" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e3_sensibilidade.py`.
