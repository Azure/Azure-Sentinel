import json
import logging
import os
import time
from ..models.connection import GuardicoreConnection
from .authentication import GuardicoreAuth
from .pagination import PaginatedResponse
from ...generic_utilities.sentinel import AzureSentinel


async def run_import_loop(destination_table: str, api_endpoint: str, method: str, params: dict,
                          chunk_size=PaginatedResponse.ENTITIES_PER_PAGE,
                          slot_identifier: str = None,
                          max_runtime_in_seconds:int = 300) -> None:
    logging.info(f'Starting import loop for {destination_table}')
    azure_connection = AzureSentinel(
        workspace_id=os.environ.get('SentinelWorkspaceId', ''),
        workspace_key=os.environ.get('SentinelWorkspaceKey', ''),
        log_analytics_url=os.getenv('logAnalyticsUri', '')
    )
    entities_found = 0
    url = os.environ.get('GuardicoreUrl', '')
    authentication_object = GuardicoreAuth(
        url=url,
        user=os.environ.get('GuardicoreUser', ''),
        password=os.environ.get('GuardicorePassword', '')
    )
    items_batch = []

    start_time = time.time()
    max_runtime_seconds = max_runtime_in_seconds  # 5 minutes
    timeout_reached = False

    async for item in PaginatedResponse(
            endpoint=f'{url}/{api_endpoint}',
            request_type=method,
            params=params,
            authentication=authentication_object,
            chunk_size=chunk_size).items():
        if time.time() - start_time > max_runtime_seconds:
            logging.info(f"Maximum runtime of 5 minutes reached. Interrupting import loop for {destination_table}")
            timeout_reached = True
            break

        entities_found += 1
        try:
            full_data = {**item, 'slot_identifier': slot_identifier}
            items_batch.append(GuardicoreConnection(**full_data).model_dump())
            if len(items_batch) >= chunk_size:
                logging.info(f"Posting {len(items_batch)} entities to Sentinel table {destination_table}")
                await azure_connection.post_data(body=json.dumps(items_batch), log_type=destination_table)
                logging.info(f"Posted {len(items_batch)} entities to Sentinel table {destination_table}")
                items_batch.clear()

        except Exception as e:
            logging.info(type(e))
            logging.exception(f"Failed to post data to Sentinel: {e}")
            logging.error(f"Failed data: {item}")

    if len(items_batch) > 0:
        try:
            logging.info(f"Posting {len(items_batch)} entities to Sentinel")
            await azure_connection.post_data(body=json.dumps(items_batch), log_type=destination_table)
            logging.info(f"Posted {len(items_batch)} entities to Sentinel")
        except Exception as e:
            logging.info(type(e))
            logging.exception(f"Failed to post data to Sentinel: {e}")
            logging.error(f"Failed data: {items_batch}")

    if timeout_reached:
        logging.warning(f"Import loop for {destination_table} was interrupted due to timeout. Processed {entities_found} entities")
    else:
        logging.info(f"Processed {entities_found} entities")
