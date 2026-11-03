---
name: brand-kit
description: 'Create or update the visual brand kit every graphic follows - logo files and usage, colour palette with hex codes and roles, fonts, layout grid, image and illustration style, iconography, and reusable templates for social, blog, ads and launches. Use when setting up the design agent, before the first graphics for a new brand, or when the visual identity changes.'
---

# Brand kit

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` and the brand brief.

## Sources, in order of trust

1. Brand guidelines or design-system files the user provides
2. Assets in `marketing/design/assets/` (logos, existing graphics, screenshots)
3. The website: fetch the home page and a product page, read the CSS for colours and font families, and look at existing social and blog graphics
4. Only if nothing exists: propose a simple starter kit and mark it **proposed — needs approval**

## Workflow

1. **Logo.** List the available files (SVG preferred, PNG fallback), versions (full, mark, mono, light/dark), clear space and minimum size. If no file is available, note that the user must add one to `marketing/design/assets/logo/`.
2. **Colour.** Primary, secondary, accent, neutrals, plus background and text colours, each with hex and a role ("primary CTA", "headline on dark"). Check text/background pairs for contrast (4.5:1 for body text, 3:1 for large text) and list the approved pairs.
3. **Type.** Heading and body fonts with weights; web-safe fallbacks; type scale for 1080 px social graphics (e.g., headline 64–88 px, body 32–40 px).
4. **Layout.** Margins (e.g., 64 px on 1080 px), logo placement, grid, maximum text per graphic (aim for 12 words or fewer on social images).
5. **Imagery.** Photo style, illustration style, icon style, screenshot treatment (device frame or not, shadow, corner radius), what to avoid.
6. **Templates.** Define 4–6 reusable layouts as HTML/CSS in `marketing/design/templates/` (see the `graphic` skill for the format): quote/tip card, announcement, feature highlight with screenshot, carousel slide, blog cover, ad creative. Each uses CSS variables for the kit's colours and fonts so later graphics stay consistent.
7. **Preview.** Render the templates with sample text to PNG (see the `graphic` skill) and assemble a one-page preview `marketing/design/brand-kit-preview.png`.

## Output

`marketing/design/brand-kit.md` with the sections above (use tables for colours and type), the template files, the preview image, and a summary for the user: what was taken from their materials, what was proposed, and what they need to supply or approve.
