#!/usr/bin/env python3
"""Marketing HQ: one visual dashboard of the whole team's state, built from the workspace files.

Usage
  python3 hq.py --workspace marketing --out marketing/dashboards/hq.html \
      [--link-base https://github.com/<owner>/<repo>/blob/<branch>/]

Reads briefs, the content inventory, reports, strategy files, campaigns, launches, the social
calendar and AI visibility metrics. Standard library only.

Every linked .md file (briefs, reports, strategy, the calendar, and the .md files those link to) is
embedded in the page as JSON and opens in a slide-over panel, so the dashboard still works when it
is published on its own (for example as a claude.ai artifact) without the repository next to it.
--link-base is the GitHub "blob" URL of the repository root; it powers the "Open on GitHub" button
and links to files that aren't embedded.

"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import unicodedata
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

AGENTS = ["strategist", "seo-agent", "web-content-agent", "social-agent", "design-agent", "ads-agent", "gtm-agent"]
AGENT_LABEL = {"strategist": "Strategist", "seo-agent": "SEO & AI visibility", "web-content-agent": "Web content",
               "social-agent": "Social & video", "design-agent": "Design", "ads-agent": "Ads", "gtm-agent": "GTM & sales"}
LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DOC_META_KEYS = ["status", "to", "from", "type", "priority", "date", "due", "campaign", "output"]
LINK_DEPTH = 1  # also embed .md files linked from the dashboard's docs, this many hops deep
MD_LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'(][^)]*)?\)|^\s*\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)", re.M)
MARKED_SRC = "https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"


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


def split_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---[ \t]*\n?", text, re.S)
    return (front_matter(text), text[m.end():]) if m else ({}, text)


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


# ---- Doc panel: a slide-over that opens briefs, reports and strategy docs inside the dashboard ----
PANEL_CSS = """
.bcard:focus-visible,.dp a:focus-visible,.dp button:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.dp-scrim{position:fixed;inset:0;background:color-mix(in srgb,var(--bg) 62%,transparent);opacity:0;visibility:hidden;
  transition:opacity .2s ease,visibility 0s linear .2s;z-index:20}
.dp{position:fixed;top:0;right:0;bottom:0;width:min(720px,92vw);background:var(--surface);color:var(--text);
  border-left:1px solid var(--border);box-shadow:-12px 0 32px color-mix(in srgb,var(--text) 14%,transparent);
  display:flex;flex-direction:column;transform:translateX(100%);visibility:hidden;
  transition:transform .24s ease,visibility 0s linear .24s;z-index:21}
.dp-open .dp-scrim{opacity:1;visibility:visible;transition:opacity .2s ease}
.dp-open .dp{transform:none;visibility:visible;transition:transform .24s ease}
.dp-head{display:flex;align-items:center;gap:8px;padding:12px 16px;border-bottom:1px solid var(--border);background:var(--bg)}
.dp-path{flex:1;min-width:0;font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--text2);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dp-btn{flex:none;font:inherit;font-size:13px;color:var(--text);background:var(--surface);border:1px solid var(--border);
  border-radius:8px;padding:5px 10px;cursor:pointer;text-decoration:none;white-space:nowrap}
.dp-btn:hover{border-color:var(--text2)}
.dp-scroll{flex:1;overflow-y:auto;overscroll-behavior:contain;padding:20px 24px 40px}
.dp-title{font-size:21px;line-height:1.3;margin:0 0 14px}
.dp-meta{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px 16px;margin:0 0 18px;padding:14px;
  background:var(--bg);border:1px solid var(--border);border-radius:10px}
.dp-meta div{min-width:0} .dp-meta dt{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin:0 0 3px}
.dp-meta dd{margin:0;font-size:13px;overflow-wrap:anywhere}
.pill{display:inline-block;font-size:12px;font-weight:600;padding:1px 9px;border-radius:10px;color:var(--text);
  background:color-mix(in srgb,var(--c,var(--neutral)) 24%,transparent);border:1px solid color-mix(in srgb,var(--c,var(--neutral)) 55%,transparent)}
.dp-body{font-size:14px;line-height:1.6;overflow-wrap:break-word}
.dp-body h1,.dp-body h2,.dp-body h3,.dp-body h4{color:var(--text);text-transform:none;letter-spacing:0;line-height:1.3;margin:22px 0 8px}
.dp-body h1{font-size:19px} .dp-body h2{font-size:16px} .dp-body h3{font-size:14px} .dp-body h4{font-size:13px}
.dp-body p{margin:0 0 10px} .dp-body ul,.dp-body ol{margin:0 0 10px;padding-left:22px}
.dp-body a{color:var(--s1)}
.dp-body code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--grid);border-radius:4px;padding:1px 4px}
.dp-body pre{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px;overflow-x:auto;white-space:pre-wrap}
.dp-body pre code{background:none;padding:0}
.dp-body blockquote{margin:0 0 10px;padding:2px 12px;border-left:3px solid var(--border);color:var(--text2)}
.dp-body hr{border:0;border-top:1px solid var(--border);margin:18px 0}
.dp-table{overflow-x:auto;margin:0 0 12px;border:1px solid var(--border);border-radius:8px}
.dp-table table{border-collapse:collapse;min-width:100%;font-size:13px}
.dp-table th,.dp-table td{text-align:left;vertical-align:top;padding:6px 10px;border-bottom:1px solid var(--border)}
.dp-table th{background:var(--bg);color:var(--text2);font-weight:600}
.dp-table tr:last-child td{border-bottom:0}
@media (max-width:640px){.dp{width:100vw;border-left:0}.dp-scroll{padding:16px 16px 32px}.dp-head{padding:10px 12px}}
@media (prefers-reduced-motion:reduce){.dp,.dp-scrim,.dp-open .dp,.dp-open .dp-scrim{transition:none}}
"""

PANEL_HTML = """<div class="dp-scrim" data-dp-close></div>
<aside class="dp" id="dp" role="dialog" aria-modal="true" aria-labelledby="dp-title" aria-hidden="true" tabindex="-1">
<div class="dp-head"><span class="dp-path" id="dp-path"></span>
<a class="dp-btn" id="dp-gh" target="_blank" rel="noopener noreferrer">Open on GitHub ↗</a>
<button type="button" class="dp-btn" data-dp-close>Close</button></div>
<div class="dp-scroll" id="dp-scroll"><h2 class="dp-title" id="dp-title"></h2><dl class="dp-meta" id="dp-meta"></dl>
<div class="dp-body" id="dp-body"></div></div>
</aside>"""

PANEL_JS = r"""(function () {
  var dataEl = document.getElementById('hq-docs');
  if (!dataEl) return;
  var data = JSON.parse(dataEl.textContent), docs = data.docs, linkBase = data.linkBase;
  var root = document.querySelector('.viz-root'), wrap = document.querySelector('.wrap');
  var panel = document.getElementById('dp'), gh = document.getElementById('dp-gh');
  var byPath = {};
  Object.keys(docs).forEach(function (id) { byPath[docs[id].path] = id; });
  var AGENTS = __AGENTS__;
  var STATUS = {'ready': 'var(--s1)', 'in-progress': 'var(--s4)', 'done': 'var(--s3)', 'blocked': 'var(--s8)'};
  var PRIORITY = {'high': 'var(--s8)', 'medium': 'var(--s4)', 'low': 'var(--neutral)'};
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var current = null, trigger = null;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function fmtDate(s) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s || '');
    return m ? (+m[3]) + ' ' + MONTHS[+m[2] - 1] + ' ' + m[1] : s;
  }
  function pill(text, color) {
    var p = el('span', 'pill', text);
    if (color) p.style.setProperty('--c', color);
    return p;
  }
  function resolvePath(base, href) {
    try {
      var u = new URL(href, 'https://repo.invalid/' + base);
      return {path: decodeURIComponent(u.pathname.replace(/^\/+/, '')), hash: u.hash};
    } catch (e) { return null; }
  }
  function ghUrl(path) {
    return linkBase ? linkBase + path.split('/').map(encodeURIComponent).join('/') : null;
  }

  function renderMeta(meta) {
    var dl = document.getElementById('dp-meta');
    dl.textContent = '';
    var rows = [
      ['Status', meta.status && pill(meta.status.replace(/-/g, ' '), STATUS[meta.status])],
      ['Priority', meta.priority && pill(meta.priority, PRIORITY[meta.priority])],
      ['Due', meta.due && fmtDate(meta.due)],
      ['Created', meta.date && fmtDate(meta.date)],
      ['Assigned to', meta.to && (AGENTS[meta.to] || meta.to)],
      ['From', meta.from && (AGENTS[meta.from] || meta.from)],
      ['Type', meta.type],
      ['Campaign', meta.campaign],
      ['Output', meta.output]
    ];
    rows.forEach(function (r) {
      if (!r[1]) return;
      var d = el('div'), dd = el('dd');
      d.appendChild(el('dt', null, r[0]));
      if (typeof r[1] === 'string') dd.textContent = r[1]; else dd.appendChild(r[1]);
      d.appendChild(dd);
      dl.appendChild(d);
    });
    dl.hidden = !dl.childNodes.length;
  }

  function renderBody(doc) {
    var body = document.getElementById('dp-body');
    body.textContent = '';
    if (window.marked && typeof window.marked.parse === 'function') {
      try {
        body.innerHTML = window.marked.parse(doc.body, {gfm: true});
      } catch (e) { body.textContent = ''; }
    }
    if (!body.childNodes.length) {
      body.appendChild(el('pre', null, doc.body));
      return;
    }
    Array.prototype.forEach.call(body.querySelectorAll('table'), function (t) {
      var w = el('div', 'dp-table');
      t.parentNode.insertBefore(w, t);
      w.appendChild(t);
    });
    Array.prototype.forEach.call(body.querySelectorAll('a[href]'), function (a) {
      var href = a.getAttribute('href');
      if (/^#/.test(href)) return;
      if (/^[a-z][a-z0-9+.-]*:/i.test(href) || /^\/\//.test(href)) {
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        return;
      }
      var r = resolvePath(doc.path, href);
      var id = r && byPath[r.path];
      if (id) {
        a.setAttribute('href', '#' + id);
        a.setAttribute('data-doc', id);
        return;
      }
      var url = r && ghUrl(r.path);
      if (url) {
        a.setAttribute('href', url + (r.hash || ''));
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      } else {
        a.removeAttribute('href');
        a.title = (r ? r.path : href) + ' (not included in this dashboard)';
      }
    });
  }

  function show(id) {
    var doc = docs[id];
    if (!doc) return false;
    var wasOpen = current !== null;
    current = id;
    document.getElementById('dp-path').textContent = doc.path;
    document.getElementById('dp-path').title = doc.path;
    var url = doc.github || ghUrl(doc.path);
    if (url) { gh.href = url; gh.hidden = false; } else { gh.removeAttribute('href'); gh.hidden = true; }
    document.getElementById('dp-title').textContent = doc.title;
    renderMeta(doc.meta || {});
    renderBody(doc);
    document.getElementById('dp-scroll').scrollTop = 0;
    root.classList.add('dp-open');
    panel.setAttribute('aria-hidden', 'false');
    if (wrap) wrap.inert = true;
    if (!wasOpen) {
      if (!trigger) trigger = document.querySelector('.wrap [data-doc="' + id + '"]');
      panel.querySelector('[data-dp-close].dp-btn').focus({preventScroll: true});
    } else {
      panel.focus({preventScroll: true});
    }
    return true;
  }
  function hide() {
    if (current === null) return;
    current = null;
    root.classList.remove('dp-open');
    panel.setAttribute('aria-hidden', 'true');
    if (wrap) wrap.inert = false;
    var t = trigger;
    trigger = null;
    if (t && document.contains(t)) t.focus({preventScroll: true});
  }

  function hashId() {
    var h = decodeURIComponent((location.hash || '').slice(1));
    return docs[h] ? h : null;
  }
  function setHash(id) {
    var target = id ? '#' + id : location.pathname + location.search;
    if (id ? location.hash === target : !location.hash) return;
    try { history.pushState(null, '', target); }
    catch (e) { try { location.hash = id || ''; } catch (e2) { /* sandboxed: the panel still works */ } }
  }
  function open(id, from) {
    if (from && current === null) trigger = from;
    if (show(id)) setHash(id);
  }
  function close() {
    if (current === null) return;
    hide();
    if (hashId()) setHash(null);
  }
  function sync() {
    var id = hashId();
    if (id) { if (id !== current) show(id); } else hide();
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-doc]');
    if (a && docs[a.getAttribute('data-doc')] && !e.metaKey && !e.ctrlKey && !e.shiftKey && e.button === 0) {
      e.preventDefault();
      open(a.getAttribute('data-doc'), a);
      return;
    }
    if (e.target.closest && e.target.closest('[data-dp-close]')) { e.preventDefault(); close(); }
  });
  document.addEventListener('keydown', function (e) {
    if (current === null) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab') return;
    var f = Array.prototype.filter.call(panel.querySelectorAll('a[href],button,[tabindex]:not([tabindex="-1"])'),
      function (x) { return !x.hidden && x.offsetParent !== null; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && (document.activeElement === first || document.activeElement === panel)) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
  window.addEventListener('popstate', sync);
  window.addEventListener('hashchange', sync);
  window.addEventListener('load', function () { if (current) renderBody(docs[current]); });
  sync();
})();"""


def repo_root(ws: Path) -> Path:
    """The git repository root above the workspace, or the workspace's parent if it isn't in git."""
    w = ws.resolve()
    for d in (w, *w.parents):
        if (d / ".git").exists():
            return d
    return w.parent


class Docs:
    """Collects the .md files the dashboard links to, so they can be embedded and opened in a panel."""

    def __init__(self, ws: Path, out: Path, link_base: str | None):
        self.ws, self.out_dir, self.root = ws.resolve(), out.parent.resolve(), repo_root(ws)
        self.link_base = (link_base.rstrip("/") + "/") if link_base else None
        self.docs: dict[str, dict] = {}      # id -> doc
        self.ids: dict[Path, str] = {}       # resolved path -> id

    def repo_path(self, p: Path) -> str:
        p = p.resolve()
        try:
            return p.relative_to(self.root).as_posix()
        except ValueError:
            return p.as_posix()

    def github(self, p: Path) -> str | None:
        rp = self.repo_path(p)
        return self.link_base + urllib.parse.quote(rp) if self.link_base and not rp.startswith("/") else None

    def _new_id(self, p: Path) -> str:
        stem = unicodedata.normalize("NFKD", p.stem).encode("ascii", "ignore").decode()
        base = "doc-" + (re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") or "file")
        i, n = base, 2
        while i in self.docs:
            i, n = f"{base}-{n}", n + 1
        return i

    def add(self, p: Path) -> str:
        p = p.resolve()
        if p in self.ids:
            return self.ids[p]
        text = p.read_text(errors="replace")
        meta, body = split_front_matter(text)
        title = title_of(body, p.stem)
        body = re.sub(r"\A\s*#[ \t]+[^\n]*\n?", "", body, count=1)  # the H1 is shown as the panel title
        doc_id = self._new_id(p)
        self.ids[p] = doc_id
        self.docs[doc_id] = {"path": self.repo_path(p), "title": title, "github": self.github(p),
                             "meta": {k: meta[k] for k in DOC_META_KEYS if meta.get(k)}, "body": body.strip("\n") + "\n"}
        return doc_id

    def link(self, p: Path) -> str:
        """The attributes of an <a> that points at a workspace file."""
        p = p.resolve()
        if p.suffix.lower() == ".md":
            doc_id = self.add(p)
            return f'href="#{doc_id}" data-doc="{doc_id}"'
        if p.parent == self.out_dir:  # sibling dashboards stay relative; publish them next to the HQ
            return f'href="{esc(p.name)}"'
        url = self.github(p)
        if not url:
            url = Path("..", p.relative_to(self.ws)).as_posix() if self.out_dir == self.ws / "dashboards" else p.as_uri()
        return f'href="{esc(url)}"'

    def linked_files(self, doc_id: str) -> list[Path]:
        base = (self.root / self.docs[doc_id]["path"]).parent
        found = []
        for m in MD_LINK.finditer(self.docs[doc_id]["body"]):
            target = urllib.parse.unquote((m.group(1) or m.group(2)).split("#", 1)[0])
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            f = (self.root / target.lstrip("/")) if target.startswith("/") else (base / target)
            f = f.resolve()
            if f.suffix.lower() == ".md" and f.is_file() and (self.root == f or self.root in f.parents):
                found.append(f)
        return found

    def follow_links(self, depth: int = LINK_DEPTH):
        frontier = list(self.docs)
        for _ in range(depth):
            nxt = []
            for doc_id in frontier:
                for f in self.linked_files(doc_id):
                    if f not in self.ids:
                        nxt.append(self.add(f))
            frontier = nxt

    def json_block(self) -> str:
        data = {"linkBase": self.link_base, "docs": self.docs}
        js = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
        js = js.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        return f'<script type="application/json" id="hq-docs">{js}</script>'


def build(ws: Path, out: Path, today: dt.date, link_base: str | None = None) -> str:
    docs = Docs(ws, out, link_base)
    link = docs.link
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
        return (f"<a class='bcard' {link(b['path'])}><span class='chip' style='--c:{color.get(b['to'], 'var(--neutral)')}'>"
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
    reports = "".join(f"<li><a {link(f)}>{esc(f.stem)}</a></li>" for f in recent_files(ws / "reports", 8)) \
        or "<li class='muted'>No reports yet</li>"
    strat_rows = []
    for name in ("marketing-strategy", "seo", "content", "social", "paid", "email"):
        f = ws / "strategy" / f"{name}.md"
        if f.exists():
            m = re.search(r"Next review:\s*(\d{4}-\d{2}-\d{2})", f.read_text(errors="replace"))
            nr = parse_date(m.group(1)) if m else None
            state = ("<span class='warn'>⚠ review due</span>" if nr and nr <= today
                     else f"review {nr:%d %b}" if nr else "no review date")
            strat_rows.append(f"<li><a {link(f)}>{name}</a> <span class='muted'>· {state}</span></li>")
        else:
            strat_rows.append(f"<li class='muted'>{name} — not written yet</li>")
    dl_rows = "".join(f"<li><b>{d:%d %b}</b> · <a {link(p)}>{esc(t)}</a> <span class='muted'>· {esc(who)}</span></li>"
                      for d, t, who, p in deadlines[:8]) or "<li class='muted'>No upcoming deadlines</li>"

    cal = sorted((ws / "calendar").glob("*.md"), reverse=True)
    cal_link = f"<a {link(cal[0])}>{esc(cal[0].stem)}</a>" if cal else "<span class='muted'>none yet</span>"

    docs.follow_links()
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
{PANEL_CSS}</style></head>
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
</div>
{PANEL_HTML}
</div>
{docs.json_block()}
<script src="{MARKED_SRC}" defer></script>
<script>{PANEL_JS.replace('__AGENTS__', json.dumps(AGENT_LABEL))}</script>
</body></html>"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", default="marketing")
    ap.add_argument("--out", default=None)
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    ap.add_argument("--link-base", help="GitHub blob URL of the repository root, e.g. "
                    "https://github.com/<owner>/<repo>/blob/main/ (for 'Open on GitHub' and non-embedded files)")
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
