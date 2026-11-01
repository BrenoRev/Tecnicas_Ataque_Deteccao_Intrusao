# CIN0114 — IDS explicável para ataques DNS over HTTPS

Projeto da disciplina CIN0114, Técnicas de Ataque e Detecção de Intrusão (CIn/UFPE, 2026.2), do Prof. Paulo Freitas de Araujo Filho. A equipe reproduz e avalia o sistema de:

> T. Zebin, S. Rezvy and Y. Luo, "An Explainable AI-Based Intrusion Detection System for DNS Over HTTPS (DoH) Attacks," IEEE Trans. Inf. Forensics Security, vol. 17, pp. 2339-2349, 2022, doi: 10.1109/TIFS.2022.3183390.

## Equipe

- Amanda Arruda (aams2)
- Breno Silva Xavier de Souza (bsxs)
- João Henrique Portela (jhpbs)
- Antonio Gonzaga (agla)

## Onde está o código

O código, os testes, os resultados, o relatório e as instruções de instalação e de execução ficam em [`project/`](project/README.md). É o único lugar necessário para reproduzir os resultados.

As demais pastas:

| Pasta | Conteúdo |
| --- | --- |
| `geracao_latex_and_pdf/` | modelo de slides do CIn e modelo LaTeX, usados para gerar a apresentação |
| `docs/` | material de estudo da equipe sobre o artigo, os dados e a disciplina |
| `planejamento/` | plano de implementação e registro das decisões da equipe |
| `.github/`, `.githooks/` | integração contínua, modelo de pull request e hooks de commit |
| `.claude/` | configuração do assistente de IA usado no desenvolvimento |

Depois de clonar, ative os hooks do Git uma vez, na raiz do repositório:

    git config core.hooksPath .githooks
