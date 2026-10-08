# Depois da implementação: o que foi feito, com a evidência, e o que resta

Este documento cobre o trecho entre "o código das tarefas está pronto" e "a entrega foi feita e defendida". Ele não substitui o plano: aponta para a tarefa que detalha cada item.

**Situação em 08/10/2026, no commit `5999c1b` (branch `tarefa/19-readme-execucao-limpa`).** O projeto está implementado, executado com os dados reais, revisado e com os entregáveis gerados. Cada caixa marcada traz o caminho da evidência. As caixas trocadas por "não se aplica" trazem a decisão que as superou. **As caixas abertas não formam uma lista própria:** cada uma aponta para o item correspondente da lista única, em [docs/07-pendencias.md](docs/07-pendencias.md), seção "O que resta de pessoa". Os caminhos de `results/`, `report/`, `scripts/` e `data/` são relativos a `project/`.

**Regra geral de evidência.** Nada vale por estar dito. Cada item fecha com um arquivo no repositório, uma saída de comando ou um registro datado em `docs/07-pendencias.md`. Nenhum número é digitado à mão: vem de `results/` ou de `report/tables/`.

**Onde rodou.** Tudo rodou na máquina local, na própria sessão de implementação (decisão 44). O cluster Apuana, admitido pela decisão 42, não foi usado: os itens sobre ele não se aplicam. Os resultados versionados e a execução limpa saíram da mesma máquina.

**Onde está o repositório.** O repositório Git é a raiz da pasta de trabalho, público no GitHub (decisão 43); o código fica em `project/`, e `docs/`, `planejamento/` e `.claude/` são versionados junto. A integração foi por avanço direto da `main`, sem pull request por tarefa (decisão 55f): onde este documento pedia "registro no pull request", vale o arquivo versionado. `main` e `origin/main` estão em `378f170`; os 15 commits seguintes, até `5999c1b`, ainda não foram enviados (item 1 da lista única).

## Datas

| Data | O que acontece | Situação |
| --- | --- | --- |
| 09/11 | Decidir se P3 (modificação) continua | meta interna; cumprido em 07 e 08/10/2026: P3 foi feito (`results/e8/corrigida/`) |
| 10/11 | Acompanhamento com o professor; primeira execução limpa | calendário da disciplina; a execução limpa foi cumprida em 08/10/2026 |
| 13/11 | Experimentos congelados: depois disso, só correção | meta interna; cumprido em 07 e 08/10/2026: os experimentos rodaram e a execução limpa os regenerou |
| 17/11 | Acompanhamento com o professor, com o relatório | calendário da disciplina |
| 18/11 | Entrega: relatório em PDF e link do GitHub | prazo da especificação |
| 19/11 | Apresentação de 15 minutos | prazo da especificação; obrigatória, porque há P3 |

Local de entrega: `[Preencher: Classroom?]` (item 5 da lista única).

## 1. Rodar tudo com os dados reais

- [x] Dados conferidos na máquina em que os experimentos rodam: `uv run python data/verify.py`. Evidência: é o passo 1 dos 22 de `scripts/execucao_limpa.sh`, que rodaram sem erro na execução limpa (`planejamento/plan/REVISAO-FINAL.md`, "Execução limpa"); o hash dos quatro Parquets é igual ao gravado (mesmo arquivo, V1).
- [x] Cada script rodado com a árvore do Git limpa, na ordem do README. Evidência: 229 arquivos `run.json` em `results/`, todos com `dirty: false` (lido em `5999c1b`); a ordem dos 22 passos está em `project/README.md`, "Ordem dos scripts".
- [x] Segunda execução de cada script com `metrics.json` idêntico. Evidência: execução limpa de 08/10/2026, em clone novo: 260 de 260 arquivos de `results/` conferem (`planejamento/plan/REVISAO-FINAL.md`, "Execução limpa"). Dois `metrics.json` de SHAP do segundo conjunto ganharam chaves novas, com as 521 chaves comuns iguais, e foram regravados (commit `97b2c8c`).
- [x] Resultados em commit `exp`, separado do código. Evidência: `git log --oneline --grep '^exp('`. Todos saíram de uma só identidade Git (decisões 44 e 55d).

Evidência por experimento, em `results/<experimento>/<trilha>/`:

| Arquivo | O que prova |
| --- | --- |
| `metrics.json` | o número, determinístico |
| `run.json` | trilha, seed, versões, hash dos dados, commit, `dirty: false`, máquina e núcleos |
| `RESUMO.md` | a interpretação: o que o número significa, o que foi medido e o que é hipótese |
| `HIPOTESE.md` (E4, E6 e E8; em E8 também `HIPOTESE-ROBUSTEZ.md`) | escrita em commit anterior à primeira execução. E3 e E7 rodaram sem hipótese escrita, e os resumos deles declaram isso |

## 2. Conferir que cada requisito do professor tem evidência

O mapa completo está em `planejamento/plan/ENTREGAS-DEMONSTRAVEIS.md`. Os três objetivos:

- [x] **P1, reprodução.** Matriz de confusão da reprodução ao lado da Fig. 4b, célula a célula, com a diferença; baselines ao lado da Tabela II; figuras SHAP equivalentes às Figs. 5 a 8. A distância ao artigo é reportada como está, sem ajuste para o número bater. Evidência: `results/e1/RESUMO.md` (Figs. 4a e 4b, nas duas leituras de profundidade), `results/e2/fiel/RESUMO.md` (Tabela II inteira), `results/e5/RESUMO.md` (Figs. 5 a 8), `results/e0/dados/RESUMO.md` (Tabela I e Fig. 2), `results/e7/RESUMO.md` (Seção VI-D e Fig. 9). O alvo são todas as tabelas e gráficos de resultado (decisão 46). As duas leituras de profundidade foram fechadas pela equipe, sem resposta do professor (decisão 55a).
- [x] **P2, segundo dataset.** Recall por ferramenta na transferência para o HKD; retreino no combinado como publicado e sem réplicas; parágrafo que justifica a escolha do dataset. Evidência: `results/e6/RESUMO.md`; justificativa em `results/e6/dados/RESUMO.md`, seção "Justificativa da escolha do segundo dataset". O dataset principal é o combinado sem réplicas (decisão 47). O professor não comentou que Non-DoH e Benign-DoH do combinado são os do CIRA; a equipe fechou o ponto sem resposta dele (decisão 55a).
- [x] **P3, modificação.** Original contra modificado nos dois datasets, dez seeds, com e sem as linhas duplicadas. Evidência: `results/e8/corrigida/RESUMO.md` (M1, M1M2) e `results/e8/corrigida/RESUMO-ROBUSTEZ.md` (robustez à duração, que é perturbação no espaço de atributos, não tráfego gerado).

Dois pontos que a especificação cobra explicitamente:

- [x] Contagem de amostras por classe em treino, validação e teste, para os **dois** datasets. Não há conjunto de validação separado: a validação é cruzada, e a tabela mostra o tamanho por fold. Evidência: `report/tables/dados_cira_contagens` e `report/tables/dados_segundo_contagens` (origem em `report/INDICE.md`).
- [x] Seção 7 com discussão e comparação com outros trabalhos, não só tabela de números. Evidência: `report/relatorio.tex`, seção "Resultados e discussões"; a revisão final conferiu o texto contra a lista do que se pode afirmar (`planejamento/plan/REVISAO-FINAL.md`, V8). A leitura pelos integrantes é o item 7 da lista única.

## 3. Gerar tabelas e figuras (tarefa 17)

- [x] Template, idioma, limite de páginas. Evidência: relatório sobre `geracao_latex_and_pdf/template.tex` (IEEEtran, decisão 53), em português, com 8 páginas; Q9 ficou sem resposta do professor e foi fechada pela equipe (decisão 55a); o template no Overleaf foi fechado por Breno em 08/10/2026 (`docs/07-pendencias.md`, tabela "Fechado").
- [x] `uv run python scripts/make_report_assets.py` gera `report/tables/` e `report/figures/` a partir de `results/`. Evidência: `report/tables/` (30 tabelas, cada uma em `.tex` e `.csv`), `report/figures/` (13 figuras, cada uma em `.pdf` e `.png`) e `report/INDICE.md`.
- [x] Apagar `report/tables/` e rodar de novo dá arquivos idênticos. Evidência: `planejamento/plan/REVISAO-FINAL.md`, V2 (60 tabelas, 26 figuras e o índice regenerados idênticos) e "Execução limpa" (56 de 56 arquivos de `report/` idênticos: 27 tabelas em `.tex` e `.csv`, o índice e o `relatorio.tex`).
- [x] Números das tabelas conferidos contra a origem. Evidência: `planejamento/plan/REVISAO-FINAL.md`, V2: 362 matrizes e 11.266 métricas recalculadas e 2.811 valores dos três agregados, sem divergência. Substitui a conferência manual de três números por tabela; o registro em pull request não se aplica (decisão 55f).
- [x] Legendas das tabelas de modelo com a seed ou o número de seeds e o nome da média. Evidência: legendas de `report/relatorio.tex`, lidas em `5999c1b` ("Seed 42; média macro", "10 seeds, média ± desvio padrão amostral"). A conferência visual no PDF entra na leitura do item 7 da lista única.

## 4. Escrever o relatório (tarefas 18 e 24)

O relatório foi gerado na tarefa 24 (decisão 53) e corrigido depois da revisão de texto (commit `17a278b`) e da revisão final (commits `3725f27` e `c74fc3f`): `report/relatorio.tex` e `report/relatorio.pdf`, 8 páginas. O `.tex` exige **XeLaTeX** (usa `fontspec`).

- [x] As nove seções existem. Evidência: `report/relatorio.tex`: resumo, Introdução, Trabalhos relacionados, Modelo de ameaça, Sistema proposto pelo artigo de referência, Solução proposta pela equipe, Metodologia, Resultados e discussões, Conclusões e trabalhos futuros, referências.
- [ ] Lista de conferência preenchida: cada pergunta da especificação com a seção e o parágrafo que a responde. Não está em arquivo versionado. → item 7 da lista única.
- [ ] Figuras que nenhum script gera. Feitas em TikZ, em `report/relatorio.tex`: o túnel DNS sobre DoH (seção 3) e o sistema do artigo (seção 4). Não feita: o modelo modificado ao lado do original (seção 5). → item 7 da lista única.
- [x] Declarado no texto: a reimplementação a partir do artigo; a leitura adotada nos pontos em aberto (as três que faltavam entraram com o tratamento do achado M5 da revisão final, commits `3725f27` e `c74fc3f`); a divergência entre a Tabela II e a Fig. 4b do próprio artigo. Evidência: `report/relatorio.tex`.
- [x] Limitações medidas, com o número vindo de `results/`. Evidência: `report/relatorio.tex`, seção de metodologia: classe maliciosa capturada em outras máquinas e em outro período; 13,67% do teste com vetor idêntico no treino; 326 vetores em mais de uma classe; HKD replicado 20 vezes no combinado; valor `-10` nas colunas de assimetria. A sexta, o teste com uma amostra a mais que o do artigo, não foi localizada no texto por busca: item 7 da lista única.
- [x] Todo número do texto confere com a origem. Evidência: `planejamento/plan/REVISAO-FINAL.md`, V2: 115 afirmações numéricas, 112 conferem; as inexatidões de texto apontadas (achados I1, I2, M1 e M2) foram corrigidas no commit `3725f27`.
- Referências com DOI: não se aplica como escrito. Breno fechou em 08/10/2026: DOI só nas duas referências conferidas; a especificação pede só o formato IEEE. A citação do dataset CIRA tem duas formas no repositório, nenhuma conferida na fonte: item 11 da lista única.
- Transcrições do manuscrito conferidas por dois integrantes: não se aplica como escrito (decisão 55b). Foram conferidas pelo assistente, em duas passagens independentes, sem divergência.
- [x] Uso de assistente de IA: aprovado na disciplina; sem frase de declaração no relatório (decisão 55a, sem resposta do professor).
- [x] Agente `revisor-de-texto` sem achado grave em aberto. Evidência: commits `17a278b` e `dc5fb1c`; revisão final, V8. A leitura cruzada por pull request não se aplica (decisão 55f); a leitura pelos quatro integrantes é o item 7 da lista única.
- [x] PDF compila sem erro. Evidência: `report/relatorio.pdf`, 8 páginas, recompilado em `3725f27`; é o passo 22 da execução limpa.

## 5. Fechar o repositório (tarefa 19)

A especificação pede "link do GitHub com todos os códigos comentados".

- [x] README completo. Evidência: `project/README.md` (instalação com uv e com pip, dados, os 22 passos com o tempo medido, a tabela resultado → script → arquivo, limitações, licença) e `README.md` da raiz, como página de apresentação.
- [x] README registra onde os resultados versionados foram gerados. Evidência: `project/README.md`: mesma máquina nos 229 `run.json`, 10 núcleos, Python 3.12.13.
- [x] Comentários revisados. Evidência: o lint exige docstring em função pública (regra `D1` em `project/pyproject.toml`); o CI barra referência a documento interno (`.github/workflows/ci.yml`); os comandos do CI ficaram verdes em clone limpo (`planejamento/plan/REVISAO-FINAL.md`, V9).
- [x] **Execução limpa.** Evidência: `planejamento/plan/REVISAO-FINAL.md`, "Execução limpa": 08/10/2026, 7 h 30 min, clone novo fora do repositório, 22 passos sem erro, 260 de 260 e 56 de 56. "Por quem não escreveu o código": não se aplica (decisões 44 e 55d); ela foi feita na sessão de implementação, na mesma máquina, e não testa outra máquina.
- [ ] Instalação pelo `requirements.txt` com pip testada. Sem registro. → item 12 da lista única.
- [x] Higiene: sem dados, sem modelo serializado, sem o PDF do artigo, sem caminho de máquina. Evidência: `planejamento/plan/REVISAO-FINAL.md`, V9.
- [ ] CI verde na `main` no commit entregue. → item 1 da lista única (a `main` está em `378f170`).
- `git shortlog -sn` com os quatro integrantes: não se aplica (decisões 44 e 55d). Os 164 commits até `5999c1b` são de uma só identidade, aceito pela equipe; nenhum commit tem coautoria de ferramenta (revisão final, V9).
- Pull requests na ordem das tarefas: não se aplica (decisão 55f). O envio dos commits finais é o item 1 da lista única.
- [x] Licença. Evidência: `LICENSE` (MIT) na raiz (decisão 55c).
- [x] Acesso do professor ao repositório. Evidência: repositório público (decisão 43); Q10 ficou sem resposta e foi fechada pela equipe (decisão 55a).
- [ ] Proteção da `main` e acesso de escrita dos integrantes, se a equipe quiser. → item 8 da lista única.

## 6. Acompanhamento com o professor (tarefa 23)

- [x] Respostas às perguntas enviadas em 07/10 registradas em `docs/07-pendencias.md`, com data. Evidência: Q1 a Q6 respondidas em 07/10/2026 (decisões 46 a 50). Q9, Q10 e a parte aberta de Q7 ficaram sem resposta do professor e foram fechadas pela equipe (decisão 55a).
- Conversa sobre as duas leituras de profundidade, o combinado e Q5 como condição para seguir: não se aplica (decisão 55a). Os três pontos continuam na página dos encontros, `docs/09-acompanhamento-professor.md`.
- [ ] **10/11:** levar a página de status, a tabela de resultados e o resultado da execução limpa. A página está pronta. → item 4 da lista única.
- [ ] **17/11:** levar o relatório e as dúvidas que restarem. → item 4 da lista única.
- [ ] Retorno de cada encontro registrado e convertido em ajuste. → item 4 da lista única.

## 7. Entrega em 18/11

- [ ] Skill `checklist-entrega projeto` rodada, com `OK`, `Pendente` ou `Não aplicável` em cada item. → item 5 da lista única.
- [ ] PDF do relatório e link do GitHub enviados. → item 5 da lista única.
- [ ] Comprovante guardado: data, hora e hash do commit entregue, em `docs/07-pendencias.md`. → item 5 da lista única.

## 8. Apresentação em 19/11 (tarefas 20 e 24)

Obrigatória: P3 foi feito. A apresentação é entregue em **PPTX**, no modelo do CIn, para subir no Google Slides (decisão 53); não há PDF dos slides a gerar.

- [ ] Confirmar com o professor o que a apresentação deve cobrir. → item 4 da lista única.
- [x] Slides no modelo institucional do CIn, só tópicos e imagens, com todo número e gráfico vindo de `report/`. Evidência: `report/apresentacao.pptx` (14 slides), gerado por `scripts/make_slides.py`; cópia em `entregaveis-apresentacao/`.
- [x] Um slide para o artigo, no máximo. Evidência: `report/roteiro.md` (slide 2, "O artigo em um slide").
- [x] PPTX conferido no Google Slides. Evidência: por Breno, em 08/10/2026 (`docs/07-pendencias.md`, tabela "Fechado").
- [x] Fala dividida. Evidência: `report/roteiro.md`: Amanda (slides 1 a 5), Antonio (6 a 10) e João (11 a 14); soma de 11 min 55 s. "Entre os quatro" não se aplica: apresentam três.
- [ ] Ensaio cronometrado em 15 minutos, pelos três. → item 2 da lista única.
- [x] `revisor-de-texto` sobre os slides. Evidência: commit `dc5fb1c`; slides e roteiro alinhados às correções do relatório em `c74fc3f`.

## 9. Preparar a arguição

O trabalho é defendido em sala. Ninguém assina o que não consegue explicar. As três caixas são o item 6 da lista única.

- [ ] Cada integrante explica, linha a linha, o código da parte que apresenta.
- [ ] Todos sabem responder: por que a reimplementação conta como reprodução; por que há duas leituras de profundidade e por que a de profundidade 5 perde uma classe; quais são os alvos (todas as tabelas e gráficos de resultado, com a Fig. 4b e a Tabela II lado a lado); quão perto ficamos e o que explica a diferença; por que as trilhas fiel, variante e corrigida não se misturam; por que este segundo dataset e por que sem réplicas; por que a transferência para o HKD falha; o que a robustez de E8 mede e o que não mede; o que cada limitação medida faz com os resultados.
- [ ] Perguntas prováveis distribuídas entre os integrantes.

## 10. Fechamento interno

- [x] Agentes `cin0114-plan-sync` e `cin0114-doc-sync` rodados depois da última tarefa. Evidência: `planejamento/MEMORY/SYNC-BASELINE.md`, linha de 08/10/2026 sobre o commit `5999c1b`.
- [x] Tarefa 22: padrões que nasceram na implementação registrados ou dispensados com justificativa. Evidência: `.claude/rules/experimentos.md`.
- [x] `planejamento/MEMORY/STATUS.md` atualizado. Evidência: o próprio arquivo, na situação de `5999c1b`. Depois da entrega, registra-se o comprovante em `docs/07-pendencias.md`.

## Pendências que travam itens acima

Nenhuma tabela própria: a lista única é a seção "O que resta de pessoa" de [docs/07-pendencias.md](docs/07-pendencias.md).
