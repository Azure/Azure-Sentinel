"""
Main Function
"""

# pylint: disable=logging-fstring-interpolation
# pylint: disable=invalid-name

import logging
from traceback import format_exc
from json import dumps, loads

import azure.functions as func

from ..joesandbox import JoeSandbox


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function handles JoeSandbox API and returns HTTP response
    :param req: func.HttpRequest
    """
    logging.info(f"Resource Requested: {func.HttpRequest}")
    web_id = req.params.get("web_id") or req.get_json().get("web_id")
    if not web_id:
        return func.HttpResponse(
            "Invalid Request. Missing 'analysis_id' parameter.", status_code=400
        )
    download_type = (
            req.params.get("type") or req.get_json().get("type") or "irjsonfixed"
    )
    try:
        joe_sandbox = JoeSandbox(logging)
        filename, file_data = joe_sandbox.download_analysis(web_id, download_type)
        return func.HttpResponse(
            dumps({"file_name": filename, "data": loads(file_data)}),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )

    except KeyError as ke:
        logging.error(f"Invalid Settings. {ke.args} configuration is missing.")
        return func.HttpResponse(
            "Invalid Settings. Configuration is missing.", status_code=500
        )
    except Exception as ex:
        error_detail = format_exc()
        logging.error(f"Exception Occurred: {str(ex)}, Traceback {error_detail}")
        return func.HttpResponse("Internal Server Exception", status_code=500)
