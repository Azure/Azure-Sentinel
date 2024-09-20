import hmac
import hashlib
import requests
import logging
from base64 import b64decode, b64encode


def build_signature(
    customer_id: str,
    shared_key: str,
    date: str,
    content_length: str,
    method: str,
    content_type: str,
    resource: str,
):
    """
    Builds the signature for authenticating requests to Azure Sentinel.

    Args:
        customer_id (str): The customer ID or workspace ID for Azure Sentinel.
        shared_key (str): The shared key for authentication with Azure Sentinel.
        date (str): The date and time of the request in RFC1123 format.
        content_length (int): The length of the request body in bytes.
        method (str): The HTTP method of the request.
        content_type (str): The content type of the request.
        resource (str): The resource being accessed.

    Returns:
        str: The authorization header value for the request.
    """

    x_headers = "x-ms-date:" + date
    string_to_hash = (
        method
        + "\n"
        + content_length
        + "\n"
        + content_type
        + "\n"
        + x_headers
        + "\n"
        + resource
    )
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = b64decode(shared_key)
    encoded_hash = b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def save_to_sentinel(
    log_analytics_uri: str, customer_id: str, shared_key: str, logs_obj: str, table_name: str
):
    """
    Saves logs to Azure Sentinel using the specified log_analytics_uri, customer_id, shared_key, and logs_obj.

    Args:
        log_analytics_uri (str): The URI for the Azure Log Analytics workspace.
        customer_id (str): The customer ID or workspace ID for Azure Sentinel.
        shared_key (str): The shared key for authentication with Azure Sentinel.
        logs_obj (str): The logs to be sent to Azure Sentinel in JSON format.
        table_name (str): The table which will be created in sentinel.

    Returns:
        int: The HTTP response status code if successful, or if there was an error.
    """
    from email.utils import formatdate

    rfc1123date = formatdate(timeval=None, localtime=False, usegmt=True)
    signature = build_signature(
        customer_id,
        shared_key,
        rfc1123date,
        str(len(logs_obj)),
        "POST",
        "application/json",
        "/api/logs",
    )
    headers = {
        "content-type": "application/json",
        "Authorization": signature,
        "Log-Type": table_name,
        "x-ms-date": rfc1123date,
        "time-generated-field": "date",
    }
    try:
        response = requests.post(log_analytics_uri, data=logs_obj, headers=headers)
    except Exception as ex:
        logging.error(str(ex))
        logging.error("Invalid Workspace ID")
        return 500

    if response.status_code in range(200, 299):
        return response.status_code
    else:
        logging.info(response.content)
        logging.info(
            "Events are not processed into Azure. Response code: {}".format(
                response.status_code
            )
        )
        return 500
