"""
Main Function
"""

import logging

# pylint: disable=logging-fstring-interpolation
import traceback
from json import dumps

import azure.functions as func

from vmray_api import VMRay


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function handles VMRay API and returns HTTP response
    :param req: func.HttpRequest
    """
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        sample_id = req.params.get("sample_id") or req.get_json().get("sample_id")
        if not sample_id:
            return func.HttpResponse(
                "Invalid Request. Missing 'sample_id' parameter.", status_code=400
            )
        logging.info(f"sample_id {sample_id}")
        vmray = VMRay(logging)
        vmray.check_id(sample_id)
        endpoint = f"/rest/sample/{sample_id}/vtis"
        response = vmray.request_vmray_api("GET", endpoint)
        return func.HttpResponse(
            dumps(response),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )
    except KeyError as ke:
        logging.error(f"Invalid Settings. {ke.args} configuration is missing.")
        return func.HttpResponse(
            "Invalid Settings. Configuration is missing.", status_code=500
        )
    except Exception as ex:
        error_detail = traceback.format_exc()
        logging.error(f"Exception Occurred: {str(ex)}, Traceback {error_detail}")
        return func.HttpResponse("Internal Server Exception", status_code=500)
