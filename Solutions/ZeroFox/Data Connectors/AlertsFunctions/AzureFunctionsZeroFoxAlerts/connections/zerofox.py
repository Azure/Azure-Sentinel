import logging
from typing import Generator, List, Dict, Any

import requests

from connections.exceptions import ApiResponseException

TIMEOUT = 60


class ZeroFoxClient:
    """ZeroFox API client for the Alerts API (v1.0)."""

    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        self._base_url = "https://api.zerofox.com"

    def get_alerts(
        self,
        last_modified_min_date: str,
        last_modified_max_date: str,
        page_size: int = 100,
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Fetch alerts from ZeroFox API with pagination.

        Args:
            last_modified_min_date: ISO format datetime string for min date filter
            last_modified_max_date: ISO format datetime string for max date filter
            page_size: Number of results per page (default 100)

        Yields:
            List of alert dictionaries for each page
        """
        url = f"{self._base_url}/1.0/alerts/"
        headers = self._get_request_headers()
        offset = 0

        while True:
            params = {
                "last_modified_min_date": last_modified_min_date,
                "last_modified_max_date": last_modified_max_date,
                "sort_direction": "asc",
                "offset": offset,
                "limit": page_size,
            }

            response = self._http_request(
                method="GET",
                url=url,
                headers=headers,
                params=params,
                timeout=TIMEOUT,
            )

            alerts = response.get("alerts", [])
            if not alerts:
                break

            yield alerts

            # Check if there are more pages
            if len(alerts) < page_size:
                break

            offset += page_size

    def _http_request(
        self,
        method: str,
        url: str,
        timeout: float = TIMEOUT,
        **kwargs,
    ) -> Dict[str, Any]:
        """Wrap request method for handling status codes."""
        response = requests.request(
            method=method,
            url=url,
            timeout=timeout,
            **kwargs,
        )
        if response.status_code != 200:
            logging.error(f"Failed to {method} {url}. Response: {response.text}")
            raise ApiResponseException(method, url=url, res=response)
        return response.json()

    def _get_request_headers(self) -> Dict[str, str]:
        """Get headers for API requests using API Key auth."""
        return {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "zf-source": "Microsoft-Sentinel",
            "User-Agent": "Microsoft-Sentinel-ZeroFox-Connector",
        }
