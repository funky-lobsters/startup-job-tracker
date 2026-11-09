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
| `abtest/` | A/B test page `/26fd193`, stats `/26fd193/stats`, traffic-source tracking |
| `templates/` | HTML pages; `base.html` is the shared layout (Pico CSS) |
| `docs/context/` | **Locked in**: course requirements, sprint checklists, our product decisions |
| `docs/notes/` | **Drafts**: shared team memory, meeting notes, brainstorming |
| `docs/mgt656/` | **Graded** course docs (team.yaml, sprint reports, technical.md); names fixed |
| `render.yaml` | Render hosting setup (staging) |
| `.env.example` | Template for your local `.env` secrets file |

## One-time setup for each teammate

About 15 minutes, once per laptop. Claude does most of it for you.

**How syncing works:** your laptop holds its own full copy of the project, and GitHub holds the shared
master copy. Nothing syncs automatically like Google Drive: your changes reach GitHub when Claude uploads
them (push, then a PR), and teammates' changes reach you when Claude downloads them (pull). `/next` downloads
the latest version at the start of every session.

1. **Accept the GitHub invite** to the `funky-lobsters` organization: open the email from GitHub, or go to
   https://github.com/orgs/funky-lobsters/invitation and click **Join funky-lobsters**.
2. **Install the GitHub CLI** (lets Claude talk to GitHub for you): go to https://cli.github.com,
   click **Download for Mac**, open the downloaded file and click through the installer.
3. **Make a folder for your projects.** Any name works (e.g. `Developer`, `Projects`, `MGT656`), but:
   - put it directly in your home folder (in Finder press **Cmd+Shift+H**, then **File → New Folder**)
   - **not** in iCloud Drive, Dropbox, OneDrive, Google Drive, or Desktop/Documents if iCloud syncs them
     (their syncing clashes with GitHub's and can corrupt files)
   - no spaces or special characters in the name (`MGT656`, not `MGT 656 Project!`)
4. In the **Claude app → Code tab**, open that folder and type:
   > *Clone funky-lobsters/startup-job-tracker into this folder and do the one-time setup from its README.*

   Claude logs you into GitHub (click **Authorize** in the browser when asked), downloads the project
   and installs what it needs. Along the way:
   - when Claude asks to run a command, click **Allow**
   - if a Mac popup asks to install "command line developer tools", click **Install** and wait (5–10 minutes)
5. **When it's done, start a new Claude Code session and choose the `startup-job-tracker` folder** (inside the
   folder you made). Always use that folder from now on: `/next` and `/review-pr` only work there.
6. **Ask Ben privately for the Neon dev database address** (never in a group chat). Claude will show you where
   to paste it in your `.env` file.

<details><summary>Doing it by hand instead (for Claude or the curious)</summary>

```bash
gh auth login        # GitHub.com → HTTPS → Yes → Login with a web browser
```
```bash
gh repo clone funky-lobsters/startup-job-tracker <your-folder>/startup-job-tracker
```
Then follow "Run it on your computer" below.
</details>

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

## Seed command (grader accounts)

```bash
python manage.py seed
```

Creates or updates `admin@example.com` and `member@example.com` with the passwords in
`GRADER_ADMIN_PASSWORD` / `GRADER_MEMBER_PASSWORD` (from `.env` locally, Render settings on staging).
Safe to run any number of times. Render runs it automatically on every start.

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
