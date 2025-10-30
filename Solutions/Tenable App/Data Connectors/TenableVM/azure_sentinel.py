"""This file contains MicrosoftSentinel class which is used to post data into log analytics workspace."""

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
import logging


logs_starts_with = "TenableVM"
function_name = "azure_sentinel"


class MicrosoftSentinel:
    """MicrosoftSentinel class is used to post data into log Analytics workspace."""

    def __init__(self, azure_ingestion_client) -> None:
        """Intialize instance variables for MicrosoftSentinel class."""
        self._ingestion_client = azure_ingestion_client

    def post_data(self, events, table_name, dcr_rule_id):
        """Post the given events into the specified table in Log Analytics workspace.

        Args:
            events (list): A list of events to be posted into log analytics workspace.
            table_name (str): The name of the table in Log Analytics workspace.
            dcr_rule_id (str): The rule id of the data collection rule.
        Raises:
            ClientAuthenticationError: If the provided credentials are invalid or expired.
            HttpResponseError: If any error occurs while uploading events to sentinel.
            Exception: If any unexpected error occurs while uploading events to sentinel.
        """
        try:
            if not isinstance(events, list):
                events = list(events)
            dcr_stream = "Custom-{}".format(table_name)
            self._ingestion_client.upload(rule_id=dcr_rule_id, stream_name=dcr_stream, logs=events)
        except ClientAuthenticationError as error:
            logging.error(
                f"{logs_starts_with} {function_name}: Error while uploading events to sentinel due "
                f"to expired or invalid credentials, Error: {error}.")
            raise Exception(
                f"Error while uploading events to sentinel due to expired or invalid credentials, Error: {error}.")
        except HttpResponseError as error:
            logging.error(
                f"{logs_starts_with} {function_name}: Http Response Error while uploading events to sentinel, Error: {error}.")
            raise Exception(
                f"Http Response Error while uploading events to sentinel, Error: {error}.")
        except Exception as error:
            logging.error(
                f"{logs_starts_with} {function_name}: Unexpected Error while uploading events to sentinel, Error: {error}.")
            raise Exception(
                f"Unexpected Error while uploading events to sentinel, Error: {error}.")
