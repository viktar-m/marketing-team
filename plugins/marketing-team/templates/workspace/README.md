# Marketing workspace — {{PRODUCT}}

Private working files for the [AI marketing team](https://github.com/viktar-m/marketing-team): the brand brief, strategy, briefs, drafts, reports, dashboards and AI visibility data. The team reads and writes everything under `marketing/`. Each scheduled run pulls the latest files, does its work, and commits the results here.

**Keep this repository private.** It holds brand data and unpublished work.

## Start here

Open **`marketing/hub.html`** — the Marketing Hub: what needs you, the work queue, and every piece of work, readable in one place. (Or ask Claude: "show me the Hub".)

## Setup checklist

- [ ] **Brand brief:** ask Claude "Set up the marketing team for <website>" with this repo connected
- [ ] **Strategy:** "Write our marketing strategy"
- [ ] **Brand kit:** "Set up our brand kit" (put the logo and screenshots in `marketing/design/assets/` first)
- [ ] **AI visibility:** "Set up AI visibility tracking", then add the `OPENAI_API_KEY` secret (Settings → Secrets and variables → Actions). [Guide](https://github.com/viktar-m/marketing-team/blob/main/docs/ai-visibility.md)
- [ ] **Routines:** ask Claude to schedule the weekly and monthly routines. [List](https://github.com/viktar-m/marketing-team/blob/main/docs/scheduling.md)

## Automation in this repo

`.github/workflows/ai-visibility.yml` tracks AI visibility. Daily schedule: **{{SCHEDULE_STATE}}**. It does nothing until `marketing/ai-visibility/config.json` exists and an API key secret is set; run it manually from the Actions tab, and see the workflow file to turn the schedule on or off.

## Layout

```
marketing/
├── hub.html          the Marketing Hub — open this
├── index.md          list of all work (generated)
├── brand-brief.md    who we are, how we sound, who we sell to
├── strategy/         the rules the team follows
├── web/ social/ video/ design/ ads/ sales/      the work, by area
├── launches/ campaigns/ research/               plans, analyses, audits
├── queue/            briefs waiting for an agent
└── site/ ai-visibility/ dashboards/             the team's working data
```
