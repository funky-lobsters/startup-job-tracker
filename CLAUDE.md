# CLAUDE.md: instructions for every AI agent working in this repo

Team: **funky-lobsters** (MGT 656 at Yale). Product: a startup/VC job tracker.

## About us

- Five Yale students in MGT 656. Backgrounds: Yale School of Public Health, VC / investing,
  startups / founders, consulting / finance. **None of us can code or read code**; we
  "vibe code" with Claude Code and direct the agent through clear user stories and review.
- **First target user: MBA students (like us) looking for startup and VC jobs.**
  Per Kyle's feedback (see the end of `docs/context/IDEA.md`), focus on *aggregating startup jobs*
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

Before doing any work, read all three files in `docs/context/`. They are the source of truth:

1. `docs/context/PROJECT_SPEC.md`: course requirements, grading, A/B test page spec
2. `docs/context/SPRINTS.md`: per-sprint "Done when" checklists and deadlines
3. `docs/context/IDEA.md`: our product idea and user journeys

If a request conflicts with these files, point out the conflict and ask before proceeding.

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
docs/context/        permanent context files (spec, sprints, idea). Do not edit casually.
docs/notes/          meeting notes and brainstorming (not graded)
docs/mgt656/         graded course docs: team.yaml, technical.md, sprints/, retrospective.md
.github/             PR template and issue templates
```

## Working rules

- **One branch per story.** Never commit directly to `main`. Name branches like `story/12-job-feed`.
- **Every PR says `Closes #<issue>`** so the issue closes automatically when merged.
- **A teammate reviews every PR before it is merged.**
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
