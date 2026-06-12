"""Upwind API client for fetching catalog assets."""

import logging

from .upwind_client import UpwindClient


class UpwindCatalogClient(UpwindClient):
    """Client for the Upwind inventory catalog API."""

    def fetch_catalog_assets(self) -> list:
        """
        Fetch all catalog assets from the Upwind inventory search API.

        :return: List of catalog asset dictionaries.
        :raises RuntimeError: If the API returns errors after exhausting retries.
        """

        url = (
            f"{self.api_base_url}/v2/organizations/{self.org_id}"
            f"/inventory/catalog/assets/search"
        )
        search_body = {
            "conditions": [
                {
                    "field": "category",
                    "operator": "eq",
                    "value": ["compute_platform"],
                }
            ]
        }

        assets = self._fetch_paginated(url, search_body)
        logging.debug("Fetched %d total catalog assets.", len(assets))
        return assets
