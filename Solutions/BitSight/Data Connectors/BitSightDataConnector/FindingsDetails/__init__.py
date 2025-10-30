"""This __init__ file will be called once triggered is generated."""
import time
from .bitsight_findings import BitSightFindings
from ..SharedCode.logger import applogger
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    applogger.info("BitSight: Findings_Details: Start processing...")
    start = time.time()
    bitsightfindings_obj = BitSightFindings(start)
    bitsightfindings_obj.get_bitsight_data_into_sentinel()
    end = time.time()
    applogger.info("BitSight: time taken for data ingestion is {} sec".format(int(end-start)))
    applogger.info("BitSight: Findings_Details: execution completed.")
    if mytimer.past_due:
        applogger.info('The timer is past due!')
