# 07. Pendências, decisões e cronograma

Atualizado em 08/10/2026, no commit `759ec29` (branch `tarefa/24-entregaveis`). As respostas do professor a Q1 a Q6 são de 07/10/2026 e não foram alteradas.

## Estado em 08/10/2026

Todos os experimentos (E0 a E8) foram executados com os dados reais em 07 e 08/10/2026, e o relatório e os slides foram gerados: `project/report/relatorio.pdf` (8 páginas), `project/report/apresentacao.pptx` (14 slides) e `project/report/roteiro.md`. Nada foi integrado na `main` ainda: `origin/main` está em `6bf80bd`, e cada tarefa está na própria branch, à espera de pull request. O que falta é quase todo de pessoa e está na seção "O que resta de pessoa".

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
| D1 | Fazer P3 (modificação, ponto extra)? | Sim / Não | Sim, com M1 + M2 de [05-plano-experimental.md](05-plano-experimental.md): custo baixo e as críticas do seminário já são a justificativa. Obriga apresentação em 19/11 | Sim (decisões 01 e 02). Feito em 08/10/2026: M1 + M2 nos dois datasets, em dez seeds, com seleção em subamostra de 25% do treino (decisões 52 e 54), e M3, a robustez à duração. Resultados em `project/results/e8/corrigida/`. A apresentação de 19/11 passa a ser obrigatória; os slides estão em `project/report/apresentacao.pptx` (decisão 53) |
| D2 | Segundo dataset | HKD + combinado / outro | HKD + combinado, se Q4 for respondida com sim | HKD + combinado (decisões 11, 36 e 47). O dataset principal de P2 é o combinado sem réplicas, em que tudo de P1 é refeito; o combinado como publicado e a transferência para o HKD ficam ao lado. Resultados em `project/results/e6/`. A ressalva de que Non-DoH e Benign-DoH são os do CIRA segue em aberto com o professor |
| D3 | Ambiente | Local / Colab / cluster Apuana | Local, com ambiente fixado; os modelos são pequenos | 07/10/2026: desenvolvimento local; execução dos experimentos local ou no Apuana, as duas valem (decisão 42). Na prática, tudo rodou na máquina local, na própria sessão de implementação (decisão 44); o Apuana não foi usado e a pasta `jobs/` não existe |
| D4 | Versionar `CLAUDE.md` e `.claude/` no repositório entregue? | Sim / Não | Sim, se Q7 permitir uso de IA: os quatro passam a trabalhar com as mesmas regras e o uso fica transparente | 07/10/2026: Sim (decisão 43, que substituiu a 32). O repositório Git é a raiz, público no GitHub; `CLAUDE.md`, `.claude/`, `docs/`, `planejamento/` e `LEIA-ME.txt` são versionados junto, e o código fica em `project/` |
| D5 | Divisão de responsabilidades do projeto | — | Por experimento, com um revisor por experimento diferente do autor | Em aberto. A execução ficou na sessão de implementação (decisão 44) e os 137 commits até `759ec29` são de uma só identidade Git (`git shortlog -sn`). Falta definir quem revisa e integra cada pull request, quem confere as transcrições e a divisão da fala; a proposta de fala está em `project/report/roteiro.md` |
| D6 | Escrever aos autores pedindo o código completo? | Sim / Não | Alinhar com o professor antes (Q1) | Sem decisão registrada. Q1 foi respondida em 07/10/2026 (reimplementação aceita) e o sistema foi reimplementado a partir do texto; nenhum contato com os autores está registrado |

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

As datas em negrito são fixas. A coluna "Estado" é a de 08/10/2026: a implementação andou à frente da proposta original, que previa os experimentos entre 21/10 e 16/11.

| Período | Foco | Marco | Estado em 08/10/2026 |
| --- | --- | --- | --- |
| 06/10 a 13/10 | Fechar slides e ensaiar o seminário. Em paralelo: dados e ambiente | Perguntas enviadas ao professor | Dados baixados e perguntas enviadas em 07/10; Q1 a Q6 respondidas em 07/10. Os ajustes do material do seminário (tabela acima) seguem por fazer |
| **14/10** | **Slides do seminário no Classroom** | Checklist do seminário rodada | a fazer |
| **15/10 e 20/10** | **Apresentação do seminário** | | a fazer; a data da equipe (Q11) não está registrada |
| previsto para 21/10 a 16/11 | E0 a E8 | Reprodução, segundo dataset e modificação medidos | **Feito em 07 e 08/10/2026**: E0 a E8 executados com os dados reais, com resumo em `project/results/e<k>/` |
| previsto para 11/11 a 16/11 | Relatório e slides do projeto | Rascunho completo | **Gerados em 08/10/2026**: `project/report/relatorio.tex` e `relatorio.pdf`, `apresentacao.pptx`, `roteiro.md`, tabelas e figuras em `project/report/tables/` e `figures/`. Falta a leitura e a conferência por pessoa |
| até 10/11 | Integração: `push`, pull requests na ordem das tarefas, CI verde | `main` com todas as tarefas | a fazer (pessoa) |
| **10/11** | **Acompanhamento de projeto** | Status de uma página, tabela de resultados e a conversa sobre as duas leituras de profundidade, o combinado e Q5 | a fazer |
| 10/11 a 16/11 | README completo, execução limpa por quem não escreveu o código, licença, padrões (tarefas 19 e 22) | Repositório reproduz do zero | a fazer |
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
| Entrega com a `main` desatualizada | `origin/main` parado em `6bf80bd` | Abrir os pull requests na ordem das tarefas e integrar com o CI verde antes de 10/11; o link entregue aponta para a `main` |
| Relatório não compila no Overleaf | Erro de fonte ou de pacote | O `.tex` exige XeLaTeX (usa `fontspec`); escolher XeLaTeX no menu do compilador. O PDF versionado foi gerado localmente |

## O que resta de pessoa

Nada aqui é feito pelo assistente: são conferências, decisões e conversas da equipe. A lista detalhada, com a evidência de cada item, está em [../POS-IMPLEMENTACAO.md](../POS-IMPLEMENTACAO.md).

| # | Item | Detalhe |
| --- | --- | --- |
| 1 | `push` e pull requests | `origin/main` está em `6bf80bd`. As branches `tarefa/17-tabelas-figuras` e `tarefa/24-entregaveis` não estão no remoto, e `tarefa/16-robustez` está à frente da cópia remota. Abrir os pull requests na ordem das tarefas, cada um lido e aprovado por outro integrante, com o CI verde |
| 2 | Conferência das transcrições por dois integrantes | Valores digitados do manuscrito em `project/src/doh_ids/config.py`: a metade inferior da Tabela II (`TABLE_II_LITERATURE`), a ordem dos atributos da Fig. 5 (`FIG5_RANKING`) e os valores das Figs. 7 e 8 (`FIG7_MALICIOUS`, `FIG8_NON_DOH`). Conferir contra o PDF e registrar quem conferiu |
| 3 | Licença do repositório | Não há arquivo `LICENSE`, e o README de `project/` traz "Licença: [Preencher]". Proposta registrada: MIT, com nota de uso acadêmico e citação do artigo e dos datasets |
| 4 | DOI e conferência das referências | Cada referência do relatório conferida na fonte, com DOI. Inclui a citação do dataset CIRA, que diverge entre `docs/04-dados.md` e a lista do artigo: confirmar no IEEE Xplore |
| 5 | Conferir o PPTX no Google Slides | Abrir `project/report/apresentacao.pptx` no Google Slides e conferir fontes, tabelas e imagens |
| 6 | Ensaio | Cronometrado, em 15 minutos. O roteiro soma 11 min 55 s (`project/report/roteiro.md`) |
| 7 | Confirmar a divisão da fala | O roteiro traz uma proposta por blocos de slides, em ordem alfabética (Amanda 1 a 4, Antonio 5 a 7, Breno 8 a 10, João 11 a 14); a equipe confirma ou troca |
| 8 | Template no Overleaf | Subir `project/report/relatorio.tex` com `tables/` e `figures/` e compilar com **XeLaTeX**; conferir contra o template indicado pelo professor (idioma e limite de páginas: Q9) |
| 9 | Conversa com o professor | (a) As duas leituras de profundidade e o resultado da profundidade 5. (b) O combinado como "outro conjunto de dados", com Non-DoH e Benign-DoH iguais aos do CIRA. (c) Q5: a explicação que ele pediu sobre a identificação da ferramenta de túnel, e o método adotado como leitura da equipe |
| 10 | Perguntas sem resposta | Q9 (limite de páginas e idioma), Q10 (repositório público ou privado; hoje é público, decisão 43) e a parte em aberto de Q7 (frase de declaração do uso de IA). Q8 e Q11 são do seminário |
| 11 | Tarefas do plano em aberto | 19 (README completo com a ordem dos scripts, execução limpa por quem não escreveu o código, checklist), 22 (padrões que nasceram na implementação) e 23 (acompanhamentos de 10/11 e 17/11) |
| 12 | Login do quarto integrante | `CLAUDE.md` traz Antonio Gonzaga com "[Preencher: login]" |
| 13 | Ajustes do material do seminário | Tabela "Ajustes no material do seminário", acima; entrega dos slides em 14/10 |

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
