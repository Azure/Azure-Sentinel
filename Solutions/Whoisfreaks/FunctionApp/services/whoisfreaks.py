import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models.feed import FeedConfig
from utils.csv_parser import parse_csv, parse_domain_list

STATUS_URLS = {
    "v3.4": "https://files.whoisfreaks.com/v3.4/status",
    "v3.3": "https://files.whoisfreaks.com/v3.3/status",
}

_RETRY = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET",),
    raise_on_status=False,
)


def _build_session() -> requests.Session:
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=_RETRY)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class WhoisFreaksClient:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        self.session = _build_session()

    def get_status(self, api_version: str = "v3.4") -> dict:
        """
        Fetch the WhoisFreaks status document for a given API version.

        Threat feeds (malware/phishing/spam) are served from v3.4 and
        their status lives in the v3.4 document. NRD feeds are served
        from v3.3 and their "newly" section lives in the v3.3 document.
        Callers must request the version that matches the feed being
        looked up (see FeedConfig.status_api_version) -- the two
        documents are not guaranteed to contain each other's sections.
        """
        status_url = STATUS_URLS.get(api_version)
        if status_url is None:
            raise ValueError(f"Unknown WhoisFreaks status API version: {api_version}")

        logging.info("Requesting WhoisFreaks status: version=%s", api_version)
        response = self.session.get(
            status_url,
            headers=self.headers,
            timeout=60,
        )
        logging.info("WhoisFreaks status response: %s", response.status_code)
        response.raise_for_status()
        return response.json()

    def get_latest_feed_date(self, feed: FeedConfig, status: dict) -> str:
        status_name = feed.status_name or feed.name
        try:
            feed_status = status[feed.status_section][status_name]
            return feed_status["last_update"]
        except KeyError as exc:
            raise RuntimeError(
                f"Feed '{feed.name}' is not available at status path "
                f"'{feed.status_section}.{status_name}'."
            ) from exc

    def fetch_page(
        self,
        feed: FeedConfig,
        feed_date: str,
        offset: int,
    ) -> tuple[list[dict], int]:
        params = {
            feed.date_parameter: feed_date,
            "offset": offset,
            "limit": feed.page_size,
        }

        is_without_whois = feed.name in {
            "nrd_gtld_without_whois",
            "nrd_cctld_without_whois",
        }

        # Explicit lowercase strings: requests would serialize Python
        # bool True/False as "True"/"False", which some WhoisFreaks
        # endpoints treat as invalid and silently ignore.
        if feed.name in {"nrd_gtld_with_whois", "nrd_cctld_with_whois"}:
            params["whois"] = "true"
        elif is_without_whois:
            params["whois"] = "false"

        logging.info(
            "Fetching feed=%s date=%s offset=%s limit=%s",
            feed.name,
            feed_date,
            offset,
            feed.page_size,
        )

        response = self.session.get(
            feed.endpoint,
            headers=self.headers,
            params=params,
            timeout=120,
        )

        logging.info(
            "WhoisFreaks feed=%s response=%s",
            feed.name,
            response.status_code,
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        # NOTE: a 2xx response with an HTML/JSON error body would pass a
        # loose "text" check (text/html matches "text"). Only accept the
        # specific content types WhoisFreaks actually returns for feed
        # data, never a bare "text" match.
        accepted_content = (
            "csv" in content_type
            or "text/plain" in content_type
            or (is_without_whois and "octet-stream" in content_type)
        )

        if not accepted_content:
            raise RuntimeError(
                f"Unexpected Content-Type '{content_type}' from "
                f"feed={feed.name}; expected a CSV or domain-list response. "
                "Aborting this page rather than ingesting it."
            )

        # raw_count is the pre-filter line/row count used by the
        # processor for offset advancement and last-page detection.
        # For CSV, DictReader already skips the header, so len(records)
        # equals the data-row count the API intended. For domain lists,
        # parse_domain_list filters header/invalid lines, so we must
        # advance offset by raw_count, not len(records).
        if is_without_whois:
            records, raw_count = parse_domain_list(response.text)
        else:
            records = parse_csv(response.text)
            raw_count = len(records)

        if raw_count == 0:
            logging.info(
                "Feed=%s date=%s offset=%s returned 0 records",
                feed.name,
                feed_date,
                offset,
            )
            return records, 0

        # Expected columns are feed-specific. These are the *mandatory*
        # columns the normalizer relies on; every one must be present,
        # not just one of them (a response missing most expected columns
        # must fail loudly rather than silently ingesting nulls).
        expected_columns = {
            "malware": {"domain"},
            "spam": {"domain"},
            "phishing": {"domain"},
            "nrd_gtld_with_whois": {
                "num",
                "domain_name",
                "query_time",
                "create_date",
                "update_date",
                "expiry_date",
            },
            "nrd_cctld_with_whois": {
                "num",
                "domain_name",
                "query_time",
                "create_date",
                "update_date",
                "expiry_date",
            },
            "nrd_gtld_without_whois": {"domain_name"},
            "nrd_cctld_without_whois": {"domain_name"},
        }

        # threat_type/threat and domain/domain_name are accepted aliases
        # in the normalizer (see services/normalizer.py) because the
        # true WhoisFreaks CSV header for these has not been confirmed
        # against a live account. At least one spelling of each aliased
        # field must be present so a genuine schema mismatch still fails
        # fast instead of silently producing null fields.
        alias_columns = {
            "malware": [{"threat_type", "threat"}],
            "spam": [{"threat_type", "threat"}],
            "phishing": [{"threat_type", "threat"}],
        }

        required_columns = expected_columns.get(feed.name)

        if required_columns:
            received_columns = set(records[0].keys())

            missing_required = required_columns - received_columns
            missing_aliases = [
                group
                for group in alias_columns.get(feed.name, [])
                if not (group & received_columns)
            ]

            if missing_required or missing_aliases:
                raise RuntimeError(
                    f"Feed={feed.name} response is missing expected "
                    f"columns: required={sorted(missing_required)} "
                    f"alias_groups_missing={[sorted(g) for g in missing_aliases]}. "
                    f"Received columns: {list(records[0].keys())}"
                )

        logging.info(
            "Feed=%s date=%s offset=%s successfully parsed %s records (raw_count=%s)",
            feed.name,
            feed_date,
            offset,
            len(records),
            raw_count,
        )

        return records, raw_count