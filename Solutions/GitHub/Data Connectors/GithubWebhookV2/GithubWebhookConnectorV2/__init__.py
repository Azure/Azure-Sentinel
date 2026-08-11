import datetime
import logging
import os
import json
import hashlib
import hmac
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError

github_webhook_secret = os.environ.get('GithubWebhookSecret')
dce_endpoint = os.environ.get('DCE_ENDPOINT')
dcr_rule_id = os.environ.get('DCR_RULE_ID')
dcr_stream_name = os.environ.get('DCR_STREAM_NAME', 'Custom-GitHubAdvancedSecurityAlerts_CL')

credential = DefaultAzureCredential()
client = LogsIngestionClient(endpoint=dce_endpoint, credential=credential)

logging.info("GithubWebhookV2: DCE_ENDPOINT=%s, DCR_STREAM_NAME=%s", dce_endpoint, dcr_stream_name)


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Info:Current retry count:{}'.format(context.retry_context.retry_count))
    logging.info('Info:Github webhook v2 data connector started')

    # check webhook signature if GitHubWebhookSecret exists
    if github_webhook_secret not in (None, '') and not str(github_webhook_secret).isspace():
        hash_object = hmac.new(github_webhook_secret.encode('utf-8'), msg=req.get_body(), digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        if 'x-hub-signature-256' not in req.headers:
            return func.HttpResponse(
                "Github webhook signature header is missing.",
                status_code=403
            )
        signature_header = req.headers['x-hub-signature-256']
        if not hmac.compare_digest(expected_signature, signature_header):
            return func.HttpResponse(
                "Github webhook signature verification failed.",
                status_code=403
            )

    req_body = req.get_json()
    if "x-github-event" in req.headers:
        req_body["event"] = req.headers["x-github-event"]
    body = json.dumps(customize_json(json.dumps(req_body)))
    logging.info("Info:Converted input json to dict and further to json")

    try:
        post_data(body)
        logging.info("Info: Github webhook v2 data connector execution completed successfully.")
        return func.HttpResponse(
            "Github webhook v2 data connector execution completed successfully.",
            status_code=200
        )
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))
        logging.error("Error: Github webhook v2 data connector execution failed with an internal server error.")
        raise


#####################
######Functions######
#####################

def customize_json(input_json):
    """Flatten nested objects to JSON strings to match CLv1 column format."""
    required_fields_data = {}
    new_json_dict = json.loads(input_json)
    for key, value in new_json_dict.items():
        if isinstance(value, dict):
            required_fields_data[key] = json.dumps(value, indent=4)
        else:
            required_fields_data[key] = value
    return required_fields_data


def post_data(body):
    """Send data to Log Analytics via the Logs Ingestion API (CLv2)."""
    log_entry = json.loads(body)
    log_entry['TimeGenerated'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    try:
        client.upload(rule_id=dcr_rule_id, stream_name=dcr_stream_name, logs=[log_entry])
        logging.info('Info:Event was ingested via Logs Ingestion API')
    except HttpResponseError as e:
        logging.error("Upload failed. Response code: {}. Message: {}".format(e.status_code, e.message))
        raise
    except Exception as e:
        logging.error("Unexpected error during upload: %s (%s)", e, type(e).__name__)
        raise
