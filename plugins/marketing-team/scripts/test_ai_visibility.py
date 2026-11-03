"""Tests for ai_visibility.py. Run: python3 -m unittest test_ai_visibility (from this folder)."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

import ai_visibility as av

BRANDS = [
    {"name": "Acme Pantry", "aliases": ["AcmePantry"], "domain": "acmepantry.example", "is_own": True},
    {"name": "Competitor A", "aliases": [], "domain": "competitor-a.example", "is_own": False},
    {"name": "Mealie", "aliases": [], "domain": "", "is_own": False},
]
for b in BRANDS:
    b["names"] = [b["name"], *b["aliases"]]


class Parsers(unittest.TestCase):
    def test_openai(self):
        r = {"output": [
            {"type": "web_search_call", "status": "completed"},
            {"type": "message", "content": [{"type": "output_text", "text": "Try Acme Pantry.",
                                             "annotations": [{"type": "url_citation", "url": "https://acmepantry.example/a",
                                                              "title": "A"}]}]}]}
        text, cites = av.parse_openai(r)
        self.assertEqual(text, "Try Acme Pantry.")
        self.assertEqual(cites[0]["url"], "https://acmepantry.example/a")

    def test_perplexity_search_results_and_fallback(self):
        r = {"choices": [{"message": {"content": "x"}}], "search_results": [{"url": "https://a.com", "title": "t"}]}
        self.assertEqual(av.parse_perplexity(r)[1][0]["url"], "https://a.com")
        r = {"choices": [{"message": {"content": "x"}}], "citations": ["https://b.com"]}
        self.assertEqual(av.parse_perplexity(r)[1][0]["url"], "https://b.com")

    def test_gemini_uses_title_as_domain(self):
        r = {"candidates": [{"content": {"parts": [{"text": "hi"}]}, "groundingMetadata": {"groundingChunks": [
            {"web": {"uri": "https://vertexaisearch.cloud.google.com/redirect/xyz", "title": "competitor-a.example"}}]}}]}
        text, cites = av.parse_gemini(r)
        self.assertEqual(av.domain_of(cites[0]), "competitor-a.example")

    def test_anthropic(self):
        r = {"content": [{"type": "server_tool_use"}, {"type": "text", "text": "See Mealie.",
                                                        "citations": [{"url": "https://www.mealie.io/x"}]}]}
        text, cites = av.parse_anthropic(r)
        self.assertEqual(text, "See Mealie.")
        self.assertEqual(av.domain_of(cites[0]), "mealie.io")


class Analyse(unittest.TestCase):
    def test_mentions_rank_and_citations(self):
        text = "Competitor A is popular, but AcmePantry starts from your fridge. acme pantry is free."
        cites = [{"url": "https://www.acmepantry.example/features"}, {"url": "https://blog.competitor-a.example/x"}]
        res = {r["brand"]: r for r in av.analyse(text, cites, BRANDS)}
        self.assertEqual(res["Competitor A"]["rank"], 1)
        self.assertEqual(res["Acme Pantry"]["rank"], 2)
        self.assertEqual(res["Acme Pantry"]["mentioned"], 1)
        self.assertEqual(res["Acme Pantry"]["cited"], 1)
        self.assertEqual(res["Competitor A"]["cited"], 1)  # subdomain counts
        self.assertEqual(res["Mealie"]["mentioned"], 0)
        self.assertEqual(res["Mealie"]["cited"], 0)  # no domain, never cited

    def test_no_partial_word_match(self):
        brands = [{"name": "Acme", "aliases": [], "domain": "", "is_own": True, "names": ["Acme"]}]
        res = av.analyse("Acmeville and acme-tools", [], brands)
        self.assertEqual(res[0]["mentioned"], 0)


class EndToEnd(unittest.TestCase):
    def test_demo_report(self):
        with tempfile.TemporaryDirectory() as d:
            av.main(["demo", "--dir", d])
            out = Path(d) / "dash.html"
            av.main(["report", "--dir", d, "--out", str(out)])
            page = out.read_text()
            self.assertIn("AI visibility — Acme Pantry", page)
            self.assertIn("<svg", page)
            m = json.loads((Path(d) / "latest-metrics.json").read_text())
            sov = sum(v["share_of_voice"] for v in m["brands"].values())
            self.assertAlmostEqual(sov, 1.0, places=6)

    def test_run_without_keys_exits_cleanly(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            av.main(["demo", "--dir", d])
            saved = {k: os.environ.pop(k) for k in list(os.environ) if k.endswith("_API_KEY")}
            try:
                self.assertEqual(av.main(["run", "--dir", d]), 2)
            finally:
                os.environ.update(saved)

    def test_run_with_mocked_engine(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            av.main(["demo", "--dir", d])
            for f in ("history.csv", "citations.csv", "sentiment.csv"):
                (Path(d) / f).unlink()
            orig = av.PROVIDERS["openai"]
            av.PROVIDERS["openai"] = lambda p, e, k: ("Acme Pantry and Competitor A both work.",
                                                      [{"url": "https://acmepantry.example"}])
            os.environ["OPENAI_API_KEY"] = "test"
            try:
                self.assertEqual(av.main(["run", "--dir", d, "--engines", "chatgpt", "--date", "2026-11-01"]), 0)
            finally:
                av.PROVIDERS["openai"] = orig
                del os.environ["OPENAI_API_KEY"]
            rows = list(csv.DictReader(open(Path(d) / "history.csv")))
            own = [r for r in rows if r["is_own"] == "1"]
            self.assertEqual(len(own), 5)
            self.assertTrue(all(r["mentioned"] == "1" and r["rank"] == "1" and r["cited"] == "1" for r in own))


if __name__ == "__main__":
    unittest.main()
