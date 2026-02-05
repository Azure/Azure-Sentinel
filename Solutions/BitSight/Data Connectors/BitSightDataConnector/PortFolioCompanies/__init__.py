"""This __init__ file will be called once triggered is generated."""
import logging
import time

import azure.functions as func

from ..SharedCode.logger import applogger
from .bitsight_portfolio import BitSightPortFolio


def main(mytimer: func.TimerRequest) -> None:
    """Start the execution.

    Args:
        mytimer (func.TimerRequest): timer trigger
    """
    applogger.info("BitSight: PortFolioCompanies: Start processing...")
    start_time = time.time()
    bitsight_obj = BitSightPortFolio(start_time)
    bitsight_obj.get_companies_data_from_portfolio()
    end_time = time.time()
    applogger.info(
        "BitSight: time taken for data ingestion is {} seconds.".format(
            int(end_time - start_time)
        )
    )
    applogger.info("BitSight: PortFolioCompanies: execution completed.")
    if mytimer.past_due:
        logging.info("The timer is past due!")
