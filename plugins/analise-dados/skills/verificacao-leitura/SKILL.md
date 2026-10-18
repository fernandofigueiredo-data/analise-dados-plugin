---
name: verificacao-leitura
description: >-
  Checagem única, feita logo depois de carregar um arquivo de dados, para
  confirmar que ele foi lido corretamente — antes de qualquer análise. Use uma
  vez, na etapa de carregar/conhecer os dados. Verifica encoding, separador,
  separador decimal, tipos e se os rótulos saíram legíveis.
---

# Os dados foram lidos corretamente?

Faça esta checagem **uma vez**, logo após o `read_csv`/`read_excel`, antes de
analisar qualquer coisa. Dado lido errado contamina tudo o que vem depois — e
rótulo com acento quebrado estraga todos os gráficos.

Há muitos motivos para uma leitura sair errada; não existe um padrão único.
Olhe para os sinais e ajuste os parâmetros do `read_*` até ficar limpo. Os
sintomas mais comuns:

- **Rótulos com caracteres estranhos** (`?`, `Ã`, caixas) → encoding errado.
  Teste outro: `utf-8`, `latin-1`, `cp1252`.
- **Tudo numa coluna só** → separador errado (`,` vs `;` vs tab). Ajuste `sep`.
- **Número virou texto ou NaN** → separador decimal/de milhar incompatível.
  Ajuste `decimal` (e `thousands` se houver separador de milhar).
- **Linhas estranhas no topo** (título, metadados antes do cabeçalho) → use
  `skiprows`.
- **Colunas a mais ou vazias no fim** → separador sobrando no fim das linhas,
  ou rodapé → veja `skipfooter`.
- **Datas como texto** → não é erro de leitura, mas anote para converter depois.

Confirme sempre olhando: `df.shape` (número de linhas/colunas bate com o
esperado?), `df.dtypes` (os números são numéricos?) e um `df.head()` para ver se
os rótulos categóricos saíram legíveis. Releia com os parâmetros corrigidos até
o `head()` ficar limpo.

Quando ficar limpo, anote os parâmetros que funcionaram em **Como ler** no
`contexto.md` — assim a próxima sessão já lê certo de primeira.

> Atalho útil: dado de governo brasileiro (PRF, IBGE, DATASUS…) costuma ser
> `sep=";", encoding="latin-1", decimal=","`. É um bom primeiro palpite — mas
> confirme com o `head()`, não assuma.
