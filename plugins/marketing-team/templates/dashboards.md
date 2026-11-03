# Visual dashboards

The team's work should look like a tool, not a pile of text. Every report with numbers, plan with dates, or queue of work also gets a visual dashboard. The Markdown file stays the record; the dashboard is how the user takes it in.

## Format

- **One self-contained HTML file** in `marketing/dashboards/` (or next to the plan it belongs to): inline CSS, inline SVG charts, no external scripts, fonts or CDNs — it must open anywhere, offline, and survive being published as an artifact.
- **Delivering it:** if the session can publish or open artifacts, publish the dashboard so it appears as a page the user can open and share; otherwise send or link the file. In a git workspace, commit it so it's viewable later.
- If a data-visualisation skill is available in the session (e.g., `dataviz`), follow it — its rules win over the defaults below.

## Layout

1. **Header:** title, one-line context (period, data sources), last updated.
2. **KPI tiles** (3–5): the number, a plain-language label, and the change vs the previous period with ▲/▼ and the size of the change. Headline numbers belong in tiles, not charts.
3. **Charts** (2–4): one question per chart, titled as the question or the answer ("Share of voice over time", "Where spend converts").
4. **Table view** of the underlying numbers, so nothing depends on reading colour.
5. **Actions:** the recommendations or next steps, linked to briefs.
6. **Footnote:** definitions and data caveats.

## Chart rules

- Pick the form by the job: change over time → line; comparing categories → horizontal bars sorted by value; part of a whole with ≤ 4 parts → stacked bar (avoid pies); a single number → tile; schedule → timeline/Gantt rows.
- One y-axis per chart, never two. Start bar axes at zero.
- Colour by identity in a fixed order — our brand is always slot 1, and an entity keeps its colour across every chart. More than 8 series → group the rest as "Other".
- Direct labels on lines (≤ 4 series) plus a legend; values on bars; recessive grid; 2 px lines; ≥ 8 px markers; rounded bar ends.
- Tooltips on marks (`<title>` inside SVG elements is enough).
- Status colours (good / warning / serious / critical) only for state, always with an icon or word, never as a series colour.
- Light and dark mode: define colours as CSS variables, with a `prefers-color-scheme: dark` block and a toggle.

## Default palette

Swap in brand colours from `marketing/design/brand-kit.md` only if they've been checked for colour-blind separation; otherwise use these, which have been.

| Slot | Light | Dark |
|------|-------|------|
| 1 (us) | `#2a78d6` | `#3987e5` |
| 2 | `#eb6834` | `#d95926` |
| 3 | `#1baf7a` | `#199e70` |
| 4 | `#eda100` | `#c98500` |
| 5 | `#e87ba4` | `#d55181` |
| 6 | `#008300` | `#008300` |
| 7 | `#6250d6` | `#9085e9` |
| 8 | `#e34948` | `#e66767` |

Surfaces: light `#fcfcfb` on page `#f6f6f4`, text `#0b0b0b` / secondary `#52514e`; dark `#1a1a19` on `#111110`, text `#f0efec` / secondary `#c3c2b7`. Status: good `#0ca30c`, warning `#fab219`, serious `#ec835a`, critical `#d03b3b`.

`${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py` (report command) and `${CLAUDE_PLUGIN_ROOT}/scripts/hq.py` are working examples of this style — reuse their CSS and chart helpers.

## Check before delivering

Render it (e.g., Playwright screenshot) and look: labels don't collide, nothing overflows on a 390 px-wide phone screen, numbers match the Markdown report.
