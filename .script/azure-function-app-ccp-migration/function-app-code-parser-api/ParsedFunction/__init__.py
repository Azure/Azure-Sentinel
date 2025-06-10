import json
import logging
from http import HTTPStatus

import azure.functions as func
from .azure_function_code_parser import parse_code


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered Azure Function that exposes `parse_code` via POST.
    """
    logging.info("ParserFunction triggered")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON body",
            status_code=HTTPStatus.BAD_REQUEST,
        )

    try:
        result = parse_code(req_body)
        return func.HttpResponse(
            body=json.dumps(result),
            status_code=HTTPStatus.OK,
            mimetype="application/json",
        )
    except Exception as exc:
        logging.exception("ParserFunction failed")
        return func.HttpResponse(
            body=json.dumps({"success": False, "error": str(exc)}),
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json",
        )