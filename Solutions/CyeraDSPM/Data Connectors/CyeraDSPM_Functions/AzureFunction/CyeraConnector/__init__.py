# CyeraConnector / Azure Function (HTTP trigger)
# Version: 1.6.1 (2025-09-23)
#
# Purpose:
#   Pulls data from the Cyera API and ingests into Microsoft Sentinel via DCE/DCR (Logs Ingestion API).
#   Keeps incremental watermarks in Blob Storage to avoid duplicates.
#
# Key env settings (examples):
#   CYERA_BASE_URL=https://api.cyera.io
#   CYERA_CLIENT_ID=...
#   CYERA_SECRET=...
#   DCE_INGEST=https://<dce-name>.<region>-1.ingest.monitor.azure.com
#   DCR_IMMUTABLE_ID=dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#   STREAM_ASSETS=Custom-CyeraAssets
#   STREAM_IDENTITIES=Custom-CyeraIdentities
#   STREAM_ISSUES=Custom-CyeraIssues
#   STREAM_CLASSIFICATIONS=Custom-CyeraClassifications
#   ENABLE_ASSETS=true/false
#   ENABLE_IDENTITIES=true/false
#   ENABLE_ISSUES=true/false
#   ENABLE_CLASSIFICATIONS=true/false
#   FULL_SYNC=false          # identities/classifications need snapshot; set true when you want a refresh
#   INITIAL_LOOKBACK_DAYS=30 # initial watermark if no cursor
#   STATE_ACCOUNT_URL=https://<storageacct>.blob.core.windows.net   # optional (MSI)
#   STATE_CONTAINER=cyera-cursors
#   STATE_PREFIX=cursors
#   PAGE_SIZE_ASSETS=500
#   PAGE_SIZE_IDENTITIES=100
#   PAGE_SIZE_ISSUES=100
#   PAGE_SIZE_CLASSIFICATIONS=100
#   RETRY_TOTAL=8
#   BACKOFF_BASE=1.5
#   HTTP_TIMEOUT=60
#   SEND_BATCH_SIZE=200
#   SEND_BYTES_MAX=900000
#   # v1.6.1 additions:
#   ASSETS_DELTA_PARAM=lastModifiedTimeGte   # or lastDataRefreshGte
#   DRY_RUN=false                            # true = fetch only; skip POST & watermark advance

import azure.functions as func
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Iterable, List, Tuple, Optional
from uuid import uuid4

import requests
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError

# -------------------- helpers: env & time --------------------

def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on")

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# -------------------- configuration --------------------

CYERA_BASE = os.getenv("CYERA_BASE_URL", "https://api.cyera.io").rstrip("/")
CYERA_CLIENT_ID = os.getenv("CYERA_CLIENT_ID")
CYERA_SECRET = os.getenv("CYERA_SECRET")

ENABLE_ASSETS = _env_bool("ENABLE_ASSETS", True)
ENABLE_IDENTITIES = _env_bool("ENABLE_IDENTITIES", True)
ENABLE_ISSUES = _env_bool("ENABLE_ISSUES", True)
ENABLE_CLASSIFICATIONS = _env_bool("ENABLE_CLASSIFICATIONS", True)

FULL_SYNC = _env_bool("FULL_SYNC", False)
LOOKBACK_DAYS = _env_int("INITIAL_LOOKBACK_DAYS", 30)

# DCE/DCR
DCE_INGEST = (os.getenv("DCR_INGEST") or os.getenv("DCE_INGEST") or "").rstrip("/")
DCR_IMMUTABLE_ID = os.getenv("DCR_IMMUTABLE_ID", "")

# State (Blob) – either MSI via STATE_ACCOUNT_URL or fallback to AzureWebJobsStorage conn string
STATE_ACCOUNT_URL = os.getenv("STATE_ACCOUNT_URL")  # optional for MSI path
STATE_CONTAINER = os.getenv("STATE_CONTAINER", "cyera-cursors")
STATE_PREFIX = os.getenv("STATE_PREFIX", "cursors")

# Paging/backoff per OpenAPI caps
PAGE_SIZE_ASSETS = _env_int("PAGE_SIZE_ASSETS", 500)               # /v2/datastores <= 1000
PAGE_SIZE_IDENTITIES = _env_int("PAGE_SIZE_IDENTITIES", 100)       # /v1/identities <= 100
PAGE_SIZE_ISSUES = _env_int("PAGE_SIZE_ISSUES", 100)               # /v3/issues <= 100
PAGE_SIZE_CLASSIFICATIONS = _env_int("PAGE_SIZE_CLASSIFICATIONS", 100)  # /v1/classifications <= 100

RETRY_TOTAL = _env_int("RETRY_TOTAL", 8)
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "1.5"))
HTTP_TIMEOUT = _env_int("HTTP_TIMEOUT", 60)  # seconds

# Ingestion batching
SEND_BATCH_SIZE = _env_int("SEND_BATCH_SIZE", 200)
SEND_BYTES_MAX = _env_int("SEND_BYTES_MAX", 900_000)  # ~ under 1MB

# Streams (DCR stream names; NOT the _CL table names)
STREAM_ASSETS = os.getenv("STREAM_ASSETS", "Custom-CyeraAssets")
STREAM_IDENTITIES = os.getenv("STREAM_IDENTITIES", "Custom-CyeraIdentities")
STREAM_ISSUES = os.getenv("STREAM_ISSUES", "Custom-CyeraIssues")
STREAM_CLASSIFICATIONS = os.getenv("STREAM_CLASSIFICATIONS", "Custom-CyeraClassifications")

# v1.6.1: configurable assets delta key & dry-run
ASSETS_DELTA_PARAM = os.getenv("ASSETS_DELTA_PARAM", "lastModifiedTimeGte").strip()
DRY_RUN = _env_bool("DRY_RUN", False)

# -------------------- Azure clients --------------------

_default_cred = DefaultAzureCredential(exclude_interactive_browser_credential=True)
_blob_client: Optional[BlobServiceClient] = None

def _init_blob_client() -> BlobServiceClient:
    global _blob_client
    if _blob_client is not None:
        return _blob_client

    # Prefer MSI to account URL if provided (Function's managed identity must have Blob Data Contributor)
    if STATE_ACCOUNT_URL:
        try:
            _blob_client = BlobServiceClient(account_url=STATE_ACCOUNT_URL, credential=_default_cred)
            try:
                _blob_client.create_container(STATE_CONTAINER)
            except ResourceExistsError:
                pass
            return _blob_client
        except Exception as e:
            logging.warning("MSI blob init failed (%s); falling back to AzureWebJobsStorage.", e)

    # Fallback: use the Functions’ connection string
    conn = os.getenv("AzureWebJobsStorage")
    if not conn:
        raise RuntimeError("Neither STATE_ACCOUNT_URL (MSI) nor AzureWebJobsStorage (conn string) is available.")
    _blob_client = BlobServiceClient.from_connection_string(conn)
    try:
        _blob_client.create_container(STATE_CONTAINER)
    except ResourceExistsError:
        pass
    return _blob_client

def _get_blob_text(name: str) -> Optional[str]:
    svc = _init_blob_client()
    blob = svc.get_blob_client(STATE_CONTAINER, name)
    try:
        return blob.download_blob(encoding="utf-8").readall()
    except ResourceNotFoundError:
        return None

def _put_blob_text(name: str, text: str):
    svc = _init_blob_client()
    svc.get_blob_client(STATE_CONTAINER, name).upload_blob(text, overwrite=True)

def _cursor_name(entity: str) -> str:
    return f"{STATE_PREFIX}/{entity}.json"

def _get_cursor(entity: str) -> Dict[str, Any]:
    raw = _get_blob_text(_cursor_name(entity))
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}

def _set_cursor(entity: str, data: Dict[str, Any]):
    _put_blob_text(_cursor_name(entity), json.dumps(data, separators=(",", ":")))

# -------------------- Cyera auth & HTTP --------------------

def _cyera_session(run_id: str) -> requests.Session:
    if not CYERA_CLIENT_ID or not CYERA_SECRET:
        raise RuntimeError("CYERA_CLIENT_ID/CYERA_SECRET are required for Cyera API login.")
    s = requests.Session()
    s.headers.update({"User-Agent": f"cyera-sentinel-connector/1.6.1 runId={run_id}"})
    r = s.post(f"{CYERA_BASE}/v1/login",
               json={"clientId": CYERA_CLIENT_ID, "secret": CYERA_SECRET},
               timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    tok = r.json().get("jwt") or r.json().get("token") or r.json().get("accessToken")
    if not tok:
        raise RuntimeError("Cyera login did not return a JWT token.")
    s.headers["Authorization"] = f"Bearer {tok}"
    return s

def _request_with_retry(s: requests.Session, method: str, url: str, run_id: str, **kw) -> requests.Response:
    for attempt in range(1, RETRY_TOTAL + 1):
        try:
            r = s.request(method, url, **kw)
            # If 5xx, force retry
            if r.status_code >= 500:
                raise requests.HTTPError(f"{r.status_code} Server Error", response=r)
            return r
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
            if attempt >= RETRY_TOTAL:
                raise
            sleep_for = BACKOFF_BASE ** attempt
            logging.warning("[runId=%s] %s %s failed (%s). Backing off %.1fs (attempt %d/%d)",
                            run_id, method, url, e, sleep_for, attempt, RETRY_TOTAL)
            time.sleep(sleep_for)

def _paged_get(s: requests.Session, path: str, base_params: Dict[str, Any],
               page_limit_cap: int, run_id: str) -> Iterable[List[Dict[str, Any]]]:
    """
    Generic pager for limit/offset endpoints.
    Expects either {"results":[...]} or {"items":[...]} or a raw list.
    """
    offset = int(base_params.get("offset", 0))
    limit = min(int(base_params.get("limit", page_limit_cap)), page_limit_cap)
    while True:
        params = dict(base_params)
        params["limit"] = limit
        params["offset"] = offset
        url = f"{CYERA_BASE}{path}"
        r = _request_with_retry(s, "GET", url, run_id, params=params, timeout=HTTP_TIMEOUT)
        if r.status_code == 204:
            yield []
            return
        r.raise_for_status()
        data = r.json()
        rows = []
        if isinstance(data, dict):
            rows = data.get("results") or data.get("items") or data.get("data") or []
        elif isinstance(data, list):
            rows = data
        yield rows
        got = len(rows)
        if got < limit:
            break
        offset += got

# -------------------- ingestion (DCR/DCE) --------------------

_ingest_sess = requests.Session()

def _ingest_batches(stream: str, records: List[Dict[str, Any]], run_id: str) -> Tuple[int, int]:
    """
    POST to Logs Ingestion endpoint (DCE/DCR) with batch size and payload size caps.
    Returns (posts, records_sent). Logs response code/body on failure.
    """
    if not records:
        return (0, 0)

    if DRY_RUN:
        logging.info("[runId=%s] DRY_RUN=true – skipping ingest for stream=%s (would send %d records)",
                     run_id, stream, len(records))
        return (0, 0)

    if not DCE_INGEST or not DCR_IMMUTABLE_ID:
        raise RuntimeError("DCE_INGEST and DCR_IMMUTABLE_ID must be set.")

    token = _default_cred.get_token("https://monitor.azure.com/.default").token
    url = f"{DCE_INGEST}/dataCollectionRules/{DCR_IMMUTABLE_ID}/streams/{stream}?api-version=2023-01-01"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    posts = 0
    sent = 0
    batch: List[Dict[str, Any]] = []
    size_bytes = 2  # for []

    def flush():
        nonlocal posts, sent, batch, size_bytes
        if not batch:
            return
        body = json.dumps(batch, separators=(",", ":"))
        resp = _ingest_sess.post(url, headers=headers, data=body, timeout=HTTP_TIMEOUT)
        if resp.status_code >= 300:
            logging.error("[runId=%s] Ingest POST failed stream=%s code=%s body=%s",
                          run_id, stream, resp.status_code, resp.text[:800])
            resp.raise_for_status()
        posts += 1
        sent += len(batch)
        logging.info("[runId=%s] Ingest POST success stream=%s batch=%d code=%s",
                     run_id, stream, len(batch), resp.status_code)
        batch = []
        size_bytes = 2

    for rec in records:
        rec = dict(rec)
        rec.setdefault("TimeGenerated", _iso(_now_utc()))
        rec_bytes = len(json.dumps(rec, separators=(",", ":")).encode("utf-8")) + (1 if batch else 0)
        if len(batch) >= SEND_BATCH_SIZE or (size_bytes + rec_bytes) >= SEND_BYTES_MAX:
            flush()
        batch.append(rec)
        size_bytes += rec_bytes

    flush()
    return (posts, sent)

# -------------------- watermarks --------------------

def _since_for(entity: str) -> Optional[str]:
    # Load watermark; if absent and not FULL_SYNC, default to LOOKBACK_DAYS
    cur = _get_cursor(entity)
    if cur.get("since"):
        return cur["since"]
    if FULL_SYNC:
        return None
    return _iso(_now_utc() - timedelta(days=LOOKBACK_DAYS))

def _update_since(entity: str, prev_since_iso: Optional[str], newest_seen_iso: Optional[str]):
    if DRY_RUN:
        logging.info("DRY_RUN=true – not updating watermark for %s", entity)
        return
    cur = _get_cursor(entity)
    if newest_seen_iso:
        prev = cur.get("since")
        if not prev or newest_seen_iso > prev:
            cur["since"] = newest_seen_iso
    elif prev_since_iso and "since" not in cur:
        cur["since"] = prev_since_iso
    _set_cursor(entity, cur)

# -------------------- collectors (endpoints per OpenAPI) --------------------

def _collect_assets(s: requests.Session, run_id: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    GET /v2/datastores
    - Paging: limit<=1000, offset required
    - Delta: lastModifiedTimeGte or lastDataRefreshGte (configurable via ASSETS_DELTA_PARAM)
    """
    path = "/v2/datastores"
    since_iso = _since_for("assets")
    params: Dict[str, Any] = {"limit": min(PAGE_SIZE_ASSETS, 1000), "offset": 0}
    if since_iso:
        params[ASSETS_DELTA_PARAM] = since_iso

    logging.info("[runId=%s] Assets delta param=%s since=%s pageSize=%d",
                 run_id, ASSETS_DELTA_PARAM, since_iso, params["limit"])

    newest = since_iso
    out: List[Dict[str, Any]] = []
    for page in _paged_get(s, path, params, page_limit_cap=1000, run_id=run_id):
        if not page:
            break
        out.extend(page)
        for row in page:
            t = row.get("lastModifiedTime") or row.get("discoveredDate") or since_iso
            if t and (newest is None or t > newest):
                newest = t
    return out, newest

def _collect_identities(s: requests.Session, run_id: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    GET /v1/identities
    - Paging: limit<=100, offset required
    - No updatedDate in spec → snapshot only when FULL_SYNC=true
    """
    path = "/v1/identities"
    if not FULL_SYNC:
        logging.info("[runId=%s] Identities: skipped incremental (no delta param); set FULL_SYNC=true to refresh.", run_id)
        return [], None

    params: Dict[str, Any] = {"limit": min(PAGE_SIZE_IDENTITIES, 100), "offset": 0}
    out: List[Dict[str, Any]] = []
    for page in _paged_get(s, path, params, page_limit_cap=100, run_id=run_id):
        if not page:
            break
        out.extend(page)
    return out, None  # no reliable next watermark

def _collect_issues(s: requests.Session, run_id: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    GET /v3/issues
    - Paging: limit<=100, offset required/accepted
    - Delta: createdDate/updatedDate (we use updatedDate)
    """
    path = "/v3/issues"
    since_iso = _since_for("issues")
    params: Dict[str, Any] = {"limit": min(PAGE_SIZE_ISSUES, 100), "offset": 0}
    if since_iso:
        params["updatedDate"] = since_iso

    newest = since_iso
    out: List[Dict[str, Any]] = []
    for page in _paged_get(s, path, params, page_limit_cap=100, run_id=run_id):
        if not page:
            break
        out.extend(page)
        for row in page:
            t = row.get("updatedDate") or row.get("createdDate") or since_iso
            if t and (newest is None or t > newest):
                newest = t
    return out, newest

def _collect_classifications(s: requests.Session, run_id: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    GET /v1/classifications
    - Paging: limit<=100, offset required
    - No delta param → snapshot only when FULL_SYNC=true
    """
    path = "/v1/classifications"
    if not FULL_SYNC:
        logging.info("[runId=%s] Classifications: skipped incremental (no delta param); set FULL_SYNC=true to refresh.", run_id)
        return [], None

    params: Dict[str, Any] = {"limit": min(PAGE_SIZE_CLASSIFICATIONS, 100), "offset": 0}
    out: List[Dict[str, Any]] = []
    for page in _paged_get(s, path, params, page_limit_cap=100, run_id=run_id):
        if not page:
            break
        out.extend(page)
    return out, None

# -------------------- shaping --------------------

def _shape_passthrough(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Keep raw; DCR transform handles shape. Customize if you want to prune or rename fields pre-ingest.
    return rows

# -------------------- function entry --------------------

def main(req: func.HttpRequest) -> func.HttpResponse:
    run_id = f"{_iso(_now_utc())}_{uuid4().hex[:8]}"
    start = _now_utc()
    logging.info("CyeraConnector v1.6.1 starting [runId=%s]", run_id)

    try:
        s = _cyera_session(run_id)
    except Exception as e:
        logging.exception("[runId=%s] Cyera login failed", run_id)
        return func.HttpResponse(
            body=json.dumps({"version": "1.6.1", "runId": run_id,
                             "error": "cyera-login-failed", "message": str(e)}, separators=(",", ":")),
            status_code=500, mimetype="application/json"
        )

    results: List[Dict[str, Any]] = []

    # ASSETS
    try:
        if ENABLE_ASSETS:
            logging.info("[runId=%s] Assets: page_size=%d lookback=%dd dryRun=%s",
                         run_id, PAGE_SIZE_ASSETS, LOOKBACK_DAYS, DRY_RUN)
            rows, newest = _collect_assets(s, run_id)
            shaped = _shape_passthrough(rows)
            posts, sent = _ingest_batches(STREAM_ASSETS, shaped, run_id)
            if not DRY_RUN:
                _update_since("assets", _since_for("assets"), newest)
            results.append({"entity": "assets", "fetched": len(rows), "ingested": sent,
                            "posts": posts, "newest": newest})
        else:
            results.append({"entity": "assets", "status": "skipped (disabled)"})
    except Exception as e:
        logging.exception("[runId=%s] Assets failed", run_id)
        results.append({"entity": "assets", "status": f"error: {e}"})

    # IDENTITIES
    try:
        if ENABLE_IDENTITIES:
            logging.info("[runId=%s] Identities: page_size=%d dryRun=%s",
                         run_id, PAGE_SIZE_IDENTITIES, DRY_RUN)
            rows, newest = _collect_identities(s, run_id)
            shaped = _shape_passthrough(rows)
            posts, sent = _ingest_batches(STREAM_IDENTITIES, shaped, run_id)
            # no reliable watermark advancement
            results.append({"entity": "identities", "fetched": len(rows), "ingested": sent, "posts": posts})
        else:
            results.append({"entity": "identities", "status": "skipped (disabled)"})
    except Exception as e:
        logging.exception("[runId=%s] Identities failed", run_id)
        results.append({"entity": "identities", "status": f"error: {e}"})

    # ISSUES
    try:
        if ENABLE_ISSUES:
            logging.info("[runId=%s] Issues: page_size=%d dryRun=%s",
                         run_id, PAGE_SIZE_ISSUES, DRY_RUN)
            rows, newest = _collect_issues(s, run_id)
            shaped = _shape_passthrough(rows)
            posts, sent = _ingest_batches(STREAM_ISSUES, shaped, run_id)
            if not DRY_RUN:
                _update_since("issues", _since_for("issues"), newest)
            results.append({"entity": "issues", "fetched": len(rows), "ingested": sent,
                            "posts": posts, "newest": newest})
        else:
            results.append({"entity": "issues", "status": "skipped (disabled)"})
    except Exception as e:
        logging.exception("[runId=%s] Issues failed", run_id)
        results.append({"entity": "issues", "status": f"error: {e}"})

    # CLASSIFICATIONS
    try:
        if ENABLE_CLASSIFICATIONS:
            logging.info("[runId=%s] Classifications: page_size=%d dryRun=%s",
                         run_id, PAGE_SIZE_CLASSIFICATIONS, DRY_RUN)
            rows, newest = _collect_classifications(s, run_id)
            shaped = _shape_passthrough(rows)
            posts, sent = _ingest_batches(STREAM_CLASSIFICATIONS, shaped, run_id)
            results.append({"entity": "classifications", "fetched": len(rows), "ingested": sent, "posts": posts})
        else:
            results.append({"entity": "classifications", "status": "skipped (disabled)"})
    except Exception as e:
        logging.exception("[runId=%s] Classifications failed", run_id)
        results.append({"entity": "classifications", "status": f"error: {e}"})

    body = {"version": "1.6.1", "runId": run_id, "when": _iso(start), "results": results}
    return func.HttpResponse(json.dumps(body, separators=(",", ":")), status_code=200, mimetype="application/json")
