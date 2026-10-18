---
description: Monta um painel interativo (HTML com Plotly) a partir das conclusões da análise
argument-hint: "[notebook da análise — padrão: analise.ipynb]"
---

Monte o painel final da análise: uma página HTML interativa, que abre offline,
para quem decide. O painel **mostra as conclusões** que a análise já sustenta —
não é lugar de achado novo.

O aluno passou isto junto do comando (pode estar vazio): `$ARGUMENTS`

## Passo 1 — A análise está pronta?

Leia o notebook (`$ARGUMENTS`, ou `analise.ipynb`) pelo Jupyter MCP e o
`contexto.md`. Confira:

- tem **conclusão** no fim — o painel nasce dela;
- passou pelo `/revisar` — se não, sugira rodar antes: painel espalha a
  conclusão, então ela precisa estar firme;
- **grava os dados tratados**: uma célula logo depois do tratamento salva
  `df.to_parquet("saidas/dados_tratados.parquet")`. Se não existir, insira-a
  pelo Jupyter MCP (seguindo as regras de casa), execute, e conte ao aluno.

## Passo 2 — Propor o painel (e esperar o ok)

Com base na conclusão e no público do `contexto.md`, proponha em poucas linhas:

- **3 a 5 KPIs** — números que a conclusão cita. Um só é o destaque (o número
  que o painel inteiro sustenta).
- **2 a 4 gráficos**, um por achado da conclusão. Para cada um: o tipo (skill
  `graficos`) e o **título que diz o achado**, já passado pela `revisao-critica`
  (sem afirmar causa, sem chamar pico sazonal de tendência).
- As **conclusões** em 2 a 4 frases curtas.

Espere o aluno aprovar ou ajustar.

## Passo 3 — Construir em `painel.ipynb`

Crie `painel.ipynb` pelo Jupyter MCP, com o mesmo ciclo e as mesmas regras de
casa (células curtas, uma coisa por célula, executa e confere cada uma):

1. Imports e tema: `import pandas as pd`, `import plotly.express as px`,
   `from analise_dados import painel`, `painel.tema()`.
2. Carregar `saidas/dados_tratados.parquet`.
3. Uma célula por KPI calculado (mostre o número; formate em reais com o
   helper `reais` da skill `analista-senior`).
4. Uma célula por gráfico (`px.bar`, `px.line`…), exibindo a figura para
   conferir. Regras da skill `graficos`: barra horizontal ordenada para
   ranking; destaque **um** elemento com a cor primária e o resto neutro
   (`#94A3B8`); rótulo direto só no ponto que importa; nunca dois eixos y.
5. Montar e salvar, numa célula curta:

   ```python
   p = painel.Painel("Título", "Subtítulo: a pergunta de negócio", fonte="dados/…")
   p.kpi("Faturamento no ano", reais(total), "5.000 vendas", destaque=True)
   p.grafico(fig_regioes, "O Sudeste concentra 41% do faturamento", "Frase de apoio.")
   p.conclusoes(["…", "…"])
   p.salvar("saidas/painel.html")
   ```

   Se a célula passar de ~8 linhas, monte o painel em duas ou três células
   (`p.kpi(...)` numa, `p.grafico(...)` noutra).

## Passo 4 — Validar e entregar

1. Rode o `/validar` em `painel.ipynb` — o painel precisa ser refeito do zero
   sempre que os dados mudarem.
2. Entregue o caminho `saidas/painel.html`: um arquivo só, abre no navegador
   sem internet, com tooltip em cada gráfico e a tabela "Ver os números" (o
   valor nunca depende só da cor ou do mouse).
3. Registre no **Histórico** do `contexto.md` que o painel foi gerado.
