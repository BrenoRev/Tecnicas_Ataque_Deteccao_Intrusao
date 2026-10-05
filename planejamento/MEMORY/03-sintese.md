# Síntese: riscos priorizados e arquitetura-alvo

## Riscos

| # | Risco | Nível | Onde nasce | Mitigação no plano |
| --- | --- | --- | --- | --- |
| R1 | Vazamento silencioso (scaler, SMOTE ou busca vendo validação/teste; identificadores no modelo) | Crítico | `docs/04-dados.md`, "Riscos de vazamento" | Split e remoção de identificadores em um único módulo (tarefas 04 e 05), testes que falham se houver interseção ou amostra sintética fora do treino, revisor metodológico no gate |
| R2 | Reprodução longe da Fig. 4b por ambiguidade do artigo | Alto | `docs/02-artigo.md`, seção 5 | Decisões 09, 13, 14 fixam uma leitura; tarefa 10 mede as outras; não reproduzir, bem documentado, é resultado aceitável |
| R3 | Ajustar seed ou hiperparâmetro olhando o teste até "bater" com o artigo | Alto | Tentação natural diante de R2 | Decisões 12 e 15 fixam seed e valores antes de rodar; variantes só as listadas na tarefa 10 |
| R4 | Download do CIRA atrasar (**encerrado em 07/10/2026: dados baixados**) | — | `01-discovery-stack.md`, "Downloads" | Tarefa 03 é a primeira da cadeia; plano B com o dataset combinado |
| R5 | Professor responder Q1, Q2 ou Q4 de forma diferente da assumida | Alto | `docs/07-pendencias.md` | Tarefas afetadas listadas em `00-decisoes-travadas.md`; nenhuma resposta invalida as tarefas 01 a 07 |
| R6 | Colunas do HKD não coincidirem com as do CIRA | Médio | `docs/04-dados.md`, seção 3 | Tarefa 13 confere coluna a coluna antes de qualquer modelo |
| R7 | Trilhas fiel e corrigida se misturarem em tabela do relatório | Médio | — | Decisão 06 e 18: trilha no caminho do resultado; tabelas geradas por script |
| R8 | Código que a equipe não sabe explicar na arguição | Médio | `CLAUDE.md`, regra 9 | Decisão 07: funções simples; revisão humana cruzada no gate |
| R9 | P3 consumir o tempo do relatório | Médio | Cronograma | Tarefa 16 (M3) cortável; tarefa 15 só começa com a 11 fechada |
| R10 | Número do relatório divergir do resultado | Médio | — | Tarefa 17: tabelas geradas a partir de `results/` |
| R11 | Código antigo de SHAP indexando `shap_values` como lista | Baixo | `01-discovery-stack.md` | Tarefa 12 fixa o formato `(n, atributos, classes)` e testa |

## Arquitetura-alvo

Um pacote pequeno de funções e um script por experimento. Nada de framework.

```
├── pyproject.toml, uv.lock, requirements.txt
├── data/
│   ├── README.md            origem, citação, SHA-256 de cada arquivo
│   ├── verify.py            confere hashes e nomes dos arquivos em raw/
│   ├── raw/                 fora do Git
│   └── processed/           fora do Git
├── src/doh_ids/
│   ├── config.py            classes, colunas, hiperparâmetros com a origem
│   ├── data.py              carga, rótulos, limpeza, remoção de identificadores
│   ├── splits.py            split estratificado, scaler, subconjuntos balanceados
│   ├── models.py            Random Forest base, empilhamento, baselines
│   ├── evaluate.py          métricas, comparação com os alvos do artigo
│   ├── runlog.py            grava resultado + metadados da execução
│   └── explain.py           SHAP
├── scripts/
│   ├── metricas_fig4.py     (já existe)
│   ├── e0_dados.py … e8_modificacao.py
│   └── make_report_assets.py
├── tests/                   pytest, dados sintéticos
├── results/<experimento>/<variante>/
└── report/                  fonte LaTeX, tabelas e figuras geradas
```

### Fluxo de dados

```
data/raw/*.csv ──data.py──▶ data/processed/cira.parquet
                                   │
                          splits.py│ split 90/10 estratificado (seed)
                    ┌──────────────┴──────────────┐
                 treino                         teste (intocado até a avaliação)
                    │ scaler.fit                    │ scaler.transform
        ┌───────────┼───────────┐                   │
   subconj. 1   subconj. 2   subconj. 3             │
   (SMOTE)      (SMOTE)      (SMOTE)                │
        │           │           │                   │
      RF 1        RF 2        RF 3                  │
        └───────────┼───────────┘                   │
           meta: regressão logística ◀── treino original normalizado
                    │
                    └────────────── evaluate.py ◀───┘
                                        │
                              results/…/metrics.json ──▶ make_report_assets.py ──▶ report/
```

### Contratos entre módulos

| Função (módulo) | Entrada | Saída | Invariante testado |
| --- | --- | --- | --- |
| `load_dataset` (data) | diretório de CSVs | DataFrame com 29 atributos + `label` em {0,1,2} | Nenhuma coluna identificadora; sem NaN/inf |
| `stratified_split` (splits) | DataFrame, seed | treino, teste | Índices disjuntos; proporção por classe preservada |
| `fit_scaler` (splits) | treino | scaler | Ajustado só com o treino |
| `balanced_subsets` (splits) | treino normalizado, seed | 3 pares (X, y) | Partes de Non-DoH disjuntas; maliciosos idênticos nos três; sintéticos só na classe benigna |
| `build_stacked_rf` (models) | 3 subconjuntos, treino original | modelo ajustado | 3 bases; meta com 3 entradas |
| `evaluate` (evaluate) | y real, y predito, probabilidades | dicionário de métricas | Aplicado à matriz da Fig. 4b reproduz a saída de `scripts/metricas_fig4.py` |
| `save_run` (runlog) | métricas, config | arquivos em `results/` | Contém seed, trilha, versões, hash dos dados, commit |

Os nomes de função são orientação para as tarefas; a assinatura final é decidida na implementação.

## Decisões levadas ao usuário

Travadas em `00-decisoes-travadas.md`: 01 a 05 respondidas no intake; 28 a 33 pedidas pelo usuário em 07/10/2026; 06 a 27 e 34 a 41 adotadas por recomendação e reabríveis.
