"""Recalcula as métricas do artigo de referência a partir das matrizes da Figura 4.

As contagens abaixo foram lidas da Figura 4 de Zebin, Rezvy e Luo (IEEE TIFS, 2022):
(a) treino, obtida em validação cruzada de 10 folds; (b) teste.
Linhas = classe real, colunas = classe predita, na ordem de CLASSES.

Uso: python scripts/metricas_fig4.py
Só usa a biblioteca padrão, para rodar antes de qualquer ambiente estar montado.
"""

CLASSES = ["Benign-DoH", "Malicious-DoH", "Non-DoH"]

MATRIZES = {
    "Fig. 4a (treino, CV 10 folds)": [
        [15946, 9, 1816],
        [9, 224496, 93],
        [503, 10, 800316],
    ],
    "Fig. 4b (teste)": [
        [1782, 1, 192],
        [0, 24949, 6],
        [50, 2, 88928],
    ],
}

# Prevalência hipotética de fluxos maliciosos usada na discussão de taxa base.
# Não é dado medido: serve só para mostrar o efeito de Bayes sobre a precisão.
PREVALENCIA_HIPOTETICA = 1e-4


def metricas_por_classe(matriz):
    """Devolve o total de fluxos e, por classe, suporte, precisão, recall e F1."""
    total = sum(map(sum, matriz))
    linhas = []
    for i, classe in enumerate(CLASSES):
        vp = matriz[i][i]
        suporte = sum(matriz[i])
        preditos = sum(linha[i] for linha in matriz)
        precisao = vp / preditos
        recall = vp / suporte
        f1 = 2 * precisao * recall / (precisao + recall)
        linhas.append((classe, suporte, precisao, recall, f1))
    return total, linhas


def relatorio(nome, matriz):
    """Imprime as métricas por classe, as médias e a visão binária de uma matriz."""
    total, linhas = metricas_por_classe(matriz)
    acertos = sum(matriz[i][i] for i in range(len(CLASSES)))

    print(f"\n{nome}")
    print(f"  fluxos={total}  erros={total - acertos}  acurácia={acertos / total:.4%}")
    for classe, suporte, p, r, f1 in linhas:
        print(f"  {classe:<14} n={suporte:<7} precisão={p:.2%} recall={r:.2%} F1={f1:.2%}")

    n = len(linhas)
    macro = [sum(linha[k] for linha in linhas) / n for k in (2, 3, 4)]
    pond = [sum(linha[k] * linha[1] for linha in linhas) / total for k in (2, 3, 4)]
    print("  macro      precisão={:.2%} recall={:.2%} F1={:.2%}".format(*macro))
    print("  ponderada  precisão={:.2%} recall={:.2%} F1={:.2%}".format(*pond))

    # Visão binária "malicioso contra o resto", que é a que gera alerta num SOC.
    i = CLASSES.index("Malicious-DoH")
    negativos = total - sum(matriz[i])
    fp = sum(matriz[j][i] for j in range(n) if j != i)
    fpr = fp / negativos
    tpr = matriz[i][i] / sum(matriz[i])
    pi = PREVALENCIA_HIPOTETICA
    precisao_operacional = pi * tpr / (pi * tpr + (1 - pi) * fpr)
    prevalencia_conjunto = sum(matriz[i]) / total
    print(
        f"  malicioso: FP={fp}/{negativos}  FPR={fpr:.4%}  "
        f"prevalência no conjunto={prevalencia_conjunto:.1%}"
    )
    print(
        f"  com prevalência hipotética de {pi:.2%}: precisão={precisao_operacional:.1%}, "
        f"{1e7 * (1 - pi) * fpr:.0f} alarmes falsos a cada 10 milhões de fluxos"
    )


if __name__ == "__main__":
    for nome, matriz in MATRIZES.items():
        relatorio(nome, matriz)
