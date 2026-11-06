---
name: keyword-research
description: 'Research and prioritise keywords and search questions for a topic, product or page — search intent, estimated demand and difficulty, competitor rankings, and clustering into topics — and map each cluster to a page or article to create or update. Use for "what keywords should we target", planning content around a topic, choosing the primary keyword for a new piece, or following up a content gap analysis.'
---

# Keyword research

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first.

Research follows `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` (primary, current sources; dated facts).

## Inputs

A seed: a topic, product feature, competitor, URL or list of gaps from `content-gap`. If none is given, use the priority topics in the brief.

## Workflow

1. **Expand the seed.** Build a long list (30–80 candidates) from:
   - connected SEO tools (Ahrefs, Semrush, Search Console queries we already appear for)
   - web search: autocomplete-style variations, "people also ask" questions, related searches
   - the language the audience uses (brief: pains, objections, communities) — buyers rarely search in our product's terminology
   - competitors' page titles and headings for the topic
2. **Classify intent** for each: informational, commercial (comparing options), transactional (ready to act), navigational (looking for a brand).
3. **Estimate demand and difficulty.** Use tool data when connected. Otherwise rate demand and difficulty as high / medium / low from evidence (strength of the ranking sites, how many results directly answer the query) and label them as estimates.
4. **Check relevance to the business.** Score 1–3: does someone searching this plausibly need what we sell? Drop anything scoring 1 unless it supports a priority topic.
5. **Cluster.** Group keywords one page could rank for together (same intent, overlapping results). Name each cluster by its primary keyword.
6. **Map clusters to pages.** For each cluster: does an existing page cover it (check `marketing/index.md` and the site)? → refresh brief. No page? → new page or blog brief. Choose blog for broad informational clusters, page for specific questions and product use cases.

## Prioritise

Rank clusters by business relevance first, then demand, then ease. A small, high-intent cluster usually beats a large, vague one.

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

1. **Report** at `marketing/research/keywords-<topic>.md`:
   - Summary: seed, data sources, top 5 clusters and the recommended action for each
   - Cluster table: cluster | primary keyword | secondary keywords | intent | demand | difficulty | relevance | existing page | action
   - Full keyword list as an appendix
2. **Proposed actions** — offer to queue them as briefs `to: web-content-agent` (only after the user agrees) for the top clusters (at most 5), using `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`.
3. If any recommended primary keywords belong in the brand brief's target keywords, suggest adding them.
