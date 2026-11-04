# docs/notes/: the team's shared memory

Things worth keeping that are **not decided yet**: meeting notes, brainstorming, research,
half-made decisions, open questions, who is doing what.

**How it works:** you don't need to write these yourself. When something in a Claude Code
session is worth keeping, the agent asks *"Want me to add this to docs/notes/?"*. Say yes and
it writes or updates a note. You can also just ask: "add this to our notes."
The full rules for agents are in [CLAUDE.md](../../CLAUDE.md) under "Notes workflow".

- **Not graded.** Graded course docs live in `docs/mgt656/`.
- **Not the source of truth.** Once the team decides something, the agent moves it to
  `docs/context/product-idea.md` (product), a GitHub issue (work to do) or `docs/mgt656/` (graded docs),
  and marks the note `status: promoted`.
- **File names:** `YYYY-MM-DD-topic.md`, e.g. `2026-11-05-kickoff.md`.
- **Each note starts with:** date, who was involved, status (`idea`, `in discussion`, `decided`, `promoted`).
- **Never** put passwords, API keys, connection strings or real personal data here.
- Teammates see new notes after the change is merged to `main` and they pull.
