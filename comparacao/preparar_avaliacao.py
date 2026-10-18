#!/usr/bin/env python3
"""
preparar_avaliacao.py — prepara a avaliação cega de dois notebooks.

    uv run --no-project --python <venv> comparacao/preparar_avaliacao.py SEM.ipynb COM.ipynb PASTA [semente]

Escreve em PASTA os arquivos A.md e B.md (cada notebook em texto: markdown,
código e resultados; gráficos viram "[gráfico]") e, ao lado da pasta,
PASTA-mapa.json, que diz qual é qual. A ordem é sorteada para o avaliador não
inferir pela posição.
"""
import json, random, sys
from pathlib import Path
import nbformat

LIMITE_SAIDA = 1500  # caracteres por resultado, para não afogar o avaliador

def em_texto(caminho):
    nb = nbformat.read(caminho, as_version=4)
    partes = []
    for i, c in enumerate(nb.cells):
        if c.cell_type == "markdown":
            partes.append(f"<!-- célula {i} · texto -->\n{c.source}")
            continue
        if c.cell_type != "code":
            continue
        partes.append(f"<!-- célula {i} · código -->\n```python\n{c.source}\n```")
        for o in c.get("outputs", []):
            dados = o.get("data", {})
            if any(k.startswith("image/") for k in dados):
                partes.append("[gráfico]")
            elif "text/plain" in dados or o.get("output_type") == "stream":
                texto = dados.get("text/plain", o.get("text", ""))
                partes.append(f"```\n{texto[:LIMITE_SAIDA]}\n```")
            elif o.get("output_type") == "error":
                partes.append(f"```\nERRO: {o.get('ename')}: {o.get('evalue')}\n```")
    return "\n\n".join(partes)

def main():
    sem, com, pasta = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    semente = int(sys.argv[4]) if len(sys.argv) > 4 else 2025
    pasta.mkdir(parents=True, exist_ok=True)
    ordem = [("sem_plugin", sem), ("com_plugin", com)]
    random.Random(semente).shuffle(ordem)
    mapa = {}
    for rotulo, (nome, caminho) in zip("AB", ordem):
        (pasta / f"{rotulo}.md").write_text(em_texto(caminho), encoding="utf-8")
        mapa[rotulo] = nome
    # o mapa fica FORA da pasta do avaliador, para ele não descobrir qual é qual
    (pasta.parent / f"{pasta.name}-mapa.json").write_text(json.dumps(mapa, indent=2), encoding="utf-8")
    print(f"A.md e B.md prontos em {pasta} (semente {semente}); mapa em {pasta.name}-mapa.json")

if __name__ == "__main__":
    main()
