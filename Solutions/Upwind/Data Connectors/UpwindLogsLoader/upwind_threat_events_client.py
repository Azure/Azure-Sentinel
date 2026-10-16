"""Upwind API client for fetching threat events."""

import logging
from datetime import datetime, timedelta, timezone

from .upwind_client import (
    UpwindClient,
    rename_reserved_columns,
    severities_at_least,
)

# "title" and "type" are reserved/invalid Log Analytics custom-table column
# names, so they're renamed before upload. The DCR/table schema uses the
# renamed names.
_COLUMN_RENAME_MAP = {"title": "title_text", "type": "event_type"}


class UpwindThreatEventsClient(UpwindClient):
    """Client for the Upwind threat events API."""

    def fetch_threat_events(self, lookback_minutes: int, on_page) -> int:
        """
        Fetch threat events last seen within the lookback window.

        :param lookback_minutes: How far back (in minutes) to query. Should be
            comfortably larger than the function's own run interval so no
            events are missed between runs; harmless duplicates are
            re-ingested on overlap.
        :param on_page: Callback invoked with each page of threat events.
        :return: Total number of threat events fetched.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        url = f"{self.api_base_url}/v1/organizations/{self.org_id}/threat-events"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=lookback_minutes)
        time_fmt = "%Y-%m-%dT%H:%M:%SZ"

        params = {
            "per-page": self.page_size,
            "min-last-seen-time": window_start.strftime(time_fmt),
            "max-last-seen-time": now.strftime(time_fmt),
        }

        severities = severities_at_least(
            self.config.get("upwind_min_severity_threat_events")
        )
        if severities:
            params["severity"] = ",".join(severities)
            logging.info(
                "Filtering threat events to severities: %s", ", ".join(severities)
            )

        def emit(items):
            on_page(rename_reserved_columns(items, _COLUMN_RENAME_MAP))

        total = self._fetch_page_paginated(url, params, emit)
        logging.info("Fetched %d total threat events.", total)
        return total
