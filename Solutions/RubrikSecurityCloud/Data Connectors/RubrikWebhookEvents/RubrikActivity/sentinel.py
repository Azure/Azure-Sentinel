"""This file contains MicrosoftSentinel class which posts data via the Log Ingestion API."""
import inspect
import time
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential, AzureAuthorityHosts
from azure.monitor.ingestion import LogsIngestionClient
from ..shared_code.consts import (
    LOGS_STARTS_WITH,
    LOG_FORMAT,
    AZURE_DATA_COLLECTION_ENDPOINT,
    SCOPE,
    MAX_RETRIES,
    RETRYABLE_STATUS,
)
from ..shared_code.logger import applogger
from ..shared_code.rubrik_exception import (
    RubrikException,
    RubrikAuthenticationException,
)

FUNCTION_NAME = "RubrikActivity"


class MicrosoftSentinel:
    """Posts data into a Log Analytics custom table via the Log Ingestion API."""

    def __init__(self) -> None:
        """Initialize the LogsIngestionClient with cloud-aware credentials."""
        __method_name = inspect.currentframe().f_code.co_name
        self.endpoint = AZURE_DATA_COLLECTION_ENDPOINT
        self.scope = SCOPE
        is_gov = ".us" in (self.scope or "").lower() or ".us" in (self.endpoint or "").lower()
        try:
            if is_gov:
                credential = DefaultAzureCredential(
                    authority=AzureAuthorityHosts.AZURE_GOVERNMENT
                )
                credential_scopes = ["https://monitor.azure.us//.default"]
            else:
                credential = DefaultAzureCredential()
                credential_scopes = ["https://monitor.azure.com//.default"]
            self.client = LogsIngestionClient(
                endpoint=self.endpoint,
                credential=credential,
                credential_scopes=credential_scopes,
            )
        except Exception as err:
            applogger.error(
                LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
            )
            raise RubrikAuthenticationException(
                "Failed to initialize LogsIngestionClient: {}".format(err)
            )

    def post_data(self, events, stream_name, rule_id):
        """Upload events to the given DCR stream with bounded retry.

        Args:
            events (list): list of event dicts to ingest.
            stream_name (str): DCR stream name (Custom-{TableName}).
            rule_id (str): DCR immutable id.

        Raises:
            RubrikException: on non-retryable errors or after exhausting retries.
        """
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug(
            LOG_FORMAT.format(
                LOGS_STARTS_WITH,
                FUNCTION_NAME,
                __method_name,
                "Uploading batch of {} event(s) to stream {} (rule_id={}).".format(
                    len(events), stream_name, rule_id
                ),
            )
        )
        attempt = 0
        while True:
            try:
                self.client.upload(
                    rule_id=rule_id, stream_name=stream_name, logs=events
                )
                applogger.info(
                    LOG_FORMAT.format(
                        LOGS_STARTS_WITH,
                        FUNCTION_NAME,
                        __method_name,
                        "Successfully posted {} event(s) to stream {} on attempt {}.".format(
                            len(events), stream_name, attempt + 1
                        ),
                    )
                )
                return
            except HttpResponseError as err:
                status = getattr(err, "status_code", None)
                if status in RETRYABLE_STATUS and attempt < MAX_RETRIES:
                    attempt += 1
                    backoff = 2 ** attempt
                    applogger.warning(
                        LOG_FORMAT.format(
                            LOGS_STARTS_WITH,
                            FUNCTION_NAME,
                            __method_name,
                            "Retryable status {} on attempt {}; sleeping {}s.".format(
                                status, attempt, backoff
                            ),
                        )
                    )
                    time.sleep(backoff)
                    continue
                if status == 401 and attempt < MAX_RETRIES:
                    attempt += 1
                    backoff = 2 ** attempt
                    applogger.warning(
                        LOG_FORMAT.format(
                            LOGS_STARTS_WITH,
                            FUNCTION_NAME,
                            __method_name,
                            "Unauthorized (401) on attempt {}; sleeping {}s before retry.".format(
                                attempt, backoff
                            ),
                        )
                    )
                    time.sleep(backoff)
                    continue
                applogger.error(
                    LOG_FORMAT.format(
                        LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err
                    )
                )
                raise RubrikException(
                    "Log Ingestion API error (status={}): {}".format(status, err)
                )
            except Exception as err:
                applogger.error(
                    LOG_FORMAT.format(
                        LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err
                    )
                )
                raise RubrikException(
                    "Unexpected error while posting data to Sentinel: {}".format(err)
                )
