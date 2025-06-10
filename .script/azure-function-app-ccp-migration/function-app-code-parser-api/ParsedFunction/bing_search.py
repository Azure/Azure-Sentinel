from __future__ import annotations

from typing import Any, Dict, List, Tuple
import warnings
from requests.exceptions import SSLError
from requests.exceptions import HTTPError

import requests
from bs4 import BeautifulSoup


class BingWebSearcher:
    """Thin wrapper around Bing Web Search v7 REST API."""

    ENDPOINT_DEFAULT = "https://api.bing.microsoft.com/v7.0/search"
    SKIP_DOMAINS: Tuple[str, ...] = ("postman.com",)   # domains to exclude from results

    def __init__(
        self,
        subscription_key: str,
        endpoint: str | None = None,
        market: str = "en-US",
        timeout: int = 10,
    ) -> None:
        if not subscription_key:
            raise ValueError("Bing subscription key not provided")
        self.subscription_key = subscription_key
        self.endpoint = endpoint or self.ENDPOINT_DEFAULT
        self.market = market
        self.timeout = timeout
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}

    # --------------- public helpers -----------------

    def search(self, query: str, top: int = 5) -> List[Dict[str, Any]]:
        """Return the first `top` results for `query`."""
        params = {"q": query, "mkt": self.market, "count": top}
        response = requests.get(
            self.endpoint, headers=self.headers, params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("webPages", {}).get("value", [])

    @staticmethod
    def fetch_page_text(url: str, max_chars: int = 500) -> str | None:
        """
        Download `url` and return first `max_chars` visible characters.
        If the first request fails with an SSL handshake error, retry once with
        verify=False (controlled by env ALLOW_INSECURE_SSL).
        """
        headers = {
            # Some sites block the default python-requests UA string.
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }

        def _get(verify: bool = True):
            return requests.get(url, headers=headers, timeout=10, verify=verify)

        try:
            r = _get()                                         # 1st try – normal TLS
        except SSLError as ssl_exc:
            warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
            try:
                r = _get(verify=False)                     # 2nd try – insecure
            except Exception as exc:                       # still bad
                print(f"Error retrieving {url}: {exc}")
                return f"[Error retrieving {url}: {exc}]"
        except Exception as exc:                               # non-SSL errors
            print(f"Error retrieving {url}: {exc}")
            return None

        try:
            try:
                r.raise_for_status()
            except HTTPError as http_err:
                print(f"HTTP {http_err.response.status_code} retrieving {url}")
                return None
            soup = BeautifulSoup(r.text, "html.parser")
            visible_text = " ".join(soup.get_text(separator=' ').split())
            return visible_text[:max_chars] + ("…" if len(visible_text) > max_chars else "")
        except Exception as exc:
            print(f"Parse error on {url}: {exc}")
            return None

    def get_search_result_links(
        self, query: str, top: int = 5, skip_domains: Tuple[str, ...] = SKIP_DOMAINS
    ) -> List[str]:
        """
        Return up to *top* URL for *query*, skipping links that
        match *skip_domains*.
        """
        print(f"Getting search result links for query: {query}, top: {top}")
        batch_size = top * 3
        raw = self.search(query, top=batch_size)

        result: List[str] = []
        for item in raw:
            if len(result) >= top:
                break

            url = item.get("url", "")
            if any(d in url.lower() for d in skip_domains):
                continue

            txt = self.fetch_page_text(url)
            if txt is None:                                  # skipped due to HTTP / parse / SSL errors
                continue

            result.append(url)
        return result 
