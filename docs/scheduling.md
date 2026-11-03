# Recurring routines

Routines are defined in the `team-lead` skill. Set each one up as a scheduled task in Claude, or ask Claude to "schedule the weekly SEO routine". Each run starts fresh and works from the workspace files. In a git workspace, each run pulls first and commits and pushes at the end.

| Routine | Suggested time | What happens |
|---------|----------------|--------------|
| AI visibility tracking | daily (GitHub Action, not Claude) | Asks the AI engines your questions and records the results. See [ai-visibility.md](ai-visibility.md) |
| `weekly-ai-visibility` | Monday | Sentiment, diagnosis of lost questions, up to 5 briefs |
| `weekly-seo` | Tuesday | Audit of commercial and recently changed pages; up to 3 briefs completed |
| `weekly-social` | Thursday | Next week's posts and the graphics for them |
| `weekly-ads` | Friday | Ad performance review and recommended changes (only if ads are running) |
| `monthly-gaps` | 1st | Competitor gap analysis and keyword research; up to 3 briefs completed |
| `monthly-refresh` | 15th | The 3 pages most in need of a refresh, refreshed |
| `quarterly-strategy` | first week of the quarter | Strategy files reviewed and updated against results |

Every routine ends by refreshing the Marketing HQ dashboard.

## Prompt pattern

> Use the marketing-team `team-lead` skill to run the `<routine>` routine for the workspace in `<folder or repo>`. Pull the latest files first, follow `marketing/brand-brief.md` and the strategy files, complete at most 3 briefs, commit and push the results, refresh the HQ, and finish with a short summary of what was done and what needs my review.

## Tips

- Nothing is published, posted or changed in ad accounts automatically. Routines produce drafts, reports and recommendations for you to review.
- Connect Search Console, Analytics and your ad platforms before scheduling the SEO and ads routines.
- If you're away for a while, briefs stay `ready` and the next run picks them up. The HQ shows anything overdue.
