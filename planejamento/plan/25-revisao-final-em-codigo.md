# 25 · fechamento · revisão final em código

**Onde:** `project/src/`, `project/scripts/`, `project/tests/`, `project/results/` (só leitura), `project/report/` (só leitura)
**Objetivo:** garantir que o que foi construído está correto verificando o código e os números já gravados, sem treinar nada de novo. A execução limpa (tarefa 19) responde "o repositório regenera os mesmos números"; esta revisão responde "os números são os que o código descrito produz, e o código faz o que o relatório diz".
**Depende de:** 19 (execução limpa concluída e comparada).
**Demonstra:** `planejamento/plan/REVISAO-FINAL.md`, com um veredito por verificação e a evidência de cada um.
**Quem executa:** agente `revisor-metodologico` para as verificações; `implementador` só se houver achado a corrigir.

## Princípio

Nenhuma verificação desta tarefa roda treino. Cada uma é de um destes quatro tipos:

1. **Leitura de código** contra o artigo, as decisões e as regras.
2. **Recomputação**: refazer um número derivado a partir do dado primário já gravado (métrica a partir da matriz de confusão, agregado a partir dos `metrics.json`, tabela a partir do agregado, frase a partir da tabela).
3. **Mutação**: quebrar de propósito um invariante em uma cópia temporária do código e conferir que o teste correspondente falha, com dados sintéticos.
4. **Rastro no Git**: conferir que o código que gerou cada resultado é o que está na `main`, ou que a diferença não toca lógica numérica.

Um achado que só se resolveria treinando de novo não é corrigido aqui: é registrado, com o experimento afetado e o custo da nova execução, para decisão da equipe.

## Verificações

### V1. Rastro de cada resultado até o código

- Todo `metrics.json` tem `run.json` ao lado, com `dirty: false`, trilha igual à do caminho e um commit que existe no histórico.
- Para cada experimento, `git diff <commit do run.json>..HEAD` sobre o script que o gerou e sobre `src/doh_ids/`: cada diferença é classificada em "só texto, nome ou organização" ou "toca lógica numérica".
- Toda diferença que toca lógica numérica precisa de prova de equivalência por outro caminho (V2 ou teste). Casos já conhecidos: `fit_system` movida para o pacote depois de E1; `evaluate` passou a receber nomes de classe depois de E1 a E6; funções de texto separadas dos scripts de treino de E3, E4 e E7.
- A execução limpa cobre isso por inteiro: se ela regenerou os mesmos `metrics.json` com o código da `main`, V1 fecha por ela, e a classificação acima fica como registro.

### V2. Recomputação em cadeia

- **Matriz → métricas:** recalcular com `evaluate.metrics_from_confusion` as métricas de toda matriz de confusão gravada e comparar com as gravadas (tolerância de ponto flutuante).
- **Totais:** a soma de cada matriz de teste é o tamanho do teste registrado em `split_counts.json` (ou no `split` do próprio arquivo); a soma por linha é a contagem por classe do teste; a matriz de validação cruzada soma o treino.
- **Execuções → agregado:** recalcular média, desvio padrão amostral, comparação pareada e vereditos de E4 e E8 a partir dos `metrics.json` por seed e comparar com `summary*.json`.
- **Resultados → tabelas:** `make_report_assets.py` em diretório temporário gera `report/tables/` e `INDICE.md` idênticos aos versionados.
- **Tabelas → texto:** extrair todo número de `relatorio.tex` (prosa) e de `make_slides.py` (tópicos) e localizar cada um em uma tabela, em um `metrics.json`/`summary*.json`, em um `RESUMO.md` ou no artigo; listar os que não têm origem.
- **Artigo → constantes:** valores do artigo em `config.py` (Tabela I, Fig. 4a e 4b, Tabela II, Fig. 5, Figs. 7 e 8, Seção VI-D, Fig. 9) contra o manuscrito; `scripts/metricas_fig4.py` e `config.py` dão as mesmas matrizes.

### V3. Invariantes de vazamento, por leitura e por mutação

Para cada invariante: onde o código o garante, que asserção de script o confere em execução real, que teste o protege, e uma mutação que precisa fazer o teste falhar.

| Invariante | Mutação |
| --- | --- |
| Teste separado antes de qualquer ajuste | ajustar o scaler na tabela inteira |
| Scaler ajustado só no treino, inclusive em cada fold da validação cruzada | ajustar o scaler antes do laço de folds |
| SMOTE só no treino; sintético só nas classes previstas | aplicar o SMOTE antes do split |
| Matriz de atributos por nome das 29 colunas; identificadores e `group` fora | montar a matriz com "tudo menos o rótulo" |
| Seleção de hiperparâmetros da modificação só com linhas do treino da seed | selecionar na tabela inteira |
| Transferência: nada do segundo conjunto entra em ajuste | ajustar o scaler com o HKD |
| Perturbação só nos maliciosos do teste, com o scaler do treino | perturbar o treino |
| Combinado sem réplicas: nenhuma cópia do HKD em treino e teste | não remover as réplicas |

A mutação é aplicada em uma cópia do repositório em diretório temporário, uma por vez, com `uv run pytest` do teste indicado. Mutação que não derruba nenhum teste é achado: o invariante só está protegido por leitura.

### V4. Fidelidade ao artigo

- Cada hiperparâmetro e cada passo do pipeline em `config.py`, `splits.py`, `models.py` e `system.py` contra a seção, a tabela ou o algoritmo do artigo que o comentário cita.
- Cada ponto em que o artigo é omisso tem comentário com a leitura adotada, e a mesma leitura aparece no relatório.
- Nenhuma correção de protocolo entrou na trilha `fiel`.

### V5. Sorteios e determinismo

- Busca por fonte de sorteio sem seed explícita: `random_state` ausente em construtor que aceita, `np.random` global, `shuffle=True` sem seed, `sample` sem `random_state`, ordem de `set` ou de `dict` influenciando resultado, `n_jobs` na predição.
- Toda seed vem de `config.py` ou de função de `config.py`.
- Nenhum valor não determinístico em `metrics.json` (tempo, data, caminho de máquina).

### V6. Coerência entre experimentos

- Mesma seed, mesmo split: `split_index_sha256` igual entre E4, E8 e a robustez; teste de E1, E2, E3, E5 com o mesmo total e as mesmas contagens por classe; hash do Parquet igual em todos os `run.json` que o leem.
- Um modelo que aparece em dois experimentos tem a mesma matriz nos dois (o modelo A de E4 e o de referência da robustez; o sistema de E1 e a linha de partida de E3; o sistema transferido em E6 no teste do CIRA e o de E1).

### V7. Testes

- Cada teste do plano de testes existe e confere o que a linha diz; nenhum `skip`, `xfail` ou asserção vazia.
- Funções que decidem resultado e não têm teste: lista, com o risco de cada uma.
- A suíte roda em menos de um minuto na máquina livre e não lê dados reais.

### V8. Texto contra a lista do que se pode afirmar

- `relatorio.tex`, `make_slides.py` e os `RESUMO.md` contra a seção "O que o relatório pode e não pode afirmar" da tarefa 24.
- README da raiz e de `project/`: cada número e cada afirmação com origem.

### V9. Higiene do repositório

- Os comandos do CI, localmente; nenhum arquivo proibido versionado; nenhum caminho de máquina; nenhuma referência a documento interno em `project/`; nenhum commit com coautoria de ferramenta; `LICENSE` presente.

## Saída

`planejamento/plan/REVISAO-FINAL.md`: uma linha por verificação (V1 a V9), com veredito `OK`, `Achado` ou `Não verificado`, a evidência (comando e saída resumida) e, para cada achado, a gravidade, o arquivo e a linha, a correção e se a correção exige treino.

## Critério de aceite

- [ ] Execução limpa comparada: `metrics.json` e agregados regenerados iguais aos versionados (tarefa 19).
- [ ] V1 a V9 com veredito e evidência.
- [ ] Todo achado que não exige treino corrigido, com lint e testes verdes.
- [ ] Todo achado que exigiria treino registrado, com o experimento e o custo, para decisão da equipe.
- [ ] Pendências do plano e de `docs/` que esta revisão resolve marcadas como fechadas, com a evidência; as que são de pessoa continuam abertas e listadas.
