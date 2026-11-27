"""Init file for http stater function."""

import logging
import inspect
from azure.functions import HttpRequest, HttpResponse
from azure.durable_functions import DurableOrchestrationClient
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.infoblox_exception import InfobloxException
from ..SharedCode.input_validation import validate_type_and_target

ALLOWED_ORCHESTRATOR = "InfobloxDossierOrchestrator"

def get_data_from_request_body(req: HttpRequest):
    """Extract type_of_data and target in a function.

    Args:
        req (HttpRequest): The HTTP request object.

    Returns:
        tuple: A tuple containing the extracted type_of_data and target.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        type_of_data = req.params.get("type").strip()
        target = req.params.get("target").strip()
        return type_of_data, target
    except (TypeError, AttributeError) as type_error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_HTTP_STARTER_FUNCTION_NAME,
                "Type error : Error-{}".format(type_error),
            )
        )
        raise InfobloxException()


async def main(req: HttpRequest, starter: str) -> HttpResponse:
    """Async function that serves as the main entry point for handling HTTP requests.

    Args:
        req (HttpRequest): The incoming HTTP request object.
        starter (str): The identifier for the DurableOrchestrationClient.

    Returns:
        HttpResponse: The response generated based on the request processing.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        function_name = req.route_params.get("functionName")
        if function_name != ALLOWED_ORCHESTRATOR:
            return HttpResponse("Unknown orchestrator.", status_code=404)
        type_of_data, target = get_data_from_request_body(req)
        if not validate_type_and_target(type_of_data, target):
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOSSIER_HTTP_STARTER_FUNCTION_NAME,
                    "Invalid or missing Type or Target in request",
                )
            )
            return HttpResponse("Invalid or missing 'type' or 'target' parameter.", status_code=400)
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_HTTP_STARTER_FUNCTION_NAME,
                "Got params from request. Type = {}, Target = {}".format(type_of_data, target),
            )
        )
        client = DurableOrchestrationClient(starter)
        instance_id = await client.start_new(
            function_name,
            None,
            {"type": type_of_data, "target": target},
        )
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)
    except InfobloxException:
        raise InfobloxException()
    except Exception as error:
        applogger.error(
            consts.LOG_FORMAT.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.DOSSIER_HTTP_STARTER_FUNCTION_NAME,
                "Unexpected error : Error-{}".format(error),
            )
        )
        raise InfobloxException()
