import os
from pathlib import Path
import shutil
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dev-flow-build-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "skill bundle"
        (self.bundle / "adapters").mkdir(parents=True)
        shutil.copy2(ROOT / "adapters/build.sh", self.bundle / "adapters/build.sh")
        # Isolate even regressions that ignore --output-dir; never use real install paths.
        script = self.bundle / "adapters/build.sh"
        source = script.read_text()
        for tool, default in (("pi", "$HOME/.pi/agent/agents"),
                              ("claude-code", "$HOME/.claude/agents")):
            original = f'local out="{default}"'
            self.assertEqual(source.count(original), 1)
            source = source.replace(original, f"local out={shlex.quote(str(self.root / 'fallback' / tool))}")
        script.write_text(source)
        shutil.copytree(ROOT / "_agents", self.bundle / "_agents")
        self.project = self.root / "target project"
        self.project.mkdir()
        self.output = self.root / "generated agents"
        self.names = sorted(path.name.removesuffix(".prompt.md")
                            for path in (self.bundle / "_agents").glob("*.prompt.md"))

    def configure(self, project, model, bold=True):
        config = project / "docs/agents/execution-mode.md"
        config.parent.mkdir(parents=True, exist_ok=True)
        field = "**基础模型**" if bold else "基础模型"
        config.write_text(f"# Execution mode: subagent\n\n{field}: {model}\n")

    def run_build(self, *args, model=None, cwd=None):
        env = os.environ.copy()
        env.pop("DEV_FLOW_MODEL", None)
        if model is not None:
            env["DEV_FLOW_MODEL"] = model
        return subprocess.run(
            ["bash", str(self.bundle / "adapters/build.sh"), *args,
             "--output-dir", str(self.output)],
            cwd=cwd or self.project, env=env, text=True, capture_output=True,
        )

    def assert_no_pinned_models(self):
        paths = sorted(self.output.glob("*/*.md"))
        self.assertTrue(paths)
        for path in paths:
            frontmatter = path.read_text().partition("\n---\n\n")[0]
            self.assertFalse(any(line.startswith("model:") for line in frontmatter.splitlines()), path)

    def assert_pi_model(self, expected):
        paths = sorted((self.output / "pi").glob("*.md"))
        self.assertEqual(len(paths), len(self.names))
        for path in paths:
            frontmatter = path.read_text().partition("\n---\n\n")[0]
            self.assertIn(f"\nmodel: {expected}\n", frontmatter, path)

    def test_supported_targets_and_prompt_fidelity(self):
        for target, tools in (("pi", ["pi"]), ("claude-code", ["claude-code"]),
                              ("all", ["pi", "claude-code"])):
            with self.subTest(target=target):
                shutil.rmtree(self.output, ignore_errors=True)
                result = self.run_build(target)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(sorted(p.name for p in self.output.iterdir()), sorted(tools))
                self.assert_no_pinned_models()
                for tool in tools:
                    self.assertEqual(sorted(p.stem for p in (self.output / tool).glob("*.md")),
                                     self.names)
                    for name in self.names:
                        generated = (self.output / tool / f"{name}.md").read_text()
                        body = generated.partition("\n---\n\n")[2]
                        expected = (self.bundle / "_agents" / f"{name}.prompt.md").read_text()
                        if name == "implementer":
                            expected += "\n\n" + (self.bundle / "_agents/workflow-contract.md").read_text()
                        self.assertEqual(body, expected)

    def test_codex_does_not_generate_agent_files(self):
        result = self.run_build("codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("adapters/codex/README.md", result.stdout)
        self.assertFalse(self.output.exists())

    def test_omitted_target_defaults_to_all(self):
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(p.name for p in self.output.iterdir()), ["claude-code", "pi"])
        self.assertIn("adapters/codex/README.md", result.stdout)

    def test_invalid_arguments_do_not_write(self):
        for args in (("unknown",), ("pi", "--unknown"), ("pi", "--output-dir"),
                     ("pi", "--project-root"), ("pi", "--project-root", ""),
                     ("pi", "--project-root", str(self.root / "missing"))):
            with self.subTest(args=args):
                result = self.run_build(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())

    def test_user_configured_project_model(self):
        for bold in (True, False):
            with self.subTest(bold=bold):
                self.configure(self.project, "provider/user-selected-model", bold=bold)
                result = self.run_build("all", "--project-root", str(self.project))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_pi_model("provider/user-selected-model")
                for path in (self.output / "claude-code").glob("*.md"):
                    self.assertNotIn("\nmodel:", path.read_text().partition("\n---\n\n")[0])

    def test_explicit_inherit_model(self):
        self.configure(self.project, "inherit")
        result = self.run_build("pi", "--project-root", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_pi_model("inherit")

    def test_explicit_environment_model_overrides_project_model(self):
        self.configure(self.project, "provider/project-model")
        result = self.run_build("pi", "--project-root", str(self.project),
                                model="provider/environment-model")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_pi_model("provider/environment-model")

    def test_default_project_is_bundle_root_not_current_directory(self):
        self.configure(self.bundle, "provider/bundle-model")
        self.configure(self.project, "provider/project-model")
        result = self.run_build("pi")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_pi_model("provider/bundle-model")

    def test_generation_is_independent_of_current_directory(self):
        self.configure(self.bundle, "provider/bundle-model")
        self.configure(self.project, "provider/project-model")
        result = self.run_build("all", "--project-root", str(self.project), cwd=self.bundle)
        self.assertEqual(result.returncode, 0, result.stderr)
        first = {p.relative_to(self.output): p.read_bytes() for p in self.output.glob("*/*.md")}
        result = self.run_build("all", "--project-root", str(self.project), cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        second = {p.relative_to(self.output): p.read_bytes() for p in self.output.glob("*/*.md")}
        self.assertEqual(first, second)
        self.assert_pi_model("provider/project-model")


if __name__ == "__main__":
    unittest.main()
