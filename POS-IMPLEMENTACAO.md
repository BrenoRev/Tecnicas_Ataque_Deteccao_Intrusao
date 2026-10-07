# Depois da implementação: o que falta fazer, documentar e evidenciar

Este documento cobre o trecho entre "o código das tarefas está pronto" e "a entrega foi feita e defendida". Ele não substitui o plano: aponta para a tarefa que detalha cada item. Marque cada caixa só com a evidência indicada na mão.

**Regra geral de evidência.** Nada vale por estar dito. Cada item fecha com um arquivo no repositório, uma saída de comando colada no pull request ou um registro datado em `docs/07-pendencias.md`. Nenhum número é digitado à mão: vem de `results/` ou de `report/tables/`.

**Onde roda.** A execução com dados reais pode ser na máquina de um integrante ou no cluster Apuana; as duas valem (decisão 42). O importante é treinar e deixar a evidência. Os resultados versionados e a execução limpa final devem sair do mesmo ambiente, porque máquinas diferentes podem divergir em casas decimais.

## Datas

| Data | O que acontece | Situação |
| --- | --- | --- |
| 09/11 | Decidir se P3 (modificação) continua | meta interna |
| 10/11 | Acompanhamento com o professor; primeira execução limpa | calendário da disciplina |
| 13/11 | Experimentos congelados: depois disso, só correção | meta interna |
| 17/11 | Acompanhamento com o professor, com o rascunho do relatório | calendário da disciplina |
| 18/11 | Entrega: relatório em PDF e link do GitHub | prazo da especificação |
| 19/11 | Slides e apresentação de 15 minutos, só se houver P3 | prazo da especificação |

Local de entrega: `[Preencher: Classroom?]`.

## 1. Rodar tudo com os dados reais

Uma tarefa de experimento está "pronta" com código, testes e revisão, e "executada" quando rodou com os dados reais. Só a executada vira número no relatório.

- [ ] Dados conferidos na máquina (ou no cluster) em que os experimentos rodam: `uv run python data/verify.py` com código 0.
- [ ] Cada script rodado com a árvore do Git limpa, na ordem do README: E0 (dados), E1 (reprodução), E2 (baselines), E3 (sensibilidade), E4 (dez seeds), E5 (SHAP), E6 (segundo dataset) e, se houver P3, E8.
- [ ] Segunda execução de cada script com `metrics.json` idêntico ao da primeira, na mesma máquina.
- [ ] Resultados em commit `exp`, separado do código, feito por quem rodou.

Evidência por experimento, em `results/<experimento>/<trilha>/`:

| Arquivo | O que prova |
| --- | --- |
| `metrics.json` | o número, determinístico |
| `run.json` | trilha, seed, versões, hash dos dados, commit, `dirty: false`, máquina e núcleos |
| `RESUMO.md` | a interpretação: o que o número significa, o que foi medido e o que é hipótese |
| `HIPOTESE.md` (E6 e E8) | escrita em commit anterior à primeira execução |
| saída do script no pull request | as asserções com dados reais passaram |

## 2. Conferir que cada requisito do professor tem evidência

O mapa completo está em `planejamento/plan/ENTREGAS-DEMONSTRAVEIS.md`. Os três objetivos:

- [ ] **P1, reprodução.** Matriz de confusão da reprodução ao lado da Fig. 4b, célula a célula, com a diferença; baselines ao lado da Tabela II; figuras SHAP equivalentes às Figs. 5 a 8. A distância ao artigo é reportada como está, sem ajuste para o número bater.
- [ ] **P2, segundo dataset.** Recall por ferramenta na transferência para o HKD; retreino no combinado como publicado e sem réplicas; parágrafo que justifica a escolha do dataset. A justificativa final depende da resposta do professor à pergunta sobre o combinado.
- [ ] **P3, modificação (opcional).** Original contra modificado nos dois datasets, dez seeds, com e sem as linhas duplicadas. Se não melhorou, o relatório diz isso e analisa por quê.

Dois pontos que a especificação cobra explicitamente:

- [ ] Contagem de amostras por classe em treino, validação e teste, para os **dois** datasets. Não há conjunto de validação separado: a validação é cruzada, e a tabela mostra o tamanho por fold.
- [ ] Seção 7 com discussão e comparação com outros trabalhos, não só tabela de números.

## 3. Gerar tabelas e figuras (tarefa 17)

- [ ] Template Overleaf lido antes: idioma, limite de páginas, estilo de tabela. Hoje ainda não foi lido.
- [ ] `uv run python scripts/make_report_assets.py` gera `report/tables/` e `report/figures/` a partir de `results/`.
- [ ] Apagar `report/tables/` e rodar de novo dá arquivos idênticos.
- [ ] Três números de cada tabela conferidos contra o `metrics.json` de origem, com o registro no pull request.
- [ ] Toda tabela de modelo traz na legenda a trilha, a seed ou o número de seeds e o nome da média. Toda figura tem eixo rotulado e unidade.

## 4. Escrever o relatório (tarefa 18)

Formato de artigo, no template Overleaf indicado, entregue em PDF, com referências IEEE.

- [ ] As nove seções existem: resumo, introdução, trabalhos relacionados, modelo de ameaça, sistema do artigo, solução da equipe (só com P3), metodologia, resultados e discussões, conclusão, referências.
- [ ] Lista de conferência preenchida: cada pergunta da especificação com a seção e o parágrafo que a responde.
- [ ] Figuras que nenhum script gera, feitas à mão pela equipe: túnel DNS sobre DoH com as premissas do atacante (seção 3), pipeline e algoritmo de treino (seção 4), modelo modificado ao lado do original (seção 5, com P3).
- [ ] Declarado no texto: o sistema foi reimplementado a partir do artigo, porque o código público não contém o modelo; a leitura adotada em cada ponto que o artigo deixa em aberto; a divergência entre a Tabela II e a Fig. 4b do próprio artigo.
- [ ] Limitações medidas, cada uma com o número vindo de `results/`: classe maliciosa capturada em outras máquinas e em outro período; 13,7% do teste com vetor idêntico no treino; 326 vetores em mais de uma classe; teste com uma amostra a mais que o do artigo; HKD replicado 20 vezes no combinado; valor `-10` nas colunas de assimetria.
- [ ] Todo número do texto confere com `report/tables/` ou com o artigo. Toda afirmação sobre o artigo cita seção, tabela ou figura.
- [ ] Cada referência conferida na fonte, com DOI, citada no texto.
- [ ] Uso de assistente de IA: aprovado na disciplina. A frase de declaração entra no relatório e no README só se o professor pedir.
- [ ] Agente `revisor-de-texto` sem achado grave em aberto e leitura cruzada por outro integrante.
- [ ] PDF compila sem erro e sem referência quebrada.

## 5. Fechar o repositório (tarefa 19)

A especificação pede "link do GitHub com todos os códigos comentados".

- [ ] README completo: o que é o projeto, integrantes, instalação com uv e com pip, como obter e conferir os dados, ordem dos scripts, tempo medido de cada um, limitações, e a tabela "resultado do relatório → script → arquivo em `results/`" cobrindo todas as tabelas e figuras.
- [ ] README registra onde os resultados versionados foram gerados: máquina e versões.
- [ ] Comentários revisados: docstring em toda função pública; comentário de decisão nos pontos em que o artigo é omisso, citando a seção do artigo; nenhuma referência a documento interno.
- [ ] **Execução limpa** por quem não escreveu o código, em diretório novo: clonar, instalar, colocar os dados, `data/verify.py`, rodar os scripts na ordem do README e comparar os `metrics.json` com os versionados. Primeira tentativa em 10/11; a final começa em 16/11.
- [ ] Instalação pelo `requirements.txt` com pip testada.
- [ ] Higiene: sem dados, sem modelo serializado, sem o PDF do artigo, sem credencial, sem caminho de máquina. Os comandos de conferência são os do CI.
- [ ] CI verde na `main` no commit entregue.
- [ ] `git shortlog -sn` mostra os quatro integrantes; nenhum commit com coautoria de ferramenta.
- [ ] Acesso do professor ao repositório, público ou privado conforme a resposta dele.

## 6. Acompanhamento com o professor (tarefa 23)

- [ ] Cada resposta às perguntas enviadas em 07/10 registrada em `docs/07-pendencias.md`, com data, e a tarefa afetada ajustada.
- [ ] **10/11:** uma página com o que funciona, o que falta e o que travou; tabela de resultados (reprodução ao lado da Fig. 4b, segundo dataset); resultado da primeira execução limpa. Se os experimentos rodaram no Apuana e a equipe quer que isso conte, dizer.
- [ ] **17/11:** rascunho completo do relatório e as dúvidas que restarem.
- [ ] Retorno de cada encontro registrado e convertido em ajuste.

## 7. Entrega em 18/11

- [ ] Skill `checklist-entrega projeto` rodada, com `OK`, `Pendente` ou `Não aplicável` em cada item e nenhum item exigido pendente.
- [ ] PDF do relatório e link do GitHub enviados.
- [ ] Guardar o comprovante: data, hora e hash do commit entregue, em `docs/07-pendencias.md`.

## 8. Apresentação em 19/11 (só com P3, tarefa 20)

- [ ] Confirmar com o professor o que a apresentação deve cobrir.
- [ ] Slides no modelo institucional do CIn, só tópicos e imagens, com todo número e gráfico vindo de `report/`.
- [ ] Um slide para o artigo, no máximo; o resto é reprodução, segundo dataset e modificação.
- [ ] Fala dividida entre os quatro e ensaio cronometrado em 15 minutos.
- [ ] `revisor-de-texto` sobre os slides.

## 9. Preparar a arguição

O trabalho é defendido em sala. Ninguém assina o que não consegue explicar.

- [ ] Cada integrante explica, linha a linha, o código da parte que apresenta.
- [ ] Todos sabem responder: por que a reimplementação conta como reprodução; por que o alvo é a Fig. 4b; quão perto ficamos e o que explica a diferença; por que duas trilhas (fiel e corrigida); por que este segundo dataset; o que cada limitação medida faz com os resultados.
- [ ] Perguntas prováveis distribuídas entre os quatro.

## 10. Fechamento interno

- [ ] Agentes `cin0114-plan-sync` e `cin0114-doc-sync` rodados depois da última tarefa: plano e `docs/` refletem o que foi implementado.
- [ ] Tarefa 22: padrões que nasceram na implementação registrados ou dispensados com justificativa.
- [ ] `planejamento/MEMORY/STATUS.md` atualizado com a situação final.

## Pendências que travam itens acima

| Pendência | Trava | Quem resolve |
| --- | --- | --- |
| Respostas do professor (reimplementação, alvo, segundo dataset, ferramenta de túnel, painel, páginas e idioma, visibilidade, declaração de IA) | seções 2, 4, 5 e 7 | professor |
| Template Overleaf não lido | seções 3 e 4 | equipe |
| Dono de cada tarefa: quem desenvolve e quem executa | seções 1 e 5 | equipe |
| Licença do repositório e link do drive da equipe | seção 5 | equipe |
| Metade inferior da Tabela II, copiada do artigo e conferida por dois | seções 3 e 4 | equipe |
| Decisão sobre P3 em 09/11 | seções 2 e 8 | equipe |
