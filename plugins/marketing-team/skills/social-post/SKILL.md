---
name: social-post
description: 'Write on-brand social media posts for LinkedIn, X (Twitter) and Facebook — single posts, X threads, carousels and announcement posts — with a strong hook, platform-native formatting, hashtags, a CTA and an image or video suggestion. Use for any request to write, draft or rewrite a post for one or more of these platforms.'
---

# Social post

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief first — especially voice, the social section (goal per platform, hashtags, content pillars) and red lines.

## Inputs

A topic, announcement, link, or source piece, plus the platforms. If no platform is named, write for every active platform in the brief. If the source is a long article or page, use `social-repurpose` instead.

## Platform guides

Before writing, read the guide for each target platform:
- LinkedIn: `${CLAUDE_SKILL_DIR}/platforms/linkedin.md`
- X: `${CLAUDE_SKILL_DIR}/platforms/x.md`
- Facebook: `${CLAUDE_SKILL_DIR}/platforms/facebook.md`

Write each platform's version natively. Don't paste the same text everywhere — the audience, length and tone differ.

## Workflow

1. **Pick the one point** the post makes. If there are three points, that's three posts (or a thread / carousel).
2. **Write the hook** — the first line decides whether anyone reads on. Draft three hooks, keep the strongest. Good hooks are specific: a surprising fact (sourced), a concrete problem, a clear promise, a short story opening.
3. **Write the body** in the brand voice, following the platform guide's format.
4. **Close with one CTA** suited to the platform goal in the brief: comment, click, save, sign up. One ask, not three.
5. **Add hashtags** per the platform guide, starting with the brief's own hashtags.
6. **Plan the visual:** image, carousel or short video, with a one-line creative description and alt text. For anything beyond a photo the user supplies, write a brief `to: design-agent` (one brief for all posts in the request) with the platform, size, on-image text and message.
7. **Self-review:**
   - [ ] The hook works on its own, before the "see more" cut
   - [ ] One clear point and one CTA
   - [ ] Within the platform's length limit (count characters for X)
   - [ ] Voice, terminology and red lines match the brief; no banned words
   - [ ] No invented stats, quotes or customer names; anything unverified marked `[VERIFY]`
   - [ ] Links included only where the platform guide recommends

## Output

Save to `marketing/content/social/YYYY-MM-DD-<slug>/posts.md`, one section per platform:

```
## LinkedIn
**Format:** text post | image post | carousel | document
**Post:**
<copy exactly as it should be published>
**Visual:** <description> — alt text: <...>
**Link placement:** <in post | first comment | none>
**Best time to post:** <suggestion, or "per calendar">

## X
...
```

Add a row to the content inventory (type `social`). Offer 2 alternative hooks for the user's preferred platform.
