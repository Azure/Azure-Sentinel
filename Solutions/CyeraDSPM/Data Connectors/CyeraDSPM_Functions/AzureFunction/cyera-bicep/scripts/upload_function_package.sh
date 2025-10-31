#!/usr/bin/env bash
# Upload a function zip to blob and point WEBSITE_RUN_FROM_PACKAGE at SAS URL
set -euo pipefail

if [[ $# -lt 6 ]]; then
  echo "Usage: $0 <resource-group> <storage-account> <container> <functionapp-name> <zip-path> <expiry-hours>" 1>&2
  exit 1
fi

RG="$1"; SA="$2"; CONT="$3"; FUNC="$4"; ZIP="$5"; EXP_HOURS="$6"

az storage container create --name "$CONT" --account-name "$SA" >/dev/null
BLOB="$(basename "$ZIP")"
az storage blob upload --account-name "$SA" -c "$CONT" -f "$ZIP" -n "$BLOB" --overwrite >/dev/null

EXPIRY=$(date -u -d "+$EXP_HOURS hour" '+%Y-%m-%dT%H:%MZ')
SAS=$(az storage blob generate-sas --account-name "$SA" -c "$CONT" -n "$BLOB" --permissions r --expiry "$EXPIRY" -o tsv)
URL="https://$SA.blob.core.windows.net/$CONT/$BLOB?$SAS"
echo "Package URL: $URL"

az functionapp config appsettings set -g "$RG" -n "$FUNC" --settings WEBSITE_RUN_FROM_PACKAGE="$URL" >/dev/null
echo "WEBSITE_RUN_FROM_PACKAGE set."
