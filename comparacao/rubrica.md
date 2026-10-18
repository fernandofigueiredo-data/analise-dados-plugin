Você vai avaliar duas análises de dados, A e B, feitas para responder à mesma
pergunta de negócio, com os mesmos dados. Você não sabe como nem por quem cada
uma foi feita — julgue só o que está escrito nos arquivos `A.md` e `B.md` desta
pasta (texto, código e resultados de cada notebook; gráficos aparecem como
`[gráfico]`).

Pergunta de negócio: onde está o faturamento de 2025 — por região, por mês e por
canal de venda — para a diretoria comercial (não técnica) decidir onde
concentrar o esforço comercial em 2026.

Fatos dos dados, para você conferir as afirmações: 5.000 vendas de 01/01/2025 a
31/12/2025 (só um ano); 154 vendas sem região; o valor médio por venda fica
entre R$ 4,7 mil e R$ 5,2 mil em todas as regiões; os meses têm tamanhos
diferentes (fevereiro tem 28 dias).

Para CADA análise, responda com rigor e sem cortesia:

1. `numeros_divergentes`: quantas afirmações numéricas do texto não batem com
   os resultados mostrados (0 se todas batem).
2. `causa_sem_base`: quantas vezes o texto afirma causa ("porque", "devido a",
   "impulsionado por") sem evidência nos resultados.
3. `pico_lido_como_tendencia`: o texto trata a alta de fim de ano como
   crescimento/tendência sem dizer que, com um só ano, não dá para separar de
   sazonalidade? (true/false)
4. `meses_sem_normalizar`: compara meses pelo total sem considerar que têm
   tamanhos diferentes? (true/false)
5. `n_visivel`: rankings, médias e percentuais mostram o tamanho da base (nº de
   vendas)? ("sempre", "às vezes", "nunca")
6. `volume_ou_ticket`: o texto explica se a liderança da maior região vem do
   número de vendas ou do valor de cada venda? (true/false)
7. `vendas_sem_regiao`: o texto diz o que fez com as 154 vendas sem região?
   (true/false)
8. `jargao`: quantos termos técnicos a diretoria não entenderia (ex.: outlier,
   dtype, DataFrame, NaN, groupby, correlação, distribuição, quartil).
9. `conclusao_acionavel`: a conclusão responde às três partes da pergunta
   (região, mês, canal) e diz o que fazer ou o que falta saber? (true/false)
10. `nota`: de 0 a 10, quanto a diretoria pode confiar nessa análise para
    decidir. `justificativa`: uma frase.

Responda SOMENTE com um JSON válido, sem texto antes ou depois, neste formato:
{"A": {"numeros_divergentes": 0, "causa_sem_base": 0, "pico_lido_como_tendencia": false,
"meses_sem_normalizar": false, "n_visivel": "sempre", "volume_ou_ticket": true,
"vendas_sem_regiao": true, "jargao": 0, "conclusao_acionavel": true, "nota": 0,
"justificativa": "..."}, "B": {...}}
