# Lumen Threat Feed Connector V3 (Blob-backed Durable)

This version eliminates reliance on local temp files by streaming each indicator type directly
from the Lumen presigned URL into Azure Blob Storage (newline-delimited JSON). Durable Functions
then fan-out over blob segments, ensuring scale-out safety. Confidence filtering is applied
upfront during streaming to reduce volume and improve throughput.

## Functions
- starter_function: HTTP trigger to start a run. Streams + filters to blobs, starts orchestration.
- orchestrator_function_v3: Builds work units (1000 indicators each) and throttles to ~95 req/min.
- activity_upload_from_blob: Reads newline-delimited STIX objects from blob, batches (100) to Sentinel.
- activity_cleanup_blob: Deletes blobs when processing completes.

## Environment Variables
Required (existing): LUMEN_API_KEY, LUMEN_BASE_URL, CLIENT_ID, CLIENT_SECRET, TENANT_ID, WORKSPACE_ID
New:
- LUMEN_BLOB_CONNECTION_STRING: Connection string to a storage account
- LUMEN_BLOB_CONTAINER (optional, default 'lumenti')
- LUMEN_CONFIDENCE_THRESHOLD (optional, default 60)

## Blob Layout
runs/{run_id}/{indicator_type}.jsonl
Each line is a single STIX object (post-filter).

## Migration Notes
- Replace previous temp file approach; no /tmp dependencies.
- If you need to retain raw unfiltered data, fork the streaming function to write a `raw/` copy.

## TODO / Enhancements
- Add reactive throttling based on actual 429 responses.
- Add optional retention policy (skip cleanup).
- Add aggregated metrics emission to Application Insights.
