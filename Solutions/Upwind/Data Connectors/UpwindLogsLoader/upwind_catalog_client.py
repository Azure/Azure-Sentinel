"""Upwind API client for fetching catalog/inventory assets."""

import logging
from datetime import datetime, timedelta, timezone

from .upwind_client import UpwindClient


class UpwindCatalogClient(UpwindClient):
    """Client for the Upwind inventory catalog API."""

    def fetch_catalog_assets(self, lookback_minutes: int, on_page) -> int:
        """
        Fetch catalog assets updated within the lookback window from the Upwind
        inventory search API, across every asset category (compute, storage,
        network, database, container, IAM, etc.) - not just compute platform.

        Pulling only recently updated assets keeps each run small enough to
        finish inside the function timeout and under the inventory API's rate
        limit, instead of re-pulling the whole catalog every run.

        :param lookback_minutes: How far back (in minutes) to query by the
            asset's ``updated_at``. Should be larger than the function's own run
            interval so no updates are missed between runs; harmless duplicates
            are re-ingested on overlap.
        :param on_page: Callback invoked with each page of assets.
        :return: Total number of catalog assets fetched.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        url = (
            f"{self.api_base_url}/v2/organizations/{self.org_id}"
            f"/inventory/catalog/assets/search"
        )
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=lookback_minutes)
        time_fmt = "%Y-%m-%dT%H:%M:%SZ"

        # The "exists" check on `category` keeps every asset category in scope
        # (every asset has a category) rather than a compute_platform allowlist.
        search_body = {
            "conditions": [
                {
                    "field": "category",
                    "operator": "exists",
                },
                {
                    # Not listed in the public docs, but supported: updated_at
                    # filters on the asset's last change and takes epoch millis.
                    "field": "updated_at",
                    "operator": "gte",
                    "value": [int(window_start.timestamp() * 1000)],
                },
            ]
        }

        logging.info(
            "Fetching catalog assets updated since %s.", window_start.strftime(time_fmt)
        )

        total = self._fetch_paginated(url, search_body, on_page)
        logging.info("Fetched %d total catalog assets (all categories).", total)
        return total
