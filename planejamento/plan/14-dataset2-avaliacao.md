# 14 · segundo dataset · transferência e retreino (E6)

**Onde:** `scripts/e6_dataset2.py`, `src/doh_ids/evaluate.py`, `tests/test_evaluate.py`, `tests/test_pipeline.py`, `results/e6/fiel/`
**Objetivo:** os resultados do sistema do artigo no segundo dataset, em quatro cenários postos lado a lado: o CIRA da tarefa 08, o modelo treinado no CIRA diante de ferramentas que nunca viu, e o sistema retreinado no dataset combinado como publicado e sem as réplicas do HKD. É a entrega de P2.
**Depende de:** 08, 13
**Demonstra:** `results/e6/fiel/`: recall por ferramenta na transferência e métricas completas nos dois retreinos, com as tabelas de amostras por conjunto. Evidência de P2 (seção 7.2).

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **E6a usa `hkd.parquet` com 5.258 fluxos**, não os 105.160 do arquivo replicado. O recall por ferramenta é o mesmo; o tamanho da amostra reportado é o real. No `Total-48h.csv` não há vetor de 29 atributos repetido nem vetor com dois rótulos (medido em 07/10/2026); o que resta é a quase-duplicata de fluxos da mesma sessão (duas máquinas, mediana de duração colada no tempo limite de 120 s), que o resumo declara.
- **E6b roda duas vezes (decisão 36):** no combinado como publicado, que é o dataset de terceiros tal como distribuído, e no combinado sem réplicas. Resultados em `results/e6/fiel/retreino_publicado/seed42/` e `results/e6/fiel/retreino_sem_replicas/seed42/`. No publicado, cada fluxo do HKD aparece 20 vezes e o split aleatório põe cópias idênticas em treino e teste: o recall das ferramentas novas mede memorização. A versão sem réplicas é a que responde se o sistema detecta as ferramentas novas. As duas vão para a mesma tabela, nomeadas.
- Asserção no script: na versão sem réplicas, nenhum vetor de 29 atributos do HKD aparece em treino e teste ao mesmo tempo. É satisfazível, pelo primeiro item.
- Hipótese a escrever antes de rodar E6a, em `results/e6/fiel/HIPOTESE.md`: os fluxos do HKD têm duração mediana de 120 s e bytes cerca de dez vezes maiores que os maliciosos do CIRA, então parte dos valores normalizados cairá fora de [0, 1].
- Com seed 42 e split 90/10, o teste do combinado sem réplicas tem cerca de 526 fluxos do HKD, perto de 150 por ferramenta. O recall por ferramenta vem com `n` e intervalo de confiança binomial exato, e o resumo declara que é uma estimativa de uma seed. As dez seeds do modelo A no combinado sem réplicas ficam na tarefa 15; se P3 for cortado, essa limitação fica escrita na seção 8 do relatório.

## Arquivos

- `scripts/e6_dataset2.py` — novo.
- `src/doh_ids/evaluate.py` — acrescentar: recall por ferramenta, contagem de valores fora de [0, 1] por atributo e a avaliação do recorte só de maliciosos (sem precisão, FPR nem acurácia).
- `tests/test_evaluate.py` (T14-1 a T14-3) e `tests/test_pipeline.py` (T14-4) — acrescentar.
- `results/e6/fiel/HIPOTESE.md` — escrita antes de rodar, em commit anterior à primeira execução.
- `results/e6/fiel/transferencia/seed42/`, `results/e6/fiel/retreino_publicado/seed42/`, `results/e6/fiel/retreino_sem_replicas/seed42/` e `results/e6/fiel/RESUMO.md` — gerados.

## O que fazer

1. Rodar a skill `experimento` para E6, trilha fiel. Escrever `HIPOTESE.md` antes da primeira execução.
2. **E6a, transferência.** Treinar o sistema da tarefa 08 no CIRA (seed 42). Normalizar os fluxos do HKD com o scaler ajustado no treino do CIRA e prever.
   - Métrica: recall de Malicious-DoH, total e por ferramenta (dnstt, tcp-over-dns, tuns), com `n` e intervalo de confiança binomial exato, e para que classe vão os erros.
   - Contar quantos valores normalizados caem fora de [0, 1], por atributo. Comparar com a contagem da tarefa 05.
   - Não há negativos neste recorte: não calcular precisão, FPR nem acurácia geral, e dizer isso no resultado.
   - Gravar a tabela de contagem do HKD por ferramenta. Neste cenário tudo é teste: não há treino nem validação, e a seção 6 do relatório diz isso com essas palavras.
3. **E6b, retreino.** Pipeline completo da tarefa 08 sobre o combinado, duas vezes (publicado e sem réplicas): split 90/10 estratificado pelas três classes, scaler ajustado no novo treino, três subconjuntos, três bases, meta. Mesma função de avaliação. A validação cruzada de 10 folds da tarefa 08 não é repetida aqui; a tabela de tamanho por classe de cada fold é gerada só com os índices, sem treinar, para a seção 6 responder "treino, validação e teste" também para o segundo dataset.
   - Reportar o recall de Malicious-DoH por ferramenta no teste, usando a coluna `tool`, com `n` e intervalo de confiança.
   - Gerar, para cada retreino, a tabela de amostras por classe em treino, por fold de validação e no teste, que a seção 6 do relatório exige.
   - Na versão sem réplicas, asserção de que nenhum vetor do HKD está em treino e teste ao mesmo tempo.
4. Colocar lado a lado os quatro cenários: CIRA (tarefa 08), transferência, retreino publicado e retreino sem réplicas.
5. Interpretar em `RESUMO.md`, com apoio das distribuições da tarefa 13: se a transferência cair, quais atributos mudaram de faixa; o que a diferença entre os dois retreinos diz sobre memorização.
6. Esta tarefa fica na trilha fiel, seed 42. As dez seeds no combinado sem réplicas são feitas na tarefa 15, com a seleção de hiperparâmetros refeita dentro do treino do combinado.

## Por quê

Objetivo P2 da especificação. O artigo avalia só com as três ferramentas presentes no treino; a transferência mede o que ele não mede. O retreino cumpre a letra do requisito, com as três classes, e a versão sem réplicas evita que o resultado seja memorização.

## Evidência — verificada no baseline

- `docs/referencias/CIN0114 - 2026.2 - Especificação do seminário e do projeto.md:29` — "obter resultados do sistema proposto no artigo reproduzido em outro conjunto de dados".
- `docs/05-plano-experimental.md:97-104` — desenho de E6a e E6b.
- `docs/04-dados.md:115` — por que os dois cenários.
- Mesma especificação, `:98-103` — a seção 7 pede os resultados do sistema do artigo nos dois conjuntos.
- Mesma especificação, `:93-94` — a seção 6 pede, para o outro dataset, como treino, validação e teste foram formados e quantas amostras há por classe em cada um.

## Risco

- Recall de transferência muito baixo é resultado, não falha. Reportar como está; é a evidência mais forte para a seção de limitações.
- Ajustar o scaler com o HKD em E6a seria vazamento e mudaria a pergunta: asserção de que o scaler usado é o do CIRA.
- No retreino, dois terços das classes são as mesmas linhas do CIRA; métricas gerais parecidas com as da tarefa 08 são esperadas e não provam generalização. A leitura útil é o recall por ferramenta.
- Com uma seed, o recall por ferramenta no retreino sem réplicas tem intervalo largo: reportar `n` e intervalo, não só a taxa.

## Critério de aceite

- [ ] `results/e6/fiel/transferencia/seed42/metrics.json` com recall por ferramenta (`n` e intervalo), destino dos erros, contagem de valores fora de faixa e a tabela do HKD por ferramenta.
- [ ] `results/e6/fiel/retreino_publicado/seed42/metrics.json` e `results/e6/fiel/retreino_sem_replicas/seed42/metrics.json` com as métricas completas, o recall por ferramenta e a tabela de amostras por classe em treino, por fold de validação e no teste.
- [ ] Nenhuma precisão ou FPR reportada para o recorte só de maliciosos.
- [ ] Asserção da versão sem réplicas verde, com a saída colada no pull request.
- [ ] Tabela comparativa dos quatro cenários gerada por script.
- [ ] `HIPOTESE.md` em commit anterior à primeira execução; interpretação em `RESUMO.md`, com uma linha por número principal.
- [ ] Revisor metodológico sem achado bloqueante.

## Testes

Seção "Tarefa 14" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo: G1–G10, com G5 = `uv run python scripts/e6_dataset2.py`.
