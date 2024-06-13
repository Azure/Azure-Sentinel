"""This file contains methods for creating microsoft indicator and custom log table."""
import inspect
import base64
import hashlib
import hmac
import datetime
import aiohttp
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.netskope_exception import NetskopeException


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


async def post_data(body, log_type, session: aiohttp.ClientSession):
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
            "{}(method={}) : {} : Error occurred: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                err,
            )
        )
        raise NetskopeException("Error while generating signature for posting data into log analytics.")
    uri = "https://" + consts.WORKSPACE_ID + ".ods.opinsights.azure.com" + resource + "?api-version=2016-04-01"

    headers = {
        "content-type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
    }
    try:
        response = await session.post(url=uri, data=body, headers=headers)
        if response.status >= 200 and response.status <= 299:
            applogger.debug(
                "{}(method={}) : {} : Status_code: {} Accepted: Data Posted Successfully to azure sentinel.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                    response.status,
                )
            )
            return response.status
        else:
            raise NetskopeException(
                "Response code: {} from posting data to log analytics.\nError: {}".format(
                    response.status, response.content
                )
            )
    except NetskopeException as error:
        applogger.error(
            "{}(method={}) : {} : Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                error,
            )
        )
        raise NetskopeException("NetskopeException: Error while posting data to sentinel.")
    except Exception as error:
        applogger.error(
            "{}(method={}) : {} : Error: {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.NETSKOPE_AZURE_STORAGE_TO_SENTINEL,
                error,
            )
        )
        raise NetskopeException("Exception: Error while posting data to sentinel.")
