# 22 · padronização · registrar os padrões que nasceram na implementação (anti-recorrência)

**Onde:** raiz do repositório, fora de `project/` (versionados desde a decisão 43) — `.claude/rules/`, `CLAUDE.md`, `docs/06-padroes.md`
**Objetivo:** os padrões que o plano define ficam escritos onde os próximos agentes e integrantes leem, para os erros que eles evitam não voltarem. Ou fica justificado por que não é preciso.
**Depende de:** 08, 11. Não bloqueia nenhuma outra tarefa
**Demonstra:** regras registradas ou dispensa justificada, conferível por `grep`.

## O que fazer

1. **Analisar criticamente se a documentação é necessária.** Para cada padrão abaixo, responder: previne um erro que de fato pode recorrer? Alguém (agente ou integrante) vai ler e aplicar? Já está coberto por regra existente ou por teste automatizado?

| Padrão que o plano introduz | Já coberto por |
| --- | --- |
| Matriz de atributos montada por nome das 29 colunas, nunca "tudo menos o rótulo" | Teste do invariante I4 |
| Trilha (`fiel`, `corrigida`, `variante` ou `dados`) obrigatória em todo resultado | `runlog` recusa outra trilha (tarefa 02) |
| Teste só é lido na avaliação final | Nada automatizado; só revisão |
| Scaler e reamostragem refeitos dentro de cada fold onde há validação cruzada (tarefa 08) ou seleção de hiperparâmetros (tarefa 15) | Testes T08-5 e T15-1 |
| Escolha em ponto omisso do artigo leva comentário com decisão, motivo e seção do artigo, sem identificador interno | `.claude/rules/codigo.md` |
| Commit sem coautoria, com lint verde, uma tarefa por vez | `.claude/rules/commits.md` e `fluxo-implementacao.md`; hooks e CI (tarefa 01) |
| Formato de `shap_values` como array (amostras, atributos, classes) | Teste na tarefa 12 |
| Lista fechada de variantes antes de ver resultado | Skill `experimento` |
| Configurações, arquitetura e teste estatístico travados em `config.py` e em decisão antes de rodar | Nada automatizado; só revisão |
| Tempos e datas fora do `metrics.json` | Gate G6 falha se entrarem |
| Predição de Random Forest com `n_jobs=1` depois do ajuste, para `predict_proba` repetir entre execuções (nasceu na tarefa 08, `models.py`) | Gate G6 falha se faltar; nada o exige em modelo novo |
| Onde o artigo admite duas leituras, as duas são medidas no mesmo protocolo e reportadas lado a lado, cada uma na sua trilha (decisão 45) | Nada automatizado; só revisão |

2. Para cada um, decidir **REGISTRAR** ou **DISPENSAR**. Padrão já garantido por teste ou por código que falha tende a ser dispensa: a regra escrita seria redundante. Padrão que só depende de disciplina (o do teste, o da lista fechada) tende a ser registro.
3. Se registrar: uma regra curta e imperativa, com o anti-padrão, o padrão correto e um exemplo, em `.claude/rules/<regra>.md` ou em seção do `CLAUDE.md`. Conferir antes que não duplica nem contradiz `docs/06-padroes.md` e o agente `revisor-metodologico`.
4. Atualizar `docs/06-padroes.md` e `docs/02-artigo.md` onde a implementação mudou o que estava previsto (nomes de coluna reais, leituras de ambiguidade confirmadas ou trocadas).
5. Citar a tarefa ou a decisão que originou cada regra.

## Por quê

O projeto é tocado por quatro pessoas e por agentes; padrão que vive só na cabeça de quem implementou a tarefa 08 não chega à tarefa 15. Ao mesmo tempo, regra demais ninguém lê: por isso a análise de necessidade vem antes do registro.

## Critério de aceite

- [ ] Para cada padrão da tabela, a decisão está escrita: **REGISTRAR** (com o caminho da regra, conferível por `grep`) ou **DISPENSAR** (com a justificativa).
- [ ] Toda regra registrada tem anti-padrão, padrão correto e exemplo.
- [ ] Nenhuma regra duplica ou contradiz `CLAUDE.md`, `docs/06-padroes.md` ou os agentes existentes.
- [ ] `docs/` reflete o que foi de fato implementado.

## Testes

Sem teste automático. Critério de aceite conferido por outro integrante.

## Verificação ao concluir

Gate de organização: G8, G10.
