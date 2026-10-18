---
name: sql
description: >-
  Como analisar dados que estão num banco (Postgres, BigQuery, DuckDB, SQLite)
  ou em arquivos grandes demais para o pandas, mantendo o ciclo de uma pergunta
  por vez: consulta SQL curta no notebook → executa → revisão crítica →
  interpretação. Use sempre que a fonte for um banco (o .env do projeto tem
  DB_URL, ou existe o servidor MCP "banco"), ou quando for escrever SQL numa
  análise — inclusive SQL sobre CSV/Parquet locais com DuckDB.
---

# SQL sem perder o método

Banco não muda o método da skill `analista-senior`: **uma pergunta por vez**,
célula curta, executa, confere, interpreta. Muda só de onde vêm os números.

## Duas ferramentas, dois papéis

- **Servidor MCP `banco`** (quando o `/banco` foi configurado): para **você
  explorar** — listar tabelas, ver colunas, testar uma consulta antes de
  escrevê-la no notebook. O que você vê ali **não entra na análise**.
- **`analise_dados.banco` no notebook**: para **a análise**. Todo número que
  aparece numa interpretação tem que vir de uma célula do notebook — é o que o
  `/validar` roda de novo, do zero, e o que outra pessoa consegue refazer.

```python
from analise_dados import banco

banco.tabelas()                 # o que existe
banco.colunas("pedidos")        # colunas e tipos de uma tabela
```

Nunca leia, mostre ou edite o `.env` — a `DB_URL` tem senha. O `banco` lê
sozinho. Postgres e DuckDB já abrem em modo somente leitura.

## O ciclo com SQL

1. **Pergunta** em markdown, como sempre.
2. **Uma consulta que responde só a ela**, curta (até ~8 linhas — a mesma regra
   de célula curta; o hook do plugin confere). Pergunta grande vira várias
   consultas pequenas, uma por célula.

   ```python
   banco.consulta("""
       SELECT regiao, COUNT(*) AS pedidos, SUM(valor) AS faturamento
       FROM pedidos
       WHERE data >= :inicio
       GROUP BY regiao
       ORDER BY faturamento DESC
   """, inicio="2025-01-01")
   ```

3. **Executa e lê** o resultado.
4. **Revisão crítica** (skill `revisao-critica`) e **interpretação**.

## Regras que valem só para banco

- **Agregue no banco, não no pandas.** `SELECT *` numa tabela de milhões de
  linhas trava o notebook e pode custar caro. Traga o resultado já resumido;
  para olhar linhas cruas, use `LIMIT 10`.
- **O `n` vem junto.** Toda média ou taxa sai com `COUNT(*)` na mesma consulta —
  a revisão crítica precisa dele.
- **Valores entram como parâmetro** (`:nome`), nunca com f-string: evita erro
  de aspas e injeção de SQL.
- **Nomes legíveis no resultado:** `AS faturamento`, `AS pedidos` — a tabela vai
  para o relatório.
- **Datas e fuso:** confira o tipo da coluna de data (`banco.colunas`) e se ela
  está em UTC antes de agrupar por dia ou mês.
- **Primeira consulta de cada tabela = conhecer os dados.** Contagem de linhas,
  período coberto, quantos nulos nas colunas da pergunta. A skill
  `qualidade-dados` vale aqui também, em SQL.
- **BigQuery cobra por dados lidos.** Antes de uma consulta sobre tabela
  grande, estime: `banco.estimar("SELECT ...")`. Filtre pela coluna de partição
  (normalmente a data) e selecione só as colunas necessárias — nunca `SELECT *`.
  Se a estimativa passar de alguns GB, mostre ao usuário antes de rodar.

## Arquivos locais grandes: DuckDB

CSV ou Parquet grande demais para o pandas? Consulte o arquivo direto, sem
servidor e sem carregar tudo na memória:

```python
banco.arquivos("""
    SELECT canal_venda, COUNT(*) AS vendas
    FROM 'dados/vendas.csv'
    GROUP BY canal_venda
""")
```

O resultado é um DataFrame pequeno; daí em diante, gráfico e interpretação
seguem como sempre.

## Registrar no `contexto.md`

Em **Dados**, anote a fonte (tipo de banco e tabelas usadas — **nunca a
DB_URL**), o período e o que cada tabela representa. Filtros fixos da análise
(ex.: "só pedidos pagos") vão em **Decisões de tratamento**.
