---
name: seo-audit
description: 'Run an SEO audit of a website, a section of it, or a single page — technical basics, on-page optimisation, content quality, internal linking, and readability for search engines and AI answer engines — and produce a prioritised report plus content briefs for fixes. Use for "audit our site/blog/page", recurring weekly SEO checks, or diagnosing a traffic or ranking drop.'
---

# SEO audit

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first.

## Scope

- **Single page:** a URL the user gives.
- **Section:** e.g. `/blog/` — sample up to 15 pages, favouring the most important (commercial pages and top traffic pages, if data is available).
- **Site:** home page, the commercial pages in the brief, and a sample of up to 15 other pages.
- **Recurring weekly run:** the commercial pages in the brief, plus pages published or refreshed in the last 30 days (from the inventory). Compare with the previous audit in `marketing/reports/` and focus on what changed.

## Data

1. **Connected tools first.** If Search Console, Analytics, Ahrefs, Semrush or similar are connected, pull: clicks, impressions, average position and CTR per page and query over the last 28 days, compared with the previous 28 days.
2. **Public data otherwise.** Fetch each page and check `robots.txt` and the sitemap. Use web search to see which pages rank for the brief's target keywords.
3. State in the report which data sources you used.

## Checklist per page

**Technical basics**
- Page returns content (not an error or redirect chain); canonical tag is sensible
- Indexable: no accidental `noindex`; not blocked in robots.txt; listed in the sitemap
- Mobile-friendly layout and no obvious heavy elements slowing it down (flag, don't measure, unless a tool gives real numbers)

**On-page**
- Title: unique, under ~60 characters, primary keyword near the front, matches intent
- Meta description: unique, under ~155 characters, says what the reader gets
- One H1 that matches the topic; headings describe their sections and follow a logical order
- Primary keyword and close variants used naturally in title, H1, intro and some subheadings — no stuffing
- Images have descriptive alt text; URLs are short and readable
- Structured data where it fits (Article, FAQ, Product, HowTo, Organization)

**Content**
- Answers the main query in the first 100–150 words
- Covers what a searcher needs; compare with the top 3 ranking pages for the primary keyword
- Up to date: no stale years, versions, prices or screenshots
- Shows expertise: specifics, examples, sources; not generic filler
- Consistent with the brand brief's positioning and terminology

**Linking**
- Links to and from related pages on the site; descriptive anchor text
- Orphan pages (no internal links in) and broken links

**AI answer readiness**
- Clear question-style headings and short direct answers beneath them
- Facts stated plainly enough to be quoted; definitions where a term is introduced
- Entity clarity: the product, company and category are named explicitly

## Prioritise

Score each issue: **impact** (high / medium / low) × **effort** (low / medium / high). Order the action list by high impact + low effort first. Group site-wide issues (e.g., all titles too long) into one item.

## Output

1. **Report** at `marketing/reports/YYYY-MM-DD-seo-audit.md`:
   - Summary: scope, data sources, overall health in three sentences, top 5 actions
   - Changes since the last audit (recurring runs)
   - Findings table: page | issue | impact | effort | fix
   - Quick wins the user can do in minutes (titles, meta descriptions, alt text) written out in full, ready to paste
   - What couldn't be checked and why
2. **Dashboard** `marketing/dashboards/seo-audit.html` per `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`: health score tiles, issues by impact, clicks and position trends if data is connected, and the action list.
3. **Briefs** (`to: web-content-agent`) for fixes that need writing — a refresh, a new section, a new page — using `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`. At most 5 per run, highest priority first.
