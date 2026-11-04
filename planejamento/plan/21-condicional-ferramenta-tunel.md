# 21 · reprodução · identificação da ferramenta de túnel (E7)

**Onde:** `scripts/e7_ferramenta.py`, `src/doh_ids/data.py`, `tests/test_data.py`, `results/e7/`
**Objetivo:** reproduzir a identificação da ferramenta de túnel (Seção VI-D do artigo e Fig. 9): as três acurácias por ferramenta e as duas distribuições da figura. É parte de P1 desde as decisões 46 e 49.
**Depende de:** 08, 13. Na ordem de execução, entra depois da 14
**Demonstra:** `results/e7/`: métricas por ferramenta ao lado dos três valores da Seção VI-D e a figura equivalente à Fig. 9. P1 (seção 7).

> **Deixou de ser condicional em 07/10/2026 (decisão 49).** O professor respondeu a Q5 pedindo uma conversa depois da aula; a equipe decidiu fazer sem esperar, porque a decisão 46 pede todos os resultados do artigo e a Seção VI-D traz três acurácias e a Fig. 9. Se o professor pedir outro método depois, ajusta-se. O nome do arquivo ficou como estava, para não quebrar as referências.

## Como ficou (conferido no código e em `results/` em `759ec29`, 08/10/2026)

**Onde este bloco e o resto do arquivo divergirem, vale este bloco.** "Executado" é comando rodado nesta reconciliação; "lido" é arquivo ou histórico aberto, sem rodar. Suíte inteira executada em `759ec29`: 110 testes verdes em 41 s; `ruff check` e `ruff format --check` sem erro.

- **Situação: pronta e executada.** `evaluate` recebe os nomes das classes em `679ed89`; carga por ferramenta em `6624612`; script em `b459e2a`; resultados em `1a0e041`; `d86b0b5` separou o resumo e passou a medir a legenda da Fig. 9 como o artigo; refeito em `38809c1`, com os `metrics.json` dos dois modelos idênticos (só os `run.json` mudaram: é a evidência de G6 dos modelos). Os `run.json` trazem o commit `ff039fa` e `dirty: false` (lido).
- **Arquivos:** `scripts/e7_ferramenta.py` (treina, avalia, mede e grava), `scripts/e7_resumo.py`, `src/doh_ids/data.py` (`load_malicious_by_tool`), `src/doh_ids/evaluate.py` (parâmetro com os nomes das classes), `tests/test_data.py`, `tests/test_evaluate.py`, `tests/test_splits.py`.
- **Comando real:** `uv run python scripts/e7_ferramenta.py` e, depois, `uv run python -m scripts.e7_resumo`. Lê `data/raw/cira/MaliciousDoH-CSVs.zip`, o manifesto e **`results/e6/dados/combinado_sem_replicas/seed42/metrics.json`** (as contagens por ferramenta, com que a carga é conferida): roda depois de `e6_dados.py`. Tempo medido: 28 s na profundidade variável, 11 s na profundidade 5 e 1 s na Fig. 9.
- **Resultados:** `results/e7/variante/ferramenta/seed42/`, `results/e7/fiel/ferramenta/seed42/`, `results/e7/dados/fig9/seed42/` (`fig9_distribuicao.png`, `fig9_curvas.csv`, `fig9_estatisticas.csv`) e `results/e7/RESUMO.md`.
- **Os pontos sem valor declarado foram fechados pela decisão 51 (a, e):** a trilha nomeia a leitura de profundidade e o recorte é `ferramenta`; dns2tcp é a classe dividida em três partes, dnscat2 a reamostrada com SMOTE até igualar iodine; os papéis saem das contagens do treino (`metrics.roles`).
- **Desvios que ficaram:** a Fig. 9 fica na trilha `dados`, recorte `fig9`, porque não treina modelo; o resumo traz as curvas normais com a média e o desvio medidos, como o artigo, e o histograma embaixo; as estatísticas da legenda da Fig. 9 são medidas também nos arquivos sem a limpeza. O resumo chama o método de "leitura nossa".
- **Concluída (08/10/2026).** A conversa com o professor sobre o método (Q5) foi fechada pela equipe, sem resposta dele (decisão 55a): fica o método implementado, e o ponto continua na página dos encontros. Integrada na `main` por avanço direto, sem pull request por tarefa (decisão 55f).

## Reconciliado com as tarefas 06 a 08 e com as decisões 44 a 50 (07/10/2026, commit `360c3d3`)

**Onde este bloco e o resto do arquivo (passos, critérios, riscos) divergirem, vale este bloco.**

- **Método (decisão 49):** o mesmo sistema da tarefa 08 aplicado só aos fluxos maliciosos, com as três ferramentas como classes. É leitura da equipe, porque o artigo não descreve o método, e isso é declarado no resumo e no relatório. As métricas são por ferramenta (precisão, recall, F1), não só acurácia, porque as classes são desbalanceadas.
- **O que o código atual não cobre, conferido em `360c3d3`:**
  - `evaluate` e `metrics_from_confusion` nomeiam as classes por `CLASS_NAMES` (Non-DoH, Benign-DoH, Malicious-DoH) e calculam "Malicious-DoH contra o resto" pelo índice da classe maliciosa. O passo 4, "avaliar com a função da tarefa 06", não funciona como está: as chaves sairiam com os nomes errados e a visão binária não faz sentido entre ferramentas. A função precisa receber os nomes das classes, ou o script precisa de um caminho próprio; as duas saídas tocam `evaluate.py` ou duplicam a conta, e são combinadas com o usuário.
  - `balanced_subsets` fixa o papel de cada código de classe: divide a classe 0 em três partes, repete as classes 1 e 2 e aumenta a classe 1 com SMOTE até o tamanho da 2. **Ponto sem valor declarado:** que ferramenta recebe cada código. Pelas contagens, a leitura que mantém os papéis é dns2tcp (167.486, a maior) como classe dividida, dnscat2 (35.770, a menor) como classe aumentada e iodine (46.580) como classe de referência; o usuário confirma antes de implementar.
  - `load_cira` lê `Total_CSVs.zip` e não lê `MaliciousDoH-CSVs.zip`: a carga por ferramenta é função nova em `data.py`, com o teste T21-1.
- **Ponto sem valor declarado: a leitura de profundidade.** A tarefa 08 mede duas, e a decisão 49 diz "o mesmo sistema da tarefa 08" sem dizer qual; a lista da decisão 45 não cita esta tarefa. O conjunto é pequeno (cerca de 250 mil fluxos, um quarto do treino do CIRA), então rodar as duas é a proposta; o usuário confirma.
- **Ponto sem valor declarado: o caminho em `results/e7/`.** A decisão 38 não lista E7. Pelo padrão de E1, seria `results/e7/fiel/proposto/seed42/` e `results/e7/variante/profundidade_variavel/seed42/`; ver "Pendências abertas pela decisão 45" em `00-README.md`.
- Protocolo, igual ao de E1: mesma regra de limpeza (remover as linhas com NaN), split 90/10 estratificado pela ferramenta com a seed 42, scaler ajustado só no treino, três subconjuntos, três bases, meta. As linhas com `DoH == True` somam 249.836 (167.486 + 35.770 + 46.580), que é o total bruto de Malicious-DoH do CIRA; depois da limpeza o esperado é 249.553, o número da Tabela I, a conferir por asserção no script. Validação cruzada não está prevista aqui: o artigo não mostra matriz para a Seção VI-D.
- **Fig. 9, conferida no manuscrito:** distribuição de (a) `ResponseTimeTimeSkewFromMode` e (b) `PacketTimeVariance` para dns2tcp, dnscat2 e iodine. A figura é gerada por este script, que lê os dados, e gravada em `results/e7/`; a tarefa 17 a leva para `report/figures/`. `ResponseTimeTimeSkewFromMode` é uma das colunas de assimetria com o valor sentinela `-10` (`SKEW_COLUMNS`, `SKEW_SENTINEL`): o resumo diz quanto da distribuição é esse marcador.
- **Custo: não medido.** O conjunto tem cerca de um quarto das linhas do treino do CIRA.
- Execução com dados reais na própria sessão (decisão 44).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **Resposta ao passo 1: o rótulo de ferramenta existe.** Em `data/raw/cira/MaliciousDoH-CSVs.zip` há um `CSVs/<ferramenta>/all.csv` por ferramenta; a coluna é `DoH` (booleana), sem `Label`, e a ferramenta é o nome da pasta. Linhas com `DoH == True`: dns2tcp 167.486, dnscat2 35.770, iodine 46.580. As linhas com `DoH == False` (31, 84, 18) não entram. A alternativa é `combinado/l3-total-add.csv`, que traz as mesmas três ferramentas com o rótulo em `Label`, mas com os números arredondados.
- Em 07/10/2026 (reconciliação no commit `0ae2d49`), `data/raw/cira/MaliciousDoH-CSVs.zip` está no disco e no manifesto, como opcional, com as linhas de cada `CSVs/<ferramenta>/all.csv` (167.517, 35.854 e 46.598, que são as somas de `True` e `False` do item acima). O ⚠️ REVISAR da tarefa 03 foi resolvido. A pasta `CSVs 2/` que sobrou da extração não é fonte: lê-se o zip.
- Em 07/10/2026 (reconciliação no commit `360c3d3`): a tarefa deixou de ser condicional (decisão 49).

## Arquivos

- `scripts/e7_ferramenta.py` — novo.
- `src/doh_ids/data.py` — carga dos fluxos maliciosos por ferramenta, a partir de `MaliciousDoH-CSVs.zip`.
- `tests/test_data.py` — T21-1.
- `results/e7/` — métricas, figura equivalente à Fig. 9 e `RESUMO.md`, gerados.

## O que fazer

1. Confirmar de onde vem o rótulo de ferramenta. Nos CSVs do CIRA ele pode não existir como coluna (conferir no registro da tarefa 03); o dataset combinado tem um arquivo de nível 3 com rótulo por ferramenta (tarefa 13).
2. Montar o conjunto só com fluxos maliciosos e rótulo em {dns2tcp, dnscat2, iodine}.
3. Aplicar o mesmo sistema da tarefa 08, agora com essas três classes. O artigo não descreve o método usado; declarar que "mesmo sistema" é a leitura da equipe.
4. Avaliar com a função da tarefa 06 e comparar o recall por ferramenta com os valores do artigo: 99,2% (dns2tcp), 92,9% (iodine), 91,3% (dnscat2). O artigo chama esses valores de acurácia sem dizer como foram calculados.
5. Reproduzir a Fig. 9: distribuições de `ResponseTimeTimeSkewFromMode` e `PacketTimeVariance` por ferramenta.

## Por quê

A seção VI-D faz parte do artigo, mas é a mais mal especificada (ambiguidade A16). Entra porque o alvo de P1 são todas as tabelas e gráficos de resultado do artigo (decisões 46 e 49), com o método declarado como leitura da equipe.

## Evidência — verificada no baseline

- `docs/02-artigo.md:26` e `:102` — o que o artigo afirma e A16.
- `docs/04-dados.md:103` — `l3-total-add.csv` com rótulo por ferramenta.
- `docs/07-pendencias.md:15` — Q5.
- Manuscrito em `docs/referencias/`, seção VI-D e Fig. 9.

## Risco

- O rótulo de ferramenta está em `MaliciousDoH-CSVs.zip` (ver o bloco acima); o `l3` do combinado é a alternativa, com números arredondados, e seu uso seria declarado.
- Classes desbalanceadas (dns2tcp tem 167 mil fluxos; as outras, 36 mil e 47 mil): métricas por classe, não só acurácia.

## Critério de aceite

- [x] Resposta de Q5 registrada em `docs/07-pendencias.md` antes do início. Lido: resposta de 07/10/2026 e a decisão da equipe de fazer sem esperar (decisão 49).
- [x] Os três pontos sem valor declarado do bloco de reconciliação (papel de cada ferramenta nos subconjuntos, leitura de profundidade, caminho em `results/e7/`) e a forma de avaliar com nomes de classe próprios estão decididos antes da primeira execução. Lido: decisão 51, itens (a) e (e), por recomendação do assistente, que o usuário pode rever; `83df7c1` vem antes de `b459e2a`.
- [x] Conjunto só com fluxos maliciosos e rótulo em {dns2tcp, dnscat2, iodine}; total depois da limpeza conferido por asserção. Lido: `e7_ferramenta.py:178`, contra a contagem de Malicious-DoH da Tabela I; executado: `test_tool_load_keeps_only_doh_rows_with_the_tool_of_the_folder`.
- [x] Métricas por ferramenta (precisão, recall, F1, com o suporte) ao lado dos três valores do artigo, que o artigo chama de acurácia, com a diferença. Lido: `article_comparison` em `metrics.json`, por ferramenta, com `article_accuracy`, `precision`, `recall`, `f1`, `support` e `difference_pp`.
- [x] Figura equivalente à Fig. 9, com eixos rotulados e unidade. **Fechado em 08/10/2026:** `results/e7/dados/fig9/seed42/fig9_distribuicao.png` aberta em `5999c1b`: quatro painéis, eixo x "ResponseTimeTimeSkewFromMode (sem unidade)" e "PacketTimeVariance (s²)", eixo y "Densidade" e "Densidade (1/s²)", legenda por ferramenta com média e desvio.
- [x] `RESUMO.md` declara que o método é leitura da equipe e por quê. Lido: seção "O método é leitura nossa", `results/e7/RESUMO.md:9`.
- [x] Revisor metodológico sem achado bloqueante. **Fechado em 08/10/2026:** `REVISAO-FINAL.md`: nenhum achado bloqueante; V3 a V6. Commits anteriores: `d86b0b5`, `38809c1`.

## Testes

Seção "Tarefa 21" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e7_ferramenta.py` e, depois, `uv run python -m scripts.e7_resumo`.
