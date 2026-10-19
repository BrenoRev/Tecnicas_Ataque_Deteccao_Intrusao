# Entregas demonstráveis — requisito do professor → tarefa → artefato

> Lê-se junto com [00-README.md](00-README.md). Diz, para cada exigência da especificação, qual tarefa a cumpre, qual arquivo prova que foi cumprida e em que seção do relatório ela aparece. Cada arquivo de tarefa traz a linha **Demonstra:** com o mesmo conteúdo, resumido.

A unidade de demonstração é o pull request da tarefa: o diff, os arquivos de `results/` ou `report/` gerados por script e a saída da verificação com dados reais colada na descrição (modelo em `.github/pull_request_template.md`, criado na tarefa 01). Quem integra vê a mudança e o artefato juntos.

> **Escopo atualizado em 07/10/2026 (commit `360c3d3`), pelas respostas do professor a Q1 a Q6 e pelas decisões 44 a 50:** P1 tem como alvo todas as tabelas e gráficos de resultado do artigo (decisão 46), com o sistema reportado nas duas leituras de profundidade (decisão 45) e a ferramenta de túnel incluída (decisão 49); P2 refaz P1 no combinado sem réplicas (decisão 47); o painel é material de demonstração (decisão 50); os experimentos rodam na sessão de implementação (decisão 44).

## 1. Requisitos da especificação e onde cada um é cumprido

As linhas da especificação são as de `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md`.

| Requisito (linha da especificação) | Tarefas | Artefato que demonstra | Seção do relatório | Quando fica demonstrável |
| --- | --- | --- | --- | --- |
| Reproduzir o artigo, implementando e executando o código, com resultados próximos (`:28`); pelo professor, "todas as tabelas e gráficos de resultados" (Q2, decisão 46) | 04 (com o complemento da Fig. 2), 05, 06, 07, 08, 09, 10, 12, 21 | Um artefato por resultado do artigo, na tabela 1a abaixo. Central: `results/e1/fiel/proposto/seed42/` e `results/e1/variante/profundidade_variavel/seed42/`, matrizes ao lado da Fig. 4a e da Fig. 4b, célula a célula, nas duas leituras de profundidade, e `results/e1/RESUMO.md` com as duas lado a lado (feito em `798ecd3`) | 7.1 | primeira matriz: feita em 07/10; onda 5 (09/11): reprodução fechada |
| Resultados do sistema em outro dataset, com a escolha justificada (`:29`); pelo professor, "fazer tudo novamente com outro dataset" (Q4, decisão 47) | 13, 14 (14a e 14b) | `results/e6/dados/`: compatibilidade, contagens e parágrafo de justificativa. `results/e6/`, no combinado sem réplicas: contagens por classe em treino, folds e teste; sistema nas duas leituras de profundidade, no teste e em validação cruzada; três baselines; figuras SHAP; tudo ao lado do CIRA. Como análises ao lado: retreino no combinado publicado e transferência para o HKD (recall por ferramenta) | 6 e 7.2 | onda 3 (27/10): carregado; onda 5 (09/11): avaliado |
| Modificação proposta, implementada e avaliada — opcional (`:30`) | 15, 16 | `results/e8/corrigida/summary.json`: original contra modificado nos dois datasets, dez seeds; robustez à duração | 5 e 7 | onda 6 (13/11) |
| Relatório com as seções e perguntas da especificação (`:31`, `:58-109`) | 17, 18 | PDF no template; lista de conferência pergunta → seção e parágrafo | todas | onda 7 (17/11): rascunho; 18/11: entrega |
| Link do GitHub com todos os códigos comentados (`:34`) | 01, 19, 22 | repositório com CI verde; README com a tabela resultado → script → arquivo; execução limpa por outro integrante; grep de referência interna vazio | — | onda 1 (21/10): repositório; onda 8 (18/11): entrega |
| Slides e apresentação de 15 minutos, se houver modificação (`:35`) | 20 | `report/slides_projeto.pdf` no modelo do CIn, números vindos de `report/` | — | 19/11 |
| Requisitos adicionais por artigo (`:32`) | 23 | resposta a Q3 registrada em `docs/07-pendencias.md` em 07/10/2026: "Por enquanto não" (decisão 48) | — | cumprido; reabre se o professor informar algum |
| Seção 3, modelo de ameaça com figura, algoritmo ou equação e premissas (`:75-76`) | 18; 16, se feita | diagrama do túnel DNS sobre DoH com as premissas do atacante; modelo de ameaça da avaliação de robustez | 3 | onda 2 (texto começa em 21/10) |
| Seção 4, sistema do artigo: componentes, entradas, saídas, métodos e por quê, com figura ou algoritmo (`:78-81`) | 02, 07, 08, 18 | `config.py` com cada hiperparâmetro e a seção do artigo de origem; resumo dos subconjuntos (razão obtida contra 15:12:12, fração sintética); diagrama do pipeline e algoritmo de treino | 4 | onda 2 a 4 |
| Seção 5, solução da equipe, se feita (`:83-87`) | 15, 18 | `results/e8/corrigida/HIPOTESE.md` escrita antes de rodar; diagrama do modelo modificado | 5 | onda 6 |
| Seção 6, para **cada** dataset: quais dados, por que, o que representam, como treino, validação e teste foram formados, quantas amostras por classe em cada conjunto (`:89-94`) | 03, 04, 05, 13, 14, 17 | `data/manifest.json` e `data/README.md`; `results/e0/dados/cira/seed42/`: reconciliação com a Tabela I e `split_counts.json` (treino, dez folds de validação, teste, por classe); `results/e6/`: mesmas tabelas para os dois retreinos e contagem do HKD por ferramenta | 6 | onda 2 e 3 (CIRA); onda 5 (segundo dataset) |
| Seção 6, métricas e experimentos (`:90`) | 06, 11 | `evaluate.py` com métricas por classe, macro e ponderada nomeadas; protocolo de dez seeds | 6 | onda 2 e 5 |
| Seção 7, resultados do sistema do artigo nos dois datasets, da proposta nos dois, comparação com outros trabalhos, gráficos e tabelas, discussão (`:96-103`) | 08, 09, 10, 11, 12, 14, 15, 17, 18, 21 | `report/tables/*.tex` e `report/figures/*.pdf` gerados por um comando; tabela com a metade inferior da Tabela II (literatura), obrigatória; as duas leituras de profundidade lado a lado; figuras de matriz de confusão, distribuição por seed, recall por ferramenta, SHAP e ferramenta de túnel | 7 | onda 6 e 7 |
| Seção 8, limitações do sistema do artigo e da proposta, trabalhos futuros (`:105-106`) | 04, 05, 11, 12, 14, 18 | tabela máquina × classe e período por classe; fração do teste duplicada no treino; métricas sem duplicatas; `-10` sentinela; retreino publicado contra sem réplicas | 8 | onda 5 a 7 |
| Seção 9, referências IEEE (`:108`) | 18 | `report/refs.bib`, cada entrada com DOI conferido | 9 | onda 7 |
| Template Overleaf e PDF (`:41`); modelo de apresentação do CIn (`:40`) | 18, 20 | `report/main.tex` copiado do template; slides no modelo | — | onda 0 (ler o template) |

### 1a. Cada resultado do artigo e o artefato que o reproduz (decisão 46)

| Resultado do artigo | Tarefa | Artefato | Situação em 07/10/2026 |
| --- | --- | --- | --- |
| Tabela I, contagens por classe | 04 | `results/e0/dados/cira/seed42/`: contagens brutas e limpas ao lado da Tabela I, diferença zero | feito |
| Fig. 2, densidades por classe | 04, complemento | figura em `results/e0/dados/cira/seed42/` | a fazer; era opcional e não foi feita |
| Fig. 4a, matriz do treino em validação cruzada | 08 | `fig4a_comparison` em `results/e1/<trilha>/<recorte>/seed42/metrics.json` | feito, nas duas leituras |
| Fig. 4b, matriz do teste | 08 | `fig4b_comparison` no mesmo arquivo | feito, nas duas leituras |
| Tabela II, metade superior | 08, 09 | `table_ii_comparison` em `results/e1/`; `results/e2/fiel/<modelo>/seed42/` | linha do proposto feita; baselines a fazer |
| Tabela II, metade inferior (literatura) | 09 | oito linhas em `config.py`, com a referência, conferidas por dois integrantes | a fazer; bloqueio de pessoa para fechar a 09 |
| Figs. 5, 6a, 6b, 7 e 8, SHAP | 12 | figuras em `results/e5/` | a fazer |
| Painel interativo (não é resultado; material de demonstração, decisão 50) | 12, 19 | script que sobe o painel localmente; comando no README | a fazer |
| Seção VI-D, acurácia por ferramenta, e Fig. 9 | 21 | `results/e7/` | a fazer |

O mesmo conjunto, menos o que não existe para o segundo dataset (não há figura nem tabela do artigo com que comparar), é refeito no combinado sem réplicas pela tarefa 14 (decisão 47).

## 2. O que estará demonstrável em cada marco

| Marco | O que mostrar | De onde sai |
| --- | --- | --- |
| 21/10 — fim da onda 1 | Pull request de prova com o CI verde; hooks barrando commit fora do padrão; `uv sync --locked` em clone limpo | tarefa 01 |
| 24/10 — fim da onda 2 | Contagens brutas e limpas ao lado da Tabela I, diferença zero; `config.py` com a origem de cada hiperparâmetro; métricas da Fig. 4b recalculadas por teste (os três já demonstráveis em 07/10) | tarefas 02, 04, 06 |
| 27/10 — fim da onda 3 | Tabela de amostras por classe em treino, folds e teste ao lado da Fig. 4; resumo dos três subconjuntos (os dois já demonstráveis em 07/10); segundo dataset carregado com compatibilidade conferida; Fig. 2 | tarefas 05, 07, 13 e o complemento da 04 |
| 30/10 — fim da onda 4 | **Matrizes de confusão ao lado da Fig. 4b e da Fig. 4a**, com a diferença célula a célula, nas duas leituras de profundidade (já demonstrável em 07/10, `results/e1/RESUMO.md`); Tabela II inteira: baselines e metade inferior | tarefas 08, 09 |
| 09/11 — fim da onda 5 | Família de leituras (sensibilidade); média e desvio em dez seeds; figuras SHAP e painel; P1 refeito no combinado sem réplicas, com transferência e combinado publicado ao lado; ferramenta de túnel (Seção VI-D e Fig. 9). Decisão sobre P3 | tarefas 10, 11, 12, 14, 21 |
| 10/11 — acompanhamento | Página de status, tabela de resultados e resultado da primeira execução limpa | tarefas 19 e 23 |
| 13/11 — experimentos congelados | P3 medido (se mantido); `report/tables/` e `report/figures/` gerados | tarefas 15, 17 |
| 17/11 — acompanhamento | Rascunho completo do relatório; slides, se P3 | tarefas 18, 20 |
| 18/11 — entrega | PDF e link do GitHub; checklist de entrega rodada | tarefas 18, 19 |
| 19/11 — apresentação, se P3 | 15 minutos no modelo do CIn | tarefa 20 |

## 3. Como demonstrar uma tarefa

1. O pull request segue o modelo do repositório: o que a mudança demonstra (caminho do artefato), como verificar (comandos), saída da verificação com dados reais, checklist.
2. Os arquivos de `results/` da tarefa entram no mesmo pull request, em commit `exp` separado do código, gerados com a árvore limpa (o `run.json` registra o commit e `dirty: false`). A execução é feita na sessão de implementação (decisão 44).
3. Para experimento, o diretório do resultado tem `metrics.json`, `run.json` e, no nível da trilha, `RESUMO.md` com a interpretação. Quem revisa lê o resumo e confere três números contra o `metrics.json`.
4. Tarefa de texto (18, 20) é demonstrada pelo PDF e pela lista de conferência pergunta → parágrafo.
5. Nenhum número é digitado à mão em pull request, slide ou relatório: vem de `results/` ou de `report/tables/`.
