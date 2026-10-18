#!/usr/bin/env python3
"""
stop.py — encerra o servidor Jupyter deste projeto. Multiplataforma.
Roda sozinho quando o Claude Code fecha (hook SessionEnd do plugin) ou na mão,
na pasta do projeto:
    uv run --no-project --python 3.12 <plugin>/scripts/stop.py
Não apaga o .venv nem as dependências — só derruba o servidor.

Primeiro pede o desligamento pela API (encerra kernels com calma). Só se a API
não responder, cai para matar o processo — e apenas se o PID ainda for Jupyter.
"""
import os, signal, subprocess, time
from _jupyter import IS_WIN, read_runtime, api, pid_alive, is_jupyter, clear_runtime

def wait_dead(pid, secs=10):
    for _ in range(secs * 4):
        if not pid or not pid_alive(pid):
            return True
        time.sleep(0.25)
    return False

def kill(pid):
    if IS_WIN:
        subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"], capture_output=True)
    else:
        try:
            os.killpg(pid, signal.SIGTERM)  # grupo inteiro: servidor + kernels
        except OSError:
            os.kill(pid, signal.SIGTERM)

def main():
    pid, port, token = read_runtime()
    if port and token and api(port, token, "/api/shutdown", method="POST") == 200:
        wait_dead(pid)
        print("✅ Servidor Jupyter encerrado.")
    elif pid and pid_alive(pid) and is_jupyter(pid):
        kill(pid)
        wait_dead(pid)
        print("✅ Servidor Jupyter encerrado (forçado — a API não respondeu).")
    else:
        print("ℹ️  Nenhum servidor Jupyter ativo para encerrar.")
    clear_runtime()

if __name__ == "__main__":
    main()
