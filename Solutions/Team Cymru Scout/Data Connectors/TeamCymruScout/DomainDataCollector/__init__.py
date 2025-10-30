"""This __init__ file will be called once triggered is generated."""

import time

import azure.functions as func
from SharedCode.logger import applogger
from SharedCode import consts
from .domain_collector import DomainDataCollector


def main(mytimer: func.TimerRequest) -> None:
    """
    Start the execution.

    Args:
        mytimer (func.TimerRequest): The timer object that triggered the function.
    """
    start_time = time.time()
    applogger.info("{} DomainDataCollector: Execution Started".format(consts.LOGS_STARTS_WITH))
    domain_data_collector = DomainDataCollector()
    domain_data_collector.get_domain_data_into_sentinel()
    end_time = time.time()
    applogger.info("{} DomainDataCollector: Time taken to ingest domain data is {}".format(consts.LOGS_STARTS_WITH, end_time - start_time))
