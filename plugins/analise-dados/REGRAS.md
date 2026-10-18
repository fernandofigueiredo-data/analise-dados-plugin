# Regras para trabalho com Jupyter Notebooks

> Estas são as **regras de casa** do plugin `analise-dados` — valem em toda
> sessão de análise. O *método* da análise (como conduzir, em que ordem, como
> interpretar) está na skill `analista-senior`.

## Ferramentas

- Use o **Jupyter MCP** do plugin para todas as operações em `.ipynb` — ler, editar, inserir, deletar, executar.
- Não use a tool `NotebookEdit` built-in: ela serializa o source como uma string JSON única, o que quebra a formatação padrão do Jupyter e gera diffs ilegíveis no git.
- Um hook do plugin confere cada célula que você escreve pelo Jupyter MCP (tamanho do código, `$` sem escape no markdown). Quando ele apontar um problema, corrija a célula na hora — a célula já foi gravada.

## Concisão é lei

IAs tendem a gerar células enormes, cheias de comentários óbvios e lógica empilhada. Não faça isso.

- **Cada célula responde UMA pergunta.** Se não dá pra dizer em uma frase o que a célula faz, ela é grande demais. Quebre.
- **Células curtas** (~5-8 linhas). A maioria das células de análise tem 1-3 linhas; plots ficam em torno de 5. Passar de 10 linhas é sinal de que a célula mistura preparação com visualização — separe.
- **Sem comentários que repetem o código.** `# Calculando a média` em cima de `df["x"].mean()` é ruído. Use células markdown para raciocínio, não comentários inline.
- **Outputs inspecionáveis, não dumps.** Prefira `.head()`, `.shape`, `.describe()`, `.value_counts()`. Nunca imprima DataFrames inteiros — enche a janela de contexto e não ajuda ninguém.
- **Series → DataFrame na hora de exibir.** A exibição padrão de uma `Series` do pandas é feia e desalinhada. Se o output da célula for uma Series (ex: `value_counts()`, `describe()`, um `groupby(...).mean()`), envolva para exibir: `serie.to_frame()` ou `pd.DataFrame(serie)`.
- **Mostrou transformou, verifique.** Toda célula que modifica o DataFrame (cria/altera colunas, converte tipos, filtra) deve terminar exibindo uma amostra das colunas afetadas, para conferir visualmente que a transformação fez o que devia. Ex:

```python
df["data"] = pd.to_datetime(df["data_inversa"], format="%Y-%m-%d")
df["hora"] = pd.to_datetime(df["horario"], format="%H:%M:%S").dt.hour
df[["data", "hora"]].head()
```

Exceções legítimas para código mais longo: lógica realmente customizada de múltiplos passos, ou uma função que será reaplicada com `.apply()`. São exceções, não a regra.

## Linguagem — zero jargão de data science

O notebook será lido por pessoas de negócio, não por estatísticos. Escreva como se explicasse pra alguém que entende o problema mas não sabe o que é "análise bivariada".

**Símbolos especiais em células markdown.** O Jupyter renderiza o markdown, então `$`, `*`, `_` e `~` viram formatação (fórmula, itálico, riscado) e quebram o texto — `R$ 8.497` é o caso mais comum.

- **Jeito à prova de falha:** envolva o valor/símbolo em código inline com crase — `` `R$ 8.497` ``, `` `a*b` ``. Dentro de crase nada é interpretado, e não precisa contar barras.
- **Se precisar do símbolo em prosa corrida:** escape com **barra dupla** — `\\$`, `\\*`, `\\~` (e não barra simples). O texto da célula passa por uma camada JSON antes de virar markdown; `\$` sozinho é consumido nessa etapa e sobra um `$` sem escape. `\\$` no JSON vira `\$` no markdown, que renderiza como `$` literal.

(Para formatar valores em reais no código, veja o helper na skill `analista-senior`.)

## Execução

- **Sempre execute** as células para verificar que funcionam. Não assuma que o código está correto.
- Se uma célula der erro, **leia o traceback real** antes de corrigir. Não chute.
- Para instalar pacotes, use `%pip install` dentro do notebook (não `!pip install`), pra garantir que instala no kernel certo. O ambiente base vem do plugin e é atualizado junto com ele; o que você instalar com `%pip` fica só neste projeto.
- Já vêm no ambiente: Excel e Parquet (`openpyxl`, `pyarrow`), gráficos interativos (`plotly`), SQL em arquivos locais (`duckdb`) e a biblioteca do plugin (`analise_dados`: `painel` e `banco`). Drivers de banco entram sozinhos quando o projeto tem `DB_URL` no `.env` (comando `/banco`).
- Quando o notebook ficar inconsistente, faça **"Restart & Run All"**: um notebook que só roda de cima a baixo depois disso é o único notebook que de fato funciona. O `/validar` faz isso num kernel novo, sem tocar no notebook ao vivo, e aponta desvios destas regras. Rode-o sempre antes de dar a análise por terminada.
- A linha `#| relatorio: mostrar` / `#| relatorio: ocultar` numa célula de código é uma marcação para o `/relatorio`, não um comentário — é a exceção à regra de não comentar.

## Segurança e dados

- Nunca imprima secrets, API keys, tokens ou senhas no output de células.
- O `.env` do projeto guarda a `DB_URL` (com senha). Nunca leia, mostre ou edite esse arquivo — quem preenche é o usuário. Para conectar, use `analise_dados.banco`, que lê o `.env` sozinho.
- O `contexto.md` (raiz) é a memória do projeto: objetivo, público, dicionário de colunas, decisões de tratamento. Leia no início de toda sessão de análise e mantenha atualizado (skill `analista-senior`).
- Não modifique nem delete os arquivos de dados brutos em `dados/`. Grave tudo o que for derivado (CSVs tratados, figuras exportadas, relatórios) em `saidas/`.

## Imports

Só importe o que for usar. Bloco padrão no topo:

```python
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)  # mostra todas as colunas, sem cortar com "..."
```

Esse `set_option` é importante: por padrão o pandas corta colunas no meio com `...`, o que impede inspecionar visualmente uma tabela larga (ex: depois do `.head()` na validação dos dados). Com `display.max_columns = None`, todas as colunas aparecem.

Não inclua numpy, seaborn, scipy, sklearn etc. no import inicial se não forem necessários. Importe na célula que precisar, quando precisar.
