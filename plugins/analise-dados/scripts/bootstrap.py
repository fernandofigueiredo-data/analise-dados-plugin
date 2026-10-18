#!/usr/bin/env python3
"""
bootstrap.py — prepara o projeto, o ambiente Python e sobe o Jupyter.
Multiplataforma (Windows, macOS, Linux). Roda na pasta do projeto do usuário:

    uv run --no-project --python 3.12 <plugin>/scripts/bootstrap.py

É IDEMPOTENTE: pode rodar quantas vezes quiser. Reusa o que já existe.
O ambiente (.venv do projeto) segue o uv.lock do PLUGIN — atualizar o plugin
atualiza as dependências de todos os projetos na próxima execução.

No final, imprime o bloco que o Claude lê para conectar:
    JUPYTER_URL=http://localhost:PORTA
    JUPYTER_TOKEN=...

Só depende de: uv (no PATH) + a própria stdlib.
"""
import os, sys, socket, secrets, subprocess, time
from _jupyter import (PLUGIN, PROJ, RT, VENV, VENV_PY, PIDF, PORTF, TOKENF, IS_WIN,
                      jupyter_env, read_runtime, server_ok)
from projeto import preparar, ler_db_url, extra_do_banco

PIN_PY = "3.12"  # versão fixa para reprodutibilidade entre máquinas
JUPYTER = VENV / ("Scripts/jupyter.exe" if IS_WIN else "bin/jupyter")
KERNEL = VENV / "share/jupyter/kernels/python3/kernel.json"

def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)

def free_port():
    for p in (8888, 8889, 8890, 8891):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p)); return p
            except OSError:
                continue
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

def log_tail(n=15):
    try:
        return "\n".join((RT / "jupyter.log").read_text(errors="replace").splitlines()[-n:])
    except OSError:
        return "(sem log)"

def sincronizar():
    """uv sync do ambiente do plugin no .venv do projeto. --frozen: segue o lock
    sem reescrevê-lo; --inexact: preserva o que o usuário instalou com %pip."""
    cmd = ["uv", "sync", "--frozen", "--inexact", "--quiet", "--python", PIN_PY,
           "--project", str(PLUGIN / "ambiente")]
    extra = extra_do_banco(ler_db_url())
    if extra:
        cmd += ["--extra", extra]
    run(cmd, env=dict(os.environ, UV_PROJECT_ENVIRONMENT=str(VENV)))
    return extra

def ligar_biblioteca():
    """Torna `import analise_dados` (painel, banco) disponível no notebook, via .pth.
    Reescrito a cada execução porque o caminho do plugin muda quando ele atualiza."""
    purelib = subprocess.run([str(VENV_PY), "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                             capture_output=True, text=True, check=True).stdout.strip()
    pth = os.path.join(purelib, "analise_dados_plugin.pth")
    with open(pth, "w", encoding="utf-8") as f:
        f.write(str(PLUGIN / "lib") + "\n")

def main():
    RT.mkdir(exist_ok=True)
    print(f"🔧 Preparando o projeto em {PROJ.name}/ ...\n")

    # 0. Pastas e arquivos de apoio do projeto (só cria o que falta)
    for item in preparar():
        print(f"✅ Criado: {item}" if not item.startswith("⚠️") else item)

    # 1. Ambiente + dependências
    first = not VENV.exists()
    if first:
        print("   1ª vez: baixando Python, pandas, matplotlib, plotly e Jupyter (~1 min)...")
    extra = sincronizar()
    ligar_biblioteca()
    print("✅ Ambiente e dependências prontos" + (f" (com drivers de banco: {extra})" if extra else ""))

    # 2. Kernel com nome claro, local ao venv (sobrescreve o "python3" padrão)
    if not KERNEL.exists() or "Claude Code" not in KERNEL.read_text(encoding="utf-8"):
        run([str(VENV_PY), "-m", "ipykernel", "install", "--prefix", str(VENV),
             "--name", "python3", "--display-name", "🤖 Análise de Dados (Claude Code)"],
            stdout=subprocess.DEVNULL)
        print("✅ Kernel do projeto registrado")

    # 3. Servidor Jupyter: reusa se a API responde com o nosso token, senão sobe
    _, port, token = read_runtime()
    proc = None
    if server_ok(port, token):
        print(f"✅ Servidor Jupyter no ar — porta {port} (reaproveitado)")
    else:
        port, token = free_port(), secrets.token_hex(24)
        PORTF.write_text(str(port)); TOKENF.write_text(token)
        log = open(RT / "jupyter.log", "w")
        args = [str(JUPYTER), "lab", "--port", str(port), "--no-browser",
                "--allow-root",
                "--IdentityProvider.token", token, f"--ServerApp.root_dir={PROJ}"]
        kw = dict(stdout=log, stderr=subprocess.STDOUT, cwd=str(PROJ), env=jupyter_env())
        if IS_WIN:
            kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008  # DETACHED
        else:
            kw["start_new_session"] = True
        proc = subprocess.Popen(args, **kw)
        PIDF.write_text(str(proc.pid))
        print(f"   Subindo o servidor Jupyter na porta {port}...")

    # 4. Espera a API responder (e falha cedo se o processo morrer no caminho)
    url = f"http://localhost:{port}"
    for _ in range(60):
        if server_ok(port, token):
            break
        if proc and proc.poll() is not None:
            print(f"❌ O Jupyter encerrou ao iniciar. Final do log:\n{log_tail()}", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
    else:
        print(f"❌ O servidor não respondeu a tempo. Veja {RT/'jupyter.log'}:\n{log_tail()}",
              file=sys.stderr)
        sys.exit(1)
    if proc:
        print(f"✅ Servidor Jupyter no ar — porta {port}")

    print()
    print("🔭 Abra o notebook ao vivo no navegador:")
    print(f"   {url}/lab?token={token}")
    print()
    print("---")
    print(f"JUPYTER_URL={url}")
    print(f"JUPYTER_TOKEN={token}")

if __name__ == "__main__":
    main()
