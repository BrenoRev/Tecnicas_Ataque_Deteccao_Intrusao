# 05. Plano experimental

O que rodar, em que ordem, com que protocolo, e o que cada experimento precisa provar. É proposta da equipe; os pontos que dependem do professor estão em [07-pendencias.md](07-pendencias.md).

> O desenho de E3, E4 e E8 foi refinado no plano de implementação, depois de uma revisão adversarial: E4 passou a ser avaliação em dez seeds com configurações fixas, sem busca; a única busca de hiperparâmetros é a de M2, em E8; o ajuste de limiar saiu de M1; E3 tem quatro variantes obrigatórias e três opcionais. Onde este documento e o plano divergirem, vale [../planejamento/MEMORY/00-decisoes-travadas.md](../planejamento/MEMORY/00-decisoes-travadas.md) (decisões 23 a 26).

## Princípio

Duas trilhas que nunca se misturam:

- **Fiel**: o sistema como o artigo descreve, inclusive nas escolhas que criticamos. Responde ao objetivo P1.
- **Corrigida**: o mesmo sistema com o protocolo consertado (reamostragem dentro dos folds, várias seeds, médias nomeadas). Mostra quanto do resultado publicado sobrevive a uma avaliação limpa.

Todo arquivo de resultado traz no nome e no conteúdo a trilha a que pertence.

## Experimentos

| ID | Experimento | Objetivo da especificação | Alvo de comparação | Depende de |
| --- | --- | --- | --- | --- |
| E0 | Integridade e descrição dos dados | P1, seção 6 do relatório | Tabela I | Download |
| E1 | Reprodução fiel do Balanced Stacked RF | P1 | Fig. 4a, Fig. 4b, Tabela II | E0 |
| E2 | Baselines do artigo | P1 | Tabela II | E0 |
| E3 | Sensibilidade às ambiguidades | P1 | Fig. 4b | E1 |
| E4 | Protocolo corrigido | P1 (discussão), base de P3 | E1 | E1 |
| E5 | Explicabilidade | P1 | Fig. 5 e Fig. 6 | E1 |
| E6 | Segundo dataset | P2 | E1 | E1 |
| E7 | Subclassificação por ferramenta | P1, se o professor pedir | Seção VI-D | E0 |
| E8 | Modificação proposta | P3, opcional | E1 e E4 | E4 |

### E0. Integridade e descrição dos dados

- Baixar, registrar SHA-256, contar linhas por arquivo e por classe.
- Contar NaN, infinitos e duplicatas por classe. Testar quais remoções levam às contagens da Tabela I (889.809 / 19.746 / 249.553).
- Conferir as 29 colunas numéricas contra [04-dados.md](04-dados.md).
- Gerar a tabela de amostras por classe em treino, validação e teste, que a seção 6 do relatório exige.
- Estatísticas descritivas e os gráficos de densidade da Fig. 2, para confirmar que estamos olhando para os mesmos dados.

Critério de conclusão: contagens da Tabela I reproduzidas, ou a diferença documentada com a limpeza que chegou mais perto.

### E1. Reprodução fiel

Passos, na ordem do artigo:

1. Split 90/10 estratificado, seed 42.
2. `MinMaxScaler` ajustado no treino.
3. Non-DoH de treino em três partes disjuntas; cada subconjunto recebe uma parte, todos os maliciosos e a classe benigna aumentada por SMOTE.
4. Três `RandomForestClassifier(n_estimators=10, max_depth=5, max_features=28)`.
5. Empilhamento com regressão logística.
6. Avaliação no teste intocado.

Decisões em aberto: ambiguidades A3 a A10 e A13, A14 de [02-artigo.md](02-artigo.md). Cada uma é resolvida com o "padrão proposto" e registrada.

Saídas: matriz de confusão do teste e da validação cruzada, métricas por classe, macro e ponderadas, AUC, tempo de treino.

Como medir "próximo o suficiente", na falta de critério do professor: diferença absoluta célula a célula contra a Fig. 4b, e diferença em pontos percentuais para acurácia, precisão, recall e F1 macro. O relatório mostra artigo, reprodução e diferença lado a lado.

### E2. Baselines do artigo

Árvore de decisão (profundidade 10), XGBoost e Random Forest (10 árvores), todos com SMOTE, mesmo split e mesmo teste de E1. O artigo não dá os demais hiperparâmetros; usar os padrões das bibliotecas e declarar isso.

A comparação que importa é Random Forest com SMOTE contra o modelo proposto: no artigo a diferença é de 0,0004 em F1. Sem variância entre execuções essa diferença não diz nada, e E4 vai medir.

### E3. Sensibilidade às ambiguidades

Como o artigo não especifica vários pontos, a reprodução é uma família de modelos. Variar um ponto por vez a partir de E1:

| Variante | O que muda |
| --- | --- |
| Com one-sided selection | Aplica OSS antes do SMOTE (A3) |
| Meta com predições out-of-fold | `StackingCVClassifier` (A8) |
| Meta com probabilidades | Em vez de rótulos (A10) |
| `class_weight='balanced'` | Como no script dos autores (A14) |
| `max_features` padrão | Em vez de 28 (crítica 5 do seminário) |

Reportar, para cada variante, a distância até a Fig. 4b. Se alguma variante reproduzir a matriz muito melhor que as outras, é indício de qual foi a configuração real dos autores.

### E4. Protocolo corrigido

- SMOTE dentro de cada fold, com `imblearn.pipeline.Pipeline`.
- N seeds para split e modelos, reportando média e desvio padrão. `[Preencher: N, com justificativa de custo]`
- Métricas por classe, macro e ponderadas, sempre nomeadas; AUC-ROC e AUC-PR; matriz de confusão.
- FPR da classe maliciosa com intervalo de confiança, e a conta de taxa base sob prevalências hipotéticas declaradas como hipotéticas.
- Split por grupo (por exemplo, IP de origem ou janela de tempo) como avaliação adicional, se os dados permitirem. `[A verificar em E0: quantos grupos distintos existem por classe]`
- Comparação entre modelo proposto e Random Forest com SMOTE usando as N execuções pareadas.

### E5. Explicabilidade

- `TreeExplainer` sobre cada Random Forest base; summary plot global e por classe.
- Comparar o ranking de atributos com a Fig. 5 (duração no topo, depois comprimento de pacote e variância do tempo de pacote).
- Dependence plot de `Duration`: verificar o limiar aparente de 40 segundos da Fig. 6a.
- Interaction plot `FlowBytesSent` × `FlowBytesReceived` (Fig. 6b).
- Explicações locais de um fluxo malicioso e de um Non-DoH, no formato das Figs. 7 e 8.
- Estabilidade: o ranking muda entre os três submodelos e entre seeds?

Limitação a declarar: isso explica os modelos base, não a decisão final do empilhamento. Explicar o empilhamento inteiro exigiria um explicador agnóstico a modelo, muito mais caro; se não for feito, dizer.

### E6. Segundo dataset

Depende da escolha em [04-dados.md](04-dados.md). Com o HKD e o combinado:

- **E6a, transferência**: modelo de E1, treinado só no CIRA, aplicado aos fluxos de dnstt, tcp-over-dns e tuns. Métrica: recall de Malicious-DoH por ferramenta. Não há negativos, então não existe precisão nem FPR neste recorte, e o relatório precisa dizer isso.
- **E6b, sistema no outro dataset**: pipeline completo de E1 retreinado no combinado, split 90/10 estratificado, mesmas métricas.

O normalizador é ajustado só no treino de cada cenário. Em E6a, o `MinMaxScaler` do CIRA é aplicado ao HKD; valores fora de [0, 1] são esperados e devem ser contados, porque indicam mudança de distribuição.

### E7. Subclassificação por ferramenta

O artigo dá 99,2% (dns2tcp), 92,9% (iodine) e 91,3% (dnscat2) sem método. Só entra se o professor considerar parte da reprodução.

### E8. Modificação proposta (ponto extra)

Candidatas, da mais barata para a mais cara. Todas saem das críticas do seminário, então a seção 5 do relatório já está meio escrita.

| Candidata | O que muda | Hipótese | Custo |
| --- | --- | --- | --- |
| M1. Protocolo sem vazamento e sem SMOTE | `class_weight` ou ajuste de limiar no lugar de 92% de benignos sintéticos | Recall de Benign-DoH igual ou maior, sem dados inventados | Baixo: é E4 com uma troca |
| M2. Random Forest com aleatorização de atributos | `max_features` menor, mais árvores, profundidade selecionada por busca declarada | Reduz o viés na classe benigna (recall de 90%) | Baixo |
| M3. Robustez à manipulação de duração | Avaliar o modelo com `Duration` e taxas perturbadas de forma válida (sessão fragmentada em fluxos curtos) e treinar uma versão sem os atributos manipuláveis | O modelo original degrada; a versão sem `Duration` perde pouco em dados limpos e ganha sob evasão | Médio; liga com as aulas de ataques adversariais |
| M4. Split por grupo e teste com ferramenta fora do treino | Deixa uma ferramenta de túnel fora do treino | Mede generalização que o artigo não mede | Médio |

Recomendação: M1 + M2 como modificação principal, porque caem quase de graça depois de E4 e atacam diretamente as críticas 3, 4 e 5. M3 se sobrar tempo, por ser a que mais conversa com a disciplina. Fazer qualquer uma obriga a apresentar em 19/11.

Sobre M3: perturbar atributos estatísticos livremente não gera tráfego válido. A perturbação precisa corresponder a algo que o atacante consegue fazer na rede (encerrar e reabrir conexões, inserir atraso, preencher pacotes) e os atributos derivados têm de ser recalculados de forma coerente. Se isso for simplificado, o relatório diz o que foi simplificado.

## Protocolo comum a todos os experimentos

- Teste de 10% separado uma vez, antes de qualquer outra coisa, e usado só para a avaliação final.
- Normalização, reamostragem e seleção de hiperparâmetros veem apenas o treino.
- Uma configuração por experimento em arquivo versionado; seed, versões das bibliotecas e hash dos dados gravados junto com o resultado.
- Resultado numérico sempre em arquivo dentro de `results/`, gerado por script. O relatório cita o arquivo.
- Cada tabela do relatório é gerada por código a partir de `results/`, sem digitação manual de números.

## Métricas e quando cada uma engana

| Métrica | Uso aqui | Cuidado |
| --- | --- | --- |
| Acurácia | Comparar com a Tabela II | Com 77% de Non-DoH, um classificador ruim nas classes DoH ainda passa de 99% |
| Precisão, recall, F1 por classe | Métrica principal | Sempre por classe antes de qualquer média |
| Macro | Resumo que respeita a classe rara | Dizer que é macro |
| Ponderada | Só para comparação com a literatura | Esconde a classe benigna |
| AUC-ROC (OvR) | Comparar com a Tabela II | Pouco sensível com classes desbalanceadas |
| AUC-PR | Classe benigna e classe maliciosa | Depende da prevalência do conjunto |
| FPR da classe maliciosa | Leitura operacional | 3 falsos positivos no teste do artigo: intervalo de confiança largo |

## Ordem e esforço

Sequência: E0, depois E1 e E2 juntos, depois E3, E4, E5 e E6 em paralelo, e E8 por último. Datas em [07-pendencias.md](07-pendencias.md).

O dataset tem cerca de 1,16 milhão de linhas e 29 colunas e os modelos são Random Forests pequenos, então tudo deve rodar em notebook pessoal. O que pode pesar é o SMOTE sobre centenas de milhares de amostras e o `GridSearchCV` com 10 folds. `[A verificar em E1: tempo real de uma execução]`
