"""Upwind API client for fetching catalog/inventory assets."""

import logging

from .upwind_client import UpwindClient


class UpwindCatalogClient(UpwindClient):
    """Client for the Upwind inventory catalog API."""

    def fetch_catalog_assets(self) -> list:
        """
        Fetch all catalog assets from the Upwind inventory search API, across
        every asset category (compute, storage, network, database, container,
        IAM, etc.) - not just compute platform.

        :return: List of catalog asset dictionaries.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        url = (
            f"{self.api_base_url}/v2/organizations/{self.org_id}"
            f"/inventory/catalog/assets/search"
        )
        # The search endpoint requires a non-empty conditions array, so an
        # "exists" check on `category` is used as a match-everything filter
        # (every asset has a category) rather than a compute_platform allowlist.
        search_body = {
            "conditions": [
                {
                    "field": "category",
                    "operator": "exists",
                }
            ]
        }

        assets = self._fetch_paginated(url, search_body)
        logging.info("Fetched %d total catalog assets (all categories).", len(assets))
        return assets
