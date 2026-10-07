# Regras de código

Valem para tudo em `project/`: `src/`, `scripts/`, `tests/` e `data/*.py`. Os caminhos abaixo são relativos a `project/`, que é o repositório Git. O objetivo é um código pequeno, direto, que qualquer integrante explica linha a linha na arguição.

## Simplicidade

- Escreva a solução mais simples que cumpre o critério de aceite da tarefa. Nada além dele.
- Função antes de classe. Classe só quando existe estado que precisa viver entre chamadas.
- Um script por experimento. Dois scripts parecidos são aceitáveis; só extraia para `src/` o que três chamadores usam de fato ou o que um teste do plano de testes precisa importar. Scripts e `data/verify.py` têm `main()` sob `if __name__ == "__main__":` e são importáveis pelos testes (`pythonpath = ["."]` no pytest).
- Parâmetro novo só quando já existe um segundo valor em uso. Sem opção "para o futuro".
- Proibido: classe base abstrata, registro de plugins, fábrica, decorador próprio, arquivo de configuração YAML, CLI com subcomandos, camada de cache, logging configurável. `config.py` com constantes e `print` nos scripts bastam.
- Dependência nova só com justificativa na tarefa. O que está no `pyproject.toml` é o conjunto fechado.
- Sem código morto, sem trecho comentado, sem função sem chamador.
- Se a função passou de cerca de 40 linhas ou de complexidade 10 (o lint barra), ela faz mais de uma coisa: divida.

## Nomes e forma

- Identificadores em inglês. Docstrings e comentários em português.
- Nome diz o que a coisa é no domínio: `balanced_subsets`, `fit_scaler`, `malicious_fpr`. Sem `utils`, `helpers`, `manager`, `process_data`.
- `X` e `y` só para matriz de atributos e rótulos, como na convenção do scikit-learn.
- Tipos anotados em toda função pública de `src/`.
- Caminhos relativos à raiz do repositório, montados com `pathlib`. Nenhum caminho de máquina.
- Nenhum número solto: hiperparâmetro, seed, fração e limiar moram em `config.py`.

## Docstring

Toda função pública de `src/` e todo script têm docstring. Ela descreve o contrato, não a implementação:

```python
def balanced_subsets(X_train, y_train, seed):
    """Monta os três subconjuntos de treino do artigo.

    Divide o Non-DoH em três partes disjuntas, repete todos os maliciosos e
    benignos em cada uma e iguala os benignos aos maliciosos com SMOTE.

    Devolve a lista de três pares (X, y) e o resumo de contagens por classe.
    """
```

Uma linha basta quando o nome já diz tudo. Não liste parâmetro cujo nome e tipo são óbvios.

## Comentário

Comentário só entra em dois casos:

1. **Regra do domínio ou do artigo** que o código sozinho não revela.
2. **Decisão** tomada onde havia mais de um caminho, com o motivo.

Comentário é prosa: `# 10 árvores, Seção IV-A do artigo` passa no lint; `# n_estimators=10 (IV-A)` não, porque a regra `ERA` barra comentário que pareça código.

```python
# Bom: decisão e motivo, com a fonte que qualquer leitor pode abrir
# O artigo não diz com que dados o meta-classificador é treinado (Seção IV-B).
# Usamos o treino original normalizado, como indica a linha 5 do Algoritmo 1.

# Bom: regra que evita erro silencioso
# O scaler é ajustado só no treino; ajustado no conjunto todo, vaza o mínimo
# e o máximo do teste.

# Ruim: repete a linha
# normaliza os dados

# Ruim: aponta para arquivo interno de planejamento
# A8, decisão 09; ver docs/02-artigo.md:94 e planejamento/plan/08
```

O que **não** entra em comentário nem em docstring:

- caminho de arquivo de `docs/`, `planejamento/` ou `.claude/`;
- número de tarefa, número de decisão, identificador de ambiguidade (A1 a A18), identificador de pergunta (Q1 a Q11);
- histórico ("antes era assim", "corrigido em"), nome de quem fez, data;
- explicação do que a biblioteca faz.

Esses arquivos ficam fora de `project/` e são documentação de trabalho, que muda: a referência envelhece e `project/` precisa ser legível sozinho. A fonte que pode ser citada é a pública: seção, tabela, figura ou algoritmo do artigo, e a documentação da biblioteca. O rastro entre ambiguidade e código fica na documentação de planejamento, não no código. O mesmo vale para o README, para `data/README.md` e para os arquivos de `results/`.

## Erros e validação

- Valide na borda: ao ler arquivo, ao receber argumento de script. Dentro do pacote, confie no contrato.
- `assert` para invariante que nunca pode falhar (29 colunas, nenhum identificador, teste intocado). `raise ValueError` com mensagem clara para entrada inválida do usuário.
- Sem `try/except` genérico. Capture a exceção específica e só quando há o que fazer com ela.

## Reprodutibilidade e vazamento

Estas regras não são negociáveis por simplicidade:

- Toda fonte de sorteio recebe seed explícita vinda de `config.py`.
- O teste é separado primeiro e só é lido na avaliação final. Nenhum `fit` enxerga o teste.
- Scaler e reamostragem são ajustados só com o treino.
- A matriz de atributos é montada por nome das 29 colunas, nunca por "tudo menos o rótulo".
- Todo resultado passa pela função de registro, com trilha, seed, versões, hash dos dados e commit.
- `metrics.json` só tem valor determinístico. Tempo e data vão para o `run.json`.
- Nenhum ajuste de seed, hiperparâmetro ou limpeza para o número "bater" com o artigo.
