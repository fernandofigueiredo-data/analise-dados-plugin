"""
_jupyter.py — peças comuns aos scripts do plugin (só stdlib, Python 3.8+).

Dois lugares diferentes:
- PLUGIN: onde o plugin está instalado (muda a cada atualização — não guarde estado aqui);
- PROJ: o projeto de análise do usuário (a pasta onde o Claude Code foi aberto).

A fonte da verdade sobre o servidor é a API do Jupyter, não o PID: um PID
antigo pode ter sido reaproveitado pelo sistema por outro processo. Se a API
responde com o NOSSO token, o servidor é nosso e está vivo.
"""
import os, subprocess, sys, urllib.request
from pathlib import Path

# Saída sempre em UTF-8: no Windows, com a saída num pipe (Bash do Claude, CI),
# o Python usaria cp1252 e quebraria nos ✅ e acentos.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PLUGIN = Path(__file__).resolve().parent.parent
PROJ = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
RT = PROJ / ".runtime"
VENV = PROJ / ".venv"
PIDF, PORTF, TOKENF = RT / "jupyter.pid", RT / "jupyter.port", RT / "jupyter.token"
IS_WIN = os.name == "nt"
VENV_PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")

def jupyter_env():
    """Ambiente para Jupyter e kernels: o kernel do .venv na frente de qualquer
    "python3" do usuário (~/Library/Jupyter, ~/.local/share/jupyter), que senão
    ganharia e rodaria as células no Python do sistema."""
    return dict(os.environ, JUPYTER_PATH=str(VENV / "share" / "jupyter"))

def read_runtime():
    """(pid, port, token) gravados pelo bootstrap, ou None no que faltar."""
    def read(f):
        try:
            return f.read_text().strip() or None
        except OSError:
            return None
    pid, port, token = read(PIDF), read(PORTF), read(TOKENF)
    return (int(pid) if pid else None, int(port) if port else None, token)

def api(port, token, path, method="GET", timeout=2):
    """Chama a API do Jupyter autenticando pelo header. Retorna o status HTTP ou None."""
    req = urllib.request.Request(f"http://localhost:{port}{path}", method=method,
                                 headers={"Authorization": f"token {token}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except Exception:
        return None

def server_ok(port, token):
    return bool(port and token) and api(port, token, "/api/status") == 200

def pid_alive(pid):
    if IS_WIN:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, text=True)
        return str(pid) in out.stdout
    try:
        os.kill(pid, 0); return True
    except OSError:
        return False

def is_jupyter(pid):
    """O PID ainda é um processo do Jupyter? (protege contra PID reaproveitado)"""
    if IS_WIN:
        query = f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"
        out = subprocess.run(["powershell", "-NoProfile", "-Command", query],
                             capture_output=True, text=True)
    else:
        out = subprocess.run(["ps", "-p", str(pid), "-o", "command="],
                             capture_output=True, text=True)
    return "jupyter" in out.stdout.lower()

def clear_runtime():
    for f in (PIDF, PORTF, TOKENF):
        f.unlink(missing_ok=True)
