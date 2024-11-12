"""Utils File."""

import inspect
import requests
import json
from json.decoder import JSONDecodeError
import hashlib
from .state_manager import StateManager
from .mimecast_exception import MimecastException
from .logger import applogger
from . import consts
from ..SharedCode.sentinel import post_data
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
import datetime


def retry_on_status_code(response):
    """Check and retry based on a list of status codes.

    Args:
        response (): API response is passed

    Returns:
        Bool: if given status code is in list then true else false
    """
    __method_name = inspect.currentframe().f_code.co_name
    if isinstance(response, dict):
        return False
    if response.status_code in consts.RETRY_STATUS_CODE:
        applogger.info(
            "{}(method={}) : Retrying due to status code : {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                response.status_code,
            )
        )
        return True
    return False


class Utils:
    """Utils Class."""

    def __init__(self, azure_function_name) -> None:
        """Init Function."""
        self.azure_function_name = azure_function_name
        self.log_format = consts.LOG_FORMAT
        self.headers = {}
        self.first_page = True

    def check_environment_var_exist(self, environment_var):
        """Check the existence of required environment variables.

        Logs the validation process and completion. Raises MimecastException if any required field is missing.

        Args:
            environment_var(list) : variables to check for existence
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Validating Environment Variables.",
                )
            )
            missing_required_field = False
            for var in environment_var:
                key, val = next(iter(var.items()))
                if not val:
                    missing_required_field = True
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Environment variable {} is not set.".format(key),
                        )
                    )
            if missing_required_field:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Validation failed.",
                    )
                )
                raise MimecastException()
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Validation Complete.",
                )
            )
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def get_checkpoint_data(self, checkpoint_obj: StateManager, load_flag=True):
        """Get checkpoint data from a StateManager object.

        Args:
            checkpoint_obj (StateManager): The StateManager object to retrieve checkpoint data from.
            load_flag (bool): A flag indicating whether to load the data as JSON (default is True).

        Returns:
            The retrieved checkpoint data.

        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Fetching checkpoint data.",
                )
            )
            checkpoint_data = checkpoint_obj.get()
            if load_flag and checkpoint_data:
                checkpoint_data = json.loads(checkpoint_data)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint data fetched.",
                )
            )
            return checkpoint_data
        except json.decoder.JSONDecodeError as json_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.JSON_DECODE_ERROR_MSG.format(json_error),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def post_checkpoint_data(self, checkpoint_obj: StateManager, data, dump_flag=True):
        """Post checkpoint data.

        It post the data to a checkpoint object based on the dump_flag parameter.

        Args:
            checkpoint_obj (StateManager): The StateManager object to post data to.
            data: The data to be posted.
            dump_flag (bool): A flag indicating whether to dump the data as JSON before posting (default is True).
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if dump_flag:
                checkpoint_obj.post(json.dumps(data))
            else:
                checkpoint_obj.post(data)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint posted to azure storage.",
                )
            )
        except TypeError as type_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TYPE_ERROR_MSG.format(type_error),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

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
            "{}(method = {})  : Retrying after {} seconds, attempt number : {} ".format(
                consts.LOGS_STARTS_WITH,
                " Retry Decorator",
                retry_state.upcoming_sleep,
                retry_state.attempt_number,
            )
        ),
    )
    def make_rest_call(
        self, method, url, params=None, data=None, json=None, check_retry=True
    ):
        """Make a rest call.

        Args:
            url (str): The URL to make the call to.
            method (str): The HTTP method to use for the call.
            params (dict, optional): The parameters to pass in the call (default is None).
            data (dict, optional): The body(in x-www-form-urlencoded formate) of the request (default is None).
            json (dict, optional): The body(in row formate) of the request (default is None).
            check_retry (bool, optional): A flag indicating whether to check for retry (default is True).

        Returns:
            dict: The JSON response if the call is successful.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Rest Call, Method :{}, url: {}".format(method, url),
                )
            )

            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                data=data,
                json=json,
                timeout=consts.MAX_TIMEOUT_SENTINEL,
            )
            if response.status_code >= 200 and response.status_code <= 299:
                response_json = response.json()
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Success, Status code : {}".format(response.status_code),
                    )
                )
                self.handle_failed_response_for_success(response_json)
                return response_json
            elif response.status_code == 400:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Bad Request = {}, Status code : {}".format(
                            response.text, response.status_code
                        ),
                    )
                )
                self.handle_failed_response_for_failure(response)
            elif response.status_code == 401:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Unauthorized, Status code : {}".format(response.status_code),
                    )
                )
                response_json = response.json()
                fail_json = response_json.get("fail", [])
                error_code = None
                error_message = None
                if fail_json:
                    error_code = fail_json[0].get("code")
                    error_message = fail_json[0].get("message")
                if check_retry:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Generating new token, Error message = {}, Error code = {}".format(
                                error_message, error_code
                            ),
                        )
                    )
                    check_retry = False
                    self.authenticate_mimecast_api(check_retry)
                    return self.make_rest_call(
                        method, url=url, json=json, check_retry=check_retry
                    )
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Max retry reached for generating access token,"
                            "Error message = {}, Error code = {}".format(
                                error_message, error_code
                            ),
                        )
                    )
                    raise MimecastException()
            elif response.status_code == 403:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Forbidden, Status code : {}".format(response.status_code),
                    )
                )
                self.handle_failed_response_for_failure(response)
            elif response.status_code == 404:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Not Found, URL : {}, Status code : {}".format(
                            url, response.status_code
                        ),
                    )
                )
                raise MimecastException()
            elif response.status_code == 409:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Conflict, Status code : {}".format(response.status_code),
                    )
                )
                self.handle_failed_response_for_failure(response)
            elif response.status_code == 429:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Too Many Requests, Status code : {} ".format(
                            response.status_code
                        ),
                    )
                )
                return response
            elif response.status_code == 500:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Internal Server Error, Status code : {}".format(
                            response.status_code
                        ),
                    )
                )
                return self.handle_failed_response_for_failure(response)
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Unexpected Error = {}, Status code : {}".format(
                        response.text, response.status_code
                    ),
                )
            )
            raise MimecastException()

        except MimecastException:
            raise MimecastException()
        except requests.exceptions.Timeout as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TIME_OUT_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()
        except JSONDecodeError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.JSON_DECODE_ERROR_MSG.format(
                        "{}, API Response = {}".format(error, response.text)
                    ),
                )
            )
            raise MimecastException()
        except requests.ConnectionError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.CONNECTION_ERROR_MSG.format(error),
                )
            )
            raise ConnectionError()
        except requests.RequestException as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.REQUEST_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def handle_failed_response_for_failure(self, response):
        """Handle the failed response for failure status codes.

        If request get authentication error it will regenerate the access token.

        Args:
            response_json (dict): The JSON response from the API.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            response_json = response.json()
            error_message = response_json
            fail_json = response_json.get("fail", [])
            error_json = response_json.get("error")
            if fail_json:
                error_message = fail_json[0].get("message")
            elif error_json:
                error_message = error_json.get("message")
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error_message,
                )
            )
            if response.status_code in consts.EXCEPTION_STATUS_CODE:
                raise MimecastException()

            return response
        except MimecastException:
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def handle_failed_response_for_success(self, response_json):
        """Handle the failed response for a successful request.

        Check if there is failure in success response or not.

        Args:
            response_json (dict): The JSON response from the request.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            fail_json = response_json.get("fail", [])
            if fail_json:
                try:
                    error_message = fail_json[0].get("errors")[0].get("message")
                except (KeyError, IndexError, ValueError, TypeError):
                    error_message = fail_json
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Failed response message = {}.".format(error_message),
                    )
                )
                raise MimecastException()
            else:
                applogger.debug(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "No failed response found.",
                    )
                )
                return
        except MimecastException:
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def authenticate_mimecast_api(self, check_retry=True):
        """Authenticate mimecast endpoint generate access token and update header.

        Args:
            check_retry (bool):  Flag for retry of generating access token.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = {
                "client_id": consts.MIMECAST_CLIENT_ID,
                "client_secret": consts.MIMECAST_CLIENT_SECRET,
                "grant_type": "client_credentials",
            }
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Generating access token.",
                )
            )
            self.headers = {}
            url = "{}{}".format(consts.BASE_URL, consts.ENDPOINTS["OAUTH2"])
            response = self.make_rest_call(
                method="POST", url=url, data=body, check_retry=check_retry
            )
            if "access_token" in response:
                access_token = response.get("access_token")
                self.headers.update(
                    {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer {}".format(access_token),
                    }
                )
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Successfully generated access token and header updated.",
                    )
                )
                return
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Error occurred while fetching the access token from the response = {}.".format(
                        response
                    ),
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except RetryError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.MAX_RETRY_ERROR_MSG.format(
                        error, error.last_attempt.exception()
                    ),
                )
            )
            raise MimecastException()
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def convert_to_hash(self, data_to_hash):
        """Convert json data records to hash.

        Args:
            data_to_hash (list): list of data to hash

        Returns:
            list: hashed data list
        """
        __method_name = inspect.currentframe().f_code.co_name
        hashed_data = []
        for record in data_to_hash:
            try:
                json_string = json.dumps(record)
                res_hash = hashlib.sha256(
                    json_string.encode("utf-8", errors="replace")
                ).hexdigest()
                hashed_data.append(res_hash)
            except TypeError as err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        consts.TYPE_ERROR_MSG.format(err),
                    )
                )
                continue
            except ValueError as err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        consts.VALUE_ERROR_MSG.format(err),
                    )
                )
                continue
            except Exception as err:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        consts.UNEXPECTED_ERROR_MSG.format(err),
                    )
                )
                continue
        return hashed_data

    def compare_data_with_checkpoint(self, data_to_compare, state_manager_obj):
        """Compare data with checkpoint hash and return unique records.

        Args:
            data_to_compare (list): list of data to compare
            state_manager_obj (Statemanager): statemanager object to get checkpoint hash data

        Returns:
            list: list of unique data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            hashed_data = self.convert_to_hash(data_to_compare)
            checkpoint_hash_list = self.get_checkpoint_data(state_manager_obj, True)
            if checkpoint_hash_list:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Found hashed data checkpoint.",
                    )
                )
                hash_record = {
                    hashed_data[i]: record for i, record in enumerate(data_to_compare)
                }
                unique_hashes = set(hashed_data) - set(checkpoint_hash_list)
                unique_data = [hash_record[hash] for hash in unique_hashes]
                return unique_data
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Hashed data checkpoint not found.",
                )
            )
            return data_to_compare
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def filter_unique_data_and_post(
        self,
        data_to_post,
        hash_file_state_manager_obj,
        table_name,
        checkpoint_data,
        checkpoint_obj,
        next_page_token_flag,
    ):
        """Filter unique data from the given data and post it to Azure Sentinel Log Analytics.

        Args:
            data_to_post (list): The data to be posted to azure Sentinel log analytics.
            hash_file_state_manager_obj (StateManager): The StateManager object to retrieve hash checkpoint data.
            table_name (str): The custom log table name in which data will be added.
            checkpoint_data (dict): The checkpoint data to be updated.
            checkpoint_obj (StateManager): The StateManager object to post checkpoint data to.
            next_page_token_flag (bool): A flag indicating whether a next page token is present.

        Returns:
            bool: True if checkpoint data is deleted, otherwise False.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if self.first_page:
                data_to_post = self.compare_data_with_checkpoint(
                    data_to_post, hash_file_state_manager_obj
                )
                self.first_page = False
            if len(data_to_post) > 0:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Posting data to azure Sentinel log analytics, data count : {}.".format(
                            len(data_to_post)
                        ),
                    )
                )
                post_data(json.dumps(data_to_post), log_type=table_name)
                if not next_page_token_flag:
                    if checkpoint_data:
                        applogger.info(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "New data found in same last page, so resetting checkpoint",
                            )
                        )
                        checkpoint_data.update(
                            {"date": datetime.datetime.utcnow().isoformat()}
                        )
                    else:
                        checkpoint_data = {
                            "date": datetime.datetime.utcnow().isoformat()
                        }
                    self.post_checkpoint_data(checkpoint_obj, checkpoint_data)
                return False
            else:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Data already posted to sentinel, no new data found.",
                    )
                )
                return self.compare_last_pagetoken_time(
                    checkpoint_data, checkpoint_obj, hash_file_state_manager_obj
                )

        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def compare_last_pagetoken_time(
        self, checkpoint_data, checkpoint_obj, hash_file_state_manager_obj
    ):
        """Compare last page token time with current time.

        Args:
            checkpoint_data (dict): checkpoint data
            checkpoint_obj (StateManager): The StateManager object to post checkpoint data to.
            hash_file_state_manager_obj (StateManager): The StateManager object to retrieve hash checkpoint data.

        Returns:
            checkpoint_data (dict): checkpoint data
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if checkpoint_data:
                last_page_token_time = checkpoint_data.get("date")
                if (
                    last_page_token_time
                    and datetime.datetime.utcnow()
                    - datetime.datetime.fromisoformat(last_page_token_time)
                    >= datetime.timedelta(hours=consts.CHECKPOINT_RESET_TIME)
                ):
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Last date time more than 12 hours old, so resetting checkpoints",
                        )
                    )
                    checkpoint_data = {}
                    self.post_checkpoint_data(checkpoint_obj, checkpoint_data)
                    self.post_checkpoint_data(
                        hash_file_state_manager_obj, checkpoint_data
                    )
                    return True
            return False
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()
