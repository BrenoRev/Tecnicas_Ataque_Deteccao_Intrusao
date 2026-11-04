# Depois da implementação: o que falta fazer, documentar e evidenciar

Este documento cobre o trecho entre "o código das tarefas está pronto" e "a entrega foi feita e defendida". Ele não substitui o plano: aponta para a tarefa que detalha cada item. Marque cada caixa só com a evidência indicada na mão.

**Situação em 08/10/2026, no commit `759ec29` (branch `tarefa/24-entregaveis`).** O código de todas as tarefas de experimento está pronto e executado, e o relatório e a apresentação foram gerados. As caixas marcadas abaixo trazem o caminho da evidência. As não marcadas são, quase todas, de pessoa: integrar, conferir, ensaiar, conversar com o professor. Os caminhos de `results/`, `report/`, `scripts/` e `data/` são relativos a `project/`.

**Regra geral de evidência.** Nada vale por estar dito. Cada item fecha com um arquivo no repositório, uma saída de comando colada no pull request ou um registro datado em `docs/07-pendencias.md`. Nenhum número é digitado à mão: vem de `results/` ou de `report/tables/`.

**Onde roda.** A execução com dados reais pode ser na máquina de um integrante ou no cluster Apuana; as duas valem (decisão 42). Na prática, tudo rodou na máquina local, na própria sessão de implementação (decisão 44); o Apuana não foi usado. Os resultados versionados e a execução limpa final devem sair do mesmo ambiente, porque máquinas diferentes podem divergir em casas decimais.

**Onde está o repositório.** O repositório Git é a raiz da pasta de trabalho, público no GitHub (decisão 43); o código fica em `project/`, e `docs/`, `planejamento/` e `.claude/` são versionados junto. `origin/main` está em `6bf80bd`: nenhuma branch de tarefa foi integrada ainda.

## Datas

| Data | O que acontece | Situação |
| --- | --- | --- |
| 09/11 | Decidir se P3 (modificação) continua | meta interna; já decidido: P3 foi feito em 08/10/2026 |
| 10/11 | Acompanhamento com o professor; primeira execução limpa | calendário da disciplina |
| 13/11 | Experimentos congelados: depois disso, só correção | meta interna; os experimentos já rodaram em 07 e 08/10/2026 |
| 17/11 | Acompanhamento com o professor, com o rascunho do relatório | calendário da disciplina |
| 18/11 | Entrega: relatório em PDF e link do GitHub | prazo da especificação |
| 19/11 | Apresentação de 15 minutos | prazo da especificação; obrigatória, porque há P3 |

Local de entrega: `[Preencher: Classroom?]`.

## 1. Rodar tudo com os dados reais

Uma tarefa de experimento está "pronta" com código, testes e revisão, e "executada" quando rodou com os dados reais. Só a executada vira número no relatório.

- [ ] Dados conferidos na máquina (ou no cluster) em que os experimentos rodam: `uv run python data/verify.py` com código 0. Os scripts conferem o SHA-256 do arquivo que leem e o gravam em `data_sha256` no `run.json`; a saída do `verify.py` não está registrada em arquivo e não foi conferida nesta sincronização.
- [x] Cada script rodado com a árvore do Git limpa: E0 a E8, em 07 e 08/10/2026. Evidência: `results/e0/` a `results/e8/`, 229 arquivos `run.json` com data de 07 ou 08/10/2026; os resumos de E3, E7 e E8 listam o commit de cada grupo de execuções e zero execuções com a árvore suja. Falta só "na ordem do README": o README ainda não lista a ordem (tarefa 19).
- [ ] Segunda execução de cada script com `metrics.json` idêntico ao da primeira, na mesma máquina. Não conferida nesta sincronização.
- [x] Resultados em commit `exp`, separado do código. Evidência: `git log --oneline --grep '^exp('`. Todos saíram de uma só identidade Git, a de quem rodou a sessão.

Evidência por experimento, em `results/<experimento>/<trilha>/`:

| Arquivo | O que prova |
| --- | --- |
| `metrics.json` | o número, determinístico |
| `run.json` | trilha, seed, versões, hash dos dados, commit, `dirty: false`, máquina e núcleos |
| `RESUMO.md` | a interpretação: o que o número significa, o que foi medido e o que é hipótese |
| `HIPOTESE.md` (E4, E6 e E8; em E8 também `HIPOTESE-ROBUSTEZ.md`) | escrita em commit anterior à primeira execução. E3 e E7 rodaram sem hipótese escrita, e os resumos deles declaram isso |
| saída do script no pull request | as asserções com dados reais passaram |

## 2. Conferir que cada requisito do professor tem evidência

O mapa completo está em `planejamento/plan/ENTREGAS-DEMONSTRAVEIS.md`. Os três objetivos:

- [x] **P1, reprodução.** Matriz de confusão da reprodução ao lado da Fig. 4b, célula a célula, com a diferença; baselines ao lado da Tabela II; figuras SHAP equivalentes às Figs. 5 a 8. A distância ao artigo é reportada como está, sem ajuste para o número bater. Evidência: `results/e1/RESUMO.md` (Figs. 4a e 4b, nas duas leituras de profundidade), `results/e2/fiel/RESUMO.md` (Tabela II inteira), `results/e5/RESUMO.md` (Figs. 5 a 8), `results/e0/dados/RESUMO.md` (Tabela I e Fig. 2), `results/e7/RESUMO.md` (Seção VI-D e Fig. 9). O alvo passou a ser todas as tabelas e gráficos de resultado (decisão 46). Falta a conversa com o professor sobre as duas leituras de profundidade.
- [x] **P2, segundo dataset.** Recall por ferramenta na transferência para o HKD; retreino no combinado como publicado e sem réplicas; parágrafo que justifica a escolha do dataset. Evidência: `results/e6/RESUMO.md`; justificativa em `results/e6/dados/RESUMO.md`, seção "Justificativa da escolha do segundo dataset". O dataset principal é o combinado sem réplicas, em que tudo de P1 é refeito (decisão 47). Falta: o professor não comentou que Non-DoH e Benign-DoH do combinado são os do CIRA; a justificativa final espera essa conversa.
- [x] **P3, modificação.** Original contra modificado nos dois datasets, dez seeds, com e sem as linhas duplicadas. Evidência: `results/e8/corrigida/RESUMO.md` (M1, M1M2) e `results/e8/corrigida/RESUMO-ROBUSTEZ.md` (robustez à duração, que é perturbação no espaço de atributos, não tráfego gerado). O resumo traz o veredito pela regra fixada antes da execução e o que ficou de fora.

Dois pontos que a especificação cobra explicitamente:

- [x] Contagem de amostras por classe em treino, validação e teste, para os **dois** datasets. Não há conjunto de validação separado: a validação é cruzada, e a tabela mostra o tamanho por fold. Evidência: `report/tables/dados_cira_contagens` e `report/tables/dados_segundo_contagens` (origem em `report/INDICE.md`).
- [ ] Seção 7 com discussão e comparação com outros trabalhos, não só tabela de números. O texto está em `report/relatorio.tex`; falta a leitura por um integrante.

## 3. Gerar tabelas e figuras (tarefa 17)

- [ ] Template Overleaf lido antes: idioma, limite de páginas, estilo de tabela. O relatório foi feito sobre `geracao_latex_and_pdf/template.tex` (IEEEtran, decisão 53); falta conferir contra o template indicado pelo professor no Overleaf. Idioma e limite de páginas seguem sem resposta (Q9).
- [x] `uv run python scripts/make_report_assets.py` gera `report/tables/` e `report/figures/` a partir de `results/`. Evidência: `report/tables/` (30 tabelas, cada uma em `.tex` e `.csv`), `report/figures/` (13 figuras, cada uma em `.pdf` e `.png`) e `report/INDICE.md`, que liga cada item à origem.
- [ ] Apagar `report/tables/` e rodar de novo dá arquivos idênticos. Não conferido nesta sincronização.
- [ ] Três números de cada tabela conferidos contra o `metrics.json` de origem, com o registro no pull request. De pessoa.
- [ ] Toda tabela de modelo traz na legenda a trilha, a seed ou o número de seeds e o nome da média. Toda figura tem eixo rotulado e unidade. As legendas sugeridas de `report/INDICE.md` trazem trilha, seed e média; falta a conferência no PDF.

## 4. Escrever o relatório (tarefas 18 e 24)

Formato de artigo, no template Overleaf indicado, entregue em PDF, com referências IEEE.

O relatório foi gerado na tarefa 24 (decisão 53) e os achados da revisão de texto foram tratados (commit `17a278b`): `report/relatorio.tex` e `report/relatorio.pdf`, 8 páginas, no teto da decisão 53. O `.tex` exige **XeLaTeX** (usa `fontspec`); no Overleaf, escolher XeLaTeX no menu do compilador. As caixas abaixo continuam abertas porque pedem leitura e conferência de pessoa sobre um texto que já existe.

- [ ] As nove seções existem: resumo, introdução, trabalhos relacionados, modelo de ameaça, sistema do artigo, solução da equipe (só com P3), metodologia, resultados e discussões, conclusão, referências.
- [ ] Lista de conferência preenchida: cada pergunta da especificação com a seção e o parágrafo que a responde.
- [ ] Figuras que nenhum script gera, feitas à mão pela equipe: túnel DNS sobre DoH com as premissas do atacante (seção 3), pipeline e algoritmo de treino (seção 4), modelo modificado ao lado do original (seção 5, com P3).
- [ ] Declarado no texto: o sistema foi reimplementado a partir do artigo, porque o código público não contém o modelo; a leitura adotada em cada ponto que o artigo deixa em aberto; a divergência entre a Tabela II e a Fig. 4b do próprio artigo.
- [ ] Limitações medidas, cada uma com o número vindo de `results/`: classe maliciosa capturada em outras máquinas e em outro período; 13,7% do teste com vetor idêntico no treino; 326 vetores em mais de uma classe; teste com uma amostra a mais que o do artigo; HKD replicado 20 vezes no combinado; valor `-10` nas colunas de assimetria.
- [ ] Todo número do texto confere com `report/tables/` ou com o artigo. Toda afirmação sobre o artigo cita seção, tabela ou figura.
- [ ] Cada referência conferida na fonte, com DOI, citada no texto. Atenção à citação do dataset CIRA: `docs/04-dados.md` e `data/README.md` trazem "IEEE Cyber Science and Technology Congress, 2020"; o relatório seguiu a lista do artigo, "2020 IEEE Intl Conf on Dependable, Autonomic and Secure Computing, pp. 63–70". Confirmar no IEEE Xplore.
- [ ] Transcrições do manuscrito conferidas por dois integrantes: metade inferior da Tabela II (`TABLE_II_LITERATURE`), `FIG5_RANKING`, `FIG7_MALICIOUS` e `FIG8_NON_DOH`, em `src/doh_ids/config.py`.
- [ ] Uso de assistente de IA: aprovado na disciplina. A frase de declaração entra no relatório e no README só se o professor pedir.
- [ ] Agente `revisor-de-texto` sem achado grave em aberto e leitura cruzada por outro integrante. A revisão automática foi feita e os achados tratados (commits `17a278b` e `dc5fb1c`); falta a leitura cruzada.
- [ ] PDF compila sem erro e sem referência quebrada. O PDF versionado foi gerado localmente; falta compilar no Overleaf com XeLaTeX.

## 5. Fechar o repositório (tarefa 19)

A especificação pede "link do GitHub com todos os códigos comentados".

- [ ] README completo: o que é o projeto, integrantes, instalação com uv e com pip, como obter e conferir os dados, ordem dos scripts, tempo medido de cada um, limitações, e a tabela "resultado do relatório → script → arquivo em `results/`" cobrindo todas as tabelas e figuras. Hoje o README de `project/` tem objetivo, instalação, dados e contribuição, mas ainda diz que os scripts "serão listados aqui"; a ordem, os comandos (`python -m` nos scripts que importam outro) e a tabela de resultados faltam. A base da tabela já existe em `report/INDICE.md`.
- [ ] README registra onde os resultados versionados foram gerados: máquina e versões.
- [ ] Comentários revisados: docstring em toda função pública; comentário de decisão nos pontos em que o artigo é omisso, citando a seção do artigo; nenhuma referência a documento interno.
- [ ] **Execução limpa** por quem não escreveu o código, em diretório novo: clonar, instalar, colocar os dados, `data/verify.py`, rodar os scripts na ordem do README e comparar os `metrics.json` com os versionados. Primeira tentativa em 10/11; a final começa em 16/11.
- [ ] Instalação pelo `requirements.txt` com pip testada.
- [ ] Higiene: sem dados, sem modelo serializado, sem o PDF do artigo, sem credencial, sem caminho de máquina. Os comandos de conferência são os do CI.
- [ ] CI verde na `main` no commit entregue.
- [ ] `git shortlog -sn` mostra os quatro integrantes; nenhum commit com coautoria de ferramenta. Em `759ec29`, os 137 commits são de uma só identidade. A equipe decide como a contribuição de cada um fica registrada (revisão e integração dos pull requests).
- [ ] `push` das branches e pull requests na ordem das tarefas. `tarefa/17-tabelas-figuras` e `tarefa/24-entregaveis` não estão no remoto, e `tarefa/16-robustez` está à frente da cópia remota.
- [ ] Licença: não há arquivo `LICENSE`, e o README traz "Licença: [Preencher]".
- [ ] Acesso do professor ao repositório, público ou privado conforme a resposta dele. O repositório está público (decisão 43); Q10 segue sem resposta.

## 6. Acompanhamento com o professor (tarefa 23)

- [ ] Cada resposta às perguntas enviadas em 07/10 registrada em `docs/07-pendencias.md`, com data, e a tarefa afetada ajustada. Feito para Q1 a Q6 (respondidas em 07/10/2026; decisões 46 a 50). Sem resposta: Q9, Q10 e a frase de declaração de IA (Q7).
- [ ] Conversa com o professor sobre três pontos: as duas leituras de profundidade (Seção IV-B contra a linha 3 do Algoritmo 1) e o resultado da profundidade 5; o combinado como "outro conjunto de dados", com Non-DoH e Benign-DoH iguais aos do CIRA; e Q5, a explicação que ele pediu sobre a ferramenta de túnel.
- [ ] **10/11:** uma página com o que funciona, o que falta e o que travou; tabela de resultados (reprodução ao lado da Fig. 4b, segundo dataset); resultado da primeira execução limpa. Se os experimentos rodaram no Apuana e a equipe quer que isso conte, dizer.
- [ ] **17/11:** rascunho completo do relatório e as dúvidas que restarem.
- [ ] Retorno de cada encontro registrado e convertido em ajuste.

## 7. Entrega em 18/11

- [ ] Skill `checklist-entrega projeto` rodada, com `OK`, `Pendente` ou `Não aplicável` em cada item e nenhum item exigido pendente.
- [ ] PDF do relatório e link do GitHub enviados.
- [ ] Guardar o comprovante: data, hora e hash do commit entregue, em `docs/07-pendencias.md`.

## 8. Apresentação em 19/11 (tarefas 20 e 24)

Obrigatória: P3 foi feito. A apresentação é entregue em **PPTX**, no modelo do CIn, para subir no Google Slides (decisão 53).

- [ ] Confirmar com o professor o que a apresentação deve cobrir.
- [x] Slides no modelo institucional do CIn, só tópicos e imagens, com todo número e gráfico vindo de `report/`. Evidência: `report/apresentacao.pptx` (14 slides), gerado por `scripts/make_slides.py` (`uv run --group slides python scripts/make_slides.py`) a partir de `report/figures/` e `report/tables/`.
- [x] Um slide para o artigo, no máximo; o resto é reprodução, segundo dataset e modificação. Evidência: `report/roteiro.md` (slide 2, "O artigo em um slide").
- [ ] Conferir o PPTX aberto no Google Slides: fontes, tabelas nativas e imagens.
- [ ] Fala dividida entre os quatro e ensaio cronometrado em 15 minutos. O roteiro soma 11 min 55 s e traz uma proposta de divisão por blocos de slides (`report/roteiro.md`); a equipe confirma a divisão e faz o ensaio.
- [x] `revisor-de-texto` sobre os slides. Evidência: commit `dc5fb1c`, que ajusta os slides aos achados da revisão.

## 9. Preparar a arguição

O trabalho é defendido em sala. Ninguém assina o que não consegue explicar.

- [ ] Cada integrante explica, linha a linha, o código da parte que apresenta.
- [ ] Todos sabem responder: por que a reimplementação conta como reprodução; por que há duas leituras de profundidade e por que a de profundidade 5 perde uma classe; quais são os alvos (todas as tabelas e gráficos de resultado, com a Fig. 4b e a Tabela II lado a lado); quão perto ficamos e o que explica a diferença; por que as trilhas fiel, variante e corrigida não se misturam; por que este segundo dataset e por que sem réplicas; por que a transferência para o HKD falha; o que a robustez de E8 mede e o que não mede; o que cada limitação medida faz com os resultados.
- [ ] Perguntas prováveis distribuídas entre os quatro.

## 10. Fechamento interno

- [ ] Agentes `cin0114-plan-sync` e `cin0114-doc-sync` rodados depois da última tarefa: plano e `docs/` refletem o que foi implementado. Rodados em 08/10/2026 sobre o commit `759ec29` (`planejamento/MEMORY/SYNC-BASELINE.md`); rodar de novo depois das tarefas 19 e 22 e da integração.
- [ ] Tarefa 22: padrões que nasceram na implementação registrados ou dispensados com justificativa.
- [ ] `planejamento/MEMORY/STATUS.md` atualizado com a situação final. Atualizado em 08/10/2026 com a situação de `759ec29`; a final vem depois da entrega.

## Pendências que travam itens acima

| Pendência | Trava | Quem resolve |
| --- | --- | --- |
| Respostas do professor que faltam: páginas e idioma (Q9), visibilidade (Q10), declaração de IA (Q7). Reimplementação, alvo, segundo dataset, ferramenta de túnel e painel foram respondidas em 07/10/2026 | seções 4, 5 e 7 | professor |
| Conversa com o professor: duas leituras de profundidade; o combinado como "outro dataset"; Q5 | seções 2, 4 e 6 | equipe e professor |
| Template Overleaf do professor não conferido; o `.tex` exige XeLaTeX | seções 3 e 4 | equipe |
| `push` e pull requests; quem revisa e integra cada um | seções 1 e 5 | equipe |
| Licença do repositório | seção 5 | equipe |
| Transcrições do manuscrito conferidas por dois: metade inferior da Tabela II, `FIG5_RANKING`, `FIG7_MALICIOUS`, `FIG8_NON_DOH` | seções 3 e 4 | equipe |
| Citação do dataset CIRA e DOI das referências | seção 4 | equipe |
| README com a ordem dos scripts e execução limpa (tarefa 19) | seção 5 | equipe |
| PPTX conferido no Google Slides, divisão da fala e ensaio | seção 8 | equipe |
