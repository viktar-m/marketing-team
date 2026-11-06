---
name: content-gap
description: 'Compare our content with competitors'' to find topics, questions and page types they cover that we don''t, pages where they outrank us, and our own thin or outdated coverage — then prioritise the gaps and turn the best into content briefs. Use for "where are competitors beating us", "what are we missing", monthly gap reviews, or planning a content roadmap.'
---

# Content gap analysis

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first.

Research follows `${CLAUDE_PLUGIN_ROOT}/templates/research-standards.md` (primary, current sources; dated facts).

## Inputs

Competitors from the brief (or ones the user names), and the topic area to compare (default: the brief's priority topics). Keep it to 2–4 competitors per run.

## Workflow

1. **Map our coverage.** List our pages on the topic area from the sitemap, the blog index and `marketing/index.md`: title, URL, primary topic, date.
2. **Map each competitor's coverage.** From their sitemap, blog and resource sections, and web searches for the brief's target keywords: what topics, questions and page types (guides, comparisons, templates, tools, glossaries, use-case pages) do they have?
3. **Find four kinds of gap:**
   - **Missing:** a topic they cover and we don't
   - **Outranked:** we cover it, but they rank above us — note why (depth, freshness, format, links)
   - **Thin or stale:** our page exists but is short, outdated or doesn't answer the query
   - **Format:** they win with a format we don't use (comparison table, template, calculator, video)
4. **Filter by fit.** Drop gaps that don't serve our audience or that conflict with the brief's positioning or red lines. Copying a competitor's topic list is not a strategy.
5. **Prioritise.** Score each gap on business relevance, search demand (estimate unless a tool is connected) and effort. Note quick wins: stale or thin pages are often cheaper to fix than new pages are to create.

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

1. **Dashboard** `marketing/dashboards/content-gap.html` per `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`: coverage by topic, us vs each competitor, gaps sized by relevance and demand.
2. **Report** at `marketing/research/content-gap-<month>.md`:
   - Summary: competitors compared, data sources, top 5 gaps and the action for each
   - Gap table: gap | type (missing / outranked / thin / format) | competitor example URL | our page (if any) | relevance | demand | effort | action
   - Topics where we're ahead — worth protecting
3. Run `keyword-research` on the top gaps when primary keywords aren't obvious.
4. **Proposed actions** — offer to queue them as briefs `to: web-content-agent` (only after the user agrees) for the top gaps (at most 5), using `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`. Refresh briefs for thin or stale pages; new-page or blog briefs for missing topics.
