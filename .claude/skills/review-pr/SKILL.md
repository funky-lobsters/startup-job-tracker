---
name: review-pr
description: Use when a teammate wants a pull request reviewed, including their own, e.g. "review PR 14", "walk me through the PR", or after /next suggests a review. Acts as the agent reviewer, explains the PR in plain language, runs the tests, checks it against the issue's acceptance criteria and for secrets, and posts the review on GitHub only after the teammate says yes.
---

# /review-pr: the agent review of a PR

Since Kyle's 2026-11-11 change (addendum in `docs/context/course-requirements.md`), **you are the reviewer**, and your
review counts. Authors run this on their own PRs, so nobody waits for a teammate. That only works if the review is
real: check everything below, and if something fails, say so and recommend changes. Never pass a PR to be nice.

If you wrote this PR's code in this same session, say so and suggest running `/review-pr <n>` in a new session for a
fresh look. Continue only if the teammate wants to.

The review is posted from the teammate's GitHub account, only after they say yes.

## 1. Pick the PR

Use only `gh api` (GitHub's REST API): it works on laptops and in cloud sessions, where `gh pr` / `gh issue` are blocked.

```bash
R=repos/funky-lobsters/startup-job-tracker
gh api user --jq .login
gh api "$R/pulls?state=open" --jq '.[] | {number, title, author: .user.login}'   # if no number was given: ask which one
gh api "$R/pulls/<n>" --jq '{number, title, body, author: .user.login, branch: .head.ref, additions, deletions, url: .html_url}'
gh api "$R/pulls/<n>/files" --jq '.[] | {filename, status}'
```

The linked issues are the `Closes #<n>` lines in the PR body.

If the author is the person running this, that's fine: it's an agent review. GitHub doesn't allow **Approve** on your own PR,
so in step 4 post it as a comment review (`event=COMMENT`) instead.

## 2. Gather the facts

1. Read the linked issue(s) (`gh api $R/issues/<issue> --jq '{title, body}'`), especially the **acceptance criteria**.
2. Read the diff: `gh api $R/pulls/<n> -H "Accept: application/vnd.github.diff"`.
3. Check the code out and run the tests:
   ```bash
   git status --porcelain        # if not empty: ask before continuing (offer `git stash`)
   git fetch -q origin <branch> && git switch --track origin/<branch>   # or `git switch <branch>` if it exists
   bash scripts/cloud-setup.sh          # cloud sessions only; on a laptop: source .venv/bin/activate && pip install -q -r requirements.txt
   .venv/bin/python manage.py test
   ```
4. Check these rules from CLAUDE.md, quickly:
   - no secrets in the diff (API keys, passwords, connection strings, `.env` files)
   - model changes come with a migration file
   - tests don't call OpenRouter or other external services for real (they're mocked)
   - the PR says `Closes #<issue>` and fills in "what the agent produced / what the team changed"
   - nothing unrelated to the story snuck in

## 3. Report in plain language

```
PR #14 "Job feed page" by sara-k  (closes #9)

What it does:   Adds a page at /jobs that lists startup jobs, newest first...
Acceptance criteria:
  ✅ Logged-in users see a list of jobs
  ✅ Works on phone (uses the shared layout)
  ⚠️ "Filter by role": not included. The PR says it's a follow-up
Tests:          ✅ 18 passed
Rule checks:    ✅ no secrets  ✅ migration included  ✅ external calls mocked
Risks:          none found / <plain-language risk>

Try it yourself: <exact steps, e.g. "run the app, go to http://127.0.0.1:8000/jobs, log in as ...">
                 or on staging after merge.

Verdict:        pass (or: changes needed because ...)
```

Be honest. If something is missing or tests fail, say so plainly and suggest "request changes" with a short reason.

## 4. Act on their decision (only after an explicit yes)

The review body always starts with `Agent review: pass` or `Agent review: changes needed`, then the report from step 3
(criteria, tests, rule checks, risks), so graders can see the check was real.

- **Pass:** `gh api -X POST $R/pulls/<n>/reviews -f event=<APPROVE, or COMMENT on your own PR> -f body="Agent review: pass ..."`
  Then ask whether to merge now: `gh api -X PUT $R/pulls/<n>/merge -f merge_method=merge`, then delete the branch with
  `gh api -X DELETE $R/git/refs/heads/<branch>`.
- **Changes needed:** same call with `event=REQUEST_CHANGES` (or `COMMENT` on your own PR) and `body="Agent review: changes needed ..."`.
  Don't merge. Offer to fix it, then review again.
- **If GitHub refuses** (this can happen in cloud sessions), give the reviewer the PR link and the clicks:
  **Files changed** tab → **Review changes** (or **Submit review**) → pick **Approve** (or **Comment** on your own PR), paste the review text → **Submit review**;
  then on the **Conversation** tab **Merge pull request** → **Confirm merge** → **Delete branch**.

Afterwards always go back: `git switch main && git pull --ff-only`, and tell them where they are.
