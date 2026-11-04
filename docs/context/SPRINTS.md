# MGT 656 Team Project: Sprints 1 to 4

Companion to `PROJECT_SPEC.md`. Sources:
- https://www.656.mba/#/assignments/project-sprint-1
- https://www.656.mba/#/assignments/project-sprint-2
- https://www.656.mba/#/assignments/project-sprint-3
- https://www.656.mba/#/assignments/project-sprint-4

Full requirements, folder layout, and report format are in `PROJECT_SPEC.md`. All deadlines are 11:59pm ET. Each sprint's report lives in the repo at `docs/mgt656/sprints/sprint-N.md` and must be on `main` by the deadline.

## Sprint report format (every sprint, about half a page)

- sprint goal
- what shipped, with links to closed issues and merged PRs
- what works on staging now
- working with agents: one concrete thing that worked or didn't, and what changed
- backlog changes for next sprint

## Sprint 1: Walking skeleton (10 pts)

**Due: Wed Nov 11, 11:59pm ET**

Goal: get the whole pipeline working end to end before building real features.

Done when:
- [ ] Repo has a framework app (Django, Rails, Laravel, Phoenix, or AdonisJS) with user accounts (unless Kyle waived them)
- [ ] App is connected to Postgres or MySQL
- [ ] App is deployed to **staging**
- [ ] Seed command creates the grader accounts
- [ ] A/B test page (`/<hash>`) and `/<hash>/stats` work on staging
- [ ] Backlog has its first user stories (`user story` label, "As a ..., I want ..., so that ...", acceptance criteria)
- [ ] Team GitHub Project exists, linked to the repo, with iterations set up for all four sprints
- [ ] `docs/mgt656/team.yaml` is on `main`
- [ ] `docs/mgt656/sprints/sprint-1.md` is on `main`

Production can wait until Sprint 2.

Graded on: the skeleton working on staging, the report, and the backlog.

Submit: repo URL, staging URL, notes (login page plus username and password per user type).

## Sprint 2: Development (15 pts)

**Due: Wed Nov 18, 11:59pm ET**

Done when:
- [ ] **Production** is deployed, with its own database
- [ ] First user stories are shipped through reviewed pull requests (`Closes #<issue>`, teammate review, PR description says what the agent produced and what the team changed or rejected)
- [ ] AI feature is started (OpenRouter, called from the server only)
- [ ] `docs/mgt656/sprints/sprint-2.md` is on `main`

Graded on: what shipped, the report, and how you worked.

Submit: repo URL, staging URL, **production URL**, notes.

## Sprint 3: MVP development (15 pts)

**Due: Wed Dec 2, 11:59pm ET**

Done when:
- [ ] Core features and the AI feature work on staging
- [ ] Technical-challenge items are started and listed in `docs/mgt656/technical.md`
- [ ] `docs/mgt656/sprints/sprint-3.md` is on `main`

Graded on: what shipped, the report, and how you worked.

Submit: repo URL, staging URL, production URL, notes.

## Sprint 4: Final sprint (15 pts)

**Due: Fri Dec 11, 11:59pm ET**

Done when:
- [ ] Features and technical-challenge items are finished and on **production**
- [ ] `docs/mgt656/technical.md` is complete (per item: what it is, main file paths and PRs, how to see it working; then testing strategy)
- [ ] `docs/mgt656/sprints/sprint-4.md` is on `main`

After the deadline, the bot makes the **A/B run against production** during an announced window. Keep production up and unchanged through that window. Before the run, delete your own test impressions and clicks from the production DB.

Graded on: what shipped, the report, and how you worked.

Submit: repo URL, staging URL, production URL, notes.

Final submission (Fri Dec 18) also needs `docs/mgt656/retrospective.md`. See `PROJECT_SPEC.md`.

## Submission notes format (all sprints)

```
Access:
https://bright-forest-staging.onrender.com/login
admin: admin@example.com / correct-horse-battery
member: member@example.com / staple-paper-lamp

Notes:
CSV export is half-done; skip it this sprint.
```

Grader accounts must use fake data, passwords used nowhere else, and no 2FA or email verification. Create them in the seed command. The sprint report goes in the repo, not in the notes. If the app or a grader account is broken at grading, the team gets 24 hours to fix it.

## Sprint rules (from the project page)

- At sprint start, put committed stories in that iteration on the GitHub Project. Unfinished stories roll to the next iteration, never deleted.
- Work on branches. Every PR says `Closes #<issue>` and gets a teammate review before merging.
- No story points, velocity, or burndown charts.
- Never put passwords or keys in the repo.

## Instructions for Claude Code

- Check the current sprint's "Done when" list against the running staging app, not just the code, before calling a sprint finished.
- Draft `sprint-N.md` from the closed issues and merged PRs for that iteration. Leave the "working with agents" item for the team to fill in with a real example.
- Keep the seed command idempotent and rerun it after any DB reset.
