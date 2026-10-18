"""
Teste de fumaça do ciclo principal: Jupyter MCP (versão do plugin) → Jupyter do
projeto → executar uma célula no kernel do .venv. Só stdlib.

    cd exemplo && uv run --no-project --python 3.12 ../tests/mcp_fumaca.py

Precisa do Jupyter no ar (bootstrap.py antes). Cria e apaga _fumaca.ipynb.
"""
import json, os, subprocess, sys, time, urllib.request
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "analise-dados"
PROJ = Path.cwd()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    servidor = json.loads((PLUGIN / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["jupyter"]
    porta = (PROJ / ".runtime" / "jupyter.port").read_text().strip()
    token = (PROJ / ".runtime" / "jupyter.token").read_text().strip()
    env = dict(os.environ, **servidor.get("env", {}))
    p = subprocess.Popen([servidor["command"], *servidor["args"]], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                         encoding="utf-8", env=env)
    n = 0

    def rpc(metodo, params=None, notificacao=False):
        nonlocal n
        msg = {"jsonrpc": "2.0", "method": metodo, "params": params or {}}
        if not notificacao:
            n += 1
            msg["id"] = n
        p.stdin.write(json.dumps(msg) + "\n")
        p.stdin.flush()
        while not notificacao:
            linha = p.stdout.readline()
            if not linha:
                raise SystemExit("❌ o servidor MCP fechou")
            r = json.loads(linha)
            if r.get("id") == n:
                return r

    def chamar(nome, args):
        r = rpc("tools/call", {"name": nome, "arguments": args})["result"]
        texto = " ".join(c.get("text", "") for c in r.get("content", []))
        if r.get("isError"):
            raise SystemExit(f"❌ {nome}: {texto[:300]}")
        return texto

    t0 = time.time()
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "fumaca", "version": "1"}})
    rpc("notifications/initialized", notificacao=True)
    print(f"✅ MCP pronto em {time.time() - t0:.1f}s")
    try:
        chamar("connect_to_jupyter", {"jupyter_url": f"http://localhost:{porta}", "jupyter_token": token})
        chamar("use_notebook", {"notebook_name": "fumaca", "notebook_path": "_fumaca.ipynb", "mode": "create"})
        saida = chamar("insert_execute_code_cell", {
            "cell_index": -1,
            "cell_source": "import sys, analise_dados\nprint('venv' if '.venv' in sys.executable else sys.executable, 6 * 7)"})
        if "venv 42" not in saida:
            raise SystemExit(f"❌ a célula não rodou no .venv do projeto: {saida[:300]}")
        print("✅ célula executada no kernel do .venv, com a biblioteca do plugin")
    finally:
        # fecha no MCP e apaga pela API: a colaboração ao vivo regravaria um arquivo apagado no disco
        try:
            chamar("unuse_notebook", {"notebook_name": "fumaca"})
        except SystemExit:
            pass
        p.terminate()
        time.sleep(2)
        req = urllib.request.Request(f"http://localhost:{porta}/api/contents/_fumaca.ipynb",
                                     method="DELETE", headers={"Authorization": f"token {token}"})
        try:
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            (PROJ / "_fumaca.ipynb").unlink(missing_ok=True)

if __name__ == "__main__":
    sys.exit(main())
