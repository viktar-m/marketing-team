#!/usr/bin/env python3
"""Marketing Hub: one page for everything the marketing team has made.

  Home      what needs you, the work queue, recent work, a few numbers
  Areas     every deliverable grouped by area (web, social, design, ads, sales, research, ...)
  Reader    click any item to read it, nicely formatted, without leaving the page

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

AREAS = [  # folder, label, description
    ("web", "Web", "Articles, pages and page refreshes"),
    ("social", "Social", "Posts and weekly calendars"),
    ("video", "Video", "Video plans and Motion briefs"),
    ("design", "Design", "Brand kit and graphics"),
    ("ads", "Ads", "Campaign plans, ad copy, reviews"),
    ("sales", "Sales", "Battlecards, one-pagers, talk tracks"),
    ("launches", "Launches", "Launch kits"),
    ("campaigns", "Campaigns", "Campaign and promo plans"),
    ("research", "Research", "Audits, analyses, reviews"),
    ("strategy", "Strategy", "The rules the team follows"),
    ("foundations", "Foundations", "Brand brief and team setup"),
]
AGENTS = {"strategist": "Strategist", "seo-agent": "SEO & AI visibility", "web-content-agent": "Web content",
          "social-agent": "Social & video", "design-agent": "Design", "ads-agent": "Ads", "gtm-agent": "GTM & sales",
          "brand-setup": "Setup", "team-lead": "Team lead", "user": "You"}
AGENT_ORDER = list(AGENTS)
SKIP_DIRS = {"queue", "ai-visibility", "site", "dashboards", "assets", "templates", "data", ".git", "node_modules"}
SKIP_FILES = {"index.md", "artifacts.md", "content-inventory.md", "README.md"}
LEGACY = {"briefs": "queue", "reports": "research", "calendar": "social", "content": None}  # old layout folders


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


def area_of(rel: str) -> str:
    first = rel.split("/")[0]
    if "/" not in rel:
        return "foundations"
    if first in LEGACY and LEGACY[first]:
        return LEGACY[first]
    if first == "content":
        sub = rel.split("/")[1] if rel.count("/") >= 1 else ""
        return {"blog": "web", "pages": "web", "refreshes": "web", "social": "social", "video": "video"}.get(sub, "web")
    return first if first in {a for a, _, _ in AREAS} else "research"


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


def collect(ws: Path) -> tuple[list[dict], list[dict]]:
    items, queue = [], []
    for p in sorted(ws.rglob("*.md")):
        rel = p.relative_to(ws).as_posix()
        parts = rel.split("/")
        if p.name in SKIP_FILES and len(parts) == 1:
            continue
        if any(x in SKIP_DIRS for x in parts[:-1]) and parts[0] not in ("queue", "briefs"):
            continue
        text = p.read_text(errors="replace")
        fm, body = parse_front_matter(text)
        mtime = dt.date.fromtimestamp(p.stat().st_mtime)
        base = {
            "id": item_id(rel), "path": rel, "title": str(fm.get("title") or title_from(body, p)),
            "type": str(fm.get("type") or ""), "agent": str(fm.get("agent") or fm.get("from") or ""),
            "status": str(fm.get("status") or ""), "date": as_date(fm.get("date"), mtime),
            "summary": str(fm.get("summary") or ""), "needs_you": as_list(fm.get("needs_you")),
            "link": str(fm.get("link") or ""), "dashboard": str(fm.get("dashboard") or ""), "md": body.strip(),
        }
        if parts[0] in ("queue", "briefs"):
            base.update({"to": str(fm.get("to") or ""), "priority": str(fm.get("priority") or "medium"),
                         "due": as_date(fm.get("due"), dt.date.min) if fm.get("due") else "",
                         "output": str(fm.get("output") or ""), "status": base["status"] or "ready",
                         "area": "queue"})
            queue.append(base)
        else:
            base["area"] = area_of(rel)
            if rel == "brand-brief.md":
                base["title"] = "Brand brief"
            items.append(base)
    return items, queue


# ------------------------------------------------------------------ outputs

def write_index(ws: Path, items: list[dict], queue: list[dict]) -> None:
    lines = ["# Work index", "", "Generated by the Marketing Hub — don't edit by hand. Open `hub.html` to read the work.", "",
             "| Date | Area | Title | Type | Status | Needs you | File |", "|---|---|---|---|---|---|---|"]
    for it in sorted(items, key=lambda x: x["date"], reverse=True):
        lines.append(f"| {it['date']} | {it['area']} | {it['title']} | {it['type']} | {it['status']} | "
                     f"{len(it['needs_you']) or ''} | {it['path']} |")
    lines += ["", "## Queue", "", "| Status | Priority | Title | To | Due | File |", "|---|---|---|---|---|---|"]
    for q in sorted(queue, key=lambda x: (x["status"] == "done", x["priority"], x["due"] or "9999")):
        lines.append(f"| {q['status']} | {q['priority']} | {q['title']} | {q['to']} | {q['due']} | {q['path']} |")
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
    items, queue = collect(ws)
    write_index(ws, items, queue)
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
        "brand": brand, "today": today.isoformat(), "items": items, "queue": queue,
        "areas": [{"key": k, "label": l, "desc": d} for k, l, d in AREAS],
        "agents": AGENTS, "artifacts": load_artifacts(ws), "dashboards": dash, "metrics": metrics,
        "source": github_base(ws) or "",
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.replace("__TITLE__", html.escape(f"Marketing Hub — {brand}")).replace("__DATA__", payload)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<style>
:root{color-scheme:light;--bg:#f6f6f4;--surface:#fcfcfb;--raised:#ffffff;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;--line:#e2e1dc;--soft:#ecebe7;--accent:#2a78d6;--warn:#b54708;--warnbg:#fff4e5;
--a1:#2a78d6;--a2:#eb6834;--a3:#1baf7a;--a4:#eda100;--a5:#e87ba4;--a6:#008300;--a7:#6250d6;--a8:#e34948}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme=light])){color-scheme:dark;--bg:#111110;--surface:#1a1a19;--raised:#20201e;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--line:#30302d;--soft:#2c2c2a;--accent:#3987e5;--warn:#f5a524;--warnbg:#2b2112;
--a1:#3987e5;--a2:#d95926;--a3:#199e70;--a4:#c98500;--a5:#d55181;--a6:#008300;--a7:#9085e9;--a8:#e66767}}
:root[data-theme=dark]{color-scheme:dark;--bg:#111110;--surface:#1a1a19;--raised:#20201e;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--line:#30302d;--soft:#2c2c2a;--accent:#3987e5;--warn:#f5a524;--warnbg:#2b2112;
--a1:#3987e5;--a2:#d95926;--a3:#199e70;--a4:#c98500;--a5:#d55181;--a6:#008300;--a7:#9085e9;--a8:#e66767}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--accent)}button{font:inherit}
.app{display:grid;grid-template-columns:240px 1fr;min-height:100vh}
nav{border-right:1px solid var(--line);background:var(--surface);padding:18px 12px;position:sticky;top:0;height:100vh;overflow:auto}
.brand{font-weight:700;font-size:15px;padding:4px 10px 2px}.brand small{display:block;font-weight:400;color:var(--muted);font-size:12px}
.navlink{display:flex;justify-content:space-between;align-items:center;padding:7px 10px;border-radius:8px;color:var(--text);text-decoration:none;font-size:14px}
.navlink:hover{background:var(--soft)}.navlink.on{background:var(--soft);font-weight:600}
.navlink .n{color:var(--muted);font-size:12px}.navlink .n.hot{color:var(--warn);font-weight:700}
.navhead{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);padding:16px 10px 4px}
main{padding:24px 32px 64px;max-width:1100px;width:100%}
.top{display:flex;gap:12px;align-items:center;margin-bottom:18px}.top h1{font-size:22px;margin:0;flex:1}
.search{border:1px solid var(--line);background:var(--raised);color:var(--text);border-radius:8px;padding:7px 10px;width:240px}
.ghost{background:var(--raised);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:6px 10px;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-bottom:18px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px}.tile .v{font-size:26px;font-weight:650}.tile .k{color:var(--text2);font-size:13px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:14px}
.card h2{font-size:15px;margin:0 0 10px}
.row{display:flex;gap:12px;align-items:flex-start;padding:10px 4px;border-top:1px solid var(--line);text-decoration:none;color:var(--text)}
.row:first-of-type{border-top:0}.row:hover{background:var(--soft);border-radius:8px}
.row .t{font-weight:600}.row .s{color:var(--text2);font-size:13px}.row .m{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap;text-align:right}
.chip{display:inline-block;font-size:11px;font-weight:600;padding:1px 8px;border-radius:10px;background:var(--soft);color:var(--text2);margin-right:4px;white-space:nowrap}
.chip.agent{border-left:3px solid var(--c,var(--muted))}
.needs{background:var(--warnbg);border:1px solid color-mix(in srgb,var(--warn) 35%,transparent);border-radius:10px;padding:10px 14px;margin:12px 0}
.needs b{color:var(--warn)}.needs ul{margin:6px 0 0;padding-left:20px}
.board{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.col{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px;min-height:80px}
.col h3{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--text2);margin:0 0 8px}
.qc{display:block;background:var(--raised);border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin-bottom:8px;text-decoration:none;color:var(--text);font-size:14px}
.qc .s{color:var(--muted);font-size:12px}
.empty{color:var(--muted);font-size:14px;padding:6px 4px}
article{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:24px 28px}
.meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px}
.doc{font-size:15.5px;line-height:1.65}.doc h1{font-size:24px;line-height:1.25}.doc h2{font-size:19px;margin-top:28px;padding-top:10px;border-top:1px solid var(--line)}
.doc h3{font-size:16px}.doc table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto;margin:12px 0}
.doc th,.doc td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}.doc th{background:var(--bg)}
.doc code{background:var(--soft);padding:1px 4px;border-radius:4px;font-size:90%}.doc pre{background:var(--soft);padding:12px;border-radius:8px;overflow:auto}
.doc pre code{background:none;padding:0}.doc blockquote{margin:12px 0;padding:6px 14px;border-left:3px solid var(--line);color:var(--text2)}
.doc img{max-width:100%}.crumbs{font-size:13px;color:var(--muted);margin-bottom:10px}.crumbs a{color:var(--muted)}
.mobilenav{display:none}
@media (max-width:820px){.app{grid-template-columns:1fr}nav{display:none}.mobilenav{display:block;margin-bottom:12px}.mobilenav select{width:100%;padding:8px;border-radius:8px;border:1px solid var(--line);background:var(--raised);color:var(--text)}
main{padding:16px}.board{grid-template-columns:1fr}.search{width:100%}.top{flex-wrap:wrap}article{padding:16px}}
</style></head>
<body><div class="app"><nav id="nav"></nav><main id="main"></main></div>
<script>
const D = __DATA__;
const AGC = {"strategist":"--a1","seo-agent":"--a2","web-content-agent":"--a3","social-agent":"--a4","design-agent":"--a5","ads-agent":"--a6","gtm-agent":"--a7"};
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const byId = Object.fromEntries([...D.items, ...D.queue].map(i => [i.id, i]));
const open = D.items.filter(i => i.needs_you.length && !["approved","published","done"].includes(i.status));
const qOpen = D.queue.filter(q => q.status !== "done");
const fmtDate = d => { if(!d) return ""; const x = new Date(d+"T00:00:00"); return isNaN(x) ? d : x.toLocaleDateString(undefined,{day:"numeric",month:"short"}); };
const agentChip = a => a ? `<span class="chip agent" style="--c:var(${AGC[a]||"--muted"})">${esc(D.agents[a]||a)}</span>` : "";
const areaLabel = k => (D.areas.find(a=>a.key===k)||{label:k}).label;
let query = "";

function renderMD(md){
  if (window.marked) { try { return marked.parse(md, {mangle:false, headerIds:false}); } catch(e) {} }
  // minimal fallback when the markdown library can't load (offline)
  const lines = md.split("\n"); let out = [], inList = false, inCode = false, para = [];
  const inline = t => esc(t).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/\*(.+?)\*/g,"<i>$1</i>").replace(/`(.+?)`/g,"<code>$1</code>").replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>');
  let tbl = [];
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
    else if (l.trim().startsWith("|")) { if (para.length) { out.push("<p>"+inline(para.join(" "))+"</p>"); para = []; } tbl.push(l); continue; }
    else para.push(l.trim());
  }
  flush(); if(inList) out.push("</ul>"); return out.join("\n");
}

function nav(route){
  const cnt = k => D.items.filter(i => i.area === k).length;
  const link = (href, label, n, hot) => `<a class="navlink ${route===href?"on":""}" href="#${href}">${label}<span class="n ${hot?"hot":""}">${n??""}</span></a>`;
  let h = `<div class="brand">Marketing Hub<small>${esc(D.brand)}</small></div>`;
  h += link("home","Home") + link("needs-you","Needs you", open.length || "", open.length>0) + link("queue","Queue", qOpen.length || "");
  h += `<div class="navhead">Work</div>` + D.areas.filter(a=>cnt(a.key)).map(a => link("area-"+a.key, a.label, cnt(a.key))).join("");
  if (D.dashboards.length || D.artifacts.length) h += `<div class="navhead">Dashboards & designs</div>` + link("links","All links", D.dashboards.length + D.artifacts.length);
  document.getElementById("nav").innerHTML = h;
  const opts = [["home","Home"],["needs-you",`Needs you (${open.length})`],["queue",`Queue (${qOpen.length})`],...D.areas.filter(a=>cnt(a.key)).map(a=>["area-"+a.key,`${a.label} (${cnt(a.key)})`]),["links","Dashboards & designs"]];
  return `<div class="mobilenav"><select onchange="location.hash=this.value">${opts.map(([v,l])=>`<option value="${v}" ${v===route?"selected":""}>${esc(l)}</option>`).join("")}</select></div>`;
}

function topbar(title){
  return `<div class="top"><h1>${title}</h1><input class="search" placeholder="Search all work…" value="${esc(query)}" oninput="query=this.value;if(location.hash!=='#search'){if(query.length>1)location.hash='search'}else{route()}"><button class="ghost" onclick="toggleTheme()">Light / dark</button></div>`;
}
function toggleTheme(){const r=document.documentElement;r.dataset.theme=r.dataset.theme==="dark"?"light":"dark";}

function row(i){
  const meta = [i.area==="queue" ? (i.due?`due ${fmtDate(i.due)}`:"") : fmtDate(i.date), i.status].filter(Boolean).join(" · ");
  return `<a class="row" href="#${i.id}"><div><div class="t">${esc(i.title)}</div><div class="s">${agentChip(i.agent||i.to)}${i.summary?esc(i.summary):`<span class="chip">${esc(areaLabel(i.area))}</span>`}</div></div><div class="m">${esc(meta)}${i.needs_you&&i.needs_you.length?`<br><span style="color:var(--warn)">${i.needs_you.length} for you</span>`:""}</div></a>`;
}
function list(arr, empty){ return arr.length ? arr.map(row).join("") : `<div class="empty">${empty}</div>`; }

function boardHTML(){
  const recentDone = D.queue.filter(q => q.status==="done").slice(-6);
  const P = {high:0, medium:1, low:2};
  const sorted = arr => [...arr].sort((a,b)=>(P[a.priority]??1)-(P[b.priority]??1) || (a.due||"9999").localeCompare(b.due||"9999"));
  const col = (st, label) => { const qs = st==="done" ? recentDone : sorted(D.queue.filter(q=>q.status===st));
    return `<div class="col"><h3>${label} · ${qs.length}</h3>${qs.map(q=>`<a class="qc" href="#${q.id}">${esc(q.title)}<div class="s">${esc(D.agents[q.to]||q.to)}${q.due?" · due "+fmtDate(q.due):""}${q.priority==="high"?" · high":""}</div></a>`).join("") || '<div class="empty">Empty</div>'}</div>`; };
  return `<div class="board">${col("ready","Ready")}${col("in-progress","In progress")}${col("done","Done")}</div>`;
}

function home(){
  const month = D.today.slice(0,7);
  const made = D.items.filter(i => i.date.startsWith(month)).length;
  const recent = [...D.items].sort((a,b)=>b.date.localeCompare(a.date)).slice(0,8);
  const needs = open.flatMap(i => i.needs_you.map(n => ({n, i}))).slice(0,8);
  let h = topbar("Home");
  h += `<div class="grid"><div class="tile"><div class="v">${needs.length? open.reduce((s,i)=>s+i.needs_you.length,0):0}</div><div class="k">things need you</div></div>
  <div class="tile"><div class="v">${qOpen.length}</div><div class="k">in the queue</div></div>
  <div class="tile"><div class="v">${made}</div><div class="k">made this month</div></div>
  ${D.metrics && D.metrics.sov!=null ? `<div class="tile"><div class="v">${Math.round(D.metrics.sov*100)}%</div><div class="k">AI share of voice</div></div>`:""}</div>`;
  h += `<div class="card"><h2>Needs you</h2>${needs.length ? needs.map(({n,i})=>`<a class="row" href="#${i.id}"><div><div class="t">${esc(n)}</div><div class="s">${esc(i.title)}</div></div><div class="m">${fmtDate(i.date)}</div></a>`).join("") : '<div class="empty">Nothing waiting for you.</div>'}</div>`;
  h += `<div class="card"><h2>Queue</h2>${boardHTML()}</div>`;
  h += `<div class="card"><h2>Recent work</h2>${list(recent,"Nothing yet — ask the team for something.")}</div>`;
  return h;
}

function itemView(it){
  const isQ = it.area === "queue";
  const back = isQ ? `<a href="#queue">Queue</a>` : `<a href="#area-${it.area}">${esc(areaLabel(it.area))}</a>`;
  let h = topbar("") + `<div class="crumbs"><a href="#home">Home</a> › ${back}</div><article>`;
  h += `<div class="meta">${agentChip(it.agent||it.to)}<span class="chip">${esc(it.type|| (isQ?"brief":areaLabel(it.area)))}</span>${it.status?`<span class="chip">${esc(it.status)}</span>`:""}<span class="chip">${fmtDate(it.date)}</span>${isQ&&it.due?`<span class="chip">due ${fmtDate(it.due)}</span>`:""}</div>`;
  if (it.needs_you.length) h += `<div class="needs"><b>Needs you</b><ul>${it.needs_you.map(n=>`<li>${esc(n)}</li>`).join("")}</ul></div>`;
  const links = [];
  if (it.link) links.push(`<a href="${esc(it.link)}" target="_blank" rel="noopener">Open in Claude ↗</a>`);
  if (it.dashboard) links.push(`<a href="${esc(it.dashboard)}" target="_blank" rel="noopener">Dashboard ↗</a>`);
  if (isQ && it.output) { const oid = Object.values(byId).find(x => it.output.endsWith(x.path)); if (oid) links.push(`<a href="#${oid.id}">Result →</a>`); }
  if (D.source) links.push(`<a href="${esc(D.source+it.path)}" target="_blank" rel="noopener">Source file ↗</a>`);
  if (links.length) h += `<div class="crumbs">${links.join(" · ")}</div>`;
  const md = /^#\s/.test(it.md) ? it.md : `# ${it.title}\n\n` + it.md;
  h += `<div class="doc">${renderMD(md)}</div></article>`;
  return h;
}

function area(k){
  const a = D.areas.find(x=>x.key===k) || {label:k, desc:""};
  const arr = D.items.filter(i=>i.area===k).sort((x,y)=>y.date.localeCompare(x.date));
  return topbar(esc(a.label)) + `<div class="card"><h2>${esc(a.desc)}</h2>${list(arr,"Nothing here yet.")}</div>`;
}

function links(){
  let h = topbar("Dashboards & designs");
  h += `<div class="card"><h2>Dashboards</h2>${D.dashboards.length ? D.dashboards.map(d=>`<a class="row" href="${esc(d.href)}" target="_blank" rel="noopener"><div class="t">${esc(d.title)}</div></a>`).join("") : '<div class="empty">None yet.</div>'}</div>`;
  h += `<div class="card"><h2>In Claude (designs, design system, videos)</h2>${D.artifacts.length ? D.artifacts.map(r=>`<a class="row" href="${esc(r.url)}" target="_blank" rel="noopener"><div><div class="t">${esc(r.title||r.url)}</div><div class="s">${esc(r.type||"")}</div></div><div class="m">${esc(r.date||"")}</div></a>`).join("") : '<div class="empty">None yet.</div>'}</div>`;
  return h;
}

function search(){
  const q = query.toLowerCase();
  const arr = [...D.items, ...D.queue].filter(i => (i.title+" "+i.summary+" "+i.md).toLowerCase().includes(q));
  return topbar("Search") + `<div class="card"><h2>${arr.length} result${arr.length===1?"":"s"} for “${esc(query)}”</h2>${list(arr,"No matches.")}</div>`;
}

function route(){
  const r = (location.hash || "#home").slice(1) || "home";
  let body;
  if (r === "home") body = home();
  else if (r === "needs-you") body = topbar("Needs you") + `<div class="card">${list(open,"Nothing waiting for you.")}</div>`;
  else if (r === "queue") body = topbar("Queue") + `<div class="card">${boardHTML()}</div><div class="card"><h2>All briefs</h2>${list(D.queue,"The queue is empty.")}</div>`;
  else if (r === "links") body = links();
  else if (r === "search") body = search();
  else if (r.startsWith("area-")) body = area(r.slice(5));
  else if (byId[r]) body = itemView(byId[r]);
  else body = home();
  document.getElementById("main").innerHTML = nav(r) + body;
  if (r === "search") { const s = document.querySelector(".search"); s.focus(); s.setSelectionRange(s.value.length, s.value.length); }
  else window.scrollTo(0,0);
}
window.addEventListener("hashchange", route);
window.addEventListener("load", route);
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
