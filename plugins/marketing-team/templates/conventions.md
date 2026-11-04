# Team conventions

Every agent and skill in the marketing team follows these rules. They keep the work consistent, let agents hand work to each other, and let the team remember what it has done.

## 1. Read before you work

Before any task, read:

1. **The brand brief** — `marketing/brand-brief.md` (in a claude.ai chat with no folder, the Project's knowledge files). Product facts, audience, positioning, voice, terminology, CTAs, red lines.
2. **The strategy file for your channel** — `marketing/strategy/`. `marketing-strategy.md` applies to everyone; then `seo.md`, `content.md`, `social.md`, `paid.md` or `email.md` for your area. Strategy decides priorities, targets and rules; follow it. If your work would break a strategy rule, say so instead of quietly deviating.
3. **The brand kit** for anything visual — `marketing/design/brand-kit.md`.
4. **The brief you were handed**, if any — it overrides defaults.

If the brand brief is missing: for a quick task, go ahead, state your assumptions at the top of the output, and suggest `brand-setup`. For larger work, stop and offer `brand-setup` first. If a strategy file is missing, work from the brand brief and mention that the strategist can create one.

Never hard-code brand facts into skills or agents. When you learn a durable fact during a task, suggest adding it to the brief.

## 2. Workspace layout

```
marketing/
├── brand-brief.md
├── content-inventory.md          # everything produced or refreshed
├── strategy/                     # strategist owns
│   ├── marketing-strategy.md
│   └── seo.md · content.md · social.md · paid.md · email.md
├── briefs/                       # all handoffs between agents
├── campaigns/<slug>/             # campaign and promo plans
├── launches/<slug>/              # product launch kits
├── site/site-index.md            # page index used for internal linking
├── content/
│   ├── blog/ · pages/ · refreshes/ · social/ · video/
├── design/
│   ├── brand-kit.md
│   ├── assets/                   # logos, photos, screenshots the user supplies
│   └── graphics/<date-slug>/     # finished graphics
├── ads/
│   ├── campaigns/<slug>/
│   └── reports/
├── sales/                        # enablement materials
├── ai-visibility/                # tracker config, raw data, history
├── artifacts.md                  # links to designs, design system, videos in Claude
├── reports/                      # audits, research, reviews
├── calendar/                     # weekly social calendars (YYYY-Www.md)
└── dashboards/                   # visual HTML dashboards, incl. hq.html
```

Create folders as needed. Lowercase, hyphenated slugs; dates are the day the work is done (`YYYY-MM-DD-<slug>`).

If the workspace is a git repository, run `git pull` before starting, and when finished, commit your changes with a one-line message saying what the team did (e.g., `seo-agent: weekly audit, 3 briefs`) and push.

## 3. Content inventory

After producing or refreshing any piece, append a row to `marketing/content-inventory.md` (create it with this header if missing):

```
| Date | Type | Title | Primary keyword | Location / URL | Agent | Status |
|------|------|-------|-----------------|----------------|-------|--------|
```

Status: `draft`, `ready`, `published`, `refreshed`. Check the inventory before proposing new work, to avoid duplicates and to find things to link to or repurpose.

## 4. Handoffs: briefs

Agents hand work to each other with **briefs** in `marketing/briefs/YYYY-MM-DD-<slug>.md`, using `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`. The `to:` field names the receiving agent; `type:` names the deliverable.

- Status moves `ready` → `in-progress` → `done`. The receiver sets `in-progress` when starting and `done` (with `output:`) when finished.
- Subagents can't call each other. An agent writes briefs and returns their paths; the main session (team lead) hands each brief to the named agent.
- Anything visual goes to the **design-agent** as a brief with `type: graphic`. Other agents describe what they need (purpose, size, message); they don't make final graphics themselves.
- Keep a run's queue short: at most 5 briefs per run unless the user asks for more.

## 5. Work that lives in Claude (artifacts)

Some deliverables live in Claude rather than in the workspace: **Design** canvases (graphics, ads, mockups), the **Design System** (the brand kit), **Motion** videos, and published dashboards. When you create or update one:

- Add or update a row in `marketing/artifacts.md` (create it with this header if missing):
  ```
  | Date | Type | Title | Link | Brief / campaign | Agent |
  |------|------|-------|------|------------------|-------|
  ```
- Put the link in the brief's `output:` and in the content inventory's Location column.
- Revise an existing artifact (use its link) rather than creating a duplicate.

Artifact tools are only available in some sessions (the Claude app, and Claude Code sessions that offer them). Where they aren't, use the file-based fallback the skill describes and say so.

## 6. Depth and evidence

- Research follows `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md`: the client's whole site, competitors' own pricing pages and listings (dated), a sweep for new entrants.
- Strategic deliverables follow `${CLAUDE_PLUGIN_ROOT}/templates/analysis-standards.md`: explain simply first, answer the real decisions with recommendation → reasoning → trade-offs → test, show the math, and pass the generic-advice test.
- If the session blocks you from writing files, return the complete deliverable in your final message so the team lead can save it — never a shortened version.

## 7. Facts and claims

- Never invent statistics, customer names, quotes, awards, benchmarks, prices or feature claims.
- Product claims come from the brand brief or the user's own pages; external facts need a source link.
- Mark anything unverified `[VERIFY]` in the text and list it under **To verify**.
- Be fair to competitors and alternatives; compare on facts.

## 8. Output and visuals

- The record of every task is Markdown in the workspace folder above.
- Reports with numbers (audits, AI visibility, ads, performance, research) also get a **visual dashboard**: follow `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`.
- Produce Word, PowerPoint or PDF only when asked or when the brief says so.
- End every task with a short summary: what was produced, where it is, what needs a human check.
- Work autonomously: make sensible choices and state them; ask only when a missing input would make the result wrong.
