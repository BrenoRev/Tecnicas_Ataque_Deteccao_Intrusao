# 04. Dados

> Os dados foram baixados e conferidos em 07/10/2026. O que foi medido nos arquivos está em [08-inventario-dados.md](08-inventario-dados.md) e prevalece sobre as estimativas e os `[A verificar]` deste documento.

## 1. CIRA-CIC-DoHBrw-2020 (dataset do artigo)

- Página: https://www.unb.ca/cic/datasets/dohbrw-2020.html
- Download: http://cicresearch.ca/CICDataset/DoHBrw-2020/ (a página pede preenchimento de formulário; não foi possível listar os arquivos automaticamente) Verificado: três zips, com MD5 do CIC conferido; a fonte é `Total_CSVs.zip` (ver [08-inventario-dados.md](08-inventario-dados.md)).
- Citação exigida pelos mantenedores: M. MontazeriShatoori, L. Davidson, G. Kaur and A. H. Lashkari, "Detection of DoH Tunnels using Time-series Classification of Encrypted Traffic," IEEE Cyber Science and Technology Congress, 2020.
- Redistribuição: a página permite redistribuir e espelhar, desde que com a citação. Mesmo assim os dados ficam fora do Git, com manifesto de hashes e script de conferência.

### Como foi gerado

| Classe | Origem | Ferramentas |
| --- | --- | --- |
| Non-DoH | Acesso HTTPS a sites da lista Alexa | Chrome, Firefox |
| Benign-DoH | Resolução DoH feita pelos navegadores | Chrome, Firefox |
| Malicious-DoH | Túneis DNS sobre DoH | dns2tcp, DNSCat2, iodine |

Resolvedores DoH: AdGuard, Cloudflare, Google DNS, Quad9.

Estrutura em duas camadas: a camada 1 separa DoH de Non-DoH; a camada 2 separa DoH benigno de malicioso. O artigo de referência achata as duas camadas em um problema de três classes.

### Contagens

| Classe | Tabela I do artigo | Dataset bruto | Diferença |
| --- | --- | --- | --- |
| Non-DoH | 889.809 | 897.493 | 7.684 |
| Benign-DoH | 19.746 | 19.807 | 61 |
| Malicious-DoH | 249.553 | 249.836 | 283 |
| Total | 1.159.108 | 1.167.136 | 8.028 |

A coluna "dataset bruto" vem do README do dataset combinado CIRA + HKD (seção 3), que informa as contagens por nível e por ferramenta; os maliciosos são a soma de dns2tcp (167.486), dnscat2 (35.770) e iodine (46.580). Confirmado nos CSVs originais em 07/10/2026.

O artigo não explica a diferença. **Ela é exatamente o número de linhas com NaN**: removê-las reproduz a Tabela I nas três classes ([08-inventario-dados.md](08-inventario-dados.md), seção 3). Reproduzir as contagens da Tabela I é o primeiro marco verificável da reprodução (ambiguidade A1 em [02-artigo.md](02-artigo.md)).

### Split implícito no artigo

Deduzido das somas da Figura 4, não do texto:

| Classe | Treino (90%) | Teste (10%) |
| --- | --- | --- |
| Non-DoH | 800.829 | 88.980 |
| Benign-DoH | 17.771 | 1.975 |
| Malicious-DoH | 224.598 | 24.955 |
| Total | 1.043.198 | 115.910 |

Subconjuntos balanceados, pela descrição da seção III-B: cada um recebe um terço do Non-DoH de treino (266.943), os 224.598 maliciosos e a classe benigna aumentada por SMOTE. Se o benigno for aumentado até o tamanho do malicioso, 17.771 de 224.598 amostras são reais, ou seja, cerca de 92% da classe benigna de cada subconjunto é sintética. Esse percentual é estimativa nossa a partir da razão declarada; o artigo não dá o número.

### Colunas

Lidas do código do extrator (DoHLyzer, `meter/flow.py`, função `get_data`). Conferido contra o cabeçalho dos CSVs em 07/10/2026: nomes e ordem idênticos.

| Grupo | Colunas | Uso |
| --- | --- | --- |
| Identificadores | `SourceIP`, `DestinationIP`, `SourcePort`, `DestinationPort`, `TimeStamp` | **Não entram no modelo** |
| Duração | `Duration` | Atributo |
| Bytes de fluxo | `FlowBytesSent`, `FlowSentRate`, `FlowBytesReceived`, `FlowReceivedRate` | Atributos |
| Comprimento de pacote | `PacketLength` + `Variance`, `StandardDeviation`, `Mean`, `Median`, `Mode`, `SkewFromMedian`, `SkewFromMode`, `CoefficientofVariation` | Atributos |
| Tempo de pacote | `PacketTime` + os mesmos oito sufixos | Atributos |
| Tempo de resposta | `ResponseTimeTime` + os mesmos oito sufixos (o prefixo duplicado é do extrator) | Atributos |
| Rótulo | `Label`, em texto (`NonDoH`, `DoH`, `Benign`, `Malicious`), nos CSVs de `Total_CSVs.zip`; `DoH` booleano nos CSVs por navegador e por ferramenta | Alvo |

1 + 4 + 8 + 8 + 8 = 29 atributos numéricos, o que bate com os "29 features" do artigo. A página do dataset fala em 28 (F1 a F28) porque não numera a duração.

### Riscos de vazamento específicos destes dados

- **IPs e portas.** No DoHLyzer, um fluxo é rotulado DoH se o IP de origem ou destino está numa lista de resolvedores (`is_doh`). O IP de destino determina o rótulo da camada 1 por construção. Usar `DestinationIP` como atributo seria aprender a regra de rotulagem.
- **`TimeStamp`.** As classes foram capturadas em sessões diferentes; o horário separa as classes sem dizer nada sobre o tráfego.
- **Fluxos da mesma sessão nos dois lados do split.** O split aleatório por fluxo põe em treino e teste fluxos consecutivos da mesma captura, quase idênticos. Um split por grupo (IP de origem, janela de tempo) mede generalização de forma mais honesta. Isso é variante de avaliação, não parte da reprodução fiel.
- **Poucas máquinas.** O tráfego vem de um testbed pequeno. Atributos como duração podem refletir a configuração da captura (tempo limite do extrator, script de navegação) e não o comportamento do protocolo. A importância dominante de `Duration` no SHAP deve ser lida com essa ressalva.

## 2. Requisitos do segundo dataset

A especificação pede resultados "do sistema proposto no artigo" em "outro conjunto de dados", com justificativa. Critérios que a equipe deve usar para escolher:

1. Mesmo problema: tráfego DoH com classes compatíveis com Non-DoH, Benign-DoH e Malicious-DoH.
2. Mesmos 29 atributos, ou PCAPs dos quais o DoHLyzer consiga extraí-los.
3. Diferença relevante em relação ao CIRA (outras ferramentas, outra rede, outro período), para que o resultado diga algo sobre generalização.
4. Licença que permita o uso, e download que caiba no prazo.

## 3. Candidatos (fontes externas à bibliografia da disciplina)

### DoH-Tunnel-Traffic-HKD

- Repositório: https://github.com/doh-traffic-dataset/DoH-Tunnel-Traffic-HKD
- Download: https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/88092 (`DoH-Tunnel-Traffic-HKD.zip`, PCAPs e CSVs) A página lista dois arquivos, de 209 MB e 485 MB, com a nota "rights Reserved". Baixados em 07/10/2026; conteúdo, tamanhos e SHA-256 em [08-inventario-dados.md](08-inventario-dados.md). Condições de uso: a página diz "rights Reserved" e o README do dataset pede a citação abaixo; os dados ficam fora do Git e são citados.
- Citação exigida: R. Mitsuhashi, Y. Jin, K. Iida, T. Shinagawa and Y. Takai, "Malicious DNS Tunnel Tool Recognition Using Persistent DoH Traffic Analysis," IEEE Trans. Netw. Service Manag., vol. 20, no. 2, pp. 2086-2095, June 2023, doi: 10.1109/TNSM.2022.3215681. Conferida no Crossref em 07/10/2026. O README do dataset cita o ano de 2022, que é o do acesso antecipado; o fascículo é de junho de 2023.
- Conteúdo: túneis DoH de três ferramentas ausentes do CIRA.

| Ferramenta | Fluxos | Observação |
| --- | --- | --- |
| dnstt | 46.080 | DoH nativo |
| tcp-over-dns | 30.040 | Precisa de proxy DoH |
| tuns | 29.040 | Precisa de proxy DoH |

- Atributos extraídos com DoHLyzer, e as colunas coincidem: mesmas 35, mesmos nomes, mesma ordem (verificado).
- Limitações: só tráfego malicioso. O arquivo `Total-48h-Augmentation.csv` é o `Total-48h.csv` (5.258 fluxos) com cada linha repetida 20 vezes; as contagens da tabela acima são as do arquivo replicado. O projeto usa os 5.258 fluxos distintos, e o combinado é avaliado também sem as réplicas.

### CIRA-CIC-DoHBrw-2020-and-DoH-Tunnel-Traffic-HKD (combinado)

- Repositório: https://github.com/doh-traffic-dataset/CIRA-CIC-DoHBrw-2020-and-DoH-Tunnel-Traffic-HKD
- Arquivos: `l1-total-add.csv` (Non-DoH 897.493, DoH 374.803), `l2-total-add.csv` (DoH normal 19.807, DoH suspeito 354.996), `l3-total-add.csv` (por ferramenta).
- Tem as três classes, mas Non-DoH e Benign-DoH são os mesmos do CIRA. Só a classe maliciosa ganha tráfego novo.

### Avaliação dos dois

| Critério | HKD puro | Combinado |
| --- | --- | --- |
| Três classes | Não | Sim |
| Atributos compatíveis | Esperado | Esperado |
| Tráfego novo | Todo | Só parte dos maliciosos |
| Conta como "outro conjunto de dados"? | Sim, mas só mede recall de malicioso | Discutível: dois terços das classes são o dataset original |

Desenho que aproveita os dois e é fácil de justificar: treinar no CIRA e testar nos fluxos do HKD (ferramentas nunca vistas), e em seguida retreinar e avaliar no combinado. O primeiro mede generalização para ferramentas novas; o segundo cumpre o "sistema proposto em outro dataset" com as três classes. Se o professor não aceitar o combinado como outro dataset, precisamos de uma alternativa com Non-DoH e Benign-DoH próprios.

### Alternativa com tráfego benigno próprio

- "Collection of datasets with DNS over HTTPS traffic" (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9168479/). Apareceu na busca e ainda não foi lido. `[A verificar: referência completa, classes disponíveis, formato, tamanho e se há tráfego malicioso]`. Provavelmente exigiria rodar o DoHLyzer sobre os PCAPs, o que aumenta bastante o custo.

### Descartado

- `endgameinc/dga_predict`: classifica nomes de domínio com LSTM. Sob DoH o nome trafega cifrado e o sistema do artigo consome estatísticas de fluxo. Não é comparável.

## 4. Organização no repositório

```
data/
├── README.md        # origem, citação e hash de cada arquivo
├── manifest.json    # nome, tamanho, linhas, SHA-256 e obrigatoriedade de cada arquivo
├── verify.py        # confere os arquivos contra o manifesto
├── raw/             # fora do Git
└── processed/       # fora do Git; gerado por script a partir de raw/
```

Todo arquivo em `raw/` tem SHA-256 registrado em `data/manifest.json`; o `data/README.md` traz origem, citação e como obter. Nada em `processed/` é editado à mão.
