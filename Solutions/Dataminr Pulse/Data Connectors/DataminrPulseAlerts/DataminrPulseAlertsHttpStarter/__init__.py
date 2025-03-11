"""This __init__ file will be called once data is generated in webhook and it creates trigger."""
import inspect
import azure.functions as func
import azure.durable_functions as df
from shared_code.logger import applogger
from shared_code.dataminrpulse_exception import DataminrPulseException
from shared_code.consts import LOGS_STARTS_WITH


def get_data_from_request_body(request):
    """Get data from request body.

    Args:
        request (func.HttpRequest): Azure function HttpRequest class object

    Raises:
        DataminrPulseException: raises when an error occurs.
    """
    __method_name = inspect.currentframe().f_code.co_name
    try:
        data = request.get_json()
        return data
    except ValueError as value_error:
        applogger.error(
            "{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, value_error)
        )
        raise DataminrPulseException(value_error)
    except Exception as err:
        applogger.error("{}(method={}) {}".format(LOGS_STARTS_WITH, __method_name, err))
        raise DataminrPulseException(err)


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
            if type(data) == dict:
                keys_list = [key.lower() for key in list(data)]
                if "integration-settings" in keys_list:
                    instance_id = await client.start_new(
                        req.route_params["functionName"],
                        client_input={
                            "data": data,
                            "activity": "DataminrPulseAlertsManualActivity",
                        },
                    )
                    response = await client.wait_for_completion_or_create_check_status_response(
                        req, instance_id=instance_id, timeout_in_milliseconds=1000000
                    )
                    response_body = response.get_body().decode()
                    if "Error" in response_body:
                        return func.HttpResponse(
                            body=response_body,
                            status_code=400,
                            headers={"Content-Length": str(len(response_body))},
                        )
                    else:
                        response_body = "Integration settings are added successfully with settingId={}".format(
                            response_body
                        )
                        return func.HttpResponse(
                            body=response_body,
                            status_code=200,
                            headers={"Content-Length": str(len(response_body))},
                        )
                else:
                    instance_id = await client.start_new(
                        req.route_params["functionName"],
                        client_input={
                            "data": data,
                            "activity": "DataminrPulseAlertsSentinelActivity",
                        },
                    )
                    applogger.info(f"Started orchestration with ID = '{instance_id}'.")
                    body = "Data Received successfully via Dataminr RTAP."
                    return func.HttpResponse(
                        body=body,
                        status_code=200,
                        headers={"Content-Length": str(len(body))},
                    )
            else:
                instance_id = await client.start_new(
                    req.route_params["functionName"],
                    client_input={
                        "data": data,
                        "activity": "DataminrPulseAlertsSentinelActivity",
                    },
                )
                applogger.info(f"Started orchestration with ID = '{instance_id}'.")
                body = "Data Received successfully via Dataminr RTAP."
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

    except DataminrPulseException as err:
        body = "Error: {}".format(err)
        return func.HttpResponse(
            body=body,
            status_code=400,
            headers={"Content-Length": str(len(body))},
        )
