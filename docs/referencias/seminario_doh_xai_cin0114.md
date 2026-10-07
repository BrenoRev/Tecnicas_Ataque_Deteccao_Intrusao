# Seminário CIN0114: IDS baseado em IA explicável para ataques DoH

Documento único com a especificação, o artigo, a análise crítica, o roteiro dos slides, a divisão da equipe e o guia de estudo.

## 1. Disciplina e equipe

| Item | Valor |
| --- | --- |
| Disciplina | CIN0114, Técnicas de Ataque e Detecção de Intrusão, 2026.2 |
| Professor | Paulo Freitas de Araujo Filho |
| Equipe | Amanda Arruda (aams2), Breno Silva Xavier de Souza (bsxs), João Henrique Portela (jhpbs), [quarto integrante] |
| Artigo escolhido | Zebin, Rezvy e Luo, IEEE TIFS, v. 17, p. 2339-2349, 2022 |
| Dataset do artigo | CIRA-CIC-DoHBrw-2020 |

Referência completa:

> T. Zebin, S. Rezvy e Y. Luo. An Explainable AI-Based Intrusion Detection System for DNS Over HTTPS (DoH) Attacks. IEEE Transactions on Information Forensics and Security, v. 17, p. 2339-2349, 2022. DOI: 10.1109/TIFS.2022.3183390.

Links:

- Artigo: https://ieeexplore.ieee.org/document/9796558
- Repositório indicado pelos autores: https://github.com/TZebin/DoH-Attack-explainer
- Template de slides do CIn: modelo institucional de apresentação
- Template do relatório: Overleaf indicado pelo professor

## 2. Entregas e prazos

| Data | Entrega |
| --- | --- |
| 17/09/2026 | Registro da equipe e do artigo no Classroom (equipe de 4 pessoas) |
| 14/10/2026 | Slides do seminário pelo Classroom |
| 15/10 e 20/10/2026 | Apresentação do seminário, 15 min mais 5 min de perguntas |
| 18/11/2026 | Relatório em PDF (template Overleaf) e link do GitHub com código comentado |
| 19/11/2026 | Apresentação do projeto, só para equipes que fizerem modificações |

Regras de formato:

- Slides no template institucional do CIn, apenas tópicos, bullets e imagens, sem textos longos.
- Relatório em formato de artigo, referências no padrão IEEE.
- O mesmo artigo vale para o seminário e para o projeto.

Seções obrigatórias do seminário: introdução (motivação, justificativa e contribuições), trabalhos relacionados com contribuições e limitações, solução proposta, experimentos, resultados e conclusão com limitações, problemas e sugestões detalhadas de melhoria.

## 3. O artigo em resumo

Problema: o DoH (RFC 8484) encapsula a consulta DNS dentro de HTTPS na porta 443, cifrada. O administrador de rede perde o nome do domínio e, com ele, a inspeção e o bloqueio por lista. Sobram apenas estatísticas de fluxo. Ferramentas de túnel DNS (dns2tcp, DNSCat2, iodine) usam isso como canal de comando e controle e de exfiltração.

Proposta: classificador de três classes (Non-DoH, Benign-DoH, Malicious-DoH) com três Random Forests treinados em subconjuntos balanceados e um meta-classificador de regressão logística por cima (Balanced Stacked Random Forest), mais explicações com SHAP em um painel interativo.

Dados: CIRA-CIC-DoHBrw-2020, captura em duas camadas, 29 atributos estatísticos de fluxo.

| Classe | Fluxos | Proporção |
| --- | --- | --- |
| Non-DoH | 889.809 | 45 |
| Benign-DoH | 19.746 | 1 |
| Malicious-DoH | 249.553 | 12 |

Pipeline: normalização min-max ajustada só no treino, split 90/10, Non-DoH dividido em três partes disjuntas, amostras maliciosas compartilhadas, SMOTE na classe benigna, razão 15:12:12 por subconjunto, GridSearchCV com validação cruzada de 10 folds.

Resultados publicados (Tabela II):

| Modelo | AUC | Acurácia | F1 |
| --- | --- | --- | --- |
| Árvore de decisão | 0,8617 | 0,9770 | 0,8197 |
| XGBoost | 0,9986 | 0,9927 | 0,9843 |
| Random Forest com SMOTE | 0,9999 | 0,9998 | 0,9987 |
| Balanced Stacked RF (proposto) | 0,9999 | 0,9998 | 0,9991 |

## 4. Análise crítica

### 4.1 Recálculo das métricas

Matriz de confusão do teste (Figura 4b do artigo), 115.910 fluxos e 251 erros:

| Real \ Predito | Benign | Malicious | Non-DoH |
| --- | --- | --- | --- |
| Benign-DoH | 1.782 | 1 | 192 |
| Malicious-DoH | 0 | 24.949 | 6 |
| Non-DoH | 50 | 2 | 88.928 |

Recálculo a partir dessa matriz:

| Classe | Precisão | Recall | F1 |
| --- | --- | --- | --- |
| Benign-DoH | 97,27% | 90,23% | 93,62% |
| Malicious-DoH | 99,99% | 99,98% | 99,98% |
| Non-DoH | 99,78% | 99,94% | 99,86% |
| Média macro | 99,01% | 96,71% | 97,82% |
| Média ponderada | 99,78% | 99,78% | 99,78% |

O que isso revela:

1. Os percentuais da figura são normalizados por coluna, ou seja, são precisão. Os 97,3% que o texto chama de acurácia da classe benigna são precisão; o recall é 90,2%, com 192 fluxos DoH benignos classificados como Non-DoH. A afirmação de separar DoH de HTTPS comum 99,9% das vezes não se sustenta (considerando benigno e malicioso juntos, o recall de DoH é 99,27%).
2. A acurácia da matriz é 99,78%. A Tabela II informa 0,9998, o equivalente a cerca de 23 erros, não 251.
3. Nenhuma média reproduz os 99,91/99,92/99,91% do resumo. A linha da árvore de decisão (acurácia 0,9770 com recall 0,7120) não pode ser média ponderada nem micro, porque essas igualariam recall e acurácia; o provável é macro, que para o modelo proposto daria 96,71% de recall.
4. A vantagem sobre o Random Forest com SMOTE é de 0,0004 em F1, com AUC e acurácia iguais, de uma única execução, sem desvio padrão. A redução de três vezes no tempo de treino não aparece medida.

### 4.2 Método

- SMOTE antes da divisão em 10 folds. O teste de 10% foi separado antes e não é afetado, mas a validação cruzada que guiou o GridSearchCV fica inflada. O certo é reamostrar dentro de cada fold.
- One-sided selection citada e nunca descrita.
- Split aleatório por fluxo, sem separar sessão, máquina ou período de captura.
- Cerca de 92% da classe benigna de cada subconjunto passa a ser sintética, e é justamente a classe com pior desempenho.
- numFeatures igual a 28 com 29 atributos quase anula a aleatorização de atributos do Random Forest.
- O Algoritmo 1 fala em profundidade variável e o texto fixa 5. A grade de busca não é informada.
- As contagens da Tabela I ficam abaixo das publicadas para o mesmo dataset, sem explicar a limpeza.

### 4.3 Auditoria do repositório

O repositório indicado no artigo não contém o sistema proposto:

- É um fork de outro repositório (Shahadate-Rezvy/salmon_explainer), montado para publicar um painel no Heroku.
- O único script de modelagem, `generate_explainers.py`, treina um Random Forest único (`n_estimators=10`, `max_depth=5`, `class_weight='balanced'`), com split estratificado 90/10. Não há SMOTE, one-sided selection, os três submodelos, o meta-classificador, GridSearchCV, validação cruzada, baselines nem a identificação da ferramenta de túnel.
- O script lê `data/new_processed.csv`, ausente do repositório. O único CSV que passou pelo histórico git é de outro domínio (1.144 linhas de bioquímica sanguínea, colunas como ALT, AST e CREA), apagado em maio de 2022.
- Os explainers serializados em `pkls/` são desse outro projeto (rótulos HEALTHY e UNHEALTHY).
- `preprocess.py` e `matrices.py` são cópias de módulos da biblioteca Orange3. O `requirements.txt` não fixa scikit-learn, imbalanced-learn, mlxtend nem xgboost.

Consequência para o projeto: o sistema terá que ser reimplementado a partir do texto.

Nota de segurança para a equipe: não desserializar pickle de terceiros, porque o carregamento executa código arbitrário. A inspeção acima foi feita com análise estática (`pickletools`).

### 4.4 Explicabilidade e ameaça

- A duração do fluxo domina a importância global; atributos de comprimento de pacote separam melhor o DoH benigno; o gráfico de dependência sugere um limiar perto de 40 segundos.
- O TreeExplainer não se aplica diretamente a um empilhamento com regressão logística no topo, e o artigo não diz qual modelo foi explicado. O código público explica um Random Forest único.
- A explicação publicada indica ao atacante adaptativo exatamente qual atributo manipular. Fragmentar a sessão em fluxos curtos derruba o atributo dominante, e esse cenário não é avaliado.
- O artigo não declara modelo de ameaça. O que dá para inferir do texto e da Figura 1: host interno comprometido, ferramenta de prateleira, resolvedor DoH público, defensor observando só fluxo na borda, atacante não adaptativo.

### 4.5 Operação

Falsos positivos da classe maliciosa: 3 em 90.955, ou 0,0033% (intervalo de confiança de 95% entre 0,0007% e 0,0096%, por serem apenas 3 eventos). O dataset tem 21,5% de fluxos maliciosos, bem longe de uma rede real. Com prevalência hipotética de 0,01%, os mesmos TPR e FPR dariam precisão perto de 75% e cerca de 330 alarmes falsos a cada 10 milhões de fluxos.

### 4.6 Atribuição

Trechos do resumo, da abertura da Seção IV e da conclusão são quase idênticos a trechos de Mitsuhashi et al., "Identifying Malicious DNS Tunnel Tools from DoH Traffic Using Hierarchical Machine Learning Classification" (ISC 2021, LNCS v. 13118), que não aparece nas referências. Esse trabalho trata do mesmo problema no mesmo dataset, inclusive a identificação da ferramenta de túnel apresentada na Seção VI.D. Esse ponto só deve entrar na apresentação se o professor validar antes.

### 4.7 Sugestões de melhoria

1. Reamostragem dentro de cada fold e split por sessão ou máquina.
2. Teste com ferramentas de túnel fora do conjunto de treino.
3. Múltiplas execuções com média, desvio e teste estatístico.
4. Explicar o modelo que de fato decide e avaliar a estabilidade das explicações.
5. Medir a degradação sob perturbações válidas de protocolo.

## 5. Divisão da apresentação

| Integrante | Bloco | Slides | Tempo | Foco |
| --- | --- | --- | --- | --- |
| Breno | 1. Problema e contexto | 3 a 10 | 3 min | Abre a apresentação e fixa o problema de segurança |
| Quarto integrante | 2. Trabalhos relacionados e dados | 11 a 20 | 3,5 min | Base bibliográfica e descrição do dataset |
| João Henrique | 3. Sistema proposto | 21 a 29 | 4 min | Modelagem, validação e crítica de método |
| Amanda | 4. Resultados, XAI e conclusão | 30 a 42 | 4,5 min | Números, explicabilidade e fechamento |

Nas perguntas, questões sobre o recálculo das métricas podem ser redirecionadas ao Breno, que fez as contas.

## 6. Roteiro dos slides

Os slides escuros são sempre críticas numeradas, de 1 a 11. Os claros são exposição e os vermelhos são separadores entre blocos.

1. Capa
2. Roteiro
3. Separador do bloco 1
4. A pergunta do artigo: dá para detectar um túnel DNS quando todo o tráfego está cifrado?
5. DNS em claro e DoH, em duas colunas
6. O que o defensor perde
7. Túnel DNS sobre DoH (figura 1 do artigo)
8. Modelo de ameaça inferido
9. Crítica 1: não há modelo de ameaça declarado
10. Contribuições declaradas
11. Separador do bloco 2
12. Trabalhos relacionados, parte 1
13. Trabalhos relacionados, parte 2
14. Crítica 2: a lacuna alegada (só com validação do professor)
15. Dataset CIRA-CIC-DoHBrw-2020
16. As três classes
17. Os 29 atributos estatísticos
18. Pré-processamento
19. Balanceamento em três subconjuntos
20. Crítica 3: o que o balanceamento esconde
21. Separador do bloco 3
22. Arquitetura em quatro etapas (figura 3 do artigo)
23. Submodelos
24. Empilhamento
25. Seleção de hiperparâmetros
26. Métricas usadas
27. Crítica 4: SMOTE antes dos folds
28. Crítica 5: divisão e hiperparâmetros
29. Crítica 6: o código publicado
30. Separador do bloco 4
31. Resultados do artigo (Tabela II)
32. Matriz de confusão do teste (figura 4b)
33. O que recalculamos a partir da matriz
34. Crítica 7: precisão apresentada como acurácia
35. Crítica 8: a acurácia não fecha
36. Crítica 9: ganho sem variância
37. Explicabilidade com SHAP (figuras 5 e 6)
38. Crítica 10: a explicação também serve ao atacante
39. Crítica 11: taxa base e operação
40. Limitações do sistema proposto
41. Sugestões de melhoria
42. Conclusão
43. Obrigado e referências

Figuras do artigo a inserir, com citação da fonte dentro da própria imagem: slides 7, 22, 32, 37.

## 7. Guia de estudo por bloco

### Bloco 1, Breno

**DNS e DoH**

- DNS tradicional resolve nomes em texto claro na porta 53, então firewall e IDS leem o domínio e aplicam política por nome.
- DoH encapsula a consulta DNS dentro de HTTPS na porta 443, cifrada fim a fim com TLS.
- O cliente fala com um resolvedor DoH público. No dataset são quatro: AdGuard, Cloudflare, Google e Quad9.
- Diferença para DoT: DoT usa a porta 853 e dá para separar por porta; DoH se mistura ao HTTPS comum.

**O que sobra para o defensor**

- Some o conteúdo da consulta, somem as listas de bloqueio por domínio.
- Resta o metadado do fluxo: duração, número e tamanho de pacotes, bytes trocados e tempo entre pacotes.
- Fluxo é a unidade de análise: o conjunto de pacotes entre um par de IP e porta de origem e destino, resumido em estatísticas.

**Túnel DNS**

- O atacante registra um domínio e aponta o servidor autoritativo para a própria máquina, que vira o outro lado do túnel.
- Dados de outros protocolos são codificados nas consultas e respostas, com registros como TXT, CNAME e NULL.
- Serve para comando e controle e para exfiltração.
- Ferramentas do dataset: dns2tcp, DNSCat2 e iodine. Sobre DoH, o túnel fica cifrado.

**Modelo de ameaça**

- Três elementos: capacidade do atacante, conhecimento (white-box, gray-box ou black-box) e restrições de perturbação.
- Inferência para este artigo: host interno comprometido, ferramenta com configuração padrão, resolvedor DoH público, defensor só com fluxo na borda, atacante sem conhecimento do detector.
- Crítica 1: nada disso está declarado.

**Contribuições declaradas**

1. Primeira aplicação de IA explicável à detecção de ataques DoH.
2. Classificador Balanced Stacked Random Forest para três classes.
3. Painel interativo de explicação com SHAP.

Decorar: 3 ferramentas de túnel, 4 resolvedores, 3 classes, 29 atributos.

### Bloco 2, quarto integrante

**Trabalhos relacionados**

- Aiello et al., 2013: PCA mais informação mútua. O limiar só funciona no ambiente calibrado.
- Preston, 2019: classifica pelo domínio primário, não pega consulta maliciosa no domínio principal.
- MontazeriShatoori et al., 2020: criaram o dataset e a ferramenta de extração (DoHLyzer).
- Banadaki, 2020: boosting no mesmo dataset, sem descrever pré-processamento nem ajuste.
- Ramakrishnan e Rajan, 2022: rede neural com poucos atributos, cerca de 90% de acurácia.
- Jafar et al., 2021: oito algoritmos clássicos, reportando só acurácia e tempo.

**Dataset**

- Duas camadas: a 1 separa DoH de HTTPS comum, a 2 separa DoH benigno de malicioso.
- Benigno gerado por navegadores (Chrome e Firefox); malicioso pelas ferramentas de túnel.
- Contagens e razão 45:1:12 na seção 3 deste documento.
- A classe rara é a benigna, não a maliciosa. Vale frisar, porque é o contrário do que a plateia espera.

**Os 29 atributos**

| Categoria | Quantidade | Exemplos |
| --- | --- | --- |
| Estatística de fluxo | 1 | duração |
| Bytes de fluxo | 4 | bytes enviados e recebidos, e as taxas |
| Comprimento de pacote | 8 | média, mediana, moda, variância, desvio, assimetria |
| Tempo de pacote | 8 | mesmas estatísticas sobre o tempo |
| Diferença requisição e resposta | 8 | mesmas estatísticas sobre o intervalo |

**Pré-processamento e balanceamento**

- Min-max ajustada só no treino e aplicada ao teste. Esse ponto está certo no artigo e evita vazamento.
- Split 90/10.
- Non-DoH em três partes disjuntas, maliciosos compartilhados, SMOTE no benigno, 15:12:12.
- SMOTE cria amostras interpolando entre vizinhos da classe minoritária. Não é cópia, é dado novo no espaço de atributos.

Armadilha a antecipar: interpolar fluxos pode gerar combinações impossíveis no protocolo.

### Bloco 3, João Henrique

**Random Forest**

- Árvores treinadas em amostras bootstrap, cada divisão escolhendo o melhor atributo dentro de um subconjunto sorteado.
- A aleatoriedade vem do bootstrap e do sorteio de atributos (numFeatures). É ela que descorrelaciona as árvores.
- Critério de divisão: índice de Gini. Classificação por voto da maioria.
- Configuração do artigo: 10 árvores, profundidade máxima 5, numFeatures 28.

**Empilhamento**

- Os três Random Forests são os modelos base; a previsão de cada um vira atributo de entrada do meta-classificador.
- Meta: regressão logística, via StackingClassifier do mlxtend.
- Diferença para votação: na votação o peso é fixo; no empilhamento o meta aprende quanto confiar em cada base.
- O meta precisa de previsões fora da amostra (out-of-fold), senão superestima a confiança.

**Validação**

- GridSearchCV faz busca exaustiva na grade.
- Validação cruzada de 10 folds sobre o treino.
- Baselines: árvore de decisão, Random Forest e XGBoost.

**As três críticas do bloco**

1. SMOTE antes dos folds, o que infla a validação cruzada que escolheu os hiperparâmetros. O jeito certo é reamostrar dentro de cada fold, com Pipeline do imbalanced-learn.
2. Split aleatório por fluxo e numFeatures de 28 em 29, que deixa as árvores correlacionadas.
3. O código publicado não implementa o modelo proposto (seção 4.3 deste documento).

Decorar: 10 árvores, profundidade 5, numFeatures 28 de 29, 10 folds, 3 submodelos, meta de regressão logística.

### Bloco 4, Amanda

**Métricas, em uma linha cada**

- Precisão: dos que o modelo chamou de X, quantos eram X.
- Recall: dos que eram X, quantos o modelo encontrou.
- F1: média harmônica das duas.
- Acurácia: acertos sobre o total. Engana quando as classes são desbalanceadas.
- Macro: média simples entre classes, peso igual para a classe rara. Ponderada: média pelo número de amostras. Micro, com rótulo único, é igual à acurácia.

**Números e divergências**

- Todos na seção 4.1 deste documento.
- O essencial: 115.910 fluxos, 251 erros, recall benigno de 90,2%, acurácia real de 99,78% contra 0,9998 da Tabela II, e os valores do resumo que nenhuma média reproduz.

**SHAP**

- Valor de Shapley vem da teoria dos jogos: distribui a contribuição de cada atributo para a diferença entre a previsão e uma linha de base.
- TreeExplainer é a versão rápida para modelos de árvore, e não se aplica diretamente ao empilhamento usado.
- Resultado: duração domina, comprimento de pacote separa o benigno, limiar aparente perto de 40 segundos.

**As duas críticas finais**

- A explicação entrega ao atacante qual atributo manipular, e o artigo não avalia atacante adaptativo.
- Taxa base: a conta é de Bayes, quanto mais rara a classe, mais os falsos positivos dominam os alertas (seção 4.5).

Decorar: 115.910 fluxos, 251 erros, recall benigno 90,2%, acurácia 99,78% contra 0,9998, FPR 0,0033%, prevalência 21,5%.

## 8. Glossário mínimo

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

## 9. Perguntas prováveis e quem responde

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

## 10. Projeto final

Escopo definido pela especificação:

1. Reproduzir o artigo, implementando e executando o código, com resultados próximos aos publicados.
2. Rodar o sistema proposto em outro dataset, com justificativa no relatório.
3. Opcional, com ponto extra: propor, implementar e avaliar modificações que melhorem o sistema.

Pontos de atenção para a reprodução:

- O modelo proposto precisa ser reimplementado a partir do texto (scikit-learn, imbalanced-learn e mlxtend).
- Usar a matriz de confusão da Figura 4b como alvo principal da reprodução, por ser o único dado bruto do artigo, e relatar a divergência com a Tabela II.
- Documentar quantas linhas sobram do dataset depois de tratar valores ausentes e duplicatas.

Candidatos a segundo dataset (fontes externas à bibliografia da disciplina):

- DoH-Tunnel-Traffic-HKD: PCAPs de túneis DoH gerados por dnstt, tcp-over-dns e tuns, com CSVs de atributos extraídos pelo DoHlyzer. Nenhuma dessas ferramentas está no CIRA-CIC-DoHBrw-2020, então testa a generalização. Só tem tráfego malicioso, então para as três classes é preciso a versão combinada com o CIRA. O CSV consolidado é aumentado, simulando 20 máquinas cliente, e isso precisa constar no relatório.
- DoH-DGA-Malware-Traffic-HKD: tráfego DoH de malwares baseados em DGA, também com versão combinada. Conversa com o trabalho futuro proposto pelo próprio artigo.

Em qualquer caso, conferir coluna a coluna se os atributos batem com os 29 do CIRA antes de fechar a escolha.

Observação: o repositório endgameinc/dga_predict não serve como segundo dataset. Ele classifica nomes de domínio com LSTM e bigramas, e sob DoH o nome do domínio trafega cifrado, além de o sistema do artigo consumir estatísticas de fluxo.

Estrutura mínima do repositório:

```
projeto/
├── README.md
├── requirements.txt
├── data/
├── notebooks/
├── src/
├── results/
└── report/
```

## 11. Pendências

- [ ] Fechar o quarto integrante e registrar a equipe no Classroom.
- [ ] Confirmar com o professor se a reimplementação a partir do texto é aceita e qual resultado vale como referência de "resultados próximos".
- [ ] Perguntar se há requisito adicional específico para este artigo.
- [ ] Decidir, com o professor, se a sobreposição com Mitsuhashi et al. entra na apresentação (slide 14).
- [ ] Trocar `[quarto integrante]` nos slides 1 e 3.
- [ ] Inserir as figuras do artigo nos slides 7, 22, 32 e 37, com a citação da fonte na imagem.
- [ ] Ensaiar cronometrando bloco a bloco.
