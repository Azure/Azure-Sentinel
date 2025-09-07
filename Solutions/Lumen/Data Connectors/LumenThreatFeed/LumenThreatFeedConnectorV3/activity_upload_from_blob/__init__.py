import logging, os
from azure.storage.blob import BlobServiceClient
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater


def _get_blob_client(config):
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING not set')
    svc = BlobServiceClient.from_connection_string(conn)
    return svc.get_container_client(config['BLOB_CONTAINER'])


def main(params: dict) -> dict:
    blob_name = params['blob_name']
    indicator_type = params['indicator_type']
    start_index = params.get('start_index', 0)
    max_indicators = params.get('max_indicators', 1000)
    work_unit_id = params.get('work_unit_id', 'wu')
    config = params['config']
    per_request = params.get('indicators_per_request', 100)

    try:
        container = _get_blob_client(config)
        blob_client = container.get_blob_client(blob_name)
        if not blob_client.exists():
            return {'success': False, 'error': 'blob not found', 'work_unit_id': work_unit_id}

        lumen_setup = LumenSetup(config['LUMEN_API_KEY'], config['LUMEN_BASE_URL'], 3)
        msal_setup = MSALSetup(config['TENANT_ID'], config['CLIENT_ID'], config['CLIENT_SECRET'], config['WORKSPACE_ID'])
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        if not updater.bearer_token:
            updater.bearer_token, updater.token_expiry_seconds = updater.acquire_token()

        indicators_uploaded = 0
        requests_made = 0
        chunk = []
        current_index = 0
        throttle_events_total = 0

        stream = blob_client.download_blob()
        for line in stream.chunks():
            for raw in line.split(b'\n'):
                if not raw:
                    continue
                if current_index < start_index:
                    current_index += 1
                    continue
                if indicators_uploaded >= max_indicators:
                    break
                try:
                    import json
                    obj = json.loads(raw)
                except Exception:
                    continue
                chunk.append(obj)
                current_index += 1
                if len(chunk) >= per_request:
                    throttle_events = 0
                    attempt = 0
                    while True:
                        resp = updater.upload_stix_objects_to_sentinel(updater.bearer_token, chunk)
                        if resp.status_code == 200:
                            break
                        if resp.status_code == 429 and attempt < 3:
                            throttle_events += 1
                            attempt += 1
                            import time as _t
                            _t.sleep(2 ** attempt)
                            continue
                        return {'success': False, 'error': f'status {resp.status_code}', 'work_unit_id': work_unit_id,
                                'indicators_uploaded': indicators_uploaded, 'requests_made': requests_made, 'throttle_events': throttle_events_total + throttle_events}
                    indicators_uploaded += len(chunk)
                    requests_made += 1
                    throttle_events_total += throttle_events
                    chunk.clear()
            if indicators_uploaded >= max_indicators:
                break

        if chunk:
            throttle_events = 0
            attempt = 0
            while True:
                resp = updater.upload_stix_objects_to_sentinel(updater.bearer_token, chunk)
                if resp.status_code == 200:
                    break
                if resp.status_code == 429 and attempt < 3:
                    throttle_events += 1
                    attempt += 1
                    import time as _t
                    _t.sleep(2 ** attempt)
                    continue
                return {'success': False, 'error': f'status {resp.status_code}', 'work_unit_id': work_unit_id,
                        'indicators_uploaded': indicators_uploaded, 'requests_made': requests_made, 'throttle_events': throttle_events_total + throttle_events}
            indicators_uploaded += len(chunk)
            requests_made += 1
            throttle_events_total += throttle_events

        logging.info(f"WU {work_unit_id} {indicator_type} uploaded {indicators_uploaded} in {requests_made} requests (throttle_events={throttle_events_total})")
        return {'success': True, 'work_unit_id': work_unit_id, 'indicator_type': indicator_type,
                'indicators_uploaded': indicators_uploaded, 'requests_made': requests_made, 'throttle_events': throttle_events_total}
    except Exception as e:
        logging.error(f"Activity blob upload error {work_unit_id}: {e}")
        return {'success': False, 'error': str(e), 'work_unit_id': work_unit_id, 'indicators_uploaded': 0, 'requests_made': 0}
