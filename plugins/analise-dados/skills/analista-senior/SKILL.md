---
name: analista-senior
description: >-
  Método para conduzir uma análise de dados em Jupyter como um analista de
  verdade pensaria — uma pergunta de cada vez, em blocos curtos, refletindo
  sobre cada resultado antes de seguir. Use sempre que for analisar dados,
  explorar um DataFrame, fazer EDA, investigar um dataset ou criar
  visualizações em Python/pandas.
---

# Como conduzir uma análise de dados

> **Nota de reconciliação:** este arquivo é a versão do template. Se você já
> tem uma skill parecida, mescle — não duplique. As *regras de sintaxe e
> higiene* (tamanho de célula, imports, sem `NotebookEdit`) moram no `REGRAS.md`;
> aqui mora o *método*. A leitura correta dos dados fica na skill
> `verificacao-leitura`; o perfil de problemas dos dados, na `qualidade-dados`;
> a revisão dos resultados, na `revisao-critica`.

A diferença entre um notebook bom e um ruim não é o código — é o raciocínio.
Um notebook ruim tem outputs mas não tem conclusões. O ciclo abaixo é o coração
de uma boa análise.

## O ciclo (obrigatório)

Para cada coisa que quiser descobrir, repita:

1. **Pergunta** — crie uma célula markdown com a pergunta que quer responder.
2. **Código** — crie a célula que responde *aquela* pergunta. Curta.
3. **Execute** — rode e leia o output de verdade.
4. **Confirme o resultado** — se a célula respondeu a uma pergunta (um achado:
   taxa, ranking, comparação, padrão), passe pela skill `revisao-critica` antes
   de interpretar: o `n` está visível? é share ou risco? tem outra explicação?
   Se algo não fechar, **ajuste a própria célula** (mostre o `n`, troque absoluto
   por taxa, controle por exposição) até a conclusão aguentar.
5. **Reflita** — crie uma célula markdown curta interpretando o resultado *já
   confirmado*. Não repita os números — interprete.
6. **Próxima pergunta** — só então decida o que investigar em seguida, com base
   no que acabou de descobrir.

**Não escreva 10 células de uma vez para rodar depois.** Uma pergunta por vez.
Pular a reflexão (passo 5) ou a confirmação do resultado (passo 4) é o erro mais
comum e o mais grave.

> Ao criar **qualquer gráfico**, siga a skill `graficos` (tipo certo para a
> pergunta, clareza, tamanho, cores consistentes). Monte a célula de estilo
> global logo depois dos imports, para todos os gráficos ficarem padronizados.

## Antes de tocar no código: entender o problema

Análise sem pergunta de negócio é só estatística descritiva à toa. Antes de
criar o notebook, faça ao usuário 2-3 perguntas curtas e interativas:

- Qual é a **pergunta de negócio** por trás disso? O que você quer decidir?
- Quem vai **ler** o resultado?
- O que significam as **colunas** que parecem ambíguas?

Espere a resposta. Não invente o objetivo. Se já existir `contexto.md` na raiz,
leia antes: ele traz as respostas de sessões anteriores — pergunte só o que falta.

## Mantenha o `contexto.md` vivo

O `contexto.md` é a memória do projeto entre sessões. Atualize na hora,
não no fim:

- o aluno explicou uma coluna → linha no dicionário de dados;
- a leitura exigiu parâmetros (`sep`, `encoding`, `decimal`) → em **Como ler**;
- você removeu, filtrou ou corrigiu dados → em **Decisões de tratamento**, com
  data e motivo (é o que permite a outra pessoa refazer a análise);
- a conclusão foi escrita ou atualizada → uma linha em **Histórico**.

Registre só fatos confirmados com o aluno ou nos dados — nunca palpites.

## Títulos de seção são perguntas, não rótulos técnicos

O título de uma seção markdown reflete O QUE se quer descobrir, não a técnica.

- ❌ "Análise Univariada" → ✅ "Quantos pedidos tiveram atraso na entrega?"
- ❌ "Análise Bivariada" → ✅ "O frete influencia a nota da avaliação?"
- ❌ "Correlações" → ✅ "Quais variáveis andam juntas?"

## Markdown ANTES da célula: a intenção

Uma frase curta dizendo o que vai investigar e por quê. Sem jargão.

```markdown
## O estado do cliente influencia o tempo de entrega?
Vamos comparar o tempo médio de entrega por estado.
```

## Markdown DEPOIS da célula: o que o resultado significa

Depois de executar e ver o output, escreva o que aquilo significa no contexto
do problema. **Não repita os números — interprete.**

```markdown
**Resultado:** entregas no Norte levam ~2x mais que no Sudeste, provavelmente
por distância dos centros de distribuição. Vale investigar o custo de frete.
```

## Valores em reais (formatação PT-BR)

Quando a análise envolve dinheiro, os números crus ficam ilegíveis: `8497.0`
em vez de `R$ 8.497,00`. Logo que perceber colunas/valores financeiros, **defina
um helper no começo do notebook** e use na hora de apresentar:

```python
def reais(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
```

Use o helper **só na exibição** — não altere os dados originais. Para uma tabela,
formate uma cópia para mostrar:

```python
faturamento_por_produto.apply(reais)
```

**Atenção com o `$` nas células markdown:** em markdown do Jupyter, `$...$` vira
fórmula matemática. Na interpretação, escreva o valor em código inline
(`` `R$ 8.497` ``) ou escape com barra dupla (`R\\$ 8.497`). Veja a regra de
símbolos especiais no `REGRAS.md`.

## O arco natural da análise

Não precisa ser rígido, mas saiba em qual etapa está:

1. **Carregar** — `read_csv`, `shape`. Logo de cara, passe pela skill
   `verificacao-leitura` (encoding, separador, decimal, rótulos legíveis?) —
   uma vez. Dado lido errado contamina todos os gráficos depois.
2. **Conhecer** — que colunas? que tipos? Depois, passe pela skill
   `qualidade-dados` — uma vez: falta, duplicados, valores impossíveis,
   categorias inconsistentes, buracos no tempo.
3. **Limpar** — corrigir tipos e tratar o que a `qualidade-dados` encontrou,
   com as decisões combinadas com o usuário e anotadas no `contexto.md`.
4. **Explorar uma variável de cada vez** — como se distribui? valores mais comuns?
5. **Cruzar variáveis** — X influencia Y? tem padrão entre essas duas colunas?
6. **Resumir** — uma célula markdown com as conclusões principais ao final.
7. **Revisar e validar** — ofereça o `/revisar` (o subagente `revisor` relê a
   análise procurando conclusões fracas) e rode `/validar`: a análise só está
   pronta se o notebook roda de cima a baixo num kernel limpo. Depois, ofereça
   o `/relatorio` e o `/painel`.

## Formato de resposta

Comece com UMA pergunta. Não planeje o notebook inteiro de antemão. Crie a
markdown + código, execute, leia, interprete, e só então avance. Trabalhe como
um analista: uma pergunta de cada vez.

## Continuar uma análise que já tem conclusão

A célula de conclusão é um **resumo vivo no fim do notebook** — não uma parede.
Quando o usuário pedir para aprofundar ou explorar mais, **não escreva as novas
células abaixo da conclusão**. Em vez disso:

1. Insira as novas células (pergunta → código → interpretação) **imediatamente
   acima** do bloco de conclusão.
2. Depois, **atualize a conclusão** para incorporar as novas descobertas.

É como um analista trabalha: a síntese fica sempre por último, refletindo tudo o
que veio antes.

**Exceção:** se o novo pedido começa uma análise de assunto realmente diferente
(e a conclusão atual era local àquela investigação), o certo seria um notebook
novo. Nesse caso, **pergunte ao usuário** se prefere continuar aqui ou começar
outro notebook — não emende um tema novo embaixo de uma conclusão fechada.
