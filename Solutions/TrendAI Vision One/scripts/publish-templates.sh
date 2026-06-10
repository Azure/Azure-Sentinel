#!/usr/bin/env bash
# Publish ARM templates to the Azure Blob container that backs the
# "Test Deploy" buttons in README.md (used while the repo is private).
#
# What it does:
#   1. Stages templates/ into a temp dir
#   2. Rewrites the `baseUrl` variable in each mainTemplate.json from the
#      GitHub raw URL -> the Azure blob URL (so nested component fetches
#      work while the repo is private)
#   3. Uploads the staged files to <account>/<container>/{workbench,oat}
#
# Usage:
#   ./scripts/publish-templates.sh                 # upload workbench + oat
#   ./scripts/publish-templates.sh workbench       # upload only workbench
#   ./scripts/publish-templates.sh oat             # upload only oat
#
# Auth (in priority order):
#   AZURE_STORAGE_KEY        -- account key
#   AZURE_STORAGE_SAS_TOKEN  -- SAS token
#   else falls back to `az login` (needs Storage Blob Data Contributor)

set -euo pipefail

ACCOUNT="${AZURE_STORAGE_ACCOUNT:-trendaiccf45}"
CONTAINER="${AZURE_STORAGE_CONTAINER:-arm-templates}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/templates"

GITHUB_BASE="https://raw.githubusercontent.com/trendmicro/trendai-sentinel-ccf-data-connector/main/templates"
BLOB_BASE="https://${ACCOUNT}.blob.core.windows.net/${CONTAINER}"

TARGETS=("$@")
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=(workbench oat)
fi

AUTH_ARGS=(--auth-mode login)
if [ -n "${AZURE_STORAGE_KEY:-}" ]; then
  AUTH_ARGS=(--account-key "$AZURE_STORAGE_KEY")
elif [ -n "${AZURE_STORAGE_SAS_TOKEN:-}" ]; then
  AUTH_ARGS=(--sas-token "$AZURE_STORAGE_SAS_TOKEN")
fi

STAGE="$(mktemp -d -t trendai-publish.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT

for t in "${TARGETS[@]}"; do
  if [ ! -d "$SRC/$t" ]; then
    echo "skip: $SRC/$t not found" >&2
    continue
  fi

  echo "==> staging templates/$t"
  cp -R "$SRC/$t" "$STAGE/$t"

  MAIN="$STAGE/$t/mainTemplate.json"
  if [ -f "$MAIN" ]; then
    # Rewrite GitHub raw baseUrl -> Azure blob baseUrl for THIS connector's components.
    # sed -i'' '' for BSD/macOS compatibility.
    sed -i'' -e "s|${GITHUB_BASE}/${t}/components|${BLOB_BASE}/${t}/components|g" "$MAIN"
    echo "    rewrote baseUrl in $t/mainTemplate.json"
  fi

  echo "==> uploading $t -> $ACCOUNT/$CONTAINER/$t"
  az storage blob upload-batch \
    --account-name "$ACCOUNT" \
    --destination "$CONTAINER" \
    --destination-path "$t" \
    --source "$STAGE/$t" \
    --overwrite \
    "${AUTH_ARGS[@]}" >/dev/null
done

echo "done. Test-deploy URLs in README.md now point to the latest code."
