---
name: review-pr
description: Use when a teammate wants to review a pull request, e.g. "review PR 14", "walk me through the PR", or after /next suggests a review. Explains the PR in plain language, runs the tests, checks it against the issue's acceptance criteria and for secrets, and approves on GitHub only after the teammate says yes.
---

# /review-pr: help a non-technical teammate review a PR

The reviewer does not read code. Your job is to give them an honest summary so they can decide in about 5 minutes.
The approval is theirs: it is posted from their GitHub account, and only after they say yes.

## 1. Pick the PR

If no number was given, list open PRs not authored by the reviewer (`gh pr list --state open`) and ask which one.

```bash
gh api user --jq .login
gh pr view <n> --json number,title,body,author,headRefName,files,additions,deletions,closingIssuesReferences,reviewDecision,url
```

If the author is the reviewer, stop: GitHub doesn't allow approving your own PR. Suggest asking a teammate.

## 2. Gather the facts

1. Read the linked issue(s) (`gh issue view <issue>`), especially the **acceptance criteria**.
2. Read the diff: `gh pr diff <n>`.
3. Check the code out and run the tests:
   ```bash
   git status --porcelain        # if not empty: ask before continuing (offer `git stash`)
   gh pr checkout <n>
   source .venv/bin/activate && pip install -q -r requirements.txt
   python manage.py test
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

- **Approve:** `gh pr review <n> --approve --body "<1–2 lines in the reviewer's words, e.g. 'Tried /jobs on my laptop, works. Reviewed with Claude Code.'>"`
  Then ask whether to merge now: `gh pr merge <n> --merge --delete-branch`.
- **Request changes:** `gh pr review <n> --request-changes --body "<what's missing, plainly>"`.
- **Comment only:** `gh pr review <n> --comment --body "..."`.

Afterwards always go back: `git switch main && git pull --ff-only`, and tell them where they are.
