#!/usr/bin/env python3
"""Marketing HQ: one visual dashboard of the whole team's state, built from the workspace files.

Usage
  python3 hq.py --workspace marketing --out marketing/dashboards/hq.html
  python3 hq.py --workspace marketing --out /tmp/hq.html \
      --link-base https://github.com/<owner>/<repo>/blob/main/

Links to briefs, reports, strategy and calendar files are relative by default (they work when hq.html
is opened from marketing/dashboards/). With --link-base, every such link is resolved against the
workspace root (the git repository holding the marketing folder), prefixed with the base URL and
opened in a new tab, so a copy published on its own (e.g. as an artifact) still has working links.
Links to sibling dashboards (e.g. ai-visibility.html) stay relative: publish those files alongside.

Reads briefs, the content inventory, reports, strategy files, campaigns, launches, the social
calendar and AI visibility metrics. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

AGENTS = ["strategist", "seo-agent", "web-content-agent", "social-agent", "design-agent", "ads-agent", "gtm-agent"]
AGENT_LABEL = {"strategist": "Strategist", "seo-agent": "SEO & AI visibility", "web-content-agent": "Web content",
               "social-agent": "Social & video", "design-agent": "Design", "ads-agent": "Ads", "gtm-agent": "GTM & sales"}
LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def front_matter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.split("#", 1)[0].strip()
    return out


def title_of(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if not m:
        return fallback
    return re.sub(r"^(Brief|Content brief):\s*", "", m.group(1)).strip()


def parse_date(s: str):
    try:
        return dt.date.fromisoformat(s[:10])
    except (ValueError, TypeError):
        return None


def load_briefs(ws: Path) -> list[dict]:
    out = []
    for f in sorted((ws / "briefs").glob("*.md")):
        t = f.read_text(errors="replace")
        fm = front_matter(t)
        fm["title"] = title_of(t, f.stem)
        fm["path"] = f
        fm.setdefault("status", "ready")
        fm.setdefault("to", "web-content-agent")
        out.append(fm)
    return out


def load_inventory(ws: Path) -> list[dict]:
    p = ws / "content-inventory.md"
    if not p.exists():
        return []
    rows, header = [], None
    for line in p.read_text(errors="replace").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def recent_files(folder: Path, n: int) -> list[Path]:
    if not folder.exists():
        return []
    files = [f for f in folder.rglob("*") if f.is_file() and f.suffix in (".md", ".html")]
    return sorted(files, key=lambda f: (f.name[:10], f.stat().st_mtime), reverse=True)[:n]


def bars(items: list[tuple[str, float, str]], w=520, fmt=lambda v: str(int(v))) -> str:
    if not items:
        return "<p class='muted'>Nothing yet.</p>"
    row, pad_l = 28, 150
    h = row * len(items) + 6
    vmax = max([v for _, v, _ in items] + [1])
    iw = w - pad_l - 40
    parts = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for i, (label, v, color) in enumerate(items):
        y = 3 + i * row
        bw = max(2, iw * v / vmax) if v else 0
        parts.append(f'<text x="{pad_l - 8}" y="{y + 16}" class="lbl" text-anchor="end">{esc(label)}</text>')
        if bw:
            parts.append(f'<rect x="{pad_l}" y="{y + 4}" width="{bw:.1f}" height="16" rx="4" style="fill:{color}">'
                         f'<title>{esc(label)}: {fmt(v)}</title></rect>')
        parts.append(f'<text x="{pad_l + bw + 6:.1f}" y="{y + 16}" class="val">{fmt(v)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def column_chart(weeks: list[tuple[str, int]], w=520, h=180) -> str:
    if not weeks or not any(v for _, v in weeks):
        return "<p class='muted'>No content logged in the inventory yet.</p>"
    pad_l, pad_b, pad_t = 30, 24, 22
    vmax = max(v for _, v in weeks) or 1
    iw, ih = w - pad_l - 8, h - pad_b - pad_t
    bw = iw / len(weeks) * 0.6
    parts = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">',
             f'<line x1="{pad_l}" x2="{w - 8}" y1="{pad_t + ih}" y2="{pad_t + ih}" class="grid"/>']
    for i, (label, v) in enumerate(weeks):
        x = pad_l + iw * (i + 0.2) / len(weeks)
        bh = ih * v / vmax
        if v:
            parts.append(f'<rect x="{x:.1f}" y="{pad_t + ih - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" '
                         f'class="s1"><title>Week of {esc(label)}: {v}</title></rect>'
                         f'<text x="{x + bw / 2:.1f}" y="{pad_t + ih - bh - 4:.1f}" class="val" '
                         f'text-anchor="middle">{v}</text>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{h - 6}" class="axis" text-anchor="middle">{esc(label)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def workspace_root(ws: Path) -> Path:
    """The git repository root holding the marketing folder (falls back to the folder's parent)."""
    ws = ws.resolve()
    for d in (ws, *ws.parents):
        if (d / ".git").exists():
            return d
    return ws.parent


def make_link(ws: Path, out: Path, link_base: str | None = None):
    """Return href(path) -> the attributes of a link to a workspace file (href, plus target when absolute)."""
    dash = (ws / "dashboards").resolve()
    root = workspace_root(ws)
    base = (link_base.rstrip("/") + "/") if link_base else None

    def href(p: Path) -> str:
        p = p.resolve()
        if base and not (p.suffix == ".html" and p.parent == dash):
            url = base + urllib.parse.quote(p.relative_to(root).as_posix())
            return f"href='{esc(url)}' target='_blank' rel='noopener'"
        if out.parent.resolve() == dash:
            return f"href='{esc(Path('..', p.relative_to(ws.resolve())).as_posix())}'"
        return f"href='{esc(p.as_uri())}'"

    return href


def build(ws: Path, out: Path, today: dt.date, link_base: str | None = None) -> str:
    rel = make_link(ws, out, link_base)
    brand = "Marketing"
    bb = ws / "brand-brief.md"
    if bb.exists():
        m = re.search(r"^#\s*Brand brief:\s*(.+)$", bb.read_text(errors="replace"), re.M)
        if m:
            brand = re.sub(r"\s*\(.*?\)\s*$", "", m.group(1)).strip()

    briefs = load_briefs(ws)
    open_b = [b for b in briefs if b["status"] in ("ready", "in-progress")]
    done_recent = [b for b in briefs if b["status"] == "done" and (parse_date(b.get("date", "")) or today)
                   >= today - dt.timedelta(days=30)]
    inv = load_inventory(ws)
    inv_recent = [r for r in inv if (parse_date(r.get("date", "")) or dt.date.min) >= today - dt.timedelta(days=30)]

    # AI visibility
    aiv = ws / "ai-visibility" / "latest-metrics.json"
    aiv_tile, aiv_chart = ("–", "no tracking yet", ""), "<p class='muted'>AI visibility tracking isn't set up yet.</p>"
    if aiv.exists():
        mtr = json.loads(aiv.read_text())
        own = mtr.get("own")
        cur = mtr["brands"].get(own, {}).get("share_of_voice")
        prev = (mtr.get("previous") or {}).get(own, {}).get("share_of_voice")
        delta = "" if prev is None or cur is None else f"{'▲' if cur > prev else '▼' if cur < prev else '■'} {(cur - prev) * 100:+.0f} pts"
        aiv_tile = (f"{cur * 100:.0f}%" if cur is not None else "–", "AI share of voice", delta)
        ordered = [own] + sorted([b for b in mtr["brands"] if b != own], key=lambda b: -mtr["brands"][b]["share_of_voice"])
        aiv_chart = bars([(b, mtr["brands"][b]["share_of_voice"] * 100, f"var(--s{min(i, 7) + 1})")
                          for i, b in enumerate(ordered[:8])], fmt=lambda v: f"{v:.0f}%")
        aiv_chart += f"<p class='muted'>{esc(mtr['window'][0])} to {esc(mtr['window'][1])} · <a href='ai-visibility.html'>Full AI visibility dashboard</a></p>"

    # deadlines
    deadlines = []
    for b in open_b:
        d = parse_date(b.get("due", ""))
        if d:
            deadlines.append((d, b["title"], AGENT_LABEL.get(b["to"], b["to"]), b["path"]))
    for kind in ("launches", "campaigns"):
        for plan in (ws / kind).glob("*/plan.md"):
            t = plan.read_text(errors="replace")
            m = re.search(r"(?:Launch|Live|Start|Launch date)[^\n]*?(\d{4}-\d{2}-\d{2})", t, re.I)
            d = parse_date(m.group(1)) if m else None
            if d and d >= today:
                deadlines.append((d, title_of(t, plan.parent.name), {"launches": "Launch", "campaigns": "Campaign"}[kind], plan))
    deadlines.sort(key=lambda x: x[0])
    next_deadline = deadlines[0] if deadlines else None

    tiles = [
        (str(len(open_b)), "open briefs", f"{sum(b['status'] == 'in-progress' for b in open_b)} in progress"),
        (str(len(inv_recent)), "pieces produced, last 30 days", f"{len(done_recent)} briefs closed"),
        (aiv_tile[0], aiv_tile[1], aiv_tile[2]),
        ((next_deadline[0].strftime("%d %b") if next_deadline else "–"),
         "next deadline" + (" — overdue" if next_deadline and next_deadline[0] < today else ""),
         esc(next_deadline[1][:40]) if next_deadline else "nothing scheduled"),
    ]

    # board by status
    color = {a: f"var(--s{i + 1})" for i, a in enumerate(AGENTS)}

    def card(b):
        due = parse_date(b.get("due", ""))
        late = due and due < today and b["status"] != "done"
        meta = " · ".join(x for x in [b.get("type", ""), b.get("priority", ""),
                                       f"due {due:%d %b}" if due else ""] if x)
        flag = "<span class='late'>⚠ overdue</span>" if late else ""
        return (f"<a class='bcard' {rel(b['path'])}><span class='chip' style='--c:{color.get(b['to'], 'var(--neutral)')}'>"
                f"{esc(AGENT_LABEL.get(b['to'], b['to']))}</span><div class='bt'>{esc(b['title'])}</div>"
                f"<div class='bm'>{esc(meta)} {flag}</div></a>")

    def sortkey(b):
        return (PRIORITY_ORDER.get(b.get("priority", "medium"), 1), b.get("due") or "9999", b.get("date", ""))

    cols = []
    for status, label in (("ready", "Ready"), ("in-progress", "In progress"), ("done", "Done · last 30 days")):
        items = sorted([b for b in (done_recent if status == "done" else open_b) if b["status"] == status], key=sortkey)
        body = "".join(card(b) for b in items[:12]) or "<p class='muted'>Empty</p>"
        more = f"<p class='muted'>+{len(items) - 12} more</p>" if len(items) > 12 else ""
        cols.append(f"<div class='col'><h3>{label} <span class='count'>{len(items)}</span></h3>{body}{more}</div>")

    load = Counter(b["to"] for b in open_b)
    load_chart = bars([(AGENT_LABEL[a], load.get(a, 0), color[a]) for a in AGENTS])

    # weekly output
    weeks = []
    start = today - dt.timedelta(days=today.weekday()) - dt.timedelta(weeks=7)
    for k in range(8):
        ws_start = start + dt.timedelta(weeks=k)
        n = sum(1 for r in inv if (d := parse_date(r.get("date", ""))) and ws_start <= d < ws_start + dt.timedelta(days=7))
        weeks.append((ws_start.strftime("%d %b"), n))

    types = Counter((r.get("type") or "other").lower() for r in inv_recent)
    type_chart = bars([(t.title(), n, "var(--s1)") for t, n in types.most_common(8)])

    # reports and strategy
    reports = "".join(f"<li><a {rel(f)}>{esc(f.stem)}</a></li>" for f in recent_files(ws / "reports", 8)) \
        or "<li class='muted'>No reports yet</li>"
    strat_rows = []
    for name in ("marketing-strategy", "seo", "content", "social", "paid", "email"):
        f = ws / "strategy" / f"{name}.md"
        if f.exists():
            m = re.search(r"Next review:\s*(\d{4}-\d{2}-\d{2})", f.read_text(errors="replace"))
            nr = parse_date(m.group(1)) if m else None
            state = ("<span class='warn'>⚠ review due</span>" if nr and nr <= today
                     else f"review {nr:%d %b}" if nr else "no review date")
            strat_rows.append(f"<li><a {rel(f)}>{name}</a> <span class='muted'>· {state}</span></li>")
        else:
            strat_rows.append(f"<li class='muted'>{name} — not written yet</li>")
    dl_rows = "".join(f"<li><b>{d:%d %b}</b> · {esc(t)} <span class='muted'>· {esc(who)}</span></li>"
                      for d, t, who, _ in deadlines[:8]) or "<li class='muted'>No upcoming deadlines</li>"

    cal = sorted((ws / "calendar").glob("*.md"), reverse=True)
    cal_link = f"<a {rel(cal[0])}>{esc(cal[0].stem)}</a>" if cal else "<span class='muted'>none yet</span>"

    lv = "".join(f"--s{i + 1}:{c};" for i, c in enumerate(LIGHT))
    dv = "".join(f"--s{i + 1}:{c};" for i, c in enumerate(DARK))
    dark_vars = f"color-scheme:dark;--bg:#111110;--surface:#1a1a19;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--grid:#2c2c2a;--border:#30302d;--neutral:#5f5e5a;{dv}"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Marketing HQ — {esc(brand)}</title>
<style>
.viz-root{{color-scheme:light;--bg:#f6f6f4;--surface:#fcfcfb;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;--grid:#e6e5e1;--border:#e2e1dc;--neutral:#b5b4ae;{lv}}}
@media (prefers-color-scheme:dark){{:root:where(:not([data-theme="light"])) .viz-root{{{dark_vars}}}}}
:root[data-theme="dark"] .viz-root{{{dark_vars}}}
*{{box-sizing:border-box}} body{{margin:0}}
.viz-root{{background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;padding:24px;min-height:100vh}}
.wrap{{max-width:1180px;margin:0 auto}} a{{color:inherit}}
h1{{font-size:24px;margin:0}} h2{{font-size:15px;margin:0 0 12px}} h3{{font-size:13px;margin:0 0 10px;color:var(--text2);text-transform:uppercase;letter-spacing:.04em}}
.sub,.muted{{color:var(--text2)}} .muted{{font-size:13px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:20px 0}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px}}
.tile .v{{font-size:32px;font-weight:650}} .tile .k{{color:var(--text2)}} .tile .h{{color:var(--muted);font-size:12px;margin-top:4px}}
.board{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:12px}}
.col{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px;min-height:120px}}
.count{{background:var(--grid);border-radius:10px;padding:1px 8px;font-size:12px;color:var(--text)}}
.bcard{{display:block;text-decoration:none;border:1px solid var(--border);border-radius:10px;padding:10px;margin-bottom:8px;background:var(--bg)}}
.bcard:hover{{border-color:var(--text2)}}
.chip{{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;color:var(--text);background:color-mix(in srgb,var(--c) 22%,transparent);border-left:3px solid var(--c)}}
.bt{{font-weight:600;margin:6px 0 2px}} .bm{{font-size:12px;color:var(--text2)}} .late,.warn{{color:#d03b3b;font-weight:600}}
.grid3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px;margin-bottom:12px}}
.chart{{width:100%;height:auto;display:block}} .chart .lbl,.chart .val{{fill:var(--text2);font-size:12px}} .chart .axis{{fill:var(--muted);font-size:11px}}
.chart .grid{{stroke:var(--grid)}} .chart .s1{{fill:var(--s1)}}
ul{{margin:0;padding-left:18px}} li{{margin:4px 0}}
.toggle{{float:right;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:6px 10px;cursor:pointer}}
@media (max-width:760px){{.board{{grid-template-columns:1fr}}}}
</style></head>
<body><div class="viz-root"><div class="wrap">
<button class="toggle" onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'">Light / dark</button>
<h1>Marketing HQ — {esc(brand)}</h1>
<div class="sub">Team status on {today:%d %B %Y} · this week's social calendar: {cal_link}</div>
<div class="tiles">{''.join(f'<div class="card tile"><div class="v">{v}</div><div class="k">{k}</div><div class="h">{h}</div></div>' for v, k, h in tiles)}</div>
<div class="board">{''.join(cols)}</div>
<div class="grid3">
<div class="card"><h2>Open work by agent</h2>{load_chart}</div>
<div class="card"><h2>Content produced per week</h2>{column_chart(weeks)}</div>
<div class="card"><h2>AI share of voice</h2>{aiv_chart}</div>
</div>
<div class="grid3">
<div class="card"><h2>Upcoming deadlines</h2><ul>{dl_rows}</ul></div>
<div class="card"><h2>Latest reports</h2><ul>{reports}</ul></div>
<div class="card"><h2>Strategy</h2><ul>{''.join(strat_rows)}</ul><h2 style="margin-top:16px">Last 30 days by type</h2>{type_chart}</div>
</div>
</div></div></body></html>"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", default="marketing")
    ap.add_argument("--out", default=None)
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    ap.add_argument("--link-base", help="URL prefix for workspace file links, e.g. "
                    "https://github.com/<owner>/<repo>/blob/main/ (sibling dashboard links stay relative)")
    a = ap.parse_args(argv)
    ws = Path(a.workspace)
    if not ws.exists():
        print(f"No workspace at {ws}", file=sys.stderr)
        return 1
    out = Path(a.out) if a.out else ws / "dashboards" / "hq.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    out.write_text(build(ws, out, today, a.link_base))
    print(f"Marketing HQ written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
