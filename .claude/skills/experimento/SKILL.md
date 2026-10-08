---
name: experimento
description: Procedimento padrão para planejar, implementar, rodar e registrar um experimento do projeto CIN0114 (E0 a E8 do plano experimental). Use antes de escrever ou executar qualquer script que produza um resultado que possa ir para o relatório, e ao pedir "roda o experimento", "implementa E1", "testa essa variante".
---

# Experimento

Um experimento só existe quando deixa um resultado em `results/` que outra pessoa consegue regenerar com um comando.

## Antes de escrever código

1. Leia `docs/05-plano-experimental.md` e localize o experimento (E0 a E8). Se não está lá, proponha a inclusão antes de implementar.
2. Declare em uma frase: o que o experimento testa, contra qual alvo compara (figura ou tabela do artigo, ou outro experimento) e o que contaria como resultado inesperado.
3. Diga a trilha: **fiel** (como o artigo descreve) ou **corrigida** (protocolo consertado). Não misture.
4. Liste as ambiguidades de `docs/02-artigo.md` (A1 a A18) que o experimento precisa resolver e como cada uma será resolvida. Se a resolução ainda não está decidida, pergunte.
5. Aponte, antes de executar, qualquer risco de vazamento, comparação injusta ou métrica inadequada no que foi pedido.

## Ao implementar

- Um script por experimento em `scripts/`, executável de dentro de `project/` (`uv run python scripts/<nome>.py`, ou `uv run python -m scripts.<nome>` quando importa outro script); lógica reutilizável em `src/`. O script de treino só grava `metrics.json` e `run.json`; o resumo sai de um script separado (`.claude/rules/experimentos.md`).
- Configuração em `src/doh_ids/config.py`: hiperparâmetros com a origem (seção do artigo ou "escolha nossa") em comentário, seed, caminhos relativos a `project/`.
- O conjunto de teste é separado primeiro e só é lido na avaliação final.
- Scaler, reamostragem e busca de hiperparâmetros são ajustados só no treino. Onde há validação cruzada ou seleção de hiperparâmetros, scaler e reamostragem são refeitos dentro de cada fold.
- Identificadores (IPs, portas, timestamp) fora da matriz de atributos.
- Padrões de código em `docs/06-padroes.md`. Prefira a versão mais simples que um integrante consiga explicar em arguição.

## Ao registrar

Antes da primeira execução, `HIPOTESE.md` em commit próprio, com o que seria inesperado e a regra de leitura. Cada execução grava em `results/<experimento>/<trilha>/<recorte>/seed<k>/`:

- métricas em arquivo legível por máquina: matriz de confusão, precisão/recall/F1 por classe, macro e ponderada, AUC, contagem por classe em cada conjunto;
- a configuração usada, a seed, as versões das bibliotecas, o hash dos dados e o commit;
- figuras geradas por código, com eixos rotulados.

Nenhum número é copiado à mão para o relatório.

## Ao reportar

1. Tabela com o resultado ao lado do alvo e a diferença.
2. Para cada número relevante, uma linha de interpretação em termos de detecção (o que significa para quem opera o IDS).
3. O que não foi feito, o que foi simplificado e o efeito provável disso.
4. Se o resultado diverge do artigo, liste as causas plausíveis sem escolher uma sem evidência.
5. Peça revisão ao agente `revisor-metodologico` antes de o resultado ser citado em qualquer texto.

Resultado ruim ou não reprodução é reportado como está. Não ajuste seed, split ou hiperparâmetro olhando para o teste até o número parecer com o do artigo: isso é vazamento, e invalida a reprodução.
