# Roteiro da apresentação

Gerado por `scripts/make_slides.py`, com os mesmos textos das anotações dos slides. Não edite à mão: mude o script e rode de novo.

Tempo disponível: 15 minutos. Soma dos tempos: 11 min 50 s.

Quem fala em cada slide: [Preencher: divisão da fala entre os quatro integrantes].

## 1. Título e equipe (0:30)

- Apresentar a equipe e o artigo reproduzido.

## 2. O artigo em um slide (0:55)

- A turma já viu o seminário: só o necessário para entender o que reproduzimos.
- Artigo: Zebin, Rezvy e Luo, IEEE TIFS, 2022. Dataset CIRA-CIC-DoHBrw-2020.
- Os valores acima de 99,9% são os do resumo do artigo.

## 3. O que construímos (0:55)

- Nada foi ajustado para aproximar número do artigo: seed, hiperparâmetro e limpeza ficaram fixos.
- As duas leituras de profundidade têm apoio no texto; reportamos as duas.
- As etapas seguintes usam a leitura de profundidade variável como base, porque a outra não prediz uma das classes.

## 4. Dados e protocolo (0:45)

- Não há conjunto de validação separado, como no artigo: a validação é cruzada.
- O combinado publicado repete 20 vezes cada fluxo do HKD; usamos a forma sem réplicas, para o teste não conter cópias do treino.
- O HKD sozinho só tem tráfego malicioso: serve de teste na transferência.

## 5. Reprodução: as duas leituras ao lado da Fig. 4b (1:05)

- Linha é a classe real, coluna a predita; entre parênteses, a diferença para o artigo.
- Trilha fiel é a profundidade 5; trilha variante, a profundidade variável.
- Com profundidade 5, os 1975 fluxos Benign-DoH do teste vão para Non-DoH.
- Com profundidade variável: F1 macro de 96,56%, contra 97,82% calculado da Fig. 4b.
- Não afirmamos que a profundidade variável é a dos autores: são duas leituras com apoio no texto.

## 6. Por que a profundidade 5 perde uma classe (0:55)

- Os bases de profundidade 5 têm precisão de Benign-DoH perto de 30%: marcam muito Non-DoH como Benign-DoH.
- A combinação em que os três dizem Benign-DoH ocorre em 49247 linhas do treino; 31025 são Non-DoH. O meta-classificador devolve Non-DoH.
- Por isso as métricas por classe vêm antes das médias, e a média é a macro.

## 7. Tabela II e ferramenta de túnel (0:55)

- Art. é o valor do artigo; Rep. e Macro são a reprodução, com média macro.
- O artigo não diz que média usa; nenhuma média reproduz a linha do modelo proposto.
- A legenda da Fig. 9 só é reproduzida com os arquivos sem a limpeza: é indício, não prova, de que essa seção usou outros dados.

## 8. Explicabilidade com SHAP (0:55)

- Uma regra com um só atributo teria recall de 99,84% e 1 falso positivo em 909555 fluxos legítimos: o modelo pode separar pela captura.
- Não dizemos que o limiar de 40 s foi refutado: a amostra tem classes em partes iguais e o artigo lê o valor a olho.
- O painel interativo foi implementado e pode ser mostrado ao final.

## 9. Protocolo corrigido: 10 seeds (0:50)

- Um ponto por seed; o traço é a média.
- Com profundidade 5, o recall de Benign-DoH é zero nas dez seeds.
- A separação entre Non-DoH e Benign-DoH aprendida em três máquinas não vale na quarta.
- Nenhuma máquina gerou tráfego legítimo e malicioso: nenhum split separa a captura do ataque.

## 10. Segundo dataset: ferramentas novas (1:05)

- É o achado principal. É compatível com um detector que aprendeu a assinatura das ferramentas e da captura do CIRA, e não o comportamento de túnel.
- Os 99,42% são 510 de 513 fluxos, e medem as mesmas ferramentas, não uma nunca vista.
- Non-DoH e Benign-DoH do combinado são os do CIRA: métricas gerais iguais são esperadas.

## 11. Modificação: Random Forest único com peso de classe (1:00)

- A é o sistema do artigo com profundidade variável; 10 seeds, média e desvio.
- M1 perde 0,50 ponto de recall de Benign-DoH em relação a A.
- Não dizemos que a modificação reduz falsos positivos: no CIRA é cerca de um fluxo por teste, e não se repete no combinado.
- Os testes das seeds se sobrepõem: não usamos a palavra significativo.

## 12. Robustez: fragmentação simulada do fluxo (0:50)

- Nenhum tráfego foi gerado: é perturbação simulada, sem retreino.
- Nos fatores 8 e 16, mais de 96% dos vetores são fisicamente incoerentes.
- Não dizemos quanto um atacante real evadiria.

## 13. Limitações e conclusão (1:00)

- A modificação melhora o F1 macro em meio ponto e não resolve a generalização.
- O segundo dataset compartilha duas classes com o primeiro.
- Relatório, código e resultados estão no repositório.

## 14. Encerramento (0:10)

- Abrir para perguntas.
