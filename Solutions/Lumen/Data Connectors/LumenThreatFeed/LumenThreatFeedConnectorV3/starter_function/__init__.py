import logging, os, uuid, json, azure.functions as func, azure.durable_functions as df
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import requests, ijson
from main import LumenSetup, MSALSetup, LumenSentinelUpdater, INDICATOR_TYPES

CONFIDENCE_THRESHOLD = int(os.environ.get('LUMEN_CONFIDENCE_THRESHOLD', '60'))
BLOB_CONTAINER = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenti')


def _get_blob_client():
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING not set')
    svc = BlobServiceClient.from_connection_string(conn)
    container = svc.get_container_client(BLOB_CONTAINER)
    try:
        container.create_container()
    except Exception:
        pass
    return container


def _stream_and_filter_to_blob(container, indicator_type, presigned_url, run_id):
    blob_name = f"runs/{run_id}/{indicator_type}.jsonl"  # newline-delimited STIX objects
    blob_client = container.get_blob_client(blob_name)
    buffer = []
    max_block = 1024 * 1024  # 1MB buffer flush size
    current_size = 0
    total = kept = filtered = 0
    logging.info(f"Downloading & filtering {indicator_type} → {blob_name}")
    with requests.get(presigned_url, stream=True, timeout=300) as r:
        r.raise_for_status()
        # raw stream parser
        parser = ijson.items(r.raw, 'stixobjects.item')
        for obj in parser:
            total += 1
            include = True
            if obj.get('type') == 'indicator':
                c = obj.get('confidence')
                try:
                    if c is not None and int(c) < CONFIDENCE_THRESHOLD:
                        include = False
                except Exception:
                    pass
            if include:
                kept += 1
                line = json.dumps(obj, separators=(',', ':')) + '\n'
                enc = line.encode('utf-8')
                buffer.append(enc)
                current_size += len(enc)
            else:
                filtered += 1
            # flush if buffer large
            # keep running length counter instead of summing each flush check
            if current_size >= max_block:
                blob_client.upload_blob(b''.join(buffer), blob_type='BlockBlob', overwrite=not blob_client.exists())
                buffer.clear()
                current_size = 0
    if buffer:
        blob_client.upload_blob(b''.join(buffer), blob_type='BlockBlob', overwrite=not blob_client.exists())
    logging.info(f"{indicator_type}: total={total} kept={kept} filtered={filtered}")
    return {
        'blob_name': blob_name,
        'indicator_type': indicator_type,
        'estimated_indicators': kept,
        'filtered_out': filtered,
        'total_downloaded': total
    }


async def main(req: func.HttpRequest, starter: str):
    try:
        run_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:6]
        logging.info(f"Starting Threat Feed V3 run {run_id}")
        client = df.DurableOrchestrationClient(starter)

        lumen_setup = LumenSetup(os.environ.get('LUMEN_API_KEY'), os.environ.get('LUMEN_BASE_URL'), 3)
        msal_setup = MSALSetup(os.environ.get('TENANT_ID'), os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'), os.environ.get('WORKSPACE_ID'))
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)

        presigned = updater.get_lumen_presigned_urls(INDICATOR_TYPES)
        container = _get_blob_client()
        sources = []
        total_post_filter = 0
        for itype, url in presigned.items():
            info = _stream_and_filter_to_blob(container, itype, url, run_id)
            sources.append(info)
            total_post_filter += info['estimated_indicators']

        config = {
            'LUMEN_API_KEY': os.environ.get('LUMEN_API_KEY'),
            'LUMEN_BASE_URL': os.environ.get('LUMEN_BASE_URL'),
            'CLIENT_ID': os.environ.get('CLIENT_ID'),
            'CLIENT_SECRET': os.environ.get('CLIENT_SECRET'),
            'TENANT_ID': os.environ.get('TENANT_ID'),
            'WORKSPACE_ID': os.environ.get('WORKSPACE_ID'),
            'CONFIDENCE_THRESHOLD': CONFIDENCE_THRESHOLD,
            'RUN_ID': run_id,
            'BLOB_CONTAINER': BLOB_CONTAINER
        }

        input_data = {
            'blob_sources': sources,
            'config': config,
            'indicators_per_request': 100
        }

        instance_id = await client.start_new('orchestrator_function', None, input_data)
        logging.info(f"Started orchestration {instance_id} run {run_id} indicators={total_post_filter}")
        return client.create_check_status_response(req, instance_id)
    except Exception as e:
        logging.error(f"Starter V3 error: {e}")
        return func.HttpResponse(str(e), status_code=500)
