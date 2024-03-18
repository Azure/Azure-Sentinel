import logging
import json
import typing
import azure.functions as func

from requests.exceptions import HTTPError
from shared_code.services.workbench_service import get_rca_task, get_workbench_detail

from shared_code import utils, configurations, transform_utils
from shared_code.exceptions import GeneralException
from shared_code.data_collector import LogAnalytics

WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()
XDR_HOST_URL = configurations.get_xdr_host_url()
WB_LOG_TYPE = configurations.get_wb_log_type()
RCA_TASK_LOG_TYPE = configurations.get_rca_task_log_type()


workbench_column = [
    'priorityScore',
    'investigationStatus',
    'workbenchName',
    'workbenchId',
    'workbenchLink',
    'createdTime',
    'updatedTime',
    'severity',
]

workbench_detail_column = [
    'alertProvider',
    'model',
    'description',
    'impactScope',
    'indicators',
    'matchedRules',
    'alertTriggerTimestamp',
    'workbenchCompleteTimestamp',
]

xdr_indicators_column_name = {
    'ip': 'IPAddress',
    'detection_name': 'MalwareName',
    'filename': 'FileName',
    'fullpath': 'FileDirectory',
    'command_line': 'ProcessCommandLine',
    'domain': 'DomainName',
    'file_sha1': 'FileHashValue',
    'registry_key': 'RegistryKey',
    'registry_value_data': 'RegistryValue',
    'registry_value': 'RegistryValueName',
    'url': 'URL',
    'emailAddress': 'MailboxPrimaryAddress',
}


def update_json_data(json_data, filed, value):
    if not filed in json_data:
        json_data[filed] = []

    if value and not value in json_data[filed]:
        json_data[filed].append(value)


def process_impact_scope(json_data):
    for impact_scope in json_data['impactScope']:
        entity_type = impact_scope['entityType']

        if entity_type == 'account':
            account_value = impact_scope['entityValue'].split("\\")

            if len(account_value) == 2:
                account = account_value[1]
                update_json_data(json_data, 'UserAccountNTDomain', account_value[0])
            else:
                account = account_value[0]

            update_json_data(json_data, 'UserAccountName', account)
        elif entity_type == 'host':
            update_json_data(
                json_data, 'HostHostName', impact_scope['entityValue']['name']
            )

    return json_data


def process_indicators(json_data):
    for indicator in json_data['indicators']:
        object_type = indicator['objectType']

        if object_type in xdr_indicators_column_name.keys():
            update_json_data(
                json_data,
                xdr_indicators_column_name[object_type],
                indicator['objectValue'],
            )

    return json_data


def customize_json(clp_id, workbench_detail, workbench_record):

    xdr_log = {}

    for column in workbench_column:
        xdr_log[column] = workbench_record[column] if column in workbench_record else ""

    for column in workbench_detail_column:
        xdr_log[column] = workbench_detail[column] if column in workbench_detail else ""

    xdr_log['xdrCustomerID'] = clp_id
    xdr_log['impactScope_Summary'] = json.dumps(workbench_record['impactScope'])
    xdr_log = process_impact_scope(xdr_log)
    xdr_log = process_indicators(xdr_log)

    return xdr_log


def build_queue_message(
    clp_id, workbench_id, task_id, task_name, target_guid, target_info
):
    return json.dumps(
        {
            'clp_id': clp_id,
            'workbench_id': workbench_id,
            'task_id': task_id,
            'task_name': task_name,
            'target_guid': target_guid,
            'target_info': target_info,
        }
    )


def main(wbMsg: func.QueueMessage, rcaMsg: func.Out[typing.List[str]]) -> None:
    try:
        payload = wbMsg.get_json()

        clp_id = payload['clp_id']
        workbench_record = payload['workbench_record']
        workbench_id = workbench_record['workbenchId']

        token = utils.find_token_by_clp(clp_id, API_TOKENS)

        if not token:
            raise GeneralException(f'Token not found for clp: {clp_id}')

        if utils.check_token_is_expired(token):
            logging.error(f"token is expired, clp: {clp_id}")
            return

        # get workbench detail
        workbench_detail = get_workbench_detail(token, workbench_id)

        if not workbench_detail:
            logging.warning(
                f'Could not get workbench data. Workbench id: {workbench_id}.'
            )
            return

        # transform data
        customized_workbench_json = customize_json(
            clp_id, workbench_detail, workbench_record
        )

        # send to log analytics
        log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, WB_LOG_TYPE)
        log_analytics.post_data(customized_workbench_json)
        logging.info(f'Send workbench data successfully. Workbench id: {workbench_id}.')

        rca_tasks = []
        rac_task_log = []

        # get rca task
        rca_raw_tasks = get_rca_task(
            token,
            workbench_id,
        )

        for task in rca_raw_tasks:
            task_status = task['status']
            if task_status != 'PROCESS_COMPLETE':
                logging.warning(
                    f'Get rca task with status: {task_status}, Workbench id: {workbench_id}. No need to get rca detail.'
                )
                continue

            # process prca task info
            rac_task_log.append(
                transform_utils.transform_rca_task(clp_id, workbench_id, task)
            )

            for target in task['targets']:
                target_status = target['targetStatus']

                if target_status != 'PROCESS_COMPLETE':
                    logging.warning(
                        f'Get rca target with status: {target_status}, Workbench id: {workbench_id}. No need to get rca detail.'
                    )
                    continue
                target_info = target.copy()
                target_info.pop('targetStatus')

                rca_tasks.append(
                    build_queue_message(
                        clp_id,
                        workbench_id,
                        task['id'],
                        task['name'],
                        target['guid'],
                        target_info,
                    )
                )

        if len(rac_task_log) > 0:
            log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, RCA_TASK_LOG_TYPE)
            log_analytics.post_data(rac_task_log)
            logging.info(
                f'Send prca task data successfully. Workbench id: {workbench_id}, Count: {len(rac_task_log)}.'
            )

        if rca_tasks:
            rcaMsg.set(rca_tasks)

    except HTTPError as e:
        logging.exception(
            f'Fail to get workbench detail! Exception: {e}',
        )
        raise
    except:
        logging.exception('Internal error.')
        raise
