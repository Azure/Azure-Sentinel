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
        hash_value = req.params.get("hash") or req.get_json().get("hash")
        if not hash_value:
            return func.HttpResponse(
                "Invalid Request. Missing 'hash' parameter.", status_code=400
            )
        logging.info(f"hash {hash}")
        hash_type_lookup = {32: "md5", 40: "sha1", 64: "sha256"}
        hash_type = hash_type_lookup.get(len(hash_value))
        if hash_type is None:
            error_string = " or ".join(
                f"{len_} ({type_})" for len_, type_ in hash_type_lookup.items()
            )
            raise ValueError(
                f"Invalid hash provided, must be of length {error_string}. "
                f"Provided hash had a length of {len(hash_value)}."
            )
        endpoint = f"/rest/sample/{hash_type}/{hash_value}"
        vmray = VMRay(logging)
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
