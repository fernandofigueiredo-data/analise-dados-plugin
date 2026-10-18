# Com e sem o plugin

A mesma pergunta de negócio, os mesmos dados, o mesmo ambiente e o mesmo modelo:
uma sessão do Claude Code **sem** o plugin e outra **com** ele, repetido em duas
rodadas. Os notebooks foram medidos pelo mesmo script e julgados às cegas, nas
duas ordens (A/B sorteados e depois invertidos).

| Rodada | Plugin | O que mudou |
|---|---|---|
| [1](rodada-1/) | v1.0.0 | — |
| [2](rodada-2/) | v1.1.0 | o `/validar` passou a apontar, por código, **soma por mês sem ajuste pelos dias** e **taxa sem contagem**, as duas falhas da rodada 1 |

## Protocolo

| | Sem plugin | Com plugin |
|---|---|---|
| Dados | `vendas.csv` (5.000 vendas de 2025) | o mesmo arquivo |
| Ambiente Python | `.venv` com as mesmas versões (`uv.lock` do plugin) e kernel registrado | criado pelo próprio plugin, do mesmo `uv.lock` |
| Contexto de negócio | [`prompts/contexto.md`](prompts/contexto.md) | o mesmo texto |
| Instrução | [`prompts/sem-plugin.md`](prompts/sem-plugin.md): criar, executar e concluir o notebook | [`prompts/com-plugin.md`](prompts/com-plugin.md): seguir o `/analise` e o `/validar` |
| Modelo | `claude-sonnet-5-5` (padrão da sessão headless) | o mesmo |
| Pasta | nova a cada rodada, isolada, sem `.mcp.json`, `CLAUDE.md` ou `.claude/` acima | idem |

O projeto sem plugin recebe um ambiente que funciona — inclusive o kernel do
`.venv` registrado —, para não falhar por um problema de ambiente que o plugin
resolve e que não é o que está sendo comparado.

**Medição** ([`medir.py`](medir.py)): roda cada notebook do zero num kernel novo
e mede a forma; todas as rodadas foram medidas com as regras da v1.1.0.
**Avaliação cega** ([`preparar_avaliacao.py`](preparar_avaliacao.py) +
[`rubrica.md`](rubrica.md)): cada notebook vira texto com rótulo A ou B; uma
sessão sem o plugin responde 10 perguntas verificáveis sem saber qual é qual.
Cada par foi julgado duas vezes, com a ordem invertida (sementes 2025 e 5); os
mapas só foram abertos depois.

## Resultados

### Nota de confiabilidade no julgamento cego (0–10)

| | Sem plugin | Com plugin |
|---|---|---|
| Rodada 1 (ordem 1 · ordem 2) | 8 · 8 | 7 · 7 |
| Rodada 2 (ordem 1 · ordem 2) | 6 · 6 | 9 · 8 |
| **Média das quatro notas** | **7,0** | **7,75** |

A ordem não mudou o veredito em nenhuma rodada (variação máxima de 1 ponto).

### O que o avaliador apontou

| Pergunta da rubrica | R1 sem | R1 com | R2 sem | R2 com |
|---|---|---|---|---|
| Meses comparados sem ajustar pelos dias | sim | sim | sim | **não** |
| Tamanho da base (`n`) visível | às vezes | às vezes | às vezes | sempre · às vezes |
| Explica se a liderança vem de volume ou de ticket | sim | sim | **não** | sim |
| Pico de fim de ano lido como tendência | não | não | não | não |
| Causa afirmada sem evidência | 0 | 0 | 0 | 0 |

Na rodada 2, o avaliador também apontou que a versão sem plugin afirma margem
de ~36% "em todas as regiões e canais" sem mostrar esse resultado, e que a
versão com plugin escreve "entre `R$ 4.800` e `R$ 5.200`" por venda deixando de
fora o Centro-Oeste (`R$ 5.231`). As justificativas completas estão em
`rodada-*/resultados/avaliacao-cega-ordem*.json`.

### Forma, legibilidade e rastreabilidade — medição

| Métrica | R1 sem | R1 com | R2 sem | R2 com |
|---|---|---|---|---|
| Roda do zero num kernel novo | sim | sim | sim | sim |
| Linhas por célula (média / máximo) | 9,8 / 16 | 3,3 / 8 | 9,5 / 17 | 3,6 / 6 |
| Células com mais de 10 linhas | 5 | 0 | 4 | 0 |
| Textos com `$` que quebra a renderização | 4 | 0 | 2 | 0 |
| Avisos das regras (v1.1.0) | 11 | 2 | 9 | **0** |
| Termina com conclusão | sim | sim | não | sim |
| Contexto e decisões registrados · validado na sessão | não · não | sim · sim | não · não | sim · sim |
| Tempo da sessão | 2,6 min | 2,6 min | 2,3 min | 2,5 min |
| Custo da sessão | US$ 0,58 | US$ 0,79 | US$ 0,57 | US$ 0,82 |

Como a diretoria leria o principal achado da rodada 1 no Jupyter:

**Sem plugin** — o `$` de "R$" abre uma fórmula e o texto entre dois valores vira matemática:

![Texto sem o plugin: o trecho entre dois R$ aparece como fórmula](../docs/img/markdown-sem-plugin.png)

**Com plugin** — os valores vão entre crases (regra de casa conferida por hook):

![Texto com o plugin: valores em reais renderizados corretamente](../docs/img/markdown-com-plugin.png)

## O que isso mostra

- **A melhoria funcionou onde devia.** Na rodada 2, o `/validar` apontou a soma
  por mês sem ajuste, e a própria sessão corrigiu: acrescentou o faturamento por
  dia e o número de vendas à tabela mensal e reviu a interpretação. O avaliador
  cego passou a registrar "normaliza os meses por dia" — a falha que os dois
  lados tinham na rodada 1.
- **O ganho em conteúdo é real, mas menor do que a rodada 2 sozinha sugere.** A
  versão com plugin subiu de 7 para 8,5; a sem plugin caiu de 8 para 6 — e essa
  queda é variação entre execuções (na rodada 2 ela deixou de separar volume de
  ticket e não terminou com conclusão), não efeito do plugin. Na média das duas
  rodadas: 7,75 com plugin, 7,0 sem.
- **Na forma e na rastreabilidade, a vantagem do plugin se repetiu nas duas
  rodadas:** células revisáveis, nenhum texto quebrado, contexto registrado e
  notebook provado do zero dentro da sessão.
- **O que só código garante.** As regras checadas pelo `/validar` foram
  cumpridas; as que dependem de o modelo seguir a skill variaram — a versão com
  plugin da rodada 2 não analisou a margem e arredondou uma faixa de valores
  deixando uma região de fora.
- **Custo:** cerca de 40% a mais por sessão, no mesmo tempo.

## Limitações

- **Duas execuções de cada lado.** É pouco para medir efeito com precisão; a
  variação de uma rodada para a outra (8 → 6 sem o plugin) é do tamanho da
  diferença entre os lados.
- **O avaliador é o mesmo modelo** que fez as análises.
- **A rubrica e os "fatos dos dados" foram escritos por quem conhece os dados e
  o plugin**; as perguntas são verificáveis, mas a escolha delas não é neutra —
  e duas delas (meses por dia, `n` visível) viraram regras do plugin depois da
  rodada 1, o que favorece a v1.1.0 nessa rubrica.
- **As métricas de forma são os critérios do próprio plugin** — é esperado que
  ele vá melhor nelas. A métrica neutra (rodar do zero) empatou nas duas rodadas.

## Reproduzir

Com o Claude Code e o `uv` instalados, em duas pastas novas com `dados/vendas.csv`
(a pasta sem plugin precisa do `.venv` antes, com o kernel registrado):

```bash
PATH="$PWD/.venv/bin:$PATH" JUPYTER_PATH="$PWD/.venv/share/jupyter" claude -p "$(cat prompts/contexto.md; echo; cat prompts/sem-plugin.md)" --output-format json --max-turns 80 --allowedTools "Read,Write,Edit,NotebookEdit,Glob,Grep,Bash(python *),Bash(python3 *),Bash(jupyter *),Bash(.venv/bin/*),Bash(ls *)" > sem.json
```

```bash
claude -p "$(cat prompts/contexto.md; echo; cat prompts/com-plugin.md)" --plugin-dir <repo>/plugins/analise-dados --output-format json --max-turns 120 --allowedTools "Read,Write,Edit,Glob,Grep,Skill,Agent,Bash(uv *),Bash(.venv/bin/*),Bash(ls *),mcp__plugin_analise-dados_jupyter__*" > com.json
```

Os caminhos de `prompts/` são relativos a esta pasta; ajuste-os ao rodar de
dentro de cada experimento. Depois, em cada pasta:
`uv run --no-project --python .venv <repo>/comparacao/medir.py analise.ipynb <sessao>.json`.
Para a avaliação cega: `preparar_avaliacao.py SEM.ipynb COM.ipynb <pasta> <semente>`
e `claude -p "$(cat rubrica.md)" --allowedTools Read` dentro da pasta gerada,
uma vez com a semente 2025 e outra com a 5.
