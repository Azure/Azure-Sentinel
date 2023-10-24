"""This __init__ file will be called once data is generated in webhook and it creates trigger."""
import inspect
import json
import azure.functions as func
import azure.durable_functions as df
from shared_code.consts import LOGS_STARTS_WITH
from shared_code.logger import applogger
from shared_code.rubrik_exception import RubrikException


def get_data_from_request_body(request):
    """Get data from request body.

    Args:
        request (func.HttpRequest): Azure function HttpRequest class object

    Raises:
        RubrikException: raises when an error occurs.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        data = request.get_json()
        json_data = json.dumps(data)
        return json_data
    except ValueError as value_error:
        applogger.error(
            "{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, value_error)
        )
        raise RubrikException(value_error)
    except Exception as err:
        applogger.error("{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, err))
        raise RubrikException(err)


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    Start the execution.

    Args:
        req (func.HttpRequest): To get data from request body pushed by webhook

    Returns:
        func.HttpResponse: Status of Http request process (successful/failed).
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.debug("{} HttpStarter Function Called.".format(LOGS_STARTS_WITH))
        data = get_data_from_request_body(req)
        if data:
            client = df.DurableOrchestrationClient(starter)
            instance_id = await client.start_new(
                req.route_params["functionName"], client_input=data
            )
            applogger.info(
                "{} Started orchestration with ID = '{}'.".format(
                    LOGS_STARTS_WITH, instance_id
                )
            )
            body = "Data Received successfully via Rubrik Webhook."
            return func.HttpResponse(
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
            return func.HttpResponse(
                body=body,
                status_code=202,
                headers={"Content-Length": str(len(body))},
            )
    except RubrikException as err:
        body = "Error: {}".format(err)
        return func.HttpResponse(
            body=body,
            status_code=400,
            headers={"Content-Length": str(len(body))},
        )
