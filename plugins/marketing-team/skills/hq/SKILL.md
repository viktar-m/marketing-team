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
3. **Show it.** If the session can publish or open artifacts, publish the dashboard so the user sees it as a page (republish the same artifact each time rather than creating new ones, when the tool allows). Otherwise send the file. When a quick inline chart in the conversation is all that's needed, a summary chart is fine too.

   A published artifact holds only the files you upload, so the relative links in `marketing/dashboards/hq.html` (`../briefs/…md`, `../reports/…`, `../strategy/…`) would break there. Keep the local `hq.html` as it is (relative links, for opening from the repo) and publish a **separate copy** whose file links point at the repository:
   - Derive the link base from the remote, stripping any credentials and `.git`, on the default branch:
     ```
     url=$(git remote get-url origin | sed -E 's#^git@([^:]+):#https://\1/#; s#^(https?://)[^@/]*@#\1#; s#\.git$##')
     branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
     [ -n "$branch" ] || branch=$(git ls-remote --symref origin HEAD | sed -n 's#^ref: refs/heads/\([^[:space:]]*\).*#\1#p')
     ```
     Never put a token or username into the page. If the remote is a local proxy rather than the real host (e.g. `http://127.0.0.1:…/git/<owner>/<repo>`), use `https://github.com/<owner>/<repo>` instead.
   - Build the published copy outside the dashboards folder, e.g. in the scratchpad:
     `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hq.py --workspace marketing --out <scratch>/hq.html --link-base "$url/blob/${branch:-main}/"`
     Every brief, report, strategy and calendar link then opens the file on GitHub in a new tab. Links to sibling dashboards (`ai-visibility.html`) stay relative.
   - Publish `<scratch>/hq.html` as the page with `marketing/dashboards/ai-visibility.html` as a supporting file at published path `ai-visibility.html` (when it exists), so the "Full AI visibility dashboard" link works.
   - The links point at the default branch, so they only resolve once the files are pushed there. If you are on another branch, push and merge first, or tell the user which cards will 404 until then.
4. **Add the human layer** in a few lines under the dashboard:
   - what changed since the last HQ (new reports, closed briefs, new overdue items)
   - what needs the user: approvals, assets to supply, decisions, overdue briefs
   - what the team will do next (top 3 ready briefs by priority)
5. In a git workspace, commit the refreshed dashboards (`hq: refresh`) and push.

Don't paste the board's contents into the chat as text — the dashboard is the view; the chat carries only the summary and the asks.
