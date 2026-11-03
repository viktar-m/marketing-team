# Team conventions

Every agent and skill in the marketing team follows these rules. They keep the work consistent, let the agents hand work to each other, and let the team remember what it has already done.

## 1. The brand brief is the source of truth

All brand facts live in one file: `marketing/brand-brief.md` in the user's project folder.

- Read it before any task. Use its voice, audience, positioning, terminology, keywords and links.
- In a claude.ai chat with no project folder, look for the brief in the Project's knowledge files instead.
- If no brief exists: for a quick task, go ahead, state the assumptions you made at the top of the output, and suggest running the `brand-setup` skill. For larger work (audits, multi-piece campaigns, page rewrites), stop and offer `brand-setup` first — guessing a brand at scale wastes the user's time.
- Never write brand facts into skills or agents. If you learn a durable fact during a task (a new product feature, a banned phrase), suggest adding it to the brief.

## 2. Workspace layout

```
marketing/
├── brand-brief.md              # who we are, how we sound, who we sell to
├── content-inventory.md        # every piece the team has produced or refreshed
├── briefs/                     # content briefs (SEO agent → content agent)
│   └── YYYY-MM-DD-<slug>.md
├── content/
│   ├── blog/YYYY-MM-DD-<slug>/
│   ├── pages/YYYY-MM-DD-<slug>/
│   ├── refreshes/YYYY-MM-DD-<slug>/
│   └── social/YYYY-MM-DD-<slug>/
├── reports/                    # audits, gap analyses, keyword research
│   └── YYYY-MM-DD-<report-type>.md
└── calendar/
    └── YYYY-Www.md             # weekly social calendar (ISO week)
```

Create folders as needed. Use lowercase, hyphenated slugs. Dates are the day the work is done.

## 3. Content inventory

After producing or refreshing any piece, append one row to `marketing/content-inventory.md` (create it with this header if missing):

```
| Date | Type | Title | Primary keyword | Location / URL | Status |
|------|------|-------|-----------------|----------------|--------|
```

Status is one of `draft`, `ready`, `published`, `refreshed`. Check the inventory before proposing new topics so the team doesn't duplicate work.

## 4. Handoffs between agents

The SEO agent never writes final content, and the content agent never decides strategy on its own. Work moves between them as **content briefs** in `marketing/briefs/`, using `${CLAUDE_PLUGIN_ROOT}/templates/content-brief.md`.

- A brief's `status` moves `ready` → `in-progress` → `done`.
- Subagents cannot call each other directly. The SEO agent writes briefs and returns their file paths; the main session (the team lead) then hands each brief to the content agent.
- When the content agent finishes a brief, it sets `status: done` and adds the output path to the brief.

## 5. Facts and claims

- Never invent statistics, customer names, quotes, awards, benchmarks, prices or feature claims.
- Product claims must come from the brand brief or a page the user owns. External facts need a source link.
- Anything you could not verify goes in the output's **To verify** list, and is marked `[VERIFY]` in the text.
- Be fair to competitors and alternatives. Don't disparage; compare on facts.

## 6. Output

- Default deliverable is Markdown in the workspace folder above.
- Produce a Word (.docx) version only when the user or the brief asks for one.
- End every task with a short summary: what was produced, where it is, and what needs a human check.
- Run autonomously. Don't stop for outline approval or routine confirmation; make sensible choices and state them. Ask only when a missing input would make the result wrong (for example, no URL for a page refresh).
