---
name: ad-creative
description: 'Write ad copy and creative concepts for Google Ads (responsive search ads, display, Performance Max assets), LinkedIn Ads and Meta Ads - multiple angles, every text field within its character limit, matched to the landing page, with visual concepts briefed to the design agent. Use for new ads, ad refreshes when creatives fatigue, A/B test variants, or promo and launch ads.'
---

# Ad creative

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, `marketing/strategy/paid.md`, the campaign plan, the landing page, and recent ad reports (what has won before).

## Field limits (working defaults — verify against current platform specs)

| Platform / format | Field | Limit |
|---|---|---|
| Google responsive search ad | Headlines (up to 15) | 30 characters each |
| | Descriptions (up to 4) | 90 characters each |
| | Display path (2) | 15 characters each |
| Google Performance Max / display | Short headlines (up to 5) / long headline / descriptions | 30 / 90 / 90 (one description ≤ 60) |
| LinkedIn single image | Intro text | 600 max; ~150 shows before truncation |
| | Headline | 70 recommended (200 max) |
| Meta (Facebook/Instagram) | Primary text | ~125 shows before "See more" |
| | Headline | ~40 recommended |
| | Description | ~30 recommended |

**Count characters with code, not by eye**, e.g. `python3 -c "for s in [...]: print(len(s), s)"`, and fix anything over the limit.

## Workflow

1. **Angles.** Write 3–5 distinct angles for the audience, each a different reason to act: pain ("stop binning half your groceries"), outcome, proof (only verified proof), offer, objection-killer, comparison, urgency (only if real). Recommend 2–3 to test.
2. **Google RSA.** Per ad group: 15 headlines covering keyword match (2–3 using the ad group's main keyword), benefits, features, proof, offer, CTA, brand; 4 descriptions that each stand alone. Avoid near-duplicates — the system combines them. Pin only what must be fixed (e.g., brand or legal text).
3. **LinkedIn / Meta.** Per angle: primary/intro text (hook in the first line), headline, description, CTA button choice, and a **visual concept**: what the image or video shows, the text on it (≤ 6–8 words), format (single image, carousel, video).
4. **Message match.** Each ad's promise appears in the landing page headline or first screen. If not, flag it.
5. **Policy check.** No unverifiable superlatives ("best", "#1") without proof, no implying personal characteristics on Meta ("Are you struggling with…" about health, finances, etc.), no misleading urgency, trademark care when naming competitors, claims within the brand brief's red lines.
6. **Visuals.** Describe every creative for the design agent (queue it as one brief only if the user says yes): angle, visual concept, on-image text, sizes per platform (see the `graphic` skill's size table).

## Output

Every file you save starts with the header from the conventions (§3: title, type, agent, status, date, summary, needs_you). Finish with the done message (§5) — no file paths in the reply.

`marketing/ads/<name>-ad-copy.md`: angle summary and test plan, then per platform a table of every field with its character count, the visual concepts, the design brief path, and anything to verify. Format the Google assets so they can be pasted into the platform or an upload sheet.
