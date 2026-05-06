import os
import logging
import azure.functions as func
from .epm import collect_events
from .exporter import send_dcr_data


def _iter_chunks(data, chunk_size: int):
    chunk = []
    for item in data:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def main(mytimer: func.TimerRequest) -> None:
    if getattr(mytimer, 'past_due', False):
        logging.info('The timer is past due!')

    logging.getLogger().setLevel(logging.INFO)
    logging.info('Starting program')

    events = collect_events()
    logging.info(f'Found {len(events)} events to export')
    if not events:
        return
    chunk_size = int(os.environ.get('CHUNK_SIZE', '2000'))
    for chunk in _iter_chunks(events, chunk_size=chunk_size):
        send_dcr_data(data=chunk)
