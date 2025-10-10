"""
Main Function
"""

# pylint: disable=logging-fstring-interpolation

import logging
import traceback
from json import dumps

import azure.functions as func

from ..joesandbox import JoeSandbox


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function handles JoeSandbox API and returns HTTP response
    :param req: func.HttpRequest
    """
    logging.info(f"Resource Requested: {func.HttpRequest}")
    query = req.params.get("query") or req.get_json().get("query")
    if not query:
        return func.HttpResponse(
            "Invalid Request. Missing 'query' parameter.", status_code=400
        )
    try:
        joe_sandbox = JoeSandbox(logging)
        response = joe_sandbox.get_analysis(query)
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
