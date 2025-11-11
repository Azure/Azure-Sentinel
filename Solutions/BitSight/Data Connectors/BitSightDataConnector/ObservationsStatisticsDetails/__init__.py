"""This __init__ file will be called once triggered is generated."""
import time

import azure.functions as func

from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.bitsight_statistics import BitSightStatistics


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    start = time.time()
    applogger.info(
        "{} {} Start processing...".format(
            consts.LOGS_STARTS_WITH, consts.ALERT_GRAPH_STATISTICS_FUNC_NAME
        )
    )
    statistics_type = consts.OBSERVATIONS_STATISTICS_TYPE
    applogger.info(
        "{} {} Statistics type is {}".format(
            consts.LOGS_STARTS_WITH, consts.ALERT_GRAPH_STATISTICS_FUNC_NAME, statistics_type
        )
    )
    bitsightstatistics_obj = BitSightStatistics(start, statistics_type=statistics_type)
    bitsightstatistics_obj.get_bitsight_data_into_sentinel()
    end = time.time()
    applogger.info(
        "{} {} time taken for data ingestion is {} sec".format(
            consts.LOGS_STARTS_WITH,
            consts.ALERT_GRAPH_STATISTICS_FUNC_NAME,
            int(end - start),
        )
    )
    applogger.info(
        "{} {} execution completed.".format(
            consts.LOGS_STARTS_WITH, consts.ALERT_GRAPH_STATISTICS_FUNC_NAME
        )
    )
    if mytimer.past_due:
        applogger.info('BitSight Connector: The timer is past due!')
