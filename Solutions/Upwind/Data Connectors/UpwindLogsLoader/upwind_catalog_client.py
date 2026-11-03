"""Upwind API client for fetching catalog/inventory assets."""

import logging
from datetime import datetime

from .upwind_client import UpwindClient

# The "exists" check on `category` keeps every asset category in scope (every
# asset has a category) rather than a compute_platform allowlist.
_ALL_CATEGORIES_CONDITION = {"field": "category", "operator": "exists"}


class UpwindCatalogClient(UpwindClient):
    """Client for the Upwind inventory catalog API."""

    def __init__(self, config, time_budget=None):
        super().__init__(config, time_budget)
        # The catalog search endpoint accepts up to 200 items per page.
        self.page_size = config.get("upwind_catalog_page_size", self.page_size)

    def _catalog_search_url(self) -> str:
        return (
            f"{self.api_base_url}/v2/organizations/{self.org_id}"
            f"/inventory/catalog/assets/search"
        )

    def fetch_catalog_assets(self, window_start: datetime, on_page) -> int:
        """
        Fetch catalog assets updated within the run's time window from the
        Upwind inventory search API, across every asset category (compute,
        storage, network, database, container, IAM, etc.) - not just compute
        platform.

        Pulling only recently updated assets keeps each run small enough to
        finish inside the function timeout and under the inventory API's rate
        limit, instead of re-pulling the whole catalog every run. Assets that
        don't change are covered by the periodic full sync
        (``fetch_catalog_assets_full``).

        :param window_start: Start of the run's time window, shared by every
            dataset in the run; assets are matched by ``updated_at``.
        :param on_page: Callback invoked with each page of assets.
        :return: Total number of catalog assets fetched.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        time_fmt = "%Y-%m-%dT%H:%M:%SZ"
        search_body = {
            "conditions": [
                _ALL_CATEGORIES_CONDITION,
                {
                    # updated_at takes epoch millis.
                    "field": "updated_at",
                    "operator": "gte",
                    "value": [int(window_start.timestamp() * 1000)],
                },
            ]
        }

        logging.info(
            "Fetching catalog assets updated since %s.", window_start.strftime(time_fmt)
        )

        total = self._fetch_paginated(self._catalog_search_url(), search_body, on_page)
        logging.info("Fetched %d total catalog assets (all categories).", total)
        return total

    def fetch_catalog_assets_full(self, start_cursor, on_page, on_cursor) -> int:
        """
        Fetch every catalog asset, regardless of when it last changed,
        resuming from ``start_cursor`` when one is given.

        A full pull of a large organization doesn't fit in one run, so the
        caller saves the cursor reported through ``on_cursor`` and passes it
        back in a later run to continue where this one stopped.

        :param start_cursor: Cursor saved by an earlier run, or None to start
            from the first page.
        :param on_page: Callback invoked with each page of assets.
        :param on_cursor: Callback invoked with the next page's cursor after
            each page (None once the last page has been fetched).
        :return: Number of catalog assets fetched in this call.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        search_body = {"conditions": [_ALL_CATEGORIES_CONDITION]}

        logging.info(
            "%s full catalog sync.", "Resuming" if start_cursor else "Starting"
        )

        total = self._fetch_paginated(
            self._catalog_search_url(),
            search_body,
            on_page,
            start_cursor=start_cursor,
            on_cursor=on_cursor,
        )
        logging.info("Full catalog sync fetched %d assets in this run.", total)
        return total
