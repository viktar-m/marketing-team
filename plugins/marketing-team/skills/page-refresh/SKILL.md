---
name: page-refresh
description: 'Refresh an existing web page from its URL or pasted copy — diagnose what''s weak, update outdated facts, improve structure, search and AI-answer visibility, internal links and conversion — and deliver the rewritten copy with a change log. Use for "refresh / update / improve / rewrite this page", pages losing rankings or traffic, or a content brief with type refresh.'
---

# Page refresh

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first. If you were given a content brief, it overrides the defaults below.

A refresh improves what exists; it isn't a rewrite for its own sake. Keep what works — especially sections and phrasing that already rank — and change what doesn't.

## Inputs

The page URL or pasted copy (required — ask if neither is provided). Optional: target keyword, known problems, performance data, a content brief.

## Workflow

1. **Understand the page.** Fetch it. Identify its job (sell, explain, support, compare), its audience, its primary query, and which conversion it should drive.
2. **Get evidence.** If an SEO tool or Search Console is connected, pull the page's queries, clicks, impressions and position. Otherwise, search the primary keyword and see where the page stands and what outranks it.
3. **Diagnose.** Note, with specifics:
   - outdated facts, versions, prices, years, screenshots, broken links
   - a slow start: the main question isn't answered near the top
   - gaps versus the top-ranking pages, and unanswered follow-up questions
   - structure: headings that don't describe their sections, walls of text, missing steps or tables
   - voice drift from the brand brief, banned words, hype
   - weak or missing CTA, proof and internal links
   - metadata: title and description length, intent match, missing structured data
4. **Decide the direction** in two or three sentences: what the refreshed page will do better. Pick the structure that fits its job:
   - **Product / feature page:** benefit-led opening → how it works → proof → use cases → objections / FAQ → CTA
   - **Tutorial / support page:** what you'll achieve → prerequisites → numbered steps → troubleshooting → next steps
   - **Comparison page:** short verdict → criteria → fair comparison table → when to choose each → CTA
   - **Informational page:** direct answer → explanation → examples → related questions → next step
5. **Rewrite.** Answer first. Keep strong existing sentences. Add the missing coverage. Improve headings so they could stand alone as answers in AI overviews. Add internal links (3–5) from the inventory and site.
6. **Metadata:** new title and meta description (only if better), structured data recommendation.
7. **Self-review:**
   - [ ] Every change has a reason in the change log
   - [ ] No content that was ranking well was removed without a reason
   - [ ] Facts are current and sourced; unverified items marked `[VERIFY]`
   - [ ] Voice and terminology match the brand brief
   - [ ] The page's main job (and its CTA) is clearer than before

## Output

Save to `marketing/content/refreshes/YYYY-MM-DD-<slug>/refresh.md` with these sections:
1. **Diagnosis** — the top problems found, with evidence
2. **Direction** — what the refresh changes and why
3. **Refreshed page copy** — publish-ready, with front matter (title, meta_description, url)
4. **Change log** — section by section: kept / changed / added / removed, and why
5. **SEO and AI visibility notes** — keyword coverage, headings, schema, internal links
6. **To verify** — claims, figures and screenshots a human must check
7. **Implementation notes** — redirects, image updates, anything for the person publishing

Then add a row to the content inventory with status `refreshed` and, if you worked from a brief, close it.
