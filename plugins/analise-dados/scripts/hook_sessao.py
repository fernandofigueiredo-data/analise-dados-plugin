#!/usr/bin/env python3
"""
hook_sessao.py — hook SessionStart: carrega as regras de casa no contexto.

Plugins não carregam CLAUDE.md, então as regras (REGRAS.md) entram por aqui —
o que este script imprime vira contexto da sessão. Só age em pastas que já
parecem projeto de análise (dados/, contexto.md, notebooks): o plugin costuma
ficar instalado para o usuário inteiro e não deve poluir outros projetos.
Só stdlib, Python 3.8+.
"""
import sys
from _jupyter import PLUGIN, PROJ
from projeto import eh_projeto_de_analise

def main():
    sys.stdin.read()  # a entrada do hook (JSON) não é necessária aqui
    if not eh_projeto_de_analise(PROJ):
        return
    regras = (PLUGIN / "REGRAS.md").read_text(encoding="utf-8")
    sys.stdout.write(
        f"A pasta {PROJ.name}/ é um projeto de análise de dados do plugin analise-dados. "
        "O usuário definiu as regras de casa abaixo para este tipo de projeto.\n\n" + regras)

if __name__ == "__main__":
    main()
