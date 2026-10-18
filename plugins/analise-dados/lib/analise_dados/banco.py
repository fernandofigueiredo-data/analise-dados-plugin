"""
analise_dados.banco — SQL no notebook, com o mesmo ciclo de uma pergunta por vez.

    from analise_dados import banco
    banco.tabelas()                                   # o que existe no banco
    banco.consulta("SELECT regiao, COUNT(*) AS n FROM vendas GROUP BY 1")
    banco.arquivos("SELECT * FROM 'dados/vendas.csv' LIMIT 5")   # CSV/Parquet locais

A conexão vem da DB_URL no .env do projeto (o usuário preenche; o Claude não
lê). Postgres e DuckDB abrem em modo somente leitura.
"""
import os, re
from functools import lru_cache
from pathlib import Path
import pandas as pd

def _ler_env():
    """DB_URL do ambiente ou do .env da pasta atual (ou de uma pasta acima)."""
    if os.environ.get("DB_URL"):
        return os.environ["DB_URL"]
    for pasta in [Path.cwd(), *Path.cwd().parents]:
        env = pasta / ".env"
        if env.exists():
            for linha in env.read_text(encoding="utf-8").splitlines():
                m = re.match(r"\s*(?:export\s+)?DB_URL\s*=\s*(.+?)\s*$", linha)
                if m:
                    return m.group(1).strip("'\"")
    raise RuntimeError("Sem DB_URL: crie o .env do projeto a partir do .env.exemplo (comando /banco).")

def tipo():
    """Tipo do banco pela DB_URL: postgresql, bigquery, duckdb, sqlite…"""
    return _ler_env().split("://", 1)[0].split("+", 1)[0].lower()

def opcoes_somente_leitura(t):
    """Opções do SQLAlchemy que impedem escrita, quando o banco permite."""
    if t in ("postgresql", "postgres"):
        return {"connect_args": {"options": "-c default_transaction_read_only=on"}}
    if t == "duckdb":
        return {"connect_args": {"read_only": True}}
    return {}

@lru_cache(maxsize=1)
def motor():
    from sqlalchemy import create_engine
    return create_engine(_ler_env(), pool_pre_ping=True, **opcoes_somente_leitura(tipo()))

def consulta(sql, **parametros):
    """Roda uma consulta e devolve um DataFrame. Valores entram como :nome
    (nunca monte SQL com f-string): consulta("... WHERE uf = :uf", uf="SP")."""
    from sqlalchemy import text
    with motor().connect() as conexao:
        return pd.read_sql(text(sql), conexao, params=parametros or None)

def tabelas():
    """Tabelas e views visíveis, uma por linha."""
    from sqlalchemy import inspect
    insp = inspect(motor())
    nomes = insp.get_table_names() + insp.get_view_names()
    return pd.DataFrame({"tabela": sorted(nomes)})

def colunas(tabela):
    """Colunas de uma tabela, com o tipo de cada uma."""
    from sqlalchemy import inspect
    try:
        cols = inspect(motor()).get_columns(tabela)
        return pd.DataFrame({"coluna": [c["name"] for c in cols],
                             "tipo": [str(c["type"]) for c in cols]})
    except Exception:
        # alguns drivers não sabem descrever tabelas: lê zero linhas e usa os tipos do pandas
        nome = ".".join(motor().dialect.identifier_preparer.quote(p) for p in tabela.split("."))
        vazio = consulta(f"SELECT * FROM {nome} LIMIT 0")
        return pd.DataFrame({"coluna": vazio.columns, "tipo": vazio.dtypes.astype(str).values})

def estimar(sql):
    """BigQuery cobra por bytes lidos: estima quanto a consulta vai ler, sem rodar."""
    if tipo() != "bigquery":
        return "estimativa de custo só se aplica ao BigQuery"
    from google.cloud import bigquery
    caminho = _ler_env().split("://", 1)[1].split("?", 1)[0].strip("/")
    projeto, _, dataset = caminho.partition("/")
    config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False,
                                     default_dataset=f"{projeto}.{dataset}" if dataset else None)
    lidos = bigquery.Client(project=projeto).query(sql, job_config=config).total_bytes_processed
    return f"a consulta vai ler ≈ {lidos / 1e9:,.2f} GB".replace(",", "X").replace(".", ",").replace("X", ".")

def arquivos(sql):
    """SQL direto em CSV/Parquet locais com DuckDB, sem servidor:
    arquivos("SELECT regiao, COUNT(*) AS n FROM 'dados/vendas.csv' GROUP BY 1")"""
    import duckdb
    return duckdb.sql(sql).df()
