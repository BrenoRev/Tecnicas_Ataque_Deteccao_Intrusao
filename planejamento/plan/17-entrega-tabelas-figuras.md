# 17 · entrega · tabelas e figuras do relatório geradas por script

**Onde:** `scripts/make_report_assets.py`, `report/tables/`, `report/figures/`
**Objetivo:** toda tabela e toda figura de resultado do relatório sai de `results/` por um comando, sem número digitado à mão.
**Depende de:** 08, 09, 12, 14, 21 e o complemento da 04 com a Fig. 2 (obrigatórias); 10, 11, 15, 16 entram se concluídas
**Demonstra:** `report/tables/` e `report/figures/` regenerados por um comando a partir de `results/`. Toda tabela e figura das seções 6 e 7.

## Como ficou (conferido no código e em `results/` em `759ec29`, 08/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Suíte inteira executada em `759ec29`: 110 testes verdes em 41 s; `ruff check` e `ruff format --check` sem erro.

- **Situação: pronta e executada.** Script em `ef6ffce`; ajustes em `3bb7c85`, `81a2928`, `48a31b8` e `30a7985`; arquivos gerados em `9aeda1d`, `65062da`, `b2a54de` e `16b7f39`.
- **Arquivos:** `scripts/make_report_assets.py`, `src/doh_ids/summary.py` (tabela Markdown e constantes, levadas dos scripts para o pacote em `32f587e`), `tests/test_report_assets.py`, `report/INDICE.md`, `report/tables/` e `report/figures/`.
- **Comando real:** `uv run python scripts/make_report_assets.py`. Não treina e não lê os dados: lê `results/` inteiro (inclusive `results/e3/variante/comparacao.csv`, `results/e4/corrigida/summary.json`, `results/e8/corrigida/summary.json` e `summary-robustez.json`, que saem dos scripts de resumo) e `config.py` (a metade inferior da Tabela II). É o último passo antes dos entregáveis. Roda em segundos.
- **Resultados:** 30 tabelas em `report/tables/`, cada uma em `.tex` e em `.csv`; 13 figuras em `report/figures/`, cada uma em `.pdf` e em `.png`; `report/INDICE.md` com a origem e a legenda sugerida de cada item. O sufixo `_dupla` marca o que pede a largura da página.
- **Desvios que ficaram:** cada tabela ganhou um `.csv` e cada figura um `.png`, que é o que `make_slides.py` lê; a lista final de itens é a do `INDICE.md`, não a do passo 1; nos `.tex` o separador decimal é a vírgula, nos `.csv` e nos eixos, o ponto. As Figs. 2 e 9 são redesenhadas a partir dos CSVs de curvas gravados por `e0_dados.py` e `e7_ferramenta.py`.
- **Concluída (08/10/2026).** A amostragem de três números por tabela foi superada pela recomputação completa da revisão final (`REVISAO-FINAL.md`, V2). Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- **Todas as tabelas e gráficos de resultado do artigo são alvo (decisão 46).** Cada um tem de ter o seu equivalente em `report/`, com a origem em `results/`:

| Resultado do artigo | Equivalente nosso | Fonte | Tarefa que gera a fonte |
| --- | --- | --- | --- |
| Tabela I (contagens por classe) | reconciliação bruta e limpa ao lado da Tabela I | `results/e0/` | 04 (feita) |
| Fig. 2 (densidade por classe de `FlowBytesReceived`, da média e da variância do comprimento de pacote) | a mesma figura, com os nossos dados | `results/e0/` | complemento da 04 (feito em `39a7007`) |
| Fig. 4a e Fig. 4b (matrizes de confusão) | matrizes de validação cruzada e de teste, nas duas leituras de profundidade, com a diferença | `results/e1/fiel/`, `results/e1/variante/` | 08 (feita) |
| Tabela II, metade superior | três baselines e o proposto nas duas leituras, ao lado do artigo | `results/e1/`, `results/e2/` | 08, 09 |
| Tabela II, metade inferior (literatura) | as oito linhas, com a referência | `config.py` | 09 |
| Figs. 5, 6a, 6b, 7 e 8 (SHAP) | figuras equivalentes | `results/e5/` | 12 |
| Seção VI-D (três acurácias por ferramenta) e Fig. 9 | métricas por ferramenta ao lado do artigo; densidade de `ResponseTimeTimeSkewFromMode` e `PacketTimeVariance` por ferramenta | `results/e7/` | 21 |

- **As duas leituras de profundidade vão lado a lado (decisão 45)** em toda tabela do sistema proposto: uma coluna ou linha por leitura, nomeada, lida de `fiel/` e de `variante/`. A recusa de juntar trilhas sem coluna que as identifique (item de risco abaixo) continua valendo e é o que protege essa tabela.
- **P2 refeito (decisão 47):** cada item acima que a tarefa 14 produz para o combinado sem réplicas (contagens por conjunto, matrizes de teste e de validação cruzada nas duas leituras, baselines, figuras SHAP) ganha a sua tabela ou figura, com o CIRA ao lado. Retreino publicado e transferência ficam em bloco próprio, nomeado como análise ao lado.
- **A tarefa 21 passa a ser obrigatória (decisão 49):** o passo 5 falha também se faltar `results/e7/`. O conjunto obrigatório é 08, 09, 12, 14 e 21, mais a Fig. 2 em `results/e0/`.
- A Fig. 2 e a Fig. 9 são densidades calculadas sobre os dados, que este script não lê: quem as calcula é o script que lê os dados (`scripts/e0_dados.py` e `scripts/e7_ferramenta.py`), e este script só as leva para `report/figures/`.
- Fonte dos tempos de treino: chave `timings` do `run.json` (`subsets_seconds`, `base_fit_seconds`, `meta_fit_seconds`, `cross_validation_seconds`, `total_seconds` em E1).
- Chaves que este script lê de `results/e1/<trilha>/<recorte>/seed42/metrics.json`: ver o bloco "Como ficou" da tarefa 08.
- Q9 (idioma e limite de páginas) continua sem resposta. A decisão 53 fixou o relatório em português, com alvo de 6 páginas e teto de 8: o relatório usa um subconjunto dos itens, e o resto fica no repositório.

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
| Figura: densidades por classe equivalentes à Fig. 2 | `results/e0/` | 6 |
| Matriz de validação cruzada: artigo (Fig. 4a), reprodução, diferença | `results/e1/` | 7 |
| Explicações locais equivalentes às Figs. 7 e 8 | `results/e5/` | 7 |
| Ferramenta de túnel: métricas por ferramenta ao lado da Seção VI-D; figura equivalente à Fig. 9 | `results/e7/` | 7 |
| P1 refeito no combinado sem réplicas: sistema nas duas leituras, validação cruzada, baselines, SHAP, ao lado do CIRA | `results/e6/` | 7 |
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
5. O script falha se faltar resultado de tarefa obrigatória (08, 09, 12, 14 e, desde a decisão 49, 21), em vez de gerar tabela incompleta. Tudo o que a lista de cortes de `00-README.md` permite cortar é opcional: tarefas 10, 11, 15 e 16 inteiras, as variantes opcionais da 10 e a avaliação por grupo da 11. Item ausente é listado na saída como "não gerado", sem erro.
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

- (Superado: a tarefa 24 usou `geracao_latex_and_pdf/template.tex` e as tabelas entram no relatório por `\input`.) O template Overleaf ainda não tinha sido lido: o formato de tabela pode precisar de ajuste. Abrir o template antes de fixar o formato dos `.tex`.
- Misturar trilhas em uma tabela (risco R7): o script lê a trilha do `run.json` e recusa juntar trilhas diferentes sem coluna que as identifique.

## Critério de aceite

- [x] `uv run python scripts/make_report_assets.py` gera todos os itens da lista a partir de um `results/` completo. Executado em `759ec29`, com saída em diretório temporário: nenhum item "não gerado".
- [x] Apagar `report/tables/` e rodar de novo produz arquivos `.tex` idênticos (`diff -r`). As figuras em PDF não são comparadas byte a byte, porque o arquivo carrega a data de criação. Executado: `diff -rq` entre o diretório temporário e `report/tables/` sem diferença, nos 30 `.tex` e nos 30 `.csv`; `INDICE.md` idêntico; os 13 `.png` idênticos byte a byte.
- [x] Toda tabela de resultado de modelo traz na legenda a trilha, a seed ou o número de seeds, e o nome da média. Tabelas de contagem de dados e de literatura não têm trilha. **Fechado em 08/10/2026:** executado em `5999c1b`: `test_model_tables_name_track_seed_and_average_in_caption` e `test_tables_with_both_depth_readings_identify_each_one`, verdes, cobrem todas as tabelas de modelo; visto no PDF do relatório, página a página: as Tabelas IV, V, VII, VIII, IX e X trazem a leitura de profundidade, a seed ou "10 seeds" e o nome da média. A conferência das 30 tabelas uma a uma por uma pessoa não foi feita; fica coberta pelos dois testes.
- [x] Amostragem do passo 7 feita. **Fechado em 08/10/2026:** `REVISAO-FINAL.md`, V2, fez mais que a amostragem: 362 matrizes e 11.266 métricas recalculadas, 2.811 valores dos três agregados e as 60 tabelas (`.tex` e `.csv`), as 26 figuras e o índice regenerados idênticos, com 0 divergências. O registro no pull request: não se aplica (decisão 55f).

## Testes

Seção "Tarefa 17" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de artefatos do relatório: G1–G5 (G5 = o script), G8, G10.
