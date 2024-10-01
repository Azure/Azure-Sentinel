"""This file contains TeamCymruScout class for interacting with TeamCymruScout APIs and posting data to Sentinel."""

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
    retry_any,
)
import inspect
import json
from requests.auth import HTTPBasicAuth
from .logger import applogger
from .teamcymruscout_exception import TeamCymruScoutException
from .sentinel import MicrosoftSentinel
from . import consts

def raise_error(retry_state):
    """raise error when number of retries exceeded

    Args:
        retry_state (obj): Retry state object

    Raises:
        TeamCymruScoutException: raise error when number of retries exceeded
    """
    applogger.error(
        "{} Maximum retries exceeded. Hence stopping the execution.".format(consts.LOGS_STARTS_WITH)
    )
    raise TeamCymruScoutException()

def retry_on_status_code(status_code):
    """Check and retry based on a list of status codes.

    Args:
        response(): API response is passed

    Returns:
        Bool: if given status code is in list then true else false
    """
    __method_name = inspect.currentframe().f_code.co_name
    if status_code in consts.RETRY_STATUS_CODES:
        applogger.info(
            "{}(method={}) Retrying due to status code : {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                status_code,
            )
        )
        return True
    return False

class TeamCymruScout:
    """Class for interacting with TeamCymruScout APIs and posting data to Sentinel."""

    def __init__(self) -> None:
        """Initialize the insatnce object of TeamCymruScout."""
        self.base_url = consts.CYMRU_SCOUT_BASE_URL
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self.auth = None
        self.ms_sentinel_obj = MicrosoftSentinel()
        self.error_logs = "{}(method={}) {}"
        self.logs_starts_with = consts.LOGS_STARTS_WITH
        self.set_authorization_header()

    def set_authorization_header(self):
        """Set the authorization header based on the authentication type."""
        if consts.AUTHENTICATION_TYPE == "API Key":
            applogger.debug("{} API Key based authentication is selected.".format(self.logs_starts_with))
            self.session.headers["Authorization"] = "Token: {}".format(consts.API_KEY)
        else:
            self.auth = HTTPBasicAuth(username=consts.USERNAME, password=consts.PASSWORD)
            applogger.debug("{} Username and password based authentication is selected.".format(self.logs_starts_with))

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=5, max=60),
        retry=retry_any(
            retry_if_result(retry_on_status_code),
            retry_if_exception_type(ConnectionError),
            retry_if_exception_type(requests.exceptions.Timeout),
        ),
        after=lambda x: applogger.error("TeamCymruScout: Retry Attempt: {}".format(x.attempt_number)),
        retry_error_callback=raise_error,
    )
    def make_rest_call(self, endpoint, params=None, body=None):
        """To call Team Cymru Scout API.

        Args:
            endpoint (str): endpoint to call.
            params (json, optional): query parameters to pass in API call. Defaults to None.
            body (json, optional): Request body to pass in API call. Defaults to None.

        Returns:
            json: returns json response if API call succeed.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "{}(method={}) Calling Team Cymru Scout API for endpoint={} with params={}".format(
                    self.logs_starts_with, __method_name, endpoint, params
                )
            )
            error_messages = {
                400: "Bad Request.",
                401: "Authentication error. Please verify the provided credentials.",
                403: "Authorization error.",
                404: "Not Found.",
                429: "Team Cymru Scout API Limit Exceeded.",
                500: "Internal Server Error.",
                503: "Service Unavailable.",
            }
            request_url = "{}{}".format(self.base_url, endpoint)
            response = self.session.get(url=request_url, params=params, data=body, auth=self.auth, timeout=consts.MAX_TIMEOUT_SENTINEL)
            if response.status_code == 200:
                applogger.info("{}(method={}) API Call Successful.".format(self.logs_starts_with, __method_name))
                if response.headers.get("Content-Type") == "application/json":
                    response_json = response.json()
                    return response_json
                applogger.error(
                    "{}(method={}) Response is not in JSON format. {}".format(self.logs_starts_with, __method_name, response.text)
                )
            elif response.status_code in error_messages:
                applogger.error(
                    "{}(method={}) {} {}".format(
                        self.logs_starts_with, __method_name, error_messages.get(response.status_code), response.text
                    )
                )
                if response.status_code in consts.RETRY_STATUS_CODES:
                    return response.status_code
            else:
                applogger.error(
                    "{}(method={}) Error while fetching data from url={}. Status code: {}, Error: {}".format(
                        self.logs_starts_with,
                        __method_name,
                        request_url,
                        response.status_code,
                        response.text,
                    )
                )
            raise TeamCymruScoutException()
        except requests.exceptions.Timeout as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.TIME_OUT_ERROR_MSG.format(error),
                )
            )
            raise requests.exceptions.Timeout()
        except json.decoder.JSONDecodeError as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.JSON_DECODE_ERROR_MSG.format(error),
                )
            )
            raise TeamCymruScoutException()
        except requests.ConnectionError as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.CONNECTION_ERROR_MSG.format(error),
                )
            )
            raise ConnectionError()
        except requests.HTTPError as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.HTTP_ERROR_MSG.format(error),
                )
            )
            raise TeamCymruScoutException()
        except requests.RequestException as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.REQUEST_ERROR_MSG.format(error),
                )
            )
            raise TeamCymruScoutException()
        except Exception as error:
            applogger.error(
                self.error_logs.format(
                    self.logs_starts_with,
                    __method_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise TeamCymruScoutException()

    def send_data_to_sentinel(self, data, table_name, indicator_value="Account Usage"):
        """
        To send the given data to the specified table in the Microsoft Sentinel.

        Args:
            data (Any): The data to be sent to the table.
            table_name (str): The name of the table in Microsoft Sentinel.
        """
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug("{}(method={}) Sending data to Sentinel.".format(self.logs_starts_with, __method_name))
        body = json.dumps(data)
        self.ms_sentinel_obj.post_data(body, table_name)
        count = len(data) if isinstance(data, list) else 1
        applogger.info(
            "{}(method={}) Posted {} records into {} of Log Analytics Workspace for {}.".format(
                self.logs_starts_with, __method_name, count, table_name, indicator_value
            )
        )
