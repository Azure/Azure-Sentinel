import datetime
import logging

from . import DS_poller
import azure.functions as func
import os

account_id = os.environ['digitalshadowsAccountID']
customer_id = os.environ['WorkspaceID']
shared_key = os.environ['WorkspaceKey']
key = os.environ['digitalshadowsKey']
secret = os.environ['digitalshadowsSecret']
connection_string = os.environ['AzureWebJobsStorage']
historical_days = os.environ['historicaldays']
url = os.environ['digitalshadowsUrl']


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    DSobj = DS_poller.poller(account_id, key, secret, customer_id, shared_key, connection_string, historical_days, url)
    
    DSobj.poll()