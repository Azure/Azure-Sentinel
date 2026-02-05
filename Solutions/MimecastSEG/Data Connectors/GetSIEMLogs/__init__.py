import datetime
import logging
import json
import os
import azure.functions as func
from ..Helpers.request_helper import RequestHelper
from ..Helpers.siem_response_helper import SIEMResponseHelper
from ..Helpers.azure_monitor_collector import AzureMonitorCollector
from ..Models.Error.errors import MimecastRequestError, AzureMonitorCollectorRequestError
from ..Models.Request.get_siem_logs import GetSIEMLogsRequest
from ..Models.Enum.mimecast_endpoints import MimecastEndpoints
from ..TransformData.siem_parser import SiemParser
from azure.storage.blob import BlobServiceClient

WORKSPACE_ID = os.environ['log_analytics_workspace_id']
WORKSPACE_KEY = os.environ['log_analytics_workspace_key']
LOG_TYPE = 'MimecastSIEM'

def main(mytimer: func.TimerRequest, checkpoint: str) -> str:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    request_helper = RequestHelper()
    response_helper = SIEMResponseHelper()
    azure_monitor_collector = AzureMonitorCollector()

    request_helper.set_request_credentials(email=os.environ['mimecast_email'],
                                           password=os.environ['mimecast_password'],
                                           app_id=os.environ['mimecast_app_id'],
                                           app_key=os.environ['mimecast_app_key'],
                                           access_key=os.environ['mimecast_access_key'],
                                           secret_key=os.environ['mimecast_secret_key'],
                                           base_url=os.environ['mimecast_base_url'])
    next_token = checkpoint
    has_more_logs = True
    siem_parser = SiemParser()
    parsed_logs = []
    file_format = 'key_value'
    model = {}
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])

    # Get a BlobClient for the specific blob
    blob_client = blob_service_client.get_blob_client(container="siem-checkpoints", blob="checkpoint.txt")

    try:
        while has_more_logs:
            parsed_logs = []
            model = GetSIEMLogsRequest(file_format, next_token)
            response = request_helper.send_post_request(model.payload, MimecastEndpoints.get_siem_logs)
            response_helper.check_response_codes(response, MimecastEndpoints.get_siem_logs)
            success_response = response_helper.parse_siem_success_response(response, file_format)
            has_more_logs, next_token = response_helper.get_siem_next_token(response)
            parsed_logs.extend(siem_parser.parse(logs=success_response))
            if parsed_logs:
                body = json.dumps(parsed_logs)
                azure_monitor_collector.post_data(WORKSPACE_ID, WORKSPACE_KEY, body, LOG_TYPE)
            else:
                logging.info("There are no SIEM logs for this period.")
                return checkpoint
            checkpoint = next_token
            blob_client.upload_blob(checkpoint, overwrite=True)
        SIEMResponseHelper.response = []
        return checkpoint
    except MimecastRequestError as e:
        logging.error('Failed to get SIEM logs from Mimecast.', extra={'request_id': request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except AzureMonitorCollectorRequestError as e:
        logging.error('Failed to send SIEM logs to Azure Sentinel.', extra={'request_id': request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except Exception as e:
        logging.error('Unknown Exception raised.', extra={'request_id': request_helper.request_id})
        raise e
