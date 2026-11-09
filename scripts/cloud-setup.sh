#!/bin/bash
# Claude runs this at the start of every CLOUD session (see CLAUDE.md, "Cloud sessions").
# Does nothing on a teammate's own laptop. In a CLOUD session (a fresh computer each time) it
# installs the project's Python packages so tests and Django commands work right away.
# It never fails the session: any problem is reported to Claude as text instead.

if [ -z "$CLAUDE_CODE_REMOTE_SESSION_ID" ] && [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || exit 0

{
  if [ ! -x .venv/bin/python ]; then
    # Prefer the project's Python (3.13); fall back to the machine's Python 3 (Django 6.1 needs 3.12+).
    uv venv -q --python 3.13 2>/dev/null || uv venv -q --python python3
  fi
  uv pip install -q --python .venv -r requirements.txt
  if [ ! -f .env ]; then
    # Local-only settings for this cloud computer. No real secrets: tests use SQLite and don't need a database.
    sed 's/^DEBUG=.*/DEBUG=true/' .env.example > .env
  fi
} > /tmp/cloud-setup.log 2>&1

if [ $? -eq 0 ]; then
  echo "Cloud setup done: Python $(.venv/bin/python -V 2>&1 | cut -d' ' -f2) and the project's packages are installed in .venv. Run tests with: .venv/bin/python manage.py test"
else
  echo "Cloud setup had a problem (details in /tmp/cloud-setup.log). Install packages with: uv venv && uv pip install -r requirements.txt"
fi
exit 0
