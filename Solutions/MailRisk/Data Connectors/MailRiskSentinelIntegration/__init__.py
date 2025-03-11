import datetime
import logging
from sentinel_integration import get_new_email_ids_and_event_types, post_emails
import azure.functions as func


def main(timer: func.TimerRequest, inputblob, outputblob) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    logging.info('Python timer trigger function started at %s', utc_timestamp)

    if inputblob is not None: 
        input = str(inputblob.read(), "utf-8") 
    else:
        input = ''

    logging.info('Finding new email ids')
    email_ids_and_event_types = get_new_email_ids_and_event_types(input, outputblob)
    if len(email_ids_and_event_types) > 0:
        logging.info(f'Pushing {len(email_ids_and_event_types)} emails to Azure Sentinel')
        post_emails(email_ids_and_event_types)
    else:
        logging.info('No emails were found')
    
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    logging.info('Python timer trigger function finished at %s', utc_timestamp)
