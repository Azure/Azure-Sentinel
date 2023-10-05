"""init file for Cofense to sentinel."""
import datetime
import logging
import azure.functions as func
from ..CofenseToSentinel import cofense_to_sentinel


async def main(mytimer: func.TimerRequest) -> None:
    """Driver method for Cofense to sentinel."""
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    cofense_to_sentinel_obj = cofense_to_sentinel.CofenseIntelligence()
    await cofense_to_sentinel_obj.get_cofense_data_post_to_sentinel()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
