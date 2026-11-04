---
name: launch-plan
description: 'Plan a product launch or release end to end - launch tier, positioning and messaging, audiences, timeline back from launch day, channel plan, asset checklist with owners, internal and sales readiness, success metrics and post-launch review - and create briefs for every agent involved. Use for new products, major or minor feature releases, version releases, pricing changes and rebrands.'
---

# Launch plan

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, `marketing/strategy/marketing-strategy.md`, and previous launches in `marketing/launches/` (reuse what worked).

Research follows `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` (primary, current sources; dated facts).

## Inputs

What's launching, when, for whom, and the source of truth for features (release notes, specs, the product team). If feature details are thin, ask for them — launch content built on guesses is dangerous. Mark anything unconfirmed `[VERIFY]`.

If the product's market, competitors or positioning haven't been analysed yet, run `marketing-team:gtm-analysis` first — a launch plan built on unexamined positioning repeats its mistakes.

## Workflow

1. **Tier the launch.**
   - **Tier 1** — new product, major version, pricing change: full campaign, PR, paid, sales training, video
   - **Tier 2** — significant feature: blog, page, email, social, sales update, maybe paid
   - **Tier 3** — improvement or fix: release notes, social post, in-app note
   Tier decides effort; don't run a Tier 1 machine for a Tier 3 change.
2. **Messaging (approve before anything else).**
   - Positioning statement: for [audience] who [need], [product/feature] is [category] that [benefit], unlike [alternative]
   - Three key messages, each with proof (feature, data, demo moment)
   - Headline and subheadline options; a 25-word and a 100-word description; a boilerplate
   - What changes for existing customers; objections and answers; what we must not claim
   Save as `messaging.md` and ask the user to confirm it before channel work starts.
3. **Timeline** back from launch day (L):
   - L−4 to L−3 weeks: messaging approved, asset briefs out, tracking ready
   - L−2 weeks: drafts reviewed (strategist `brand-review`), sales and support enablement
   - L−1 week: everything final, scheduled, landing page staged
   - L: publish, post, send, ads live; monitor
   - L+1 to L+4 weeks: sustain content, retargeting, customer stories, review
   Compress for Tier 2–3.
4. **Asset checklist** — one row per asset: asset · channel · owner agent · due · status. Typical Tier 1 set: landing/feature page and page refreshes (web-content-agent); launch blog post (web-content-agent); release video and social set (social-agent); graphics set and ad creatives (design-agent); paid plan (ads-agent); campaign around the launch (strategist); sales one-pager, battlecard update, demo script, FAQ, customer email (you, via `sales-enablement`).
5. **Readiness.** Sales and support briefed, docs updated, pricing and availability confirmed, website updated (navigation, pricing page, comparison pages), analytics events in place.
6. **Success metrics.** 2–4 measurable goals (sign-ups, adoption of the feature, pipeline, traffic, AI visibility for the new feature's questions) and when to review them.
7. **Briefs.** One brief per asset with `campaign: <launch-slug>` and `due:` date. Messaging file path in every brief.

## Output

`marketing/launches/<slug>/`: `plan.md` (tier, summary, timeline, asset checklist, readiness, metrics), `messaging.md`, `timeline.html` (visual timeline per `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`, rows by asset, coloured by owner agent, launch day marked), and the briefs. After launch, add `review.md`: results vs metrics, what worked, what to change next time.
