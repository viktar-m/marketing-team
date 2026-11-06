---
name: workspace-setup
description: 'Set up a new marketing workspace for a product, company or client in an empty (or partly set-up) repository or folder - session instructions (CLAUDE.md), folder structure, brand brief template, AI visibility workflow and the Marketing Hub - then start the brand brief. Use for "set up a marketing workspace for X", a new client or product, an empty repo, or when a workspace is missing its CLAUDE.md or folders.'
---

# Workspace setup

One workspace per product or client: a private git repository (preferred, so scheduled runs and the AI visibility workflow work without anyone's computer) or a local folder. This skill turns an empty one into a ready workspace in one step, then hands over to `brand-setup`.

## Inputs

- Product, company or client name (required — ask if missing)
- Website URL (strongly recommended; brand-setup drafts the brief from it)
- Any brand material the user attached (guidelines, decks, style guides)

## Steps

1. **Check where you are.** Work at the root of the repository or folder the user chose. If it's a git repository, run `git pull` (an empty repository has nothing to pull; that's fine). If the folder already contains unrelated files (code, another project), stop and ask before adding a workspace there.
2. **Create the workspace** — it never overwrites existing files, so it's also safe for repairing a partial workspace:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_workspace.py --root . --product "<name>" --website "<url>"
   ```
   Leave the AI visibility schedule off (the default). Turn it on later, once `marketing/ai-visibility/config.json` exists and an API key secret is set — and only if the user wants daily tracking.
3. **Save it.** In a git repository: commit (`workspace-setup: <name>`) and push. If the push of `.github/workflows/` is rejected for permissions, push the rest and tell the user to add the workflow file through the GitHub website (or leave AI visibility for later).
4. **Write the brand brief** — continue straight into `marketing-team:brand-setup` with the website and any attached material. Don't make the user ask twice.
5. **Show the result:** a short summary of what was created, the brief's open questions (from brand-setup), and the next steps in order — strategy (`marketing-team:strategy`), brand kit (`marketing-team:brand-kit`, after the user adds a logo and screenshots to `marketing/design/assets/`), AI visibility setup (`marketing-team:ai-visibility`).

## Notes

- Keep client workspaces private. Never put two clients in one workspace.
- The workspace's `CLAUDE.md` tells every future session in it to route requests through `marketing-team:team-lead`, pull first, and commit at the end — so the user can start any new session there with a plain request.
- Recommend a naming pattern for repositories, e.g. `mkt-<product>`.
