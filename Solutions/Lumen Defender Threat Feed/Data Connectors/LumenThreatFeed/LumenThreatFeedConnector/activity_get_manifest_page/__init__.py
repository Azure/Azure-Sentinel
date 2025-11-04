import json
import logging
import os
from azure.storage.blob import BlobServiceClient


def _get_blob_container():
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')

    container_name = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenthreatfeed')
    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client(container_name)
    return container_client


def main(work):
    """Return a page slice from the manifest blob.

    work = {
        'manifest_blob_name': str,
        'offset': int,
        'limit': int
    }
    """
    manifest_blob_name = work['manifest_blob_name']
    offset = int(work.get('offset', 0))
    limit = int(work.get('limit', 1000))

    container_client = _get_blob_container()
    blob_client = container_client.get_blob_client(manifest_blob_name)
    content = blob_client.download_blob(max_concurrency=1).readall()
    items = json.loads(content)
    # Return a slice of items
    page = items[offset: offset + limit]
    return {
        'items': page,
        'next_offset': offset + len(page),
        'has_more': (offset + len(page)) < len(items),
        'total': len(items)
    }
