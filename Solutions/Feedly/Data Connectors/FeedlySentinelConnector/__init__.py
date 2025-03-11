import logging

from azure.functions import TimerRequest
from FeedlySentinelConnector.worker import FeedlySentinelWorker


def main(mytimer: TimerRequest) -> None:
    if mytimer.past_due:
        logging.warning("The timer is past due!")

    FeedlySentinelWorker.from_env().run()
