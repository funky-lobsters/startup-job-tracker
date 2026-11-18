# Sprint 2: Development

**Team:** funky-lobsters · **Dates:** Nov 12 to Nov 18, 2026 ·
**Staging:** https://funky-lobsters-staging.onrender.com · **Production:** https://funky-lobsters.onrender.com

## Sprint goal

Put the site live on production with its own database, ship the first job seeker stories through reviewed
pull requests, and start the AI feature (job recommendations through OpenRouter, called from the server only).

## What shipped

- **Production with its own database:** https://funky-lobsters.onrender.com on its own Neon Postgres database,
  promoted from staging with a deliberate Manual Deploy in Render
  ([#41](https://github.com/funky-lobsters/startup-job-tracker/issues/41), PR [#48](https://github.com/funky-lobsters/startup-job-tracker/pull/48)).
- **Browse startup jobs** at `/jobs/`, newest first, with demo data from the seed command
  ([#25](https://github.com/funky-lobsters/startup-job-tracker/issues/25), PR [#37](https://github.com/funky-lobsters/startup-job-tracker/pull/37)),
  and a **job detail page** ([#45](https://github.com/funky-lobsters/startup-job-tracker/issues/45), PR [#53](https://github.com/funky-lobsters/startup-job-tracker/pull/53)).
- **Filter jobs** by role type, location and company stage, combined, with the choices kept in the page address
  ([#26](https://github.com/funky-lobsters/startup-job-tracker/issues/26), PR [#57](https://github.com/funky-lobsters/startup-job-tracker/pull/57)), and **company pages**: `/companies/` lists every company, each
  with its own page and jobs ([#27](https://github.com/funky-lobsters/startup-job-tracker/issues/27), PR [#58](https://github.com/funky-lobsters/startup-job-tracker/pull/58)).
- **AI feature, first version:** job seeker **profile** at `/profile/`
  ([#31](https://github.com/funky-lobsters/startup-job-tracker/issues/31), PR [#38](https://github.com/funky-lobsters/startup-job-tracker/pull/38)),
  and **"Recommended for you"** at `/recommendations/`: the server sends the profile and the job list to an LLM
  through OpenRouter, asks for structured JSON output, and keeps only real jobs (max 5), each with a one-sentence
  reason ([#32](https://github.com/funky-lobsters/startup-job-tracker/issues/32), PR [#40](https://github.com/funky-lobsters/startup-job-tracker/pull/40)).
  The key is set on staging and production; OpenRouter is mocked in every test.
- **Import companies from a CSV file** ([#33](https://github.com/funky-lobsters/startup-job-tracker/issues/33), PR [#54](https://github.com/funky-lobsters/startup-job-tracker/pull/54)).
- **Delivery, following Kyle's Sprint 1 feedback ([#39](https://github.com/funky-lobsters/startup-job-tracker/issues/39)):**
  tests and Gitleaks run on every pull request, and `main` only accepts a merge when both are green
  ([#42](https://github.com/funky-lobsters/startup-job-tracker/issues/42), PR [#47](https://github.com/funky-lobsters/startup-job-tracker/pull/47));
  a `/health/` page shows which commit is live and whether the database is OK
  ([#43](https://github.com/funky-lobsters/startup-job-tracker/issues/43), PR [#51](https://github.com/funky-lobsters/startup-job-tracker/pull/51), fix PR [#56](https://github.com/funky-lobsters/startup-job-tracker/pull/56)).

## What works on staging now

Log in at `/login/` (grader accounts: see the submission notes), then:
- **Jobs**: all demo jobs, newest first; click one for its detail page, **Apply** opens the posting in a new tab.
- Filter the jobs by role type, location and company stage; **Clear filters** resets the list.
- **Companies**: every company A to Z; click one for its details and jobs (company names on job pages link there too).
- **Profile**: save your background, skills and preferences.
- **For you**: up to 5 jobs the AI picked for your profile, each with a reason (with no profile, it asks you to fill one in first).
- `/health/` shows the live commit and database status; `/26fd193` and `/26fd193/stats` still work, with traffic sources.

The same build is live on production.

## Working with agents

- **A separate agent reviews every pull request.** After Kyle's comments in class, we changed our rule: instead of a
  teammate approving, a fresh agent that did not write the code reviews each PR, and the person running `/review-pr`
  confirms before anything is posted or merged (PR [#49](https://github.com/funky-lobsters/startup-job-tracker/pull/49)).
  It paid off on its first run: reviewing PR #49 itself, the reviewer agent asked for changes and caught two real bugs
  in our own `/next` command, which were fixed and re-reviewed before merging.
- **Asking the AI for structured output, then checking it.** For "Recommended for you" we first considered letting
  the model write free text. We chose a fixed JSON format (job id + reason) and check every answer against our own
  database, so the AI can never show a job or link that doesn't exist.

## Backlog changes for next sprint

- Sprint 3 starts with real data, as Kyle suggested: import real startups and jobs from one source first
  ([#30](https://github.com/funky-lobsters/startup-job-tracker/issues/30), [#34](https://github.com/funky-lobsters/startup-job-tracker/issues/34)),
  then the application tracker ([#28](https://github.com/funky-lobsters/startup-job-tracker/issues/28)) and newest jobs on the home page ([#46](https://github.com/funky-lobsters/startup-job-tracker/issues/46)).
- New this sprint: code style checks and error tracking ([#52](https://github.com/funky-lobsters/startup-job-tracker/issues/52)) and an agreed visual design ([#55](https://github.com/funky-lobsters/startup-job-tracker/issues/55)).
- Possible AI follow-ups: save recommendations instead of asking the AI on every page load, and per-user AI usage limits.
- Small fix carried over: the filter heading says "1 open role match" instead of "matches" (found in review of PR #57).
