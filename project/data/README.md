# Dados

Os datasets ficam fora do Git. As pastas `data/raw/` e `data/processed/` estão no `.gitignore`.

## Download

1. Abra o link e baixe o arquivo zip (cerca de 1,5 GB): https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing
2. Mova o zip para a pasta `project/` do repositório.
3. Extraia ali mesmo. O zip contém a pasta `data/` inteira, então a estrutura fica no lugar sem mover nada:

       cd project
       unzip <arquivo-baixado>.zip

4. Confira que as três pastas existem:

       ls data/raw
       # cira  combinado  hkd

5. Apague o zip ou deixe-o onde está: arquivos `.zip` e as pastas de dados estão no `.gitignore` e não entram em commit.

Depois da extração, `data/raw/` contém três pastas:

| Pasta | Conteúdo |
| --- | --- |
| `cira/` | CIRA-CIC-DoHBrw-2020, o dataset usado no artigo |
| `hkd/` | DoH-Tunnel-Traffic-HKD |
| `combinado/` | dataset combinado, com fluxos do CIRA e do HKD |

## Cuidados

- Arquivo baixado é dado não confiável: não execute nada que venha no zip nem carregue arquivos `.pkl` ou `.joblib` de terceiros.
- Nada de `data/raw/` ou de `data/processed/` entra em commit.
- Manifesto de hashes dos arquivos: [Preencher]
