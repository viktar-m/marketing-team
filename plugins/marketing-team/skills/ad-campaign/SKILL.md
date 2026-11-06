---
name: ad-campaign
description: 'Plan a paid campaign on Google Ads, LinkedIn Ads or Meta Ads - objective, conversion tracking, account structure (campaigns, ad groups or ad sets), keywords or audiences, budget and bidding, creative needs, landing page, testing plan and launch checklist. Use for "plan a campaign for X", new paid launches, promo or webinar ads, or restructuring an existing account.'
---

# Ad campaign plan

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief (section 9), `marketing/strategy/paid.md`, the campaign plan or launch kit behind this (if any), and past reports in `marketing/ads/`.

## Workflow

1. **Objective and conversion.** One conversion action that matches the business goal (purchase, trial, demo request, lead form, registration) and the value of a conversion if known. Confirm tracking exists (pixel / tag, conversion events, UTMs `utm_source=<platform>&utm_medium=paid&utm_campaign=<slug>`). If it doesn't, setting it up is step one of the launch checklist.
2. **Platform choice.** Where the audience is and what intent exists:
   - **Google Search:** people already searching for the problem or category — highest intent
   - **LinkedIn:** B2B targeting by job title, function, seniority, company size, industry — higher cost per click, precise
   - **Meta (Facebook/Instagram):** consumer and broad B2B reach, strong for visual offers and retargeting
   Recommend a split and say why.
3. **Structure.**
   - Google Search: campaigns by goal or product line; ad groups by tight keyword theme (5–20 keywords each, phrase and exact match to start); negative keyword list from day one (jobs, free, competitors' support terms, irrelevant meanings); brand campaign separate from non-brand
   - LinkedIn: campaign per audience × objective; audience size roughly 50k–500k [check current guidance]; exclude current customers and competitors' employees where relevant
   - Meta: prospecting vs retargeting campaigns; broad or interest audiences plus lookalikes from customer lists; let placements auto-optimise unless creative is placement-specific
4. **Budget and bidding.** Daily budgets per campaign that can buy enough conversions to learn (rule of thumb: daily budget ≥ target CPA where possible); start with the platform's conversion-based bidding once tracking works, manual or click-based only for very small budgets. State the expected cost range as an estimate.
5. **Landing page.** Message match: the page repeats the ad's promise in its headline, has one CTA, loads fast. If the page doesn't match, suggest it as a next step for the web-content-agent (queue a brief only if the user says yes).
6. **Creative needs.** List every ad and format needed, then run `marketing-team:ad-creative` for copy and describe all visuals (each size, the copy on each).
7. **Testing plan.** One variable at a time per test (offer, angle, creative format, audience); minimum run time and volume before judging; what "winner" means.
8. **Launch checklist.** Tracking verified with a test conversion, UTMs, negatives, exclusions, budgets and end dates, ad approvals, landing page live, reporting dashboard ready.

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

`marketing/ads/<name>-plan.md`: summary (objective, platforms, budget, dates, target CPA), structure table (campaign · ad group/set · targeting · budget · bidding), keyword lists or audience definitions, landing pages, creative list, test plan, launch checklist, and a visual budget-split chart (`plan.html`, per `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`). The user builds or approves the campaign in the ad platform; never launch or change live campaigns yourself.
