"""Utils module is for helping methods."""
import inspect
import requests
import time
from .consts import (
    LOGS_STARTS_WITH,
    AZURE_AUTHENTICATION_URL,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_TENANT_ID,
    AZURE_RESOURCE_GROUP,
    AZURE_SUBSCRIPTION_ID,
    AZURE_WORKSPACE_NAME,
    COFENSE_BASE_URL,
    COFENSE_CLIENT_ID,
    COFENSE_CLIENT_SECRET,
    ENDPOINTS,
    CONNECTION_STRING,
    PROXY_USERNAME,
    PROXY_PASSWORD,
    PROXY_URL,
    PROXY_PORT,
    PROXY_REQUEST,
    THREAT_LEVEL_BENIGN,
    THREAT_LEVEL_INTERMEDIATE,
    THREAT_LEVEL_MALICIOUS,
    THREAT_LEVEL_SUSPICIOUS,
    REPORTS_TABLE_NAME,
    WORKSPACE_ID,
    WORKSPACE_KEY,
    SCHEDULE,
    THREAT_LEVEL,
)
from .logger import applogger
from requests.compat import quote_plus
from .cofense_exception import CofenseException


def make_rest_call(
    url,
    method,
    azure_function_name,
    headers=None,
    params=None,
    payload=None,
    ssl_cert_path=True,
    proxies=None,
):
    """To make rest api calls to MS Sentinel rest api.

    Args:
        url (String): URL of the rest call.
        method (String): HTTP method of rest call. Eg. "GET", etc.
        headers (Dict, optional): headers. Defaults to None.
        params (Dict, optional): parameters. Defaults to None.
        payload (Type : As required by the rest call, optional): body. Defaults to None.
        ssl_cert_path (bool, optional): path to the certificate if True. Defaults to False.

    Returns:
        response : response of the rest call.
    """
    __method_name = inspect.currentframe().f_code.co_name
    error_log = "{}(method={}) : {}: {}"
    response_error_log = "{}(method={}) : {}: url: {}, Status Code : {}: {}"
    try:
        applogger.debug(
            "{}(method={}) : {}: Calling url: {}".format(
                LOGS_STARTS_WITH, __method_name, azure_function_name, url
            )
        )
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=payload,
            verify=ssl_cert_path,
            proxies=proxies,
        )
        if response.status_code >= 200 and response.status_code <= 299:
            applogger.debug(
                "{}(method={}) : {}: got the response from url : {} : Status code : {}".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    azure_function_name,
                    url,
                    response.status_code,
                )
            )
        elif response.status_code >= 400 and response.status_code <= 499:
            log_message = "error occurred while calling url."
            applogger.error(
                response_error_log.format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    azure_function_name,
                    url,
                    response.status_code,
                    log_message,
                )
            )
        elif response.status_code == 500:
            log_message = "Internal Server Error"
            applogger.error(
                response_error_log.format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    azure_function_name,
                    url,
                    response.status_code,
                    log_message,
                )
            )
        else:
            log_message = "Unexpected error occurred."
            applogger.error(
                response_error_log.format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    azure_function_name,
                    url,
                    response.status_code,
                    log_message,
                )
            )
    except requests.ConnectionError as error:
        applogger.error(
            error_log.format(
                LOGS_STARTS_WITH, __method_name, azure_function_name, error
            )
        )
        raise CofenseException()
    except requests.HTTPError as error:
        applogger.error(
            error_log.format(
                LOGS_STARTS_WITH, __method_name, azure_function_name, error
            )
        )
        raise CofenseException()
    except requests.RequestException as error:
        applogger.error(
            error_log.format(
                LOGS_STARTS_WITH, __method_name, azure_function_name, error
            )
        )
        raise CofenseException()
    except CofenseException as error:
        applogger.error(
            error_log.format(
                LOGS_STARTS_WITH, __method_name, azure_function_name, error
            )
        )
        raise CofenseException()
    # To do: check the flow of return statement.
    return response


def auth_sentinel(azure_function_name):
    """To authenticate with microsoft sentinel."""
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.info(
            "{}(method={}) : {}: generating microsoft sentinel access token.".format(
                LOGS_STARTS_WITH, __method_name, azure_function_name
            )
        )
        azure_auth_url = AZURE_AUTHENTICATION_URL.format(AZURE_TENANT_ID)
        body = {
            "client_id": AZURE_CLIENT_ID,
            "client_secret": AZURE_CLIENT_SECRET,
            "grant_type": "client_credentials",
            "resource": "https://management.azure.com",
        }
        response = make_rest_call(
            url=azure_auth_url,
            method="POST",
            azure_function_name=azure_function_name,
            payload=body,
        )
        if response.status_code >= 200 and response.status_code <= 299:
            json_response = response.json()
            if "access_token" not in json_response:
                applogger.error(
                    "{}(method={}) : {}: Access token not found in sentinel api call.".format(
                        LOGS_STARTS_WITH, __method_name, azure_function_name
                    )
                )
                raise CofenseException()
            else:
                bearer_token = json_response.get("access_token")
                applogger.info(
                    "{}(method={}) : {}: microsoft sentinel access token generated successfully.".format(
                        LOGS_STARTS_WITH, __method_name, azure_function_name
                    )
                )
                applogger.debug(
                    "{}(method={}) : {}: url: {}, Status Code : {}: Microsoft Sentinel access token generated.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        azure_auth_url,
                        response.status_code,
                    )
                )
                return bearer_token
        else:
            applogger.error(
                "{}(method={}) : {}: url: {}, Status Code : {}: Error while creating microsoft sentinel access_token."
                " Error Reason: {}".format(
                    LOGS_STARTS_WITH,
                    __method_name,
                    azure_function_name,
                    azure_auth_url,
                    response.status_code,
                    response.reason,
                )
            )
            raise CofenseException()
    except CofenseException as error:
        applogger.error(
            "{}(method={}) : Error generated while getting sentinel access token :{}".format(
                LOGS_STARTS_WITH, __method_name, error
            )
        )
        raise CofenseException()


def auth_cofense(azure_function_name):
    """To authenticate with cofense."""
    __method_name = inspect.currentframe().f_code.co_name
    try:
        applogger.info(
            "{}(method={}) : {}: generating cofense access token.".format(
                LOGS_STARTS_WITH, __method_name, azure_function_name
            )
        )
        cofense_auth_url = "{}{}".format(COFENSE_BASE_URL, ENDPOINTS["authentication"])
        COFENSE_429_SLEEP = 60
        body = {
            "client_id": COFENSE_CLIENT_ID,
            "client_secret": COFENSE_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        proxies = create_proxy()
        retry_count_429 = 0
        while retry_count_429 <= 1:
            response = make_rest_call(
                url=cofense_auth_url,
                method="POST",
                azure_function_name=azure_function_name,
                payload=body,
                proxies=proxies,
            )
            response_status_code = response.status_code
            if response_status_code >= 200 and response_status_code <= 299:
                json_response = response.json()
                if "access_token" not in json_response:
                    applogger.error(
                        "{}(method={}) : {}: url: {}, Status Code : {} : "
                        "Access token field not found in cofense authentication api call response.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            azure_function_name,
                            cofense_auth_url,
                            response.status_code,
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                        "Access token not found in cofense authentication api call.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            azure_function_name,
                            cofense_auth_url,
                            response.status_code,
                            response.reason,
                            response.text,
                        )
                    )
                    raise CofenseException()
                else:
                    access_token = json_response.get("access_token")
                    applogger.info(
                        "{}(method={}) : {}: cofense access token generated successfully.".format(
                            LOGS_STARTS_WITH, __method_name, azure_function_name
                        )
                    )
                    applogger.debug(
                        "{}(method={}) : {}: url: {}, Status Code : {}: Cofense Triage access token generated.".format(
                            LOGS_STARTS_WITH,
                            __method_name,
                            azure_function_name,
                            cofense_auth_url,
                            response.status_code,
                        )
                    )
                    return access_token
            elif response_status_code == 429:
                applogger.error(
                    "{}(method={}) : {}: url: {}, Status Code : {} : "
                    "Getting 429 from cofense api call. Retrying again after {} seconds.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        cofense_auth_url,
                        response.status_code,
                        COFENSE_429_SLEEP,
                    )
                )
                applogger.debug(
                    "{}(method={}) : {}: url: {}, Status Code : {}, Response reason: {}, Response: {} : "
                    "Getting 429 from cofense api call. Retry count: {}.".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        cofense_auth_url,
                        response.status_code,
                        response.reason,
                        response.text,
                        retry_count_429,
                    )
                )
                retry_count_429 += 1
                time.sleep(COFENSE_429_SLEEP)
            else:
                applogger.error(
                    "{}(method={}) : {}: url: {}, Status Code : {}: Error while creating cofense triage access token."
                    " Error Reason: {}".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        cofense_auth_url,
                        response.status_code,
                        response.reason,
                    )
                )
                applogger.debug(
                    "{}(method={}) : {}: url: {}, Status Code : {}, Response: {} :"
                    " Error while creating cofense triage access token. Error Reason: {}".format(
                        LOGS_STARTS_WITH,
                        __method_name,
                        azure_function_name,
                        cofense_auth_url,
                        response.status_code,
                        response.text,
                        response.reason,
                    )
                )
                raise CofenseException()
        applogger.error(
            "{}(method={}) : {} : Max retries exceeded for getting cofense access token.".format(
                azure_function_name, LOGS_STARTS_WITH, __method_name
            )
        )
        raise CofenseException()
    except CofenseException as error:
        applogger.error(
            "{}(method={}) : {}: Error generated while getting cofense access token :{}".format(
                LOGS_STARTS_WITH,
                __method_name,
                azure_function_name,
                error,
            )
        )
        raise CofenseException()


def check_environment_var_exist(azure_function_name):
    """To verify that all required environment variables are exist.

    Raises:
        CofenseException: raise exception if any of the required environment variable is not set.
    """
    __method_name = inspect.currentframe().f_code.co_name
    env_var = [
        {"CofenseClientId": COFENSE_CLIENT_ID},
        {"CofenseClientSecret": COFENSE_CLIENT_SECRET},
        {"AzureClientId": AZURE_CLIENT_ID},
        {"AzureClientSecret": AZURE_CLIENT_SECRET},
        {"AzureTenantId": AZURE_TENANT_ID},
        {"AzureResourceGroup": AZURE_RESOURCE_GROUP},
        {"AzureWorkspaceName": AZURE_WORKSPACE_NAME},
        {"AzureSubscriptionId": AZURE_SUBSCRIPTION_ID},
        {"ConnectionString": CONNECTION_STRING},
        {"CofenseBaseURL": COFENSE_BASE_URL},
        {"Reports_Table_name": REPORTS_TABLE_NAME},
        {"WorkspaceID": WORKSPACE_ID},
        {"WorkspaceKey": WORKSPACE_KEY},
        {"Schedule": SCHEDULE},
        {"Threat_Level": THREAT_LEVEL},
    ]
    try:
        applogger.debug(
            "{}(method={}) : Checking if all the environment variables exist or not.".format(
                LOGS_STARTS_WITH, __method_name
            )
        )
        # To do: convert i to each.
        for i in env_var:
            key, val = next(iter(i.items()))
            if val is None or not val:
                # To do: append val to list, at last raise exception for all vals.
                raise CofenseException(
                    "{} : {} : {} is not set in the environment please set the environment"
                    " variable and run the app.".format(
                        LOGS_STARTS_WITH, azure_function_name, key
                    )
                )
    except CofenseException as err:
        applogger.error(
            "{} : {} : {} : error occurred while checking environment variables : {}".format(
                LOGS_STARTS_WITH, azure_function_name, __method_name, err
            )
        )
        raise CofenseException()


def create_proxy():
    """To create proxy."""
    proxies = None
    if PROXY_USERNAME and PROXY_PASSWORD and PROXY_URL and PROXY_PORT:
        proxy_url = "{}://{}:{}@{}:{}".format(
            PROXY_REQUEST,
            quote_plus(PROXY_USERNAME),
            quote_plus(PROXY_PASSWORD),
            PROXY_URL,
            PROXY_PORT,
        )
        proxies = {"http": proxy_url, "https": proxy_url}
    # To do: Informative proxy message when proxy error occurred.
    return proxies


def cofense_to_sentinel_threat_level_mapping(
    indicator_threat_level, azure_function_name
):
    """To map threat level with confidence for microsoft sentinel indicator data."""
    __method_name = inspect.currentframe().f_code.co_name
    indicator_threat_level = indicator_threat_level.lower()
    if indicator_threat_level == "benign" or not indicator_threat_level:
        threat_level = THREAT_LEVEL_BENIGN
    elif indicator_threat_level == "suspicious":
        threat_level = THREAT_LEVEL_SUSPICIOUS
    elif indicator_threat_level == "malicious":
        threat_level = THREAT_LEVEL_MALICIOUS
    else:
        applogger.error(
            "{}(method={}) : {} : Unknown threat type.".format(
                LOGS_STARTS_WITH, __method_name, azure_function_name
            )
        )
        raise CofenseException()
    return threat_level


def sentinel_to_cofense_threat_level_mapping(confidence, azure_function_name):
    """To convert sentinel confidence value to threat level."""
    __method_name = inspect.currentframe().f_code.co_name
    if (
        confidence is None
        or confidence == ""
        or int(confidence) == 0
        or (
            int(confidence) >= THREAT_LEVEL_BENIGN
            and int(confidence) <= THREAT_LEVEL_INTERMEDIATE
        )
    ):
        threat_level = "Benign"
    elif (
        int(confidence) > THREAT_LEVEL_INTERMEDIATE
        and int(confidence) <= THREAT_LEVEL_SUSPICIOUS
    ):
        threat_level = "Suspicious"
    elif (
        int(confidence) > THREAT_LEVEL_SUSPICIOUS
        and int(confidence) <= THREAT_LEVEL_MALICIOUS
    ):
        threat_level = "Malicious"
    else:
        applogger.error(
            "{}(method={}) : {} : Unknown confidence value.".format(
                LOGS_STARTS_WITH, __method_name, azure_function_name
            )
        )
        raise CofenseException()

    return threat_level
