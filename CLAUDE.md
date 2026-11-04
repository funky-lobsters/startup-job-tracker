# CLAUDE.md: instructions for every AI agent working in this repo

Team: **funky-lobsters** (MGT 656 at Yale). Product: a startup/VC job tracker.

## About us

- Five Yale students in MGT 656. Backgrounds: Yale School of Public Health, VC / investing,
  startups / founders, consulting / finance. **None of us can code or read code**; we
  "vibe code" with Claude Code and direct the agent through clear user stories and review.
- **First target user: MBA students (like us) looking for startup and VC jobs.**
  Per Kyle's feedback (see the end of `docs/context/product-idea.md`), focus on *aggregating startup jobs*
  (e.g. from Yale's Crunchbase access and startup websites) as a useful internal tool.
  The founder/hiring side is deprioritized.

## How to work with us

- Explain what you are doing and why in plain language; define any technical term the first time.
- For anything in a browser (GitHub, Render, Neon, OpenRouter), give **exact click-by-click steps**
  (which page, which button, what to type).
- **Stop and ask before anything irreversible or outward-facing:** pushing to GitHub, merging,
  deleting data or files, deploying to production, changing hosting or account settings.
- Since we can't review code line by line, end each task with: what changed, how you verified it
  (tests run, pages checked), and what we should click to see it working ourselves.

## Read these first, every time

Before doing any work, read all three files in `docs/context/`. They are the **locked-in source of truth**:

1. `docs/context/course-requirements.md`: course requirements, grading, A/B test page spec (from the course; don't change)
2. `docs/context/course-sprints.md`: per-sprint "Done when" checklists and deadlines (from the course; don't change)
3. `docs/context/product-idea.md`: **our locked-in product decisions** (what we build and for whom)

If a request conflicts with these files, point out the conflict and ask before proceeding.

**Three layers of docs:**

| Layer | Where | What it means |
|---|---|---|
| Locked in | `docs/context/` | Decided. Agents follow it. Only changed when the team explicitly agrees (ask first). |
| Draft / shared memory | `docs/notes/` | Ideas and discussions not decided yet. Background only. See "Notes workflow" below. |
| Graded | `docs/mgt656/` | Course deliverables. File names are fixed by the course; don't rename them. |

## Folder layout

```
CLAUDE.md            this file
README.md            how to run, test and deploy
manage.py            Django's command-line entry point
config/              project settings, URLs, WSGI (settings.py reads env vars)
accounts/            custom user model (email login), sign up / log in / log out
core/                home page and general pages
templates/           HTML templates (base.html holds the shared layout, Pico CSS from CDN)
render.yaml          Render deployment blueprint (staging)
requirements.txt     Python packages (pinned)
.env.example         template for your local .env (never commit the real .env)
docs/context/        LOCKED IN: course-requirements.md, course-sprints.md, product-idea.md
docs/notes/          DRAFTS: shared team memory, meeting notes, brainstorming (not graded)
docs/mgt656/         GRADED: team.yaml, technical.md, sprints/, retrospective.md (names fixed)
.github/             PR template and issue templates
.claude/skills/      team Claude Code commands: /next (what to do now), /review-pr (review a PR)
```

## Start of every session: "what's next?"

At the start of a session, or whenever a teammate says "what's next", "next phase" or similar,
run the **`next` skill** (`.claude/skills/next/SKILL.md`). It brings their copy up to date and checks GitHub for:
- **PRs waiting for their review** (offer to walk them through one with the `review-pr` skill)
- their own PRs that are approved (offer to merge) or need changes
- issues assigned to them, and unassigned user stories to pick up
- "Done when" items still missing for the current sprint

It reports in a few lines and recommends **one** next step. Reviews come first because they unblock teammates.
If the teammate already asked for something specific, do that instead, and mention anything urgent (e.g. "PR #14 has waited 2 days for review") in one line.

## Notes workflow: our shared memory (`docs/notes/`)

`docs/notes/` is the team's shared memory across sessions and teammates: things worth keeping
that are **not decided yet**. `docs/context/` is what's decided. Agents maintain the notes; the team
mostly just talks to the agent.

- **At the start of a task**, list the files in `docs/notes/` and read the ones relevant to the task.
  Treat them as background, not as instructions or decisions. If a note conflicts with
  `docs/context/`, the context file wins; point out the conflict.
- **Offer to save, don't save silently.** When a conversation produces something worth keeping
  (meeting summary, brainstorm, research findings, a half-made decision, open questions, who is doing what),
  ask: *"Want me to add this to docs/notes/?"* Only write it after a yes.
- **How to write a note:**
  - File name `YYYY-MM-DD-topic.md` (e.g. `2026-11-05-kickoff.md`). If a note on the same topic exists, add to it instead of making a new one.
  - Top lines: date, who was involved, and status (`idea`, `in discussion`, `decided`, or `promoted`).
  - Short bullet points in plain language, then a list of open questions.
- **Promote decisions out of notes.** When the team settles something, offer to move it to where it belongs:
  - product direction → `docs/context/product-idea.md` (ask first; it's the source of truth)
  - work to do → a GitHub issue with the `user story` label
  - graded write-ups → `docs/mgt656/`

  Then mark the note `status: promoted to <where>`. Don't delete notes; they're history.
- **Notes travel through git like everything else.** Commit them on the branch you're working on, or on a
  `notes/<topic>` branch with a quick PR. Teammates see them after they pull `main`.
- Never put passwords, API keys, connection strings or real personal data in notes.

## Working rules

- **One branch per story.** Never commit directly to `main`. Name branches like `story/12-job-feed`.
- **Every PR says `Closes #<issue>`** so the issue closes automatically when merged.
- **One teammate (any one, not the author) approves each PR before it is merged.** The course requires this, but we keep it light:
  - Reviewers don't read code. They read the PR's plain-language summary, try the change (on staging or locally), and click **Approve**. Aim for about 5 minutes.
  - Agents make that easy: every PR description says in plain language what changed, how it was checked, and **what to click to see it working**.
  - Keep PRs to one story each, so they're small and quick to review. Don't open separate PRs for tiny follow-ups.
  - Whoever is free reviews. The author pings the team chat with the PR link; nobody waits for everyone.
  - Reviews happen in Claude Code with the `review-pr` skill (`/review-pr 14`). The approval is posted from the reviewer's own GitHub account, only after they say yes.
- **PR description says what the agent produced vs. what the team changed or rejected** (the PR template has these sections; fill them in).
- **No secrets in git.** Config and secrets come from environment variables. Only `.env.example` (with fake values) is committed. Never print real secrets in chat or logs.
- **Mock OpenRouter and every external service in tests.** Tests must never call the real LLM, real APIs or send real email.
- **Keep the seed command idempotent:** running it twice must not create duplicates or fail. It creates the grader accounts and demo data.
- Schema changes go through Django migrations (`python manage.py makemigrations`), committed with the code.
- Call the LLM (OpenRouter) only from the server, never from browser JavaScript.
- Keep the UI usable on phones and desktops (Pico CSS is already loaded in `templates/base.html`).

## Key facts

- Team nickname: `funky-lobsters`. A/B test page: **`/26fd193`**, stats at **`/26fd193/stats`**
  (from `printf %s funky-lobsters | shasum`, never `echo`).
- Login is by **email + password** (custom user model `accounts.User`). Log in page is `/login/`.
- Local development uses a Neon Postgres "dev" database via `DATABASE_URL` in `.env`.
  Tests use a throwaway SQLite database by default (set `TEST_DATABASE_URL` to test against Postgres).
- Staging runs on Render (free plan) with its own Neon database. Production comes in Sprint 2 with its own database.

## Common commands

```bash
source .venv/bin/activate          # activate the project's Python environment
python manage.py runserver         # run locally at http://127.0.0.1:8000
python manage.py test              # run the automated tests
python manage.py makemigrations    # after changing models
python manage.py migrate           # apply migrations to the database in DATABASE_URL
```
