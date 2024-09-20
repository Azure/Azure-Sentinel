import datetime
import json
import logging
from Helpers.date_helper import DateHelper

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class CheckpointHelper:
    """Helper for checkpoint."""

    def initialize_new_checkpoint(self, checkpoint):
        """Initialize new interval of checkpoint.

        Args:
            checkpoint (json): checkpoint object

        Returns:
            json : Updated checkpoint.
        """
        try:
            utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
            start_date = checkpoint["first_endtime"]
            mimecast_start_date = datetime.datetime.strptime(start_date, TIME_FORMAT) + datetime.timedelta(seconds=1)
            checkpoint["start_time"] = mimecast_start_date.strftime(TIME_FORMAT)
            end_date = datetime.datetime.fromisoformat(utc_timestamp) - datetime.timedelta(seconds=15)
            mimecast_end_date = end_date.strftime(TIME_FORMAT)
            checkpoint["end_time"] = mimecast_end_date
            checkpoint["first_endtime"] = mimecast_end_date
            return checkpoint
        except Exception as e:
            logging.error("Unknown Exception raised while initializing new checkpoint.")
            raise e

    def get_checkpoint(self, checkpoint: str):
        """checkpoint helper to parse checkpoint.

        Args:
            checkpoint (str): checkpoint

        Returns:
            json : parsed checkpoint
        """
        try:
            # datetime manipulation is done to assure there is neither duplicate nor missing logs
            if checkpoint != "":
                checkpoint = json.loads(checkpoint)
            else:
                checkpoint = {}
            utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
            if checkpoint.get("first_endtime") is None:
                start_date = DateHelper.get_utc_time_in_past(days=7)
                mimecast_start_date = datetime.datetime.strptime(start_date, TIME_FORMAT) + datetime.timedelta(
                    seconds=1
                )
                checkpoint["start_time"] = mimecast_start_date.strftime(TIME_FORMAT)
                end_date = datetime.datetime.fromisoformat(utc_timestamp) - datetime.timedelta(seconds=15)
                mimecast_end_date = end_date.strftime(TIME_FORMAT)
                checkpoint["end_time"] = mimecast_end_date
                checkpoint["first_endtime"] = mimecast_end_date

            elif checkpoint["start_time"] >= checkpoint["end_time"]:
                checkpoint = self.initialize_new_checkpoint(checkpoint)

            return checkpoint
        except Exception as e:
            logging.error("Unknown Exception raised while getting checkpoint.")
            raise e
