# 02. O artigo como especificação de implementação

Ficha do que o artigo afirma, com a origem de cada afirmação, e a lista do que ele deixa em aberto. A análise crítica voltada para a apresentação está em `docs/referencias/seminario_doh_xai_cin0114.md`; aqui o foco é o que precisamos para reimplementar.

Referências a seções seguem o manuscrito aceito em `referencias/`.

## 1. O que o sistema faz

Classificador de três classes sobre estatísticas de fluxo (Non-DoH, Benign-DoH, Malicious-DoH), seguido de explicações SHAP em um painel interativo. Entrada: 29 atributos numéricos por fluxo. Saída: rótulo, probabilidade, gráfico e tabela de contribuição (Algoritmo 1).

## 2. Pipeline declarado

| Etapa | O que o artigo diz | Onde |
| --- | --- | --- |
| Dados | CIRA-CIC-DoHBrw-2020; 889.809 Non-DoH, 19.746 Benign-DoH, 249.553 Malicious-DoH | Tabela I |
| Split | 90% treino, 10% teste | III-B |
| Normalização | `MinMaxScaler`; `fit` e `transform` no treino, teste transformado com os parâmetros do treino | III-C, eq. 1 |
| Balanceamento | "one-sided selection with SMOTE"; três splits do treino; cada um recebe uma parte diferente do Non-DoH e as mesmas amostras maliciosas; SMOTE na classe benigna; razão final 15:12:12 em cada subconjunto | III-B |
| Validação | "The training sets were further split into 10 folds" | III-B |
| Busca | `GridSearchCV`, busca exaustiva em valores "(manually) pre-configured", com 10 folds | III-D |
| Modelos base | Três `RandomForestClassifier` (sklearn), `numTrees = 10`, `numFeatures = 28`, profundidade máxima 5, índice de Gini | IV-A, IV-B |
| Meta-classificador | Regressão logística, `StackingClassifier` de `mlxtend.classifier` | IV-B |
| Baselines | Árvore de decisão (profundidade 10, SMOTE), XGBoost (SMOTE), Random Forest (10 árvores, SMOTE) | V-C, Tabela II |
| Métricas | Acurácia, precisão, recall, F1, AUC, matriz de confusão | V-A |
| XAI | `TreeExplainer` do SHAP; summary plot, dependence plot, interaction plot; painel `explainerdashboard` | Alg. 1, VI |
| Ferramenta de túnel | Subclassificação do tráfego malicioso: 99,2% dns2tcp, 92,9% iodine, 91,3% dnscat2 | VI-D |
| Ambiente | Linux, Intel Core i9, 64 GB de RAM, GPU NVIDIA RTX | III-B |

## 3. Resultados que servem de alvo

### 3.1 Matrizes de confusão (Figura 4)

São o único dado bruto do artigo. Linhas = classe real, colunas = predita.

Teste (Fig. 4b), 115.910 fluxos:

| Real \ Predito | Benign | Malicious | Non-DoH | Total |
| --- | --- | --- | --- | --- |
| Benign-DoH | 1.782 | 1 | 192 | 1.975 |
| Malicious-DoH | 0 | 24.949 | 6 | 24.955 |
| Non-DoH | 50 | 2 | 88.928 | 88.980 |

Treino (Fig. 4a), "results are obtained in a 10-fold cross-validation process", 1.043.198 fluxos:

| Real \ Predito | Benign | Malicious | Non-DoH | Total |
| --- | --- | --- | --- | --- |
| Benign-DoH | 15.946 | 9 | 1.816 | 17.771 |
| Malicious-DoH | 9 | 224.496 | 93 | 224.598 |
| Non-DoH | 503 | 10 | 800.316 | 800.829 |

Métricas recalculadas com `scripts/metricas_fig4.py`:

| Conjunto | Acurácia | Precisão macro | Recall macro | F1 macro | Recall Benign-DoH |
| --- | --- | --- | --- | --- | --- |
| Treino (CV) | 99,77% | 98,88% | 96,54% | 97,66% | 89,73% |
| Teste | 99,78% | 99,01% | 96,72% | 97,82% | 90,23% |

### 3.2 Tabela II

| Modelo | AUC | Acurácia | F1 | Precisão | Recall |
| --- | --- | --- | --- | --- | --- |
| Árvore de decisão (profundidade 10, SMOTE) | 0,8617 | 0,9770 | 0,8197 | 0,9658 | 0,7120 |
| XGBoost (SMOTE) | 0,9986 | 0,9927 | 0,9843 | 0,9956 | 0,9732 |
| Random Forest (10 árvores, SMOTE) | 0,9999 | 0,9998 | 0,9987 | 0,9989 | 0,9985 |
| Balanced Stacked RF | 0,9999 | 0,9998 | 0,9991 | 0,9991 | 0,9992 |

### 3.3 Qual alvo vale

A Tabela II e a Figura 4b descrevem o mesmo modelo no mesmo teste e não concordam: a matriz dá 251 erros (acurácia 99,78%), a tabela informa 0,9998 (cerca de 23 erros). Proposta da equipe, a validar com o professor: tratar a Figura 4b como alvo principal, reportar a Tabela II ao lado e documentar a divergência.

## 4. O que a Figura 4a revela e o texto não diz

Três fatos que saem só das contagens:

1. **O split é estratificado.** As somas das linhas do treino (17.771 / 224.598 / 800.829) e do teste (1.975 / 24.955 / 88.980) são exatamente 90% e 10% de cada classe da Tabela I. O artigo não menciona estratificação, mas os números fecham.
2. **A matriz de treino só tem amostras reais.** O total é 1.043.198, que é o treino original, sem nenhuma amostra sintética e sem a redução do balanceamento. Então a avaliação em validação cruzada reportada foi feita sobre o treino original, não sobre os subconjuntos 15:12:12. Isso é compatível com reamostragem dentro dos folds e também com outras leituras (por exemplo, prever o treino inteiro com um modelo já ajustado). O texto não permite decidir.
3. **O erro na classe benigna é viés, não variância.** O recall de Benign-DoH é 89,7% no treino e 90,2% no teste. O modelo erra a classe benigna na mesma proporção nos dados em que foi ajustado, o que aponta para capacidade limitada (profundidade 5, 10 árvores) e não para sobreajuste.

Consequência para o seminário: a crítica "SMOTE antes dos folds" (slide 27) decorre da ordem em que o texto descreve as etapas na seção III-B, mas a Figura 4a não a confirma. A formulação defensável é que o artigo não especifica onde a reamostragem ocorre em relação aos folds, e que a ordem descrita sugere vazamento na seleção de hiperparâmetros.

## 5. Ambiguidades que a reprodução precisa resolver

Cada linha vira uma decisão registrada no relatório. A coluna "padrão proposto" é sugestão da equipe, ainda não validada.

| # | Ponto | O que o artigo diz | Leituras possíveis | Padrão proposto |
| --- | --- | --- | --- | --- |
| A1 (**resolvida em 07/10/2026: remover linhas com NaN reproduz a Tabela I; ver 08-inventario-dados.md**) | Limpeza dos dados | Nada. A Tabela I traz contagens menores que as do dataset bruto (ver [04-dados.md](04-dados.md)) | Remoção de NaN, de duplicatas, de infinitos, ou combinação | Testar as combinações e ficar com a que reproduz as contagens da Tabela I |
| A2 | Quais são os 29 atributos | "29 features"; "selected at random from 28 features" (IV-A) | 29 estatísticas numéricas do DoHLyzer, sem IPs, portas e timestamp | As 29 numéricas; ver 04-dados.md |
| A3 | One-sided selection | Citada uma vez, nunca descrita; a referência [15] é um livro-texto (Witten et al.) | Aplicada ao Non-DoH antes do split em três; ou não aplicada de fato | Rodar sem OSS como base e com OSS como variante |
| A4 | Razão 15:12:12 | Razão final por subconjunto | O artigo parte da razão inicial arredondada 45:1:12 e divide o Non-DoH por três: 15:12:12. Com as contagens reais (266.943 de Non-DoH e 224.598 maliciosos) dá 14,3:12; a diferença é arredondamento, não subamostragem | Benigno reamostrado até igualar o malicioso; reportar a razão obtida |
| A5 | Onde o SMOTE ocorre em relação aos folds | Texto: balanceia e depois divide em folds. Fig. 4a: avaliação sobre amostras reais | Antes dos folds (vazamento) ou dentro | Reprodução fiel segue o texto; variante corrigida usa `imblearn.pipeline.Pipeline` |
| A6 | Parâmetros do SMOTE | Nada | `k_neighbors`, estratégia de amostragem | Padrão da biblioteca, declarado como tal no relatório |
| A7 | Grade do GridSearchCV | "pre-configured parameter values", sem listar. Alg. 1 fala em "variable tree depth" | Desconhecida | Usar os valores finais do artigo; rodar uma grade nossa, declarada, como variante |
| A8 | Dados de treino do meta-classificador | Nada | Predições dos bases no próprio treino (padrão do `StackingClassifier` sem CV) ou out-of-fold (`StackingCVClassifier`) | Seguir a classe citada pelo artigo; variante com out-of-fold |
| A9 | Como três bases treinados em subconjuntos diferentes entram no `StackingClassifier` | Nada | O `StackingClassifier` do mlxtend ajusta todos os bases no mesmo `X` passado a `fit`. Verificado no mlxtend 0.25.0: bases pré-treinados entram com `fit_base_estimators=False` (ver `planejamento/MEMORY/01-discovery-stack.md`) | Bases pré-treinados, um por subconjunto (decisão 09 do planejamento) |
| A10 | Entrada do meta | Nada | Rótulos preditos (padrão, 3 entradas) ou probabilidades (`use_probas=True`, 9 entradas); verificado | Padrão da biblioteca como base; probabilidades como variante |
| A11 | Média das métricas da Tabela II | Nada | Macro, ponderada ou micro. A linha da árvore de decisão (acurácia 0,9770, recall 0,7120) exclui ponderada e micro | Reportar macro e ponderada, sempre nomeadas |
| A12 | AUC multiclasse | Nada | One-vs-rest ou one-vs-one, macro ou ponderada | OvR macro, declarado |
| A13 | Seed | O artigo não informa. O script do repositório usa `random_state=42` no split e no modelo | 42 ou várias | 42 na reprodução fiel; várias seeds na variante corrigida |
| A14 | `class_weight` | O artigo não menciona. O script do repositório usa `class_weight='balanced'` | Com ou sem | Sem na reprodução fiel (segue o texto); com como variante |
| A15 | Modelo explicado pelo SHAP | "TreeExplainer" (Alg. 1); Fig. 5 "from the proposed model", valores "obtained from the training data" | `TreeExplainer` não se aplica ao empilhamento com regressão logística no topo. O código público explica um Random Forest único | Explicar cada RF base com `TreeExplainer` e dizer isso no relatório |
| A16 | Subclassificação por ferramenta (VI-D) | Só as acurácias; nenhum método, split ou modelo | Mesmo sistema com rótulo de ferramenta, ou outro classificador | Perguntar ao professor se entra no escopo de P1 |
| A17 | Tempo de treino "três vezes menor" | Afirmado na introdução e em III-B, sem medição | Não reproduzível como está | Medir e reportar os nossos tempos, sem comparar com número inexistente |
| A18 | Versões das bibliotecas | Nada. O repositório fixa `explainerdashboard==0.3.6.1` e Python 3.8.6 | — | Versões atuais compatíveis, fixadas e listadas |

## 6. Inconsistências internas do artigo

Úteis para a seção de limitações do relatório e para as perguntas do seminário.

- Resumo: precisão 99,91%, recall 99,92%, F1 99,91%. Nenhuma média aplicada à Figura 4b chega nesses valores (macro: 99,01 / 96,72 / 97,82; ponderada: 99,78 nos três).
- Tabela II, acurácia 0,9998, contra 99,78% da matriz.
- "Class-wise accuracy" de 97,3% / 99,99% / 99,8% (V-C): são percentuais normalizados por coluna, isto é, precisão. A própria legenda da Fig. 4 diz "percentage of predicted".
- "Distinguish DoH traffic from normal HTTPS 99.9% of the time" (V-C): juntando as duas classes DoH, o recall de DoH no teste é 99,26%.
- 29 atributos no Algoritmo 1 e na seção VI-C; "at random from 28 features" na IV-A.
- Benign-DoH gerado com "Chrome, Firefox, and safari" (III); a página do dataset lista Chrome e Firefox.
- A seção III diz que o tráfego DoH da camada 1 foi coletado com ferramentas de túnel; na descrição do dataset, a camada 1 separa DoH de Non-DoH com tráfego de navegador.
- A referência dada para one-sided selection e SMOTE ([15]) é um livro-texto de mineração de dados, não os artigos originais dos métodos.
- Os erros da classe benigna são descritos como "less damaging to the system because of their benign nature". Não há análise de custo que sustente a frase.

## 7. Modelo de ameaça

O artigo não declara. A especificação do relatório pede a seção "caso se aplique", e aqui se aplica. O que se infere do texto e da Figura 1:

| Elemento | Inferência | Base |
| --- | --- | --- |
| Objetivo do atacante | Canal encoberto para comando e controle e exfiltração | II-A |
| Capacidade | Host interno comprometido executando cliente de túnel DNS; controle do servidor autoritativo do domínio | Fig. 1, II-A |
| Ferramentas | dns2tcp, DNSCat2, iodine, em configuração de prateleira | Tabela I |
| Canal | DoH (RFC 8484) via resolvedor público: AdGuard, Cloudflare, Google, Quad9 | III |
| Posição do defensor | Observação passiva na borda, só metadados de fluxo, sem decifrar TLS | IV |
| Conhecimento do atacante sobre o detector | Nenhum; atacante não adaptativo | Ausência de qualquer avaliação adversarial |
| Restrições de perturbação | Não se aplica: o artigo não considera evasão | — |

Tudo nesta tabela é inferência da equipe e deve ser apresentado assim.

## 8. Trabalhos relacionados citados

| Ref. | Trabalho | Contribuição segundo o artigo | Limitação segundo o artigo |
| --- | --- | --- | --- |
| [4] | Aiello et al., 2013 | PCA e informação mútua como índice de identificação de túnel DNS | Limiar depende do ambiente; pouca generalidade |
| [9] | Preston, 2019 | Aprendizado supervisionado sobre o domínio primário | Não detecta consulta maliciosa no domínio principal |
| [14] | MontazeriShatoori et al., 2020 | Dataset CIRA-CIC-DoHBrw-2020 e DoHLyzer | — |
| [10] | Banadaki, 2020 | XGBoost, Gradient Boosting e LightGBM no mesmo dataset | Pré-processamento e otimização não descritos; teste com 4.000 amostras |
| [11] | Ramakrishnan e Rajan, 2022 | IDS com rede neural e poucos atributos | Cerca de 90% de acurácia |
| [12] | Jafar et al., 2021 | Oito algoritmos clássicos no mesmo dataset | Só acurácia e tempo; sem métricas por classe |
| [22] | Ahakonye et al., 2022 | Ensemble com tempo de processamento reduzido, 99,5% de acurácia | — |
| [2] | Vekshin et al., 2020 | DoH Insight, detecção de DoH por aprendizado de máquina | Citado só na introdução |
| [24] | Behnke et al., 2021 | Engenharia de atributos e comparação de modelos para DoH malicioso | Citado só como trabalho futuro |

Para o relatório, cada linha precisa da referência completa em formato IEEE, tirada da lista de referências do artigo e conferida na fonte original.

Fora das referências do artigo, com relação direta ao problema (fonte externa à bibliografia da disciplina): Mitsuhashi et al., ISC 2021, sobre identificação de ferramentas de túnel no mesmo dataset. Ver a seção 4.6 do documento do seminário antes de usar.
