# Decisões travadas

Fonte única. Não se reabrem sem o usuário. Fato novo que contradiga uma decisão vira `⚠️ REVISAR` no topo da tarefa afetada.

Origem: **U** = respondida pelo usuário no intake; **R** = recomendação técnica adotada como padrão, que o usuário pode reabrir.

01. **[U] Escopo: P1 + P2 + P3.** O plano cobre reprodução, segundo dataset e modificação opcional, mais repositório e relatório. O seminário fica fora deste plano.
    P3 vale ponto extra e reaproveita as críticas do seminário. (afeta: todas)

02. **[U] P3 = M1 + M2; M3 é extra cortável.** M1 troca SMOTE por ponderação de classe (o ajuste de limiar, cogitado no intake, foi retirado depois do red-team: ver decisão 25); M2 devolve a aleatorização de atributos ao Random Forest e seleciona profundidade por busca declarada. M3 (robustez à manipulação de `Duration`) é tarefa separada, a primeira a ser cortada se o prazo apertar.
    M1 e M2 saem quase de graça do protocolo corrigido. (afeta: 15, 16, 20)

03. **[U] Ambiente: uv + `pyproject.toml`, Python 3.12, com `requirements.txt` exportado.** Versões fixadas nas verificadas em `01-discovery-stack.md`.
    Lockfile garante reprodução; o `requirements.txt` atende quem não usa uv. (afeta: 01, 19)

04. **[U] Workspace de planejamento em `planejamento/` (não versionado desde a decisão 32).** Gestão das tarefas só pelos `.md`.
    A pasta de trabalho é compartilhada entre os integrantes por meio fora do Git (`[Preencher: drive da equipe]`). (afeta: —)

05. **[U] Na fase de planejamento não há código nem commit (encerrada pela decisão 28).** O Git de `project/` está inicializado e sem commits. O primeiro commit é da equipe, na tarefa 01.
    Pedido explícito do usuário. (afeta: 01)

06. **[R] Duas trilhas que não se misturam: `fiel` e `corrigida`.** Todo resultado carrega a trilha no caminho e no conteúdo. A trilha fiel segue o texto do artigo mesmo onde o criticamos.
    P1 pede reproduzir o artigo; a correção é contribuição nossa e base de P3. (afeta: 07 a 16)

07. **[R] Código como pacote `src/doh_ids/` + um script por experimento em `scripts/`.** Módulos de função, sem framework e sem hierarquia de classes. Configuração em constantes Python com a origem de cada valor comentada; sem YAML.
    É o mínimo que evita copiar código entre scripts e que a equipe consegue explicar em arguição. (afeta: 02 a 16)

08. **[R] Atributos do modelo: as 29 colunas numéricas do DoHLyzer.** `SourceIP`, `DestinationIP`, `SourcePort`, `DestinationPort` e `TimeStamp` são removidos na carga e nunca chegam ao modelo.
    O rótulo DoH é definido pelo IP de destino no extrator; mantê-los é vazamento por construção. Resolve A2. (afeta: 04)

09. **[R] Empilhamento da trilha fiel: três Random Forests pré-treinados, um por subconjunto balanceado, combinados com `mlxtend.StackingClassifier(fit_base_estimators=False)` e regressão logística.** O meta-classificador é treinado nas predições dos bases sobre o treino original normalizado (amostras reais, sem sintéticas), com `use_probas=False`.
    É a única leitura em que cada base vê um subconjunto diferente, como o artigo descreve, usando a classe que o artigo cita; o Algoritmo 1, linha 5, manda calcular os rótulos "for each sample xn of the training dataset X" antes do empilhamento. As leituras alternativas (`use_probas=True` no núcleo; meta sobre a união dos subconjuntos e `StackingCVClassifier` como opcionais) são variantes da tarefa 10. Consequência conhecida e aceita na trilha fiel: com `use_probas=False` o meta recebe os rótulos 0, 1, 2 como número; a tarefa 08 mede e declara o efeito. Resolve A8, A9, A10. (afeta: 08, 10)

10. **[R] Alvo principal da reprodução: Figura 4b.** A Tabela II é reportada ao lado, com a divergência documentada. Vale até o professor responder Q2.
    A matriz de confusão é o único dado bruto do artigo. (afeta: 06, 08, 17, 18)

11. **[R] Segundo dataset: DoH-Tunnel-Traffic-HKD (transferência) + dataset combinado (retreino).** Vale até o professor responder Q4. Se o combinado não for aceito como "outro conjunto de dados", a tarefa 13 troca a fonte e a 14 se mantém.
    Mesmos atributos, ferramentas de túnel inéditas, custo baixo. (afeta: 13, 14)

12. **[R] Seeds: 42 na trilha fiel; dez seeds (0 a 9) na trilha corrigida e em P3.** A seed controla split, reamostragem e modelos.
    42 é a seed do script dos autores. Dez execuções custam minutos (medido) e dão média e desvio; é escolha nossa, declarada como tal no relatório. Resolve A13. (afeta: 08 a 16)

13. **[R] Trilha fiel sem `class_weight` e sem one-sided selection.** `class_weight` é variante do núcleo da tarefa 10; one-sided selection é variante opcional, a primeira a cortar.
    O texto não menciona `class_weight`; cita one-sided selection sem descrever. Resolve A3 e A14. (afeta: 08, 10)

14. **[R] SMOTE na trilha fiel: classe benigna aumentada até o tamanho da classe maliciosa do subconjunto, `k_neighbors` no padrão da biblioteca.** A razão obtida é reportada ao lado dos 15:12:12 declarados.
    O 15:12:12 do artigo é a razão inicial arredondada (45:1:12) com o Non-DoH dividido por três; com as contagens reais dá 14,3:12:12, e não há subamostragem a reproduzir. Resolve A4 e A6. (afeta: 07)

15. **[R] Hiperparâmetros da trilha fiel são os valores finais do artigo, sem busca.** A única busca do projeto é a de M2, na tarefa 15, com grade declarada por nós e aninhada no treino de cada seed (decisão 25).
    A grade do artigo não foi publicada; refazê-la seria invenção. Resolve A5 e A7. (afeta: 08, 15)

16. **[R] Métricas sempre por classe, depois macro e ponderada, nomeadas.** AUC-ROC one-vs-rest macro; AUC-PR por classe; FPR da classe maliciosa com intervalo de confiança. Para o modelo empilhado, a AUC é reportada de duas formas, nomeadas: pela saída do meta e pela média das probabilidades dos bases.
    A média usada na Tabela II não é informada. Resolve A11 e A12. (afeta: 06)

17. **[R] Dados: CSV bruto em `data/raw/` com SHA-256; Parquet limpo em `data/processed/`; ambos fora do Git.** O download do CIRA é manual (formulário); o script só confere os hashes.
    O site não permite download automatizado (verificado). (afeta: 03, 13)

18. **[R] Resultados em `results/<experimento>/<variante>/`, com métricas em JSON e metadados da execução.** Entram no Git. Tabelas e figuras do relatório são geradas por script a partir deles.
    Nenhum número digitado à mão. (afeta: 02, 17)

19. **[R] Explicabilidade: `TreeExplainer` sobre cada Random Forest base.** O relatório declara que isso não explica a decisão do empilhamento. O painel `explainerdashboard` só é construído se o professor exigir (Q6).
    O `TreeExplainer` rejeita o modelo empilhado (verificado). Resolve A15. (afeta: 12)

20. **[R] Subclassificação por ferramenta de túnel (seção VI-D) fica fora, salvo exigência do professor (Q5).** Existe como tarefa condicional.
    O artigo dá só três acurácias, sem método. Resolve A16. (afeta: 21)

21. **[R] Testes automatizados com pytest sobre dados sintéticos pequenos; as verificações que dependem do dataset real ficam como asserções dentro dos scripts.**
    Os testes rodam sem os dados, que estão fora do Git. (afeta: 02 a 11)

22. **[R] Tempo de treino é medido e reportado, sem comparação com a "redução de três vezes" do artigo.**
    O artigo não publica nenhum tempo. Resolve A17. (afeta: 08, 09)

23. **[R] Trilha corrigida = avaliação em dez seeds com configurações fixadas antes, sem busca.** Três modelos: A, empilhado com os valores do artigo; B, Random Forest único com os mesmos hiperparâmetros (10, 5, 28) e SMOTE; C, Random Forest único como na Tabela II (10 árvores, resto no padrão) e SMOTE. O meta do modelo A é treinado como na trilha fiel.
    A contra B isola a arquitetura; A contra C é a comparação do artigo. Uma busca única contaminaria os testes das outras seeds, e uma busca por seed com SMOTE não cabe no prazo (red-team F1, F2, F15). (afeta: 11)

24. **[R] Comparação entre modelos: pareada por seed, com contagem de vitórias e teste de postos sinalizados de Wilcoxon, sempre com a ressalva de que os dez testes se sobrepõem.**
    Fixado antes de ver os números, para não escolher o teste pelo resultado (red-team F10). (afeta: 11, 15)

25. **[R] Modelo modificado de P3: Random Forest único, sem SMOTE, com `class_weight='balanced'` e hiperparâmetros selecionados por validação cruzada de 5 folds dentro do treino de cada seed, com o scaler dentro do `Pipeline`.** Arquitetura fixada antes dos resultados da tarefa 11. Comparado contra o modelo A. No combinado, a seleção é refeita dentro do treino do combinado. Sem variante de ajuste de limiar e sem variante "só M2".
    Sem SMOTE, a divisão em três subconjuntos perde a razão de ser; escolher a arquitetura pelo teste violaria I5; o limiar não tem sobre o que operar no empilhado e não está definido para três classes (red-team F3, F4, F5). (afeta: 15, 16)

26. **[R] Valores de trilha: `fiel`, `corrigida`, `variante` (leituras alternativas da tarefa 10) e `dados` (E0 e preparação do segundo dataset).** `metrics.json` só tem valores determinísticos; tempos e datas ficam no `run.json`.
    As variantes de E3 não são nem fiel nem corrigida, e E0 não treina modelo (red-team F12, F6). (afeta: 02, 04, 10, 13, 17)

27. **[R] Experimentos congelados em 13/11; primeira execução limpa em 10/11; fluxo repositório → Overleaf definido na onda 0.**
    O relatório é o maior risco de prazo (red-team F13). (afeta: 17, 18, 19)

28. **[U] A implementação é feita pelo agente `implementador`, uma tarefa por vez, no ciclo implementa → testa → revisa → integra.** A tarefa seguinte não começa com a anterior vermelha. Substitui a decisão 05 a partir da tarefa 01: código e commits passam a ser produzidos, dentro desse ciclo.
    Pedido do usuário em 07/10/2026: desenvolvimento em fila, como em um time. (afeta: todas; `.claude/rules/fluxo-implementacao.md`)

29. **[U] Commits sem `Co-Authored-By` nem assinatura de ferramenta, e todo commit com lint e formatação verdes.** Garantido por hooks (`pre-commit`, `commit-msg`) e pelo CI. O uso de assistente de IA está aprovado (decisão 33).
    Pedido do usuário em 07/10/2026. (afeta: 01, 19; `.claude/rules/commits.md`)

30. **[U] Código direto, sem excesso de engenharia: funções com docstring, comentário só para regra do artigo ou decisão com motivo, e nenhuma referência no código a arquivo de `docs/`, `planejamento/` ou `.claude/`, a número de tarefa, de decisão ou a identificador de ambiguidade.** A fonte citável no código é a seção, tabela ou figura do artigo. O rastro ambiguidade → código fica em `docs/02-artigo.md`.
    Pedido do usuário em 07/10/2026. Muda a regra anterior de citar o ID da ambiguidade no comentário. (afeta: 02, 08, 09, 19, 22; `.claude/rules/codigo.md`)

31. **[U] Testes só da funcionalidade macro e dos pontos de erro silencioso, com dados sintéticos, rodando no CI do GitHub; um plano de testes por tarefa.** O que depende dos datasets é verificação local, por asserção no script, registrada no pull request.
    Pedido do usuário em 07/10/2026. O CI não tem acesso aos dados, que ficam fora do Git. (afeta: todas; `plan/PLANO-DE-TESTES.md`, `.claude/rules/testes.md`)

32. **[U] O repositório Git do projeto é a pasta `project/`, dentro da pasta de trabalho.** Só ela tem Git e só ela é entregue. `docs/`, `planejamento/`, `.claude/`, `CLAUDE.md` e `LEIA-ME.txt` ficam fora e não são versionados. Todo caminho de código do plano é relativo a `project/`. Resolve D4 (não versionar) e altera a decisão 04.
    Pedido do usuário em 07/10/2026: repositório limpo, só com o projeto. (afeta: 01 e todas as de código; `scripts/metricas_fig4.py` é movido na tarefa 01)

33. **[U] Uso de assistente de IA aprovado na disciplina; commits sem coautoria por limpeza e padrão do repositório.** Resolve Q7. Se o relatório precisa de frase de declaração fica a confirmar com o professor.
    Informado pelo usuário em 07/10/2026. (afeta: 18, 19)

34. **[R] Limpeza do CIRA: remover as linhas com NaN, e só isso.** Reproduz a Tabela I exatamente (889.809 / 19.746 / 249.553). Fonte: `l1-nondoh.csv`, `l2-benign.csv` e `l2-malicious.csv` de `Total_CSVs.zip`, lidos direto do zip; `l1-doh.csv` não é lido. Duplicatas nos 29 atributos ficam. Resolve A1.
    Medido em 07/10/2026 (`docs/08-inventario-dados.md`). É a regra que a tarefa 04 já mandava adotar: a que reproduz a Tabela I. (afeta: 03, 04, 05)

35. **[R] O split usa `test_size=0.1`, sem forçar o tamanho do teste.** O teste fica com 115.911 amostras, uma de Non-DoH a mais que na Fig. 4b.
    É o parâmetro do script dos autores; forçar 115.910 seria ajustar para o número bater. O arredondamento do scikit-learn explica o nosso 115.911; a causa do 115.910 do artigo é desconhecida. A diferença mínima de 1 é declarada. (afeta: 05, 06, 08)

36. **[R] Segundo dataset: transferência com os 5.258 fluxos de `Total-48h.csv`; retreino no combinado reportado como publicado e sem as réplicas do HKD; as dez seeds de P3 só sem réplicas.** O arquivo "aumentado" do HKD, que é o que entra no combinado, repete cada fluxo 20 vezes.
    Com as réplicas, o split aleatório põe cópias idênticas em treino e teste e o resultado para as ferramentas novas é memorização. Medido em 07/10/2026. Muda o desenho de E6 em relação à decisão 11: reabrível pelo usuário. (afeta: 13, 14, 15)

37. **[R] Grupo de um fluxo é a máquina local (`192.168.20.x` na origem ou no destino); janela de tempo é o dia.** Só `group` vai para o Parquet do CIRA; o dia é usado na tabela de período por classe da tarefa 04 e não é gravado. A avaliação por grupo da tarefa 11, se feita, usa quatro dobras: uma máquina benigna e um quarto das dez maliciosas de fora por dobra. Não se aplica ao segundo dataset (decisão 40).
    Os fluxos são bidirecionais e `SourceIP` às vezes é o resolvedor; há só quatro máquinas com tráfego benigno e Non-DoH. (afeta: 04, 11)

38. **[R] Layout único de `results/`: `results/<experimento>/<trilha>/<recorte>/seed<k>/metrics.json` e `run.json`, montado por `save_run`.** `<recorte>` é o modelo, a variante ou o cenário (`proposto` em E1 e E5; `<modelo>` em E2 e E4; `<variante>` em E3 sob a trilha `variante`; `transferencia`, `retreino_publicado` e `retreino_sem_replicas` em E6; `<modelo>-<dataset>` e `robustez-<variante>` em E8; `cira`, `hkd`, `combinado` e `combinado_sem_replicas` sob a trilha `dados`, com a seed do split). Arquivos auxiliares nomeados ficam no mesmo diretório. A interpretação fica em `results/<experimento>/<trilha>/RESUMO.md`; a hipótese escrita antes de rodar, em `HIPOTESE.md` no mesmo nível, em commit anterior à primeira execução. Resultado é gerado com a árvore limpa, depois do commit do código, e entra em commit `exp`; o `run.json` registra o commit e `dirty: false`.
    Sem um padrão, `save_run` não sabe montar o caminho, o G6 não acha o `metrics.json`, a decisão 06 (trilha no caminho) falhava em E3, e resumo e hipótese não tinham arquivo (revisão de 07/10/2026). (afeta: 02, 04, 05, 08 a 16, 17)

39. **[R] A tarefa 14 roda assumindo a decisão 11, sem esperar a resposta a Q4.** Só a justificativa final da tarefa 13 e o texto do relatório esperam a resposta. Se for "não", a 13 troca a fonte e a 14 roda de novo.
    Esperar travaria 14, 15, 16, 17, 18 e 19, que são o caminho crítico; o custo de rodar sem a resposta é uma execução a mais. (afeta: 13, 14)

40. **[R] Esquema do segundo dataset: 29 atributos, `label`, `origin` (CIRA ou HKD) e `tool`; sem `group` nem `time_window`.** Três Parquets: `hkd`, `combinado` e `combinado_sem_replicas`. O CIRA mantém 29 atributos, `label` e `group`.
    No HKD todas as linhas têm as duas máquinas locais (`192.168.11.12` e `.16`), uma em cada ponta, e a regra de `group` do CIRA não se aplica (medido em 07/10/2026). (afeta: 04, 13, 14, 15)

41. **[R] Seeds derivadas: o SMOTE do subconjunto `i` usa `seed * 100 + i`; os Random Forests e o meta-classificador usam `seed`.** Declarado em `config.py`.
    Sem colisão entre seeds 0 a 9 e 42, e sem valor escolhido pelo implementador. (afeta: 02, 07)

42. **[U] A execução com dados reais (N2 das tarefas 08 a 16 e a execução limpa final) pode ser feita na máquina local ou no cluster Apuana do CIn; o importante é treinar e gerar a evidência.** A evidência é a mesma nos dois casos: resultados em `results/`, `run.json` com máquina, núcleos, versões, hash dos dados e commit, saída colada no pull request e commit `exp` de quem rodou, com a árvore limpa. Desenvolvimento e testes N1 são locais. Cada tarefa de experimento tem dois fechamentos: "pronta" (código, N1 e revisão) e "executada" (rodada com os dados reais). A seguinte pode começar com a anterior "pronta", salvo quando depende de resultado real (05, 11, 15, 17). Atualiza D3 de `docs/07-pendencias.md`.
    Pedido do usuário em 07/10/2026. O Apuana usa Slurm, com acesso por formulário e `/home` compartilhado (página do Helpdesk do CIn, 07/10/2026); acesso de graduação, partições, limites e versão do Python não foram verificados. Os modelos treinam em minutos na máquina local, então o cluster é opção, não requisito. Resultados versionados e execução limpa saem do mesmo ambiente, porque máquinas diferentes podem divergir em casas decimais. (afeta: 01, 02, 03, 08 a 16, 19, 23; `.claude/rules/fluxo-implementacao.md`)

## Pendentes da equipe (valores que o implementador não pode escolher)

Cada item tem uma proposta; a equipe confirma ou troca antes da tarefa indicada, e o valor vai para `config.py` ou para o arquivo citado. Enquanto não decidido, a tarefa para nesse ponto.

| Item | Proposta (a confirmar) | Tarefa | Antes de |
| --- | --- | --- | --- |
| Licença do repositório | MIT, com nota de uso acadêmico e citação do artigo e dos datasets | 01 | tarefa 01 |
| Visibilidade do repositório (Q10 enviada) | privado com acesso para o professor até a resposta | 01 | tarefa 01 |
| Dono de cada tarefa (D5) | `[Preencher]` na tabela de ondas de `plan/00-README.md`; cada um roda o ciclo na própria máquina | 00-README | tarefa 01 |
| Link do drive da equipe (dados e pasta de trabalho) | `[Preencher]` | 03, decisão 04 | tarefa 03 |
| `.git` vazio na pasta de trabalho, acima de `project/` (apareceu em 07/10/2026) | remover (`rm -rf .git` na pasta de trabalho); a decisão 32 diz que só `project/` tem Git | — | tarefa 01 |
| Metade inferior da Tabela II (resultados de outros trabalhos) | copiar do manuscrito para `config.py`, com as referências, conferido por dois integrantes | 06 | tarefa 06 |
| Prevalências hipotéticas da taxa base | 10⁻³, 10⁻⁴ e 10⁻⁵ (o script `metricas_fig4.py` já usa 10⁻⁴) | 11 | tarefa 11 |
| Tamanho das amostras do SHAP | 2.000 fluxos por classe, estratificados, uma amostra do treino e uma do teste | 12 | tarefa 12 |
| Grade de M2 | profundidade {5, 10, sem limite} × árvores {10, 100} com `max_features` `sqrt`, mais a combinação do artigo (10 árvores, profundidade 5, 28): sete combinações | 15 | tarefa 15 |
| Fração da subamostra para a seleção, se o tempo exigir | 25% do treino, estratificada | 15 | tarefa 15 |
| Fatores de fragmentação | 2, 4, 8 e 16 | 16 | tarefa 16 |
| Acesso ao Apuana, só se a equipe for usá-lo: formulário do Helpdesk do CIn | `[Preencher: quem pediu, data, situação]` | 08 | tarefa 08 |
| Python 3.12 e uv no cluster; partição e recursos a pedir (só se for usar o Apuana) | `[Preencher: conferir no cluster ou com cluster.apuana-l@cin.ufpe.br]` | 01, 08 | tarefa 08 |
| Quem desenvolve e quem executa cada tarefa | `[Preencher]` na tabela de ondas de `plan/00-README.md` | todas | tarefa 01 |
| `N_JOBS` de `config.py`, igual ao `--cpus-per-task` dos jobs quando houver | `[Decidir: valor]` | 02 | tarefa 08 |

## Pendentes de terceiros (não são decisões nossas)

| Pendência | Decisão que pode mudar | Tarefa afetada |
| --- | --- | --- |
| Q1 reimplementação aceita? | — (premissa de todo o plano) | todas |
| Q2 alvo e tolerância | 10 | 08, 18 |
| Q9 idioma e limite de páginas | lista de tabelas | 17, 18 |
| Q3 requisito adicional | pode criar tarefa nova | — |
| Q4 segundo dataset | 11 (as tarefas seguem assumindo; decisão 39) | 13, 14 |
| Q5 ferramenta de túnel | 20 | 21 |
| Q6 painel | 19 | 12 |
| Q7 política de IA | resolvida (decisão 33) | 18, 19 |
