"""This file contains MicrosoftSentinel class which is used to post data into log analytics workspace."""

import inspect
from azure.core.exceptions import HttpResponseError
from .logger import applogger
from . import consts
from .teamcymruscout_exception import (
    TeamCymruScoutException,
)


class MicrosoftSentinel:
    """MicrosoftSentinel class is used to post data into log Analytics workspace."""

    def __init__(self, azure_ingestion_client) -> None:
        """Intialize instance variables for MicrosoftSentinel class."""
        self.logs_start_with = "{}(MicrosoftSentinel)".format(consts.LOGS_STARTS_WITH)
        self._ingestion_client = azure_ingestion_client

    def post_data(self, events, table_name, dcr_rule_id):
        """Post the given events into the specified table in Log Analytics workspace.

        Args:
            events (list): A list of events to be posted into log analytics workspace.
            table_name (str): The name of the table in Log Analytics workspace.
            dcr_rule_id (str): The rule id of the data collection rule.
        Raises:
            TeamCymruScoutException: If an error occurs while posting the events into sentinel.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            dcr_stream = "Custom-{}".format(table_name)
            self._ingestion_client.upload(rule_id=dcr_rule_id, stream_name=dcr_stream, logs=events)
        except HttpResponseError as error:
            applogger.error(
                "{}(method={}) : Error while uploading events to sentinel, Error: {}.".format(
                    self.logs_start_with,
                    __method_name,
                    error,
                )
            )
            raise TeamCymruScoutException()
