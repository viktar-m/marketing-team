---
name: campaign-plan
description: 'Plan a marketing campaign or promotion end to end - objective, audience, offer, core message and creative concept, channel mix, timeline, budget, KPIs - and split it into briefs for the web, social, design, ads and GTM agents. Use for promos and discounts, seasonal campaigns (Black Friday, back to school, year end), webinars and events, lead-generation pushes, or a campaign around a product launch.'
---

# Campaign and promo plan

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, `marketing/strategy/marketing-strategy.md` and the channel strategies, and past campaigns in `marketing/campaigns/` (what worked before).

Research follows `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` (primary, current sources; dated facts).

## Inputs

What the campaign is for, rough dates, and budget if any. For product launches, read the launch kit in `marketing/launches/<name>/` — the gtm-agent owns launch messaging; the campaign builds on it.

## Workflow

1. **Objective and KPI.** One primary objective (e.g., 300 trial sign-ups, $50k promo revenue, 400 webinar registrations), its KPI, and the guardrail metric (e.g., discount cost, CPA).
2. **Audience.** Which segment from the brief, at what stage; existing customers vs new.
3. **Offer** (promos). What exactly, for whom, from when to when, terms and exclusions. Check it against the brief's red lines and pricing. Flag anything that needs approval (legal, finance).
4. **Big idea.** One core message (one sentence) and a creative concept that every channel expresses: a theme line, visual direction, tone. Offer 2–3 concepts with a recommendation if the user hasn't set one.
5. **Channel plan.** For each channel the strategy uses — website (landing page, banner), blog, email, social (LinkedIn / X / Facebook), video, paid (Google / LinkedIn / Meta), sales, partners — what it does in the campaign, the assets needed, and the owner agent.
6. **Timeline.** Phases: prepare → tease → launch → sustain → last chance → wrap. Dates for each asset being ready and going live. Work back from launch day; leave time for review.
7. **Budget.** Split by channel when there's paid spend; keep a test reserve.
8. **Measurement.** Tracking (UTM convention: `utm_campaign=<slug>`), what to report and when, and the decision points (e.g., "day 3: shift budget to the best ad set").
9. **Briefs, after approval.** Once the user approves the plan: one brief per deliverable using `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`, with `campaign: <slug>` and a `due:` date — to web-content-agent, social-agent, design-agent (one brief for the whole visual set, so it stays consistent), ads-agent, gtm-agent. Highest priority first; no 5-brief limit for campaigns, but group small items.

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

- `marketing/campaigns/<name>/plan.md`: summary box (objective, dates, offer, core message, budget), concept, channel plan table (channel · role · assets · owner · due), timeline, measurement, risks and approvals
- `marketing/campaigns/<name>/timeline.html`: a visual timeline (Gantt-style, one row per asset, coloured by owner agent) following `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`
- The briefs, and a summary for the user with the decisions they need to make
