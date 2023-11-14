import json
import requests
import logging
from msal import ConfidentialClientApplication

from ..Models.Error.errors import GraphAPIRequestError


class GraphApiCollector:
    def get_token(self, app_id, app_secret, tenant_id):
        try:
            app = ConfidentialClientApplication(
                app_id, authority="https://login.microsoftonline.com/" + tenant_id, client_credential=app_secret
            )
        except ConnectionError:
            logging.error("Failed to establish connection with GS API. Server is probably not available at the moment.")
            raise GraphAPIRequestError(
                "Failed to establish connection with GS API. Server is probably not available at the moment."
            )

        for i in range(4):
            result = app.acquire_token_silent(["https://graph.microsoft.com/.default"], account=None)
            if not result:
                result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            if result["access_token"]:
                break

        headers = {"Content-type": "application/json", "Authorization": "Bearer " + result["access_token"]}
        return headers

    def create_threat_indicators(self, headers, body):
        """
        Makes a POST request to create a TI indicator.
        :param headers: Header of the POST request.
        :param body: Body of the POST request.
        :returns: json response.
        :raises GraphAPIRequestError: raises an exception
        """
        ti_url = "https://graph.microsoft.com/beta/security/tiIndicators/submitTiIndicators"
        if body is None:
            logging.error("Request body cannot be empty.")
            raise GraphAPIRequestError("Request body cannot be empty.")

        try:
            response = requests.post(
                url=ti_url, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), headers=headers, stream=False
            )
        except ConnectionError:
            raise GraphAPIRequestError("Error on Graph API while creating new indicators.")

        if 200 <= response.status_code <= 299:
            logging.info(str(len(body["value"])) + " Threat Indicators sent successfully!")
        else:
            logging.error("Graph API Connector error occurred!")
            logging.error(response.content)
            raise GraphAPIRequestError("Error on Graph API while creating new indicators.")
