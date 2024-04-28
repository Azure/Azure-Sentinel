"""Module with BitSight class for interacting with BitSight APIs and posting data to Sentinel."""
import base64
import inspect
import json

import requests

from ..SharedCode.azure_sentinel import MicrosoftSentinel
from .bitsight_exception import BitSightException
from .utils import CheckpointManager
from .consts import API_TOKEN, BASE_URL, LOGS_STARTS_WITH
from .logger import applogger


class BitSight:
    """Class for handling BitSight API interactions."""

    def __init__(self) -> None:
        """Initialize BitSight object."""
        self.headers = None
        self.base_url = BASE_URL
        self.api_token = API_TOKEN
        self.logs_starts_with = LOGS_STARTS_WITH
        self.error_logs = "{}(method={}) {}"
        self.azuresentinel = MicrosoftSentinel()
        self.messages = {
            403: "You cannot view this company as company might be removed from your portfolio."
        }

    def check_environment_var_exist(self, environment_var):
        """Check if required environment variables are set.

        Args:
            environment_var (list): List of dictionaries containing environment variable names and values.

        Returns:
            bool: True if all environment variables are set, False otherwise.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.debug(
                "BitSight: check_environment_var_exist: started checking existence of all custom environment variable"
            )
            for i in environment_var:
                key, val = next(iter(i.items()))
                if val is None:
                    applogger.error(
                        "BitSight: ENVIRONMENT VARIABLE: {} is not set in the environment.".format(
                            key
                        )
                    )
                    return False
            applogger.debug(
                "BitSight: check_environment_var_exist: All custom environment variable is exist."
            )
            return True
        except BitSightException as error:
            applogger.exception(error)
            raise BitSightException()
        except Exception as error:
            applogger.exception("BitSight: ENVIRONMENT VARIABLE {}".format(error))
            raise BitSightException()

    def generate_auth_token(self):
        """Generate authentication token."""
        try:
            applogger.info(
                "BitSight: Started generating auth header to authenticate BitSight APIs."
            )
            api = [self.api_token, self.api_token]
            connector = ":"
            api = connector.join(api)
            user_and_pass = base64.b64encode(api.encode()).decode("ascii")
            headers = {
                "Accept": "application/json",
                "X-BITSIGHT-CONNECTOR-NAME-VERSION": "BitSight Security Performance Management for Microsoft Sentinel Data Connector 1.0.0",
                "X-BITSIGHT-CALLING-PLATFORM-VERSION": "Microsoft-Sentinel",
            }
            headers["Authorization"] = "Basic %s" % user_and_pass
            self.headers = headers
            applogger.info(
                "BitSight: Successfully generated the authentication header."
            )
        except Exception as error:
            applogger.exception("BitSight: GENERATE AUTH TOKEN: {}".format(error))
            raise BitSightException()

    def get_last_data_index(
        self, company_names, checkpoint_obj: CheckpointManager, company_state
    ):
        """Get the index for fetching last data.

        Args:
            company_names (list): List of company names.
            checkpoint_obj (CheckpointManager): CheckpointManager object.
            company_state (str): State of the company.

        Returns:
            int: Index for fetching last data.
        """
        last_company_name = checkpoint_obj.get_last_data(
            company_state, company_name_flag=True
        )
        fetching_index = -1
        if last_company_name is not None:
            if last_company_name != company_names[-1]:
                fetching_index = company_names.index(last_company_name)
                applogger.debug(
                    "{} Started data fetching from index {}.".format(
                        self.logs_starts_with, fetching_index + 1
                    )
                )
            else:
                applogger.debug(
                    "{} Fetching should start from first index.".format(
                        self.logs_starts_with
                    )
                )
        return fetching_index

    def get_specified_companies_list(self, company_names, companies_str):
        """Get the list of specified companies.

        Args:
            company_names (list): List of company names.
            companies_str (str): String containing specified companies.

        Returns:
            list: List of specified companies.
        """
        company_list_set = set(map(str.strip, map(str.lower, companies_str.split("*"))))
        company_names_set = set(map(str.lower, company_names))
        companies_to_get = list(company_names_set.intersection(company_list_set))
        return companies_to_get

    def get_bitsight_data(self, url, query_parameter=None):
        """Fetch data from BitSight APIs.

        Args:
            url (str): URL of the API endpoint.
            query_parameter (json, optional): Query parameters for the API. Defaults to None.

        Returns:
            json: Response of the API.

        Raises:
            BitSightException: Raised if an error occurs during the API request.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            resp = requests.get(url=url, headers=self.headers, params=query_parameter)
            if resp.status_code == 403:
                applogger.info("BitSight: get_bitsight_data: {} url={}".format(self.messages.get(resp.status_code, ""), url))
                return None
            resp.raise_for_status()
            response = resp.json()
            applogger.debug(
                "BitSight: get_bitsight_data: Successfully got response for url: {}".format(
                    url
                )
            )
            return response
        except requests.exceptions.Timeout as err:
            applogger.exception("BitSight: Request Timeout for {}: {}".format(url, err))
            raise BitSightException()
        except requests.ConnectionError as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException()
        except requests.HTTPError as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException()
        except requests.RequestException as err:
            applogger.error(
                self.error_logs.format(self.logs_starts_with, __method_name, err)
            )
            raise BitSightException()
        except Exception as err:
            applogger.exception(
                "BitSight: GET BITSIGHT DATA FOR {}: {}".format(url, err)
            )
            raise BitSightException()

    def send_data_to_sentinel(self, data, data_table, company_name, endpoint):
        """To post the data into sentinel.

        Args:
            data (dict): data to post in sentinel
            data_table (str): log type
            company_name (str): company name
        """
        try:
            body = json.dumps(data, sort_keys=True)
            post_data_status_code = self.azuresentinel.post_data(body, data_table)
            if post_data_status_code >= 200 and post_data_status_code <= 299:
                applogger.info(
                    "BitSight: [status code {}] Successfully posted the {} of {} company.".format(
                        post_data_status_code, endpoint, company_name
                    )
                )
            else:
                applogger.error(
                    "BitSight: [status code {}] The {} of {} company is not posted".format(
                        post_data_status_code, endpoint, company_name
                    )
                )
                raise BitSightException()
        except BitSightException:
            raise BitSightException()
        except Exception as err:
            applogger.exception("BitSight: SEND DATA TO SENTINEL: {}".format(err))
            raise BitSightException()
