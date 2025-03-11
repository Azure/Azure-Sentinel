import requests
import datetime
import hashlib
import hmac
import base64
import logging

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    try:
        x_headers = 'x-ms-date:' + date
        string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
        decoded_key = base64.b64decode(shared_key)
    except Exception as e:
        logging.exception(f"Error decoding shared_key: {e}")
        return None
    
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    
    if signature is None:
        return
    
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    try:
        response = requests.post(uri, data=body, headers=headers)
    except requests.RequestException as e:
        logging.error(f"Error sending data to Sentinel: {e}")
        return

    if 200 <= response.status_code < 300:
        logging.info(f"Data sent to Sentinel.")
    else:
        logging.error(f"Response code: {response.status_code}, Response content: {response.content}")