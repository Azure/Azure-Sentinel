import azure.functions as func
import logging
import json
import requests
from base64 import b64encode
from ..CommonCode.constants import (
    ONPREM_API_KEY,
    ONPREM_API_SECRET,
    ONPREM_PCE_FQDN,
    ONPREM_PCE_PORT,
)

URL = "https://{}:{}/api/v2/health".format(ONPREM_PCE_FQDN, ONPREM_PCE_PORT)

credentials = b64encode(f"{ONPREM_API_KEY}:{ONPREM_API_SECRET}".encode()).decode(
    "utf-8"
)
headers = {"Authorization": f"Basic {credentials}", "Content-type": "application/json"}


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Making an api call to onprem PCE to get health metadata")
    response = requests.request("GET", URL, headers=headers, data={})

    if response:
        logging.info("[OnPremHealth] Response from url is {}".format(response.headers))
    else:
        logging.info("[OnPremHealth] Error in response {}".format(response))
        return

    parsed_response = json.loads(response.text)
    # if this has a notifications, just remove it.
    if "notifications" in parsed_response[0].keys():
        del parsed_response[0]["notifications"]

    sanitized_response = json.dumps(parsed_response)

    return func.HttpResponse(
        sanitized_response,
        status_code=response.status_code,
        mimetype="application/json",
    )
