# 06. Padrões da equipe

Regras internas de código, commits, escrita e revisão. Vão além do que a especificação exige (ver [01-requisitos.md](01-requisitos.md)); servem para o trabalho sair reprodutível e para que qualquer integrante consiga defender qualquer parte.

## 1. Autoria e uso de IA

O trabalho é apresentado e arguido em sala. O critério prático é um só: **quem assina consegue explicar**.

- Nenhum trecho de código ou de texto entra sem que pelo menos um integrante o tenha lido, entendido e, se preciso, reescrito com as próprias palavras.
- Quem faz o commit responde por ele na apresentação.
- O uso de assistentes de IA está aprovado na disciplina (registrado em [07-pendencias.md](07-pendencias.md), 07/10/2026). Os commits não levam coautoria de ferramenta, por limpeza e padrão do histórico. Se o professor pedir declaração, a mesma frase vai no README e no relatório; se não pedir, nenhuma.
- O assistente serve para acelerar leitura, revisão, checagem de contas e rascunho. Decisão metodológica, interpretação de resultado e texto final são da equipe.

O que faz um trabalho parecer não escrito por quem o entrega é a falta de decisão própria: código genérico demais para o problema, comentário que repete a linha, texto que não se compromete com nada. As regras abaixo atacam isso diretamente.

## 2. Código

**Estrutura**

O repositório Git é a raiz; o código fica na pasta `project/`. A árvore abaixo é o conteúdo dela. `docs/`, `planejamento/` e `.claude/` ficam na raiz, ao lado de `project/`, com `.github/` e `.githooks/`.

```
├── README.md            # objetivo, setup, como reproduzir cada tabela e figura
├── pyproject.toml       # dependências com versão fixada
├── data/                # manifesto de hashes e script de conferência; dados fora do Git
├── src/                 # código reutilizável
├── scripts/             # um script por experimento, executável da raiz
├── tests/               # testes com dados sintéticos, rodam no CI
├── jobs/                # scripts de submissão ao cluster, só para o que rodar no Apuana (decisão 42)
├── results/             # métricas, figuras e logs gerados por script
└── report/              # fonte LaTeX e PDF do relatório
```

**Regras**

A versão normativa, usada pelo agente implementador e pelo lint, está em `.claude/rules/codigo.md`, `commits.md`, `testes.md` e `fluxo-implementacao.md`. O resumo abaixo não pode contradizê-la.

- Python 3.12 com `ruff` para formatação e lint. Versões fixadas em `project/pyproject.toml` e `uv.lock` (tarefa 01): scikit-learn 1.9.1, imbalanced-learn 0.14.2, mlxtend 0.25.0, xgboost 3.4.1, shap 0.52.0, pandas 3.0.6, numpy 2.3.5, pyarrow 25.0.1, matplotlib 3.11.2, scipy 1.18.1; pytest 9.1.1 e ruff 0.16.10. Compatibilidade verificada em `planejamento/MEMORY/01-discovery-stack.md`; `explainerdashboard` 0.5.8 só entra se o painel for exigido.
- Identificadores em inglês, comentários e docstrings em português. Escolher isso uma vez e manter.
- Função faz uma coisa. Se precisa de comentário para explicar o que faz, o nome está ruim.
- Comentário explica **por que**, nunca o quê. Bom: `# ajusta o scaler só no treino; ajustar no conjunto todo vaza min e max do teste`. Ruim: `# normaliza os dados`.
- Toda escolha feita onde o artigo é omisso leva um comentário com a decisão e o motivo, citando a seção, tabela ou figura do artigo: `# O artigo não diz com que dados o meta é treinado (Seção IV-B); usamos o treino original normalizado`. O comentário não cita arquivo de `docs/` ou `planejamento/`, número de tarefa, de decisão nem identificador de ambiguidade: esse rastro fica na tabela de ambiguidades de `docs/02-artigo.md`.
- Nenhum número mágico. Hiperparâmetros ficam em configuração, com a origem ao lado (seção do artigo ou "escolha nossa").
- Caminhos relativos à raiz do repositório. Nada de caminho de máquina local.
- Seeds explícitas em tudo que sorteia: split, SMOTE, Random Forest, validação cruzada.
- Sem abstração antecipada. Três scripts parecidos são melhores que um framework que ninguém da equipe sabe explicar. Classe só quando há estado; o resto é função.
- Sem `try/except` genérico, sem código morto, sem funções "para uso futuro".
- Teste automatizado da funcionalidade macro e de onde o erro é silencioso: split sem interseção entre treino e teste, scaler ajustado só no treino, nenhuma amostra sintética fora do treino, métricas da Fig. 4b, e um teste de ponta a ponta. Poucos testes, com dados sintéticos, rodando no CI do GitHub. A lista por tarefa está em `planejamento/plan/PLANO-DE-TESTES.md`.

A especificação pede "códigos comentados". Isso se cumpre com docstring curta em cada função pública e comentários de justificativa nos pontos de decisão, não com um comentário por linha.

**Notebooks**

- Um por assunto, com nome sem espaço nem acento.
- Executado do início ao fim com kernel limpo antes do commit.
- Lógica que será reutilizada sai do notebook e vai para `src/`.

## 3. Git

- Conventional Commits: `feat`, `fix`, `test`, `exp`, `refactor`, `docs`, `chore`, `ci`, com escopo opcional. Mensagens em português.
- Commit pequeno, com uma mudança só. A mensagem diz o que mudou e por quê.
- Nenhum commit leva `Co-Authored-By` nem assinatura de ferramenta. Uma frase sobre o uso de assistente de IA (aprovado em 07/10/2026) entra no README e no relatório só se o professor pedir.
- Todo commit passa pelo lint e pela formatação (`ruff`). Os hooks em `.githooks/` barram o commit fora do padrão; ative com `git config core.hooksPath .githooks`. Não se usa `--no-verify`.
- Uma tarefa por vez: implementa, testa, revisa, integra. A tarefa seguinte não começa com a anterior vermelha.
- Uma branch por tarefa (`tarefa/NN-nome`), integração por pull request com revisão de outro integrante e CI verde.
- Cada integrante faz os próprios commits, com a própria conta. O histórico é a evidência de contribuição.
- Fora do Git: dados, modelos serializados, o PDF do artigo, ambiente virtual, credenciais.
- `results/` entra no Git quando o arquivo é pequeno e é citado no relatório.

## 4. Escrita (relatório e slides)

**Conteúdo**

- Toda afirmação sobre o artigo traz seção, tabela ou figura.
- Todo número nosso aponta para um arquivo em `results/`.
- Resultado vem com interpretação: o que o número significa para quem opera um IDS.
- Limitação da nossa reprodução é declarada com o mesmo rigor que cobramos do artigo.
- Não afirmar mais do que o experimento sustenta. "Não reproduzimos" é resultado válido.

**Forma**

- Português direto, frases curtas, voz ativa. Termo técnico na forma da literatura (stacking ou empilhamento, mas sempre o mesmo ao longo do texto).
- Uma ideia por parágrafo, com a conclusão na primeira frase.
- Cortar: adjetivo sem número ("resultado excelente"), frase de transição vazia ("vale ressaltar que"), repetição da mesma ideia em três formas, conclusão que só reescreve a introdução.
- Listas só quando o conteúdo é lista. Relatório é em texto corrido; a especificação pede respostas "em formato de texto".
- Slides: tópicos, bullets e imagens, sem texto longo (regra da especificação). Uma mensagem por slide.
- Figura reproduzida do artigo leva a citação na própria imagem. Gráfico nosso tem eixo rotulado e unidade.
- Referências em formato IEEE, cada uma conferida na fonte original, com DOI.

**Teste final de um parágrafo**: se ele serviria igual em um relatório sobre outro artigo, está genérico e precisa de um fato específico do nosso.

## 5. Revisão

Nada é dado como pronto sem passar por duas leituras:

1. **Revisão automática**: agente `revisor-metodologico` para código e experimento; agente `revisor-de-texto` para relatório e slides.
2. **Revisão humana cruzada**: outro integrante lê, roda e assina o pull request.

Ordem de prioridade na revisão de experimento:

1. Vazamento: o teste influenciou alguma etapa? A reamostragem tocou validação ou teste?
2. Fidelidade: a trilha fiel segue o artigo? A corrigida está identificada como corrigida?
3. Reprodutibilidade: roda do zero com um comando e dá o mesmo número?
4. Métrica: a média está nomeada? A classe rara aparece?
5. Rastreio: o número do relatório é o do arquivo de resultado?
6. Clareza: outro integrante entende sem perguntar?

## 6. Checklists de entrega

Ficam nas skills, para serem executadas e não só lidas:

- `checklist-entrega seminario`
- `checklist-entrega projeto`
