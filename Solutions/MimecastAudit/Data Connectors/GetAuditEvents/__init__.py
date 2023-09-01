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


def main(mytimer: func.TimerRequest, checkpoint: str) -> str:

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    request_helper = RequestHelper()
    response_helper = ResponseHelper()
    azure_monitor_collector = AzureMonitorCollector()

    request_helper.set_request_credentials(email=os.environ['mimecast_email'],
                                           password=os.environ['mimecast_password'],
                                           app_id=os.environ['mimecast_app_id'],
                                           app_key=os.environ['mimecast_app_key'],
                                           access_key=os.environ['mimecast_access_key'],
                                           secret_key=os.environ['mimecast_secret_key'],
                                           base_url=os.environ['mimecast_base_url'])

    # datetime manipulation is done to assure there is neither duplicate nor missing logs
    start_date = checkpoint if checkpoint else DateHelper.get_utc_time_in_past(days=7)
    mimecast_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(seconds=1)
    mimecast_start_date = mimecast_start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    end_date = datetime.datetime.fromisoformat(utc_timestamp) - datetime.timedelta(seconds=15)
    mimecast_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S%z")

    audit_parser = AuditParser()
    parsed_logs = []
    mapped_response_data, model, next_token, has_more_logs = request_helper.set_initial_values()

    try:
        while has_more_logs:
            model = GetAuditEventsRequest(mimecast_start_date, mimecast_end_date, next_token)
            response = request_helper.send_post_request(model.payload, MimecastEndpoints.get_audit_events)
            response_helper.check_response_codes(response, MimecastEndpoints.get_audit_events)
            success_response = response_helper.parse_success_response(response)
            has_more_logs, next_token = response_helper.get_next_token(response)
            parsed_logs.extend(audit_parser.parse(logs=success_response))
    except MimecastRequestError as e:
        logging.error('Failed to get Audit logs from Mimecast.', extra={'request_id': request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e

    except Exception as e:
        logging.error('Unknown Exception raised.', extra={'request_id': request_helper.request_id})
        raise e

    try:
        if parsed_logs:
            workspace_id = os.environ['log_analytics_workspace_id']
            workspace_key = os.environ['log_analytics_workspace_key']
            log_type = 'MimecastAudit'
            body = json.dumps(parsed_logs)
            azure_monitor_collector.post_data(workspace_id, workspace_key, body, log_type)
            parsed_logs.sort(key=lambda x: x['time_generated'])
            latest_log = datetime.datetime.fromisoformat(parsed_logs[-1]['time_generated']).strftime("%Y-%m-%dT%H:%M:%S%z")
            return latest_log
        else:
            logging.info("There are no Audit Events for this period.")
            return mimecast_end_date
    except AzureMonitorCollectorRequestError as e:
        logging.error('Failed to send Audit logs to Azure Sentinel.', extra={'request_id': request_helper.request_id})
        e.request_id = request_helper.request_id
        raise e
    except Exception as e:
        logging.error('Unknown Exception raised.', extra={'request_id': request_helper.request_id})
        raise e
