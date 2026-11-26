"""
luminar_manager.py

Generic Luminar TAXII client SDK: a single ``LuminarManager`` class that owns
the whole retrieval pipeline

    Luminar API calls -> pagination -> batching -> sliding window
        -> reference resolution -> batched results

Intended usage from a platform client script::

    manager = LuminarManager(
        cognyte_client_id=...,
        cognyte_client_secret=...,
        cognyte_account_id=...,
        cognyte_base_url=...,
        added_after="2024-01-01T00:00:00.000000Z",  # default fetch-from
    )
    for feed_name in ("iocs", "leakedrecords", "cyberfeeds"):
        for batch in manager.get_objects(feed_name, added_after=checkpoint):
            ingest(batch["results"]["data"])                 # platform call
            save_checkpoint(feed_name,
                            batch["results"]["last_success"])

``get_objects()`` is a generator: it produces one resolved batch at a time
rather than accumulating an entire collection in memory. Each yield is

    {
        "results": {
            "data": [...],          # augmented records for this batch
            "last_success": "...",  # checkpoint for this batch
        },
        "error": None or "<error text>",
    }

``results["data"]`` is a fresh list per yield owned by the caller; persist
``results["last_success"]`` as the feed's resume checkpoint after ingesting.

Everything Anomali-related (Feed, Indicator, Report, FeedConfigManager, the
per-alias processors, IOC mappings/expirations and the ingest step) has been
removed. The algorithm itself is unchanged.
"""

from __future__ import annotations


import re
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

import requests

# -------------------------
# Logging
# -------------------------

import logging

logger = logging.getLogger(__name__)

# -------------------------
# Config / Constants
# -------------------------

TIMEOUT = 60.0

LUMINAR_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# API RETRY CONFIG
RETRY_ATTEMPTS = 3
RETRY_DELAY = 60  # seconds (1 minute)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

# Network-error retry for `next`-cursored page fetches.
# These are intentionally small: a `next` cursor has a ~2-minute TTL, so we
# must recover from a transient transport blip (ConnectionError, Timeout,
# SSLError, etc.) WITHOUT burning enough time to let the cursor go stale.
# This retry covers ONLY raised network exceptions; HTTP status handling
# (500 -> StaleCursorError, 429/502/503/504 -> execute_with_retry) is left to
# the caller and is deliberately untouched.
CURSOR_NETWORK_RETRY_ATTEMPTS = 2
CURSOR_NETWORK_RETRY_DELAY = 2  # seconds

# Stall guard for stale-cursor recovery. A persistent backend 500 already
# self-bounds (stale -> drop cursor -> fresh request -> 500 -> raise -> break),
# so this does NOT guard that case. It guards only the narrow no-progress
# stall: the fresh request keeps succeeding (HTTP 200) but the cursored
# follow-up keeps going stale (HTTP 500) AND the last-seen X-TAXII-Date-Added
# never advances, so each rebuild re-fetches the same slice forever. We abort
# only when last_added_seen fails to advance across this many CONSECUTIVE
# stale rebuilds; any forward progress resets the counter, so a healthy
# slow-but-degraded run (one batch per cycle) is never penalized.
MAX_STALE_REBUILDS_WITHOUT_PROGRESS = 5

EXPECTED_COLLECTION_ALIASES = ["iocs", "leakedrecords", "cyberfeeds"]

# -------------------------
# Luminar configuration (module-level globals)
# -------------------------
# These were read from feed.feed_config on the Anomali backend via
# FeedConfigManager.get(...). With the Anomali half removed there is no
# backend to read from, so they live here. Set them before calling luminar().

LUMINAR_BASE_URL = ""
LUMINAR_CLIENT_ID = ""
LUMINAR_CLIENT_SECRET = ""
LUMINAR_ACCOUNT_ID = ""
LUMINAR_INITIAL_FETCH_DATE = ""  # "YYYY-MM-DD"


# Resume checkpoints, one per alias -- the feed_config keys of the same names.
# Each holds the last_success value of a previously handled batch; leave blank
# to start that alias from LUMINAR_INITIAL_FETCH_DATE.
LAST_SUCCESS_IOCS_ADDED = ""
LAST_SUCCESS_LEAKEDRECORDS_ADDED = ""
LAST_SUCCESS_CYBERFEEDS_ADDED = ""

# Pagination / batching
DEFAULT_LIMIT = 9999

# User-Agent sent on every Luminar request when the caller does not pass one.
DEFAULT_USER_AGENT = "CognyteLuminar-TAXII-Client"
PAGES_PER_BATCH = 10

# Persistent cache for life of the manager (required), bounded to avoid
# unbounded memory growth on long-running / large-backfill runs.
HYDRATED_OBJECTS_MAX_SIZE = 50000

# STIX 2.x identifier shape: "<object-type>--<UUID>". Covers standard types
# (indicator--, identity--, ...) and custom x-* object types. A *_ref(s)
# property holding anything else is not a fetchable TAXII object id, so
# extract_relationship_refs drops it instead of poisoning a match[id] chunk
# (a single malformed id could make the server reject the whole request).
STIX_ID_PATTERN = re.compile(
    r"^[a-z][a-z0-9-]*--[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


# -------------------------
# Exceptions
# -------------------------


class LuminarAPIError(Exception):
    """Carries an already-formatted Luminar failure up to the caller.

    The message is exactly what lands in the response ``error`` key, i.e. one of

        "HTTP <status>: <API error message>"
        "Network error: <exception message>"
        "Invalid response from Luminar: <exception message>"

    It exists so a failure that survives every retry keeps its status code and
    API message instead of being flattened into a generic HTTPError or, worse,
    silently converted into an empty end-of-stream.
    """


class StaleCursorError(Exception):
    """Raised when a TAXII 'next' cursor has expired.

    Luminar signals this with HTTP 410 Gone:

        {"title": "Expired pagination token",
         "description": "The pagination token has expired. Please restart the
                         query from the beginning.",
         "http_status": "410"}

    The caller should drop the cursor and rebuild the request with
    `added_after` taken from the last successful X-TAXII-Date-Added-Last, so
    pagination restarts from that point instead of from the beginning."""


# -------------------------
# API client + pipeline
# -------------------------


class LuminarManager:
    """Manages interactions with the Cognyte Luminar TAXII API.

    Uses a single `requests.Session` for connection pooling and shared headers.
    The bearer token is stored on `self.session.headers["Authorization"]` after
    a successful auth call, so individual request callers don't need to plumb
    headers through.

    The class also owns the retrieval pipeline built on top of those calls:
    pagination (``fetch_page``), batching (``iter_page_batches``), reference
    resolution (``resolve_and_augment_batch``) and the sliding window
    (``iter_collection_batches``), plus the bounded
    hydrated-object LRU cache they share.
    """

    def __init__(
        self,
        cognyte_client_id: str,
        cognyte_client_secret: str,
        cognyte_account_id: str,
        cognyte_base_url: str,
        added_after: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        pages_per_batch: int = PAGES_PER_BATCH,
        match_id_batch_size: int = 100,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        # Strict input validation: bail out early instead of failing mid-pipeline.
        missing = [
            name
            for name, val in [
                ("client_id", cognyte_client_id),
                ("client_secret", cognyte_client_secret),
                ("account_id", cognyte_account_id),
                ("base_url", cognyte_base_url),
            ]
            if not isinstance(val, str) or not val.strip()
        ]
        if missing:
            raise ValueError(
                f"LuminarManager missing required parameters: {', '.join(missing)}"
            )

        # Tuning params must be positive ints (bool excluded: it is an int
        # subclass and would silently pass isinstance(True, int)).
        for name, val in [
            ("limit", limit),
            ("pages_per_batch", pages_per_batch),
            ("match_id_batch_size", match_id_batch_size),
        ]:
            if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
                raise ValueError(f"{name} must be a positive integer, got {val!r}")

        # Default fetch-from anchor; get_objects() may override it per feed.
        if added_after is not None:
            if not isinstance(added_after, str) or not added_after.strip():
                raise ValueError(
                    "added_after must be a non-empty ISO Z timestamp string"
                )
            added_after = added_after.strip()
            try:
                datetime.strptime(added_after, LUMINAR_DATE_FORMAT)
            except ValueError:
                raise ValueError(
                    "added_after must match LUMINAR_DATE_FORMAT "
                    f"({LUMINAR_DATE_FORMAT}), got {added_after!r}"
                )

        # Normalize base_url (drop trailing slashes).
        self.base_url = cognyte_base_url.strip().rstrip("/")
        self.account_id = cognyte_account_id.strip()
        self.client_id = cognyte_client_id.strip()
        self.client_secret = cognyte_client_secret.strip()

        # Pipeline configuration (instance-level defaults).
        self.added_after = added_after
        self.limit = limit
        self.pages_per_batch = pages_per_batch
        self.match_id_batch_size = match_id_batch_size

        self.payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "externalAPI/stix.readonly",
        }

        # Persistent session: connection pooling + central header management.
        # These headers apply to every Luminar API call by default.
        # access_token() overrides Content-Type per-call (x-www-form-urlencoded)
        # because that endpoint expects form-encoded payloads, not JSON.
        # User-Agent identifies the calling platform to Luminar; each
        # integration passes its own (e.g. "Sentinel").
        if not isinstance(user_agent, str) or not user_agent.strip():
            raise ValueError("user_agent must be a non-empty string")
        user_agent = user_agent.strip()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Content-Type": "application/json",
            }
        )

        self.taxi_collection: Dict[str, str] = {}

        # Bounded least-recently-used cache for hydrated STIX objects, keyed by
        # id, held as a plain OrderedDict on this instance (formerly the
        # module-level LRUCache/HYDRATED_OBJECTS).
        #
        # Purpose: avoid re-fetching cross-batch references within the sliding
        # window. References are overwhelmingly local (an object referenced by
        # a relationship sits within a batch or two of it), so the
        # most-recently touched entries carry the live re-reference value and
        # stale entries from thousands of batches ago are dead weight. Evicting
        # a still-needed entry is correctness-preserving: it just triggers an
        # idempotent match[id] re-fetch.
        #
        # Access rules, maintained inline by resolve_and_augment_batch:
        #   - ``oid in cache``     membership test; does NOT change recency, so
        #                          the skip-if-cached check never perturbs
        #                          eviction order
        #   - ``cache[oid]``       read; marks oid most-recently-used
        #   - ``cache[oid] = obj`` insert/update; marks oid most-recently-used
        #                          and evicts the least-recently-used entry
        #                          once the cache exceeds the cap
        # Last formatted Luminar failure ("HTTP <status>: <message>" or
        # "Network error: <message>"), recorded by _format_api_error(). Methods
        # whose return type cannot express a failure (access_token,
        # get_taxi_collections, get_objects_by_match_id) leave it here so the
        # status and API message are never lost.
        self.last_api_error: Optional[str] = None

        self.hydrated_objects: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
        self.hydrated_objects_max_size = HYDRATED_OBJECTS_MAX_SIZE

    # ----- auth -----

    def access_token(self) -> Optional[str]:
        """Obtain an access token using client credentials. Returns the token
        string on success, or None on any failure (no message returned)."""
        req_url = f"{self.base_url}/externalApi/v2/realm/{self.account_id}/token"
        try:
            logger.info("Requesting access token at %s", req_url)
            response = self.execute_with_retry(
                lambda: self.session.post(
                    req_url,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data=self.payload,
                    timeout=TIMEOUT,
                )
            )
            if not response.ok:
                logger.info(
                    "Error obtaining access token: %s",
                    self._format_api_error(response),
                )
                return None
            data = response.json() if response.content else {}
            if not isinstance(data, dict):
                self.last_api_error = (
                    "Invalid response from Luminar: unexpected token payload type "
                    f"{type(data).__name__}"
                )
                logger.error("%s", self.last_api_error)
                return None
            token = data.get("access_token")
            if isinstance(token, str) and token:
                return token
            self.last_api_error = (
                "Invalid response from Luminar: token response contained no "
                "access_token"
            )
            logger.error("%s", self.last_api_error)
            return None
        except requests.RequestException as err:
            self.last_api_error = f"Network error: {err}"
            logger.error("Error obtaining access token: %s", self.last_api_error)
            return None
        except (ValueError, KeyError) as err:
            self.last_api_error = f"Invalid response from Luminar: {err}"
            logger.error("Error obtaining access token: %s", self.last_api_error)
            return None

    def _refresh_token(self) -> bool:
        """Refresh the bearer token and update the session headers in-place.
        Returns True on success."""
        logger.info("Refreshing access token...")
        token = self.access_token()
        if not token:
            return False
        self.session.headers["Authorization"] = f"Bearer {token}"
        return True

    def set_bearer_token(self, token: str) -> None:
        """Install a bearer token on the session."""
        if not isinstance(token, str) or not token:
            raise ValueError("token must be a non-empty string")
        self.session.headers["Authorization"] = f"Bearer {token}"

    # ----- collections -----

    def get_taxi_collections(self) -> Dict[str, str]:
        """Fetch TAXII collection IDs and return a mapping of alias -> collection_id."""
        taxii_collection_ids: Dict[str, str] = {}
        req_url = f"{self.base_url}/externalApi/taxii/collections/"
        try:
            logger.info("Fetching TAXII collections at %s", req_url)
            response = self.execute_with_retry(
                lambda: self.session.get(req_url, timeout=TIMEOUT)
            )

            # One-shot 401 -> token refresh -> retry
            if response.status_code == 401 and self._refresh_token():
                response = self.execute_with_retry(
                    lambda: self.session.get(req_url, timeout=TIMEOUT)
                )

            if not response.ok:
                logger.info(
                    "Error fetching collections: %s",
                    self._format_api_error(response),
                )
                return taxii_collection_ids

            payload = response.json() if response.content else {}
            if not isinstance(payload, dict):
                self.last_api_error = (
                    "Invalid response from Luminar: unexpected collections payload "
                    f"type {type(payload).__name__}"
                )
                logger.error("%s", self.last_api_error)
                return taxii_collection_ids

            collections_data = payload.get("collections", []) or []
            if not isinstance(collections_data, list):
                logger.error("Unexpected 'collections' type: %s", type(collections_data))
                return taxii_collection_ids

            logger.info("Cognyte Luminar collections: %s", collections_data)
            for collection in collections_data:
                if not isinstance(collection, dict):
                    continue
                alias = collection.get("alias")
                collection_id = collection.get("id")
                if isinstance(alias, str) and isinstance(collection_id, str):
                    taxii_collection_ids[alias] = collection_id
        except requests.RequestException as err:
            self.last_api_error = f"Network error: {err}"
            logger.error("Error fetching collections: %s", self.last_api_error)
        except (ValueError, KeyError) as err:
            self.last_api_error = f"Invalid response from Luminar: {err}"
            logger.error("Error fetching collections: %s", self.last_api_error)
        return taxii_collection_ids

    # ----- objects -----

    def get_objects_by_match_id(
        self,
        collection_id: str,
        object_ids: Sequence[str],
        batch_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch objects from a TAXII collection in chunks by match[id]."""
        all_objects: List[Dict[str, Any]] = []
        if not collection_id or not object_ids:
            return all_objects
        if batch_size is None:
            batch_size = self.match_id_batch_size

        url = f"{self.base_url}/externalApi/taxii/collections/{collection_id}/objects/"
        logger.info(
            "Fetching objects by match[id] in chunks of %d for collection_id=%s",
            batch_size,
            collection_id,
        )

        ids_list = list(object_ids)
        for i in range(0, len(ids_list), batch_size):
            chunk = ids_list[i : i + batch_size]
            params = {"match[id]": ",".join(chunk), "limit": len(chunk)}

            try:
                logger.info(
                    "Fetching match[id] chunk %d for collection_id=%s",
                    (i // batch_size) + 1,
                    collection_id,
                )
                response = self.execute_with_retry(
                    lambda p=params: self.session.get(url, params=p, timeout=TIMEOUT)
                )

                if response.status_code == 401 and self._refresh_token():
                    response = self.execute_with_retry(
                        lambda p=params: self.session.get(
                            url, params=p, timeout=TIMEOUT
                        )
                    )

                if not response.ok:
                    logger.info(
                        "Error fetching match[id] chunk %d: %s",
                        (i // batch_size) + 1,
                        self._format_api_error(response),
                    )
                    # Hydration failure is not fatal: other chunks still run and
                    # any unresolved refs simply stay unresolved.
                    continue

                data = response.json() if response.content else {}
                if not isinstance(data, dict):
                    logger.error("Unexpected match[id] payload type: %s", type(data))
                    continue
                objs = data.get("objects", []) or []
                if isinstance(objs, list):
                    all_objects.extend(o for o in objs if isinstance(o, dict))
            except (requests.RequestException, ValueError, KeyError) as err:
                logger.info(
                    "Error fetching match[id] chunk %d: %s",
                    (i // batch_size) + 1,
                    err,
                )
                # Continue with other chunks rather than failing the whole pipeline.
                continue

        return all_objects

    def fetch_page(
        self,
        collection_id: str,
        params: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str], Optional[str]]:
        """
        Fetch a single page from the TAXII objects endpoint.

        Returns: (objects, next_token, last_added, first_added)

        Special handling when the request is using a `next` cursor: an expired
        cursor comes back as HTTP 410 Gone ("Expired pagination token"), which
        is terminal for that cursor, so we do NOT retry it. Instead we raise
        StaleCursorError so the caller can rebuild a fresh request using
        `added_after` from the last successful header value.

        A 500 on a cursored request is an ordinary server error, not an expired
        cursor, and is retried like any other retryable status.
        """
        if not collection_id:
            raise ValueError("collection_id is required")
        if not isinstance(params, dict):
            raise ValueError("params must be a dict")

        url = f"{self.base_url}/externalApi/taxii/collections/{collection_id}/objects/"
        using_next = "next" in params and params.get("next")

        try:
            if using_next:
                # No retry on 410 when using a next cursor: the pagination token
                # has expired and will never come back. We DO retry
                # transport-level errors (dropped packet, TLS glitch, brief
                # timeout) via _get_with_network_retry, with short delays so a
                # recovered request can't blow the cursor TTL. Status codes are
                # still interpreted here, unchanged.
                response = self._get_with_network_retry(url, params)
                if response.status_code == 410:
                    # Format it too: recovery is automatic, but the reason is
                    # worth keeping in last_api_error for diagnostics.
                    raise StaleCursorError(self._format_api_error(response))
                if response.status_code == 401:
                    if self._refresh_token():
                        response = self._get_with_network_retry(url, params)
                        if response.status_code == 410:
                            raise StaleCursorError(
                                self._format_api_error(response)
                                + " (after token refresh)"
                            )
                # Retry on retryable codes (429, 500, 502, 503, 504). 410 is not
                # retryable and has already been raised above.
                if response.status_code in RETRYABLE_STATUS_CODES:
                    response = self.execute_with_retry(
                        lambda: self.session.get(url, params=params, timeout=TIMEOUT)
                    )
            else:
                response = self.execute_with_retry(
                    lambda: self.session.get(url, params=params, timeout=TIMEOUT)
                )
                if response.status_code == 401 and self._refresh_token():
                    response = self.execute_with_retry(
                        lambda: self.session.get(url, params=params, timeout=TIMEOUT)
                    )

            if not response.ok:
                # Retries are already exhausted here, so this is the page's
                # final outcome. Keep the status and the API's own message.
                error_text = self._format_api_error(response)
                logger.info(
                    "Page fetch failed with params %s: %s",
                    self._sanitize_params_for_log(params),
                    error_text,
                )
                raise LuminarAPIError(error_text)

            payload = response.json() if response.content else {}
            if not isinstance(payload, dict):
                # `objects` and `next` are unreadable, so treating this as an
                # empty page would silently end pagination. Fail loudly instead.
                error_text = (
                    "Invalid response from Luminar: unexpected page payload type "
                    f"{type(payload).__name__}"
                )
                self.last_api_error = error_text
                logger.error("%s", error_text)
                raise LuminarAPIError(error_text)

            objs = payload.get("objects", []) or []
            if not isinstance(objs, list):
                logger.error("Unexpected 'objects' type: %s", type(objs))
                objs = []
            objs = [o for o in objs if isinstance(o, dict)]

            next_token = payload.get("next")
            if next_token is not None and not isinstance(next_token, str):
                next_token = str(next_token)

            last_added = response.headers.get("X-TAXII-Date-Added-Last")
            first_added = response.headers.get("X-TAXII-Date-Added-First")
            return objs, next_token, last_added, first_added

        except (StaleCursorError, LuminarAPIError):
            raise
        except requests.RequestException as err:
            # No usable response was received, so there is no HTTP status to
            # report. Never invent one.
            error_text = f"Network error: {err}"
            self.last_api_error = error_text
            logger.info(
                "Error fetching page with params %s: %s",
                self._sanitize_params_for_log(params),
                error_text,
            )
            raise LuminarAPIError(error_text) from err
        except (ValueError, KeyError) as err:
            error_text = f"Invalid response from Luminar: {err}"
            self.last_api_error = error_text
            logger.info(
                "Error fetching page with params %s: %s",
                self._sanitize_params_for_log(params),
                error_text,
            )
            raise LuminarAPIError(error_text) from err

    # ----- retry -----

    def _get_with_network_retry(
        self,
        url: str,
        params: Dict[str, Any],
        retries: int = CURSOR_NETWORK_RETRY_ATTEMPTS,
        delay: int = CURSOR_NETWORK_RETRY_DELAY,
    ) -> requests.Response:
        """
        GET that retries ONLY on transport-layer exceptions
        (requests.RequestException: ConnectionError, Timeout, SSLError,
        ChunkedEncodingError, ...), with short delays.

        This exists for the `next`-cursored page fetch path, where we must not
        route through execute_with_retry: a 410 there means an expired
        pagination token (the caller turns it into StaleCursorError), and
        execute_with_retry's 60s delay would risk expiring an otherwise-valid
        cursor. A dropped packet, however, is not a stale cursor, so we recover
        from it here.

        Status codes are NOT inspected: the returned response is handed back
        as-is for the caller to interpret (410 -> stale, 429/5xx -> its own
        retry). Only raised exceptions are retried; on final failure the last
        exception is re-raised.
        """
        last_err: Optional[requests.RequestException] = None
        for attempt in range(1, retries + 1):
            try:
                return self.session.get(url, params=params, timeout=TIMEOUT)
            except requests.RequestException as err:
                last_err = err
                logger.info(
                    "Cursored GET raised %s on attempt %d of %d",
                    err.__class__.__name__,
                    attempt,
                    retries,
                )
                if attempt < retries:
                    time.sleep(delay)
                    continue
                logger.error("Cursored GET failed after %d attempts: %s", retries, err)
                raise
        # Unreachable when retries >= 1: the loop returns on success or raises
        # on the final attempt. Explicit guard (not assert, so it survives
        # `python -O`) covers a degenerate retries < 1 call.
        if last_err is not None:
            raise last_err
        raise RuntimeError(
            "_get_with_network_retry exited without a response " f"(retries={retries})"
        )

    def execute_with_retry(
        self,
        request_call: Callable[[], requests.Response],
        retries: int = RETRY_ATTEMPTS,
        delay: int = RETRY_DELAY,
    ) -> requests.Response:
        """
        Execute a request callable with retry on retryable HTTP statuses and
        on network/transport exceptions.

        - Retries when response.status_code in RETRYABLE_STATUS_CODES.
        - Retries on requests.RequestException (network, timeout, etc.).
        - Sleeps `delay` seconds between attempts.
        - On final failure: returns the last response if any, else re-raises
          the last network exception.

        Always returns a requests.Response or raises; never returns None.

        Note: 410 on a `next`-cursored objects call is handled separately in
        fetch_page (no retry there) because the pagination token is gone.
        """
        last_response: Optional[requests.Response] = None

        for attempt in range(1, retries + 1):
            try:
                logger.info("API request attempt %d of %d", attempt, retries)
                response = request_call()
                last_response = response

                if response.status_code in RETRYABLE_STATUS_CODES:
                    if attempt < retries:
                        logger.info(
                            "Request returned HTTP %d (%s); retrying in %ds",
                            response.status_code,
                            response.reason,
                            delay,
                        )
                        time.sleep(delay)
                        continue
                    logger.info(
                        "Request returned HTTP %d (%s) after %d attempts",
                        response.status_code,
                        response.reason,
                        retries,
                    )
                return response

            except requests.RequestException as err:
                logger.info(
                    "Request raised %s on attempt %d of %d",
                    err.__class__.__name__,
                    attempt,
                    retries,
                )
                if attempt < retries:
                    time.sleep(delay)
                    continue
                logger.error("Request failed after %d attempts: %s", retries, err)
                if last_response is not None:
                    return last_response
                raise

        # Unreachable when retries >= 1: every iteration returns, continues, or
        # raises, and the final attempt returns (retryable status) or raises
        # (network error). Explicit guard (not assert, so it survives
        # `python -O`) covers a degenerate retries < 1 call.
        if last_response is not None:
            return last_response
        raise RuntimeError(
            f"execute_with_retry exited without a response (retries={retries})"
        )

    # ----- helpers -----

    def _sanitize_params_for_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a copy of request params safe/compact for logging.

        The TAXII `next` cursor is an opaque ~250+ char token that bloats log
        lines and carries no diagnostic value in full. Truncate it to a tail
        preview (matching the convention used in iter_page_batches); leave
        `limit` / `added_after` intact.
        """
        if not isinstance(params, dict):
            return params
        safe = dict(params)
        nxt = safe.get("next")
        if isinstance(nxt, str) and len(nxt) > 42:
            safe["next"] = f"\u2026{nxt[-42:]}"
        return safe

    def _format_api_error(self, response: requests.Response) -> str:
        """Build "HTTP <status>: <API error message>" from a failed response.

        The response body is inspected first for an API-provided error message;
        if it does not carry one, we fall back to the HTTP reason phrase rather
        than dumping the raw body. The formatted text is also recorded in
        self.last_api_error.
        """
        status = getattr(response, "status_code", None)
        message = ""

        try:
            body = response.json() if response.content else None
        except ValueError:
            body = None

        if isinstance(body, dict):
            for key in (
                "description",
                "title",
            ):
                value = body.get(key)
                if isinstance(value, str) and value.strip():
                    message = value.strip()
                    break

        if not message:
            reason = getattr(response, "reason", None)
            if isinstance(reason, str) and reason.strip():
                message = reason.strip()
            else:
                message = "Unknown error"

        formatted = f"HTTP {status}: {message}"
        self.last_api_error = formatted
        return formatted

    @staticmethod
    def _normalise_timestamp(ts: str) -> str:
        """Return `ts` with exactly six fractional digits and a trailing Z.

        The Luminar server rejects any other fractional precision with HTTP
        400 even though `strptime` with %f accepts 1-6 digits, so a checkpoint
        saved with millisecond precision must be widened before it is sent.
        """
        return datetime.strptime(ts, LUMINAR_DATE_FORMAT).strftime(
            LUMINAR_DATE_FORMAT
        )

    def _subtract_one_second(self, ts: str) -> str:
        """
        Subtract 1 second from an ISO Z timestamp and return in the same format.
        Used to apply a small overlap buffer when rebuilding a stale cursor,
        so we won't miss records due to sub-second boundaries.
        On any parsing failure, returns the original timestamp unchanged.
        """
        if not ts or not isinstance(ts, str):
            return ts
        try:
            dt = datetime.strptime(ts, LUMINAR_DATE_FORMAT) - timedelta(seconds=1)
            return dt.strftime(LUMINAR_DATE_FORMAT)
        except (ValueError, TypeError) as err:
            logger.error("Could not subtract 1s from timestamp '%s': %s", ts, err)
            return ts

    def create_lookup_dict(
        self,
        list_of_dicts: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Create a lookup dictionary from a list of dictionaries, keyed by 'id'."""
        return {d["id"]: d for d in list_of_dicts if "id" in d}

    def extract_relationship_refs(
        self,
        records: List[Dict[str, Any]],
    ) -> Set[str]:
        """Extract unique object references from all STIX reference properties.

        STIX expresses object references through top-level properties ending
        in ``_ref`` (a single id string) or ``_refs`` (a list of id strings):
        ``source_ref``/``target_ref`` on relationships, ``object_refs`` on
        reports/groupings/notes/opinions, ``created_by_ref``,
        ``object_marking_refs``, ``sighting_of_ref``, ``sample_refs``, etc.
        Scanning by suffix covers every standard and custom ref property,
        where a fixed per-type allowlist silently missed e.g.
        ``vulnerability.created_by_ref``. ``external_references`` is not a
        ref property (it holds embedded dicts, not ids) and does not match
        either suffix, so it is correctly excluded.
        """
        refs: Set[str] = set()
        dropped: Set[str] = set()
        for r in records:
            if not isinstance(r, dict):
                continue
            for key, value in r.items():
                candidates: List[str] = []
                if key.endswith("_ref") and isinstance(value, str):
                    candidates = [value]
                elif key.endswith("_refs") and isinstance(value, list):
                    candidates = [x for x in value if isinstance(x, str)]
                for ref in candidates:
                    if ref and STIX_ID_PATTERN.match(ref):
                        refs.add(ref)
                    elif ref:
                        dropped.add(ref)

        if dropped:
            logger.info(
                "Skipped %d non-STIX-id ref value(s) (not fetchable via "
                "match[id]): %s",
                len(dropped),
                sorted(dropped)[:10],
            )
        return refs

    # ----- batching -----

    def iter_page_batches(
        self,
        collection_id: str,
        start_added_after: str,
        pages_per_batch: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterator[Tuple[List[Dict[str, Any]], str]]:
        """
        Yields (batch_records, last_added_seen) every `pages_per_batch` pages
        fetched from the TAXII objects endpoint. Any partial trailing batch
        (fewer than `pages_per_batch` pages because the stream ended) is also
        yielded once before the iterator stops.

        Pagination:
          - First call: GET ...objects/?limit=<limit>&added_after=<start_added_after>
          - Subsequent calls: include the `next` cursor returned by the previous page.
          - On every successful page, we record X-TAXII-Date-Added-Last (or fall
            back to X-TAXII-Date-Added-First) as the "checkpoint of last seen".

        Stale `next` cursor recovery:
          - When the `next` cursor expires the server returns HTTP 410 Gone
            ("Expired pagination token"). `fetch_page` raises StaleCursorError.
          - On StaleCursorError we DROP the cursor and rebuild a fresh request
            using `added_after = last_seen_X-TAXII-Date-Added-Last`. We do NOT
            increment the page counter for the failed call — only successful pages
            count toward the batch.
        """
        if not isinstance(start_added_after, str) or not start_added_after:
            raise ValueError("start_added_after must be a non-empty ISO Z timestamp")

        if pages_per_batch is None:
            pages_per_batch = self.pages_per_batch
        if limit is None:
            limit = self.limit

        added_after = start_added_after
        next_token: Optional[str] = None
        last_added_seen: Optional[str] = None

        batch: List[Dict[str, Any]] = []
        pages_in_batch = 0

        # No-progress stall tracking (see MAX_STALE_REBUILDS_WITHOUT_PROGRESS).
        # We remember the last_added_seen value as of the previous stale rebuild;
        # if a rebuild happens and the value hasn't advanced, we count it. Any
        # advance resets the counter.
        stale_rebuilds_without_progress = 0
        last_added_at_prev_rebuild: Optional[str] = None

        while True:
            params: Dict[str, Any] = {"limit": limit, "added_after": added_after}
            if next_token:
                params["next"] = next_token

            # Log what we're about to fetch with a running page counter so the
            # progress within a 10-page batch is obvious in the log. The
            # `next` cursor changes every call; we show its tail to prove we're
            # not stuck on the same cursor.
            attempted_page = pages_in_batch + 1
            next_preview = f"{next_token[-42:]}\u2026" if next_token else "\u2014"
            logger.info(
                "Fetching page=%d/%d collection_id=%s next=%s added_after=%s",
                attempted_page,
                pages_per_batch,
                collection_id,
                next_preview,
                added_after,
            )

            try:
                objs, new_next, last_added, first_added = self.fetch_page(
                    collection_id, params
                )
            except StaleCursorError as err:
                # The next cursor expired (HTTP 410) mid-pagination while there
                # is still more data to fetch (more=true). Rebuild a fresh
                # `added_after` from the last successful X-TAXII-Date-Added-Last
                # we observed, minus a 1-second safety buffer to avoid any
                # sub-second gap at the boundary. Any duplicates this introduces
                # are harmless: the hydrated-object cache dedupes by id.
                if last_added_seen:
                    rebuild_anchor = self._subtract_one_second(last_added_seen)
                    logger.info(
                        "Stale next cursor (%s). Rebuilding with "
                        "added_after=%s (last_added=%s minus 1s buffer)",
                        err,
                        rebuild_anchor,
                        last_added_seen,
                    )
                else:
                    # No successful page yet in this iter call; reuse the
                    # caller-provided anchor unchanged.
                    rebuild_anchor = added_after
                    logger.info(
                        "Stale next cursor (%s) before any successful page. "
                        "Reusing added_after=%s",
                        err,
                        rebuild_anchor,
                    )
                added_after = rebuild_anchor
                next_token = None

                # No-progress stall detection. If this rebuild's last_added_seen is
                # the same as the previous rebuild's (or still None), we made no
                # forward progress; otherwise reset the counter. Abort only after
                # MAX_STALE_REBUILDS_WITHOUT_PROGRESS consecutive no-progress
                # rebuilds, so a healthy run that advances one batch per cycle is
                # never aborted.
                if (
                    last_added_seen is not None
                    and last_added_seen != last_added_at_prev_rebuild
                ):
                    stale_rebuilds_without_progress = 0
                else:
                    stale_rebuilds_without_progress += 1
                last_added_at_prev_rebuild = last_added_seen

                if (
                    stale_rebuilds_without_progress
                    >= MAX_STALE_REBUILDS_WITHOUT_PROGRESS
                ):
                    logger.info(
                        "Stale-cursor recovery made no progress across %d consecutive "
                        "rebuilds (last_added stuck at %s). Aborting iteration to avoid "
                        "an infinite loop; the checkpoint stays at the last returned "
                        "batch and the next run will resume from there.",
                        stale_rebuilds_without_progress,
                        last_added_seen,
                    )
                    # Emit any partial batch accumulated so far, then report
                    # the abort so the caller sees why iteration stopped.
                    if batch:
                        yield batch, (last_added_seen or added_after)
                    stall_error = (
                        "Stale-cursor recovery made no progress across "
                        f"{stale_rebuilds_without_progress} consecutive rebuilds "
                        f"(last_added={last_added_seen}); "
                        f"last API error: {self.last_api_error}"
                    )
                    self.last_api_error = stall_error
                    raise LuminarAPIError(stall_error)

                # Do not increment pages_in_batch; loop again.
                continue
            except LuminarAPIError as err:
                logger.error("Unrecoverable fetch error; stopping iteration: %s", err)
                # The server crashed / stopped responding part-way through.
                # Hand back every page successfully fetched before the failure,
                # together with the last X-TAXII-Date-Added header the server
                # actually returned. The caller can then persist that header as
                # its checkpoint, and the next run resumes at the page that
                # failed. Nothing already retrieved is thrown away.
                if batch:
                    logger.info(
                        "Returning %d record(s) from the %d page(s) fetched "
                        "before the failure; checkpoint=%s",
                        len(batch),
                        pages_in_batch,
                        last_added_seen or added_after,
                    )
                    yield batch, (last_added_seen or added_after)
                # Re-raise so the formatted "HTTP <status>: <message>" reaches
                # the caller's `error` key instead of looking like a clean end
                # of stream.
                raise

            # Track last-seen header for checkpointing and stale-cursor recovery.
            la_seen = last_added or first_added
            if isinstance(la_seen, str) and la_seen:
                last_added_seen = la_seen

            if objs:
                batch.extend(objs)

            pages_in_batch += 1
            next_token = new_next

            # Yield a full batch whenever we've accumulated pages_per_batch pages.
            if pages_in_batch >= pages_per_batch:
                if batch:
                    yield batch, (last_added_seen or added_after)
                batch = []
                pages_in_batch = 0

            # End of stream: emit trailing partial batch (if any) and stop.
            if not next_token:
                if batch:
                    yield batch, (last_added_seen or added_after)
                logger.info("Stream exhausted. Ending iteration.")
                break

    # ----- hydration: resolve missing IDs via prev/next, cache, match[id] -----

    def resolve_and_augment_batch(
        self,
        collection_id: str,
        target_batch: List[Dict[str, Any]],
        prev_batch: Optional[List[Dict[str, Any]]],
        next_batch: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Returns an augmented record list for `target_batch` only:
        - Includes:
            * all relationship objects from target_batch
            * all non-relationship objects from target_batch
            * any referenced objects found in prev/next by ID
            * any referenced objects found in the hydrated-object cache
            * any newly hydrated objects fetched via match[id]
        - Does NOT include prev/next relationship objects, to avoid pulling in
          other batches' records unintentionally.

        Correctness note (eviction safety):
            Every referenced object needed for THIS batch is first resolved into a
            local dict (`resolved`) that is never subject to eviction. Only after
            the batch is fully resolved do we write those objects into the bounded
            hydrated-object LRU (for cross-batch reuse). This makes correctness
            independent of the LRU's max size: a batch that references more distinct
            objects than the cache can hold (missing > max size) still resolves
            completely, because we read from `resolved`, not from the LRU. The LRU
            cap only governs how much cross-batch history is retained afterward.
        """

        # Lookups for quick ID resolution
        target_lookup = self.create_lookup_dict(
            [x for x in target_batch if x.get("id")]
        )
        prev_lookup = self.create_lookup_dict(
            [x for x in (prev_batch or []) if x.get("id")]
        )
        next_lookup = self.create_lookup_dict(
            [x for x in (next_batch or []) if x.get("id")]
        )

        # Extract refs from all *_ref/_refs properties in target batch
        refs = self.extract_relationship_refs(target_batch)

        # Resolve every needed ref into a LOCAL dict before touching the LRU.
        # Reads from the LRU happen here (before any insert), so an entry that was
        # a cache hit can't be evicted out from under us by this batch's own inserts.
        resolved: Dict[str, Dict[str, Any]] = {}
        still_missing: List[str] = []
        for oid in refs:
            if oid in target_lookup:
                # Already present in the target batch itself; no need to attach.
                continue
            if oid in prev_lookup:
                resolved[oid] = prev_lookup[oid]
            elif oid in next_lookup:
                resolved[oid] = next_lookup[oid]
            elif oid in self.hydrated_objects:
                # Membership above does not reorder; the read below does.
                # Read NOW, while it's still resident, into the eviction-proof dict.
                self.hydrated_objects.move_to_end(oid)
                resolved[oid] = self.hydrated_objects[oid]
            else:
                still_missing.append(oid)

        # Hydrate the genuinely-missing refs via match[id].
        if still_missing:
            try:
                hydrated = self.get_objects_by_match_id(collection_id, still_missing)
            except Exception as err:
                logger.error("Hydration via match[id] failed: %s", err)
                hydrated = []
            for obj in hydrated:
                oid = obj.get("id") if isinstance(obj, dict) else None
                if oid:
                    resolved[oid] = obj

        # Now update the cross-batch LRU. Eviction here is harmless: everything
        # this batch needs is already held in `resolved`. The LRU exists only to
        # serve FUTURE batches, so retaining the most-recently-resolved objects is
        # exactly the right policy.
        #
        # Eviction runs per insert (exactly as LRUCache.__setitem__ did), not
        # once after the loop, so the cache never transiently exceeds its cap
        # even when `resolved` is far larger than the cap itself. The
        # `self.hydrated_objects and` guard replaces the old
        # LRUCache.__init__ `max_size <= 0` validation: a non-positive cap now
        # empties the cache instead of raising KeyError on popitem.
        for oid, obj in resolved.items():
            if oid in self.hydrated_objects:
                self.hydrated_objects.move_to_end(oid)
            self.hydrated_objects[oid] = obj
            # Evict the oldest entries until back within the cap.
            while (
                self.hydrated_objects
                and len(self.hydrated_objects) > self.hydrated_objects_max_size
            ):
                evicted_key, _ = self.hydrated_objects.popitem(last=False)
                logger.info(
                    "Hydrated-object cache evicted least-recently-used id=%s",
                    evicted_key,
                )

        # Build augmented list:
        # - all target records
        # - plus each referenced object resolved above (complete, never evicted)
        augmented: List[Dict[str, Any]] = list(target_batch)
        for oid in refs:
            if oid in target_lookup:
                continue
            obj = resolved.get(oid)
            if obj is not None:
                augmented.append(obj)

        return augmented

    # ----- client-facing feed API -----

    def get_objects(
        self,
        feed_name: str,
        added_after: Optional[str] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Client-facing generator: yield resolved batches for a feed alias.

        `feed_name` is a TAXII collection alias (e.g. "iocs",
        "leakedrecords", "cyberfeeds"). `added_after` overrides the
        instance-level default for this feed only -- pass the persisted
        per-feed checkpoint to resume, or omit to use the constructor value.

        Authentication and collection discovery happen lazily on first use:
        the bearer token is fetched if the session has none, and the
        alias -> collection_id map is fetched once and cached on
        `self.taxi_collection`.

        Yields one dict per resolved batch:

            {
                "results": {
                    "data": [...],          # augmented STIX objects
                    "last_success": "...",  # checkpoint for this batch
                },
                "error": None or "<error text>",
            }

        Consume `results["data"]` inside the loop (ingest into the
        platform), then persist `results["last_success"]` as the feed's
        resume checkpoint. A non-None `error` marks the final yield of a
        run that failed part-way; batches already yielded remain valid.

        Raises ValueError for a blank feed_name, an unknown alias, or a
        missing/malformed added_after; raises LuminarAPIError if the
        initial token request fails.
        """
        if not isinstance(feed_name, str) or not feed_name.strip():
            raise ValueError("feed_name must be a non-empty string")
        feed_name = feed_name.strip()

        # Authenticate lazily: the first call obtains a token; later calls
        # reuse it and mid-run 401s are handled per-request by
        # _refresh_token().
        if "Authorization" not in self.session.headers:
            if not self._refresh_token():
                raise LuminarAPIError(
                    self.last_api_error or "Failed to obtain Luminar access token"
                )

        # Resolve alias -> collection_id, discovering collections once.
        if not self.taxi_collection:
            self.taxi_collection = self.get_taxi_collections()
        collection_id = self.taxi_collection.get(feed_name)
        if not collection_id:
            raise ValueError(
                f"Unknown feed_name {feed_name!r}; available aliases: "
                f"{sorted(self.taxi_collection) or 'none discovered'}"
            )

        anchor = added_after or self.added_after
        if not anchor or not isinstance(anchor, str):
            raise ValueError(
                "added_after is required: pass it to get_objects() or set it "
                "on the LuminarManager constructor"
            )
        try:
            anchor = self._normalise_timestamp(anchor)
        except ValueError:
            raise ValueError(
                "added_after must match LUMINAR_DATE_FORMAT "
                f"({LUMINAR_DATE_FORMAT}), got {anchor!r}"
            )

        yield from self.iter_collection_batches(collection_id, anchor)

    # ----- sliding window engine per collection -----

    def iter_collection_batches(
        self,
        collection_id: str,
        added_after: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Page-wise batching + 3-batch sliding window. GENERATOR: yields one
        result dict per resolved batch.

        Each batch = up to `pages_per_batch` pages from iter_page_batches.
        Sliding window holds at most 3 such batches: [prev, center, next].

        Startup:    resolve B1 using B2 + B3 as ref-lookup context.
        Steady:     resolve the center batch using prev + next as context,
                    then drop prev, shift the window, fetch a new next batch.
        Tail (>3):  on StopIteration after steady, resolve the final center
                    batch using the previous (already yielded) batch as
                    reference context -- prev must NOT be merged back in or
                    its records would be delivered twice.
        Small (<=3): if iter exhausted during preload, merge all and resolve once.

        Each yield has the shape:

            {
                "results": {
                    "data": [...],          # this batch's augmented records
                    "last_success": "...",  # this batch's checkpoint
                },
                "error": None or "<error text>",
            }

        `last_success` is the X-TAXII-Date-Added-Last of the batch just
        resolved (NOT the latest fetched batch); persist it after consuming
        `data` to resume from it on the next run. `results["data"]` is a
        fresh list owned by the caller. A non-None `error` marks the final
        yield of a run that failed part-way; batches already yielded remain
        valid.
        """
        # Reset the cross-batch hydration cache at the start of every run.
        # STIX references never cross collections (an `iocs` relationship cannot
        # reference a `cyberfeeds` object), so entries from a previous collection
        # have no re-reference value here and would only occupy LRU slots. The
        # LRU cap bounds growth WITHIN a large collection; this reset bounds
        # growth ACROSS collections. The two are complementary.
        self.hydrated_objects.clear()
        self.last_api_error = None
        logger.info("Cleared hydration cache at start of collection_id=%s", collection_id)

        api_error: Optional[str] = None

        def _result(
            data: List[Dict[str, Any]],
            last_success: Optional[str],
            error: Optional[str],
        ) -> Dict[str, Any]:
            return {
                "results": {
                    # Copy so the caller owns the list: the local buffers are
                    # cleared right after the yield for memory hygiene.
                    "data": list(data),
                    "last_success": last_success,
                },
                "error": error,
            }

        try:
            page_iter = self.iter_page_batches(collection_id, added_after)
        except ValueError as err:
            logger.error("Cannot start iteration for collection_id=%s: %s", collection_id, err)
            yield _result([], None, str(err))
            return

        batches: List[List[Dict[str, Any]]] = []
        batch_last_addeds: List[str] = []
        exhausted = False

        # Preload up to 3 batches
        for _ in range(3):
            try:
                batch, last_added_to_save = next(page_iter)
                batches.append(batch)
                batch_last_addeds.append(last_added_to_save)
                logger.info(
                    "Fetched batch #%d collection_id=%s records=%d last_added=%s",
                    len(batches),
                    collection_id,
                    len(batch),
                    last_added_to_save,
                )
            except StopIteration:
                exhausted = True
                break
            except Exception as err:
                logger.info(
                    "Error fetching batch during preload for collection_id=%s: %s",
                    collection_id,
                    err,
                )
                api_error = (
                    str(err)
                    if isinstance(err, LuminarAPIError)
                    else f"{err.__class__.__name__}: {err}"
                )
                # Fetching is over for this run, so fall through to the
                # merge-and-resolve path and deliver whatever was already
                # retrieved rather than losing it.
                exhausted = True
                break

        if not batches:
            logger.warning("No batches to process for collection_id=%s", collection_id)
            if api_error:
                # Surface the preload failure on the error channel instead of
                # ending the generator silently.
                yield _result([], None, api_error)
            return

        # Case 3: Small dataset (<=3 batches total) and fetching complete
        if exhausted:
            logger.info(
                "Small dataset for collection_id=%s; merging %d batch(es) and "
                "returning once.",
                collection_id,
                len(batches),
            )
            merged: List[Dict[str, Any]] = []
            for b in batches:
                merged.extend(b)
            augmented = self.resolve_and_augment_batch(
                collection_id, merged, None, None
            )
            result = _result(augmented, batch_last_addeds[-1], api_error)
            logger.info(
                "Batch ready for processing: collection_id=%s records=%d "
                "last_success=%s error=%s",
                collection_id,
                len(result["results"]["data"]),
                result["results"]["last_success"],
                result["error"],
            )
            yield result

            # Cleanup aggressively
            augmented.clear()
            del augmented
            merged.clear()
            del merged
            for b in batches:
                b.clear()
            batches.clear()
            del batches
            return

        # We have exactly 3 batches loaded and more may be available.
        B1, B2, B3 = batches[0], batches[1], batches[2]

        # Phase A: Startup (resolve B1 using B2 + B3 as context)
        logger.info("Startup resolving B1 (collection_id=%s)", collection_id)
        augmented_B1 = self.resolve_and_augment_batch(collection_id, B1, None, B2 + B3)
        result = _result(augmented_B1, batch_last_addeds[0], None)
        logger.info(
            "Batch ready for processing: collection_id=%s records=%d "
            "last_success=%s error=%s",
            collection_id,
            len(result["results"]["data"]),
            result["results"]["last_success"],
            result["error"],
        )
        yield result
        augmented_B1.clear()
        del augmented_B1
        # Keep B1 in memory; B2 will need it as prev context.

        # Steady-state
        prev_batch = B1
        center_batch = B2
        next_batch = B3
        center_idx = (
            1  # index into batch_last_addeds for the batch currently being resolved
        )

        while True:
            # Phase B: resolve center batch using prev and next
            logger.info(
                "Steady resolving CENTER (collection_id=%s) batch_idx=%d",
                collection_id,
                center_idx,
            )
            augmented_center = self.resolve_and_augment_batch(
                collection_id,
                center_batch,
                prev_batch,
                next_batch,
            )
            result = _result(augmented_center, batch_last_addeds[center_idx], None)
            logger.info(
                "Batch ready for processing: collection_id=%s records=%d "
                "last_success=%s error=%s",
                collection_id,
                len(result["results"]["data"]),
                result["results"]["last_success"],
                result["error"],
            )
            yield result
            augmented_center.clear()
            del augmented_center

            # Drop prev batch from memory now that we no longer need it.
            logger.info(
                "Memory cleanup: dropping PREV batch (collection_id=%s)", collection_id
            )
            prev_batch.clear()
            del prev_batch

            # Shift window: prev <- center, center <- next, next <- fetched
            prev_batch = center_batch
            center_batch = next_batch
            center_idx += 1

            # Fetch next batch
            try:
                new_batch, new_last_added = next(page_iter)
                next_batch = new_batch
                batch_last_addeds.append(new_last_added)
                logger.info(
                    "Fetched next batch collection_id=%s records=%d last_added=%s",
                    collection_id,
                    len(next_batch),
                    new_last_added,
                )
            except StopIteration:
                # Tail end: prev_batch was already delivered as the previous
                # CENTER; only center_batch is still unprocessed. Resolve it
                # with prev as reference context -- merging prev back in would
                # re-deliver all of its records to the caller.
                logger.info(
                    "No more records; tail end for collection_id=%s. Resolving "
                    "final batch.",
                    collection_id,
                )

                augmented_tail = self.resolve_and_augment_batch(
                    collection_id,
                    center_batch,
                    prev_batch,
                    None,
                )
                result = _result(augmented_tail, batch_last_addeds[-1], None)
                logger.info(
                    "Batch ready for processing: collection_id=%s records=%d "
                    "last_success=%s error=%s",
                    collection_id,
                    len(result["results"]["data"]),
                    result["results"]["last_success"],
                    result["error"],
                )
                yield result

                # Cleanup everything
                augmented_tail.clear()
                del augmented_tail

                prev_batch.clear()
                center_batch.clear()
                del prev_batch
                del center_batch

                try:
                    next_batch.clear()
                except AttributeError:
                    next_batch = []

                break
            except Exception as err:
                logger.info(
                    "Error fetching next batch (collection_id=%s); flushing what we "
                    "have. %s",
                    collection_id,
                    err,
                )
                api_error = (
                    str(err)
                    if isinstance(err, LuminarAPIError)
                    else f"{err.__class__.__name__}: {err}"
                )
                # Don't lose what's already in memory: resolve the still
                # unprocessed center_batch with prev as context (prev was
                # already yielded, so merging it back in would duplicate
                # its records).
                try:
                    augmented_tail = self.resolve_and_augment_batch(
                        collection_id,
                        center_batch,
                        prev_batch,
                        None,
                    )
                    result = _result(augmented_tail, batch_last_addeds[-1], api_error)
                    logger.info(
                        "Batch ready for processing: collection_id=%s records=%d "
                        "last_success=%s error=%s",
                        collection_id,
                        len(result["results"]["data"]),
                        result["results"]["last_success"],
                        result["error"],
                    )
                    yield result
                    augmented_tail.clear()
                except Exception as inner:
                    logger.info(
                        "Failed to flush tail after fetch error for collection_id=%s: "
                        "%s",
                        collection_id,
                        inner,
                    )
                break


# -------------------------
# Main orchestration
# -------------------------


def luminar() -> None:
    """Reference client: fetch all configured feeds from Luminar TAXII.

    Demonstrates the intended SDK usage pattern -- platform integrations
    should copy this shape::

        manager = LuminarManager(client_id, secret, account_id, base_url,
                                 added_after=<initial fetch date>)
        for feed_name in aliases:
            for batch in manager.get_objects(feed_name,
                                             added_after=<feed checkpoint>):
                ingest(batch["results"]["data"])
                save_checkpoint(feed_name,
                                batch["results"]["last_success"])

    Configuration comes from the module globals (formerly feed.feed_config):
    LUMINAR_* credentials, LUMINAR_INITIAL_FETCH_DATE, and the per-alias
    LAST_SUCCESS_<ALIAS>_ADDED resume checkpoints.

    Any per-feed failure is isolated so the remaining feeds still run.
    """
    try:
        logger.info("Starting execution of program at: %s", datetime.now().isoformat())

        # --- 1. Read Luminar credentials from module globals ----------------

        luminar_base_url = LUMINAR_BASE_URL
        luminar_client_id = LUMINAR_CLIENT_ID
        luminar_client_secret = LUMINAR_CLIENT_SECRET
        luminar_account_id = LUMINAR_ACCOUNT_ID
        luminar_initial_fetch_date_raw = LUMINAR_INITIAL_FETCH_DATE
        if not all(
            [
                luminar_base_url,
                luminar_client_id,
                luminar_client_secret,
                luminar_account_id,
                luminar_initial_fetch_date_raw,
            ]
        ):
            logger.info(
                "Luminar credentials missing. Set these module globals: "
                "LUMINAR_BASE_URL, LUMINAR_CLIENT_ID, LUMINAR_CLIENT_SECRET, "
                "LUMINAR_ACCOUNT_ID, LUMINAR_INITIAL_FETCH_DATE."
            )
            return

        luminar_initial_fetch_date = (
            f"{str(luminar_initial_fetch_date_raw).strip()}T00:00:00.000000Z"
        )
        try:
            datetime.strptime(luminar_initial_fetch_date, LUMINAR_DATE_FORMAT)
        except ValueError:
            logger.info(
                "Invalid initial_fetch_date format. Expected YYYY-MM-DD. Got: %s",
                luminar_initial_fetch_date_raw,
            )
            return

        # --- 2. Init Luminar manager -----------------------------------------

        try:
            luminar_manager = LuminarManager(
                str(luminar_client_id),
                str(luminar_client_secret),
                str(luminar_account_id),
                str(luminar_base_url),
                added_after=luminar_initial_fetch_date,
            )
        except ValueError as err:
            logger.error("Failed to initialize LuminarManager: %s", err)
            return

        # --- 3. Run each feed: get_objects yields resolved batches -----------

        last_success = {
            "iocs": LAST_SUCCESS_IOCS_ADDED,
            "leakedrecords": LAST_SUCCESS_LEAKEDRECORDS_ADDED,
            "cyberfeeds": LAST_SUCCESS_CYBERFEEDS_ADDED,
        }
        logger.info(
            "Resume checkpoints: %s. "
            "Aliases without a checkpoint will start from initial_fetch_date=%s.",
            last_success,
            luminar_initial_fetch_date_raw,
        )

        for alias in EXPECTED_COLLECTION_ALIASES:
            checkpoint = last_success.get(alias) or None
            logger.info(
                "=== Fetching feed alias=%s added_after=%s ===",
                alias,
                checkpoint or luminar_initial_fetch_date,
            )
            try:
                for result in luminar_manager.get_objects(
                    alias, added_after=checkpoint
                ):
                    data = result["results"]["data"]
                    batch_checkpoint = result["results"]["last_success"]
                    # ================= PROCESSING / INGESTION HOOK ==========
                    # Ingest `data` into the platform here, then persist
                    # `batch_checkpoint` as the feed's resume checkpoint
                    # (formerly last_success_<alias>_added).
                    # ======================================================
                    logger.info(
                        "Batch received: alias=%s records=%d last_success=%s "
                        "error=%s",
                        alias,
                        len(data),
                        batch_checkpoint,
                        result["error"],
                    )
                    if result["error"]:
                        # Final yield of a failed run; the resume checkpoint
                        # stays at the last successfully ingested batch.
                        break
            except (LuminarAPIError, ValueError) as err:
                logger.error("Error processing alias=%s: %s", alias, err)
                # Continue with the next alias rather than aborting the run.
                continue
            logger.info("Finished alias=%s.", alias)

        logger.info("Execution ended at: %s", datetime.now().isoformat())

    except Exception as err:
        logger.error("Fatal error: %s", err)


if __name__ == "__main__":
    luminar()
