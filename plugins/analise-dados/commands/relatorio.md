---
description: Gera um relatório HTML da análise, sem código, para quem é de negócio
argument-hint: "[notebook — padrão: analise.ipynb]"
---

Gere o relatório da análise para quem vai ler o resultado (o público anotado
em `contexto.md`). O relatório mostra os textos e os gráficos do notebook;
o código nunca aparece.

O aluno passou isto junto do comando (pode estar vazio): `$ARGUMENTS`

## Passo 1 — O notebook está pronto para virar relatório?

Leia o notebook pelo Jupyter MCP e confira:

- **Termina com uma conclusão** em markdown (skill `analista-senior`). Se não
  tiver, escreva antes de exportar — relatório sem fecho não serve para decidir.
- **A análise já passou pelo `/revisar`?** Se não, sugira ao aluno rodar antes —
  relatório espalha a conclusão, então ela precisa estar firme.
- **Os textos falam com o público**, sem jargão (`REGRAS.md`). Markdown técnico
  ("vamos checar os dtypes") vai aparecer no relatório: delegue ao subagente
  **editor** do plugin a reescrita do markdown em linguagem de negócio.

## Passo 2 — Escolher o que aparece

Regra padrão do relatório:
- markdown → aparece;
- gráficos → aparecem;
- tabelas e textos de saída (`.head()`, `.shape`, contagens) → **não** aparecem;
- código → nunca aparece.

Para mudar isso numa célula, adicione **uma linha própria** no código, pelo
Jupyter MCP (é uma marcação para o exportador, não um comentário):

- `#| relatorio: mostrar` → nas tabelas que **respondem a uma pergunta** da
  análise (o ranking, a comparação final). Garanta que a tabela está
  apresentável: valores em reais com o helper `reais`, poucas linhas,
  `.to_frame()` se for Series.
- `#| relatorio: ocultar` → em gráficos auxiliares que não ajudam o leitor.

Não precisa reexecutar o kernel ao vivo por causa dessas linhas.

## Passo 3 — Gerar

Rode `uv run --no-project --python .venv "${CLAUDE_PLUGIN_ROOT}/scripts/relatorio.py" $ARGUMENTS`. O script roda o notebook do zero
antes de exportar. Se falhar, siga o fluxo do `/validar` (leia o traceback,
corrija no notebook ao vivo, tente de novo).

## Passo 4 — Entregar

Mostre o caminho do arquivo (`saidas/relatorio-<notebook>.html`) e diga ao
aluno que basta abrir no navegador. Para PDF: no navegador, **Imprimir →
Salvar como PDF**.
