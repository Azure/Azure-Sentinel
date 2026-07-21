FROM docker.elastic.co/logstash/logstash:8.15.0

USER root

# Install the new (Java-based, v2.x) Microsoft Sentinel Log Analytics output plugin.
# The new gem name is different from the retired Ruby plugin
# (microsoft-sentinel-logstash-output-plugin → microsoft-sentinel-log-analytics-logstash-output-plugin).
#
# The netbase package is required in containers — without it the new plugin's
# Java HTTP stack hits getprotobyname_r failures on first request.
ENV LS_JVM_OPTS="-Xmx1g"
RUN apt-get update \
 && apt-get install -y --no-install-recommends netbase \
 && rm -rf /var/lib/apt/lists/*
RUN bin/logstash-plugin install --no-verify microsoft-sentinel-log-analytics-logstash-output-plugin

# Disable the noisy elasticsearch monitoring/license checks.
# Also disable ECS v8 compatibility — Microsoft's plugin README explicitly
# recommends this on Logstash 8 (silences the per-grok-block "ECS v8 support
# is a preview" warnings and avoids surprises when ECS v8 actually ships).
RUN echo "xpack.monitoring.enabled: false"        >> /usr/share/logstash/config/logstash.yml \
 && echo "monitoring.enabled: false"               >> /usr/share/logstash/config/logstash.yml \
 && echo "pipeline.ecs_compatibility: disabled"    >> /usr/share/logstash/config/logstash.yml \
 && echo "allow_superuser: true"                   >> /usr/share/logstash/config/logstash.yml

# MaxMind GeoLite2 databases for IP → Country/City/ASN enrichment.
# Requires a free MaxMind account — sign up at https://www.maxmind.com/en/geolite2/signup
# Credentials are passed via BuildKit secrets (NOT build args) so they never
# appear in build logs or image history. docker-compose.yml mounts them from
# the MAXMIND_ACCOUNT_ID / MAXMIND_LICENSE_KEY env vars in .env at build time.
# If the secret files are empty the build skips silently — pipeline still works,
# just no ingest-time enrichment (geo_info_from_ip_address() still works at
# query time without these databases).
#
# Requires DOCKER_BUILDKIT=1 (default in modern docker compose).
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=secret,id=maxmind_account_id \
    --mount=type=secret,id=maxmind_license_key \
    if [ -s /run/secrets/maxmind_license_key ]; then \
      mkdir -p /etc/logstash/geoip /etc/GeoIP && \
      printf "AccountID %s\nLicenseKey %s\nEditionIDs GeoLite2-City GeoLite2-ASN\nDatabaseDirectory /etc/logstash/geoip\n" \
        "$(cat /run/secrets/maxmind_account_id)" "$(cat /run/secrets/maxmind_license_key)" \
        > /etc/GeoIP/GeoIP.conf && \
      curl -fsSL https://github.com/maxmind/geoipupdate/releases/download/v7.0.1/geoipupdate_7.0.1_linux_amd64.tar.gz \
        | tar xz -C /tmp && \
      /tmp/geoipupdate_7.0.1_linux_amd64/geoipupdate -v -f /etc/GeoIP/GeoIP.conf && \
      rm -f /etc/GeoIP/GeoIP.conf && \
      rm -rf /tmp/geoipupdate* && \
      echo "GeoIP databases installed:" && ls -la /etc/logstash/geoip/ ; \
    else \
      echo "MaxMind license key not provided — skipping GeoIP database install" ; \
    fi

# Threat-intel feeds for ingest-time enrichment.
# refresh-ti-feeds.sh runs at build time (initial download). The wrapper
# entrypoint below schedules subsequent refreshes every 6 hours from inside
# the container — no host cron needed. Logstash auto-reloads the files via
# refresh_interval.
COPY refresh-ti-feeds.sh /usr/local/bin/refresh-ti-feeds.sh
COPY entrypoint-with-ti-refresh.sh /usr/local/bin/entrypoint-with-ti-refresh.sh
RUN chmod +x /usr/local/bin/refresh-ti-feeds.sh \
              /usr/local/bin/entrypoint-with-ti-refresh.sh && \
    /usr/local/bin/refresh-ti-feeds.sh

# Override the base image's entrypoint to schedule TI refresh alongside
# Logstash. The wrapper exec's into the upstream docker-entrypoint so it
# becomes PID 1 — preserving signal handling and config validation.
ENTRYPOINT ["/usr/local/bin/entrypoint-with-ti-refresh.sh"]
CMD ["-f", "/usr/share/logstash/pipeline/logstash.conf"]

# Bake the pipeline config into the image — bind-mounting from /boot (FAT32) on
# UnRAID doesn't preserve Unix permissions, so the logstash user can't read it.
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
RUN chmod 644 /usr/share/logstash/pipeline/logstash.conf

# Stay as root so we can bind to port 514 (no setcap required).
# Logstash 8.x supports running as root.
