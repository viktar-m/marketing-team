"""Tests for hub.py: areas, stages, goals and brief/result merging."""
import tempfile
import unittest
from pathlib import Path

import hub


def write(ws: Path, rel: str, text: str) -> None:
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


class HubTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        write(self.ws, "goals.md", "# Goals\n\n## Site sells the offer\nHomepage live.\n- **By:** 2026-11-30\n\n## More inquiries\n- By: 2027-04-30\n")
        write(self.ws, "queue/homepage.md", "---\ntitle: Homepage refresh\ntype: brief\nto: web-content-agent\ngoal: site-sells-the-offer\npriority: high\nstatus: done\ndue: 2026-11-17\noutput: marketing/web/homepage.md\n---\nBrief body\n")
        write(self.ws, "queue/posts.md", "---\ntitle: Posts\ntype: brief\nto: social-agent\nstatus: in-progress\n---\n")
        write(self.ws, "queue/keywords.md", "---\ntitle: Keywords\ntype: brief\nto: seo-agent\n---\n")
        write(self.ws, "web/homepage.md", "---\ntitle: Homepage refresh\nagent: web-content-agent\nstatus: draft\nneeds_you:\n  - Pick a headline\n---\n# Homepage refresh\n")
        write(self.ws, "research/battlecard-x.md", "---\ntitle: Battlecard\nstatus: approved\n---\n")
        write(self.ws, "brand-brief.md", "# Brand brief: Acme\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_goals(self):
        goals = hub.load_goals(self.ws)
        self.assertEqual([g["key"] for g in goals], ["site-sells-the-offer", "more-inquiries"])
        self.assertEqual([g["by"] for g in goals], ["2026-11-30", "2027-04-30"])

    def test_tasks(self):
        tasks, briefs = hub.collect(self.ws, hub.load_goals(self.ws))
        by = {t["path"]: t for t in tasks}
        self.assertNotIn("queue/homepage.md", by)  # merged into its result
        home = by["web/homepage.md"]
        self.assertEqual((home["area"], home["stage"], home["goal"], home["due"], home["brief"]),
                         ("content", "needs-you", "site-sells-the-offer", "2026-11-17", "queue--homepage"))
        self.assertEqual((by["queue/posts.md"]["area"], by["queue/posts.md"]["stage"]), ("social", "in-progress"))
        self.assertEqual((by["queue/keywords.md"]["area"], by["queue/keywords.md"]["stage"]), ("seo", "todo"))
        self.assertEqual((by["research/battlecard-x.md"]["area"], by["research/battlecard-x.md"]["stage"]), ("gtm", "done"))
        self.assertEqual((by["brand-brief.md"]["area"], by["brand-brief.md"]["stage"]), ("strategy", "done"))
        self.assertTrue(any(b.get("merged") for b in briefs))

    def test_build(self):
        out = self.ws / "hub.html"
        out.write_text(hub.build(self.ws, out, hub.dt.date(2026, 11, 6)))
        html = out.read_text()
        self.assertIn("Site sells the offer", html)
        self.assertNotIn("__DATA__", html)
        self.assertIn("| needs-you | content | Homepage refresh | site-sells-the-offer |", (self.ws / "index.md").read_text())


if __name__ == "__main__":
    unittest.main()
