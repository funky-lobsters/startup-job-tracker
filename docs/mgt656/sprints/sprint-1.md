# Sprint 1: Walking skeleton

**Team:** funky-lobsters · **Dates:** Nov 5 to Nov 11, 2026 · **Staging:** https://funky-lobsters-staging.onrender.com

## Sprint goal

Get the whole pipeline working end to end before building features: a Django app with email login,
connected to Postgres, deployed to staging, with grader accounts, the A/B test page, a project board
and a first backlog of user stories.

## What shipped

- **Walking skeleton:** Django app with email + password accounts (sign up, log in, log out), tests,
  and the Render deployment config (commit `79387d4`).
- **A/B test page and grader accounts:** `/26fd193` and `/26fd193/stats`, including traffic source
  tracking from the `Referer` header, plus an idempotent `python manage.py seed` command that creates
  the grader accounts. [#9](https://github.com/funky-lobsters/startup-job-tracker/issues/9),
  [#10](https://github.com/funky-lobsters/startup-job-tracker/issues/10),
  PR [#11](https://github.com/funky-lobsters/startup-job-tracker/pull/11); spec
  [#7](https://github.com/funky-lobsters/startup-job-tracker/issues/7) / PR
  [#8](https://github.com/funky-lobsters/startup-job-tracker/pull/8).
- **Staging on Render + Neon Postgres:**
  [#20](https://github.com/funky-lobsters/startup-job-tracker/issues/20). Redeploys on every merge to `main`.
- **Project board** with an iteration per sprint (Sprint 1 to 4, ending on the course deadlines),
  linked to the repo, with auto add and auto close workflows on:
  [#22](https://github.com/funky-lobsters/startup-job-tracker/issues/22).
- **First backlog:** 6 user stories with acceptance criteria, the two big ones split into sub-issues:
  [#25](https://github.com/funky-lobsters/startup-job-tracker/issues/25) browse jobs,
  [#26](https://github.com/funky-lobsters/startup-job-tracker/issues/26) filter jobs,
  [#27](https://github.com/funky-lobsters/startup-job-tracker/issues/27) company pages,
  [#28](https://github.com/funky-lobsters/startup-job-tracker/issues/28) application tracker,
  [#29](https://github.com/funky-lobsters/startup-job-tracker/issues/29) AI recommendations
  (sub-issues [#31](https://github.com/funky-lobsters/startup-job-tracker/issues/31),
  [#32](https://github.com/funky-lobsters/startup-job-tracker/issues/32)),
  [#30](https://github.com/funky-lobsters/startup-job-tracker/issues/30) import real startups and jobs
  (sub-issues [#33](https://github.com/funky-lobsters/startup-job-tracker/issues/33),
  [#34](https://github.com/funky-lobsters/startup-job-tracker/issues/34)). Closes
  [#21](https://github.com/funky-lobsters/startup-job-tracker/issues/21).
- **Team file:** `docs/mgt656/team.yaml` with all 5 members
  ([#12](https://github.com/funky-lobsters/startup-job-tracker/issues/12), PRs
  [#13](https://github.com/funky-lobsters/startup-job-tracker/pull/13),
  [#18](https://github.com/funky-lobsters/startup-job-tracker/pull/18),
  [#19](https://github.com/funky-lobsters/startup-job-tracker/pull/19) and this PR).
- **Team workflow for non-coders:** `/next` and `/review-pr` Claude Code commands, cloud mode setup,
  plain-language README, and a notes workflow for shared memory
  ([#1](https://github.com/funky-lobsters/startup-job-tracker/issues/1),
  [#3](https://github.com/funky-lobsters/startup-job-tracker/issues/3),
  [#5](https://github.com/funky-lobsters/startup-job-tracker/issues/5),
  [#14](https://github.com/funky-lobsters/startup-job-tracker/issues/14),
  [#16](https://github.com/funky-lobsters/startup-job-tracker/issues/16)).

## What works on staging now

- Sign up, log in at `/login/` and log out (grader accounts: see the Canvas submission notes).
- `/26fd193` shows the team's nicknames and one A/B button variant; clicks and the visitor's traffic
  source are recorded.
- `/26fd193/stats` returns JSON with the preferred variant, counts per variant and the traffic source breakdown.

## Working with agents

<!-- TEAM: replace this with one real example from this sprint: something the agent did well or got
wrong, and what you changed because of it (2 to 4 sentences). -->
TODO (team)

## Backlog changes for next sprint

- Following Kyle's feedback, the backlog covers only the job seeker side (aggregating startup jobs
  for MBA students); the founder / hiring side is deprioritized.
- Sprint 2 plan: production deploy with its own database, then
  [#25](https://github.com/funky-lobsters/startup-job-tracker/issues/25) browse jobs,
  [#26](https://github.com/funky-lobsters/startup-job-tracker/issues/26) filters, and start the AI feature with
  [#31](https://github.com/funky-lobsters/startup-job-tracker/issues/31) profile.
- Open question for Kyle: what startup data we can use (Crunchbase export, crawling career pages) before building
  [#30](https://github.com/funky-lobsters/startup-job-tracker/issues/30).
