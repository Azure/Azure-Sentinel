#!/bin/bash
# =============================================================================
# entrypoint-with-ti-refresh.sh
# =============================================================================
# Wraps the Logstash entrypoint with an in-container TI feed refresh loop so
# the container is self-managing — no host cron required.
#
# Refresh cadence: every 6 hours. Logstash auto-reloads the files via the
# cidr/translate filters' refresh_interval setting, so no Logstash restart.
#
# Initial feed files are baked in at image build time. After container start
# they're refreshed in-place every 6 hours, with Logstash picking up the
# updates within its own refresh_interval window.
#
# Manual on-demand refresh still works:
#   docker exec unifi-syslog-logstash /usr/local/bin/refresh-ti-feeds.sh
# =============================================================================

(
  while true; do
    sleep 21600  # 6 hours
    /usr/local/bin/refresh-ti-feeds.sh > /var/log/ti-refresh.log 2>&1 || \
      echo "[ti-refresh-loop] refresh failed at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >&2
  done
) &

# Hand off to Logstash's standard entrypoint as PID 1 so signal handling,
# config validation, and process lifecycle remain identical to upstream.
exec /usr/local/bin/docker-entrypoint "$@"
