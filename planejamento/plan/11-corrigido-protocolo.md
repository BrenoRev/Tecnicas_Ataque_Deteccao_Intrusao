# 11 · protocolo corrigido · variância e comparação justa (E4)

**Onde:** `scripts/e4_corrigido.py`, `src/doh_ids/evaluate.py`, `src/doh_ids/config.py`, `tests/`, `results/e4/corrigida/`
**Objetivo:** dizer, com dez execuções e hiperparâmetros idênticos, se o empilhamento em três subconjuntos é melhor que um Random Forest único, e quanto o resultado varia de um split para outro.
**Depende de:** 08, 09
**Demonstra:** `results/e4/corrigida/summary.json`: média e desvio em dez seeds, A contra B e C, com e sem duplicatas. Seção 7 (discussão) e 8 (limitações).

> ⚠️ REVISAR (07/10/2026, reconciliação no commit `0ae2d49`), **só o passo 9, opcional:** o caminho `results/e4/corrigida/grupo-A/fold<k>/` não pode ser gravado por `save_run`, que sempre monta `<experimento>/<trilha>/<recorte>/seed<k>/` (`runlog.py:78`), e sai do layout único da decisão 38. O resto da tarefa não é afetado. Antes de implementar o passo 9, o usuário decide como a dobra entra no caminho; a decisão não foi reescrita e o passo ficou como estava.

> ⚠️ REVISAR (07/10/2026, reconciliação no commit `360c3d3`), **antes de escrever as configurações em `config.py`:** a decisão 45 manda esta tarefa rodar sobre a variante de profundidade variável; a decisão 23 define o modelo A como "empilhado com os valores do artigo" e o modelo B como Random Forest único "com os mesmos hiperparâmetros (10, 5, 28)". Com A sem limite de profundidade, um B com profundidade 5 deixa de ter os mesmos hiperparâmetros de A, e a comparação A contra B deixa de isolar a arquitetura. O usuário decide o que B passa a ser (sem limite de profundidade, profundidade 5, ou um B para cada leitura de A); nenhuma das duas decisões foi reescrita, e a tabela do passo 2 ficou como estava. A escolha é feita antes de qualquer execução desta tarefa (invariante I5).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- Dependências: 08 pronta e executada (`798ecd3`); 09 a fazer. Esta tarefa depende de resultado real das duas.
- **Sistema base (decisão 45):** o modelo A é o empilhado com `base_forests(subsets, seed, MAX_DEPTH_VARIABLE)`. O A com profundidade 5 é reportado ao lado onde o custo permitir. O que isso faz com B e C está no ⚠️ REVISAR acima.
- **Ponto sem valor declarado: o nome dos recortes.** A decisão 38 dá `results/e4/corrigida/<modelo>/seed<k>/`. Com A em duas leituras de profundidade, o recorte precisa dizer qual é qual; o nome não está em nenhuma decisão. Ver "Pendências abertas pela decisão 45" em `00-README.md`.
- **Custo estimado, sem cortar nada.** Um ajuste do sistema inteiro leva 194 s na profundidade variável e 112 s na profundidade 5 (medidos na tarefa 08, o primeiro com a máquina carregada). Dez seeds do modelo A: cerca de 32 minutos na profundidade variável, mais 19 minutos se o A de profundidade 5 for rodado ao lado. B e C não foram medidos: são Random Forests únicos sobre o treino com SMOTE inteiro, 2.402.484 linhas, e o tempo sai da tarefa 09. A avaliação por grupo do passo 9, se feita, são quatro ajustes a mais. O "dezenas de segundos" da seção "Evidência" está superado.
- `evaluate.py` já tem o que os passos 7 e 8 consomem: `malicious_vs_rest(confusion)` devolve `fpr` e `recall`, e `base_rate(fpr, recall, prevalence)` devolve a precisão operacional e os alarmes falsos por dez milhões de fluxos, com a prevalência obrigatória. A comparação pareada e a agregação por seed ainda não existem.
- `fit_system(train, seed, max_depth)` mora em `scripts/e1_reproducao.py`; ver o bloco "Como ficou" da tarefa 08 sobre levá-la para o pacote. `N_JOBS = -1` existe.
- Execução com dados reais na própria sessão (decisão 44).

## Reconciliado com as tarefas 02 a 05 (07/10/2026, commit `0ae2d49`)

- **O filtro sem duplicatas já tem a sua função.** `seen_in_train(train, test)`, em `splits.py`, devolve o vetor booleano das linhas do teste cujo vetor de 29 atributos existe no treino, e tem teste (T05-5). A métrica sem duplicatas do passo 7 usa `test[~seen_in_train(train, test)]`; não se escreve um segundo filtro em `evaluate.py`. O teste T11-3 cobre só o que for novo.
- Seeds: `SEEDS_CORRIGIDA` de `config.py`. Split por seed: `stratified_split(table, seed)`; scaler: `fit_scaler(train)`.
- Fração de referência com a seed 42: `split_counts.json["test_seen_in_train"]`, 15.842 linhas, 13,67% do teste; por classe 17,68% / 5,42% / 0,008%. Confere com o bloco abaixo.
- `group` está no Parquet como texto (`192.168.20.111`). `results/e0/dados/cira/seed42/maquina_por_classe.csv` confirma quatro máquinas com Non-DoH e Benign-DoH (`.111`, `.112`, `.113`, `.191`) e dez com Malicious-DoH (`.144` e `.204` a `.212`), sem nenhuma em comum.
- `summary.json` e `RESUMO.md` são arquivos auxiliares, gravados pelo script em `results/e4/corrigida/`; cada par modelo e seed passa por `save_run(experiment="e4", track="corrigida", slice_name=<modelo>, seed=k, ...)`.
- `metrics.json` só com tipos nativos do Python. `N_JOBS = -1` está em `config.py` desde `4746c22` e foi confirmado pela decisão 45; não altera resultado, só o tempo.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **A métrica sem duplicatas (passo 7) deixa de ser detalhe.** Com seed 42, 13,7% do teste tem vetor idêntico no treino: 17,7% do Non-DoH, 5,4% do Benign-DoH, 0,01% do Malicious-DoH. Ela é reportada em toda seed, ao lado da métrica completa.
- **Avaliação por grupo (passo 9): viável só com poucas dobras.** O grupo é a máquina local. Há quatro máquinas com Non-DoH e Benign-DoH e dez com Malicious-DoH, sem nenhuma em comum. O desenho possível é deixar uma máquina benigna e uma ou mais maliciosas de fora por dobra, em quatro dobras. Continua opcional e a primeira a cortar.
- O malicioso foi capturado em outras máquinas e dois meses depois das outras classes. Nenhum split dentro do CIRA remove esse confundimento; o resumo do experimento declara isso.

## Arquivos

- `scripts/e4_corrigido.py` — novo.
- `src/doh_ids/config.py` — as configurações A, B e C e as prevalências hipotéticas, em commit anterior à primeira execução.
- `src/doh_ids/evaluate.py` — acrescentar a comparação pareada e a agregação por seed. O filtro sem duplicatas reutiliza `seen_in_train` de `splits.py` (ver o bloco de reconciliação).
- `tests/test_evaluate.py` (T11-2 a T11-4) e `tests/test_pipeline.py` (T11-1) — acrescentar.
- `results/e4/corrigida/<modelo>/seed<k>/`, `results/e4/corrigida/summary.json` e `results/e4/corrigida/RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento` para E4, trilha corrigida.
2. **Sem busca de hiperparâmetros nesta tarefa.** As três configurações abaixo ficam escritas em `config.py` antes da primeira execução (decisão 23):

| Modelo | Arquitetura | Árvores | Profundidade | `max_features` | Balanceamento |
| --- | --- | --- | --- | --- | --- |
| A | Empilhado, três subconjuntos (tarefa 08) | 10 | 5 | 28 | SMOTE por subconjunto |
| B | Random Forest único | 10 | 5 | 28 | SMOTE no treino inteiro, como na tarefa 09 |
| C | Random Forest único, como na Tabela II (tarefa 09) | 10 | padrão da biblioteca | padrão da biblioteca | SMOTE no treino inteiro, como na tarefa 09 |

   A contra B isola o efeito da arquitetura, com tudo o mais igual. A contra C é a comparação que o artigo faz.
3. Para cada seed de 0 a 9: novo split 90/10 estratificado, scaler ajustado no treino da seed, os três modelos treinados nesse treino e avaliados no teste da mesma seed. Os três modelos de uma seed veem exatamente o mesmo split.
4. O meta-classificador do modelo A é treinado como na trilha fiel (decisão 09). Isso não envolve o teste; fica declarado que a trilha corrigida corrige a avaliação, não o desenho do empilhamento.
5. Agregar: média e desvio padrão de cada métrica por modelo; recall de Benign-DoH em destaque.
6. Comparação pareada por seed, A contra B e A contra C, com o método fixado antes (decisão 24): diferença média de F1 macro e de recall de Benign-DoH, número de seeds em que cada um vence, e teste de postos sinalizados de Wilcoxon. Escrever junto a ressalva: os dez conjuntos de teste se sobrepõem, então os pares não são independentes e o teste é indicativo.
7. Métrica sem duplicatas: reportar as métricas também excluindo do teste as linhas cujo vetor de 29 atributos existe no treino da mesma seed (ver tarefa 05, passo 6).
8. Taxa base: com o FPR e o recall médios da classe maliciosa, a precisão operacional sob as prevalências hipotéticas declaradas em `config.py` como hipotéticas (`[Decidir: valores; proposta em "Pendentes da equipe" de 00-decisoes-travadas.md]`).
9. **Opcional, primeiro a cortar:** avaliação por grupo com o modelo A, trilha corrigida, em quatro dobras. Em cada dobra ficam de fora uma das quatro máquinas com Non-DoH e Benign-DoH (`.111`, `.112`, `.113`, `.191`) e um quarto das dez máquinas maliciosas (ordenadas pelo endereço: 3, 3, 2 e 2). Nenhum `group` aparece em treino e teste da mesma dobra; scaler, subconjuntos e SMOTE são refeitos dentro de cada dobra. Resultado em `results/e4/corrigida/grupo-A/fold<k>/`. O critério de dados já está satisfeito (quatro e dez máquinas, medido na tarefa 04); se a avaliação for cortada, a dispensa cita o prazo.
10. Revisão do agente `revisor-metodologico`, com atenção ao invariante I5.

## Por quê

Decisões 06, 12, 23 e 24. O artigo sustenta a vantagem do modelo proposto com 0,0004 de F1 em uma única execução, contra um baseline com outros hiperparâmetros. Com hiperparâmetros iguais e dez execuções, a pergunta "o empilhamento ajuda?" passa a ter resposta. A seleção de hiperparâmetros fica na tarefa 15, onde ela é a própria modificação e roda dentro do treino de cada seed.

## Evidência — verificada no baseline

- `docs/02-artigo.md:58-65` — Tabela II: diferença de 0,0004 em F1 entre o proposto e o Random Forest com SMOTE.
- `docs/05-plano-experimental.md:77-84` — escopo de E4.
- `docs/04-dados.md:70` — fluxos da mesma sessão nos dois lados do split.
- `planejamento/MEMORY/04-red-team.md`, achados F1, F2, F10 e F15 — por que a busca saiu desta tarefa e por que as configurações e o teste são fixados antes.
- `planejamento/MEMORY/01-discovery-stack.md` — custo de um ajuste na casa de dezenas de segundos; 30 treinos cabem em uma sessão.

## Risco

- Escolher configuração ou teste estatístico depois de ver os números: as duas coisas estão travadas em decisão e em `config.py` antes da execução.
- Com dez pares sobrepostos, o texto não pode dizer "significativo" sem a ressalva, nem "igual" sem mostrar o desvio.
- Uma seed controla split, reamostragem e modelo, então o desvio mistura as três fontes. Dizer isso no relatório.

## Critério de aceite

- [ ] As três configurações estão em `config.py` em commit anterior ao da primeira execução.
- [ ] Em cada seed, os três modelos foram avaliados no mesmo teste (asserção de igualdade dos índices).
- [ ] `summary.json` traz média e desvio de cada métrica para A, B e C em dez seeds.
- [ ] Comparação pareada gravada, com o método e a ressalva de dependência entre os pares.
- [ ] Métricas com e sem as linhas duplicadas entre treino e teste.
- [ ] Avaliação por grupo feita (quatro dobras, modelo A), ou dispensa registrada por prazo.
- [ ] Todo resultado tem trilha `corrigida` no caminho e no `run.json`.
- [ ] Revisor metodológico sem achado bloqueante.

## Execução com dados reais: na sessão de implementação (decisões 42 e 44)

O script roda na própria sessão de implementação, nesta máquina, quando a tarefa chega ao ponto de executar (decisão 44); não se espera um integrante designado. O Apuana continua sendo opção (decisão 42). A evidência é a mesma: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e4.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). As dez seeds podem ser um job por seed, em paralelo; para isso o script aceita a seed como argumento e a agregação do `summary.json` roda depois, em um passo próprio. A execução é feita com a árvore limpa (o plano em commit antes de rodar, porque `dirty` mede o repositório inteiro) e o resultado entra em commit `exp`. Os dois fechamentos, "pronta" e "executada", acontecem na mesma sessão.

## Testes

Seção "Tarefa 11" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e4_corrigido.py`.
