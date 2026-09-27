"""Dataverse OData request helpers."""

import logging
from typing import Generator

import requests


def get_data(
    client: requests.Session, request_url: str, timeout: int
) -> requests.Response:
    """Get data from the OData API without rebuilding its continuation URL."""
    try:
        response = client.get(url=request_url, timeout=timeout)
        response.raise_for_status()
    except requests.Timeout as exc:
        logging.error("Request timed out: %s", exc)
        raise
    except requests.HTTPError as exc:
        response = exc.response
        logging.error(
            "HTTP error: %s, %s",
            response.status_code if response is not None else "unknown",
            response.text if response is not None else str(exc),
        )
        raise
    return response


def get_all_data(
    client: requests.Session, request_url: str, timeout: int
) -> Generator[list, None, None]:
    """Yield every OData page while treating @odata.nextLink as opaque."""
    while request_url:
        logging.info("GET %s", request_url)
        response_json = get_data(client, request_url, timeout).json()
        data = response_json.get("value")
        if data:
            yield data
        request_url = response_json.get("@odata.nextLink")
