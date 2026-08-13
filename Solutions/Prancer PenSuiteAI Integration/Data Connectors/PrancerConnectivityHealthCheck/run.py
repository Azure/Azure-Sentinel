"""
Azure Function App - Prancer Connectivity Health Check

Prancer's backend (pac-result-receiver) pushes security findings directly into a
customer's PrancerFindings_CL Log Analytics table via the Azure Monitor Logs
Ingestion API and a Data Collection Rule (DCR) auto-provisioned by Prancer's
in-product connectivity wizard. That is a push architecture with no polling
connector, which means nothing on the customer side independently verifies that
ingestion is still working: if a DCR role assignment is revoked, a workspace is
reconfigured, or Prancer's backend has an outage, the customer has no signal
other than noticing PrancerFindings_CL has gone stale.

This Function runs on a timer schedule (default every 6 hours) and:
  1. Queries the customer's own PrancerFindings_CL table via the Log Analytics
     Query API for max(TimeGenerated).
  2. Compares the age of the most recent row against a configurable staleness
     threshold (default 48 hours - scan cadence varies by customer, so this
     does not assume near-real-time freshness).
  3. Reports the result through a channel that does NOT depend on the same
     DCR/table being healthy:
       a. POSTs a status payload to a configurable webhook URL (Teams
          incoming webhook, Slack incoming webhook, or a generic HTTP
          endpoint). This is the primary, DCR-independent signal.
       b. If the Log Analytics query itself succeeded (i.e. workspace/API
          access is fine - the data may be stale OR fresh), also writes a
          lightweight status row into a SEPARATE, purpose-built table,
          PrancerConnectivityHealth_CL, via the Logs Ingestion API, using a
          SEPARATE, simpler DCR/DCE from the one used for PrancerFindings_CL.
          A failure specific to the findings DCR must not also take out the
          health signal, so the two paths are deliberately decoupled. This
          also lets customers build a native Sentinel analytic rule on
          "no healthy check-in in N hours" if they want in-product alerting
          in addition to the webhook.
  4. Authenticates using the same service-principal client-credentials
     pattern already established elsewhere in this solution: client ID +
     client secret + tenant ID -> OAuth2 client_credentials grant against
     https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token.
       - Log Analytics Query API calls use scope https://api.loganalytics.io/.default
       - Logs Ingestion API calls use scope https://monitor.azure.com/.default
         (per https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview)

Application Settings (configured by the ARM template / Function App configuration):
    WORKSPACE_ID               - GUID of the Log Analytics workspace hosting
                                  PrancerFindings_CL (used for the Query API URL).
    WORKSPACE_NAME              - Optional human-readable label for the workspace,
                                  used in webhook messages. Falls back to WORKSPACE_ID.
    TENANT_ID                   - Azure AD Tenant ID.
    CLIENT_ID                   - App Registration (Service Principal) Client ID.
    CLIENT_SECRET                - App Registration Client Secret.
    STALENESS_THRESHOLD_HOURS  - Hours after which the most recent finding is
                                  considered stale. Default: 48.
    HEALTH_CHECK_WEBHOOK_URL    - Optional but strongly recommended. Teams
                                  incoming webhook / Slack incoming webhook /
                                  generic HTTPS endpoint that receives the
                                  status payload on every run.
    HEALTH_DCE_ENDPOINT          - Logs ingestion endpoint of the SEPARATE,
                                  minimal DCE provisioned for the health-status
                                  table (NOT the findings DCE).
    HEALTH_DCR_IMMUTABLE_ID     - immutableId of the SEPARATE, minimal DCR
                                  provisioned for PrancerConnectivityHealth_CL
                                  (NOT the findings DCR).
    HEALTH_STREAM_NAME          - DCR stream name for the health table.
                                  Default: Custom-PrancerConnectivityHealth_CL.
    CUSTOMER_ID                  - Optional Prancer-side customer identifier,
                                  written into the CustomerId column of the
                                  health status row (mirrors the CustomerId
                                  column already present on PrancerFindings_CL).
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import azure.functions as func
import requests

# ---------------------------------------------------------------------------
# Configuration from Application Settings
# ---------------------------------------------------------------------------
WORKSPACE_ID = os.environ.get("WORKSPACE_ID")
WORKSPACE_NAME = os.environ.get("WORKSPACE_NAME") or WORKSPACE_ID
TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

try:
    STALENESS_THRESHOLD_HOURS = float(os.environ.get("STALENESS_THRESHOLD_HOURS") or "48")
except ValueError:
    STALENESS_THRESHOLD_HOURS = 48.0

HEALTH_CHECK_WEBHOOK_URL = os.environ.get("HEALTH_CHECK_WEBHOOK_URL")
HEALTH_DCE_ENDPOINT = os.environ.get("HEALTH_DCE_ENDPOINT")
HEALTH_DCR_IMMUTABLE_ID = os.environ.get("HEALTH_DCR_IMMUTABLE_ID")
HEALTH_STREAM_NAME = os.environ.get("HEALTH_STREAM_NAME") or "Custom-PrancerConnectivityHealth_CL"
CUSTOMER_ID = os.environ.get("CUSTOMER_ID") or ""

__version__ = "1.0"

AAD_TOKEN_URL_TMPL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
LOG_ANALYTICS_QUERY_SCOPE = "https://api.loganalytics.io/.default"
LOGS_INGESTION_SCOPE = "https://monitor.azure.com/.default"
LOG_ANALYTICS_QUERY_URL_TMPL = "https://api.loganalytics.io/v1/workspaces/{workspace_id}/query"
LOGS_INGESTION_API_VERSION = "2023-01-01"

KQL_QUERY = "PrancerFindings_CL | summarize LastReceived = max(TimeGenerated)"

HTTP_TIMEOUT_SECONDS = 30

logs_prefix = "PrancerConnectivityHealthCheck"
function_name = "run"


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------
def _get_aad_token(scope: str) -> str:
    """Acquire an Azure AD access token via the OAuth2 client_credentials grant."""
    token_url = AAD_TOKEN_URL_TMPL.format(tenant_id=TENANT_ID)
    resp = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": scope,
        },
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    body = resp.json()
    token = body.get("access_token")
    if not token:
        raise RuntimeError(f"{logs_prefix}: Token response for scope '{scope}' did not contain an access_token.")
    return token


# ---------------------------------------------------------------------------
# Log Analytics Query API
# ---------------------------------------------------------------------------
def _query_last_received(token: str) -> Optional[datetime]:
    """
    Query PrancerFindings_CL for the most recent TimeGenerated value via the
    Log Analytics Query API. Returns None if the table has no rows yet
    (empty table / never ingested). Raises on any query/auth/API failure -
    callers must treat that as "connectivity to the workspace itself is
    broken", which is distinct from "connectivity is fine but data is stale".
    """
    url = LOG_ANALYTICS_QUERY_URL_TMPL.format(workspace_id=WORKSPACE_ID)
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"query": KQL_QUERY},
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    body = resp.json()

    tables = body.get("tables") or []
    if not tables or not tables[0].get("rows"):
        return None

    columns = [c["name"] for c in tables[0]["columns"]]
    row = tables[0]["rows"][0]
    row_dict = dict(zip(columns, row))
    last_received_raw = row_dict.get("LastReceived")
    if not last_received_raw:
        return None

    # Log Analytics returns ISO-8601 UTC timestamps, e.g. "2026-08-11T12:34:56.789Z"
    normalized = last_received_raw.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


# ---------------------------------------------------------------------------
# Webhook notification (DCR/table-independent channel)
# ---------------------------------------------------------------------------
def _post_webhook(payload: dict) -> None:
    """
    POST the health status payload to the configured webhook URL, if any.
    This is deliberately the primary customer-facing alerting channel and
    does NOT depend on PrancerFindings_CL, its DCR, or the health table being
    healthy - it only depends on outbound HTTPS from the Function App, which
    is independent of every failure mode this check exists to detect.
    """
    if not HEALTH_CHECK_WEBHOOK_URL:
        logging.info(f"{logs_prefix}: HEALTH_CHECK_WEBHOOK_URL not configured; skipping webhook notification.")
        return

    if payload.get("stalenessHours") is not None:
        staleness_display = f"{payload['stalenessHours']:.1f}h ago"
    else:
        staleness_display = "unknown"

    status_text = (
        f"Prancer Connectivity Health Check - {payload['workspaceName']}: "
        f"{'HEALTHY' if payload['isHealthy'] else 'UNHEALTHY'} "
        f"(last finding received {staleness_display}, threshold {payload['stalenessThresholdHours']}h)"
    )
    if payload.get("error"):
        status_text += f" - {payload['error']}"

    # "text" is understood by both Teams incoming webhooks and Slack incoming
    # webhooks; a generic HTTP endpoint still receives the full structured
    # payload alongside it.
    webhook_body = dict(payload)
    webhook_body["text"] = status_text

    try:
        resp = requests.post(HEALTH_CHECK_WEBHOOK_URL, json=webhook_body, timeout=HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        logging.info(f"{logs_prefix}: Webhook notification sent successfully.")
    except Exception as exc:
        # A webhook failure must never abort the run - the
        # PrancerConnectivityHealth_CL row (if configured) is the fallback
        # signal when this channel is unreachable.
        logging.error(f"{logs_prefix}: Failed to POST to HEALTH_CHECK_WEBHOOK_URL: {exc}")


# ---------------------------------------------------------------------------
# Logs Ingestion API (separate DCE/DCR from the findings pipeline)
# ---------------------------------------------------------------------------
def _push_health_row(token: str, payload: dict) -> None:
    """
    Push a single status row into PrancerConnectivityHealth_CL via the Logs
    Ingestion API, using a DCE/DCR that is separate from the one used for
    PrancerFindings_CL. No-ops (with a log line) if HEALTH_DCE_ENDPOINT or
    HEALTH_DCR_IMMUTABLE_ID are not configured - the webhook above is not
    affected by that.
    """
    if not HEALTH_DCE_ENDPOINT or not HEALTH_DCR_IMMUTABLE_ID:
        logging.info(
            f"{logs_prefix}: HEALTH_DCE_ENDPOINT / HEALTH_DCR_IMMUTABLE_ID not configured; "
            f"skipping PrancerConnectivityHealth_CL row (the webhook, if configured, is unaffected)."
        )
        return

    url = (
        f"{HEALTH_DCE_ENDPOINT.rstrip('/')}/dataCollectionRules/{HEALTH_DCR_IMMUTABLE_ID}"
        f"/streams/{HEALTH_STREAM_NAME}?api-version={LOGS_INGESTION_API_VERSION}"
    )
    row = [{
        "TimeGenerated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "CustomerId": CUSTOMER_ID,
        "WorkspaceId": WORKSPACE_ID,
        "LastFindingReceived": payload["lastReceived"],
        "StalenessHours": payload["stalenessHours"],
        "IsHealthy": payload["isHealthy"],
    }]

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=row,
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    logging.info(f"{logs_prefix}: Pushed health status row to PrancerConnectivityHealth_CL.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(timer: func.TimerRequest) -> None:
    """Entry point for the timer-triggered connectivity health check."""
    run_start = datetime.now(timezone.utc)

    if timer.past_due:
        logging.warning(f"{logs_prefix} {function_name}: Timer is running late!")

    logging.info(f"{logs_prefix} {function_name}: Health check starting at {run_start.strftime('%Y-%m-%dT%H:%M:%SZ')}")

    # ------------------------------------------------------------------
    # 0. Validate required application settings
    # ------------------------------------------------------------------
    missing = [k for k, v in {
        "WORKSPACE_ID": WORKSPACE_ID,
        "TENANT_ID": TENANT_ID,
        "CLIENT_ID": CLIENT_ID,
        "CLIENT_SECRET": CLIENT_SECRET,
    }.items() if not v]
    if missing:
        raise EnvironmentError(f"{logs_prefix}: Missing required app settings: {', '.join(missing)}")

    # ------------------------------------------------------------------
    # 1. Query PrancerFindings_CL for max(TimeGenerated)
    # ------------------------------------------------------------------
    try:
        query_token = _get_aad_token(LOG_ANALYTICS_QUERY_SCOPE)
        last_received = _query_last_received(query_token)
    except Exception as exc:
        # The query itself failed (auth, network, workspace access, DCR role
        # assignment revoked, etc.) - this is exactly the failure mode this
        # Function exists to detect, so it is itself reported via the
        # webhook rather than silently swallowed. We cannot compute a
        # staleness value here, since we have no data point to compute it
        # from.
        logging.error(f"{logs_prefix} {function_name}: Log Analytics query failed: {exc}")
        _post_webhook({
            "workspaceName": WORKSPACE_NAME,
            "workspaceId": WORKSPACE_ID,
            "lastReceived": None,
            "stalenessHours": None,
            "stalenessThresholdHours": STALENESS_THRESHOLD_HOURS,
            "isHealthy": False,
            "error": f"Log Analytics query failed: {exc}",
        })
        raise

    # ------------------------------------------------------------------
    # 2. Compare staleness against the configured threshold
    # ------------------------------------------------------------------
    staleness_hours: Optional[float]
    if last_received is None:
        staleness_hours = None
        is_healthy = False
        logging.warning(f"{logs_prefix}: PrancerFindings_CL has no rows yet (empty table or never ingested).")
    else:
        staleness_hours = (run_start - last_received).total_seconds() / 3600.0
        is_healthy = staleness_hours <= STALENESS_THRESHOLD_HOURS
        logging.info(
            f"{logs_prefix}: Last finding received at {last_received.strftime('%Y-%m-%dT%H:%M:%SZ')} "
            f"({staleness_hours:.2f}h ago); threshold={STALENESS_THRESHOLD_HOURS}h; healthy={is_healthy}"
        )

    payload = {
        "workspaceName": WORKSPACE_NAME,
        "workspaceId": WORKSPACE_ID,
        "lastReceived": last_received.strftime("%Y-%m-%dT%H:%M:%SZ") if last_received else None,
        "stalenessHours": round(staleness_hours, 2) if staleness_hours is not None else None,
        "stalenessThresholdHours": STALENESS_THRESHOLD_HOURS,
        "isHealthy": is_healthy,
    }

    # ------------------------------------------------------------------
    # 3a. Report via webhook - independent of the findings DCR/table
    # ------------------------------------------------------------------
    _post_webhook(payload)

    # ------------------------------------------------------------------
    # 3b. The query succeeded (workspace/API access is fine), so also write
    #     a status row into the separate PrancerConnectivityHealth_CL table
    #     via its own DCE/DCR.
    # ------------------------------------------------------------------
    try:
        ingest_token = _get_aad_token(LOGS_INGESTION_SCOPE)
        _push_health_row(ingest_token, payload)
    except Exception as exc:
        # Do not fail the whole run over this - the webhook above already
        # delivered the health signal through an independent channel, and a
        # health-table outage should not be conflated with a findings-table
        # outage.
        logging.error(f"{logs_prefix} {function_name}: Failed to push health status row: {exc}")

    elapsed = (datetime.now(timezone.utc) - run_start).total_seconds()
    logging.info(
        f"{logs_prefix} {function_name}: Health check finished at "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} (elapsed: {elapsed:.1f}s)."
    )
