---
name: ai-visibility
description: 'Track and improve how AI answer engines (ChatGPT, Perplexity, Gemini, Claude) answer the questions our audience asks - whether the brand is mentioned, in what position, which sources are cited, share of voice and sentiment versus competitors - with a visual dashboard and an action plan (AEO / GEO). Use to set up AI visibility tracking, for weekly AI visibility reviews, or for "how do AI assistants talk about us / our competitors".'
---

# AI visibility (AEO / GEO)

Read `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`, the brand brief (section 10: names, competitors, questions) and `marketing/strategy/seo.md` if present.

Two parts work together:
- **The tracker** (`${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py`) asks each AI engine the audience's questions through its API, every day, and records mentions, positions and citations in `marketing/ai-visibility/`. It runs best as a scheduled GitHub Actions workflow in the workspace repository, where API keys are stored as repository secrets.
- **This skill** sets the tracker up, reviews the answers (sentiment, why competitors win), and turns findings into actions.

## Mode 1 — Set up tracking

1. **Build the question set** in `marketing/ai-visibility/config.json` from `${CLAUDE_PLUGIN_ROOT}/templates/workspace/ai-visibility-config.example.json`:
   - brand name, aliases (including common misspellings and the domain), domain
   - 2–5 competitors with domains
   - 20–40 prompts written the way real people ask assistants: category questions ("best X for Y"), problem questions ("how do I…"), comparisons ("A vs B"), and buying questions ("is X worth it"). Mix in prompts from the brief, the keyword research, sales objections and support questions. Give each a short stable `id`, a `topic` and an `intent`.
   - don't include the brand name in category and problem prompts — that would make visibility meaningless.
2. **Schedule it.** In a git workspace, copy `${CLAUDE_PLUGIN_ROOT}/templates/workspace/github-workflows/ai-visibility.yml` to `.github/workflows/ai-visibility.yml` and tell the user to add `OPENAI_API_KEY` (and any other engine keys) under the repository's **Settings → Secrets and variables → Actions**. Never ask the user to paste a key into the chat or write one into a file.
3. **No API access?** If no key can be set up, say plainly that true tracking isn't possible, and offer a manual baseline instead: use web search plus your own answer to the prompts, and label the results "Claude-only snapshot", never as ChatGPT or Perplexity data.

## Mode 2 — Weekly review

1. **Refresh the numbers.** If you can run Python with network access and keys are present, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py run --dir marketing/ai-visibility`; otherwise use the data the scheduled workflow committed (`git pull` first). Then build the dashboard:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_visibility.py report --dir marketing/ai-visibility --out marketing/dashboards/ai-visibility.html`
2. **Review sentiment.** Read the raw answers for the review period in `marketing/ai-visibility/data/*.jsonl`. For each answer that mentions a tracked brand, classify how it's described — `positive` (recommended, praised), `neutral` (listed, described), `negative` (criticised, warned against, described inaccurately) — and append rows to `marketing/ai-visibility/sentiment.csv` with columns `date,engine,prompt_id,brand,sentiment,note`. Note factual errors about our product in `note`; they're high priority.
3. **Rebuild the dashboard** so it includes sentiment, and read `latest-metrics.json` for the numbers.
4. **Diagnose** (this is the valuable part):
   - Which questions do we lose, and who wins them? Read those answers: what do they say about the winner that they don't say about us?
   - Which sources are cited most for the questions we lose? Third-party sites (review sites, communities, publications, Wikipedia, YouTube) are where mentions are earned.
   - Is our own site cited? If not, which of our pages should answer that question and doesn't — or doesn't answer it clearly enough to be quoted?
   - Are any answers wrong about us (pricing, features, positioning)?
5. **Act.** Write up to 5 briefs, highest impact first:
   - `to: web-content-agent` — pages that directly answer lost questions in quotable form: a clear one-paragraph answer, explicit entity names, comparison tables, FAQs, up-to-date facts, structured data
   - `to: strategist` — earned-media and community opportunities on the most-cited third-party sources (reviews, listings, guest content, community answers)
   - `to: gtm-agent` or `to: web-content-agent` — corrections where AI answers are wrong (fix the source pages they rely on)

## Output

- Report: `marketing/reports/YYYY-MM-DD-ai-visibility.md` — headline numbers and change vs the previous period (visibility, share of voice, citation rate, average position, sentiment), wins and losses by question, top cited sources, errors found, and the actions with brief paths
- Dashboard: `marketing/dashboards/ai-visibility.html` — share it or open it as an artifact when the environment supports that (see `${CLAUDE_PLUGIN_ROOT}/templates/dashboards.md`)

## Caveats to state in reports

API answers approximate what users see; consumer apps add personalisation, location and different model versions. Single answers vary — trends over weeks matter more than one day. Visibility means "mentioned", not "recommended"; sentiment tells the difference.
