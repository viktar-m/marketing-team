---
name: internal-linking
description: 'Plan internal links for a new or updated web page - which existing pages it should link to (with anchor text and placement), and which existing pages should be updated to link to it (with the exact sentence to edit) - based on a site index and site search. Also builds and refreshes the site index. Use inside every blog article, page creation and page refresh, or on its own for "what should link to this page" and "fix our internal linking".'
---

# Internal linking

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief (website and key pages).

Internal links help readers find the next useful page, help search engines understand which pages matter, and spread authority to new pages. Every new or refreshed page gets links **out** and links **in**.

## Step 1 — Make sure the site index is current

The index lives at `marketing/site/site-index.md`:

```
Indexed: YYYY-MM-DD · Source: <sitemap URL>
| URL | Title | Type | Main topic / keyword | Notes |
|-----|-------|------|----------------------|-------|
```

- If it's missing or older than 30 days, build it: fetch the sitemap (try `/sitemap.xml`, `/sitemap_index.xml`, or the `Sitemap:` line in `/robots.txt`). Record every URL with its type (product, pricing, blog, docs, landing, comparison, other). Fetch titles and topics for the pages that matter most: commercial pages from the brief, and pages in the same section and topic as the current task. For large sites (500+ URLs), index all URLs but only fetch details for the relevant sections.
- Add pages the team produced since the last index from the content inventory.
- Use connected tools when available (Search Console's top pages, an SEO tool's site crawl) to mark the pages with the most traffic or links — they're the strongest pages to link **from**.

## Step 2 — Links out (inside the new or updated piece)

- Choose 3–8 internal links for a typical article or page (fewer for short pages). Each must help the reader at that exact point: a definition, the next step, a deeper guide, the product feature that solves the problem being discussed.
- Include at least one commercial page (product, feature, pricing) where it fits naturally, and at least one closely related article or guide.
- **Anchor text** describes the destination ("plan meals from your pantry"), never "click here" or a bare URL. Vary anchors; don't use the exact same anchor for two different pages.
- Don't link the same destination twice; don't link to redirected, broken or `noindex` pages.
- Write the links into the draft itself, in Markdown.

## Step 3 — Links in (existing pages that should link to this one)

1. Find candidates: pages in the index on the same or a parent topic, plus `site:<domain> <topic keywords>` web searches, plus pages that rank for related keywords (from SEO data, if connected).
2. Pick the 3–5 best: relevant to the topic, strong (traffic, links, commercial importance), and with a natural place to mention it. Prefer pages that already discuss the topic briefly — the link then completes a thought.
3. For each, fetch the page and find the exact sentence or paragraph where the link belongs. Propose the edit:
   - **Page:** URL
   - **Current text:** the sentence as it is
   - **New text:** the sentence with the link added (or one new sentence, if no existing sentence fits)
   - **Anchor:** the linked words
   - **Why:** one line
4. When refreshing a page, also check its own inbound links: if important pages don't link to it, propose those edits the same way.

## Step 4 — Record

- Add a **Internal linking** section to the piece's publishing notes with the links out and the links-in edits.
- Append the links-in edits to `marketing/site/link-tasks.md` as checkbox items (`- [ ] <page> → <new page>: <anchor>`), so whoever publishes can work through them. Mark items done when the user confirms.
- If you find broken internal links or orphan pages along the way, list them in the publishing notes.

## Standalone audit

For "fix our internal linking": refresh the index, then report orphan pages (no internal links in), important pages with few links in, broken internal links, and over-optimised anchors — with a prioritised list of edits in the same format, saved to `marketing/reports/YYYY-MM-DD-internal-linking.md`.
