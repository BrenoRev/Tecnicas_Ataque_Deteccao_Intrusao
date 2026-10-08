---
name: checklist-entrega
description: Roda a checklist de entrega do projeto CIN0114 item a item e reporta OK, Pendente ou Não aplicável com a evidência de cada um. Use antes de submeter slides do seminário, relatório, repositório ou slides do projeto, e sempre que alguém disser que uma entrega está pronta. Argumento - seminario ou projeto.
---

# Checklist de entrega

Argumento: `seminario` ou `projeto`. Sem argumento, pergunte qual.

## Como executar

1. Leia a especificação oficial em `docs/referencias/` e `docs/01-requisitos.md`.
2. Para cada item da lista correspondente, **verifique de fato**: abra o arquivo, rode o comando, conte as seções. Não marque `OK` com base no que foi dito na conversa.
3. Reporte em tabela: item, status (`OK` / `Pendente` / `Não aplicável`), evidência (arquivo e linha, saída de comando) ou o que falta.
4. Item que depende de algo fora do repositório (ensaio, aprovação do professor, envio no Classroom) é `Pendente` até a equipe confirmar. Pergunte.
5. Termine com a lista só dos pendentes, em ordem de gravidade. Não declare a entrega pronta se houver item `Pendente` marcado como exigido.

Os itens marcados **[exigido]** vêm da especificação do professor. Os demais são padrão interno da equipe (`docs/06-padroes.md`).

## seminario

Conteúdo

- [ ] **[exigido]** Introdução com motivação, justificativa e principais contribuições.
- [ ] **[exigido]** Trabalhos relacionados com contribuições e limitações de cada um.
- [ ] **[exigido]** Solução proposta: arquitetura e funcionamento.
- [ ] **[exigido]** Experimentos: dados utilizados e experimentos realizados.
- [ ] **[exigido]** Resultados expostos e analisados.
- [ ] **[exigido]** Conclusão com principais limitações e problemas do sistema e sugestões detalhadas de melhoria.
- [ ] Modelo de ameaça apresentado e marcado como inferência da equipe.
- [ ] Todo número tem fonte: seção, tabela ou figura do artigo, ou `scripts/metricas_fig4.py`.
- [ ] Números recalculados conferem com a saída atual de `cd project && python3 scripts/metricas_fig4.py`.
- [ ] Críticas formuladas no limite do que o artigo permite afirmar (ver ajustes em `docs/07-pendencias.md`).

Formato

- [ ] **[exigido]** Modelo institucional de apresentação do CIn.
- [ ] **[exigido]** Só tópicos, bullets e imagens; nenhum slide com texto longo.
- [ ] Figuras do artigo com citação da fonte na imagem.
- [ ] Nomes dos quatro integrantes corretos na capa.
- [ ] Revisão de português.

Apresentação

- [ ] **[exigido]** Ensaio cronometrado em até 15 minutos.
- [ ] Divisão de fala definida e perguntas prováveis distribuídas.
- [ ] **[exigido]** Slides enviados pelo Classroom até 14/10/2026.

## projeto

Objetivos

- [ ] **[exigido]** P1: sistema do artigo implementado e executado; resultados ao lado dos do artigo, com a diferença.
- [ ] **[exigido]** P2: resultados do mesmo sistema em outro dataset.
- [ ] **[exigido]** P2: escolha do dataset justificada no relatório.
- [ ] P3 (opcional): modificação implementada e avaliada nos dois datasets.
- [ ] Requisitos adicionais do professor: não há (resposta de 07/10/2026 e decisão 48); `Não aplicável`, salvo pedido novo registrado em `docs/07-pendencias.md`.

Relatório

- [ ] **[exigido]** PDF no template da disciplina (`geracao_latex_and_pdf/template.tex`, decisão 53), formato de artigo, em até 8 páginas.
- [ ] **[exigido]** Abstract/Resumo com contexto, problema, soluções existentes, método e resultados.
- [ ] **[exigido]** 1. Introdução breve, respondendo às seis perguntas da especificação, com contribuições em lista.
- [ ] **[exigido]** 2. Trabalhos relacionados com contribuições e limitações.
- [ ] **[exigido]** 3. Modelo de ameaça com figuras, algoritmos ou equações e premissas.
- [ ] **[exigido]** 4. Sistema proposto pelo artigo: componentes, entradas, saídas, métodos e por quê.
- [ ] **[exigido se P3]** 5. Solução da equipe.
- [ ] **[exigido]** 6. Metodologia: para cada dataset, origem, motivo, o que representa, formação de treino/validação/teste e contagem por classe em cada conjunto.
- [ ] **[exigido]** 7. Resultados e discussões, com gráficos e tabelas, comparação com outros trabalhos e discussão (não só descrição).
- [ ] **[exigido]** 8. Conclusão, limitações e trabalhos futuros.
- [ ] **[exigido]** 9. Referências em formato IEEE.
- [ ] Todo número do relatório confere com um arquivo em `results/`.
- [ ] Trilha fiel e trilha corrigida identificadas em toda tabela.
- [ ] Limitações da própria reprodução declaradas.
- [ ] Revisão pelo agente `revisor-de-texto` sem achado grave em aberto.

Código e repositório (comandos rodados dentro de `project/`)

- [ ] **[exigido]** Link do GitHub acessível ao professor.
- [ ] **[exigido]** Todos os códigos comentados.
- [ ] Clone limpo + instruções do README reproduzem os resultados (testar em diretório novo).
- [ ] Dependências com versão fixada.
- [ ] Seeds fixadas; resultado idêntico em duas execuções.
- [ ] Dados fora do Git, com manifesto de hashes (`data/manifest.json`) e script de conferência (`data/verify.py`).
- [ ] Nenhuma credencial, pickle de terceiros ou PDF do artigo versionado.
- [ ] Sem caminho absoluto, sem referência interna e sem arquivo proibido: as três checagens de higiene de `.github/workflows/ci.yml` não devolvem nada.
- [ ] Testes passam; lint limpo.
- [ ] Revisão pelo agente `revisor-metodologico` sem achado bloqueante em aberto.
- [ ] Histórico com uma só identidade Git, aceito pela equipe (decisão 55); nenhum commit com coautoria de ferramenta.
- [ ] Uso de assistente de IA: aprovado na disciplina (07/10/2026); sem frase de declaração no README e no relatório (decisão 55), salvo pedido do professor.
- [ ] `entregaveis-apresentacao/` idêntico a `project/report/` em `relatorio.pdf`, `apresentacao.pptx` e `roteiro.md` (`cmp`).
- [ ] Nenhum commit com `Co-Authored-By` (`git log --format=%B | grep -ci "co-authored-by"` devolve 0).
- [ ] Nenhum arquivo interno (`docs/`, `planejamento/`, `.claude/`, `CLAUDE.md`) dentro de `project/`.

Apresentação (só com P3)

- [ ] **[exigido]** Slides no modelo do CIn, entregues em PPTX, e apresentação de 15 minutos em 19/11/2026, por três integrantes.
