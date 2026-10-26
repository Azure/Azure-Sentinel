"""This module contains the CyjaxIOCHelper class for IOC collection, enrichment, and orchestration."""

import inspect
import json
import time
from datetime import datetime, timedelta, timezone
from SharedCode import consts
from SharedCode.logger import applogger
from SharedCode.exceptions import (
    CyjaxException,
    CyjaxTimeoutException,
    CyjaxAuthenticationException,
)
from SharedCode.cyjax_client import CyjaxClient
from SharedCode.cyjax_to_stix_mapping import map_cyjax_ioc_to_stix
from SharedCode.sentinel import MicrosoftSentinel
from SharedCode.state_manager import StateManager


class CyjaxIOCHelper:
    """Orchestrates the full Cyjax IOC collection, enrichment, STIX mapping, and upload flow.

    This class handles:
    - Fetching IOCs from the Cyjax API page by page
    - Enriching each IOC with additional context
    - Mapping IOC + enrichment data to STIX 2.1 indicators
    - Uploading indicators to Microsoft Sentinel via Upload Indicator API
    - Logging failed enrichment lookups to a custom error table
    - Managing checkpoints for incremental fetching
    - Handling function timeout at 9:30 minutes
    """

    def __init__(self, start_time):
        """Initialize the CyjaxIOCHelper with required clients and state.

        Args:
            start_time (int): The Unix timestamp when the function started.
        """
        self.start_time = start_time
        self.log_format = consts.LOG_FORMAT
        self.cyjax_client = CyjaxClient()
        self.sentinel_client = MicrosoftSentinel()
        self.state_manager = StateManager(
            connection_string=consts.CONN_STRING,
            file_path=consts.CHECKPOINT_FILE,
            share_name=consts.FILE_SHARE_NAME,
        )
        self.total_fetched = 0
        self.total_enriched = 0
        self.total_indicators = 0
        self.total_success = 0
        self.total_failed = 0
        self.total_mapping_errors = 0

    def _check_timeout(self):
        """Check if the function is approaching the 9:30 minute timeout.

        Raises:
            CyjaxTimeoutException: If the function has been running for more than 570 seconds.
        """
        elapsed = time.time() - self.start_time
        if elapsed >= consts.FUNCTION_APP_TIMEOUT_SECONDS:
            applogger.warning(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    "_check_timeout",
                    consts.FUNCTION_NAME,
                    "Function approaching timeout at {} seconds. Saving checkpoint and exiting.".format(int(elapsed)),
                )
            )
            raise CyjaxTimeoutException("Function timeout reached at {} seconds".format(int(elapsed)))

    def _get_checkpoint(self):
        """Retrieve the checkpoint data from Azure File Share.

        Returns:
            dict: Checkpoint data with 'since', 'until', and 'page' keys,
                  or None if no checkpoint exists.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint_data = self.state_manager.get()
            if checkpoint_data:
                checkpoint = json.loads(checkpoint_data)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Checkpoint found: {}".format(checkpoint),
                    )
                )
                return checkpoint
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "No checkpoint found. Starting fresh.",
                )
            )
            return None
        except json.JSONDecodeError as json_err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    consts.JSON_DECODE_ERROR_MSG.format(json_err),
                )
            )
            return None
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            return None

    def _format_timestamp(self, timestamp):
        """Format timestamp to ISO8601 compliance.

        Args:
            timestamp (str): Input timestamp string that may need formatting.

        Returns:
            str: Formatted timestamp in ISO8601 format.
        """
        if not timestamp:
            return None

        # Convert timezone format +0000 to Z for ISO8601 compliance
        if timestamp.endswith("+0000"):
            return timestamp.replace("+0000", "Z")
        # Ensure other timezone formats are handled
        elif "+" in timestamp and not timestamp.endswith("Z"):
            # Split at the + and remove colon if present
            parts = timestamp.split("+")
            if len(parts) == 2:
                tz = parts[1].replace(":", "")
                return f"{parts[0]}+{tz}"

        return timestamp

    def _save_checkpoint(self, since, until, page):
        """Save the checkpoint data to Azure File Share.

        Args:
            since (str): Start datetime for the current fetch window (ISO8601).
            until (str): End datetime for the current fetch window (ISO8601).
            page (int): Current page number within the window.
        """
        __method_name = inspect.currentframe().f_code.co_name
        checkpoint = {
            "since": since,
            "until": until,
            "page": page,
        }
        try:
            self.state_manager.post(json.dumps(checkpoint))
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "Checkpoint saved: {}".format(checkpoint),
                )
            )
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "Error saving checkpoint: {}".format(err),
                )
            )

    def _validate_environment_variables(self):
        """Validate that all required environment variables are set.

        Raises:
            CyjaxException: If any required environment variable is missing.
        """
        __method_name = inspect.currentframe().f_code.co_name
        required_vars = {
            "CYJAX_ACCESS_TOKEN": consts.CYJAX_ACCESS_TOKEN,
            "CYJAX_BASE_URL": consts.CYJAX_BASE_URL,
            "AZURE_CLIENT_ID": consts.AZURE_CLIENT_ID,
            "AZURE_CLIENT_SECRET": consts.AZURE_CLIENT_SECRET,
            "AZURE_TENANT_ID": consts.AZURE_TENANT_ID,
            "WORKSPACE_ID": consts.WORKSPACE_ID,
            "AzureWebJobsStorage": consts.CONN_STRING,
        }
        missing = [key for key, val in required_vars.items() if not val]
        if missing:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "Required environment variables are not configured. Check application settings.",
                )
            )
            raise CyjaxException("Missing required environment variables: {}".format(", ".join(missing)))
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "All required environment variables validated.",
            )
        )

    def collect_and_enrich_iocs(self, since, until, page):
        """Fetch a page of IOCs and enrich each one.

        Args:
            since (str): Start datetime (ISO8601).
            until (str): End datetime (ISO8601).
            page (int): Page number to fetch.

        Returns:
            tuple: (list of merged IOC+enrichment dicts, raw IOC list)

        Observability:
            Updates self.total_fetched with the count of raw IOCs retrieved.
            Updates self.total_enriched with the count of IOCs successfully enriched.
        """
        __method_name = inspect.currentframe().f_code.co_name
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Fetching IOCs: since={}, until={}, page={}".format(since, until, page),
            )
        )
        query = consts.IOC_QUERY if consts.IOC_QUERY else None
        indicator_types = None
        if consts.INDICATOR_TYPE:
            requested = [t.strip() for t in consts.INDICATOR_TYPE.split(",") if t.strip()]
            allowed_lower = {a.lower(): a for a in consts.ALLOWED_INDICATOR_TYPES}
            invalid = [t for t in requested if t.lower() not in allowed_lower]
            if invalid:
                applogger.warning(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Invalid indicator types ignored: {}. Allowed: {}".format(
                            invalid, consts.ALLOWED_INDICATOR_TYPES
                        ),
                    )
                )
            valid = [allowed_lower[t.lower()] for t in requested if t.lower() in allowed_lower]
            indicator_types = ",".join(valid) if valid else None
        ioc_list = self.cyjax_client.get_indicators(
            since=since,
            until=until,
            page=page,
            query=query,
            indicator_types=indicator_types,
        )

        if not ioc_list:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "No IOCs returned for page {}".format(page),
                )
            )
            return [], []

        self.total_fetched += len(ioc_list)
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Fetched {} IOCs on page {} (total fetched so far: {})".format(len(ioc_list), page, self.total_fetched),
            )
        )

        merged_records = []

        if not consts.ENABLE_ENRICHMENT:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "Enrichment disabled (ENABLE_ENRICHMENT=false). Skipping enrichment for page {}.".format(page),
                )
            )
            merged_records = [{"ioc_data": ioc, "enrichment_data": None} for ioc in ioc_list]
            return merged_records, ioc_list

        enriched_values = []
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Enriching {} IOCs of page {}".format(len(ioc_list), page),
            )
        )
        for ioc in ioc_list:
            self._check_timeout()
            ioc_value = ioc.get("value", "")
            enrichment_data = None

            try:
                enrichment_data = self.cyjax_client.get_enrichment(ioc_value)
                self.total_enriched += 1
                enriched_values.append(ioc_value)
            except CyjaxAuthenticationException as auth_err:
                # Authentication failures will affect all IOCs - stop immediately
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Enrichment authentication failed: {}. Stopping enrichment for all IOCs.".format(auth_err),
                    )
                )
                raise
            except Exception as enrich_err:
                applogger.warning(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Enrichment failed for IOC value={}: {}. Continuing.".format(ioc_value, enrich_err),
                    )
                )

            merged_records.append({"ioc_data": ioc, "enrichment_data": enrichment_data})

        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Enrichment complete for page {}. Succeeded: {} {}, Failed: {}".format(
                    page,
                    len(enriched_values),
                    enriched_values,
                    len(ioc_list) - len(enriched_values),
                ),
            )
        )

        return merged_records, ioc_list

    def process_batch(self, merged_records):
        """Map merged IOC+enrichment records to STIX and upload to Sentinel.

        STIX indicators are uploaded via sentinel_client.upload_indicators(), which internally
        sub-batches at consts.STIX_BATCH_SIZE (100) to comply with the Microsoft Upload
        Indicators API limit. All sub-batches must succeed before the caller advances the
        checkpoint; on any failure the caller should retry the full page.

        Args:
            merged_records (list): List of dicts with 'ioc_data' and 'enrichment_data'.

        Returns:
            dict: Upload result with 'success_count', 'failure_count', 'failed_indicators'.

        Observability:
            Updates self.total_mapping_errors for IOCs that fail STIX mapping.
        """
        __method_name = inspect.currentframe().f_code.co_name
        stix_indicators = []

        for record in merged_records:
            try:
                stix_obj = map_cyjax_ioc_to_stix(
                    ioc_data=record["ioc_data"],
                    enrichment_data=record["enrichment_data"],
                )
                if stix_obj:
                    stix_indicators.append(stix_obj)
            except CyjaxException as map_err:
                self.total_mapping_errors += 1
                applogger.warning(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Skipping IOC due to mapping error: {}".format(map_err),
                    )
                )

        if not stix_indicators:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    consts.FUNCTION_NAME,
                    "No valid STIX indicators to upload.",
                )
            )
            return {"success_count": 0, "failure_count": 0, "failed_indicators": []}

        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Uploading {} STIX indicators to Sentinel in batches of {}".format(
                    len(stix_indicators), consts.STIX_BATCH_SIZE
                ),
            )
        )

        result = self.sentinel_client.upload_indicators(stix_indicators)
        return result

    def run(self):
        """Orchestrate the full Cyjax IOC collection, enrichment, mapping, and upload flow.

        Raises:
            CyjaxTimeoutException: If the function approaches the 9:30 minute timeout.
            CyjaxException: If a critical error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Starting Cyjax IOC ingestion run.",
            )
        )

        self._validate_environment_variables()

        checkpoint = self._get_checkpoint()
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if checkpoint:
            since = checkpoint.get("since")
            until = checkpoint.get("until")
            page = checkpoint.get("page", 1)
        else:
            lookback_days = consts.LOOKBACK_DAYS
            if lookback_days < 1 or lookback_days > 7:
                applogger.warning(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "LOOKBACK_DAYS {} is out of range (1-7). Defaulting to 1.".format(lookback_days),
                    )
                )
                lookback_days = 1
            lookback = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            since = lookback.strftime("%Y-%m-%dT%H:%M:%SZ")
            until = now_utc
            page = 1

        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                "Processing window: since={}, until={}, starting page={}".format(since, until, page),
            )
        )

        while True:
            self._check_timeout()

            # Handle page 100 limit: reset to page 1 with new timestamp
            if page > consts.CYJAX_MAX_PAGE:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Reached maximum page limit ({}). Resetting to page 1 with new timestamp.".format(
                            consts.CYJAX_MAX_PAGE
                        )
                        + " Previous window: since={}, until={}".format(since, until),
                    )
                )
                # Store current until as new since, update until to current time
                new_since = until
                new_until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "New window after page reset: since={}, until={}".format(new_since, new_until),
                    )
                )
                since = new_since
                until = new_until
                page = 1
                # Save checkpoint with new timestamp before making API call
                self._save_checkpoint(since, until, page)

            merged_records, raw_iocs = self.collect_and_enrich_iocs(since, until, page)

            # Store the last record's time for potential page reset
            if raw_iocs and len(raw_iocs) > 0:
                # Get the timestamp from the last record in the page
                last_ioc = raw_iocs[-1]
                # Get discovered_at timestamp and format it
                discovered_at = self._format_timestamp(last_ioc.get("discovered_at"))
                self.last_record_time = discovered_at or until  # fallback to current until if no timestamp found

            if merged_records:
                result = self.process_batch(merged_records)
                attempted = result["success_count"] + result["failure_count"]
                self.total_indicators += attempted
                self.total_success += result["success_count"]
                self.total_failed += result["failure_count"]
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Page {} ingestion complete. Attempted: {}, Succeeded: {}, Failed: {}".format(
                            page,
                            attempted,
                            result["success_count"],
                            result["failure_count"],
                        ),
                    )
                )

                # If all indicators failed, this indicates a critical error (auth, config, etc.)
                # Stop execution to prevent wasting resources and allow investigation
                if attempted > 0 and result["success_count"] == 0:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            consts.FUNCTION_NAME,
                            "All {} indicators failed on page {}. Stopping execution to prevent further failures. "
                            "Check authentication, permissions, and configuration.".format(attempted, page),
                        )
                    )
                    raise CyjaxException(
                        "All {} indicators failed on page {}. This indicates a critical error "
                        "(authentication, permissions, or configuration). Check logs for details.".format(
                            attempted, page
                        )
                    )

            if len(raw_iocs) < consts.CYJAX_PAGE_SIZE:
                # Empty page (0 items) or last partial page - window is complete
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        consts.FUNCTION_NAME,
                        "Last page reached (received {} < {} items). Window complete.".format(
                            len(raw_iocs), consts.CYJAX_PAGE_SIZE
                        ),
                    )
                )
                new_since = until
                new_until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                self._save_checkpoint(new_since, new_until, 1)
                break

            # Full page returned - save checkpoint and continue to next page
            page += 1
            self._save_checkpoint(since, until, page)

        applogger.info(
            self.log_format.format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.FUNCTION_NAME,
                (
                    "Run complete. "
                    "Fetched: {}, Enriched: {}, "
                    "Mapping errors: {}, "
                    "Attempted ingestion: {}, Succeeded: {}, Failed: {}"
                ).format(
                    self.total_fetched,
                    self.total_enriched,
                    self.total_mapping_errors,
                    self.total_indicators,
                    self.total_success,
                    self.total_failed,
                ),
            )
        )
