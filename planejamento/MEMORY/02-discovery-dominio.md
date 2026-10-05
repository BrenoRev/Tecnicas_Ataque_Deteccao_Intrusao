# Domínio — discovery (ponteiros)

O discovery de domínio foi feito em 06/10/2026 e está em `docs/`. Este arquivo só aponta para os fatos que o plano usa, para não duplicar.

## Fatos (com evidência)

**O que é cobrado**

- P1 reproduzir, P2 outro dataset com justificativa, P3 opcional com ponto extra — `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:27-31`.
- Entrega em 18/11/2026: relatório e link do GitHub com códigos comentados; apresentação em 19/11 só para quem modificar — mesma especificação, `:33-35`.
- Relatório no template Overleaf, formato de artigo, 9 seções, referências IEEE — `:41`, `:58-109`.
- Seção 6 exige, para cada dataset, formação de treino/validação/teste e contagem por classe em cada conjunto — `:89-94`.
- Seção 7 pede discussão e comparação com outros trabalhos, não só descrição — `:96-97`.
- Mapa requisito → evidência — `docs/01-requisitos.md`, seção "Rastreabilidade".

**O sistema do artigo**

- Pipeline declarado, com seção de origem de cada etapa — `docs/02-artigo.md`, seção 2.
- Alvos numéricos: Fig. 4a, Fig. 4b, Tabela II — `docs/02-artigo.md`, seção 3; contagens conferíveis com `scripts/metricas_fig4.py:13-24`.
- Split estratificado 90/10 e validação cruzada sobre amostras reais, deduzidos da Fig. 4a — `docs/02-artigo.md`, seção 4.
- 18 ambiguidades (A1 a A18) com padrão proposto — `docs/02-artigo.md`, seção 5.
- Modelo de ameaça inferido — `docs/02-artigo.md`, seção 7.

**O código dos autores**

- Não contém o sistema proposto; um Random Forest único com `class_weight='balanced'`, `random_state=42`, rótulos `0=Non-DoH, 1=Benign-DoH, 2=Malicious-DoH`, coluna `Attack_label` — `docs/03-auditoria-repositorio.md`, seções "O script de modelagem" e "Artigo contra código".

**Dados**

- 29 atributos numéricos e 5 identificadores que não entram no modelo — `docs/04-dados.md`, seção "Colunas".
- Contagens brutas (897.493 / 19.807 / 249.836) contra a Tabela I (889.809 / 19.746 / 249.553) — `docs/04-dados.md`, seção "Contagens".
- Split implícito por classe — `docs/04-dados.md`, seção "Split implícito no artigo".
- Riscos de vazamento específicos — `docs/04-dados.md`, seção "Riscos de vazamento".
- Segundo dataset: HKD (dnstt 46.080, tcp-over-dns 30.040, tuns 29.040 fluxos) e combinado (`l1/l2/l3-total-add.csv`) — `docs/04-dados.md`, seção 3.

**Experimentos**

- E0 a E8, trilhas fiel e corrigida, protocolo comum, métricas — `docs/05-plano-experimental.md`.

## Problemas / riscos

- Perguntas enviadas ao professor em 07/10/2026 (Q1 a Q6, Q9, Q10 e parte de Q7), ainda sem resposta; Q7 (uso de IA) resolvida — `docs/07-pendencias.md`, "Perguntas ao professor". O plano assume a resposta mais provável e isola o que depende delas (ver `03-sintese.md`).
- A reprodução pode não chegar perto da Fig. 4b por causa das ambiguidades — `docs/07-pendencias.md`, "Riscos e plano B".

## Perguntas em aberto / a decidir

- Alvo oficial de "resultados próximos" (Q2) → decisão 10 assume Fig. 4b.
- Segundo dataset (Q4) → decisão 11 assume HKD + combinado.
- Subclassificação por ferramenta (Q5) e painel (Q6) → tarefas condicionais 21 e 12.
