# 07. Pendências, decisões e cronograma

Atualizado em 07/10/2026.

## Perguntas ao professor

Em ordem de impacto no projeto. Levar por escrito e registrar a resposta aqui, com a data.

| # | Pergunta | Por que importa | Resposta |
| --- | --- | --- | --- |
| Q1 | O repositório dos autores não contém o modelo proposto. A reimplementação a partir do texto é aceita como reprodução? | Define se P1 é viável como planejado | Respondida em 07/10/2026 (relato de Breno): "Podem sim reimplementar a partir da descrição feita no artigo original, evidentemente tomando os devidos cuidados para que a reprodução seja a mais fiel possível." |
| Q2 | A Tabela II e a Figura 4b divergem (acurácia 0,9998 contra 99,78%). Qual vale como referência de "resultados próximos o suficiente", e existe tolerância? | Define o critério de sucesso de P1 | Respondida em 07/10/2026: "Devem obter todas as tabelas e gráficos de resultados. Pequenas diferenças são aceitáveis e esperadas." Não disse qual das duas referências vale nem deu margem numérica. Efeito: decisão 46. |
| Q3 | Há requisito adicional específico para este artigo? | A especificação prevê essa possibilidade | Respondida em 07/10/2026: "Por enquanto não." A equipe fechou em 07/10/2026: sem requisito adicional (decisão 48). |
| Q4 | O dataset combinado CIRA + DoH-Tunnel-Traffic-HKD conta como "outro conjunto de dados", sendo que Non-DoH e Benign-DoH são os mesmos do CIRA? | Define P2 | Respondida em 07/10/2026: "'Outro conjunto de dados' significa que, após reproduzir o trabalho e obter os seus resultados com os datasets originalmente usados nele, devem fazer tudo novamente com outro dataset não usado no trabalho." Não comentou as duas ressalvas (classes Non-DoH e benigna iguais às do CIRA; réplicas). Efeito: decisão 47. |
| Q5 | A subclassificação por ferramenta de túnel (seção VI-D), que o artigo relata sem método, entra na reprodução? | Escopo de P1 | Respondida em 07/10/2026: "Peço que me expliquem melhor isso depois da aula para entendermos melhor e decidirmos." A equipe decidiu em 07/10/2026 fazer sem esperar (decisão 49). |
| Q6 | O painel interativo (`explainerdashboard`) precisa ser reproduzido, ou bastam as figuras SHAP? | Escopo de P1 | Respondida em 07/10/2026: "Se conseguirem fazer, ótimo. Mas não é necessário. O ponto principal é obterem os gráficos e tabelas." A equipe decidiu em 07/10/2026 implementar o painel (decisão 50). |
| Q7 | Qual a política da disciplina para uso de assistentes de IA no código e no relatório? Precisa ser declarado? | Integridade acadêmica | 07/10/2026, informado por Breno: uso aprovado. `[Preencher: se o relatório precisa de frase de declaração]` |
| Q8 | A sobreposição textual com Mitsuhashi et al. (ISC 2021) pode entrar na apresentação? | Slide 14 do seminário | |
| Q9 | O relatório tem limite de páginas? Pode ser em português? | Formato | |
| Q10 | O repositório deve ser público ou privado com acesso para o professor? | Entrega | |
| Q11 | Em que data a equipe apresenta o seminário, 15/10 ou 20/10? | Ensaio | |

## Decisões da equipe

| # | Decisão | Opções | Recomendação | Decidido |
| --- | --- | --- | --- | --- |
| D1 | Fazer P3 (modificação, ponto extra)? | Sim / Não | Sim, com M1 + M2 de [05-plano-experimental.md](05-plano-experimental.md): custo baixo e as críticas do seminário já são a justificativa. Obriga apresentação em 19/11 | |
| D2 | Segundo dataset | HKD + combinado / outro | HKD + combinado, se Q4 for respondida com sim | |
| D3 | Ambiente | Local / Colab / cluster Apuana | Local, com ambiente fixado; os modelos são pequenos | 07/10/2026: desenvolvimento local; execução dos experimentos local ou no Apuana, as duas valem (decisão 42) |
| D4 | Versionar `CLAUDE.md` e `.claude/` no repositório entregue? | Sim / Não | Sim, se Q7 permitir uso de IA: os quatro passam a trabalhar com as mesmas regras e o uso fica transparente | | 07/10/2026: Não. O repositório é `project/`; `CLAUDE.md`, `.claude/`, `docs/` e `planejamento/` ficam fora dele |
| D5 | Divisão de responsabilidades do projeto | — | Por experimento, com um revisor por experimento diferente do autor | |
| D6 | Escrever aos autores pedindo o código completo? | Sim / Não | Alinhar com o professor antes (Q1) | |

## Ajustes no material do seminário

Encontrados nesta revisão. Entrega dos slides em 14/10.

| Item | Onde | O que fazer |
| --- | --- | --- |
| Recall macro do teste | Slides 33 a 35; seção 4.1 do documento do seminário; guia, bloco 4 | O valor é 96,72%, não 96,71%: (90,2278 + 99,9760 + 99,9416) / 3 = 96,7151. Conferir com `cd project && python3 scripts/metricas_fig4.py` |
| Crítica 4, SMOTE antes dos folds | Slide 27 | A Figura 4a mostra a validação cruzada avaliada sobre 1.043.198 amostras reais, sem sintéticas. A crítica continua válida como "o artigo não especifica, e a ordem descrita sugere vazamento", mas não como fato demonstrado. Reformular para não ser desmontada numa pergunta |
| Quarto integrante | Documento do seminário (seções 1, 5, 7, 9 e 11); tabela de perguntas do guia | O guia já traz Antonio Gonzaga no bloco 2; o documento consolidado e a tabela de perguntas ainda dizem "quarto integrante" |
| Argumento novo para o slide 34 ou 40 | — | O recall de Benign-DoH é 89,7% no treino e 90,2% no teste. O modelo erra a classe benigna igualmente nos dados em que foi ajustado: é capacidade limitada (profundidade 5), não sobreajuste |
| Split estratificado | Slide 18 | As somas das linhas da Figura 4 mostram que o 90/10 é estratificado, embora o texto não diga |
| Contagens brutas | Slide 20 | A diferença para a Tabela I agora tem número: 897.493 / 19.807 / 249.836 no bruto, segundo o README do dataset combinado. Citar a fonte como indireta |
| Figuras do artigo | Slides 7, 22, 32, 37 | Ainda sem as imagens, segundo a lista de pendências do seminário |

## Cronograma proposto

Proposta, a ajustar pela equipe. As datas em negrito são fixas.

| Período | Foco | Marco |
| --- | --- | --- |
| 06/10 a 13/10 | Fechar slides e ensaiar. Em paralelo, sem competir com o seminário: dados baixados (feito em 07/10) e ambiente (tarefa 01) | Perguntas enviadas ao professor (feito em 07/10/2026) |
| **14/10** | **Slides no Classroom** | Checklist do seminário rodada |
| **15/10 e 20/10** | **Apresentação do seminário** | |
| 21/10 a 27/10 | E0, E1 e E2 | Contagens da Tabela I e primeira matriz de confusão |
| 28/10 a 03/11 | E3, E4 e E5 | Reprodução fechada, com variância |
| 04/11 a 09/11 | E6 | Resultados no segundo dataset |
| **10/11** | **Acompanhamento de projeto** | Levar status de uma página e tabela de resultados parciais |
| 11/11 a 16/11 | E8, se D1 for sim. Relatório | Rascunho completo do relatório |
| **17/11** | **Acompanhamento de projeto** | Últimas correções de rumo |
| **18/11** | **Relatório em PDF e link do GitHub** | Checklist do projeto rodada; repositório reproduz do zero |
| **19/11** | **Apresentação, se houver modificação** | |

Riscos e plano B:

| Risco | Sinal | Plano B |
| --- | --- | --- |
| Reprodução não chega perto da Fig. 4b | E3 esgotado e diferença grande | Reportar a diferença, as variantes testadas e a análise das causas. A especificação pede resultados próximos; uma não reprodução bem documentada ainda é defensável, sobretudo com o código dos autores ausente |
| Segundo dataset com colunas incompatíveis | Conferência de colunas falha | Extrair atributos dos PCAPs com o DoHLyzer, ou trocar de dataset |
| Download do CIRA demorado ou indisponível | Formulário sem resposta | Resolvido em 07/10/2026: os três datasets estão em `project/data/raw/` |
| Tempo curto para P3 | E6 não fechado em 09/11 | Cortar P3. É opcional e libera a apresentação de 19/11 |
| Incompatibilidade de bibliotecas | mlxtend, shap ou explainerdashboard não instalam juntos | Substituir o `StackingClassifier` do mlxtend pelo equivalente do scikit-learn, declarando a troca; dispensar o painel se Q6 permitir |

## Primeiros passos concretos

1. Enviar as perguntas ao professor (feito em 07/10/2026; ver "Mensagem enviada ao professor").
2. Aplicar os ajustes do seminário listados acima.
3. Criar o repositório no GitHub a partir de `project/`, com os quatro integrantes (tarefa 01). A central de conhecimento fica fora dele.
4. Dados baixados (07/10/2026); registrar hashes (tarefa 03) e rodar E0 (tarefa 04).
5. Montar o ambiente e fixar as versões.

## Mensagem enviada ao professor

Enviada por Breno em 07/10/2026 (informado por ele; canal `[Preencher]`). Nove perguntas, na ordem abaixo. As respostas são registradas na tabela "Perguntas ao professor", com a data.

| Nº na mensagem | Pergunta | Corresponde a |
| --- | --- | --- |
| 1 | Reimplementar a partir do texto vale como reprodução? | Q1 |
| 2 | Matriz de confusão (Fig. 4b) como alvo; existe tolerância? | Q2 |
| 3 | HKD para transferência e combinado para retreino atendem a "outro conjunto de dados"? Com as duas ressalvas: classes Non-DoH e benigna iguais às do CIRA; fluxos do HKD repetidos 20 vezes no combinado | Q4 |
| 4 | Há requisito adicional para este artigo? | Q3 |
| 5 | A identificação da ferramenta de túnel entra na reprodução? | Q5 |
| 6 | O painel interativo precisa ser reproduzido? | Q6 |
| 7 | Limite de páginas e idioma do relatório | Q9 |
| 8 | Repositório público ou privado? | Q10 |
| 9 | O uso de assistente de IA precisa ser declarado no relatório? | Q7 (parte em aberto) |

Não foram enviadas Q8 e Q11, que são do seminário. O rascunho citava o artigo do HKD como "IEEE TNSM, 2022"; a referência correta é de 2023 (ver [04-dados.md](04-dados.md)). `[Preencher: se a mensagem saiu com 2022 ou 2023]`
