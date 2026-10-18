#!/usr/bin/env python3
"""
banco.py — liga o projeto a um banco de dados (comando /banco).

    uv run --no-project --python .venv <plugin>/scripts/banco.py configurar postgres|bigquery|duckdb|sqlite [caminho do arquivo]
    uv run --no-project --python .venv <plugin>/scripts/banco.py testar

configurar: escreve o .env.exemplo (modelo da DB_URL, sem senha) e registra o
servidor MCP "banco" no .mcp.json do projeto, para o Claude explorar tabelas e
colunas. Quem cria o .env com a senha é o usuário — este script nunca lê nem
imprime a DB_URL de verdade.
testar: conecta usando o .env e mostra só o tipo do banco e as tabelas visíveis.
"""
import json, sys
from _jupyter import PROJ

MCP_ALCHEMY = "mcp-alchemy==2026.9.5.185701"            # Postgres, BigQuery, SQLite
MCP_DUCKDB = "mcp-server-motherduck==1.0.8"             # DuckDB (o mcp-alchemy não funciona com ele)

TIPOS = {
    "postgres": {
        "exemplo": "DB_URL=postgresql+psycopg://USUARIO_SO_LEITURA:SENHA@HOST:5432/BANCO",
        "driver": "psycopg[binary]",
        "opcoes": {"connect_args": {"options": "-c default_transaction_read_only=on"}},
        "dica": "Use um usuário só de leitura. A conexão já abre em modo somente leitura.",
    },
    "bigquery": {
        "exemplo": "DB_URL=bigquery://ID_DO_PROJETO_GCP/DATASET",
        "driver": "sqlalchemy-bigquery",
        "opcoes": {},
        "dica": ("Autentique uma vez com `gcloud auth application-default login`. "
                 "Use um papel só de leitura (BigQuery Data Viewer + Job User). "
                 "O BigQuery cobra por dados lidos: estime antes com banco.estimar()."),
    },
    "duckdb": {
        "exemplo": "DB_URL=duckdb:///dados/base.duckdb",
        "driver": "duckdb-engine",
        "opcoes": {"connect_args": {"read_only": True}},
        "dica": "O arquivo .duckdb abre em modo somente leitura.",
    },
    "sqlite": {
        "exemplo": "DB_URL=sqlite:///dados/base.sqlite",
        "driver": None,
        "opcoes": {},
        "dica": "Caminho relativo à pasta do projeto.",
    },
}

def servidor_mcp(tipo, caminho=None):
    if tipo == "duckdb":  # arquivo local, sem senha: o caminho vai direto; abre só leitura por padrão
        return {"command": "uvx", "args": [MCP_DUCKDB, "--db-path", caminho or "dados/base.duckdb"]}
    t = TIPOS[tipo]
    args = ["--env-file", ".env", "--from", MCP_ALCHEMY]
    if t["driver"]:
        args += ["--with", t["driver"]]
    env = {"EXECUTE_QUERY_MAX_CHARS": "4000"}
    if t["opcoes"]:
        env["DB_ENGINE_OPTIONS"] = json.dumps(t["opcoes"])
    return {"command": "uvx", "args": args + ["mcp-alchemy"], "env": env}

def configurar(tipo, caminho=None):
    if tipo not in TIPOS:
        print(f"❌ Tipo desconhecido: {tipo}. Use: {', '.join(TIPOS)}")
        return 2
    t = TIPOS[tipo]
    exemplo = t["exemplo"]
    if caminho and tipo in ("duckdb", "sqlite"):
        exemplo = f"DB_URL={tipo}:///{caminho}"
    (PROJ / ".env.exemplo").write_text(
        "# Copie este arquivo para .env e preencha. O .env fica fora do git.\n"
        f"{exemplo}\n", encoding="utf-8")
    arq = PROJ / ".mcp.json"
    cfg = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    cfg.setdefault("mcpServers", {})["banco"] = servidor_mcp(tipo, caminho)
    arq.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ .env.exemplo criado com o modelo da DB_URL ({tipo})")
    print("✅ Servidor MCP \"banco\" registrado no .mcp.json do projeto")
    print(f"ℹ️  {t['dica']}")
    print("👉 Próximo passo (é do usuário): copiar .env.exemplo para .env e preencher a DB_URL.")
    return 0

def testar():
    from analise_dados import banco  # vem do plugin via .pth no .venv (bootstrap)
    try:
        tipo = banco.tipo()
        nomes = banco.tabelas()["tabela"].tolist()
    except Exception as e:
        print(f"❌ Não conectou: {type(e).__name__}. Confira a DB_URL no .env "
              "(este script não mostra a mensagem completa porque ela pode conter a senha).")
        return 1
    mostrar = ", ".join(nomes[:10]) + (" …" if len(nomes) > 10 else "")
    print(f"✅ Conectado ({tipo}) — {len(nomes)} tabela(s) visível(is): {mostrar or '(nenhuma)'}")
    return 0

def main():
    acao = sys.argv[1] if len(sys.argv) > 1 else ""
    if acao == "configurar" and len(sys.argv) > 2:
        return configurar(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    if acao == "testar":
        return testar()
    print(__doc__)
    return 2

if __name__ == "__main__":
    sys.exit(main())
