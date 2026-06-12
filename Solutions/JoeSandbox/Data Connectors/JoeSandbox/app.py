"""
Main Function
"""

# pylint: disable=logging-fstring-interpolation
import logging
from datetime import datetime, timedelta, timezone
from json import loads
from traceback import format_exc

import azure.functions as func

from .const import IOC_LIST, joe_config
from .utils import (IOC_MAPPING_FUNCTION, joe_api, parse_analysis_data, state,
                    submit_indicator, DATE_FORMAT)

def main(mytimer: func.TimerRequest) -> None:
    """
    Timer-triggered Azure Function to interact with the JoeSandbox API.

    This function fetches recent analyses from JoeSandbox, processes finished results,
    extracts IOCs, and submits them to Microsoft Sentinel. It handles pagination, API
    errors, and maintains state using checkpointing.

    Parameters
    ----------
    mytimer : func.TimerRequest
        Timer trigger object.
    """
    try:
        if mytimer.past_due:
            logging.info("The timer is past due!")
            return

        last_run_value = state.get()
        if last_run_value is not None:
            last_run = str(last_run_value)
            logging.info(f"Last run timestamp: {last_run}")
        else:
            last_run = (
                datetime.now(timezone.utc) - timedelta(days=int(joe_config.INITIAL_FETCH_DAYS))
            ).strftime(DATE_FORMAT)
            logging.info(f"No checkpoint found. Using initial fetch date: {last_run}")

        current_time = datetime.now(timezone.utc).strftime(DATE_FORMAT)

        verdicts = joe_config.JOE_ANALYSIS_VERDICTS.split(" & ")
        logging.info(f"Configured analysis verdicts: {verdicts}")

        analysis_list = joe_api.get_analysis_list(last_run, verdicts)
        if not analysis_list:
            logging.info("No analyses returned.")
            return

        logging.info(f"Number of analyses returned: {len(analysis_list)}")
        all_indicators = []
        for analysis in analysis_list:
            webid = analysis.get("webid", "")

            _, file_data = joe_api.download_analysis(webid, "irjsonfixed")
            if not file_data:
                logging.warning(f"No file data returned for analysis {webid}")
                continue

            json_file_data = loads(file_data)

            analysis_info = joe_api.get_analysis_info(webid)
            if not analysis_info or analysis_info.get("status") != "finished":
                logging.info(f"Analysis {webid} is not marked as finished. Skipping.")
                continue

            iocs = parse_analysis_data(json_file_data) or {}
            for key, values in iocs.items():
                if key in IOC_LIST and key in IOC_MAPPING_FUNCTION:
                    indicators = IOC_MAPPING_FUNCTION[key](values, analysis_info)
                    all_indicators.extend(indicators)
        submit_indicator(all_indicators)
        state.post(current_time)

    except Exception as ex:
        logging.error("An unexpected error occurred.")
        logging.error(f"Error: {ex}")
        logging.error(f"Traceback: {format_exc()}")
