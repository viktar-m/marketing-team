"""Tests for hq.py. Run: python3 -m unittest test_hq"""
import json
import re
import tempfile
import unittest
from pathlib import Path

import hq

BRIEF = """---
status: in-progress
to: seo-agent
from: strategist
type: page
priority: high   # comment
date: 2026-11-03
due: 2026-11-17
campaign:
---

# Brief: Ünïcode page </script>

See [SEO strategy](../strategy/seo.md#rules), [notes](../notes/deep.md) and [site](https://example.com).

| a | b |
|---|---|
| 1 | 2 |
"""


def make_ws(root: Path) -> Path:
    (root / ".git").mkdir()
    ws = root / "marketing"
    for d in ("briefs", "strategy", "reports", "notes", "dashboards"):
        (ws / d).mkdir(parents=True)
    (ws / "briefs" / "2026-11-03-ünïcode page.md").write_text(BRIEF)
    (ws / "strategy" / "seo.md").write_text("# SEO\n\nNext review: 2027-01-01\n\nMore in [deep](../notes/deep.md).\n")
    (ws / "notes" / "deep.md").write_text("# Deep\n\nNot linked from the dashboard.\n[two hops](other.md)\n")
    (ws / "notes" / "other.md").write_text("# Other\n")
    (ws / "reports" / "2026-11-04-ai-visibility.md").write_text("# Report\n")
    (ws / "reports" / "2026-11-04-chart.html").write_text("<p>x</p>")
    return ws


class Hq(unittest.TestCase):
    def build(self, link_base="https://github.com/o/r/blob/main"):
        self.tmp = tempfile.TemporaryDirectory()
        ws = make_ws(Path(self.tmp.name))
        out = ws / "dashboards" / "hq.html"
        hq.main(["--workspace", str(ws), "--out", str(out), "--today", "2026-11-04"]
                + (["--link-base", link_base] if link_base else []))
        page = out.read_text()
        m = re.search(r'<script type="application/json" id="hq-docs">(.*?)</script>', page, re.S)
        return page, json.loads(m.group(1))

    def tearDown(self):
        self.tmp.cleanup()

    def test_docs_embedded_and_links_rewritten(self):
        page, data = self.build()
        docs = data["docs"]
        self.assertEqual(data["linkBase"], "https://github.com/o/r/blob/main/")
        brief = docs["doc-2026-11-03-unicode-page"]
        self.assertEqual(brief["path"], "marketing/briefs/2026-11-03-ünïcode page.md")
        self.assertEqual(brief["title"], "Ünïcode page </script>")
        self.assertEqual(brief["meta"], {"status": "in-progress", "to": "seo-agent", "from": "strategist", "type": "page",
                                         "priority": "high", "date": "2026-11-03", "due": "2026-11-17"})
        self.assertTrue(brief["body"].startswith("See [SEO strategy]"))  # front matter and H1 removed
        self.assertEqual(brief["github"],
                         "https://github.com/o/r/blob/main/marketing/briefs/2026-11-03-%C3%BCn%C3%AFcode%20page.md")
        self.assertIn('href="#doc-2026-11-03-unicode-page" data-doc="doc-2026-11-03-unicode-page"', page)
        self.assertIn("doc-seo", docs)
        self.assertIn("doc-deep", docs)             # linked from an embedded doc: one hop
        self.assertNotIn("doc-other", docs)         # two hops: opens on GitHub instead
        self.assertNotIn(".md'", page)
        self.assertNotIn('.md"', page.split('<script type="application/json"')[0])
        self.assertIn('href="https://github.com/o/r/blob/main/marketing/reports/2026-11-04-chart.html"', page)
        self.assertEqual(page.count("</script>"), 3)  # JSON, marked, panel script; content can't close a tag
        self.assertIn("cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js", page)

    def test_without_link_base(self):
        page, data = self.build(link_base=None)
        self.assertIsNone(data["linkBase"])
        self.assertIsNone(data["docs"]["doc-seo"]["github"])
        self.assertIn('href="../reports/2026-11-04-chart.html"', page)


if __name__ == "__main__":
    unittest.main()
