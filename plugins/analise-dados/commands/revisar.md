---
description: Revisão crítica da análise pronta (subagente revisor) e, se quiser, reescrita do texto em linguagem de negócio (subagente editor)
argument-hint: "[notebook — padrão: analise.ipynb]"
---

Faça a revisão de uma análise que já tem conclusão. O objetivo é que nada
chegue a quem decide sem ter passado por um segundo par de olhos.

O aluno passou isto junto do comando (pode estar vazio): `$ARGUMENTS`

## Passo 1 — Revisão de conteúdo

Delegue ao subagente **revisor** do plugin a releitura do notebook
(`$ARGUMENTS`, ou `analise.ipynb` se vazio). Ele só lê e devolve um veredito
e uma tabela de achados por gravidade.

Mostre ao aluno o veredito e os achados de gravidade **alta** e **média**,
resumidos. Os de gravidade baixa, só a contagem.

## Passo 2 — Corrigir, com o aluno

Para cada achado alto ou médio, proponha a correção e espere o ok do aluno
antes de aplicar. Ele conhece o negócio e pode discordar — se discordar,
registre o porquê em uma linha na interpretação da célula.

Aplique pelo Jupyter MCP seguindo a skill `analista-senior`: ajuste a célula de
código (mostrar o `n`, trocar absoluto por taxa…), **execute**, releia o output,
reescreva a interpretação e, por fim, atualize a conclusão.

## Passo 3 — Texto para o público (opcional)

Pergunte se o notebook vai para alguém não técnico (relatório, painel, reunião).
Se sim, delegue ao subagente **editor** do plugin a reescrita do markdown em
linguagem de negócio. Mostre o resumo do que ele mudou.

## Passo 4 — Fechar

Rode o `/validar` — as correções podem ter quebrado a ordem do notebook.
Resuma em 2 linhas: o que foi corrigido, o que ficou como está e por quê.
