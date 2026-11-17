"""This file ingests Rubrik webhook data into Sentinel via the Log Ingestion API."""
import inspect
import json
from .sentinel import MicrosoftSentinel
from shared_code.consts import (
    LOGS_STARTS_WITH,
    LOG_FORMAT,
    AZURE_DATA_COLLECTION_ENDPOINT,
    DCR_WEBHOOK_RULE_ID,
    DCR_EVENTS_RULE_ID,
    ANOMALY_LOG_TYPE,
    RANSOMWARE_LOG_TYPE,
    THREATHUNT_LOG_TYPE,
    EVENTS_LOG_TYPE,
    VIOLATION_LOG_TYPE,
)
from shared_code.rubrik_exception import RubrikException
from shared_code.logger import applogger

FUNCTION_NAME = "RubrikActivity"


class Rubrik:
    """Ingests data received via the Rubrik Webhook into Sentinel."""

    def __init__(self) -> None:
        """Initialize instance variables and validate environment variables."""
        self.microsoftsentinel = MicrosoftSentinel()
        self.check_environment_var_existance()

    def check_environment_var_existance(self):
        """Verify all required environment variables are set.

        Raises:
            RubrikException: if any required environment variable is missing.
        """
        __method_name = inspect.currentframe().f_code.co_name
        env_var = [
            {"Anomalies_table_name": ANOMALY_LOG_TYPE},
            {"RansomwareAnalysis_table_name": RANSOMWARE_LOG_TYPE},
            {"ThreatHunts_table_name": THREATHUNT_LOG_TYPE},
            {"Events_table_name": EVENTS_LOG_TYPE},
            {"Violation_table_name": VIOLATION_LOG_TYPE},
            {"AZURE_DATA_COLLECTION_ENDPOINT": AZURE_DATA_COLLECTION_ENDPOINT},
            {"DCR_WEBHOOK_RULE_ID": DCR_WEBHOOK_RULE_ID},
            {"DCR_EVENTS_RULE_ID": DCR_EVENTS_RULE_ID},
        ]
        try:
            for item in env_var:
                key, val = next(iter(item.items()))
                if val is None:
                    raise RubrikException(
                        "{} is not set in the environment; please set the "
                        "environment variable.".format(key)
                    )
            applogger.info(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH,
                    FUNCTION_NAME,
                    __method_name,
                    "All required environment variables exist.",
                )
            )
        except RubrikException as err:
            applogger.error(
                LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
            )
            raise

    def post_data_to_sentinel(self, data):
        """Post data received via Rubrik Webhook into Sentinel.

        Args:
            data (dict): payload with keys data, log_type, stream_name, rule_id.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = data.get("data")
            stream_name = data.get("stream_name")
            rule_id = data.get("rule_id")
            log_type = data.get("log_type")

            applogger.info(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH,
                    FUNCTION_NAME,
                    __method_name,
                    "Processing payload for log_type={}, rule_id={}.".format(
                        log_type, rule_id
                    ),
                )
            )

            if isinstance(body, str):
                applogger.debug(
                    LOG_FORMAT.format(
                        LOGS_STARTS_WITH,
                        FUNCTION_NAME,
                        __method_name,
                        "Parsing webhook payload from JSON string (length={} bytes).".format(
                            len(body)
                        ),
                    )
                )
                body = json.loads(body)

            events = body if isinstance(body, list) else [body]
            applogger.debug(
                LOG_FORMAT.format(
                    LOGS_STARTS_WITH,
                    FUNCTION_NAME,
                    __method_name,
                    "Posting {} event(s) to table {} via Log Ingestion API.".format(
                        len(events), log_type
                    ),
                )
            )
            self.microsoftsentinel.post_data(events, stream_name, rule_id)
        except json.JSONDecodeError as err:
            applogger.error(
                LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
            )
            raise RubrikException("Invalid JSON in webhook payload: {}".format(err))
        except RubrikException:
            raise
        except Exception as err:
            applogger.error(
                LOG_FORMAT.format(LOGS_STARTS_WITH, FUNCTION_NAME, __method_name, err)
            )
            raise RubrikException(str(err))
