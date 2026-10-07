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

# Painéis da Fig. 2 do artigo: atributo, unidade, início e fim do eixo
# horizontal e se o eixo é logarítmico. As faixas foram lidas nos eixos da
# figura; o artigo não diz como recortou os dados. A unidade vem do extrator
# DoHLyzer, que mede o comprimento do pacote em bytes.
FIG2_PANELS = [
    ("FlowBytesReceived", "bytes", 0, 17500, False),
    ("PacketLengthMean", "bytes", 0, 800, False),
    ("PacketLengthVariance", "bytes²", 10, 1_000_000, True),
]
# Pontos do eixo horizontal em que cada curva da Fig. 2 é calculada.
FIG2_GRID_POINTS = 400

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

# Tabela II do artigo, metade inferior ("Comparison with literature"): resultados
# de outros trabalhos sobre o mesmo dataset, que o artigo copia das referências
# [10] (Banadaki), [12] (Jafar et al.) e [22] (Ahakonye et al.) da sua lista.
# Os valores estão como impressos na tabela, na ordem das linhas. `None` marca a
# célula que o artigo imprime como "–". As sete primeiras linhas estão impressas
# como fração, entre 0 e 1; a última, Random Forest [22], está impressa em
# percentual (99.5, 99.4 e 99.6), e `percent` diz a escala de cada linha. O
# artigo declara que o método experimental desses trabalhos não é diretamente
# comparável ao dele (Seção V).
TABLE_II_LITERATURE = [
    {
        "model": "Decision Tree",
        "reference": "[10]",
        "auc": 0.998,
        "accuracy": 0.998,
        "f1": 0.998,
        "precision": 0.998,
        "recall": 0.999,
        "percent": False,
    },
    {
        "model": "Gradient Boosting(XGB)",
        "reference": "[10]",
        "auc": 1,
        "accuracy": 0.999,
        "f1": 1,
        "precision": 1,
        "recall": 1,
        "percent": False,
    },
    {
        "model": "Random Forest",
        "reference": "[10]",
        "auc": 1,
        "accuracy": 0.998,
        "f1": 0.997,
        "precision": 0.999,
        "recall": 0.998,
        "percent": False,
    },
    {
        "model": "Decision Tree",
        "reference": "[12]",
        "auc": None,
        "accuracy": 0.999715,
        "f1": None,
        "precision": None,
        "recall": None,
        "percent": False,
    },
    {
        "model": "Random Forest",
        "reference": "[12]",
        "auc": None,
        "accuracy": 0.999802,
        "f1": None,
        "precision": None,
        "recall": None,
        "percent": False,
    },
    {
        "model": "Decision Tree",
        "reference": "[22]",
        "auc": None,
        "accuracy": 0.993,
        "f1": None,
        "precision": 0.992,
        "recall": 0.993,
        "percent": False,
    },
    {
        "model": "Gradient Boosting(XGB)",
        "reference": "[22]",
        "auc": None,
        "accuracy": 0.951,
        "f1": None,
        "precision": 0.957,
        "recall": 0.951,
        "percent": False,
    },
    {
        "model": "Random Forest",
        "reference": "[22]",
        "auc": None,
        "accuracy": 99.5,
        "f1": None,
        "precision": 99.4,
        "recall": 99.6,
        "percent": True,
    },
]

# Avaliação.

# Nível do intervalo de confiança da taxa de falsos positivos. O artigo não
# reporta intervalo: 95% é escolha nossa.
CONFIDENCE_LEVEL = 0.95

# Tamanho do tráfego em que os alarmes falsos da conta de taxa base são contados.
BASE_RATE_FLOWS = 10_000_000

# Diferença, em pontos percentuais, a partir da qual um modelo de comparação é
# destacado como muito acima da sua linha na Tabela II. Escolha nossa: 5 pontos
# estão longe do que a seed ou a versão de uma biblioteca muda em um modelo
# com os mesmos hiperparâmetros.
TABLE_II_FAR_ABOVE_PP = 5.0

# Membros de Total_CSVs.zip que formam as três classes, na ordem de CLASS_NAMES.
# O quarto membro, l1-doh.csv, é a união dos dois l2: lê-lo contaria o DoH em dobro.
CIRA_ZIP_MEMBERS = ["l1-nondoh.csv", "l2-benign.csv", "l2-malicious.csv"]

# Rede das máquinas que geraram o tráfego do CIRA-CIC-DoHBrw-2020. O endereço
# dessa rede que aparece no fluxo identifica a máquina local.
CIRA_LOCAL_PREFIX = "192.168.20."

# Segundo dataset: DoH-Tunnel-Traffic-HKD e o combinado CIRA + HKD.

# Os CSVs do HKD e parte dos do combinado começam com a marca de ordem de bytes
# (BOM). Lida como UTF-8 comum, a marca fica colada ao nome da primeira coluna;
# esta codificação a descarta e lê do mesmo jeito o arquivo que não a tem.
SECOND_DATASET_ENCODING = "utf-8-sig"

# Conjunto de origem de cada fluxo do segundo dataset.
ORIGINS = ["CIRA", "HKD"]

# Ferramenta de túnel que gerou o fluxo malicioso e o conjunto de onde ela vem.
# No combinado, o arquivo de nível 3 traz a ferramenta na coluna Label, e ela
# basta para dizer a origem: as três primeiras são do CIRA-CIC-DoHBrw-2020 e as
# três últimas, do DoH-Tunnel-Traffic-HKD.
TOOL_ORIGIN = {
    "dns2tcp": "CIRA",
    "dnscat2": "CIRA",
    "iodine": "CIRA",
    "dnstt": "HKD",
    "tcp-over-dns": "HKD",
    "tuns": "HKD",
}

# Rótulos em texto, nos arquivos de nível 1 e 2 do combinado, das duas classes
# sem ferramenta de túnel. Os outros rótulos desses arquivos, DoH e Malicious,
# não são lidos: os fluxos maliciosos vêm todos do arquivo de nível 3.
COMBINED_NON_DOH_LABEL = "NonDoH"
COMBINED_BENIGN_LABEL = "Benign"

# Colunas das tabelas do segundo dataset: os atributos, o rótulo, o conjunto de
# origem e a ferramenta de túnel, que fica vazia fora da classe maliciosa.
SECOND_DATASET_COLUMNS = FEATURE_COLUMNS + ["label", "origin", "tool"]

# Vezes que cada fluxo do HKD aparece em Total-48h-Augmentation.csv e no
# combinado. O README do HKD descreve o arquivo como "augmented assuming 20
# client PCs"; a contagem é conferida nos dados pelo script que os prepara.
HKD_REPLICAS = 20

# Maior diferença aceita, em um atributo, entre um fluxo de Total-48h.csv e a
# cópia dele nos arquivos replicados, que gravam os números arredondados.
HKD_ROUNDING_TOLERANCE = 1e-7

# Fluxos por classe do combinado, na ordem de CLASS_NAMES, e por ferramenta,
# como o README.txt do dataset combinado os informa.
README_CLASS_ROWS = [897493, 19807, 354996]
README_TOOL_ROWS = {
    "dns2tcp": 167486,
    "dnscat2": 35770,
    "iodine": 46580,
    "dnstt": 46080,
    "tcp-over-dns": 30040,
    "tuns": 29040,
}

# Comparação de um atributo entre o CIRA e o HKD: quantos dos valores mais
# frequentes de cada classe e origem são gravados.
TOP_VALUES_SHOWN = 5

# Regra de um só atributo, usada para medir quanto um atributo sozinho separa
# o tráfego malicioso do CIRA: ficam na regra os valores que cobrem ao menos 1%
# dos fluxos Malicious-DoH do CIRA e no máximo 0,01% dos fluxos legítimos
# (Non-DoH e Benign-DoH). Os dois limites são escolha nossa, para a regra não
# depender de valor que aparece em poucos fluxos.
RULE_MIN_MALICIOUS_FRACTION = 0.01
RULE_MAX_LEGITIMATE_FRACTION = 0.0001

# Recall de uma ferramenta de túnel abaixo do qual ele é descrito como perto
# de zero. Escolha nossa: 1%.
NEAR_ZERO_RECALL = 0.01

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

# Modelos de comparação da Tabela II do artigo: a árvore de decisão tem
# profundidade máxima 10 ("Tree Depth=10") e o Random Forest tem 10 árvores
# ("number of Trees=10"). São os únicos hiperparâmetros que a tabela informa;
# o XGBoost não tem nenhum.
TABLE_II_TREE_DEPTH = 10
TABLE_II_FOREST_TREES = 10

# Núcleos usados no treino: -1 pede todos os da máquina. Não altera o
# resultado, porque cada árvore recebe a própria seed; muda só o tempo.
N_JOBS = -1

# Explicabilidade (Seção VI do artigo).

# O artigo não diz quantos fluxos entram no cálculo dos valores SHAP: a Fig. 5
# fala em "training data" e a Fig. 6 em "all the observations of the test set".
# Usamos uma amostra de até 2.000 fluxos por classe, uma do treino e uma do
# teste: escolha nossa, para o cálculo sobre árvores sem limite de profundidade
# caber em minutos. A amostra tem as três classes em partes iguais, e a
# importância média pesa cada classe por igual, não na proporção do tráfego.
SHAP_SAMPLE_PER_CLASS = 2000

# Atributos do topo de cada ranking comparados entre os três submodelos.
SHAP_TOP_FEATURES = 10

# O artigo não diz qual modelo o TreeExplainer explica (linha 8 do Algoritmo
# 1), e o SHAP não aceita o modelo empilhado. As figuras e o painel explicam o
# Random Forest do primeiro subconjunto; a tabela de importância traz os três.
EXPLAINED_BASE = 0

# Limiar de duração, em segundos, que a legenda da Fig. 6 do artigo atribui ao
# modelo para o tráfego malicioso.
ARTICLE_DURATION_THRESHOLD_SECONDS = 40

# Tolerância da conferência de que o valor base mais a soma dos valores SHAP
# reproduz a probabilidade do modelo.
ADDITIVITY_TOLERANCE = 1e-6

# Ordem dos 29 atributos na Fig. 5 do artigo, do mais para o menos importante,
# lida dos rótulos do eixo vertical da figura.
FIG5_RANKING = [
    "Duration",
    "PacketLengthMode",
    "PacketTimeVariance",
    "PacketLengthCoefficientofVariation",
    "PacketLengthVariance",
    "PacketLengthMean",
    "FlowBytesSent",
    "PacketTimeMean",
    "ResponseTimeTimeMedian",
    "FlowBytesReceived",
    "PacketLengthStandardDeviation",
    "PacketLengthMedian",
    "PacketTimeMedian",
    "PacketLengthSkewFromMode",
    "PacketTimeCoefficientofVariation",
    "PacketLengthSkewFromMedian",
    "PacketTimeSkewFromMode",
    "FlowReceivedRate",
    "PacketTimeSkewFromMedian",
    "PacketTimeStandardDeviation",
    "PacketTimeMode",
    "FlowSentRate",
    "ResponseTimeTimeCoefficientofVariation",
    "ResponseTimeTimeVariance",
    "ResponseTimeTimeSkewFromMedian",
    "ResponseTimeTimeMean",
    "ResponseTimeTimeMode",
    "ResponseTimeTimeSkewFromMode",
    "ResponseTimeTimeStandardDeviation",
]

# Figs. 7 e 8 do artigo, lidas das telas do painel: a classe explicada, a
# probabilidade predita, a média da população e o atributo de maior
# contribuição, com o valor dele no fluxo e o efeito. Probabilidade, média e
# efeito em pontos percentuais. A legenda da Fig. 8 fala em 86,1% de confiança; a
# tela mostra 88,85%, que é o valor registrado aqui.
FIG7_MALICIOUS = {
    "class_name": "Malicious-DoH",
    "prediction": 76.4,
    "population_average": 33.31,
    "top_feature": "Duration",
    "top_value": 120.817079,
    "top_effect": 14.68,
}
FIG8_NON_DOH = {
    "class_name": "Non-DoH",
    "prediction": 88.85,
    "population_average": 33.33,
    "top_feature": "PacketLengthVariance",
    "top_value": 468846.35165895056,
    "top_effect": 19.15,
}

# A tabela de contribuição das Figs. 7 e 8 do artigo lista dez atributos e
# soma os demais em "Other features combined".
LOCAL_TABLE_FEATURES = 10

# Endereço do painel interativo: só a própria máquina, na porta padrão da
# biblioteca explainerdashboard.
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050

# Fluxos por classe na amostra do teste que o painel explica. A versão 0.5.8 do
# explainerdashboard só monta o painel sem um módulo que as versões atuais do
# setuptools não trazem (pkg_resources) quando há no máximo 1.000 linhas: 333
# por classe é o maior valor igual nas três classes que cabe nesse limite. As
# figuras estáticas usam a amostra maior, de SHAP_SAMPLE_PER_CLASS.
DASHBOARD_SAMPLE_PER_CLASS = 333

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
HKD_CSV_PATH = DATA_RAW_DIR / "hkd" / "DoH-CSVs" / "DoH-CSVs-48h" / "Total-48h.csv"
HKD_AUGMENTED_CSV_PATH = DATA_RAW_DIR / "hkd" / "Total-48h-Augmentation.csv"
# Arquivos de nível 1, 2 e 3 do combinado, nessa ordem.
COMBINED_CSV_PATHS = [
    DATA_RAW_DIR / "combinado" / "l1-total-add.csv",
    DATA_RAW_DIR / "combinado" / "l2-total-add.csv",
    DATA_RAW_DIR / "combinado" / "l3-total-add.csv",
]
HKD_PARQUET_PATH = DATA_PROCESSED_DIR / "hkd.parquet"
COMBINED_PARQUET_PATH = DATA_PROCESSED_DIR / "combinado.parquet"
COMBINED_UNIQUE_PARQUET_PATH = DATA_PROCESSED_DIR / "combinado_sem_replicas.parquet"


def smote_seed(seed: int, subset_index: int) -> int:
    """Devolve a seed do SMOTE do subconjunto de índice `subset_index`.

    Cada subconjunto precisa de um sorteio próprio, e o valor não pode coincidir
    com o de outra execução: `seed * 100 + subset_index` não colide entre as
    seeds 0 a 9 e 42 com três subconjuntos. Os Random Forests e o
    meta-classificador usam `seed` diretamente.
    """
    return seed * 100 + subset_index
