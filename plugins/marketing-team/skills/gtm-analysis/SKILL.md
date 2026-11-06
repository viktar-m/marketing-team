---
name: gtm-analysis
description: 'Deep product, market and go-to-market analysis at senior-advisor level - what the product is in plain words, why it exists, the business model, competitive landscape from current primary sources, positioning assessment, answers to the founder''s strategic questions (pricing, free tier, first segment, competing with incumbents, partner economics, proof before launch, launch sequencing, hiring, metrics) with recommendations, reasoning, math and tests, and immediate priorities. Use for "analyse this product / its competitors / its positioning", "who needs it and why", "suggest GTM motions", GTM strategy for a new product or client, or answering a founder''s strategic questions.'
---

# GTM analysis

This is the team's flagship strategic deliverable. It must read like the work of a senior product marketer who studied this company for days. Read these three files first and follow them exactly:

- `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` — how to research (primary, current, complete)
- `${CLAUDE_PLUGIN_ROOT}/templates/analysis-standards.md` — how to think and write (decisions, math, no generic advice)

Then read the brand brief and any strategy files. Research handed to you by the team lead is a starting point: verify anything decision-critical yourself.

## Step 1 — Get the questions

- If the user or founder gave questions, copy them **verbatim** into your working notes; the analysis must answer each one, in order, with its number.
- If not, derive 6–10 decisions this company actually faces from its site and situation (pricing and free-tier limit, first segment, how to win against incumbents, partner/referral economics, minimum proof before launch, launch sequencing, team and capacity, metrics). State at the top that you derived them, so the user can replace them.

## Step 2 — Research (research standards, all of it)

At minimum:
1. Every relevant page of the product's site, with all numbers captured (prices per tier, limits, minimums, trial, discounts, referral %, SLAs, Enterprise terms).
2. Each serious alternative's own pricing page and marketplace listing, dated — including native/"do nothing", build-it-yourself, spreadsheet workflows, free/open-source options and the platform vendor's own moves.
3. A sweep for entrants and changes in the last 12 months.
4. Platform rules that affect GTM (marketplace listing and security review, revenue share, accessibility/procurement requirements in target sectors).
5. Save notes with sources to `marketing/research/<product>-research-notes.md`.

## Step 3 — Calculate

Before writing, compute with the client's real numbers (show the math in the report):
- first-year revenue for one realistic customer (e.g., 20 and 50 seats) at each tier
- that revenue after partner reward and marketplace revenue share (state the share as an assumption if the exact rate isn't public)
- the free-to-paid jump for a realistic org (e.g., 100 users all needing licenses)
- price per seat versus each main competitor, including their minimum seats

## Step 4 — Write the report

Save to `marketing/launches/<name>/gtm-analysis.md` (or `marketing/research/gtm-analysis-<name>.md` if no launch folder fits), with the header from the conventions (§3, type `research`, `needs_you` = the founder decisions that need an answer), following the structure in the analysis standards:

1. **What it is, in simple words** — plain explanation + a concrete scenario; the 4–6 capabilities that matter, in user language
2. **Why it exists** — the underlying problems
3. **The business model** — tiers and terms, with your note on what each tier is really for
4. **My overall interpretation** — the core bet and the defining challenge
5. **Assessment** — positioning strengths, what to change in the message hierarchy (lead with / differentiate with / build confidence with), competitive table with prices (sourced, dated) and an "implication" column, the most important competitive findings in prose, and website/launch-readiness caveats
6. **Answers to the strategic questions** — each: Recommendation → reasoning (prose) → trade-offs → how to test; with tables where they genuinely help (segment priorities, partner reward tiers, proof targets, launch phases, metrics with why)
7. **What I'd prioritize immediately** — 3–5 numbered priorities
8. **The most important strategic takeaway** — and a recommended positioning line with a one-paragraph supporting statement
9. **Sources** and **To verify**

## Step 5 — Self-review

Run the self-review checklist in the analysis standards. In particular, delete or rewrite anything that fails the generic-advice test, and confirm every competitor price came from a primary source checked during this task.

## Step 6 — Hand-offs (only if asked or in a real workspace)

Messaging (`messaging.md` via `launch-plan` conventions), briefs for web pages, comparison content and partner materials. In a test run, skip briefs.

## If you can't write files

If the session blocks writing files, return the complete report in your final message, clearly delimited, so the team lead can save it. Don't shorten it.
