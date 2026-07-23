"""This __init__ file will be called once data is generated in webhook and it creates trigger."""

import inspect

from azure.functions import HttpRequest, HttpResponse
from azure.durable_functions import DurableOrchestrationClient
from SharedCode.consts import LOGS_STARTS_WITH
from SharedCode.logger import applogger
from SharedCode.extrahop_exceptions import ExtraHopException


def get_data_from_request_body(request):
    """Get data from request body.

    Args:
        request (func.HttpRequest): Azure function HttpRequest class object

    Raises:
        ExtraHopException: raises when an error occurs.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        data = request.get_json()
        return data
    except ValueError as value_error:
        applogger.error(
            "{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, value_error)
        )
        raise ExtraHopException(value_error)
    except Exception as err:
        applogger.error("{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, err))
        raise ExtraHopException(err)


async def main(req: HttpRequest, starter: str) -> HttpResponse:
    """
    Start the execution.

    Args:
        req (func.HttpRequest): To get data from request body pushed by webhook

    Returns:
        func.HttpResponse: Status of Http request process (successful/failed).
    """
    __method_name = inspect.currentframe().f_code.co_name
    applogger.debug("{}(method={}) HttpStarter Function Called.".format(LOGS_STARTS_WITH, __method_name))
    try:
        data = get_data_from_request_body(req)
        if data:
            client = DurableOrchestrationClient(starter)
            instance_id = await client.start_new(req.route_params["functionName"], client_input=data)
            applogger.debug(
                "{}(method={}) Started orchestration with ID = '{}'.".format(
                    LOGS_STARTS_WITH, __method_name, instance_id
                )
            )
            body = "Data Received successfully from ExtraHop webhook"
            applogger.info(
                "{}(method={}) {} and passed to orchestrator for processing.".format(
                    LOGS_STARTS_WITH, __method_name, body
                )
            )
            return HttpResponse(
                body=body,
                status_code=200,
                headers={"Content-Length": str(len(body))},
            )
        else:
            applogger.info(
                "{}(method={})No required data found.".format(
                    LOGS_STARTS_WITH, __method_name
                )
            )
            body = "No required data found."
            return HttpResponse(
                body=body,
                status_code=202,
                headers={"Content-Length": str(len(body))},
            )
    except ExtraHopException as err:
        applogger.error(
                "{}(method={}) {}.".format(
                    LOGS_STARTS_WITH, __method_name, err
                )
            )
        body = "Error: {}".format(err)
        return HttpResponse(
            body=body,
            status_code=400,
            headers={"Content-Length": str(len(body))},
        )
