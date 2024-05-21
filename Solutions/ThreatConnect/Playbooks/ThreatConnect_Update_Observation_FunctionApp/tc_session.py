"""TcEx Framework Module"""

import logging

import urllib3
from requests import Session, adapters
from urllib3.util.retry import Retry

from hmac_auth import HmacAuth

# get logger
_logger = logging.getLogger(__name__.split(".", maxsplit=1)[0])

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore


class TcSession(Session):
    """ThreatConnect REST API Requests Session"""

    def __init__(
        self,
        auth: HmacAuth,
        base_url: str | None = None,
        proxies: dict[str, str] | None = None,
        proxies_enabled: bool | None = False,
        user_agent: dict | None = None,
        verify: bool | str | None = True,
    ):
        """Initialize the Class properties."""
        super().__init__()
        self.base_url = base_url.strip("/") if base_url is not None else base_url
        self.log = _logger

        # configure auth
        self.auth = auth

        # configure optional headers
        if user_agent:
            self.headers.update(user_agent)

        # configure proxy
        if proxies and proxies_enabled:
            self.proxies = proxies

        # configure verify
        self.verify = verify

        # Add Retry
        self.retry()

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Override request method disabling verify on token renewal if disabled on session."""
        response = super().request(method, self.url(url), **kwargs)

        # retry request in case we encountered a race condition with token renewal monitor
        if response.status_code == 401:
            self.log.debug(
                "Unexpected response received while attempting to send a request using internal "
                "session object. Retrying request. feature=tc-session, "
                f"request-url={response.request.url}, status-code={response.status_code}"
            )
            response = super().request(method, self.url(url), **kwargs)

        # log request and response data
        self.log.debug(
            f"feature=tc-session, method={method}, request-url={response.request.url}, "
            f"status-code={response.status_code}, elapsed={response.elapsed}"
        )

        return response

    def retry(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        """Add retry to Requests Session

        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry
        """
        retries = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        # mount all https requests
        self.mount("https://", adapters.HTTPAdapter(max_retries=retries))

    def url(self, url: str) -> str:
        """Return appropriate URL string.

        The method allows the session to accept the URL Path or the full URL.
        """
        if not url.startswith("https"):
            return f"{self.base_url}{url}"
        return url
