"""Tests for init_workspace.py. Run: python3 -m unittest test_init_workspace"""
import tempfile
import unittest
from pathlib import Path

import init_workspace as iw


class InitWorkspace(unittest.TestCase):
    def test_creates_everything_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            iw.main(["--root", d, "--product", "Test Co", "--website", "https://test.example"])
            root = Path(d)
            for rel in ["CLAUDE.md", "README.md", ".gitignore", ".github/workflows/ai-visibility.yml",
                        "marketing/brand-brief.md", "marketing/hub.html", "marketing/index.md", "marketing/queue/.gitkeep", "marketing/web/.gitkeep"]:
                self.assertTrue((root / rel).exists(), rel)
            claude = (root / "CLAUDE.md").read_text()
            self.assertIn("Test Co (https://test.example)", claude)
            self.assertNotIn("{{", claude + (root / "README.md").read_text())
            self.assertIn("# schedule:", (root / ".github/workflows/ai-visibility.yml").read_text())
            (root / "marketing/brand-brief.md").write_text("my edits")
            iw.main(["--root", d, "--product", "Other"])
            self.assertEqual((root / "marketing/brand-brief.md").read_text(), "my edits")

    def test_schedule_on(self):
        with tempfile.TemporaryDirectory() as d:
            iw.main(["--root", d, "--product", "X", "--schedule", "on"])
            wf = (Path(d) / ".github/workflows/ai-visibility.yml").read_text()
            self.assertIn('\n  schedule:\n    - cron:', wf)


if __name__ == "__main__":
    unittest.main()
