import datetime
import logging
import azure.functions as func
from ..Helpers.date_helper import DateHelper
from ..Helpers.threat_intel_feed_request_helper import ThreatIntelFeedRequestHelper
from ..Models.Error.errors import MimecastRequestError, GraphAPIRequestError


def main(mytimer: func.TimerRequest, checkpoint: str) -> str:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    # datetime manipulation is done to assure there is neither duplicate nor missing logs
    start_date = checkpoint if checkpoint else DateHelper.get_utc_time_in_past(days=3)
    mimecast_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(seconds=1)
    mimecast_start_date = mimecast_start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    end_date = datetime.datetime.fromisoformat(utc_timestamp) - datetime.timedelta(seconds=15)
    mimecast_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S%z")

    threat_intel_feed_request_helper = ThreatIntelFeedRequestHelper()

    try:
        grid_feeds = threat_intel_feed_request_helper.get_threat_intel_feed(
            mimecast_start_date, mimecast_end_date, "malware_grid"
        )
    except MimecastRequestError as e:
        logging.error(
            "Failed to get TI logs from Mimecast.", extra={"request_id": threat_intel_feed_request_helper.request_id}
        )
        e.request_id = threat_intel_feed_request_helper.request_id
        raise e
    except Exception as e:
        logging.error("Unknown Exception raised.", extra={"request_id": threat_intel_feed_request_helper.request_id})
        raise e

    try:
        if grid_feeds:
            latest_feed = threat_intel_feed_request_helper.send_feeds_to_azure(grid_feeds)
            return latest_feed
        else:
            logging.info("There are no Regional Threat Intel Feeds for this period.")
            return mimecast_end_date
    except GraphAPIRequestError as e:
        logging.error("Failed to send TI logs.", extra={"request_id": threat_intel_feed_request_helper.request_id})
        e.request_id = threat_intel_feed_request_helper.request_id
        raise e
    except Exception as e:
        logging.error("Unknown Exception raised.", extra={"request_id": threat_intel_feed_request_helper.request_id})
        raise e
