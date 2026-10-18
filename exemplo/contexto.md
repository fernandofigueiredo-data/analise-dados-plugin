# Contexto da análise

## Objetivo
- **Pergunta de negócio:** onde está o faturamento de 2025 — por região, mês e canal?
- **Quem lê o resultado:** diretoria comercial.
- **Decisão que a análise apoia:** onde concentrar esforço comercial em 2026.

## Dados

### vendas.csv
- **O que é:** uma linha por venda · **Período:** 01/01/2025 a 31/12/2025 · **Linhas:** 5.000
- **Como ler:** `sep=","`, `encoding="utf-8"`, `parse_dates=["data"]`

| Coluna | Significado | Unidade / formato | Observações |
|---|---|---|---|
| data | dia da venda | data | |
| produto | produto vendido | texto | 12 produtos |
| categoria | grupo do produto | texto | Acessórios, Eletrônicos, Móveis |
| regiao | região do cliente | texto | 154 vendas sem região |
| quantidade | unidades na venda | inteiro | de 1 a 10 |
| preco_unitario | preço de cada unidade | reais | |
| custo_unitario | custo de cada unidade | reais | |
| canal_venda | onde a venda aconteceu | texto | Online, Loja física, Marketplace |

## Decisões de tratamento
- 2026-10-18 — 154 vendas sem região mantidas como "Não informada" (apagar tiraria quase 3% do faturamento dos totais).
- 2026-10-18 — criadas `faturamento` (quantidade × preço) e `lucro` (quantidade × (preço − custo)).

## Histórico
- 2026-10-18 — `analise.ipynb`: o Sudeste lidera por volume (não por ticket); fim de ano mais de 60% acima de outubro por dia, sem 2024 para separar sazonalidade; margem igual nos canais.
- 2026-10-18 — `painel.ipynb`: painel gerado em `saidas/painel.html`.
