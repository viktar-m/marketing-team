---
name: sales-enablement
description: 'Create sales enablement materials - competitive battlecards, product one-pagers, pitch narratives and talk tracks, objection-handling guides, discovery questions, demo scripts, sales email and LinkedIn outreach templates, release briefings for sales and support, and FAQ sheets. Use for "make a battlecard against X", "one-pager for sales", "help sales sell the new feature", or enablement for a launch.'
---

# Sales enablement

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief (positioning, audiences, competitors, sales motion), launch messaging if this supports a launch, and existing materials in `marketing/sales/`.

Sales materials are used live — on a call, in a follow-up email, five minutes before a demo. Make them short, scannable and honest.

Research follows `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` (primary, current sources; dated facts).

## Formats

**Battlecard** (one page per competitor)
- Who they are and who they win with; their pitch in one line
- Where we win (with proof) · where they win (honestly) · how to reposition
- Landmines: questions to ask that expose their weaknesses fairly
- Objections they cause and our answers
- Pricing comparison (sourced and dated) · recent news
- Research the competitor's site, pricing, reviews and docs; date every fact and link the source.

**One-pager** — headline, the problem, how we solve it (3 benefits, each with a proof point), who it's for, key features, social proof (only approved), CTA. Fits one A4/Letter page.

**Pitch narrative / talk track** — the story in 5–7 beats (the shift in the world, the problem, the stakes, the new way, how we deliver it, proof, next step), with suggested phrasing and the slide or demo moment for each beat.

**Objection handling** — table: objection · what's really behind it · response · proof · follow-up question. Cover price, timing, competitor, "we built it ourselves", security, switching cost.

**Discovery questions** — grouped by stage (situation, pain, impact, decision process), 15–25 total.

**Demo script** — the 3 "wow" moments for the audience, click path, what to say, time per section, demo data needed.

**Email and outreach templates** — first touch, follow-up, post-demo, re-engagement; each under 120 words, with personalisation slots `{first_name}`, `{company}`, `{trigger}`.

**Release briefing** (for launches) — what's new, who cares and why, how to demo it, what to say to existing customers, FAQ, what not to promise, availability and pricing.

## Workflow

1. Confirm the audience (sales reps, SDRs, partners, support) and the buyer the material targets.
2. Gather facts from the brief, launch messaging, product docs and competitor research. Mark anything unconfirmed `[VERIFY]`.
3. Write in plain language a rep can say out loud. Front-load: the first screen of every document should be useful on its own.
4. For documents that will be printed or shared externally (one-pagers), also produce a designed version: write a brief `to: design-agent`, or produce a PDF if asked.
5. Check with the strategist's `brand-review` for anything customer-facing.

## Output

`marketing/sales/<type>/<slug>.md` (e.g., `marketing/sales/battlecards/competitor-a.md`), an index `marketing/sales/README.md` listing every material with its date and owner, and a summary for the user. Battlecards get a "Last verified: YYYY-MM-DD" line; suggest a quarterly refresh.
