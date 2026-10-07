# 11 · protocolo corrigido · variância e comparação justa (E4)

**Onde:** `scripts/e4_corrigido.py`, `src/doh_ids/evaluate.py`, `src/doh_ids/config.py`, `tests/`, `results/e4/corrigida/`
**Objetivo:** dizer, com dez execuções e hiperparâmetros idênticos, se o empilhamento em três subconjuntos é melhor que um Random Forest único, e quanto o resultado varia de um split para outro.
**Depende de:** 08, 09
**Demonstra:** `results/e4/corrigida/summary.json`: média e desvio em dez seeds, A contra B e C, com e sem duplicatas. Seção 7 (discussão) e 8 (limitações).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **A métrica sem duplicatas (passo 7) deixa de ser detalhe.** Com seed 42, 13,7% do teste tem vetor idêntico no treino: 17,7% do Non-DoH, 5,4% do Benign-DoH, 0,01% do Malicious-DoH. Ela é reportada em toda seed, ao lado da métrica completa.
- **Avaliação por grupo (passo 9): viável só com poucas dobras.** O grupo é a máquina local. Há quatro máquinas com Non-DoH e Benign-DoH e dez com Malicious-DoH, sem nenhuma em comum. O desenho possível é deixar uma máquina benigna e uma ou mais maliciosas de fora por dobra, em quatro dobras. Continua opcional e a primeira a cortar.
- O malicioso foi capturado em outras máquinas e dois meses depois das outras classes. Nenhum split dentro do CIRA remove esse confundimento; o resumo do experimento declara isso.

## Arquivos

- `scripts/e4_corrigido.py` — novo.
- `src/doh_ids/config.py` — as configurações A, B e C e as prevalências hipotéticas, em commit anterior à primeira execução.
- `src/doh_ids/evaluate.py` — acrescentar a comparação pareada, o filtro sem duplicatas e a agregação por seed.
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

## Execução com dados reais: local ou Apuana (decisão 42)

O script roda na máquina de quem tem os dados ou no cluster Apuana; as duas formas valem. O que importa é treinar e deixar a evidência: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e4.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). As dez seeds podem ser um job por seed, em paralelo; para isso o script aceita a seed como argumento e a agregação do `summary.json` roda depois, em um passo próprio. Quem executa roda com a árvore limpa e faz o commit `exp`. A tarefa fica "pronta" sem isso e "executada" com isso.

## Testes

Seção "Tarefa 11" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e4_corrigido.py`.
