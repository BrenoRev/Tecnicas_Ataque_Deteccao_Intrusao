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

# As seis colunas de assimetria. Nelas o extrator DoHLyzer grava -10 quando o
# desvio padrão é zero (métodos get_skew e get_skew2 de packet_length.py e
# response_time.py): o valor marca o fluxo, não mede assimetria.
SKEW_COLUMNS = [column for column in FEATURE_COLUMNS if "Skew" in column]
SKEW_SENTINEL = -10

# Fluxos por classe na Tabela I do artigo, na ordem de CLASS_NAMES.
TABLE_I_COUNTS = [889809, 19746, 249553]

# Alvos do artigo.

# Matrizes de confusão da Fig. 4 do artigo: (a) treino, em validação cruzada de
# 10 folds; (b) teste. Linha é a classe real e coluna a classe predita, as duas
# na ordem de CLASS_NAMES. A figura desenha as classes em outra ordem (Benign-DoH,
# Malicious-DoH, Non-DoH): as contagens foram reordenadas para a codificação do
# projeto, porque comparar matrizes em ordens diferentes dá distância errada
# sem erro aparente.
FIG4A_CONFUSION = [
    [800316, 503, 10],
    [1816, 15946, 9],
    [93, 9, 224496],
]
FIG4B_CONFUSION = [
    [88928, 50, 2],
    [192, 1782, 1],
    [6, 0, 24949],
]

# Amostras por classe no treino e no teste do artigo, na ordem de CLASS_NAMES:
# soma de cada linha das matrizes da Fig. 4a e da Fig. 4b.
FIG4_TRAIN_COUNTS = [sum(row) for row in FIG4A_CONFUSION]
FIG4_TEST_COUNTS = [sum(row) for row in FIG4B_CONFUSION]

# Tabela II do artigo, metade superior: os três modelos de comparação e o modelo
# proposto, avaliados no teste. O artigo não diz que média (macro, ponderada ou
# micro) usa em F1, precisão e recall, nem como calcula a AUC com três classes.
TABLE_II = {
    "decision_tree": {
        "auc": 0.8617,
        "accuracy": 0.9770,
        "f1": 0.8197,
        "precision": 0.9658,
        "recall": 0.7120,
    },
    "xgboost": {
        "auc": 0.9986,
        "accuracy": 0.9927,
        "f1": 0.9843,
        "precision": 0.9956,
        "recall": 0.9732,
    },
    "random_forest": {
        "auc": 0.9999,
        "accuracy": 0.9998,
        "f1": 0.9987,
        "precision": 0.9989,
        "recall": 0.9985,
    },
    "balanced_stacked_rf": {
        "auc": 0.9999,
        "accuracy": 0.9998,
        "f1": 0.9991,
        "precision": 0.9991,
        "recall": 0.9992,
    },
}

# Avaliação.

# Nível do intervalo de confiança da taxa de falsos positivos. O artigo não
# reporta intervalo: 95% é escolha nossa.
CONFIDENCE_LEVEL = 0.95

# Tamanho do tráfego em que os alarmes falsos da conta de taxa base são contados.
BASE_RATE_FLOWS = 10_000_000

# Membros de Total_CSVs.zip que formam as três classes, na ordem de CLASS_NAMES.
# O quarto membro, l1-doh.csv, é a união dos dois l2: lê-lo contaria o DoH em dobro.
CIRA_ZIP_MEMBERS = ["l1-nondoh.csv", "l2-benign.csv", "l2-malicious.csv"]

# Rede das máquinas que geraram o tráfego do CIRA-CIC-DoHBrw-2020. O endereço
# dessa rede que aparece no fluxo identifica a máquina local.
CIRA_LOCAL_PREFIX = "192.168.20."

# Hiperparâmetros da trilha fiel.

# 10% dos fluxos para teste, Seção III-B do artigo.
TEST_SIZE = 0.10

# Três subconjuntos balanceados de treino, um por Random Forest, Seção III-B.
N_SUBSETS = 3

# Razão Non-DoH : Benign-DoH : Malicious-DoH de cada subconjunto, como a Seção
# III-B do artigo a declara. A razão obtida é reportada ao lado desta.
ARTICLE_SUBSET_RATIO = [15, 12, 12]

# Validação cruzada de 10 folds sobre o treino (Seção III-B e legenda da
# Fig. 4a do artigo). O artigo não tem conjunto de validação separado e não diz
# se os folds são estratificados nem se as linhas são embaralhadas. Leitura
# adotada: folds estratificados, para a classe benigna, a menor, ter a mesma
# proporção em todos; com embaralhamento e seed, para os folds dependerem só
# da seed e não da ordem das linhas da tabela.
CV_FOLDS = 10
CV_SHUFFLE = True

# 10 árvores por Random Forest, Seção IV-A do artigo.
N_ESTIMATORS = 10

# A Seção IV-A do artigo diz que os atributos de cada divisão são "selected at
# random from 28 features". A frase admite duas leituras: 28 atributos
# candidatos em cada divisão, de 29 disponíveis, ou um modelo com 28 atributos
# no total. Adotamos a primeira, porque o Algoritmo 1 e a Seção VI-C falam em
# 29 atributos de entrada e o artigo não diz qual seria o atributo retirado.
MAX_FEATURES = 28

# O artigo traz duas passagens sobre a profundidade das árvores. A Seção IV-B
# declara profundidade máxima 5 nos submodelos; a linha 3 do Algoritmo 1 fala
# em "variable tree depth". A trilha fiel usa 5, o único valor numérico que o
# texto fornece. A leitura sem limite de profundidade, com todo o resto
# igual, é reportada como variante nomeada, porque também tem apoio no texto.
# As duas são medidas no mesmo protocolo e nenhuma foi escolhida pelo resultado.
MAX_DEPTH = 5
MAX_DEPTH_VARIABLE = None

# Núcleos usados no treino: -1 pede todos os da máquina. Não altera o
# resultado, porque cada árvore recebe a própria seed; muda só o tempo.
N_JOBS = -1

# Leitura adotada na trilha fiel em cada ponto que o artigo deixa em aberto.
# O dicionário é gravado no registro de cada execução, para o resultado dizer
# sozinho que sistema foi treinado.
FIEL_READINGS = {
    "base_estimators": "um Random Forest por subconjunto, treinado antes do empilhamento",
    "meta_training_data": "predições dos bases no treino original normalizado, sem sintéticas",
    "meta_input": "rótulo predito por cada base (use_probas=False), três entradas",
    "meta_parameters": "regressão logística com os parâmetros padrão do scikit-learn",
    "smote_target": "só Benign-DoH, aumentada até o tamanho de Malicious-DoH no subconjunto",
    "smote_parameters": "padrão do imbalanced-learn",
    "one_sided_selection": "não aplicada: o artigo a cita sem descrever",
    "class_weight": "nenhum: o artigo não menciona",
    "hyperparameter_source": "valores finais do artigo (Seções IV-A e IV-B), sem busca",
    "cross_validation": "scaler, subconjuntos, SMOTE, bases e meta refeitos em cada fold",
}

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
CIRA_ZIP_PATH = DATA_RAW_DIR / "cira" / "Total_CSVs.zip"
CIRA_PARQUET_PATH = DATA_PROCESSED_DIR / "cira.parquet"


def smote_seed(seed: int, subset_index: int) -> int:
    """Devolve a seed do SMOTE do subconjunto de índice `subset_index`.

    Cada subconjunto precisa de um sorteio próprio, e o valor não pode coincidir
    com o de outra execução: `seed * 100 + subset_index` não colide entre as
    seeds 0 a 9 e 42 com três subconjuntos. Os Random Forests e o
    meta-classificador usam `seed` diretamente.
    """
    return seed * 100 + subset_index
