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

## DoH-Tunnel-Traffic-HKD

### Origem

- Repositório do dataset: https://github.com/doh-traffic-dataset/DoH-Tunnel-Traffic-HKD
- Download: https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/88092, repositório da Universidade de Hokkaido. O download é manual.
- Data do download: 07/10/2026.
- Condições de uso: a página de download traz a nota "rights Reserved", e o `README.txt` do dataset pede a citação abaixo. Os arquivos ficam fora do Git.
- Citação exigida pelos mantenedores: R. Mitsuhashi, Y. Jin, K. Iida, T. Shinagawa and Y. Takai, "Malicious DNS Tunnel Tool Recognition Using Persistent DoH Traffic Analysis," IEEE Trans. Netw. Service Manag., vol. 20, no. 2, pp. 2086-2095, June 2023, doi: 10.1109/TNSM.2022.3215681. O `README.txt` do dataset cita o artigo com o ano de 2022.

### Arquivos

Ficam em `data/raw/hkd/`:

| Arquivo | Linhas | Uso | No manifesto |
| --- | --- | --- | --- |
| `DoH-CSVs/DoH-CSVs-48h/Total-48h.csv` | 5.258 | Fonte do projeto: um registro por fluxo | obrigatório |
| `Total-48h-Augmentation.csv` | 105.160 | Lido só para conferir que é o arquivo anterior com cada fluxo repetido 20 vezes | obrigatório |
| `README.txt` | não se aplica | Descrição e citação do dataset | fora do manifesto |

- O dataset só tem tráfego de túnel DoH, de três ferramentas: dnstt, tcp-over-dns e tuns. A coluna `Label` traz o nome da ferramenta. Não há fluxo Non-DoH nem Benign-DoH.
- O `README.txt` descreve `Total-48h-Augmentation.csv` como "augmented assuming 20 client PCs". Medido: são as 5.258 linhas de `Total-48h.csv`, cada uma repetida exatamente 20 vezes, com os números arredondados. O projeto usa `Total-48h.csv`.
- `DoH-CSVs/` tem ainda um CSV por ferramenta e CSVs por hora de captura, e `DoH-Pcaps/` tem as capturas de pacotes. Não são lidos pelo projeto: `Total-48h.csv` reúne os fluxos, e os atributos já vêm extraídos.

## Combinado (CIRA-CIC-DoHBrw-2020 + DoH-Tunnel-Traffic-HKD)

### Origem

- Repositório do dataset: https://github.com/doh-traffic-dataset/CIRA-CIC-DoHBrw-2020-and-DoH-Tunnel-Traffic-HKD
- Download: a mesma página do DoH-Tunnel-Traffic-HKD, com as mesmas condições de uso. Data do download: 07/10/2026.
- Citação exigida pelos mantenedores: as duas anteriores, a do CIRA-CIC-DoHBrw-2020 e a do DoH-Tunnel-Traffic-HKD, porque o dataset tem dados dos dois.

### Arquivos

Ficam em `data/raw/combinado/`, todos obrigatórios no manifesto:

| Arquivo | Nível | Valores de `Label` | Linhas | O que o projeto lê |
| --- | --- | --- | --- | --- |
| `l1-total-add.csv` | 1 | `NonDoH` 897.493; `DoH` 374.803 | 1.272.296 | As linhas `NonDoH`: classe Non-DoH |
| `l2-total-add.csv` | 2 | `Benign` 19.807; `Malicious` 354.996 | 374.803 | As linhas `Benign`: classe Benign-DoH |
| `l3-total-add.csv` | 3 | `dns2tcp` 167.486; `dnscat2` 35.770; `iodine` 46.580; `dnstt` 46.080; `tcp-over-dns` 30.040; `tuns` 29.040 | 354.996 | Todas as linhas: classe Malicious-DoH, com a ferramenta |

- As linhas `DoH` do nível 1 e `Malicious` do nível 2 são os mesmos fluxos do nível 3 com rótulo menos detalhado. Lê-las também contaria o tráfego malicioso mais de uma vez.
- A ferramenta diz de onde o fluxo vem: dns2tcp, dnscat2 e iodine são do CIRA-CIC-DoHBrw-2020; dnstt, tcp-over-dns e tuns são do DoH-Tunnel-Traffic-HKD.
- **Os fluxos do HKD entram replicados**: as 105.160 linhas das três ferramentas do HKD são 5.258 fluxos distintos, cada um 20 vezes. O projeto grava o combinado de duas formas, como publicado e com cada fluxo do HKD uma única vez.

## Formato dos CSVs do HKD e do combinado

- Cabeçalho: as mesmas 35 colunas do CIRA-CIC-DoHBrw-2020, com os mesmos nomes e na mesma ordem.
- Codificação: os CSVs do HKD e `l3-total-add.csv` começam com a marca de ordem de bytes (BOM) do UTF-8; `l1-total-add.csv` e `l2-total-add.csv` não. Todos são lidos com `encoding="utf-8-sig"`, que descarta a marca quando ela existe. Lido como UTF-8 comum, o arquivo com a marca fica com a primeira coluna sem o nome `SourceIP`.
- `TimeStamp`: no formato `2020/1/14 15:49`, sem segundos e sem zero à esquerda. No CIRA é `2020-01-14 15:49:11`.
- Em `Total-48h.csv`, os atributos `FlowBytesSent`, `FlowBytesReceived` e `PacketLengthMode` só têm valores inteiros. A carga converte os 29 atributos para decimal.

## Arquivos gerados

`uv run python scripts/e6_dados.py` confere os arquivos acima e grava em `data/processed/`, fora do Git:

| Arquivo | Conteúdo |
| --- | --- |
| `hkd.parquet` | Os fluxos de `Total-48h.csv` |
| `combinado.parquet` | As três classes do combinado, como publicado, sem as linhas com valor ausente |
| `combinado_sem_replicas.parquet` | O mesmo, com cada fluxo do HKD uma única vez |

Os três têm as mesmas colunas: os 29 atributos, `label` (0 Non-DoH, 1 Benign-DoH, 2 Malicious-DoH), `origin` (`CIRA` ou `HKD`) e `tool` (a ferramenta de túnel, vazia fora da classe maliciosa). Nenhum tem identificador do fluxo. As contagens medidas ficam em `results/e6/dados/`.


## Cuidados

- Arquivo baixado é dado não confiável: não execute nada que venha no zip nem carregue arquivos `.pkl` ou `.joblib` de terceiros.
- Nada de `data/raw/` ou de `data/processed/` entra em commit.
- Manifesto de hashes dos arquivos: `data/manifest.json`, conferido por `data/verify.py`.
