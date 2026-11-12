#!/usr/bin/env bash
set -euo pipefail

OWNER="${GITHUB_OWNER:-ObiwanKenobee}"
REPO="${GITHUB_REPO:-ebrr-agent}"
VISIBILITY="${GITHUB_VISIBILITY:-public}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required. Install it from https://cli.github.com/" >&2
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "Authenticate first with: gh auth login" >&2
  exit 1
fi
if [[ "$VISIBILITY" != "public" && "$VISIBILITY" != "private" ]]; then
  echo "GITHUB_VISIBILITY must be 'public' or 'private'." >&2
  exit 1
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This directory is already a Git repository. Review its remotes before proceeding." >&2
  exit 1
fi

git init -b main
git add .
git commit -m "chore: establish EBRR research scaffold"

gh repo create "$OWNER/$REPO" "--$VISIBILITY" --source=. --remote=origin --push

echo "Published https://github.com/$OWNER/$REPO"
