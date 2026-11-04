# MGT 656 Team Project: Final Submission Spec

Context file for Claude Code. Source: https://www.656.mba/#/assignments/project-final-submission

Build a web app in a team the way professional teams do: batteries-included framework, relational DB, tests, staging and production environments, and a backlog that drives the work. AI agents write most of the code. The job is to direct them well (clear stories, careful review, an app the team understands). 60 points total. Everyone on a team gets the same grade.

## Deadlines (all 11:59pm ET)

- Wed Oct 28: Team selection
- Mon Nov 2: Proposal
- Wed Nov 11: Sprint 1 (walking skeleton)
- Wed Nov 18: Sprint 2
- Wed Dec 2: Sprint 3
- Fri Dec 11: Sprint 4, then the A/B run on production
- Fri Dec 18: Final submission

## Required (all of these)

1. **Framework:** Django, Rails, Laravel, Phoenix, or AdonisJS (Phoenix/AdonisJS: agents are less reliable).
2. **Database:** PostgreSQL or MySQL. Staging and production each have their own DB.
3. **User accounts** via the framework's standard auth (Kyle may waive if accounts make no sense).
4. **An AI feature.** Call the LLM through OpenRouter (https://openrouter.ai) from the server, never from browser JS.
5. **Automated tests.** Must not call the real LLM or other external services. Mock them.
6. **Staging and production** environments, both public.
7. **12-factor basics** (https://12factor.net):
   - config and secrets in env vars, never in git
   - DB attached via a URL in an env var
   - logs to stdout
   - no uploads or lasting data on local disk (use DB or object storage)
   - app listens on `$PORT`
   - schema changes via migrations
8. **Seed command** that creates demo data and the grader accounts. Idempotent (safe to run repeatedly). Run it after any DB reset.
9. **Usable interface** on phones and desktops (a CSS framework makes this easy).
10. **The A/B test page** (see below).

## Technical challenge (20 pts)

Build about 3 items done well: tested, working in the deployed app, handling failure. Three solid items beat eight shallow ones. Pick from this list or propose your own.

- **Delivery:** CI (tests + lint on every PR, merge blocked on failure); CD (merge to `main` auto-deploys staging, deliberate step to promote to production); Docker Compose dev setup; error tracking and a health-check endpoint.
- **Backend:** background job queue with separate worker; scheduled jobs; documented JSON API with token auth; importing external data; roles and permissions beyond logged-in or not; full-text search; file uploads to object storage; email notifications; webhooks; social login.
- **AI:** retrieval over own data with pgvector; structured LLM output that drives app behavior; an evaluation set run like tests; per-user AI usage limits.
- **Frontend and quality:** live updates without full reloads (Hotwire, LiveView, Livewire, htmx); end-to-end browser tests (Playwright); accessibility checks in CI; measured performance work (indexes, N+1 fixes, caching).

## How we work

- **Project board:** one GitHub Project for the team, linked to the repo. Add an **Iteration** field with one iteration per sprint, dated to match course deadlines. Turn on the built-in workflows that add new issues and move finished items to Done.
- **Backlog:** issues labeled `user story`, each with "As a ..., I want ..., so that ..." and acceptance criteria. Write criteria precisely enough to hand to an AI agent (they are its spec). Break big stories into **sub-issues**.
- **Sprints:** at sprint start, put committed stories in that iteration. Unfinished stories roll to the next iteration, never deleted.
- **Milestones** (optional): product goals that span sprints (e.g. "MVP", "launch"), not sprints.
- **Branches and PRs:** work on branches. Each PR says `Closes #<issue>`, is reviewed by a teammate before merging, and its description says what the agent produced and what the team changed or rejected.
- No story points, velocity, or burndown charts.

## `docs/mgt656/` folder (graded from `main` at each deadline)

Never put passwords or keys in the repo.

```
docs/mgt656/
  team.yaml          # who you are and what you built with
  technical.md       # technical-challenge items + testing strategy
  sprints/
    sprint-1.md      # one short report per sprint
    sprint-2.md
    sprint-3.md
    sprint-4.md
    img/             # screenshots; link to videos instead of committing them
  retrospective.md   # final: what you learned
```

`team.yaml`:

```yaml
framework: django        # django | rails | laravel | phoenix | adonisjs
database: postgres       # postgres | mysql
members:
  - nickname: bald-chicken    # course nickname
    github: kljensen          # GitHub username
```

**Sprint report** (about half a page):
- sprint goal
- what shipped, with links to closed issues and merged PRs
- what works on staging now
- working with agents: one concrete thing that worked or didn't, and what you changed
- backlog changes for next sprint

**`technical.md`:** for each technical-challenge item, a line or two on what it is, main file paths and PRs, and how to see it working. Then the testing strategy: what is tested at which level, what is mocked, what is not tested and why.

**`retrospective.md`** (about half a page): what went well, what to do differently, how the way of working with AI agents changed over the project.

## A/B test page

Serve a public page at `/` + first 7 chars of the SHA-1 of the **team** nickname (not a member's), exactly as shown on the course site.

```sh
printf %s bright-forest | shasum      # 211c220... so the page is /211c220
```

Do not use `echo` (hashes a trailing newline, gives `1ea0cdf`). Verify the method on `bright-forest` first.

**Our team nickname: `funky-lobsters` → page at `/26fd193`, stats at `/26fd193/stats`.** (Spelling confirmed from the course site.)

The page must:

- return 200 without login and with no pop-up in the way
- list the team members' nicknames
- contain exactly one `<button id="abtest">` whose text (trimmed) is exactly `kudos` or `thanks` (lowercase)
- give each new visitor `kudos` or `thanks` at random 50/50 and keep showing the same one (session or cookie). Text must be in server-rendered HTML, not set by JavaScript
- count one **impression** per visitor, the first time they see the page (reloads and redirects do not count again)
- send a request to the server on button click (a plain `<form method="post">` is simplest) and count at most one **click** per visitor. If the click redirects back, it must not count a new impression or change the variant
- store impressions and clicks in the DB, with timestamps

Also serve public `/<hash>/stats` returning JSON with a `preferred` key (`"kudos"` or `"thanks"`): the variant with the higher click rate (clicks / impressions), computed live from the DB. Extra keys are fine:

```json
{"preferred": "kudos", "kudos": {"impressions": 212, "clicks": 63}, "thanks": {"impressions": 207, "clicks": 21}}
```

After Sprint 4, a Playwright bot visits production during an announced window of a few hours. Each visit is a new visitor. It clicks one variant more often than the other, with a fixed preference. Free hosting that sleeps is fine (the bot wakes the app first). There is no practice run, so test the counting yourself. **Your own test visits count, so delete them before the run.** Kyle reads `preferred` from `/stats` right after the run, and that value is graded.

## Hosting

Free tiers can work. Suggestions:
- Render for the app plus Neon for Postgres (course default)
- Railway
- Fly.io plus Neon

Check current limits first. As of Oct 2026, Render's free Postgres is deleted after 30 days (use Neon), and background workers usually cost a few dollars a month.

## Submitting

Final submission fields (team assignment):

- **Team GitHub repo URL** (`https://github.com/...`, repo with app code and `docs/mgt656/`)
- **Staging app URL** (public)
- **Production app URL** (public, the A/B run goes here)
- **Notes: how to use your app**

Notes format:

```
Access:
https://bright-forest-staging.onrender.com/login
admin: admin@example.com / correct-horse-battery
member: member@example.com / staple-paper-lamp

Notes:
CSV export is half-done; skip it this sprint.
```

Grader accounts must use fake data, passwords used nowhere else, and no 2FA or email verification. Create them in the seed command. Sprint reports go in the repo, not in the notes. If the app or a grader account is broken at grading, the team gets 24 hours to fix it.

## Grading (60 pts)

- 20: Working app and required items
- 20: Technical challenge
- 10: A/B test (working page and a correct `preferred` value after the run)
- 10: Process and docs (backlog, PRs, `technical.md`, retrospective)

Sprints are graded separately: Sprint 1 = 10 pts, Sprints 2 to 4 = 15 pts each.

## Instructions for Claude Code

- Treat the Required list and A/B spec as hard acceptance criteria. Verify each against the running app, not just the code.
- Never commit secrets. All config via env vars. Provide `.env.example` only.
- Mock the LLM (OpenRouter) and any external service in tests.
- Keep the seed command idempotent and make it create the grader accounts.
- For every change: work on a branch, open a PR with `Closes #<issue>`, and note in the PR what the agent produced versus what the team changed.
- Before the A/B run: compute the hash with `printf %s`, test impression and click counting end to end, then purge test data from production.
