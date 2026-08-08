"""Upwind API client for fetching configuration (posture) findings."""

import logging
from datetime import datetime, timedelta, timezone

from .upwind_client import UpwindClient, rename_reserved_columns

# "title" is a reserved/invalid Log Analytics custom-table column name, so
# it's renamed before upload. The DCR/table schema uses "title_text".
_COLUMN_RENAME_MAP = {"title": "title_text"}


class UpwindConfigurationFindingsClient(UpwindClient):
    """Client for the Upwind configuration findings API."""

    def fetch_configuration_findings(self, lookback_minutes: int) -> list:
        """
        Fetch configuration findings evaluated within the lookback window.

        :param lookback_minutes: How far back (in minutes) to query. Should be
            comfortably larger than the function's own run interval so no
            findings are missed between runs; harmless duplicates are
            re-ingested on overlap.
        :return: List of configuration finding dictionaries.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        url = f"{self.api_base_url}/v2/organizations/{self.org_id}/configurations/findings/search"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=lookback_minutes)
        time_fmt = "%Y-%m-%dT%H:%M:%SZ"

        search_body = {
            "conditions": [
                {"field": "evaluation_time", "operator": "gt", "value": [window_start.strftime(time_fmt)]},
                {"field": "evaluation_time", "operator": "lt", "value": [now.strftime(time_fmt)]},
            ]
        }

        findings = self._fetch_paginated(url, search_body)
        findings = rename_reserved_columns(findings, _COLUMN_RENAME_MAP)
        logging.info("Fetched %d total configuration findings.", len(findings))
        return findings
