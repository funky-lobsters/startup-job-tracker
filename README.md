# Funky Lobsters: Startup & VC Job Tracker

MGT 656 team project. A two-sided startup jobs platform: job seekers track opportunities,
founders find candidates. Built with Django + Postgres, hosted on Render + Neon.

- Product idea: [docs/context/product-idea.md](docs/context/product-idea.md)
- Course requirements (source of truth, kept up to date by Kyle): [yale-mgt-656-fall-2026/project-requirements](https://github.com/yale-mgt-656-fall-2026/project-requirements)
- Our notes on the requirements: [docs/context/course-requirements.md](docs/context/course-requirements.md) and [docs/context/course-sprints.md](docs/context/course-sprints.md)
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
| `scripts/cloud-setup.sh` | Installs the Python packages at the start of a cloud session (Claude runs it) |

## Getting started: Claude Code in the cloud (recommended for everyone)

You don't install anything. Each Claude Code session runs on a fresh computer in the cloud with the latest copy of our
GitHub project. Claude makes the changes there, then sends them back to GitHub as a branch and a pull request (PR).
**Nothing is saved on your laptop**, and you never deal with Python, folders or passwords.

**You need:** a GitHub account, and a **paid Claude plan (Pro or higher)**. Cloud sessions aren't included in the free plan.

### One-time setup (about 5 minutes)

1. **Accept the GitHub invite** to `funky-lobsters`: open the email from GitHub, or go to
   https://github.com/orgs/funky-lobsters/invitation and click **Join funky-lobsters**.
2. **Open Claude Code:** the Claude desktop app → **Code** tab, or https://claude.ai/code in your browser (both work the same).
3. **Switch to the cloud.** Below the message box, bottom left, is the environment button. Click it and choose the cloud
   option, **Anthropic-hosted Default** (cloud icon), not **Local**.
4. **Connect GitHub** (first time only). When Claude asks you to connect GitHub, click it, sign in to GitHub and click
   **Authorize** (or **Install & Authorize**). You're sent back to Claude.
5. **Pick our project.** Click **Repo** (next to the environment button), type `startup` in **Search repositories…**
   and click **funky-lobsters/startup-job-tracker**.

**Repo not in the list?**
- Make sure you accepted the GitHub invite (step 1).
- Click the **refresh** icon (⟳) in the search box.
- Click the **gear** icon (⚙) next to it, and make sure Claude has access to the **funky-lobsters** organization on GitHub.
  If GitHub says the request was sent to an owner, message Ben to approve it.

### Every time you work

1. Claude Code → **Code** tab. Check the environment says **Anthropic-hosted Default** and **Repo** says
   **funky-lobsters/startup-job-tracker**.
2. In **Describe a task or ask a question**, type **`/next`** and press Enter. Claude gets ready (about a minute the first
   time), then tells you what's waiting for you: PRs to review, your issues, and what's missing for this sprint.
3. Work on **one story per session**: say which issue to work on (e.g. "work on issue #14"). Claude builds it, runs the
   tests, and opens a PR that says `Closes #14`. If you see a **Create PR** button instead, click it.
4. Post the PR link in the team chat. One teammate reviews it with **`/review-pr 14`**. After it's merged, staging updates
   on its own, and the PR says what to click there to see your change.

**Good to know**
- You **can't open the app running inside the cloud computer**. Claude shows it works through automated tests, and
  you see the real thing on **staging** after the merge.
- Each session is its own computer. If you close a session before Claude has pushed and opened the PR, ask it to do that first.
- **Never paste passwords, API keys or database addresses into a chat.**

## Day to day in Claude Code

- Type **`/next`** (or "what's next?"). Claude checks GitHub and tells you which PRs are waiting for your review,
  the state of your own PRs, issues to pick up, and what's missing for this sprint. It recommends one step.
- Type **`/review-pr 14`** to review PR #14. Claude explains it in plain language, runs the tests, checks it against
  the issue, and posts your approval only after you say yes. If GitHub refuses the approval from the cloud, Claude
  tells you which buttons to click on GitHub instead.

## Working on your own laptop (optional, more setup)

Only needed if you want to run the app on your own computer (e.g. to click around before a PR is merged).
Most teammates should use the cloud instead.

### One-time laptop setup

About 15–20 minutes, once per laptop. Claude does almost all of it for you.

**How syncing works:** your laptop holds its own full copy of the project, and GitHub holds the shared
master copy. Nothing syncs automatically like Google Drive: your changes reach GitHub when Claude uploads
them (push, then a PR), and teammates' changes reach you when Claude downloads them (pull). `/next` downloads
the latest version at the start of every session.

1. **Accept the GitHub invite** to the `funky-lobsters` organization: open the email from GitHub, or go to
   https://github.com/orgs/funky-lobsters/invitation and click **Join funky-lobsters**.
2. **Make a folder for your projects.** Any name works (e.g. `Developer`, `Projects`, `MGT656`), but:
   - put it directly in your home folder (in Finder press **Cmd+Shift+H**, then **File → New Folder**)
   - **not** in iCloud Drive, Dropbox, OneDrive, Google Drive, or Desktop/Documents if iCloud syncs them
     (their syncing clashes with GitHub's and can corrupt files)
   - no spaces or special characters in the name (`MGT656`, not `MGT 656 Project!`)
3. In the **Claude app → Code tab**, open that folder and paste:
   > *Clone https://github.com/funky-lobsters/startup-job-tracker into this folder with git, then do the one-time setup from its README.*

   Claude downloads the project, installs everything it needs (no admin password) and logs you into GitHub.
   Along the way:
   - when Claude asks to run a command, click **Allow**
   - if a Mac popup asks to install "command line developer tools", click **Install** and wait (5–10 minutes),
     then tell Claude it's done
   - when GitHub opens in your browser, enter the code Claude shows you and click **Authorize**
4. **When it's done, start a new Claude Code session and choose the `startup-job-tracker` folder** (inside the
   folder you made). Always use that folder from now on when working locally.
5. **Ask Ben privately for the Neon dev database address** (never in a group chat). Claude will show you where
   to paste it in your `.env` file.

<details><summary>For Claude: how to do the one-time setup</summary>

Do these in order, explaining each step in one plain sentence. The teammate has never used a terminal.

1. **Git:** `xcode-select -p` succeeds if it's installed. If not, run `xcode-select --install`, tell the teammate
   to click **Install** in the popup, and wait until they say it finished.
2. **GitHub CLI (`gh`)**, without admin rights or Homebrew, if `command -v gh` finds nothing: download the official
   release zip for this Mac (`uname -m`: `arm64` → `macOS_arm64`, `x86_64` → `macOS_amd64`) from
   https://github.com/cli/cli/releases/latest into a temporary folder, unzip it, copy `bin/gh` to `~/.local/bin/`,
   and make sure `~/.local/bin` is on `PATH` in `~/.zshrc`.
3. **Log in to GitHub:** `gh auth login --hostname github.com --git-protocol https --web`. It needs a real terminal,
   so run it where the teammate can see it (e.g. the app's Terminal panel) and walk them through it.
   Then `gh auth setup-git` so pushing works. Check with `gh auth status`.
4. Follow "Run it on your computer" below (create `.env`; leave `DATABASE_URL` for the teammate to paste).
5. Run `python manage.py test` to confirm it works, then tell them to reopen Claude in the `startup-job-tracker` folder.
</details>

### Run it on your computer (first time)

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
