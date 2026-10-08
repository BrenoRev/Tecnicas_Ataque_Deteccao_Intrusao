# 07. Pendências, decisões e cronograma

Atualizado em 08/10/2026, no commit `5999c1b` (branch `tarefa/19-readme-execucao-limpa`). As respostas do professor a Q1 a Q6 são de 07/10/2026 e não foram alteradas.

**Esta é a única lista viva de pendências do projeto.** `POS-IMPLEMENTACAO.md`, `planejamento/MEMORY/STATUS.md` e `LEIA-ME.txt` apontam para a seção "O que resta de pessoa", abaixo, e não mantêm lista própria.

## Estado em 08/10/2026

O projeto está implementado, executado com os dados reais, revisado e com os entregáveis gerados. O que resta é de pessoa e está na seção "O que resta de pessoa".

- Experimentos E0 a E8 executados em 07 e 08/10/2026; resultados em `project/results/`.
- Entregáveis em `project/report/`, com cópia em `entregaveis-apresentacao/`: `relatorio.pdf` (8 páginas), `apresentacao.pptx` (14 slides) e `roteiro.md` (11 min 55 s; apresentam Amanda, Antonio e João).
- Execução limpa feita em 08/10/2026, em clone novo, em 7 h 30 min: 260 de 260 arquivos de `results/` e 56 de 56 de `report/` conferem com os versionados (`planejamento/plan/REVISAO-FINAL.md`, "Execução limpa").
- Revisão final em código sem achado bloqueante; os cinco achados importantes e os nove menores foram tratados; a suíte tem 118 testes (`planejamento/plan/REVISAO-FINAL.md`, "Tratamento").
- `LICENSE` (MIT) na raiz; README da raiz como página de apresentação e guia técnico em `project/README.md`.
- Integração por avanço direto, sem pull request por tarefa (decisão 55f). `main` e `origin/main` estão em `378f170`. Os 15 commits seguintes, até `5999c1b` (revisão final, tratamento dos achados e registro da execução limpa), estão na branch local `tarefa/19-readme-execucao-limpa` e ainda não foram enviados ao GitHub: é o item 1 da lista viva.

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
| Q7 | Qual a política da disciplina para uso de assistentes de IA no código e no relatório? Precisa ser declarado? | Integridade acadêmica | 07/10/2026, informado por Breno: uso aprovado. Parte aberta (se o relatório precisa de frase de declaração): sem resposta do professor; fechado pela equipe em 08/10/2026 (decisão 55): sem frase de declaração no relatório |
| Q8 | A sobreposição textual com Mitsuhashi et al. (ISC 2021) pode entrar na apresentação? | Slide 14 do seminário | em aberto; não foi enviada (é do seminário) |
| Q9 | O relatório tem limite de páginas? Pode ser em português? | Formato | sem resposta do professor; fechado pela equipe em 08/10/2026 (decisão 55): relatório em português, com até 8 páginas |
| Q10 | O repositório deve ser público ou privado com acesso para o professor? | Entrega | sem resposta do professor; fechado pela equipe em 08/10/2026 (decisão 55): repositório público |
| Q11 | Em que data a equipe apresenta o seminário, 15/10 ou 20/10? | Ensaio | em aberto; não foi enviada (é do seminário) |

## Decisões da equipe

| # | Decisão | Opções | Recomendação | Decidido |
| --- | --- | --- | --- | --- |
| D1 | Fazer P3 (modificação, ponto extra)? | Sim / Não | Sim, com M1 + M2 de [05-plano-experimental.md](05-plano-experimental.md): custo baixo e as críticas do seminário já são a justificativa. Obriga apresentação em 19/11 | Sim (decisões 01 e 02). Feito em 08/10/2026: M1 + M2 nos dois datasets, em dez seeds, com seleção em subamostra de 25% do treino (decisões 52 e 54), e M3, a robustez à duração. Resultados em `project/results/e8/corrigida/`. A apresentação de 19/11 passa a ser obrigatória; os slides estão em `project/report/apresentacao.pptx` (decisão 53) |
| D2 | Segundo dataset | HKD + combinado / outro | HKD + combinado, se Q4 for respondida com sim | HKD + combinado (decisões 11, 36 e 47). O dataset principal de P2 é o combinado sem réplicas, em que tudo de P1 é refeito; o combinado como publicado e a transferência para o HKD ficam ao lado. Resultados em `project/results/e6/`. A ressalva de que Non-DoH e Benign-DoH são os do CIRA não foi comentada pelo professor; a equipe fechou o ponto em 08/10/2026, sem resposta dele (decisão 55), e ele continua na página dos encontros ([09-acompanhamento-professor.md](09-acompanhamento-professor.md)) |
| D3 | Ambiente | Local / Colab / cluster Apuana | Local, com ambiente fixado; os modelos são pequenos | 07/10/2026: desenvolvimento local; execução dos experimentos local ou no Apuana, as duas valem (decisão 42). Na prática, tudo rodou na máquina local, na própria sessão de implementação (decisão 44); o Apuana não foi usado e a pasta `jobs/` não existe |
| D4 | Versionar `CLAUDE.md` e `.claude/` no repositório entregue? | Sim / Não | Sim, se Q7 permitir uso de IA: os quatro passam a trabalhar com as mesmas regras e o uso fica transparente | 07/10/2026: Sim (decisão 43, que substituiu a 32). O repositório Git é a raiz, público no GitHub; `CLAUDE.md`, `.claude/`, `docs/`, `planejamento/` e `LEIA-ME.txt` são versionados junto, e o código fica em `project/` |
| D5 | Divisão de responsabilidades do projeto | — | Por experimento, com um revisor por experimento diferente do autor | Fechado em 08/10/2026 pela decisão 55 (d, f), de outro modo que o recomendado: a execução ficou na sessão de implementação (decisão 44); o histórico tem uma só identidade Git (164 commits em `5999c1b`, `git shortlog -sn`), aceito; não há pull request por tarefa nem revisor por experimento. A conferência das transcrições foi feita pelo assistente (decisão 55b). A fala é de três integrantes (`project/report/roteiro.md`) |
| D6 | Escrever aos autores pedindo o código completo? | Sim / Não | Alinhar com o professor antes (Q1) | Não feito; decisão da equipe. Q1 foi respondida em 07/10/2026 (reimplementação aceita) e o sistema foi reimplementado a partir do texto; nenhum contato com os autores está registrado |

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

## Cronograma

As datas em negrito são fixas. A coluna "Estado" é a de 08/10/2026, no commit `5999c1b`: a implementação andou à frente da proposta original, que previa os experimentos entre 21/10 e 16/11.

| Período | Foco | Marco | Estado em 08/10/2026 |
| --- | --- | --- | --- |
| 06/10 a 13/10 | Fechar slides e ensaiar o seminário. Em paralelo: dados e ambiente | Perguntas enviadas ao professor | Dados baixados e perguntas enviadas em 07/10; Q1 a Q6 respondidas em 07/10. Os ajustes do material do seminário (tabela acima) seguem por fazer |
| **14/10** | **Slides do seminário no Classroom** | Checklist do seminário rodada | a fazer |
| **15/10 e 20/10** | **Apresentação do seminário** | | a fazer; a data da equipe (Q11) não está registrada |
| previsto para 21/10 a 16/11 | E0 a E8 | Reprodução, segundo dataset e modificação medidos | **Feito em 07 e 08/10/2026**: E0 a E8 executados com os dados reais, com resumo em `project/results/e<k>/` |
| previsto para 11/11 a 16/11 | Relatório e slides do projeto | Rascunho completo | **Gerados em 08/10/2026**: `project/report/relatorio.tex` e `relatorio.pdf`, `apresentacao.pptx`, `roteiro.md`, tabelas e figuras em `project/report/tables/` e `figures/`. Os números do texto foram conferidos na revisão final (`planejamento/plan/REVISAO-FINAL.md`, V2 e V8). Falta a leitura pelos quatro integrantes |
| até 10/11 | Integração: `push`, pull requests na ordem das tarefas, CI verde | `main` com todas as tarefas | Feito de outro modo em 08/10/2026: avanço direto da `main`, sem pull request por tarefa (decisão 55f), até `378f170`. Falta enviar os 15 commits posteriores, até `5999c1b` |
| **10/11** | **Acompanhamento de projeto** | Status de uma página, tabela de resultados e a conversa sobre as duas leituras de profundidade, o combinado e Q5 | a fazer; a página está pronta em [09-acompanhamento-professor.md](09-acompanhamento-professor.md) |
| 10/11 a 16/11 | README completo, execução limpa por quem não escreveu o código, licença, padrões (tarefas 19 e 22) | Repositório reproduz do zero | **Cumprido em 08/10/2026**: `project/README.md` com os 22 passos; execução limpa na sessão de implementação, em clone novo, e não por quem não escreveu o código (decisões 44 e 55d); `LICENSE`; padrões em `.claude/rules/experimentos.md`. Sem registro: instalação por `requirements.txt` com pip |
| **17/11** | **Acompanhamento de projeto** | Últimas correções de rumo | a fazer |
| **18/11** | **Relatório em PDF e link do GitHub** | Checklist do projeto rodada | a fazer |
| **19/11** | **Apresentação do projeto** (obrigatória: há modificação) | Ensaio cronometrado feito | a fazer |

Riscos e plano B:

| Risco | Sinal | Plano B |
| --- | --- | --- |
| Reprodução não chega perto da Fig. 4b | E3 esgotado e diferença grande | **Ocorreu em parte, e o plano B foi o adotado.** Com a profundidade máxima 5 da Seção IV-B, o modelo empilhado não prediz Benign-DoH no teste; com "variable tree depth" (Algoritmo 1) fica perto do artigo sem igualá-lo. As duas leituras são reportadas lado a lado (decisão 45), com a distância célula a célula e as variantes de E3 (`project/results/e1/RESUMO.md`, `project/results/e3/variante/RESUMO.md`). Nada foi ajustado para aproximar. Vai à conversa com o professor |
| Segundo dataset com colunas incompatíveis | Conferência de colunas falha | Não ocorreu: os cinco arquivos têm as 35 colunas, mesmos nomes e ordem (`project/results/e6/dados/RESUMO.md`). Apareceu outro problema, que a conferência de colunas não pega: os valores de `PacketLengthMode` do malicioso do CIRA não ocorrem no HKD (mesmo resumo). É declarado como limitação |
| Download do CIRA demorado ou indisponível | Formulário sem resposta | Resolvido em 07/10/2026: os três datasets estão em `project/data/raw/` |
| Tempo curto para P3 | E6 não fechado em 09/11 | Não ocorreu: E6 e E8 foram executados em 08/10/2026. A seleção de hiperparâmetros no treino inteiro custaria cerca de 8 horas e foi feita em subamostra de 25% (decisão 54), com a limitação declarada |
| Incompatibilidade de bibliotecas | mlxtend, shap ou explainerdashboard não instalam juntos | Não ocorreu: as três estão fixadas no `pyproject.toml` e o painel foi implementado (decisão 50), em `project/scripts/painel_xai.py`. Restrição encontrada: com o `explainerdashboard` 0.5.8 o painel só é montado com até 1.000 linhas, e a amostra dele é de 333 fluxos por classe (`config.DASHBOARD_SAMPLE_PER_CLASS`) |
| Professor não aceitar o combinado como "outro conjunto de dados" | Resposta na conversa de acompanhamento | Q4 foi respondida sem comentar a ressalva de que Non-DoH e Benign-DoH são os do CIRA. Se a resposta for negativa, a tarefa 13 troca a fonte e a 14 roda de novo (decisões 11 e 39); a alternativa com tráfego benigno próprio de [04-dados.md](04-dados.md) não foi avaliada |
| Entrega com a `main` desatualizada | `origin/main` em `378f170`, 15 commits atrás de `5999c1b` | Enviar a branch e avançar a `main` (decisão 55f), conferir o CI verde no commit final; o link entregue aponta para a `main` |
| Relatório não compila no Overleaf | Erro de fonte ou de pacote | O `.tex` exige XeLaTeX (usa `fontspec`); escolher XeLaTeX no menu do compilador. O PDF versionado foi gerado localmente |

## O que resta de pessoa

Lista viva, conferida em 08/10/2026 no commit `5999c1b`. Nada aqui é feito pelo assistente sem pedido: são envios, ensaios, conversas, leituras e decisões da equipe. As caixas correspondentes de [../POS-IMPLEMENTACAO.md](../POS-IMPLEMENTACAO.md) apontam para o número do item.

| # | Item | Detalhe |
| --- | --- | --- |
| 1 | Enviar os commits finais e avançar a `main` | **Fechado em 08/10/2026:** a ponta do trabalho foi enviada e a `main` avançada por avanço direto (decisão 55); o CI roda a cada envio na `main` |
| 2 | Ensaio cronometrado | Pelos três que apresentam (Amanda, slides 1 a 5; Antonio, 6 a 10; João, 11 a 14), em 15 minutos. O roteiro soma 11 min 55 s (`project/report/roteiro.md`) |
| 3 | Seminário | Ajustes da tabela "Ajustes no material do seminário"; slides em 14/10; apresentação em 15 ou 20/10. Em aberto: Q8 e Q11 |
| 4 | Encontros com o professor, 10/11 e 17/11 | Levar a página [09-acompanhamento-professor.md](09-acompanhamento-professor.md); perguntar também o que a apresentação de 19/11 deve cobrir. Registrar aqui o retorno de cada encontro, com a data, e convertê-lo em ajuste. Resposta que contrarie uma decisão vira `⚠️ REVISAR` em `planejamento/MEMORY/00-decisoes-travadas.md` |
| 5 | Entrega em 18/11 | Rodar a skill `checklist-entrega projeto`; enviar o PDF e o link do GitHub; guardar aqui o comprovante (data, hora e hash do commit entregue). Local de entrega: `[Preencher]` |
| 6 | Apresentação em 19/11 e arguição | Obrigatória, porque há modificação. Preparação: cada um explica o código da parte que apresenta; perguntas prováveis distribuídas (lista em `POS-IMPLEMENTACAO.md`, seção 9) |
| 7 | Leitura do relatório pelos quatro integrantes | Todos precisam conseguir defendê-lo. Três pontos para decidir na leitura: a lista de conferência "pergunta da especificação → seção e parágrafo" não está em arquivo versionado; a seção 5 não tem a figura do modelo modificado ao lado do original (o relatório tem duas figuras em TikZ, do túnel e do sistema do artigo); a diferença de uma amostra no teste em relação ao artigo não foi localizada no texto por busca |
| 8 | GitHub | Proteção da `main` e acesso de escrita dos integrantes, se a equipe quiser |
| 9 | Mensagem enviada ao professor | Canal e ano citado para o artigo do HKD: dois `[Preencher]` na seção "Mensagem enviada ao professor", que só Breno sabe |
| 10 | D6, escrever aos autores pedindo o código | Não feito; decisão da equipe |
| 11 | Citação do dataset CIRA | Duas formas no repositório, nenhuma conferida na fonte: `project/data/README.md` traz "IEEE Cyber Science and Technology Congress, 2020"; `project/report/relatorio.tex` segue a lista do artigo, "2020 IEEE Intl Conf on Dependable, Autonomic and Secure Computing, pp. 63–70". Breno fechou as referências como estão (tabela "Fechado", DOI); a divergência fica registrada ([04-dados.md](04-dados.md)) |
| 12 | Instalação por `requirements.txt` com pip | **Fechado em 08/10/2026:** testada em clone descartável com `venv` de Python 3.12.13 (`pip install -r requirements.txt`, `pip install -e .`, 118 testes verdes); registrado na tarefa 19 do plano |

## Fechado

O que saiu da lista viva, com a data e a evidência.

| Item | Fechado em | Evidência |
| --- | --- | --- |
| Integração sem pull request por tarefa | 08/10/2026 | decisão 55f; `main` avançada até `378f170` (o que falta enviar é o item 1 da lista viva) |
| Conferência das transcrições do artigo | 08/10/2026 | decisão 55b: feita pelo assistente em duas passagens independentes, a pedido de Breno, e não por dois integrantes; Tabela II contra a camada de texto da página 7; Figs. 5, 7 e 8 contra a imagem das páginas 8 e 9; sem divergência |
| Licença do repositório | 08/10/2026 | decisão 55c; `LICENSE` (MIT) na raiz; proposta aplicada, sem escolha explícita |
| DOI das referências | 08/10/2026 | por Breno: fica como está (DOI só nas duas referências conferidas); a especificação pede só o formato IEEE |
| PPTX conferido no Google Slides | 08/10/2026 | por Breno |
| Divisão da fala | 08/10/2026 | por Breno; `project/report/roteiro.md`: três integrantes; o ponto de corte dos blocos é proposta |
| Template no Overleaf | 08/10/2026 | por Breno; se for usar, compilar com XeLaTeX |
| Pontos que dependiam de conversa com o professor | 08/10/2026 | decisão 55a: fechados pela equipe, sem resposta dele; segue o que está implementado. Os pontos continuam em [09-acompanhamento-professor.md](09-acompanhamento-professor.md) |
| Q9, Q10 e a parte aberta de Q7 | 08/10/2026 | decisão 55a: português, até 8 páginas; repositório público; sem frase de declaração de IA. Não são respostas do professor |
| Histórico com uma só identidade Git; dono e revisor por tarefa (D5) | 08/10/2026 | decisões 44 e 55d |
| Decisões 51, 52 e 54, tomadas por recomendação do assistente | 08/10/2026 | decisão 55e: mantidas |
| Tarefa 19: README e execução limpa | 08/10/2026 | `project/README.md`; `planejamento/plan/REVISAO-FINAL.md`, "Execução limpa": 22 passos, 7 h 30 min, 260 de 260 e 56 de 56 |
| Tarefa 22: padrões que nasceram na implementação | 08/10/2026 | `.claude/rules/experimentos.md` |
| Tarefa 23: página de status | 08/10/2026 | [09-acompanhamento-professor.md](09-acompanhamento-professor.md); os encontros são o item 4 da lista viva |
| Tarefa 25: revisão final em código | 08/10/2026 | `planejamento/plan/REVISAO-FINAL.md`: nenhum bloqueante; achados tratados; 118 testes |
| Login do quarto integrante | sem data registrada | `agla` (`CLAUDE.md`, `project/README.md`) |

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
