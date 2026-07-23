"""This file contains methods for validations, checkpoint, pulling and pushing data."""

import sys
import datetime
import json
from json.decoder import JSONDecodeError
import inspect
import requests
import hashlib
import time
from datetime import timedelta
from requests.auth import HTTPBasicAuth
from ..SharedCode import consts, keyvault_secrets_management
from ..SharedCode.consts import DETECTIONS_DETAILS_ENDPOINT, EXCLUDE_GROUP_DETAILS_FROM_DETECTIONS
from ..SharedCode.logger import applogger
from ..SharedCode.sentinel import send_data_to_sentinel
from ..SharedCode.vectra_exception import VectraException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
    retry_any,
    RetryError,
)
from requests.exceptions import ConnectionError


class BaseCollector:
    """This class contains methods to create object and helper methods."""

    def __init__(
        self, start_time, function_name, client_id, client_secret
    ) -> None:
        """Initialize instance variable for class."""
        self.connection_string = consts.CONNECTION_STRING
        self.log_format = consts.LOG_FORMAT
        self.base_url = consts.BASE_URL
        self.client_id = client_id
        self.client_secret = client_secret
        self.start_time = consts.START_TIME
        self.execution_start_time = start_time
        self.session = requests.Session()
        self.session.headers["User-Agent"] = consts.USER_AGENT
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.function_name = function_name
        self.access_token_expiration = None
        self.refresh_token_expiration = None
        self.access_token = None
        self.refresh_token = None
        self.keyvault_obj = keyvault_secrets_management.KeyVaultSecretManage()

    def load_tokens_from_keyvault(self):
        """Load tokens from KeyVault based on access and refresh token keys."""
        properties_list = self.keyvault_obj.get_properties_list_of_secrets()
        if self.access_token_key in properties_list:
            self.access_token = self.keyvault_obj.get_keyvault_secret(self.access_token_key)
        if self.refresh_token_key in properties_list:
            self.refresh_token = self.keyvault_obj.get_keyvault_secret(self.refresh_token_key)

    def load_expiration_time_from_checkpoint_file(self):
        """Load expiration time from checkpoint file."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            data = self.state.get()
            if data is not None and data:
                data = json.loads(data)
                self.access_token_expiration = data.get(self.access_token_expiry, None)
                self.refresh_token_expiration = data.get(self.refresh_token_expiry, None)
        except VectraException:
            raise VectraException()
        except Exception as err:
            applogger.error(
                "{}(method={}) : {} : Exception occured while getting data from storage account. : {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            raise VectraException()

    def add_token_expiration_to_checkpoint_file(self, token_data, from_refresh_token: bool):
        """Add token to keyvault and expiration time to checkpoint file.

        Args:
            token_data (json): token_data to be added in checkpoint file and keyvault.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            checkpoint_data = {}
            self.access_token = token_data["access_token"]
            self.session.headers["Authorization"] = "bearer {}".format(
                self.access_token
            )
            self.access_token_expiration = (
                datetime.datetime.now() + timedelta(seconds=token_data["expires_in"])
            ).isoformat()
            if not from_refresh_token:
                applogger.info(
                    "{}(method={}) : {} : Both access token and refresh token are generated successfully.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                self.refresh_token = token_data["refresh_token"]
                self.keyvault_obj.set_keyvault_secret(self.refresh_token_key, self.refresh_token)
                self.refresh_token_expiration = (
                    datetime.datetime.now() + timedelta(seconds=token_data["refresh_expires_in"])
                ).isoformat()
                token_data = {
                    self.access_token_expiry: self.access_token_expiration,
                    self.refresh_token_expiry: self.refresh_token_expiration,
                }
            else:
                applogger.info(
                    "{}(method={}) : {} :  Access Token Generated from Refresh Token.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                token_data = {self.access_token_expiry: self.access_token_expiration}
            checkpoint_data.update(token_data)
            self.keyvault_obj.set_keyvault_secret(self.access_token_key, self.access_token)
            self.save_checkpoint(data=checkpoint_data, token_expiry_time=True)
        except VectraException:
            raise VectraException()
        except Exception as err:
            applogger.error(
                "{}(method={}) : {} : Error occured in storing token or expiration time: {} ".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            raise VectraException()

    def generate_access_token(self, from_refresh_token: bool):
        """Generate the Token and Refresh token.

        Args:
            from_refresh_token (bool): To generate Access Token from refresh token or not

        Raises:
            ValueError: When response status code is not [200,201]
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            url = self.base_url + consts.OAUTH2_ENDPOINT
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            data = None
            if from_refresh_token:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                }
                applogger.debug(
                    "{}(method={}) : {} : Generating access token using refresh token.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
            else:
                data = {"grant_type": "client_credentials"}
                applogger.debug(
                    "{}(method={}) : {} : Generating access token.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
            for _ in range(2):
                response = requests.post(url, auth=auth, data=data, timeout=consts.API_TIMEOUT)
                if response.status_code in [200, 201]:
                    token_data = response.json()
                    self.add_token_expiration_to_checkpoint_file(token_data, from_refresh_token)
                    self.update_checkpoint_of_disabling_function(make_count_zero=True)
                    applogger.debug(
                        "{}(method={}) : {} : New access token generated successfully ".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    return
                elif response.status_code in [400, 401, 403, 404]:
                    self.update_checkpoint_of_disabling_function()
                    applogger.error(
                        "{}(method={}) : {} : status code={}, reason={}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            response.status_code,
                            response.text
                        )
                    )
                    raise VectraException()
                elif response.status_code == 429:
                    sleep_count = int(response.headers.get("Retry-After", "30")) + 5
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            "Too Many Requests, Status code : {}, Sleeping for {} seconds".format(
                                response.status_code, sleep_count
                            ),
                        )
                    )
                    time.sleep(sleep_count)
                else:
                    applogger.error(
                        "{}(method={}) : {} : Unknown status code: {} ".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            response.status_code,
                        )
                    )
                    raise VectraException()
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    "Max retries exceeded for generating access token."
                )
            )
            raise VectraException()
        except VectraException:
            raise VectraException()
        except requests.exceptions.RequestException as err:
            applogger.error(
                "{}(method={}) : {} : Error occurred while generating a Access Token : {} ".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            raise VectraException()
        except Exception as err:
            applogger.error(
                "{}(method={}) : {} : Error occurred while generating a Access Token : {} ".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            raise VectraException()

    def validate_access_token(self):
        """Validate the existing token and refresh token."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            from_refresh_token = 0
            if self.access_token:
                if self.is_token_expired(self.access_token_expiration) and not self.is_token_expired(
                    self.refresh_token_expiration
                ):
                    applogger.info(
                        "{}(method={}) : {} : Access token expired. Generating new access token using refresh token.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    from_refresh_token = 1
                    self.generate_access_token(from_refresh_token)
                elif self.is_token_expired(self.access_token_expiration) and self.is_token_expired(
                    self.refresh_token_expiration
                ):
                    applogger.info(
                        "{}(method={}) : {} : Both access token and refresh token are expired or expiration time does not exist.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    self.generate_access_token(from_refresh_token)
                else:
                    applogger.info(
                        "{}(method={}) : {} : Using existing and valid access token.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
            else:
                applogger.info(
                    "{}(method={}) : {} : Access token does not exist.Generating new access token and refresh token.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                self.generate_access_token(from_refresh_token)
        except VectraException:
            raise VectraException()
        except Exception as err:
            applogger.error(
                "{}(method={}) : {} : Error in getting access token. : {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            raise VectraException()

    def is_token_expired(self, token_expiration):
        """To check if token is expired or not.

        Returns:
            bool: True or False
        """
        if not token_expiration:
            return True
        current_time = datetime.datetime.now().isoformat()
        return bool(token_expiration and (current_time > (token_expiration)))

    def update_checkpoint_of_disabling_function(self, make_count_zero=False):
        """Update checkpoint file for disabling function.

        Args:
            make_count_zero (bool): True when count of status code should be made zero

        Raises:
            Exception: if anything goes unintended
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            checkpoint_file = self.state.get()
            checkpoint_json_data = {"disable_function": False}
            if checkpoint_file:
                checkpoint_json_data.update(json.loads(checkpoint_file))
            if checkpoint_json_data.get("disable_function"):
                checkpoint_json_data.update({"disable_function": False, "status_code_count": 0})
                self.state.post(json.dumps(checkpoint_json_data))
            if make_count_zero:
                if checkpoint_json_data.get("status_code_count") != 0:
                    checkpoint_json_data.update({"status_code_count": 0})
                    self.state.post(json.dumps(checkpoint_json_data))
                    applogger.debug(
                        "{}(method={}): {}: Checkpoint file updated as total count of status code made zero.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                else:
                    applogger.debug(
                        "{}(method={}): {}: Checkpoint file already have total count of status code equal to zero.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
            else:
                current_count = checkpoint_json_data.get("status_code_count", 0)
                updated_status_code_count = current_count + 1
                if updated_status_code_count >= 10:
                    applogger.info(
                        "{}(method={}): {}: Function App will be Disabled.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    checkpoint_json_data.update({"disable_function": True, "status_code_count": updated_status_code_count})
                    self.state.post(json.dumps(checkpoint_json_data))
                    self.disable_function()
                    return

                checkpoint_json_data.update({"status_code_count": updated_status_code_count})
                self.state.post(json.dumps(checkpoint_json_data))
                applogger.debug(
                    "{}(method={}): {}: Updated failed status code count in checkpoint file.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
        except VectraException:
            raise VectraException()
        except Exception as err:
            applogger.error(
                "{}(method={}): {}: Error Occured while updating checkpoint file of disabling function. : '{}'".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )

            raise VectraException()

    def disable_function(self):
        """Disable a function app as failure count reached to 10.

        Raises:
            Exception: if any error occurs
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            url = (consts.DISABLE_FUNCTION_APP_URL).format(consts.SUBSCRIPTION_ID, consts.RESOURCE_GROUP, consts.FUNCTION_APP_NAME)

            access_token = self.azure_token_generator()
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(url=url, headers=headers)

            response.raise_for_status()
            if response.status_code in [200, 201]:
                applogger.info(
                    "{}(method={}): {}: Function App disabled successfully.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
            else:
                applogger.error(
                    "{}(method={}): {}: Error occurred while disabling function. status_code={}, reason={}".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name, response.status_code, response.text
                    )
                )
                raise VectraException()
        except VectraException:
            raise VectraException()
        except requests.exceptions.HTTPError as err:
            applogger.error(
                "{}(method={}): {}: Error occurred while disabling function : status code: {}, reason: '{}'.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, response.status_code, err
                )
            )
            self.save_checkpoint(data={"disable_function": False}, disable_function_error=True)
            raise VectraException()
        except Exception as err:
            applogger.error(
                "{}(method={}): {}: Error occured while disabling function : '{}'.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            self.save_checkpoint(data={"disable_function": False}, disable_function_error=True)
            raise VectraException()

    def azure_token_generator(self):
        """Generate access token for azure."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            url = consts.AZURE_AUTHENTICATION_URL.format(consts.AZURE_TENANT_ID)

            data = {
                "client_id": consts.AZURE_CLIENT_ID,
                "client_secret": consts.AZURE_CLIENT_SECRET,
                "grant_type": "client_credentials",
                "scope": consts.AZURE_AUTHENTICATION_SCOPE,
            }

            response = requests.get(url=url, data=data)
            if response.status_code in [200, 201]:
                applogger.info(
                    "{}(method={}): {}: Azure Token Generated Successfully.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                return response.json()["access_token"]
            else:
                applogger.error(
                    "{}(method={}): {}: Unknown Status code while generating access token for AZURE: {} .".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name, response.status_code
                    )
                )
                self.save_checkpoint(data={"disable_function": False}, disable_function_error=True)
                raise VectraException()
        except VectraException:
            raise VectraException()
        except Exception as err:
            applogger.info(
                "{}(method={}): {}: Error occured while generating access token for AZURE: {}.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, err
                )
            )
            self.save_checkpoint(data={"disable_function": False}, disable_function_error=True)
            raise VectraException()

    def validate_params(self, client_id_name, client_secret_name, snapshot=False):
        """To validate parameters of function app."""
        __method_name = inspect.currentframe().f_code.co_name
        required_params = {
            "BaseURL": self.base_url,
            client_id_name: self.client_id,
            client_secret_name: self.client_secret,
            "Detections_Table_Name": consts.DETECTIONS_TABLE_NAME,
            "Audits_Table_Name": consts.AUDITS_TABLE_NAME,
            "Entity_Scoring_Table_Name": consts.ENTITY_SCORING_TABLE_NAME,
            "Lockdown_Table_Name": consts.LOCKDOWN_TABLE_NAME,
            "Health_Table_Name": consts.HEALTH_TABLE_NAME,
            "AZURE_CLIENT_ID": consts.AZURE_CLIENT_ID,
            "AZURE_CLIENT_SECRET": consts.AZURE_CLIENT_SECRET,
            "AZURE_TENANT_ID": consts.AZURE_TENANT_ID,
            "KeyVaultName": consts.KEYVAULT_NAME,
            "Entities_Table_Name": consts.ENTITIES_TABLE_NAME,
            "Azure_Subscription_Id": consts.SUBSCRIPTION_ID,
            "Azure_Resource_Group_Name": consts.RESOURCE_GROUP,
        }
        missing_required_field = False
        for label, params in required_params.items():
            if not params:
                missing_required_field = True
                applogger.error(
                    '{}(method={}): {}: "{}" field is not configured. field_value="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        label,
                        params,
                    )
                )
        if missing_required_field:
            raise Exception("Error Occurred while validating params. Required fields missing.")
        if not self.base_url.startswith("https://"):
            applogger.error(
                '{}(method={}) : {} : "BaseURL" must start with ”https://” schema followed '
                'by hostname. BaseURL="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    self.base_url,
                )
            )
            raise Exception("Error Occurred while validating params. Invalid format for BaseURL.")

        if not snapshot:
            try:
                if self.start_time:
                    input_date = datetime.datetime.strptime(self.start_time, r"%m/%d/%Y %H:%M:%S")
                    now = datetime.datetime.utcnow()
                    if input_date > now:
                        applogger.error(
                            '{}(method={}) : {} : "StartTime" should not be in future. StartTime="{}"'.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                self.start_time,
                            )
                        )
                        raise VectraException()
                    self.start_time = datetime.datetime.strftime(input_date, r"%Y-%m-%dT%H:%M:%SZ")
                else:
                    self.start_time = (
                        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=24)
                    ).strftime(r"%Y-%m-%dT%H:%M:%SZ")
            except VectraException:
                raise VectraException()
            except ValueError:
                applogger.error(
                    '{}(method={}) : {} : "StartTime" should be in "MM/DD/YYYY HH:MM:SS" (UTC) '
                    'format. StartTime="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        self.start_time,
                    )
                )
                raise VectraException()

    def validate_connection(self):
        """To validate the connection with vectra and generate access token."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.load_tokens_from_keyvault()
            self.load_expiration_time_from_checkpoint_file()
            self.validate_access_token()
            if self.access_token:
                self.session.headers["Authorization"] = "bearer {}".format(self.access_token)
                applogger.info(
                    "{}(method={}) : {} : Token or Connection validation is successful.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
                return
        except VectraException:
            raise VectraException()
        except Exception as ex:
            raise VectraException(ex)

    def pull_data(self, endpoint, params=None):
        """To call vectra API till retry condition is not met.

        Args:
            endpoint (str): endpoint to call in Vectra.
            params (dict, optional): params to pass to API. Defaults to None.

        Returns:
            response: response object
        """
        __method_name = inspect.currentframe().f_code.co_name
        if endpoint == DETECTIONS_DETAILS_ENDPOINT:
            res = self.pull_detections_data(url=self.base_url + endpoint, params=params)
            final_res = {"results": res}
            applogger.info(
                "{}(method={}) : {} : Received Data for Detections. Length of data: {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, len(res)
                )
            )
            return final_res
        else:
            res, _ = self.pull(url=self.base_url + endpoint, params=params)
            return res

    def retry_on_status_code(response):
        """Check and retry based on a list of status codes.

        Args:
            tuple_response (): API response and function name is passed

        Returns:
            Bool: if given status code is in list then true else false
        """
        __method_name = inspect.currentframe().f_code.co_name
        function_name = response[1]
        response = response[0]
        if isinstance(response, dict) or isinstance(response, list):
            return False
        if response.status_code in consts.RETRY_STATUS_CODE:
            applogger.info(
                "{}(method={}) : {} : Retrying due to status code : {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, function_name, response.status_code
                )
            )
            return True
        return False

    @retry(
        stop=stop_after_attempt(consts.MAX_RETRIES),
        wait=wait_exponential(
            multiplier=consts.BACKOFF_MULTIPLIER,
            min=consts.MIN_SLEEP_TIME,
            max=consts.MAX_SLEEP_TIME,
        ),
        retry=retry_any(
            retry_if_result(retry_on_status_code),
            retry_if_exception_type(ConnectionError),
        ),
        before_sleep=lambda retry_state: applogger.error(
            "{}(method = {}) : Retring after {} secends, attempt number: {} ".format(
                consts.LOGS_STARTS_WITH,
                " Retry Decorator",
                retry_state.upcoming_sleep,
                retry_state.attempt_number,
            )
        ),
    )
    def pull(self, url, params=None, data=None, auth=None, method="GET", check_retry = True):
        """Will pull data from each API.

        Args:
            url (str): _description_
            params (json, optional): _description_. Defaults to None.
            data (json, optional): _description_. Defaults to None.
            auth (json, optional): _description_. Defaults to None.
            method (str, optional): _description_. Defaults to "GET".

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "{}(method={}) : {} request: url='{}' version='{}'".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    url,
                    self.session.headers["User-Agent"],
                )
            )
            if method == "POST":
                res = self.session.post(
                    url=url,
                    auth=auth,
                    params=params,
                    data=data,
                    timeout=consts.API_TIMEOUT,
                )
            else:
                res = self.session.get(
                    url=url,
                    auth=auth,
                    params=params,
                    data=data,
                    timeout=consts.API_TIMEOUT,
                )
            if res.status_code == 401:
                if check_retry:
                    check_retry = False
                    applogger.warning(
                        "{}(method={}) : {} : Access token is invalid. generating new token.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    if not self.is_token_expired(self.access_token_expiration) and not self.is_token_expired(
                        self.refresh_token_expiration
                    ):
                        self.generate_access_token(from_refresh_token=False)
                    else:
                        self.validate_access_token()
                    return self.pull(url=url, params=params, data=data, auth=auth, method=method, check_retry=check_retry)
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            "Max retry reached for generating access token."
                            ),
                        )
                self.update_checkpoint_of_disabling_function()
                raise VectraException()
            elif res and res.status_code in [200, 201]:
                applogger.debug(
                    '{}(method={}) : {} : API call: Response received successfully. url="{}" params="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        params,
                    )
                )
                self.update_checkpoint_of_disabling_function(make_count_zero=True)
                return res.json(), self.function_name

            elif res.status_code in [400, 403]:
                applogger.error(
                    "{}(method={}) : {} : API call: response: url={} status_code={} response={}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        res.status_code,
                        res.text,
                    )
                )
                self.update_checkpoint_of_disabling_function()
                raise VectraException()
            elif res.status_code == 404:
                applogger.error(
                    "{}(method={}) : {} : API call: response: url={} status_code={} response={}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        res.status_code,
                        res.text,
                    )
                )
                if "That page contains no results" in res.text:
                    applogger.info(
                        "{}(method={}) : {} : All data ingested. No more data found for url = {}, params = {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            url,
                            params,
                        )
                    )
                    return {}, self.function_name
                self.update_checkpoint_of_disabling_function()
                raise VectraException()
            elif res.status_code == 429:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        "Too Many Requests, Status code : {} ".format(
                            res.status_code
                        ),
                    )
                )
                return res, self.function_name
            elif res.status_code == 500:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        "Internal Server Error, Status code : {}".format(
                            res.status_code
                        ),
                    )
                )
                return res, self.function_name
            else:
                applogger.error(
                    "{}(method={}) : {} : API call: Unknown status code or empty "
                    'response: url="{}" status_code="{}" response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        res.status_code,
                        res.text,
                    )
                )
                raise VectraException("Received unknown status code or empty response.")
        except VectraException:
            raise VectraException()
        except requests.ConnectionError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    consts.CONNECTION_ERROR_MSG.format(error),
                )
            )
            raise ConnectionError()
        except requests.exceptions.Timeout as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    consts.TIME_OUT_ERROR_MSG.format(error),
                )
            )
            raise VectraException()
        except JSONDecodeError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    consts.JSON_DECODE_ERROR_MSG.format(
                        "{}, API Response = {}".format(error, res.text)
                    ),
                )
            )
            raise VectraException()
        except requests.exceptions.RequestException as ex:
            if res.status_code == 404:
                applogger.debug(
                    '{}(method={}) : {} : API call: Got {} Status Code : url="{}"'
                    ' response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        ex.response.status_code,
                        ex.response.text,
                    )
                )
                return {}, self.function_name
            else:
                applogger.error(
                    '{}(method={}) : {} : API call: Unsuccessful response: url="{}" status_code="{}"'
                    ' response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        ex.response.status_code,
                        ex.response.text,
                    )
                )
                raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : API call: Unexpected error while API call url="{}" error="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    url,
                    str(ex),
                )
            )
            raise VectraException()

    def pull_detections_data(self, url, params=None, data=None, auth=None):
        """Fetch detection data from the specified API endpoint, handling authentication, retries, and error scenarios.

        Args:
            url (str): The API endpoint URL to fetch detection data from.
            params (dict, optional): Query parameters to include in the request.
            data (dict, optional): Data to send in the request body.
            auth (tuple, optional): Authentication credentials for the request.

        Returns:
            list: A list of detection results if the request is successful.
            dict: An empty dictionary if a 404 error occurs.

        Raises:
            VectraException: If an error occurs during the API call or if retry limits are exceeded.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "{}(method={}) : {} request: url='{}' version='{}'".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    url,
                    self.session.headers["User-Agent"],
                )
            )
            counter = 0
            for _ in range(2):
                res = self.session.get(
                    url=url,
                    auth=auth,
                    params=params,
                    data=data,
                    timeout=consts.API_TIMEOUT,
                )
                if res.status_code == 401:
                    applogger.warning(
                        "{}(method={}) : {} : Access token is invalid. generating new token.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    if not self.is_token_expired(
                        self.access_token_expiration
                    ) and not self.is_token_expired(self.refresh_token_expiration):
                        self.generate_access_token(from_refresh_token=False)
                    else:
                        self.validate_access_token()
                    counter += 1
                    continue
                elif res and res.status_code in [200, 201]:
                    applogger.debug(
                        '{}(method={}) : {} : API call: Response received successfully. url="{}" params="{}"'.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            url,
                            params,
                        )
                    )
                    self.update_checkpoint_of_disabling_function(make_count_zero=True)
                    return res.json().get("results", [])
                elif res.status_code == 429:
                    applogger.error(
                        "{}(method={}) : {} : API call: response: url={} status_code={} response={}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            url,
                            res.status_code,
                            res.text,
                        )
                    )
                    counter += 1
                    time.sleep(5)
                    continue
                elif res.status_code in [400, 403, 404]:
                    applogger.error(
                        "{}(method={}) : {} : API call: response: url={} status_code={} response={}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            url,
                            res.status_code,
                            res.text,
                        )
                    )
                    self.update_checkpoint_of_disabling_function()
                    raise VectraException()
                elif res.status_code in [413, 502]:
                    applogger.error(
                        "{}(method={}) : {} : API call: response: url={} status_code={} Entity Too Large"
                        "Trying to divide list of IDs and fetch data again.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            url,
                            res.status_code,
                        )
                    )
                    if DETECTIONS_DETAILS_ENDPOINT not in url:
                        raise VectraException(
                            "Status code {} occurred in another endpoint".format(
                                res.status_code
                            )
                        )

                    detection_ids_str = params.get("id")
                    detection_ids = detection_ids_str.split(",")
                    length = len(detection_ids)
                    applogger.info(
                        "{}(method={}) : {} : Dividing available detection IDs: {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            detection_ids_str,
                        )
                    )
                    if len(detection_ids) == 1:
                        return []
                    detection_id1 = detection_ids[: length // 2]
                    detection_id2 = detection_ids[length // 2:]
                    try:
                        params["id"] = ",".join(detection_id1)
                        if EXCLUDE_GROUP_DETAILS_FROM_DETECTIONS:
                            params["exclude_fields"] = "grouped_details"
                        applogger.info(
                            "{}(method={}) : {} : Calling API for left part detection IDs with params: {}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                params,
                            )
                        )
                        left_side_response = self.pull_detections_data(
                            url=url, params=params
                        )
                        applogger.info(
                            "{}(method={}) : {} : Received Data for left side detection IDs: {}"
                            ", length of data: {}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                detection_id1,
                                len(left_side_response),
                            )
                        )
                    except Exception as err:
                        applogger.error(
                            "{}(method={}) : {} : API call: response: url={} status_code={} response={}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                url,
                                res.status_code,
                                res.text,
                            )
                        )
                        raise VectraException(err)
                    try:
                        params["id"] = ",".join(detection_id2)
                        applogger.info(
                            "{}(method={}) : {} : Calling API for right part detection IDs with params: {}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                params,
                            )
                        )
                        right_side_response = self.pull_detections_data(
                            url=url, params=params
                        )
                        applogger.info(
                            "{}(method={}) : {} : Received Data for right side detection IDs: {}"
                            ", length of data: {}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                detection_id2,
                                len(right_side_response),
                            )
                        )
                    except Exception as err:
                        applogger.error(
                            "{}(method={}) : {} : API call: response: url={} status_code={} response={}".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                url,
                                res.status_code,
                                res.text,
                            )
                        )
                        raise VectraException(err)

                    left_side_response.extend(right_side_response)
                    return left_side_response

                else:
                    applogger.error(
                        "{}(method={}) : {} : API call: Unknown status code or empty "
                        'response: url="{}" status_code="{}" response="{}"'.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            url,
                            res.status_code,
                            res.text,
                        )
                    )
                    raise VectraException("Received unknown status code or empty response.")

            if counter > 2:
                self.update_checkpoint_of_disabling_function()
                raise VectraException("Retry limit exceeded. Hence exiting the function.")
        except requests.exceptions.RequestException as ex:
            if res.status_code == 404:
                applogger.debug(
                    '{}(method={}) : {} : API call: Got {} Status Code : url="{}"'
                    ' response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        ex.response.status_code,
                        ex.response.text,
                    )
                )
                return {}
            else:
                applogger.error(
                    '{}(method={}) : {} : API call: Unsuccessful response: url="{}" status_code="{}"'
                    ' response="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        url,
                        ex.response.status_code,
                        ex.response.text,
                    )
                )
                raise VectraException("HTTP Error Occurred while getting response from api.")
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : API call: Unexpected error while API call url="{}" error="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    url,
                    str(ex),
                )
            )
            raise VectraException("Error Occurred while getting response from api.")

    def get_checkpoint_field_and_value(self):
        """Fetch last data from checkpoint file.

        Returns:
            None/json: last_data
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            field = None
            checkpoint = self.state.get()
            if checkpoint:
                checkpoint = json.loads(checkpoint)
                if checkpoint.get("from", None):
                    field, checkpoint = "from", checkpoint.get("from")
                elif checkpoint.get("event_timestamp_gte"):
                    field, checkpoint = "event_timestamp_gte", checkpoint.get("event_timestamp_gte")
                else:
                    field, checkpoint = "event_timestamp_gte", self.start_time
                    self.state.post(json.dumps({"event_timestamp_gte": self.start_time}))
            else:
                field, checkpoint = "event_timestamp_gte", self.start_time
                self.state.post(json.dumps({"event_timestamp_gte": self.start_time}))
            applogger.info(
                '{}(method={}) : {} : Checkpoint field="{}" and value="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    field,
                    checkpoint,
                )
            )
            return field, checkpoint
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : Unexpected error while getting checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException()

    def save_checkpoint(
        self, data, token_expiry_time=False, entity_state=None, entities_endpoint=False, disable_function_error=False
    ):
        """Post checkpoint into sentinel."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            checkpoint_data = self.state.get()
            checkpoint_data_json = {}
            if checkpoint_data:
                checkpoint_data_json = json.loads(checkpoint_data)
            if token_expiry_time:
                checkpoint_data_json.update(data)
                self.state.post(json.dumps(checkpoint_data_json))
                applogger.info(
                    '{}(method={}) : {} : successfully saved updated expiration time in checkpoint."{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        data,
                    )
                )
            elif entities_endpoint:
                checkpoint_data_json.update(data)
                entity_state.post(json.dumps(checkpoint_data_json))
                applogger.info(
                    '{}(method={}) : {} : successfully saved checkpoint. Checkpoint modified for entities endpoint="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        checkpoint_data_json,
                    )
                )
            elif disable_function_error:
                checkpoint_data_json.update(data)
                self.state.post(json.dumps(checkpoint_data_json))
                applogger.debug(
                    '{}(method={}) : {} : error while disabling function. So making disable_function flag to False.'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name
                    )
                )
            else:
                checkpoint_data_json.update({"from": data})
                self.state.post(json.dumps(checkpoint_data_json))
                applogger.info(
                    '{}(method={}) : {} : successfully saved checkpoint. from="{}"'.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        data,
                    )
                )
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.exception(
                '{}(method={}) : {} : Unexpected error while saving checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException()

    def post_data_to_sentinel(self, data, table_name, fields):
        """To post data into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if fields:
                for event in data:
                    for field in fields:
                        event[field] = [event.get(field)]
            send_data_to_sentinel(data, table_name)
            applogger.info(
                '{}(method={}) : {} : Successfully posted the data in the table="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    table_name,
                )
            )
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : Error while posting data to sentinel. Error="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException(ex)

    def _get_size_of_chunk_in_mb(self, chunk):
        """Get the size of chunk in MB."""
        return sys.getsizeof(json.dumps(chunk)) / (1024 * 1024)

    def _create_chunks_and_post_to_sentinel(
        self, data, table_name, fields, entity_state=None, entities_endpoint=False
    ):
        """Create chunks and post to chunk to sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        chunk = []
        total_events = len(data)
        total_ingested_events = 0
        if entities_endpoint:
            applogger.info(
                "{}(method={}) : Ingesting data. length of data={}".format(
                    consts.LOGS_STARTS_WITH, __method_name, len(data)
                )
            )
            self.post_data_to_sentinel(data, table_name, fields)
            return
        if self._get_size_of_chunk_in_mb(data) < 25:
            applogger.info(
                "{}(method={}) : Data is less than 25 MB hence posting it directly. length of data={}".format(
                    consts.LOGS_STARTS_WITH, __method_name, len(data)
                )
            )
            self.post_data_to_sentinel(data, table_name, fields)
            return

        skipped_events = 0
        for event in data:
            chunk.append(event)
            if self._get_size_of_chunk_in_mb(chunk) >= 25:
                applogger.info(
                    "{}(method={}) : Data is greater than 25 MB.".format(
                        consts.LOGS_STARTS_WITH, __method_name
                    )
                )
                if chunk[:-1]:
                    total_ingested_events += len(chunk[:-1])
                    applogger.info(
                        "{}(method={}) : Posting data except last event. data to post={} and total_ingested_events={}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            len(chunk[:-1]),
                            total_ingested_events,
                        )
                    )
                    self.post_data_to_sentinel(chunk[:-1], table_name, fields)

                    next_checkpoint = chunk[-2].get("id")
                    self.save_checkpoint(
                        data=next_checkpoint,
                        entity_state=entity_state,
                        entities_endpoint=entities_endpoint,
                    )
                    chunk = [event]
                else:
                    skipped_events += 1
                    event_id = chunk[0].get("id")
                    applogger.error(
                        "{}(method={}) : {} : event with id {} is too large to post into the sentinel hence skipping it.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            event_id,
                        )
                    )
                    chunk = []
        applogger.info(
            "{}(method={}) : {} events are skipped.".format(
                consts.LOGS_STARTS_WITH, __method_name, skipped_events
            )
        )
        if chunk:
            total_ingested_events += len(chunk)
            self.post_data_to_sentinel(chunk, table_name, fields)
        applogger.info(
            "{}(method={}) : {} of {} events are ingested.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                total_ingested_events,
                total_events,
            )
        )

    def pull_and_push_the_data(
        self,
        endpoint,
        checkpoint_field,
        checkpoint_value,
        table_name,
        fields=None,
        query_params=dict(),
    ):
        """To pull the data from vectra and push into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        posted_event_count = 0
        iter_next = True
        query_params.update({"limit": consts.PAGE_SIZE, checkpoint_field: checkpoint_value})
        try:
            while iter_next:
                if (
                    int(time.time())
                    >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                ):
                    applogger.info(
                        "{}(method={}) : 9:30 mins executed hence terminating the function.".format(
                            consts.LOGS_STARTS_WITH, __method_name
                        )
                    )
                    break
                res = self.pull_data(endpoint, params=query_params)
                next_checkpoint = res.get("next_checkpoint", None)
                if endpoint == consts.DETECTIONS_ENDPOINT and len(res.get("events")):
                    applogger.debug(
                        "{}(method={}) : {} : Trying to collect the additional information from"
                        " /detections endpoint for type=host and type=account.".format(
                            consts.LOGS_STARTS_WITH, __method_name, self.function_name
                        )
                    )
                    detection_ids_list = []
                    for event in res.get("events"):
                        if event.get("type") == "host" or event.get("type") == "account":
                            detection_ids_list.append(str(event.get("detection_id")))

                    detection_id_set = set(detection_ids_list)
                    detections_ids = ",".join(detection_id_set)
                    next = True
                    page = 1
                    merge_json = {}

                    if detections_ids:
                        while next:
                            if (
                                int(time.time())
                                >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                            ):
                                applogger.info(
                                    "{}(method={}) : 9:30 mins executed hence terminating the function for detections processing.".format(
                                        consts.LOGS_STARTS_WITH, __method_name
                                    )
                                )
                                break
                            detection_endpoint = DETECTIONS_DETAILS_ENDPOINT
                            applogger.debug(
                                "{}(method={}) : {} : GET call to /detections endpoint with URL = {}".format(
                                    consts.LOGS_STARTS_WITH,
                                    __method_name,
                                    self.function_name,
                                    self.base_url + detection_endpoint,
                                )
                            )
                            host_details = self.pull_data(
                                detection_endpoint,
                                params={"id": detections_ids, "page": page},
                            )
                            if host_details.get("results"):
                                for each in host_details.get("results"):
                                    merge_json[each.get("id")] = each
                            if not host_details.get("next"):
                                break
                            page += 1

                    for event in res.get("events"):
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        if event.get("type") == "host" and merge_json.get(event.get("detection_id"), {}):
                            temp_host = merge_json.get(event.get("detection_id"), {})
                            event["d_detection_details"] = [temp_host]
                            event["is_targeting_key_asset"] = str(temp_host.get("is_targeting_key_asset", ""))
                            event["src_host"] = [temp_host.get("src_host", {})]
                            event["normal_domains"] = temp_host.get("normal_domains", [])
                            event["src_ip"] = temp_host.get("src_ip", "")
                            event["summary"] = [temp_host.get("summary", {})]
                            if not EXCLUDE_GROUP_DETAILS_FROM_DETECTIONS:
                                event["grouped_details"] = temp_host.get("grouped_details", [])
                            event["tags"] = temp_host.get("tags", [])
                        elif event.get("type") == "account":
                            if event.get("detail", {}):
                                event["d_detection_details"] = [event.get("detail", {})]
                            if merge_json.get(event.get("detection_id"), {}):
                                account_data = merge_json.get(event.get("detection_id"), {})
                                event["tags"] = account_data.get("tags", [])
                        else:
                            event["d_detection_details"] = []
                        event["entity_type"] = event.get("type", "")
                        applogger.debug(
                            "{}(method={}) : {} :  Successfully modified events/detections"
                            " response for id={}.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.function_name,
                                event.get("id"),
                            )
                        )
                else:
                    for event in res.get("events"):
                        event["entity_type"] = event.get("type", "")
                if res and len(res.get("events")):
                    self._create_chunks_and_post_to_sentinel(res.get("events"), table_name, fields)
                    posted_event_count += len(res.get("events"))
                    iter_next = True if int(res.get("remaining_count")) > 0 else False
                    query_params.update({"limit": consts.PAGE_SIZE, "from": next_checkpoint})
                else:
                    iter_next = False
                if endpoint == consts.ENTITY_SCORING_ENDPOINT and (next_checkpoint is None or next_checkpoint == "null"):
                    break
                else:
                    self.save_checkpoint(data=next_checkpoint)

            applogger.info(
                "{}(method={}) : {} : Posted total {} event(s) into MS Sentinel. No more events."
                " Stopping the collection.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    posted_event_count,
                )
            )
        except VectraException:
            raise VectraException()
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            self.update_checkpoint_of_disabling_function()
            raise VectraException()

    def pull_and_push_the_snapshot_data(
        self,
        endpoint,
        table_name,
        hashed_events_list=list(),
        hash_field_list=[],
        fields=None,
    ):
        """To pull the snapshot type data from vectra and push into sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        posted_event_count = 0
        try:
            res = self.pull_data(endpoint)
            if res and len(res):
                if endpoint == consts.HEALTH_ENDPOINT:
                    link_status_dict, aggregated_peak_traffic_dict = {}, {}
                    connectivity_dict, trafficdrop_dict = {}, {}

                    # for link_status
                    for k, v in (
                        res.get("network", {})
                        .get("interfaces", {})
                        .get("sensors", {})
                        .items()
                    ):
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function for link status.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        link_status = "UP"
                        for x, y in v.items():
                            if y.get("link", "") != "UP":
                                link_status = "Degraded"
                                break
                        link_status_dict[k] = link_status

                    # for aggregated_peak_traffic
                    for key, value in res.get("network", {}).get("traffic", {}).get("sensors", {}).items():
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function from peak_traffic.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        aggregated_peak_traffic_dict[key] = value.get("aggregated_peak_traffic_mbps", "")

                    # for connectivity status and error
                    for item in res.get("connectivity", {}).get("sensors", {}):
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function from connectivity status.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        connectivity_dict[item.get("name", "")] = {
                            "status": item.get("status", ""),
                            "error": item.get("error", ""),
                        }

                    # for traffic_drop status and error
                    for item in res.get("trafficdrop", {}).get("sensors", {}):
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function from traffic drop.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        trafficdrop_dict[item.get("name", "")] = {
                            "status": item.get("status", ""),
                            "error": item.get("error", ""),
                        }

                    for i in range(len(res.get("sensors", {}))):
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function from sensors.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        # adding d_link_status
                        res["sensors"][i]["d_link_status"] = link_status_dict.get(
                            res.get("sensors", {})[i].get("luid", ""), ""
                        )
                        # adding d_aggregated_peak_traffic
                        res["sensors"][i]["d_aggregated_peak_traffic"] = aggregated_peak_traffic_dict.get(
                            res.get("sensors", {})[i].get("name", ""), ""
                        )
                        # adding d_connectivity_status
                        res["sensors"][i]["d_connectivity_status"] = connectivity_dict.get(
                            res.get("sensors", {})[i].get("name", ""), {}
                        ).get("status", "")
                        # adding d_connectivity_error
                        res["sensors"][i]["d_connectivity_error"] = connectivity_dict.get(
                            res.get("sensors", {})[i].get("name", ""), {}
                        ).get("error", "")
                        # adding d_trafficdrop_status
                        res["sensors"][i]["d_trafficdrop_status"] = trafficdrop_dict.get(
                            res.get("sensors", {})[i].get("name", ""), {}
                        ).get("status", "")
                        # adding d_trafficdrop_error
                        res["sensors"][i]["d_trafficdrop_error"] = trafficdrop_dict.get(
                            res.get("sensors", {})[i].get("name", ""), {}
                        ).get("error", "")

                    list_res = [res]
                    self.post_data_to_sentinel(list_res, table_name, fields)
                    posted_event_count += 1
                else:
                    for event in res:
                        event["entity_type"] = event.get("type", "")
                        if (
                            int(time.time())
                            >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                        ):
                            applogger.info(
                                "{}(method={}) : 9:30 mins executed hence terminating the function.".format(
                                    consts.LOGS_STARTS_WITH, __method_name
                                )
                            )
                            break
                        temp_dict = {}
                        for field in hash_field_list:
                            temp_dict[field] = event.get(field)
                        hash_of_event = self.get_results_hash(temp_dict)
                        if hash_of_event not in hashed_events_list:
                            self.post_data_to_sentinel(event, table_name, fields)
                            posted_event_count += 1
                            hashed_events_list.append(hash_of_event)
                            self.save_checkpoint_snapshot(hashed_events_list)

            applogger.info(
                "{}(method={}) : {} : Posted total {} event(s) into MS Sentinel. No more events."
                " Stopping the collection.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    posted_event_count,
                )
            )
        except VectraException:
            raise VectraException()
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            self.update_checkpoint_of_disabling_function()
            raise VectraException()

    def get_results_hash(self, data):
        """Generate hash digest.

        :data: Data to be hashed.
        :return: SHA512 hexdigest of data.
        """
        data = json.dumps(data, sort_keys=True)
        result = hashlib.sha512(data.encode())
        result_hash = result.hexdigest()
        return result_hash

    def get_checkpoint_snapshot(self):
        """Fetch snapshot hash from checkpoint file.

        Returns:
            List: hash_list
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            checkpoint = self.state.get()
            if checkpoint:
                checkpoint = json.loads(checkpoint)
                checkpoint = checkpoint.get("snapshot")
                applogger.info(
                    "{}(method={}) : {} : Checkpoint list fetched successfully. checkpoint={}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        checkpoint,
                    )
                )
            else:
                checkpoint = []
                self.state.post(json.dumps({"snapshot": checkpoint}))
                applogger.info(
                    "{}(method={}) : {} : Checkpoint list not found. Created new checkpoint list.".format(
                        consts.LOGS_STARTS_WITH, __method_name, self.function_name
                    )
                )
            return checkpoint
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : Unexpected error while getting checkpoint list: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException()

    def save_checkpoint_snapshot(self, value):
        """Post checkpoint snapshot into sentinel."""
        try:
            __method_name = inspect.currentframe().f_code.co_name
            checkpoint_data = self.state.get()
            checkpoint_data_json = {}
            if checkpoint_data:
                checkpoint_data_json = json.loads(checkpoint_data)
            checkpoint_data_json.update({"snapshot": value})
            self.state.post(json.dumps(checkpoint_data_json))
            applogger.info(
                "{}(method={}) : {} : successfully saved checkpoint.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name
                )
            )
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.exception(
                '{}(method={}) : {} : Unexpected error while saving checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException()

    def get_entities_checkpoint(self, entity_state):
        """Fetch last data from checkpoint file for entities.

        Args:
            entity_state (object): State manager object

        Returns:
            tuple : last_modified_timestamp, page
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "{}(method={}) : {} : Fetching last data from checkpoint file.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name
                )
            )
            checkpoint = entity_state.get()
            if checkpoint:
                checkpoint = json.loads(checkpoint)
                if checkpoint.get("last_modified_timestamp", None):
                    last_modified_timestamp = checkpoint.get("last_modified_timestamp")
                    page = checkpoint.get("page", 1)
                    applogger.info(
                        '{}(method={}) : {} : Checkpoint last_modified_timestamp="{}", page="{}'.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            last_modified_timestamp,
                            page,
                        )
                    )
                    return last_modified_timestamp, page
            return None, 1
        except VectraException:
            raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : Unexpected error while getting checkpoint: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException()

    def pull_and_push_entities_data(
        self,
        endpoint,
        last_modified_timestamp,
        page,
        table_name,
        entity_type,
        entity_state,
        fields=None,
    ):
        """
        To pull the entities data from vectra and push into sentinel.

        Args:
            endpoint (str): endpoint url
            checkpoint_value (str): Checkpoint value from checkpoint file
            table_name (str): Table name to ingest data into sentinel
            entity_type (str): Type of the entity (host/account)
            entity_state (object): State manager object
            fields (list): list of fields
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "{}(method={}) : {} Pull and Push entities data".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name
                )
            )
            posted_entities_count = 0
            page = page if page else 1
            store_page = page
            params = {
                "page_size": consts.PAGE_SIZE,
                "ordering": "last_modified_timestamp",
                "type": entity_type,
            }

            if last_modified_timestamp:
                params.update({"last_modified_timestamp_gte": last_modified_timestamp})
            while True:
                if (
                    int(time.time())
                    >= self.execution_start_time + consts.MAX_EXECUTION_TIME
                ):
                    applogger.info(
                        "{}(method={}) : 9:30 mins executed hence terminating the function.".format(
                            consts.LOGS_STARTS_WITH, __method_name
                        )
                    )
                    break
                params["page"] = page
                applogger.info(
                    "{}(method={}) : {} : Trying to collect information from"
                    " /entities endpoint using params = {}.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.function_name,
                        params,
                    )
                )
                res = self.pull_data(endpoint, params=params)
                entity_response = res.get("results", [])
                next_link = res.get("next", None)
                if len(entity_response):
                    last_modified_timestamp_from_response = entity_response[-1].get(
                        "last_modified_timestamp"
                    )
                    first_modified_timestamp_from_response = entity_response[0].get(
                        "last_modified_timestamp"
                    )
                    for event in entity_response:
                        event["entity_type"] = event.get("type", "")
                    self._create_chunks_and_post_to_sentinel(
                        entity_response,
                        table_name,
                        fields,
                        entity_state,
                        entities_endpoint=True,
                    )
                    entity_response_count = len(entity_response)
                    posted_entities_count += entity_response_count
                    applogger.info(
                        "{}(method={}) : {} : Posted Entities Count : {}".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.function_name,
                            posted_entities_count,
                        )
                    )
                    checkpoint_data_to_store = {}
                    page += 1
                    if last_modified_timestamp_from_response == last_modified_timestamp:
                        store_page += 1
                        checkpoint_data_to_store = {
                            "last_modified_timestamp": last_modified_timestamp_from_response
                        }
                        checkpoint_data_to_store["page"] = store_page
                    elif (last_modified_timestamp is None) and (
                        first_modified_timestamp_from_response
                        == last_modified_timestamp_from_response
                    ):
                        store_page = 2
                        checkpoint_data_to_store = {
                            "last_modified_timestamp": last_modified_timestamp_from_response,
                            "page": store_page,
                        }
                        last_modified_timestamp = last_modified_timestamp_from_response
                    else:
                        store_page = 1
                        checkpoint_data_to_store = {
                            "last_modified_timestamp": last_modified_timestamp_from_response,
                            "page": store_page,
                        }
                        last_modified_timestamp = last_modified_timestamp_from_response

                    if not next_link:
                        checkpoint_data_to_store = {
                            "last_modified_timestamp": (
                                datetime.datetime.strptime(
                                    last_modified_timestamp_from_response,
                                    "%Y-%m-%dT%H:%M:%SZ",
                                )
                                + timedelta(seconds=1)
                            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "page": 1,
                        }
                    self.save_checkpoint(
                        data=checkpoint_data_to_store,
                        entity_state=entity_state,
                        entities_endpoint=True,
                    )
                if not next_link:
                    break
        except VectraException:
            raise VectraException()
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            self.update_checkpoint_of_disabling_function()
            raise VectraException()
        except Exception as ex:
            applogger.error(
                '{}(method={}) : {} : Unexpected error while getting or posting entities data: err="{}"'.format(
                    consts.LOGS_STARTS_WITH, __method_name, self.function_name, str(ex)
                )
            )
            raise VectraException()
