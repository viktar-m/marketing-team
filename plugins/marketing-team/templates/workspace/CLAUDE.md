# Marketing workspace

This folder is the workspace of an AI marketing team (the **marketing-team** plugin: strategist, seo-agent, web-content-agent, social-agent, design-agent, ads-agent, gtm-agent). Everything lives under `marketing/`. The user reads the work in **`marketing/hub.html`** — the Marketing Hub.

- If the plugin's skills (`marketing-team:team-lead` etc.) are available, route every marketing request through `marketing-team:team-lead`.
- If they are **not** available, tell the user to install the plugin and restart: Claude Code: `/plugin marketplace add viktar-m/marketing-team` then `/plugin install marketing-team@ai-marketing-team`; Claude app: Customize → Plugins → + → Add marketplace → `viktar-m/marketing-team`.

## How to work here

1. **Start of a session:** if this is a git repo, `git pull`. If the user starts without a task or asks "what's going on", show the Hub (`marketing-team:hq`) and list what needs them.
2. **Every request** goes through `marketing-team:team-lead`. Read `marketing/brand-brief.md` and the relevant `marketing/strategy/*.md` first.
3. **One task, one deliverable file** with the standard header; no briefs unless the user agrees to follow-up work.
4. **Reply with the short done message** — title, one link, up to 3 things that need the user, one suggested next step. No file paths or process narration.
5. **End of a task:** rebuild the Hub (`python3 <plugin>/scripts/hub.py --workspace marketing`), republish it if it's published, and (in git) commit and push.
6. One chat per task. The files are the team's memory.

## Status

- Product: {{PRODUCT}}{{WEBSITE_SUFFIX}}
- Workspace created {{DATE}}. Recurring routines: none scheduled yet. Daily AI visibility schedule: {{SCHEDULE_STATE}}.
