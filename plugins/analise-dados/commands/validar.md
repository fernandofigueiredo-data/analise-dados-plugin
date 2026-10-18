---
description: Roda o notebook do zero num kernel novo e aponta erros e desvios das regras de casa
argument-hint: "[notebook — padrão: analise.ipynb]"
---

Valide o notebook como um "Restart & Run All" de verdade: um notebook só
funciona se roda de cima a baixo num kernel limpo, não só no kernel ao vivo
(onde variáveis antigas e células rodadas fora de ordem escondem erros).

O aluno passou isto junto do comando (pode estar vazio): `$ARGUMENTS`

## Passo 1 — Rodar

Rode `uv run --no-project --python .venv "${CLAUDE_PLUGIN_ROOT}/scripts/validar.py" $ARGUMENTS` e mostre a saída ao aluno.

O script executa uma **cópia** em `saidas/validacao/` — o notebook aberto no
navegador e o kernel ao vivo não são tocados.

## Passo 2 — Se deu erro

1. Leia o traceback que o script mostrou. Não chute a causa.
2. Corrija a célula **no notebook ao vivo**, pelo Jupyter MCP. Nunca edite a
   cópia em `saidas/validacao/` — ela é descartável e é sobrescrita a cada vez.
3. O erro clássico é a célula depender de algo que só existe no kernel ao vivo
   (uma variável criada e depois apagada, uma célula rodada fora de ordem). A
   correção é tornar o notebook autossuficiente, na ordem em que está.
4. Rode a validação de novo até passar.

## Passo 3 — Avisos

Os avisos apontam desvios das regras do `REGRAS.md` (célula longa, `$` sem
escape, Series crua, dump de tabela, resultado sem interpretação, falta de
conclusão) e duas checagens da skill `revisao-critica`: **soma por mês sem
ajustar pelos dias** e **tabela com taxa, média ou percentual sem a contagem
(n) ao lado**. Os índices das células começam em 0, como no Jupyter MCP.

Nas duas checagens da revisão crítica, corrigir é mexer no conteúdo: adicione
a coluna por dia (ou a contagem) na própria célula, execute, releia o
resultado e **reveja a interpretação** — o achado pode mudar.

- Corrija os que forem legítimos, pelo Jupyter MCP.
- Se decidir manter algum (ex.: uma função que justifica célula longa), diga
  ao aluno qual e por quê, em uma linha.

## Passo 4 — Fechar

Resuma em 1-2 linhas: passou ou não, quantos avisos foram corrigidos e quantos
ficaram (e por quê).
