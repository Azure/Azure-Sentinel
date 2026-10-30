"""Rubrik Security Cloud (RSC) client used by the Violation classification gate.

Resolves a snapshot for an object and returns its policy-hit count. Used only to
decide whether to ingest the original webhook payload; it ingests nothing itself.
"""
import inspect
import datetime
import requests
from shared_code.consts import (
    LOGS_STARTS_WITH,
    LOG_FORMAT,
    RUBRIK_INSTANCE_URL,
    RUBRIK_CLIENT_ID,
    RUBRIK_CLIENT_SECRET,
    RSC_HTTP_TIMEOUT,
    RSC_RESOLVE_SNAPSHOT_QUERY,
    RSC_HIT_COUNT_QUERY,
)
from shared_code.logger import applogger
from shared_code.rubrik_exception import (
    RubrikException,
    RubrikAuthenticationException,
)

FUNCTION_NAME = "RubrikClassificationActivity"


class RubrikDSPM:
    """Minimal RSC GraphQL client for the classification hit-count gate."""

    def __init__(self):
        """Validate RSC config and prepare endpoints."""
        __method_name = inspect.currentframe().f_code.co_name
        if not (RUBRIK_INSTANCE_URL and RUBRIK_CLIENT_ID and RUBRIK_CLIENT_SECRET):
            message = (
                "RSC configuration missing: set RubrikInstanceUrl, RubrikClientId, "
                "RubrikClientSecret app settings."
            )
            applogger.error(
                LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, message)
            )
            raise RubrikException(message)
        self.base_url = RUBRIK_INSTANCE_URL.rstrip("/")
        self.token_url = "{}/api/client_token".format(self.base_url)
        self.graphql_url = "{}/api/graphql".format(self.base_url)
        self.token = None

    def get_token(self):
        """Exchange client credentials for a bearer token."""
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Requesting RSC bearer token: POST {}".format(self.token_url),
            )
        )
        resp = requests.post(
            self.token_url,
            json={"client_id": RUBRIK_CLIENT_ID, "client_secret": RUBRIK_CLIENT_SECRET},
            headers={"Content-Type": "application/json"},
            timeout=RSC_HTTP_TIMEOUT,
        )
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "RSC token response: HTTP {}".format(resp.status_code),
            )
        )
        if resp.status_code == 401:
            raise RubrikAuthenticationException("RSC token request returned 401 (bad credentials).")
        if resp.status_code < 200 or resp.status_code > 299:
            raise RubrikException(
                "RSC token request failed: {} {}".format(resp.status_code, resp.text)
            )
        self.token = resp.json().get("access_token")
        if not self.token:
            raise RubrikAuthenticationException("RSC token response missing access_token.")
        return self.token

    def _graphql(self, query, variables):
        """POST a GraphQL query, checking HTTP status and the errors array."""
        resp = requests.post(
            self.graphql_url,
            json={"query": query, "variables": variables},
            headers={
                "Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json",
            },
            timeout=RSC_HTTP_TIMEOUT,
        )
        if resp.status_code == 401:
            raise RubrikAuthenticationException("RSC GraphQL returned 401.")
        if resp.status_code < 200 or resp.status_code > 299:
            raise RubrikException(
                "RSC GraphQL HTTP error: {} {}".format(resp.status_code, resp.text)
            )
        body = resp.json()
        if body.get("errors"):
            raise RubrikException("RSC GraphQL errors: {}".format(body["errors"]))
        return body.get("data", {})

    @staticmethod
    def _round_up_to_minute(event_timestamp):
        """Round an ISO-8601 timestamp UP to the next whole minute, return ISO Z string."""
        ts = event_timestamp.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(ts)
        if dt.second or dt.microsecond:
            dt = dt.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
        return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def resolve_snapshot(self, object_id, event_timestamp):
        """Return the snapshot id closest to (before) the rounded-up event time, or None."""
        __method_name = inspect.currentframe().f_code.co_name
        before_time = self._round_up_to_minute(event_timestamp)
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Resolving snapshot: object_id={}, event_timestamp={}, "
                "beforeTime={}".format(object_id, event_timestamp, before_time),
            )
        )
        data = self._graphql(
            RSC_RESOLVE_SNAPSHOT_QUERY,
            {"snappableId": object_id, "beforeTime": before_time},
        )
        results = data.get("allSnapshotsClosestToPointInTime") or []
        if not results:
            applogger.debug(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH,
                    FUNCTION_NAME,
                    __method_name,
                    "No snapshot returned for object_id={} (beforeTime={}).".format(
                        object_id, before_time
                    ),
                )
            )
            return None
        first = results[0] or {}
        if first.get("error"):
            applogger.debug(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH,
                    FUNCTION_NAME,
                    __method_name,
                    "Snapshot resolution error for object_id={} (beforeTime={}): "
                    "{}".format(object_id, before_time, first.get("error")),
                )
            )
            return None
        snap = first.get("snapshot") or {}
        snapshot_id = snap.get("id")
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Resolved snapshot_id={} for object_id={} (snapshot date={}, "
                "beforeTime={}).".format(
                    snapshot_id, object_id, snap.get("date"), before_time
                ),
            )
        )
        return snapshot_id

    def count_hits(self, object_id, snapshot_id):
        """Return policyObj.rootFileResult.hits.totalHits (0 if absent)."""
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Counting hits: object_id={}, snapshot_id={}".format(
                    object_id, snapshot_id
                ),
            )
        )
        data = self._graphql(
            RSC_HIT_COUNT_QUERY,
            {"snappableFid": object_id, "snapshotFid": snapshot_id},
        )
        policy_obj = data.get("policyObj") or {}
        root = policy_obj.get("rootFileResult") or {}
        hits = root.get("hits") or {}
        total = hits.get("totalHits")
        hit_count = int(total) if total is not None else 0
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Hit count for object_id={}, snapshot_id={}: totalHits={}".format(
                    object_id, snapshot_id, hit_count
                ),
            )
        )
        return hit_count

    def get_hit_count(self, object_id, event_timestamp):
        """Full gate: token -> resolve snapshot -> count hits. Never raises (fail-closed)."""
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Starting hit-count gate for object_id={}, "
                "event_timestamp={}".format(object_id, event_timestamp),
            )
        )
        try:
            self.get_token()
            snapshot_id = self.resolve_snapshot(object_id, event_timestamp)
            if not snapshot_id:
                return {
                    "snapshotId": None,
                    "hitCount": 0,
                    "error": "snapshot not resolved for object {}".format(object_id),
                }
            hit_count = self.count_hits(object_id, snapshot_id)
            return {"snapshotId": snapshot_id, "hitCount": hit_count, "error": None}
        except (RubrikException, requests.RequestException, ValueError) as err:
            applogger.error(
                LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
            )
            return {"snapshotId": None, "hitCount": 0, "error": str(err)}
