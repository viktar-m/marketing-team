---
name: hq
description: 'Show the Marketing HQ - a visual dashboard of the whole team: open briefs on a board by status and agent, overdue work, upcoming deadlines and launches, content produced per week, AI share of voice, latest reports and strategy review dates. Use for "show me the dashboard / HQ", "what is the team working on", "status update", at the start of a working session, and at the end of every scheduled routine.'
---

# Marketing HQ

1. If the workspace is a git repository, `git pull` first.
2. Build the dashboard:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hq.py --workspace marketing --out marketing/dashboards/hq.html
   ```
   If AI visibility data exists but its dashboard is older than the latest data, rebuild it first:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py report --dir marketing/ai-visibility --out marketing/dashboards/ai-visibility.html`
3. **Show it.** If the session can publish or open artifacts, publish `hq.html` so the user sees it as a page (republish the same artifact each time rather than creating new ones, when the tool allows). Otherwise send the file. When a quick inline chart in the conversation is all that's needed, a summary chart is fine too.
4. **Add the human layer** in a few lines under the dashboard:
   - what changed since the last HQ (new reports, closed briefs, new overdue items)
   - what needs the user: approvals, assets to supply, decisions, overdue briefs
   - what the team will do next (top 3 ready briefs by priority)
5. In a git workspace, commit the refreshed dashboards (`hq: refresh`) and push.

Don't paste the board's contents into the chat as text — the dashboard is the view; the chat carries only the summary and the asks.
