"""Upwind API client for fetching threat stories."""

import logging
from datetime import datetime, timedelta, timezone

from .upwind_client import (
    UpwindClient,
    rename_reserved_columns,
    severities_at_least,
)

# "title" is a reserved/invalid Log Analytics custom-table column name, so
# it's renamed before upload. The DCR/table schema uses "title_text".
_COLUMN_RENAME_MAP = {"title": "title_text"}


class UpwindThreatStoriesClient(UpwindClient):
    """Client for the Upwind threat stories API."""

    def fetch_threat_stories(self, lookback_minutes: int, on_page) -> int:
        """
        Fetch threat stories updated within the lookback window.

        :param lookback_minutes: How far back (in minutes) to query. Should be
            comfortably larger than the function's own run interval so no
            stories are missed between runs; harmless duplicates are
            re-ingested on overlap.
        :param on_page: Callback invoked with each page of threat stories.
        :return: Total number of threat stories fetched.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        url = f"{self.api_base_url}/v2/organizations/{self.org_id}/threats/stories/search"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=lookback_minutes)
        time_fmt = "%Y-%m-%dT%H:%M:%SZ"

        search_body = {
            "conditions": [
                {"field": "update_time", "operator": "gte", "value": [window_start.strftime(time_fmt)]},
                {"field": "update_time", "operator": "lte", "value": [now.strftime(time_fmt)]},
            ]
        }

        severities = severities_at_least(
            self.config.get("upwind_min_severity_threat_stories")
        )
        if severities:
            search_body["conditions"].append(
                {"field": "severity", "operator": "in", "value": severities}
            )
            logging.info(
                "Filtering threat stories to severities: %s", ", ".join(severities)
            )

        def emit(items):
            on_page(rename_reserved_columns(items, _COLUMN_RENAME_MAP))

        total = self._fetch_paginated(url, search_body, emit)
        logging.info("Fetched %d total threat stories.", total)
        return total
