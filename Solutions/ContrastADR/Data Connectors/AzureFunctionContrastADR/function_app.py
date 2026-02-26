import azure.functions as func
import logging
import json
import datetime
import hashlib
import hmac
import base64
import requests
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Load environment variables
LOG_ANALYTICS_WORKSPACE_ID = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")
LOG_ANALYTICS_SHARED_KEY = os.getenv("LOG_ANALYTICS_SHARED_KEY")

@app.route(route="contrast_ADR_trigger", methods=["POST"])
def webhook_listener(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Webhook received a request.")

    if not LOG_ANALYTICS_WORKSPACE_ID or not LOG_ANALYTICS_SHARED_KEY:
        logging.error("Missing Log Analytics credentials in environment variables.")
        return func.HttpResponse(
            "Server configuration error: Missing Log Analytics credentials.",
            status_code=500
        )

    try:
        json_data = req.get_json()
    except ValueError:
        logging.error("Invalid JSON received.")
        return func.HttpResponse("Invalid JSON body.", status_code=400)

    # Detect schema and assign log type(Table)
    if "eventUuid" in json_data:
        log_type = "ContrastADR_CL"
        logging.info(f"Schema: event | Event UUID: {json_data.get('eventUuid')} | Rule: {json_data.get('rule')}")
    elif "incidentId" in json_data:
        log_type = "ContrastADRIncident"
        logging.info(f"Schema: incident | Incident ID: {json_data.get('incidentId')} | Summary: {json_data.get('summary')}")
    else:
        logging.error(f"Unrecognized schema. Sample data: {json.dumps(json_data)[:300]}")
        return func.HttpResponse("Unsupported schema.", status_code=400)

    # Post to Sentinel
    try:
        post_data_to_sentinel(json_data, log_type)
    except Exception as e:
        logging.error(f"Failed to post to Sentinel: {str(e)}")
        return func.HttpResponse("Error sending data to Sentinel.", status_code=500)

    return func.HttpResponse("Webhook received and sent to Sentinel.", status_code=200)


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = f'x-ms-date:{date}'
    string_to_hash = f'{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}'
    bytes_to_hash = bytes(string_to_hash, encoding='utf-8')
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    return f"SharedKey {customer_id}:{encoded_hash}"


def post_data_to_sentinel(json_data, log_type):
    customer_id = LOG_ANALYTICS_WORKSPACE_ID
    shared_key = LOG_ANALYTICS_SHARED_KEY
    body = json.dumps(json_data)
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)

    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)

    uri = f'https://{customer_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01'

    headers = {
        'Content-Type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri, data=body, headers=headers)
    if 200 <= response.status_code <= 299:
        logging.info(f"Data posted successfully to Sentinel table '{log_type}'. Status Code: {response.status_code}")
    else:
        logging.error(f"Failed to post data to Sentinel. Status Code: {response.status_code}, Response: {response.text}")
        raise Exception(f"Failed to post data to Sentinel. Response: {response.text}")
