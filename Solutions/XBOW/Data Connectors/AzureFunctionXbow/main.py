"""
Azure Function App – XBOW Security Platform → Microsoft Sentinel Data Connector

Pulls asset inventory/configuration, vulnerability findings, and assessment activity from the XBOW API on a
timer schedule and ingests only new/changed records into Sentinel:
    - Assets       → XbowAssets_CL     (full JSON snapshot from GET /assets/{assetId}, credentials excluded)
  - Findings     → XbowFindings_CL   (with full enrichment: evidence, PoC, impact, mitigations)
  - Assessments  → XbowAssessments_CL (with lifecycle event history)

Incremental sync strategy:
  State (last-seen updatedAt per asset) is persisted in Azure Blob Storage
  (container: xbow-connector-state, blob: sync_state.json) using the
  AzureWebJobsStorage connection string. On each run, only records with an
  updatedAt timestamp newer than the stored value are ingested, then the
  state is updated. On first run, all existing records are ingested.

Application Settings (configured automatically by the ARM template):
    TENANT_ID               – Azure AD Tenant ID
    CLIENT_ID               – App Registration (Service Principal) Client ID
    CLIENT_SECRET           – App Registration Client Secret
    DCE_ENDPOINT            – Data Collection Endpoint logs-ingestion URL
    DCR_ID                  – Data Collection Rule immutableId
    ASSETS_STREAM_NAME      – DCR stream for assets    (Custom-XbowAssets_CL)
    FINDINGS_STREAM_NAME    – DCR stream for findings  (Custom-XbowFindings_CL)
    ASSESSMENTS_STREAM_NAME – DCR stream for assessments (Custom-XbowAssessments_CL)
    XBOW_API_TOKEN          – XBOW Personal Access Token
    XBOW_ORG_ID             – XBOW Organization ID
    AzureWebJobsStorage     – Azure Storage connection string (for state persistence)
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Generator

import requests
import azure.functions as func
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.storage.blob import BlobServiceClient, BlobClient

# ---------------------------------------------------------------------------
# Configuration from Application Settings
# ---------------------------------------------------------------------------
TENANT_ID               = os.environ.get("TENANT_ID")
CLIENT_ID               = os.environ.get("CLIENT_ID")
CLIENT_SECRET           = os.environ.get("CLIENT_SECRET")
DCE_ENDPOINT            = os.environ.get("DCE_ENDPOINT")
DCR_ID                  = os.environ.get("DCR_ID")
ASSETS_STREAM_NAME      = os.environ.get("ASSETS_STREAM_NAME", "Custom-XbowAssets_CL")
FINDINGS_STREAM_NAME    = os.environ.get("FINDINGS_STREAM_NAME", "Custom-XbowFindings_CL")
ASSESSMENTS_STREAM_NAME = os.environ.get("ASSESSMENTS_STREAM_NAME", "Custom-XbowAssessments_CL")
XBOW_API_TOKEN          = os.environ.get("XBOW_API_TOKEN")
XBOW_ORG_ID             = os.environ.get("XBOW_ORG_ID")
STORAGE_CONN_STR        = os.environ.get("AzureWebJobsStorage")

XBOW_API_BASE    = "https://console.xbow.com/api/v1"
XBOW_API_VERSION = "2026-02-01"
PAGE_SIZE        = 100
INGEST_BATCH_SIZE = 500          # max records per upload() call
STATE_CONTAINER  = "xbow-connector-state"
STATE_BLOB       = "sync_state.json"

logs_prefix   = "XbowConnector"
function_name = "main"


# ---------------------------------------------------------------------------
# State persistence helpers (Azure Blob Storage)
# ---------------------------------------------------------------------------

SyncState = dict  # {"assets": {asset_id: last_updated_at}, "findings": {...}, "assessments": {...}}


def _get_blob_client() -> BlobClient:
    """Return a BlobClient for the sync state blob."""
    svc = BlobServiceClient.from_connection_string(STORAGE_CONN_STR)
    container = svc.get_container_client(STATE_CONTAINER)
    try:
        container.create_container()
    except Exception:
        pass  # already exists
    return svc.get_blob_client(container=STATE_CONTAINER, blob=STATE_BLOB)


def load_state() -> SyncState:
    """Load sync state from blob storage. Returns empty state on first run."""
    try:
        blob = _get_blob_client()
        data = blob.download_blob().readall()
        state = json.loads(data)
        logging.info(f"{logs_prefix}: Loaded sync state from blob storage.")
        return state
    except Exception as exc:
        logging.info(f"{logs_prefix}: No existing sync state found (first run or error: {exc}). Starting fresh.")
        return {"assets": {}, "findings": {}, "assessments": {}}


def save_state(state: SyncState) -> None:
    """Persist sync state to blob storage."""
    try:
        blob = _get_blob_client()
        blob.upload_blob(json.dumps(state, indent=2), overwrite=True)
        logging.info(f"{logs_prefix}: Sync state saved to blob storage.")
    except Exception as exc:
        logging.error(f"{logs_prefix}: Failed to save sync state: {exc}. State will not persist across runs.")


def _parse_ts(ts: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime, or None."""
    if not ts:
        return None
    try:
        # Handle both 'Z' suffix and '+00:00'
        normalized = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _is_newer(record_ts: str | None, last_seen_ts: str | None) -> bool:
    """
    Return True if record_ts is strictly after last_seen_ts.
    If last_seen_ts is None (first run), always return True.
    If record_ts cannot be parsed, return True (err on the side of ingesting).
    """
    if last_seen_ts is None:
        return True
    r = _parse_ts(record_ts)
    l = _parse_ts(last_seen_ts)
    if r is None:
        return True
    if l is None:
        return True
    return r > l


def _max_ts(a: str | None, b: str | None) -> str | None:
    """Return the later of two ISO timestamp strings."""
    da, db = _parse_ts(a), _parse_ts(b)
    if da is None:
        return b
    if db is None:
        return a
    return a if da >= db else b


# ---------------------------------------------------------------------------
# XBOW API helpers
# ---------------------------------------------------------------------------

def _xbow_headers() -> dict:
    return {
        "User-Agent": "XBOW-Sentinel-Connector/1.0",
        "Authorization": f"Bearer {XBOW_API_TOKEN}",
        "X-XBOW-API-Version": XBOW_API_VERSION,
    }


def _paginate(url: str, params: dict | None = None) -> Generator[dict, None, None]:
    """Cursor-based pagination over a XBOW list endpoint, yielding each item."""
    cursor = None
    while True:
        p = {**(params or {}), "limit": PAGE_SIZE}
        if cursor:
            p["after"] = cursor
        resp = requests.get(url, headers=_xbow_headers(), params=p, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            yield item
        cursor = data.get("nextCursor")
        if not cursor:
            break


def _fetch_finding_detail(finding_id: str) -> dict:
    """Fetch the full finding record including evidence, recipe, and mitigations."""
    resp = requests.get(
        f"{XBOW_API_BASE}/findings/{finding_id}",
        headers=_xbow_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _fetch_asset_detail(asset_id: str) -> dict:
    """Fetch full details for a specific asset."""
    resp = requests.get(
        f"{XBOW_API_BASE}/assets/{asset_id}",
        headers=_xbow_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _list_assets(org_id: str) -> list[dict]:
    """Return all assets for the organization."""
    return list(_paginate(f"{XBOW_API_BASE}/organizations/{org_id}/assets"))


def _safe_asset_payload(asset: dict) -> dict:
    """Return a copy of an asset payload with sensitive fields removed."""
    safe = dict(asset or {})
    safe.pop("credentials", None)
    return safe


# ---------------------------------------------------------------------------
# Event builders with incremental diff
# ---------------------------------------------------------------------------

def collect_finding_events(
    org_id: str,
    assets: list[dict],
    last_seen: dict[str, str],
) -> tuple[list[dict], dict[str, str]]:
    """
    For each asset, fetch findings where updatedAt > last_seen[asset_id].
    Returns (new_events, updated_last_seen).

    Each finding is enriched with the full detail record (evidence, PoC recipe,
    impact statement, and mitigation guidance) from GET /findings/{findingId}.
    """
    events: list[dict] = []
    new_last_seen: dict[str, str] = dict(last_seen)  # copy; update as we go

    for asset in assets:
        asset_id   = asset["id"]
        asset_name = asset["name"]
        asset_last = last_seen.get(asset_id)
        asset_max_ts = asset_last  # track highest updatedAt we see this run

        for finding in _paginate(f"{XBOW_API_BASE}/assets/{asset_id}/findings"):
            record_ts = finding.get("updatedAt") or finding.get("createdAt")

            if not _is_newer(record_ts, asset_last):
                continue  # already ingested on a previous run

            # Enrich with full detail (evidence, recipe, impact, mitigations)
            try:
                detail = _fetch_finding_detail(finding["id"])
            except Exception as exc:
                logging.warning(
                    f"{logs_prefix}: Could not enrich finding {finding['id']}: {exc}. "
                    "Using summary record."
                )
                detail = finding

            events.append({
                "TimeGenerated":  detail.get("updatedAt") or detail.get("createdAt"),
                "FindingId":      detail.get("id", ""),
                "FindingName":    detail.get("name", ""),
                "Severity":       detail.get("severity", ""),
                "State":          detail.get("state", ""),
                "Summary":        (detail.get("summary") or "")[:32000],  # guard oversized fields
                "Evidence":       (detail.get("evidence") or "")[:32000],
                "Impact":         (detail.get("impact") or "")[:8000],
                "Mitigations":    (detail.get("mitigations") or "")[:8000],
                "Recipe":         (detail.get("recipe") or "")[:32000],
                "AssetId":        asset_id,
                "AssetName":      asset_name,
                "OrganizationId": org_id,
                "CreatedAt":      detail.get("createdAt", ""),
            })

            asset_max_ts = _max_ts(asset_max_ts, record_ts)

        if asset_max_ts:
            new_last_seen[asset_id] = asset_max_ts

    return events, new_last_seen


def collect_asset_events(
    org_id: str,
    assets: list[dict],
    last_seen: dict[str, str],
) -> tuple[list[dict], dict[str, str]]:
    """
    For each asset from the organization list endpoint, fetch GET /assets/{assetId}
    when updatedAt > last_seen[asset_id], and emit a sanitized JSON snapshot event.
    """
    events: list[dict] = []
    new_last_seen: dict[str, str] = dict(last_seen)

    for asset in assets:
        asset_id = asset.get("id", "")
        if not asset_id:
            continue

        asset_last = last_seen.get(asset_id)
        record_ts = asset.get("updatedAt") or asset.get("createdAt")
        if not _is_newer(record_ts, asset_last):
            continue

        try:
            detail = _fetch_asset_detail(asset_id)
        except Exception as exc:
            logging.warning(
                f"{logs_prefix}: Could not fetch asset detail for {asset_id}: {exc}. "
                "Using list payload."
            )
            detail = asset

        safe_detail = _safe_asset_payload(detail)
        checks = safe_detail.get("checks") or {}
        asset_reachable = checks.get("assetReachable") or {}

        events.append({
            "TimeGenerated":          safe_detail.get("updatedAt") or safe_detail.get("createdAt") or record_ts,
            "AssetId":                safe_detail.get("id", asset_id),
            "AssetName":              safe_detail.get("name", ""),
            "Lifecycle":              safe_detail.get("lifecycle", ""),
            "OrganizationId":         safe_detail.get("organizationId", org_id),
            "StartUrl":               (safe_detail.get("startUrl") or "")[:2048],
            "Sku":                    safe_detail.get("sku", ""),
            "MaxRequestsPerSecond":   safe_detail.get("maxRequestsPerSecond") or 0,
            "CreatedAt":              safe_detail.get("createdAt", ""),
            "UpdatedAt":              safe_detail.get("updatedAt", ""),
            "AssetReachableState":    asset_reachable.get("state", ""),
            "AssetReachableMessage":  (asset_reachable.get("message") or "")[:4000],
            "Checks":                 json.dumps(checks),
            "ApprovedTimeWindows":    json.dumps(safe_detail.get("approvedTimeWindows")),
            "DnsBoundaryRules":       json.dumps(safe_detail.get("dnsBoundaryRules")),
            "HttpBoundaryRules":      json.dumps(safe_detail.get("httpBoundaryRules")),
            "Headers":                json.dumps(safe_detail.get("headers")),
            "RawAsset":               json.dumps(safe_detail)[:32000],
        })

        if record_ts:
            new_last_seen[asset_id] = record_ts

    return events, new_last_seen


def collect_assessment_events(
    org_id: str,
    assets: list[dict],
    last_seen: dict[str, str],
) -> tuple[list[dict], dict[str, str]]:
    """
    For each asset, fetch assessments where updatedAt > last_seen[asset_id].
    Returns (new_events, updated_last_seen).

    Includes recentEvents (state-change history: started/paused/resumed/cancelled)
    serialised as a JSON string for use in KQL queries.
    """
    events: list[dict] = []
    new_last_seen: dict[str, str] = dict(last_seen)

    for asset in assets:
        asset_id   = asset["id"]
        asset_name = asset["name"]
        asset_last = last_seen.get(asset_id)
        asset_max_ts = asset_last

        for assessment in _paginate(f"{XBOW_API_BASE}/assets/{asset_id}/assessments"):
            record_ts = assessment.get("updatedAt") or assessment.get("createdAt")

            if not _is_newer(record_ts, asset_last):
                continue

            events.append({
                "TimeGenerated":   assessment.get("updatedAt") or assessment.get("createdAt"),
                "AssessmentId":    assessment.get("id", ""),
                "AssessmentName":  assessment.get("name", ""),
                "State":           assessment.get("state", ""),
                "Progress":        assessment.get("progress", 0),
                "AttackCredits":   assessment.get("attackCredits", 0),
                "RecentEvents":    json.dumps(assessment.get("recentEvents") or []),
                "AssetId":         asset_id,
                "AssetName":       asset_name,
                "OrganizationId":  org_id,
                "CreatedAt":       assessment.get("createdAt", ""),
            })

            asset_max_ts = _max_ts(asset_max_ts, record_ts)

        if asset_max_ts:
            new_last_seen[asset_id] = asset_max_ts

    return events, new_last_seen


# ---------------------------------------------------------------------------
# Ingestion helper (batched upload)
# ---------------------------------------------------------------------------

def _ingest_batched(
    client: LogsIngestionClient,
    stream: str,
    events: list[dict],
) -> None:
    """
    Upload events to Sentinel in batches of INGEST_BATCH_SIZE.
    The Azure Monitor Ingestion SDK handles individual payload size limits,
    but explicit batching keeps memory usage predictable for large datasets.
    No-ops on empty event lists.
    """
    if not events:
        logging.info(f"{logs_prefix}: No new events to ingest for stream '{stream}'.")
        return

    total = 0
    for i in range(0, len(events), INGEST_BATCH_SIZE):
        batch = events[i : i + INGEST_BATCH_SIZE]
        client.upload(rule_id=DCR_ID, stream_name=stream, logs=batch)
        total += len(batch)
        logging.info(f"{logs_prefix}: Uploaded batch of {len(batch)} events to '{stream}' ({total}/{len(events)} total).")

    logging.info(f"{logs_prefix}: Finished ingesting {total} event(s) → '{stream}'.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(mytimer: func.TimerRequest) -> None:
    """Entry point for the timer-triggered Azure Function."""
    run_start = datetime.now(timezone.utc)
    utc_timestamp = run_start.strftime("%Y-%m-%dT%H:%M:%SZ")

    if mytimer.past_due:
        logging.warning(f"{logs_prefix} {function_name}: Timer is running late!")

    logging.info(f"{logs_prefix} {function_name}: Connector starting at {utc_timestamp}")

    # ------------------------------------------------------------------
    # 1. Validate required application settings
    # ------------------------------------------------------------------
    missing = [k for k, v in {
        "XBOW_API_TOKEN":    XBOW_API_TOKEN,
        "XBOW_ORG_ID":       XBOW_ORG_ID,
        "TENANT_ID":         TENANT_ID,
        "CLIENT_ID":         CLIENT_ID,
        "CLIENT_SECRET":     CLIENT_SECRET,
        "DCE_ENDPOINT":      DCE_ENDPOINT,
        "DCR_ID":            DCR_ID,
        "AzureWebJobsStorage": STORAGE_CONN_STR,
    }.items() if not v]
    if missing:
        raise EnvironmentError(
            f"{logs_prefix}: Missing required app settings: {', '.join(missing)}"
        )

    # ------------------------------------------------------------------
    # 2. Load persisted sync state
    # ------------------------------------------------------------------
    state = load_state()
    assets_last_seen:      dict[str, str] = state.get("assets", {})
    findings_last_seen:    dict[str, str] = state.get("findings", {})
    assessments_last_seen: dict[str, str] = state.get("assessments", {})

    logging.info(
        f"{logs_prefix}: State loaded — "
        f"{len(assets_last_seen)} asset(s) tracked for assets, "
        f"{len(findings_last_seen)} asset(s) tracked for findings, "
        f"{len(assessments_last_seen)} for assessments."
    )

    # ------------------------------------------------------------------
    # 3. Enumerate all assets (single pass, reused for both data types)
    # ------------------------------------------------------------------
    logging.info(f"{logs_prefix}: Listing all assets for org {XBOW_ORG_ID}...")
    assets = _list_assets(XBOW_ORG_ID)
    logging.info(f"{logs_prefix}: Found {len(assets)} asset(s).")

    # ------------------------------------------------------------------
    # 4. Collect new/changed asset snapshots
    # ------------------------------------------------------------------
    logging.info(f"{logs_prefix}: Collecting new/changed asset snapshots...")
    asset_events, new_assets_last_seen = collect_asset_events(
        XBOW_ORG_ID, assets, assets_last_seen
    )
    logging.info(f"{logs_prefix}: {len(asset_events)} new/changed asset snapshot(s) to ingest.")

    # ------------------------------------------------------------------
    # 5. Collect new/changed findings (with full enrichment)
    # ------------------------------------------------------------------
    logging.info(f"{logs_prefix}: Collecting new/changed findings...")
    finding_events, new_findings_last_seen = collect_finding_events(
        XBOW_ORG_ID, assets, findings_last_seen
    )
    logging.info(f"{logs_prefix}: {len(finding_events)} new/changed finding(s) to ingest.")

    # ------------------------------------------------------------------
    # 6. Collect new/changed assessments
    # ------------------------------------------------------------------
    logging.info(f"{logs_prefix}: Collecting new/changed assessments...")
    assessment_events, new_assessments_last_seen = collect_assessment_events(
        XBOW_ORG_ID, assets, assessments_last_seen
    )
    logging.info(f"{logs_prefix}: {len(assessment_events)} new/changed assessment(s) to ingest.")

    # ------------------------------------------------------------------
    # 7. Create Sentinel ingestion client
    # ------------------------------------------------------------------
    try:
        creds = ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        ingestion_client = LogsIngestionClient(endpoint=DCE_ENDPOINT, credential=creds)
    except Exception as exc:
        logging.error(
            f"{logs_prefix} {function_name}: Failed to create Azure credential/client. "
            f"Check TENANT_ID, CLIENT_ID, CLIENT_SECRET, DCE_ENDPOINT. Error: {exc}"
        )
        raise

    # ------------------------------------------------------------------
    # 8. Ingest to Sentinel
    # ------------------------------------------------------------------
    try:
        _ingest_batched(ingestion_client, ASSETS_STREAM_NAME, asset_events)
        _ingest_batched(ingestion_client, FINDINGS_STREAM_NAME, finding_events)
        _ingest_batched(ingestion_client, ASSESSMENTS_STREAM_NAME, assessment_events)
    except ClientAuthenticationError as exc:
        logging.error(
            f"{logs_prefix} {function_name}: Authentication failed — verify CLIENT_ID, "
            f"CLIENT_SECRET, TENANT_ID, and that the App Registration has "
            f"'Monitoring Metrics Publisher' role on the DCR. Error: {exc}"
        )
        raise
    except HttpResponseError as exc:
        logging.error(
            f"{logs_prefix} {function_name}: HTTP error from Azure Monitor Ingestion API. "
            f"Check DCE_ENDPOINT, DCR_ID, and stream names. Error: {exc}"
        )
        raise
    except Exception as exc:
        logging.error(f"{logs_prefix} {function_name}: Unexpected ingestion error: {exc}")
        raise

    # ------------------------------------------------------------------
    # 9. Persist updated state (only after successful ingest)
    # ------------------------------------------------------------------
    save_state({
        "assets":      new_assets_last_seen,
        "findings":    new_findings_last_seen,
        "assessments": new_assessments_last_seen,
    })

    elapsed = (datetime.now(timezone.utc) - run_start).total_seconds()
    logging.info(
        f"{logs_prefix} {function_name}: Connector finished at {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
        f"(elapsed: {elapsed:.1f}s, assets: {len(asset_events)}, findings: {len(finding_events)}, assessments: {len(assessment_events)})"
    )
