---
name: blog-create
description: 'Write a complete, publish-ready blog article from a short input — a title, idea, keyword, content brief, or source material — including research, outline, draft in the brand voice, SEO metadata, internal links, image suggestions and an editorial self-review. Use for blog posts, guides, how-to articles, listicles and thought-leadership pieces.'
---

# Blog article

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first. If you were given a content brief, it overrides the defaults below.

## Inputs

Any of: title, idea, audience, primary keyword, target length, links or source material, a content brief. Infer what's missing and state your choices in the publishing notes. Don't stop to ask.

Defaults: audience = the brief's main segment; length = 1,200–1,800 words; CTA = the brief's primary CTA.

## Workflow

1. **Decide silently:** the reader, the one question the article answers, the primary keyword, the angle that makes this better than what already ranks, and the format (how-to, list, explainer, opinion, comparison).
2. **Research.**
   - Search the primary keyword and read the top 3–5 results. Note what they all cover (table stakes) and what they miss (your angle).
   - Gather facts from primary sources (official docs, original research, standards bodies) over aggregators. Keep the source URL for every fact.
   - Check `marketing/index.md` and the site for our own related pages to link to.
3. **Outline:** a working title, an intro that answers the question fast, 4–8 H2 sections in a logical order, H3s only where a section needs them, and a conclusion with the CTA.
4. **Draft** in the brand voice:
   - The first 100 words say what the reader will get and give the short answer.
   - Every section earns its place: a concrete example, step, comparison or number in each.
   - Mention the product only where it genuinely helps the reader do the thing the article is about — usually once or twice, plus the CTA.
   - Short paragraphs (1–4 sentences); lists and tables where they make scanning easier.
   - Sentence-level clarity: active voice, specific verbs, no filler openings ("In today's fast-paced world…").
5. **Optimise:** primary keyword in the title, H1, intro and at least one H2, naturally. Cover secondary keywords and related questions. Add 2–5 external links to credible sources.
6. **Internal linking:** Run `marketing-team:internal-linking` (Steps 1–4): write the links out into the draft, and list the existing pages that should link to this article, with the exact edits.
7. **Graphics:** describe the cover image and any diagrams the article needs (purpose, message, size, placement) in the notes, and offer to have the design agent make them (queue a brief only if the user says yes).
8. **Self-review** with the checklist below. Fix, don't just note.

## Checklist

- [ ] The title promises something specific, and the article delivers it
- [ ] The question is answered in the first 100–150 words
- [ ] Voice, terminology, spelling and heading case match the brand brief
- [ ] No invented facts, stats, quotes or customer names; every external fact is linked; unverified items are `[VERIFY]`
- [ ] No hype words or phrases the brief bans
- [ ] Competitors and alternatives are described fairly
- [ ] Each section has something concrete; nothing could be cut without loss
- [ ] Internal and external links work and use descriptive anchor text
- [ ] At least 3 existing pages are proposed to link to this article, with exact edits
- [ ] The CTA matches the brief and fits the reader's stage

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

Save to `marketing/web/<name>.md`:

```
---
title: <article title>
type: blog
agent: web-content-agent
status: draft
date: YYYY-MM-DD
summary: <one line>
needs_you:
  - <only real actions, e.g. "Check the [VERIFY] figure in section 3">
seo_title: <under ~60 characters>
meta_description: <under ~155 characters>
slug: <url-slug>
primary_keyword: <keyword>
secondary_keywords: [<...>]
word_count: <n>
---

# <H1>

<article body>

---

## Notes for you
- **Audience and angle:** <one line each>
- **Internal linking:** links out (anchor → URL) and links in (page, current text, new text, anchor)
- **Graphics:** design brief path; alt text for each image
- **Schema:** Article (+ FAQ if the article has a FAQ section)
- **Social cut-downs:** offer `social-repurpose`
- **To verify before publishing:** <list, or "nothing">
```

If you worked from a brief, close it. Rebuild the Hub and reply with the done message (conventions §5–6).
