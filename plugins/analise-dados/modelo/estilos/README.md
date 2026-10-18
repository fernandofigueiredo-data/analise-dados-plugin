# estilos/

Pasta opcional para definir a **identidade visual dos gráficos** do projeto.

Como funciona:

1. Coloque aqui **imagens de referência** — dashboards, paletas, gráficos cujo
   estilo você curte (`.png`, `.jpg`).
2. Ao rodar a análise, o Claude olha essas imagens e constrói (ou atualiza) o
   `design-system.md`: cores em hex, estilo e princípios.
3. O notebook consome o `design-system.md` numa **célula de estilo** logo abaixo
   dos imports — e todos os gráficos seguem esse padrão.

Se você não colocar nenhuma imagem, vale o `design-system.md` padrão que já vem
aqui (uma paleta limpa e segura para daltônicos).
