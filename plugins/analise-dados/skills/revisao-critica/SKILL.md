---
name: revisao-critica
description: >-
  Passo mental rápido para confirmar que um resultado se sustenta antes de
  transformá-lo em conclusão. Use depois de executar a(s) célula(s) que respondem
  a uma pergunta da análise (um achado: taxa, ranking, comparação, padrão
  temporal) — antes de escrever a interpretação. Não se aplica a células de
  import, carregamento ou transformação. Verifica tamanho de amostra, se o número
  é share ou risco, explicações alternativas e causalidade sem base — e, quando o
  achado envolve tempo (subiu, caiu, cresceu, melhor mês), se é sazonalidade,
  se a comparação com o período anterior é justa e se é tendência ou ruído.
---

# Confirmar o resultado antes de virar conclusão

Use **só nas células que respondem a uma pergunta** da análise — um achado de
verdade (uma taxa, um ranking, uma comparação, um padrão no tempo). Em import,
carregamento ou transformação, não precisa.

Antes de escrever a interpretação, pare e percorra mentalmente:

- **O `n` está visível?** Toda taxa ou média vem com o tamanho da base do lado.
  Taxa sobre base pequena não é achado, é ruído — e num ranking por taxa, um
  único caso extremo pode liderar.
- **É share ou risco?** "X concentra 70% das mortes" mede o tamanho do grupo;
  "X tem 2,3× mais mortes por ocorrência" mede o risco. São coisas diferentes —
  se a pergunta é sobre risco, use a taxa, não o share.
- **Tem outra explicação?** Pergunte "o que mais explicaria isso?". Ex: "dias
  limpos têm mais mortes" pode ser só porque dia limpo é o mais comum — mais
  exposição, não mais risco. Quando a pergunta é risco, controle por exposição
  (use a taxa por ocorrência, não o número absoluto).
- **A janela é pequena?** Recortes curtos (um feriado de 3 dias, um único mês)
  são sensíveis a um evento extremo. Sinalize a fragilidade, não venda como
  tendência.
- **Estou afirmando causa sem base?** Os dados mostram associação, não causa.
  Não escreva que A "causa" B sem como isolar isso — e nunca cite uma variável
  que não existe no dataset.

## Quando o achado envolve tempo

"Subiu", "caiu", "cresceu", "o melhor mês" — toda afirmação sobre o tempo é uma
comparação, e comparação injusta é o jeito mais comum de enganar sem querer.
Antes de interpretar, percorra também:

- **É sazonalidade?** "Dezembro vendeu 3× mais que janeiro" pode ser só o Natal
  — acontece todo ano. Sazonalidade se prova com o **mesmo mês de anos
  diferentes**, não com meses vizinhos. Com **só um ano de dados**, não dá para
  separar sazonalidade de crescimento: diga isso com todas as letras, em vez de
  chamar o pico de tendência.
- **A comparação com o período anterior é justa?**
  - Compare com o **mesmo período do ano anterior** quando o negócio tem
    sazonalidade; mês contra mês anterior só quando não tem.
  - **Mesmo tamanho de janela**: fevereiro tem 28 dias, março 31; um mês tem
    cinco fins de semana, outro quatro. Se o tamanho muda, compare **por dia**
    (ou por dia útil).
  - **Período fechado**: o mês corrente ainda não acabou — compará-lo com um mês
    inteiro sempre mostra "queda". Compare os mesmos dias (1 a 15 com 1 a 15) ou
    espere fechar.
  - Mostre a variação **em % e em valor absoluto**: sobre base pequena, "+200%"
    pode ser de 2 para 6.
- **É tendência ou ruído?** Dois pontos não fazem tendência. Um mês fora da
  curva é um evento (promoção, falta de estoque, falha de coleta — veja os
  buracos no tempo da skill `qualidade-dados`), não uma virada. Tendência é a
  direção se mantendo por vários períodos.
- **Mudou o desempenho ou mudou o mix?** O ticket médio pode subir só porque se
  vendeu mais produto caro, sem nenhum preço ter subido. Quando uma média geral
  muda, confira se a mudança aparece **dentro de cada grupo** ou só no total.

Para comparar com o mesmo mês do ano anterior, ajuste a célula assim:

```python
mensal = df.set_index("data").resample("MS")["faturamento"].sum().to_frame("atual")
mensal["mesmo mês, ano anterior"] = mensal["atual"].shift(12)
mensal["variação %"] = (mensal["atual"] / mensal["mesmo mês, ano anterior"] - 1) * 100
mensal.tail(12)
```

Se a coluna do ano anterior sair vazia (`NaN`), os dados não cobrem o ano
anterior: a comparação não é possível — diga isso na interpretação em vez de
comparar com o mês vizinho.

E, quando os meses têm tamanhos diferentes, por dia:
`mensal["por dia"] = mensal["atual"] / mensal.index.days_in_month`.

Se algum ponto não fechar, não escreva a interpretação ingênua: ajuste a própria
célula (mostre o `n`, troque absoluto por taxa, controle por exposição) e escreva
a conclusão honesta — a que sobrevive a essas perguntas. Se o achado não se
sustenta, diga isso; é uma conclusão válida.
