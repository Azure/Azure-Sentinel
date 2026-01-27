import datetime
import json
import logging
import os
import time
from typing import Type

from .authentication import GuardicoreAuth
from .pagination import PaginatedResponse
from .sentinel import AzureSentinel


async def run_import_loop(destination_table: str, api_endpoint: str, method: str, params: dict, model_class: Type,
                          add_sampling_timestamp: bool = False,
                          field_name_for_last_timestamp: str | None = None,
                          chunk_size=PaginatedResponse.ENTITIES_PER_PAGE,
                          max_runtime_in_seconds:int = 300) -> str:
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
    sampling_timestamp = int(datetime.datetime.now(tz=datetime.UTC).timestamp())
    last_time = 0

    # Set the start time for the timeout check
    start_time = time.time()
    max_runtime_seconds = max_runtime_in_seconds  # 5 minutes
    timeout_reached = False

    async for item in PaginatedResponse(
            endpoint=f'{url}/{api_endpoint}',
            request_type=method,
            params=params,
            authentication=authentication_object,
            chunk_size=chunk_size).items():
        # Check if we've exceeded the time limit
        if time.time() - start_time > max_runtime_seconds:
            logging.info(f"Maximum runtime of 5 minutes reached. Interrupting import loop for {destination_table}")
            timeout_reached = True
            break

        entities_found += 1
        try:
            if add_sampling_timestamp:
                full_data = {**item, 'sampling_timestamp': sampling_timestamp}
            else:
                full_data = item
            items_batch.append(model_class(**full_data).model_dump())
            if len(items_batch) >= chunk_size:
                logging.info(f"Posting {len(items_batch)} entities to Sentinel table {destination_table}")
                await azure_connection.post_data(body=json.dumps(items_batch), log_type=destination_table)
                logging.info(f"Posted {len(items_batch)} entities to Sentinel table {destination_table}")
                items_batch.clear()
            if field_name_for_last_timestamp:
                potential_next_conn_time = int(item[field_name_for_last_timestamp]) + 1
                if potential_next_conn_time > last_time:
                    last_time = potential_next_conn_time

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

    return str(last_time)
