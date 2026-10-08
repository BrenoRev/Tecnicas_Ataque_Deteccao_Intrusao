# 05. Plano experimental

O que rodar, em que ordem, com que protocolo, e o que cada experimento precisa provar. É proposta da equipe; os pontos que dependem do professor estão em [07-pendencias.md](07-pendencias.md).

> O desenho de E3, E4 e E8 foi refinado no plano de implementação, depois de uma revisão adversarial: E4 passou a ser avaliação em dez seeds com configurações fixas, sem busca; a única busca de hiperparâmetros é a de M2, em E8; o ajuste de limiar saiu de M1; E3 tem quatro variantes obrigatórias e três opcionais. Onde este documento e o plano divergirem, vale [../planejamento/MEMORY/00-decisoes-travadas.md](../planejamento/MEMORY/00-decisoes-travadas.md) (decisões 23 a 26).
>
> **Estado em 08/10/2026 (commit `759ec29`): E0 a E8 foram executados com os dados reais em 07 e 08/10/2026**, nesta máquina (decisão 44), com a árvore limpa e o commit gravado em cada `run.json`. A seção "Como foi executado" diz, por experimento, o script, o caminho em `project/results/` e o que ficou de fora. As seções por experimento, mais abaixo, guardam o desenho original; onde ele mudou, há uma nota. Este documento não copia resultados: os números estão nos `RESUMO.md`.
>
> **Fechamento em 08/10/2026 (commit `5999c1b`).** A execução limpa refez os 22 passos em um clone novo, em 7 h 30 min: 260 de 260 arquivos de `results/` e 56 de 56 de `report/` conferem com os versionados. A revisão final em código recalculou 362 matrizes e 11.266 métricas, sem divergência, e não achou bloqueante; os achados foram tratados com asserções nos scripts de E1, E2, E4 e E6 e cinco testes novos, sem mudar a lógica numérica. A suíte tem 118 testes. Fonte: `planejamento/plan/REVISAO-FINAL.md`. A ordem de execução está em `project/README.md`, "Ordem dos scripts", e em `project/scripts/execucao_limpa.sh`.

## Princípio

Duas trilhas que nunca se misturam:

- **Fiel**: o sistema como o artigo descreve, inclusive nas escolhas que criticamos. Responde ao objetivo P1.
- **Corrigida**: o mesmo sistema com o protocolo consertado (reamostragem dentro dos folds, várias seeds, médias nomeadas). Mostra quanto do resultado publicado sobrevive a uma avaliação limpa.

Todo arquivo de resultado traz no nome e no conteúdo a trilha a que pertence.

## Experimentos

| ID | Experimento | Objetivo da especificação | Alvo de comparação | Depende de |
| --- | --- | --- | --- | --- |
| E0 | Integridade e descrição dos dados | P1, seção 6 do relatório | Tabela I | Download |
| E1 | Reprodução fiel do Balanced Stacked RF | P1 | Fig. 4a, Fig. 4b, Tabela II | E0 |
| E2 | Baselines do artigo | P1 | Tabela II | E0 |
| E3 | Sensibilidade às ambiguidades | P1 | Fig. 4b | E1 |
| E4 | Protocolo corrigido | P1 (discussão), base de P3 | E1 | E1 |
| E5 | Explicabilidade | P1 | Figs. 5 a 8 | E1 |
| E6 | Segundo dataset | P2 | E1 | E1 |
| E7 | Subclassificação por ferramenta | P1 (obrigatório desde a decisão 49) | Seção VI-D e Fig. 9 | E0, E1 |
| E8 | Modificação proposta | P3, opcional | E1 e E4 | E4 |

## Como foi executado

Caminhos relativos a `project/`. Os scripts rodam dentro de `project/`; os que importam outro script rodam como módulo (`uv run python -m scripts.<nome>`), os demais como arquivo (`uv run python scripts/<nome>.py`). O comando de cada um está na linha "Uso:" da docstring.

**Duas leituras de profundidade em todo experimento que treina o sistema do artigo** (decisões 45 e 51). A Seção IV-B do artigo dá profundidade máxima 5; a linha 3 do Algoritmo 1 fala em "variable tree depth". Nas trilhas `fiel` e `variante`, a trilha nomeia a leitura (`fiel` = 5, `variante` = sem limite). Na trilha `corrigida`, o sistema base é o de profundidade variável e a leitura de profundidade 5 leva o sufixo `-prof5` no recorte. O motivo de a variável ser a base: com profundidade 5 e a seed 42, o modelo empilhado não prediz Benign-DoH em nenhuma linha do teste (`results/e1/RESUMO.md`).

| ID | Scripts | Resultados | Como rodou | O que ficou de fora (declarado no resumo) |
| --- | --- | --- | --- | --- |
| E0 | `scripts/e0_dados.py` | `results/e0/dados/cira/seed42/`; resumo em `results/e0/dados/RESUMO.md` | Seed 42. Regras de limpeza ao lado da Tabela I, máquinas e período, split, folds, vetores repetidos, teste normalizado e a figura equivalente à Fig. 2 | A Fig. 2 é comparada por mediana e quartil, sem teste estatístico e sem olhar a forma das curvas |
| E1 | `scripts/e1_reproducao.py` | `results/e1/fiel/proposto/seed42/`, `results/e1/variante/profundidade_variavel/seed42/`; resumo comparado em `results/e1/RESUMO.md` | Seed 42, uma execução por leitura. Teste ao lado da Fig. 4b e validação cruzada de 10 folds ao lado da Fig. 4a; bases isolados; tabela de decisão do meta | Sem média entre seeds (ela está em E4) |
| E2 | `scripts/e2_baselines.py` | `results/e2/fiel/{decision_tree,xgboost,random_forest}/seed42/`; `results/e2/fiel/RESUMO.md` | Seed 42. SMOTE no treino inteiro; Tabela II superior ao lado das médias macro e ponderada; metade inferior transcrita do artigo | Sem busca de hiperparâmetros; sem validação cruzada dos modelos de comparação; trabalhos da metade inferior não reproduzidos; uma execução por modelo |
| E3 | `scripts/e3_sensibilidade.py`, depois `scripts.e3_resumo` | `results/e3/variante/<recorte>/seed42/`, `comparacao.csv` e `RESUMO.md` | Seed 42, só no teste. Cinco leituras alternativas (`class_weight`, `use_probas`, `max_features_padrao`, `meta_uniao`, `rf_unico`), cada uma partindo das duas leituras de profundidade (sufixo `-prof5`): dez recortes | Meta com predições fora da amostra (`StackingCVClassifier`); one-sided selection; modelo com 28 atributos no total; duas leituras trocadas ao mesmo tempo; validação cruzada e outras seeds. **Não houve `HIPOTESE.md`** antes de rodar; o resumo declara |
| E4 | `scripts/e4_corrigido.py`, depois `scripts.e4_resumo` | `results/e4/corrigida/{A,B,C,A-prof5,B-prof5}/seed<k>/`, `A-fold<k>/seed0/`, `summary.json`, `HIPOTESE.md`, `RESUMO.md` | Dez seeds (0 a 9); configurações fixadas antes, sem busca; comparação pareada por seed com Wilcoxon; teste inteiro e teste sem vetores repetidos do treino; taxa base com prevalências hipotéticas de 10⁻³, 10⁻⁴ e 10⁻⁵; avaliação por máquina em quatro dobras (modelo A, seed 0) | Sem seleção de hiperparâmetros. A contra B não isola a arquitetura: o par difere também no balanceamento, e a diferença mede as duas coisas juntas |
| E5 | `scripts/e5_xai.py`; painel em `scripts/painel_xai.py` | `results/e5/fiel/proposto/seed42/`, `results/e5/variante/profundidade_variavel/seed42/`; `results/e5/RESUMO.md` | Seed 42. `TreeExplainer` sobre os três Random Forests base, em amostras de até 2.000 fluxos por classe (treino e teste); figuras equivalentes às Figs. 5 a 8; estabilidade entre os bases; corte de `Duration` | Explica os bases, não o empilhamento; amostras, não treino e teste inteiros; sem média entre seeds; o painel não grava resultado |
| E6 | `scripts/e6_dados.py`; `scripts/e6_dataset2.py`; `scripts.e6_baselines_xai`; `scripts.e6_resumo` | `results/e6/dados/{hkd,combinado,combinado_sem_replicas}/seed42/`; `results/e6/{fiel,variante}/{transferencia,retreino_publicado,retreino_sem_replicas}/seed42/`; baselines e SHAP em `retreino_sem_replicas-<modelo>` e `retreino_sem_replicas-shap`; `results/e6/RESUMO.md`; hipótese em `results/e6/fiel/HIPOTESE.md` | Seed 42. Tudo o que P1 produz é refeito no combinado sem réplicas (decisão 47); combinado como publicado e transferência ao lado; recall por ferramenta com intervalo de confiança; proximidade dos fluxos do HKD do teste ao treino | Validação cruzada grava só a matriz (sem AUC nem recall por ferramenta nos folds); os efeitos de peso do HKD no treino e de cópia no teste não são separados; a causa da diferença em `PacketLengthMode` não foi medida |
| E7 | `scripts/e7_ferramenta.py`, depois `scripts.e7_resumo` | `results/e7/{fiel,variante}/ferramenta/seed42/`, `results/e7/dados/fig9/seed42/`; `results/e7/RESUMO.md` | Seed 42. O sistema da reprodução aplicado só aos fluxos maliciosos, com as três ferramentas como classes (leitura da equipe); recall, precisão e F1 por ferramenta ao lado da "accuracy" do artigo; figura equivalente à Fig. 9 e a legenda medida de duas formas | Sem validação cruzada; sem outro classificador ou outro split; nada mede detecção. **Não houve `HIPOTESE.md`** antes de rodar; o resumo declara |
| E8, modificação | `scripts.e8_modificacao`, depois `scripts.e8_resumo` | `results/e8/corrigida/{M1-cira,M1-prof5-cira,M1M2-cira,A-combinado_sem_replicas,M1M2-combinado_sem_replicas}/seed<k>/`, `summary.json`, `HIPOTESE.md`, `RESUMO.md` | Dez seeds, nos dois datasets. Random Forest único, sem SMOTE, com `class_weight='balanced'` e scaler no `Pipeline`. Seleção de hiperparâmetros (M1M2) em **subamostra estratificada de 25% do treino** de cada seed, 5 folds, grade de oito combinações; ajuste final no treino inteiro (decisão 54) | Explicabilidade do modelo proposto; ajuste de limiar; variante com SMOTE e só seleção; M1, M1-prof5 e A-prof5 no combinado; par do M1M2 no HKD nas mesmas seeds |
| E8, robustez | `scripts.e8_robustez`, depois `scripts.e8_robustez_resumo` | `results/e8/corrigida/robustez-<modelo>-<colunas>/seed<k>/`, `summary-robustez.json`, `HIPOTESE-ROBUSTEZ.md`, `RESUMO-ROBUSTEZ.md` | Dez seeds, no CIRA. Parte A: ablação (todos os atributos; sem `Duration`; sem `Duration` e as duas taxas). Parte B: **perturbação no espaço de atributos**, não tráfego gerado: `Duration`, `FlowBytesSent` e `FlowBytesReceived` dos fluxos maliciosos do teste divididos por 2, 4, 8 e 16, com as estatísticas por pacote fixas | Perturbação das estatísticas por pacote, preenchimento e atraso; atacante com acesso ao modelo; combinado; teste sem vetores repetidos; treino com fluxos fragmentados; custo para o atacante. A leitura descritiva e os limiares dela foram acrescentados depois da execução, e o resumo diz |

Tabelas e figuras do relatório: `scripts/make_report_assets.py` lê `results/` e grava `report/tables/` e `report/figures/`, com o índice em `report/INDICE.md`.

### E0. Integridade e descrição dos dados

- Baixar, registrar SHA-256, contar linhas por arquivo e por classe.
- Contar NaN, infinitos e duplicatas por classe. Testar quais remoções levam às contagens da Tabela I (889.809 / 19.746 / 249.553).
- Conferir as 29 colunas numéricas contra [04-dados.md](04-dados.md).
- Gerar a tabela de amostras por classe em treino, validação e teste, que a seção 6 do relatório exige.
- Estatísticas descritivas e os gráficos de densidade da Fig. 2, para confirmar que estamos olhando para os mesmos dados.

Critério de conclusão: contagens da Tabela I reproduzidas, ou a diferença documentada com a limpeza que chegou mais perto.

### E1. Reprodução fiel

Passos, na ordem do artigo:

1. Split 90/10 estratificado, seed 42.
2. `MinMaxScaler` ajustado no treino.
3. Non-DoH de treino em três partes disjuntas; cada subconjunto recebe uma parte, todos os maliciosos e a classe benigna aumentada por SMOTE.
4. Três `RandomForestClassifier(n_estimators=10, max_depth=5, max_features=28)`.
5. Empilhamento com regressão logística.
6. Avaliação no teste intocado.

Decisões em aberto: ambiguidades A3 a A10 e A13, A14 de [02-artigo.md](02-artigo.md). Cada uma é resolvida com a leitura adotada, registrada na seção 5 daquele documento com o arquivo e a função do código. O passo 4 foi executado duas vezes, com `max_depth=5` e sem limite de profundidade.

Saídas: matriz de confusão do teste e da validação cruzada, métricas por classe, macro e ponderadas, AUC, tempo de treino.

Como medir "próximo o suficiente", na falta de critério do professor: diferença absoluta célula a célula contra a Fig. 4b, e diferença em pontos percentuais para acurácia, precisão, recall e F1 macro. O relatório mostra artigo, reprodução e diferença lado a lado.

### E2. Baselines do artigo

Árvore de decisão (profundidade 10), XGBoost e Random Forest (10 árvores), todos com SMOTE, mesmo split e mesmo teste de E1. O artigo não dá os demais hiperparâmetros; usar os padrões das bibliotecas e declarar isso.

A comparação que importa é Random Forest com SMOTE contra o modelo proposto: no artigo a diferença é de 0,0004 em F1. Sem variância entre execuções essa diferença não diz nada, e E4 vai medir.

### E3. Sensibilidade às ambiguidades

Como o artigo não especifica vários pontos, a reprodução é uma família de modelos. Variar um ponto por vez a partir de E1:

| Variante | O que muda |
| --- | --- |
| Com one-sided selection | Aplica OSS antes do SMOTE (A3) |
| Meta com predições out-of-fold | `StackingCVClassifier` (A8) |
| Meta com probabilidades | Em vez de rótulos (A10) |
| `class_weight='balanced'` | Como no script dos autores (A14) |
| `max_features` padrão | Em vez de 28 (crítica 5 do seminário) |

Reportar, para cada variante, a distância até a Fig. 4b. Se alguma variante reproduzir a matriz muito melhor que as outras, é indício de qual foi a configuração real dos autores.

Como executado: das cinco linhas acima, foram medidas as de probabilidades, `class_weight` e `max_features` padrão; one-sided selection e predições out-of-fold não foram. Entraram duas que a tabela não tinha: o meta ajustado na união dos três subconjuntos (`meta_uniao`) e a configuração do script publicado pelos autores (`rf_unico`). O resumo não aponta nenhum recorte como o mais próximo da Fig. 4b: a diferença entre recortes é menor que a variação entre seeds medida em E4.

### E4. Protocolo corrigido

- SMOTE dentro de cada fold, com `imblearn.pipeline.Pipeline`. Como executado: o `imblearn.pipeline.Pipeline` não foi usado. Em cada seed, o SMOTE é ajustado só no treino (por subconjunto no modelo empilhado; no treino inteiro nos Random Forests únicos), e a validação cruzada de E1 refaz a reamostragem dentro de cada fold (`system.cross_validated_confusion`).
- N seeds para split e modelos, reportando média e desvio padrão. N = 10, seeds 0 a 9 (decisão 12; `config.SEEDS_CORRIGIDA`).
- Métricas por classe, macro e ponderadas, sempre nomeadas; AUC-ROC e AUC-PR; matriz de confusão.
- FPR da classe maliciosa com intervalo de confiança, e a conta de taxa base sob prevalências hipotéticas declaradas como hipotéticas.
- Split por grupo (por exemplo, IP de origem ou janela de tempo) como avaliação adicional, se os dados permitirem. Medido em E0: quatro máquinas para Non-DoH e Benign-DoH, dez para Malicious-DoH, nenhuma em comum (`project/results/e0/dados/RESUMO.md`). Feito com quatro dobras por máquina, no modelo A.
- Comparação entre modelo proposto e Random Forest com SMOTE usando as N execuções pareadas.

### E5. Explicabilidade

- `TreeExplainer` sobre cada Random Forest base; summary plot global e por classe.
- Comparar o ranking de atributos com a Fig. 5 (duração no topo, depois comprimento de pacote e variância do tempo de pacote).
- Dependence plot de `Duration`: verificar o limiar aparente de 40 segundos da Fig. 6a.
- Interaction plot `FlowBytesSent` × `FlowBytesReceived` (Fig. 6b).
- Explicações locais de um fluxo malicioso e de um Non-DoH, no formato das Figs. 7 e 8.
- Estabilidade: o ranking muda entre os três submodelos e entre seeds?

Limitação a declarar: isso explica os modelos base, não a decisão final do empilhamento. Explicar o empilhamento inteiro exigiria um explicador agnóstico a modelo, muito mais caro; se não for feito, dizer. Não foi feito. O resumo mede o alcance da explicação: a fração da amostra em que a classe mais provável do base é a classe que o modelo empilhado devolve (`project/results/e5/RESUMO.md`). A estabilidade foi medida entre os três submodelos; entre seeds, não.

### E6. Segundo dataset

Depende da escolha em [04-dados.md](04-dados.md). Com o HKD e o combinado:

- **E6a, transferência**: modelo de E1, treinado só no CIRA, aplicado aos fluxos de dnstt, tcp-over-dns e tuns. Métrica: recall de Malicious-DoH por ferramenta. Não há negativos, então não existe precisão nem FPR neste recorte, e o relatório precisa dizer isso.
- **E6b, sistema no outro dataset**: pipeline completo de E1 retreinado no combinado, split 90/10 estratificado, mesmas métricas.

O normalizador é ajustado só no treino de cada cenário. Em E6a, o `MinMaxScaler` do CIRA é aplicado ao HKD; valores fora de [0, 1] são esperados e devem ser contados, porque indicam mudança de distribuição.

Como executado: E6b virou o cenário principal, no combinado **sem réplicas**, com tudo o que P1 produz refeito nele (decisões 36 e 47); o combinado como publicado e E6a ficam ao lado. A expectativa de valores fora de [0, 1] na transferência não se confirmou: foram contados 0 (`project/results/e6/RESUMO.md`).

### E7. Subclassificação por ferramenta

O artigo dá 99,2% (dns2tcp), 92,9% (iodine) e 91,3% (dnscat2) sem método.

Deixou de ser condicional. O professor pediu uma conversa sobre o ponto (Q5) e a equipe decidiu fazer sem esperar (decisão 49), porque a decisão 46 pede todos os resultados do artigo. O método é leitura da equipe, declarada como tal: ver a linha A16 em [02-artigo.md](02-artigo.md) e a tabela "Como foi executado".

### E8. Modificação proposta (ponto extra)

Candidatas, da mais barata para a mais cara. Todas saem das críticas do seminário, então a seção 5 do relatório já está meio escrita.

| Candidata | O que muda | Hipótese | Custo |
| --- | --- | --- | --- |
| M1. Protocolo sem vazamento e sem SMOTE | `class_weight` ou ajuste de limiar no lugar de 92% de benignos sintéticos | Recall de Benign-DoH igual ou maior, sem dados inventados | Baixo: é E4 com uma troca |
| M2. Random Forest com aleatorização de atributos | `max_features` menor, mais árvores, profundidade selecionada por busca declarada | Reduz o viés na classe benigna (recall de 90%) | Baixo |
| M3. Robustez à manipulação de duração | Avaliar o modelo com `Duration` e taxas perturbadas de forma válida (sessão fragmentada em fluxos curtos) e treinar uma versão sem os atributos manipuláveis | O modelo original degrada; a versão sem `Duration` perde pouco em dados limpos e ganha sob evasão | Médio; liga com as aulas de ataques adversariais |
| M4. Split por grupo e teste com ferramenta fora do treino | Deixa uma ferramenta de túnel fora do treino | Mede generalização que o artigo não mede | Médio |

Recomendação: M1 + M2 como modificação principal, porque caem quase de graça depois de E4 e atacam diretamente as críticas 3, 4 e 5. M3 se sobrar tempo, por ser a que mais conversa com a disciplina. Fazer qualquer uma obriga a apresentar em 19/11.

Como executado: M1 + M2 e M3 foram feitos (decisões 02, 52 e 54). M1 ficou sem ajuste de limiar (decisão 25). Em M3 foi feita a ablação (versões sem `Duration` e sem `Duration` e as taxas) e a fragmentação como perturbação no espaço de atributos; "treinar uma versão" com fluxos fragmentados não foi feito. M4 não foi feita como modificação: a avaliação por máquina está em E4, e não há teste com uma ferramenta de túnel do CIRA fora do treino (o que existe é a transferência para as ferramentas do HKD, em E6).

Sobre M3: perturbar atributos estatísticos livremente não gera tráfego válido. A perturbação precisa corresponder a algo que o atacante consegue fazer na rede (encerrar e reabrir conexões, inserir atraso, preencher pacotes) e os atributos derivados têm de ser recalculados de forma coerente. Se isso for simplificado, o relatório diz o que foi simplificado.

Foi simplificado, e o resumo diz: as estatísticas por pacote não foram recalculadas, e os vetores perturbados ficam incoerentes (tempo médio de pacote maior que a duração) em fração crescente com o fator. Os números da parte B são um limite aproximado, não a medição de um ataque (`project/results/e8/corrigida/RESUMO-ROBUSTEZ.md`, "Simplificações e o efeito delas").

## Protocolo comum a todos os experimentos

- Teste de 10% separado uma vez, antes de qualquer outra coisa, e usado só para a avaliação final.
- Normalização, reamostragem e seleção de hiperparâmetros veem apenas o treino.
- Uma configuração por experimento em arquivo versionado (`project/src/doh_ids/config.py`); seed, versões das bibliotecas, hash dos dados, commit e `dirty` gravados junto com o resultado, no `run.json` (`runlog.save_run`).
- Resultado numérico sempre em arquivo dentro de `results/`, gerado por script. O relatório cita o arquivo.
- Cada tabela do relatório é gerada por código a partir de `results/`, sem digitação manual de números.

## Métricas e quando cada uma engana

| Métrica | Uso aqui | Cuidado |
| --- | --- | --- |
| Acurácia | Comparar com a Tabela II | Com 77% de Non-DoH, um classificador ruim nas classes DoH ainda passa de 99% |
| Precisão, recall, F1 por classe | Métrica principal | Sempre por classe antes de qualquer média |
| Macro | Resumo que respeita a classe rara | Dizer que é macro |
| Ponderada | Só para comparação com a literatura | Esconde a classe benigna |
| AUC-ROC (OvR) | Comparar com a Tabela II | Pouco sensível com classes desbalanceadas |
| AUC-PR | Classe benigna e classe maliciosa | Depende da prevalência do conjunto |
| FPR da classe maliciosa | Leitura operacional | 3 falsos positivos no teste do artigo: intervalo de confiança largo |

## Ordem e esforço

Sequência: E0, depois E1 e E2 juntos, depois E3, E4, E5 e E6 em paralelo, e E8 por último. Datas em [07-pendencias.md](07-pendencias.md).

O dataset tem cerca de 1,16 milhão de linhas e 29 colunas e os modelos são Random Forests pequenos, então tudo deve rodar em notebook pessoal. O que pode pesar é o SMOTE sobre centenas de milhares de amostras e o `GridSearchCV` com 10 folds.

Tempo medido em E1, em uma execução com a seed 42, em máquina de 10 núcleos (`timings` e `cpu_count` dos `run.json` de `project/results/e1/`): 902,3 s no total com profundidade 5 e 2.473,4 s sem limite de profundidade, dos quais 784,9 s e 2.270,3 s são a validação cruzada de 10 folds. Os tempos por etapa de E1 e E2 estão em `project/report/tables/tempos_treino.csv`. O tempo varia entre execuções e não entra em comparação com o artigo. A seleção de hiperparâmetros de E8 no treino inteiro foi estimada em cerca de 8 horas, e por isso roda em subamostra de 25% (decisão 54).
