---
description: Liga o projeto a um banco de dados (Postgres, BigQuery, DuckDB ou SQLite) para analisar com SQL
argument-hint: "[postgres | bigquery | duckdb | sqlite]"
---

Ligue este projeto de análise a um banco de dados. O aluno passou isto junto
do comando (pode estar vazio): `$ARGUMENTS`

A senha **nunca passa por você**: o aluno escreve a `DB_URL` no `.env` do
projeto, e tanto o notebook quanto o servidor MCP leem de lá. Nunca leia,
mostre ou edite o `.env` (a leitura já está bloqueada nas permissões do
projeto).

## Passo 1 — Qual banco?

Se `$ARGUMENTS` não disser, pergunte: Postgres, BigQuery, DuckDB (arquivo
`.duckdb`) ou SQLite. Para DuckDB e SQLite, pergunte também o caminho do
arquivo (o padrão é `dados/base.duckdb` ou `dados/base.sqlite`).

## Passo 2 — Configurar

Garanta que o ambiente existe (se não houver `.venv`, rode antes o Passo 2 do
`/analise`). Depois, na pasta do projeto:

`uv run --no-project --python .venv "${CLAUDE_PLUGIN_ROOT}/scripts/banco.py" configurar <tipo> [caminho]`

Isso cria o `.env.exemplo` (o modelo da `DB_URL`, sem senha) e registra o
servidor MCP `banco` no `.mcp.json` do projeto. Mostre a saída ao aluno.

## Passo 3 — O aluno preenche o `.env`

Peça ao aluno, com as palavras do tipo de banco dele:

- copiar `.env.exemplo` para `.env` e trocar os valores de exemplo pelos reais;
- **Postgres:** usar um usuário só de leitura, se a empresa tiver;
- **BigQuery:** rodar uma vez `gcloud auth application-default login` no
  terminal e usar um papel só de leitura (BigQuery Data Viewer + Job User);
- avisar quando terminar.

Espere a resposta.

## Passo 4 — Instalar o driver e testar

1. Rode o bootstrap de novo (Passo 2 do `/analise`): ele lê o tipo de banco do
   `.env` e instala o driver certo no ambiente — a saída diz "com drivers de
   banco: …". Se o Jupyter já estava no ar, reinicie o kernel do notebook para
   ele enxergar o driver.
2. Teste a conexão:
   `uv run --no-project --python .venv "${CLAUDE_PLUGIN_ROOT}/scripts/banco.py" testar`
   — mostra só o tipo do banco e as tabelas visíveis, nunca a URL. Se falhar,
   peça ao aluno para conferir o `.env`; não tente adivinhar a senha nem o host.

## Passo 5 — Ligar o servidor MCP

O servidor `banco` foi registrado agora, então ainda não está ativo nesta
sessão. Peça ao aluno para digitar `/mcp`, aprovar o servidor **banco** do
projeto e conectar (ou reabrir o Claude Code nesta pasta).

## Passo 6 — Registrar e seguir

Anote em **Dados** no `contexto.md` o tipo de banco e as tabelas que importam
(nunca a `DB_URL`). A partir daqui, a análise segue a skill `sql`, com o mesmo
ciclo de uma pergunta por vez.
