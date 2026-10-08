# 19 · entrega · README, execução limpa e checklist final

**Onde:** `README.md`, repositório inteiro
**Objetivo:** o professor abre o link do GitHub, entende o que há ali e consegue reproduzir os resultados do relatório sem falar com a equipe. Entrega em 18/11/2026.
**Depende de:** 17 para a execução limpa e o README; 24 só para o envio final (as duas concluídas)
**Demonstra:** README com a tabela resultado → script → arquivo e a execução limpa em um clone novo. Entregável "link do GitHub com os códigos comentados".

## Como ficou (fechamento de 08/10/2026, conferido em `5999c1b`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado neste fechamento; "lido" é arquivo ou histórico aberto, sem rodar.

- **Situação: concluída; resta de pessoa a entrega de 18/11**, com a checklist de entrega e o comprovante.
- **README completo** em `7657501`, com ajustes em `b6bcbcc`, `b82a82f`, `7813020` e `3da178e`: instalação com uv e com pip, dados, "Ordem dos scripts" com os 22 passos e o tempo medido de cada um, a regra do `python -m`, "Execução limpa", "Do relatório ao arquivo", painel, limitações, "Onde os resultados foram gerados" e licença (lido). O `README.md` da raiz apresenta o projeto (`7813020`, afirmações ajustadas em `3e42795`).
- **Dois scripts novos, criados nesta tarefa:** `scripts/execucao_limpa.sh` (`88c0e88`), que roda os 22 passos na ordem, com um log por passo, e para no primeiro erro; `scripts/comparar_resultados.py` (`53f1ca4`, `47cdabe`), que compara duas árvores `results/` e, se pedido, duas `report/`, com `tests/test_comparar_resultados.py` (três testes).
- **Execução limpa feita em 08/10/2026**, de 04:54 a 12:24 (7 h 30 min), em um clone novo fora do repositório, no commit `e2379b7`, com os dados do zip da equipe e a árvore limpa: 22 passos sem erro; 260 de 260 arquivos de `results/` e 56 de 56 de `report/` conferem (`REVISAO-FINAL.md`, "Execução limpa"). Na primeira comparação, 256 de 260 saíram idênticos; os quatro restantes eram dois `metrics.json` de SHAP do segundo conjunto, regravados em `97b2c8c` depois de conferidas as 521 chaves comuns, e os dois agregados de E8, diferentes só no campo `commits` e nos tempos, que o script passou a ignorar em `47cdabe`. Dito sem atenuar: a execução não foi feita por outro integrante nem em outra máquina (decisão 44).
- **O ponto que estava por resolver com o usuário** (os dois agregados de E8 guardam tempos) ficou resolvido pela comparação sem as chaves de tempo e sem `commits`; nenhum arquivo de resumo mudou de formato. A regra está em `.claude/rules/experimentos.md`, regra 2.
- **Das 30 tabelas de `report/tables/`, 27 são comparadas byte a byte;** as três que citam tempo de treino (`tempos_treino`, `modificacao_metricas_dupla`, `modificacao_pareada_dupla`) são só informadas pelo script (lido em `scripts/comparar_resultados.py`). Daí os 56 arquivos: 27 `.tex`, 27 `.csv`, o índice e o `relatorio.tex`.
- **Licença:** `LICENSE` (MIT) na raiz, em `7813020` (decisão 55c).
- **Histórico com uma identidade Git:** 164 commits de um autor em `5999c1b` (executado: `git shortlog -sn`); aceito pela equipe (decisão 55d).
- **Na `main` do GitHub:** `origin/main` está em `378f170`, com o CI verde (executado: `gh run list --branch main`). Os 15 commits de `378f170` a `5999c1b`, mais o deste fechamento, são enviados em seguida; o CI do commit entregue é conferido no envio.

## Estado de partida (registro de `759ec29`, 08/10/2026; superado pelo bloco acima)

A tarefa podia começar: todos os experimentos (tarefas 03 a 16 e 21), as tabelas e figuras (17) e os entregáveis (24) estavam prontos e executados.

- **Onde roda (decisão 44):** na própria sessão de implementação, nesta máquina, em um **clone novo fora do repositório**, em diretório novo, com os dados extraídos do zip da equipe (link no `README.md`; o zip traz a pasta `data/` inteira e é extraído dentro de `project/`). Efeito, dito sem atenuar: a execução não é feita por quem não escreveu o código e não testa outra máquina; o que ela testa é que um clone limpo, com o ambiente do lock e os dados conferidos pelo manifesto, regenera os resultados versionados. O relato diz isso. A leitura e a aprovação do pull request (G10) continuam sendo de uma pessoa.
- (Superado em `7657501` e `7813020`.) Em `759ec29` o `README.md` não tinha a ordem dos scripts nem a licença, e não havia arquivo `LICENSE`.
- **Padrão de execução do repositório.** Script de treino só treina, avalia e grava `metrics.json` e `run.json`. Onde há agregação, o `RESUMO.md`, o `summary.json` e a tabela comparativa saem de um script de resumo, que não treina: `e3_resumo`, `e4_resumo`, `e6_resumo`, `e7_resumo`, `e8_resumo` e `e8_robustez_resumo`. Em E0, E1, E2, E5 e na etapa de dados de E6, o próprio script escreve o resumo. Script que importa outro script roda como módulo, com `python -m scripts.<nome>`: os seis de resumo, `e6_baselines_xai`, `e8_modificacao` e `e8_robustez`.
- **Todos os resultados versionados saíram desta máquina:** os 229 `run.json` trazem o mesmo `hostname`, 10 núcleos e `dirty: false` (lido).
- **`git shortlog -sn` mostra um único autor** (137 commits em `759ec29`; 164 em `5999c1b`). O critério dos quatro integrantes não se aplica (decisões 44 e 55d).

## Ordem real dos scripts

Derivada do código em `759ec29`: o que cada script lê de `results/` e de `data/processed/`, e quais scripts ele importa. Todos os comandos rodam dentro de `project/`. Tempo medido: soma da chave `timings` dos `run.json` versionados; não inclui carga do Parquet, split, gravação de figura nem o que fica fora dos cronômetros. Os scripts sem `run.json` (conferência, resumos, tabelas, slides) rodam em segundos e não têm tempo registrado.

| # | Comando | Precisa de | Grava | Tempo medido |
| --- | --- | --- | --- | --- |
| 1 | `uv run python data/verify.py` | `data/raw/`, `data/manifest.json` | nada | segundos (executado em 08/10: 8 de 8 arquivos conferidos) |
| 2 | `uv run python scripts/e0_dados.py` | `data/raw/cira/` | `data/processed/cira.parquet`; `results/e0/` | 44 s |
| 3 | `uv run python scripts/e6_dados.py` | `data/raw/hkd/`, `data/raw/combinado/`; passo 2 | os três Parquets do segundo dataset; `results/e6/dados/` | 18 s em cada um dos três `run.json` |
| 4 | `uv run python scripts/e1_reproducao.py` | passo 2 | `results/e1/` | 3.376 s (56 min): 902 s na profundidade 5 e 2.473 s na variável, esta com a máquina carregada |
| 5 | `uv run python scripts/e2_baselines.py` | passos 2 e 4 (`results/e1/`, para o resumo) | `results/e2/` | 172 s (3 min) |
| 6 | `uv run python scripts/e5_xai.py` | passos 2, 3 (`results/e6/dados/hkd/`) e 4 | `results/e5/` | 560 s (9 min) |
| 7 | `uv run python scripts/e6_dataset2.py` | passos 2, 3 e 4 | `results/e6/{fiel,variante}/{transferencia,retreino_publicado,retreino_sem_replicas}/` | 2.512 s (42 min) |
| 8 | `uv run python -m scripts.e6_baselines_xai` | passos 6 e 7; importa os scripts dos passos 5, 6 e 7 | `results/e6/fiel/retreino_sem_replicas-<modelo>/`; `results/e6/{fiel,variante}/retreino_sem_replicas-shap/` | 1.839 s (31 min) |
| 9 | `uv run python -m scripts.e6_resumo` | passos 4 a 8 | `results/e6/RESUMO.md` e o de cada trilha | segundos |
| 10 | `uv run python scripts/e7_ferramenta.py` | `data/raw/cira/MaliciousDoH-CSVs.zip`; passo 3 (`results/e6/dados/combinado_sem_replicas/`) | `results/e7/` | 40 s |
| 11 | `uv run python -m scripts.e7_resumo` | passo 10 | `results/e7/RESUMO.md` | segundos |
| 12 | `uv run python scripts/e3_sensibilidade.py` | passo 2 | `results/e3/variante/<recorte>/` | 535 s (9 min) |
| 13 | `uv run python scripts/e4_corrigido.py` | passo 2 | `results/e4/corrigida/<modelo>/seed<k>/` e `A-fold<k>/` | 7.118 s (1 h 59 min) |
| 14 | `uv run python -m scripts.e4_resumo` | passo 13 | `results/e4/corrigida/summary.json` e `RESUMO.md` | segundos |
| 15 | `uv run python -m scripts.e3_resumo` | passos 4, 12 e **13** (`results/e4/corrigida/A/`) | `results/e3/variante/comparacao.csv` e `RESUMO.md` | segundos |
| 16 | `uv run python -m scripts.e8_modificacao` | passos 2, 3 e 13 (confere o split contra `results/e4/`) | `results/e8/corrigida/<modelo>-<dados>/` | 7.143 s (1 h 59 min) |
| 17 | `uv run python -m scripts.e8_robustez` | passos 13 e 16 (`M1M2-cira`, os hiperparâmetros selecionados) | `results/e8/corrigida/robustez-<modelo>-<colunas>/` | 7.000 s (1 h 57 min) |
| 18 | `uv run python -m scripts.e8_resumo` | passos 7, 13, 16 e **17** (`robustez-<modelo>-todos`) | `results/e8/corrigida/summary.json` e `RESUMO.md` | segundos |
| 19 | `uv run python -m scripts.e8_robustez_resumo` | passos 13, 16 e 17 | `results/e8/corrigida/summary-robustez.json` e `RESUMO-ROBUSTEZ.md` | segundos |
| 20 | `uv run python scripts/make_report_assets.py` | todos os anteriores | `report/tables/`, `report/figures/`, `report/INDICE.md` | segundos (executado em 08/10, em diretório temporário) |
| 21 | `uv run --group slides python scripts/make_slides.py` | passo 20; `geracao_latex_and_pdf/` na raiz do clone | `report/apresentacao.pptx`, `report/roteiro.md` | segundos |
| 22 | `tectonic relatorio.tex`, dentro de `report/` | passo 20 | `report/relatorio.pdf` | 1,5 s (executado em 08/10, em diretório temporário) |

Fora da sequência: `python3 scripts/metricas_fig4.py` (só a biblioteca padrão, roda no CI) e `uv run python scripts/painel_xai.py` (o painel, que não grava resultado).

**Tempo total estimado.** A soma dos tempos medidos de treino é 30.393 s, 8 h 27 min. Com a carga dos dados, os splits, as figuras e o que fica fora dos cronômetros (no passo 13, o intervalo entre o primeiro e o último `run.json` indica cerca de 4 minutos a mais que a soma), a execução inteira deve levar cerca de 9 horas nesta máquina; reservar 10. Os tempos foram medidos com a máquina em uso e variam: a mesma configuração de Random Forest levou 39 s no passo 5 e 372 s no passo 8. Os passos 13, 16 e 17 somam 5 h 54 min e não dependem dos passos 5 a 12: podem começar logo depois do passo 3.

**Retomada.** Os passos 16 e 17 pulam a execução já gravada pelo commit atual com a árvore limpa: interrompidos, continuam de onde pararam se forem relançados no mesmo commit. No clone novo, o commit dos `run.json` versionados é anterior ao do clone, e por isso tudo é refeito. Os passos 4 e 13 não têm retomada.

**Árvore limpa.** `dirty` mede o repositório inteiro, menos `project/results/`. No clone, `data/` e o zip estão no `.gitignore` e não sujam a árvore. Os passos 20 a 22 escrevem em `project/report/`: se a comparação abaixo usar `git diff`, ela é feita antes de qualquer commit e não precisa de `run.json` novo com `dirty: false` depois do passo 19.

## O que a execução limpa compara

Depois do passo 22, de dentro do clone, contra o que está versionado:

| O que | Quantos | Esperado | Como |
| --- | --- | --- | --- |
| `project/results/**/metrics.json` | 229 | idênticos byte a byte | `git diff --stat -- ':(glob)project/results/**/metrics.json'` sem linha |
| `summary.json` de E4 | 1 | idêntico | `git diff` |
| `summary.json` de E8 e `summary-robustez.json` | 2 | idênticos **fora das chaves de tempo** | comparar depois de retirar `train_seconds`, `selection_seconds`, `time_checks` e `fit_seconds`: esses valores vêm dos `run.json` e mudam a cada execução |
| `split_counts.json`, os CSVs auxiliares de `results/` e `comparacao.csv` | — | idênticos | `git diff --stat -- project/results` |
| `report/tables/*.tex` e `*.csv`, `report/INDICE.md` | 30 + 30 + 1 | idênticos | `git diff --stat -- project/report/tables project/report/INDICE.md` |
| Hash dos Parquets | 4 | `parquet_sha256` igual ao versionado | sai dos `metrics.json` de E0 e de `results/e6/dados/` |

Diferença esperada, que não é defeito: os `run.json` (commit, data, tempos); os `RESUMO.md` que citam tempo de treino; `relatorio.pdf` e `apresentacao.pptx`, que carregam data de criação; as figuras em PDF. Qualquer outra diferença é defeito a corrigir ou a explicar no README.

O painel não entra na comparação: confere-se só que o comando do README o sobe e que nenhum modelo serializado aparece no disco.

**Ponto resolvido (`47cdabe`):** os dois agregados de E8 guardam tempos e o commit de cada execução. `scripts/comparar_resultados.py` os compara sem as chaves `train_seconds`, `selection_seconds`, `time_checks`, `fit_seconds` e `commits`. A alternativa, tirar os tempos desses arquivos, não foi adotada: mexeria em dois scripts de resumo, em dois arquivos versionados de `results/` e nas tabelas que leem o tempo de treino deles.

## Arquivos

- `README.md` — completar.
- `LICENSE` — criado na raiz em `7813020` (MIT, decisão 55c); a nota de uso está na seção "Licença" do `README.md`.
- Todo o repositório — revisão final de comentários e de higiene.

## O que fazer

1. Completar o `README.md`: o que é o projeto e qual artigo reproduz; integrantes; requisitos (uv ou pip, Python 3.12; `tectonic` ou XeLaTeX só para o relatório; o grupo `slides` só para a apresentação); como obter os dados e conferir os hashes; **a tabela da seção "Ordem real dos scripts"**, com o que cada um gera e o tempo medido; a regra de rodar como módulo os scripts que importam outros; tabela "resultado do relatório → script → arquivo em `results/`", cobrindo todas as tabelas e gráficos de resultado do artigo (decisão 46), as duas leituras de profundidade (decisão 45), o P1 refeito no combinado sem réplicas (decisão 47), a ferramenta de túnel (decisão 49) e a modificação; a seção do painel, que já existe; onde os resultados versionados foram gerados (máquina e versões, dos `run.json`); limitações conhecidas. A fonte da tabela resultado → arquivo é `report/INDICE.md`.
2. Uso de assistente de IA: aprovado na disciplina (07/10/2026). Sem frase de declaração no README nem no relatório: a equipe fechou a parte em aberto de Q7 sem resposta do professor (decisão 55a).
3. Revisar os comentários do código contra `docs/06-padroes.md`: docstring curta em toda função pública, comentário de justificativa nos pontos de decisão, com a seção do artigo onde ele é omisso, e nenhuma referência a arquivo interno, tarefa ou decisão (o mesmo grep do CI: `grep -rnE "docs/|planejamento/|\.claude/|[Dd]ecis[ãa]o [0-9]|[Tt]arefa [0-9]|\b[AQ][0-9]{1,2}\b" --include="*.py" --include="*.md" --include="*.json" src scripts tests data README.md results` não devolve nada). A especificação pede "todos os códigos comentados".
4. **Execução limpa.** As datas do plano continuam valendo como limite: primeira execução limpa até 10/11, experimentos congelados em 13/11, execução final começando em 16/11. Como os experimentos já terminaram, a primeira execução é feita agora, nesta tarefa. Procedimento: clonar em diretório novo, fora do repositório; `cd project`; `uv sync --locked`; extrair o zip da equipe dentro de `project/`; rodar os passos 1 a 22 da tabela, na ordem.
5. Comparar pelo quadro "O que a execução limpa compara". Diferença fora das esperadas é defeito a corrigir ou a explicar no README.
6. Repetir a instalação pelo `requirements.txt`, com pip (`pip install -r requirements.txt` e depois `pip install -e .`), e rodar a suíte, para garantir o caminho de quem não usa uv. O `requirements.txt` não traz o `python-pptx`: o README diz que os slides pedem o grupo `slides`.
7. Conferir higiene: sem dados, sem modelos serializados, sem PDF do artigo, sem credenciais, sem caminho absoluto.
8. Não se aplica (decisões 44 e 55d): o histórico tem uma só identidade Git, aceito pela equipe.
9. Rodar a skill `checklist-entrega projeto` e resolver todo item pendente marcado como exigido.
10. Dar acesso ao professor (ou manter público, conforme Q10) e enviar o link junto com o PDF.

## Por quê

A especificação pede "link do Github com todos os códigos comentados". Reprodução em clone limpo é o que separa código que roda para quem escreveu de código reprodutível, e é o critério interno da equipe (`CLAUDE.md`, regra 5).

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:34` — entregável e prazo.
- `.claude/skills/checklist-entrega/SKILL.md`, seção "projeto" — itens a verificar.
- `planejamento/plan/VERIFICACAO.md`, "Execução limpa" — sequência de comandos.
- `docs/06-padroes.md:49` — como "códigos comentados" é cumprido.

## Risco

- A execução limpa leva cerca de 9 horas: lançar em segundo plano, com a saída em arquivo, e não editar o clone enquanto roda. Uma falha no passo 13 ou no 4 custa o passo inteiro, porque eles não têm retomada.
- Os resultados de E1 foram gerados no commit `b00e471`, antes de `fit_system` ir para o pacote (`472bb79`); os de E2, E3, E4 e da 14a são anteriores a mudanças posteriores no pacote (`evaluate.py`, `models.py`, `config.py`). Só E5, a etapa de dados de E6 e E7 foram rodados de novo depois da revisão (`38809c1`), e ali os `metrics.json` da etapa de dados e dos modelos de E7 saíram idênticos. A execução limpa é a primeira conferência de que o código atual regenera esses `metrics.json`; diferença ali é o achado mais provável.
- (Fechado.) O G6 de E1, que estava em aberto na reconciliação de `360c3d3`, foi fechado pela execução limpa: os `metrics.json` de `results/e1/` saíram idênticos.
- Resultado não determinístico entre execuções (paralelismo): seeds fixadas e predição com `n_jobs=1`; o determinismo do XGBoost com `n_jobs` maior que um não tem conferência registrada. Se variar, registrar a ordem de grandeza no README.
- Dados indisponíveis para o professor: o README explica o download e indica o hash.

## Critério de aceite

- [x] Execução limpa concluída na sessão de implementação, em clone novo fora do repositório, com os 229 `metrics.json` e os três `summary*.json` iguais aos versionados (os dois de E8, fora das chaves de tempo) (decisão 44). **Fechado em 08/10/2026:** `REVISAO-FINAL.md`, "Execução limpa" (lido): 08/10/2026, 7 h 30 min, commit `e2379b7`, 22 passos sem erro, 260 de 260 depois de `97b2c8c` e `47cdabe`; o texto diz que foi em um clone novo, nesta máquina. **Parte sem arquivo versionado:** o tempo de cada passo da execução limpa ficou nos logs do clone, fora do repositório; o que está versionado é o total e, no README, o tempo de cada passo medido nas execuções originais.
- [x] `report/tables/` regenerado no clone sem diferença. **Fechado em 08/10/2026:** `REVISAO-FINAL.md`: 56 de 56 arquivos de `report/` idênticos (27 tabelas em `.tex` e `.csv`, o índice e o `relatorio.tex`). As outras três tabelas citam tempo de treino e são só informadas pelo script de comparação; as demais células delas vêm dos agregados, comparados fora do tempo.
- [x] README com a ordem dos 22 passos, o tempo medido de cada um e a regra do `python -m`. **Fechado em 08/10/2026:** lido em `5999c1b`: `README.md`, seção "Ordem dos scripts" (tabela dos passos, com "Precisa de" e tempo) e a frase da linha 113 sobre rodar como módulo; `7657501`.
- [x] README com o comando do painel e com `explainerdashboard` entre as dependências (decisão 50). **Fechado em 08/10/2026:** lido em `5999c1b`: `README.md`, linha 47 (lista de bibliotecas, com "explainerdashboard (o painel)") e seção "Relatório, slides e painel".
- [x] Instalação por `requirements.txt` testada. **Fechado em 08/10/2026:** executado pelo `cin0114-plan-sync` em um clone descartável do commit `5999c1b`, fora do repositório: `venv` de Python 3.12.13, `pip install -r requirements.txt` e `pip install -e .` com código 0, `python -m pytest` com 118 testes verdes em 47 s. Não havia registro versionado de teste anterior. Não testado: `python-pptx`, que fica fora do `requirements.txt`.
- [x] README com a tabela resultado → script → arquivo, cobrindo todas as tabelas e figuras do relatório. **Fechado em 08/10/2026:** lido em `5999c1b`: `README.md`, seção "Do relatório ao arquivo": as Tabelas II a X e as Figs. 3 a 5 do relatório, uma linha cada; a Tabela I e as Figs. 1 e 2 são escritas no `.tex` e não têm número de experimento; uma segunda tabela cobre o que só os slides e o texto usam.
- [x] `git ls-files | grep -E "\.(pkl|joblib|pcap|parquet)$|^project/data/(raw|processed)/|referencias/.*\.pdf"` não devolve nada. Arquivos pequenos de resultado em `results/` podem ser CSV. **Fechado em 08/10/2026:** executado em `5999c1b`: nenhuma linha.
- [x] `grep -rnE "/Users/|/home/|[A-Z]:\\\\" --include="*.py" src scripts tests data` não devolve nada (o mesmo grep do CI). **Fechado em 08/10/2026:** executado em `5999c1b`: nenhuma linha; o grep de referência interna também não devolve nada.
- Não se aplica (decisões 44 e 55d): `git shortlog -sn` mostra os quatro integrantes. Executado em `5999c1b`: 164 commits de uma identidade; a execução ficou na sessão de implementação e a equipe aceitou o histórico assim. Nenhum commit tem coautoria de ferramenta (executado: 0 ocorrências).
- [x] Licença decidida e `LICENSE` no repositório. **Fechado em 08/10/2026:** `LICENSE` (MIT) na raiz, em `7813020`; decisão 55c.
- [ ] **Pessoa:** checklist do projeto rodada (skill `checklist-entrega projeto`), sem item exigido pendente. Faz parte da entrega de 18/11 (item 5 de `docs/07-pendencias.md`, "O que resta de pessoa"). Não há registro versionado de que já tenha sido rodada.
- [ ] **Pessoa:** link e PDF enviados até 18/11/2026, com o comprovante (data, hora e hash do commit entregue) guardado em `docs/07-pendencias.md`; antes, enviar os commits finais e conferir o CI verde no commit entregue (itens 1 e 5 de "O que resta de pessoa").

## Testes

Seção "Tarefa 19" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md).

## Verificação ao concluir

Gate de entrega: G1–G4, G7–G10, mais a execução limpa descrita em `VERIFICACAO.md`.
