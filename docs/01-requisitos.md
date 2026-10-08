# 01. O que é cobrado

Fonte: especificação oficial do professor (em `docs/referencias/`). Quando este documento e a especificação divergirem, vale a especificação.

## Prazos

| Data | Entrega | Onde |
| --- | --- | --- |
| 17/09/2026 | Equipe de 4 pessoas e artigo registrados | Classroom |
| 14/10/2026 | Slides do seminário | Classroom |
| 15/10 e 20/10/2026 | Apresentação do seminário: 15 min + 5 min de perguntas | Sala |
| 18/11/2026 | Relatório em PDF e link do GitHub com todos os códigos comentados | [Preencher: Classroom?] |
| 19/11/2026 | Slides e apresentação de 15 min, só para equipes que fizerem modificações no artigo | Sala |

Peso informado no material da disciplina: seminário 30%, projeto 70%. A especificação em si não traz os pesos nem a rubrica de correção.

## Seminário

Cobertura mínima, na ordem da especificação:

1. Introdução: motivação, justificativa e principais contribuições.
2. Trabalhos relacionados: contribuições e limitações de cada um.
3. Solução proposta: arquitetura e funcionamento.
4. Experimentos: dados e experimentos realizados.
5. Resultados: exposição e análise.
6. Conclusão: conclusões, **principais limitações e problemas do sistema e sugestões detalhadas de melhoria**.

Formato: modelo institucional de apresentação do CIn; só tópicos, bullets e imagens; textos longos devem ser evitados.

O item 6 está em negrito na especificação. É o único trecho destacado do seminário, então é razoável supor que pesa na nota.

## Projeto

### Os três objetivos

| # | Objetivo | Obrigatório | Critério da especificação |
| --- | --- | --- | --- |
| P1 | Reproduzir o artigo, implementando e executando o código | Sim | "resultados próximos o suficiente dos resultados exibidos no artigo" |
| P2 | Obter resultados do sistema do artigo em outro dataset | Sim | "a escolha do novo conjunto de dados deve ser devidamente justificada no relatório" |
| P3 | Propor, implementar e avaliar modificações no sistema | Não, vale ponto extra | Se feito, obriga slides e apresentação em 19/11 |

A especificação avisa que requisitos adicionais podem ser exigidos por artigo. Ainda não sabemos se há algum para o nosso (ver [07-pendencias.md](07-pendencias.md)).

### Entregáveis

- Relatório em PDF, formato de artigo, no template Overleaf indicado, referências em formato IEEE.
- Link do GitHub com todos os códigos **comentados**.
- Se houver P3: slides (modelo do CIn) e apresentação de 15 minutos.

### Seções do relatório e o que cada uma precisa responder

| Seção | Perguntas obrigatórias | De onde sai o conteúdo |
| --- | --- | --- |
| Abstract/Resumo | Contexto, problema, soluções existentes, método, resultados | Escrita por último |
| 1. Introdução (breve) | Qual o problema? Por que interessa? Por que o artigo precisou propor a solução? Soluções existentes e desvantagens? O que é proposto? Contribuições em lista | Seminário, blocos 1 e 2 |
| 2. Trabalhos relacionados | Contribuições e limitações de cada trabalho | Seminário, bloco 2; [02-artigo.md](02-artigo.md) |
| 3. Modelo de ameaça (se aplicável) | Ataques considerados, com figuras, algoritmos ou equações; premissas para o ataque ser possível | O artigo não declara; a equipe formaliza (ver 02-artigo.md, seção 7) |
| 4. Sistema proposto pelo artigo | Componentes, entradas e saídas, o que fazem e como; métodos empregados e por quê | [02-artigo.md](02-artigo.md) |
| 5. Solução da equipe (se feita) | O que se espera melhorar; componentes; métodos e por quê | Só com P3 |
| 6. Metodologia | Para **cada** dataset: quais dados, por que escolhidos, o que representam, como treino/validação/teste foram formados, quantas amostras por classe em cada conjunto. Métricas e experimentos | [04-dados.md](04-dados.md), [05-plano-experimental.md](05-plano-experimental.md) |
| 7. Resultados e discussões | Solução do artigo nos dados do artigo e no segundo dataset; proposta da equipe nos dois (se feita). Comparar com outros trabalhos, com gráficos e tabelas, **explicando e discutindo**, não só descrevendo | `results/` |
| 8. Conclusão e trabalhos futuros | Conclusão, limitações e problemas do sistema do artigo e da proposta, trabalhos futuros | Seminário, críticas 1 a 11 |
| 9. Referências | Formato IEEE | `report/` |

Dois pontos que derrubam nota se esquecidos, porque a especificação pede explicitamente:

- Contagem de amostras por classe em treino, validação **e** teste, para os dois datasets. O código precisa gerar essa tabela.
- A seção 7 pede discussão e comparação com outros trabalhos. Tabela de números sem interpretação não atende.

## O que a especificação não pede

O arquivo de instruções gerais que a equipe vinha usando lista itens que não constam da especificação oficial. Ficam registrados aqui para ninguém tratá-los como exigência do professor:

| Item das instruções gerais | Situação real |
| --- | --- |
| Componente adversarial obrigatório (FGSM, ε, black-box) | Não é exigido. Pode ser a modificação opcional de P3, se a equipe quiser |
| Apresentação do projeto para todos em 19/11 | Só para quem fizer modificações |
| Citações em "ABNT ou IEEE" | IEEE, sem alternativa |
| Slides em formato livre exportado em PDF | Modelo institucional do CIn |
| Múltiplas execuções com média e desvio, baseline simples, repositório privado, notebooks executados exportados | Boas práticas adotadas pela equipe ([06-padroes.md](06-padroes.md)); não são requisito formal |

## Rastreabilidade: requisito, evidência, responsável

| Requisito | Evidência que fecha o item | Responsável |
| --- | --- | --- |
| P1 reprodução | Matriz de confusão e métricas no CIRA-CIC-DoHBrw-2020 ao lado dos valores do artigo, com a diferença calculada. Gerado em 07 e 08/10/2026: `project/results/e0/dados/RESUMO.md`, `e1/RESUMO.md`, `e2/fiel/RESUMO.md`, `e5/RESUMO.md`, `e7/RESUMO.md` | [Preencher] |
| P2 segundo dataset | Mesmas métricas no segundo dataset + parágrafo de justificativa da escolha. Gerado em 08/10/2026: `project/results/e6/RESUMO.md`; justificativa em `project/results/e6/dados/RESUMO.md` | [Preencher] |
| P3 modificação | Mesma tabela, sistema original contra modificado, nos dois datasets. Gerado em 08/10/2026: `project/results/e8/corrigida/RESUMO.md` e `RESUMO-ROBUSTEZ.md` | [Preencher] |
| Código comentado | Revisão pelo agente `revisor-metodologico` e leitura cruzada entre integrantes | [Preencher] |
| Relatório | PDF no template, 9 seções, checklist rodada. Gerado em 08/10/2026: `project/report/relatorio.pdf`; a checklist de entrega ainda não foi rodada | [Preencher] |
