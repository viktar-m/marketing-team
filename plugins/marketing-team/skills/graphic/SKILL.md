---
name: graphic
description: 'Design on-brand marketing graphics and export them as PNG in every size needed - social post images and carousels for LinkedIn, X and Facebook, blog cover images, diagrams and page graphics, ad creatives for Google, LinkedIn and Meta, release and launch visuals, promo banners and event graphics. Use for any request to make, design or resize a graphic, and for every graphic brief from another agent.'
---

# Graphic

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief, `marketing/design/brand-kit.md` (run `brand-kit` first if it's missing) and the brief.

## How graphics are made

Each graphic is a small self-contained HTML/CSS file, built from the brand kit's templates in `marketing/design/templates/` and rendered to PNG at exact pixel sizes:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_graphics.py marketing/design/graphics/<folder> --sheet marketing/design/graphics/<folder>/contact-sheet.png
```

- Declare sizes in each file: `<meta name="graphic-size" content="1080x1080,1080x1350">`. Body = canvas; use `vmin`/`vw` units or CSS media queries so the layout holds at every declared size. Landscape sizes (1200×627, 1600×900, 1200×628) usually need their own layout rules (`@media (min-aspect-ratio: 3/2)`) — check them separately.
- Use the brand fonts if available locally or via a stylesheet the page can load; otherwise the kit's fallbacks.
- Images and logos are referenced by relative path from `marketing/design/assets/`.
- If Playwright isn't available, run `pip install playwright && playwright install chromium`. If it still can't run, deliver the HTML files and say they need rendering. In the Claude app, a Design artifact is an alternative for one-off pieces the user wants to edit by hand.

## Sizes (working defaults — check current platform specs when precision matters)

| Use | Size (px) |
|-----|-----------|
| LinkedIn / Facebook feed image | 1080×1080 or 1080×1350 (portrait performs well in feeds) |
| LinkedIn / Facebook link image | 1200×627 |
| LinkedIn carousel (PDF document) | 1080×1350 per slide |
| X image | 1600×900 (16:9) or 1080×1080 |
| Stories / Reels cover | 1080×1920 (keep text out of the top and bottom 250 px) |
| Blog cover / Open Graph | 1200×630 |
| Meta ads | 1080×1080, 1080×1350, 1080×1920 |
| LinkedIn ads | 1200×627, 1080×1080 |
| Google display (responsive) | 1200×628 landscape, 1200×1200 square, logo 1200×1200 |

## Workflow

1. **One message per graphic.** Write the headline (12 words or fewer for social), any supporting line, and the CTA before designing. Get the copy from the brief; don't invent claims.
2. **Choose the template** that fits (tip card, announcement, feature with screenshot, carousel slide, cover, ad). For a campaign or launch, design one master layout and derive every size and variant from it.
3. **Build** the HTML in `marketing/design/graphics/YYYY-MM-DD-<slug>/`, one file per design (carousels: one file per slide, numbered `01-…`, `02-…`).
4. **Render** with the script, then **look at every PNG** (open the images): text fits and isn't cropped, contrast is readable, nothing overlaps, it's legible at phone size (imagine it at 400 px wide), the logo is present but not dominant, sizes are exact.
5. **Fix and re-render** until it passes. Then build the contact sheet.
6. **Carousels for LinkedIn:** combine the slide PNGs into a PDF (`python3 -c` with Pillow: `images[0].save('carousel.pdf', save_all=True, append_images=images[1:])`).

## Rules

- Never fake product screenshots, customer logos, ratings, testimonials or press badges. If a real asset is missing, use a clearly labelled placeholder box ("SCREENSHOT: dashboard, weekly plan view") and list it for the user.
- Text on images: high contrast (4.5:1), no text over busy photo areas without an overlay, at least 28 px on a 1080 px canvas.
- Ads: keep text light (platforms penalise or reject text-heavy images); the offer and brand must be clear without reading the ad copy.
- Accessibility: write alt text for every graphic.

## Output

The folder with HTML sources, PNGs (and PDF for carousels), `contact-sheet.png`, and `README.md` listing each file, its size, its use, alt text and any placeholders. Close the brief with the folder path.
