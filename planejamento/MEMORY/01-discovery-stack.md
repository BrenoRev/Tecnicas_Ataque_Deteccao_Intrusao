# Stack — discovery

Verificado em 06/10/2026 num ambiente descartável (`uv venv --python 3.12` + `uv pip install`), fora do projeto. Nada foi instalado nem escrito no repositório.

## Fatos (com evidência)

**Ferramentas na máquina**

- `uv` disponível em `~/.local/bin/uv`; Python do sistema 3.14.4; `git` e `pdftotext` presentes; `conda` ausente — saída de `which`/`--version`.

**Versões que instalam juntas em Python 3.12** — saída de `uv pip list`

| Pacote | Versão |
| --- | --- |
| scikit-learn | 1.9.1 |
| imbalanced-learn | 0.14.2 |
| mlxtend | 0.25.0 |
| xgboost | 3.4.1 |
| shap | 0.52.0 |
| explainerdashboard | 0.5.8 |
| pandas | 3.0.6 |
| numpy | 2.3.5 |
| scipy | 1.18.1 |
| pyarrow | 25.0.1 |
| pytest | 9.1.1 |
| ruff | 0.16.10 |

Python 3.14 não foi testado. O plano fixa 3.12.

**APIs conferidas por introspecção e execução em dados sintéticos (29 atributos, 3 classes)**

- `mlxtend.classifier.StackingClassifier(classifiers, meta_classifier, use_probas=False, drop_proba_col=None, average_probas=False, verbose=0, use_features_in_secondary=False, store_train_meta_features=False, use_clones=True, fit_base_estimators=True)` — `inspect.signature`.
- **Três Random Forests pré-treinados em subconjuntos diferentes entram no `StackingClassifier` com `fit_base_estimators=False`.** O `fit` então só treina o meta-classificador. Executado sem erro. Resolve a ambiguidade A9.
- Com `use_probas=False` (padrão) o meta recebe 3 atributos, um rótulo predito por base; com `use_probas=True` recebe 9 (3 bases × 3 classes) — `meta_clf_.n_features_in_`. Resolve o "a verificar" de A10.
- Alternativa: cada base como `imblearn.pipeline.Pipeline([SMOTE, RandomForest])` dentro do `StackingClassifier` também executa. Nesse desenho todos os bases veem o mesmo treino, o que não é o que o artigo descreve.
- `mlxtend.classifier.StackingCVClassifier(..., cv=2, shuffle=True, random_state=None, stratify=True, ...)` executa; gera predições out-of-fold para o meta. Não aceita bases pré-treinados em subconjuntos distintos (ele mesmo reajusta os bases).
- `imblearn.over_sampling.SMOTE(*, sampling_strategy='auto', random_state=None, k_neighbors=5)`; `sampling_strategy` aceita dicionário `{classe: n}`.
- `imblearn.under_sampling.OneSidedSelection(*, sampling_strategy='auto', random_state=None, n_neighbors=None, n_seeds_S=1, n_jobs=None)` existe.
- `shap.TreeExplainer(RandomForestClassifier).shap_values(X)` devolve um `ndarray` de forma `(amostras, 29, 3)`, não uma lista por classe.
- `shap.TreeExplainer(<modelo empilhado do mlxtend>)` levanta `InvalidModelError: Model type not yet supported by TreeExplainer`. Confirma a crítica do seminário: o "TreeExplainer" do Algoritmo 1 não pode ter sido aplicado ao empilhamento.
- `explainerdashboard.ClassifierExplainer(RandomForest, X_df, y)` constrói sem erro na 0.5.8.
- `xgboost.XGBClassifier` treina no mesmo ambiente.

**Custo** — cronometrado com dados aleatórios no tamanho de um subconjunto real (510 mil linhas × 29 colunas)

- SMOTE de 18 mil para 225 mil amostras: 0,4 s.
- Random Forest (10 árvores, profundidade 5, `max_features=28`, `n_jobs=-1`) em 717 mil linhas: 24,8 s.
- Dado aleatório é o pior caso para o tempo de árvore; em dado real deve ser menor. Uma execução completa de E1 cabe em poucos minutos, e 10 seeds de E4 cabem em uma sessão.

**Downloads**

- CIRA-CIC-DoHBrw-2020: `cicresearch.ca/CICDataset/DoHBrw-2020/` devolve uma página da UNB com formulário, sem listagem de arquivos. **Download manual.** Nomes e tamanhos dos CSVs ainda desconhecidos.
- DoH-Tunnel-Traffic-HKD: a página do repositório da Universidade de Hokkaido (`eprints.lib.hokudai.ac.jp/dspace/handle/2115/88092`) respondeu e lista dois arquivos, de 209 MB e 485 MB, com a nota "rights Reserved". Os links diretos não foram extraídos.
- Os dois repositórios GitHub do HKD contêm só `README.md`; os dados estão no eprints.

## Problemas / riscos

- Download do CIRA depende de formulário: não dá para automatizar, e pode demorar — impacto: bloqueia toda a cadeia de dados. Mitigação: o dataset combinado contém as linhas do CIRA.
- "rights Reserved" no HKD: a licença de redistribuição não está clara — impacto: os dados não podem ir para o Git (já não iriam) e a citação é obrigatória.
- pandas 3 e numpy 2 são versões recentes; exemplos antigos de `explainerdashboard` e `shap` na internet podem não valer — impacto: tempo de depuração. Mitigação: versões fixadas e os testes acima já passaram.
- `shap_values` em formato `(n, atributos, classes)`: código copiado de tutoriais antigos (lista por classe) quebra silenciosamente ao indexar.

## Perguntas em aberto / a decidir

- Em que dados o meta-classificador é treinado quando os bases são pré-treinados → decisão 09.
- Nomes reais dos CSVs e da coluna de rótulo do CIRA → resolvido na tarefa 03.
