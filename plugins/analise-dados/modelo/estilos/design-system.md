# Design System — Gráficos

> Paleta e estilo padrão dos gráficos deste projeto. A skill `graficos` consome
> este arquivo ao montar a célula de estilo do notebook. Para personalizar:
> coloque imagens de referência em `estilos/` e peça para o Claude reconstruir
> este arquivo a partir delas.

## Paleta

| Papel | Cor | Hex |
|---|---|---|
| Primária (série principal) | azul | `#0072B2` |
| Secundária / neutra (apoio) | cinza | `#94A3B8` |
| Destaque (realçar o ponto-chave) | laranja | `#E69F00` |

## Paleta categórica (Okabe–Ito — segura para daltônicos)

`#0072B2`, `#E69F00`, `#009E73`, `#CC79A7`, `#56B4E9`, `#D55E00`, `#F0E442`

## Escala sequencial (heatmaps, intensidade)

`viridis` (perceptualmente uniforme). Para intensidade em tons quentes: `YlOrRd`.

## Princípios

- Menos é mais: só o essencial na figura.
- Mesma categoria = mesma cor em todos os gráficos.
- Destaque um elemento por figura; o resto neutro.
- Sem moldura superior/direita; grade discreta.
- Barra começa no zero; rótulos legíveis; a figura usa o espaço disponível.
