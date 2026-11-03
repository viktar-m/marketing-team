# AI visibility setup

The tracker needs API access to each AI engine you want to measure. It runs as a daily GitHub Actions workflow in your **private workspace repository**. Your API keys are stored there as encrypted repository secrets: you never paste them into a chat or a file, and Claude never sees them.

## 1. Get API keys

A ChatGPT subscription (Plus, Pro, Team) does **not** include API access. The API is a separate, pay-as-you-go account on the OpenAI Platform.

| Engine | Where | Secret name |
|--------|-------|-------------|
| ChatGPT (OpenAI) | platform.openai.com → API keys (add billing credit first) | `OPENAI_API_KEY` |
| Perplexity (optional) | perplexity.ai → Settings → API | `PERPLEXITY_API_KEY` |
| Gemini (optional) | aistudio.google.com → Get API key | `GEMINI_API_KEY` |
| Claude (optional) | console.anthropic.com → API keys | `ANTHROPIC_API_KEY` |

Start with OpenAI alone if you like. Engines without a key are skipped. Set a monthly spending limit on each platform.

**Cost:** each question is one API call with web search. 30 questions × 1 engine × 30 days = 900 calls a month. Check current per-call and web-search prices on each platform's pricing page and set `runs_per_prompt` and the number of questions to fit your budget.

## 2. Add the workflow and secrets

1. In the workspace repo, the team copies `templates/workspace/github-workflows/ai-visibility.yml` to `.github/workflows/ai-visibility.yml` and creates `marketing/ai-visibility/config.json` (ask: "Set up AI visibility tracking").
2. On GitHub, open the workspace repo → **Settings → Secrets and variables → Actions → New repository secret**. Add `OPENAI_API_KEY` with your key, and any optional keys.
3. **Actions** tab → **AI visibility tracker** → **Run workflow** to test. It commits results to `marketing/ai-visibility/` and `marketing/dashboards/ai-visibility.html`.

From then on it runs daily at 05:17 UTC. Change the `cron` line to adjust the time.

## 3. Weekly review

The `weekly-ai-visibility` routine, or "Review our AI visibility", has the SEO agent read the week's answers, add sentiment, diagnose lost questions and write briefs.

## Notes

- API answers approximate what users see. Consumer apps add personalisation, location and different model versions. Watch the trend over weeks rather than single days.
- Model names in `config.json` (`engines.<name>.model`) can be updated as providers release new models.
- Try the dashboard without any keys: `python3 plugins/marketing-team/scripts/ai_visibility.py demo --dir /tmp/demo && python3 plugins/marketing-team/scripts/ai_visibility.py report --dir /tmp/demo --out /tmp/demo/dashboard.html`
