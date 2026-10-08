# Central de conhecimento do projeto

Tudo o que a equipe precisa para sair do seminário e chegar ao projeto entregue. Cada arquivo responde a uma pergunta.

| Arquivo | Pergunta que responde |
| --- | --- |
| [01-requisitos.md](01-requisitos.md) | O que o professor cobra, quando e em que formato? |
| [02-artigo.md](02-artigo.md) | O que exatamente o artigo diz que fez, e o que ele deixa em aberto? |
| [03-auditoria-repositorio.md](03-auditoria-repositorio.md) | O que dá para aproveitar do código dos autores? |
| [04-dados.md](04-dados.md) | Que dados usamos, como são, e qual será o segundo dataset? |
| [05-plano-experimental.md](05-plano-experimental.md) | Que experimentos rodar, com que protocolo e que métricas? |
| [06-padroes.md](06-padroes.md) | Como escrevemos código, commits e texto, e como revisamos? |
| [07-pendencias.md](07-pendencias.md) | O que está indefinido e o que perguntar ao professor? |
| [08-inventario-dados.md](08-inventario-dados.md) | O que há, de fato, nos arquivos baixados, e o que isso muda? |

Material de origem, em `docs/referencias/`:

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md`: especificação oficial.
- `docs/referencias/seminario_doh_xai_cin0114.md`: documento consolidado do seminário (análise crítica, roteiro de slides).
- `docs/referencias/Guia de estudo do seminário CIN0114.md`: guia por bloco e divisão de fala.
- `docs/referencias/zebin2022_manuscrito_aceito.pdf`: manuscrito aceito do artigo, obtido do repositório institucional da Brunel University (https://bura.brunel.ac.uk/handle/2438/27256). A paginação e pequenos detalhes de edição podem diferir da versão final do IEEE Xplore; ao citar no relatório, confira na versão publicada.

## Estado em 08/10/2026

Reconciliado com o repositório no commit `759ec29` (branch `tarefa/24-entregaveis`).

- Lidos e conferidos: especificação, artigo completo, repositório dos autores, página do dataset, código do extrator de atributos (DoHLyzer).
- Dados baixados e inventariados em 07/10/2026 ([08-inventario-dados.md](08-inventario-dados.md)).
- Sistema implementado e todos os experimentos (E0 a E8) executados com os dados reais em 07 e 08/10/2026. Os resultados e a interpretação de cada um estão em `project/results/e<k>/`, no `RESUMO.md`; esta central aponta para eles e não os copia.
- Relatório, apresentação, tabelas e figuras gerados em `project/report/`; o índice que liga cada item à origem é `project/report/INDICE.md`.
- Não feito ainda: integração na `main`, conferências de pessoa, README completo e execução limpa. A lista está em [07-pendencias.md](07-pendencias.md), seção "O que resta de pessoa".
- Próxima entrega: slides do seminário em 14/10/2026.

## Como as afirmações desta central foram verificadas

- Texto do artigo: leitura integral do manuscrito aceito. As citações trazem seção, tabela ou figura.
- Números recalculados: `cd project && python3 scripts/metricas_fig4.py`, a partir das contagens da Figura 4.
- Repositório dos autores: clone em 06/10/2026, commit `38e2f23`, leitura dos arquivos e do histórico git. Nenhum pickle foi carregado.
- Colunas do dataset: lidas do código-fonte do DoHLyzer (`meter/flow.py`) e conferidas contra o cabeçalho dos CSVs em 07/10/2026.
- Medições nos dados e resultados de modelo: arquivo em `project/results/`, gerado por script versionado, com o commit e a seed no `run.json` ao lado. Todo número citado nesta central traz o caminho do arquivo.
- O que não pôde ser verificado está marcado como `[A verificar]`.
