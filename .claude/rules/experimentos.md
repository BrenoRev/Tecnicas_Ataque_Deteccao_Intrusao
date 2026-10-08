# Regras de experimento

Valem para todo script que produz arquivo em `project/results/`. Nasceram na implementação dos experimentos E0 a E8 e dependem de disciplina: nenhum teste as garante sozinho. As regras de vazamento e de reprodutibilidade estão em `codigo.md`; o procedimento passo a passo, na skill `experimento`.

## 1. Treinar e resumir são scripts diferentes

- **Errado:** o script que treina também escreve o `RESUMO.md`. Corrigir uma frase do resumo passa a exigir horas de treino, e o script fica grande demais para defender.
- **Certo:** o script de treino só treina, avalia e grava `metrics.json` e `run.json`. Um script de resumo lê esses arquivos e grava `RESUMO.md`, `summary.json` e a tabela comparativa, sem treinar.
- **Exemplo:** `scripts/e4_corrigido.py` e `scripts/e4_resumo.py`.
- Vale para experimento novo e para o que treina por mais de alguns minutos. Os scripts antigos e rápidos que ainda escrevem o próprio resumo (E0, E2, E5, etapa de dados de E6) não precisam ser reescritos.

## 2. Tempo não entra em arquivo que se compara

- **Errado:** tempo de treino dentro de `metrics.json` ou misturado, sem nome que o identifique, em um agregado.
- **Certo:** `metrics.json` só tem valor determinístico; tempo e data ficam no `run.json`. Agregado que precisar de tempo o põe em chave com `seconds` ou `time` no nome, para a comparação entre execuções poder ignorá-la.
- **Exemplo:** `train_seconds` em `results/e8/corrigida/summary.json`, ignorada por `scripts/comparar_resultados.py`.

## 3. Hipótese antes, análise posterior marcada

- **Errado:** escrever o que se esperava depois de ver o número, ou acrescentar uma comparação nova ao resumo como se estivesse prevista.
- **Certo:** `HIPOTESE.md` em commit anterior ao da primeira execução, com o que seria resultado inesperado e a regra de leitura; ele não muda depois. O que for acrescentado depois de ver os números fica em bloco próprio, com a palavra "posterior" no arquivo e na legenda da tabela, e não altera a regra nem os vereditos fixados antes.
- **Exemplo:** `results/e8/corrigida/HIPOTESE.md` e a chave `posterior` do `summary.json` da mesma pasta.
- Um segundo experimento na mesma pasta usa sufixo no nome: `HIPOTESE-ROBUSTEZ.md`, `RESUMO-ROBUSTEZ.md`.

## 4. Duas leituras do artigo, as duas medidas

- **Errado:** escolher a leitura do artigo que aproxima o número e reportar só ela.
- **Certo:** onde o artigo admite duas leituras, as duas rodam no mesmo protocolo e aparecem lado a lado em toda tabela, com a coluna que as identifica. O texto diz qual serve de base às etapas seguintes e por quê, e não afirma qual os autores usaram.
- **Exemplo:** profundidade 5 (Seção IV-B) e profundidade variável (Algoritmo 1) em `results/e1/`; na trilha `corrigida`, o sufixo `-prof5`.

## 5. Lista do que se pode afirmar antes do texto

- **Errado:** escrever relatório ou slide direto dos resumos, deixando a frase ir além do número.
- **Certo:** antes do texto, uma lista do que os resultados sustentam e do que não sustentam, cada item com o número e o arquivo de origem; o revisor de texto confere o documento contra ela.
- **Exemplo:** frase proibida: "a modificação é mais robusta". Frase permitida: "com fator 2, o recall cai 0,34 ponto na modificação e 3,19 no sistema do artigo, nas dez seeds, em perturbação simulada".

## 6. Determinismo se confere fora de `results/`

- **Errado:** rodar o script duas vezes sobre `results/` e comparar com `git diff`, sobrescrevendo o que está versionado.
- **Certo:** a função de execução recebe o diretório de saída; a segunda execução grava em diretório temporário e os `metrics.json` são comparados com os versionados.
- **Exemplo:** `run_experiment(table, data_sha256, results_dir, ...)` nos scripts; `scripts/comparar_resultados.py` para a comparação.

## Dispensados, com o motivo

- **Rodar como módulo (`python -m scripts.<nome>`) quando um script importa outro:** não vira regra. Rodar pelo caminho falha na importação com erro claro, e o README traz o comando de cada script.
- **Retomada por commit em execução longa:** não vira regra. São dois scripts que a têm e dois longos que não a têm; exigir retomada em todos acrescentaria código a defender sem proteger resultado.
