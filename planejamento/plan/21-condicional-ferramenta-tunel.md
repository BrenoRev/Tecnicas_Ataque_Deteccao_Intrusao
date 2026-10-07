# 21 · condicional · subclassificação por ferramenta de túnel (E7)

**Onde:** `scripts/e7_ferramenta.py`, `results/e7/`
**Objetivo:** reproduzir a identificação da ferramenta de túnel (seção VI-D do artigo), se e somente se o professor considerar isso parte da reprodução.
**Depende de:** 08, 13 — e da resposta a Q5
**Demonstra:** se feita, recall por ferramenta ao lado dos valores da seção VI-D do artigo; se não, a frase de fora de escopo.

> **Tarefa condicional.** Não começa sem a resposta do professor a Q5 (decisão 20). Sem exigência, fica registrada como fora de escopo no relatório, com o motivo: o artigo dá três acurácias e nenhum método.

## Verificado nos dados (07/10/2026)

Medido nos arquivos de `project/data/raw/`; detalhe em `docs/08-inventario-dados.md`. **Onde este bloco e o resto do arquivo (passos, arquivos, critérios, riscos, evidência) divergirem, vale este bloco.**

- **Resposta ao passo 1: o rótulo de ferramenta existe.** Em `data/raw/cira/MaliciousDoH-CSVs.zip` há um `CSVs/<ferramenta>/all.csv` por ferramenta; a coluna é `DoH` (booleana), sem `Label`, e a ferramenta é o nome da pasta. Linhas com `DoH == True`: dns2tcp 167.486, dnscat2 35.770, iodine 46.580. As linhas com `DoH == False` (31, 84, 18) não entram. A alternativa é `combinado/l3-total-add.csv`, que traz as mesmas três ferramentas com o rótulo em `Label`, mas com os números arredondados.
- Em 07/10/2026 (reconciliação no commit `5e11d56`), o disco tem esse zip extraído como `data/raw/cira/CSVs 2/<ferramenta>/all.csv`; `CSVs 2` é nome gerado pela extração. O zip da equipe traz o `.zip`. Ver o ⚠️ REVISAR no topo da [tarefa 03](03-dados-aquisicao-cira.md) antes de fixar o caminho.
- A tarefa continua condicional à resposta do professor.

## Arquivos

- `scripts/e7_ferramenta.py` — novo.
- `results/e7/fiel/` — gerado.

## O que fazer

1. Confirmar de onde vem o rótulo de ferramenta. Nos CSVs do CIRA ele pode não existir como coluna (conferir no registro da tarefa 03); o dataset combinado tem um arquivo de nível 3 com rótulo por ferramenta (tarefa 13).
2. Montar o conjunto só com fluxos maliciosos e rótulo em {dns2tcp, dnscat2, iodine}.
3. Aplicar o mesmo sistema da tarefa 08, agora com essas três classes. O artigo não descreve o método usado; declarar que "mesmo sistema" é a leitura da equipe.
4. Avaliar com a função da tarefa 06 e comparar o recall por ferramenta com os valores do artigo: 99,2% (dns2tcp), 92,9% (iodine), 91,3% (dnscat2). O artigo chama esses valores de acurácia sem dizer como foram calculados.
5. Reproduzir a Fig. 9: distribuições de `ResponseTimeTimeSkewFromMode` e `PacketTimeVariance` por ferramenta.

## Por quê

A seção VI-D faz parte do artigo, mas é a mais mal especificada (ambiguidade A16). Entra só se o professor pedir, para não gastar prazo com algo que não será cobrado.

## Evidência — verificada no baseline

- `docs/02-artigo.md:26` e `:102` — o que o artigo afirma e A16.
- `docs/04-dados.md:103` — `l3-total-add.csv` com rótulo por ferramenta.
- `docs/07-pendencias.md:15` — Q5.
- Manuscrito em `docs/referencias/`, seção VI-D e Fig. 9.

## Risco

- O rótulo de ferramenta está em `MaliciousDoH-CSVs.zip` (ver o bloco acima); o `l3` do combinado é a alternativa, com números arredondados, e seu uso seria declarado.
- Classes desbalanceadas (dns2tcp tem 167 mil fluxos; as outras, 36 mil e 47 mil): métricas por classe, não só acurácia.

## Critério de aceite

- [ ] Resposta de Q5 registrada em `docs/07-pendencias.md` antes do início.
- [ ] Se feita: métricas por ferramenta ao lado dos valores do artigo, com a leitura adotada declarada.
- [ ] Se não feita: frase de fora de escopo pronta para a seção de limitações do relatório.

## Testes

Seção "Tarefa 21" de [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md): os testes listados ali são escritos junto com o código e precisam estar verdes antes da tarefa seguinte.

## Verificação ao concluir

Gate de experimento completo, se executada: G1–G10, com G5 = `uv run python scripts/e7_ferramenta.py`.
