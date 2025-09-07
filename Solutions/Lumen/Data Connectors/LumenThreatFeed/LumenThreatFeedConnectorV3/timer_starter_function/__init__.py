import logging, os, uuid, azure.functions as func, azure.durable_functions as df
from datetime import datetime
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater, INDICATOR_TYPES
from ..starter_function import _get_blob_client, _stream_and_filter_to_blob, CONFIDENCE_THRESHOLD, BLOB_CONTAINER


def main(mytimer: func.TimerRequest, starter: str):
    try:
        run_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:6]
        logging.info(f"Timer V3 run {run_id} triggered")
        client = df.DurableOrchestrationClient(starter)
        lumen_setup = LumenSetup(os.environ.get('LUMEN_API_KEY'), os.environ.get('LUMEN_BASE_URL'), 3)
        msal_setup = MSALSetup(os.environ.get('TENANT_ID'), os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'), os.environ.get('WORKSPACE_ID'))
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        presigned = updater.get_lumen_presigned_urls(INDICATOR_TYPES)
        container = _get_blob_client()
        sources = []
        for itype, url in presigned.items():
            info = _stream_and_filter_to_blob(container, itype, url, run_id)
            sources.append(info)
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
        input_data = {'blob_sources': sources, 'config': config, 'indicators_per_request': 100}
        instance_id = client.start_new('orchestrator_function_v3', None, input_data)
        logging.info(f"Timer started orchestration V3 {instance_id}")
    except Exception as e:
        logging.error(f"Timer starter V3 error: {e}")
