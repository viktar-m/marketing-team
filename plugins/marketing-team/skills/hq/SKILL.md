---
name: hq
description: 'Show the Marketing Hub - a simple project board of all marketing work, filtered by area (strategy, content, SEO & AI visibility, social & video, design, ads, GTM & sales) and stage (to do, in progress, needs you, done), with goal progress, what needs the user, a built-in reader and links to dashboards and designs. Use for "show me the Hub / HQ / dashboard", "what is the team working on", "what needs me", "status update", at the start of a working session, and at the end of every routine.'
---

# Marketing Hub

The Hub is a project board: every task is one card with an **area** and a **stage** (to do → in progress → needs you → done), goals from `marketing/goals.md` show progress, and clicking a card opens the work. Stages come from each file's `status:` (conventions §3).

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
5. Reply in a few lines, not a report: the Hub link, then **Needs you** (up to 5 actions, most urgent first, each with its task), **Up next** (top 3 to-do tasks by priority and due date) and, if goals exist, one line per goal (`2 of 5 done, by Jan 31`). Nothing else.
6. In a git workspace, commit (`hub: refresh`) and push.
