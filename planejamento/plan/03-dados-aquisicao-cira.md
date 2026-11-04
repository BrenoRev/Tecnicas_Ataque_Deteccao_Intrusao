# 03 · dados · aquisição do CIRA-CIC-DoHBrw-2020

> **Situação (07/10/2026, reconciliação no commit `0ae2d49`): pronta e executada em `acc297a`** (branch `tarefa/03-dados-cira`, nascida de `tarefa/02-config-runlog`; commits `c2b69e0` e `acc297a`). **Concluída.** Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f).
>
> O ⚠️ REVISAR de `5e11d56` (zips do CIRA ausentes) foi **resolvido em 07/10/2026**: os três zips originais e os três `.md5` foram repostos em `project/data/raw/cira/` a partir do zip da equipe, e a decisão 34 vale como escrita. Conferido nesta reconciliação: `uv run python data/verify.py` devolve "OK: 3 de 3 arquivos do manifesto conferidos" e o MD5 de cada zip é o do `.md5` correspondente. As pastas extraídas `Total_CSVs/`, `CSVs/` e `CSVs 2/` continuam no disco ao lado dos zips; o projeto não as lê e elas podem ser apagadas.

## Como ficou (conferido no código em `0ae2d49`)

- `data/manifest.json`: `{"files": [...]}`; cada entrada tem `path` (relativo a `data/raw/`), `size_bytes`, `sha256`, `required` e `rows` (dicionário membro do zip → linhas sem o cabeçalho). Três entradas, todas do CIRA; `hkd/` e `combinado/` são da tarefa 13.
- `data/verify.py`: `check_files(manifest, raw_dir)` devolve `(erros, avisos)`; `main()` termina com código 1 se houver erro. Lê o manifesto de forma genérica: entrada nova não exige mudança no script.
- `sha256_of(path)` existe em `data/verify.py` e, igual, em `scripts/e0_dados.py`. O terceiro chamador leva a função para `src/`, pela regra de `.claude/rules/codigo.md`.
- `data/README.md` registra também o nome de cada zip no servidor do CIC e que os `all.csv` dos dois zips opcionais não têm `Label`: a última coluna é `DoH`, booleana.

**Onde:** `data/README.md`, `data/manifest.json`, `data/verify.py`, `tests/test_verify.py`, `data/raw/cira/` (fora do Git)
**Objetivo:** os CSVs do dataset do artigo estão na máquina de quem vai rodar, com origem e integridade registradas.
**Depende de:** — para o download e o registro manual (passos 1 a 4, onda 0); 01 para o script de conferência (passo 5)
**Demonstra:** `data/manifest.json` e `data/README.md` com origem, citação e SHA-256; `data/verify.py` verde na máquina de quem baixou. Seção 6: origem dos dados.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **Os passos 1 a 4 estão feitos.** Os dados estão em `project/data/raw/cira/`: `Total_CSVs.zip`, `BenignDoH-NonDoH-CSVs.zip`, `MaliciousDoH-CSVs.zip` e os três `.md5` do CIC, que conferem.
- Tamanho e SHA-256 de cada arquivo: tabela da seção 1 de `docs/08-inventario-dados.md`. O `data/manifest.json` (fonte única dos hashes) e o `data/README.md` são escritos a partir dela, recalculando os hashes na hora (não copiar sem conferir).
- A fonte do projeto é `Total_CSVs.zip`, lido direto, sem extrair. Os outros dois zips entram no manifesto como opcionais: só são necessários para a tarefa 21.
- Linhas por membro: `l1-nondoh.csv` 897.493; `l1-doh.csv` 269.643; `l2-benign.csv` 19.807; `l2-malicious.csv` 249.836.
- Coluna de rótulo: `Label`, em texto. Cabeçalho idêntico ao previsto.
- O plano B (extrair o CIRA de dentro do combinado) não é mais necessário, e seria pior: o combinado arredonda os números para 8 casas.
- (Feito em `c2b69e0` e `acc297a`.) Faltava desta tarefa: `data/manifest.json`, `data/verify.py` e o teste dele, e completar o `data/README.md` (passos 2 e 5). Os passos 3 e 7 já estão feitos.
- **`data/README.md` já existe** (tarefa 01, commit `5e11d56`), com o link do drive e o tutorial: o zip da equipe contém a pasta `data/` e é extraído dentro de `project/`. O passo 6 está feito. Esta tarefa acrescenta ao arquivo origem, data do download, citação exigida, registro do cabeçalho e da coluna de rótulo, e troca a linha do manifesto de hashes, que estava por preencher, pelo apontamento para `data/manifest.json`. O arquivo passa pela checagem de referência interna do CI: não cita `docs/`.
- O zip da equipe traz também `hkd/` e `combinado/`; o registro deles no manifesto é da tarefa 13.
- Cluster: não se aplica. Nada rodou no Apuana; a execução foi nesta máquina (decisão 44), e o `data/README.md` não precisa de caminho no servidor.

## Arquivos

- `data/raw/cira/` — CSVs baixados, fora do Git.
- `data/manifest.json` — novo: fonte única de nome, tamanho, número de linhas, SHA-256 e se o arquivo é obrigatório ou opcional.
- `data/README.md` — já existe (tarefa 01); completar com origem, data do download, citação exigida, como obter os arquivos e onde a equipe os compartilha; aponta para o manifesto, sem repetir os hashes.
- `data/verify.py` — novo: confere que os arquivos do manifesto existem e que os hashes batem.
- `tests/test_verify.py` — novo.

## O que fazer

1. (Feito em 07/10/2026.) Preencher o formulário em http://cicresearch.ca/CICDataset/DoHBrw-2020/ e baixar os CSVs de atributos estatísticos (não os PCAPs).
2. Registrar no `data/manifest.json` os nomes reais dos arquivos, o tamanho, o número de linhas (sem o cabeçalho), o SHA-256 (`shasum -a 256`) e se são obrigatórios (`Total_CSVs.zip`) ou opcionais (os outros dois zips, usados só na tarefa 21). No `data/README.md`: origem, data, citação, instruções de download e o local do drive da equipe (link e tutorial já estão no arquivo desde a tarefa 01).
3. (Feito; ver o bloco acima.) O cabeçalho é idêntico ao de `docs/04-dados.md:54-62` e o rótulo está em `Label`; registrar isso no `data/README.md`.
4. Registrar a citação exigida pelos mantenedores (`docs/04-dados.md:9`).
5. Escrever `data/verify.py`: lê `data/manifest.json`, recalcula os hashes e falha, com mensagem que nomeia o arquivo, se faltar arquivo obrigatório ou se qualquer hash divergir; arquivo opcional ausente gera aviso, não erro. Tem `main()` sob `if __name__ == "__main__":`, para o teste importar a função de conferência.
6. Os arquivos são compartilhados fora do Git, em um zip no drive da equipe: https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing. O link fica no README e em `data/README.md`.
7. (Feito em 07/10/2026: `docs/04-dados.md:8` e `:62` já não têm `[A verificar]`.) Qualquer ajuste novo em `docs/` é do agente `cin0114-doc-sync`, no fechamento; o implementador não edita `docs/`.

## Por quê

Decisão 17. É a primeira tarefa do caminho crítico: sem dados não há E0, e o download é manual (risco R4).

## Evidência — verificada no baseline

- `planejamento/MEMORY/01-discovery-stack.md`, "Downloads" — a URL devolve página com formulário, sem listagem de arquivos.
- `docs/04-dados.md:8` — nomes e fonte dos arquivos, verificados em 07/10/2026.
- `docs/04-dados.md:26-31` — contagens brutas esperadas: 897.493 Non-DoH, 19.807 Benign-DoH, 249.836 Malicious-DoH (fonte indireta).

## Risco

- Download: resolvido em 07/10/2026; o plano B (extrair o CIRA do combinado) não é mais necessário.
- Os CSVs virem em estrutura diferente da esperada (por camada, por ferramenta): só registrar o que veio; quem decide como unir é a tarefa 04.

## Critério de aceite

Conferido em 07/10/2026 no commit `0ae2d49`.

- [x] `data/manifest.json` lista cada arquivo com nome, tamanho, linhas, SHA-256 e obrigatoriedade; `data/README.md` traz origem, citação, data e o local do compartilhamento. Lido nos dois arquivos.
- [x] `uv run python data/verify.py` termina com código 0 na máquina de quem baixou e falha quando um arquivo obrigatório é alterado ou removido; opcional ausente só avisa. Executado: o script com os dados reais (código 0, três arquivos conferidos) e os quatro testes de `tests/test_verify.py`.
- [x] As contagens de linhas por classe estão registradas e comparadas com as de `docs/04-dados.md:26-31`. Lido: tabela "Linhas por arquivo" de `data/README.md` e campo `rows` do manifesto, com 897.493 / 19.807 / 249.836 ao lado da Tabela I. `results/e0/dados/cira/seed42/metrics.json` traz os mesmos três números em `raw_rows`, e o script de E0 falha se o bruto lido diferir do manifesto.
- [x] O cabeçalho real está registrado, com a coluna de rótulo identificada. Lido: seção "Cabeçalho e coluna de rótulo" de `data/README.md`.
- [x] `git status` não mostra nenhum arquivo de `data/raw/`. Executado: `git status` limpo e `git ls-files` sem nada de `project/data/raw/` nem de `project/data/processed/`.

## Testes

Seção "Tarefa 03" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de dados: G1–G5 (G5 = `uv run python data/verify.py`), G7–G10.
