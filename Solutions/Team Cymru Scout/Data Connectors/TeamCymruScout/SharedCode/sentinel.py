"""This file contains MicrosoftSentinel class which is used to post data into log analytics workspace."""

import base64
import datetime
import hashlib
import hmac
import inspect
import time
import requests
from .logger import applogger
from . import consts
from .teamcymruscout_exception import TeamCymruScoutException, SentinelIncorrectCredentialsException, InvalidDataFormatException
from urllib3.exceptions import NameResolutionError

customer_id = consts.WORKSPACE_ID
shared_key = consts.WORKSPACE_KEY
_RETRY_STATUS_CODES = {
    429: "Error occurred: Too many request. sleeping for {} seconds and retrying..".format(consts.INGESTION_ERROR_SLEEP_TIME),
    500: "Error occurred: Internal Server Error. sleeping for {} seconds and retrying..".format(consts.INGESTION_ERROR_SLEEP_TIME),
    503: "Error occurred: Service Unavailable. sleeping for {} seconds and retrying..".format(consts.INGESTION_ERROR_SLEEP_TIME),
}


class MicrosoftSentinel:
    """MicrosoftSentinel class is used to post data into log Analytics workspace."""

    def __init__(self) -> None:
        """Intialize instance variables for MicrosoftSentinel class."""
        self.logs_start_with = "{}(MicrosoftSentinel)".format(consts.LOGS_STARTS_WITH)

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
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
        return authorization

    def post_data(self, body, log_type):
        """Build and send a request to the POST API.

        Args:
            body (str): Data to post into Sentinel log analytics workspace
            log_type (str): Custom log table name in which data wil be added.

        Returns:
            status_code: Returns the response status code got while posting data to sentinel.

        Raises:
            SentinelIncorrectCredentialsException: When credentials are incorrect.
            InvalidDataFormatException: When data format is incorrect.
            TeamCymruScoutException: When custom exception is raised.
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
                "{}(method={}) : {} : Error occurred for build signature, Issue with Microsoft Sentinel Credentials".format(
                    self.logs_start_with,
                    __method_name,
                    err,
                )
            )
            raise SentinelIncorrectCredentialsException("Error while generating signature for posting data into log analytics.")
        uri = "https://" + consts.WORKSPACE_ID + ".ods.opinsights.azure.com" + resource + "?api-version=2016-04-01"

        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
        }
        retry_count = 0
        while retry_count < consts.SENTINEL_RETRY_COUNT:
            try:
                response = requests.post(uri, data=body, headers=headers, timeout=consts.MAX_TIMEOUT_SENTINEL)
                if response.status_code >= 200 and response.status_code <= 299:
                    applogger.debug(
                        "{}(method={}) : Status_code: {} Accepted: Data Posted Successfully"
                        " to Microsoft Sentinel.".format(
                            self.logs_start_with,
                            __method_name,
                            response.status_code,
                        )
                    )
                    return response.status_code
                elif response.status_code == 400:
                    applogger.error(
                        "{}(method={}) : Error occurred: Response code: {} "
                        "Bad Request while posting data to log analytics.\nError: {}".format(
                            self.logs_start_with, __method_name, response.status_code, response.content
                        )
                    )
                    raise InvalidDataFormatException()
                elif response.status_code == 403:
                    applogger.error(
                        "{}(method={}) : Error occurred for build signature: Issue with WorkspaceKey. "
                        "Kindly verify your WorkspaceKey.".format(
                            self.logs_start_with,
                            __method_name,
                        )
                    )
                    raise SentinelIncorrectCredentialsException()
                elif response.status_code in _RETRY_STATUS_CODES:
                    applogger.error(
                        "{}(method={}) : Response code : {} {}. ".format(
                            self.logs_start_with, __method_name, response.status_code, _RETRY_STATUS_CODES[response.status_code]
                        )
                    )
                    time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                    retry_count += 1
                    continue
                raise TeamCymruScoutException(
                    "Response code: {} from posting data to log analytics.\nError: {}".format(response.status_code, response.content)
                )
            except InvalidDataFormatException:
                raise InvalidDataFormatException()
            except SentinelIncorrectCredentialsException:
                applogger.error(
                    "{}(method={}) : Workspace Key is wrong, sleeping for {} seconds and retrying.".format(
                        self.logs_start_with,
                        __method_name,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                continue
            except requests.exceptions.ConnectionError as id_error:
                try:
                    if isinstance(id_error.args[0].reason, NameResolutionError):
                        applogger.error(
                            "{}(method={}) : Either Workspace ID is wrong or Sentinel Workspace is unreachable: {}"
                            ", Sleeping for {} seconds and retrying.".format(
                                self.logs_start_with,
                                __method_name,
                                id_error,
                                consts.INGESTION_ERROR_SLEEP_TIME,
                            )
                        )
                        time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                        retry_count += 1
                        continue
                except Exception as unknown_connect_error:
                    applogger.error(
                        "{}(method={}) : Unknown Error in ConnectionError, sleeping - {} seconds and retrying."
                        "Error - {}".format(
                            self.logs_start_with,
                            __method_name,
                            consts.INGESTION_ERROR_SLEEP_TIME,
                            unknown_connect_error,
                        )
                    )
                    time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                    retry_count += 1
                    continue
                applogger.error(
                    "{}(method={}) : Unknown Connection Error, sleeping - {} seconds and retrying."
                    "Error - {}".format(
                        self.logs_start_with,
                        __method_name,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                        id_error,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
            except requests.exceptions.Timeout as error:
                applogger.error("{}(method={}) : Timeout Error: {}".format(self.logs_start_with, __method_name, error))
                raise TeamCymruScoutException()
            except TeamCymruScoutException as custom_err:
                applogger.error(
                    "{}(method={}) : Error: {}, sleeping - {} seconds and retrying.".format(
                        self.logs_start_with,
                        __method_name,
                        custom_err,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
            except Exception as error:
                applogger.error(
                    "{}(method={}) : Unknown Error: {}, sleeping - {} seconds and retrying.".format(
                        self.logs_start_with,
                        __method_name,
                        error,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
        if retry_count == consts.SENTINEL_RETRY_COUNT:
            applogger.error(
                "{}(method={}) : Maximum Retry count of {} exceeded, hence stopping execution.".format(
                    self.logs_start_with,
                    __method_name,
                    consts.SENTINEL_RETRY_COUNT,
                )
            )
            raise TeamCymruScoutException()
        return None
