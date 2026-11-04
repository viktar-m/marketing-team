"""Tests for hq.py. Run: python3 -m unittest test_hq"""
import re
import tempfile
import unittest
from pathlib import Path

import hq

BASE = "https://github.com/acme/site/blob/main/"


def workspace(root: Path) -> Path:
    (root / ".git").mkdir()
    ws = root / "marketing"
    for d in ("briefs", "reports", "strategy", "calendar", "dashboards"):
        (ws / d).mkdir(parents=True)
    (ws / "briefs/2026-11-03-home page.md").write_text("---\nstatus: ready\nto: seo-agent\n---\n# Brief: Home\n")
    (ws / "reports/2026-11-04-audit.md").write_text("# Audit\n")
    (ws / "strategy/seo.md").write_text("Next review: 2027-01-01\n")
    (ws / "calendar/2026-w45.md").write_text("# Week 45\n")
    (ws / "dashboards/ai-visibility.html").write_text("<html></html>")
    (ws / "ai-visibility").mkdir()
    (ws / "ai-visibility/latest-metrics.json").write_text(
        '{"own": "Us", "brands": {"Us": {"share_of_voice": 0.2}}, "window": ["2026-10-28", "2026-11-04"]}')
    return ws


def hrefs(page: str) -> list[str]:
    return re.findall(r"href='([^']*)'", page)


class LinkBase(unittest.TestCase):
    def test_local_links_stay_relative(self):
        with tempfile.TemporaryDirectory() as d:
            ws = workspace(Path(d))
            page = hq.build(ws, ws / "dashboards/hq.html", hq.dt.date(2026, 11, 4))
            links = hrefs(page)
            self.assertIn("../briefs/2026-11-03-home page.md", links)
            self.assertIn("ai-visibility.html", links)
            self.assertNotIn("target=", page)
            for h in links:
                self.assertTrue((ws / "dashboards" / h).exists(), h)

    def test_link_base_makes_file_links_absolute_and_resolvable(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ws = workspace(root)
            page = hq.build(ws, root / "elsewhere/hq.html", hq.dt.date(2026, 11, 4), BASE)
            links = hrefs(page)
            self.assertIn("ai-visibility.html", links)  # sibling dashboard stays relative
            absolute = [h for h in links if h != "ai-visibility.html"]
            self.assertEqual(len(absolute), 4)  # brief, report, strategy, calendar
            for h in absolute:
                self.assertTrue(h.startswith(BASE + "marketing/"), h)
                path = hq.urllib.parse.unquote(h[len(BASE):])
                self.assertTrue((root / path).is_file(), path)
            self.assertIn("home%20page.md", page)
            self.assertEqual(page.count("target='_blank' rel='noopener'"), 4)


if __name__ == "__main__":
    unittest.main()
