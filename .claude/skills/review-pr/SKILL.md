---
name: review-pr
description: Use when a teammate wants to review a pull request, e.g. "review PR 14", "walk me through the PR", or after /next suggests a review. Explains the PR in plain language, runs the tests, checks it against the issue's acceptance criteria and for secrets, and approves on GitHub only after the teammate says yes.
---

# /review-pr: help a non-technical teammate review a PR

The reviewer does not read code. Your job is to give them an honest summary so they can decide in about 5 minutes.
The approval is theirs: it is posted from their GitHub account, and only after they say yes.

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

If the author is the reviewer, stop: GitHub doesn't allow approving your own PR. Suggest asking a teammate.

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

My suggestion: approve (or: ask for changes because ...)
```

Be honest. If something is missing or tests fail, say so plainly and suggest "request changes" with a short reason.

## 4. Act on their decision (only after an explicit yes)

- **Approve:** `gh api -X POST $R/pulls/<n>/reviews -f event=APPROVE -f body="<1–2 lines in the reviewer's words, e.g. 'Tried it on staging, works. Reviewed with Claude Code.'>"`
  Then ask whether to merge now: `gh api -X PUT $R/pulls/<n>/merge -f merge_method=merge`, then delete the branch with
  `gh api -X DELETE $R/git/refs/heads/<branch>`.
- **Request changes:** same review call with `-f event=REQUEST_CHANGES -f body="<what's missing, plainly>"`.
- **Comment only:** same review call with `-f event=COMMENT -f body="..."`.
- **If GitHub refuses** (this can happen in cloud sessions), give the reviewer the PR link and the clicks:
  **Files changed** tab → **Review changes** (or **Submit review**) → pick **Approve** → **Submit review**;
  then on the **Conversation** tab **Merge pull request** → **Confirm merge** → **Delete branch**.

Afterwards always go back: `git switch main && git pull --ff-only`, and tell them where they are.
