# Funky Lobsters: Startup & VC Job Tracker

MGT 656 team project. A two-sided startup jobs platform: job seekers track opportunities,
founders find candidates. Built with Django + Postgres, hosted on Render + Neon.

- Product idea: [docs/context/product-idea.md](docs/context/product-idea.md)
- Course requirements: [docs/context/course-requirements.md](docs/context/course-requirements.md) and [docs/context/course-sprints.md](docs/context/course-sprints.md)
- AI agent instructions: [CLAUDE.md](CLAUDE.md)

## Folder layout

| Path | What's there |
|---|---|
| `config/` | Django settings (reads environment variables), URL routes |
| `accounts/` | User accounts: email login, sign up / log in / log out |
| `core/` | Home page and general pages |
| `templates/` | HTML pages; `base.html` is the shared layout (Pico CSS) |
| `docs/context/` | **Locked in**: course requirements, sprint checklists, our product decisions |
| `docs/notes/` | **Drafts**: shared team memory, meeting notes, brainstorming |
| `docs/mgt656/` | **Graded** course docs (team.yaml, sprint reports, technical.md); names fixed |
| `render.yaml` | Render hosting setup (staging) |
| `.env.example` | Template for your local `.env` secrets file |

## One-time setup for each teammate

Tip: after step 3 you can open the folder in Claude Code and say *"do the one-time setup in README.md for me"*.

1. **Accept the GitHub invite** to the `funky-lobsters` organization (check your email or github.com/funky-lobsters).
2. **Install the GitHub CLI** (lets Claude Code read issues, open PRs and post your approvals):
   go to https://cli.github.com, click **Download for Mac**, open the downloaded file and click through the installer.
   Then, in Terminal:
   ```bash
   gh auth login
   ```
   Answer: **GitHub.com** → **HTTPS** → **Yes** (authenticate Git) → **Login with a web browser**, then paste the code it shows into the browser page.
3. **Get the code** onto your laptop:
   ```bash
   gh repo clone funky-lobsters/startup-job-tracker ~/Developer/startup-job-tracker
   ```
   In the Claude desktop app, open the **Code** tab and choose that folder.
4. Do "Run it on your computer" below. Ask a teammate privately for the Neon **dev** connection string.

## Day to day in Claude Code

- Type **`/next`** (or "what's next?"). Claude checks GitHub and tells you which PRs are waiting for your review,
  the state of your own PRs, issues to pick up, and what's missing for this sprint. It recommends one step.
- Type **`/review-pr 14`** to review PR #14. Claude explains it in plain language, runs the tests, checks it against
  the issue, and posts your approval only after you say yes.

## Run it on your computer (first time)

1. Install `uv` (a Python manager; installs Python for you, no admin password):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Then close and reopen your terminal.
2. In this folder, create the Python environment and install packages:
   ```bash
   uv venv --python 3.13
   ```
   ```bash
   uv pip install -r requirements.txt
   ```
3. Create your secrets file: copy `.env.example` to `.env`, then paste the Neon **dev**
   connection string into `DATABASE_URL` (ask a teammate for it, never commit it):
   ```bash
   cp .env.example .env
   ```
4. Create the database tables and start the app:
   ```bash
   source .venv/bin/activate
   ```
   ```bash
   python manage.py migrate
   ```
   ```bash
   python manage.py runserver
   ```
   Open http://127.0.0.1:8000.

Every later time, only `source .venv/bin/activate` and `python manage.py runserver` are needed.

## Run the tests

```bash
source .venv/bin/activate
```
```bash
python manage.py test
```

Tests use a throwaway SQLite database (no internet needed, no clash between teammates).
To run them against Postgres instead, set `TEST_DATABASE_URL` in `.env`.
Tests must never call OpenRouter or other external services: mock them.

## Deploy

- **Staging** (Render, free plan) deploys automatically on every merge to `main`.
  Config is in `render.yaml`; secrets (`DATABASE_URL`, `SECRET_KEY`) live only in the Render dashboard.
  Migrations run automatically when the app starts.
- **Production**: added in Sprint 2, with its own Neon database.

Environment variables: `DATABASE_URL`, `SECRET_KEY`, `DEBUG`, optional `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `LOG_LEVEL`. Render's own hostname is allowed automatically.

## How we work

Branch per story → PR with `Closes #<issue>` → **one** teammate approves (via `/review-pr`, ~5 minutes) → merge → staging redeploys. See [CLAUDE.md](CLAUDE.md).
