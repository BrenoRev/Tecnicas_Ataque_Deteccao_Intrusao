# Guia de estudo do seminário CIN0114

Artigo: Zebin, Rezvy e Luo, IEEE TIFS, v. 17, p. 2339-2349, 2022

Oct 5, 2026 · @Breno Silva

## Divisão dos blocos

Cada um fica com o bloco mais próximo do que já vinha acompanhando no artigo. A ordem segue a do próprio texto, então a apresentação corre do problema até os resultados.

| Integrante | Bloco | Slides | Tempo | Foco |
| --- | --- | --- | --- | --- |
| Breno | 1. Problema e contexto | 3 a 10 | 3 min | Abre a apresentação e fixa o problema de segurança |
| Antonio Gonzaga | 2. Trabalhos relacionados e dados | 11 a 20 | 3,5 min | Base bibliográfica e descrição do dataset |
| João Henrique | 3. Sistema proposto | 21 a 29 | 4 min | Modelagem, validação e crítica de método |
| Amanda | 4. Resultados, XAI e conclusão | 30 a 42 | 4,5 min | Números, explicabilidade e fechamento |

Um ajuste a combinar entre vocês: nas perguntas, questões sobre o recálculo das métricas podem ser redirecionadas ao Breno, que fez as contas, mesmo ele não apresentando o bloco 4.

## Bloco 1, Breno

Objetivo do bloco: deixar claro por que existe um problema antes de qualquer técnica aparecer.

**DNS e DoH**

- DNS tradicional resolve nomes em texto claro na porta 53, então firewall e IDS leem o domínio consultado e aplicam política por nome.
- DoH (RFC 8484) encapsula a consulta DNS dentro de HTTPS na porta 443, cifrada fim a fim com TLS.
- O cliente fala com um resolvedor DoH público. No dataset são quatro: AdGuard, Cloudflare, Google e Quad9.
- Diferença para DoT: DoT usa a porta 853 e dá para separar por porta; DoH se mistura ao HTTPS comum, e esse é o problema.

**O que sobra para o defensor**

- Some o conteúdo da consulta, somem as listas de bloqueio por domínio.
- Resta o metadado do fluxo: duração, número e tamanho de pacotes, bytes trocados e tempo entre pacotes.
- Fluxo é a unidade de análise do artigo: o conjunto de pacotes entre um par de IP e porta de origem e destino, resumido em estatísticas.

**Túnel DNS**

- O atacante registra um domínio e aponta o servidor autoritativo dele para a própria máquina, que vira o outro lado do túnel.
- Dados de outros protocolos são codificados nas consultas e respostas, usando registros como TXT, CNAME e NULL.
- Serve para comando e controle e para exfiltração de dados.
- Ferramentas do dataset: dns2tcp, DNSCat2 e iodine. Sobre DoH, o túnel fica cifrado e invisível à inspeção.

**Modelo de ameaça**

- Três elementos sempre: capacidade do atacante, conhecimento (white-box, gray-box ou black-box) e restrições de perturbação.
- O que inferimos aqui: host interno comprometido, ferramenta de prateleira com configuração padrão, resolvedor DoH público, defensor observando só fluxo na borda, atacante sem conhecimento do detector.
- Crítica 1: nada disso está declarado no artigo. Sem o modelo, não dá para dizer contra qual adversário o IDS foi avaliado.

**Contribuições declaradas pelos autores**

1. Primeira aplicação de IA explicável à detecção de ataques DoH.
2. Classificador Balanced Stacked Random Forest para três classes.
3. Painel interativo de explicação com SHAP.

Decorar: 3 ferramentas de túnel, 4 resolvedores DoH, 3 classes, 29 atributos de fluxo.

## Bloco 2, Antonio Gonzaga

Objetivo do bloco: mostrar de onde vêm os dados e o que o artigo herdou da literatura.

**Trabalhos relacionados**

- Aiello et al., 2013: PCA mais informação mútua para detectar túnel DNS. O limiar só funciona no ambiente em que foi calibrado.
- Preston, 2019: classifica pelo domínio primário, então não pega consulta maliciosa no próprio domínio principal.
- MontazeriShatoori et al., 2020: criaram o CIRA-CIC-DoHBrw-2020 e a ferramenta de extração de atributos (DoHLyzer).
- Banadaki, 2020: XGBoost, Gradient Boosting e LightGBM no mesmo dataset, sem descrever pré-processamento nem ajuste.
- Ramakrishnan e Rajan, 2022: rede neural com poucos atributos, cerca de 90% de acurácia.
- Jafar et al., 2021: oito algoritmos clássicos, reportando só acurácia e tempo.

**Dataset CIRA-CIC-DoHBrw-2020**

- Captura em duas camadas: camada 1 separa DoH de HTTPS comum, camada 2 separa DoH benigno de DoH malicioso.
- Benigno gerado por navegadores (Chrome e Firefox) acessando sites; malicioso gerado pelas ferramentas de túnel.
- Contagens: 889.809 Non-DoH, 19.746 Benign-DoH e 249.553 Malicious-DoH. Razão 45:1:12.
- A classe rara é a benigna, não a maliciosa. Isso é o contrário do que a plateia espera, vale frisar.

**Os 29 atributos**

| Categoria | Quantidade | Exemplos |
| --- | --- | --- |
| Estatística de fluxo | 1 | duração |
| Bytes de fluxo | 4 | bytes enviados e recebidos, e as taxas |
| Comprimento de pacote | 8 | média, mediana, moda, variância, desvio, assimetria |
| Tempo de pacote | 8 | mesmas estatísticas sobre o tempo |
| Diferença requisição e resposta | 8 | mesmas estatísticas sobre o intervalo |

**Pré-processamento e balanceamento**

- Normalização min-max ajustada só no treino e aplicada ao teste. Isso é o jeito certo e evita vazamento.
- Divisão 90% treino e 10% teste.
- O Non-DoH é dividido em três partes disjuntas; as amostras maliciosas são compartilhadas entre as três; SMOTE aumenta a classe benigna. Cada subconjunto fica em 15:12:12.
- SMOTE cria amostras novas interpolando entre vizinhos da classe minoritária. Não é cópia, é dado inventado dentro do espaço de atributos.

**Crítica 3, que fecha o bloco**

- Pela razão declarada, cerca de 92% da classe benigna de cada subconjunto passa a ser sintética, e é justamente a classe com pior desempenho no teste.
- A one-sided selection é citada e nunca descrita.
- As contagens da Tabela I ficam abaixo das publicadas para o mesmo dataset, sem explicar que limpeza foi feita.

Armadilha a antecipar: interpolar fluxos de rede pode gerar combinações impossíveis no protocolo, por exemplo duração e número de pacotes que não existiriam juntos.

## Bloco 3, João Henrique

Objetivo do bloco: explicar o modelo e, logo em seguida, mostrar onde o protocolo experimental falha.

**Random Forest**

- Conjunto de árvores de decisão treinadas em amostras bootstrap do treino, cada divisão escolhendo o melhor atributo dentro de um subconjunto sorteado.
- A aleatoriedade vem de duas fontes: a amostra (bootstrap) e o subconjunto de atributos (numFeatures). É ela que descorrelaciona as árvores.
- Critério de divisão: índice de Gini. Classificação por voto da maioria das árvores.
- Configuração do artigo: 10 árvores, profundidade máxima 5, numFeatures igual a 28.

**Empilhamento (stacking)**

- Os três Random Forests são os modelos base; a previsão de cada um vira atributo de entrada do meta-classificador.
- Meta-classificador: regressão logística. Implementação com StackingClassifier do mlxtend.
- Diferença para votação: na votação os modelos têm peso fixo; no empilhamento o meta aprende quanto confiar em cada base.
- Ponto fino: o meta precisa ser treinado com previsões fora da amostra (out-of-fold), senão aprende sobre previsões que os bases já viram e superestima a confiança.

**Validação**

- GridSearchCV faz busca exaustiva na grade de hiperparâmetros.
- Validação cruzada de 10 folds: o treino é dividido em 10 partes, cada uma serve de validação uma vez.
- Baselines de comparação: árvore de decisão, Random Forest e XGBoost.

**As três críticas do bloco**

1. SMOTE antes dos folds. Vazamento de dados é quando informação da validação chega ao treino. Aqui, uma amostra sintética criada a partir de um ponto que caiu na validação pode estar no treino. Isso infla a validação cruzada que escolheu os hiperparâmetros. O teste de 10% foi separado antes, então não é afetado. O jeito certo é reamostrar dentro de cada fold, com um Pipeline do imbalanced-learn.
2. Divisão e hiperparâmetros. O split é aleatório por fluxo, sem separar sessão, máquina ou período, então fluxos quase idênticos da mesma captura podem cair nos dois lados. E numFeatures de 28 em 29 atributos quase elimina o sorteio de atributos: as árvores ficam parecidas entre si e o Random Forest perde o que o diferencia de um bagging simples.
3. Código publicado. O repositório indicado é um fork do painel de outro projeto dos autores; o único script de modelagem treina um Random Forest único, sem SMOTE, empilhamento ou baselines, e o arquivo de dados que ele lê não está lá.

Decorar: 10 árvores, profundidade 5, numFeatures 28 de 29, 10 folds, 3 submodelos, meta de regressão logística.

## Bloco 4, Amanda

Objetivo do bloco: mostrar o resultado publicado, o que ele realmente significa e o que não se sustenta.

**Métricas, em uma linha cada**

- Precisão: dos que o modelo chamou de X, quantos eram X.
- Recall: dos que eram X, quantos o modelo encontrou.
- F1: média harmônica das duas.
- Acurácia: acertos sobre o total. Engana quando as classes são desbalanceadas.
- Macro: média simples entre classes, dá o mesmo peso à classe rara. Ponderada: média pelo número de amostras. Micro, em classificação multiclasse com rótulo único, é igual à acurácia.

**O que está na matriz de confusão do teste**

- 115.910 fluxos, 251 erros.
- Os percentuais da figura do artigo são normalizados por coluna, ou seja, são precisão, não recall.
- Benign-DoH: precisão 97,27% e recall 90,23%, porque 192 fluxos benignos foram classificados como Non-DoH.
- Acurácia real 99,78%. Macro 99,01% de precisão, 96,71% de recall e 97,82% de F1.

**As divergências numéricas**

- A Tabela II informa acurácia 0,9998, o que corresponderia a cerca de 23 erros, não 251.
- Os 99,91/99,92/99,91% do resumo não saem de nenhuma média aplicada à matriz.
- A linha da árvore de decisão (acurácia 0,9770 com recall 0,7120) indica que as médias são macro, porque ponderada e micro igualariam recall e acurácia. Com macro, o modelo proposto daria 96,71% de recall.
- A vantagem sobre o Random Forest com SMOTE é de 0,0004 em F1, de uma única execução, sem desvio padrão.

**SHAP**

- Valor de Shapley vem da teoria dos jogos: distribui a contribuição de cada atributo para a diferença entre a previsão e uma linha de base.
- TreeExplainer é a versão rápida para modelos de árvore. Não se aplica diretamente a um empilhamento com regressão logística no topo, e o artigo não diz qual modelo foi explicado.
- Resultado: duração do fluxo domina; comprimento de pacote separa melhor o DoH benigno; o gráfico de dependência sugere um limiar perto de 40 segundos.

**As duas críticas finais**

- A explicação publicada entrega ao atacante qual atributo manipular. Fragmentar a sessão em fluxos curtos derruba o atributo dominante, e o artigo não avalia atacante adaptativo.
- Taxa base: os falsos positivos da classe maliciosa são 3 em 90.955, ou 0,0033%. Mas o dataset tem 21,5% de fluxos maliciosos. Numa rede real a proporção é muito menor, e com prevalência hipotética de 0,01% a precisão cairia para cerca de 75%, com uns 330 alarmes falsos a cada 10 milhões de fluxos. A conta é Bayes: quanto mais rara a classe, mais os falsos positivos dominam os alertas.

Decorar: 115.910 fluxos, 251 erros, recall benigno 90,2%, acurácia 99,78% contra 0,9998 da tabela, FPR 0,0033%, prevalência 21,5%.

## Glossário mínimo

Os quatro precisam responder a qualquer um destes sem hesitar, mesmo fora do próprio bloco.

| Termo | Em uma linha |
| --- | --- |
| DoH | Consulta DNS encapsulada em HTTPS na porta 443, cifrada e misturada ao tráfego web |
| Fluxo | Conjunto de pacotes entre um par de IP e porta, resumido em estatísticas |
| Túnel DNS | Canal de dados escondido em consultas e respostas DNS, usado para C2 e exfiltração |
| SMOTE | Gera amostras novas da classe minoritária interpolando entre vizinhos |
| Empilhamento | As previsões de vários modelos viram entrada de um meta-classificador |
| Vazamento de dados | Informação da validação ou do teste chega ao treino e infla o resultado |
| Macro contra ponderada | Macro dá peso igual a cada classe; ponderada dá peso pelo tamanho da classe |
| SHAP | Atribui a cada atributo sua contribuição para a previsão, via valores de Shapley |
| Taxa de falso positivo | Negativos classificados como positivos sobre o total de negativos |
| Taxa base | Proporção real da classe na população; quanto menor, pior a precisão operacional |
| Modelo de ameaça | Capacidade, conhecimento e restrições do atacante considerado |

## Perguntas prováveis e quem responde

Combinem isso antes: quem recebe a pergunta responde, e quem não souber passa o nome do colega em vez de improvisar.

| Pergunta | Responde | Núcleo da resposta |
| --- | --- | --- |
| Por que não basta bloquear a porta 443? | Breno | É a porta de todo o tráfego web; bloquear derruba a navegação |
| Por que não forçar um resolvedor interno? | Breno | Se o cliente usa um resolvedor público, o administrador perde a visibilidade de novo |
| Qual a diferença entre DoH e DoT? | Breno | DoT tem porta própria (853) e dá para separar; DoH se mistura ao HTTPS |
| Por que a classe rara é a benigna? | Quarto integrante | A captura gerou muito tráfego de navegação e de túnel, e pouco DoH benigno |
| Por que SMOTE e não undersampling? | Quarto integrante | Para não descartar dados; o custo é que a classe vira quase toda sintética |
| Interpolar fluxos gera tráfego válido? | Quarto integrante | Não necessariamente, e o artigo não discute restrição de protocolo |
| Qual a diferença entre empilhamento e votação? | João Henrique | Na votação o peso é fixo; no empilhamento o meta aprende quanto confiar em cada base |
| Por que o SMOTE deveria ficar dentro do fold? | João Henrique | Senão amostra sintética derivada da validação entra no treino e infla a métrica |
| Por que numFeatures 28 é um problema? | João Henrique | Elimina o sorteio de atributos e deixa as árvores correlacionadas |
| Como vocês chegaram nesses números recalculados? | Amanda, com apoio do Breno | Recomputamos precisão, recall e F1 direto da matriz de confusão do artigo |
| Por que macro e não ponderada? | Amanda | Ponderada esconde a classe rara, que é justamente onde o modelo erra |
| Se a FPR é 0,0033%, qual o problema? | Amanda | Com classe rara na vida real, os falsos positivos passam a dominar os alertas |
| Vocês vão reproduzir isso no projeto? | Breno | Sim, reimplementando a partir do texto, já que o repositório não traz o modelo proposto |
