import datetime
import logging
import json
import os
import azure.functions as func
from ..Helpers.date_helper import DateHelper
from ..Helpers.request_helper import RequestHelper
from ..Helpers.response_helper import ResponseHelper
from ..Helpers.azure_monitor_collector import AzureMonitorCollector
from ..Models.Request.get_ttp_attachment_logs import GetTTPAttachmentLogsRequest
from ..Models.Error.errors import MimecastRequestError, AzureMonitorCollectorRequestError
from ..Models.Enum.mimecast_endpoints import MimecastEndpoints
from ..TransformData.ttp_attachment_parser import TTPAttachmentParser
from azure.storage.blob import BlobServiceClient

WORKSPACE_ID = os.environ["log_analytics_workspace_id"]
WORKSPACE_KEY = os.environ["log_analytics_workspace_key"]
LOG_TYPE = "MimecastTTPAttachment"

def main(mytimer: func.TimerRequest, checkpoint: str) -> str:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    request_helper = RequestHelper()
    response_helper = ResponseHelper()
    azure_monitor_collector = AzureMonitorCollector()

    request_helper.set_request_credentials(
        email=os.environ["mimecast_email"],
        password=os.environ["mimecast_password"],
        app_id=os.environ["mimecast_app_id"],
        app_key=os.environ["mimecast_app_key"],
        access_key=os.environ["mimecast_access_key"],
        secret_key=os.environ["mimecast_secret_key"],
        base_url=os.environ["mimecast_base_url"],
    )

    # datetime manipulation is done to assure there is neither duplicate nor missing logs
    start_date = checkpoint if checkpoint else DateHelper.get_utc_time_in_past(days=7)
    mimecast_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(seconds=1)
    mimecast_start_date = mimecast_start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    end_date = datetime.datetime.fromisoformat(utc_timestamp) - datetime.timedelta(seconds=15)
    mimecast_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    checkpoint = mimecast_end_date
    mapped_response_data, model, next_token, has_more_logs = request_helper.set_initial_values()
    ttp_attachment_parser = TTPAttachmentParser()
    parsed_logs = []
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])

    # Get a BlobClient for the specific blob
    blob_client = blob_service_client.get_blob_client(container="ttp-checkpoints", blob="attachment-checkpoint.txt")
    try:
        while has_more_logs:
            parsed_logs = []
            model = GetTTPAttachmentLogsRequest(mimecast_start_date, mimecast_end_date, next_token)
            response = request_helper.send_post_request(model.payload, MimecastEndpoints.get_ttp_attachment_logs)
            response_helper.check_response_codes(response, MimecastEndpoints.get_ttp_attachment_logs)
            success_response = response_helper.parse_success_response(response)
            has_more_logs, next_token = response_helper.get_next_token(response)
            parsed_logs.extend(ttp_attachment_parser.parse(logs=success_response[0]["attachmentLogs"]))
            if parsed_logs:
                body = json.dumps(parsed_logs)
                azure_monitor_collector.post_data(WORKSPACE_ID, WORKSPACE_KEY, body, LOG_TYPE)
                # logs are sorted so next line will return the latest log date
                checkpoint =  parsed_logs[-1]["date"]
                blob_client.upload_blob(checkpoint, overwrite=True)
            else:
                logging.info("There are no TTP Attachment logs for this period.")
                return checkpoint
        return checkpoint
    except AzureMonitorCollectorRequestError as e:
        logging.error(
            "Failed to send TTP Attachment to Azure Sentinel.", extra={"request_id": request_helper.request_id}
        )
        e.request_id = request_helper.request_id
        raise e
    except MimecastRequestError as e:
        logging.error(
            "Failed to get TTP Attachment logs from Mimecast.", extra={"request_id": request_helper.request_id}
        )
        e.request_id = request_helper.request_id
        raise e
    except Exception as e:
        logging.error("Unknown Exception raised.", extra={"request_id": request_helper.request_id})
        raise e
