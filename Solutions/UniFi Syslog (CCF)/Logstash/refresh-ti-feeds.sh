#!/bin/bash
# =============================================================================
# refresh-ti-feeds.sh
# =============================================================================
# Pulls latest threat-intel feeds for Logstash ingest-time enrichment.
# Runs at image build time AND callable at runtime via docker exec:
#
#   docker exec unifi-syslog-logstash /usr/local/bin/refresh-ti-feeds.sh
#
# Logstash's cidr/translate filters re-read the files via `refresh_interval`,
# so no container restart is required after refresh.
#
# Suggested cron on the host (UnRAID User Scripts):
#   0 */6 * * * docker exec unifi-syslog-logstash /usr/local/bin/refresh-ti-feeds.sh
# =============================================================================
set -e

TI_DIR=/etc/logstash/ti
mkdir -p "$TI_DIR"
TMP=$(mktemp -d)
trap 'rm -rf $TMP' EXIT

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] $*"; }

fetch() {
  local url="$1" out="$2"
  curl -fsSL --max-time 30 "$url" -o "$out"
}

log "Refreshing TI feeds into $TI_DIR ..."

# -----------------------------------------------------------------------------
# FireHOL Level 1 — aggregated blocklist of high-confidence bad actors
# Format: text, one CIDR or IP per line, comments with '#'
# -----------------------------------------------------------------------------
if fetch "https://iplists.firehol.org/files/firehol_level1.netset" "$TMP/firehol_l1.txt"; then
  grep -v '^#' "$TMP/firehol_l1.txt" | awk 'NF' > "$TI_DIR/firehol_l1.txt"
  log "  firehol_l1.txt: $(wc -l <"$TI_DIR/firehol_l1.txt") entries"
else
  log "  WARN: firehol_l1 fetch failed (keeping existing file if any)"
fi

# -----------------------------------------------------------------------------
# Spamhaus DROP + EDROP — confirmed malicious /24+ blocks
# Format: 'cidr ; comment' — strip comments + blanks
# -----------------------------------------------------------------------------
{
  if fetch "https://www.spamhaus.org/drop/drop.txt"  "$TMP/spamhaus_drop.raw"; then
    grep -v '^;' "$TMP/spamhaus_drop.raw" | awk 'NF{print $1}'
  fi
  if fetch "https://www.spamhaus.org/drop/edrop.txt" "$TMP/spamhaus_edrop.raw"; then
    grep -v '^;' "$TMP/spamhaus_edrop.raw" | awk 'NF{print $1}'
  fi
} > "$TMP/spamhaus_combined.txt"

if [ -s "$TMP/spamhaus_combined.txt" ]; then
  mv "$TMP/spamhaus_combined.txt" "$TI_DIR/spamhaus_drop.txt"
  log "  spamhaus_drop.txt: $(wc -l <"$TI_DIR/spamhaus_drop.txt") entries"
else
  log "  WARN: spamhaus fetch failed (keeping existing file if any)"
fi

# -----------------------------------------------------------------------------
# Tor exit nodes — IP list (plain text, one per line)
# Convert to YAML dictionary for logstash translate filter (key: value pairs)
# -----------------------------------------------------------------------------
if fetch "https://check.torproject.org/torbulkexitlist" "$TMP/tor_exits.raw"; then
  {
    echo "---"
    awk 'NF{print $1": \"tor\""}' "$TMP/tor_exits.raw"
  } > "$TI_DIR/tor_exits.yaml"
  log "  tor_exits.yaml: $(($(wc -l <"$TI_DIR/tor_exits.yaml") - 1)) entries"
else
  log "  WARN: tor exit list fetch failed (keeping existing file if any)"
fi

log "Done."
