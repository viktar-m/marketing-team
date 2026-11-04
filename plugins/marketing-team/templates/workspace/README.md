# Marketing workspace — {{PRODUCT}}

Private working files for the [AI marketing team](https://github.com/viktar-m/marketing-team): the brand brief, strategy, briefs, drafts, reports, dashboards and AI visibility data. The team reads and writes everything under `marketing/`. Each scheduled run pulls the latest files, does its work, and commits the results here.

**Keep this repository private.** It holds brand data and unpublished work.

## Start here

| | |
|---|---|
| Team dashboard | [`marketing/dashboards/hq.html`](marketing/dashboards/hq.html) (download it, or ask Claude to "show me the HQ") |
| Brand brief | [`marketing/brand-brief.md`](marketing/brand-brief.md) |
| Work queue | [`marketing/briefs/`](marketing/briefs/) |
| Everything produced | [`marketing/content-inventory.md`](marketing/content-inventory.md) |

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
├── brand-brief.md         who we are, how we sound, who we sell to
├── content-inventory.md   everything the team has produced
├── strategy/              strategist's rules for each channel
├── briefs/                handoffs between agents (the work queue)
├── campaigns/  launches/  plans and timelines
├── content/               blog, pages, refreshes, social, video
├── design/                brand kit, assets (add yours), graphics
├── ads/  sales/           ad plans and reports; sales materials
├── ai-visibility/         tracker config, daily data, history
├── site/                  site index and internal-link tasks
├── reports/  calendar/    audits, reviews; weekly social calendars
└── dashboards/            hq.html, ai-visibility.html, …
```
