"""
Testes do plugin que não precisam de Jupyter nem do ambiente de análise (só stdlib).

    uv run --no-project --python 3.12 -m unittest discover -s tests -v

Os scripts leem a pasta do projeto de CLAUDE_PROJECT_DIR na importação, então
tudo que depende dela roda em subprocesso, numa pasta temporária.
"""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS = RAIZ / "plugins" / "analise-dados" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import regras  # noqa: E402

FERRAMENTA = "mcp__plugin_analise-dados_jupyter__"
LONGA = "\n".join(f"x{i} = {i}" for i in range(12))

def rodar(script, *args, entrada="", projeto=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(projeto or tempfile.gettempdir()))
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], input=entrada,
                          capture_output=True, text=True, env=env, cwd=str(projeto or RAIZ))

def hook(nome, entrada, resposta=None):
    evento = {"tool_name": FERRAMENTA + nome, "tool_input": entrada, "tool_response": resposta}
    return rodar("hook_celula.py", entrada=json.dumps(evento))


class TestRegras(unittest.TestCase):
    def test_codigo_curto_passa(self):
        self.assertEqual(regras.problemas_codigo("df.shape"), [])

    def test_codigo_longo_aponta(self):
        self.assertIn("12 linhas", regras.problemas_codigo(LONGA)[0])

    def test_marcacao_do_relatorio_nao_conta(self):
        fonte = "#| relatorio: mostrar\n" + "\n".join(f"x{i} = {i}" for i in range(10))
        self.assertEqual(regras.problemas_codigo(fonte), [])

    def test_cifrao_solto_aponta(self):
        self.assertTrue(regras.problemas_markdown("Ticket de R$ 100"))

    def test_cifrao_em_crase_ou_escapado_passa(self):
        self.assertEqual(regras.problemas_markdown("Ticket de `R$ 100`"), [])
        self.assertEqual(regras.problemas_markdown("Ticket de R\\$ 100"), [])
        self.assertEqual(regras.problemas_markdown("```\ncusto = 'R$'\n```"), [])


class TestHookCelula(unittest.TestCase):
    def test_insert_codigo_longo_avisa_o_claude(self):
        r = hook("insert_cell", {"cell_index": 3, "cell_type": "code", "cell_source": LONGA})
        self.assertEqual(r.returncode, 2)
        self.assertIn("célula 3", r.stderr)

    def test_insert_codigo_curto_passa(self):
        r = hook("insert_cell", {"cell_index": 3, "cell_type": "code", "cell_source": "df.shape"})
        self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_insert_markdown_com_cifrao(self):
        r = hook("insert_cell", {"cell_index": 4, "cell_type": "markdown", "cell_source": "R$ 5 mil"})
        self.assertEqual(r.returncode, 2)

    def test_insert_execute_e_sempre_codigo(self):
        r = hook("insert_execute_code_cell", {"cell_index": -1, "cell_source": LONGA})
        self.assertEqual(r.returncode, 2)

    def test_overwrite_codigo_com_cifrao_em_string_passa(self):
        fonte = "def reais(v):\n    return f'R$ {v:,.2f}'"
        self.assertEqual(hook("overwrite_cell_source", {"cell_index": 2, "cell_source": fonte}).returncode, 0)

    def test_overwrite_markdown_com_cifrao(self):
        fonte = "**Resultado:** custou R$ 5 mil"
        self.assertEqual(hook("overwrite_cell_source", {"cell_index": 2, "cell_source": fonte}).returncode, 2)

    def test_edit_que_passa_de_10_linhas_pelo_diff(self):
        diff = ("Cell 1 edited successfully!\n\n```diff\n--- \n+++ \n@@ -8,3 +8,5 @@\n x7 = 7\n x8 = 8\n"
                "+x9 = 9\n+x10 = 10\n x11 = 11\n x12 = 12\n```")
        r = hook("edit_cell_source", {"cell_index": 1, "old_string": "a", "new_string": "b"},
                 [{"type": "text", "text": diff}])
        self.assertEqual(r.returncode, 2)
        self.assertIn("12 linhas", r.stderr)

    def test_matcher_do_hook_pega_os_dois_nomes_do_servidor(self):
        import re
        hooks = json.loads((SCRIPTS.parent / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        matcher = hooks["hooks"]["PostToolUse"][0]["matcher"]
        for nome in ("mcp__plugin_analise-dados_jupyter__insert_cell", "mcp__jupyter__overwrite_cell_source"):
            self.assertTrue(re.search(matcher, nome), nome)
        self.assertFalse(re.search(matcher, "mcp__plugin_analise-dados_jupyter__read_cell"))

    def test_entrada_invalida_nao_quebra(self):
        self.assertEqual(rodar("hook_celula.py", entrada="lixo").returncode, 0)


class TestProjeto(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def preparar(self):
        codigo = "from projeto import preparar; print('\\n'.join(preparar()))"
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.proj))
        return subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True,
                              env=env, cwd=str(SCRIPTS))

    def test_sessao_so_carrega_regras_em_projeto_de_analise(self):
        self.assertEqual(rodar("hook_sessao.py", entrada="{}", projeto=self.proj).stdout, "")
        (self.proj / "dados").mkdir()
        self.assertIn("Regras para trabalho", rodar("hook_sessao.py", entrada="{}", projeto=self.proj).stdout)

    def test_preparar_cria_e_e_idempotente(self):
        self.assertEqual(self.preparar().returncode, 0)
        for item in ("dados", "saidas/.gitkeep", "estilos/design-system.md", ".gitignore",
                     ".claude/settings.json"):
            self.assertTrue((self.proj / item).exists(), item)
        self.assertEqual(self.preparar().stdout.strip(), "")  # 2ª vez não faz nada

    def test_preparar_preserva_o_que_o_usuario_tinha(self):
        (self.proj / ".claude").mkdir()
        (self.proj / ".claude" / "settings.json").write_text(json.dumps(
            {"model": "opus", "permissions": {"allow": ["Bash(make *)"]}}))
        (self.proj / ".gitignore").write_text("meu-arquivo.txt\n")
        self.preparar()
        cfg = json.loads((self.proj / ".claude" / "settings.json").read_text())
        self.assertEqual(cfg["model"], "opus")
        self.assertIn("Bash(make *)", cfg["permissions"]["allow"])
        self.assertIn("Read(./.env)", cfg["permissions"]["deny"])
        gi = (self.proj / ".gitignore").read_text()
        self.assertTrue(gi.startswith("meu-arquivo.txt"))
        self.assertIn(".env", gi)

    def test_extra_do_banco_pela_db_url(self):
        from projeto import extra_do_banco
        casos = {"postgresql+psycopg://u:s@h/db": "postgres", "bigquery://proj/ds": "bigquery",
                 "duckdb:///dados/x.duckdb": "duckdb", "sqlite:///x.db": "sql", None: None}
        for url, extra in casos.items():
            self.assertEqual(extra_do_banco(url), extra, url)

    def test_banco_configurar_registra_mcp_sem_senha(self):
        for tipo in ("postgres", "bigquery", "duckdb", "sqlite"):
            r = rodar("banco.py", "configurar", tipo, projeto=self.proj)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            servidor = json.loads((self.proj / ".mcp.json").read_text())["mcpServers"]["banco"]
            self.assertEqual(servidor["command"], "uvx")
            if tipo != "duckdb":
                self.assertIn("--env-file", servidor["args"])  # a senha só existe no .env
            self.assertIn("DB_URL=", (self.proj / ".env.exemplo").read_text())
        self.assertFalse((self.proj / ".env").exists())


if __name__ == "__main__":
    unittest.main()
