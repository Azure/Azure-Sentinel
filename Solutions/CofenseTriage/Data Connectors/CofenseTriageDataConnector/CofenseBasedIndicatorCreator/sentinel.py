"""This file contains methods for creating microsoft indicator and custom log table."""
import base64
import time
import requests
import json
import hashlib
import hmac
import inspect
import datetime
from ..SharedCode.consts import (
    AZURE_SUBSCRIPTION_ID,
    AZURE_RESOURCE_GROUP,
    AZURE_WORKSPACE_NAME,
    CREATE_SENTINEL_INDICATORS_URL,
    LOGS_STARTS_WITH,
    COFENSE_TO_SENTINEL,
    SENTINEL_429_SLEEP,
    WORKSPACE_KEY,
    WORKSPACE_ID,
)
from ..SharedCode.logger import applogger
from ..SharedCode.cofense_exception import CofenseException
from ..SharedCode.utils import (
    auth_sentinel,
    make_rest_call,
)


class MicrosoftSentinel:
    """This class contains methods to create indicator into Microsoft Sentinel."""

    def __init__(self):
        """Initialize instance variable for class."""
        self.bearer_token = auth_sentinel(COFENSE_TO_SENTINEL)

    def create_indicator(self, indicator_data):
        """To create indicator into Microsoft Sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            retry_count_429 = 0
            retry_count_401 = 0
            while retry_count_429 <= 3 and retry_count_401 <= 1:
                create_indicator_url = CREATE_SENTINEL_INDICATORS_URL.format(
                    subscriptionId=AZURE_SUBSCRIPTION_ID,
                    resourceGroupName=AZURE_RESOURCE_GROUP,
                    workspaceName=AZURE_WORKSPACE_NAME,
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(self.bearer_token),
                }
                response = make_rest_call(
                    url=create_indicator_url,
                    method="POST",
                    azure_function_name=COFENSE_TO_SENTINEL,
                    payload=json.dumps(indicator_data),
                    headers=headers,
                )
                if response.status_code >= 200 and response.status_code <= 299:
                    response_json = response.json()
                    applogger.debug(
                        "{}(method={}) : {} : Created the indicator into the sentinel with status code {}"
                        " and got the response {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                            response.status_code,
                            response_json,
                        )
                    )
                    return response_json
                elif response.status_code == 429:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 429.".format(
                            LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(SENTINEL_429_SLEEP)
                elif response.status_code == 401:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 401.".format(
                            LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                        )
                    )
                    self.bearer_token = auth_sentinel(COFENSE_TO_SENTINEL)
                    headers["Authorization"] = ("Bearer {}".format(self.bearer_token),)
                    retry_count_401 += 1
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {}: Error while creating microsoft"
                        " sentinel access_token. Error Reason: {}".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            COFENSE_TO_SENTINEL,
                            create_indicator_url,
                            response.status_code,
                            response.reason,
                        )
                    )
                    raise CofenseException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded for microsoft sentinel.".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL
                )
            )
            raise CofenseException()
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error generated while getting sentinel access token :{}".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL, error
                )
            )
            raise CofenseException()

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
        decoded_key = base64.b64decode(WORKSPACE_KEY)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = "SharedKey {}:{}".format(WORKSPACE_ID, encoded_hash)
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
        __method_name = inspect.currentframe().f_code.co_name
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
            applogger.error(
                "{}(method={}) : {} : Error occurred: {}".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL, err
                )
            )
            raise CofenseException(
                "Error while generating signature for posting data into log analytics."
            )
        uri = (
            "https://"
            + WORKSPACE_ID
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
                applogger.debug(
                    "{}(method={}) : {} : Status_code: {} Accepted: Data Posted Successfully to microsoft sentinel.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        COFENSE_TO_SENTINEL,
                        response.status_code,
                    )
                )
                return response.status_code
            else:
                raise CofenseException(
                    "Response code: {} from posting data to log analytics.\nError: {}".format(
                        response.status_code, response.content
                    )
                )
        except CofenseException as error:
            applogger.error(
                "{}(method={}) : {} : Error:{}".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL, error
                )
            )
            raise CofenseException(
                "CofenseException: Error while posting data to sentinel."
            )
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error:{}".format(
                    LOGS_STARTS_WITH, __method_name, COFENSE_TO_SENTINEL, error
                )
            )
            raise CofenseException("Exception: Error while posting data to sentinel.")
