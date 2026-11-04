# 02. O artigo como especificação de implementação

Ficha do que o artigo afirma, com a origem de cada afirmação, e a lista do que ele deixa em aberto. A análise crítica voltada para a apresentação está em `docs/referencias/seminario_doh_xai_cin0114.md`; aqui o foco é o que precisamos para reimplementar.

Referências a seções seguem o manuscrito aceito em `referencias/`.

> Atualizado em 08/10/2026, no commit `759ec29`: o sistema foi implementado e executado. A seção 5 traz a leitura adotada em cada ambiguidade e o arquivo e a função de `project/` em que ela está. Os números medidos ficam em `project/results/`; aqui só entram os que são necessários para ler a tabela, com o caminho do arquivo.

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

Métricas recalculadas com `project/scripts/metricas_fig4.py`. As duas matrizes estão em `project/src/doh_ids/config.py` (`FIG4A_CONFUSION`, `FIG4B_CONFUSION`), reordenadas para a codificação do projeto (Non-DoH, Benign-DoH, Malicious-DoH):

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

A Tabela II e a Figura 4b descrevem o mesmo modelo no mesmo teste e não concordam: a matriz dá 251 erros (acurácia 99,78%), a tabela informa 0,9998 (cerca de 23 erros).

O professor respondeu em 07/10/2026 (Q2 em [07-pendencias.md](07-pendencias.md)): o alvo são todas as tabelas e gráficos de resultado, e pequenas diferenças são aceitáveis. Ele não disse qual das duas referências vale. As duas seguem reportadas (decisão 46): a reprodução fica ao lado da Fig. 4a e da Fig. 4b, célula a célula, em `project/results/e1/RESUMO.md`, e ao lado da Tabela II inteira em `project/results/e2/fiel/RESUMO.md`. A metade inferior da Tabela II (resultados de outros trabalhos) está transcrita em `config.py` (`TABLE_II_LITERATURE`).

## 4. O que a Figura 4a revela e o texto não diz

Três fatos que saem só das contagens:

1. **O split é estratificado.** As somas das linhas do treino (17.771 / 224.598 / 800.829) e do teste (1.975 / 24.955 / 88.980) são exatamente 90% e 10% de cada classe da Tabela I. O artigo não menciona estratificação, mas os números fecham.
2. **A matriz de treino só tem amostras reais.** O total é 1.043.198, que é o treino original, sem nenhuma amostra sintética e sem a redução do balanceamento. Então a avaliação em validação cruzada reportada foi feita sobre o treino original, não sobre os subconjuntos 15:12:12. Isso é compatível com reamostragem dentro dos folds e também com outras leituras (por exemplo, prever o treino inteiro com um modelo já ajustado). O texto não permite decidir.
3. **O erro na classe benigna é viés, não variância.** O recall de Benign-DoH é 89,7% no treino e 90,2% no teste. O modelo erra a classe benigna na mesma proporção nos dados em que foi ajustado, o que aponta para capacidade limitada (profundidade 5, 10 árvores) e não para sobreajuste.

Os itens 1 e 2 foram levados ao código: o split é estratificado (`splits.stratified_split`) e a validação cruzada refaz normalizador, subconjuntos, SMOTE, bases e meta em cada fold e soma só amostras reais (`system.cross_validated_confusion`). Sobre o item 3, o que a reprodução mediu com a seed 42 (`project/results/e1/RESUMO.md`): com profundidade máxima 5, o modelo empilhado tem recall de Benign-DoH de 0,00% no teste, e os três Random Forests base, avaliados sozinhos, têm 85,16%, 85,97% e 85,16%; sem limite de profundidade, o empilhado tem 92,91%. O recall de cerca de 90% do artigo não saiu de nenhuma das duas leituras.

Consequência para o seminário: a crítica "SMOTE antes dos folds" (slide 27) decorre da ordem em que o texto descreve as etapas na seção III-B, mas a Figura 4a não a confirma. A formulação defensável é que o artigo não especifica onde a reamostragem ocorre em relação aos folds, e que a ordem descrita sugere vazamento na seleção de hiperparâmetros.

## 5. Ambiguidades que a reprodução precisa resolver

Cada linha é uma decisão registrada no relatório. A coluna "leitura adotada" diz o que o código faz; "onde no código" aponta o arquivo e a função em `project/` (os módulos são os de `src/doh_ids/`). O código não cita estes identificadores: o rastro ambiguidade → código fica nesta tabela.

| # | Ponto | O que o artigo diz | Leituras possíveis | Leitura adotada | Onde no código |
| --- | --- | --- | --- | --- | --- |
| A1 | Limpeza dos dados | Nada. A Tabela I traz contagens menores que as do dataset bruto (ver [04-dados.md](04-dados.md)) | Remoção de NaN, de duplicatas, de infinitos, ou combinação | Remover as linhas com NaN em algum dos 29 atributos, e só isso. Reproduz a Tabela I com diferença zero nas três classes. Quatro regras empatam (NaN; NaN e infinito; NaN e duplicatas exatas; as três juntas), porque não há infinito nem duplicata exata: fica a mais simples (`project/results/e0/dados/RESUMO.md`) | `data.clean_flows`; as regras são medidas, uma por linha, em `scripts/e0_dados.py` (`cleaning_table`) |
| A2 | Quais são os 29 atributos | "29 features"; "selected at random from 28 features" (IV-A) | 29 estatísticas numéricas do DoHLyzer, sem IPs, portas e timestamp | As 29 numéricas, pelo nome e na ordem do cabeçalho; os cinco identificadores nunca chegam ao modelo | `config.FEATURE_COLUMNS`, `config.ID_COLUMNS`; `data.feature_matrix` |
| A3 | One-sided selection | Citada uma vez, nunca descrita; a referência [15] é um livro-texto (Witten et al.) | Aplicada ao Non-DoH antes do split em três; ou não aplicada de fato | Não aplicada: o Non-DoH só é dividido em três partes. A variante com one-sided selection não foi medida (declarado em `project/results/e3/variante/RESUMO.md`, "O que não foi medido") | comentário em `system.fit_system`; `config.FIEL_READINGS["one_sided_selection"]` |
| A4 | Razão 15:12:12 | Razão final por subconjunto | O artigo parte da razão inicial arredondada 45:1:12 e divide o Non-DoH por três: 15:12:12. Com as contagens reais dá 14,3:12; a diferença é arredondamento, não subamostragem | Benigno aumentado até igualar o malicioso; a razão obtida é gravada ao lado da declarada. Medido: 14,3:12,0:12,0 nos três subconjuntos, com 92,09% de Benign-DoH sintético (`project/results/e1/fiel/RESUMO.md`) | `splits.balanced_subsets`; `config.ARTICLE_SUBSET_RATIO` |
| A5 | Onde o SMOTE ocorre em relação aos folds | Texto: balanceia e depois divide em folds. Fig. 4a: avaliação sobre amostras reais | Antes dos folds (vazamento) ou dentro | Dentro: em cada fold, normalizador, subconjuntos, SMOTE, bases e meta são refeitos com os nove folds de treino, e o fold de fora só é transformado e predito. É o que a Fig. 4a sustenta (matriz só com amostras reais). Vale para as duas leituras de profundidade; não há variante com SMOTE antes dos folds | `system.cross_validated_confusion`; `config.FIEL_READINGS["cross_validation"]` |
| A6 | Parâmetros do SMOTE | Nada | `k_neighbors`, estratégia de amostragem | Padrão do imbalanced-learn; só Benign-DoH é aumentada, até o tamanho de Malicious-DoH no subconjunto | `splits.balanced_subsets` (`sampling_strategy={BENIGN: len(malicious)}`) |
| A7 | Grade do GridSearchCV | "pre-configured parameter values", sem listar. Alg. 1 fala em "variable tree depth" | Desconhecida | A busca do artigo não é refeita: os hiperparâmetros são os valores finais das Seções IV-A e IV-B. A única busca do projeto é a da modificação (E8), com grade de oito combinações declarada por nós | `config.FIEL_READINGS["hyperparameter_source"]`; grade nossa em `config.MODIFIED_GRID`, usada por `scripts/e8_modificacao.py` |
| A8 | Dados de treino do meta-classificador | Nada | Predições dos bases no próprio treino (padrão do `StackingClassifier` sem CV) ou out-of-fold (`StackingCVClassifier`) | Predições dos bases sobre o treino original normalizado, só com amostras reais (linha 5 do Algoritmo 1). Variante medida: meta ajustado na união dos três subconjuntos (`meta_uniao`, E3). Predições fora da amostra (`StackingCVClassifier`) não foram medidas: a classe ajusta todos os bases no mesmo conjunto | `models.stacked_forest`; `system.fit_system` (argumento `meta_on_subsets`) |
| A9 | Como três bases treinados em subconjuntos diferentes entram no `StackingClassifier` | Nada | O `StackingClassifier` do mlxtend ajusta todos os bases no mesmo `X` passado a `fit`. Verificado no mlxtend 0.25.0: bases pré-treinados entram com `fit_base_estimators=False` (ver `planejamento/MEMORY/01-discovery-stack.md`) | Bases pré-treinados, um por subconjunto (decisão 09) | `models.base_forests`; `models.stacked_forest` (`fit_base_estimators=False`, `use_clones=False`) |
| A10 | Entrada do meta | Nada | Rótulos preditos (padrão, 3 entradas) ou probabilidades (`use_probas=True`, 9 entradas); verificado | Rótulo predito por cada base, três entradas. Variante medida: probabilidades (`use_probas`, E3). A tabela de decisão do meta por combinação de rótulos é gravada em E1 | `models.stacked_forest` (argumento `use_probas`); `scripts/e1_reproducao.py` (`meta_decision_table`) |
| A11 | Média das métricas da Tabela II | Nada | Macro, ponderada ou micro. A linha da árvore de decisão (acurácia 0,9770, recall 0,7120) exclui ponderada e micro | Por classe, depois macro e ponderada, sempre nomeadas; cada valor da Tabela II fica ao lado das duas | `evaluate.metrics_from_confusion`, `evaluate.evaluate` |
| A12 | AUC multiclasse | Nada | One-vs-rest ou one-vs-one, macro ou ponderada | One-vs-rest macro. No modelo empilhado, duas formas nomeadas: saída do meta (`roc_auc_ovr_macro`) e média das probabilidades dos bases (`roc_auc_ovr_macro_base_mean`) | `evaluate.evaluate`, que calcula a AUC com `multi_class="ovr"` e `average="macro"`; `scripts/e1_reproducao.py` (`base_mean_proba`) |
| A13 | Seed | O artigo não informa. O script do repositório usa `random_state=42` no split e no modelo | 42 ou várias | 42 nas trilhas `fiel` e `variante`; dez seeds, de 0 a 9, na trilha `corrigida` | `config.SEED_FIEL`, `config.SEEDS_CORRIGIDA`, `config.smote_seed` |
| A14 | `class_weight` | O artigo não menciona. O script do repositório usa `class_weight='balanced'` | Com ou sem | Sem. Variante medida: `class_weight='balanced'` nos três bases (`class_weight`, E3) | `models.base_forests` (argumento `class_weight`, padrão `None`) |
| A15 | Modelo explicado pelo SHAP | "TreeExplainer" (Alg. 1); Fig. 5 "from the proposed model", valores "obtained from the training data" | `TreeExplainer` não se aplica ao empilhamento com regressão logística no topo. O código público explica um Random Forest único | `TreeExplainer` sobre cada Random Forest base; as figuras e o painel usam o do primeiro subconjunto, e a tabela de importância traz os três. O erro com que o `TreeExplainer` recusa o modelo empilhado é gravado no resumo (`project/results/e5/variante/RESUMO.md`, "Limitação") | `explain.forest_shap_values`; `config.EXPLAINED_BASE`; `scripts/e5_xai.py`; painel em `scripts/painel_xai.py` |
| A16 | Subclassificação por ferramenta (VI-D) | Só as acurácias; nenhum método, split ou modelo | Mesmo sistema com rótulo de ferramenta, ou outro classificador | **Leitura da equipe, declarada como tal** (decisões 49 e 51): o mesmo sistema da reprodução, só com os fluxos maliciosos e as três ferramentas como classes; nos subconjuntos, a ferramenta com mais fluxos (dns2tcp) é dividida em três partes, a com menos (dnscat2) é aumentada com SMOTE até o tamanho da terceira (iodine). O valor do artigo fica ao lado de recall, precisão e F1 por ferramenta (`project/results/e7/RESUMO.md`) | `scripts/e7_ferramenta.py` (`tool_roles`, `run_experiment`); `data.load_malicious_by_tool`; `config.SECTION_VI_D_ACCURACY` |
| A17 | Tempo de treino "três vezes menor" | Afirmado na introdução e em III-B, sem medição | Não reproduzível como está | Os tempos de cada etapa são medidos e gravados no `run.json`, sem comparação com o artigo | `system.fit_system` (devolve `timings`); `runlog.save_run`; tabela `project/report/tables/tempos_treino` |
| A18 | Versões das bibliotecas | Nada. O repositório fixa `explainerdashboard==0.3.6.1` e Python 3.8.6 | — | Versões atuais compatíveis, fixadas e gravadas em cada `run.json` | `project/pyproject.toml`, `project/uv.lock`; `runlog.save_run` |

### 5.1 Leituras que o código adota e que não tinham linha na tabela

Apareceram na implementação. Não ganharam identificador: a lista A1 a A18 fica como está.

| Ponto | O que o artigo diz | Leitura adotada | Onde no código | Resultado |
| --- | --- | --- | --- | --- |
| Profundidade das árvores dos Random Forests base | Seção IV-B: profundidade máxima 5. Linha 3 do Algoritmo 1: "variable tree depth" | As duas são medidas no mesmo protocolo e reportadas lado a lado (decisão 45): 5 na trilha `fiel`; sem limite, com todo o resto igual, na trilha `variante`. Nenhuma foi escolhida pelo resultado. Os experimentos que usam o sistema como base partem da profundidade variável, com a de profundidade 5 ao lado | `config.MAX_DEPTH`, `config.MAX_DEPTH_VARIABLE`; `models.base_forests` (argumento `max_depth`) | `project/results/e1/RESUMO.md` |
| "selected at random from 28 features" (IV-A) | A frase admite 28 candidatos por divisão, de 29 atributos, ou um modelo com 28 atributos no total | `max_features=28` sobre os 29 atributos, porque o Algoritmo 1 e a Seção VI-C falam em 29 e o artigo não diz qual atributo sairia. A leitura alternativa (modelo com 28 atributos) não foi medida. Variante medida: `max_features` no padrão da biblioteca (`max_features_padrao`, E3) | `config.MAX_FEATURES`; `models.base_forests` (argumento `max_features`) | `project/results/e3/variante/RESUMO.md` |
| Folds da validação cruzada | "10 folds" (III-B e legenda da Fig. 4a); não diz se são estratificados nem se há embaralhamento | Estratificados, com embaralhamento e a seed da execução | `config.CV_FOLDS`, `config.CV_SHUFFLE`; `system.cross_validated_confusion` | contagem por fold em `project/results/e0/dados/RESUMO.md` |
| Split 90/10 | Não diz que o sorteio é por classe; as somas da Fig. 4 só fecham se for | Estratificado, `test_size=0.1`, sem forçar o tamanho do teste (decisão 35) | `splits.stratified_split`; `config.TEST_SIZE` | `project/results/e0/dados/RESUMO.md` |
| Sorteio das três partes de Non-DoH | Divide em três e não diz como sorteia | Linhas embaralhadas com a seed da execução antes do corte; a seed do SMOTE do subconjunto `i` é `seed * 100 + i` (decisões 41 e 51) | `splits.balanced_subsets`; `config.smote_seed` | — |
| Parâmetros da regressão logística | Nada além de "regressão logística" (IV-B) | Padrão do scikit-learn, com `random_state` igual à seed | `models.stacked_forest`; `config.FIEL_READINGS["meta_parameters"]` | — |
| SMOTE dos modelos de comparação | A Tabela II só diz "SMOTE balanced" | Treino inteiro, com as duas classes menores igualadas à maior (`sampling_strategy="not majority"`), vizinhos no padrão; seed `smote_seed(seed, 3)`. Os hiperparâmetros que a tabela não informa ficam no padrão do scikit-learn e do XGBoost | `splits.balanced_train`; `models.fit_baseline` | `project/results/e2/fiel/RESUMO.md` |
| Classe da Fig. 5 | A figura não diz a classe; a legenda fala do tráfego malicioso | A comparação é com o ranking de importância da classe Malicious-DoH; as figuras das outras duas classes ficam na mesma pasta | `scripts/e5_xai.py` (`article_comparison`); `config.FIG5_RANKING` | `project/results/e5/RESUMO.md` |
| Tamanho da amostra do SHAP | Fig. 5: "training data"; Fig. 6: "all the observations of the test set" | Amostra estratificada de até 2.000 fluxos por classe, uma do treino e uma do teste; escolha nossa, pelo custo. A importância pesa as três classes por igual | `config.SHAP_SAMPLE_PER_CLASS`; `explain.stratified_sample` | `project/results/e5/variante/RESUMO.md`, "Amostras" |
| Recorte dos dados na Fig. 2 | Não diz como recortou os dados nem a largura de banda | Faixas lidas nos eixos da figura; a densidade usa só os fluxos dentro da faixa, com a fração que fica de fora reportada; KDE gaussiano com a largura de banda padrão do SciPy | `config.FIG2_PANELS`; `scripts/e0_dados.py` (`fig2_densities`) | `project/results/e0/dados/RESUMO.md`, "Fig. 2" |
| Dados da Fig. 9 | Não diz que dados a figura usa | Figura feita com os fluxos limpos. A legenda foi medida de duas formas: com todas as linhas dos três `all.csv` de `MaliciousDoH-CSVs.zip`, sem o filtro da coluna `DoH` e sem a limpeza, e desvio padrão populacional, 12 das 12 médias e desvios saem iguais aos impressos; com os fluxos limpos e desvio amostral, 0 das 12. É **indício**, não demonstração, de que a Seção VI-D usou os arquivos sem a limpeza que leva à Tabela I | `scripts/e7_ferramenta.py` (`fig9_statistics`, `run_fig9`); `config.FIG9_PANELS`, `config.FIG9_MEAN_STD` | `project/results/e7/RESUMO.md`, "Figura equivalente à Fig. 9" |
| Transcrições lidas de figura | — | `FIG5_RANKING`, `FIG7_MALICIOUS`, `FIG8_NON_DOH` e a metade inferior da Tabela II foram lidos do manuscrito e digitados em `config.py`. A conferência por dois integrantes está pendente ([07-pendencias.md](07-pendencias.md)) | `config.py` | — |

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
