# 04. Dados

> Os dados foram baixados e conferidos em 07/10/2026. O que foi medido nos arquivos está em [08-inventario-dados.md](08-inventario-dados.md) e prevalece sobre as estimativas e os `[A verificar]` deste documento.
>
> Atualizado em 08/10/2026, no commit `759ec29`: a carga, a limpeza, o split e o segundo dataset foram implementados e executados. Os números por script versionado estão em `project/results/e0/dados/RESUMO.md` (CIRA) e `project/results/e6/dados/RESUMO.md` (HKD e combinado); são eles que valem para o relatório.

## 1. CIRA-CIC-DoHBrw-2020 (dataset do artigo)

- Página: https://www.unb.ca/cic/datasets/dohbrw-2020.html
- Download: http://cicresearch.ca/CICDataset/DoHBrw-2020/ (a página pede preenchimento de formulário; não foi possível listar os arquivos automaticamente) Verificado: três zips, com MD5 do CIC conferido; a fonte é `Total_CSVs.zip` (ver [08-inventario-dados.md](08-inventario-dados.md)).
- Citação exigida pelos mantenedores, como registrada aqui e em `project/data/README.md`: M. MontazeriShatoori, L. Davidson, G. Kaur and A. H. Lashkari, "Detection of DoH Tunnels using Time-series Classification of Encrypted Traffic," IEEE Cyber Science and Technology Congress, 2020.
- **Divergência na citação, a resolver.** A lista de referências do artigo de Zebin et al. traz o mesmo trabalho, na referência [14], com outro nome de evento e com páginas: "in *2020 IEEE Intl Conf on Dependable, Autonomic and Secure Computing*, 2020, pp. 63–70" (manuscrito aceito, página 11). O relatório (`project/report/relatorio.tex`, `\bibitem{montazeri2020}`) seguiu a forma do artigo. As duas ficam registradas; nenhuma foi conferida na fonte original. **Confirmar no IEEE Xplore** o nome do evento, as páginas e o DOI antes da entrega, e corrigir o arquivo que estiver errado.
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

Refeito por script versionado (`project/scripts/e0_dados.py`, resultado em `project/results/e0/dados/RESUMO.md`): a regra "NaN" dá diferença zero para a Tabela I nas três classes. Quatro regras empatam com diferença zero (NaN; NaN e infinito; NaN e duplicatas exatas; NaN, infinito e duplicatas exatas), porque o conjunto não tem infinito nem duplicata exata nas 35 colunas. A adotada é a mais simples: remover as linhas com NaN em algum dos 29 atributos, e só isso (`data.clean_flows`). Os NaN estão em `ResponseTimeTimeMedian` e `ResponseTimeTimeSkewFromMedian`, 8.028 linhas em cada.

### Split implícito no artigo

Deduzido das somas da Figura 4, não do texto:

| Classe | Treino (90%) | Teste (10%) |
| --- | --- | --- |
| Non-DoH | 800.829 | 88.980 |
| Benign-DoH | 17.771 | 1.975 |
| Malicious-DoH | 224.598 | 24.955 |
| Total | 1.043.198 | 115.910 |

Subconjuntos balanceados, pela descrição da seção III-B: cada um recebe um terço do Non-DoH de treino (266.943), os 224.598 maliciosos e a classe benigna aumentada por SMOTE. Se o benigno for aumentado até o tamanho do malicioso, 17.771 de 224.598 amostras são reais, ou seja, cerca de 92% da classe benigna de cada subconjunto é sintética. Esse percentual era estimativa nossa a partir da razão declarada; o artigo não dá o número. Medido na reprodução: os três subconjuntos têm 266.943, 266.943 e 266.942 de Non-DoH, 224.598 de Benign-DoH e 224.598 de Malicious-DoH, razão 14,3:12,0:12,0, com 92,09% de Benign-DoH sintético (`project/results/e1/fiel/RESUMO.md`, "Subconjuntos de treino").

### Split e conjunto limpo, como medidos

Fonte: `project/results/e0/dados/RESUMO.md` (seed 42, `test_size=0.1`, estratificado). O detalhe e as consequências estão em [08-inventario-dados.md](08-inventario-dados.md), seção 3.

| Medida | Valor |
| --- | --- |
| Treino, por classe (Non-DoH, Benign-DoH, Malicious-DoH) | 800.828 / 17.771 / 224.598, total 1.043.197 |
| Teste, por classe | 88.981 / 1.975 / 24.955, total 115.911 |
| Diferença para a Fig. 4 | uma amostra de Non-DoH: uma a menos no treino, uma a mais no teste; Benign-DoH e Malicious-DoH batem |
| Validação | cruzada, 10 folds estratificados dentro do treino; por fold, de 80.082 a 80.083 de Non-DoH, 1.777 ou 1.778 de Benign-DoH, 22.459 ou 22.460 de Malicious-DoH |
| Linhas do teste com vetor de 29 atributos presente no treino | 15.842 de 115.911 (13,67%) |
| A mesma medida por classe | Non-DoH 15.733 de 88.981 (17,68%); Benign-DoH 107 de 1.975 (5,42%); Malicious-DoH 2 de 24.955 (0,01%) |
| Dessas, com o vetor no treino sob outro rótulo | Non-DoH 2.358; Benign-DoH 48; Malicious-DoH 0 |
| Valores do teste normalizado fora de [0, 1] | 3 valores em 3 linhas (`FlowSentRate`, `PacketLengthMean`, `ResponseTimeTimeCoefficientofVariation`, um em cada) |
| Dias de captura | 13 dias para Non-DoH e para Benign-DoH (09/12/2019 a 14/01/2020); 15 dias para Malicious-DoH (18/03/2020 a 01/04/2020); nenhum dia e nenhuma máquina em comum entre a classe maliciosa e as outras |

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
- **Fluxos da mesma sessão nos dois lados do split.** O split aleatório por fluxo põe em treino e teste fluxos consecutivos da mesma captura, quase idênticos. Um split por grupo (IP de origem, janela de tempo) mede generalização de forma mais honesta. Isso é variante de avaliação, não parte da reprodução fiel. Foi medido no protocolo corrigido, com quatro dobras por máquina local e o teste sem os vetores repetidos do treino: `project/results/e4/corrigida/RESUMO.md`, seções "Teste sem vetores repetidos do treino" e "Avaliação por máquina".
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
- **Colunas iguais não garantem valores comparáveis: `PacketLengthMode`.** Fato medido nos conjuntos limpos inteiros (`project/results/e6/dados/RESUMO.md`, seção "`PacketLengthMode` no CIRA e no HKD"; números em `project/results/e6/dados/hkd/seed42/metrics.json`):

| Origem e classe | Fluxos | Valores distintos | Valores mais frequentes (fração dos fluxos) |
| --- | --- | --- | --- |
| CIRA, Non-DoH | 889.809 | 237 | 54 (33,57%), 66 (28,09%), 55 (22,63%), 1514 (5,56%), 60 (3,18%) |
| CIRA, Benign-DoH | 19.746 | 14 | 66 (50,70%), 105 (22,12%), 54 (12,21%), 60 (7,95%), 74 (2,03%) |
| CIRA, Malicious-DoH | 249.553 | 20 | 68 (88,09%), 56 (7,56%), 62 (2,20%), 87 (1,99%), 165 (0,10%) |
| HKD, Malicious-DoH | 5.258 | 2 | 66 (99,90%), 285 (0,10%) |

  No CIRA, a regra de um só atributo "malicioso se `PacketLengthMode` está em {56, 62, 68, 87}" tem recall de 99,84% sobre os 249.553 fluxos Malicious-DoH e 1 falso positivo em 909.555 fluxos legítimos, medida no mesmo conjunto de onde os valores foram tirados (descreve os dados; não é modelo avaliado em teste). Nos 5.258 fluxos do HKD ela detecta 0. Os limites que definem a regra (ao menos 1% dos maliciosos, no máximo 0,01% dos legítimos) são escolha nossa, em `config.py`. A causa da diferença entre as capturas não foi medida; o resumo a registra como hipótese.

### CIRA-CIC-DoHBrw-2020-and-DoH-Tunnel-Traffic-HKD (combinado)

- Repositório: https://github.com/doh-traffic-dataset/CIRA-CIC-DoHBrw-2020-and-DoH-Tunnel-Traffic-HKD
- Arquivos: `l1-total-add.csv` (Non-DoH 897.493, DoH 374.803), `l2-total-add.csv` (DoH normal 19.807, DoH suspeito 354.996), `l3-total-add.csv` (por ferramenta).
- Tem as três classes, mas Non-DoH e Benign-DoH são os mesmos do CIRA. Só a classe maliciosa ganha tráfego novo.

### Avaliação dos dois

| Critério | HKD puro | Combinado |
| --- | --- | --- |
| Três classes | Não | Sim |
| Atributos compatíveis | Verificado: 35 colunas, mesmos nomes e ordem (`project/results/e6/dados/RESUMO.md`) | Verificado, idem |
| Tráfego novo | Todo | Só parte dos maliciosos |
| Conta como "outro conjunto de dados"? | Sim, mas só mede recall de malicioso | Discutível: dois terços das classes são o dataset original |

Desenho que aproveita os dois e é fácil de justificar: treinar no CIRA e testar nos fluxos do HKD (ferramentas nunca vistas), e em seguida retreinar e avaliar no combinado. O primeiro mede generalização para ferramentas novas; o segundo cumpre o "sistema proposto em outro dataset" com as três classes. Se o professor não aceitar o combinado como outro dataset, precisamos de uma alternativa com Non-DoH e Benign-DoH próprios.

**O que foi decidido e feito.** O professor respondeu a Q4 em 07/10/2026 ("fazer tudo novamente com outro dataset não usado no trabalho") sem comentar as duas ressalvas enviadas (Non-DoH e Benign-DoH iguais aos do CIRA; réplicas). A equipe fixou (decisões 36 e 47): o dataset principal de P2 é o combinado **sem réplicas**, 1.164.366 fluxos depois da limpeza (889.809 / 19.746 / 254.811), em que tudo o que P1 produz é refeito; o combinado como publicado (1.264.268 fluxos) e a transferência para o HKD ficam como análises ao lado. A justificativa escrita está em `project/results/e6/dados/RESUMO.md`, seção "Justificativa da escolha do segundo dataset"; os resultados, em `project/results/e6/RESUMO.md`. A ressalva de que o segundo dataset só difere do primeiro na classe maliciosa continua em aberto com o professor ([07-pendencias.md](07-pendencias.md)).

### Alternativa com tráfego benigno próprio

- "Collection of datasets with DNS over HTTPS traffic" (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9168479/). Apareceu na busca e ainda não foi lido. `[A verificar: referência completa, classes disponíveis, formato, tamanho e se há tráfego malicioso]`. Provavelmente exigiria rodar o DoHLyzer sobre os PCAPs, o que aumenta bastante o custo. Não foi usado: só seria retomado se o professor recusar o combinado como "outro conjunto de dados".

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

Os caminhos são relativos a `project/`. Os arquivos que o projeto lê em `raw/` têm SHA-256 registrado em `data/manifest.json` (oito entradas: os três zips do CIRA, os dois CSVs do HKD e os três do combinado); o `data/README.md` traz origem, citação e como obter. Nada em `processed/` é editado à mão.

Em disco, `data/raw/cira/` tem os três zips, os três `.md5` do CIC e também pastas extraídas (`CSVs/`, `CSVs 2/`, `Total_CSVs/`). As pastas extraídas **não são fonte**: a carga lê direto dos zips (`Total_CSVs.zip` e `MaliciousDoH-CSVs.zip`), a integridade conferida é a do zip, e elas não estão no manifesto. O mesmo vale para `hkd/DoH-Pcaps/` e para os CSVs por ferramenta e por hora do HKD.

`processed/` é gerado por `scripts/e0_dados.py` (`cira.parquet`, com os 29 atributos, `label` e `group`) e por `scripts/e6_dados.py` (`hkd.parquet`, `combinado.parquet` e `combinado_sem_replicas.parquet`, com os 29 atributos, `label`, `origin` e `tool`). O SHA-256 de cada Parquet está no resumo do experimento que o gera.
