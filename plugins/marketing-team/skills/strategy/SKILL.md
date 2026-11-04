---
name: strategy
description: 'Create or update the marketing strategy and channel strategies - content, SEO and AI visibility, social, paid, email - as rule files every agent on the team follows (goals, audiences, priorities, targets, do and don''t rules). Use for "build our marketing / content / SEO / social / paid / email strategy", quarterly planning, or when results show the current strategy isn''t working.'
---

# Strategy

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, existing `marketing/strategy/` files, recent reports (SEO, AI visibility, ads, performance) and the content inventory.

Follow `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` and `${CLAUDE_PLUGIN_ROOT}/templates/analysis-standards.md`: every priority and rule must be specific to this company and backed by evidence or labelled as a hypothesis.

Strategy here is not a slide deck. It's a short set of decisions written so that other agents can follow them and a human can check them. Every rule should be specific enough that you could tell whether a piece of work follows it.

## Which file

| File | Covers |
|------|--------|
| `marketing-strategy.md` | Business goal for marketing, target segments in priority order, positioning summary, the role of each channel, quarterly objectives and KPIs, budget split, what we're NOT doing |
| `seo.md` | Priority topic clusters, target keywords by cluster, page types to build, AI visibility goals and priority questions, refresh cadence, linking rules |
| `content.md` | Content pillars, formats and cadence, editorial standards beyond the brand voice, funnel coverage, repurposing rules |
| `social.md` | Role and goal per platform, cadence, pillar mix, formats, engagement rules, what we never post |
| `paid.md` | Objectives, platforms and budget split, target CPA / ROAS, audiences, testing plan, guardrails (max daily spend changes, brand-safety exclusions) |
| `email.md` | Lists and segments, programs (newsletter, nurture, onboarding), cadence, goals |

Write `marketing-strategy.md` first if it doesn't exist; channel files depend on it.

## Workflow

1. **Situation.** Summarise what the evidence says: what's working, what isn't, where competitors are strong, where the audience is. Use numbers from reports where they exist; mark estimates.
2. **Choices.** Decide priorities explicitly — which audiences, topics, channels and formats get effort, and which don't. A strategy that says yes to everything isn't one.
3. **Targets.** Set 3–5 measurable objectives per file with a baseline and a date (e.g., "AI share of voice on category questions from 20% to 35% by 31 March"). If there's no baseline, make measuring it the first action.
4. **Rules.** Write the rules agents must follow as short imperative statements under a `## Rules` heading (e.g., "Every blog article targets a keyword from a priority cluster", "No more than 1 in 4 social posts is promotional", "Pause any ad set with CPA above 2× target after 1,000 impressions"). Keep it under 15 rules per file.
5. **Plan.** List the next 30/60/90-day actions, each mapped to an agent. Turn the next 30 days into briefs (at most 5) with `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`.
6. **Review date.** End each file with `Next review: YYYY-MM-DD` (usually quarterly).

## File format

```
# <Channel> strategy
Updated YYYY-MM-DD · Owner: strategist · Next review: YYYY-MM-DD

## Situation
## Goals and targets
| Objective | Metric | Baseline | Target | By |
## Priorities
## Rules
## What we're not doing
## 30 / 60 / 90 days
## Changes since last version
```

When updating, keep the history short: replace the content and note what changed and why under "Changes since last version".

## Output

The strategy file(s), the briefs created, and a summary for the user: the 3 most important decisions, the targets, and anything you need them to confirm (budget, priorities between product lines).
