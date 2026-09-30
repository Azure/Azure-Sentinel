"""Upwind API client for fetching configuration (posture) findings."""

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


class UpwindConfigurationFindingsClient(UpwindClient):
    """Client for the Upwind configuration findings API."""

    def fetch_configuration_findings(self, lookback_minutes: int, on_page) -> int:
        """
        Fetch configuration findings evaluated within the lookback window.

        :param lookback_minutes: How far back (in minutes) to query. Should be
            comfortably larger than the function's own run interval so no
            findings are missed between runs; harmless duplicates are
            re-ingested on overlap.
        :param on_page: Callback invoked with each page of configuration findings.
        :return: Total number of configuration findings fetched.
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

        severities = severities_at_least(
            self.config.get("upwind_min_severity_config_findings")
        )
        if severities:
            search_body["conditions"].append(
                {"field": "severity", "operator": "in", "value": severities}
            )
            logging.info(
                "Filtering configuration findings to severities: %s", ", ".join(severities)
            )

        def emit(items):
            on_page(rename_reserved_columns(items, _COLUMN_RENAME_MAP))

        total = self._fetch_paginated(url, search_body, emit)
        logging.info("Fetched %d total configuration findings.", total)
        return total
