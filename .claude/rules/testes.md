# Regras de teste

O plano de testes por tarefa está em `planejamento/plan/PLANO-DE-TESTES.md`. Este arquivo diz como escrever os testes; aquele diz quais.

Os caminhos são relativos a `project/`; o repositório Git é a raiz.

## O que testar

Teste a funcionalidade macro e os pontos em que o erro é silencioso. Poucos testes, cada um protegendo algo que derrubaria um resultado do relatório:

- os invariantes de vazamento: treino e teste disjuntos, scaler só no treino, sintético só no treino, identificadores fora do modelo;
- o contrato de cada função pública que outra tarefa consome;
- os números de referência do artigo (as métricas da Fig. 4b);
- o caminho inteiro, de dados sintéticos até o resultado gravado, em um teste de ponta a ponta.

## O que não testar

- A biblioteca: não teste que o `RandomForestClassifier` aprende ou que o `MinMaxScaler` normaliza.
- Qualidade de modelo: nenhum teste exige acurácia mínima. Desempenho é resultado de experimento, não critério de teste.
- Getter, constante e função de uma linha sem regra.
- O mesmo comportamento duas vezes com entradas diferentes. Um caso típico e os casos de borda que têm regra própria.

Se um teste novo não protege nenhum item da lista "O que testar", ele não entra.

## Como escrever

- `pytest`, um arquivo por módulo: `tests/test_<modulo>.py`. O teste de ponta a ponta fica em `tests/test_pipeline.py`.
- Dados sempre sintéticos, gerados em `tests/conftest.py` com seed fixa e os nomes reais das 29 colunas. Nenhum teste lê `data/raw/` ou `data/processed/`: esses arquivos não existem no CI.
- Nome do teste diz o comportamento esperado: `test_scaler_is_fitted_on_train_only`, `test_no_synthetic_sample_outside_benign`.
- Um comportamento por teste. Sem mock quando dá para usar o objeto real com dados pequenos.
- Arquivos temporários só com a fixture `tmp_path`.
- A suíte inteira roda em menos de um minuto. Teste lento é sinal de dado sintético grande demais.
- Teste não tem aleatoriedade sem seed nem depende de ordem de execução.

## Dados reais

O que depende dos datasets não é teste do `pytest`: é asserção dentro do script do experimento e conferência do arquivo gerado em `results/`. O script falha com mensagem clara quando a asserção quebra. Isso roda na sessão de implementação (decisão 44), e a saída fica no relato da tarefa e no `run.json`.

## CI

O workflow do GitHub roda em todo `push` na `main` e em todo pull request, na mesma ordem do gate local:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
python3 scripts/metricas_fig4.py
```

Mais três checagens de higiene: nenhum caminho absoluto de máquina no código, nenhuma referência a documento interno em `project/` e nenhum arquivo proibido versionado. Pull request com CI vermelho não é integrado.
