import datetime
import logging
import json
import os
import azure.functions as func
from ..Helpers.date_helper import DateHelper
from ..Helpers.request_helper import RequestHelper
from ..Helpers.response_helper import ResponseHelper
from ..Helpers.azure_monitor_collector import AzureMonitorCollector
from ..Models.Request.get_ttp_url_logs import GetTTPUrlLogsRequest
from ..Models.Error.errors import MimecastRequestError, AzureMonitorCollectorRequestError
from ..Models.Enum.mimecast_endpoints import MimecastEndpoints
from ..TransformData.ttp_url_parser import TTPUrlParser


def main(mytimer: func.TimerRequest, checkpoint3: str) -> str:
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
    start_date = checkpoint3 if checkpoint3 else DateHelper.get_utc_time_in_past(days=7)
    mimecast_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(seconds=1)
    mimecast_start_date = mimecast_start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    end_date = datetime.datetime.fromisoformat(utc_timestamp) - datetime.timedelta(seconds=15)
    mimecast_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S%z")

    mapped_response_data, model, next_token, has_more_logs = request_helper.set_initial_values()
    ttp_url_parser = TTPUrlParser()
    parsed_logs = []

    try:
        while has_more_logs:
            model = GetTTPUrlLogsRequest(mimecast_start_date, mimecast_end_date, next_token)
            response = request_helper.send_post_request(model.payload, MimecastEndpoints.get_ttp_url_logs)
            response_helper.check_response_codes(response, MimecastEndpoints.get_ttp_url_logs)
            success_response = response_helper.parse_success_response(response)
            has_more_logs, next_token = response_helper.get_next_token(response)
            parsed_logs.extend(ttp_url_parser.parse(logs=success_response[0]["clickLogs"]))
    except MimecastRequestError as e:
        logging.error("Failed to get TTP Url logs from Mimecast.", extra={"request_id": request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except Exception as e:
        logging.error("Unknown Exception raised.", extra={"request_id": request_helper.request_id})
        raise e

    try:
        if parsed_logs:
            workspace_id = os.environ["log_analytics_workspace_id"]
            workspace_key = os.environ["log_analytics_workspace_key"]
            log_type = "MimecastTTPUrl"
            body = json.dumps(parsed_logs)
            azure_monitor_collector.post_data(workspace_id, workspace_key, body, log_type)
            # logs are sorted so next line will return the latest log date
            return parsed_logs[-1]["date"]
        else:
            logging.info("There are no TTP Url logs for this period.")
            return mimecast_end_date
    except AzureMonitorCollectorRequestError as e:
        logging.error("Failed to send TTP Url to Azure Sentinel.", extra={"request_id": request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except Exception as e:
        logging.error("Unknown Exception raised.", extra={"request_id": request_helper.request_id})
        raise e
