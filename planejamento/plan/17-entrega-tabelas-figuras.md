# 17 · entrega · tabelas e figuras do relatório geradas por script

**Onde:** `scripts/make_report_assets.py`, `report/tables/`, `report/figures/`
**Objetivo:** toda tabela e toda figura de resultado do relatório sai de `results/` por um comando, sem número digitado à mão.
**Depende de:** 08, 09, 12, 14 (obrigatórias); 10, 11, 15, 16 entram se concluídas
**Demonstra:** `report/tables/` e `report/figures/` regenerados por um comando a partir de `results/`. Toda tabela e figura das seções 6 e 7.

## Arquivos

- `scripts/make_report_assets.py` — novo.
- `tests/test_report_assets.py` — novo (T17-1 a T17-4).
- `report/tables/*.tex`, `report/figures/*.pdf` — gerados, no Git.

## O que fazer

1. Listar as tabelas e figuras que o relatório precisa, a partir das perguntas da especificação:

| Item | Fonte | Seção do relatório |
| --- | --- | --- |
| Amostras por classe em treino e teste, CIRA | `results/e0/` | 6 |
| Amostras por classe em treino, por fold de validação e no teste, segundo dataset (retreino publicado e sem réplicas); contagem do HKD por ferramenta na transferência (só teste) | `results/e6/` | 6 |
| Reconciliação com a Tabela I | `results/e0/` | 6 |
| Matriz de confusão: artigo (Fig. 4b), reprodução, diferença | `results/e1/` | 7 |
| Tabela II: artigo, reprodução, diferença, quatro modelos | `results/e1/`, `results/e2/` | 7 |
| Sensibilidade às ambiguidades | `results/e3/` | 7 |
| Protocolo corrigido: média e desvio, dez seeds | `results/e4/` | 7 |
| Importância de atributos e dependence plot | `results/e5/` | 7 |
| Segundo dataset: transferência e retreino, recall por ferramenta | `results/e6/` | 7 |
| Modificação contra original, nos dois datasets | `results/e8/` | 7 |
| Comparação com resultados da literatura (metade inferior da Tabela II) | `config.py`, com a referência | 7 |
| Tamanho por classe de cada fold de validação | `results/e0/` | 6 |
| Tempos de treino medidos | `run.json` de `results/e1/`, `results/e2/` | 7 |
| Tabela de decisão do meta e desacordo entre bases | `results/e1/` | 7 |
| Taxa base: precisão operacional sob prevalências hipotéticas | `results/e4/` | 7 ou 8 |
| Estabilidade do ranking SHAP entre submodelos | `results/e5/` | 7 |
| Máquina × classe e período de captura por classe | `results/e0/` | 6 e 8 |
| Métricas com e sem as linhas duplicadas entre treino e teste | `results/e4/`, `results/e8/` | 7 |
| Retreino no combinado publicado contra sem réplicas | `results/e6/` | 7 |
| Avaliação por grupo, se feita | `results/e4/` | 7 |
| Figura: matrizes de confusão lado a lado (Fig. 4b, reprodução, diferença) | `results/e1/`, `config.py` | 7 |
| Figura: distribuição por seed do recall de Benign-DoH e do F1 macro (A, B, C e, se houver, M1+M2) | `results/e4/`, `results/e8/` | 7 |
| Figura: recall por ferramenta na transferência e nos retreinos | `results/e6/` | 7 |

2. Para cada item, o script lê os `metrics.json` e escreve um arquivo `.tex` de tabela ou uma figura em PDF. Formatação numérica única: vírgula decimal ou ponto, escolher um e manter; mesma quantidade de casas.
3. Toda tabela leva na legenda a trilha (fiel ou corrigida), a seed ou o número de seeds, e o nome da média.
4. Toda figura tem eixos rotulados e unidade.
5. O script falha se faltar resultado de tarefa obrigatória (08, 09, 12, 14), em vez de gerar tabela incompleta. Tudo o que a lista de cortes de `00-README.md` permite cortar é opcional: tarefas 10, 11, 15 e 16 inteiras, as variantes opcionais da 10 e a avaliação por grupo da 11. Item ausente é listado na saída como "não gerado", sem erro.
6. Antes de fixar a lista, conferir o limite de páginas do template (tarefa 18, passo 1): se não couberem todas as tabelas, decidir quais vão para o corpo e quais ficam só no repositório.
7. Conferir, por amostragem, três números de cada tabela contra o `metrics.json` de origem.

## Por quê

Decisão 18 e risco R10. É o que garante o item "nenhum número do relatório sem o arquivo de resultado correspondente" e torna barato refazer tudo se um experimento mudar na véspera.

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:89-103` — o que as seções 6 e 7 do relatório precisam mostrar.
- `docs/01-requisitos.md`, tabela "Seções do relatório" — pergunta por seção.
- `docs/06-padroes.md`, seção 4 — figura com eixo e unidade; número com fonte.
- `docs/02-artigo.md:58-65` e manuscrito, Tabela II — resultados da literatura citados pelo artigo.

## Risco

- O template Overleaf ainda não foi lido: o formato de tabela pode precisar de ajuste. Abrir o template antes de fixar o formato dos `.tex`.
- Misturar trilhas em uma tabela (risco R7): o script lê a trilha do `run.json` e recusa juntar trilhas diferentes sem coluna que as identifique.

## Critério de aceite

- [ ] `uv run python scripts/make_report_assets.py` gera todos os itens da lista a partir de um `results/` completo.
- [ ] Apagar `report/tables/` e rodar de novo produz arquivos `.tex` idênticos (`diff -r`). As figuras em PDF não são comparadas byte a byte, porque o arquivo carrega a data de criação.
- [ ] Toda tabela de resultado de modelo traz na legenda a trilha, a seed ou o número de seeds, e o nome da média. Tabelas de contagem de dados e de literatura não têm trilha. Conferido na revisão, tabela por tabela.
- [ ] Amostragem do passo 7 feita e registrada no pull request.

## Testes

Seção "Tarefa 17" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de artefatos do relatório: G1–G5 (G5 = o script), G8, G10.
