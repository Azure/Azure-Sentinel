"""This file contains AzureSentinel class which is used to post data into log analytics workspace."""
import base64
import datetime
import hashlib
import hmac
import requests
from ..shared_code.consts import LOGS_STARTS_WITH, WORKSPACE_ID, WORKSPACE_KEY
from ..shared_code.logger import applogger
from ..shared_code.rubrik_exception import RubrikException


class MicrosoftSentinel:
    """AzureSentinel class is used to post data into log Analytics workspace."""

    def __init__(self) -> None:
        """Intialize instance variables for MicrosoftSentinel class."""
        self.logs_start_with = "{}(MicrosoftSentinel)".format(LOGS_STARTS_WITH)
        self.customer_id = WORKSPACE_ID
        self.shared_key = WORKSPACE_KEY

    def build_signature(
        self,
        date,
        content_length,
        method,
        content_type,
        resource,
    ):
        """To build signature which is required in header."""
        x_headers = "x-ms-date:" + date
        string_to_hash = (
            method
            + "\n"
            + str(content_length)
            + "\n"
            + content_type
            + "\n"
            + x_headers
            + "\n"
            + resource
        )
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(self.customer_id, encoded_hash)
        return authorization

    # Build and send a request to the POST API
    def post_data(self, body, log_type):
        """Build and send a request to the POST API.

        Args:
            body (str): Data to post into Sentinel log analytics workspace
            log_type (str): Custom log table name in which data wil be added.

        Returns:
            status_code: Returns the response status code got while posting data to sentinel.
        """
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        content_length = len(body)
        try:
            signature = self.build_signature(
                rfc1123date,
                content_length,
                method,
                content_type,
                resource,
            )
        except Exception as err:
            applogger.error("{} Error occurred: {}".format(self.logs_start_with, err))
            raise RubrikException(
                "Error while generating signature for posting data into log analytics."
            )
        uri = (
            "https://"
            + self.customer_id
            + ".ods.opinsights.azure.com"
            + resource
            + "?api-version=2016-04-01"
        )

        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
        }
        try:
            response = requests.post(uri, data=body, headers=headers)
            if response.status_code >= 200 and response.status_code <= 299:
                applogger.info(
                    "{} Data posted successfully to {} table in Log Analytics Workspace.".format(
                        self.logs_start_with, log_type
                    )
                )
            else:
                applogger.info(
                    "Response code: {} from posting data to log analytics.\nError: {}".format(
                        response.status_code, response.content
                    )
                )
                raise RubrikException(
                    "Response code: {} from posting data to log analytics.\nError: {}".format(
                        response.status_code, response.content
                    )
                )
        except RubrikException as error:
            applogger.error("{} Error:{}".format(self.logs_start_with, error))
            raise RubrikException(
                "RubrikException: Error while posting data to sentinel."
            )
        except Exception as error:
            applogger.error("{} Error:{}".format(self.logs_start_with, error))
            raise RubrikException()
