"""This file contains helper methods."""
import inspect
import requests
from .cofense_intelligence_exception import CofenseIntelligenceException
from .logger import applogger
from ..SharedCode import consts
import time
from requests.compat import quote_plus
from cryptography.fernet import Fernet


class Utils:
    """This class contains helper methods."""

    key = Fernet.generate_key()
    f = Fernet(key)

    def __init__(self, azure_function_name) -> None:
        """Initialize instance variable for class.

        Args:
            azure_function_name (String): Azure function name
        """
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Cofense Intelligence"
        self.azure_function_name = azure_function_name
        self.auth = (consts.COFENSE_USERNAME, consts.COFENSE_PASSWORD)

    def create_proxy(self):
        """To create proxy.

        Raises:
            CofenseIntelligenceException: custom cofense exception

        Returns:
            dict: proxies
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            proxies = None
            if consts.IS_PROXY_REQUIRED == "Yes":
                if consts.PROXY_URL and consts.PROXY_PORT:
                    if consts.PROXY_USERNAME and consts.PROXY_PASSWORD:
                        proxy_url = "{}://{}:{}@{}:{}".format(
                            consts.PROXY_REQUEST,
                            quote_plus(consts.PROXY_USERNAME),
                            quote_plus(consts.PROXY_PASSWORD),
                            consts.PROXY_URL,
                            consts.PROXY_PORT,
                        )
                        proxies = {"http": proxy_url, "https": proxy_url}
                        applogger.info(
                            "{}(method={}) : {} : Proxy created successfully and the integration"
                            " uses proxy for further execution.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.COFENSE_TO_SENTINEL,
                            )
                        )
                    elif consts.PROXY_USERNAME or consts.PROXY_PASSWORD:
                        applogger.error(
                            "{}(method={}) : {} : Proxy username or password is missing.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                            )
                        )
                        raise CofenseIntelligenceException()
                    else:
                        proxy_url = "{}://{}:{}".format(
                            consts.PROXY_REQUEST,
                            consts.PROXY_URL,
                            consts.PROXY_PORT,
                        )
                        proxies = {"http": proxy_url, "https": proxy_url}
                        applogger.info(
                            "{}(method={}) : {} : Proxy created successfully and the integration"
                            " uses proxy for further execution.".format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                consts.COFENSE_TO_SENTINEL,
                            )
                        )
                else:
                    applogger.error(
                        "{}(method={}) : {} : Proxy Url or Port is missing.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                        )
                    )
                    raise CofenseIntelligenceException()
            else:
                applogger.info(
                    "{}(method={}) : {} : Proxy not required. Execution gets started without using proxy.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.COFENSE_TO_SENTINEL,
                    )
                )
            return proxies
        except CofenseIntelligenceException:
            raise CofenseIntelligenceException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Error while creating proxy :{}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    def validate_params(self):
        """To validate parameters of function app."""
        __method_name = inspect.currentframe().f_code.co_name
        required_params = {
            "BaseURL": consts.COFENSE_BASE_URL,
            "AzureClientId": consts.AZURE_CLIENT_ID,
            "AzureClientSecret": "" if consts.AZURE_CLIENT_SECRET is None or consts.AZURE_CLIENT_SECRET == "" else self.f.encrypt(bytes(consts.AZURE_CLIENT_SECRET, 'utf-8')),
            "AzureTenantId": consts.AZURE_TENANT_ID,
            "AzureResourceGroup": consts.AZURE_RESOURCE_GROUP,
            "AzureWorkspaceName": consts.AZURE_WORKSPACE_NAME,
            "AzureSubscriptionId": consts.AZURE_SUBSCRIPTION_ID,
            "ConnectionString": consts.CONNECTION_STRING,
            "Schedule": consts.SCHEDULE,
            "Cofense_username": consts.COFENSE_USERNAME,
            "Cofense_password": "" if consts.COFENSE_PASSWORD is None or consts.COFENSE_PASSWORD == "" else self.f.encrypt(bytes(consts.COFENSE_PASSWORD, 'utf-8')),
            "LogLevel": consts.LOG_LEVEL,
            "WorkspaceID": consts.WORKSPACE_ID,
            "WorkspaceKey": consts.WORKSPACE_KEY,
            "Malware_Table_Name": consts.MALWARE_DATA_TABLE_NAME,
            "Function_App_Name": consts.FUNCTION_APP_NAME,
        }
        applogger.debug(
            "{}(method={}) : Checking if all the environment variables exist or not.".format(
                consts.LOGS_STARTS_WITH, __method_name
            )
        )
        missing_required_field = False
        for label, params in required_params.items():
            if not params or params == "":
                missing_required_field = True
                applogger.error(
                    '{}(method={}) : {} : "{}" field is not set in the environment please set '
                    "the environment variable and run the app.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        label,
                    )
                )
        if missing_required_field:
            raise CofenseIntelligenceException(
                "Error Occurred while validating params. Required fields missing."
            )
        if not consts.COFENSE_BASE_URL.startswith("https://"):
            applogger.error(
                '{}(method={}) : {} : "BaseURL" must start with "https://" schema followed '
                'by hostname. BaseURL="{}"'.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.COFENSE_BASE_URL,
                )
            )
            raise CofenseIntelligenceException(
                "Error Occurred while validating params. Invalid format for BaseURL."
            )

    def make_http_request(
        self,
        url,
        method,
        auth=None,
        headers=None,
        parameters=None,
        body=None,
        proxies=None,
    ):
        """To make rest api calls to  rest api.

        Args:
            url (String): URL of the rest call.
            method (String): HTTP method of rest call. Eg. "GET", etc.
            auth(Tuple,optional):auth tuple which contains username and password.Defaults to None
            headers (Dict, optional): headers. Defaults to None.
            parameters (Dict, optional): parameters. Defaults to None.
            body (Dict , optional): body. Defaults to None.
            proxies (Dict, optional): proxies. Defaults to None.

        Returns:
            response : response of the rest call.
        """
        __method_name = inspect.currentframe().f_code.co_name
        error_log = "{}(method={}) : {}: {}"
        response_error_log = "{}(method={}) : {}: url: {}, Status Code : {}: {}"
        try:
            applogger.debug(
                "{}(method={}) : {}: Calling url: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    url,
                )
            )
            if method == "POST":
                response = self.session.post(
                    url=url,
                    headers=headers,
                    params=parameters,
                    data=body,
                    auth=auth,
                    proxies=proxies,
                    timeout=consts.API_TIMEOUT,
                )
            else:
                response = self.session.get(
                    url=url,
                    headers=headers,
                    params=parameters,
                    data=body,
                    auth=auth,
                    proxies=proxies,
                    timeout=consts.API_TIMEOUT,
                )

            if response.status_code >= 200 and response.status_code <= 299:
                applogger.debug(
                    "{}(method={}) : {}: Got the response from url : {} : Status code : {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        url,
                        response.status_code,
                    )
                )
            elif response.status_code >= 400 and response.status_code <= 499:
                log_message = "error occurred while calling url."
                applogger.error(
                    response_error_log.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        url,
                        response.status_code,
                        log_message,
                    )
                )
            elif response.status_code == 500:
                log_message = "Internal Server Error"
                applogger.error(
                    response_error_log.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        url,
                        response.status_code,
                        log_message,
                    )
                )
            else:
                log_message = "Unexpected error occurred."
                applogger.error(
                    response_error_log.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        url,
                        response.status_code,
                        log_message,
                    )
                )
            return response
        except requests.ConnectionError as error:
            applogger.error(
                error_log.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()
        except requests.HTTPError as error:
            applogger.error(
                error_log.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()
        except requests.RequestException as error:
            applogger.error(
                error_log.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()
        except Exception as error:
            applogger.error(
                error_log.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()

    def auth_sentinel(self):
        """
        Authenticate with microsoft sentinel.

        Raises:
            CofenseIntelligenceException: Custom cofense Exception

        Returns:
            String: Bearer token
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                "{}(method={}) : {}: generating microsoft sentinel access token.".format(
                    consts.LOGS_STARTS_WITH, __method_name, self.azure_function_name
                )
            )
            azure_auth_url = consts.AZURE_AUTHENTICATION_URL.format(
                consts.AZURE_TENANT_ID
            )
            body = {
                "client_id": consts.AZURE_CLIENT_ID,
                "client_secret": consts.AZURE_CLIENT_SECRET,
                "grant_type": "client_credentials",
                "resource": "https://management.azure.com",
            }
            response = self.make_http_request(
                url=azure_auth_url,
                method="POST",
                body=body,
            )
            if response.status_code >= 200 and response.status_code <= 299:
                json_response = response.json()
                if "access_token" not in json_response:
                    applogger.error(
                        "{}(method={}) : {}: Access token not found in sentinel api call.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                        )
                    )
                    raise CofenseIntelligenceException()
                else:
                    bearer_token = json_response.get("access_token")
                    applogger.info(
                        "{}(method={}) : {}: Microsoft sentinel access token generated successfully.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) :{}: url:{}, Status Code :{}: Microsoft Sentinel access token generated.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            azure_auth_url,
                            response.status_code,
                        )
                    )
                    return bearer_token
            else:
                applogger.error(
                    "{}(method={}) :{}: url:{}, Status Code :{}: Error while creating microsoft sentinel access_token."
                    " Error Reason: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        azure_auth_url,
                        response.status_code,
                        response.reason,
                    )
                )
                raise CofenseIntelligenceException()
        except CofenseIntelligenceException as error:
            applogger.error(
                "{}(method={}) : Error generated while getting sentinel access token :{}".format(
                    consts.LOGS_STARTS_WITH, __method_name, error
                )
            )
            raise CofenseIntelligenceException()

    def get_cofense_data(self, url, params=None, endpoint_name="", proxies=None):
        """Get the Cofense Intelligence Indicators data.

        Args:
            url (String): url for fetch cofense data.
            params (dict, optional): parameter for request. Defaults to None.
            endpoint_name (String, optional):endpoint name. Defaults to ''.
            proxies(dict,optional):proxy, Defaults to None.

        Raises:
            CofenseIntelligenceException: Custom cofense Exception

        Returns:
            json: Cofense data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            retry_count_429 = 0
            while retry_count_429 <= 1:
                cofense_intelligence_data = self.make_http_request(
                    url=url,
                    method="GET",
                    parameters=params,
                    auth=self.auth,
                    proxies=proxies,
                )
                cofense_intelligence_data_status_code = (
                    cofense_intelligence_data.status_code
                )
                if (
                    cofense_intelligence_data_status_code >= 200
                    and cofense_intelligence_data_status_code <= 299
                ):
                    indicator_json = cofense_intelligence_data.json()
                    return indicator_json
                elif cofense_intelligence_data_status_code == 401:
                    applogger.error(
                        "{}(method={}) : {} : Unauthorized, Invalid Cofense Username or Cofense Password.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                        )
                    )

                    raise CofenseIntelligenceException()
                elif cofense_intelligence_data_status_code == 429:
                    applogger.error(
                        "{}(method={}) : {} : trying again error 429 in {}.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                            endpoint_name,
                        )
                    )
                    retry_count_429 += 1
                    time.sleep(consts.COFENSE_429_SLEEP)
                else:
                    applogger.error(
                        "{}(method={}) : {} : url: {}, Status Code : {} : error in {}."
                        " while pulling indicator data.".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.COFENSE_TO_SENTINEL,
                            url,
                            cofense_intelligence_data_status_code,
                            endpoint_name,
                        )
                    )
                    raise CofenseIntelligenceException()
            applogger.error(
                "{}(method={}) : {} : Max retries exceeded in {} while fetching data.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    endpoint_name,
                )
            )
            raise CofenseIntelligenceException()
        except CofenseIntelligenceException:
            applogger.error(
                "{}(method={}) : {} : error in {} while pulling data of indicator.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    endpoint_name,
                )
            )
            raise CofenseIntelligenceException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : error in {} while pulling data of indicator: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.COFENSE_TO_SENTINEL,
                    endpoint_name,
                    error,
                )
            )
            raise CofenseIntelligenceException()
