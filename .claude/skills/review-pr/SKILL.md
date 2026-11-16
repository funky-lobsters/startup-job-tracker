---
name: review-pr
description: Use when a teammate wants a pull request reviewed (their own or someone else's), e.g. "review PR 14", "walk me through the PR", or after /next suggests a review. A separate agent that did not write the code reviews it (tests, acceptance criteria, secrets, team rules) and reports in plain language. Nothing is posted and nothing is merged until the teammate says yes.
---

# /review-pr: a separate agent reviews the PR, the teammate confirms

Team rule (CLAUDE.md, "Working rules"): every PR is reviewed by a **separate agent** that did not write the code, and a
**human confirms** before anything happens. The teammate doesn't read code; give them an honest summary so they can decide
in a few minutes. **Never post a review or merge without an explicit yes in this conversation.**

Anyone can run this, including the PR's author. No teammate approval is required by GitHub, but `main` only accepts a
merge when the automatic checks (`tests`, `secrets`) are green.

## 1. Pick the PR

Use only `gh api` (GitHub's REST API): it works on laptops and in cloud sessions, where `gh pr` / `gh issue` are blocked.

```bash
R=repos/funky-lobsters/startup-job-tracker
gh api user --jq .login
gh api "$R/pulls?state=open" --jq '.[] | {number, title, author: .user.login}'   # if no number was given: ask which one
gh api "$R/pulls/<n>" --jq '{number, title, author: .user.login, branch: .head.ref, sha: .head.sha, url: .html_url}'
```

## 2. Hand the review to a separate agent

Start a **fresh subagent** (Agent tool, `general-purpose`) so the review isn't anchored on whoever wrote the code,
including you in this session. Give it the PR number and this brief, and tell it explicitly: **read-only on GitHub and on
the teammate's working copy. Don't post, approve, comment, merge or push; only the temporary review folder from step 3 may
be created. Return the report as text.**

The subagent's brief:
1. Read the PR (`gh api $R/pulls/<n>`), its diff (`gh api $R/pulls/<n> -H "Accept: application/vnd.github.diff"`) and
   the linked issue(s) from the `Closes #<n>` lines (`gh api $R/issues/<issue> --jq '{title, body}'`), especially the
   **acceptance criteria**.
2. Read the live course requirements (`curl -fsSL https://raw.githubusercontent.com/yale-mgt-656-fall-2026/project-requirements/main/README.md`) and `CLAUDE.md`.
3. Run the tests on the PR's code in a temporary folder, without disturbing the teammate's working copy. Run it as
   **one** shell command from the repo folder (the working directory resets between commands):
   ```bash
   REPO=$(git rev-parse --show-toplevel); W="$REPO/../review-<n>"
   git -C "$REPO" worktree remove --force "$W" 2>/dev/null
   git -C "$REPO" fetch -q origin <branch> && git -C "$REPO" worktree add -q "$W" FETCH_HEAD \
     && (cd "$W" && bash scripts/cloud-setup.sh >/dev/null && .venv/bin/python manage.py test 2>&1 | tail -5)
   git -C "$REPO" worktree remove --force "$W"
   ```
   (`scripts/cloud-setup.sh` creates `.venv` and a local `.env` without real secrets. On a laptop without it:
   `python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt`.)
4. Check the GitHub checks: `gh api $R/commits/<sha>/check-runs --jq '.check_runs[] | {name, conclusion}'`.
5. Check the team rules:
   - no secrets in the diff (API keys, passwords, connection strings, `.env` files)
   - model changes come with a migration file
   - tests don't call OpenRouter or other external services for real (they're mocked)
   - the PR says `Closes #<issue>` and fills in "what the agent produced / what the team changed"
   - nothing unrelated to the story snuck in
6. Return: a verdict (**approve** or **request changes**), each acceptance criterion ✅/⚠️/❌, test result, rule checks,
   and only *verified* problems (not hunches), with why they matter.

## 3. Report to the teammate in plain language

Translate the subagent's report. No jargon; define any technical term you must use.

```
PR #14 "Job feed page" by sara-k  (closes #9), reviewed by a separate agent

What it does:   Adds a page at /jobs that lists startup jobs, newest first...
Acceptance criteria:
  ✅ Logged-in users see a list of jobs
  ✅ Works on phone (uses the shared layout)
  ⚠️ "Filter by role": not included. The PR says it's a follow-up
Tests:          ✅ 18 passed   GitHub checks: ✅ tests ✅ secrets
Rule checks:    ✅ no secrets  ✅ migration included  ✅ external calls mocked
Risks:          none found / <plain-language risk>

Try it yourself: on staging after merge: <exact clicks>

Agent's verdict: approve
Post this review and merge? (yes / post the review only / no)
```

If the verdict is **request changes**, end instead with: *"Post this review so the author knows what to fix? (yes / no)
Or shall I fix it now?"*. Never offer to merge a PR with a "request changes" verdict.

Be honest. If something is missing, a check is red or tests fail, say so plainly and suggest "request changes".

## 4. Act only after an explicit yes

The review body always starts with the verdict, so `/next` can recognise it, and mentions it was a separate agent.

- **Approve:**
  - On a teammate's PR: `gh api -X POST $R/pulls/<n>/reviews -f event=APPROVE -f body="Agent review: approve. <1–2 lines>. Reviewed by a separate agent, confirmed by <name of the person running /review-pr>."`
  - On your **own** PR (GitHub doesn't allow approving your own PR): same call with `-f event=COMMENT` and the same body.
  - Then, only if they said yes to merging and the checks are green: `gh api -X PUT $R/pulls/<n>/merge -f merge_method=merge`,
    then delete the branch with `gh api -X DELETE $R/git/refs/heads/<branch>`.
- **Request changes:** on a teammate's PR `-f event=REQUEST_CHANGES`, on your own PR `-f event=COMMENT`; body starts with
  `Agent review: changes needed.` and says plainly what's missing. Then offer to fix it.
- **If GitHub refuses** (this can happen in cloud sessions, e.g. deleting a branch), give the teammate the PR link, the exact
  review text to paste (starting with `Agent review: approve.` or `Agent review: changes needed.`, so `/next` recognises it)
  and the clicks: **Files changed** tab → **Review changes** (or **Submit review**) → paste the text → pick **Approve**
  (or **Comment** on your own PR) → **Submit review**; then on the **Conversation** tab **Merge pull request** →
  **Confirm merge** → **Delete branch**.

Afterwards tell them where they are, then run `git switch main && git pull --ff-only` (or, if they're on a work branch, just `git fetch`).
