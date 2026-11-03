#!/usr/bin/env python3
"""Render HTML graphics to PNG at exact sizes, and build a contact sheet.

Each graphic is a self-contained HTML file whose <body> is the canvas. Declare its size with
    <meta name="graphic-size" content="1080x1350">
Optionally declare several sizes for one design (the layout must be responsive):
    <meta name="graphic-size" content="1080x1080,1080x1350,1200x627">

Usage
  python3 render_graphics.py <folder-or-file> [...] [--scale 1] [--sheet contact-sheet.png]

PNG files are written next to each HTML file as <name>-<w>x<h>.png.
Requires Playwright with Chromium (pip install playwright && playwright install chromium).
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

SIZE_RE = re.compile(r'<meta\s+name=["\']graphic-size["\']\s+content=["\']([^"\']+)["\']', re.I)


def sizes_of(path: Path) -> list[tuple[int, int]]:
    m = SIZE_RE.search(path.read_text(errors="replace"))
    if not m:
        return [(1080, 1080)]
    out = []
    for part in m.group(1).split(","):
        w, h = part.lower().strip().split("x")
        out.append((int(w), int(h)))
    return out


def collect(targets: list[str]) -> list[Path]:
    files = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            files += sorted(x for x in p.glob("*.html") if not x.name.startswith("_"))
        elif p.suffix.lower() == ".html":
            files.append(p)
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--scale", type=float, default=1.0, help="device scale factor (2 for retina-sharp exports)")
    ap.add_argument("--sheet", help="also write a contact sheet PNG of everything rendered")
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed. Run: pip install playwright && playwright install chromium",
              file=sys.stderr)
        return 2
    files = collect(a.targets)
    if not files:
        print("No .html graphics found.", file=sys.stderr)
        return 1
    rendered = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for f in files:
            for w, h in sizes_of(f):
                page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=a.scale)
                page.goto(f.resolve().as_uri())
                page.wait_for_load_state("networkidle")
                page.evaluate("document.fonts && document.fonts.ready")
                out = f.with_name(f"{f.stem}-{w}x{h}.png")
                page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": w, "height": h})
                page.close()
                rendered.append((out, w, h))
                print(f"{out}")
        if a.sheet and rendered:
            cells = "".join(
                f'<figure><img src="{o.resolve().as_uri()}" style="aspect-ratio:{w}/{h}">'
                f'<figcaption>{html.escape(o.name)}</figcaption></figure>' for o, w, h in rendered)
            sheet_html = Path(a.sheet).with_suffix(".html")
            sheet_html.write_text(
                "<html><body style='margin:0;padding:24px;background:#f2f2f0;font:13px system-ui'>"
                "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px'>"
                + cells.replace("<figure>", "<figure style='margin:0'>").replace(
                    "<img ", "<img style='width:100%;display:block;border-radius:6px;"
                            "box-shadow:0 1px 4px #0002' ")
                + "</div></body></html>")
            page = browser.new_page(viewport={"width": 1200, "height": 800})
            page.goto(sheet_html.resolve().as_uri())
            page.wait_for_load_state("networkidle")
            page.screenshot(path=a.sheet, full_page=True)
            sheet_html.unlink()
            print(f"contact sheet: {a.sheet}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
