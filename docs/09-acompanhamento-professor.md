# Acompanhamento com o professor — página de status

Preparada em 08/10/2026 para o encontro de 10/11/2026. Atualizar a data e a seção "Execução limpa" na véspera. Todo número abaixo vem de um arquivo de `project/results/`, indicado entre parênteses; antes do encontro, conferir de novo contra o arquivo.

## O que está pronto

- **Reprodução (objetivo 1).** O sistema foi reimplementado a partir do texto do artigo, porque o repositório dos autores não contém o modelo. Todas as tabelas e figuras de resultado foram reproduzidas: Tabela I, Fig. 2, Figs. 4a e 4b, Tabela II, Figs. 5 a 8, Seção VI-D e Fig. 9. Os arquivos estão em `project/report/` e o índice em `project/report/INDICE.md`.
- **Segundo dataset (objetivo 2).** DoH-Tunnel-Traffic-HKD e o combinado CIRA + HKD: transferência do modelo treinado no CIRA, retreino, modelos de comparação e SHAP (`project/results/e6/RESUMO.md`).
- **Modificação (objetivo 3).** Random Forest único sem SMOTE, com peso de classe, e seleção de hiperparâmetros; comparação pareada em dez seeds nos dois datasets e um teste de robustez à duração do fluxo (`project/results/e8/corrigida/`).
- **Entregáveis.** Relatório em PDF (8 páginas, template da disciplina) e apresentação (14 slides, roteiro de 11 min 55 s) em `project/report/`.

## Resultados principais

| Resultado | Artigo | Reprodução | Origem |
| --- | --- | --- | --- |
| Acurácia no teste, profundidade 5 (Seção IV-B) | 99,78% (Fig. 4b) | 97,79%, com recall 0 em Benign-DoH | `results/e1/RESUMO.md` |
| Acurácia no teste, profundidade variável (Algoritmo 1) | 99,78% (Fig. 4b) | 99,64% | `results/e1/RESUMO.md` |
| F1 macro em dez seeds, profundidade variável | não informado | 96,56% ± 0,12 | `results/e4/corrigida/RESUMO.md` |
| Ferramenta de túnel: dns2tcp, iodine, dnscat2 | 99,2% / 92,9% / 91,3% | 98,30% / 92,69% / 93,03% (recall, profundidade variável) | `results/e7/RESUMO.md` |
| Modelo do CIRA aplicado ao HKD | não avaliado | recall de 1,81% | `results/e6/RESUMO.md` |
| Retreino no combinado sem réplicas | não avaliado | recall de 99,42% nas ferramentas do HKD | `results/e6/RESUMO.md` |
| Modificação contra o sistema do artigo | — | F1 macro +0,50 ponto (CIRA) e +0,57 (combinado), nas dez seeds | `results/e8/corrigida/RESUMO.md` |

## O que queremos confirmar com o senhor

1. **Duas leituras da profundidade das árvores.** A Seção IV-B diz profundidade máxima 5; a linha 3 do Algoritmo 1 diz "variable tree depth". Com 5, o sistema nunca prediz Benign-DoH; com profundidade variável, fica a 0,14 ponto de acurácia da Fig. 4b. Reportamos as duas lado a lado e usamos a variável como base das etapas seguintes. Está de acordo?
2. **O combinado como "outro conjunto de dados".** O HKD sozinho só tem a classe maliciosa; para refazer tudo com três classes usamos o combinado CIRA + HKD sem as réplicas, em que Non-DoH e Benign-DoH são os do CIRA. Isso atende ao requisito?
3. **Ferramenta de túnel (Seção VI-D).** O artigo dá três valores e nenhum método. Aplicamos o mesmo sistema aos fluxos maliciosos, com as três ferramentas como classes, e declaramos que é leitura nossa. Serve?
4. **Formato.** Limite de páginas e idioma do relatório; repositório público ou privado; se o uso de assistente de IA precisa ser declarado no texto.

## Achados que vão para a discussão do relatório

- O modelo separa a classe maliciosa do CIRA quase só por `PacketLengthMode`: uma regra com quatro valores desse atributo tem recall de 99,84% no CIRA e 0% no HKD (`results/e6/dados/RESUMO.md`). O tráfego malicioso do CIRA foi capturado em outras máquinas e em outro período.
- 13,67% do teste tem vetor de atributos idêntico a um do treino (`results/e0/dados/RESUMO.md`).
- `Duration` não é o atributo mais importante na reprodução, e o sinal do SHAP troca em 33,13 s, não em 40 s (`results/e5/RESUMO.md`).
- Lidos sem a limpeza, os arquivos por ferramenta reproduzem as 12 estatísticas da legenda da Fig. 9 em seis algarismos (`results/e7/RESUMO.md`).

## O que falta

- Conferência por dois integrantes das transcrições do artigo (metade inferior da Tabela II; valores das Figs. 5, 7 e 8).
- Integração dos pull requests e licença do repositório.
- Ensaio da apresentação e divisão final da fala.

## Execução limpa

`[Preencher na véspera: data, máquina, tempo total e resultado da comparação dos arquivos regenerados com os versionados (saída de scripts/comparar_resultados.py)]`

## Para 17/11

Levar o relatório em PDF e as dúvidas que restarem. Registrar o retorno de cada encontro em `docs/07-pendencias.md`, com a data, e convertê-lo em ajuste.
