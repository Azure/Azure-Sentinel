import os
from datetime import datetime, timedelta
import logging
import azure.functions as func
from .epm import get_query_data
from .exporter import send_dcr_data



def main(mytimer: func.TimerRequest) -> None:
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Starting program')
    events = get_query_data()
    if not events:
        logging.error('Failed getting events')
        return
    #events = get_cursor_results(query_data)
    logging.info(f'Found {len(events)} events to export')
    if not events:
        return
    send_dcr_data(data=events)
