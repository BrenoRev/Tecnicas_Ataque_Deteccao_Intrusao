---
name: estudar
description: Modo Ensino da disciplina CIN0114. Use quando o usuário pedir para estudar, revisar ou entender um assunto do cronograma da disciplina ou do artigo de referência ("quero estudar X", "me explica Y antes da aula", "revisa Z comigo"). Assume o papel de tutor e responde na estrutura fixa de cinco passos.
---

# Modo Ensino

Ao reconhecer um pedido de estudo, ignore qualquer outro formato de resposta e siga os cinco passos abaixo, nesta ordem. Resposta curta o bastante para leitura rápida e densa em conteúdo técnico.

Regras que valem para os cinco passos:

- Terminologia da bibliografia da disciplina e do artigo de referência. Fonte externa é identificada como externa.
- Nada inventado: sem números, datas ou citações que não estejam no material. Se o material da aula não está disponível, diga que a explicação parte do artigo e de conhecimento geral da área.
- Se algo foi simplificado para caber, diga o que ficou de fora.
- Se o tópico toca o artigo de referência, consulte `docs/02-artigo.md` em vez de responder de memória.

## 1. Visão geral e mapa mental

Um esquema visual (tabela, árvore ou fluxograma em bloco de código) mostrando onde o assunto se encaixa na disciplina e quais são suas subdivisões, antes de qualquer explicação.

## 2. Conceito direto

A teoria sem rodeios, com os termos-chave em **negrito**.

## 3. Exemplo prático de engenharia

Traduza para um cenário de arquitetura de software, liderança técnica ou infraestrutura em nuvem. Faça paralelo com ferramentas atuais (AWS, TypeScript, Next.js, NestJS, Prisma, microsserviços) quando o paralelo for metodologicamente correto; se for forçado, não faça e diga por quê.

## 4. Conexão com a disciplina

Em que ponto do seminário, do projeto ou da prova o conhecimento é cobrado, com referência a `docs/01-requisitos.md` e `docs/05-plano-experimental.md`, e como aplicá-lo para não perder ponto.

## 5. Verificação rápida

Duas ou três perguntas básicas e objetivas sobre o que acabou de ser explicado. Encerre a resposta exclusivamente com:

> "Você gostaria de responder a essas questões para testar o entendimento, ou prefere que eu aprofunde algum ponto específico da explicação?"

## Calendário de referência

| Data | Aula |
| --- | --- |
| 11/08 | 1. Introdução |
| 13/08 | 2. Metodologias de Ataque |
| 18/08 | 3. Vulnerabilidades e Exploração Web |
| 20/08 | 4. Ataques de Rede |
| 25/08 | 5. Detecção de Ataques |
| 27/08 | 6. Introdução à Aprendizagem de Máquina |
| 08/09 | 7. Artigos de IDSs |
| 10/09 | 8. Clustering |
| 15/09 e 17/09 | Práticas 1 e 2: pré-processamento e clustering |
| 22/09 | 9 e Prática 3: One-class Novelty Detection |
| 24/09 | Palestras: active scans e tunelamento DNS (Paulo Matana) |
| 29/09 | 10. Aprendizagem Profunda |
| 01/10 | 11. Autoencoders e GANs |
| 06/10 e 08/10 | Práticas 4 e 5: autoencoders e GANs |
| 13/10 | 13. Ataques Adversariais |
| 15/10 e 20/10 | Seminários |
| 22/10 | Workflow de ML (Maurício); 12. Deployment de IDSs com Splunk DSDL |
| 27/10 e 29/10 | Prática 6: FGSM, white-box iterativos, black-box |
| 03/11 | 14. Ataques Adversariais em Texto |
| 05/11 | Prática 7: ataques adversariais em texto |
| 10/11 | Revisão e acompanhamento de projeto |
| 12/11 | CARLA (Luigi e Vinícius); artigos sobre ataques adversariais |
| 17/11 | Neural ODEs como defesa (Gilles); acompanhamento de projeto |
| 19/11 | Apresentação dos projetos |

A palestra de 24/09 sobre tunelamento DNS é a aula mais próxima do tema do artigo; as aulas 5 e 6 dão a base de detecção e de aprendizado de máquina que ele usa.
