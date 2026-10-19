# VERIFICAÇÃO — gate de "pronto" por tarefa

> **Onde fica o código (decisão 43):** o repositório Git é a raiz; o código fica em `project/`. Todo caminho de código deste plano (`pyproject.toml`, `src/`, `scripts/`, `tests/`, `data/`, `results/`, `report/`, `README.md`) é relativo a `project/`, e os comandos `uv` rodam dentro dela. `.github/` e `.githooks/` ficam na raiz do repositório, porque o GitHub e o Git só os leem ali.

Regra: a tarefa só é "pronta" com tudo verde. Vermelho → conserta e repete. Não conseguiu → reporta com a saída do comando, sem maquiar.

## Gate universal

Executado de dentro de `project/`. A raiz do repositório fica um nível acima (decisão 43); os comandos `git` funcionam dos dois lugares.

| # | Verificação | Esperado |
| --- | --- | --- |
| G1 | Ambiente sincronizado | sem alterações no `uv.lock` |
| G2 | Lint | 0 erros |
| G3 | Formatação | nenhum arquivo a reformatar |
| G4 | Testes | suíte inteira verde, sem regressão; os testes da tarefa em [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md) existem; no pull request, CI verde |
| G5 | Script da tarefa | termina com código 0 e grava em `results/`; roda com a árvore limpa e o código já commitado, e o `run.json` versionado tem `dirty: false` (ordem: commit do código, execução, commit `exp` do resultado) |
| G6 | Determinismo | duas execuções seguidas produzem o mesmo `metrics.json` |
| G7 | Higiene | nenhum caminho absoluto de máquina; nenhuma referência a documento interno, tarefa, decisão ou identificador de ambiguidade no código, no README ou em `results/` |
| G8 | Critérios da tarefa | diff relido contra "Critério de aceite", item a item |
| G9 | Revisão automática | agente `revisor-metodologico` (código e experimento) ou `revisor-de-texto` (texto): nenhum achado bloqueante em aberto |
| G10 | Revisão humana | pull request lido e aprovado por outro integrante |

Comandos:

```bash
uv sync --locked                                   # G1
uv run ruff check .                                # G2
uv run ruff format --check .                       # G3
uv run pytest                                      # G4
uv run python scripts/<script>.py                  # G5
# G6: rodar G5, copiar o metrics.json para fora, rodar de novo e comparar
cp results/<exp>/<trilha>/<recorte>/seed<k>/metrics.json /tmp/metrics_a.json
uv run python scripts/<script>.py
diff /tmp/metrics_a.json results/<exp>/<trilha>/<recorte>/seed<k>/metrics.json
# G7: nenhum dos dois pode devolver linha
grep -rnE "/Users/|/home/|[A-Z]:\\\\" --include="*.py" src scripts tests data
grep -rnE "docs/|planejamento/|\.claude/|[Dd]ecis[ãa]o [0-9]|[Tt]arefa [0-9]|\b[AQ][0-9]{1,2}\b" --include="*.py" --include="*.md" --include="*.json" src scripts tests data README.md results
```

Para G6 funcionar, `metrics.json` não contém nada que varie entre execuções: tempos de treino, data e hora ficam no `run.json`. Também por causa do G6, todo Random Forest prediz com `n_jobs=1` depois de ajustado (`base_forests`, em `models.py`): em paralelo, a soma das probabilidades das árvores depende da ordem das threads e difere na última casa. Modelo novo com `predict_proba` em paralelo segue o mesmo cuidado.

`dirty` mede o repositório inteiro, menos `project/results/`: edição não commitada em `docs/` ou em `planejamento/` também grava `dirty: true`. O plano e a documentação vão para commit antes de qualquer execução do G5.

G2 e G3 também rodam no hook `pre-commit`, em todo commit. G1 a G4 e G7 rodam no CI do GitHub, em todo pull request. Os testes de G4 usam dados sintéticos; o que depende dos datasets é o nível N2 do plano de testes e entra em G5.

G1 a G4 e G7 existem desde a tarefa 01 (commit `5e11d56`): rodaram verdes em 07/10/2026 na árvore de trabalho e em um clone descartável. No CI, cada checagem do G7 é um passo próprio, e a de arquivo proibido roda na raiz do repositório.

G5 e G6 das tarefas 03 a 16 e da 21 rodam na própria sessão de implementação, nesta máquina (decisão 44); o cluster Apuana continua opção (decisão 42). A comparação do G6 é entre duas execuções na mesma máquina, no mesmo commit. Script que grava mais de um recorte (o de E1 grava as duas leituras de profundidade) tem o G6 conferido em cada `metrics.json`. Resultado gerado em máquinas diferentes pode divergir em casas decimais (versão de BLAS, número de threads); por isso os resultados versionados e a execução limpa da tarefa 19 saem do mesmo ambiente.

## Quais itens valem por tipo de tarefa

O rodapé de cada tarefa repete a linha correspondente desta tabela.

| Tipo | Tarefas | Gate |
| --- | --- | --- |
| Fundação | 01, 02 | G1–G4, G7, G8, G10 |
| Biblioteca (função e teste, sem script novo) | 06, 07 | G1–G4, G7–G10 |
| Dados (dependem de arquivos fora do Git) | 03, 04 (e o complemento da Fig. 2), 05, 13 | G1–G5, G7–G10; G6 em 04, 05 e 13 |
| Experimento | 08 a 12, 14 (o gate vale para a 14a e para a 14b, cada uma), 15, 16, 21 (obrigatória desde a decisão 49) | G1–G10 |
| Artefatos do relatório | 17 | G1–G5, G8, G10 |
| Texto | 18, 20 | G8, G9 (`revisor-de-texto`), G10 |
| Entrega | 19 | G1–G4, G7–G10 e a execução limpa abaixo |
| Organização | 22, 23 | G8, G10 |

## Invariantes do domínio

Valem para toda tarefa que toca dados ou modelo. Cada um tem teste automatizado ou asserção dentro do script.

| # | Invariante | Onde é checado |
| --- | --- | --- |
| I1 | Treino e teste não compartilham nenhuma linha (por índice); a fração do teste cujo vetor de atributos também existe no treino é medida e reportada | teste de `stratified_split`; `split_counts.json` (tarefa 05) |
| I2 | O scaler é ajustado só com o treino; em validação cruzada, só com os folds de treino | teste de `fit_scaler`; scaler dentro do laço de folds (tarefa 08, T08-5; a tarefa 14 reutiliza o mesmo laço no combinado sem réplicas) e como primeiro passo do `Pipeline` (tarefa 15) |
| I3 | Nenhuma amostra sintética em validação ou teste | teste de `balanced_subsets`; asserção de contagem na avaliação |
| I4 | `SourceIP`, `DestinationIP`, `SourcePort`, `DestinationPort`, `TimeStamp` nunca chegam ao modelo | testes de `load_cira` e de `feature_matrix` (T04-1, T04-2), e os das cargas novas (T13-1, T21-1); asserção de 29 colunas antes de todo ajuste (em `fit_system`, tarefa 08) |
| I5 | O teste só é lido na avaliação final; nenhuma escolha (seed, hiperparâmetro, arquitetura, teste estatístico) é feita olhando para ele | escolhas travadas em decisão e em `config.py` antes de rodar; revisão G9 |
| I6 | Todo resultado declara a trilha, a seed, as versões, o hash dos dados e o commit | teste de `save_run` |
| I7 | Métrica agregada sempre com o nome da média | teste de `evaluate` |
| I8 | As métricas calculadas a partir da matriz da Fig. 4b são as de `scripts/metricas_fig4.py` | teste de `metrics_from_confusion` |

Valores de trilha aceitos: `fiel`, `corrigida`, `variante` e `dados` (E0 e a preparação do segundo dataset, que não treinam modelo). `variante` cobre as leituras alternativas da tarefa 10 e, desde a decisão 45, a leitura de profundidade variável dos Random Forests base (`results/e1/variante/profundidade_variavel/`). Na trilha `fiel` a profundidade máxima é 5. As duas leituras são medidas no mesmo protocolo, e nenhuma tabela as junta sem a coluna que as identifica.

## Execução limpa (tarefa 19)

Roda na sessão de implementação (decisão 44), em um clone novo. Em um diretório novo, sem a pasta de trabalho por perto: `git clone` → `cd project` → `uv sync --locked` → baixar o zip da equipe e extraí-lo dentro de `project/`, conforme `data/README.md` → `uv run python data/verify.py` → rodar os scripts na ordem do README → comparar os `metrics.json` gerados com os versionados.

Uma primeira execução limpa, só com o que existir, é feita em 10/11, para o problema aparecer com uma semana de folga.

O painel da tarefa 12 (decisão 50) não entra na comparação de `metrics.json`: não grava resultado. Na execução limpa confere-se só que o comando do README o sobe e que nenhum modelo serializado aparece no disco.

## Situação do gate nas tarefas prontas (07/10/2026, commit `360c3d3`)

| Tarefa | Conferido nesta reconciliação | Em aberto |
| --- | --- | --- |
| 06 | G4 da tarefa: `tests/test_evaluate.py` executado, verde; G7: os dois greps executados, sem linha | G10 |
| 07 | G4 da tarefa: `tests/test_splits.py` executado, verde | G10 |
| 08 | G5: `run.json` das duas leituras com o commit `b00e471` e `dirty: false` (lido); G7 executado, sem linha, inclusive em `results/e1/` | **G6 das duas leituras** (segunda execução rodando); G9 informado pela sessão principal, sem artefato para conferir; G10 |

Não executados nesta reconciliação, porque havia um treino em andamento na máquina: a suíte inteira (`tests/test_models.py` e `tests/test_pipeline.py` treinam modelo), `uv sync --locked`, o lint e qualquer script de experimento. Executados, pelo Python do ambiente do projeto e sem `uv run`: `test_evaluate.py`, `test_splits.py`, `test_config.py`, `test_data.py`, `test_runlog.py` e `test_verify.py`, 44 funções, todas verdes.
