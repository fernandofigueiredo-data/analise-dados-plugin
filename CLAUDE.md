# Repositório do plugin analise-dados

Este repositório é um marketplace do Claude Code com um plugin
(`plugins/analise-dados/`) e um projeto de exemplo (`exemplo/`).

- As **regras de análise** ficam em `plugins/analise-dados/REGRAS.md` — plugins
  não carregam `CLAUDE.md`; o hook SessionStart injeta esse arquivo nas pastas
  de análise. Ao trabalhar dentro de `exemplo/`, siga-as.
- Scripts do plugin: só stdlib, Python 3.8+ (exceto `validar.py`/`relatorio.py`,
  que rodam no `.venv`). Eles tratam a pasta atual (ou `CLAUDE_PROJECT_DIR`)
  como o projeto do usuário e o próprio diretório como o plugin.
- Caminhos do plugin em comandos, skills e agentes: `${CLAUDE_PLUGIN_ROOT}`.
- Regra checável nova? Coloque em `scripts/regras.py` — o hook e o `/validar`
  usam o mesmo código.
- Antes de concluir uma mudança: `uv run --no-project --python 3.12 -m unittest
  discover -s tests` e `claude plugin validate --strict plugins/analise-dados`.
  Mudou ambiente, scripts ou notebooks do exemplo? Rode também os passos do
  `.github/workflows/ci.yml` dentro de `exemplo/`.
