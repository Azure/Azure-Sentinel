"""Module with BitSight class for interacting with BitSight APIs and posting data to Sentinel."""
import base64
import inspect
import requests
import time

from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from .bitsight_exception import BitSightException, BitSightTimeOutException
from .utils import CheckpointManager
from .consts import *
from .logger import applogger


class BitSight:
    """Class for handling BitSight API interactions."""

    def __init__(self, start_time) -> None:
        """Initialize BitSight object."""
        self.start_time = start_time
        self.headers = None
        self.base_url = BASE_URL
        self.api_token = API_TOKEN
        self.logs_starts_with = LOGS_STARTS_WITH
        self.error_logs = "{}(method={}) {}"
        self.messages = {
            403: "You cannot view this company as company might be removed from your portfolio.",
            429: "You have reached your BitSight API rate limit. Please try again later.",
        }

    def check_environment_var_exist(self, environment_var):
        """Check if required environment variables are set.

        Args:
            environment_var (list): List of dictionaries containing environment variable names and values.

        Returns:
            bool: True if all environment variables are set, False otherwise.
        """
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
                "X-BITSIGHT-CALLING-PLATFORM-VERSION": "Microsoft-Sentinel",
                "X-BITSIGHT-CONNECTOR-NAME-VERSION": "3.0.2"
            }
            headers["Authorization"] = "Basic %s" % user_and_pass
            self.headers = headers
            applogger.info(
                "BitSight: Successfully generated the authentication header."
            )
        except Exception as error:
            applogger.exception("BitSight: GENERATE AUTH TOKEN: {}".format(error))
            raise BitSightException()

    def check_timeout(self):
        """Check if the function has timed out.

        Raises:
            BitSightTimeOutException: Raises exception if the function has timed out.
        """
        if int(time.time()) >= self.start_time + FUNCTION_APP_TIMEOUT_SECONDS:
            raise BitSightTimeOutException()
    
    def get_last_data_index(
        self, company_names, checkpoint_obj: CheckpointManager
    ):
        """Get the index for fetching last data.

        Args:
            company_names (list): List of company names.
            checkpoint_obj (CheckpointManager): CheckpointManager object.

        Returns:
            int: Index for fetching last data.
        """
        last_company_name = checkpoint_obj.get_checkpoint(
            partition_key=COMPANY_CHECKPOINT_PARTITION_KEY,
            row_key=COMPANY_CHECKPOINT_ROW_KEY
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
        for _ in range(RETRY_COUNT):
            try:
                self.check_timeout()
                resp = requests.get(url=url, headers=self.headers, params=query_parameter)
                if resp.status_code == 403:
                    applogger.info(
                        "BitSight: get_bitsight_data: {} url={}".format(
                            self.messages.get(resp.status_code, ""), url
                        )
                    )
                    return None
                elif resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", RETRY_AFTER)) + 1
                    if int(time.time()) + retry_after >= self.start_time + FUNCTION_APP_TIMEOUT_SECONDS:
                        raise BitSightTimeOutException()
                    applogger.info(
                        "BitSight: get_bitsight_data: {} url={}, Retrying after {} seconds".format(
                            self.messages.get(resp.status_code, ""), url, retry_after
                        )
                    )
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                response = resp.json()
                applogger.debug(
                    "BitSight: get_bitsight_data: Successfully got response for url: {}".format(
                        url
                    )
                )
                return response
            except BitSightTimeOutException:
                raise BitSightTimeOutException()
            except requests.exceptions.Timeout as err:
                applogger.exception("BitSight: Request Timeout for {}: {}".format(url, err))
                raise BitSightException()
            except requests.exceptions.ConnectionError as err:
                retry_after = RETRY_AFTER + 1
                if int(time.time()) + retry_after >= self.start_time + FUNCTION_APP_TIMEOUT_SECONDS:
                        raise BitSightTimeOutException()
                applogger.error(
                    "{}, Retrying after {} seconds".format(
                        self.error_logs.format(self.logs_starts_with, __method_name, err), retry_after
                    )
                )
                time.sleep(retry_after)
                continue
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
        applogger.error(
                    "BitSight: GET BITSIGHT DATA FOR {}: {}, Retry count exceeded".format(url, err)
                )
        raise BitSightException()

    def send_data_to_sentinel(self, data, data_table, company_name=None, endpoint=None):
        """
        Post data to Azure Sentinel via the ingestion API.

        Args:
            data (dict or list): Data to be ingested into Sentinel.
            data_table (str): Log type/table name for ingestion.
            company_name (str, optional): Name of the company for logging context. Defaults to None.
            endpoint (str, optional): Endpoint name for logging context. Defaults to None.

        Raises:
            BitSightException: For any error during data upload to Sentinel.
        """
        try:
            # Determine appropriate Azure credentials
            if ".us" in SCOPE:
                creds = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)      # CodeQL [SM05139] CCF based data connector is in development. This will be retired once that data connector is GA.
            else:
                creds = DefaultAzureCredential()                                                    # CodeQL [SM05139] CCF based data connector is in development. This will be retired once that data connector is GA.

            azure_client = LogsIngestionClient(
                AZURE_DATA_COLLECTION_ENDPOINT,
                credential=creds,
                credential_scopes=[SCOPE]
            )

            # Ensure data is a list for ingestion
            if not isinstance(data, list):
                data = [data] if isinstance(data, dict) else list(data)

            dcr_stream = f"Custom-{data_table}"
            azure_client.upload(rule_id=TABLE_NAME_RULE_ID_MAPPING.get(data_table), stream_name=dcr_stream, logs=data)

        except ClientAuthenticationError as error:
            if company_name is None:
                applogger.error(
                    "BitSight: Authentication error while uploading data to Sentinel. "
                    f"Error: {error}"
                )
            else:
                applogger.error(
                    "BitSight: Authentication error while uploading data to Sentinel. "
                    f"Endpoint: {endpoint}, Company: {company_name}. Error: {error}"
                )
            raise BitSightException(
                f"Authentication error while uploading data to Sentinel: {error}"
            )
        except HttpResponseError as error:
            if company_name is None:
                applogger.error(
                    "BitSight: HTTP response error while uploading data to Sentinel. "
                    f"Error: {error}"
                )
            else:
                applogger.error(
                    "BitSight: HTTP response error while uploading data to Sentinel. "
                    f"Endpoint: {endpoint}, Company: {company_name}. Error: {error}"
                )
            raise BitSightException(
                f"HTTP response error while uploading data to Sentinel: {error}"
            )
        except Exception as error:
            if company_name is None:
                applogger.error(
                    "BitSight: Unexpected error while uploading data to Sentinel. "
                    f"Error: {error}"
                )
            else:
                applogger.error(
                    "BitSight: Unexpected error while uploading data to Sentinel. "
                    f"Endpoint: {endpoint}, Company: {company_name}. Error: {error}"
                )
            raise BitSightException(
                f"Unexpected error while uploading data to Sentinel: {error}"
            )
