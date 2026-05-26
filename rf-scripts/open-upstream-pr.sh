#!/usr/bin/env bash
set -euo pipefail

# open-upstream-pr.sh
# Takes the current feature branch (based on master-rf) and prepares a clean
# upstream branch based on master, then pushes and opens the PR creation URL.

MASTER_BRANCH="master"
INTERNAL_BRANCH="master-rf"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── helpers ───────────────────────────────────────────────────────────────────

red()   { echo -e "\033[0;31m$*\033[0m"; }
green() { echo -e "\033[0;32m$*\033[0m"; }
bold()  { echo -e "\033[1m$*\033[0m"; }

abort() { red "Error: $*"; exit 1; }

# ── checks ────────────────────────────────────────────────────────────────────

git rev-parse --git-dir > /dev/null 2>&1 || abort "Not inside a git repository."

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

[[ "$CURRENT_BRANCH" == "$MASTER_BRANCH" ]]   && abort "You are on '$MASTER_BRANCH'. Checkout a feature branch first."
[[ "$CURRENT_BRANCH" == "$INTERNAL_BRANCH" ]] && abort "You are on '$INTERNAL_BRANCH'. Checkout a feature branch first."
[[ "$CURRENT_BRANCH" == feat/* ]]              && abort "You are already on an upstream branch ('$CURRENT_BRANCH')."

# ── derive upstream branch name ───────────────────────────────────────────────

STRIPPED="${CURRENT_BRANCH#rf/}"
UPSTREAM_BRANCH="feat/${STRIPPED}"

# ── check if upstream branch already exists ───────────────────────────────────

LOCAL_EXISTS=false
REMOTE_EXISTS=false

git show-ref --verify --quiet "refs/heads/$UPSTREAM_BRANCH"          && LOCAL_EXISTS=true  || true
git show-ref --verify --quiet "refs/remotes/origin/$UPSTREAM_BRANCH" && REMOTE_EXISTS=true || true

if $LOCAL_EXISTS || $REMOTE_EXISTS; then
  read -r -p "$(bold "Branch '$UPSTREAM_BRANCH' already exists. Overwrite? [y/N] ")" CONFIRM
  [[ "$CONFIRM" =~ ^[Yy]$ ]] || abort "Aborted."
  $LOCAL_EXISTS  && git branch -D "$UPSTREAM_BRANCH"
  $REMOTE_EXISTS && git push origin --delete "$UPSTREAM_BRANCH" 2>/dev/null || true
fi

# ── run shared logic ──────────────────────────────────────────────────────────

bold "\nCommits to be cherry-picked onto '$UPSTREAM_BRANCH':"

if ! COMMIT_LIST=$("$SCRIPT_DIR/lib/cherry-pick-to-upstream.sh" "$CURRENT_BRANCH" "$UPSTREAM_BRANCH"); then
  abort "$(cat)"
fi

echo "$COMMIT_LIST"
echo ""

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
