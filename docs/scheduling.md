# Recurring routines

The `team-lead` skill defines four routines. Set each one up as a scheduled task in Claude (ask Claude: "schedule this every Monday at 8:00") or in Claude Code. Each run starts in a fresh session, so the prompts below are self-contained and point to the workspace files.

| Routine | Suggested schedule | What happens |
|---------|-------------------|--------------|
| `weekly-seo` | Monday morning | Audit of commercial and recently changed pages; up to 3 fixes written |
| `weekly-social` | Friday | Next week's LinkedIn / X / Facebook posts drafted into `marketing/calendar/` |
| `monthly-gaps` | 1st of the month | Competitor gap analysis + keyword research; up to 3 new pieces written |
| `monthly-refresh` | 15th of the month | The 3 pages most in need of a refresh are refreshed |

## Prompts

**weekly-seo**
> Use the marketing-team `team-lead` skill to run the `weekly-seo` routine for the project in this folder. Read `marketing/brand-brief.md` first. Save the audit to `marketing/reports/`, have the content agent complete the top 3 briefs, and finish with a short summary of findings, outputs, and anything that needs my review.

**weekly-social**
> Use the marketing-team `team-lead` skill to run the `weekly-social` routine: plan and draft next week's posts for LinkedIn, X and Facebook into `marketing/calendar/`, based on `marketing/brand-brief.md` and recent entries in `marketing/content-inventory.md`. Finish with the overview table and anything that needs my input.

**monthly-gaps**
> Use the marketing-team `team-lead` skill to run the `monthly-gaps` routine against the competitors in `marketing/brand-brief.md`. Save the reports to `marketing/reports/`, have the content agent complete the top 3 briefs, and summarise what was found and produced.

**monthly-refresh**
> Use the marketing-team `team-lead` skill to run the `monthly-refresh` routine: pick the 3 pages most in need of a refresh, write refresh briefs, have the content agent refresh them, and summarise the changes and what I should check before publishing.

## Tips

- Nothing is published automatically. Routines produce drafts and reports; you review and publish.
- Connect Search Console / Analytics before scheduling SEO routines — measured data makes the weekly audit far more useful.
- If you're away for a while, leftover briefs stay at `status: ready` and the next run picks them up.
