from re import escape, sub
import hmac
import hashlib
import requests
import logging
from base64 import b64decode, b64encode


BLACKLIST_PATTERNS = ["@sixgill-start-highlight@", "@sixgill-end-highlight@"]

def remove_patterns(alert):
    new_dict = {}
    for k, v in alert.items():
        if isinstance(v, str):
            new_dict[k] = sub(r"|".join(map(escape, BLACKLIST_PATTERNS)), "", v)
        elif isinstance(v, list):
            new_dict[k] = [
                sub(r"|".join(map(escape, BLACKLIST_PATTERNS)), "", i) for i in v
            ]
        elif isinstance(v, dict):
            new_dict[k] = remove_patterns(v)
        else:
            new_dict[k] = v
    return new_dict


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = b64decode(shared_key)
    encoded_hash = b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


def save_to_sentinel(logAnalyticsUri, customer_id, shared_key, alert_obj):
    from email.utils import formatdate
    rfc1123date = formatdate(timeval=None, localtime=False, usegmt=True)
    signature = build_signature(customer_id, shared_key, rfc1123date, len(alert_obj), "POST", "application/json", "/api/logs")
    uri = logAnalyticsUri + '/api/logs?api-version=2016-04-01'

    headers = {
        'content-type': "application/json",
        'Authorization': signature,
        'Log-Type': "CyberSixgill_Alerts",
        'x-ms-date': rfc1123date,
        'time-generated-field': 'date'
    }
    response = requests.post(uri,data=alert_obj, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        return response.status_code
    else:
        logging.info(response.content)
        logging.info("Events are not processed into Azure. Response code: {}".format(response.status_code))
        return None