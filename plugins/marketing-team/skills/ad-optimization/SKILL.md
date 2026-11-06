---
name: ad-optimization
description: 'Analyse paid ad performance on Google Ads, LinkedIn Ads and Meta Ads and recommend optimisations - spend efficiency, CPA and ROAS by campaign, ad group, keyword, search term, audience and creative; wasted spend and negative keywords; creative fatigue; budget reallocation; landing page issues - with a visual dashboard and a prioritised change list. Use for weekly or monthly ad reviews, "why is CPA up", or before changing budgets.'
---

# Ad optimisation

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, `marketing/strategy/paid.md` (targets and guardrails), the campaign plans, and previous reports in `marketing/ads/`.

## Data

- Use connected ad-platform or analytics tools if available; otherwise ask the user for exports (CSV) for the period and the previous period: campaign, ad group/ad set, ad, keyword and search-term reports for Google; campaign and creative reports for LinkedIn and Meta; conversions from analytics or CRM if the platforms' numbers are doubtful.
- Load the data with Python (pandas if available) and compute metrics in code — never estimate numbers in prose.
- Default period: last 30 days vs the 30 days before. Note attribution windows and tracking changes that could distort the comparison.

## Analysis

1. **Overview:** spend, impressions, clicks, CTR, CPC, conversions, conversion rate, CPA, conversion value and ROAS — per platform and in total, vs previous period and vs targets in the strategy.
2. **Where money works and where it doesn't:** rank campaigns and ad groups/ad sets by CPA (or ROAS); spend with zero or few conversions above a threshold (e.g., 2× target CPA spent, no conversion).
3. **Google search terms:** irrelevant terms to add as negatives (exact or phrase, at the right level); converting terms not yet keywords to add; match-type issues.
4. **Creatives:** winners and losers by CTR and conversion rate with enough volume to judge; fatigue (rising frequency with falling CTR on Meta/LinkedIn, typically after a few weeks); which angles win.
5. **Audiences and placements:** segments, placements, devices, locations or times that clearly over- or under-perform.
6. **Funnel:** if CTR is fine but conversion rate is poor, check the landing page (message match, speed, form length) and suggest it as a next step for the web-content-agent (queue a brief only if the user says yes) if needed.
7. **Budget:** where to move money, within the strategy's guardrails (e.g., no more than ±20% budget change per campaign per week, to avoid resetting learning).

## Recommendations

A prioritised change list, each with: what to change, where, why (the number behind it), expected impact, and risk. Group into **do now**, **test next**, **watch**. New creatives go to `marketing-team:ad-creative` and the design agent via briefs.

**Never apply changes in the ad platforms yourself.** The user applies them, or explicitly asks you to make a specific change.

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

- `marketing/ads/ads-review-<month>.md`: summary (3–5 bullet findings), KPI table vs previous period and target, the change list, briefs created, data caveats
- `marketing/dashboards/ads.html`: KPI tiles with deltas, spend vs conversions by campaign, CPA trend, top and bottom creatives, wasted spend — per `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`
- Negative keyword lists and other bulk changes as CSV files ready to upload, in `marketing/ads/<name>.csv`
