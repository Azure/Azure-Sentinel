#!/usr/bin/env bash
# validate-urls.sh — single source of truth for URL validation.
#
# Usage:
#   scripts/validate-urls.sh <url1> [url2] [url3] ...
#
# For each URL, performs HEAD with redirect-follow, falls back to GET on 405/403,
# and prints one JSON line per URL with the final status code, the final
# effective URL, and a pass/fail verdict. Exits non-zero if ANY URL fails.
#
# A URL "passes" only when:
#   * Final HTTP status is exactly 200, AND
#   * Final effective URL is on the same registrable host as the input URL
#     (i.e., not redirected to a login wall or marketing site on a different host).
#
# This script is the ONLY approved way to mark a URL as validated. The
# agent must run it and surface its output before saving any URL to
# config/progress.json or including any URL in an @sentinel prompt.

set -u

if [[ $# -lt 1 ]]; then
  echo '{"error":"no URLs provided","usage":"scripts/validate-urls.sh <url> [url ...]"}' >&2
  exit 2
fi

# Extract the host portion of a URL (scheme://host[:port]/...).
host_of() {
  printf '%s' "$1" | sed -E 's#^[a-zA-Z]+://([^/]+).*#\1#' | tr '[:upper:]' '[:lower:]'
}

json_escape() {
  printf '%s' "$1" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()), end="")'
}

any_failed=0

for url in "$@"; do
  # HEAD with redirect-follow.
  read -r code effective < <(curl -sIL --max-time 15 -o /dev/null -w '%{http_code} %{url_effective}' "$url" 2>/dev/null || echo "000 ")

  # Fall back to GET when HEAD is rejected.
  if [[ "$code" == "405" || "$code" == "403" || "$code" == "000" ]]; then
    read -r code effective < <(curl -sL  --max-time 20 -o /dev/null -w '%{http_code} %{url_effective}' "$url" 2>/dev/null || echo "000 ")
  fi

  input_host=$(host_of "$url")
  effective_host=$(host_of "${effective:-$url}")

  reason=""
  pass="false"
  if [[ "$code" == "200" ]]; then
    if [[ "$input_host" == "$effective_host" ]]; then
      pass="true"
    else
      reason="redirected off vendor host (${input_host} -> ${effective_host})"
    fi
  else
    reason="http ${code}"
  fi

  if [[ "$pass" != "true" ]]; then
    any_failed=1
  fi

  printf '{"url":%s,"finalUrl":%s,"status":%s,"pass":%s,"reason":%s}\n' \
    "$(json_escape "$url")" \
    "$(json_escape "${effective:-$url}")" \
    "${code:-0}" \
    "$pass" \
    "$(json_escape "$reason")"
done

exit "$any_failed"
