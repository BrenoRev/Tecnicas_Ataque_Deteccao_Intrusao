# Red-team e endurecimento do plano

Revisão feita em 06/10/2026 por um agente independente, sem acesso às conclusões de quem escreveu o plano. Ele leu a especificação, o artigo (texto extraído do PDF), as decisões e as 22 tarefas, e executou testes em ambiente descartável. Três passes: correção metodológica, implementabilidade, excesso de engenharia.

Resultado: 19 achados, nenhum crítico, 6 altos, 9 médios, 4 baixos. Todos tratados. Nenhuma decisão respondida pelo usuário mudou de conteúdo, com uma exceção sinalizada (o ajuste de limiar de M1, na decisão 02).

## Achados e resolução

| ID | Gravidade | Achado | Como foi verificado | Resolução | Onde |
| --- | --- | --- | --- | --- | --- |
| F1 | alto | A busca de hiperparâmetros da tarefa 11 ou rodava uma vez (contaminando o teste das outras seeds) ou rodava por seed com SMOTE (horas por seed) | Leitura da tarefa; cronometragem de Random Forest em 300 mil linhas | Busca retirada da tarefa 11. A única busca é a de M2, aninhada por seed, sem SMOTE | decisões 15, 23, 25; tarefas 11, 15 |
| F2 | alto | Comparação "empilhado contra Random Forest" com hiperparâmetros afinados para um e transplantados para o outro; "os do artigo" ambíguo para o Random Forest | Leitura; `cross_val_predict` sobre o empilhado pré-treinado levanta `NotFittedError` | Três configurações fixadas antes: A, B (mesmos hiperparâmetros de A) e C (como na Tabela II) | decisão 23; tarefa 11 |
| F3 | alto | Com `use_probas=False`, o empilhado devolve no máximo 27 vetores de probabilidade distintos; a AUC mede a discretização (0,800 contra 0,861 do Random Forest base em teste sintético) e o ajuste de limiar não tem sobre o que operar | Teste executado com três bases pré-treinados | AUC do empilhado reportada de duas formas, nomeadas; ajuste de limiar retirado de M1 | decisões 16, 25; tarefas 06, 08, 15 |
| F4 | alto | A tarefa 15 escolhia a arquitetura do modelo modificado olhando o teste da tarefa 11, e repetia um modelo que a 11 já media | Leitura | Arquitetura fixada antes (Random Forest único com `class_weight`), com justificativa independente dos resultados; "original" definido como o modelo A | decisão 25; tarefa 15 |
| F5 | alto | As dez seeds no combinado não tinham tarefa garantida e herdariam hiperparâmetros selecionados com linhas do CIRA que caem no teste do combinado | Leitura | Dez seeds no combinado movidas para a tarefa 15, com seleção refeita dentro do treino do combinado | decisão 25; tarefas 14, 15 |
| F6 | alto | Itens do gate davam falso verde ou eram impossíveis: o grep de higiene nunca casava por causa do escape de tabela; pytest sem testes sai com código 5; greps de cobertura que não provam nada; PDFs não idênticos entre execuções; tempos dentro do `metrics.json` | Comandos executados | Comandos em bloco de código; teste mínimo na tarefa 01; tempos no `run.json`; comparação só dos `.tex`; greps de cobertura trocados por item de revisão | `VERIFICACAO.md`; tarefas 01, 02, 08, 17, 19 |
| F7 | médio | O scaler ficava fora dos folds em duas validações cruzadas | Leitura | Scaler reajustado por fold na tarefa 08 e como primeiro passo do `Pipeline` na 15; invariante I2 ampliado | `VERIFICACAO.md`; tarefas 08, 15 |
| F8 | médio | Linhas idênticas podem cair em treino e teste sem violar a checagem por índice | Leitura; depende dos dados | Fração do teste duplicada no treino medida na tarefa 05; trilha corrigida reporta métricas também sem essas linhas | I1; tarefas 05, 11 |
| F9 | médio | O meta recebe os rótulos 0, 1, 2 como número; Benign-DoH fica "entre" as outras classes e desacordos são resolvidos como Benign-DoH | Teste executado: trocar a codificação muda 919 de 20.000 predições | Mantido na trilha fiel (é o padrão da biblioteca citada pelo artigo); tabela de decisão do meta e fração de desacordo medidas e declaradas | decisão 09; tarefa 08 |
| F10 | médio | Teste estatístico em aberto; pares não independentes | Leitura | Wilcoxon pareado e contagem de vitórias fixados antes, com a ressalva escrita | decisão 24; tarefas 11, 15 |
| F11 | médio | Grafo com arestas que a tabela não tinha; 09 lia resultado da 08 estando em paralelo; lista de cortes quebrava a tarefa 17; ciclo no plano B do download | Conferência do grafo contra os campos "Depende de" | Resumo dos quatro modelos movido para a 17; 15 passa a depender de 12; opcionais explícitos na 17; download da 13 na onda 0; grafo reescrito como lista | `00-README.md`; tarefas 03, 09, 13, 15, 17 |
| F12 | médio | Trilha obrigatória não cobria E0, a preparação do segundo dataset nem as variantes de E3 | Leitura | Valores `variante` e `dados` admitidos | decisão 26; tarefas 02, 10 |
| F13 | médio | Relatório com o maior risco de prazo: template não lido, sem fluxo repositório → Overleaf, execução limpa na véspera | Leitura | Template e fluxo na onda 0; primeira execução limpa em 10/11; congelamento em 13/11; 19 deixa de depender de 22 | decisão 27; tarefas 17, 18, 19 |
| F14 | médio | Itens sem consumidor no relatório | Comparação da lista da tarefa 17 com o que as outras geram | Ver "Cortes" abaixo | várias |
| F15 | médio | A trilha corrigida não dizia o que fazia com o meta treinado sobre dados vistos pelos bases | Leitura | Declarado: mantém o meta do artigo; corrige a avaliação, não o desenho | decisão 23; tarefas 08, 11 |
| F16 | baixo | A função de avaliação exigia probabilidades e era testada com uma matriz, que não tem | Leitura | Duas funções: `metrics_from_confusion` e `evaluate`; `metricas_fig4.py` continua só com a biblioteca padrão | tarefa 06 |
| F17 | baixo | Três leituras do artigo mais fracas que a direta: o 15:12:12 é a razão arredondada 45:1:12 dividida por três; a Fig. 4a declara validação cruzada na legenda interna; a Fig. 5 usa dados de treino | Texto do artigo e figura renderizada | Textos corrigidos; apoio da decisão 09 trocado para o Algoritmo 1, linha 5; SHAP global calculado também no treino | decisões 09, 14; `docs/02-artigo.md`; tarefas 07, 08, 12 |
| F18 | baixo | Quatro referências `arquivo:linha` deslocadas em uma linha | 26 referências abertas | Corrigidas | tarefas 05, 07, 16, 21 |
| F19 | baixo | Inconsistências menores: gate por tipo contra rodapé das tarefas; Q4 "parar" contra "baixar"; D4 tratada como decidida; matplotlib não declarado; contagem de validação | Leitura; metadados do mlxtend | Alinhadas | `VERIFICACAO.md`; tarefas 01, 04, 05, 13 |

Lacunas da especificação sem tarefa, também apontadas: figuras, algoritmos e equações das seções 3, 4 e 5 do relatório (agora passo da tarefa 18); contagens de validação (tarefa 05, passo 5); perguntas ao professor e material dos acompanhamentos (tarefa 23, nova).

## Cortes por excesso de engenharia

| # | Corte proposto pelo revisor | Aplicado? | Motivo |
| --- | --- | --- | --- |
| O1 | Reduzir E3 de sete para quatro variantes | Sim, em parte | Quatro no núcleo; três viram opcionais, com `oss` como a primeira a cortar |
| O2 | Retirar a variante de ajuste de limiar de M1 | Sim | Não tem sobre o que operar no empilhado e não está definida para três classes (F3) |
| O3 | Retirar a variante "só M2" e a busca com SMOTE | Sim | Custo alto; o efeito de M2 aparece em M1 contra M1+M2 |
| O4 | Cortar a parte B da tarefa 16 | Em parte | Virou opcional dentro de uma tarefa já cortável |
| O5 | Tirar da tarefa 04 os gráficos de densidade da Fig. 2 | Em parte | Opcionais |
| O6 | Cortar a tarefa 22 | Não | Ficou, mas deixou de bloquear a 19. A própria tarefa decide, padrão a padrão, se registrar vale a pena |
| O7 | Fundir 05 com 07 e 13 com 14 | Não | Separadas permitem dividir o trabalho entre integrantes, e a 13 tem uma parte que começa na onda 0 |
| O8 | Tirar taxa base, tempos e estabilidade do SHAP por não terem consumidor | Não | Passaram a ter: entraram na lista da tarefa 17. A taxa base é a crítica 11 do seminário |
| O9 | One-sided selection como parâmetro da tarefa 07 | Sim | Só é implementada se a variante opcional for feita |

Regra seguida: nenhum corte retira proteção contra vazamento de dados.

## O que o revisor confirmou

- A saída de `scripts/metricas_fig4.py` bate com os valores esperados na tarefa 06.
- Tabela I, Tabela II e matrizes da Fig. 4 conferem com o PDF.
- `fit_base_estimators=False` com três bases pré-treinados funciona, e o meta recebe três entradas.
- 22 de 26 referências `arquivo:linha` estavam corretas; as quatro erradas foram corrigidas.
- Todas as seções do relatório, o PDF no template, o repositório comentado, a justificativa do segundo dataset, os slides no modelo do CIn e o formato IEEE têm tarefa.

## Ressalvas que continuam valendo

- Os custos de execução são extrapolados de dados sintéticos. As tarefas 08, 11 e 15 medem antes de lançar tudo.
- O achado F8 (duplicatas) e a compatibilidade do segundo dataset dependem de dados ainda não baixados. Resolvido em 07 e 08/10/2026: os vetores repetidos estão medidos em `project/results/e0/dados/RESUMO.md` e a compatibilidade de colunas em `project/results/e6/dados/RESUMO.md`.
- O revisor leu o plano antes das correções; as correções não passaram por uma segunda rodada independente.
