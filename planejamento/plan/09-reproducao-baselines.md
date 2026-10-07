# 09 · reprodução · baselines do artigo (E2)

**Onde:** `src/doh_ids/models.py`, `scripts/e2_baselines.py`, `results/e2/fiel/`
**Objetivo:** os três modelos de comparação da Tabela II, no mesmo split e no mesmo teste do modelo proposto.
**Depende de:** 05, 06, 08 (a 08 cria `models.py`; esta tarefa pode começar da branch da 08)
**Demonstra:** `results/e2/fiel/<modelo>/seed42/`: três baselines ao lado das linhas da Tabela II. Seção 7: comparação com outros trabalhos.

## Arquivos

- `src/doh_ids/models.py` — acrescentar os construtores dos baselines.
- `src/doh_ids/splits.py` — acrescentar o SMOTE do treino inteiro (iguala as duas classes minoritárias à majoritária).
- `src/doh_ids/config.py` — profundidade 10 da árvore e 10 árvores do Random Forest, com a origem (Tabela II).
- `scripts/e2_baselines.py` — novo.
- `tests/test_models.py` — acrescentar T09-1 a T09-3.
- `results/e2/fiel/<modelo>/seed42/` e `results/e2/fiel/RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento` para E2, trilha fiel.
2. Preparar o treino dos baselines: treino normalizado completo, com SMOTE aplicado para igualar as classes minoritárias à majoritária. O artigo só diz "SMOTE balanced"; a estratégia exata é escolha nossa e leva comentário dizendo isso (ambiguidade A6, sem citar o identificador no código).
3. Árvore de decisão com profundidade máxima 10 (Tabela II); XGBoost; Random Forest com 10 árvores (Tabela II). Os demais hiperparâmetros ficam no padrão das bibliotecas, com comentário dizendo que o artigo não os informa.
4. Avaliar os três no mesmo teste da tarefa 08, com a mesma função de avaliação.
5. Gravar métricas, tempo de treino e a comparação com as três linhas correspondentes da Tabela II.
6. O resumo dos quatro modelos lado a lado (os três baselines e o proposto) é montado na tarefa 17, a partir de `results/e1/` e `results/e2/`. Aqui não se lê resultado da tarefa 08, para as duas poderem andar em paralelo.

## Por quê

P1: a Tabela II é metade dos resultados do artigo. A comparação que o artigo usa para justificar o modelo proposto é contra o Random Forest com SMOTE, por 0,0004 em F1; sem reproduzir o baseline não dá para discutir essa afirmação.

## Evidência — verificada no baseline

- `docs/02-artigo.md:58-65` — Tabela II.
- `docs/05-plano-experimental.md:57-61` — escopo de E2.
- `planejamento/MEMORY/01-discovery-stack.md` — `XGBClassifier` treina no ambiente fixado.

## Risco

- SMOTE sobre o treino inteiro cria 783.057 amostras sintéticas de Benign-DoH e 576.230 de Malicious-DoH (cada classe sobe para 800.828); o treino passa a 2.402.484 linhas. Pela medição cabe em memória e em minutos; se não couber, registrar e reduzir declaradamente.
- A linha da árvore de decisão no artigo (recall 0,7120) é muito pior que as outras. Se a nossa sair muito melhor, é indício de que os autores usaram outra configuração; reportar, não ajustar.
- Rótulos inteiros 0, 1, 2 são exigidos pelo XGBoost: já é a codificação de `config.py`.

## Critério de aceite

- [ ] Três diretórios de resultado, um por baseline, com métricas e `run.json`.
- [ ] Todos avaliados sobre o mesmo teste: o total da matriz é igual ao de `results/e0/dados/cira/seed42/split_counts.json` (asserção).
- [ ] Cada baseline tem métricas macro e ponderada nomeadas e a diferença para a sua linha da Tabela II.
- [ ] Hiperparâmetros não informados pelo artigo estão comentados como padrão da biblioteca.
- [ ] Revisor metodológico sem achado bloqueante.

## Testes

Seção "Tarefa 09" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e2_baselines.py`.
