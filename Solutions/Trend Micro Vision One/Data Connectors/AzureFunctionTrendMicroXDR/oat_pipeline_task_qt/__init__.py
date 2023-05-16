from typing import Dict, List

import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient, UpdateMode
from shared_code import configurations, utils
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.models.oat import OATFileMessage, OATTaskMessage
from shared_code.services import oat_service
from shared_code.trace_utils.trace import trace_manager

API_TOKENS = configurations.get_api_tokens()
STORAGE_CONNECTION_STRING = configurations.get_storage_connection_string()
REGISTER_STATUS_TABLE = 'XdrOatRegisterStatus'

logger = get_customized_json_logger()


def _build_oat_file_queue_message(
    clp_id: str, oat_package_list: List[Dict], pipeline_id: str
):
    return [
        OATFileMessage(
            clp_id=clp_id,
            package_id=package_item['id'],
            task_id=trace_manager.task_id,
            pipeline_id=pipeline_id,
        ).json()
        for package_item in oat_package_list
    ]


def main(
    oatTaskMsg: func.QueueMessage,
    oatFileMsg: func.Out[List[str]],
) -> None:

    taskMessage = OATTaskMessage.parse_obj(oatTaskMsg.get_json())
    try:
        clp_id = taskMessage.clp_id
        start_time = taskMessage.start_time
        end_time = taskMessage.end_time
        if taskMessage.task_id:
            trace_manager.task_id = taskMessage.task_id
        else:
            logger.info(f'No task id from msg, create new: {trace_manager.task_id}.')

        token = utils.find_token_by_clp(clp_id, API_TOKENS)
        if not token:
            logger.warning(f'Account token not found, clp: {clp_id}, stop current job.')
            return

        pipeline_id = oat_service.get_oat_pipeline_id(clp_id)

        if not pipeline_id:
            logger.info(f'Cannot get the pipeline id in table for customer [{clp_id}].')
            pipeline_id = oat_service.register_oat_and_get_pipeline_id(
                token, configurations.get_oat_config(), clp_id
            )
            oat_service.update_oat_pipeline_id(clp_id, pipeline_id)

        count, package_list = oat_service.get_oat_package_list(
            token, start_time, end_time, pipeline_id
        )
        if count == 0:
            logger.info(
                f'Get no oat package list, stop processing, queue msg: {taskMessage}'
            )
            return

        logger.info(
            f'Get oat package list for clp id: {clp_id}, count: {count}, pipeline id: {pipeline_id}.'
        )
        file_msg = _build_oat_file_queue_message(clp_id, package_list, pipeline_id)
        oatFileMsg.set(file_msg)
    except Exception as e:
        logger.exception(f'Internal error. Exception: {str(e)}')
        raise
