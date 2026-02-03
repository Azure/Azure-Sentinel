"""
Main Function
"""

# pylint: disable=logging-fstring-interpolation

import base64
import logging
import traceback
from io import BytesIO
from json import dumps

import azure.functions as func

from ..joesandbox import JoeSandbox


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function handles JoeSandbox API and returns HTTP response
    :param req: func.HttpRequest
    """
    logging.info(f"Resource Requested: {func.HttpRequest}")
    file = req.params.get("file") or req.get_json().get("file")
    if not file:
        return func.HttpResponse(
            "Invalid Request. Missing 'file' parameter.", status_code=400
        )
    name = req.params.get("name") or req.get_json().get("name")
    doc_pass = req.params.get("document_password") or req.get_json().get(
        "document_password"
    )
    arch_pass = req.params.get("archive_password") or req.get_json().get(
        "archive_password"
    )
    tags = req.params.get("tags", []) or req.get_json().get("tags", [])
    try:
        joe_sandbox = JoeSandbox(logging)
        binary_data = base64.b64decode(file)
        file_object = BytesIO(binary_data)
        file_object.name = name
        params = {}
        if doc_pass:
            params["document-password"] = doc_pass
        if arch_pass:
            params["archive-password"] = arch_pass
        if tags:
            params["tags"] = tags
        response = joe_sandbox.submit_files_to_joesandbox(
            file=file_object, params=params
        )
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
