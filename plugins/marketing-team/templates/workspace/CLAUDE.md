# Marketing workspace

This repository is the working folder of an AI marketing team. Everything lives under `marketing/` (brand brief, strategy, briefs, content, reports, dashboards).

## The team

The team is the **marketing-team** plugin (https://github.com/viktar-m/marketing-team): 7 agents (strategist, seo-agent, web-content-agent, social-agent, design-agent, ads-agent, gtm-agent) and their skills.

- If the plugin's skills (`marketing-team:team-lead` etc.) are available, use them: route every marketing request through `marketing-team:team-lead`.
- If they are **not** available, tell the user to install the plugin, then restart the session:
  - Claude Code / Code tab: `/plugin marketplace add viktar-m/marketing-team` then `/plugin install marketing-team@ai-marketing-team`
  - Claude app: Customize → Plugins → + → Add marketplace → `viktar-m/marketing-team` → install **marketing-team**

## How to work here

1. **Start of a session:** `git pull`. If the user asks "what's going on" or starts without a task, run `marketing-team:hq` and summarise what needs them.
2. **Every request** goes through `marketing-team:team-lead`, which picks the agent and relays briefs between agents.
3. **Always read** `marketing/brand-brief.md` and the relevant `marketing/strategy/*.md` before working.
4. **End of a task:** update `marketing/content-inventory.md`, refresh the HQ, commit with a message naming the agent and what it did (e.g. `web-content-agent: homepage refresh`), and push.
5. One chat or session per task. The files are the team's memory; chats don't need to carry history.

## Status

- Product: {{PRODUCT}}{{WEBSITE_SUFFIX}}
- Workspace created {{DATE}}. Recurring routines: none scheduled yet. Daily AI visibility schedule: {{SCHEDULE_STATE}}.
