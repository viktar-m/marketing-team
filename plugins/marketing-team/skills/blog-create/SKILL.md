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
   - Check the content inventory and the site for our own related pages to link to.
3. **Outline:** a working title, an intro that answers the question fast, 4–8 H2 sections in a logical order, H3s only where a section needs them, and a conclusion with the CTA.
4. **Draft** in the brand voice:
   - The first 100 words say what the reader will get and give the short answer.
   - Every section earns its place: a concrete example, step, comparison or number in each.
   - Mention the product only where it genuinely helps the reader do the thing the article is about — usually once or twice, plus the CTA.
   - Short paragraphs (1–4 sentences); lists and tables where they make scanning easier.
   - Sentence-level clarity: active voice, specific verbs, no filler openings ("In today's fast-paced world…").
5. **Optimise:** primary keyword in the title, H1, intro and at least one H2, naturally. Cover secondary keywords and related questions. Add 3–5 internal links with descriptive anchors and 2–5 external links to credible sources.
6. **Self-review** with the checklist below. Fix, don't just note.

## Checklist

- [ ] The title promises something specific, and the article delivers it
- [ ] The question is answered in the first 100–150 words
- [ ] Voice, terminology, spelling and heading case match the brand brief
- [ ] No invented facts, stats, quotes or customer names; every external fact is linked; unverified items are `[VERIFY]`
- [ ] No hype words or phrases the brief bans
- [ ] Competitors and alternatives are described fairly
- [ ] Each section has something concrete; nothing could be cut without loss
- [ ] Internal and external links work and use descriptive anchor text
- [ ] The CTA matches the brief and fits the reader's stage

## Output

Save to `marketing/content/blog/YYYY-MM-DD-<slug>/article.md`:

```
---
title: <SEO title, under ~60 characters>
meta_description: <under ~155 characters>
slug: <url-slug>
primary_keyword: <keyword>
secondary_keywords: [<...>]
word_count: <n>
---

# <H1>

<article body>

---

## Publishing notes
- **Audience and angle:** <one line each>
- **Internal links used:** <list>
- **Suggested images:** <2–4 ideas with alt text; a cover image description>
- **Schema:** Article (+ FAQ if the article has a FAQ section)
- **Social cut-downs:** offer `social-repurpose`
- **To verify before publishing:** <list, or "nothing">
```

Then add a row to the content inventory and, if you worked from a brief, close it.
