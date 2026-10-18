# Changelog

## 1.1.0 — 2026-10-18

- `/validar` aponta, por código, duas regras da revisão crítica que antes
  dependiam só de o modelo seguir a skill: **soma por mês sem ajustar pelos
  dias** e **tabela com taxa, média ou percentual sem a contagem ao lado**.
  Motivo: na [comparação com e sem o plugin](comparacao/), as duas passaram
  despercebidas na rodada 1.
- `/validar` só conta como aviso do Python o que é aviso de verdade
  (`UserWarning`, `FutureWarning`…) — recados informativos no stderr, como o
  cache de fontes do matplotlib numa máquina nova, não contam mais.
- Comparação com e sem o plugin em duas rodadas, com julgamento cego nas duas ordens.

## 1.0.0 — 2026-10-18

- Primeira versão: comandos `/analise`, `/banco`, `/revisar`, `/validar`,
  `/relatorio` e `/painel`; skills, subagentes `revisor` e `editor`; hooks de
  sessão e de célula; fontes SQL; painel Plotly; exemplo, testes e CI.
