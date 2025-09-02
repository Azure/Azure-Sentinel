"""
Main Function
"""

# pylint: disable=logging-fstring-interpolation

import logging
from datetime import datetime, timedelta
from traceback import format_exc

import azure.functions as func

from .const import IOC_LIST, VMRay_CONFIG
from .utils import (
    IOC_MAPPING_FUNCTION,
    get_last_saved_timestamp,
    get_sample_ioc,
    get_submission,
    save_checkpoint,
    submit_indicator,
)


def main(mytimer: func.TimerRequest) -> None:
    """
    Main handler function to interact with the VMRay API, triggered on a timer.

    This function manages VMRay API access tokens, performs API calls including
    pagination to retrieve all relevant data, and handles errors gracefully.
    It is designed to run at scheduled intervals via a timer trigger.

    Parameters
    ----------
    mytimer : func.TimerRequest
        Timer object that triggers the function execution on a defined schedule.
    """
    try:
        if mytimer.past_due:
            logging.info("The timer is past due!")
            return

        initial_date_time = get_last_saved_timestamp() or (
            datetime.now() - timedelta(days=int(VMRay_CONFIG.INITIAL_FETCH))
        ).strftime("%Y-%m-%dT00:00:00")
        logging.info(f"last_run {get_last_saved_timestamp()}")
        sample_verdict = VMRay_CONFIG.VMRAY_SAMPLE_VERDICTS
        sample_verdict = sample_verdict.split(" & ")
        logging.info(f"verdict {sample_verdict}")
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        submissions_list = get_submission(
            sample_verdict, initial_date_time, current_date
        )
        for sub in submissions_list:
            if sub.get("submission_finished"):
                iocs = get_sample_ioc(sub.get("submission_sample_id"))
                for key, value in iocs.items():
                    if key in IOC_LIST:
                        IOC_MAPPING_FUNCTION[key](
                            value,
                            sub.get("submission_sample_id"),
                            sub.get("submission_id"),
                            sample_verdict,
                        )
        submit_indicator()
        save_checkpoint(current_date)
    except Exception as ex:
        error_detatl = format_exc()
        logging.error(f"something went wrong. Error: {ex}. Traceback {error_detatl}")

