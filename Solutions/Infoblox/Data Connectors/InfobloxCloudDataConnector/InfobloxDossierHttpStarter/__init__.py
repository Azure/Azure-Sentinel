"""Init file for http stater function."""

import logging
import inspect
from azure.functions import HttpRequest, HttpResponse
from azure.durable_functions import DurableOrchestrationClient
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.infoblox_exception import InfobloxException


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
    except TypeError as type_error:
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
        type_of_data, target = get_data_from_request_body(req)
        if not type_of_data or not target:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.DOSSIER_HTTP_STARTER_FUNCTION_NAME,
                    "No Type or Target found in request",
                )
            )
        else:
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
                req.route_params["functionName"],
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
