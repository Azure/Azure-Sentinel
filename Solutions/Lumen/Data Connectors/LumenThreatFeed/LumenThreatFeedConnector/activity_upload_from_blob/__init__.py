import logging
import json
import os
import sys
import tempfile
from typing import Optional
from azure.storage.blob import BlobServiceClient

# Add parent directory to path for importing main module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import LumenSentinelUpdater, LumenSetup, MSALSetup


def _get_blob_container():
    """Get blob container client, creating container if needed."""
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')

    container_name = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenthreatfeed')

    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client(container_name)

    # Create container if it doesn't exist
    try:
        container_client.create_container()
        logging.debug(f"Created blob container: {container_name}")
    except Exception as e:
        # Best-effort create; ignore already-exists
        if "ContainerAlreadyExists" in str(e):
            logging.debug(f"Blob container {container_name} already exists")
        else:
            logging.warning(f"Error creating container {container_name}: {e}")

    return container_client


def main(work_unit):
    """Activity uploads indicators from the given blob to Sentinel

    Reads the JSONL blob via a temp file and processes only the requested window of lines.
    """
    # Extract parameters
    blob_name = work_unit['blob_name']
    indicator_type = work_unit['indicator_type']
    batch_index = work_unit.get('batch_index', 0)
    indicators_per_request = int(work_unit.get('indicators_per_request', 100))
    start_batch: Optional[int] = work_unit.get('start_batch')
    num_batches: Optional[int] = work_unit.get('num_batches')
    config = work_unit['config']
    run_id = work_unit['run_id']
    work_unit_id = work_unit['work_unit_id']
    process_all = work_unit.get('process_all', False)

    logging.debug(f"Processing work unit: {work_unit_id}")

    uploaded_total = 0
    error_total = 0
    throttle_total = 0

    # Determine item window to process (counted by objects, not raw lines)
    if start_batch is not None and num_batches is not None:
        first_index = start_batch * indicators_per_request
        items_to_process = num_batches * indicators_per_request
        window_desc = f"batches {start_batch + 1}-{start_batch + num_batches}"
    elif process_all:
        first_index = 0
        items_to_process = None  # until EOF
        window_desc = "all"
    else:
        first_index = batch_index * indicators_per_request
        items_to_process = indicators_per_request
        window_desc = f"batch {batch_index + 1}"

    try:
        # Initialize updater
        updater = LumenSentinelUpdater(
            LumenSetup(config['LUMEN_API_KEY'], config['LUMEN_BASE_URL'], 3),
            MSALSetup(config['TENANT_ID'], config['CLIENT_ID'], config['CLIENT_SECRET'], config['WORKSPACE_ID'])
        )

        # Prepare blob download
        container_client = _get_blob_container()
        blob_client = container_client.get_blob_client(blob_name)

        # Stream download to a temp file to avoid memory spikes
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            tmp_path = tmp.name
            downloader = blob_client.download_blob()
            downloader.readinto(tmp)

        # Now iterate the file line by line and process only the selected window of objects
        buffer = []
        CHUNK = indicators_per_request  # logical chunk to send to API
        skipped = 0
        processed_in_window = 0

        def flush_buffer(batch_info_suffix: str):
            nonlocal uploaded_total, error_total, throttle_total, buffer
            if not buffer:
                return
            result = updater.upload_indicators_to_sentinel(buffer, batch_info_suffix)
            uploaded_total += result.get('uploaded_count', 0)
            error_total += result.get('error_count', 0)
            throttle_total += result.get('throttle_events', 0)
            buffer = []

        try:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                # Skip objects before the window
                while skipped < first_index:
                    line = f.readline()
                    if line == '':
                        break  # EOF
                    if not line.strip():
                        continue
                    skipped += 1

                # Process exactly items_to_process (or until EOF) for this window
                for line in f:
                    if items_to_process is not None and processed_in_window >= items_to_process:
                        break
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        # count malformed object as processed and record error
                        error_total += 1
                        processed_in_window += 1
                        continue
                    buffer.append(obj)
                    processed_in_window += 1
                    if len(buffer) >= CHUNK:
                        flush_buffer(f"({indicator_type} {window_desc})")

                # Flush any remainder for this window (can be < 100)
                flush_buffer(f"({indicator_type} {window_desc})")
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
