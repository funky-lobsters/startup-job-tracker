---
name: next
description: Use when a teammate starts a session or asks "what's next", "what should I do", "next phase" or "anything waiting for me". Checks GitHub for PRs waiting for their review, their own PRs, open user stories and missing sprint items, then recommends one next step.
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
- If `gh auth status` fails, stop and walk them through `gh auth login` (see README.md, "One-time setup").

## 2. Collect what's open

```bash
gh api user --jq .login                                   # who am I
gh pr list --state open --json number,title,author,reviewDecision,isDraft,url,createdAt
gh issue list --state open --label "user story" --json number,title,assignees,url
gh issue list --state open --assignee @me --json number,title,url
```

Sort into:
1. **PRs waiting for my review**: open, not draft, author is not me, `reviewDecision` is not `APPROVED`. Oldest first.
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
- **Merge my approved PR** → `gh pr merge <n> --merge --delete-branch`, then `git switch main && git pull --ff-only`.
- **Start an issue** → `gh issue edit <n> --add-assignee @me`; `git switch main && git pull --ff-only`;
  `git switch -c story/<n>-<short-slug>`; read the issue's acceptance criteria; explain the plan in plain language; then build it.
  The PR must say `Closes #<n>` and fill in the PR template (including "What a reviewer should click to see it").

Never merge, approve, assign or push without the teammate saying yes in this conversation.
