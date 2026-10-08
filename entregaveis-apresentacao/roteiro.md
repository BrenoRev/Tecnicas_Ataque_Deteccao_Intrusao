# Roteiro da apresentação

Gerado por `scripts/make_slides.py`, com os mesmos textos das anotações dos slides. Não edite à mão: mude o script e rode de novo.

Tempo disponível: 15 minutos. Soma dos tempos: 11 min 55 s.

Apresentam três integrantes, em blocos contíguos de slides (a divisão dos blocos é proposta; a equipe pode trocar o ponto de corte).

- Amanda: slides 1 a 5 (4 min 00 s)
- Antonio: slides 6 a 10 (4 min 30 s)
- João: slides 11 a 14 (3 min 25 s)

## 1. Título e equipe (0:30)

- Apresentar a equipe e o artigo reproduzido.

## 2. O artigo em um slide (0:55)

- A turma já viu o seminário: só o necessário para entender o que reproduzimos.
- Artigo: Zebin, Rezvy e Luo, IEEE TIFS, 2022. Conjunto de dados CIRA-CIC-DoHBrw-2020.
- Os valores acima de 99,9% são os do resumo do artigo.

## 3. O que construímos (0:55)

- Nada foi ajustado para aproximar número do artigo: seed, hiperparâmetro e limpeza ficaram fixos.
- As duas leituras de profundidade têm apoio no texto; reportamos as duas.
- Os experimentos seguintes usam a leitura de profundidade variável como base, porque a outra não prediz uma das classes.
- Protocolo corrigido: dez seeds em vez de uma, comparação pareada no mesmo split, teste sem vetores repetidos e folds por máquina.
- Um script por experimento; resultado gravado com seed, versões e commit.

## 4. Dados e protocolo (0:45)

- Não há conjunto de validação separado, como no artigo: a validação é cruzada.
- O combinado publicado repete 20 vezes cada fluxo do HKD; usamos a forma sem réplicas, para o teste não conter cópias do treino.
- O HKD sozinho só tem tráfego malicioso: serve de teste na transferência.

## 5. Reprodução: as duas leituras ao lado da Fig. 4b (0:55)

- Linha é a classe real, coluna a predita; entre parênteses, a diferença para o artigo.
- Com profundidade 5, os 1975 fluxos Benign-DoH do teste vão para Non-DoH.
- Com profundidade variável: F1 macro de 96,56%, contra 97,82% calculado da Fig. 4b.
- Não afirmamos que a profundidade variável é a dos autores: são duas leituras com apoio no texto.

## 6. Por que a profundidade 5 perde uma classe (0:50)

- Os bases de profundidade 5 têm precisão de Benign-DoH perto de 30%: marcam muito Non-DoH como Benign-DoH.
- A combinação em que os três dizem Benign-DoH ocorre em 49247 fluxos do treino; 31025 são Non-DoH. O meta-classificador devolve Non-DoH.
- Por isso as métricas por classe vêm antes das médias, e a média é a macro.

## 7. Tabela II e ferramenta de túnel (0:50)

- A coluna do artigo é a da Tabela II; a da reprodução usa a média macro.
- O artigo não diz que média usa; nenhuma média reproduz a linha do modelo proposto.
- A legenda da Fig. 9 só é reproduzida com os arquivos sem a limpeza: é indício, não prova, de que essa seção usou outros dados.

## 8. Explicabilidade com SHAP (0:55)

- Uma regra com um só atributo teria recall de 99,84% e 1 falso positivo em 909555 fluxos legítimos (Non-DoH e Benign-DoH): o modelo pode separar pela captura.
- Acima de 40 s, têm SHAP positivo 97,37% dos fluxos com profundidade variável e 99,53% com profundidade 5.
- Não dizemos que o limiar de 40 s foi refutado: a amostra tem classes em partes iguais e o artigo lê o valor a olho.
- O painel interativo foi implementado e pode ser mostrado ao final.

## 9. Protocolo corrigido: 10 seeds (0:50)

- Um ponto por seed; o traço é a média.
- O que muda em relação à reprodução: dez seeds em vez de uma e comparação pareada no mesmo split; o SMOTE já era ajustado só no treino.
- Com profundidade 5, o recall de Benign-DoH é zero nas dez seeds.
- A separação entre Non-DoH e Benign-DoH aprendida em três máquinas não vale na quarta.
- Nenhuma máquina gerou tráfego legítimo e malicioso: nenhum split separa a captura do ataque.

## 10. Segundo conjunto de dados: ferramentas novas (1:05)

- É o achado principal. É compatível com um detector que aprendeu a assinatura das ferramentas e da captura do CIRA, e não o comportamento de túnel.
- Ferramenta e captura não se separam: o HKD traz outras ferramentas e outra captura.
- Os 99,42% são 510 de 513 fluxos, e medem as mesmas ferramentas, não uma nunca vista.
- Non-DoH e Benign-DoH do combinado são os do CIRA: métricas gerais iguais são esperadas.

## 11. Modificação: Random Forest único com peso de classe (1:25)

- A hipótese foi registrada antes da execução: sem amostras sintéticas e sem empilhamento, F1 macro maior por menos de 1 ponto, sem ganho esperado no recall de Benign-DoH.
- A é o sistema do artigo com profundidade variável; 10 seeds, média e desvio, em %. Prec. Benign é a precisão de Benign-DoH.
- A seleção escolheu a mesma combinação nas dez seeds, nos dois conjuntos: 100 árvores, sem limite de profundidade, raiz quadrada dos atributos por divisão.
- M1 perde 0,50 ponto de recall de Benign-DoH e o FPR de Malicious-DoH vai de 0,0015% para 0,0048%.
- Com profundidade 5, o modelo único recupera o recall de Benign-DoH (87,64%), mas com precisão de 26,23% e F1 macro de 78,66%.
- Tempo: 1,6 vez no CIRA e 2,3 vezes no combinado; o tempo de A no CIRA foi medido sob outra carga e, reajustado, é 112,5 s (2,3 vezes).
- Não dizemos que a modificação reduz falsos positivos: no CIRA é cerca de um fluxo por teste, e não se repete no combinado.
- Os testes das seeds se sobrepõem: não usamos a palavra significativo.

## 12. Robustez: fragmentação simulada do fluxo (0:50)

- A e A-prof5 são o sistema do artigo com profundidade variável e com profundidade 5; M1M2 é a modificação.
- O artigo publica que a duração pesa na decisão: é o que o atacante usaria.
- Nenhum tráfego foi gerado: é perturbação simulada, sem retreino.
- Nos fatores 8 e 16, mais de 96% dos vetores são fisicamente incoerentes.
- Não dizemos quanto um atacante real evadiria.

## 13. Limitações e conclusão (1:00)

- A modificação melhora o F1 macro em meio ponto e não resolve a detecção das ferramentas do HKD; sob fragmentação, seu recall cai em algumas seeds.
- O segundo conjunto de dados compartilha duas classes com o primeiro.
- Próximo passo: gerar tráfego fragmentado e testar uma ferramenta deixada de fora.
- Relatório, código e resultados estão no repositório.

## 14. Encerramento (0:10)

- Abrir para perguntas.
