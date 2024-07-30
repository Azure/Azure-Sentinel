"""Init File for InfoBloxParseRawIndicators."""

import datetime
import logging
import time
import azure.functions as func
from .parse_json_files import ParseJsonFiles
from ..SharedCode import consts
from ..SharedCode.logger import applogger


def main(mytimer: func.TimerRequest) -> None:
    """Infoblox Parse Json Main Function."""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    start = time.time()
    applogger.info(
        "{} : Function App started at {}".format(consts.LOGS_STARTS_WITH, datetime.datetime.fromtimestamp(start))
    )
    parse_json_files_obj = ParseJsonFiles(int(start))
    parse_json_files_obj.list_file_names_and_parse_to_complete_json()
    end = time.time()
    applogger.info(
        "{} : Function App ended at {}".format(consts.LOGS_STARTS_WITH, datetime.datetime.fromtimestamp(end))
    )
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
