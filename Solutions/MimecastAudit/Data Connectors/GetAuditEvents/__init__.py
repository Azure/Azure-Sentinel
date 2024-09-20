import datetime
import logging
import json
import os
import azure.functions as func

from Helpers.date_helper import DateHelper
from TransformData.audit_parser import AuditParser
from Helpers.request_helper import RequestHelper
from Helpers.response_helper import ResponseHelper
from Helpers.azure_monitor_collector import AzureMonitorCollector
from Models.Request.get_audit_events import GetAuditEventsRequest
from Models.Error.errors import MimecastRequestError, AzureMonitorCollectorRequestError
from Models.Enum.mimecast_endpoints import MimecastEndpoints
from azure.storage.blob import BlobServiceClient
from Helpers.checkpoint_helper import CheckpointHelper

WORKSPACE_ID = os.environ['log_analytics_workspace_id']
WORKSPACE_KEY = os.environ['log_analytics_workspace_key']
LOG_TYPE = 'MimecastAudit'
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

def main(mytimer: func.TimerRequest, checkpoint: str) -> str:

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    request_helper = RequestHelper()
    response_helper = ResponseHelper()
    azure_monitor_collector = AzureMonitorCollector()
    checkpoint_helper = CheckpointHelper()

    request_helper.set_request_credentials(email=os.environ['mimecast_email'],
                                           password=os.environ['mimecast_password'],
                                           app_id=os.environ['mimecast_app_id'],
                                           app_key=os.environ['mimecast_app_key'],
                                           access_key=os.environ['mimecast_access_key'],
                                           secret_key=os.environ['mimecast_secret_key'],
                                           base_url=os.environ['mimecast_base_url'])

    checkpoint = checkpoint_helper.get_checkpoint(checkpoint)
    mimecast_start_date = checkpoint["start_time"]
    mimecast_end_date = checkpoint["end_time"]
    
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])

    # Get a BlobClient for the specific blob
    blob_client = blob_service_client.get_blob_client(container="audit-checkpoints", blob="checkpoint.txt")


    audit_parser = AuditParser()
    mapped_response_data, model, next_token, has_more_logs = request_helper.set_initial_values()

    try:
        while has_more_logs:
            parsed_logs = []
            model = GetAuditEventsRequest(mimecast_start_date, mimecast_end_date, next_token)
            response = request_helper.send_post_request(model.payload, MimecastEndpoints.get_audit_events)
            response_helper.check_response_codes(response, MimecastEndpoints.get_audit_events)
            success_response = response_helper.parse_success_response(response)
            has_more_logs, next_token = response_helper.get_next_token(response)
            parsed_logs.extend(audit_parser.parse(logs=success_response))
            if parsed_logs:
                body = json.dumps(parsed_logs)
                azure_monitor_collector.post_data(WORKSPACE_ID, WORKSPACE_KEY, body, LOG_TYPE)
                checkpoint['end_time'] = datetime.datetime.fromisoformat(parsed_logs[-1]['time_generated']).strftime(TIME_FORMAT)
                blob_client.upload_blob(json.dumps(checkpoint), overwrite=True)
            else:
                logging.info("There are no Audit Events for this period.")
                checkpoint = checkpoint_helper.initialize_new_checkpoint(checkpoint)
                return json.dumps(checkpoint)
        if has_more_logs is False:
            checkpoint = checkpoint_helper.initialize_new_checkpoint(checkpoint)
        return json.dumps(checkpoint)
    except MimecastRequestError as e:
        logging.error('Failed to get Audit logs from Mimecast.', extra={'request_id': request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except AzureMonitorCollectorRequestError as e:
        logging.error('Failed to send Audit logs to Azure Sentinel.', extra={'request_id': request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except Exception as e:
        logging.error('Unknown Exception raised.', extra={'request_id': request_helper.request_id})
        raise e
