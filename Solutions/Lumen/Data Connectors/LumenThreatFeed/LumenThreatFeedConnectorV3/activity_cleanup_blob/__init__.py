import logging, os
from azure.storage.blob import BlobServiceClient

def _get_blob_client(config):
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING not set')
    svc = BlobServiceClient.from_connection_string(conn)
    return svc.get_container_client(config['BLOB_CONTAINER'])


def main(params: dict) -> dict:
    blob_name = params['blob_name']
    indicator_type = params.get('indicator_type','unknown')
    config = params['config']
    try:
        container = _get_blob_client(config)
        blob_client = container.get_blob_client(blob_name)
        if blob_client.exists():
            size = blob_client.get_blob_properties().size
            blob_client.delete_blob()
            logging.info(f"Deleted blob {blob_name} ({size/1024/1024:.2f} MB) for {indicator_type}")
            return {'success': True, 'blob_name': blob_name}
        else:
            logging.warning(f"Blob not found during cleanup {blob_name}")
            return {'success': True, 'blob_name': blob_name, 'warning': 'not found'}
    except Exception as e:
        logging.error(f"Blob cleanup error {blob_name}: {e}")
        return {'success': False, 'blob_name': blob_name, 'error': str(e)}
