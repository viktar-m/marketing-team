#!/usr/bin/env python3
"""Set up (or repair) a marketing workspace for the marketing team.

Creates, without overwriting anything that already exists:
  CLAUDE.md, README.md, .gitignore           session instructions and a human guide
  .github/workflows/ai-visibility.yml        daily AI visibility tracker (schedule off by default)
  marketing/...                              the folder structure from the team conventions
  marketing/brand-brief.md                   the brand brief template, ready for brand-setup
  marketing/content-inventory.md             empty inventory with its header
  marketing/dashboards/hq.html               an empty Marketing HQ

Usage
  python3 init_workspace.py --root . --product "Acme Pantry" [--website https://acme.example] [--schedule on]

Standard library only. Prints what it created and what it left alone.
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
FOLDERS = ["strategy", "briefs", "campaigns", "launches", "site", "content", "design/assets", "ads", "sales",
           "ai-visibility", "reports", "calendar", "dashboards"]
INVENTORY_HEADER = ("| Date | Type | Title | Primary keyword | Location / URL | Agent | Status |\n"
                    "|------|------|-------|-----------------|----------------|-------|--------|\n")
GITIGNORE = ".env\n.env.*\n__pycache__/\n.DS_Store\n*.tmp\n"
SCHEDULE_ON = '''  schedule:
    - cron: "17 5 * * *"   # daily at 05:17 UTC
'''
SCHEDULE_OFF = '''  # Daily schedule is off. To turn it on, uncomment the two lines below.
  # schedule:
  #   - cron: "17 5 * * *"   # daily at 05:17 UTC
'''


def fill(text: str, values: dict) -> str:
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="workspace root (the repository or folder)")
    ap.add_argument("--product", required=True, help="product, company or client name")
    ap.add_argument("--website", default="")
    ap.add_argument("--schedule", choices=["on", "off"], default="off",
                    help="daily AI visibility schedule (default off; turn on once config and API key exist)")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    values = {
        "PRODUCT": a.product,
        "WEBSITE_SUFFIX": f" ({a.website})" if a.website else "",
        "DATE": today,
        "SCHEDULE_STATE": "on" if a.schedule == "on" else "off",
    }
    created, kept = [], []

    def write(rel: str, content: str):
        p = root / rel
        if p.exists():
            kept.append(rel)
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        created.append(rel)

    write("CLAUDE.md", fill((TEMPLATES / "workspace" / "CLAUDE.md").read_text(), values))
    write("README.md", fill((TEMPLATES / "workspace" / "README.md").read_text(), values))
    write(".gitignore", GITIGNORE)

    wf = (TEMPLATES / "workspace" / "github-workflows" / "ai-visibility.yml").read_text()
    if a.schedule == "off":
        wf = wf.replace(SCHEDULE_ON, SCHEDULE_OFF)
    write(".github/workflows/ai-visibility.yml", wf)

    brief = (TEMPLATES / "brand-brief-template.md").read_text()
    brief = brief.replace("# Brand brief: <Company or product name>", f"# Brand brief: {a.product}", 1)
    if a.website:
        brief = brief.replace("- **Website:** main URL", f"- **Website:** {a.website}", 1)
    write("marketing/brand-brief.md", brief)
    write("marketing/content-inventory.md", INVENTORY_HEADER)
    write("marketing/artifacts.md", "# Work in Claude\n\nDesigns, the design system, videos and dashboards that live in Claude.\n\n"
          "| Date | Type | Title | Link | Brief / campaign | Agent |\n|------|------|-------|------|------------------|-------|\n")

    for folder in FOLDERS:
        d = root / "marketing" / folder
        d.mkdir(parents=True, exist_ok=True)
        if not any(d.iterdir()):
            (d / ".gitkeep").write_text("")

    hq = root / "marketing" / "dashboards" / "hq.html"
    if not hq.exists():
        subprocess.run([sys.executable, str(HERE / "hq.py"), "--workspace", str(root / "marketing"),
                        "--out", str(hq)], check=False, stdout=subprocess.DEVNULL)
        if hq.exists():
            created.append("marketing/dashboards/hq.html")

    print(f"Workspace for {a.product} at {root}")
    print("Created:" if created else "Created: nothing new")
    for c in created:
        print(f"  + {c}")
    if kept:
        print("Left unchanged (already existed):")
        for k in kept:
            print(f"  = {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
