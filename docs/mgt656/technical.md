# Technical challenge

Team funky-lobsters · Staging: https://funky-lobsters-staging.onrender.com · Production: https://funky-lobsters.onrender.com

Items are grouped by the categories in Kyle's requirements. This file grows each sprint (Sprint 4: complete).

## Delivery

### 1. CI: tests and secret scanning on every pull request, merge blocked on failure
- **What:** GitHub Actions runs our Django tests and [Gitleaks](https://github.com/gitleaks/gitleaks) (scans the whole git
  history for leaked API keys or passwords) on every pull request and every push to `main`. Branch protection on `main`
  requires both checks (`tests`, `secrets`) to pass before a PR can be merged.
- **Files / PRs:** `.github/workflows/checks.yml`, `.gitleaks.toml`; issue #42, PR #47.
- **See it working:** open any pull request and scroll to the bottom: "Checks / tests" and "Checks / secrets" with green ticks.
  The Merge button stays disabled until both are green.

### 2. CD: staging deploys automatically, production is promoted on purpose
- **What:** two Render services from one `render.yaml` blueprint, each with its own Neon Postgres database. Every merge to
  `main` redeploys staging automatically; production only changes when someone clicks **Manual Deploy** in Render, after
  checking staging. Each start runs migrations and the idempotent seed command.
- **Files / PRs:** `render.yaml`, README "Deploy"; issue #41, PRs #48 and #50.
- **See it working:** compare the `commit` on staging's and production's `/health/` (item 3): after a merge, staging shows
  the new commit and production keeps the old one until it is promoted.

### 3. Health check: which version is live, and is the database reachable?
- **What:** a public `/health/` page returning JSON like
  `{"status": "ok", "commit": "8610813", "service": "funky-lobsters", "database": "ok"}`.
  `commit` is the short id of the running code (from Render's `RENDER_GIT_COMMIT`; `unknown` locally), `service` is the
  Render service name (`local` locally). If the database can't be reached it answers **503** with `"database": "error"`
  instead of crashing, and logs only the kind of error (never connection details). No login needed, no secrets shown,
  never cached.
- **Files / PRs:** `core/views.py` (`health`), `config/urls.py`, tests in `core/tests.py`; issue #43.
- **See it working:** https://funky-lobsters-staging.onrender.com/health/ and https://funky-lobsters.onrender.com/health/.
  The first visit after a quiet period can take up to a minute (free Render sites sleep).

## AI

### 4. Structured LLM output that drives app behaviour (in progress)
- **What:** "Recommended for you" sends the user's profile and the open jobs to an LLM through OpenRouter (server-side only)
  and asks for JSON that must follow a schema (`job_id` + one-sentence `reason`). The app checks every answer against the
  database: unknown or duplicate job ids are dropped, at most 5 are kept, and any failure (no key, timeout, bad JSON)
  shows a friendly message instead of an error page.
- **Files / PRs:** `recommendations/ai.py`, `recommendations/views.py`, `templates/recommendations/list.html`;
  issues #29 and #32, PR #40.
- **See it working:** log in on staging, fill in your profile, click **For you**.

## Testing strategy

- **Where:** Django's test runner (`python manage.py test`), run by CI on every pull request. Tests use a throwaway SQLite
  database, so they need no internet and no real database.
- **What we test:**
  - Each page's behaviour through Django's test client: status codes, what the page shows, login requirements.
  - The graded A/B page in detail: impressions and clicks counted once per visitor, 50/50 assignment, traffic source taken
    from the first visit's `Referer`, and the `/stats` JSON including `preferred`.
  - The AI feature's parsing and safety rules: unknown, duplicate or extra job ids dropped; bad JSON and timeouts handled.
  - The health check's ok and database-error cases (the database error is simulated).
- **What we mock:** OpenRouter. Tests replace the network call with a fake answer, and the settings blank the API key during
  tests, so a test can never reach the real AI. No test sends email or calls other outside services.
- **What we don't test automatically, and why:** the real OpenRouter model's answers (they vary and cost money; we check them
  by hand on staging), Render and Neon themselves (checked after each deploy through `/health/` and by clicking through
  staging), and the look of pages in a real browser (checked by hand on phone and desktop).
