#!/usr/bin/env python3
"""
hook_celula.py — hook PostToolUse nas edições de célula do Jupyter MCP.

Confere a célula que o Claude acabou de escrever contra as regras checáveis
(regras.py): código com mais de 10 linhas, `$` sem escape no markdown. Achou
problema → sai com código 2 e a explicação no stderr, que o Claude Code mostra
ao Claude (a célula já foi gravada; o aviso pede a correção).

O que cada ferramenta entrega:
- insert_cell / insert_execute_code_cell: texto e tipo da célula — checagem exata;
- overwrite_cell_source: texto sem o tipo — o tipo é deduzido pelo conteúdo;
- edit_cell_source: só um diff na resposta — melhor esforço (o /validar
  pega o resto no notebook inteiro).
Só stdlib, Python 3.8+.
"""
import json, re, sys
import _jupyter  # noqa: F401 — saída em UTF-8 também no Windows
from regras import MAX_LINHAS, problemas, problemas_markdown

def parece_codigo(fonte):
    """Python válido (ignorando magics %/!) e não só comentários → código."""
    linhas = [l for l in fonte.splitlines() if l.strip() and not l.lstrip().startswith(("%", "!"))]
    if not linhas or all(l.lstrip().startswith("#") for l in linhas):
        return False
    try:
        compile("\n".join(linhas), "<celula>", "exec")
        return True
    except SyntaxError:
        return False

def textos(obj):
    """Todas as strings dentro da resposta da ferramenta (formato varia)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from textos(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from textos(v)

def analisar_diff(resposta):
    """(menor nº de linhas que a célula tem agora, texto novo/visível) a partir do diff."""
    diff = next((m.group(1) for t in textos(resposta)
                 for m in [re.search(r"```diff\n(.*?)```", t, re.S)] if m), "")
    minimo, visiveis = 0, []
    for linha in diff.splitlines():
        h = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", linha)
        if h:
            minimo = max(minimo, int(h.group(1)) + int(h.group(2) or 1) - 1)
        elif linha.startswith(("+", " ")) and not linha.startswith("+++"):
            visiveis.append(linha[1:])
    return minimo, "\n".join(visiveis)

def checar(nome, entrada, resposta):
    if nome.endswith(("insert_cell", "insert_execute_code_cell")):
        tipo = entrada.get("cell_type", "code")
        return problemas(tipo, entrada.get("cell_source", ""))
    if nome.endswith("overwrite_cell_source"):
        fonte = entrada.get("cell_source", "")
        return problemas("code" if parece_codigo(fonte) else "markdown", fonte)
    if nome.endswith("edit_cell_source"):
        minimo, visivel = analisar_diff(resposta)
        if parece_codigo(visivel):
            return [f"{minimo} linhas de código — a regra é ~5-8 (máximo {MAX_LINHAS}); "
                    "quebre em células menores"] if minimo > MAX_LINHAS else []
        return problemas_markdown(entrada.get("new_string", ""))
    return []

def main():
    try:
        evento = json.load(sys.stdin)
    except ValueError:
        return 0
    nome = evento.get("tool_name", "")
    entrada = evento.get("tool_input") or {}
    achados = checar(nome, entrada, evento.get("tool_response"))
    if not achados:
        return 0
    indice = entrada.get("cell_index", entrada.get("cell_id", "?"))
    onde = "a célula inserida no fim" if indice == -1 else f"a célula {indice}"
    print(f"Regra de casa (hook do plugin analise-dados) — {onde} acabou de ser "
          "gravada com problema:\n" + "\n".join(f"- {a}" for a in achados) +
          "\nCorrija esta célula pelo Jupyter MCP antes de seguir.", file=sys.stderr)
    return 2

if __name__ == "__main__":
    sys.exit(main())
