# 03 · dados · aquisição do CIRA-CIC-DoHBrw-2020

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
- Falta desta tarefa: `data/README.md`, `data/manifest.json`, `data/verify.py` e o teste dele (passos 2, 5 e 6). Os passos 3 e 7 já estão feitos.
- Cluster, opcional (decisão 42): se a execução for no Apuana, os arquivos são copiados à mão para o Apuana e conferidos lá com `data/verify.py`; o `data/README.md` diz onde ficam no servidor `[Preencher: caminho]`.

## Arquivos

- `data/raw/cira/` — CSVs baixados, fora do Git.
- `data/manifest.json` — novo: fonte única de nome, tamanho, número de linhas, SHA-256 e se o arquivo é obrigatório ou opcional.
- `data/README.md` — origem, data do download, citação exigida, como obter os arquivos e onde a equipe os compartilha; aponta para o manifesto, sem repetir os hashes.
- `data/verify.py` — novo: confere que os arquivos do manifesto existem e que os hashes batem.
- `tests/test_verify.py` — novo.

## O que fazer

1. (Feito em 07/10/2026.) Preencher o formulário em http://cicresearch.ca/CICDataset/DoHBrw-2020/ e baixar os CSVs de atributos estatísticos (não os PCAPs).
2. Registrar no `data/manifest.json` os nomes reais dos arquivos, o tamanho, o número de linhas (sem o cabeçalho), o SHA-256 (`shasum -a 256`) e se são obrigatórios (`Total_CSVs.zip`) ou opcionais (os outros dois zips, usados só na tarefa 21). No `data/README.md`: origem, data, citação, instruções de download e o local do drive da equipe `[Preencher: link]`.
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

- [ ] `data/manifest.json` lista cada arquivo com nome, tamanho, linhas, SHA-256 e obrigatoriedade; `data/README.md` traz origem, citação, data e o local do compartilhamento.
- [ ] `uv run python data/verify.py` termina com código 0 na máquina de quem baixou e falha quando um arquivo obrigatório é alterado ou removido; opcional ausente só avisa.
- [ ] As contagens de linhas por classe estão registradas e comparadas com as de `docs/04-dados.md:26-31`.
- [ ] O cabeçalho real está registrado, com a coluna de rótulo identificada.
- [ ] `git status` não mostra nenhum arquivo de `data/raw/`.

## Testes

Seção "Tarefa 03" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de dados: G1–G5 (G5 = `uv run python data/verify.py`), G7–G10.
