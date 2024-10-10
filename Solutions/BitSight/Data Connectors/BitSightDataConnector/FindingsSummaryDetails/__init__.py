"""This __init__ file will be called once triggered is generated."""
import time

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .bitsight_findings_summary import BitSightFindingsSummary


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    start_time = time.time()
    applogger.info(
        "{} {} Start processing...".format(
            consts.LOGS_STARTS_WITH, consts.FINDINGS_SUMMARY_FUNC_NAME
        )
    )
    finding_summary_obj = BitSightFindingsSummary(start_time)
    finding_summary_obj.get_findings_summary_data_into_sentinel()
    end = time.time()
    applogger.info(
        "{} {} time taken for data ingestion is {} sec".format(
            consts.LOGS_STARTS_WITH, consts.FINDINGS_SUMMARY_FUNC_NAME, int(end - start_time)
        )
    )
    applogger.info(
        "{} {} execution completed.".format(
            consts.LOGS_STARTS_WITH, consts.FINDINGS_SUMMARY_FUNC_NAME
        )
    )
    if mytimer.past_due:
        applogger.info("The timer is past due!")
