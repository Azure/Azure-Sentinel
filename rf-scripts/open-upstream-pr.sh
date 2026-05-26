#!/usr/bin/env bash
set -euo pipefail

# open-upstream-pr.sh
# Takes the current feature branch (based on master-rf) and prepares a clean
# upstream branch based on master, then pushes and opens the PR creation URL.

MASTER_BRANCH="master"
INTERNAL_BRANCH="master-rf"

# ── helpers ──────────────────────────────────────────────────────────────────

red()   { echo -e "\033[0;31m$*\033[0m"; }
green() { echo -e "\033[0;32m$*\033[0m"; }
bold()  { echo -e "\033[1m$*\033[0m"; }

abort() { red "Error: $*"; exit 1; }

# ── checks ───────────────────────────────────────────────────────────────────

git rev-parse --git-dir > /dev/null 2>&1 || abort "Not inside a git repository."

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

[[ "$CURRENT_BRANCH" == "$MASTER_BRANCH" ]]   && abort "You are on '$MASTER_BRANCH'. Checkout a feature branch first."
[[ "$CURRENT_BRANCH" == "$INTERNAL_BRANCH" ]] && abort "You are on '$INTERNAL_BRANCH'. Checkout a feature branch first."
[[ "$CURRENT_BRANCH" == feat/* ]]              && abort "You are already on an upstream branch ('$CURRENT_BRANCH')."

# ── derive upstream branch name ───────────────────────────────────────────────

# Strip leading rf/ prefix if present, then prepend feat/
STRIPPED="${CURRENT_BRANCH#rf/}"
UPSTREAM_BRANCH="feat/${STRIPPED}"

# ── find commits to cherry-pick ───────────────────────────────────────────────

COMMITS=$(git log --oneline --reverse "$INTERNAL_BRANCH..HEAD")

if [[ -z "$COMMITS" ]]; then
  abort "No commits found between '$INTERNAL_BRANCH' and '$CURRENT_BRANCH'. Nothing to do."
fi

bold "\nCommits to be cherry-picked onto '$UPSTREAM_BRANCH':"
echo "$COMMITS"
echo ""

# ── check if upstream branch already exists ──────────────────────────────────

LOCAL_EXISTS=false
REMOTE_EXISTS=false

git show-ref --verify --quiet "refs/heads/$UPSTREAM_BRANCH"       && LOCAL_EXISTS=true  || true
git show-ref --verify --quiet "refs/remotes/origin/$UPSTREAM_BRANCH" && REMOTE_EXISTS=true || true

if $LOCAL_EXISTS || $REMOTE_EXISTS; then
  read -r -p "$(bold "Branch '$UPSTREAM_BRANCH' already exists. Overwrite? [y/N] ")" CONFIRM
  [[ "$CONFIRM" =~ ^[Yy]$ ]] || abort "Aborted."
  $LOCAL_EXISTS  && git branch -D "$UPSTREAM_BRANCH"
  $REMOTE_EXISTS && git push origin --delete "$UPSTREAM_BRANCH" 2>/dev/null || true
fi

# ── create upstream branch from master ───────────────────────────────────────

git fetch origin "$MASTER_BRANCH" --quiet
git checkout -b "$UPSTREAM_BRANCH" "origin/$MASTER_BRANCH"

# ── cherry-pick commits ───────────────────────────────────────────────────────

COMMIT_SHAS=$(git log --format="%H" --reverse "$INTERNAL_BRANCH..@{-1}")

if ! git cherry-pick $COMMIT_SHAS; then
  git cherry-pick --abort 2>/dev/null || true
  git checkout "$CURRENT_BRANCH"
  git branch -D "$UPSTREAM_BRANCH"
  red "\nCherry-pick failed due to conflicts."
  echo "Resolve conflicts manually:"
  echo "  1. git checkout $UPSTREAM_BRANCH  (recreate manually or re-run after fixing)"
  echo "  2. git cherry-pick <sha>"
  echo "  3. Resolve conflicts, then: git cherry-pick --continue"
  exit 1
fi

# ── push and open PR URL ──────────────────────────────────────────────────────

TMP_FILE=$(mktemp)
git push -u origin "$UPSTREAM_BRANCH" 2>&1 | tee "$TMP_FILE"
OUTPUT=$(cat "$TMP_FILE")
rm -f "$TMP_FILE"

PR_URL=$(echo "$OUTPUT" | grep -oE "https://github.com/.+/.+/pull/new/[^[:space:]]+" || true)

echo ""
if [[ -n "$PR_URL" ]]; then
  green "Opening PR creation URL..."
  open "$PR_URL"
else
  bold "Branch pushed. Open a PR manually at:"
  echo "  https://github.com/recordedfuture/Azure-Sentinel/compare/$UPSTREAM_BRANCH"
fi

green "\nDone. Upstream branch: $UPSTREAM_BRANCH"
