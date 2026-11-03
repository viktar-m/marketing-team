---
name: brand-setup
description: 'Create or update the brand brief that every marketing agent reads (marketing/brand-brief.md) — product, audience, positioning, voice, SEO targets, social platforms, CTAs and red lines. Use when setting up the marketing team for a new company or product, when no brand brief exists, or when the user wants to change their brand facts or voice.'
---

# Brand setup

The brand brief is what makes the team know the product. A thin brief produces generic content, so this skill aims for a brief that is specific, factual and short enough to read every time.

## Inputs

Any mix of: the company website URL, existing brand or style guides, sample content the user likes, pitch decks, answers from the user.

## Workflow

1. **Collect what exists.** If there's a website, fetch the home, product/features, pricing and about pages, and two or three recent blog posts. Read any files the user attached.
2. **Draft the brief** in `marketing/brand-brief.md` using `${CLAUDE_PLUGIN_ROOT}/templates/brand-brief-template.md`. Fill every section you can from the sources. For an example of a finished brief, see `${CLAUDE_PLUGIN_ROOT}/templates/sample-brand-brief.md`.
3. **Infer voice from evidence.** Derive the voice section from the user's own published writing: quote one real sentence that sounds right as the "we sound like" example.
4. **Mark gaps.** Anything you couldn't find gets `TODO:` with a short question. Don't invent positioning, audiences, statistics or competitors.
5. **Ask once.** Put the open TODOs to the user as one short list of questions (at most 8), most important first. Positioning, audience and voice matter most; social cadence and hashtags matter least.
6. **Finalise.** Fold the answers in, remove resolved TODOs, and save. Create `marketing/content-inventory.md` with its header if it doesn't exist (see conventions).
7. **Recommend next steps** to the user, in this order: the strategist's `strategy` (marketing strategy first), the design agent's `brand-kit`, and `ai-visibility` setup using section 10 of the brief.

## Updating an existing brief

Change only the sections the user mentions, keep everything else, and add a line at the bottom: `Updated YYYY-MM-DD: <what changed>`.

## Done when

- Sections 1–4 of the template have no TODOs left.
- Product claims in the brief can be traced to the user's site or the user's answers.
- The user has seen a short summary of the brief: one-line positioning, audiences, voice in three words, and the remaining TODOs.
