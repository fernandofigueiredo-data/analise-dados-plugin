#!/usr/bin/env python3
"""
validar.py — o "Restart & Run All" de verdade, fora do kernel ao vivo.

    uv run --no-project --python .venv <plugin>/scripts/validar.py [analise.ipynb]

Roda o notebook de cima a baixo num kernel NOVO (o do .venv), sem tocar no
notebook aberto no navegador, e grava a cópia executada em saidas/validacao/.
Depois confere as regras de casa (REGRAS.md) e lista avisos.

Saída: 0 = rodou inteiro · 1 = alguma célula deu erro · 2 = notebook não encontrado.
"""
import os, re, subprocess, sys
from pathlib import Path
from _jupyter import PROJ, jupyter_env
from regras import (linhas_de_codigo, problemas_codigo, problemas_markdown, meses_sem_ajuste_por_dia,
                    tabela_taxa_sem_n, MSG_MESES, MSG_TAXA_SEM_N)

os.environ.update(jupyter_env())  # kernel do .venv, antes de importar o Jupyter

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError, DeadKernelError

SAIDA = PROJ / "saidas" / "validacao"
MAX_LINHAS_TEXTO = 40    # output de texto maior que isso é dump
MAX_LINHAS_TABELA = 30   # idem para tabela HTML (linhas <tr>)
MAX_RESULTADOS_SEGUIDOS = 4  # células com output sem markdown no meio = sem interpretação?

def resolver(arg):
    p = Path(arg) if arg else PROJ / "analise.ipynb"
    return (p if p.is_absolute() else Path.cwd() / p).resolve()

def primeira_linha(cell):
    for linha in cell.source.splitlines():
        if linha.strip() and not linha.lstrip().startswith("#|"):
            return linha.strip()[:70]
    return "(vazia)"

def executar(caminho):
    """Roda num kernel novo. Retorna (notebook executado, índice da célula com erro, mensagem)."""
    nb = nbformat.read(caminho, as_version=4)
    client = NotebookClient(nb, timeout=600, kernel_name="python3",
                            resources={"metadata": {"path": str(caminho.parent)}})
    erro, msg = None, ""
    try:
        client.execute(stderr=subprocess.DEVNULL)  # sem o ruído de log do processo do kernel
    except (CellExecutionError, DeadKernelError) as e:
        erro, msg = -1, str(e).strip().splitlines()[-1] if str(e).strip() else type(e).__name__
        for i, c in enumerate(nb.cells):
            if c.cell_type == "code" and any(o.output_type == "error" for o in c.get("outputs", [])):
                erro = i
                break
    SAIDA.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, SAIDA / f"{caminho.stem}.executado.ipynb")
    return nb, erro, msg

def avisos_output(o):
    data = o.get("data", {})
    if o.output_type == "stream" and o.get("name") == "stderr":
        # Só avisos de verdade (UserWarning, FutureWarning…) e erros. Recados
        # informativos de pacotes no stderr — "Matplotlib is building the font
        # cache" numa máquina nova, barras de progresso — não indicam problema.
        m = re.search(r"(\w+(?:Warning|Error)): (.+)", o.text)
        return [f"emitiu um aviso do Python — {m.group(1)}: {m.group(2)[:80]}"] if m else []
    if "text/html" in data:
        html = data["text/html"]
        linhas = html.count("<tr")
        av = [f"tabela com ~{linhas} linhas no output — mostre .head() ou um top N"] \
            if linhas > MAX_LINHAS_TABELA else []
        return av + ([MSG_TAXA_SEM_N] if tabela_taxa_sem_n(html) else [])
    texto = o.get("text", "") if o.output_type == "stream" else data.get("text/plain", "")
    av = []
    if texto.count("\n") > MAX_LINHAS_TEXTO:
        av.append(f"output de texto com {texto.count(chr(10))} linhas — parece um dump")
    if o.output_type != "stream" and re.search(r"dtype: \w+\s*$", texto):
        av.append("o output é uma Series crua — envolva com .to_frame() para exibir")
    return av

def avisos(nb):
    """Desvios das regras de casa (REGRAS.md). Não impedem a validação."""
    av, seguidos = [], 0
    for i, c in enumerate(nb.cells):
        if c.cell_type == "markdown":
            seguidos = 0
            av += [(i, m) for m in problemas_markdown(c.source)]
            continue
        if c.cell_type != "code":
            continue
        if not linhas_de_codigo(c.source):
            av.append((i, "célula de código vazia"))
            continue
        av += [(i, m) for m in problemas_codigo(c.source)]
        outputs = c.get("outputs", [])
        if outputs:
            seguidos += 1
            if seguidos == MAX_RESULTADOS_SEGUIDOS:
                av.append((i, f"{seguidos} resultados seguidos sem markdown — falta pergunta ou interpretação?"))
        for o in outputs:
            av += [(i, m) for m in avisos_output(o)]
    codigo = [(i, c.source) for i, c in enumerate(nb.cells) if c.cell_type == "code"]
    textos = [c.source for c in nb.cells if c.cell_type == "markdown"]
    sem_ajuste = meses_sem_ajuste_por_dia([s for _, s in codigo], textos)
    if sem_ajuste is not None:
        av.append((codigo[sem_ajuste][0], MSG_MESES))
    if nb.cells and nb.cells[-1].cell_type != "markdown":
        av.append((len(nb.cells) - 1, "o notebook não termina com uma conclusão em markdown"))
    return list(dict.fromkeys(av))  # a mesma célula pode repetir a tabela em dois outputs

def main():
    caminho = resolver(sys.argv[1] if len(sys.argv) > 1 else None)
    if not caminho.exists():
        print(f"❌ Notebook não encontrado: {caminho}")
        sys.exit(2)
    print(f"🧪 Rodando {caminho.name} do zero, num kernel novo (o notebook ao vivo não é tocado)...")
    nb, erro, msg = executar(caminho)
    codigo = sum(c.cell_type == "code" for c in nb.cells)

    if erro is None:
        print(f"✅ Rodou de cima a baixo: {codigo} células de código, nenhum erro.")
    elif erro < 0:
        print(f"❌ A execução parou: {msg}")
    else:
        e = next(o for o in nb.cells[erro].outputs if o.output_type == "error")
        tb = re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(e.traceback)).strip().splitlines()
        print(f"❌ Parou na célula {erro}: {primeira_linha(nb.cells[erro])}")
        print(f"   {e.ename}: {e.evalue}")
        print("   Final do traceback:\n      " + "\n      ".join(tb[-6:]))

    av = avisos(nb)
    if av:
        print(f"\n⚠️  {len(av)} aviso(s) das regras de casa (índices começam em 0, como no Jupyter MCP):")
        for i, m in av:
            print(f"   [célula {i}] {m}")
    else:
        print("✅ Nenhum desvio das regras de casa encontrado.")
    print(f"\nCópia executada: {(SAIDA / (caminho.stem + '.executado.ipynb')).relative_to(PROJ)}")
    sys.exit(0 if erro is None else 1)

if __name__ == "__main__":
    main()
