import os
from pathlib import Path
import shutil
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENAMED_SKILLS = {
    "init-dev-flow": "flow-init", "grill-with-docs": "flow-clarify",
    "to-spec": "flow-spec", "to-plan": "flow-plan", "to-tickets": "flow-todo",
    "implement": "flow-do", "find": "flow-status", "amend": "flow-amend",
    "simplify": "flow-simplify", "diagnosing-bugs": "flow-debug",
    "e2e-test": "flow-e2e", "to-api-contract": "flow-api", "export-session": "flow-export",
}


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
                        expected += "\n\n" + (self.bundle / "_agents/language-policy.md").read_text()
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

    def test_project_language_is_not_baked_into_global_agent_prompts(self):
        language = self.project / "docs/agents/language.md"
        language.parent.mkdir(parents=True)
        outputs = []
        for interaction, artifact in (("zh-CN", "en"), ("en", "zh-CN")):
            with self.subTest(interaction=interaction, artifact=artifact):
                language.write_text(f"# Workflow language\ninteraction_language: {interaction}\n"
                                    f"artifact_language: {artifact}\n")
                before = language.read_bytes()
                result = self.run_build("all", "--project-root", str(self.project))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(language.read_bytes(), before)
                outputs.append({p.relative_to(self.output): p.read_bytes()
                                for p in self.output.glob("*/*.md")})
        self.assertEqual(outputs[0], outputs[1])

    def test_missing_language_policy_does_not_write_outputs(self):
        (self.bundle / "_agents/language-policy.md").unlink()
        result = self.run_build("all")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertFalse((self.root / "fallback").exists())


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dev-flow-install-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bundle = self.root / "skill bundle"
        shutil.copytree(ROOT, self.bundle,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store", "tests"))
        self.home = self.root / "user home"
        self.project = self.root / "target project"
        self.project.mkdir()
        self.skills = sorted(path.parent.name for path in self.bundle.glob("*/SKILL.md"))
        self.locations = {"pi": ".pi/agent/skills", "claude-code": ".claude/skills",
                          "codex": ".agents/skills"}

    def install(self, *args, home=None, model=None):
        env = os.environ.copy()
        # Keep both the explicit destination and HOME isolated, even on regressions.
        env["HOME"] = str(home or self.home)
        env.pop("DEV_FLOW_MODEL", None)
        if model is not None:
            env["DEV_FLOW_MODEL"] = model
        return subprocess.run(
            ["bash", str(self.bundle / "install.sh"), *args,
             "--home", str(home or self.home)],
            cwd=self.project, env=env, text=True, capture_output=True,
        )

    def backup_files(self):
        return sorted((self.home / ".local/share/dev-flow-skills/backups").rglob("SKILL.md"))

    def test_install_targets_include_shared_resources_and_agents(self):
        for target in (*self.locations, "all"):
            with self.subTest(target=target):
                home = self.root / target
                result = self.install(target, home=home)
                self.assertEqual(result.returncode, 0, result.stderr)
                for tool, location in self.locations.items():
                    folder = home / location
                    if target not in (tool, "all"):
                        self.assertFalse(folder.exists())
                        continue
                    for name in (*self.skills, "_agents"):
                        self.assertTrue((folder / name).is_symlink(), folder / name)
                        self.assertEqual((folder / name).resolve(), self.bundle / name)
                    self.assertEqual((folder / "flow-plan/../_agents/workflow-contract.md").read_bytes(),
                                     (self.bundle / "_agents/workflow-contract.md").read_bytes())
                for tool, location in (("pi", ".pi/agent/agents"),
                                       ("claude-code", ".claude/agents")):
                    files = sorted((home / location).glob("*.md"))
                    self.assertEqual(len(files), 5 if target in (tool, "all") else 0)
                    for path in files:
                        header = path.read_text().partition("\n---\n")[0]
                        self.assertNotIn("\nmodel:", header)
                self.assertFalse((self.project / "docs").exists())

    def test_repeated_install_and_source_updates(self):
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".local").exists())
        (self.bundle / "flow-plan/SKILL.md").write_text("updated skill\n")
        for location in self.locations.values():
            self.assertEqual((self.home / location / "flow-plan/SKILL.md").read_text(), "updated skill\n")
        updated = b"\nUpdated scout instructions.\n"
        (self.bundle / "_agents/scout.prompt.md").write_bytes(updated)
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        language = (self.bundle / "_agents/language-policy.md").read_bytes()
        for location in (".pi/agent/agents", ".claude/agents"):
            expected = b"\n" + updated + b"\n\n" + language
            self.assertTrue((self.home / location / "scout.md").read_bytes().endswith(expected))
        backups = list((self.home / ".local").rglob("scout.md"))
        self.assertEqual(len(backups), 2)
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.home / ".local").rglob("scout.md"))), 2)

    def test_agent_updates_keep_user_frontmatter_and_backup_previous_body(self):
        header = ("---\r\nname: scout\r\nmodel: user/chosen-model\r\n"
                  "tools:\r\n  - Read\r\n  - Bash\r\ncustom: |\r\n  user value\r\n---\r\n")
        previous = (header + "\r\nold prompt\r\n").encode()
        for location in (".pi/agent/agents", ".claude/agents"):
            path = self.home / location / "scout.md"
            path.parent.mkdir(parents=True)
            path.write_bytes(previous)
            path.chmod(0o600)
        managed = self.home / ".cc-switch/agents/scout.md"
        managed.parent.mkdir(parents=True)
        shutil.move(str(self.home / ".claude/agents/scout.md"), str(managed))
        (self.home / ".claude/agents/scout.md").symlink_to(managed)
        result = self.install("all", model="different/installation-model")
        self.assertEqual(result.returncode, 0, result.stderr)
        body = ((self.bundle / "_agents/scout.prompt.md").read_bytes() + b"\n\n"
                + (self.bundle / "_agents/language-policy.md").read_bytes())
        for location in (".pi/agent/agents", ".claude/agents"):
            path = self.home / location / "scout.md"
            self.assertEqual(path.read_bytes(), header.encode() + b"\n" + body)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertFalse(path.is_symlink())
        self.assertEqual(managed.read_bytes(), previous)
        backups = list((self.home / ".local").rglob("scout.md"))
        self.assertEqual(len(backups), 2)
        self.assertTrue(all(path.read_bytes() == previous for path in backups))
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.home / ".local").rglob("scout.md"))), 2)

    def test_migration_backs_up_copies_and_links_without_editing_their_targets(self):
        old_bundles = [self.home / location for location in
                       (".pi/agent/skills/dev-flow-skills", ".codex/skills/dev-flow-skills")]
        for old in old_bundles:
            old.mkdir(parents=True)
            for name in self.skills:
                (old / name).mkdir()
                (old / name / "SKILL.md").write_text("old bundled skill\n")
            (old / "_agents").mkdir()
        managed = self.home / ".cc-switch/skills/flow-plan"
        managed.mkdir(parents=True)
        (managed / "SKILL.md").write_text("managed skill\n")
        for folder in (".agents/skills", ".claude/skills", ".codex/skills"):
            path = self.home / folder / "flow-plan"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(managed, target_is_directory=True)
        unrelated = self.home / ".claude/skills/user-only/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("user skill\n")
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        for old in old_bundles:
            self.assertFalse(old.exists(), old)
        self.assertFalse((self.home / ".codex/skills/flow-plan").exists())
        self.assertEqual((managed / "SKILL.md").read_text(), "managed skill\n")
        self.assertEqual(unrelated.read_text(), "user skill\n")
        self.assertEqual(len(self.backup_files()), len(old_bundles) * len(self.skills))
        backup_links = [p for p in (self.home / ".local").rglob("*") if p.is_symlink()]
        self.assertEqual(len(backup_links), 3)
        self.assertTrue(all(p.resolve() == managed for p in backup_links))

    def test_dry_run_and_invalid_input_leave_destinations_untouched(self):
        old = self.home / ".claude/skills/flow-plan/SKILL.md"
        old.parent.mkdir(parents=True)
        old.write_text("previous skill\n")
        result = self.install("all", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(old.read_text(), "previous skill\n")
        self.assertFalse((self.home / ".pi").exists())
        self.assertFalse((self.home / ".local").exists())
        for args in ((), ("unknown",), ("pi", "--unknown"),
                     ("pi", "--project-root", str(self.root / "missing"))):
            with self.subTest(args=args):
                result = self.install(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(old.read_text(), "previous skill\n")
                self.assertFalse((self.home / ".pi").exists())

    def test_renamed_skills_back_up_owned_links_and_copies(self):
        self.assertEqual(self.skills, sorted(RENAMED_SKILLS.values()))
        previous = {}
        managed_sources = {}
        for location_index, location in enumerate([*self.locations.values(), ".codex/skills"]):
            for index, (old, new) in enumerate(RENAMED_SKILLS.items()):
                path = self.home / location / old
                path.parent.mkdir(parents=True, exist_ok=True)
                data = (self.bundle / new / "SKILL.md").read_bytes()
                data = data.replace(f"name: {new}\n".encode(), f"name: {old}\n".encode(), 1)
                for old_command, new_command in RENAMED_SKILLS.items():
                    data = data.replace(f"/{new_command}".encode(), f"/{old_command}".encode())
                kind = (index + location_index) % 3
                if kind == 0:
                    path.symlink_to(self.bundle / old, target_is_directory=True)
                elif kind == 1:
                    path.mkdir()
                    (path / "SKILL.md").write_bytes(data)
                else:
                    managed = self.home / ".cc-switch/skills" / old
                    managed.mkdir(parents=True, exist_ok=True)
                    (managed / "SKILL.md").write_bytes(data)
                    managed_sources[managed] = data
                    path.symlink_to(managed, target_is_directory=True)
                previous[path] = os.readlink(path) if path.is_symlink() else data
        result = self.install("all", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".local").exists())
        self.assertFalse((self.home / ".pi/agent/agents").exists())
        for path, data in previous.items():
            if isinstance(data, str):
                self.assertEqual(os.readlink(path), data)
            else:
                self.assertEqual((path / "SKILL.md").read_bytes(), data)
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        backup_directory = self.home / ".local/share/dev-flow-skills/backups"
        self.assertTrue(backup_directory.is_dir())
        backups = list(backup_directory.iterdir())
        self.assertEqual(len(backups), 1)
        for path, data in previous.items():
            self.assertFalse(path.exists() or path.is_symlink(), path)
            backup = backups[0] / path.relative_to(self.home)
            if isinstance(data, str):
                self.assertEqual(os.readlink(backup), data)
            else:
                self.assertEqual((backup / "SKILL.md").read_bytes(), data)
        for managed, data in managed_sources.items():
            self.assertEqual((managed / "SKILL.md").read_bytes(), data)
        for location in self.locations.values():
            for name in self.skills:
                self.assertEqual((self.home / location / name).resolve(), self.bundle / name)
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("安装内容已是当前版本。", result.stdout)
        self.assertEqual(list(backups[0].parent.iterdir()), backups)

    def test_bundles_with_pre_rename_names_are_retired(self):
        bundles = []
        for location in [*self.locations.values(), ".codex/skills"]:
            bundle = self.home / location / "dev-flow-skills"
            (bundle / "_agents").mkdir(parents=True)
            for old in RENAMED_SKILLS:
                (bundle / old).mkdir()
                (bundle / old / "SKILL.md").write_text("previous bundled skill\n")
            bundles.append(bundle)
        result = self.install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        for bundle in bundles:
            self.assertFalse(bundle.exists(), bundle)
        self.assertEqual(len(self.backup_files()), len(bundles) * len(RENAMED_SKILLS))

    def test_rename_respects_target_selection_and_unrelated_same_names(self):
        for target in [*self.locations, "all"]:
            with self.subTest(target=target):
                home = self.root / target
                unrelated = home / "personal skill"
                unrelated.mkdir(parents=True)
                data = b"---\nname: find\ndescription: Personal file search.\n---\n\nMy instructions.\n"
                (unrelated / "SKILL.md").write_bytes(data)
                for location in [*self.locations.values(), ".codex/skills"]:
                    directory = home / location
                    directory.mkdir(parents=True)
                    (directory / "to-plan").symlink_to(self.bundle / "to-plan", target_is_directory=True)
                    (directory / "find").symlink_to(unrelated, target_is_directory=True)
                result = self.install(target, home=home)
                self.assertEqual(result.returncode, 0, result.stderr)
                for tool, location in {**self.locations, "legacy-codex": ".codex/skills"}.items():
                    old = home / location / "to-plan"
                    selected = target == "all" or target == tool or (target == "codex" and tool == "legacy-codex")
                    self.assertEqual(old.is_symlink(), not selected, old)
                    personal = home / location / "find"
                    self.assertTrue(personal.is_symlink(), personal)
                    self.assertEqual((personal / "SKILL.md").read_bytes(), data)
                self.assertEqual((unrelated / "SKILL.md").read_bytes(), data)

    def test_invalid_existing_agent_is_reported_before_any_installation(self):
        path = self.home / ".claude/agents/scout.md"
        path.parent.mkdir(parents=True)
        path.write_text("user prompt without frontmatter\n")
        result = self.install("all")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(path), result.stderr)
        self.assertFalse((self.home / ".pi").exists())
        self.assertFalse((self.home / ".claude/skills").exists())
        self.assertEqual(path.read_text(), "user prompt without frontmatter\n")

    def test_project_model_is_applied_only_to_new_agents(self):
        config = self.project / "docs/agents/execution-mode.md"
        config.parent.mkdir(parents=True)
        config.write_text("# Execution mode: subagent\n\n**基础模型**: user/project-model\n")
        before = config.read_bytes()
        result = self.install("pi", "--project-root", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (self.home / ".pi/agent/agents").glob("*.md"):
            self.assertIn("\nmodel: user/project-model\n", path.read_text())
        self.assertEqual(config.read_bytes(), before)

    def test_source_checkout_is_never_moved_or_replaced(self):
        original = self.bundle
        for target, location in (("pi", ".pi/agent/skills/dev-flow-skills"),
                                 ("codex", ".agents/skills"),
                                 ("codex", ".codex/skills"),
                                 ("codex", ".codex/skills/dev-flow-skills")):
            with self.subTest(location=location):
                self.home = self.root / location.replace("/", "-")
                self.bundle = self.home / location
                shutil.copytree(original, self.bundle)
                before = (self.bundle / "flow-plan/SKILL.md").read_bytes()
                result = self.install(target)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("独立目录", result.stderr)
                self.assertEqual((self.bundle / "flow-plan/SKILL.md").read_bytes(), before)
                self.assertFalse((self.home / ".local").exists())

    def test_linked_parent_directory_is_not_modified(self):
        managed = self.root / "managed skills"
        (managed / "flow-plan").mkdir(parents=True)
        original = managed / "flow-plan/SKILL.md"
        original.write_text("managed skill\n")
        path = self.home / ".claude/skills"
        path.parent.mkdir(parents=True)
        path.symlink_to(managed, target_is_directory=True)
        result = self.install("all")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(path), result.stderr)
        self.assertEqual(original.read_text(), "managed skill\n")
        self.assertFalse((self.home / ".pi").exists())
        self.assertFalse((self.home / ".local").exists())

    def test_linked_backup_directory_is_rejected_before_installation(self):
        backup_directory = self.home / ".local/share/dev-flow-skills/backups"
        backup_directory.parent.mkdir(parents=True)
        backup_directory.symlink_to(self.bundle, target_is_directory=True)
        before = set(self.bundle.iterdir())
        old = self.home / ".claude/skills/flow-plan/SKILL.md"
        old.parent.mkdir(parents=True)
        old.write_text("previous skill\n")
        result = self.install("all")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(backup_directory), result.stderr)
        self.assertEqual(old.read_text(), "previous skill\n")
        self.assertEqual(set(self.bundle.iterdir()), before)
        self.assertFalse((self.home / ".pi").exists())


if __name__ == "__main__":
    unittest.main()
