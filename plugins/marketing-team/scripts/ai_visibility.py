#!/usr/bin/env python3
"""AI visibility tracker for the marketing team.

Asks AI answer engines (ChatGPT via the OpenAI API, Perplexity, Gemini, Claude) the
questions your audience asks, then records whether your brand and your competitors
are mentioned, in what order, and which sources are cited.

Commands
  run     Query every engine that has an API key set and append results to the history.
  report  Build a self-contained HTML dashboard from the history.
  demo    Write synthetic history for trying the dashboard (no API calls).

Usage
  python3 ai_visibility.py run    --dir marketing/ai-visibility
  python3 ai_visibility.py report --dir marketing/ai-visibility --out marketing/dashboards/ai-visibility.html
  python3 ai_visibility.py demo   --dir /tmp/ai-vis-demo

API keys are read from environment variables only (never from files in the repo):
  OPENAI_API_KEY, PERPLEXITY_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY
Engines without a key are skipped. Standard library only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_ENGINES = {
    "chatgpt": {"provider": "openai", "model": "gpt-5-mini", "key_env": "OPENAI_API_KEY"},
    "perplexity": {"provider": "perplexity", "model": "sonar", "key_env": "PERPLEXITY_API_KEY"},
    "gemini": {"provider": "gemini", "model": "gemini-2.5-flash", "key_env": "GEMINI_API_KEY"},
    "claude": {"provider": "anthropic", "model": "claude-sonnet-5-5", "key_env": "ANTHROPIC_API_KEY"},
}

HISTORY_FIELDS = ["date", "engine", "model", "prompt_id", "run", "brand", "is_own", "mentioned", "rank", "cited"]
CITATION_FIELDS = ["date", "engine", "prompt_id", "run", "domain", "url", "brand"]


# ---------------------------------------------------------------- config

def load_config(d: Path) -> dict:
    p = d / "config.json"
    if not p.exists():
        sys.exit(f"No config at {p}. The ai-visibility skill creates it from the brand brief.")
    cfg = json.loads(p.read_text())
    for key in ("brand", "prompts"):
        if key not in cfg:
            sys.exit(f"config.json is missing '{key}'")
    cfg.setdefault("competitors", [])
    cfg.setdefault("runs_per_prompt", 1)
    engines = {}
    for name, base in DEFAULT_ENGINES.items():
        engines[name] = {**base, **cfg.get("engines", {}).get(name, {})}
    for name, e in cfg.get("engines", {}).items():
        if name not in engines:
            engines[name] = e
    cfg["engines"] = engines
    return cfg


def brands_of(cfg: dict) -> list[dict]:
    out = [{**cfg["brand"], "is_own": True}]
    out += [{**c, "is_own": False} for c in cfg["competitors"]]
    for b in out:
        b.setdefault("aliases", [])
        b["names"] = [b["name"], *b["aliases"]]
        b["domain"] = (b.get("domain") or "").lower().removeprefix("www.")
    return out


# ---------------------------------------------------------------- engines

def _post(url: str, payload: dict, headers: dict, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            last = f"HTTP {e.code}: {body}"
            if e.code in (429, 500, 502, 503, 529):
                retry_after = e.headers.get("retry-after") if e.headers else None
                wait = float(retry_after) if retry_after and retry_after.replace(".", "").isdigit() else 5 * 2 ** attempt
                time.sleep(min(wait, 90))
                continue
            raise RuntimeError(last) from None
        except urllib.error.URLError as e:
            last = str(e)
            time.sleep(2 ** attempt * 3)
    raise RuntimeError(last or "request failed")


def ask_openai(prompt: str, e: dict, key: str) -> tuple[str, list[dict]]:
    payload = {"model": e["model"], "input": prompt, "tools": [{"type": e.get("search_tool", "web_search")}]}
    r = _post("https://api.openai.com/v1/responses", payload, {"Authorization": f"Bearer {key}"})
    return parse_openai(r)


def parse_openai(r: dict) -> tuple[str, list[dict]]:
    texts, cites = [], []
    for item in r.get("output", []):
        if item.get("type") != "message":
            continue
        for c in item.get("content", []):
            if c.get("type") == "output_text":
                texts.append(c.get("text", ""))
                for a in c.get("annotations", []):
                    if a.get("type") == "url_citation" and a.get("url"):
                        cites.append({"url": a["url"], "title": a.get("title", "")})
    return "\n".join(texts), cites


def ask_perplexity(prompt: str, e: dict, key: str) -> tuple[str, list[dict]]:
    payload = {"model": e["model"], "messages": [{"role": "user", "content": prompt}]}
    r = _post("https://api.perplexity.ai/chat/completions", payload, {"Authorization": f"Bearer {key}"})
    return parse_perplexity(r)


def parse_perplexity(r: dict) -> tuple[str, list[dict]]:
    text = (r.get("choices") or [{}])[0].get("message", {}).get("content", "")
    cites = [{"url": s.get("url"), "title": s.get("title", "")} for s in r.get("search_results", []) if s.get("url")]
    if not cites:
        cites = [{"url": u, "title": ""} for u in r.get("citations", []) if isinstance(u, str)]
    return text, cites


def ask_gemini(prompt: str, e: dict, key: str) -> tuple[str, list[dict]]:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(e['model'])}"
           f":generateContent")
    payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
    r = _post(url, payload, {"x-goog-api-key": key})
    return parse_gemini(r)


def parse_gemini(r: dict) -> tuple[str, list[dict]]:
    cand = (r.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    cites = []
    for ch in cand.get("groundingMetadata", {}).get("groundingChunks", []):
        w = ch.get("web", {})
        if w.get("uri"):
            # Gemini returns redirect URLs; the title holds the source domain.
            cites.append({"url": w["uri"], "title": w.get("title", ""), "domain_hint": w.get("title", "")})
    return text, cites


def ask_anthropic(prompt: str, e: dict, key: str) -> tuple[str, list[dict]]:
    payload = {"model": e["model"], "max_tokens": 2048, "messages": [{"role": "user", "content": prompt}],
               "tools": [{"type": e.get("search_tool", "web_search_20250305"), "name": "web_search", "max_uses": 5}]}
    r = _post("https://api.anthropic.com/v1/messages", payload,
              {"x-api-key": key, "anthropic-version": "2023-06-01"})
    return parse_anthropic(r)


def parse_anthropic(r: dict) -> tuple[str, list[dict]]:
    texts, cites = [], []
    for b in r.get("content", []):
        if b.get("type") == "text":
            texts.append(b.get("text", ""))
            for c in b.get("citations") or []:
                if c.get("url"):
                    cites.append({"url": c["url"], "title": c.get("title", "")})
    return "".join(texts), cites


PROVIDERS = {"openai": ask_openai, "perplexity": ask_perplexity, "gemini": ask_gemini, "anthropic": ask_anthropic}


# ---------------------------------------------------------------- analysis

def domain_of(c: dict) -> str:
    hint = (c.get("domain_hint") or "").lower()
    if hint and "." in hint and " " not in hint:
        return hint.removeprefix("www.")
    host = urllib.parse.urlparse(c.get("url", "")).netloc.lower()
    return host.removeprefix("www.")


def analyse(text: str, cites: list[dict], brands: list[dict]) -> list[dict]:
    """Per brand: mentioned?, rank of first mention among tracked brands, cited?"""
    first = {}
    for b in brands:
        pos = None
        for n in b["names"]:
            m = re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", text, flags=re.IGNORECASE)
            if m and (pos is None or m.start() < pos):
                pos = m.start()
        if pos is not None:
            first[b["name"]] = pos
    order = sorted(first, key=first.get)
    domains = {domain_of(c) for c in cites}
    rows = []
    for b in brands:
        d = b["domain"]
        cited = bool(d) and any(x == d or x.endswith("." + d) for x in domains)
        rows.append({
            "brand": b["name"], "is_own": int(b["is_own"]),
            "mentioned": int(b["name"] in first),
            "rank": order.index(b["name"]) + 1 if b["name"] in first else "",
            "cited": int(cited),
        })
    return rows


def append_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- run

def cmd_run(args) -> int:
    d = Path(args.dir)
    cfg = load_config(d)
    brands = brands_of(cfg)
    today = args.date or dt.date.today().isoformat()
    active = {n: e for n, e in cfg["engines"].items() if e.get("enabled", True) and os.environ.get(e["key_env"])}
    if args.engines:
        active = {n: e for n, e in active.items() if n in args.engines.split(",")}
    if not active:
        print("No engine has an API key set. Set OPENAI_API_KEY (and optionally PERPLEXITY_API_KEY, "
              "GEMINI_API_KEY, ANTHROPIC_API_KEY).", file=sys.stderr)
        return 2
    raw_path = d / "data" / f"{today}.jsonl"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if raw_path.exists():  # a re-run on the same day only fills the gaps
        for line in raw_path.read_text().splitlines():
            try:
                r = json.loads(line)
                done.add((r["engine"], r["prompt_id"], int(r["run"])))
            except (ValueError, KeyError):
                pass
    err_path = d / "data" / f"{today}-errors.jsonl"
    hist, cit, errors, skipped = [], [], 0, 0
    with raw_path.open("a") as raw, err_path.open("a") as errlog:
        for name, e in active.items():
            ask = PROVIDERS[e["provider"]]
            key = os.environ[e["key_env"]]
            for p in cfg["prompts"]:
                for run in range(1, int(cfg["runs_per_prompt"]) + 1):
                    if (name, p["id"], run) in done:
                        skipped += 1
                        continue
                    time.sleep(float(cfg.get("pause_seconds", 2)))
                    try:
                        text, cites = ask(p["prompt"], e, key)
                    except Exception as ex:  # keep going; one failure shouldn't lose the run
                        errors += 1
                        msg = str(ex).replace(key, "***")[:400]
                        print(f"[{name}] {p['id']}: {msg}", file=sys.stderr)
                        errlog.write(json.dumps({"time": dt.datetime.utcnow().isoformat(timespec="seconds"),
                                                 "engine": name, "prompt_id": p["id"], "run": run,
                                                 "error": msg}) + "\n")
                        continue
                    res = analyse(text, cites, brands)
                    raw.write(json.dumps({"date": today, "engine": name, "model": e["model"], "prompt_id": p["id"],
                                          "prompt": p["prompt"], "run": run, "answer": text, "citations": cites,
                                          "results": res}) + "\n")
                    for r in res:
                        hist.append({"date": today, "engine": name, "model": e["model"], "prompt_id": p["id"],
                                     "run": run, **r})
                    for c in cites:
                        dom = domain_of(c)
                        owner = next((b["name"] for b in brands if b["domain"] and
                                      (dom == b["domain"] or dom.endswith("." + b["domain"]))), "")
                        cit.append({"date": today, "engine": name, "prompt_id": p["id"], "run": run,
                                    "domain": dom, "url": c.get("url", ""), "brand": owner})
                    print(f"[{name}] {p['id']} run {run}: "
                          f"{'mentioned' if res[0]['mentioned'] else 'not mentioned'}, {len(cites)} citations")
    append_csv(d / "history.csv", HISTORY_FIELDS, hist)
    append_csv(d / "citations.csv", CITATION_FIELDS, cit)
    if err_path.exists() and err_path.stat().st_size == 0:
        err_path.unlink()
    print(f"Done: {len(hist) // max(len(brands), 1)} answers recorded, {skipped} already done, {errors} errors"
          + (f" (see {err_path})" if errors else "") + ".")
    return 1 if errors and not hist and not skipped else 0


# ---------------------------------------------------------------- metrics

def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def metrics(hist: list[dict], since: str | None = None) -> dict:
    rows = [r for r in hist if not since or r["date"] >= since]
    answers = {(r["date"], r["engine"], r["prompt_id"], r["run"]) for r in rows}
    by_brand = defaultdict(lambda: {"mentioned": 0, "cited": 0, "rank_sum": 0, "first": 0})
    own = None
    for r in rows:
        b = by_brand[r["brand"]]
        if r["is_own"] == "1":
            own = r["brand"]
        if r["mentioned"] == "1":
            b["mentioned"] += 1
            b["rank_sum"] += int(r["rank"])
            b["first"] += r["rank"] == "1"
        if r["cited"] == "1":
            b["cited"] += 1
    total_mentions = sum(b["mentioned"] for b in by_brand.values()) or 1
    n = len(answers) or 1
    out = {}
    for name, b in by_brand.items():
        out[name] = {
            "visibility": b["mentioned"] / n,
            "citation_rate": b["cited"] / n,
            "share_of_voice": b["mentioned"] / total_mentions,
            "avg_rank": (b["rank_sum"] / b["mentioned"]) if b["mentioned"] else None,
            "first_mention_rate": b["first"] / n,
        }
    return {"answers": len(answers), "own": own, "brands": out}


def daily_series(hist: list[dict], metric: str, smooth: int = 7) -> dict[str, list[tuple[str, float]]]:
    """Metric per day; with `smooth` > 1, each point covers the trailing `smooth` days."""
    dates = sorted({r["date"] for r in hist})
    series = defaultdict(list)
    for i, day in enumerate(dates):
        span = set(dates[max(0, i - smooth + 1): i + 1])
        m = metrics([r for r in hist if r["date"] in span])
        for b, v in m["brands"].items():
            series[b].append((day, v[metric]))
    return series


# ---------------------------------------------------------------- report

PALETTE_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
PALETTE_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]


def esc(s) -> str:
    return html.escape(str(s))


def pct(v) -> str:
    return "–" if v is None else f"{v * 100:.0f}%"


def line_chart(series: dict, order: list[str], w=720, h=260) -> str:
    pad_l, pad_r, pad_t, pad_b = 44, 120, 16, 28
    dates = sorted({d for s in series.values() for d, _ in s})
    if not dates:
        return "<p class='muted'>No data yet.</p>"
    vmax = max([v for s in series.values() for _, v in s] + [0.05])
    vmax = min(1.0, (int(vmax * 5) + 1) / 5)  # round up to a multiple of 20% so quarter ticks are clean
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    x = (lambda i: pad_l + (iw * i / (len(dates) - 1) if len(dates) > 1 else iw / 2))
    y = (lambda v: pad_t + ih - ih * v / vmax)
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" class="chart" aria-label="Trend chart">']
    for k in range(0, 5):
        v = vmax * k / 4
        out.append(f'<line x1="{pad_l}" x2="{pad_l + iw}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/>'
                   f'<text x="{pad_l - 6}" y="{y(v) + 4:.1f}" class="axis" text-anchor="end">{v * 100:.0f}%</text>')
    step = max(1, len(dates) // 6)
    for i, day in enumerate(dates):
        if i % step == 0 or i == len(dates) - 1:
            out.append(f'<text x="{x(i):.1f}" y="{h - 8}" class="axis" text-anchor="middle">{esc(day[5:])}</text>')
    labels = []
    for idx, name in enumerate(order):
        pts = [(dates.index(d), v) for d, v in series.get(name, [])]
        if not pts:
            continue
        cls = f"s{idx + 1}"
        path = " ".join(f"{'M' if j == 0 else 'L'}{x(i):.1f},{y(v):.1f}" for j, (i, v) in enumerate(pts))
        out.append(f'<path d="{path}" class="line {cls}"/>')
        for i, v in pts:
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="4" class="dot {cls}">'
                       f'<title>{esc(name)} · {esc(dates[i])}: {v * 100:.0f}%</title></circle>')
        labels.append((y(pts[-1][1]), name, cls))
    labels.sort()
    last_y = -99
    for ly, name, cls in labels:
        ly = max(ly, last_y + 14)
        last_y = ly
        out.append(f'<text x="{pad_l + iw + 8}" y="{ly + 4:.1f}" class="lbl">'
                   f'<tspan class="sw {cls}">■</tspan> {esc(name)}</text>')
    out.append("</svg>")
    return "".join(out)


def bar_chart(items: list[tuple[str, float, str]], w=720, fmt=pct) -> str:
    if not items:
        return "<p class='muted'>No data yet.</p>"
    row, pad_l = 30, 190
    h = row * len(items) + 8
    vmax = max([v for _, v, _ in items] + [1e-9])
    iw = w - pad_l - 60
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" class="chart" aria-label="Bar chart">']
    for i, (label, v, cls) in enumerate(items):
        yy = 4 + i * row
        bw = max(2, iw * v / vmax)
        out.append(f'<text x="{pad_l - 8}" y="{yy + 17}" class="lbl" text-anchor="end">{esc(label[:28])}</text>'
                   f'<rect x="{pad_l}" y="{yy + 5}" width="{bw:.1f}" height="16" rx="4" class="bar {cls}">'
                   f'<title>{esc(label)}: {fmt(v)}</title></rect>'
                   f'<text x="{pad_l + bw + 6:.1f}" y="{yy + 17}" class="val">{fmt(v)}</text>')
    out.append("</svg>")
    return "".join(out)


def cmd_report(args) -> int:
    d = Path(args.dir)
    hist = read_csv(d / "history.csv")
    cites = read_csv(d / "citations.csv")
    sentiment = read_csv(d / "sentiment.csv")
    if not hist:
        sys.exit("No history yet. Run `run` first (or `demo` to try the dashboard).")
    cfg_path = d / "config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    last = max(r["date"] for r in hist)
    days = args.days
    since = (dt.date.fromisoformat(last) - dt.timedelta(days=days - 1)).isoformat()
    prev_since = (dt.date.fromisoformat(since) - dt.timedelta(days=days)).isoformat()
    window = [r for r in hist if r["date"] >= since]
    prev = [r for r in hist if prev_since <= r["date"] < since]
    m, mp = metrics(window), metrics(prev) if prev else None
    own = m["own"]
    comp = sorted((b for b in m["brands"] if b != own), key=lambda b: -m["brands"][b]["share_of_voice"])
    order = [own] + comp[:7]
    if len(comp) > 7:
        order_note = f"{len(comp) - 7} smaller competitors omitted from charts (see table)."
    else:
        order_note = ""
    cls = {b: f"s{i + 1}" for i, b in enumerate(order)}

    def delta(metric):
        if not mp or own not in mp["brands"]:
            return ""
        a, b = m["brands"][own][metric], mp["brands"][own][metric]
        diff = (a - b) * 100
        sign = "▲" if diff > 0.5 else "▼" if diff < -0.5 else "■"
        return f'<span class="delta">{sign} {diff:+.0f} pts vs previous {days} days</span>'

    o = m["brands"].get(own, {})
    tiles = [
        ("Visibility", pct(o.get("visibility")), "answers that mention us", delta("visibility")),
        ("Share of voice", pct(o.get("share_of_voice")), "of all tracked-brand mentions", delta("share_of_voice")),
        ("Cited as a source", pct(o.get("citation_rate")), "answers citing our domain", delta("citation_rate")),
        ("Average position", f"{o['avg_rank']:.1f}" if o.get("avg_rank") else "–",
         "order of first mention (1 = first)", ""),
    ]
    smooth = 7 if len({r["date"] for r in window}) > 10 else 1
    sov_series = daily_series(window, "share_of_voice", smooth)
    vis_series = daily_series(window, "visibility", smooth)

    # per engine
    engines = sorted({r["engine"] for r in window})
    eng_items = []
    for e in engines:
        me = metrics([r for r in window if r["engine"] == e])
        eng_items.append((e, me["brands"].get(own, {}).get("visibility", 0), "s1"))

    # prompts table
    prompts = {p["id"]: p for p in cfg.get("prompts", [])}
    ptable = []
    for pid in sorted({r["prompt_id"] for r in window}):
        rs = [r for r in window if r["prompt_id"] == pid]
        mp_ = metrics(rs)
        winner = max(mp_["brands"].items(), key=lambda kv: kv[1]["visibility"])
        ptable.append((pid, prompts.get(pid, {}).get("prompt", pid), mp_["brands"].get(own, {}),
                       winner[0] if winner[1]["visibility"] > 0 else "–"))

    # citations
    wc = [c for c in cites if c["date"] >= since]
    dom_counts = Counter(c["domain"] for c in wc)
    top_domains = [(dname, n, cls.get(next((c["brand"] for c in wc if c["domain"] == dname and c["brand"]), ""), "neutral"))
                   for dname, n in dom_counts.most_common(12)]

    # sentiment
    sent_html = "<p class='muted'>No sentiment review yet. The ai-visibility skill adds one when it reviews the answers.</p>"
    ws = [s for s in sentiment if s.get("date", "") >= since]
    if ws:
        rows = []
        for b in order:
            c = Counter(s["sentiment"] for s in ws if s["brand"] == b)
            tot = sum(c.values())
            if tot:
                rows.append(f"<tr><td><span class='sw {cls[b]}'>■</span> {esc(b)}</td>"
                            f"<td>{c['positive']}</td><td>{c['neutral']}</td><td>{c['negative']}</td>"
                            f"<td>{pct(c['positive'] / tot)}</td></tr>")
        sent_html = ("<table><thead><tr><th>Brand</th><th>Positive</th><th>Neutral</th><th>Negative</th>"
                     "<th>% positive</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")

    def brand_row(b, v):
        rank = "–" if v["avg_rank"] is None else f"{v['avg_rank']:.1f}"
        us = " (us)" if b == own else ""
        return (f"<tr><td><span class='sw {cls.get(b, 'neutral')}'>■</span> {esc(b)}{us}</td>"
                f"<td>{pct(v['visibility'])}</td><td>{pct(v['share_of_voice'])}</td>"
                f"<td>{pct(v['citation_rate'])}</td><td>{rank}</td></tr>")

    brand_rows = "".join(brand_row(b, v) for b, v in
                         sorted(m["brands"].items(), key=lambda kv: -kv[1]["share_of_voice"]))
    prompt_rows = "".join(
        f"<tr><td title='{esc(pid)}'>{esc(text)}</td><td>{pct(v.get('visibility'))}</td>"
        f"<td>{pct(v.get('citation_rate'))}</td><td>{esc(win)}</td></tr>"
        for pid, text, v, win in sorted(ptable, key=lambda t: (t[2].get("visibility") or 0)))

    css_vars = "".join(f"--s{i + 1}:{c};" for i, c in enumerate(PALETTE_LIGHT))
    css_dark = "".join(f"--s{i + 1}:{c};" for i, c in enumerate(PALETTE_DARK))
    series_css = "".join(f".s{i}{{color:var(--s{i});stroke:var(--s{i});fill:var(--s{i})}}" for i in range(1, 9))
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI visibility — {esc(own)}</title>
<style>
.viz-root{{color-scheme:light;--bg:#f6f6f4;--surface:#fcfcfb;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;--grid:#e6e5e1;--border:#e2e1dc;--neutral:#b5b4ae;{css_vars}}}
@media (prefers-color-scheme:dark){{:root:where(:not([data-theme="light"])) .viz-root{{color-scheme:dark;--bg:#111110;--surface:#1a1a19;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--grid:#2c2c2a;--border:#30302d;--neutral:#5f5e5a;{css_dark}}}}}
:root[data-theme="dark"] .viz-root{{color-scheme:dark;--bg:#111110;--surface:#1a1a19;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--grid:#2c2c2a;--border:#30302d;--neutral:#5f5e5a;{css_dark}}}
*{{box-sizing:border-box}} body{{margin:0}}
.viz-root{{background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;padding:24px;min-height:100vh}}
.wrap{{max-width:1080px;margin:0 auto}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:15px;margin:0 0 12px}} .sub,.muted{{color:var(--text2)}} .muted{{font-size:13px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:20px 0}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px}}
.tile .k{{color:var(--text2);font-size:13px}} .tile .v{{font-size:32px;font-weight:650;margin:4px 0}} .tile .h{{color:var(--muted);font-size:12px}}
.delta{{display:block;font-size:12px;color:var(--text2);margin-top:4px}}
.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:12px;margin-bottom:12px}}
.chart{{width:100%;height:auto;display:block}}
.chart .grid{{stroke:var(--grid);stroke-width:1}} .chart .axis{{fill:var(--muted);font-size:11px}}
.chart .line{{fill:none;stroke-width:2}} .chart .dot{{stroke:var(--surface);stroke-width:2}}
.chart .lbl{{fill:var(--text2);font-size:12px}} .chart .val{{fill:var(--text2);font-size:12px}}
.chart .bar.neutral{{fill:var(--neutral)}}
{series_css}
.chart .lbl .sw{{stroke:none}}
table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{text-align:left;padding:8px 6px;border-bottom:1px solid var(--border)}}
th{{color:var(--text2);font-weight:600}} td .sw{{stroke:none}}
.foot{{color:var(--muted);font-size:12px;margin-top:16px}}
.toggle{{float:right;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:6px 10px;cursor:pointer}}
</style></head>
<body><div class="viz-root"><div class="wrap">
<button class="toggle" onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'">Light / dark</button>
<h1>AI visibility — {esc(own)}</h1>
<div class="sub">How AI answer engines answer your audience's questions · last {days} days to {esc(last)} · {m['answers']} answers across {len(engines)} engine(s): {esc(', '.join(engines))}</div>
<div class="tiles">{''.join(f'<div class="card tile"><div class="k">{k}</div><div class="v">{v}</div><div class="h">{h}</div>{dl}</div>' for k, v, h, dl in tiles)}</div>
<div class="grid2">
<div class="card"><h2>Share of voice over time</h2><p class="muted">{'7-day rolling average' if smooth > 1 else 'Daily'}</p>{line_chart(sov_series, order)}</div>
<div class="card"><h2>Visibility over time</h2><p class="muted">{'7-day rolling average' if smooth > 1 else 'Daily'}</p>{line_chart(vis_series, order)}</div>
</div>
<div class="grid2">
<div class="card"><h2>Our visibility by engine</h2>{bar_chart(eng_items)}</div>
<div class="card"><h2>Most-cited sources</h2>{bar_chart(top_domains, fmt=lambda v: str(int(v)))}<p class="muted">Coloured = a tracked brand's domain; grey = third-party sources worth earning mentions on.</p></div>
</div>
<div class="card" style="margin-bottom:12px"><h2>Brands compared</h2>
<table><thead><tr><th>Brand</th><th>Visibility</th><th>Share of voice</th><th>Cited</th><th>Avg position</th></tr></thead><tbody>{brand_rows}</tbody></table>
<p class="muted">{esc(order_note)}</p></div>
<div class="card" style="margin-bottom:12px"><h2>Questions — weakest first</h2>
<table><thead><tr><th>Question</th><th>Our visibility</th><th>We're cited</th><th>Most visible brand</th></tr></thead><tbody>{prompt_rows}</tbody></table></div>
<div class="card"><h2>Sentiment</h2>{sent_html}</div>
<div class="foot">Visibility = share of answers that mention the brand. Share of voice = the brand's mentions ÷ all tracked-brand mentions. Cited = the brand's own domain appears among the answer's sources. Answers come from the engines' APIs with web search on; consumer apps can differ (personalisation, location, model version).</div>
</div></div></body></html>"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    summary = {"window": [since, last], "answers": m["answers"], "own": own, "brands": m["brands"],
               "previous": mp["brands"] if mp else None}
    (d / "latest-metrics.json").write_text(json.dumps(summary, indent=2))
    print(f"Dashboard written to {out}")
    return 0


# ---------------------------------------------------------------- demo

def cmd_demo(args) -> int:
    d = Path(args.dir)
    d.mkdir(parents=True, exist_ok=True)
    cfg = {
        "brand": {"name": "Acme Pantry", "aliases": ["AcmePantry"], "domain": "acmepantry.example"},
        "competitors": [{"name": "Competitor A", "domain": "competitor-a.example"},
                        {"name": "Competitor B", "domain": "competitor-b.example"}],
        "prompts": [{"id": f"q{i}", "prompt": q} for i, q in enumerate([
            "What's the best meal planning app for families?",
            "How can I plan meals using what's already in my fridge?",
            "Which app makes a shopping list from a meal plan?",
            "How do I stop wasting food at home?",
            "Is there a meal planning app for a shared household?"], 1)],
        "runs_per_prompt": 1,
    }
    (d / "config.json").write_text(json.dumps(cfg, indent=2))
    for f in ("history.csv", "citations.csv", "sentiment.csv"):
        (d / f).unlink(missing_ok=True)
    rnd = random.Random(7)
    brands = brands_of(load_config(d))
    start = dt.date.today() - dt.timedelta(days=27)
    hist, cit, sent = [], [], []
    for k in range(28):
        day = (start + dt.timedelta(days=k)).isoformat()
        for eng, base in (("chatgpt", 0.25), ("perplexity", 0.4)):
            for p in cfg["prompts"]:
                lift = k / 27 * 0.25
                probs = {"Acme Pantry": base + lift, "Competitor A": 0.6, "Competitor B": 0.35}
                present = [b for b in probs if rnd.random() < probs[b]]
                rnd.shuffle(present)
                for b in brands:
                    mentioned = b["name"] in present
                    cited = mentioned and rnd.random() < (0.5 if b["is_own"] else 0.4)
                    hist.append({"date": day, "engine": eng, "model": "demo", "prompt_id": p["id"], "run": 1,
                                 "brand": b["name"], "is_own": int(b["is_own"]), "mentioned": int(mentioned),
                                 "rank": present.index(b["name"]) + 1 if mentioned else "", "cited": int(cited)})
                    if cited:
                        cit.append({"date": day, "engine": eng, "prompt_id": p["id"], "run": 1,
                                    "domain": b["domain"], "url": f"https://{b['domain']}/", "brand": b["name"]})
                    if mentioned and k >= 21:
                        sent.append({"date": day, "engine": eng, "prompt_id": p["id"], "brand": b["name"],
                                     "sentiment": rnd.choices(["positive", "neutral", "negative"], [5, 4, 1])[0],
                                     "note": ""})
                for dom in rnd.sample(["reddit.com", "nytimes.com", "wikipedia.org", "eatingwell.com",
                                       "youtube.com", "consumerreports.org"], 2):
                    cit.append({"date": day, "engine": eng, "prompt_id": p["id"], "run": 1, "domain": dom,
                                "url": f"https://{dom}/", "brand": ""})
    append_csv(d / "history.csv", HISTORY_FIELDS, hist)
    append_csv(d / "citations.csv", CITATION_FIELDS, cit)
    append_csv(d / "sentiment.csv", ["date", "engine", "prompt_id", "brand", "sentiment", "note"], sent)
    print(f"Demo data written to {d}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--dir", default="marketing/ai-visibility")
    r.add_argument("--engines", help="comma-separated subset, e.g. chatgpt,perplexity")
    r.add_argument("--date", help="override the date (YYYY-MM-DD)")
    rp = sub.add_parser("report")
    rp.add_argument("--dir", default="marketing/ai-visibility")
    rp.add_argument("--out", default="marketing/dashboards/ai-visibility.html")
    rp.add_argument("--days", type=int, default=28)
    dm = sub.add_parser("demo")
    dm.add_argument("--dir", default="/tmp/ai-visibility-demo")
    a = ap.parse_args(argv)
    return {"run": cmd_run, "report": cmd_report, "demo": cmd_demo}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
