#!/usr/bin/env python3
"""Marketing Hub: one page for all the marketing work, like a simple project board.

  Two filters   Area (strategy, content, SEO & AI visibility, social & video, design, ads, GTM & sales)
                Stage (to do → in progress → needs you → done)
  Goals         progress per goal from marketing/goals.md (tasks link to a goal with `goal:`)
  Board         every task as a card; a brief and the file it produced are one task
  Reader        click any task to read it, nicely formatted, without leaving the page

Also writes marketing/index.md — the plain list of all work that agents read.

Usage
  python3 hub.py --workspace marketing                 # writes marketing/hub.html and marketing/index.md
  python3 hub.py --workspace marketing --out hub.html

Each item has a stable link: hub.html#<id>, where <id> is the file path without "marketing/" and ".md",
"/" replaced by "--" and other characters by "-" (e.g. #web--homepage-refresh).
Standard library only (PyYAML used if installed).
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

AREAS = [  # key, label, description — one area per agent
    ("strategy", "Strategy & brand", "Strategy, brand brief, goals and campaign plans"),
    ("content", "Content", "Articles, pages and page refreshes"),
    ("seo", "SEO & AI visibility", "Audits, keywords and how AI answers talk about you"),
    ("social", "Social & video", "Posts, calendars and video briefs"),
    ("design", "Design", "Brand kit and graphics"),
    ("ads", "Ads", "Paid campaigns, ad copy and reviews"),
    ("gtm", "GTM & sales", "Launches, battlecards, one-pagers"),
]
STAGES = [("todo", "To do"), ("in-progress", "In progress"), ("needs-you", "Needs you"), ("done", "Done")]
AGENTS = {"strategist": "Strategist", "seo-agent": "SEO & AI visibility", "web-content-agent": "Web content",
          "social-agent": "Social & video", "design-agent": "Design", "ads-agent": "Ads", "gtm-agent": "GTM & sales",
          "brand-setup": "Setup", "team-lead": "Team lead", "user": "You"}
AGENT_AREA = {"strategist": "strategy", "brand-setup": "strategy", "seo-agent": "seo", "web-content-agent": "content",
              "social-agent": "social", "design-agent": "design", "ads-agent": "ads", "gtm-agent": "gtm"}
FOLDER_AREA = {"web": "content", "content": "content", "social": "social", "video": "social", "calendar": "social",
               "design": "design", "ads": "ads", "sales": "gtm", "launches": "gtm", "campaigns": "strategy",
               "strategy": "strategy", "ai-visibility": "seo"}
SKIP_DIRS = {"ai-visibility", "site", "dashboards", "assets", "templates", "data", ".git", "node_modules"}
SKIP_FILES = {"index.md", "artifacts.md", "content-inventory.md", "README.md", "goals.md"}
BRIEF_DIRS = {"queue", "briefs"}
DONE = {"approved", "published", "done", "live", "complete", "completed"}


# ------------------------------------------------------------------ parsing

def parse_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    raw, body = m.group(1), text[m.end():]
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(raw) or {}
        if isinstance(data, dict):
            return {k: v for k, v in data.items()}, body
    except Exception:
        pass
    data, key = {}, None
    for line in raw.splitlines():
        if re.match(r"^\s+-\s+", line) and key:
            data.setdefault(key, [])
            if isinstance(data[key], list):
                data[key].append(line.strip()[2:].strip().strip('"\''))
            continue
        mm = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if mm:
            key, val = mm.group(1), mm.group(2).split(" #")[0].strip()
            data[key] = [] if val == "" else val.strip('"\'')
    return data, body


def as_list(v) -> list[str]:
    if v is None or v == "":
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)]


def as_date(v, fallback: dt.date) -> str:
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()[:10]
    s = str(v or "")
    return s[:10] if re.match(r"\d{4}-\d{2}-\d{2}", s) else fallback.isoformat()


def item_id(rel: str) -> str:
    rel = re.sub(r"\.md$", "", rel)
    return re.sub(r"[^a-z0-9-]", "-", rel.lower().replace("/", "--")).strip("-") or "item"


def title_from(body: str, path: Path) -> str:
    m = re.search(r"^#\s+(.+)$", body, re.M)
    if m:
        return re.sub(r"^(Brief|Content brief):\s*", "", m.group(1)).strip()
    return path.stem.replace("-", " ").strip().capitalize()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def area_for(fm: dict, rel: str, agent: str) -> str:
    """Area = front matter `area:` if set, else the folder, else the agent, else a guess from the name."""
    want = slug(fm.get("area") or "")
    for k, label, _ in AREAS:
        if want and want in (k, slug(label)):
            return k
    first = rel.split("/")[0] if "/" in rel else ""
    if first in FOLDER_AREA:
        return FOLDER_AREA[first]
    if agent in AGENT_AREA:
        return AGENT_AREA[agent]
    name = rel.lower()
    if re.search(r"seo|keyword|ai-visib|audit|serp", name):
        return "seo"
    if re.search(r"gtm|launch|battlecard|competit|sales|pitch", name):
        return "gtm"
    return "strategy"


def stage_for(status: str, needs_you: list, is_brief: bool) -> str:
    s = slug(status)
    if s in DONE:
        return "done"
    if s in ("in-progress", "doing", "working", "started"):
        return "in-progress"
    if s in ("needs-you", "needs-review", "review", "in-review", "draft"):
        return "needs-you"
    if s in ("ready", "todo", "to-do", "backlog", "blocked", "planned"):
        return "todo"
    if is_brief:
        return "todo"
    return "needs-you" if needs_you else "done"


def load_goals(ws: Path) -> list[dict]:
    """marketing/goals.md: one `## Goal` heading per goal; `By: YYYY-MM-DD` anywhere under it sets the date."""
    p = ws / "goals.md"
    if not p.exists():
        return []
    _, body = parse_front_matter(p.read_text(errors="replace"))
    goals = []
    for m in re.finditer(r"^##\s+(.+?)\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S):
        title, text = m.group(1).strip(), m.group(2).strip()
        by = re.search(r"\bBy:?\**\s*(\d{4}-\d{2}-\d{2})", text)
        goals.append({"key": slug(title), "title": title, "md": text, "by": by.group(1) if by else ""})
    return goals


def match_goal(v, goals: list[dict]) -> str:
    s = slug(v or "")
    if not s:
        return ""
    for g in goals:
        if s == g["key"] or g["key"].startswith(s) or s.startswith(g["key"]):
            return g["key"]
    return s


def github_base(ws: Path) -> str | None:
    def git(*args):
        r = subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    url, root = git("remote", "get-url", "origin"), git("rev-parse", "--show-toplevel")
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    if not (m and root):
        return None
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "main"
    branch = "main" if branch == "HEAD" else branch
    prefix = ws.resolve().relative_to(Path(root).resolve()).as_posix()
    prefix = "" if prefix == "." else prefix + "/"
    return f"https://github.com/{m.group(1)}/{m.group(2)}/blob/{branch}/{prefix}"


def collect(ws: Path, goals: list[dict]) -> tuple[list[dict], list[dict]]:
    """Returns (tasks, briefs). A brief whose output file exists merges into that file's task."""
    work, briefs = [], []
    for p in sorted(ws.rglob("*.md")):
        rel = p.relative_to(ws).as_posix()
        parts = rel.split("/")
        if len(parts) == 1 and p.name in SKIP_FILES:
            continue
        if any(x in SKIP_DIRS for x in parts[:-1]):
            continue
        fm, body = parse_front_matter(p.read_text(errors="replace"))
        mtime = dt.date.fromtimestamp(p.stat().st_mtime)
        is_brief = parts[0] in BRIEF_DIRS
        agent = str(fm.get("to") if is_brief else (fm.get("agent") or fm.get("from")) or "")
        t = {
            "id": item_id(rel), "path": rel, "title": str(fm.get("title") or title_from(body, p)),
            "kind": "brief" if is_brief else "work", "type": str(fm.get("type") or ""), "agent": agent,
            "status": str(fm.get("status") or ("ready" if is_brief else "")), "date": as_date(fm.get("date"), mtime),
            "due": as_date(fm.get("due"), mtime) if fm.get("due") else "", "priority": str(fm.get("priority") or ""),
            "goal": match_goal(fm.get("goal"), goals), "summary": str(fm.get("summary") or ""),
            "needs_you": as_list(fm.get("needs_you")), "link": str(fm.get("link") or ""),
            "dashboard": str(fm.get("dashboard") or ""), "output": str(fm.get("output") or ""),
            "from": str(fm.get("from") or ""), "brief": "", "md": body.strip(),
        }
        if rel == "brand-brief.md":
            t["title"] = "Brand brief"
        t["area"] = area_for(fm, rel, agent)
        t["stage"] = stage_for(t["status"], t["needs_you"], is_brief)
        (briefs if is_brief else work).append(t)
    by_path = {w["path"]: w for w in work}
    for b in briefs:
        out = re.sub(r"^marketing/", "", b["output"].strip())
        w = by_path.get(out)
        if not w:
            continue
        b["merged"], b["result"] = True, w["id"]
        w["brief"] = b["id"]
        for k in ("goal", "priority", "due"):
            w[k] = w[k] or b[k]
        if not w["agent"]:
            w["agent"] = b["agent"]
    tasks = work + [b for b in briefs if not b.get("merged")]
    return tasks, briefs


# ------------------------------------------------------------------ outputs

def write_index(ws: Path, tasks: list[dict], goals: list[dict]) -> None:
    order = {k: i for i, (k, _) in enumerate(STAGES)}
    lines = ["# Work index", "", "Generated by the Marketing Hub — don't edit by hand. Open `hub.html` to read the work.", "",
             "Stages: to do → in progress → needs you → done. A brief and the file it produced are one task.", "",
             "| Stage | Area | Title | Goal | Due | Date | Needs you | File |", "|---|---|---|---|---|---|---|---|"]
    for t in sorted(tasks, key=lambda x: (order.get(x["stage"], 9), x["due"] or "9999", x["date"])):
        lines.append(f"| {t['stage']} | {t['area']} | {t['title']} | {t['goal']} | {t['due']} | {t['date']} | "
                     f"{len(t['needs_you']) or ''} | {t['path']} |")
    if goals:
        lines += ["", "## Goals", ""] + [f"- {g['title']}" + (f" (by {g['by']})" if g["by"] else "") + f" — key `{g['key']}`"
                                         for g in goals]
    (ws / "index.md").write_text("\n".join(lines) + "\n")


def load_artifacts(ws: Path) -> list[dict]:
    p = ws / "artifacts.md"
    rows, header = [], None
    if not p.exists():
        return rows
    for line in p.read_text(errors="replace").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        r = dict(zip(header, cells))
        m = re.search(r"https?://[^)\s|]+", r.get("link", ""))
        r["url"] = m.group(0) if m else ""
        rows.append(r)
    return rows


def build(ws: Path, out: Path, today: dt.date) -> str:
    goals = load_goals(ws)
    tasks, briefs = collect(ws, goals)
    write_index(ws, tasks, goals)
    brand = "Marketing"
    bb = ws / "brand-brief.md"
    if bb.exists():
        m = re.search(r"^#\s*Brand brief:\s*(.+)$", bb.read_text(errors="replace"), re.M)
        if m:
            brand = re.sub(r"\s*\(.*?\)\s*$", "", m.group(1)).strip()
            brand = re.sub(r"\s+[—-]\s+.*$", "", brand)
    dash = []
    for d in sorted((ws / "dashboards").glob("*.html")) if (ws / "dashboards").exists() else []:
        dash.append({"title": d.stem.replace("-", " ").capitalize(), "href": "dashboards/" + d.name
                     if out.parent.resolve() == ws.resolve() else d.resolve().as_uri()})
    metrics = None
    mp = ws / "ai-visibility" / "latest-metrics.json"
    if mp.exists():
        try:
            m = json.loads(mp.read_text())
            own = m.get("own")
            cur = (m.get("brands") or {}).get(own, {}).get("share_of_voice")
            metrics = {"sov": cur, "window": m.get("window")}
        except Exception:
            pass
    data = {
        "brand": brand, "today": today.isoformat(), "tasks": tasks, "briefs": [b for b in briefs if b.get("merged")],
        "goals": goals, "areas": [{"key": k, "label": l, "desc": d} for k, l, d in AREAS],
        "stages": [{"key": k, "label": l} for k, l in STAGES], "agents": AGENTS,
        "artifacts": load_artifacts(ws), "dashboards": dash, "metrics": metrics, "source": github_base(ws) or "",
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.replace("__TITLE__", html.escape(f"Marketing Hub — {brand}")).replace("__DATA__", payload)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<style>
:root{color-scheme:light;--bg:#f6f6f4;--surface:#fcfcfb;--raised:#ffffff;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;--line:#e2e1dc;--soft:#ecebe7;--accent:#2a78d6;--warn:#b54708;--warnbg:#fff4e5;--ok:#0f7b52;
--a1:#2a78d6;--a2:#eb6834;--a3:#1baf7a;--a4:#eda100;--a5:#e87ba4;--a6:#008300;--a7:#6250d6;--a8:#e34948}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme=light])){color-scheme:dark;--bg:#111110;--surface:#1a1a19;--raised:#20201e;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--line:#30302d;--soft:#2c2c2a;--accent:#3987e5;--warn:#f5a524;--warnbg:#2b2112;--ok:#3cc68a;
--a1:#3987e5;--a2:#d95926;--a3:#199e70;--a4:#c98500;--a5:#d55181;--a6:#008300;--a7:#9085e9;--a8:#e66767}}
:root[data-theme=dark]{color-scheme:dark;--bg:#111110;--surface:#1a1a19;--raised:#20201e;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--line:#30302d;--soft:#2c2c2a;--accent:#3987e5;--warn:#f5a524;--warnbg:#2b2112;--ok:#3cc68a;
--a1:#3987e5;--a2:#d95926;--a3:#199e70;--a4:#c98500;--a5:#d55181;--a6:#008300;--a7:#9085e9;--a8:#e66767}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--accent)}button,select,input{font:inherit}
header{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.hwrap{max-width:1180px;margin:0 auto;padding:12px 24px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.brand{font-weight:700;font-size:16px;margin-right:auto;text-decoration:none;color:var(--text)}.brand small{font-weight:400;color:var(--muted);margin-left:8px;font-size:13px}
.filters{display:flex;gap:8px;align-items:center;flex-wrap:wrap;width:100%}
.sel{display:flex;flex-direction:column;gap:2px}.sel label{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);padding-left:2px}
select{border:1px solid var(--line);background:var(--raised);color:var(--text);border-radius:8px;padding:7px 30px 7px 10px;min-width:190px;cursor:pointer}
.search{border:1px solid var(--line);background:var(--raised);color:var(--text);border-radius:8px;padding:7px 10px;width:220px}
.ghost{background:var(--raised);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:6px 10px;cursor:pointer;text-decoration:none;font-size:14px;white-space:nowrap}
.pill{display:inline-flex;align-items:center;gap:6px;align-self:flex-end;background:var(--soft);border-radius:16px;padding:5px 6px 5px 12px;font-size:13px}
.pill a{color:var(--text2);text-decoration:none;border-radius:50%;width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center}.pill a:hover{background:var(--line)}
.clear{align-self:flex-end;font-size:13px;color:var(--muted);padding:6px}
main{max-width:1180px;margin:0 auto;padding:20px 24px 64px}
h1{font-size:22px;margin:4px 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:16px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--text)}a.tile:hover{border-color:var(--muted)}
.tile .v{font-size:26px;font-weight:650}.tile .k{color:var(--text2);font-size:13px}.tile.hot .v{color:var(--warn)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:14px}
.card h2{font-size:15px;margin:0 0 10px;display:flex;justify-content:space-between;align-items:baseline}.card h2 a{font-size:13px;font-weight:400}
.goals{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}
.goal{display:block;background:var(--raised);border:1px solid var(--line);border-radius:10px;padding:12px;text-decoration:none;color:var(--text)}.goal:hover{border-color:var(--muted)}
.goal .t{font-weight:600;font-size:14px}.goal .s{color:var(--muted);font-size:12px;margin-top:6px;display:flex;justify-content:space-between}
.bar{height:6px;background:var(--soft);border-radius:4px;margin-top:8px;overflow:hidden}.bar i{display:block;height:100%;background:var(--ok);border-radius:4px}
.row{display:flex;gap:12px;align-items:flex-start;padding:10px 6px;border-top:1px solid var(--line);text-decoration:none;color:var(--text)}
.row:first-of-type{border-top:0}.row:hover{background:var(--soft);border-radius:8px}
.row .t{font-weight:600}.row .s{color:var(--text2);font-size:13px;margin-top:2px}.row .m{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap;text-align:right}
.row ul{margin:6px 0 0;padding-left:18px;font-size:13px;color:var(--warn)}
.chip{display:inline-block;font-size:11px;font-weight:600;padding:1px 8px;border-radius:10px;background:var(--soft);color:var(--text2);margin-right:4px;white-space:nowrap}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--c,var(--muted));margin-right:5px;vertical-align:1px}
.board{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.col{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px;min-height:90px}
.col h3{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--text2);margin:0 0 8px;display:flex;justify-content:space-between}
.col h3 a{color:var(--text2);text-decoration:none}.col.nu{background:var(--warnbg);border-color:color-mix(in srgb,var(--warn) 30%,transparent)}
.qc{display:block;background:var(--raised);border:1px solid var(--line);border-left:3px solid var(--c,var(--line));border-radius:8px;padding:8px 10px;margin-bottom:8px;text-decoration:none;color:var(--text);font-size:14px;line-height:1.35}
.qc:hover{border-color:var(--muted);border-left-color:var(--c,var(--muted))}
.qc .s{color:var(--muted);font-size:12px;margin-top:4px}.qc .w{color:var(--warn);font-weight:600}.qc .late{color:var(--a8);font-weight:600}
.more{display:block;font-size:13px;color:var(--muted);padding:2px 4px}
.empty{color:var(--muted);font-size:14px;padding:6px 4px}
article{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:24px 28px}
.meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px}
.needs{background:var(--warnbg);border:1px solid color-mix(in srgb,var(--warn) 35%,transparent);border-radius:10px;padding:10px 14px;margin:12px 0}
.needs b{color:var(--warn)}.needs ul{margin:6px 0 0;padding-left:20px}
.hint{font-size:13px;color:var(--muted);margin-top:18px;border-top:1px solid var(--line);padding-top:10px}
.doc{font-size:15.5px;line-height:1.65}.doc h1{font-size:24px;line-height:1.25}.doc h2{font-size:19px;margin-top:28px;padding-top:10px;border-top:1px solid var(--line)}
.doc h3{font-size:16px}.doc table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto;margin:12px 0}
.doc th,.doc td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}.doc th{background:var(--bg)}
.doc code{background:var(--soft);padding:1px 4px;border-radius:4px;font-size:90%}.doc pre{background:var(--soft);padding:12px;border-radius:8px;overflow:auto}
.doc pre code{background:none;padding:0}.doc blockquote{margin:12px 0;padding:6px 14px;border-left:3px solid var(--line);color:var(--text2)}
.doc img{max-width:100%}.crumbs{font-size:13px;color:var(--muted);margin-bottom:10px}.crumbs a{color:var(--muted)}
@media (max-width:980px){.board{grid-template-columns:repeat(2,1fr)}}
@media (max-width:640px){.hwrap{padding:10px 14px}main{padding:14px}.board{grid-template-columns:1fr}.sel{flex:1 1 140px}select{min-width:0;width:100%}.search{width:100%;order:3}article{padding:16px}}
</style></head>
<body><header><div class="hwrap" id="head"></div></header><main id="main"></main>
<script>
const D = __DATA__;
const AC = {strategy:"--a1",content:"--a3",seo:"--a2",social:"--a4",design:"--a5",ads:"--a6",gtm:"--a7"};
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const byId = Object.fromEntries([...D.tasks, ...D.briefs].map(t => [t.id, t]));
const goalBy = Object.fromEntries(D.goals.map(g => [g.key, g]));
const areaLabel = k => (D.areas.find(a=>a.key===k)||{label:k}).label;
const stageLabel = k => (D.stages.find(s=>s.key===k)||{label:k}).label;
const fmtDate = d => { if(!d) return ""; const x = new Date(d+"T00:00:00"); return isNaN(x) ? d : x.toLocaleDateString(undefined,{day:"numeric",month:"short"}); };
const dot = k => `<span class="dot" style="--c:var(${AC[k]||"--muted"})"></span>`;
const P = {high:0, medium:1, low:2};
let F = {area:"all", stage:"all", goal:"", q:""}, lastBoard = "#";

function readHash(){
  const h = decodeURIComponent((location.hash||"").slice(1));
  // old links from the first Hub version
  const legacy = {"home":"", "needs-you":"stage=needs-you", "queue":"stage=todo"};
  const oldArea = {web:"content",social:"social",video:"social",design:"design",ads:"ads",sales:"gtm",launches:"gtm",campaigns:"strategy",research:"seo",strategy:"strategy",foundations:"strategy"};
  let s = h in legacy ? legacy[h] : h.startsWith("area-") ? "area="+(oldArea[h.slice(5)]||h.slice(5)) : h;
  if (s === "" || s.includes("=")) { const p = new URLSearchParams(s); F = {area:p.get("area")||"all", stage:p.get("stage")||"all", goal:p.get("goal")||"", q:p.get("q")||""}; return {view:"board"}; }
  if (s === "links") return {view:"links"};
  if (byId[s]) return {view:"item", id:s};
  F = {area:"all", stage:"all", goal:"", q:""}; return {view:"board"};
}
function hashFor(f){ const p = new URLSearchParams(); if(f.area!=="all")p.set("area",f.area); if(f.stage!=="all")p.set("stage",f.stage); if(f.goal)p.set("goal",f.goal); if(f.q)p.set("q",f.q); const s = p.toString(); return "#"+(s||""); }
function go(ch){ location.hash = hashFor({...F, ...ch}) || "#"; if (hashFor({...F, ...ch})==="#") route(); }

const inArea = t => F.area==="all" || t.area===F.area;
const inGoal = t => !F.goal || t.goal===F.goal;
const matchQ = t => !F.q || (t.title+" "+t.summary+" "+t.md).toLowerCase().includes(F.q.toLowerCase());
const scoped = () => D.tasks.filter(t => inArea(t) && inGoal(t) && matchQ(t));

function header(){
  const base = D.tasks.filter(t => inGoal(t));
  const aCount = k => base.filter(t => k==="all" || t.area===k).filter(t => F.stage==="all" || t.stage===F.stage).length;
  const sCount = k => base.filter(t => inArea(t)).filter(t => k==="all" || t.stage===k).length;
  const areaOpts = [["all","All areas"], ...D.areas.map(a=>[a.key,a.label])].map(([k,l])=>`<option value="${k}" ${F.area===k?"selected":""}>${esc(l)} (${aCount(k)})</option>`).join("");
  const stageOpts = [["all","All stages"], ...D.stages.map(s=>[s.key,s.label])].map(([k,l])=>`<option value="${k}" ${F.stage===k?"selected":""}>${esc(l)} (${sCount(k)})</option>`).join("");
  const g = F.goal && goalBy[F.goal];
  const filtered = F.area!=="all" || F.stage!=="all" || F.goal || F.q;
  document.getElementById("head").innerHTML =
    `<a class="brand" href="#">Marketing Hub<small>${esc(D.brand)}</small></a>
     <input class="search" placeholder="Search…" value="${esc(F.q)}" oninput="clearTimeout(window._t);window._t=setTimeout(()=>go({q:this.value}),250)">
     ${D.dashboards.length||D.artifacts.length?`<a class="ghost" href="#links">Dashboards & designs</a>`:""}
     <button class="ghost" onclick="toggleTheme()" title="Switch light / dark">Theme</button>
     <div class="filters">
       <div class="sel"><label for="fa">Area</label><select id="fa" onchange="go({area:this.value})">${areaOpts}</select></div>
       <div class="sel"><label for="fs">Stage</label><select id="fs" onchange="go({stage:this.value})">${stageOpts}</select></div>
       ${g?`<span class="pill">Goal: ${esc(g.title)} <a href="${hashFor({...F,goal:""})}" title="Remove goal filter">✕</a></span>`:""}
       ${filtered?`<a class="clear" href="#" onclick="F={area:'all',stage:'all',goal:'',q:''}">Clear filters</a>`:""}
     </div>`;
}
function toggleTheme(){const r=document.documentElement;r.dataset.theme=r.dataset.theme==="dark"?"light":"dark";}

function renderMD(md){
  if (window.marked) { try { return marked.parse(md, {mangle:false, headerIds:false}); } catch(e) {} }
  const lines = md.split("\n"); let out = [], inList = false, inCode = false, para = [], tbl = [];
  const inline = t => esc(t).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/\*(.+?)\*/g,"<i>$1</i>").replace(/`(.+?)`/g,"<code>$1</code>").replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>');
  const flushTable = () => { if (!tbl.length) return; const rows = tbl.filter(r => !/^\s*\|?\s*:?-{2,}/.test(r)).map(r => r.trim().replace(/^\||\|$/g,"").split("|").map(c=>c.trim()));
    out.push("<table>" + rows.map((r,i)=>"<tr>"+r.map(c=> i===0?`<th>${inline(c)}</th>`:`<td>${inline(c)}</td>`).join("")+"</tr>").join("") + "</table>"); tbl = []; };
  const flush = () => { flushTable(); if (para.length) { out.push("<p>"+inline(para.join(" "))+"</p>"); para = []; } };
  for (const l of lines) {
    if (l.startsWith("```")) { flush(); out.push(inCode ? "</code></pre>" : "<pre><code>"); inCode = !inCode; continue; }
    if (inCode) { out.push(esc(l)); continue; }
    const h = l.match(/^(#{1,4})\s+(.*)/); const li = l.match(/^\s*[-*]\s+(.*)/) || l.match(/^\s*\d+\.\s+(.*)/);
    if (!l.trim().startsWith("|")) flushTable();
    if (h) { flush(); if(inList){out.push("</ul>");inList=false;} out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`); }
    else if (li) { flush(); if(!inList){out.push("<ul>");inList=true;} out.push("<li>"+inline(li[1])+"</li>"); }
    else if (!l.trim()) { flush(); if(inList){out.push("</ul>");inList=false;} }
    else if (/^\s*(-{3,}|\*{3,})\s*$/.test(l)) { flush(); if(inList){out.push("</ul>");inList=false;} out.push("<hr>"); }
    else if (/^>\s?/.test(l)) { flush(); out.push("<blockquote>"+inline(l.replace(/^>\s?/,""))+"</blockquote>"); }
    else if (l.trim().startsWith("|")) { if (para.length) { out.push("<p>"+inline(para.join(" "))+"</p>"); para = []; } tbl.push(l); continue; }
    else para.push(l.trim());
  }
  flush(); if(inList) out.push("</ul>"); return out.join("\n");
}

function sortStage(arr, st){
  if (st==="todo" || st==="in-progress") return [...arr].sort((a,b)=>(P[a.priority]??1)-(P[b.priority]??1) || (a.due||"9999").localeCompare(b.due||"9999"));
  return [...arr].sort((a,b)=>b.date.localeCompare(a.date));
}
function metaLine(t){
  const late = t.due && t.stage!=="done" && t.due < D.today;
  return [F.area==="all"?`${dot(t.area)}${esc(areaLabel(t.area))}`:"",
    t.stage==="done" ? fmtDate(t.date) : (t.due?`<span class="${late?"late":""}">due ${fmtDate(t.due)}</span>`:""),
    t.priority==="high"&&t.stage!=="done"?"high":"",
    t.needs_you.length&&t.stage!=="done"?`<span class="w">${t.needs_you.length} for you</span>`:""].filter(Boolean).join(" · ");
}
function card(t){ return `<a class="qc" style="--c:var(${AC[t.area]||"--muted"})" href="#${t.id}">${esc(t.title)}<div class="s">${metaLine(t)}</div></a>`; }

function boardHTML(tasks){
  return `<div class="board">` + D.stages.map(s => {
    let arr = sortStage(tasks.filter(t=>t.stage===s.key), s.key); const n = arr.length;
    const lim = s.key==="done" ? 6 : 12;
    return `<div class="col ${s.key==="needs-you"&&n?"nu":""}"><h3><a href="${hashFor({...F,stage:s.key})}">${s.label}</a><span>${n}</span></h3>${arr.slice(0,lim).map(card).join("") || '<div class="empty">—</div>'}${n>lim?`<a class="more" href="${hashFor({...F,stage:s.key})}">All ${n} →</a>`:""}</div>`;
  }).join("") + `</div>`;
}
function rowHTML(t){
  const items = t.stage==="needs-you" && t.needs_you.length ? `<ul>${t.needs_you.map(n=>`<li>${esc(n)}</li>`).join("")}</ul>` : "";
  return `<a class="row" href="#${t.id}"><div><div class="t">${dot(t.area)}${esc(t.title)}</div>${t.summary?`<div class="s">${esc(t.summary)}</div>`:""}${items}</div><div class="m">${esc(stageLabel(t.stage))}<br>${t.stage==="done"?fmtDate(t.date):(t.due?"due "+fmtDate(t.due):fmtDate(t.date))}</div></a>`;
}
function goalsHTML(){
  if (!D.goals.length) return "";
  return `<div class="card"><h2>Goals</h2><div class="goals">${D.goals.map(g=>{
    const ts = D.tasks.filter(t=>t.goal===g.key && inArea(t)); const done = ts.filter(t=>t.stage==="done").length; const pct = ts.length? Math.round(100*done/ts.length):0;
    return `<a class="goal" href="${hashFor({...F,goal:g.key})}"><div class="t">${esc(g.title)}</div><div class="bar"><i style="width:${pct}%"></i></div><div class="s"><span>${ts.length?`${done} of ${ts.length} task${ts.length===1?"":"s"} done`:"No tasks yet"}</span><span>${g.by?"by "+fmtDate(g.by):""}</span></div></a>`;}).join("")}</div></div>`;
}

function boardView(){
  const tasks = scoped();
  const n = k => tasks.filter(t=>t.stage===k).length;
  const actions = tasks.filter(t=>t.stage==="needs-you").reduce((s,t)=>s+t.needs_you.length,0);
  const g = F.goal && goalBy[F.goal];
  const title = F.q ? `Search: “${esc(F.q)}”` : g ? esc(g.title) : F.area!=="all" ? esc(areaLabel(F.area)) : "All work";
  let h = `<h1>${title}${F.stage!=="all"?` <span style="color:var(--muted);font-weight:400">· ${esc(stageLabel(F.stage))}</span>`:""}</h1>`;
  if (g && g.md) h += `<div class="card doc" style="font-size:14px">${renderMD(g.md)}</div>`;
  if (F.stage !== "all") {
    const arr = sortStage(tasks.filter(t=>t.stage===F.stage), F.stage);
    return h + `<div class="card">${arr.length?arr.map(rowHTML).join(""):'<div class="empty">Nothing here.</div>'}</div>`;
  }
  if (F.q) return h + `<div class="card">${tasks.length?tasks.map(rowHTML).join(""):'<div class="empty">No matches.</div>'}</div>`;
  const month = D.today.slice(0,7);
  h += `<div class="grid">
    <a class="tile ${actions?"hot":""}" href="${hashFor({...F,stage:"needs-you"})}"><div class="v">${actions}</div><div class="k">things need you</div></a>
    <a class="tile" href="${hashFor({...F,stage:"todo"})}"><div class="v">${n("todo")}</div><div class="k">to do</div></a>
    <a class="tile" href="${hashFor({...F,stage:"in-progress"})}"><div class="v">${n("in-progress")}</div><div class="k">in progress</div></a>
    <a class="tile" href="${hashFor({...F,stage:"done"})}"><div class="v">${tasks.filter(t=>t.stage==="done"&&t.date.startsWith(month)).length}</div><div class="k">done this month</div></a>
    ${D.metrics && D.metrics.sov!=null && (F.area==="all"||F.area==="seo") ? `<a class="tile" href="#links"><div class="v">${Math.round(D.metrics.sov*100)}%</div><div class="k">AI share of voice</div></a>`:""}</div>`;
  if (!g) h += goalsHTML();
  const needs = sortStage(tasks.filter(t=>t.stage==="needs-you"&&t.needs_you.length),"needs-you").flatMap(t=>t.needs_you.map(x=>({x,t}))).slice(0,6);
  if (needs.length) h += `<div class="card"><h2>Needs you <a href="${hashFor({...F,stage:"needs-you"})}">See all</a></h2>${needs.map(({x,t})=>`<a class="row" href="#${t.id}"><div><div class="t">${esc(x)}</div><div class="s">${dot(t.area)}${esc(t.title)}</div></div><div class="m">${fmtDate(t.date)}</div></a>`).join("")}</div>`;
  h += `<div class="card"><h2>Board</h2>${boardHTML(tasks)}</div>`;
  return h;
}

function itemView(t){
  const back = lastBoard && lastBoard!=="#" ? lastBoard : "#";
  let h = `<div class="crumbs"><a href="${back}">← Back to the board</a></div><article>`;
  const g = goalBy[t.goal];
  h += `<div class="meta"><span class="chip">${dot(t.area)}${esc(areaLabel(t.area))}</span><span class="chip">${esc(stageLabel(t.stage))}</span>${t.kind==="brief"?'<span class="chip">brief</span>':""}${t.status?`<span class="chip">${esc(t.status)}</span>`:""}<span class="chip">${fmtDate(t.date)}</span>${t.due?`<span class="chip">due ${fmtDate(t.due)}</span>`:""}${g?`<a class="chip" href="#goal=${g.key}" style="text-decoration:none">Goal: ${esc(g.title)}</a>`:""}</div>`;
  if (t.needs_you.length && t.stage!=="done") h += `<div class="needs"><b>Needs you</b><ul>${t.needs_you.map(n=>`<li>${esc(n)}</li>`).join("")}</ul></div>`;
  const links = [];
  if (t.link) links.push(`<a href="${esc(t.link)}" target="_blank" rel="noopener">Open in Claude ↗</a>`);
  if (t.dashboard) links.push(`<a href="${esc(t.dashboard)}" target="_blank" rel="noopener">Dashboard ↗</a>`);
  if (t.brief && byId[t.brief]) links.push(`<a href="#${t.brief}">The brief</a>`);
  if (t.result && byId[t.result]) links.push(`<a href="#${t.result}">The result →</a>`);
  if (D.source) links.push(`<a href="${esc(D.source+t.path)}" target="_blank" rel="noopener">Source file ↗</a>`);
  if (links.length) h += `<div class="crumbs">${links.join(" · ")}</div>`;
  const md = /^#\s/.test(t.md) ? t.md : `# ${t.title}\n\n` + t.md;
  h += `<div class="doc">${renderMD(md)}</div>`;
  const name = t.title.split(":")[0].toLowerCase();
  const tip = {todo:`To start it, tell Claude “do the ${name}”.`, "in-progress":"The team is working on this.", "needs-you":`When you're happy, tell Claude “approve the ${name}”, or say what to change.`, done:"Done."}[t.stage];
  h += `<div class="hint">${tip}</div></article>`;
  return h;
}

function linksView(){
  let h = `<h1>Dashboards & designs</h1>`;
  h += `<div class="card"><h2>Dashboards</h2>${D.dashboards.length ? D.dashboards.map(d=>`<a class="row" href="${esc(d.href)}" target="_blank" rel="noopener"><div class="t">${esc(d.title)}</div></a>`).join("") : '<div class="empty">None yet.</div>'}</div>`;
  h += `<div class="card"><h2>In Claude (designs, docs, videos)</h2>${D.artifacts.length ? D.artifacts.map(r=>`<a class="row" href="${esc(r.url)}" target="_blank" rel="noopener"><div><div class="t">${esc(r.title||r.url)}</div><div class="s">${esc(r.type||"")}</div></div><div class="m">${esc(r.date||"")}</div></a>`).join("") : '<div class="empty">None yet.</div>'}</div>`;
  return h;
}

function route(){
  const r = readHash();
  if (r.view === "board") lastBoard = location.hash || "#";
  header();
  const m = document.getElementById("main");
  m.innerHTML = r.view==="item" ? itemView(byId[r.id]) : r.view==="links" ? linksView() : boardView();
  if (r.view === "board" && F.q) { const s = document.querySelector(".search"); s.focus(); s.setSelectionRange(s.value.length, s.value.length); }
  else if (r.view !== "board") window.scrollTo(0,0);
}
window.addEventListener("hashchange", route);
route();
</script></body></html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", default="marketing")
    ap.add_argument("--out", default=None, help="default: <workspace>/hub.html")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    a = ap.parse_args(argv)
    ws = Path(a.workspace)
    if not ws.exists():
        print(f"No workspace at {ws}", file=sys.stderr)
        return 1
    out = Path(a.out) if a.out else ws / "hub.html"
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    out.write_text(build(ws, out, today))
    print(f"Marketing Hub written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
