"""Get GTI Alerts data and ingest into Microsoft Sentinel."""

import inspect
import re
import time

from SharedCode.utils import Utils
from SharedCode.logger import applogger
from SharedCode import consts
from SharedCode.exceptions import GTIRelevanceSystemAlertsException, GTIRelevanceSystemAlertsTimeoutException
from SharedCode.state_manager import StateManager
from SharedCode.sentinel import send_data_to_sentinel
from SharedCode.gti_client import GTIClient


CHECKPOINT_FILE_PATH = "gti_alerts_checkpoint"
FUNCTION_NAME = "RelevanceSystemAlerts"


class GTIRelevanceSystemAlertsHelper(Utils):
    """Helper class for ingesting Google Threat Intelligence alerts into Sentinel.

    Inherits from Utils for checkpoint and environment variable management.
    Orchestrates GTI API authentication, pagination, Sentinel ingestion,
    and checkpoint persistence.
    """

    def __init__(self, start_time: int) -> None:
        """Initialise the GTIRelevanceSystemAlertsHelper.

        Args:
            start_time (int): Unix epoch timestamp of function start (for timeout guard).
        """
        super().__init__(FUNCTION_NAME)
        self.start = start_time
        self.gti_client = GTIClient()
        self.checkpoint_obj = StateManager(
            consts.CONN_STRING, CHECKPOINT_FILE_PATH, consts.FILE_SHARE_NAME
        )

    def get_gti_alerts_in_sentinel(self):
        """Fetch GTI alerts and ingest them into Microsoft Sentinel.

        Reads the last checkpoint (timestamp and optional page token), fetches
        alerts from the GTI API using cursor-based pagination, sends alerts to
        Sentinel, and updates the checkpoint after each page.

        Raises:
            GTIRelevanceSystemAlertsTimeoutException: If approaching the Azure Function timeout limit.
            GTIRelevanceSystemAlertsException: For any unrecoverable error during the ingestion workflow.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_data = self.get_checkpoint_data(self.checkpoint_obj)
            if checkpoint_data:
                last_checkpoint = checkpoint_data.get("last_checkpoint")
                saved_page_token = checkpoint_data.get("page_token")
            else:
                last_checkpoint = self.get_start_date_of_data_fetching()
                saved_page_token = None

            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Starting GTI alerts ingestion from checkpoint: {}, resuming_page_token={}".format(
                        last_checkpoint, bool(saved_page_token)
                    ),
                )
            )

            self._fetch_and_ingest_alerts(last_checkpoint, saved_page_token)

        except GTIRelevanceSystemAlertsTimeoutException:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Function approaching 9:30-minute timeout limit, stopping gracefully.",
                )
            )
            return
        except GTIRelevanceSystemAlertsException:
            raise
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "Unexpected error during GTI alerts ingestion: {}".format(err)
            )

    def _build_filter_expression(self, last_checkpoint: str) -> str:
        """Build the GTI API filter expression combining the checkpoint time and optional user filter.

        The base filter is always: audit.update_time > "<checkpoint>".

        All audit.update_time conditions are stripped from the user-supplied
        GTI_FILTER_EXPRESSION regardless of operator (>, >=, ==, <=, <) and time
        format, then the remaining expression is AND-combined with the base filter.

        If the remaining user expression contains OR, the entire expression is
        wrapped in parentheses to preserve operator precedence (AND binds tighter
        than OR in the GTI API):

            user filter : 'severity_analysis.severity_level = "HIGH" AND state = "NEW" OR state = "TRIAGED"'
            effective   : 'audit.update_time > "<cp>" AND
                           (severity_analysis.severity_level = "HIGH" AND state = "NEW" OR state = "TRIAGED")'

        Args:
            last_checkpoint (str): ISO 8601 checkpoint timestamp.

        Returns:
            str: The combined filter expression ready to pass to the GTI API.
        """
        __method_name = inspect.currentframe().f_code.co_name
        base_filter = 'audit.update_time > "{}"'.format(last_checkpoint)
        user_filter = consts.GTI_FILTER_EXPRESSION.strip()

        if not user_filter:
            return base_filter

        # Remove every audit.update_time condition regardless of operator or time format.
        # Pattern matches: audit.update_time <op> "<any chars>"
        # Operators covered: >, >=, ==, <=, <, !=
        cleaned = re.sub(
            r'audit\.update_time\s*(?:>=|<=|==|!=|>|<)\s*"[^"]*"',
            '',
            user_filter,
            flags=re.IGNORECASE,
        )

        # Clean up dangling connectors INSIDE parentheses first.
        # e.g. "(state = "NEW" OR )" → "(state = "NEW")"
        # e.g. "( OR state = "NEW")" → "(state = "NEW")"
        cleaned = re.sub(r'\(\s*(?:AND|OR)\s+', '(', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+(?:AND|OR)\s*\)', ')', cleaned, flags=re.IGNORECASE)
        # Remove parentheses that are now empty: ()
        cleaned = re.sub(r'\(\s*\)', '', cleaned)
        # Remove unnecessary parentheses around a single expression with no OR.
        # e.g. "(state = "NEW")" → 'state = "NEW"'
        # Parens around OR expressions are kept to preserve precedence.
        cleaned = re.sub(
            r'\(([^()]*)\)',
            lambda m: m.group(1).strip() if not re.search(r'\bOR\b', m.group(1), re.IGNORECASE) else m.group(0),
            cleaned,
        )
        # Normalise leftover AND / OR connectors at the top level.
        # e.g. "AND  AND" → "AND", leading/trailing "AND"/"OR" → stripped.
        cleaned = re.sub(r'(?:\bAND\b\s*){2,}', 'AND ', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^\s*(?:AND|OR)\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*(?:AND|OR)\s*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()

        if removed_parts := re.findall(
            r'audit\.update_time\s*(?:>=|<=|==|!=|>|<)\s*"[^"]*"',
            user_filter,
            flags=re.IGNORECASE,
        ):
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Removed audit.update_time condition(s) from user filter: {}".format(removed_parts),
                )
            )

        if not cleaned:
            return base_filter

        # If the remaining expression contains OR, wrap it in parentheses to
        # preserve operator precedence when AND-combining with the base filter.
        if re.search(r'\bOR\b', cleaned, re.IGNORECASE):
            user_part = "({})".format(cleaned)
        else:
            user_part = cleaned

        combined = "{} AND {}".format(base_filter, user_part)
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                self.azure_function_name,
                "Combined filter expression: {}".format(combined),
            )
        )
        return combined

    def _check_timeout(self, page_number: int, last_checkpoint: str):
        """Raise a timeout exception if the function is approaching its execution limit.

        Args:
            page_number (int): Current page number (used for log context).
            last_checkpoint (str): Current checkpoint timestamp (used for log context).

        Raises:
            GTIRelevanceSystemAlertsTimeoutException: If the timeout threshold has been reached.
        """
        __method_name = inspect.currentframe().f_code.co_name
        if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Timeout guard triggered at page {}, checkpoint saved at: {}".format(
                        page_number, last_checkpoint
                    ),
                )
            )
            raise GTIRelevanceSystemAlertsTimeoutException(
                "Function timeout limit reached after page {}".format(page_number)
            )

    def _ingest_page_alerts(self, alerts: list, total_ingested: int, method_name: str) -> int:
        """Send a page of alerts to Sentinel and return the updated ingestion count.

        Args:
            alerts (list): Alerts retrieved from the current API page.
            total_ingested (int): Running count of ingested alerts before this page.
            method_name (str): Caller method name for log context.

        Returns:
            int: Updated total ingested count after this page.
        """
        if alerts:
            send_data_to_sentinel(alerts, consts.GTI_RELEVANCE_SYSTEM_ALERTS_TABLE_NAME)
            total_ingested += len(alerts)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    method_name,
                    self.azure_function_name,
                    "Ingested {} alerts, total so far: {}".format(len(alerts), total_ingested),
                )
            )
        return total_ingested

    def _save_page_checkpoint(self, alerts: list, next_page_token: str, last_checkpoint: str) -> str:
        """Persist the checkpoint after processing one API page.

        If there is a next page token the checkpoint retains the current
        ``last_checkpoint`` time plus the token so the next invocation can
        resume at the correct position.  On the final page the checkpoint
        is advanced to the last alert's ``audit.updateTime`` with no token.

        Args:
            alerts (list): Alerts from the current page.
            next_page_token (str | None): Continuation token from the API response.
            last_checkpoint (str): Current checkpoint timestamp.

        Returns:
            str: Updated ``last_checkpoint`` value (unchanged when a next page token exists).
        """
        if next_page_token:
            self.post_checkpoint_data(
                self.checkpoint_obj,
                {"last_checkpoint": last_checkpoint, "page_token": next_page_token},
            )
        else:
            if alerts:
                last_update_time = alerts[-1].get("audit", {}).get("updateTime", "")
                if last_update_time:
                    last_checkpoint = last_update_time
            self.post_checkpoint_data(
                self.checkpoint_obj,
                {"last_checkpoint": last_checkpoint},
            )
        return last_checkpoint

    def _fetch_and_ingest_alerts(self, last_checkpoint: str, saved_page_token: str):
        """Paginate through GTI alerts and ingest them into Sentinel.

        Checkpoint strategy
        -------------------
        After each page that has a next page token: save the checkpoint with
        the current ``last_checkpoint`` time and the new ``page_token``.  The
        time is NOT advanced yet — the next invocation will resume exactly at
        the saved page.

        After the final page (no next page token): advance ``last_checkpoint``
        to the last alert's audit.updateTime and save without a ``page_token``.

        If the checkpoint loaded at the start of this invocation contained a
        page token, both the filter expression AND the page token are passed to
        the first API call so the server can resume at the correct position.

        Args:
            last_checkpoint (str): ISO 8601 timestamp used as the filter baseline.
            saved_page_token (str | None): Page token from the checkpoint, if any.

        Raises:
            GTIRelevanceSystemAlertsTimeoutException: If approaching the Azure Function timeout limit.
            GTIRelevanceSystemAlertsException: For API errors or ingestion failures.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            filter_expr = self._build_filter_expression(last_checkpoint)
            page_token = saved_page_token
            page_number = 0
            total_ingested = 0

            while True:
                self._check_timeout(page_number, last_checkpoint)

                page_number += 1
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Fetching page {}, page_token_present={}".format(page_number, bool(page_token)),
                    )
                )

                response = self.gti_client.list_alerts(
                    filter_expr=filter_expr,
                    page_token=page_token,
                )

                alerts = response.get("alerts", [])
                next_page_token = response.get("nextPageToken")

                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Page {} received {} alerts, has_next_page={}".format(
                            page_number, len(alerts), bool(next_page_token)
                        ),
                    )
                )

                total_ingested = self._ingest_page_alerts(alerts, total_ingested, __method_name)
                last_checkpoint = self._save_page_checkpoint(alerts, next_page_token, last_checkpoint)

                if next_page_token:
                    page_token = next_page_token
                else:
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Pagination complete. Total alerts ingested: {}. Next checkpoint: {}".format(
                                total_ingested, last_checkpoint
                            ),
                        )
                    )
                    break

        except GTIRelevanceSystemAlertsTimeoutException:
            raise
        except GTIRelevanceSystemAlertsException:
            raise
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise GTIRelevanceSystemAlertsException(
                "Unexpected error during alert pagination and ingestion: {}".format(err)
            )
