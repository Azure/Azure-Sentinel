import datetime
import logging

from . import DS_poller
import azure.functions as func
import os

logger = logging.getLogger("__init__")

account_id = os.environ['DigitalShadowsAccountID']
dce_url = os.environ['DCE_URL']
dcr_immutable_id = os.environ['DCR_IMMUTABLE_ID']
stream_name = os.environ['STREAM_NAME']
key = os.environ['DigitalShadowsKey']
secret = os.environ['DigitalShadowsSecret']
connection_string = os.environ['AzureWebJobsStorage']
historical_days = os.environ['HistoricalDays']
url = os.environ['DigitalShadowsURL']
classification_filter_operation = os.environ['ClassificationFilterOperation']
high_variability_classifications = os.environ['HighVariabilityClassifications']
function_name = os.environ['FUNCTION_NAME']


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info('starting')

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    DSobj = DS_poller.poller(function_name, account_id, key, secret, dce_url, dcr_immutable_id, stream_name, connection_string, historical_days, url)
    classification_list = high_variability_classifications.split(",")

    DSobj.poll(classification_filter_operation, classification_list)