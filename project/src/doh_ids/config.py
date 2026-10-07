"""Constantes do projeto: classes, colunas, hiperparâmetros, seeds e caminhos.

Todo experimento lê os valores daqui. Cada hiperparâmetro traz a seção do
artigo de onde vem; onde o artigo é omisso, o comentário diz a leitura adotada.
"""

from pathlib import Path

# Codificação das classes, na ordem usada pelo script dos autores.
# A posição na lista é o código inteiro da classe.
CLASS_NAMES = ["Non-DoH", "Benign-DoH", "Malicious-DoH"]

# Nos CSVs do CIRA-CIC-DoHBrw-2020 o rótulo vem em texto, na coluna Label.
LABEL_COLUMN = "Label"
LABEL_ENCODING = {"NonDoH": 0, "Benign": 1, "Malicious": 2}

# Identificadores do fluxo. Nunca entram no modelo: o extrator rotula o tráfego
# DoH pelo endereço IP, e as classes foram capturadas em máquinas e datas
# diferentes, de modo que essas colunas entregam o rótulo sem descrever o tráfego.
ID_COLUMNS = ["SourceIP", "DestinationIP", "SourcePort", "DestinationPort", "TimeStamp"]

# Os 29 atributos do modelo. O artigo fala em 29 atributos (Algoritmo 1 e
# Seção VI-C) mas não os lista: adotamos as 29 estatísticas numéricas do fluxo,
# com os nomes e na ordem do cabeçalho dos CSVs. O prefixo duplicado em
# ResponseTimeTime vem do extrator.
FEATURE_COLUMNS = [
    "Duration",
    "FlowBytesSent",
    "FlowSentRate",
    "FlowBytesReceived",
    "FlowReceivedRate",
    "PacketLengthVariance",
    "PacketLengthStandardDeviation",
    "PacketLengthMean",
    "PacketLengthMedian",
    "PacketLengthMode",
    "PacketLengthSkewFromMedian",
    "PacketLengthSkewFromMode",
    "PacketLengthCoefficientofVariation",
    "PacketTimeVariance",
    "PacketTimeStandardDeviation",
    "PacketTimeMean",
    "PacketTimeMedian",
    "PacketTimeMode",
    "PacketTimeSkewFromMedian",
    "PacketTimeSkewFromMode",
    "PacketTimeCoefficientofVariation",
    "ResponseTimeTimeVariance",
    "ResponseTimeTimeStandardDeviation",
    "ResponseTimeTimeMean",
    "ResponseTimeTimeMedian",
    "ResponseTimeTimeMode",
    "ResponseTimeTimeSkewFromMedian",
    "ResponseTimeTimeSkewFromMode",
    "ResponseTimeTimeCoefficientofVariation",
]

# As duas únicas colunas com valor ausente nos CSVs, sempre nas mesmas linhas:
# fluxos sem nenhum par requisição-resposta, em que o extrator não calcula a mediana.
NAN_COLUMNS = ["ResponseTimeTimeMedian", "ResponseTimeTimeSkewFromMedian"]

# Hiperparâmetros da trilha fiel.

# 10% dos fluxos para teste, Seção III-B do artigo.
TEST_SIZE = 0.10

# Três subconjuntos balanceados de treino, um por Random Forest, Seção III-B.
N_SUBSETS = 3

# 10 árvores por Random Forest, Seção IV-A do artigo.
N_ESTIMATORS = 10

# 28 atributos candidatos em cada divisão, de 29 disponíveis, Seção IV-A.
MAX_FEATURES = 28

# Profundidade máxima 5, Seção IV-B do artigo.
MAX_DEPTH = 5

# Seeds. O artigo não informa a seed. Na trilha fiel usamos 42, a que aparece
# no script publicado pelos autores. Na trilha corrigida usamos dez seeds, de
# 0 a 9, para reportar média e desvio padrão: escolha nossa, não do artigo.
SEED_FIEL = 42
SEEDS_CORRIGIDA = list(range(10))

# Trilhas aceitas no registro de resultados. As duas primeiras são a reprodução
# como o artigo descreve e o protocolo consertado; "variante" é para leituras
# alternativas do texto do artigo e "dados" para etapas que não treinam modelo.
TRACKS = ["fiel", "corrigida", "variante", "dados"]

# Caminhos. A raiz é a pasta que contém src/, descoberta a partir deste arquivo,
# para que os scripts gravem no mesmo lugar de qualquer diretório em que rodem.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"


def smote_seed(seed: int, subset_index: int) -> int:
    """Devolve a seed do SMOTE do subconjunto de índice `subset_index`.

    Cada subconjunto precisa de um sorteio próprio, e o valor não pode coincidir
    com o de outra execução: `seed * 100 + subset_index` não colide entre as
    seeds 0 a 9 e 42 com três subconjuntos. Os Random Forests e o
    meta-classificador usam `seed` diretamente.
    """
    return seed * 100 + subset_index
