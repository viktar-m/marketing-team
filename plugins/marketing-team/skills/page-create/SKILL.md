---
name: page-create
description: 'Create a new, focused web page that answers one specific search query or use case — answer-first copy, a short explanation, a comparison or steps where useful, an FAQ, related links, a CTA, metadata and structured data. Use for landing pages, use-case pages, "how to do X with our product" pages, comparison pages and glossary pages, or when a content brief has type page.'
---

# New page

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first. If you were given a content brief, it overrides the defaults below.

A page is not a short blog post. It answers **one** question, fast, for someone who searched exactly that — and shows how our product helps where it genuinely does.

## Inputs

The query or use case the page answers (required). Optional: target keyword, audience, competitor pages, a content brief. If the query isn't clear, infer it from the request and say what you assumed.

## Page structure

1. **H1** — the query, phrased the way the reader would say it, in the brief's heading case
2. **Direct answer** — 40–80 words that fully answer the question. If someone reads only this, they're served.
3. **How it works / steps** — the explanation the answer needs, nothing more. Use numbered steps for tasks.
4. **Comparison or options** (when the query implies a choice) — a table that compares fairly, including options that aren't ours
5. **Where our product fits** — one short section: what it does for this exact question, with a concrete example. Skip it if the product doesn't genuinely help.
6. **FAQ** — 3–5 real follow-up questions (from "people also ask" and related searches), each answered in 1–3 sentences
7. **Related links** — 3–5 internal pages that help next
8. **CTA** — from the brief, matched to the reader's intent

Target length: 500–1,000 words. Shorter is better if the question is fully answered.

## Workflow

1. **Research the query:** read the top-ranking pages, note what format wins (steps, table, definition) and what's missing. Collect follow-up questions.
2. **Confirm the product angle** from the brief and our own site — never claim a feature the brief doesn't list.
3. **Write** to the structure above in the brand voice.
4. **Add metadata:** SEO title (under ~60 characters), meta description (under ~155), slug, and the schema types to use (FAQPage, HowTo, Product or SoftwareApplication as fitting). Include the FAQ schema as JSON-LD.
5. **Suggest one graphic** that makes the answer clearer (diagram, comparison table image, annotated screenshot) with alt text.
6. **Self-review:**
   - [ ] Someone who reads only the H1 and direct answer gets what they came for
   - [ ] One question per page; tangents moved to related links
   - [ ] Fair to alternatives; product claims come from the brief
   - [ ] Voice, terminology and heading case match the brief
   - [ ] No invented facts; unverified items marked `[VERIFY]`

## Output

Save to `marketing/content/pages/YYYY-MM-DD-<slug>/page.md`:
- **Part 1 — Page copy:** front matter (title, meta_description, slug, primary_keyword), then the page exactly as it should be published
- **Part 2 — Publishing notes:** target query and intent, internal links, graphic brief, JSON-LD, items to verify

Then add a row to the content inventory and, if you worked from a brief, close it.
