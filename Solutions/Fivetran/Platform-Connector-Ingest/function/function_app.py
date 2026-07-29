"""
Fivetran Platform Connector -> Sentinel ingest function (all Platform tables).

Event Grid (Blob Created on the ADLS Gen2 lake) -> this Azure Function -> Azure
Monitor Logs Ingestion API -> DCR (kind: Direct) -> Sentinel custom tables.

The Fivetran Platform Connector lands 12 tables into the managed data lake, each as
its own Delta + Iceberg (UniForm) table:

    audit_trail, user, team, team_membership, role, role_permission,
    role_connector_type, resource_membership, connection, destination,
    account, connector_type

Row parquet lives under .../<table>/data/*.parquet, alongside a Delta _delta_log/ and
Iceberg metadata/ (*.metadata.json + *.avro). We only process blobs whose path contains
'/<table>/data/' and end in '.parquet', which skips _delta_log checkpoint parquet,
Iceberg avro/json metadata, and orphans/.

Routing (two Sentinel tables, one DCR):
  - audit_trail  -> typed  Custom-Fivetran_AuditTrail_CL  (security events, typed cols)
  - all others   -> generic Custom-Fivetran_Platform_CL   ({FivetranTable, Record json})

Delta/Iceberg compaction can rewrite data files, re-emitting rows already ingested, so
downstream KQL MUST dedupe by the immutable primary key (audit `id`, else per-table id
inside Record). This connector is deliberately at-least-once; correctness comes from the
dedupe (the ASIM parser dedupes audit_trail by id), not the transport.

Auth is managed identity end to end (DefaultAzureCredential):
  - Storage Blob Data Reader on the storage account  -> read the parquet
  - Monitoring Metrics Publisher on the DCR           -> post to logsIngestion
  When a user-assigned managed identity is used, set the app setting AZURE_CLIENT_ID to
  the identity's client id so DefaultAzureCredential selects it.

App settings (see local.settings.json.example):
  DCR_ENDPOINT        DCR logs ingestion endpoint (https://<dcr>-xxxx.<region>.ingest.monitor.azure.com)
  DCR_RULE_ID         DCR properties.immutableId
  AUDIT_STREAM        default Custom-Fivetran_AuditTrail_CL
  PLATFORM_STREAM     default Custom-Fivetran_Platform_CL
  AZURE_CLIENT_ID     (optional) client id of the user-assigned managed identity
"""

import io
import json
import logging
import os

import azure.functions as func
import pyarrow.parquet as pq
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.storage.blob import BlobClient

app = func.FunctionApp()

_credential = DefaultAzureCredential()
_logs_client = LogsIngestionClient(
    endpoint=os.environ["DCR_ENDPOINT"],
    credential=_credential,
    logging_enable=False,
)

_RULE_ID = os.environ["DCR_RULE_ID"]
_AUDIT_STREAM = os.environ.get("AUDIT_STREAM", "Custom-Fivetran_AuditTrail_CL")
_PLATFORM_STREAM = os.environ.get("PLATFORM_STREAM", "Custom-Fivetran_Platform_CL")

# The 12 Fivetran Platform Connector tables we ingest.
_TABLES = {
    "audit_trail",
    "user",
    "team",
    "team_membership",
    "role",
    "role_permission",
    "role_connector_type",
    "resource_membership",
    "connection",
    "destination",
    "account",
    "connector_type",
}

# Typed projection for audit_trail. old_values / new_values are JSON strings in parquet
# and are parsed to dynamic by the DCR transformKql.
_AUDIT_COLUMNS = [
    "id",
    "captured_at",
    "user_id",
    "action",
    "interaction_method",
    "primary_resource_type",
    "primary_resource_id",
    "secondary_resource_type",
    "secondary_resource_id",
    "old_values",
    "new_values",
]


def _jsonable(value):
    """Make parquet cell values JSON-serialisable (datetimes -> ISO 8601)."""
    isoformat = getattr(value, "isoformat", None)
    return isoformat() if callable(isoformat) else value


def _table_name(blob_url: str) -> str | None:
    """Return the Fivetran table name from '.../<table>/data/<file>.parquet'."""
    marker = "/data/"
    if marker not in blob_url:
        return None
    prefix = blob_url.rsplit(marker, 1)[0]
    return prefix.rsplit("/", 1)[-1]


def _audit_rows(records: list[dict]) -> list[dict]:
    rows = []
    for rec in records:
        rows.append({col: _jsonable(rec.get(col)) for col in _AUDIT_COLUMNS if col in rec})
    return rows


def _platform_rows(table: str, records: list[dict]) -> list[dict]:
    rows = []
    for rec in records:
        clean = {k: _jsonable(v) for k, v in rec.items()}
        rows.append({"FivetranTable": table, "Record": json.dumps(clean, default=str)})
    return rows


@app.function_name(name="FivetranPlatformIngest")
@app.event_grid_trigger(arg_name="event")
def ingest(event: func.EventGridEvent):
    data = event.get_json()
    blob_url = data.get("url", "")
    api = data.get("api", "")

    if api not in ("PutBlob", "PutBlockList", "FlushWithClose", ""):
        logging.info("Skipping event api=%s for %s", api, blob_url)
        return

    if not blob_url.endswith(".parquet") or "/data/" not in blob_url:
        logging.info("Skipping non /data/*.parquet blob: %s", blob_url)
        return

    table = _table_name(blob_url)
    if table not in _TABLES:
        logging.info("Skipping unknown/uningested table '%s': %s", table, blob_url)
        return

    logging.info("Processing %s blob: %s", table, blob_url)
    blob = BlobClient.from_blob_url(blob_url, credential=_credential)
    raw = blob.download_blob().readall()
    records = pq.read_table(io.BytesIO(raw)).to_pylist()
    if not records:
        logging.info("No rows in %s", blob_url)
        return

    if table == "audit_trail":
        stream, rows = _AUDIT_STREAM, _audit_rows(records)
    else:
        stream, rows = _PLATFORM_STREAM, _platform_rows(table, records)

    # LogsIngestionClient gzips and splits into <=1 MB requests automatically.
    _logs_client.upload(rule_id=_RULE_ID, stream_name=stream, logs=rows)
    logging.info("Uploaded %d rows from %s to %s", len(rows), table, stream)
