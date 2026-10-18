# analise-dados — análise de dados com IA que um gestor consegue usar

[![CI](https://github.com/fernandofigueiredo-data/analise-dados-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/fernandofigueiredo-data/analise-dados-plugin/actions/workflows/ci.yml)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE)

Plugin do [Claude Code](https://code.claude.com) que conduz uma análise de dados em Jupyter **uma pergunta por
vez**: cada resultado passa por uma revisão crítica antes de virar conclusão, o
notebook é provado rodando do zero, e o que sai no fim (relatório e painel) é
escrito para quem decide, não para quem programa.

![Painel gerado pelo plugin a partir da análise de exemplo](docs/img/painel.png)

## O problema

Pedir uma análise a um assistente de IA costuma render um notebook que **parece**
pronto e não é:

- **células enormes**, cheias de lógica empilhada e comentários óbvios — ninguém revisa;
- **conclusões mais fortes que os dados**: concentração lida como risco, pico de
  fim de ano chamado de crescimento, associação vendida como causa;
- **notebooks que só funcionam no kernel de quem escreveu** — rodados do zero, quebram;
- **texto em jargão** ("análise bivariada", "outliers") que a área de negócio não usa.

Instruções no prompt não resolvem: o modelo esquece no meio da análise.

## A solução

O método vira **regra executada pelo sistema**, não sugestão:

| Onde | O que garante |
|---|---|
| Hook `PostToolUse` em cada célula gravada | Código com mais de 10 linhas ou `$` sem escape no markdown → o Claude é avisado na hora e corrige |
| Skills `revisao-critica` e `qualidade-dados` | Antes de interpretar: o `n` está visível? é share ou risco? é sazonalidade? os dados têm buracos? |
| Subagente `revisor` (só lê) | Relê a análise pronta e aponta conclusões que não se sustentam, com célula, trecho e correção |
| `/validar` | Roda o notebook num kernel novo, de cima a baixo, e confere as regras no notebook inteiro |
| Subagente `editor` + `/relatorio` + `/painel` | Texto em linguagem de negócio; HTML sem código; painel interativo offline |
| Permissões do projeto | `dados/` não pode ser editado; o `.env` (senhas de banco) não pode ser lido pelo Claude |

## Resultado no projeto de exemplo

[`exemplo/analise.ipynb`](exemplo/analise.ipynb) analisa um conjunto de exemplo
com 5.000 vendas de 2025 para responder **onde está o faturamento**. Os três achados,
como o método obrigou a escrevê-los:

| Pergunta | Achado | O que a revisão crítica mudou |
|---|---|---|
| Qual região fatura mais? | Sudeste, com 39% do faturamento | Mostrou que é **volume, não ticket**: o valor por venda fica entre `R$ 4,7 mil` e `R$ 5,2 mil` em todas as regiões |
| O faturamento muda no ano? | Nov–dez faturam **por dia** mais de 60% acima de outubro | Comparação por dia (meses têm tamanhos diferentes) e a ressalva: **só há 2025**, não dá para separar sazonalidade de crescimento |
| Algum canal dá mais margem? | Não: ~36% nos três canais | `n` visível (mais de mil vendas por canal) antes de afirmar igualdade |

<p>
  <img src="docs/img/faturamento-por-regiao.png" width="49%" alt="Faturamento por região, Sudeste em destaque">
  <img src="docs/img/faturamento-por-dia.png" width="49%" alt="Faturamento por dia ao longo de 2025, com salto em novembro e dezembro">
</p>

O mesmo notebook também registra a decisão de tratamento (154 vendas sem região
mantidas como "Não informada", em vez de apagadas) em
[`exemplo/contexto.md`](exemplo/contexto.md), a memória que a próxima sessão lê.

## Evidências técnicas

| O que foi medido | Resultado |
|---|---|
| Início do servidor Jupyter MCP | **~125 s → 2,6 s**. A causa era o servidor esperando 120 s por um Jupyter que ainda não existia; resolvido com `START_NEW_CODE_SANDBOX=false` |
| Kernel usado pelas células | Corrigido: um kernel `python3` do usuário ganhava do kernel do projeto e rodava as células no Python do sistema, sem as dependências |
| Testes | 19 testes de unidade (regras, hooks, preparação do projeto, configuração de banco) + teste de fumaça que executa uma célula pelo Jupyter MCP |
| CI | Workflow para Linux, macOS e Windows: bootstrap, ciclo pelo MCP, `/validar` sem avisos, `/relatorio`, `/painel`, validação estrita dos manifestos. Passos executados localmente no macOS; o status no GitHub está no selo acima |
| Sessão real do Claude Code | Plugin carregado com `--plugin-dir`: regras injetadas no início, hook disparando nas duas regras, Jupyter desligado ao fechar |
| Somente leitura nos bancos | `DELETE` bloqueado num arquivo DuckDB, tanto pela biblioteca do notebook quanto pelo servidor MCP. No Postgres, a conexão abre com transação somente leitura (sem teste contra banco real — ver limitações) |

## Como funciona

```mermaid
flowchart LR
    U["Você: /analise"] --> C["Claude Code"]
    P["Plugin analise-dados<br/>comandos · skills · subagentes"] --> C
    C -- "Jupyter MCP" --> J["JupyterLab do projeto"]
    J --> K["kernel do .venv<br/>pandas · plotly · duckdb"]
    C -. "PostToolUse" .-> H["hook: confere a célula"]
    H -. "aviso" .-> C
    C -- "/validar" --> V["kernel novo:<br/>roda do zero"]
    V --> S["saidas/<br/>relatório · painel"]
    K -- "analise_dados.banco" --> DB[("Postgres · BigQuery<br/>DuckDB · SQLite")]
    C -. "MCP banco: explorar" .-> DB
```

O ambiente Python de todos os projetos vem do `uv.lock` do plugin: atualizar o
plugin atualiza as dependências de cada projeto na próxima execução.

## Instalar e usar

Pré-requisito único: [`uv`](https://docs.astral.sh/uv/) (nem Python precisa).

```bash
claude plugin marketplace add fernandofigueiredo-data/analise-dados-plugin
```

```bash
claude plugin install analise-dados@analise-dados
```

Numa pasta com seus dados em `dados/`, abra o Claude Code e digite `/analise`.

| Comando | O que faz |
|---|---|
| `/analise` | Prepara a pasta e o ambiente, sobe o Jupyter, lê o `contexto.md` e conduz a análise |
| `/banco` | Liga o projeto a Postgres, BigQuery, DuckDB ou SQLite (a senha fica no `.env`, preenchido por você) |
| `/revisar` | Revisor crítico + editor de linguagem de negócio |
| `/validar` | Roda o notebook do zero e aponta erros e desvios das regras |
| `/relatorio` | `saidas/relatorio-analise.html`, sem código |
| `/painel` | `saidas/painel.html`, interativo e offline |

O plugin fica instalado para o usuário, mas só age em pastas de análise (com
`dados/`, `contexto.md` ou notebooks). Para ativar em um projeto só, use
`--scope project` na instalação.

## Decisões técnicas

- **Plugin em vez de pasta-modelo.** A primeira versão era um template copiado
  para cada projeto; corrigir uma regra exigia recopiar tudo. Como plugin,
  regras, skills e ambiente atualizam em todos os projetos. Custo: plugins não
  carregam `CLAUDE.md`, então as regras entram por um hook `SessionStart`.
- **Hook em vez de instrução.** O tamanho de célula e o escape de `$` são checados
  por código (`scripts/regras.py`), o mesmo usado pelo `/validar`. O que exige
  julgamento (share ou risco, causalidade) fica nas skills e no revisor.
- **MCP para explorar, notebook para analisar.** O servidor MCP de banco deixa o
  Claude descobrir tabelas e colunas, mas todo número de uma conclusão vem de uma
  célula — é o que o `/validar` refaz do zero.
- **Conectores de banco:** o `postgres-mcp` está quebrado no PyPI (depende de uma
  versão inexistente do `pglast`); o [`mcp-alchemy`](https://github.com/runekaagaard/mcp-alchemy)
  cobre Postgres, BigQuery e SQLite com a mesma `DB_URL` do notebook, mas falha
  com DuckDB — para ele, `mcp-server-motherduck`, que já abre somente leitura.
- **Painel só em fundo claro.** A paleta categórica (Okabe–Ito, segura para
  daltônicos) passou no validador de contraste no modo claro e falhou no escuro;
  como o painel é um documento para circular, ficou só o modo claro, com tabela
  de valores em cada gráfico para não depender só da cor.

## Limitações conhecidas

- **Postgres e BigQuery não foram testados contra um banco real** — só a
  configuração gerada e o caminho completo com DuckDB e SQLite.
- **Fechar uma sessão desliga o Jupyter** das outras sessões abertas no mesmo projeto.
- **O hook em `edit_cell_source` é melhor esforço**: a ferramenta devolve só um
  diff; o `/validar` cobre o notebook inteiro no fim.
- Textos, comandos e regras estão em **português**.

## Estrutura

```
.claude-plugin/marketplace.json   ← o repositório é um marketplace
plugins/analise-dados/
├── REGRAS.md                     ← regras de casa (hook SessionStart)
├── commands/ skills/ agents/     ← 6 comandos · 6 skills · 2 subagentes
├── hooks/hooks.json              ← regras no início · checagem de célula · desliga o Jupyter
├── .mcp.json                     ← Jupyter MCP com versão fixada
├── ambiente/                     ← pyproject.toml + uv.lock dos projetos
├── lib/analise_dados/            ← banco (SQL) e painel (Plotly), usados no notebook
└── scripts/                      ← bootstrap, validar, relatorio, banco, hooks
exemplo/                          ← projeto completo que o CI executa
tests/                            ← testes de unidade e teste de fumaça do MCP
```

## Desenvolver

```bash
claude --plugin-dir ./plugins/analise-dados
```

```bash
uv run --no-project --python 3.12 -m unittest discover -s tests -v
```

```bash
claude plugin validate --strict plugins/analise-dados
```

Para publicar uma versão, suba `version` em
`plugins/analise-dados/.claude-plugin/plugin.json`. Para trocar a versão do
Jupyter MCP, edite `plugins/analise-dados/.mcp.json` e confira a compatibilidade
de `jupyterlab` e `jupyter-collaboration` em `ambiente/pyproject.toml` — o passo
do Jupyter MCP no CI pega a quebra.

## Licença

[MIT](LICENSE)
