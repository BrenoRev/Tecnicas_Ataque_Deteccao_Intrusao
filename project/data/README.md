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

## Conferência

Depois de extrair, confira a integridade dos arquivos:

    cd project
    uv run python data/verify.py

O script recalcula o SHA-256 de cada arquivo listado em `data/manifest.json` e compara com o registrado. Termina com erro, nomeando o arquivo, se faltar um arquivo obrigatório ou se algum hash divergir. Arquivo opcional ausente gera só um aviso.

`data/manifest.json` é a fonte única de nome, tamanho, número de linhas, SHA-256 e obrigatoriedade de cada arquivo. Os hashes não são repetidos aqui.

## CIRA-CIC-DoHBrw-2020

### Origem

- Página do dataset: https://www.unb.ca/cic/datasets/dohbrw-2020.html
- Download: http://cicresearch.ca/CICDataset/DoHBrw-2020/. A página pede o preenchimento de um formulário, por isso o download é manual. Foram baixados os CSVs de atributos estatísticos, não os PCAPs.
- Data do download: 07/10/2026.
- Citação exigida pelos mantenedores: M. MontazeriShatoori, L. Davidson, G. Kaur and A. H. Lashkari, "Detection of DoH Tunnels using Time-series Classification of Encrypted Traffic," IEEE Cyber Science and Technology Congress, 2020.

### Arquivos

Ficam em `data/raw/cira/`:

| Arquivo | Nome no servidor do CIC | Uso | No manifesto |
| --- | --- | --- | --- |
| `Total_CSVs.zip` | `DoH_Dataset_CSVs.zip` | Fonte do projeto | obrigatório |
| `BenignDoH-NonDoH-CSVs.zip` | `DoHBenign-NonDoH-CSVs.zip` | Fluxos por navegador (Chrome, Firefox) | opcional |
| `MaliciousDoH-CSVs.zip` | `Mal-CSVs.zip` | Fluxos por ferramenta de túnel (dns2tcp, dnscat2, iodine) | opcional |

- Cada zip vem com um arquivo `.md5` do próprio CIC, que cita o nome do arquivo no servidor. Os três MD5 conferem com os zips.
- `Total_CSVs.zip` é lido direto, sem extrair: a integridade conferida é a do zip. Pastas extraídas ao lado dos zips não são usadas pelo projeto.

### Linhas por arquivo

Linhas de dados, sem contar o cabeçalho, de cada membro de `Total_CSVs.zip`:

| Membro | Camada | Valor de `Label` | Linhas | Tabela I do artigo | Diferença |
| --- | --- | --- | --- | --- | --- |
| `l1-nondoh.csv` | 1 | `NonDoH` | 897.493 | 889.809 | 7.684 |
| `l1-doh.csv` | 1 | `DoH` | 269.643 | não se aplica | não se aplica |
| `l2-benign.csv` | 2 | `Benign` | 19.807 | 19.746 | 61 |
| `l2-malicious.csv` | 2 | `Malicious` | 249.836 | 249.553 | 283 |

- A camada 1 separa DoH de Non-DoH; a camada 2 separa o DoH em benigno e malicioso. O artigo trata o problema com três classes: Non-DoH, Benign-DoH e Malicious-DoH.
- `l1-doh.csv` tem o mesmo número de linhas que `l2-benign.csv` e `l2-malicious.csv` somados (19.807 + 249.836 = 269.643). As três classes vêm de `l1-nondoh.csv`, `l2-benign.csv` e `l2-malicious.csv`; ler também `l1-doh.csv` contaria o DoH duas vezes.
- Os arquivos brutos têm 8.028 linhas a mais do que a Tabela I do artigo, que não explica a diferença. Ela é tratada na etapa de limpeza, não aqui.

### Cabeçalho e coluna de rótulo

Os quatro membros de `Total_CSVs.zip` têm o mesmo cabeçalho, com 35 colunas nesta ordem:

| Grupo | Colunas | Uso |
| --- | --- | --- |
| Identificadores (5) | `SourceIP`, `DestinationIP`, `SourcePort`, `DestinationPort`, `TimeStamp` | Não entram no modelo |
| Duração (1) | `Duration` | Atributo |
| Bytes de fluxo (4) | `FlowBytesSent`, `FlowSentRate`, `FlowBytesReceived`, `FlowReceivedRate` | Atributos |
| Comprimento de pacote (8) | `PacketLengthVariance`, `PacketLengthStandardDeviation`, `PacketLengthMean`, `PacketLengthMedian`, `PacketLengthMode`, `PacketLengthSkewFromMedian`, `PacketLengthSkewFromMode`, `PacketLengthCoefficientofVariation` | Atributos |
| Tempo de pacote (8) | `PacketTimeVariance`, `PacketTimeStandardDeviation`, `PacketTimeMean`, `PacketTimeMedian`, `PacketTimeMode`, `PacketTimeSkewFromMedian`, `PacketTimeSkewFromMode`, `PacketTimeCoefficientofVariation` | Atributos |
| Tempo de resposta (8) | `ResponseTimeTimeVariance`, `ResponseTimeTimeStandardDeviation`, `ResponseTimeTimeMean`, `ResponseTimeTimeMedian`, `ResponseTimeTimeMode`, `ResponseTimeTimeSkewFromMedian`, `ResponseTimeTimeSkewFromMode`, `ResponseTimeTimeCoefficientofVariation` | Atributos |
| Rótulo (1) | `Label` | Alvo |

- **A coluna de rótulo é `Label`, a última, em texto.** Cada membro tem um único valor, o da tabela anterior.
- São 29 atributos numéricos (1 + 4 + 8 + 8 + 8). O prefixo duplicado em `ResponseTimeTime` vem do extrator.
- Nos dois zips opcionais, os arquivos `CSVs/<nome>/all.csv` têm as mesmas 34 primeiras colunas, mas não têm `Label`: a última coluna é `DoH`, booleana (`True` ou `False`).

## Cluster

Se a execução for no cluster Apuana, os arquivos são copiados à mão para o servidor, na mesma estrutura de `data/raw/`, e conferidos lá com `uv run python data/verify.py`. Caminho no servidor: [Preencher: caminho].

## Cuidados

- Arquivo baixado é dado não confiável: não execute nada que venha no zip nem carregue arquivos `.pkl` ou `.joblib` de terceiros.
- Nada de `data/raw/` ou de `data/processed/` entra em commit.
- Manifesto de hashes dos arquivos: `data/manifest.json`, conferido por `data/verify.py`.
