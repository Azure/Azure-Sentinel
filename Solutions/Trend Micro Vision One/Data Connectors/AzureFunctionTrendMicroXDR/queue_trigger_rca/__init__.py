import azure.functions as func

from requests.exceptions import HTTPError
from shared_code.services.workbench_service import get_rca_task_detail
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)

from shared_code import utils, configurations, utils, transform_utils
from shared_code.exceptions import GeneralException
from shared_code.data_collector import LogAnalytics
from shared_code.trace_utils.trace import trace_manager

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()

logger = get_customized_json_logger()


def main(rcaMsg: func.QueueMessage) -> None:
    try:
        payload = rcaMsg.get_json()
        clp_id = payload['clp_id']
        workbench_id = payload['workbench_id']
        rca_task_id = payload.get('rca_task_id') or payload.get('task_id')
        task_name = payload['task_name']
        target_guid = payload['target_guid']
        target_info = payload['target_info']
        trace_manager_task_id = payload.get('trace_manager_task_id')

        if trace_manager_task_id:
            trace_manager.task_id = trace_manager_task_id
        else:
            logger.info(f"No task id from msg, create new: {trace_manager.task_id}.")

        token = utils.find_token_by_clp(clp_id, API_TOKENS)
        if not token:
            raise GeneralException(f'Token not found for clp: {clp_id}')

        if utils.check_token_is_expired(token):
            logger.error(f"token is expired, clp: {clp_id}")
            return

        rca_task_detail = get_rca_task_detail(token, rca_task_id, target_guid)
        
        if not rca_task_detail:
            logger.error(f"No rca_task_detail for clp: {clp_id}")
            return
        
        target_info = {
            'xdrCustomerID': clp_id,
            'taskId': rca_task_id,
            'taskName': task_name,
            'agentEntity': target_info,
            'workbenchId': workbench_id
        }

        rca_task_result_log = transform_utils.transform_rca_result(target_info, rca_task_detail)

        if len(rca_task_result_log) > 0:
            log_type = configurations.get_rca_log_type()
            log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, log_type)
            log_analytics.post_data(
                rca_task_result_log
            )

        logger.info(
            f'Send rca data successfully. Task id: {rca_task_id}, Task name: {task_name},Target guid: {target_guid}'
        )
    except HTTPError as e:
        logger.exception(
            f'Fail to get rca detail!  Exception: {e}',
        )
        raise
    except:
        logger.exception('Internal error.')
        raise
