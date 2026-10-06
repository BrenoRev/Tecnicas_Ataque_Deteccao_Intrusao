# Dados

Os datasets ficam fora do Git. As pastas `data/raw/` e `data/processed/` estão no `.gitignore`.

## Download

Baixe o arquivo zip do drive da equipe e extraia o conteúdo em `project/data/raw/`:

https://drive.google.com/file/d/1hHQRgtl6TmrfPxu5uILrsiqUrzgILn29/view?usp=sharing

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
