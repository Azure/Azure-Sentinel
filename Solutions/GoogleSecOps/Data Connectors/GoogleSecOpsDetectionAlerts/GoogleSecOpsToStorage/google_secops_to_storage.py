"""Fetch detection alerts from Google SecOps and save to Azure File Share.

Polls the SecOps API for detection alerts and saves each response batch
to Azure File Share for durable buffering. The companion AzureStorageToSentinel
function monitors and ingests the files into Microsoft Sentinel.
"""

import inspect
import json
import time
from typing import Optional

from ..SharedCode import consts
from ..SharedCode.google_secops_client import GoogleSecOpsClient
from ..SharedCode.exceptions import GoogleSecOpsConnectorError
from ..SharedCode.google_auth import GoogleServiceAccountAuth
from ..SharedCode.logger import applogger
from ..SharedCode.state_manager import StateManager


class GoogleSecOpsToStorage:
    """Fetch detection batches from Google SecOps and save to Azure File Share."""

    def __init__(self) -> None:
        """Initialize Google SecOps client, checkpoint manager, and validate configuration."""
        self._auth = GoogleServiceAccountAuth()
        self._client = GoogleSecOpsClient(self._auth)
        self._checkpoint = StateManager(
            connection_string=consts.CONN_STRING,
            file_path=consts.CHECKPOINT_FILE_NAME,
            share_name=consts.FILE_SHARE_NAME,
        )

    def run(self) -> None:
        """Fetch detection batches from SecOps API and save to Azure File Share.

        Runs once per timer trigger. Fetches all available batches and updates checkpoint.
        """
        __method_name = inspect.currentframe().f_code.co_name
        page_start, page_token = self._checkpoint.resolve_initial_start_time()

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"Fetching: start={page_start[:10]}, token={page_token if page_token else 'no'}",
            )
        )

        batch_count = 0
        total_detections = 0

        try:
            for batch, next_token, next_start in self._client.poll_detection_batches(
                page_start_time=page_start,
                page_token=page_token,
                deadline_epoch=None,  # No deadline - run until window complete
            ):
                batch_count += 1

                # Save batch to file
                batch_detection_count = self._write_response_to_file(batch, batch_count)
                total_detections += batch_detection_count

                # Update checkpoint after successful save
                self._update_checkpoint(page_start, next_token, next_start)

            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Fetch cycle complete: batches={batch_count}, detections={total_detections}",
                )
            )

        except GoogleSecOpsConnectorError as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"CRITICAL: API error (batches={batch_count}): {exc}",
            )
            applogger.error(error_msg)
            raise
        except Exception as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"CRITICAL: Unexpected error (batches={batch_count}): {exc}",
            )
            applogger.error(error_msg)
            raise

    def _write_response_to_file(self, response: dict, index: int) -> int:
        """Save full API response to Azure File Share.

        Writes the complete response as a JSON file and tracks detection count.

        Args:
            response: Complete API response dict
            index: Batch number in this invocation

        Returns:
            Number of detections in this batch
        """
        __method_name = inspect.currentframe().f_code.co_name
        current_epoch = int(time.time())
        filename = f"{consts.FILE_NAME_PREFIX}_{current_epoch}_{index}"

        # Extract detection count
        detections = response.get("detections", [])
        detection_count = len(detections)

        # Log response summary
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"API response #{index} has {detection_count} detections (keys={list(response.keys())})",
            )
        )
        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"Response #{index} structure: top_level_keys={list(response.keys())}",
            )
        )

        # Write to file share
        content = json.dumps(response, indent=2)
        size_kb = len(content.encode("utf-8")) / 1024

        write_start = time.time()
        sm = StateManager(
            connection_string=consts.CONN_STRING,
            file_path=filename,
            share_name=consts.FILE_SHARE_NAME_DATA,
        )
        sm.post(content)
        write_elapsed = time.time() - write_start

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"Batch #{index} saved: detections={detection_count},"
                f" file_size={size_kb:.1f}KB, write_time={write_elapsed:.2f}s, filename={filename}",
            )
        )

        return detection_count

    def _update_checkpoint(
        self, page_start: str, next_token: Optional[str], next_start: Optional[str]
    ) -> None:
        """Update checkpoint after successful file write.

        Handles two scenarios:
        1. Window complete: Save new start time and clear token
        2. Mid-window: Save pagination token and keep start time

        Args:
            page_start: Current window start time
            next_token: Pagination token from response (if any)
            next_start: Next window start time (if any)
        """
        __method_name = inspect.currentframe().f_code.co_name
        checkpoint_start = time.time()

        if next_start:
            # Window complete: advance to next time window
            self._checkpoint.set_checkpoint(next_start, None)
            elapsed = time.time() - checkpoint_start
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Window complete, checkpoint advanced to {next_start} (update={elapsed:.2f}s)",
                )
            )
        elif next_token:
            # Mid-window: pagination needed
            self._checkpoint.set_checkpoint(page_start, next_token)
            elapsed = time.time() - checkpoint_start
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Mid-window checkpoint saved with pagination token (update={elapsed:.2f}s)",
                )
            )
