---
name: next
description: Use automatically on the first message of every session (teammates may not know this command exists), and whenever a teammate asks "what's next", "what should I do", "next phase" or "anything waiting for me". Checks GitHub for PRs waiting for their review, their own PRs, open user stories and missing sprint items, then recommends one next step.
---

# /next: what should I work on?

The team is non-technical. Speak in plain language, keep the answer short, and end with ONE recommended next step plus a question.

## 1. Get up to date (silently, unless something is wrong)

```bash
git status -sb
git fetch -q origin
```

- If there are uncommitted changes, say so in one line and ask what to do before switching anything.
- If on `main` and behind `origin/main`, run `git pull --ff-only` and say "Updated your copy to the latest version."
- **Cloud session** (a fresh computer each time): run `bash scripts/cloud-setup.sh` once first (see CLAUDE.md, "Cloud sessions"). You're already up to date.
- **On a laptop:** if `gh api user` fails, walk them through `gh auth login` (see README.md, "Working on your own laptop").

## 2. Collect what's open

Use only `gh api` (GitHub's REST API). It works both on laptops and in cloud sessions, where `gh pr` / `gh issue` are blocked.

```bash
R=repos/funky-lobsters/startup-job-tracker
ME=$(gh api user --jq .login)                              # who am I
gh api "$R/pulls?state=open" --jq '.[] | {number, title, author: .user.login, draft, created_at, branch: .head.ref}'
gh api "$R/pulls/<n>/reviews" --jq '[.[] | {user: .user.login, state}]'     # for each open PR: its reviews
gh api "$R/issues?state=open&labels=user%20story" --jq '.[] | select(.pull_request | not) | {number, title, assignees: [.assignees[].login]}'
gh api "$R/issues?state=open&assignee=$ME" --jq '.[] | select(.pull_request | not) | {number, title}'
```

A PR counts as **approved** if its latest review from some teammate is `APPROVED`, and **changes requested** if the latest is `CHANGES_REQUESTED`.

Sort into:
1. **PRs waiting for my review**: open, not draft, author is not me, not approved. Oldest first.
2. **My own PRs**: `APPROVED` → offer to merge. `CHANGES_REQUESTED` → offer to fix. Otherwise "waiting for a reviewer; post the link in the team chat."
3. **My assigned issues** that have no open PR yet.
4. **Unassigned user stories** that anyone can pick up.

## 3. Check the current sprint

Read `docs/context/course-sprints.md` and pick the current sprint from today's date (the first sprint whose deadline hasn't passed).
For each "Done when" item, check quickly whether it looks done (e.g. the file exists on `main`, the page exists in `config/urls.py`, a seed command exists).
List only the items that look **missing**, with the days left until the deadline.

## 4. Report and recommend

Format (keep it under ~15 lines):

```
Sprint 2 — due Wed Nov 18 (5 days left)

Waiting for your review:   #14 Job feed page (by sara-k, 2 days old)
Your PRs:                  #12 Save job to tracker: approved, ready to merge
Your issues:               #9 Company profile page (no PR yet)
Up for grabs:              #15 Import startups from CSV, #16 ...
Missing for this sprint:   docs/mgt656/sprints/sprint-2.md

Recommended next: review #14. Reviews unblock teammates. Want me to walk you through it?
```

Priority for the recommendation: reviews waiting more than 1 day → merge my approved PRs → fix my PRs with requested changes → my assigned issues → a missing sprint item close to its deadline → pick up an unassigned story.

## 5. Acting on their answer

- **Review a PR** → follow the `review-pr` skill.
- **Merge my approved PR** → `gh api -X PUT $R/pulls/<n>/merge -f merge_method=merge`, then delete its branch with
  `gh api -X DELETE $R/git/refs/heads/<branch>`, then `git switch main && git pull --ff-only`.
  If the cloud refuses the merge, give the teammate the PR link and tell them to click **Merge pull request** → **Confirm merge**.
- **Start an issue** → `gh api -X POST $R/issues/<n>/assignees -f "assignees[]=$ME"`; `git switch main && git pull --ff-only`;
  `git switch -c story/<n>-<short-slug>`; read the issue's acceptance criteria; explain the plan in plain language; then build it.
  The PR must say `Closes #<n>` and fill in the PR template (including "What a reviewer should click to see it").

Never merge, approve, assign or push without the teammate saying yes in this conversation.
