"""This file contains implementation to ingest Dataminr RTAP alert data into sentinel."""
import inspect
from .sentinel import MicrosoftSentinel
from shared_code.consts import (
    LOGS_STARTS_WITH,
    ANOMALY_LOG_TYPE,
    RANSOMWARE_LOG_TYPE,
    THREATHUNT_LOG_TYPE,
)
from shared_code.rubrik_exception import RubrikException
from shared_code.logger import applogger


class Rubrik:
    """This class contains methods to get data from request body pushed via Rubrik Webhook and ingest into Sentinel."""

    def __init__(self) -> None:
        """Initialize instance variables for class."""
        self.logs_starts_with = LOGS_STARTS_WITH
        self.microsoftsentinel = MicrosoftSentinel()
        self.error_logs = "{}(method={}) {}"
        self.check_environment_var_existance()

    def check_environment_var_existance(self):
        """To verify that all required environment variables exist.

        Raises:
            RubrikException: raise exception if any of the required environment variable is not set.
        """
        __method_name = inspect.currentframe().f_code.co_name
        env_var = [
            {"Anomalies_table_name": ANOMALY_LOG_TYPE},
            {"RansomwareAnalysis_table_name": RANSOMWARE_LOG_TYPE},
            {"ThreatHunts_table_name": THREATHUNT_LOG_TYPE},
        ]
        try:
            applogger.debug(
                "{}(method={}) Checking environment variables are exist or not.".format(
                    self.logs_starts_with, __method_name
                )
            )
            for i in env_var:
                key, val = next(iter(i.items()))
                if val is None:
                    raise RubrikException(
                        "{} is not set in the environment please set the environment variable.".format(
                            key
                        )
                    )
            applogger.debug(
                "{}(method={}) All custom environment variables exist.".format(
                    self.logs_starts_with, __method_name
                )
            )
        except RubrikException as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise RubrikException(err)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise RubrikException(err)

    def post_data_to_sentinel(self, data):
        """To post data received via Rubrik Webhook into Sentinel.

        Args:
            data (dict): data received via Rubrik Webhook.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            sentinel_obj = MicrosoftSentinel()
            body = data.get("data")
            log_type = data.get("log_type")
            sentinel_obj.post_data(body, log_type)
        except Exception as err:
            applogger.error(
                "{}".format(
                    self.error_logs.format(self.logs_starts_with, __method_name, err)
                )
            )
            raise RubrikException(err)
