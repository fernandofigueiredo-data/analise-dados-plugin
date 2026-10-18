---
name: qualidade-dados
description: >-
  Perfil de qualidade dos dados, feito uma vez logo depois da verificação de
  leitura e antes de limpar ou analisar. Procura dados faltando, linhas
  duplicadas, valores impossíveis (negativos, datas no futuro, preço abaixo do
  custo), categorias escritas de jeitos diferentes, valores fora do comum e
  buracos no tempo — e transforma o que achar em decisões de tratamento
  combinadas com o usuário. Use na etapa de conhecer/limpar os dados, ou de novo
  quando chegar um arquivo novo.
---

# Os dados têm problemas?

A `verificacao-leitura` garante que o arquivo foi **lido** certo. Esta skill
pergunta outra coisa: o que foi lido **faz sentido**? Dado com problema não
avisa — ele só distorce a média, infla a contagem e sustenta uma conclusão
errada lá na frente.

Faça **uma vez**, logo depois da leitura, numa seção própria do notebook:
`## Os dados têm problemas?`. Cada checagem é **uma célula curta** respondendo
uma pergunta (regras do `REGRAS.md`). Antes de começar, leia o `contexto.md`:
ele pode já dizer o que é normal nesses dados.

## As checagens, uma por célula

**1. Falta informação em alguma coluna?** Mostre só as colunas com falta, com o
tamanho do buraco em %:

```python
faltando = df.isna().sum().to_frame("linhas")
faltando["%"] = (faltando["linhas"] / len(df) * 100).round(1)
faltando[faltando["linhas"] > 0]
```

Pouca falta numa coluna secundária é diferente de 30% faltando na coluna que
responde à pergunta de negócio. Diga qual é o caso.

**2. Tem linha repetida?** `int(df.duplicated().sum())` conta linhas idênticas
(o `int` evita a exibição feia `np.int64(0)`). Se existir uma coluna que deveria
ser única (id do pedido, CPF, código), confira também por ela:
`int(df.duplicated(subset=["id_pedido"]).sum())`. Se não souber qual
coluna identifica cada linha, pergunte — e anote no `contexto.md`.

**3. Tem valor impossível?** Escreva as regras de negócio como um dicionário e
conte quantas linhas quebram cada uma. As regras vêm do significado das colunas,
não de um padrão genérico — adapte ao dataset:

```python
regras = {
    "quantidade zero ou negativa": df["quantidade"] <= 0,
    "preço zero ou negativo": df["preco_unitario"] <= 0,
    "vendido abaixo do custo": df["preco_unitario"] < df["custo_unitario"],
    "data no futuro": df["data"] > pd.Timestamp.today(),
}
pd.DataFrame({"linhas": {regra: int(m.sum()) for regra, m in regras.items()}})
```

Outras regras comuns: percentual fora de 0–100, idade negativa ou acima de 120,
data de entrega antes da data do pedido, nota fora da escala. Quebrar uma regra
nem sempre é erro (vender abaixo do custo pode ser liquidação) — na dúvida,
pergunte.

**4. A mesma categoria aparece escrita de jeitos diferentes?** `"Sul"`,
`"sul"` e `"Sul "` viram três regiões no gráfico. Compare o número de valores
antes e depois de padronizar:

```python
texto = df.select_dtypes(include=["object", "string"]).columns
pd.DataFrame({
    "valores": df[texto].nunique(),
    "depois de padronizar": df[texto].apply(lambda s: s.str.strip().str.lower().nunique()),
})
```

Se os números diferirem, mostre o `value_counts()` daquela coluna.

**5. Tem valor fora do comum?** Olhe mínimo e máximo das colunas numéricas
(`df.describe().T[["min", "max"]]`) e pergunte se são plausíveis. Valor extremo
**não é erro por definição** — uma venda gigante pode ser um cliente
corporativo. Erro de digitação (preço `1599000` em vez de `1599.00`) se trata;
caso raro e real se mantém e se menciona.

**6. Tem buraco no tempo?** Se houver data, conte registros por mês:
`df.groupby(df["data"].dt.to_period("M")).size().to_frame("registros")`.
Mês faltando ou com muito menos registros pode ser falha de coleta — e vai
parecer "queda" em qualquer análise de evolução. Anote também o período coberto:
ele define que comparações no tempo são possíveis (skill `revisao-critica`).

## Do achado à decisão

Ao final das checagens, escreva **uma célula markdown** resumindo em tabela:
problema, quantas linhas, quanto representa, e o que você propõe.

```markdown
| Problema | Linhas | % | Proposta |
|---|---|---|---|
| Região em branco | 154 | 3,1% | Manter como "Não informada" |
| Nenhum valor impossível | 0 | — | — |
```

Regras para tratar:

- **Nunca apague nem corrija em silêncio.** Quando a decisão muda o resultado
  (remover linhas, preencher valores, juntar categorias), **pergunte ao
  usuário** antes. Ele conhece o negócio; você só conhece o arquivo.
- **Prefira marcar a apagar.** Dado faltando numa categoria vira "Não
  informada", e entra nas contagens como um grupo visível. Apagar a linha some
  com o problema da vista e enviesa os totais.
- **Aplique o tratamento numa célula que mostra o antes e o depois** (`shape`
  antes → depois, ou o `value_counts()` da coluna corrigida), como manda o
  `REGRAS.md`.
- **Registre cada decisão** em **Decisões de tratamento** no `contexto.md`, com
  data e motivo. É o que permite outra pessoa refazer a análise e chegar no
  mesmo número.
- **Dados sem problema também são um achado.** Diga isso em uma linha e siga.
  Não invente problema para preencher a seção.

Os arquivos em `dados/` nunca são alterados: o tratamento vive no notebook. Se
precisar salvar a versão tratada, grave em `saidas/`.
