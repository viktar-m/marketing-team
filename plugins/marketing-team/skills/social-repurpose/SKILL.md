---
name: social-repurpose
description: 'Turn a long piece — a blog article, web page, page refresh, report, webinar transcript, or product announcement — into a set of native social posts for LinkedIn, X and Facebook, with different angles spread over days or weeks. Use for "turn this into posts", "promote this article", "social cut-downs", or after a new article, page or release is published.'
---

# Social repurpose

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first.

One good article holds several posts. The goal is a small set of posts that each stand alone and each send the right reader back to the source.

## Inputs

The source (path, URL or pasted text) and the platforms (default: all active platforms in the brief). Optional: how many posts, over what period.

## Workflow

1. **Read the source** and extract 5–8 **post-worthy atoms**: a key takeaway, a surprising fact (with its source), a step-by-step, a common mistake, a quote-able line, a question it answers, a before/after, a mini case.
2. **Choose angles per platform** using the brief's goal for each and the `social-post` platform guides (`${CLAUDE_PLUGIN_ROOT}/skills/social-post/platforms/`):
   - **LinkedIn:** the lesson or framework; a carousel if the source has steps
   - **X:** the sharpest single insight, plus one thread covering the steps or list
   - **Facebook:** the most relatable, practical tip with a warm question, plus a link post
3. **Default set** (adjust to the brief's cadence):
   - LinkedIn: 2 posts (one text, one carousel or image)
   - X: 1 thread + 2–3 single posts
   - Facebook: 2 posts (one link post, one engagement post)
4. **Write each post** following the `social-post` workflow: hook, body, one CTA, hashtags, visual suggestion. Vary the hooks — no two posts should open the same way.
5. **Sequence** the posts: launch post with the link on publish day, then value posts over the following 1–3 weeks that point back to the source.
6. **Self-review:** every post stands alone without the article; every fact appears in the source or is marked `[VERIFY]`; voice and red lines match the brief.

## Output

Save to `marketing/content/social/YYYY-MM-DD-<source-slug>-repurpose/posts.md`:
- a schedule table: day | platform | format | angle | link?
- each post, in the `social-post` output format

Add the posts to the content inventory as one row (type `social`, title "Repurpose: <source title>"). If a weekly calendar exists for those weeks in `marketing/calendar/`, add the posts to it.
