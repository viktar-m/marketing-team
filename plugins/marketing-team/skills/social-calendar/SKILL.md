---
name: social-calendar
description: 'Plan a week (or several) of social media posts across LinkedIn, X and Facebook — balanced across the brand''s content pillars, built around recent and upcoming content, launches and dates — with every post drafted and ready to schedule. Use for "plan next week''s posts", content calendars, the recurring weekly social routine, or filling gaps in an existing schedule.'
---

# Social calendar

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first — especially the social section: active platforms, cadence, goal per platform and content pillars.

## Inputs

The period (default: the next ISO week, Monday to Sunday). Optional: launches, events, campaigns, posts already scheduled.

## Workflow

1. **Count the slots.** Use the brief's cadence per platform. If there's no cadence, default to LinkedIn 2, X 5, Facebook 3 per week.
2. **Gather material:**
   - content published or refreshed in the last 30 days (content inventory) that hasn't been fully promoted
   - repurpose sets already planned for this period (`marketing/content/social/`)
   - launches, events and campaigns the user mentioned
   - relevant dates (industry events, seasonal moments, holidays in the audience's region) — only ones that genuinely fit the brand
3. **Balance the pillars.** Spread posts across the brief's content pillars so no pillar takes more than about 40% of the week. Keep promotional posts (product, offers) to about one in four.
4. **Assign each slot:** day, platform, pillar, format, angle, source (if any). Don't put the same message on all three platforms on the same day — stagger and adapt.
5. **Draft every post** with the `social-post` workflow and platform guides (`${CLAUDE_PLUGIN_ROOT}/skills/social-post/platforms/`).
6. **Visuals:** write one brief `to: design-agent` covering every graphic the week needs (post, platform, size, on-image text), so the set is consistent. Write `video-brief` requests for any video slots.
7. **Self-review:** cadence met; pillars balanced; no two posts in a row with the same hook style; all links and facts checked or marked `[VERIFY]`.

## Output

Save to `marketing/calendar/YYYY-Www.md`:

```
# Social calendar — week WW, YYYY (Mon DD Mon – Sun DD Mon)

## Overview
| Day | Platform | Pillar | Format | Angle | Source | Status |
|-----|----------|--------|--------|-------|--------|--------|

## Posts
### Mon — LinkedIn — <angle>
<post in the social-post output format>
...

## Notes
- Gaps or ideas that need the user's input (e.g., a photo from the team, a customer quote to approve)
- To verify before scheduling
```

Status starts as `draft`. Add one row to the content inventory (type `social`, title "Calendar week WW").
