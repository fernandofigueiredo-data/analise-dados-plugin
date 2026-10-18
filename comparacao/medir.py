#!/usr/bin/env python3
"""
medir.py — métricas objetivas de um notebook de análise (comparação com e sem o plugin).

    cd <projeto> && uv run --no-project --python .venv <repo>/comparacao/medir.py analise.ipynb [sessao.json]

Roda o notebook do zero num kernel novo (mesma execução do /validar) e mede a
forma do notebook. `sessao.json` é a saída de `claude -p --output-format json`,
para tempo, custo e turnos. Imprime um JSON com as métricas.
"""
import json, re, statistics, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugins" / "analise-dados" / "scripts"))
from validar import executar, avisos  # noqa: E402
from regras import linhas_de_codigo, MAX_LINHAS, problemas_markdown  # noqa: E402

# Termos que a diretoria comercial (o público declarado no prompt) não usa
JARGAO = ["univariad", "bivariad", "multivariad", "outlier", "dtype", "dataframe", r"\bnan\b",
          "groupby", "agregaç", "p-valor", "quartil", "boxplot", "desvio padrão", "kde",
          "correlaç", "estatisticamente", r"\beda\b", "feature"]

def medir(caminho, sessao=None):
    nb, erro, _ = executar(Path(caminho).resolve())
    codigo = [c for c in nb.cells if c.cell_type == "code"]
    md = [c for c in nb.cells if c.cell_type == "markdown"]
    linhas = [len(linhas_de_codigo(c.source)) for c in codigo] or [0]
    # blocos = sequências de células de código consecutivas; um bloco com resultado
    # conta como interpretado quando o texto vem logo depois dele
    blocos, atual = [], []
    for i, c in enumerate(nb.cells + [None]):
        if c is not None and c.cell_type == "code":
            atual.append(i)
        elif atual:
            blocos.append(atual); atual = []
    com_saida = [b for b in blocos if any(nb.cells[i].get("outputs") for i in b)]
    interpretadas = sum(1 for b in com_saida if b[-1] + 1 < len(nb.cells))
    texto_md = "\n".join(c.source for c in md).lower()
    ultima = nb.cells[-1] if nb.cells else None
    m = {
        "roda_do_zero": erro is None,
        "celulas_codigo": len(codigo),
        "celulas_markdown": len(md),
        "linhas_por_celula_media": round(statistics.mean(linhas), 1),
        "linhas_por_celula_max": max(linhas),
        "celulas_acima_de_10_linhas": sum(1 for n in linhas if n > MAX_LINHAS),
        "blocos_de_resultado_seguidos_de_texto_pct": round(100 * interpretadas / len(com_saida)) if com_saida else 0,
        "markdown_com_cifrao_sem_escape": sum(1 for c in md if problemas_markdown(c.source)),
        "termos_de_jargao": sum(len(re.findall(t, texto_md)) for t in JARGAO),
        "termina_com_conclusao": bool(ultima is not None and ultima.cell_type == "markdown"
                                      and "conclus" in ultima.source.lower()),
        "avisos_das_regras_de_casa": len(avisos(nb)),
    }
    if sessao and Path(sessao).exists():
        s = json.loads(Path(sessao).read_text(encoding="utf-8"))
        m.update({"tempo_min": round(s.get("duration_ms", 0) / 60000, 1),
                  "custo_usd": round(s.get("total_cost_usd", 0), 2),
                  "turnos": s.get("num_turns")})
    return m

if __name__ == "__main__":
    print(json.dumps(medir(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None),
                     ensure_ascii=False, indent=2))
