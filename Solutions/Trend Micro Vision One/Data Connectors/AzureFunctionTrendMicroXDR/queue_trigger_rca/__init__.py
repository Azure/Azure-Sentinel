import logging
import requests
import json
import urllib
import azure.functions as func

from requests.exceptions import HTTPError
from shared_code.services.workbench_service import get_rca_task_detail

from shared_code import utils, configurations, utils, transform_utils
from shared_code.exceptions import GeneralException
from shared_code.data_collector import LogAnalytics

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()



def main(rcaMsg: func.QueueMessage) -> None:
    try:
        payload = rcaMsg.get_json()
        clp_id = payload['clp_id']
        workbench_id = payload['workbench_id']
        task_id = payload['task_id']
        task_name = payload['task_name']
        target_guid = payload['target_guid']
        target_info = payload['target_info']

        token = utils.find_token_by_clp(clp_id, API_TOKENS)
        if not token:
            raise GeneralException(f'Token not found for clp: {clp_id}')

        rca_task_detail = get_rca_task_detail(token, task_id, target_guid)
        
        
        target_info = {
            'xdrCustomerID': clp_id,
            'taskId': task_id,
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

        logging.info(
            f'Send rca data successfully. Task id: {task_id}, Task name: {task_name},Target guid: {target_guid}'
        )
    except HTTPError as e:
        logging.exception(
            f'Fail to get rca detail!  Exception: {e}',
        )
        raise
    except:
        logging.exception('Internal error.')
        raise
