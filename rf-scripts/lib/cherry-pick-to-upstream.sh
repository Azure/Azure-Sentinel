#!/usr/bin/env bash
set -euo pipefail

# lib/cherry-pick-to-upstream.sh
# Shared core logic for preparing an upstream branch from a master-rf feature branch.
#
# Usage: cherry-pick-to-upstream.sh <current_branch> <upstream_branch>
#
# Exits 0 on success, 1 on failure.
# On success, prints commit list to stdout.
# On failure, prints error message to stderr.

MASTER_BRANCH="master"
INTERNAL_BRANCH="master-rf"

CURRENT_BRANCH="${1:-}"
UPSTREAM_BRANCH="${2:-}"

[[ -z "$CURRENT_BRANCH" ]]  && { echo "Usage: $0 <current_branch> <upstream_branch>" >&2; exit 1; }
[[ -z "$UPSTREAM_BRANCH" ]] && { echo "Usage: $0 <current_branch> <upstream_branch>" >&2; exit 1; }

# ── find commits ─────────────────────────────────────────────────────────────

COMMIT_SHAS=$(git log --format="%H" --reverse "origin/${INTERNAL_BRANCH}..origin/${CURRENT_BRANCH}")
COMMIT_ONELINES=$(git log --oneline --reverse "origin/${INTERNAL_BRANCH}..origin/${CURRENT_BRANCH}")

if [[ -z "$COMMIT_SHAS" ]]; then
  echo "No commits found between '$INTERNAL_BRANCH' and '$CURRENT_BRANCH'." >&2
  exit 1
fi

echo "$COMMIT_ONELINES"

# ── create upstream branch from master ───────────────────────────────────────

git fetch origin "$MASTER_BRANCH" --quiet >&2
git checkout -b "$UPSTREAM_BRANCH" "origin/$MASTER_BRANCH" >&2

# ── cherry-pick ───────────────────────────────────────────────────────────────

if ! git cherry-pick $COMMIT_SHAS >&2; then
  git cherry-pick --abort 2>/dev/null || true
  git checkout master-rf 2>/dev/null || true
  git branch -D "$UPSTREAM_BRANCH" 2>/dev/null || true
  echo "Cherry-pick failed due to conflicts. Run ./rf-scripts/upstream-pr.sh locally to resolve." >&2
  exit 1
fi
