# 18 · entrega · relatório

> **Execução (07/10/2026):** a relatório é produzida pela tarefa [24](24-entrega-pdfs-finais.md), com o agente `gerador-entregaveis` e os modelos de `geracao_latex_and_pdf/`. Este arquivo continua valendo para o conteúdo exigido e a lista de conferência; em tamanho e formato vale a tarefa 24 (relatório: alvo de 6 páginas, teto de 8; apresentação: 12 a 14 slides em PPTX, para o Google Slides; a apresentação é feita mesmo sem a modificação).

> **Cumprida pela tarefa 24 (08/10/2026, commit `759ec29`):** `report/relatorio.tex` e `report/relatorio.pdf`, 8 páginas, revistos pelo `revisor-de-texto`. Os nomes de arquivo deste documento (`main.tex`, `refs.bib`, `relatorio_doh_xai.pdf`) não foram usados: as referências estão em `thebibliography`, dentro do `.tex`. **Fechamento de 08/10/2026 (`5999c1b`): concluída.** O relatório foi corrigido depois da revisão final (`3725f27`) e continua com 8 páginas. Fechados por Breno em 08/10/2026 (`docs/07-pendencias.md`, "Fechado"): o DOI das referências (fica como está) e o template no Overleaf. Sem frase sobre uso de IA (decisão 55a). **Resta, de pessoa:** a leitura do relatório pelos integrantes, com a lista de conferência pergunta → seção e parágrafo.

**Onde:** `report/` (cópia do template Overleaf), PDF final
**Objetivo:** o relatório em formato de artigo, com as nove seções e todas as perguntas da especificação respondidas em texto. Entrega em 18/11/2026.
**Depende de:** 17 para as seções 5 a 8. O passo 1 é da onda 0 e as seções 1 a 4 começam logo depois do seminário, sem esperar resultado
**Demonstra:** o PDF no template, com as nove seções e a lista de conferência pergunta → parágrafo. Entregável de 18/11.

## Reconciliado com as decisões 44 a 50 e com as respostas do professor (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** Q1 a Q6 foram respondidas em 07/10/2026 (`docs/07-pendencias.md`); Q7 (frase de declaração), Q9 e Q10 ficaram sem resposta do professor e foram fechadas pela equipe em 08/10/2026 (decisão 55a): sem frase de declaração, português, até 8 páginas, repositório público.

- **Q1:** a reimplementação a partir do texto é aceita, "tomando os devidos cuidados para que a reprodução seja a mais fiel possível". O passo 6 declara a reimplementação e as leituras adotadas.
- **Decisão 45, seções 6 e 7:** o relatório mostra as duas leituras de profundidade lado a lado, com os números de `results/e1/` (a de profundidade 5 como saiu, inclusive o recall zero em Benign-DoH), e declara qual foi usada como sistema base nas demais análises e por quê. As duas têm apoio textual (Seção IV-B e linha 3 do Algoritmo 1); nenhuma foi escolhida por aproximar o número.
- **Decisão 46, seção 7:** todas as tabelas e gráficos de resultado do artigo têm equivalente no relatório (lista no bloco de reconciliação da tarefa 17). O professor não disse qual referência vale entre a Tabela II e a Fig. 4b nem deu margem numérica: seguem as duas reportadas, com a distância célula a célula.
- **Decisão 47, seções 6 e 7:** P2 é o P1 refeito no combinado sem réplicas. O texto declara que o HKD sozinho só tem a classe maliciosa, que Non-DoH e Benign-DoH do combinado são os do CIRA (ressalva fechada pela equipe, sem resposta do professor: decisão 55a) e que o combinado publicado replica o HKD.
- **Decisão 48:** sem requisito adicional (Q3).
- **Decisão 49, seção 7:** a identificação da ferramenta de túnel (Seção VI-D e Fig. 9) entra, com a declaração de que o método é leitura da equipe, porque o artigo não o descreve.
- **Decisão 50:** o painel interativo é material de demonstração; a evidência do relatório são as figuras estáticas. O relatório pode citar que o painel existe e como abri-lo, sem tela do painel como resultado.

## Arquivos

- `report/main.tex` e arquivos do template — cópia do Overleaf indicado na especificação.
- `report/refs.bib` — referências em formato IEEE.
- `report/tables/`, `report/figures/` — da tarefa 17.
- `report/relatorio_doh_xai.pdf` — entrega.

## O que fazer

1. **Na onda 0:** copiar o template (`https://www.overleaf.com/read/vfhbdfgbtxqj#1169e9`) e ler suas instruções: idioma, limite de páginas, estilo de citação. Registrar em `docs/07-pendencias.md` o que responder a Q9 e perguntar ao professor o que o template não disser.
   - Definir o fluxo entre o repositório e o Overleaf, para as tabelas geradas não serem copiadas à mão: ou a fonte do relatório vive em `report/` e é enviada ao Overleaf por sincronização com Git ou upload do diretório, ou é compilada localmente. Escolher um, testar com uma tabela de exemplo e anotar no README.
2. Escrever as seções que não dependem de experimento, aproveitando o material do seminário:

| Seção | Conteúdo | Fonte interna |
| --- | --- | --- |
| 1. Introdução (breve) | As seis perguntas da especificação; contribuições em lista | `docs/referencias/seminario_doh_xai_cin0114.md`, seção 3; `docs/02-artigo.md`, seção 1 |
| 2. Trabalhos relacionados | Contribuição e limitação de cada trabalho | `docs/02-artigo.md:136-150` |
| 3. Modelo de ameaça | Ataques considerados, figura do túnel, premissas; marcado como inferência da equipe | `docs/02-artigo.md:120-134` |
| 4. Sistema do artigo | Componentes, entradas e saídas, métodos e por quê; figura da arquitetura; algoritmo | `docs/02-artigo.md:11-27` |

   A especificação pede figuras, algoritmos ou equações nas seções 3, 4 e 5. Nenhum script as gera, então são trabalho desta tarefa: um diagrama do túnel DNS sobre DoH com as premissas do atacante (seção 3); um diagrama do pipeline e o algoritmo de treino, redesenhados pela equipe ou reproduzidos do artigo com a citação na imagem (seção 4); um diagrama do modelo modificado ao lado do original (seção 5, se houver). Equações: normalização min-max, métricas, e a ponderação de classe de M1.

3. Escrever as seções que dependem de resultado:

| Seção | Conteúdo | Fonte interna |
| --- | --- | --- |
| 5. Solução da equipe | Só se a tarefa 15 foi feita: o que se espera melhorar, componentes, métodos e por quê | `results/e8/`, hipótese escrita na tarefa 15 |
| 6. Metodologia | Para cada dataset: quais dados, por que, o que representam, como treino/validação/teste foram formados, contagem por classe em cada conjunto; métricas; experimentos; decisões tomadas onde o artigo é omisso | `results/e0/`, `results/e6/dados/`, `planejamento/MEMORY/00-decisoes-travadas.md` |
| 7. Resultados e discussões | Sistema do artigo nos dois datasets; proposta da equipe nos dois; comparação com outros trabalhos; discussão, não só descrição | tabelas e figuras da tarefa 17 |
| 8. Conclusão e trabalhos futuros | Conclusão; limitações do sistema do artigo, da nossa reprodução e da proposta; trabalhos futuros | `docs/02-artigo.md:106-118`; críticas do seminário |
| 9. Referências | Formato IEEE, cada uma conferida na fonte, com DOI | — |

4. Na seção 6, dizer explicitamente que não há conjunto de validação separado: a validação é cruzada, dentro do treino, e apresentar o tamanho por classe de cada fold (tabela da tarefa 17).
5. Na seção 7, para cada tabela: o que o número significa para a detecção, a diferença para o artigo e as causas plausíveis, separando medido de hipótese. Reportar a divergência entre a Tabela II e a Fig. 4b do artigo.
6. Declarar: a reimplementação a partir do texto (o código público não contém o modelo), as leituras adotadas para as ambiguidades e as limitações da reprodução. Sobre o uso de assistente de IA (aprovado em 07/10/2026): nenhuma frase: a equipe fechou a parte em aberto de Q7 sem declaração (decisão 55a).
6a. Limitações medidas nos dados, que entram nas seções 6 e 8 com o número vindo de `results/`: na leitura de profundidade 5, o sistema não prediz Benign-DoH em nenhuma linha do teste (`results/e1/fiel/`); Malicious-DoH capturado em outras máquinas e dois meses depois das outras classes, confundimento que nenhum split interno remove; 13,7% do teste com vetor idêntico no treino, e as métricas sem essas linhas; 326 vetores presentes em mais de uma classe; teste com 115.911 amostras contra 115.910 do artigo; HKD replicado 20 vezes no combinado publicado, e o retreino sem réplicas; valor sentinela `-10` nas colunas de assimetria e seu efeito na leitura do SHAP.
7. Resumo e abstract por último.
8. Rodar o agente `revisor-de-texto` sobre o PDF e corrigir os achados. Leitura cruzada por outro integrante.

## Por quê

É um dos dois entregáveis obrigatórios de 18/11 e o documento que o professor corrige. A especificação lista as perguntas de cada seção e pede que sejam respondidas "de maneira clara, precisa e em formato de texto".

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:41` — template Overleaf e PDF.
- Mesma especificação, `:58-109` — seções e perguntas.
- `docs/01-requisitos.md`, "Seções do relatório" — mapa pergunta → fonte.
- `docs/06-padroes.md`, seção 4 — regras de escrita.

## Risco

- Deixar o texto para depois dos experimentos e não sobrar tempo: as seções 1 a 4 começam em 21/10, em paralelo com as tarefas 03 a 08.
- Seção 7 virar lista de números: o revisor de texto tem instrução específica para apontar isso.
- Afirmação sobre o artigo sem fonte: toda afirmação leva seção, tabela ou figura.
- Parágrafo genérico que serviria para qualquer artigo: reescrever com o fato específico do nosso caso.

## Critério de aceite

- [x] PDF compilado a partir do template, sem erro de compilação e sem referência quebrada. **Fechado em 08/10/2026:** `report/relatorio.pdf`, 8 páginas (executado: `mdls`, e as 8 páginas vistas uma a uma em `5999c1b`); compilado com `tectonic` no passo 22 da execução limpa, sem erro (`REVISAO-FINAL.md`); recompilado depois das correções de texto em `3725f27`.
- [x] As nove seções existem; a 5 só se P3 foi feito. **Fechado em 08/10/2026:** lido em `report/relatorio.tex`: oito `\section` (Introdução; Trabalhos relacionados; Modelo de ameaça; Sistema proposto pelo artigo de referência; Solução proposta pela equipe; Metodologia; Resultados e discussões; Conclusões e trabalhos futuros) e as Referências. A seção 5 está presente, porque P3 foi feito.
- [ ] **Pessoa:** cada pergunta da especificação (`:63-106`) tem resposta localizável: lista de conferência preenchida com seção e parágrafo. A lista não está em arquivo versionado; é feita na leitura do relatório pelos integrantes (item 7 de `docs/07-pendencias.md`, "O que resta de pessoa").
- [x] Seção 6 traz, para os dois datasets, a tabela de amostras por classe em cada conjunto. **Fechado em 08/10/2026:** visto no PDF, página 3: Tabela II (CIRA: bruto, limpo, Tabela I do artigo, treino, validação e teste, por classe) e Tabela III (segundo conjunto: publicado e sem réplicas, com treino, validação e teste, e o HKD isolado).
- [x] Todo número do texto confere com `report/tables/` ou com o artigo. **Fechado em 08/10/2026:** `REVISAO-FINAL.md`, V2: 115 afirmações numéricas do relatório recalculadas, 112 conferiam; as inexatas (achados I1, I2, M1 e M2) foram corrigidas em `3725f27`.
- [x] Referências em IEEE, todas citadas no texto e vice-versa. **Fechado em 08/10/2026:** executado em `5999c1b`: 12 `\bibitem` e 12 chaves em `\cite`, os dois conjuntos iguais. "Com DOI": não se aplica como escrito; só duas referências trazem DOI, e Breno fechou o ponto como está, porque a especificação pede só o formato IEEE (`docs/07-pendencias.md`, "Fechado").
- [x] Uso de IA: aprovado na disciplina; sem frase de declaração no relatório. **Fechado em 08/10/2026:** decisão 55a: a equipe fechou o ponto sem resposta do professor. Não é resposta dele; se ele pedir a frase nos encontros de 10/11 ou 17/11, ajusta-se.
- [x] `revisor-de-texto` sem achado grave em aberto. **Fechado em 08/10/2026:** achados da revisão de texto tratados em `17a278b`; `REVISAO-FINAL.md`, V8, sem frase proibida, com os achados de texto I1 a I3 e M1 a M5 corrigidos em `3725f27`, `c74fc3f` e `3e42795`.
- [ ] **Pessoa:** leitura do relatório pelos integrantes, para que todos consigam defendê-lo (item 7 de `docs/07-pendencias.md`, "O que resta de pessoa").

## Testes

Sem teste automático. Seção "Tarefa 18" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): revisão N3 pelo `revisor-de-texto` e conferência de cada número contra `results/`.

## Verificação ao concluir

Gate de texto: G8, G9 (`revisor-de-texto`), G10. Antes de enviar: skill `checklist-entrega projeto`.
