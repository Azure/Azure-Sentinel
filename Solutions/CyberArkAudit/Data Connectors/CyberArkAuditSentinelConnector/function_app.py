import logging
import os
import azure.functions as func
from audit import get_query_model, get_cursor_results
from exporter import send_dcr_data

trigger_cron = os.environ.get('TriggerSchedule')
app = func.FunctionApp()


@app.function_name(name="TimmerTriggeredApp")
@app.schedule(schedule=trigger_cron,
              arg_name="mytimer",
              run_on_startup=True)
def main(mytimer: func.TimerRequest) -> None:
    run_program()


def run_program():
    logging.info('Starting program')

    query_model = get_query_model()
    if not query_model:
        logging.error('Failed getting query model')
        return
    events = get_cursor_results(query_model)
    logging.info(f'Found {len(events)} events to export')
    if not events:
        return
    send_dcr_data(data=events)

