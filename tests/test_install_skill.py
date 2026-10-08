"""Check standalone installation, conflict preservation, and preflight behavior."""

import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install_skill", ROOT / "scripts/install_skill.py")
install_skill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install_skill)


class SkillInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "bundle"
        shutil.copytree(ROOT / "skills/long-horizon-agents", self.source,
                        ignore=shutil.ignore_patterns("__pycache__"))
        # Keep these tests usable while the skill instructions are being authored.
        if not (self.source / "SKILL.md").exists():
            (self.source / "SKILL.md").write_text(
                "---\nname: long-horizon-agents\ndescription: Test bundle\n---\n", encoding="utf-8")
        self.discovery = self.root / "discovery"
        self.installed = self.discovery / "long-horizon-agents"

    def install(self, **kwargs):
        return install_skill.install(self.discovery, source_root=self.source, **kwargs)

    def snapshot(self):
        return {str(path.relative_to(self.discovery)): path.read_bytes()
                for path in self.discovery.rglob("*") if path.is_file()}

    def test_installed_initializer_works_without_source_repository(self):
        outcomes = self.install()
        self.assertTrue(all(line.startswith("CREATED ") for line in outcomes))
        self.assertEqual({path.name for path in self.discovery.iterdir()}, {"long-horizon-agents"})
        shutil.rmtree(self.source)
        project = self.root / "independent-project"
        result = subprocess.run(
            [sys.executable, str(self.installed / "scripts/init_project.py"),
             "--target", str(project), "--name", "Independent Project"],
            cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Independent Project", (project / "docs/agent/MISSION.md").read_text(encoding="utf-8"))
        self.assertTrue((project / ".agent/roles/planner.md").is_file())
        self.assertTrue((project / ".agent/codex/setup.md").is_file())
        self.assertIn("$long-horizon-agents", (project / "AGENTS.md").read_text(encoding="utf-8"))

    def test_matching_install_is_idempotent_and_keeps_extra_files(self):
        self.install()
        (self.installed / "local-notes.md").write_bytes(b"User's additional instructions\n")
        before = self.snapshot()
        outcomes = self.install()
        self.assertTrue(all(line.startswith("SKIPPED ") for line in outcomes))
        self.assertEqual(self.snapshot(), before)

    def test_modified_skill_is_preserved_and_conflict_prevents_partial_writes(self):
        self.install()
        changed = self.installed / "scripts/init_project.py"
        changed.write_bytes(b"User's custom initializer\n")
        missing = self.installed / "assets/templates/project/MISSION.md"
        missing.unlink()
        before = self.snapshot()
        with self.assertRaisesRegex(install_skill.InstallError, "Existing skill differs.*--skills-dir"):
            self.install()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(missing.exists())

    def test_dry_run_creates_nothing_and_preserves_existing_install(self):
        outcomes = self.install(dry_run=True)
        self.assertTrue(any(line.startswith("CREATED ") for line in outcomes))
        self.assertFalse(self.discovery.exists())
        self.install()
        before = self.snapshot()
        self.install(dry_run=True)
        self.assertEqual(self.snapshot(), before)

    def test_incomplete_source_does_not_create_destination(self):
        (self.source / "assets/roles/executor.md").unlink()
        with self.assertRaisesRegex(install_skill.InstallError, "Incomplete skill bundle"):
            self.install()
        self.assertFalse(self.discovery.exists())

    def test_directory_conflict_does_not_partially_install(self):
        collision = self.installed / "scripts/init_project.py"
        collision.mkdir(parents=True)
        with self.assertRaisesRegex(install_skill.InstallError, "Existing skill differs"):
            self.install()
        self.assertFalse((self.installed / "SKILL.md").exists())

    def test_root_initializer_cli_uses_bundled_assets(self):
        project = self.root / "compatibility-project"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/init_project.py"), "--target", str(project)],
            cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / "docs/agent/MISSION.md").is_file())

    def test_cli_default_and_dry_run(self):
        stdout = io.StringIO()
        with patch.object(install_skill, "install", return_value=["CREATED SKILL.md"]) as call:
            with contextlib.redirect_stdout(stdout):
                status = install_skill.main(["--dry-run"])
        self.assertEqual(status, 0)
        call.assert_called_once_with(Path.home() / ".agents" / "skills", True)
        self.assertIn("DRY RUN", stdout.getvalue())

    def test_cli_conflict_returns_actionable_error(self):
        stderr = io.StringIO()
        with patch.object(install_skill, "install", side_effect=install_skill.InstallError("Choose another --skills-dir")):
            with contextlib.redirect_stderr(stderr):
                status = install_skill.main(["--skills-dir", str(self.discovery)])
        self.assertEqual(status, 1)
        self.assertIn("ERROR: Choose another --skills-dir", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
