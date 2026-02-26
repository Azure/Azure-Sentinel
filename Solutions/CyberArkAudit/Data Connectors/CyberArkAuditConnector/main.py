import logging
import azure.functions as func
from .audit import get_query_data, get_cursor_results
from .exporter import send_dcr_data


def main(myTimer: func.TimerRequest) -> None:
    logging.info('Starting program')

    query_data = get_query_data()
    if not query_data:
        logging.error('Failed getting query data')
        return
    events = get_cursor_results(query_data)
    logging.info(f'Found {len(events)} events to export')
    if not events:
        return
    send_dcr_data(data=events)
