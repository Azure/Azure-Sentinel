"""
Main Function
"""
# pylint: disable=logging-fstring-interpolation

import logging

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
        submission_id = req.params.get("submission_id") or req.get_json().get(
            "submission_id"
        )
        if not submission_id:
            return func.HttpResponse(
                "Invalid Request. Missing 'submission_id' parameter.", status_code=400
            )
        logging.info(f"submission_id {submission_id}")
        vmray = VMRay(logging)
        vmray.check_id(submission_id)

        endpoint = f"/rest/submission/{submission_id}"
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
