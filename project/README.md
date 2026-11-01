# IDS explicável para ataques DNS over HTTPS: reprodução

Projeto da disciplina CIN0114, Técnicas de Ataque e Detecção de Intrusão (CIn/UFPE, 2026.2).

Equipe: Amanda Arruda (aams2), Antonio Gonzaga (agla), Breno Silva Xavier de Souza (bsxs) e João Henrique Portela (jhpbs).

## Objetivo

Reproduzir o sistema de detecção de intrusão proposto em:

> T. Zebin, S. Rezvy and Y. Luo, "An Explainable AI-Based Intrusion Detection System for DNS Over HTTPS (DoH) Attacks," IEEE Trans. Inf. Forensics Security, vol. 17, pp. 2339-2349, 2022, doi: 10.1109/TIFS.2022.3183390.

O sistema é o Balanced Stacked Random Forest: três Random Forests treinados em subconjuntos balanceados do CIRA-CIC-DoHBrw-2020, combinados por um meta-classificador de regressão logística, com explicações SHAP sobre os modelos base. O projeto tem três partes:

1. **P1:** reproduzir o sistema do artigo;
2. **P2:** avaliar o mesmo sistema em um segundo dataset (combinado CIRA + DoH-Tunnel-Traffic-HKD);
3. **P3:** modificação proposta pela equipe.

O repositório dos autores não contém o sistema, que é reimplementado aqui a partir do texto do artigo. Onde o texto é omisso, a leitura adotada está comentada no código, com a seção do artigo.

Todo resultado declara a trilha a que pertence, e as trilhas não se misturam:

| Trilha | O que é |
| --- | --- |
| `fiel` | o artigo como escrito, com profundidade máxima 5 nos Random Forests base (Seção IV-B) |
| `variante` | uma leitura alternativa de um ponto que o artigo deixa em aberto; a principal é a profundidade variável (linha 3 do Algoritmo 1) |
| `corrigida` | protocolo de avaliação corrigido pela equipe: 10 seeds, comparação pareada, folds por máquina |

## Estrutura

Este diretório (`project/`) contém o código. Os comandos abaixo rodam dentro dele.

```
├── pyproject.toml       # dependências com versão fixada
├── uv.lock              # versões resolvidas, usadas por uv sync --locked
├── requirements.txt     # exportado do uv.lock, para instalação com pip
├── data/                # manifesto de hashes e conferência; os dados ficam fora do Git
├── src/doh_ids/         # código reutilizável: dados, splits, modelos, avaliação, SHAP, registro
├── scripts/             # um script por experimento, os de resumo e os do relatório
├── tests/               # testes com dados sintéticos
├── results/             # métricas, resumos e figuras gerados pelos scripts
└── report/              # relatório, apresentação, tabelas e figuras geradas
```

## Instalação

O projeto usa Python 3.12, com as versões das bibliotecas fixadas no `pyproject.toml` e no `uv.lock`: scikit-learn, imbalanced-learn, mlxtend, xgboost, shap, explainerdashboard (o painel), pandas, numpy, pyarrow, scipy e matplotlib; pytest e ruff para testes e lint.

Com [uv](https://docs.astral.sh/uv/):

    cd project
    uv sync --locked

Com pip, em um ambiente virtual com Python 3.12:

    cd project
    python3.12 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -e .

O `requirements.txt` é gerado por `uv export --no-emit-project --no-hashes -o requirements.txt` e não é editado à mão. Com pip, os comandos deste README rodam sem o prefixo `uv run`.

Dois requisitos ficam fora desse ambiente e só servem aos entregáveis escritos:

- a apresentação pede o `python-pptx`, que está no grupo `slides` do `pyproject.toml` e não entra no `requirements.txt` (com pip: `pip install python-pptx==1.0.2`);
- o PDF do relatório pede o [tectonic](https://tectonic-typesetting.github.io/) ou uma instalação com XeLaTeX.

## Dados

Os datasets não são versionados; ficam em um zip no drive da equipe.

1. Abra o link e baixe o arquivo zip (cerca de 1,5 GB): https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing
2. Mova o zip para a pasta `project/` do repositório.
3. Extraia ali mesmo. O zip contém a pasta `data/` inteira, então a estrutura fica no lugar sem mover nada:

       cd project
       unzip <arquivo-baixado>.zip

4. Confira que as três pastas existem:

       ls data/raw
       # cira  combinado  hkd

5. Apague o zip ou deixe-o onde está: arquivos `.zip` e as pastas de dados estão no `.gitignore` e não entram em commit.

   Se a extração criar uma pasta `__MACOSX/`, apague-a (`rm -rf __MACOSX`): ela não está no `.gitignore`, e um arquivo novo na árvore faz os `run.json` registrarem `dirty: true`.

6. Confira a integridade dos arquivos:

       uv run python data/verify.py

   O script recalcula o SHA-256 de cada arquivo de `data/manifest.json` e termina com erro, nomeando o arquivo, se algum faltar ou divergir.

A origem de cada dataset, as citações exigidas e as pastas esperadas estão em [`data/README.md`](data/README.md).

## Como rodar

Lint, formatação e testes (os testes usam dados sintéticos e não precisam dos datasets):

    uv run ruff check .
    uv run ruff format --check .
    uv run pytest

Métricas recalculadas a partir das matrizes de confusão da Fig. 4 do artigo, só com a biblioteca padrão:

    python3 scripts/metricas_fig4.py

### Ordem dos scripts

Os 22 passos abaixo regeneram tudo o que está em `results/` e em `report/`. Cada script de treino treina, avalia e grava `metrics.json` (só valores determinísticos) e `run.json` (configuração, commit, máquina e tempos) em `results/<experimento>/<trilha>/<recorte>/seed<k>/`. Os scripts de resumo não treinam: leem esses arquivos e escrevem o `RESUMO.md` e os agregados.

Script que importa outro script roda como módulo, com `python -m scripts.<nome>`; os demais, pelo caminho do arquivo. A coluna "Precisa de" indica os passos que têm de ter rodado antes.

| # | Comando | O que faz | Precisa de | Tempo medido | Grava em |
| --- | --- | --- | --- | --- | --- |
| 1 | `uv run python data/verify.py` | confere os hashes dos arquivos baixados | `data/raw/` | segundos | nada |
| 2 | `uv run python scripts/e0_dados.py` | limpa o CIRA, grava o Parquet e descreve os dados (Tabela I e Fig. 2 do artigo) | `data/raw/cira/` | 44 s | `data/processed/`, `results/e0/` |
| 3 | `uv run python scripts/e6_dados.py` | prepara o segundo dataset: HKD, combinado como publicado e combinado sem réplicas | `data/raw/hkd/`, `data/raw/combinado/`, 2 | menos de 1 min | `data/processed/`, `results/e6/dados/` |
| 4 | `uv run python scripts/e1_reproducao.py` | reprodução do sistema nas duas leituras de profundidade, com a validação cruzada de 10 folds (Fig. 4) | 2 | 56 min | `results/e1/` |
| 5 | `uv run python scripts/e2_baselines.py` | árvore de decisão, XGBoost e Random Forest da Tabela II | 2, 4 | 3 min | `results/e2/` |
| 6 | `uv run python scripts/e5_xai.py` | SHAP sobre os Random Forests base (Figs. 5 a 8) | 2, 3, 4 | 9 min | `results/e5/` |
| 7 | `uv run python scripts/e6_dataset2.py` | sistema no segundo dataset: transferência e retreino nos dois combinados | 2, 3, 4 | 42 min | `results/e6/{fiel,variante}/` |
| 8 | `uv run python -m scripts.e6_baselines_xai` | modelos de comparação e SHAP no combinado sem réplicas | 6, 7 | 31 min | `results/e6/{fiel,variante}/retreino_sem_replicas-*/` |
| 9 | `uv run python -m scripts.e6_resumo` | resumo do segundo dataset ao lado do CIRA | 4 a 8 | segundos | `results/e6/RESUMO.md` e o de cada trilha |
| 10 | `uv run python scripts/e7_ferramenta.py` | identificação da ferramenta de túnel (Seção VI-D e Fig. 9) | `data/raw/cira/`, 3 | 40 s | `results/e7/` |
| 11 | `uv run python -m scripts.e7_resumo` | resumo da ferramenta de túnel | 10 | segundos | `results/e7/RESUMO.md` |
| 12 | `uv run python scripts/e3_sensibilidade.py` | sensibilidade às leituras alternativas dos pontos em aberto | 2 | 9 min | `results/e3/variante/` |
| 13 | `uv run python scripts/e4_corrigido.py` | protocolo corrigido: cinco modelos em 10 seeds e folds por máquina | 2 | 1 h 59 min | `results/e4/corrigida/` |
| 14 | `uv run python -m scripts.e4_resumo` | médias, desvios e comparação pareada do protocolo corrigido | 13 | segundos | `results/e4/corrigida/summary.json`, `RESUMO.md` |
| 15 | `uv run python -m scripts.e3_resumo` | tabela comparativa da sensibilidade | 4, 12, 13 | segundos | `results/e3/variante/comparacao.csv`, `RESUMO.md` |
| 16 | `uv run python -m scripts.e8_modificacao` | modificação da equipe (Random Forest único com peso de classe e seleção de hiperparâmetros), em 10 seeds, nos dois datasets | 2, 3, 13 | 1 h 59 min | `results/e8/corrigida/<modelo>-<dados>/` |
| 17 | `uv run python -m scripts.e8_robustez` | robustez: ablação da duração e fragmentação simulada do fluxo | 13, 16 | 1 h 57 min | `results/e8/corrigida/robustez-*/` |
| 18 | `uv run python -m scripts.e8_resumo` | médias e comparação pareada da modificação | 7, 13, 16, 17 | segundos | `results/e8/corrigida/summary.json`, `RESUMO.md` |
| 19 | `uv run python -m scripts.e8_robustez_resumo` | médias da robustez | 13, 16, 17 | segundos | `results/e8/corrigida/summary-robustez.json`, `RESUMO-ROBUSTEZ.md` |
| 20 | `uv run python scripts/make_report_assets.py` | tabelas e figuras do relatório e dos slides | 1 a 19 | segundos | `report/tables/`, `report/figures/`, `report/INDICE.md` |
| 21 | `uv run --group slides python scripts/make_slides.py` | apresentação e roteiro da fala | 20 | segundos | `report/apresentacao.pptx`, `report/roteiro.md` |
| 22 | `tectonic relatorio.tex`, dentro de `report/` | PDF do relatório | 20 | segundos | `report/relatorio.pdf` |

O tempo medido é a soma dos tempos registrados nos `run.json` versionados. Ele não inclui a carga dos dados nem a gravação das figuras, foi medido com a máquina em uso e varia entre execuções. A sequência inteira leva cerca de 9 horas na máquina descrita em "Onde os resultados foram gerados". Os passos 13, 16 e 17 somam quase 6 horas e não dependem dos passos 4 a 12.

Os passos 16 e 17 retomam de onde pararam se forem relançados no mesmo commit, com a árvore limpa. Os passos 4 e 13 não têm retomada.

### Execução limpa

Para rodar os 22 passos de uma vez, parando no primeiro erro, com a saída de cada passo em um arquivo de log:

    bash scripts/execucao_limpa.sh <diretório de logs, fora do repositório>

O diretório de logs fica fora do repositório porque um arquivo novo dentro dele deixa a árvore suja, e o `run.json` registra esse estado (`dirty`).

Para comparar o que foi regenerado com o que está versionado, guarde uma cópia de `results/` e de `report/` antes de rodar, ou use um segundo clone:

    uv run python scripts/comparar_resultados.py <results versionado> <results regenerado> \
        --report <report versionado> <report regenerado>

O script compara byte a byte os `metrics.json`, o `split_counts.json`, o agregado do protocolo corrigido, os CSV e as tabelas do relatório, e sai com código 1 se houver diferença. Diferenças esperadas, que ele não conta:

- os `run.json`, que trazem commit, data e tempos;
- os valores de tempo dos dois agregados da modificação (`results/e8/corrigida/summary.json` e `summary-robustez.json`), comparados sem eles;
- os `RESUMO*.md` e as três tabelas do relatório que citam tempo de treino (`tempos_treino`, `modificacao_metricas_dupla` e `modificacao_pareada_dupla`), listados na saída quando diferem;
- PNG, PDF e a apresentação, que carregam data de criação.

## Do relatório ao arquivo

Toda tabela e toda figura numérica do relatório é gerada por `scripts/make_report_assets.py` (passo 20) a partir de `results/`; nenhum número é digitado. A coluna "Script" indica quem gera os resultados lidos. Tabelas em `report/tables/` (`.tex` e `.csv`) e figuras em `report/figures/` (`.pdf` e `.png`).

| No relatório | Arquivo em `report/` | Script | Arquivo em `results/` |
| --- | --- | --- | --- |
| Tabela II, fluxos por classe do CIRA | `tables/dados_cira_contagens` | `e0_dados.py` | `e0/dados/cira/seed42/` |
| Tabela III, fluxos por classe do segundo dataset | `tables/dados_segundo_contagens` | `e6_dados.py`, `e6_dataset2.py` | `e6/dados/`, `e6/fiel/retreino_*/seed42/` |
| Fig. 3, matrizes de confusão no teste (Fig. 4b do artigo) | `figures/matriz_confusao_teste_dupla` | `e1_reproducao.py` | `e1/fiel/proposto/seed42/`, `e1/variante/profundidade_variavel/seed42/` |
| Tabela IV, métricas da reprodução | `tables/reproducao_metricas` | `e1_reproducao.py` | os mesmos |
| Tabela V, metade superior da Tabela II do artigo | `tables/tabela2_superior_macro_dupla` | `e1_reproducao.py`, `e2_baselines.py` | `e1/`, `e2/fiel/<modelo>/seed42/` |
| Tabela VI, metade inferior da Tabela II do artigo | `tables/tabela2_literatura` | nenhum: valores do artigo | transcritos em `src/doh_ids/config.py` |
| Fig. 4, importância global SHAP (Fig. 5 do artigo) | `figures/shap_importancia_cira` | `e5_xai.py` | `e5/fiel/proposto/seed42/`, `e5/variante/profundidade_variavel/seed42/` |
| Tabela VII, ferramenta de túnel (Seção VI-D do artigo) | `tables/ferramenta_metricas` | `e7_ferramenta.py` | `e7/{fiel,variante}/ferramenta/seed42/` |
| Tabela VIII, modelos nos dois datasets | `tables/segundo_baselines_dupla` | `e1_reproducao.py`, `e2_baselines.py`, `e6_dataset2.py`, `e6_baselines_xai` | `e1/`, `e2/`, `e6/{fiel,variante}/retreino_sem_replicas*/seed42/` |
| Tabela IX, recall por ferramenta no segundo dataset | `tables/segundo_recall_ferramenta` | `e6_dataset2.py` | `e6/{fiel,variante}/{transferencia,retreino_publicado,retreino_sem_replicas}/seed42/` |
| Tabela X, modificação contra o sistema do artigo | `tables/modificacao_metricas_dupla` | `e4_corrigido.py`, `e8_modificacao`, `e8_resumo` | `e8/corrigida/summary.json` |
| Fig. 5, recall sob fragmentação | `figures/robustez_fragmentacao` | `e8_robustez`, `e8_robustez_resumo` | `e8/corrigida/summary-robustez.json` |

A Tabela I (trabalhos relacionados) e as Figs. 1 e 2 (modelo de ameaça e diagrama do sistema) são escritas em `report/relatorio.tex` e não têm número de experimento.

Os números citados no texto do relatório, fora das tabelas, vêm destes arquivos, que também alimentam os slides:

| Resultado | Arquivo em `report/` | Script | Arquivo em `results/` |
| --- | --- | --- | --- |
| Captura do CIRA; Fig. 2 do artigo | `tables/dados_cira_captura`, `figures/fig2_densidades_dupla` | `e0_dados.py` | `e0/dados/cira/seed42/` |
| Ferramentas do segundo dataset | `tables/dados_segundo_ferramentas` | `e6_dados.py`, `e6_dataset2.py` | `e6/dados/` |
| Validação cruzada (Fig. 4a do artigo) e matrizes em tabela | `figures/matriz_confusao_validacao_dupla`, `tables/reproducao_matriz_{teste,validacao}` | `e1_reproducao.py` | `e1/` |
| Tabela II do artigo com média ponderada; meta-classificador; tempos | `tables/tabela2_superior_ponderada_dupla`, `tables/reproducao_meta`, `tables/tempos_treino` | `e1_reproducao.py`, `e2_baselines.py` | `e1/`, `e2/` (os tempos, dos `run.json`) |
| SHAP: ranking, estabilidade, Figs. 6 a 8 do artigo, nos dois datasets | `tables/shap_{ranking,estabilidade}`, `figures/shap_{importancia,dependencia,local}_*` | `e5_xai.py`, `e6_baselines_xai` | `e5/`, `e6/{fiel,variante}/retreino_sem_replicas-shap/seed42/` |
| Segundo dataset: métricas, matrizes, réplicas, recall por ferramenta | `tables/segundo_{metricas,matrizes,replicas}`, `figures/segundo_recall_ferramenta` | `e6_dataset2.py` | `e6/{fiel,variante}/` |
| Fig. 9 do artigo | `figures/fig9_ferramentas_dupla` | `e7_ferramenta.py` | `e7/dados/fig9/seed42/` |
| Sensibilidade às leituras alternativas | `tables/sensibilidade_dupla` | `e3_sensibilidade.py`, `e3_resumo` | `e3/variante/comparacao.csv` |
| Protocolo corrigido: métricas, linhas repetidas, taxa base, folds por máquina, distribuição por seed | `tables/corrigido_*`, `figures/corrigido_seeds` | `e4_corrigido.py`, `e4_resumo` | `e4/corrigida/summary.json`, `e4/corrigida/<modelo>/seed<k>/` |
| Modificação: comparação pareada e transferência | `tables/modificacao_{pareada_dupla,transferencia}` | `e8_modificacao`, `e8_resumo` | `e8/corrigida/summary.json` |
| Robustez: tabela e recall por seed | `tables/robustez_{fragmentacao_dupla,seeds}` | `e8_robustez`, `e8_robustez_resumo` | `e8/corrigida/summary-robustez.json` |

A origem e a legenda de cada arquivo, um a um, estão em [`report/INDICE.md`](report/INDICE.md), gerado pelo mesmo script.

## Relatório, slides e painel

Tabelas e figuras, a partir de `results/`:

    uv run python scripts/make_report_assets.py

Apresentação e roteiro da fala. O script parte do modelo de slides do CIn, que fica na pasta `geracao_latex_and_pdf/`, na raiz do repositório:

    uv run --group slides python scripts/make_slides.py

PDF do relatório, com tectonic ou com XeLaTeX:

    cd report
    tectonic relatorio.tex

Painel interativo de explicabilidade, como o da Seção VI-C do artigo (precisa dos dados):

    uv run python scripts/painel_xai.py

O script treina o sistema na memória, calcula os valores SHAP de um dos Random Forests base em uma amostra do teste e serve o painel em http://127.0.0.1:8050, só na própria máquina. O endereço responde depois de alguns minutos de treino e cálculo. Nenhum modelo é gravado nem lido do disco, e o painel não grava resultado: é material de demonstração, e os números vêm de `scripts/e5_xai.py`. Para encerrar, Ctrl+C.

## Resultados

Os números abaixo estão nos arquivos indicados; as tabelas completas ficam nos `RESUMO.md` e no relatório.

- **P1, reprodução.** Com profundidade 5, o sistema empilhado não prediz Benign-DoH em nenhum fluxo do teste, e a matriz de confusão fica a 4711 fluxos da Fig. 4b do artigo. Com profundidade variável fica a 553, com F1 macro de 96,56%; nenhuma das duas leituras reproduz a Tabela II do artigo. Ver [`results/e1/RESUMO.md`](results/e1/RESUMO.md), [`results/e2/fiel/RESUMO.md`](results/e2/fiel/RESUMO.md), [`results/e5/RESUMO.md`](results/e5/RESUMO.md), [`results/e7/RESUMO.md`](results/e7/RESUMO.md), [`results/e3/variante/RESUMO.md`](results/e3/variante/RESUMO.md) e [`results/e4/corrigida/RESUMO.md`](results/e4/corrigida/RESUMO.md).
- **P2, segundo dataset.** Treinado no CIRA, o sistema detecta 1,81% dos 5258 fluxos de túnel do HKD. Retreinado no combinado sem réplicas, detecta 99,42% (510 de 513) dos fluxos do HKD do teste, que são das mesmas ferramentas vistas no treino. Ver [`results/e6/RESUMO.md`](results/e6/RESUMO.md).
- **P3, modificação.** Um Random Forest único com peso de classe e seleção de hiperparâmetros tem F1 macro 0,50 ponto acima do sistema do artigo no CIRA, nas dez seeds, com tempo de treino maior (263,2 s contra 161,0 s). Sob fragmentação simulada do fluxo, o resultado não ordena os dois modelos em robustez. Ver [`results/e8/corrigida/RESUMO.md`](results/e8/corrigida/RESUMO.md) e [`results/e8/corrigida/RESUMO-ROBUSTEZ.md`](results/e8/corrigida/RESUMO-ROBUSTEZ.md).

## Limitações

A discussão completa está na seção de conclusões do relatório (`report/relatorio.pdf`).

- A reprodução e o segundo dataset têm uma execução, com seed 42. Só o protocolo corrigido e a modificação têm dez seeds, e os conjuntos de teste das seeds se sobrepõem; por isso o relatório não usa significância estatística.
- O segundo dataset compartilha duas das três classes com o CIRA; só a classe maliciosa ganha fluxos novos.
- A fragmentação é uma perturbação no espaço de atributos, não tráfego gerado.
- Os valores SHAP explicam os Random Forests base, não a saída do modelo empilhado.
- O método da identificação da ferramenta de túnel é leitura da equipe: o artigo não o descreve.
- Os tempos de treino foram medidos em uma máquina em uso e variam entre execuções.

## Onde os resultados foram gerados

Os 229 `run.json` versionados registram a mesma máquina (mesmo `hostname`), com 10 núcleos (`cpu_count`), Python 3.12.13 e a árvore limpa (`dirty: false`). As versões das bibliotecas gravadas coincidem com as do `uv.lock` (13 execuções mais antigas registram só as oito primeiras): scikit-learn 1.9.1, imbalanced-learn 0.14.2, mlxtend 0.25.0, xgboost 3.4.1, shap 0.52.0, pandas 3.0.6, numpy 2.3.5, pyarrow 25.0.1, matplotlib 3.11.2, scipy 1.18.1 e explainerdashboard 0.5.8. Cada `run.json` traz ainda o commit do código, o hash dos dados, a seed e a configuração da execução.

## Como contribuir

1. Ative os hooks do Git uma vez por clone, na raiz do repositório:

       git config core.hooksPath .githooks

   O `pre-commit` roda o lint e a conferência de formatação; o `commit-msg` confere a mensagem.

2. Instale o ambiente como em "Instalação", com uv ou com pip.

3. Antes de cada commit, dentro de `project/`:

       uv run ruff check .
       uv run ruff format --check .
       uv run pytest

   Para corrigir: `uv run ruff check --fix .` e `uv run ruff format .`. Não use `--no-verify`.

4. Mensagem de commit: `tipo(escopo): resumo no imperativo`, em português, com até 72 caracteres na primeira linha. Tipos aceitos: `feat`, `fix`, `docs`, `exp`, `refactor`, `test`, `chore`, `ci`. Exemplo: `feat(splits): adiciona split estratificado com seed`. Sem `Co-Authored-By` e sem assinatura de ferramenta.

5. Adicione arquivos pelo nome (`git add caminho/do/arquivo`), nunca `git add -A` nem `git add .`. Dados, modelos serializados (`.pkl`, `.joblib`) e o PDF do artigo não entram em commit.

6. Uma branch por mudança, criada da `main` atualizada, e integração por pull request com o CI verde e a revisão de outro integrante. A descrição do pull request segue o modelo em `.github/pull_request_template.md`: escopo, o que demonstra, como verificar e a verificação com dados reais.

## Licença

Licença: [Preencher]
