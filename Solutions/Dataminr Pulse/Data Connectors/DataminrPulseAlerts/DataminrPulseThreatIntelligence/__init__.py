"""init file for Dataminr Pulse Threat Intelligence."""
import datetime
import logging
import azure.functions as func
from .dataminr_pulse_threat_intelligence import DataMinrPulseThreatIntelligence


async def main(mytimer: func.TimerRequest) -> None:
    """Driver method for Dataminr Pulse Threat Intelligence."""
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    dataminr_pulse_threat_intelligence_obj = DataMinrPulseThreatIntelligence()
    await dataminr_pulse_threat_intelligence_obj.get_dataminr_pulse_data_post_to_sentinel()
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
