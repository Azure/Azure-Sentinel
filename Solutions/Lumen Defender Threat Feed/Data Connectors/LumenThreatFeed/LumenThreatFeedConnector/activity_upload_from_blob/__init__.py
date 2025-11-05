import logging
import json
import os
import sys
import tempfile
from typing import Optional
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

# Add parent directory to path for importing main module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import LumenSentinelUpdater, LumenSetup, MSALSetup

# Suppress verbose Azure SDK HTTP logs
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
logging.getLogger('azure.storage').setLevel(logging.ERROR)


def _get_blob_container():
    """Get blob container client, creating container if needed."""
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')

    container_name = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenthreatfeed')

    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client(container_name)

    # Create container if it doesn't exist (avoid 409 by probing first)
    try:
        if not container_client.exists():
            container_client.create_container()
            logging.debug(f"Created blob container: {container_name}")
        else:
            logging.debug(f"Blob container already present: {container_name}")
    except ResourceExistsError:
        logging.debug(f"Blob container {container_name} already exists (race)")
    except Exception as e:
        logging.warning(f"Error ensuring container {container_name}: {e}")

    return container_client


def main(work_unit):
    """Activity uploads indicators for a single chunk-blob to Sentinel.

    Downloads the JSONL blob and uploads objects in batches of 100. If rate-limited and
    external_backoff flag is set, returns a throttled signal with suggested retry_after seconds.
    """
    # Extract parameters
    blob_name = work_unit['blob_name']
    indicator_type = work_unit['indicator_type']
    indicators_per_request = int(work_unit.get('indicators_per_request', 100))
    run_id = work_unit['run_id']
    work_unit_id = work_unit['work_unit_id']
    # Default to internal backoff to avoid orchestrator timer floods
    external_backoff = bool(work_unit.get('external_backoff', False))

    logging.info(f"Processing work unit: {work_unit_id}")

    uploaded_total = 0
    error_total = 0
    throttle_total = 0

    window_desc = "chunk"

    try:
        # Initialize updater from environment (avoid secrets in inputs)
        api_key = os.environ.get('LUMEN_API_KEY')
        base_url = os.environ.get('LUMEN_BASE_URL')
        tenant_id = os.environ.get('TENANT_ID')
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
        workspace_id = os.environ.get('WORKSPACE_ID')

        missing = [k for k, v in {
            'LUMEN_API_KEY': api_key,
            'LUMEN_BASE_URL': base_url,
            'TENANT_ID': tenant_id,
            'CLIENT_ID': client_id,
            'CLIENT_SECRET': client_secret,
            'WORKSPACE_ID': workspace_id,
        }.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

        updater = LumenSentinelUpdater(
            LumenSetup(api_key, base_url, 3),
            MSALSetup(tenant_id, client_id, client_secret, workspace_id)
        )

        # Prepare blob download
        container_client = _get_blob_container()
        blob_client = container_client.get_blob_client(blob_name)

        # Stream download to a temp file to avoid memory spikes
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            tmp_path = tmp.name
            downloader = blob_client.download_blob()
            downloader.readinto(tmp)

        # Now iterate the file line by line and process all objects in this chunk blob
        buffer = []
        CHUNK = indicators_per_request  # logical chunk to send to API

        def flush_buffer(batch_info_suffix: str):
            nonlocal uploaded_total, error_total, throttle_total, buffer
            if not buffer:
                return
            result = updater.upload_indicators_to_sentinel(buffer, batch_info_suffix, external_backoff=external_backoff)
            if result.get('throttled'):
                # return early to let the orchestrator back off
                return result
            uploaded_total += result.get('uploaded_count', 0)
            error_total += result.get('error_count', 0)
            throttle_total += result.get('throttle_events', 0)
            buffer = []

        try:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        # count malformed object as processed and record error
                        error_total += 1
                        continue
                    buffer.append(obj)
                    if len(buffer) >= CHUNK:
                        result = flush_buffer(f"({indicator_type} {window_desc})")
                        if isinstance(result, dict) and result.get('throttled'):
                            return result

                # Flush any remainder for this window (can be < 100)
                result = flush_buffer(f"({indicator_type} {window_desc})")
                if isinstance(result, dict) and result.get('throttled'):
                    return result
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        logging.debug(
            f"✓ Work unit {work_unit_id} completed: uploaded={uploaded_total}, errors={error_total}, throttles={throttle_total}"
        )
        return {'uploaded_count': uploaded_total, 'error_count': error_total, 'throttle_events': throttle_total}

    except Exception as e:
        logging.error(f"Activity error for {work_unit_id}: {e}", exc_info=True)
        return {
            'uploaded_count': 0,
            'error_count': error_total,
            'throttle_events': throttle_total,
            'error': str(e)
        }
