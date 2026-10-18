"""
regras.py — as regras de casa (REGRAS.md) que dá para checar por código.

Usadas em dois momentos, com as mesmas mensagens:
- hook_celula.py: na hora em que o Claude escreve a célula (PostToolUse);
- validar.py: no notebook inteiro, depois de rodar do zero.
Só stdlib, Python 3.8+.
"""
import re

MAX_LINHAS = 10  # REGRAS.md: passou de 10 linhas, a célula mistura coisas

def linhas_de_codigo(fonte):
    """Linhas que contam: sem as vazias e sem as marcações `#|` do relatório."""
    return [l for l in fonte.splitlines() if l.strip() and not l.lstrip().startswith("#|")]

def fora_de_codigo(md):
    """Markdown sem blocos e trechos de código — onde `$` vira fórmula."""
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", md)

def problemas_codigo(fonte):
    n = len(linhas_de_codigo(fonte))
    if n > MAX_LINHAS:
        return [f"{n} linhas de código — a regra é ~5-8 (máximo {MAX_LINHAS}); "
                "quebre em células menores, separando preparação de visualização"]
    return []

def problemas_markdown(fonte):
    if re.search(r"(?<!\\)\$", fora_de_codigo(fonte)):
        return ["`$` sem escape no markdown vira fórmula — use crase (`R$ 10`) ou \\\\$"]
    return []

def problemas(tipo, fonte):
    return problemas_markdown(fonte) if tipo == "markdown" else problemas_codigo(fonte)
