# 24 · entrega · relatório em PDF e apresentação em PPTX

**Onde:** `project/report/` (`relatorio.tex`, `relatorio.pdf`, `apresentacao.pptx`, `roteiro.md`), `project/scripts/` (script que monta os slides); modelos em `geracao_latex_and_pdf/`
**Objetivo:** os dois entregáveis finais, gerados a partir dos resultados versionados: o relatório em PDF, no template LaTeX da disciplina, e a apresentação em PPTX, no modelo de slides do CIn, que o usuário sobe no Google Slides.
**Depende de:** 17 (tabelas e figuras). Entra o que estiver executado até lá; se a modificação (15 e 16) não tiver sido feita, as seções correspondentes saem do relatório e dos slides.
**Demonstra:** `project/report/relatorio.pdf` e `project/report/apresentacao.pptx`. São os entregáveis "relatório em PDF" e "slides" da especificação.
**Quem executa:** o agente `gerador-entregaveis`. É a última tarefa do plano; a 19 (README e execução limpa) pode correr em paralelo.

## Pedido do usuário (07/10/2026)

- Relatório bem resumido e direto, sem enrolação, o mais breve possível, deixando claro tudo o que foi construído.
- Apresentação rápida, mostrando tudo o que foi construído, sem ficar extensa, cabendo no tempo com folga. Entregue em PPTX, para subir no Google Slides.
- Tamanho do relatório aprovado: alvo de 6 páginas, teto de 8.
- O número da disciplina é CIN0114; o "IF848" do título de exemplo do template não é usado.

Esta tarefa executa as tarefas 18 e 20: o conteúdo exigido, a lista de conferência e as limitações a declarar continuam descritos nelas; a forma, o tamanho e a geração dos PDFs são os daqui. Onde divergirem em tamanho ou formato, vale esta.

## Verificado em 07/10/2026

- `geracao_latex_and_pdf/template.tex`: classe `IEEEtran`, opção `conference`, em português, 649 linhas. Seções: Introdução; Trabalhos relacionados; Modelo de ameaça; Sistema proposto pelo artigo de referência; Solução proposta pela equipe (caso feita); Metodologia (dados do artigo, novo conjunto de dados, métricas); Resultados e discussões (reprodução, nos dois conjuntos; proposta de melhoria, caso feita); Conclusões e trabalhos futuros; referências em `thebibliography`. O título de exemplo cita "IF848" e precisa ser trocado. O template usa `algorithm` e `algpseudocode` e uma figura de exemplo em `imagens/`, que não acompanha o arquivo.
- `geracao_latex_and_pdf/Apresentação Padrão CIn-UFPE.pptx`: 16:9, 14 slides de exemplo, 11 layouts; o slide 2 traz as orientações de uso.
- O usuário informou em 07/10/2026 que instalou um compilador LaTeX; o agente confere qual está disponível antes de compilar. Não há LibreOffice; há Keynote, usado só para exportar um PDF de conferência dos slides.
- Não respondido pelo professor: limite de páginas e idioma. O template está em português; o relatório segue em português.

## Arquivos

- `project/report/relatorio.tex`, `project/report/relatorio.pdf` — novos.
- `project/report/apresentacao.pptx`, `project/report/roteiro.md` — novos. `project/report/apresentacao.pdf` só se a exportação de conferência ficar fiel.
- `project/scripts/make_slides.py` — novo: monta o `.pptx` a partir do modelo.
- `project/pyproject.toml`, `project/uv.lock` — grupo de dependência próprio para `python-pptx`, fora do conjunto de execução dos experimentos.

## O que fazer

1. Ler as entradas listadas no agente e conferir que `project/report/tables/` e `project/report/figures/` existem e estão atualizados.
2. Relatório: copiar o template, responder a cada pergunta de cada seção, apagar o texto de instrução. Alvo de 6 páginas, teto de 8. Tabelas por `\input` dos arquivos gerados.
3. Desenhar as duas figuras que nenhum script gera: túnel DNS sobre DoH com as premissas do atacante, e o pipeline do sistema.
4. Compilar, renderizar as páginas e conferir uma a uma.
5. Apresentação: de 12 a 14 slides, alvo de 12 minutos de fala em 15 disponíveis, no modelo do CIn, em PPTX compatível com o Google Slides; exportar um PDF de conferência e olhar página a página; escrever o roteiro com o tempo por slide.
6. Conferir cada número contra a origem e rodar o agente `revisor-de-texto` nos dois documentos.
7. Commits `docs(report)`.

## Risco

- Sem o compilador LaTeX, o PDF do relatório não sai: o agente para e relata o comando de instalação.
- O Google Slides pode trocar fonte ou deslocar caixas ao importar o `.pptx`: usar só layouts e espaços reservados do modelo; a conferência final no Google Slides é de uma pessoa.
- Relatório curto demais pode deixar pergunta da especificação sem resposta: a lista de conferência da tarefa 18 é o que impede isso.
- O template Overleaf do professor pode diferir deste arquivo: se a equipe trouxer outra versão, refazer a cópia.

## Critério de aceite

- [ ] `relatorio.pdf` compila sem erro, sem referência indefinida, com as seções do template, em até 8 páginas.
- [ ] Lista de conferência da tarefa 18 preenchida: cada pergunta da especificação com seção e parágrafo.
- [ ] Nenhum número digitado: tabelas por `\input`; números em frase conferidos contra a origem, com a lista no relato.
- [ ] As duas leituras de profundidade aparecem lado a lado onde a reprodução é citada.
- [ ] `apresentacao.pptx` com 12 a 14 slides no modelo do CIn, sem os slides de exemplo; `roteiro.md` com soma de tempos de até 13 minutos.
- [ ] **Pessoa:** o `.pptx` abre no Google Slides sem quebra de layout.
- [ ] Páginas do relatório e do PDF de conferência dos slides olhadas uma a uma em imagem.
- [ ] `revisor-de-texto` sem achado grave em aberto.
- [ ] Nenhum arquivo de `project/results/` alterado; lint e testes verdes.

## Verificação ao concluir

Gate de texto: G2, G3, G4, G7, G8, G9 (com o `revisor-de-texto`), G10.
