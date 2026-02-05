"""This __init__ file will be called once triggered is generated."""

import time

import azure.functions as func
from SharedCode.logger import applogger
from SharedCode import consts
from .ip_collector import IPDataCollector


def main(mytimer: func.TimerRequest) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): The timer object that triggered the function.
    """
    start_time = time.time()
    applogger.info("{} IPDataCollector: Execution Started".format(consts.LOGS_STARTS_WITH))
    ip_data_collector = IPDataCollector()
    ip_data_collector.get_ip_data_into_sentinel()
    end_time = time.time()
    applogger.info("{} IPDataCollector: Time taken to ingest IP data is {}".format(consts.LOGS_STARTS_WITH, end_time - start_time))
