#!/usr/bin/env python3
"""
relatorio.py — transforma o notebook num relatório HTML para quem é de negócio.

    uv run --no-project --python .venv <plugin>/scripts/relatorio.py [analise.ipynb]

Antes de exportar, roda o notebook do zero (a mesma execução do validar.py):
relatório só sai de notebook que funciona de cima a baixo.

O que entra no HTML: os textos (markdown) e os gráficos. O código nunca aparece.
Tabelas e textos de saída ficam de fora, a não ser que a célula tenha, numa
linha própria, uma destas marcações:

    #| relatorio: mostrar     → mostra a saída desta célula (ex.: tabela-resposta)
    #| relatorio: ocultar     → tira a célula inteira (ex.: gráfico auxiliar)

Saída: saidas/relatorio-<notebook>.html (para PDF: abrir no navegador → Imprimir).
"""
import re, sys, datetime
from validar import PROJ, resolver, executar, primeira_linha
import nbformat
from nbconvert import HTMLExporter

MARCA = re.compile(r"^\s*#\|\s*relatorio:\s*(mostrar|ocultar)\s*$", re.M)
IMAGENS = ("image/png", "image/svg+xml", "image/jpeg")
CSS = "<style>body{max-width:960px;margin:0 auto;padding:24px 16px}</style>"

def tem_imagem(o):
    return any(k in o.get("data", {}) for k in IMAGENS)

def opcao(c):
    m = MARCA.search(c.source)
    return m.group(1) if m else None

def filtrar(nb):
    """Fica com markdown, gráficos e as saídas marcadas com `mostrar`."""
    celulas = []
    for c in nb.cells:
        if c.cell_type == "markdown":
            celulas.append(c)
            continue
        if c.cell_type != "code":
            continue
        if opcao(c) == "ocultar":
            continue
        outs = [o for o in c.get("outputs", [])
                if not (o.output_type == "stream" and o.get("name") == "stderr")]
        if opcao(c) != "mostrar":
            outs = [o for o in outs if tem_imagem(o)]
        if outs:
            c.outputs = outs
            celulas.append(c)
    nb.cells = sem_titulos_vazios(celulas)
    return nb

def nivel_titulo(c):
    """Nível do título (1 = #) se a célula markdown for só título; senão None."""
    linhas = [l for l in c.source.splitlines() if l.strip()] if c.cell_type == "markdown" else []
    if linhas and all(l.lstrip().startswith("#") for l in linhas):
        return len(linhas[0].lstrip()) - len(linhas[0].lstrip().lstrip("#"))
    return None

def sem_titulos_vazios(celulas):
    """Tira seções que ficaram sem conteúdo depois do filtro (ex.: 'Como são os dados?')."""
    final = []
    for i, c in enumerate(celulas):
        nivel = nivel_titulo(c)
        if nivel and nivel > 1:
            prox = celulas[i + 1] if i + 1 < len(celulas) else None
            prox_nivel = nivel_titulo(prox) if prox is not None else 0
            if prox is None or (prox_nivel and prox_nivel <= nivel):
                continue
        final.append(c)
    return final

def titulo(nb, padrao):
    for c in nb.cells:
        if c.cell_type == "markdown":
            m = re.search(r"^#\s+(.+)$", c.source, re.M)
            if m:
                return m.group(1).strip()
    return padrao

def carimbo(nb, nome):
    """Linha 'gerado em' logo abaixo do título (ou no topo, se não houver título)."""
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    cel = nbformat.v4.new_markdown_cell(f"*Relatório gerado em {hoje} a partir de `{nome}`.*")
    primeira = nb.cells[0] if nb.cells else None
    pos = 1 if primeira is not None and primeira.cell_type == "markdown" \
        and primeira.source.lstrip().startswith("# ") else 0
    nb.cells.insert(pos, cel)

def main():
    caminho = resolver(sys.argv[1] if len(sys.argv) > 1 else None)
    if not caminho.exists():
        print(f"❌ Notebook não encontrado: {caminho}")
        sys.exit(2)
    print(f"📄 Rodando {caminho.name} do zero antes de exportar...")
    nb, erro, msg = executar(caminho)
    if erro is not None:
        onde = f"célula {erro}: {primeira_linha(nb.cells[erro])}" if erro >= 0 else msg
        print(f"❌ O notebook não roda de cima a baixo ({onde}).")
        print("   Rode /validar, corrija e gere o relatório de novo.")
        sys.exit(1)
    if nb.cells and nb.cells[-1].cell_type != "markdown":
        print("⚠️  O notebook não termina com uma conclusão em markdown — o relatório fica sem fecho.")

    nb = filtrar(nb)
    textos = sum(c.cell_type == "markdown" for c in nb.cells)
    graficos = sum(tem_imagem(o) for c in nb.cells if c.cell_type == "code" for o in c.outputs)
    marcadas = sum(c.cell_type == "code" and opcao(c) == "mostrar" for c in nb.cells)
    carimbo(nb, caminho.name)

    exportador = HTMLExporter(template_name="lab", exclude_input=True,
                              exclude_input_prompt=True, exclude_output_prompt=True)
    html, _ = exportador.from_notebook_node(
        nb, resources={"metadata": {"name": titulo(nb, caminho.stem)}})
    html = html.replace("</head>", CSS + "</head>", 1)

    destino = PROJ / "saidas" / f"relatorio-{caminho.stem}.html"
    destino.write_text(html, encoding="utf-8")
    print(f"✅ Relatório pronto: {destino.relative_to(PROJ)}")
    print(f"   blocos de texto: {textos} · gráficos: {graficos} · saídas marcadas com `mostrar`: {marcadas}")

if __name__ == "__main__":
    main()
