# 12 · explicabilidade · SHAP sobre os modelos base (E5)

**Onde:** `src/doh_ids/explain.py`, `scripts/e5_xai.py`, `tests/test_explain.py`, `results/e5/fiel/proposto/seed42/`
**Objetivo:** as figuras de explicabilidade do artigo reproduzidas com o nosso modelo, e a resposta a duas perguntas: o ranking de atributos se repete, e o limiar de 40 segundos em `Duration` aparece?
**Depende de:** 08
**Demonstra:** `results/e5/fiel/proposto/seed42/`: figuras equivalentes às Figs. 5 a 8 e tabela de importância. P1: a parte explicável do artigo (seção 7).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- As colunas de assimetria têm o valor `-10` em 298.766 linhas do conjunto limpo. É o valor sentinela do DoHLyzer para desvio padrão zero (confirmado nos métodos `get_skew` e `get_skew2` de `meter/features/packet_length.py` e `response_time.py` do extrator): 294.474 das ocorrências estão em `ResponseTimeTimeSkew...`, das quais 290.123 em Non-DoH e só 804 em Malicious-DoH. A análise de importância de qualquer `...SkewFromMedian` ou `...SkewFromMode` diz que parte do sinal é esse marcador de "fluxo com no máximo um tempo de resposta", e não a assimetria.
- A classe maliciosa vem de outras máquinas e de outro período. A importância de `Duration` é lida com essa ressalva: medianas de `Duration` no CIRA limpo de 34,1 s (malicioso), 4,1 s (benigno) e 0,3 s (Non-DoH), medidas em 07/10/2026 (`docs/08-inventario-dados.md`).

## Arquivos

- `src/doh_ids/explain.py` — novo.
- `scripts/e5_xai.py` — novo.
- `tests/test_explain.py` — novo (T12-1 a T12-4).
- `results/e5/fiel/proposto/seed42/` — figuras e tabela de importância.
- `results/e5/fiel/RESUMO.md` — comparação com o artigo e limitação do passo 8.

## O que fazer

1. Rodar a skill `experimento` para E5.
2. Treinar o modelo da tarefa 08 (seed 42) e aplicar `shap.TreeExplainer` a cada um dos três Random Forests base. Os valores vêm em um array de forma (amostras, 29 atributos, 3 classes); indexar a classe pelo último eixo.
3. Calcular os valores sobre duas amostras estratificadas, de tamanho declarado em `config.py` e registrado no resultado (`[Decidir: tamanho; proposta em "Pendentes da equipe"]`): uma do treino, porque a Fig. 5 do artigo diz que a importância global foi obtida "from the training data", e uma do teste, porque a Fig. 6 usa o teste.
4. Importância global (amostra do treino, como na Fig. 5): média do valor absoluto por atributo e por classe; ranking por submodelo.
5. Figuras equivalentes às do artigo: summary plot (Fig. 5), dependence plot de `Duration` para a classe maliciosa (Fig. 6a), interação `FlowBytesSent` × `FlowBytesReceived` (Fig. 6b), e explicação local de um fluxo malicioso e de um Non-DoH do teste (Figs. 7 e 8). Eixos rotulados, com unidade.
6. Comparar o ranking com o que o artigo afirma: duração no topo, depois comprimento de pacote e variância do tempo de pacote. Atenção: os valores estão normalizados em [0, 1]; para discutir o limiar de 40 segundos, converter o eixo de `Duration` de volta para segundos com o scaler.
7. Estabilidade: concordância do ranking entre os três submodelos (correlação de postos dos dez primeiros).
8. Escrever a limitação: isto explica os Random Forests base, não a decisão do empilhamento; o `TreeExplainer` rejeita o modelo empilhado.
9. Só se o professor exigir (Q6): construir o painel com `explainerdashboard` sobre um dos modelos base e documentar como abrir. Caso contrário, não fazer.

## Por quê

A explicabilidade é a contribuição que dá nome ao artigo; P1 não fecha sem ela. Decisão 19 e ambiguidade A15: o artigo não diz qual modelo foi explicado, e verificamos que não pode ter sido o empilhamento.

## Evidência — verificada no baseline

- `docs/02-artigo.md:101` — A15.
- `docs/05-plano-experimental.md:86-95` — escopo de E5.
- `planejamento/MEMORY/01-discovery-stack.md` — forma `(n, 29, 3)` de `shap_values`; `InvalidModelError` no modelo empilhado; `ClassifierExplainer` constrói na 0.5.8.
- Manuscrito em `docs/referencias/`, seção VI e legendas das Figs. 5 e 6 — o que o artigo afirma sobre importância e sobre o limiar.

## Risco

- Indexar `shap_values` como lista por classe, como em tutoriais antigos (risco R11): teste que confere a forma do array.
- `Duration` dominante pode ser artefato do testbed (tempo limite do extrator) e não do protocolo. Reportar como ressalva, com o que a tarefa 04 mostrar sobre a distribuição de duração por classe.
- Calcular SHAP sobre o teste inteiro é desnecessário e lento: usar amostra e declarar.

## Critério de aceite

- [ ] Figuras equivalentes às Figs. 5, 6a, 6b, 7 e 8 em `results/e5/fiel/proposto/seed42/`, geradas pelo script.
- [ ] Tabela de importância por atributo, classe e submodelo em arquivo.
- [ ] O dependence plot de `Duration` está em segundos.
- [ ] Texto de comparação com o artigo: ranking e limiar, com o que confirmou e o que não confirmou.
- [ ] Medida de estabilidade entre submodelos registrada.
- [ ] A limitação do passo 8 está escrita em `results/e5/fiel/RESUMO.md`.
- [ ] Painel: construído, ou dispensado com referência à resposta de Q6.

## Execução com dados reais: local ou Apuana (decisão 42)

O script roda na máquina de quem tem os dados ou no cluster Apuana; as duas formas valem. O que importa é treinar e deixar a evidência: resultados em `results/`, `run.json` com máquina, núcleos, versões e commit, e a saída colada no pull request. Só se a execução for no Apuana, a tarefa ganha `jobs/e5.sh`, script de submissão ao Slurm (`[Preencher: partição, núcleos, memória, tempo]`). Quem executa roda com a árvore limpa e faz o commit `exp`. A tarefa fica "pronta" sem isso e "executada" com isso.

## Testes

Seção "Tarefa 12" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e5_xai.py`.
