"""
projeto.py — prepara a pasta do usuário como projeto de análise (só stdlib).

Idempotente e conservador: cria o que falta e acrescenta o que falta, nunca
apaga nem sobrescreve o que o usuário já tem.
"""
import json, re, shutil
from _jupyter import PLUGIN, PROJ

IGNORAR = [
    ".venv/", ".runtime/", "saidas/*", "!saidas/.gitkeep", ".ipynb_checkpoints/",
    "__pycache__/", ".jupyter/", ".jupyter_ystore.db", ".env",
    ".claude/settings.local.json", ".DS_Store", "Thumbs.db",
]

# Comandos do fluxo liberados sem perguntar. O caminho do plugin muda a cada
# versão instalada, por isso o curinga antes do nome do script.
PERMITIR = [
    "Bash(uv --version)",
    "Bash(uv run --no-project --python 3.12 *analise-dados*bootstrap.py*)",
    "Bash(uv run --no-project --python 3.12 *analise-dados*stop.py*)",
    "Bash(uv run --no-project --python .venv *analise-dados*banco.py*)",
    "Bash(uv run --no-project --python .venv *analise-dados*validar.py*)",
    "Bash(uv run --no-project --python .venv *analise-dados*relatorio.py*)",
    "mcp__plugin_analise-dados_jupyter__*",
    # servidor "banco" do /banco: só as ferramentas que leem a estrutura;
    # consultas (execute_query) continuam pedindo confirmação
    "mcp__banco__all_table_names",
    "mcp__banco__filter_table_names",
    "mcp__banco__schema_definitions",
    "mcp__banco__list_databases",
    "mcp__banco__list_tables",
    "mcp__banco__list_columns",
]
# Edit(...) cobre todas as ferramentas que editam arquivos (Write incluso)
NEGAR = ["Edit(./dados/**)", "Read(./.env)"]

# Esquema da DB_URL → extra do ambiente com o driver certo
EXTRAS = {"postgresql": "postgres", "postgres": "postgres", "bigquery": "bigquery",
          "duckdb": "duckdb", "sqlite": "sql"}

def eh_projeto_de_analise(pasta=PROJ):
    """Sinais de que a pasta é um projeto de análise (para não poluir outros projetos)."""
    return any([(pasta / "dados").is_dir(), (pasta / "contexto.md").exists(),
                (pasta / ".runtime").exists(), any(pasta.glob("*.ipynb"))])

def ler_db_url(pasta=PROJ):
    """DB_URL do .env do projeto, ou None. Nunca imprima o valor: tem senha."""
    env = pasta / ".env"
    if not env.exists():
        return None
    for linha in env.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(?:export\s+)?DB_URL\s*=\s*(.+?)\s*$", linha)
        if m:
            return m.group(1).strip("'\"")
    return None

def extra_do_banco(db_url):
    if not db_url:
        return None
    esquema = db_url.split("://", 1)[0].split("+", 1)[0].lower()
    return EXTRAS.get(esquema)

def _gitignore(feito):
    gi = PROJ / ".gitignore"
    atual = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    faltando = [l for l in IGNORAR if l not in atual]
    if faltando:
        bloco = ["", "# analise-dados (plugin)"] if atual else ["# analise-dados (plugin)"]
        gi.write_text("\n".join(atual + bloco + faltando) + "\n", encoding="utf-8")
        feito.append(".gitignore" + (" (completado)" if atual else ""))

def _settings(feito):
    arq = PROJ / ".claude" / "settings.json"
    try:
        cfg = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    except json.JSONDecodeError:
        feito.append("⚠️  .claude/settings.json inválido — não mexi; permissões não configuradas")
        return
    perms = cfg.setdefault("permissions", {})
    mudou = False
    for chave, regras in (("allow", PERMITIR), ("deny", NEGAR)):
        lista = perms.setdefault(chave, [])
        for r in regras:
            if r not in lista:
                lista.append(r); mudou = True
    if "MCP_TIMEOUT" not in cfg.setdefault("env", {}):
        cfg["env"]["MCP_TIMEOUT"] = "90000"; mudou = True
    if mudou:
        arq.parent.mkdir(exist_ok=True)
        arq.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        feito.append(".claude/settings.json (permissões do fluxo)")

def preparar():
    """Cria pastas e arquivos de apoio que faltarem. Retorna a lista do que fez."""
    feito = []
    for pasta in ("dados", "saidas"):
        if not (PROJ / pasta).is_dir():
            (PROJ / pasta).mkdir(); feito.append(f"{pasta}/")
    (PROJ / "saidas" / ".gitkeep").touch()
    ds = PROJ / "estilos" / "design-system.md"
    if not ds.exists():
        shutil.copytree(PLUGIN / "modelo" / "estilos", PROJ / "estilos", dirs_exist_ok=True)
        feito.append("estilos/design-system.md (paleta padrão)")
    _gitignore(feito)
    _settings(feito)
    return feito
