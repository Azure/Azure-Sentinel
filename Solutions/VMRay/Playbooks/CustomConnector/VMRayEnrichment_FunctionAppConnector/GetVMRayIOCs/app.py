# pylint: disable=logging-fstring-interpolation
import logging
import traceback
from json import dumps

import azure.functions as func

from vmray_api import VMRay

from .utils import IOC_LIST, IOC_MAPPING_FUNCTION, INDICATOR_LIST


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function handles VMRay API and returns HTTP response
    :param req: func.HttpRequest
    """
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        sample_id = req.params.get("sample_id") or req.get_json().get("sample_id")
        submission_id = req.params.get("submission_id") or req.get_json().get(
            "submission_id"
        )
        sample_verdict = req.params.get("sample_verdict") or req.get_json().get(
            "sample_verdict"
        )
        incident_id = req.params.get("incident_id") or req.get_json().get("incident_id")
        valid_until = req.params.get("valid_until") or req.get_json().get("valid_until")

        if not sample_id:
            return func.HttpResponse(
                "Invalid Request. Missing 'sample_id' parameter.", status_code=400
            )
        logging.info(f"sample_id: {sample_id}")
        vmray = VMRay(logging)
        vmray.check_id(sample_id)
        endpoint = f"/rest/sample/{sample_id}/iocs"
        response = vmray.request_vmray_api("GET", endpoint)

        if submission_id and sample_verdict:
            iocs_resp = response.get("iocs", {})
            for key, value in iocs_resp.items():
                if key in IOC_LIST:
                    IOC_MAPPING_FUNCTION[key](
                        value,
                        int(sample_id),
                        submission_id,
                        sample_verdict,
                        incident_id,
                        valid_until
                    )
            logging.info(f"length of indicator {len(INDICATOR_LIST)}")

            return func.HttpResponse(
                dumps({"api_resp": response, "custom_resp": INDICATOR_LIST}),
                headers={"Content-Type": "application/json"},
                status_code=200,
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

