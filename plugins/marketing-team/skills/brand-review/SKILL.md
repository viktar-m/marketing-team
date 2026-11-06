---
name: brand-review
description: 'Review any marketing deliverable before it ships - article, page, refresh, social posts, ad copy, graphics, sales material, launch kit - against the brand brief, the strategy rules, factual accuracy, channel best practice and legal red lines, with a pass / fix verdict and exact fixes. Use for "review this", "check this before we publish", "is this on brand", or as the final quality gate on campaign and launch work.'
---

# Brand review

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, the strategy files that apply to the deliverable's channel, the brand kit (for visuals), and the brief the deliverable was made from (if any).

The goal is a decision, not a lecture: can this ship, and if not, exactly what changes?

## Checks

**Brief fit** — does it do what its brief asked: goal, audience, keywords, CTA, deliverables?

**Strategy rules** — check every rule in the relevant strategy file that applies. Quote the rule when something breaks it.

**Brand voice** — voice, terminology, product-name spelling, heading case, US/UK spelling, banned words. Compare with the brief's "we sound like / we never sound like".

**Facts and claims** — every product claim traceable to the brief or our own pages; every external fact sourced; no invented stats, quotes, customers or awards; `[VERIFY]` items still open; no claims the brief's red lines forbid; competitor statements fair and accurate; offers and prices match the campaign plan.

**Channel quality**
- Web: answers the query early, internal linking done (links out + links in), metadata lengths, schema
- Social: hook before the cut-off, one point, one CTA, length limits, hashtags per strategy
- Ads: character limits, policy-risky wording (superlatives, personal attributes, unverifiable claims), message match with the landing page
- Visuals: brand kit colours and fonts, legibility on mobile, contrast, text amount, correct sizes, no fake screenshots or logos
- Sales material: scannable in a live call, honest about competitors, current pricing and features

**Depth (strategic and long-form work)** — passes the generic-advice test in `${CLAUDE_PLUGIN_ROOT}/templates/analysis-standards.md`; decisions have a recommendation, reasoning and trade-offs; competitor facts are primary and dated. Generic advice is a **major** issue.

**Accessibility and inclusion** — alt text, readable contrast, plain language, inclusive wording.

## Verdict

- **Ship** — no changes needed
- **Ship with fixes** — small fixes you list exactly (current → corrected)
- **Revise** — problems that need the author: send back as a brief to the agent that made it, listing the issues

For "ship with fixes", apply the fixes yourself when the deliverable is a text file in the workspace, and say so; otherwise list them.

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

`marketing/research/review-<name>.md`:

```
Verdict: Ship | Ship with fixes | Revise
Deliverable: <path>  ·  Brief: <path>

| # | Severity | Check | Issue | Fix |
|---|----------|-------|-------|-----|
```

Severity: **blocker** (false or risky claim, legal/red-line breach, wrong price or date), **major** (off-brand, misses the brief, broken links), **minor** (polish). Anything with a blocker can't be "Ship".
