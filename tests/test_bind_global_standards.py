"""Exercise real Git snapshots and global discovery links in temporary directories."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("bind_global_standards", Path(__file__).resolve().parents[1] / "scripts/bind_global_standards.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.dest, self.state = (self.root / p for p in ("repo", "skills", "state"))
        self.repo.mkdir()
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        for domain, name in zip(MODULE.DOMAINS, ("release-check", "restore-check")):
            directory = self.repo / domain / name
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(f"---\nname: {name}\ndescription: fixture\n---\nfirst\n")
        self.run_git("add", "skills")
        self.run_git("commit", "-qm", "first")
        self.first = self.run_git("rev-parse", "HEAD")

    def run_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True).strip()

    def install(self, ref=None, apply=True):
        return MODULE.bind(self.repo, ref or self.first, self.dest, self.state, apply)

    def test_preview_has_no_filesystem_side_effects(self):
        self.install(apply=False)
        self.assertFalse(self.dest.exists())
        self.assertFalse(self.state.exists())

    def test_pinned_install_ignores_source_dirty_files_and_reapplies(self):
        self.install()
        source = self.repo / MODULE.DOMAINS[0] / "release-check/SKILL.md"
        source.write_text(source.read_text() + "uncommitted\n")
        self.assertNotIn("uncommitted", (self.dest / "release-check/SKILL.md").read_text())
        self.assertEqual(self.install()["status"], "verified")

    def test_update_and_explicit_rollback(self):
        self.install()
        source = self.repo / MODULE.DOMAINS[0] / "release-check/SKILL.md"
        source.write_text(source.read_text() + "second\n")
        self.run_git("commit", "-qam", "second")
        second = self.run_git("rev-parse", "HEAD")
        self.install(second)
        self.assertIn("second", (self.dest / "release-check/SKILL.md").read_text())
        self.install(self.first)
        self.assertNotIn("second", (self.dest / "release-check/SKILL.md").read_text())
        self.assertEqual(json.loads((self.state / "lock.json").read_text())["commit"], self.first)

    def test_unmanaged_directory_conflict_prevents_partial_install(self):
        existing = self.dest / "restore-check"
        existing.mkdir(parents=True)
        (existing / "keep.txt").write_text("preserve")
        with self.assertRaisesRegex(ValueError, "unmanaged"):
            self.install()
        self.assertFalse((self.dest / "release-check").exists())
        self.assertEqual((existing / "keep.txt").read_text(), "preserve")

    def test_modified_snapshot_or_link_is_detected(self):
        self.install()
        (self.dest / "release-check/SKILL.md").write_text("drift")
        with self.assertRaisesRegex(ValueError, "local changes"):
            MODULE.check_install(self.state)

    def test_relative_cross_domain_reference_survives_install(self):
        self.install()
        reference = self.dest / "release-check/../../operations-management/restore-check/SKILL.md"
        self.assertTrue(reference.is_file())

    def test_moving_ref_rejected(self):
        with self.assertRaisesRegex(ValueError, "full 40-character"):
            self.install("HEAD")


if __name__ == "__main__":
    unittest.main()
