"""Init file for Dossier Orchestrator Function."""

import json
import inspect
from azure.durable_functions import DurableOrchestrationContext, Orchestrator
from .create_dossier_job import DossierCreateJob
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.infoblox_exception import InfobloxException


def orchestrator_function(context: DurableOrchestrationContext):
    """Entry point of orchestrator function.

    Args:
        context: DurableOrchestrationContext object containing the orchestration context.

    Returns:
        A list of results from different functions.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        json_data = context.get_input()
        target_type = json_data.get("type")
        target = json_data.get("target")

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                "Type = {}, Target = {}".format(target_type, target),
            )
        )
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                "Calling Activity Function = InfobloxDossierRequiredSource",
            )
        )
        lookup_source_list = yield context.call_activity("InfobloxDossierRequiredSource", json.dumps(json_data))

        lookup_source_list = list(json.loads(lookup_source_list))
        result_source_list = (
            "Lookup source list = {}, Type = {}, Target = {}".format(str(lookup_source_list), target_type, target),
        )
        result1 = "No need dossier api call, data already available in the system"
        if len(lookup_source_list) != 0:
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                    "Creating Job and Checking Job Status",
                )
            )
            dossier_job_obj = DossierCreateJob(target_type, target)
            dossier_job_id = dossier_job_obj.get_dossier_job_id(lookup_source_list)
            status = dossier_job_obj.check_job_status(dossier_job_id)
            if status is True:
                applogger.info(
                    consts.LOG_FORMAT.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                        "Calling Activity Function = InfobloxDossierJobResult",
                    )
                )
                result1 = yield context.call_activity("InfobloxDossierJobResult", dossier_job_id)
                result1 += ", job_id = {}".format(dossier_job_id)
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                    "Orchestrator function completed successfully",
                )
            )
        return [result_source_list, result1]
    except TypeError as type_error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                "Type error : Error-{}".format(type_error),
            )
        )
        raise InfobloxException()
    except Exception as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_ORCHESTRATOR_FUNCTION_NAME,
                "Unexpected error : Error-{}".format(error),
            )
        )
        raise InfobloxException()


main = Orchestrator.create(orchestrator_function)
