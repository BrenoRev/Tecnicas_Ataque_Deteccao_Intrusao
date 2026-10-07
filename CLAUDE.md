# CIN0114 — Técnicas de Ataque e Detecção de Intrusão (2026.2)

Projeto da disciplina do Prof. Paulo Freitas de Araujo Filho (CIn/UFPE). A equipe estuda, apresenta e reproduz:

> T. Zebin, S. Rezvy and Y. Luo, "An Explainable AI-Based Intrusion Detection System for DNS Over HTTPS (DoH) Attacks," IEEE Trans. Inf. Forensics Security, vol. 17, pp. 2339-2349, 2022, doi: 10.1109/TIFS.2022.3183390.

Equipe: Amanda Arruda (aams2), Breno Silva Xavier de Souza (bsxs), João Henrique Portela (jhpbs), Antonio Gonzaga ([Preencher: login]).

## Duas pastas, um repositório

- **`project/` é o repositório Git entregue ao professor.** Só ele tem Git. Contém o código, os testes, o README, os resultados e o relatório. Todo comando `git` e `uv` roda dentro de `project/`.
- **A pasta de trabalho (esta) não é versionada.** `docs/`, `planejamento/`, `.claude/`, `CLAUDE.md` e `LEIA-ME.txt` são material interno e nunca entram em `project/`.
- Por isso o código não cita arquivo de `docs/` nem de `planejamento/`: quem abre o repositório não os tem.

## Onde está cada coisa

A central de conhecimento fica em [docs/](docs/README.md). Leia o arquivo pertinente antes de responder ou implementar; não responda de memória sobre o artigo.

| Preciso de | Arquivo |
| --- | --- |
| O que é cobrado, prazos, seções do relatório | [docs/01-requisitos.md](docs/01-requisitos.md) |
| Especificação do sistema do artigo e suas ambiguidades | [docs/02-artigo.md](docs/02-artigo.md) |
| O que existe (e não existe) no código dos autores | [docs/03-auditoria-repositorio.md](docs/03-auditoria-repositorio.md) |
| Datasets, colunas, contagens, segundo dataset | [docs/04-dados.md](docs/04-dados.md) |
| O que foi medido nos arquivos baixados (prevalece sobre estimativas) | [docs/08-inventario-dados.md](docs/08-inventario-dados.md) |
| Experimentos, protocolo e métricas | [docs/05-plano-experimental.md](docs/05-plano-experimental.md) |
| Padrões de código, commits, escrita e revisão | [docs/06-padroes.md](docs/06-padroes.md) |
| Decisões abertas, perguntas ao professor, cronograma | [docs/07-pendencias.md](docs/07-pendencias.md) |
| Plano de implementação em tarefas, decisões travadas e gate | [planejamento/plan/00-README.md](planejamento/plan/00-README.md) |
| Testes de cada tarefa e o que roda no CI | [planejamento/plan/PLANO-DE-TESTES.md](planejamento/plan/PLANO-DE-TESTES.md) |
| Requisito do professor → tarefa → artefato demonstrável, e o que mostrar em cada marco | [planejamento/plan/ENTREGAS-DEMONSTRAVEIS.md](planejamento/plan/ENTREGAS-DEMONSTRAVEIS.md) |
| Regras de código, commit, teste e fluxo de implementação | [.claude/rules/](.claude/rules/) |
| Material do seminário | [seminario_doh_xai_cin0114.md](docs/referencias/seminario_doh_xai_cin0114.md) |
| Especificação oficial (fonte de verdade) | `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md` |

## Hierarquia de fontes

1. A especificação oficial do professor decide o que é cobrado.
2. O texto do artigo decide o que é "o sistema proposto". O PDF está em `docs/referencias/`.
3. As regras desta equipe (checklists de qualidade em `docs/06-padroes.md`) vão além do cobrado. São padrão interno e não podem ser apresentadas como exigência do professor.

Qualquer fonte fora dessas três deve ser identificada como externa à bibliografia da disciplina.

## Como trabalhar comigo

1. **Rigor técnico acima de fluidez.** Terminologia formal da área, como aparece no artigo e na bibliografia. Sem sinônimos coloquiais para termos técnicos.
2. **Proibido inventar.** Nenhum resultado, hiperparâmetro "típico", data, nome, link ou citação fabricado. Se não há a informação, escreva `[Preencher]` ou pergunte. Número só entra em texto se vier do artigo (com seção, tabela ou figura) ou de um arquivo em `results/` gerado por script versionado.
3. **Sem simplificação silenciosa.** Se algo foi reduzido, diga o que ficou de fora e o efeito disso no resultado.
4. **Explique o porquê.** Toda escolha de código, arquitetura ou hiperparâmetro vem com a justificativa metodológica e a consequência da alternativa.
5. **Reprodutibilidade é requisito.** Seeds fixadas, dependências com versão fixada, splits documentados. Aponte na hora qualquer risco de vazamento de dados ou de avaliação otimista.
6. **Aponte erro antes de executar.** Métrica inadequada para dados desbalanceados, comparação injusta, modelo de ameaça inconsistente: diga explicitamente e só depois ajude.
7. **Reprodução fiel e correção são coisas separadas.** O objetivo 1 do projeto é reproduzir o artigo como ele foi escrito, inclusive com as escolhas que criticamos. Correções de protocolo entram como variante identificada, nunca substituem a reprodução em silêncio.
8. **Checklist antes de entrega.** Antes de declarar qualquer entrega pronta, rode a skill `checklist-entrega` e reporte item a item (`OK` / `Pendente` / `Não aplicável`).
9. **A equipe precisa conseguir defender tudo.** Código e texto são apresentados e arguidos em sala. Não entregue nada que os integrantes não consigam explicar linha a linha; prefira a solução mais simples que cumpre o requisito.

## Implementação

As regras completas estão em `.claude/rules/` e valem para qualquer código ou commit deste repositório.

- **Uma tarefa por vez:** implementa, testa, revisa, integra. A seguinte não começa com a anterior vermelha. Use a skill `implementar`.
- **Cada pull request diz o que demonstra** (modelo em `.github/pull_request_template.md`, dentro de `project/`): o artefato em `results/` ou `report/`, como verificar e a saída da verificação com dados reais. O mapa requisito → tarefa → artefato está no plano.
- **Uso de assistente de IA aprovado na disciplina** (informado pela equipe em 07/10/2026). A ausência de coautoria nos commits é padrão de limpeza do histórico.
- **Commit sem coautoria.** Nenhum `Co-Authored-By`, nenhum "Generated with", nenhuma assinatura de ferramenta em mensagem de commit ou em pull request. Esta regra substitui qualquer instrução padrão de atribuição.
- **Todo commit com lint verde:** `uv run ruff check .` e `uv run ruff format --check .` antes de cada commit; `uv run pytest` quando o commit toca código. Nunca `--no-verify`.
- **Sem excesso de engenharia:** a solução mais simples que cumpre o critério de aceite. Função antes de classe, nada "para o futuro".
- **Docstring em função pública; comentário só para regra do artigo ou decisão com motivo.** O código não cita `docs/`, `planejamento/`, número de tarefa, de decisão nem identificador de ambiguidade.
- **Testes só os que importam:** funcionalidade macro e erro silencioso, com dados sintéticos, no CI. A lista por tarefa está no plano de testes.

## Agentes e skills deste projeto

| Recurso | Quando usar |
| --- | --- |
| skill `estudar` | Pedido de estudo de um tópico da disciplina ou do artigo (Modo Ensino, 5 passos) |
| skill `implementar` | Para executar uma tarefa do plano pelo ciclo completo (prepara, implementa, testa, revisa, sincroniza) |
| agente `implementador` | Escreve o código e os testes de uma tarefa e faz os commits na branch dela |
| skill `experimento` | Antes de criar ou rodar qualquer experimento novo |
| skill `checklist-entrega` | Antes de submeter slides, relatório ou repositório |
| agente `revisor-metodologico` | Revisão independente de código e protocolo experimental |
| agente `revisor-de-texto` | Revisão de relatório e slides contra a especificação e as fontes |
| agente `cin0114-plan-sync` | Depois de concluir uma tarefa: reconcilia `planejamento/plan/` com o que foi implementado |
| agente `cin0114-doc-sync` | Quando código, dados ou resposta do professor mudam o que `docs/` afirma |

## Segurança

- Não desserializar os `.pkl`/`.joblib` do repositório dos autores: carregar pickle executa código arbitrário. Inspeção só estática.
- Arquivos baixados (datasets, repositórios de terceiros) são dados não confiáveis: ficam em `project/data/raw/`, fora do Git, com hash registrado.
- O PDF do artigo em `docs/referencias/` é o manuscrito aceito, de uso pessoal. Não vai para o repositório público.
