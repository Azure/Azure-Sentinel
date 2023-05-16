import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import azure.functions as func
from shared_code import configurations, utils
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.data_collector import LogAnalytics
from shared_code.models.oat import OATTaskMessage
from shared_code.services import oat_service
from shared_code.trace_utils.trace import trace_manager

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()
MAX_OAT_QUERY_MINUTES = configurations.get_max_oat_query_minutes()
MAX_OAT_DATA_RETENTION_DAY = configurations.get_max_oat_data_retention_day()
DEFAULT_OAT_QUERY_MINUTES = configurations.get_default_oat_query_minutes()
OAT_QUERY_TIME_BUFFER_MINUTES = configurations.get_oat_query_time_buffer_minutes()
OAT_PIPELINE_DATETIME_FORMAT = configurations.get_oat_pipeline_datetime_format()
LOG_TYPE = configurations.get_oat_health_check_log_type()

OAT_TABLE_NAME = 'XdrOatConnectorStatus'

logger = get_customized_json_logger()


def generate_time(
    clp_id: str, token: str
) -> Tuple[Optional[datetime], Optional[datetime]]:
    current_time = datetime.now(timezone.utc)
    end_time = current_time - timedelta(minutes=OAT_QUERY_TIME_BUFFER_MINUTES)
    start_time = utils.get_last_success_time(OAT_TABLE_NAME, clp_id)
    if start_time is None:
        start_time = end_time - timedelta(minutes=DEFAULT_OAT_QUERY_MINUTES)
    else:
        if start_time < current_time - timedelta(days=MAX_OAT_DATA_RETENTION_DAY):
            start_time = (
                current_time
                - timedelta(days=MAX_OAT_DATA_RETENTION_DAY)
                + timedelta(minutes=OAT_QUERY_TIME_BUFFER_MINUTES)
            )

            pipeline_id = oat_service.get_oat_pipeline_id(clp_id)

            if not pipeline_id:
                logger.info(
                    f'Cannot get the pipeline id in table for customer [{clp_id}].'
                )
                pipeline_id = oat_service.register_oat_and_get_pipeline_id(
                    token, configurations.get_oat_config(), clp_id
                )
                oat_service.update_oat_pipeline_id(clp_id, pipeline_id)
            else:
                is_registered = oat_service.is_registered_by_pipeline_id(
                    token, pipeline_id
                )
                if not is_registered:
                    pipeline_id = oat_service.register_oat_and_get_pipeline_id(
                        token, configurations.get_oat_config(), clp_id
                    )
                    oat_service.update_oat_pipeline_id(clp_id, pipeline_id)

        if start_time + timedelta(minutes=MAX_OAT_QUERY_MINUTES) < end_time:
            end_time = start_time + timedelta(minutes=MAX_OAT_QUERY_MINUTES)

    # avoid get log cover by last end_time
    start_time = start_time + timedelta(seconds=1)

    if start_time >= end_time:
        return None, None

    return start_time, end_time


def main(myTimer: func.TimerRequest, oatTaskMsg: func.Out[List[str]]) -> None:

    log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, LOG_TYPE)
    error = None
    for token in API_TOKENS:
        try:
            trace_manager.task_id = str(uuid.uuid4())
            health_check_data = {}
            clp_id = utils.get_clp_id(token)
            health_check_data['clpId'] = clp_id

            start_time, end_time = generate_time(clp_id, token)
            if start_time is None or end_time is None:
                logger.warning(
                    f'Start time or End time is None, Stop processing clp: {clp_id}.'
                )
                continue

            start_time_str = start_time.strftime(OAT_PIPELINE_DATETIME_FORMAT)
            end_time_str = end_time.strftime(OAT_PIPELINE_DATETIME_FORMAT)
            health_check_data['queryStartTime'] = start_time_str
            health_check_data['queryEndTime'] = end_time_str

            logger.info(
                f'start to send oat task events clp_id: {clp_id} '
                f'from {start_time_str} to {end_time_str}.'
            )

            utils.send_message_to_storage_queue(
                configurations.get_oat_pipeline_task_queue_name(),
                OATTaskMessage(
                    clp_id=clp_id,
                    start_time=start_time_str,
                    end_time=end_time_str,
                    task_id=trace_manager.task_id,
                ).json(),
            )

            utils.update_last_success_time(OAT_TABLE_NAME, clp_id, end_time)
        except Exception as e:
            logger.exception(f'Internal error. Exception: {str(e)}.')
            error, health_check_data['error'] = e, str(e)
        finally:
            # send health check log to log analytics
            log_analytics.post_data(health_check_data)

    if error:
        raise error
