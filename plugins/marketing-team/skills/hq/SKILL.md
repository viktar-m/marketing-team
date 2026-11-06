---
name: hq
description: 'Show the Marketing Hub - one page with everything the team made: what needs the user, the work queue, every deliverable by area (web, social, design, ads, sales, research, strategy) with a built-in reader, and links to dashboards and designs. Use for "show me the Hub / HQ / dashboard", "what is the team working on", "what needs me", "status update", at the start of a working session, and at the end of every routine.'
---

# Marketing Hub

1. In a git workspace, `git pull` first.
2. If AI visibility data exists and its dashboard is older than the data, rebuild it:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py report --dir marketing/ai-visibility --out marketing/dashboards/ai-visibility.html`
3. Build the Hub (also regenerates `marketing/index.md`):
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hub.py --workspace marketing
   ```
4. **Show it.**
   - If the session can publish artifacts: publish `marketing/hub.html` as `index.html`, plus each file in `marketing/dashboards/` at `dashboards/<name>.html` (the Hub links to them). Republish the **same** artifact every time — its link is the "Marketing Hub" row in `marketing/artifacts.md` (add the row the first time). Item links are that URL plus `#<item-id>`.
   - Otherwise, give the user the path to `marketing/hub.html` to open in a browser.
5. Reply in a few lines, not a report: the Hub link, then **Needs you** (up to 5 items, most urgent first, each with the item it belongs to) and **Ready in the queue** (top 3). Nothing else.
6. In a git workspace, commit (`hub: refresh`) and push.
