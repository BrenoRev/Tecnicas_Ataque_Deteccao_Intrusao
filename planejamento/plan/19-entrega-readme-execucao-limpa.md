# 19 · entrega · README, execução limpa e checklist final

**Onde:** `README.md`, repositório inteiro
**Objetivo:** o professor abre o link do GitHub, entende o que há ali e consegue reproduzir os resultados do relatório sem falar com a equipe. Entrega em 18/11/2026.
**Depende de:** 17 para a execução limpa e o README; 18 só para o envio final (passo 10)
**Demonstra:** README com a tabela resultado → script → arquivo e a execução limpa feita por outro integrante. Entregável "link do GitHub com os códigos comentados".

## Reconciliado com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.**

- **Decisão 44: a execução limpa roda na própria sessão de implementação, nesta máquina**, em um clone novo, em diretório novo. Deixa de valer a espera por um integrante designado para executar. Efeito, dito sem atenuar: a execução deixa de ser feita por quem não escreveu o código e deixa de testar outra máquina; o que ela continua testando é que um clone limpo, com o ambiente do lock e os dados conferidos pelo manifesto, regenera os `metrics.json` versionados. A leitura e a aprovação do pull request por outro integrante (G10) continuam sendo de uma pessoa.
- **Decisão 50: dependência nova e comando do painel no README.** `explainerdashboard==0.5.8` entra no `pyproject.toml` na tarefa 12. O README ganha a seção do painel: o comando que o sobe localmente, o endereço em que ele responde, que o modelo é treinado na hora e que nada é serializado. A instalação por `requirements.txt` (passo 6) confere também essa dependência.
- **Tabela resultado → script → arquivo (passo 1):** cobre todas as tabelas e gráficos de resultado do artigo (decisão 46; lista no bloco de reconciliação da tarefa 17), as duas leituras de profundidade (decisão 45), o P1 refeito no combinado sem réplicas (decisão 47) e a ferramenta de túnel (decisão 49). A ordem dos scripts inclui `e7_ferramenta.py`.
- **Custo da execução limpa, medido até aqui:** `scripts/e1_reproducao.py` leva cerca de 56 minutos (902 s na profundidade 5 e 2.473 s na profundidade variável, com a máquina carregada na segunda). Os demais scripts ainda não têm tempo medido; o README recebe o tempo de cada um à medida que forem executados.
- O README declara as duas leituras de profundidade e onde está cada resultado (`results/e1/fiel/` e `results/e1/variante/`).

## Arquivos

- `README.md` — completar.
- `LICENSE` e nota de uso — a tarefa 01 não os criou (licença pendente da equipe; `README.md` tem `Licença: [Preencher]`). Criar quando a equipe decidir e conferir aqui.
- Todo o repositório — revisão final de comentários e de higiene.

## O que fazer

1. Completar o `README.md`: o que é o projeto e qual artigo reproduz; integrantes; requisitos (uv ou pip, Python 3.12); como obter os dados e conferir os hashes; a ordem dos scripts e o que cada um gera; tabela "resultado do relatório → script → arquivo em `results/`"; tempo aproximado de cada script, medido; limitações conhecidas.
2. Uso de assistente de IA: aprovado na disciplina (07/10/2026). Só se o professor pedir (parte em aberto de Q7): a mesma frase no README e no relatório; caso contrário, nada.
3. Revisar os comentários do código contra `docs/06-padroes.md`: docstring curta em toda função pública, comentário de justificativa nos pontos de decisão, com a seção do artigo onde ele é omisso, e nenhuma referência a arquivo interno, tarefa ou decisão (o mesmo grep do CI: `grep -rnE "docs/|planejamento/|\.claude/|[Dd]ecis[ãa]o [0-9]|[Tt]arefa [0-9]|\b[AQ][0-9]{1,2}\b" --include="*.py" --include="*.md" --include="*.json" src scripts tests data README.md results` não devolve nada). A especificação pede "todos os códigos comentados".
4. **Primeira execução limpa em 10/11**, com o que existir até lá, para o problema aparecer com uma semana de folga. **Congelar os experimentos em 13/11**: depois dessa data só entram correções. A execução final repete o procedimento: executar do zero, em clone e diretório novos, na própria sessão de implementação (decisão 44; o Apuana continua opção pela decisão 42); o README registra onde os resultados versionados foram gerados, com máquina e versões: clonar, `uv sync --locked`, colocar os dados, `data/verify.py`, rodar os scripts na ordem do README.
5. Comparar os `metrics.json` gerados com os versionados. Diferença em qualquer métrica é defeito a corrigir ou a explicar no README.
6. Repetir a instalação pelo `requirements.txt`, com pip (`pip install -r requirements.txt` e depois `pip install -e .`), para garantir o caminho de quem não usa uv.
7. Conferir higiene: sem dados, sem modelos serializados, sem PDF do artigo, sem credenciais, sem caminho absoluto.
8. Conferir que o histórico tem commits dos quatro integrantes.
9. Rodar a skill `checklist-entrega projeto` e resolver todo item pendente marcado como exigido.
10. Dar acesso ao professor (ou tornar público, conforme Q10) e enviar o link junto com o PDF.

## Por quê

A especificação pede "link do Github com todos os códigos comentados". Reprodução em máquina limpa é o que separa código que roda para quem escreveu de código reprodutível, e é o critério interno da equipe (`CLAUDE.md`, regra 5).

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:34` — entregável e prazo.
- `.claude/skills/checklist-entrega/SKILL.md`, seção "projeto" — itens a verificar.
- `planejamento/plan/VERIFICACAO.md`, "Execução limpa" — sequência de comandos.
- `docs/06-padroes.md:49` — como "códigos comentados" é cumprido.

## Risco

- A execução limpa falhar na véspera: por isso a primeira tentativa é em 10/11.
- A execução completa de todos os scripts leva horas (validação cruzada da tarefa 08, dez seeds das tarefas 11 e 15). Medir os tempos na primeira execução e registrar no README; a execução final começa em 16/11, não em 18/11.
- Resultado não determinístico entre máquinas (paralelismo, versão de BLAS): seeds fixadas; se ainda variar, registrar a ordem de grandeza da variação no README.
- Dados indisponíveis para o professor: o README explica o download manual do CIRA e indica o hash.

## Critério de aceite

- [ ] Execução limpa concluída na sessão de implementação, em clone novo, com os `metrics.json` gerados iguais aos versionados (decisão 44). O relato diz que não foi feita por outro integrante nem em outra máquina.
- [ ] README com o comando do painel e com `explainerdashboard` entre as dependências (decisão 50).
- [ ] Instalação por `requirements.txt` testada.
- [ ] README com a tabela resultado → script → arquivo, cobrindo todas as tabelas e figuras do relatório.
- [ ] `git ls-files | grep -E "\.(pkl|joblib|pcap|parquet)$|^data/(raw|processed)/|referencias/.*\.pdf"` não devolve nada. Arquivos pequenos de resultado em `results/` podem ser CSV.
- [ ] `grep -rnE "/Users/|/home/|[A-Z]:\\\\" --include="*.py" src scripts tests data` não devolve nada (o mesmo grep do CI).
- [ ] `git shortlog -sn` mostra os quatro integrantes.
- [ ] Checklist do projeto rodada, sem item exigido pendente.
- [ ] Link e PDF enviados até 18/11/2026.

## Testes

Seção "Tarefa 19" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de entrega: G1–G4, G7–G10, mais a execução limpa descrita em `VERIFICACAO.md`.
