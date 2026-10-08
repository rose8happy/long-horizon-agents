"""Preservation and preflight checks for the additive initializer."""

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "long-horizon-agents" / "scripts" / "init_project.py"
SPEC = importlib.util.spec_from_file_location("init_project", SCRIPT)
init_project = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = init_project
SPEC.loader.exec_module(init_project)


class InitializerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.target = self.root / "my-project"
        for source, _ in init_project._sources():
            path = self.source / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# {{PROJECT_NAME}}\n" + source + "\n", encoding="utf-8")

    def initialize(self, **kwargs):
        return init_project.initialize(self.target, source_root=self.source, **kwargs)

    def snapshot(self, root=None):
        root = self.target if root is None else root
        return {str(path.relative_to(root)): path.read_bytes()
                for path in root.rglob("*") if path.is_file()}

    def make_link(self, path, destination, directory=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.symlink_to(destination, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlinks unavailable: {error}")

    def test_complete_install_replaces_name_and_maps_sources(self):
        outcomes = self.initialize(name="Example Project")
        self.assertEqual(len(outcomes), 14)
        self.assertTrue(all(line.startswith("CREATED ") for line in outcomes))
        for source, destination in init_project._sources():
            self.assertEqual((self.target / destination).read_text(encoding="utf-8"),
                             "# Example Project\n" + source + "\n")
        readme = (self.target / "docs/agent/README.md").read_text(encoding="utf-8")
        self.assertIn("Example Project", readme)
        self.assertIn("../../.agent/codex/setup.md", readme)
        self.assertEqual((self.target / "AGENTS.md").read_bytes().count(init_project.START), 1)
        instructions = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("invoke $long-horizon-agents", instructions)
        self.assertIn("If the skill is unavailable", instructions)

    def test_default_name_and_idempotence_preserve_modified_files(self):
        self.initialize()
        mission = self.target / "docs/agent/MISSION.md"
        self.assertIn("my-project", mission.read_text(encoding="utf-8"))
        mission.write_bytes(b"customized mission\n")
        before = self.snapshot()
        outcomes = self.initialize(name="Different name")
        self.assertTrue(all(line.startswith("SKIPPED ") for line in outcomes))
        self.assertEqual(self.snapshot(), before)

    def test_existing_marked_block_is_preserved_without_upgrade(self):
        self.target.mkdir()
        original = init_project.START + b"\nCustom older workflow\n" + init_project.END + b"\n"
        (self.target / "AGENTS.md").write_bytes(original)
        self.initialize()
        self.assertEqual((self.target / "AGENTS.md").read_bytes(), original)

    def test_project_name_quotes_keep_configuration_valid(self):
        source = self.source / "templates/project/agent.config.example.toml"
        source.write_text('name = "{{PROJECT_NAME}}"\n', encoding="utf-8")
        self.initialize(name='Research "A" \\ B\nNext')
        actual = (self.target / ".agent/agent.config.example.toml").read_text(encoding="utf-8")
        self.assertEqual(actual, 'name = "Research \\"A\\" \\\\ B\\nNext"\n')

    def test_arbitrary_agents_and_existing_template_are_preserved(self):
        self.target.mkdir()
        original = b"Existing instructions\r\n\xff\nNo final newline"
        (self.target / "AGENTS.md").write_bytes(original)
        modified = self.target / "docs/agent/PLAN.md"
        modified.parent.mkdir(parents=True)
        modified.write_bytes(b"A user's plan, unrelated to the template")
        self.initialize()
        self.assertTrue((self.target / "AGENTS.md").read_bytes().startswith(original + b"\n\n"))
        self.assertEqual(modified.read_bytes(), b"A user's plan, unrelated to the template")
        before = self.snapshot()
        self.initialize()
        self.assertEqual(self.snapshot(), before)

    def test_dry_run_does_not_create_missing_target_or_change_existing(self):
        outcomes = self.initialize(dry_run=True)
        self.assertTrue(any(line.startswith("CREATED ") for line in outcomes))
        self.assertFalse(self.target.exists())
        self.initialize()
        before = self.snapshot()
        self.initialize(dry_run=True)
        self.assertEqual(self.snapshot(), before)

    def test_malformed_markers_preflight_without_partial_install(self):
        for content in (init_project.START, init_project.END,
                        init_project.END + init_project.START,
                        init_project.START * 2 + init_project.END):
            with self.subTest(content=content):
                self.target.mkdir(exist_ok=True)
                (self.target / "AGENTS.md").write_bytes(content)
                with self.assertRaisesRegex(init_project.InitError, "Malformed.*markers"):
                    self.initialize()
                self.assertEqual(list(self.target.iterdir()), [self.target / "AGENTS.md"])

    def test_destination_directory_collision_does_not_partially_install(self):
        collision = self.target / ".agent/codex/executor-wake.md"
        collision.mkdir(parents=True)
        before = self.snapshot()
        with self.assertRaisesRegex(init_project.InitError, "regular file"):
            self.initialize()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.target / "docs").exists())

    def test_parent_file_collision_and_target_file_are_rejected(self):
        self.target.mkdir()
        (self.target / ".agent").write_bytes(b"existing file")
        with self.assertRaisesRegex(init_project.InitError, "Expected a directory"):
            self.initialize()
        self.assertFalse((self.target / "docs").exists())
        with self.assertRaisesRegex(init_project.InitError, "Expected a directory"):
            init_project.initialize(self.target / ".agent", source_root=self.source)

    def test_symlinked_parent_cannot_escape_target(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep").write_bytes(b"unchanged")
        self.make_link(self.target / "docs", outside, directory=True)
        with self.assertRaisesRegex(init_project.InitError, "Unsafe link"):
            self.initialize()
        self.assertEqual(self.snapshot(outside), {"keep": b"unchanged"})
        self.assertFalse((self.target / ".agent").exists())

    def test_symlinked_target_ancestor_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.root / "linked"
        self.make_link(link, outside, directory=True)
        with self.assertRaisesRegex(init_project.InitError, "Unsafe link"):
            init_project.initialize(link / "new-project", source_root=self.source)
        self.assertEqual(list(outside.iterdir()), [])

    def test_existing_and_dangling_file_symlinks_are_rejected(self):
        outside = self.root / "existing-file"
        outside.write_bytes(b"preserve this file")
        for filename in ("AGENTS.md", "docs/agent/MISSION.md"):
            for destination in (outside, self.root / "missing-file"):
                with self.subTest(filename=filename, destination=destination.name):
                    link = self.target / filename
                    self.make_link(link, destination)
                    with self.assertRaisesRegex(init_project.InitError, "Unsafe link"):
                        self.initialize()
                    self.assertFalse((self.root / "missing-file").exists())
                    self.assertEqual(outside.read_bytes(), b"preserve this file")
                    link.unlink()

    def test_missing_source_does_not_create_target(self):
        (self.source / "adapters/codex/executor-wake.md").unlink()
        with self.assertRaisesRegex(init_project.InitError, "Missing source template"):
            self.initialize()
        self.assertFalse(self.target.exists())

    def test_cli_reports_actionable_error_and_nonzero_status(self):
        self.target.write_bytes(b"file, not directory")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = init_project.main(["--target", str(self.target)])
        self.assertEqual(status, 1)
        self.assertIn("ERROR: Expected a directory", stderr.getvalue())

    def test_cli_dry_run_output(self):
        stdout = io.StringIO()
        with patch.object(init_project, "initialize", return_value=["CREATED AGENTS.md"]) as call:
            with contextlib.redirect_stdout(stdout):
                status = init_project.main(["--target", str(self.target), "--name", "Chosen", "--dry-run"])
        self.assertEqual(status, 0)
        call.assert_called_once_with(self.target, "Chosen", True)
        self.assertIn("DRY RUN", stdout.getvalue())
        self.assertIn("CREATED AGENTS.md", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
