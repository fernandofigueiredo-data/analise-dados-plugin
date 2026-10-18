---
name: graficos
description: >-
  Como criar gráficos claros e bonitos numa análise — escolher o tipo certo de
  gráfico para cada pergunta, aplicar princípios de clareza (Gestalt, menos é
  mais), usar tamanho e legibilidade adequados, e manter cores consistentes
  vindas de um design system. Use sempre que for criar, melhorar ou revisar
  qualquer visualização (gráfico, plot, chart, figura) num notebook. Dispara ao
  plotar com matplotlib ou seaborn.
---

# Gráficos: claros primeiro, bonitos sempre

Um gráfico existe para tornar uma resposta óbvia. Se o leitor precisa se esforçar
para ler, o gráfico falhou — por mais bonito que seja.

## 1. Escolher o gráfico certo para a pergunta

Comece pela pergunta, não pelo gráfico. Barra e linha resolvem a maioria, e tá
ótimo. Use o tipo que torna a resposta imediata:

- **Comparar categorias / ranking** → barra. Rótulos longos ou muitas categorias?
  **Barra horizontal ordenada por valor** (não alfabética).
- **Evolução no tempo** → linha. Marque eventos relevantes (ex: feriados) com
  anotação direta sobre a linha.
- **Distribuição de uma variável** → histograma; boxplot/violino para comparar a
  distribuição entre grupos.
- **Relação entre dois números** → dispersão (scatter).
- **Dois categóricos × uma métrica** → heatmap.
- **Parte do todo** → evite pizza; barra (ou empilhada, com parcimônia) lê melhor.

**Quando barra/linha não bastam** — use com critério, nunca novidade por novidade:
- antes/depois entre grupos → slope chart;
- ranking ao longo do tempo → bump chart;
- a mesma relação em vários recortes → small multiples (facetas), em vez de um
  gráfico poluído;
- ranking limpo → lollipop no lugar da barra.

A regra: o gráfico diferente só se justifica se tornar a resposta **mais** clara.

## 2. Clareza e carga cognitiva — menos é mais

Tire tudo que não ajuda a responder a pergunta (Gestalt + foco):

- **Ordene** barras por valor — o ranking deve se ler de imediato.
- **Destaque o essencial** com a cor de destaque e deixe o resto neutro: o olho
  vai direto ao que importa.
- **Tire o lixo gráfico**: sem moldura superior/direita, grade discreta ou
  ausente, sem legenda redundante. Quando der, **rotule direto** (valor na ponta
  da barra, nome no fim da linha) em vez de mandar o leitor ao eixo/legenda.
- **Título que informa**: "Faturamento por produto" é ok; melhor ainda quando o
  título diz o achado — mas respeite a `revisao-critica`, sem afirmar o que o
  dado não sustenta.
- **Honestidade visual**: barra começa no zero; não compare grupos de tamanhos
  muito diferentes sem normalizar; escala justa.

## 3. Tamanho e legibilidade — use o espaço

Nada de figura espremida no canto. Os defaults vêm da célula de estilo (seção 4):
`figsize` confortável (maior quando há muitas categorias), fontes legíveis
(título ~15, eixos ~12), marcadores e linhas com espessura visível. Rótulo longo
→ barra horizontal ou rotação; nunca deixe texto sobreposto.

## 4. Cores consistentes — a célula de estilo global

Logo abaixo dos primeiros imports, crie **uma célula de estilo** com as variáveis
de cor e os parâmetros globais do matplotlib. Todo gráfico usa essas variáveis.
Precisou de um parâmetro novo? Adicione aqui e re-rode — o notebook inteiro fica
consistente.

```python
import matplotlib.pyplot as plt

COR_PRIMARIA   = "#0072B2"   # série principal
COR_SECUNDARIA = "#94A3B8"   # apoio / elementos neutros
COR_DESTAQUE   = "#E69F00"   # realçar o ponto-chave
PALETA = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]

plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 110,
    "font.size": 12,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.prop_cycle": plt.cycler(color=PALETA),
})
```

Mesma categoria = mesma cor em todos os gráficos. `COR_DESTAQUE` só para realçar
o ponto-chave de cada figura. (Para heatmaps e gráficos estatísticos, seaborn
ajuda — `%pip install seaborn` quando precisar, e `sns.set_palette(PALETA)`.)

## 5. De onde vêm as cores — a pasta `estilos/`

A paleta pode vir de um design system próprio do projeto, na pasta `estilos/`
(ao lado de `dados/`). Antes do **primeiro gráfico**, olhe o que tem nela:

- **Tem imagens de referência mas ainda não tem `design-system.md`** → construa
  um. Olhe as imagens (dashboards/paletas que o usuário curte), extraia as cores
  em hex (primária, secundária, destaque, categórica), a fonte se der para
  identificar e os princípios de estilo, e escreva em `estilos/design-system.md`.
  Confirme com o usuário antes de adotar.
- **Já tem `design-system.md`** → consuma: transcreva os hex e parâmetros para a
  célula de estilo do notebook.
- **`estilos/` vazia** → use o `design-system.md` padrão que já vem no template.

A célula de estilo do notebook é o ponto de consumo: ela materializa o design
system em código. Assim o estilo é decisão de projeto (versionada, reutilizável),
não improviso a cada figura.
