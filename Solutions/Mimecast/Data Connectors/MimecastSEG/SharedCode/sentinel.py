"""This file contains methods for creating microsoft custom log table."""

import base64
import requests
import hashlib
import hmac
import inspect
import datetime
import time
import aiohttp
from .logger import applogger
from .mimecast_exception import MimecastException
from . import consts
from .state_manager import StateManager
from urllib3.exceptions import NameResolutionError


def build_signature(
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
    decoded_key = base64.b64decode(consts.WORKSPACE_KEY)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(consts.WORKSPACE_ID, encoded_hash)

    return authorization


def post_data(body, log_type):
    """Build and send a request to the POST API.

    Args:
        body (str): Data to post into Sentinel log analytics workspace
        log_type (str): Custom log table name in which data wil be added.

    Returns:
        status_code: Returns the response status code got while posting data to sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)
    try:
        signature = build_signature(
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
    except Exception as err:
        applogger.error(
            "{}(method={}) : Error in build signature-{}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                err,
            )
        )
        raise MimecastException()
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

            result = handle_response(response, body, log_type, async_call=False)

            if result is not False:
                return result
            retry_count += 1
            continue
        except requests.exceptions.ConnectionError as error:
            try:
                if isinstance(error.args[0].reason, NameResolutionError):
                    applogger.error(
                        "{}(method={}) : {} : Workspace ID is wrong: {}, Sleeping for {} seconds and retrying..".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            log_type,
                            error,
                            consts.INGESTION_ERROR_SLEEP_TIME,
                        )
                    )
                    time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                    retry_count += 1
                    continue
            except Exception as unknown_connect_error:
                applogger.error(
                    "{}(method={}) : {} : Unknown Error in ConnectionError: {}, Sleeping for {} seconds."
                    " and retrying..".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        unknown_connect_error,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                continue
            applogger.error(
                "{}(method={}) : {} : Unknown Connection Error, sleeping for {} seconds and retrying.."
                "Error - {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                    error,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            retry_count += 1
            continue
        except requests.exceptions.Timeout as error:
            applogger.error(
                "{}(method={}) : {} : sleeping - {} seconds and retrying.. Timeout Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                    error,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            retry_count += 1
            continue
        except requests.RequestException as error:
            applogger.error(
                "{}(method={}) : {} : Request Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Unknown Error: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
    applogger.error(
        "{}(method={}) : {} : Maximum Retry count of {} exceeded, hence stopping execution.".format(
            consts.LOGS_STARTS_WITH,
            __method_name,
            log_type,
            consts.SENTINEL_RETRY_COUNT,
        )
    )
    raise MimecastException()


async def post_data_async(index, body, session: aiohttp.ClientSession, log_type):
    """Build and send a request to the POST API.

    Args:
        body (str): Data to post into Sentinel log analytics workspace
        log_type (str): Custom log table name in which data wil be added.

    Returns:
        status_code: Returns the response status code got while posting data to sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)
    try:
        signature = build_signature(
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
    except Exception as err:
        applogger.error(
            "{}(method={}) : Error in build signature-{} for task = {}".format(
                consts.LOGS_STARTS_WITH, __method_name, err, index
            )
        )
        raise MimecastException()
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

            response = await session.post(uri, data=body, headers=headers, timeout=consts.MAX_TIMEOUT_SENTINEL)

            result = handle_response(response, body, log_type, async_call=True)

            if result is not False:
                return result
            retry_count += 1
            continue
        except requests.exceptions.ConnectionError as error:
            try:
                if isinstance(error.args[0].reason, NameResolutionError):
                    applogger.error(
                        "{}(method={}) : {} : Workspace ID is wrong: {}, Sleeping for {} seconds and retrying..".format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            log_type,
                            error,
                            consts.INGESTION_ERROR_SLEEP_TIME,
                        )
                    )
                    time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                    retry_count += 1
                    continue
            except Exception as unknown_connect_error:
                applogger.error(
                    "{}(method={}) : {} : Unknown Error in ConnectionError: {}, Sleeping for {} seconds."
                    " and retrying..".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        unknown_connect_error,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                continue
            applogger.error(
                "{}(method={}) : {} : Unknown Connection Error, sleeping for {} seconds and retrying.."
                "Error - {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                    error,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            retry_count += 1
            continue
        except requests.exceptions.Timeout as error:
            applogger.error(
                "{}(method={}) : {} : sleeping - {} seconds and retrying.. Timeout Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                    error,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            retry_count += 1
            continue
        except requests.RequestException as error:
            applogger.error(
                "{}(method={}) : {} : Request Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Unknown Error: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
    applogger.error(
        "{}(method={}) : {} : Maximum Retry count of {} exceeded, hence stopping execution.".format(
            consts.LOGS_STARTS_WITH,
            __method_name,
            log_type,
            consts.SENTINEL_RETRY_COUNT,
        )
    )
    raise MimecastException()


def handle_response(response, body, log_type, async_call=True):
    """Handle the response from Azure Sentinel."""
    try:
        __method_name = inspect.currentframe().f_code.co_name

        if async_call is False:
            response_code = response.status_code
        else:
            response_code = response.status

        if response_code >= 200 and response_code <= 299:
            applogger.debug(
                "{}(method={}) : Status_code: {} Accepted: Data Posted Successfully to azure sentinel.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    response_code,
                )
            )
            return response_code
        elif response_code == 400:
            applogger.error(
                "{}(method={}) : {} : Response code: {} from posting data to log analytics. Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    response_code,
                    response.text,
                )
            )
            curent_corrupt_data_obj = StateManager(
                consts.CONN_STRING,
                "{}-Ingest-To-Sentinel-Corrupt_{}".format(log_type, str(int(time.time()))),
                consts.FILE_SHARE_NAME,
            )
            curent_corrupt_data_obj.post(body)
            raise MimecastException()
        elif response_code == 403:
            applogger.error(
                "{}(method={}) : {} : Response code :{} Error occurred for build signature: Response: {} ."
                " Issue with WorkspaceKey ,Kindly verify your WorkspaceKey".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    response_code,
                    response.text,
                )
            )
            raise MimecastException()
        elif response_code == 429:
            applogger.error(
                "{}(method={}) : {} : Error occurred: Response code : {} Too many request: Response: {} . "
                "sleeping for {} seconds and retrying..".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    response_code,
                    response.text,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            return False
        elif response_code == 500:
            applogger.error(
                "{}(method={}) : {} : Error occurred:  Response code : {} Internal Server Error: Response: {} . "
                "sleeping for {} seconds and retrying..".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    response_code,
                    response.text,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            return False
        elif response_code == 503:
            applogger.error(
                "{}(method={}) : {} : Error occurred: Response code : {} Service Unavailable: Response: {} . "
                "sleeping for {} seconds and retrying..".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    response_code,
                    response.text,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            return False
        applogger.error(
            "{}(method={}) : {} : Response code: {} from posting data to log analytics. Response: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                log_type,
                response_code,
                response.text,
            )
        )
        raise MimecastException()
    except MimecastException:
        raise MimecastException()
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Unknown Error: {}.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                log_type,
                error,
            )
        )
        raise MimecastException()
