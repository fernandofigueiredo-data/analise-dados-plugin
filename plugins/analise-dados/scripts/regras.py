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


# ---- Regras da revisão crítica que dá para checar no notebook inteiro (/validar) ----
# Antes dependiam só de o modelo seguir a skill revisao-critica; na comparação
# com e sem o plugin, as duas passaram despercebidas.

_AGRUPA = re.compile(r"groupby|pivot_table|resample|Grouper|crosstab")
_MENSAL = re.compile(r"""["']m[eê]s["']|\.month\b|to_period\(\s*["']M|freq\s*=\s*["']M|resample\(\s*["']M""")
_SOMA = re.compile(r"""\.sum\(|\.size\(|\.count\(|aggfunc\s*=\s*["'](?:sum|count|size)|["']sum["']|np\.sum""")
_POR_DIA_CODIGO = re.compile(r"""days_in_month|daysinmonth|por[ _]dia|resample\(\s*["']D["']""")
_POR_DIA_TEXTO = re.compile(r"por dia|dias (?:do|de cada) m[eê]s|tamanhos? diferentes", re.I)

def agrupa_mes_somando(fonte):
    """A célula soma (ou conta) por mês? Média por mês não precisa de ajuste."""
    return bool(_AGRUPA.search(fonte) and _MENSAL.search(fonte) and _SOMA.search(fonte))

def meses_sem_ajuste_por_dia(codigos, textos):
    """Índice (na lista `codigos`) da 1ª célula que soma por mês, se o notebook
    em nenhum momento ajusta pelos dias do mês nem explica por que não precisa."""
    if any(_POR_DIA_CODIGO.search(c) for c in codigos) or any(_POR_DIA_TEXTO.search(t) for t in textos):
        return None
    return next((i for i, c in enumerate(codigos) if agrupa_mes_somando(c)), None)

MSG_MESES = ("soma por mês sem ajustar pelos dias — meses têm tamanhos diferentes (fevereiro tem 28); "
             "compare por dia (`/ index.days_in_month`) ou explique no texto por que não muda a conclusão")

_TAXA = re.compile(r"%|pct|percent|taxa|share|particip|margem|m[eé]dia|ticket|propor|fatia", re.I)
_CONTAGEM = re.compile(r"^(?:n|n[ºo°]?\b.*|n_.*|qtd.*|quantidade.*|vendas|pedidos|registros|linhas|count|"
                       r"contagem|clientes|casos|ocorr[eê]ncias|transa[cç][oõ]es|n[uú]mero de .*|total de .*)$", re.I)

def cabecalhos(html):
    """Textos dos <th> do cabeçalho de uma tabela HTML do pandas."""
    cab = html.split("</thead>")[0] if "</thead>" in html else ""
    textos = (re.sub(r"<[^>]+>", "", t).replace("&nbsp;", " ").strip()
              for t in re.findall(r"<th[^>]*>(.*?)</th>", cab, re.S))
    return [t for t in textos if t]

def tabela_taxa_sem_n(html):
    """Tabela com taxa, média ou percentual, mas sem nenhuma coluna de contagem."""
    cab = cabecalhos(html)
    return any(_TAXA.search(c) for c in cab) and not any(_CONTAGEM.match(c) for c in cab)

MSG_TAXA_SEM_N = ("tabela com taxa, média ou percentual sem a contagem ao lado — inclua o nº de "
                  "vendas/casos (n) na mesma tabela: taxa sobre base pequena não é achado")
