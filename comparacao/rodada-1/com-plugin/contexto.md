# Contexto da análise

## Objetivo
- **Pergunta de negócio:** onde está o faturamento de 2025 — por região, por mês e por canal de venda?
- **Quem lê o resultado:** diretoria comercial (não técnica)
- **Decisão que a análise apoia:** onde concentrar o esforço comercial em 2026

## Dados

### vendas.csv
- **O que é:** uma linha por venda · **Período:** ? (a confirmar nos dados) · **Linhas:** 5.000
- **Como ler:** `sep=","`, `encoding="utf-8"` (a confirmar na verificação de leitura)

| Coluna | Significado | Unidade / formato | Observações |
|---|---|---|---|
| data | data da venda | AAAA-MM-DD | |
| produto | produto vendido | texto | |
| categoria | categoria do produto | texto | |
| regiao | região da venda | texto | |
| quantidade | unidades vendidas | unidades | |
| preco_unitario | preço de cada unidade | R$ | |
| custo_unitario | custo de cada unidade vendida | R$ | |
| canal_venda | canal da venda | texto | |

**Faturamento = quantidade × preco_unitario.**

## Decisões de tratamento
- 2026-10-18 — 154 vendas (2,9% do faturamento) sem `regiao`: mantidas como "Sem região informada", para o total fechar
- 2026-10-18 — Sem duplicadas, sem preço abaixo do custo; período confirmado: 2025-01-01 a 2025-12-31, 5.000 linhas

## Histórico
- 2026-10-18 — `analise.ipynb`: faturamento 2025 = R$ 25,0 mi; Sudeste 39%, Online 45%, Nov-Dez 29% do ano; margem ~36% em todo lugar
