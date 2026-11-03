# AI Marketing Team for Claude

A two-agent marketing team that plugs into Claude. An **SEO agent** decides what the site needs; a **content agent** writes it. Both read one **brand brief**, so everything they produce sounds like your company — and the same team can be set up for any company by swapping the brief.

```
You: "Get more traffic to our pricing page."

Team lead ─▶ SEO agent      audits the page, researches keywords, finds gaps
                 │           writes 3 prioritised content briefs
                 ▼
             Content agent  refreshes the pricing page, writes a supporting
                            article, and cuts it into LinkedIn / X / Facebook posts
```

## What's inside

| Agent | Role | Skills |
|-------|------|--------|
| **SEO agent** | Strategy: what to create, fix or refresh — and why | `seo-audit` · `keyword-research` · `content-gap` |
| **Content agent** | Production: publish-ready content in the brand voice | `blog-create` · `page-create` · `page-refresh` · `social-post` · `social-repurpose` · `social-calendar` |

Plus two team skills:

- **`team-lead`** — routes any marketing request to the right agent, relays SEO briefs to the content agent, and runs the recurring routines
- **`brand-setup`** — builds the brand brief from your website and a few questions

## How it works

1. **One brand brief** (`marketing/brand-brief.md`) holds product facts, audience, positioning, voice, keywords, social platforms, CTAs and red lines. Agents read it before every task. Nothing brand-specific is hard-coded in the skills.
2. **Routing by description.** Claude picks the agent and skill whose description matches the request. Ask in plain words — "audit our blog", "write a post about X", "plan next week's posts" — or call a skill by name, e.g. `/marketing-team:seo-audit`.
3. **Handoffs through files.** The SEO agent writes content briefs to `marketing/briefs/`; the team lead hands them to the content agent; the content agent marks them done. Everything is traceable.
4. **Team memory.** `marketing/content-inventory.md` records every piece produced or refreshed, so the team doesn't repeat itself and can link new work to old.
5. **Recurring work.** Weekly SEO audits, weekly social calendars, monthly gap analyses and monthly refreshes run as scheduled tasks. See [docs/scheduling.md](docs/scheduling.md).

More detail in [docs/architecture.md](docs/architecture.md).

## Install

### Claude Code

```
/plugin marketplace add viktar-m/marketing-team
/plugin install marketing-team@ai-marketing-team
```

### Claude app (desktop / web)

Zip the `plugins/marketing-team` folder and upload it as a plugin in the Claude app's settings. Agents and file-based handoffs work best where Claude has a working folder (Claude Code, or a Claude desktop task with a folder connected).

## Get started

1. **Create the brand brief:** "Set up the marketing team for <your website URL>." The `brand-setup` skill drafts `marketing/brand-brief.md` and asks a few questions. Want to try it first? Copy [`templates/sample-brand-brief.md`](plugins/marketing-team/templates/sample-brand-brief.md) (a fictional company) to `marketing/brand-brief.md`.
2. **Connect your data (optional but recommended):** Google Search Console, Analytics, Ahrefs or Semrush. Without them, the SEO agent works from public data and labels its numbers as estimates.
3. **Give the team a task.** Examples:
   - "Run an SEO audit of our blog."
   - "Where are our competitors beating us?"
   - "Refresh this page: https://…"
   - "Write a blog article about <topic>, then turn it into posts."
   - "Plan next week's LinkedIn, X and Facebook posts."
4. **Schedule the routines** in [docs/scheduling.md](docs/scheduling.md).

## Workspace

The team works in a `marketing/` folder in your project:

```
marketing/
├── brand-brief.md
├── content-inventory.md
├── briefs/          SEO agent → content agent
├── content/         blog/ · pages/ · refreshes/ · social/
├── reports/         audits, keyword research, gap analyses
└── calendar/        weekly social calendars
```

`marketing/` is git-ignored here on purpose: the framework is public, your brand data and drafts stay private.

## Design principles

- **Strategy and production are separate agents.** SEO decides what and why; content decides how. Neither does the other's job.
- **No invented facts.** Unverifiable claims are marked `[VERIFY]` and listed for a human check before publishing.
- **Autonomous by default.** Agents make reasonable choices and state them, rather than stopping for approval at every step.
- **Brand-agnostic.** Swap the brief, get a different company's team.

## Customise

- **Add a platform** (e.g., Instagram): add `skills/social-post/platforms/instagram.md` and mention it in the `social-post` skill.
- **Add an agent** (e.g., email marketing): add `agents/email-agent.md`, its skills under `skills/`, and a row in `team-lead`.
- **Change a standard** for every agent: edit `templates/conventions.md`.

## Roadmap

- [ ] Email agent: newsletters, nurture sequences
- [ ] Analytics agent: monthly performance reports from connected data
- [ ] Paid social / ads copy
- [ ] Instagram and YouTube platform guides

## License

MIT — see [LICENSE](LICENSE).
