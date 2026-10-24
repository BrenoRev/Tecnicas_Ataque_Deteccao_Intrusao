"""Painel interativo de explicabilidade, como o da Seção VI-C do artigo.

Lê data/processed/cira.parquet, separa 10% para teste com a seed 42, ajusta o
sistema na leitura de profundidade variável e sobe o painel do
explainerdashboard sobre o Random Forest do primeiro subconjunto, com uma
amostra estratificada do teste. O modelo é treinado na memória a cada execução:
nenhum modelo é gravado nem lido do disco, e o painel não grava resultado.

O painel é material de demonstração; os números do relatório vêm de
scripts/e5_xai.py. Os atributos aparecem normalizados em [0, 1], que é o que o
modelo recebe. O treino e o cálculo dos valores SHAP levam alguns minutos antes
de o endereço responder. Para encerrar, Ctrl+C.

Uso: uv run python scripts/painel_xai.py
"""

import pandas as pd
from explainerdashboard import ClassifierExplainer, ExplainerDashboard

from doh_ids.config import (
    CIRA_PARQUET_PATH,
    CLASS_NAMES,
    DASHBOARD_HOST,
    DASHBOARD_PORT,
    EXPLAINED_BASE,
    FEATURE_COLUMNS,
    MAX_DEPTH_VARIABLE,
    SEED_FIEL,
    SHAP_SAMPLE_PER_CLASS,
)
from doh_ids.data import feature_matrix
from doh_ids.explain import stratified_sample
from doh_ids.splits import stratified_split
from doh_ids.system import fit_system


def build_dashboard(table: pd.DataFrame) -> ExplainerDashboard:
    """Treina o sistema sobre `table` e monta o painel, sem abrir o servidor.

    `table` tem os atributos do modelo e `label`. O painel explica um Random
    Forest base nas linhas de uma amostra do teste.
    """
    # O teste é separado antes do ajuste e só é lido para ser explicado.
    train, test = stratified_split(table, SEED_FIEL)
    scaler, stacked, _, _ = fit_system(train, SEED_FIEL, MAX_DEPTH_VARIABLE)
    sample = stratified_sample(test, SHAP_SAMPLE_PER_CLASS, SEED_FIEL)
    X = pd.DataFrame(scaler.transform(feature_matrix(sample)), columns=FEATURE_COLUMNS)

    # O SHAP não aceita o modelo empilhado: o painel explica o Random Forest do
    # primeiro subconjunto, o mesmo das figuras estáticas. A classe em destaque
    # ao abrir é Malicious-DoH; as outras são escolhidas na própria página.
    explainer = ClassifierExplainer(
        stacked.clfs_[EXPLAINED_BASE],
        X,
        sample["label"].reset_index(drop=True),
        shap="tree",
        labels=CLASS_NAMES,
        pos_label=CLASS_NAMES.index("Malicious-DoH"),
    )
    # Ficam as abas que correspondem às figuras do artigo: importância (Fig. 5),
    # dependência (Fig. 6) e contribuições de um fluxo (Figs. 7 e 8). As métricas
    # de desempenho ficam de fora porque a amostra tem as classes em partes
    # iguais e não mede o modelo; as demais, pelo custo de cálculo.
    return ExplainerDashboard(
        explainer,
        title="Explicação do Random Forest base (Balanced Stacked Random Forest)",
        importances=True,
        shap_dependence=True,
        contributions=True,
        model_summary=False,
        whatif=False,
        shap_interaction=False,
        decision_trees=False,
        no_permutations=True,
    )


def main() -> None:
    """Monta o painel com os dados reais e o serve só na própria máquina."""
    dashboard = build_dashboard(pd.read_parquet(CIRA_PARQUET_PATH))
    print(f"Painel em http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    dashboard.run(port=DASHBOARD_PORT, host=DASHBOARD_HOST)


if __name__ == "__main__":
    main()
