"""Utility module."""

import inspect
import logging
from Exceptions.ArmisExceptions import ArmisException
import requests
from . import consts
from .state_manager import StateManager


class Utils:
    """Utils Class."""

    def __init__(self) -> None:
        """Init Function."""
        self.retry_count = 0
        self.header = {}
        self.check_environment_var_exist(
            [
                {"ArmisURL": consts.URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"ArmisSecretKey": consts.API_KEY},
                {"AzureWebJobsStorage": consts.CONNECTION_STRING},
                {"ArmisAlertsTableName": consts.ARMIS_ALERTS_TABLE},
                {"ArmisActivitiesTableName": consts.ARMIS_ACTIVITIES_TABLE},
            ]
        )
        self._secret_key = consts.API_KEY
        self.get_access_token()
        self.state_manager_obj = StateManager(
            connection_string=consts.CONNECTION_STRING, file_path=consts.CHECKPOINT_FILE_TIME
        )

    def check_environment_var_exist(self, environment_var):
        """Check the existence of required environment variables.

        Args:
            environment_var(list) : variables to check for existence
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            logging.info(consts.LOG_FORMAT.format(__method_name, "Validating Environment Variables."))
            missing_required_field = False
            for var in environment_var:
                key, val = next(iter(var.items()))
                if not val:
                    missing_required_field = True
                    logging.error(
                        consts.LOG_FORMAT.format(__method_name, "Environment variable {} is not set.".format(key))
                    )
            if missing_required_field:
                logging.error(consts.LOG_FORMAT.format(__method_name, "Environment Variables validation failed."))
                raise ArmisException()
            logging.info(consts.LOG_FORMAT.format(__method_name, "Environment Variables validation Success."))
        except ArmisException:
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(__method_name, "Error while checking environment variables: {}".format(err))
            )
            raise ArmisException()

    def make_rest_call(self, method, url, params=None, headers=None, data=None, retry_401=0):
        """Make a rest call.

        Args:
            url (str): The URL to make the call to.
            method (str): The HTTP method to use for the call.
            params (dict, optional): The parameters to pass in the call (default is None).
            headers (dict, optional): The headers to pass in the call (default is None).
            data (dict, optional): The body of the request (default is None).
            retry_401(int): Number of retry in 401(default is 0).

        Returns:
            dict: The JSON response if the call is successful.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            for _ in range(retry_401 + 1):
                response = requests.request(
                    method, url, headers=self.header, params=params, data=data, timeout=consts.REQUEST_TIMEOUT
                )
                if response.status_code == 200:
                    response_json = response.json()
                    logging.info(
                        consts.LOG_FORMAT.format(
                            __method_name, "Success, Status code : {}.".format(response.status_code)
                        )
                    )
                    return response_json
                elif response.status_code == 400:
                    logging.error(
                        consts.LOG_FORMAT.format(
                            __method_name,
                            "Bad Request = {}, Status code : {}.".format(response.text, response.status_code),
                        )
                    )
                    raise ArmisException()
                elif response.status_code == 401:
                    logging.error(
                        consts.LOG_FORMAT.format(
                            __method_name, "Unauthorized, Status code : {}, Retrying...".format(response.status_code)
                        )
                    )
                    self.get_access_token()
                    self.retry_count += 1
                    continue
                elif response.status_code == 429:
                    logging.error(
                        consts.LOG_FORMAT.format(
                            __method_name,
                            "Too Many Requests, Status code : {}.".format(response.status_code),
                        )
                    )
                    raise ArmisException()
                elif response.status_code == 500:
                    logging.error(
                        consts.LOG_FORMAT.format(
                            __method_name,
                            "Internal Server Error, Status code : {}.".format(response.status_code),
                        )
                    )
                    raise ArmisException()
                elif response.status_code == 502:
                    logging.error(
                        consts.LOG_FORMAT.format(
                            __method_name,
                            "Bad GateWay, Status code : {}.".format(response.status_code),
                        )
                    )
                    raise ArmisException()
                else:
                    logging.error(
                        consts.LOG_FORMAT.format(
                            __method_name,
                            "Unexpected Error = {}, Status code : {}.".format(response.text, response.status_code),
                        )
                    )
                    raise ArmisException()
            logging.error(consts.LOG_FORMAT.format(__method_name, "Max retries exceeded."))
            raise ArmisException()
        except ArmisException:
            raise ArmisException()
        except requests.ConnectionError as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Connection error : {}.".format(err),
                )
            )
            raise ArmisException()
        except requests.HTTPError as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "HTTP error : {}.".format(err),
                )
            )
            raise ArmisException()
        except requests.Timeout as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Timeout error : {}.".format(err),
                )
            )
            raise ArmisException()
        except requests.exceptions.InvalidURL as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Invalid URL error : {}.".format(err),
                )
            )
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(
                    __method_name,
                    "Unexpected error : {}.".format(err),
                )
            )
            raise ArmisException()

    def get_formatted_time(self, alert_time):
        """Format alert time.

        Args:
            alert_time (str): time to format

        Returns:
            str: formatted time
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if len(alert_time) != 19:
                if len(alert_time) == 10:
                    alert_time += "T00:00:00"
                    logging.info(
                        consts.LOG_FORMAT.format(__method_name, "'T:00:00:00' added as only date is available.")
                    )
                else:
                    splited_time = alert_time.split("T")
                    if len(splited_time[1]) == 5:
                        splited_time[1] += ":00"
                        logging.info(consts.LOG_FORMAT.format(__method_name, "':00' added as seconds not available."))
                    elif len(splited_time[1]) == 2:
                        splited_time[1] += ":00:00"
                        logging.info(
                            consts.LOG_FORMAT.format(__method_name, "':00:00' added as only hour is available.")
                        )
                    alert_time = "T".join(splited_time)
            return alert_time
        except KeyError as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Key error : {}.".format(err)))
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(__method_name, "Error while posting alerts checkpoint : {}.".format(err))
            )
            raise ArmisException()

    def get_access_token(self):
        """get_access_token method will fetch the access token using api and set it in header for further use."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = {"secret_key": self._secret_key}
            logging.info(consts.LOG_FORMAT.format(__method_name, "Getting access token."))
            response = self.make_rest_call(method="POST", url=consts.URL + consts.ACCESS_TOKEN_SUFFIX, data=body)
            access_token = response.get("data", {}).get("access_token")
            self.header.update({"Authorization": access_token})
            logging.info(consts.LOG_FORMAT.format(__method_name, "Generated access token Successfully."))
        except KeyError as err:
            logging.error(consts.LOG_FORMAT.format(__method_name, "Key error : {}.".format(err)))
            raise ArmisException()
        except ArmisException:
            raise ArmisException()
        except Exception as err:
            logging.error(
                consts.LOG_FORMAT.format(__method_name, "Error while generating the access token : {}.".format(err))
            )
            raise ArmisException()
