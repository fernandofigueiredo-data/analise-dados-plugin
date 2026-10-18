"""
analise_dados.painel — painel interativo em HTML a partir das conclusões.

    from analise_dados import painel
    painel.tema()                                    # gráficos Plotly com o design system
    p = painel.Painel("Vendas 2025", "O que mudou no ano", fonte="dados/vendas.csv")
    p.kpi("Faturamento no ano", "R$ 23,9 mi", "5.000 vendas", destaque=True)
    p.grafico(fig, "O Sudeste concentra 41% do faturamento", "Texto curto do achado.")
    p.conclusoes(["Primeira conclusão.", "Segunda conclusão."])
    p.salvar()                                       # saidas/painel.html

Um arquivo só, que abre offline (o Plotly vai embutido). Cada gráfico tem
tooltip e uma tabela "Ver os números" — o valor nunca depende só da cor ou do
mouse. As cores vêm do estilos/design-system.md do projeto.
"""
import datetime, html, re
from pathlib import Path

# Tokens da página (fundo claro: o painel é um documento, como o relatório)
SUPERFICIE, CARTAO, TINTA, TINTA_2, APAGADO, LINHA = (
    "#fcfcfb", "#ffffff", "#0b0b0b", "#52514e", "#8a8880", "#e7e6e2")
PALETA_PADRAO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]
FONTE = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

def paleta(design_system="estilos/design-system.md"):
    """Paleta categórica do design system do projeto (ordem fixa), ou a padrão."""
    arq = Path(design_system)
    if arq.exists():
        for linha in arq.read_text(encoding="utf-8").splitlines():
            cores = re.findall(r"#[0-9A-Fa-f]{6}\b", linha)
            if len(cores) >= 4:  # a linha da paleta categórica
                return cores
    return PALETA_PADRAO

def tema():
    """Registra e ativa o tema 'analise' do Plotly: marcas finas, grade discreta,
    cores do design system em ordem fixa."""
    import plotly.graph_objects as go
    import plotly.io as pio
    eixo = dict(gridcolor=LINHA, linecolor=LINHA, zeroline=False, ticks="", automargin=True,
                title_font=dict(color=TINTA_2, size=12), tickfont=dict(color=TINTA_2, size=12))
    pio.templates["analise"] = go.layout.Template(
        layout=dict(
            font=dict(family=FONTE, color=TINTA_2, size=13),
            title=dict(font=dict(color=TINTA, size=15)),
            paper_bgcolor=CARTAO, plot_bgcolor=CARTAO, colorway=paleta(),
            separators=",.",  # decimal com vírgula, milhar com ponto
            xaxis=eixo, yaxis=eixo, bargap=0.3, barcornerradius=4,
            legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title_text=""),
            hoverlabel=dict(bgcolor=CARTAO, bordercolor=LINHA, font=dict(color=TINTA, family=FONTE)),
            margin=dict(l=8, r=8, t=40, b=8),
        ),
        data=dict(scatter=[go.Scatter(line=dict(width=2), marker=dict(size=8))]),
    )
    pio.templates.default = "analise"
    return "analise"

def compacto(v, prefixo=""):
    """Número curto para KPI: 25016139 → '25,0 mi'; compacto(v, 'R$ ') → 'R$ 25,0 mi'."""
    for limite, sufixo in ((1e9, " bi"), (1e6, " mi"), (1e3, " mil")):
        if abs(v) >= limite:
            return f"{prefixo}{v / limite:.1f}".replace(".", ",") + sufixo
    return f"{prefixo}{v:.0f}"

def _numero(v):
    """1234567.8 → 1.234.567,8 e 2025-01-31 → 31/01/2025 (só para a tabela de apoio)."""
    data = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(v))
    if data:
        return f"{data.group(3)}/{data.group(2)}/{data.group(1)}"
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return str(v)
    txt = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return txt[:-3] if txt.endswith(",00") else txt

def _texto(t):
    """Escapa HTML e aceita **negrito**, como no markdown das células."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(t))

def _tem_datas(fig):
    """O eixo x de algum traço é de datas?"""
    import pandas as pd
    for tr in fig.data:
        x = getattr(tr, "x", None)
        if x is not None and len(x):
            try:
                return pd.api.types.is_datetime64_any_dtype(pd.Series(list(x)).infer_objects()) or \
                    bool(re.match(r"^\d{4}-\d{2}-\d{2}", str(x[0])))
            except Exception:
                return False
    return False

def _tabela(fig):
    """Tabela com os valores de cada série do gráfico (a visão sem cor e sem mouse)."""
    linhas, cab = [], None
    for tr in fig.data:
        x, y = getattr(tr, "x", None), getattr(tr, "y", None)
        if x is None or y is None:
            continue
        cat, val = (y, x) if getattr(tr, "orientation", None) == "h" else (x, y)
        nome = tr.name or ""
        eixo_cat = fig.layout.yaxis if getattr(tr, "orientation", None) == "h" else fig.layout.xaxis
        cab = cab or [eixo_cat.title.text or "Categoria", "Série", "Valor"]
        linhas += [(c, nome, v) for c, v in zip(cat, val)]
    if not linhas:
        return ""
    mostrar_serie = len({l[1] for l in linhas}) > 1
    th = "".join(f"<th>{html.escape(str(h))}</th>" for i, h in enumerate(cab) if mostrar_serie or i != 1)
    tds = "".join("<tr>" + "".join(f"<td>{html.escape(_numero(v))}</td>"
                                   for i, v in enumerate(l) if mostrar_serie or i != 1) + "</tr>"
                  for l in linhas)
    return f"<details><summary>Ver os números</summary><table><tr>{th}</tr>{tds}</table></details>"

CSS = f"""
:root {{ color-scheme: light; --superficie:{SUPERFICIE}; --cartao:{CARTAO}; --tinta:{TINTA};
  --tinta-2:{TINTA_2}; --apagado:{APAGADO}; --linha:{LINHA}; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--superficie); color:var(--tinta); font-family:{FONTE}; line-height:1.5; }}
main {{ max-width:1180px; margin:0 auto; padding:32px 16px 48px; }}
header h1 {{ font-size:28px; margin:0 0 4px; }}
header .sub {{ font-size:17px; color:var(--tinta-2); margin:0; }}
header .meta {{ font-size:13px; color:var(--apagado); margin:8px 0 0; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); gap:12px; margin:28px 0; }}
.kpi {{ background:var(--cartao); border:1px solid var(--linha); border-radius:10px; padding:16px; }}
.kpi .rotulo {{ display:block; font-size:13px; color:var(--tinta-2); }}
.kpi .valor {{ display:block; font-size:28px; font-weight:600; margin:2px 0; }}
.kpi.destaque .valor {{ font-size:48px; line-height:1.1; }}
.kpi .detalhe {{ display:block; font-size:13px; color:var(--apagado); }}
.graficos {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 480px), 1fr)); gap:16px; }}
.card {{ background:var(--cartao); border:1px solid var(--linha); border-radius:10px; padding:16px; min-width:0; }}
.card h2 {{ font-size:17px; margin:0 0 4px; }}
.card p {{ font-size:14px; color:var(--tinta-2); margin:0 0 8px; }}
details {{ margin-top:8px; font-size:13px; }}
summary {{ cursor:pointer; color:var(--tinta-2); }}
table {{ border-collapse:collapse; width:100%; margin-top:8px; font-variant-numeric:tabular-nums; }}
th, td {{ text-align:left; padding:4px 8px; border-bottom:1px solid var(--linha); }}
td:last-child, th:last-child {{ text-align:right; }}
.conclusoes {{ background:var(--cartao); border:1px solid var(--linha); border-radius:10px;
  padding:16px 20px; margin-top:16px; }}
.conclusoes h2 {{ font-size:17px; margin:0 0 8px; }}
.conclusoes li {{ margin:4px 0; }}
footer {{ margin-top:24px; font-size:12px; color:var(--apagado); }}
"""

# Cada gráfico acompanha a largura real do seu card (grade responsiva, celular)
AJUSTE_LARGURA = """
const graficos = document.querySelectorAll('.card .js-plotly-plot');
const ajustar = g => Plotly.Plots.resize(g);
const obs = new ResizeObserver(es => es.forEach(e => ajustar(e.target)));
graficos.forEach(g => { obs.observe(g.parentElement); ajustar(g); });
"""

class Painel:
    def __init__(self, titulo, subtitulo="", fonte=""):
        self.titulo, self.subtitulo, self.fonte = titulo, subtitulo, fonte
        self._kpis, self._graficos, self._conclusoes = [], [], []

    def kpi(self, rotulo, valor, detalhe="", destaque=False):
        """Um número em destaque. `valor` já formatado (ex.: com o helper reais).
        Use destaque=True em um só: o número que o painel inteiro sustenta."""
        self._kpis.append((rotulo, str(valor), detalhe, destaque))
        return self

    def grafico(self, fig, titulo, texto=""):
        """Um gráfico Plotly. `titulo` diz o achado (passado pela revisão crítica)."""
        self._graficos.append((fig, titulo, texto))
        return self

    def conclusoes(self, itens):
        self._conclusoes = list(itens)
        return self

    def __repr__(self):
        return (f"Painel '{self.titulo}': {len(self._kpis)} KPIs, "
                f"{len(self._graficos)} gráficos, {len(self._conclusoes)} conclusões")

    def _cartao(self, original, titulo, texto):
        import plotly.graph_objects as go
        tabela = _tabela(original)  # da figura original: na cópia os dados viram binário
        fig = go.Figure(original)
        fig.update_layout(title=None, height=360, autosize=True, margin=dict(t=30))
        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)
        if _tem_datas(fig):  # o Plotly escreve os meses em inglês; número não tem idioma
            fig.update_xaxes(tickformat="%m/%Y", hoverformat="%d/%m/%Y")
        corpo = fig.to_html(full_html=False, include_plotlyjs=False,
                            config={"displayModeBar": False, "responsive": True})
        return (f'<article class="card"><h2>{_texto(titulo)}</h2>'
                + (f"<p>{_texto(texto)}</p>" if texto else "") + corpo + tabela + "</article>")

    def html(self):
        from plotly.offline import get_plotlyjs
        hoje = datetime.date.today().strftime("%d/%m/%Y")
        meta = f"Atualizado em {hoje}" + (f" · Fonte: {html.escape(self.fonte)}" if self.fonte else "")
        kpis = "".join(
            f'<div class="kpi{" destaque" if d else ""}"><span class="rotulo">{_texto(r)}</span>'
            f'<span class="valor">{html.escape(v)}</span>'
            + (f'<span class="detalhe">{_texto(det)}</span>' if det else "") + "</div>"
            for r, v, det, d in self._kpis)
        graficos = "".join(self._cartao(*g) for g in self._graficos)
        concl = ("<section class=\"conclusoes\"><h2>Conclusões</h2><ul>"
                 + "".join(f"<li>{_texto(c)}</li>" for c in self._conclusoes) + "</ul></section>"
                 if self._conclusoes else "")
        return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                f"<title>{html.escape(self.titulo)}</title><style>{CSS}</style>"
                f"<script>{get_plotlyjs()}</script></head><body><main>"
                f"<header><h1>{html.escape(self.titulo)}</h1>"
                + (f'<p class="sub">{_texto(self.subtitulo)}</p>' if self.subtitulo else "")
                + f'<p class="meta">{meta}</p></header>'
                + (f'<section class="kpis">{kpis}</section>' if kpis else "")
                + f'<section class="graficos">{graficos}</section>{concl}'
                + "<footer>Painel gerado com o plugin analise-dados.</footer></main>"
                + f"<script>{AJUSTE_LARGURA}</script></body></html>")

    def salvar(self, caminho="saidas/painel.html"):
        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(self.html(), encoding="utf-8")
        return destino
