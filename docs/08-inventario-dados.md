# 08. Inventário dos dados baixados

O que existe em `project/data/raw/`, conferido arquivo a arquivo em 07/10/2026. Tudo aqui foi medido nos arquivos; nada vem de README de terceiros sem conferência. Onde este documento e [04-dados.md](04-dados.md) divergirem, vale este.

Como foi medido: leitura com pandas 3.0.6 em ambiente descartável, direto dos zips, sem extrair. Os scripts de análise ficaram fora do repositório; a tarefa 04 refaz as contagens por script versionado, e são esses os números que vão para o relatório.

## 1. Arquivos e integridade

| Arquivo | Tamanho (bytes) | SHA-256 | Uso |
| --- | --- | --- | --- |
| `cira/Total_CSVs.zip` | 309.971.509 | `6f939eff75dfc05b192cf1392df582c77bfa08065836226cba7c35d42d806b41` | **Fonte do CIRA** |
| `cira/BenignDoH-NonDoH-CSVs.zip` | 368.599.172 | `2e86a58edc88137320df51b4aa607119022a3e0cb8313d634b851b71ae3c0f0a` | Só se for preciso separar por navegador |
| `cira/MaliciousDoH-CSVs.zip` | 132.326.153 | `a4b3e546a9a4b9d307af6bf86d5bd60ba14db110ebd09e27b9da524c6b55deb1` | Rótulo de ferramenta (tarefa 21) |
| `combinado/l1-total-add.csv` | 550.693.495 | `5d63812bbb59814b164134ad076d35d8203f2ada5269fbf7b2a99c726bdae1c1` | Non-DoH do combinado |
| `combinado/l2-total-add.csv` | 128.339.584 | `29fb3026da5579ebebeb0b0083aadb9cd8e347367a7f9defba86d91d917365f9` | Benign-DoH do combinado |
| `combinado/l3-total-add.csv` | 145.676.121 | `0fb59f6ce896907880ddeca2a0f206b8226883d189370cb2071e0a7d11acff94` | Malicious-DoH do combinado, com a ferramenta |
| `hkd/DoH-CSVs/DoH-CSVs-48h/Total-48h.csv` | 1.877.058 | `f587d696e2fea253730aef22a9a92a01d15882acf1379af24da13edff10a710a` | **Fonte do HKD** (fluxos únicos) |
| `hkd/Total-48h-Augmentation.csv` | 37.441.530 | `c7dd2a03af0bd2c7f5739931eb30b91d41ff8a57340d0017369b6824bc87ae26` | Não usar como conjunto de avaliação (seção 4) |

- Os três zips do CIRA vieram com arquivos `.md5` do próprio CIC, e os três conferem. Os `.md5` citam os nomes originais no servidor (`DoH_Dataset_CSVs.zip`, `DoHBenign-NonDoH-CSVs.zip`, `Mal-CSVs.zip`); os arquivos foram renomeados no download.
- `hkd/DoH-Pcaps/` tem 765 MB de PCAPs. Não são usados. Ficam em `data/raw/`, fora do Git.
- `hkd/DoH-CSVs/` tem ainda um CSV por ferramenta em `DoH-CSVs-48h/` e 48 CSVs horários por ferramenta. Não são usados: `Total-48h.csv` já os reúne.

## 2. Esquema comum

Todos os CSVs de atributos têm as mesmas 35 colunas, na mesma ordem: os 5 identificadores, os 29 atributos e o rótulo. Os nomes são exatamente os lidos do código do DoHLyzer e listados em [04-dados.md](04-dados.md): nenhuma diferença de grafia.

| Arquivo | Coluna de rótulo | Valores |
| --- | --- | --- |
| `Total_CSVs.zip` → `l1-doh.csv`, `l1-nondoh.csv` | `Label` | `DoH`, `NonDoH` |
| `Total_CSVs.zip` → `l2-benign.csv`, `l2-malicious.csv` | `Label` | `Benign`, `Malicious` |
| `BenignDoH-NonDoH-CSVs.zip` e `MaliciousDoH-CSVs.zip` → `CSVs/<nome>/all.csv` | `DoH` (booleano), sem `Label` | `True`, `False` |
| `combinado/l1`, `l2`, `l3` | `Label` | `NonDoH`/`DoH`; `Benign`/`Malicious`; nome da ferramenta |
| HKD | `Label` | `dnstt`, `tcp-over-dns`, `tuns` |

Diferenças de formato que quebram a leitura se ignoradas:

| Item | CIRA (zips) | Combinado e HKD |
| --- | --- | --- |
| Codificação | UTF-8 | UTF-8 **com BOM**: ler com `encoding="utf-8-sig"`, senão a primeira coluna vira `﻿SourceIP` |
| `TimeStamp` | `2020-01-14 15:49:11`, com segundos | `2020/1/14 15:49`, sem segundos e sem zero à esquerda |
| Precisão numérica | até cerca de 28 casas | arredondada para 8 casas (em `l2`, de 5 a 8), com espaço depois do número em `l3` |

Os 29 atributos são lidos como numéricos em todos os arquivos, sem conversão manual.

## 3. CIRA-CIC-DoHBrw-2020

### Composição

| Membro do zip | Linhas | Rótulo |
| --- | --- | --- |
| `l1-nondoh.csv` | 897.493 | NonDoH |
| `l1-doh.csv` | 269.643 | DoH |
| `l2-benign.csv` | 19.807 | Benign |
| `l2-malicious.csv` | 249.836 | Malicious |

- `l1-doh.csv` é exatamente a união de `l2-benign.csv` e `l2-malicious.csv` (mesmo multiconjunto de linhas, conferido por hash). **O conjunto de três classes é `l1-nondoh` + `l2-benign` + `l2-malicious`. Ler também `l1-doh` contaria o DoH em dobro.**
- Total bruto: 1.167.136 fluxos. As contagens por classe são as que o README do combinado informava; agora estão confirmadas na fonte.
- Por ferramenta, nos `all.csv` do zip de maliciosos (linhas com `DoH == True`): dns2tcp 167.486, dnscat2 35.770, iodine 46.580. Soma 249.836. Esses arquivos têm também linhas com `DoH == False` (31, 84 e 18), que não entram.
- Por navegador, linhas com `DoH == True`: Chrome 3.534, Firefox 16.273. Soma 19.807.

### Limpeza: a Tabela I está reproduzida

| Regra | Non-DoH | Benign-DoH | Malicious-DoH |
| --- | --- | --- | --- |
| Bruto | 897.493 | 19.807 | 249.836 |
| **Remover linhas com NaN** | **889.809** | **19.746** | **249.553** |
| Tabela I do artigo | 889.809 | 19.746 | 249.553 |
| Remover duplicatas exatas (35 colunas) | 897.493 | 19.807 | 249.836 |
| Remover NaN e duplicatas nos 29 atributos | 750.456 | 18.797 | 249.538 |

- **Remover as linhas com NaN reproduz a Tabela I exatamente, nas três classes.** Resolve a ambiguidade A1.
- Os NaN estão em duas colunas só, `ResponseTimeTimeMedian` e `ResponseTimeTimeSkewFromMedian`, e sempre juntos: 8.028 linhas (7.684 + 61 + 283). A causa está no extrator: em fluxo sem nenhum par requisição-resposta, a mediana é calculada sobre uma lista vazia (`response_time.py`, `get_median`, sem proteção), enquanto variância, média e moda devolvem o sentinela `-1`. As linhas removidas são, portanto, os fluxos sem tempo de resposta medido.
- Não há infinitos nem duplicata exata nas 35 colunas.
- As 4.719 linhas com `Duration == 0`, que têm taxas negativas, estão todas dentro das linhas com NaN e saem com elas.
- Remover duplicatas nos 29 atributos **não** é o que os autores fizeram: derruba o Non-DoH para 750.456.

### O que sobra depois da limpeza e importa para o método

| Fato medido | Valor | Consequência |
| --- | --- | --- |
| Linhas com o mesmo vetor de 29 atributos | 139.353 em Non-DoH, 949 em Benign-DoH, 15 em Malicious-DoH | O split aleatório põe cópias em treino e teste |
| Fração do teste (seed 42) cujo vetor também está no treino | 13,7% no total; 17,7% em Non-DoH, 5,4% em Benign-DoH, 0,01% em Malicious-DoH | A métrica do teste é otimista para Non-DoH; a trilha corrigida reporta também sem essas linhas |
| Vetores de 29 atributos que aparecem em mais de uma classe | 326 | Ruído de rótulo irredutível; teto para qualquer modelo |
| Valor `-10` em colunas de assimetria | 298.766 linhas: 294.474 em `ResponseTimeTimeSkew...` (290.123 Non-DoH, 3.547 Benign-DoH, 804 Malicious-DoH) e 4.928 em `PacketLengthSkew...` (4.616 Malicious-DoH, 312 Non-DoH); nenhuma em `PacketTimeSkew...` | **É valor sentinela do extrator, confirmado em 07/10/2026**: o DoHLyzer devolve `-10` quando o desvio padrão é zero (`meter/features/packet_length.py` e `response_time.py`, métodos `get_skew` e `get_skew2`), e nos dados todo `-10` coincide com desvio padrão zero, sem exceção. Marca fluxos com no máximo um tempo de resposta: um terço do Non-DoH e 0,3% do malicioso. É um atributo binário disfarçado, que separa classes; pesa no `MinMaxScaler` e precisa de ressalva na leitura do SHAP |
| Colunas com valor negativo legítimo | as seis de assimetria | Esperado; não é erro |

### Split: uma amostra de diferença para a Fig. 4

| Conjunto | Nosso (`test_size=0.1`, estratificado, seed 42) | Fig. 4 do artigo |
| --- | --- | --- |
| Treino | 800.828 / 17.771 / 224.598 = 1.043.197 | 800.829 / 17.771 / 224.598 = 1.043.198 |
| Teste | 88.981 / 1.975 / 24.955 = 115.911 | 88.980 / 1.975 / 24.955 = 115.910 |

O scikit-learn arredonda o tamanho do teste para cima (10% de 1.159.108 é 115.910,8), o que explica o nosso 115.911. A causa do 115.910 do artigo é desconhecida: outra limpeza, outro arredondamento ou um tamanho de teste fixado. O artigo tem uma amostra de Non-DoH a menos no teste. Benign-DoH e Malicious-DoH batem exatamente. A comparação célula a célula com a Fig. 4b carrega, portanto, uma diferença mínima de 1 que não é erro de modelo.

Com 800.828 Non-DoH no treino, as três partes dos subconjuntos têm 266.943, 266.943 e 266.942 amostras.

### Máquinas e período de captura

| Classe | Máquinas locais (`192.168.20.x`) | Período |
| --- | --- | --- |
| Non-DoH | `.111`, `.112`, `.113`, `.191` | 09/12/2019 a 14/01/2020 |
| Benign-DoH | `.111`, `.112`, `.113`, `.191` | 09/12/2019 a 14/01/2020 |
| Malicious-DoH | `.144` e `.204` a `.212` (dez máquinas) | 18/03/2020 a 01/04/2020 |

- O tráfego malicioso foi capturado em **outras máquinas e dois meses depois** do benigno e do Non-DoH. Não há máquina nem dia em comum. `TimeStamp` e os IPs separam a classe maliciosa sozinhos: confirma, nos dados, por que os identificadores ficam fora do modelo.
- É também uma limitação a declarar no relatório: qualquer diferença sistemática entre as duas campanhas de captura se confunde com "ser malicioso".
- Os fluxos são bidirecionais: `SourceIP` às vezes é o resolvedor. O grupo de um fluxo é o endereço `192.168.20.x` que aparece na origem **ou** no destino, não a coluna `SourceIP`.
- Split por grupo: há só quatro máquinas para Non-DoH e Benign-DoH, e dez para Malicious-DoH. É viável em poucas dobras (deixar uma máquina de fora), não em dez.

## 4. DoH-Tunnel-Traffic-HKD

| Arquivo | Linhas | dnstt | tcp-over-dns | tuns |
| --- | --- | --- | --- | --- |
| `DoH-CSVs-48h/Total-48h.csv` | 5.258 | 2.304 | 1.502 | 1.452 |
| `Total-48h-Augmentation.csv` | 105.160 | 46.080 | 30.040 | 29.040 |

- **A "augmentation" é replicação.** O arquivo aumentado tem 5.258 linhas distintas, cada uma repetida exatamente 20 vezes (5.258 × 20 = 105.160). As contagens por ferramenta são as do `Total-48h.csv` vezes 20. O README chama isso de "augmented assuming 20 client PCs". As 5.258 linhas distintas são as do `Total-48h.csv`, confirmado em 07/10/2026: identificadores e rótulos idênticos, e maior diferença absoluta entre os 29 atributos de 5 × 10⁻⁸, que é arredondamento na oitava casa.
- Para avaliar transferência, usa-se `Total-48h.csv`: 5.258 fluxos reais. O recall por ferramenta é o mesmo nos dois arquivos, mas reportar 105.160 fluxos de teste seria inflar o tamanho da amostra por vinte.
- Sem NaN, sem infinito. Só fluxos maliciosos: três rótulos de ferramenta, nenhum negativo.
- Duas máquinas apenas (`192.168.11.12` e `192.168.11.16`), capturas de 27/10 a 04/11/2021.
- Os fluxos do HKD são muito diferentes dos maliciosos do CIRA. Medianas, HKD contra CIRA: `Duration` 120,1 s contra 34,1 s; `FlowBytesSent` 21.375 contra 1.807; `FlowBytesReceived` 21.724 contra 4.896; `PacketLengthMean` 148,6 contra 223,4. A mediana de duração colada em 120 s sugere fluxos cortados pelo tempo limite do extrator. Isso antecipa a interpretação da transferência: o modelo treinado no CIRA verá valores fora da faixa em que foi normalizado. No CIRA limpo, a mediana de `Duration` por classe é 0,31 s (Non-DoH), 4,1 s (Benign-DoH) e 34,07 s (Malicious-DoH), medida em 07/10/2026.

## 5. Combinado (CIRA + HKD)

| Arquivo | Linhas | Rótulos |
| --- | --- | --- |
| `l1-total-add.csv` | 1.272.296 | NonDoH 897.493; DoH 374.803 |
| `l2-total-add.csv` | 374.803 | Benign 19.807; Malicious 354.996 |
| `l3-total-add.csv` | 354.996 | dns2tcp 167.486; dnscat2 35.770; iodine 46.580; dnstt 46.080; tcp-over-dns 30.040; tuns 29.040 |

- As contagens batem com o README do dataset.
- Como montar as três classes: Non-DoH das linhas `NonDoH` de `l1`; Benign-DoH das linhas `Benign` de `l2`; Malicious-DoH de **todas** as linhas de `l3`, que já traz a ferramenta. Não é preciso alinhar `l2` com `l3`, e as linhas não estão na mesma ordem entre os arquivos.
- **Os 105.160 fluxos do HKD dentro do combinado são os replicados**: 5.258 distintos, cada um 20 vezes. Num split aleatório 90/10, praticamente todo fluxo do HKD no teste tem cópias idênticas no treino. O resultado do retreino para as ferramentas novas é memorização, não detecção.
- A parte do CIRA dentro do combinado não é idêntica ao CIRA original: os números foram arredondados para 8 casas e o `TimeStamp` perdeu os segundos. As mesmas 8.028 linhas têm NaN. Extrair o CIRA de dentro do combinado, que era o plano B, perderia precisão; com o CIRA original baixado, o plano B deixa de ser necessário.
- Origem de cada linha de `l3`: as três ferramentas do CIRA vêm primeiro (linhas 0 a 249.835), depois as três do HKD. O rótulo de ferramenta basta para dizer a origem.

## 6. O que isto muda no plano

| Achado | Efeito | Tarefa |
| --- | --- | --- |
| Remover NaN reproduz a Tabela I | A1 resolvida; a limpeza adotada é essa, e as outras combinações ficam só como registro | 04 |
| `l1-doh` duplica `l2` | A carga lê três membros do zip, não quatro | 04 |
| Rótulo em texto (`NonDoH`, `Benign`, `Malicious`) | O mapa para 0, 1, 2 fica em `config.py` | 02, 04 |
| Leitura direto do zip | Sem etapa de extração; a integridade é o hash do zip | 03, 04 |
| Teste com 115.911 amostras, não 115.910 | A comparação com a Fig. 4b tem diferença mínima de 1; não se força o tamanho | 05, 06, 08 |
| 13,7% do teste repetido no treino | A métrica "sem duplicatas" da trilha corrigida deixa de ser detalhe: muda o Non-DoH | 05, 11 |
| Malicioso capturado em outras máquinas e outro período | Limitação a declarar; grupo = máquina local, poucas dobras | 04, 11, 18 |
| Sentinela `-10` nas assimetrias (confirmado no extrator) | Ressalva na leitura do SHAP; contagem por classe gravada em E0 | 04, 12 |
| HKD aumentado é replicação de 20 vezes | Transferência usa `Total-48h.csv`; retreino no combinado é reportado como publicado **e** sem as réplicas | 13, 14, 15 |
| BOM e `TimeStamp` diferente no combinado e no HKD | A carga do segundo dataset trata os dois | 13 |
| HKD com duração e bytes muito maiores | Hipótese para a transferência, escrita antes de rodar | 14 |
| Rótulo de ferramenta existe | A tarefa 21 é viável com `l3` ou com o zip de maliciosos, se o professor pedir | 21 |
