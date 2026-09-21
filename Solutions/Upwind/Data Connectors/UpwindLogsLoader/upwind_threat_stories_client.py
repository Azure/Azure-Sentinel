"""Upwind API client for fetching threat stories."""

import logging
from datetime import datetime, timedelta, timezone

from .upwind_client import UpwindClient, rename_reserved_columns

# "title" is a reserved/invalid Log Analytics custom-table column name, so
# it's renamed before upload. The DCR/table schema uses "title_text".
_COLUMN_RENAME_MAP = {"title": "title_text"}


class UpwindThreatStoriesClient(UpwindClient):
    """Client for the Upwind threat stories API."""

    def fetch_threat_stories(self, lookback_minutes: int) -> list:
        """
        Fetch threat stories updated within the lookback window.

        :param lookback_minutes: How far back (in minutes) to query. Should be
            comfortably larger than the function's own run interval so no
            stories are missed between runs; harmless duplicates are
            re-ingested on overlap.
        :return: List of threat story dictionaries.
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

        stories = self._fetch_paginated(url, search_body)
        stories = rename_reserved_columns(stories, _COLUMN_RENAME_MAP)
        logging.info("Fetched %d total threat stories.", len(stories))
        return stories
