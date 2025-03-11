"""This __init__ file will be called once triggered is generated."""
import time

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .bitsight_companies import BitSightCompanies


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    start = time.time()
    applogger.info(
        "{} {} Start processing...".format(
            consts.LOGS_STARTS_WITH, consts.COMPANY_DETAIL_TABLE_NAME
        )
    )
    bitsightcompanies_obj = BitSightCompanies(start)
    bitsightcompanies_obj.get_bitsight_data_into_sentinel()
    end = time.time()
    applogger.info(
        "{} {} time taken for data ingestion is {} sec".format(
            consts.LOGS_STARTS_WITH,
            consts.COMPANY_DETAILS_FUNC_NAME,
            int(end - start),
        )
    )
    applogger.info(
        "{} {} execution completed.".format(
            consts.LOGS_STARTS_WITH, consts.COMPANY_DETAILS_FUNC_NAME
        )
    )
    if mytimer.past_due:
        applogger.info("The timer is past due!")
