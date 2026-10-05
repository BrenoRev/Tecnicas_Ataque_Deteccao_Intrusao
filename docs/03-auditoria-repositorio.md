# 03. Auditoria do repositório dos autores

Repositório: https://github.com/TZebin/DoH-Attack-explainer, indicado na seção "Supplementary Material" do artigo como contendo "code implementation for the model".

Auditado em 06/10/2026, commit `38e2f23`, 2021-07-20 a 2022-06-06. Leitura de arquivos e histórico git; nenhum pickle carregado.

## Conclusão

O repositório não contém o sistema descrito no artigo. É o código de um painel `explainerdashboard` preparado para deploy no Heroku, mais um script de 25 linhas que treina um Random Forest único. O sistema terá de ser reimplementado a partir do texto.

## O que há

| Caminho | O que é | Serve para nós? |
| --- | --- | --- |
| `generate_explainers.py` | Único script de modelagem (abaixo) | Como evidência do que os autores rodaram; dá `random_state=42` e o nome da coluna de rótulo |
| `dashboard/` | Cópia do código-fonte da biblioteca `explainerdashboard` (o `__init__.py` declara versão 0.3.8.2) | Não. Instala-se a biblioteca |
| `preprocess.py`, `matrices.py` | Módulos da biblioteca Orange3 (importam `Orange.data`); nada os chama | Não |
| `pkls/explainer.pkl`, `pkls/explainer.joblib` | Explainers serializados | Não carregar |
| `requirements.txt` | `explainerdashboard==0.3.6.1`, `pandas>=1.3.0`, `joblib`, `gunicorn`, `requests` | Só como registro da versão do painel |
| `runtime.txt` | `python-3.8.6` | Registro |
| `Procfile`, `Makefile`, `.heroku/run.sh` | Deploy do painel; o `run.sh` desinstala o xgboost | Não |
| `README.md` | Texto da documentação do `explainerdashboard` e um vídeo do painel | Não |

## O script de modelagem

```python
df = pd.read_csv(data_dir / 'new_processed.csv')
y = df['Attack_label']
X = df.drop(columns=['Attack_label'])
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.1, random_state=42)
model = RandomForestClassifier(n_estimators=10, random_state=42, max_depth=5, class_weight='balanced')
model.fit(X_train, y_train)
class_explainer = ClassifierExplainer(model, X_test, y_test,
                                      labels=['Non-DOH', 'Benign-DoH', 'Malicious-DOH'])
```

## Artigo contra código

| Componente do artigo | No repositório |
| --- | --- |
| Split 90/10 | Sim, estratificado, `random_state=42` |
| Random Forest com 10 árvores e profundidade 5 | Sim, um único |
| `numFeatures = 28` | Não: `max_features` fica no padrão da biblioteca |
| Normalização min-max | Não aparece (pode estar embutida no CSV pré-processado, que não está lá) |
| SMOTE, one-sided selection | Não. Usa `class_weight='balanced'`, que o artigo não menciona |
| Três submodelos em subconjuntos balanceados | Não |
| Meta-classificador de regressão logística, mlxtend | Não |
| GridSearchCV, 10 folds | Não |
| Baselines (árvore de decisão, XGBoost) | Não; o deploy desinstala o xgboost |
| Subclassificação por ferramenta de túnel | Não |
| Explicações SHAP | Sim, via `ClassifierExplainer`, sobre o Random Forest único e o conjunto de teste |

## O que o código acrescenta ao que sabemos

- Ordem dos rótulos: `0 = Non-DoH`, `1 = Benign-DoH`, `2 = Malicious-DoH`, coluna `Attack_label`.
- Seed 42 no split e no modelo.
- O painel publicado no artigo (Figuras 7 e 8) provavelmente explica esse Random Forest único, não o empilhamento. É inferência: o artigo não diz qual modelo alimenta o painel.

## Dados e histórico

- O script lê `data/new_processed.csv`, que não existe no repositório.
- Um arquivo com esse nome passou pelo histórico e foi removido no commit `5cb7c94` (11/05/2022). Tinha 1.144 linhas e colunas de bioquímica sanguínea (`ALT, ALP, AST, TP, LDH, CK, ...`, rótulo `JB_category`). Não é tráfego de rede.
- O repositório nasceu em julho de 2021 com commits de Shahadate Rezvy para um painel de outro projeto e foi adaptado depois. Os pickles em `pkls/` são dessa fase anterior, segundo a análise estática registrada no documento do seminário (seção 4.3).

## O que perguntar aos autores, se a equipe decidir escrever

O artigo indica t.zebin@uea.ac.uk para dúvidas. Perguntas que destravariam a reprodução: o script de criação dos subconjuntos balanceados; a limpeza aplicada antes da Tabela I; a grade do GridSearchCV; de onde saem os valores da Tabela II. Escrever ou não é decisão da equipe e convém alinhar com o professor antes.
