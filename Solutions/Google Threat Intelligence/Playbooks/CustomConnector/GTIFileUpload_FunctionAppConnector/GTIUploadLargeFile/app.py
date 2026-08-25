"""Main function."""

# pylint: disable=logging-fstring-interpolation

import logging
import traceback
from json import dumps

import azure.functions as func

from ..gti_uploader import GTIUploader


VALID_STORAGE_REGIONS = ("US", "CA", "EU", "GB")


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Download a blob and submit it to Google Threat Intelligence via the large-file upload flow.

    Shared by GTIFileScanEnrichment and GTIFileScanBlobEnrichment playbooks.
    :param req: func.HttpRequest
    """
    body = req.get_json()
    storage_account_name = body.get("storageAccountName")
    container_name = body.get("containerName")
    blob_path = body.get("blobPath")
    api_key = body.get("apiKey")
    disable_sandbox = body.get("disable_sandbox")
    password = body.get("password")
    storage_region = body.get("storage_region")

    missing = [
        name
        for name, value in (
            ("storageAccountName", storage_account_name),
            ("containerName", container_name),
            ("blobPath", blob_path),
            ("apiKey", api_key),
        )
        if not value
    ]
    if missing:
        return func.HttpResponse(
            dumps({"analysisId": None, "statusCode": 400, "error": f"Missing required parameter(s): {', '.join(missing)}"}),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )

    if storage_region and storage_region not in VALID_STORAGE_REGIONS:
        return func.HttpResponse(
            dumps({
                "analysisId": None,
                "statusCode": 400,
                "error": f"Invalid storage_region '{storage_region}'. Allowed values: {', '.join(VALID_STORAGE_REGIONS)}",
            }),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )

    try:
        gti_uploader = GTIUploader(logging)
        result = gti_uploader.upload(
            storage_account_name,
            container_name,
            blob_path,
            api_key,
            disable_sandbox=disable_sandbox,
            password=password,
            storage_region=storage_region,
        )
        return func.HttpResponse(
            dumps(result),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )
    except Exception as ex:
        error_detail = traceback.format_exc()
        logging.error(f"Exception Occurred: {str(ex)}, Traceback {error_detail}")
        return func.HttpResponse(
            dumps({"analysisId": None, "statusCode": 500, "error": str(ex)}),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )
