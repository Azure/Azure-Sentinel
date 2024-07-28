import json
import typing
import azure.functions as func

from requests.exceptions import HTTPError
from shared_code.services.workbench_service import get_rca_task, get_workbench_detail

from shared_code import utils, configurations, transform_utils
from shared_code.exceptions import GeneralException
from shared_code.data_collector import LogAnalytics
from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.trace_utils.trace import trace_manager


WORKSPACE_ID = configurations.get_workspace_id()
WORKSPACE_KEY = configurations.get_workspace_key()
API_TOKENS = configurations.get_api_tokens()
XDR_HOST_URL = configurations.get_xdr_host_url()
WB_LOG_TYPE = configurations.get_wb_log_type()
RCA_TASK_LOG_TYPE = configurations.get_rca_task_log_type()

logger = get_customized_json_logger()


def build_queue_message(
    clp_id, workbench_id, rca_task_id, task_name, target_guid, target_info
):
    return json.dumps(
        {
            "clp_id": clp_id,
            "workbench_id": workbench_id,
            "trace_manager_task_id": trace_manager.task_id,
            "rca_task_id": rca_task_id,
            "task_name": task_name,
            "target_guid": target_guid,
            "target_info": target_info,
        }
    )


def main(wbMsg: func.QueueMessage, rcaMsg: func.Out[typing.List[str]]) -> None:
    try:
        payload = wbMsg.get_json()

        clp_id = payload["clp_id"]
        workbench_record = payload["workbench_record"]
        workbench_id = workbench_record["workbenchId"]
        task_id = workbench_record.get("task_id")
        if task_id:
            trace_manager.task_id = task_id
        else:
            logger.info(f"No task id from msg, create new: {trace_manager.task_id}.")

        token = utils.find_token_by_clp(clp_id, API_TOKENS)

        if not token:
            raise GeneralException(f"Token not found for clp: {clp_id}")

        if utils.check_token_is_expired(token):
            logger.error(f"token is expired, clp: {clp_id}")
            return

        # get workbench detail
        workbench_detail = get_workbench_detail(token, workbench_id)

        if not workbench_detail:
            logger.warning(
                f"Could not get workbench data. Workbench id: {workbench_id}."
            )
            return

        # transform data
        customized_workbench_json = transform_utils.customize_workbench_json(
            clp_id, workbench_detail, workbench_record
        )

        # send to log analytics
        log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, WB_LOG_TYPE)
        log_analytics.post_data(customized_workbench_json)
        logger.info(f"Send workbench data successfully. Workbench id: {workbench_id}.")

        rca_tasks = []
        rac_task_log = []

        # get rca task
        rca_raw_tasks = get_rca_task(
            token,
            workbench_id,
        )

        for task in rca_raw_tasks:
            task_status = task["status"]
            if task_status != "PROCESS_COMPLETE":
                logger.warning(
                    f"Get rca task with status: {task_status}, Workbench id: {workbench_id}. No need to get rca detail."
                )
                continue

            # process prca task info
            rac_task_log.append(
                transform_utils.transform_rca_task(clp_id, workbench_id, task)
            )

            for target in task["targets"]:
                target_status = target["targetStatus"]

                if target_status != "PROCESS_COMPLETE":
                    logger.warning(
                        f"Get rca target with status: {target_status}, Workbench id: {workbench_id}. No need to get rca detail."
                    )
                    continue
                target_info = target.copy()
                target_info.pop("targetStatus")

                rca_tasks.append(
                    build_queue_message(
                        clp_id,
                        workbench_id,
                        task["id"],
                        task["name"],
                        target["guid"],
                        target_info,
                    )
                )

        if len(rac_task_log) > 0:
            log_analytics = LogAnalytics(WORKSPACE_ID, WORKSPACE_KEY, RCA_TASK_LOG_TYPE)
            log_analytics.post_data(rac_task_log)
            logger.info(
                f"Send prca task data successfully. Workbench id: {workbench_id}, Count: {len(rac_task_log)}."
            )

        if rca_tasks:
            rcaMsg.set(rca_tasks)

    except HTTPError as e:
        logger.exception(
            f"Fail to get workbench detail! Exception: {e}",
        )
        raise
    except:
        logger.exception("Internal error.")
        raise
