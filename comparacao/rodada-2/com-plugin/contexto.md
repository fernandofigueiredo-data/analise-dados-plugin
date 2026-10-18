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
| preco_unitario | preço de cada unidade | R$ | faturamento = quantidade × preco_unitario |
| custo_unitario | custo de cada unidade vendida | R$ | |
| canal_venda | canal pelo qual a venda ocorreu | texto | |

## Decisões de tratamento
- 2026-10-18 — leitura com `sep=","`, `encoding="utf-8"` confirmada; período 2025-01-01 a 2025-12-31, 5.000 linhas, sem duplicadas, sem preço abaixo do custo
- 2026-10-18 — 154 vendas (2,9% do faturamento) sem `regiao`, espalhadas por todos os canais: mantidas como "Sem região informada" para o total fechar
- 2026-10-18 — faturamento = quantidade × preco_unitario (definição do usuário); margem não analisada

## Histórico
- 2026-10-18 — `analise.ipynb`: R$ 25,0 mi em 2025; Sudeste 39%, Online 44,6%, nov+dez 28,6% do ano; valor médio por venda parecido entre regiões e canais
