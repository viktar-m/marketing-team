---
name: video-brief
description: 'Prepare a short marketing video for production - define the goal and story, organise the assets already available, tell the user exactly what to record or provide (shot list, screen recordings, photos, voice-over), and write a scene-by-scene production brief ready to paste into Claude''s Motion video tool. Use for release videos, product teasers, feature explainers, social video, ad videos and event promos.'
---

# Video brief

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, the brand kit (`marketing/design/brand-kit.md`), `marketing/strategy/social.md`, and the brief or launch kit behind the video.

A good video brief does two jobs: it gets the right raw material collected, and it gives the video tool everything it needs to make the piece in one pass. Work in two phases.

## Phase 1 — Plan and asset list

1. **Define the video.**
   - Goal and the one message the viewer must remember
   - Audience and where it will be watched (LinkedIn feed, X, Facebook, Reels, YouTube, website hero, ad)
   - Length (social: 15–45 s; explainer: 60–90 s; ad: 6, 15 or 30 s) and aspect ratios (9:16 vertical, 1:1 square, 16:9 landscape, 4:5 feed)
   - Style: motion graphics, product screen demo, kinetic typography, talking head with graphics, or a mix
2. **Story.** A simple structure: hook (first 2–3 seconds, works with sound off) → problem → product moment → proof or result → CTA. Draft the script or on-screen text for each beat.
3. **Inventory what exists.** Look in `marketing/design/assets/` and the launch or campaign folder: logos, screenshots, product UI recordings, photos, earlier videos, music licences. List each usable asset with its path.
4. **Shot and asset list — what the user must provide.** For every gap, a precise request:
   - **Screen recordings:** what to show, click by click; resolution (at least 1920×1080, or the product's native size), length, clean demo data, hidden personal info, cursor highlighted
   - **Photos or footage:** subject, framing, orientation, lighting
   - **Voice-over** (if used): the script, tone, target length; or note that the tool's generated voice is fine
   - **Approvals:** customer logos or quotes need permission
   Mark each as **must have** or **nice to have**, and suggest a motion-graphics fallback for nice-to-haves (e.g., an animated mock-up instead of a real recording).

Save to `marketing/content/video/YYYY-MM-DD-<slug>/plan.md` and tell the user the must-have list in one short message. Ask them to drop the files into `marketing/content/video/YYYY-MM-DD-<slug>/assets/`. If everything needed already exists, go straight to Phase 2.

## Phase 2 — Motion brief

When assets are in place (or the user says to proceed with fallbacks), write `motion-brief.md` in the same folder. It must stand alone — the video tool sees only this text and the attached files:

```
# <Video title>
Format: <aspect ratio(s)> · Length: <seconds> · Platform: <where it runs>
Goal: <one sentence>  ·  Key message: <one sentence>
Style: <motion style, pace, mood>; brand colours <hex list>; fonts <names>; logo <file>
Audio: <music mood / none>; voice-over <yes/no, script below>; captions burned in: yes

## Scenes
| # | Time | Visual (what we see, which asset file) | On-screen text | VO / sound | Transition |
|---|------|----------------------------------------|----------------|------------|------------|
| 1 | 0–3 s | ... | ... | ... | ... |

## End card
Logo, CTA text, URL, duration

## Assets attached
- <file name> — what it is and which scene uses it

## Must not
- e.g., no stock footage of people, no fake UI, no claims beyond the script
```

Rules for the brief: on-screen text short enough to read in the scene's time (about 3 words per second); every scene names its asset file or describes the generated visual; brand colours as hex codes; the first scene works without sound.

## Output

`plan.md` (Phase 1), `motion-brief.md` (Phase 2), and a content inventory row (type `video`). Tell the user how to use it: open Claude's Motion feature, attach the files listed under "Assets attached", and paste the brief. For cut-downs (other lengths or ratios), add one short section per variant listing which scenes to keep.
