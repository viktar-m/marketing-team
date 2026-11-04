---
name: hq
description: 'Show the Marketing HQ - a visual dashboard of the whole team: open briefs on a board by status and agent, overdue work, upcoming deadlines and launches, content produced per week, AI share of voice, latest reports and strategy review dates. Use for "show me the dashboard / HQ", "what is the team working on", "status update", at the start of a working session, and at the end of every scheduled routine.'
---

# Marketing HQ

1. If the workspace is a git repository, `git pull` first.
2. Build the dashboard. Briefs, reports and strategy docs are embedded in the page and open in a side panel
   when clicked; `--link-base` (the repository's GitHub "blob" URL) powers the panel's "Open on GitHub" button and
   links to files that aren't embedded. In a git workspace, derive it from the origin remote (credentials stripped,
   default branch):
   ```
   remote=$(git remote get-url origin 2>/dev/null | sed -E 's#^git@([^:]+):#https://\1/#; s#://[^/@]*@#://#; s#\.git$##; s#^https?://(127\.0\.0\.1|localhost)(:[0-9]+)?/git/#https://github.com/#')
   branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
   [ -n "$branch" ] || branch=$(git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p')
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hq.py --workspace marketing --out marketing/dashboards/hq.html \
     ${remote:+--link-base "$remote/blob/${branch:-main}/"}
   ```
   Without a remote, leave `--link-base` out: docs still open in the panel, the GitHub button is hidden.
   If AI visibility data exists but its dashboard is older than the latest data, rebuild it first:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py report --dir marketing/ai-visibility --out marketing/dashboards/ai-visibility.html`
3. **Show it.** If the session can publish or open artifacts, publish `hq.html` so the user sees it as a page (republish the same artifact each time rather than creating new ones, when the tool allows). The page is self-contained except for its link to the AI visibility dashboard: when `marketing/dashboards/ai-visibility.html` exists, publish it as a supporting file next to the HQ, at the published path `ai-visibility.html` (e.g. `files: {"ai-visibility.html": "marketing/dashboards/ai-visibility.html"}`), so that link works too. Otherwise send the file. When a quick inline chart in the conversation is all that's needed, a summary chart is fine too.
4. **Add the human layer** in a few lines under the dashboard:
   - what changed since the last HQ (new reports, closed briefs, new overdue items)
   - what needs the user: approvals, assets to supply, decisions, overdue briefs
   - what the team will do next (top 3 ready briefs by priority)
5. In a git workspace, commit the refreshed dashboards (`hq: refresh`) and push.

Don't paste the board's contents into the chat as text — the dashboard is the view; the chat carries only the summary and the asks.
