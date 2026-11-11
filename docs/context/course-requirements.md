# MGT 656 Team Project: Course Requirements

## Source of truth: Kyle's requirements repo

The course requirements live in Kyle's repo, which he updates over time:

**https://github.com/yale-mgt-656-fall-2026/project-requirements** (the `README.md` file)

We don't keep a copy here, so there's nothing to go stale. **Every agent must read the live version before doing any work:**

```bash
curl -fsSL https://raw.githubusercontent.com/yale-mgt-656-fall-2026/project-requirements/main/README.md
```

(This works on laptops and in cloud sessions. `gh api` can't read that repo from a cloud session, so use `curl`.)

It covers: timeline and deadlines, the required items, the technical challenge, how we work (project board, backlog, sprints, PRs),
the `docs/mgt656/` folder and report formats, the A/B test page spec, hosting, what to submit, and grading.

Rules for agents:
- Treat its Required list and A/B test spec as hard acceptance criteria. Verify each against the running app, not just the code.
- If it conflicts with anything in this repo (including `course-sprints.md` or the addendum below), **Kyle's repo wins**.
  Point out the conflict to the teammate and offer to update our files.
- If you can't fetch it (no network), say so and don't guess the requirements from memory.
- Questions for Kyle go in the course's GitHub Discussions: https://github.com/orgs/yale-mgt-656-fall-2026/discussions

## Our team's facts (not in Kyle's repo)

- **Team nickname: `funky-lobsters` → A/B page at `/26fd193`, stats at `/26fd193/stats`.**
  Computed with `printf %s funky-lobsters | shasum` (never `echo`). Spelling confirmed from the course site.

## Addendum from Kyle (2026-11-11): agents may review pull requests

*Kyle confirmed verbally to the team on 2026-11-11 that this applies **as of now**. He will update his requirements repo
later; until he does, his repo still says "reviewed by a teammate", and this addendum is the exception to "Kyle's repo wins" for this one point.
When his repo changes, his wording wins and this section should be updated or removed.*

What Kyle said: what matters is that every pull request gets a real check and review, not that a human does it.
A reviewing agent counts as the "team member" reviewer. The goal is to remove waiting on each other.

Our rules from this:
- **Every PR still gets a review before merging.** It can come from an agent (the `review-pr` skill) instead of a teammate.
  The author can run it on their own PR; nobody has to wait for someone else.
- **The review is a real check, not a rubber stamp:** run the tests, check every acceptance criterion in the issue,
  check the CLAUDE.md rules (no secrets, migrations, mocked external calls), and say plainly if something fails.
  A failing review blocks the merge until it's fixed and reviewed again.
- **The review is written on the PR** as a GitHub review comment starting with `Agent review:`, so graders can see it.
  (GitHub never lets you click **Approve** on your own PR, so an agent working from the author's account posts a comment
  review instead.)
- **Agents may also do the writing:** PR descriptions, sprint reports, `technical.md`, notes. The writing must stay true:
  "What the team changed or rejected" and the sprint report's "working with agents" example describe what really happened
  in the session, and an agent never invents them.
- **One human click stays:** the author still says "yes, merge" in their own session. That's not a bottleneck on anyone else.
  Deploying to production and deleting data still need a human yes.

## Addendum from class: traffic source tracking (graded)

*Added by the team on 2026-11-04 from Kyle's announcement in class. It is not in Kyle's requirements repo yet. When Kyle adds it there, his version wins and this section should be updated or removed.*

Kyle will send bot traffic to our A/B page from **three sources**: the Law School, SOM, and a third one (name not remembered; confirm with Kyle). It is **graded**: we must work out where each visitor came from, using the HTTP **`Referer`** header (the address of the page that linked to us; the header name is misspelled in the HTTP standard). Kyle said to ask our AI how to do it, and that it should be fairly easy.

Our interpretation (acceptance criteria for the A/B page story):

- On a visitor's **first** visit to `/26fd193` (the same moment the impression is counted), store with the impression:
  - the raw `Referer` header value (empty if missing), and
  - the derived **source**: the referrer's host name, e.g. `law.yale.edu`, `som.yale.edu`, or `direct` if there was no Referer.
  - Don't hard-code a list of three: record whatever host arrives, so the unknown third source is counted automatically.
- A visitor's click belongs to that visitor's source. **Never** take the source from the click request: its Referer is our own page.
- Reloads and the redirect after a click must not overwrite the stored source (same rule as impressions).
- `/26fd193/stats` keeps the `preferred` key exactly as specified and adds a breakdown by source (extra keys are allowed), e.g.:

```json
{"preferred": "kudos",
 "kudos": {"impressions": 212, "clicks": 63},
 "thanks": {"impressions": 207, "clicks": 21},
 "sources": {
   "law.yale.edu": {"kudos": {"impressions": 80, "clicks": 30}, "thanks": {"impressions": 78, "clicks": 9}},
   "som.yale.edu": {"kudos": {"impressions": 70, "clicks": 20}, "thanks": {"impressions": 69, "clicks": 7}},
   "direct":       {"kudos": {"impressions": 62, "clicks": 13}, "thanks": {"impressions": 60, "clicks": 5}}
 }}
```

- Tests cover: Referer from two different sites, a missing Referer (`direct`), a reload with a different Referer (source unchanged), and a click (source unchanged).
- Test visits count here too: purge them from production before the run.

Open questions to confirm with Kyle (update this addendum when answered):
1. Exactly how is it graded? Does he read a key from `/stats` (and what name/format), or something else?
2. What is the third source (besides the Law School and SOM)?
3. Is it the same bot run as the A/B run after Sprint 4, or a separate one? When?
4. Should the source be the host name (`law.yale.edu`) or a school label (`Law School`)?
