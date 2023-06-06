"""This file contains implementation to configure integration settings for Dataminr RTAP."""
import os
import json
import inspect
import requests
from shared_code.consts import LOGS_STARTS_WITH, ENDPOINTS, BASE_URL
from shared_code.dataminrpulse_exception import DataminrPulseException
from shared_code.logger import applogger

client_id = os.environ.get("ClientId")
client_secret = os.environ.get("ClientSecret")


class DataminrPulseConfigureSettings:
    """This class will add integation settings in DataminrPulse to receive data via RTAPin Sentinel."""

    def __init__(self) -> None:
        """Initialize instance variables for class."""
        self.base_url = BASE_URL
        self.auth_endpoint = ENDPOINTS["authentication"]
        self.get_lists_path = ENDPOINTS.get("get_lists")
        self.add_settings_path = ENDPOINTS.get("add_integration_settings")
        self.logs_starts_with = LOGS_STARTS_WITH
        self.error_logs = "{}(method={}) {}"
        self.auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers = {"Content-Type": "application/json"}
        self.list_ids = []
        self.check_environment_var_existance()

    def check_environment_var_existance(self):
        """To verify that all required environment variables are exist.

        Raises:
            DataminrPulseException: raise exception if any of the required environment variable is not set.
        """
        __method_name = inspect.currentframe().f_code.co_name
        env_var = [
            {"ClientId": client_id},
            {"ClientSecret": client_secret},
            {"BaseURL": BASE_URL},
        ]
        try:
            applogger.debug(
                "{}(method={}) Checking environment variables are exist or not.".format(
                    self.logs_starts_with, __method_name
                )
            )
            for i in env_var:
                key, val = next(iter(i.items()))
                if val is None:
                    raise DataminrPulseException(
                        "{} is not set in the environment please set the environment variable.".format(
                            key
                        )
                    )
            applogger.debug(
                "{}(method={}) All custom environment variable exists.".format(
                    self.logs_starts_with, __method_name
                )
            )
        except DataminrPulseException as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def make_rest_call(
        self, endpoint, request_method, api_headers, params=None, body=None
    ):
        """To call DataminrPulse API.

        Args:
            endpoint (str): endpoint to call.
            request_method: method to use for requesting an endpoint.(POST/GET)
            params (json, optional): query parameters to pass in API call. Defaults to None.
            body (json, optional): Request body to pass in API call. Defaults to None.

        Returns:
            json: returns json response if API call succeed.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "{}(method={}) Calling DataminrPulse API for endpoint={}".format(
                    self.logs_starts_with, __method_name, endpoint
                )
            )
            dataminr_api_url = "{}{}".format(self.base_url, endpoint)
            response = requests.request(
                method=request_method,
                url=dataminr_api_url,
                headers=api_headers,
                params=params,
                data=body,
            )
            if response.status_code == 400:
                applogger.error(
                    "{}(method={}) The format of the request is incorrect. {}(StatusCode={})".format(
                        self.logs_starts_with,
                        __method_name,
                        response.text,
                        response.status_code,
                    )
                )
            elif response.status_code == 401:
                applogger.error(
                    "{}(method={}) Invalid dma token. {}(StatusCode={})".format(
                        self.logs_starts_with,
                        __method_name,
                        response.text,
                        response.status_code,
                    )
                )
            elif response.status_code == 403:
                applogger.error(
                    "{}(method={}) Not permitted to access this resource.{} (StatusCode={})".format(
                        self.logs_starts_with,
                        __method_name,
                        response.text,
                        response.status_code,
                    )
                )
            elif response.status_code == 500:
                applogger.error(
                    "{}(method={}) The Dataminr server experienced an error. {}(StatusCode={})".format(
                        self.logs_starts_with,
                        __method_name,
                        response.text,
                        response.status_code,
                    )
                )
            elif response.status_code == 200:
                applogger.debug(
                    "{}(method={}) request to endpoint {} is completed successfully.".format(
                        self.logs_starts_with, __method_name, endpoint
                    )
                )
            else:
                applogger.error(
                    "{}(method={}) Error while calling Dataminr API: StatusCode={} , Message={}".format(
                        self.logs_starts_with,
                        __method_name,
                        response.status_code,
                        response.text,
                    )
                )
        except requests.ConnectionError as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)
        except requests.HTTPError as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)
        except requests.RequestException as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}(method={}) Exception{}".format(
                    self.logs_starts_with, __method_name, err
                )
            )
            raise DataminrPulseException(err)
        return response

    def authentication(self, client_id, client_secret):
        """To authenticate with DataminrPulse account.

        Args:
            client_id (str): clientid of Dataminr account to authenticate with it.
            client_secret (str): clientsecret of Dataminr account to authenticate with it.

        Raises:
            DataminrPulseException: raises when any error occurs.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            body = {
                "grant_type": "api_key",
                "client_id": client_id,
                "client_secret": client_secret,
            }
            auth_response = self.make_rest_call(
                self.auth_endpoint, "POST", self.auth_headers, body=body
            )
            if auth_response.status_code == 200:
                applogger.info(
                    "{}(method={}) Successfully authenticated with DataminrPulse account.".format(
                        self.logs_starts_with, __method_name
                    )
                )
                json_auth_response = auth_response.json()
                access_token = json_auth_response.get("dmaToken")
                self.headers.update({"Authorization": "Dmauth {}".format(access_token)})
            else:
                applogger.error(
                    "{}(method={}) Error while authenticating with DataminrPulse account.".format(
                        self.logs_starts_with,
                        __method_name,
                    )
                )
                raise DataminrPulseException(auth_response.text)
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise DataminrPulseException(err)

    def get_lists(self):
        """To fetch lists from Dataminr API.

        Args:
            names (list): names of lists

        Returns:
            list: list of watchlists configured in Dataminr account.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "{}(method={}) Getting lists from Dataminr API.".format(
                    self.logs_starts_with, __method_name
                )
            )
            api_response = self.make_rest_call(self.get_lists_path, "GET", self.headers)
            if api_response.status_code == 200:
                json_api_response = api_response.json()
                lists_resp = json_api_response.get("watchlists").values()
                watchlists = sum(lists_resp, [])
                return watchlists
            else:
                applogger.error(
                    "{}(method={}) Error while fetching lists configured in provided Dataminr account.".format(
                        self.logs_starts_with,
                        __method_name,
                    )
                )
                raise DataminrPulseException(api_response.text)
        except KeyError as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)

    def get_list_ids(self, watchlists):
        """Get list ids.

        Args:
            lists (list): list of cofigured watchlists.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.list_ids = [lst.get("id") for lst in watchlists]
        except KeyError as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)

    def prepare_integration_settings_body(self, data):
        """Prepare request body to add integration settings.

        Args:
            data (json): data required for configuration.

        Raises:
            DataminrPulseException: raises when any error occurs.

        Returns:
            json: request body require for adding integration settings.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = {
                "watchlists": [],
                "deliveryType": "ms_sentinel",
                "deliveryInfo": {"webhook": "", "authToken": ""},
            }
            watchlists = []
            for id in self.list_ids:
                watchlist = {"id": id, "brands": ["ALERT", "FLASH", "URGENT"]}
                watchlists.append(watchlist)
            body.update({"watchlists": watchlists})
            webhook_url = data.get("url")
            auth_token = data.get("token")
            if webhook_url and auth_token:
                body.update(
                    {
                        "deliveryInfo": {
                            "webhook": webhook_url,
                            "authToken": auth_token,
                        }
                    }
                )
            else:
                applogger.error(
                    "{}(method_name={}) Please provide valid key-value for url and token as mentioned below.".format(
                        self.logs_starts_with, __method_name
                    )
                )
                applogger.error('("url": "<url>", "token": "<token>")')
                raise DataminrPulseException(
                    'Please provide valid key-value for url and token as mentioned:("url": "<url>", "token": "<token>")'
                )
            return body
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)

    def add_integration_settings(self, data):
        """To add integration settings for Dataminr RTAP.

        Args:
            data (json): data obtained via HTTP request of azure function.

        Raises:
            DataminrPulseException: raises when any error occurs.

        Returns:
            json: json response of API
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = self.prepare_integration_settings_body(data)
            api_response = self.make_rest_call(
                self.add_settings_path, "POST", self.headers, body=json.dumps(body)
            )
            if api_response.status_code == 200:
                return api_response.json()
            else:
                applogger.error(
                    "{}(method={}) Error while adding integration settings in DataminrPulse account.".format(
                        self.logs_starts_with,
                        __method_name,
                    )
                )
                raise DataminrPulseException(api_response.text)
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)

    def add_webhook_configuration_to_dataminr(self, data):
        """To configure integration settings for Dataminr RTAP.

        Args:
            data (json): data obtained via HTTP request of azure function.
            client_id (str): clientid of Dataminr account to authenticate with it.
            client_secret (str): clientsecret of Dataminr account to authenticate with it.

        Raises:
            DataminrPulseException: raises when any error occurs.

        Returns:
            tuple: return success_flag and settings_id if configureation is done successfully.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            setting_id = None
            self.authentication(client_id, client_secret)
            watchlists = self.get_lists()
            if watchlists:
                self.get_list_ids(watchlists)
            else:
                applogger.warning(
                    "{}(method={}) At least one watchlist must be configured on Dataminr acoount to get alerts.".format(
                        self.logs_starts_with, __method_name
                    )
                )
                raise DataminrPulseException(
                    "Please configure atleast one watchlist on your Dataminr account."
                )
            json_response = self.add_integration_settings(data)
            if json_response:
                applogger.info(
                    "{}(method={}) Integration settings are added successfully to Dataminr with settingId={}".format(
                        self.logs_starts_with,
                        __method_name,
                        json_response.get("deliverySettingId"),
                    )
                )
                setting_id = json_response.get("deliverySettingId")
                return setting_id
            else:
                raise DataminrPulseException(
                    "Problem while adding integration settings."
                )
        except DataminrPulseException as err:
            raise DataminrPulseException(err)
        except Exception as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise DataminrPulseException(err)
