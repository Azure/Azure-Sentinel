"""Manage checkpoint state and data files in Azure File Share.

This module handles:
1. Checkpoint persistence: tracks API pagination state between runs
2. Data file I/O: stores raw detection batches from Google SecOps
3. Time window management: computes lookback windows for fetching

Checkpoint Format:
  {
    "pageStartTime": "2026-04-23T00:00:00Z",  # Window start (for new window)
    "pageToken": "token123"                    # Pagination token (for mid-window)
  }

Time Windows:
- If pageToken exists: continue mid-window (resume pagination)
- If pageStartTime exists: start new window from that time
- If neither: compute new start time from LookbackDays
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import inspect

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import ShareClient, ShareFileClient

from . import consts
from .logger import applogger

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Buffer time added when computing lookback window
LOOKBACK_BUFFER_MINUTES = -5


class StateManager:
    """Manage checkpoint and data file persistence in Azure File Share.

    Two use cases:
    1. Checkpoint tracking: save pagination state between function invocations
    2. Raw data storage: buffer detection batches from Google SecOps before ingestion
    """

    def __init__(
        self,
        connection_string: str = consts.CONN_STRING,
        file_path: str = consts.CHECKPOINT_FILE_NAME,
        share_name: str = consts.FILE_SHARE_NAME,
    ):
        """Initialize file share clients.

        Args:
            connection_string: Azure Storage connection string
            file_path: File to read/write (checkpoint or data file)
            share_name: File share name (checkpoint or data share)

        Raises:
            ValueError: If connection string is empty
        """
        __method_name = inspect.currentframe().f_code.co_name

        if not connection_string:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "StateManager",
                "Azure Storage connection string required (AzureWebJobsStorage)",
            )
            applogger.error(error_msg)
            raise ValueError(error_msg)

        self._file_client = ShareFileClient.from_connection_string(
            conn_str=connection_string,
            share_name=share_name,
            file_path=file_path,
        )
        self._share_client = ShareClient.from_connection_string(
            conn_str=connection_string,
            share_name=share_name,
        )

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "StateManager",
                f"Initialized StateManager for share={share_name}, file={file_path}",
            )
        )

    # ═══════════════════════════════════════════════════════════════════════════════
    # FILE I/O: Read/Write/Delete
    # ═══════════════════════════════════════════════════════════════════════════════

    def get(self) -> Optional[str]:
        """Read file contents as text.

        Returns:
            File contents, or None if file not found
        """
        try:
            return self._file_client.download_file().readall().decode()
        except ResourceNotFoundError:
            return None

    def post(self, text: str) -> None:
        """Write text to file (creates share if needed).

        Creates the file share on first write (idempotent).

        Args:
            text: Content to write
        """
        try:
            self._file_client.upload_file(text)
        except ResourceNotFoundError:
            # Share doesn't exist: create it, then upload
            try:
                self._share_client.create_share()
            except ResourceExistsError:
                # Race condition: share was created by another process
                pass
            self._file_client.upload_file(text)

    def delete(self) -> None:
        """Delete file (safe if file doesn't exist)."""
        try:
            self._file_client.delete_file()
        except ResourceNotFoundError:
            pass

    # ═══════════════════════════════════════════════════════════════════════════════
    # CHECKPOINT MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_checkpoint(self) -> Optional[dict]:
        """Load checkpoint from file.

        Checkpoint tracks API pagination state:
        - pageStartTime: current time window start
        - pageToken: pagination token (if mid-window)

        Returns:
            Checkpoint dict, or None if not found or corrupt
        """
        __method_name = inspect.currentframe().f_code.co_name
        raw_content = self.get()
        if not raw_content:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "StateManager",
                    "No checkpoint file found",
                )
            )
            return None

        try:
            checkpoint = json.loads(raw_content)
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "StateManager",
                    f"Successfully loaded checkpoint: {checkpoint}",
                )
            )
            return checkpoint
        except json.JSONDecodeError as err:
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "StateManager",
                    f"Checkpoint file is corrupt (invalid JSON), discarding: {err}",
                )
            )
            return None

    def set_checkpoint(
        self,
        page_start_time: str,
        page_token: Optional[str] = None,
    ) -> None:
        """Save checkpoint to file.

        Args:
            page_start_time: Current time window start (ISO format)
            page_token: Pagination token if mid-window, None if starting new window
        """
        __method_name = inspect.currentframe().f_code.co_name
        checkpoint_data = {
            "pageStartTime": page_start_time,
            "pageToken": page_token,
        }
        self.post(json.dumps(checkpoint_data))
        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "StateManager",
                f"Checkpoint saved (start={page_start_time[:10]}, token={page_token if page_token else 'no'})",
            )
        )

    def resolve_initial_start_time(self) -> Tuple[str, Optional[str]]:
        """Determine where to start fetching detections.

        Decision Tree:
        1. If checkpoint exists:
           - If stale (>7 days old): reset to MAX_LOOKBACK_DAYS
           - Otherwise: resume from checkpoint (with pagination token if any)
        2. If no checkpoint: compute from LookbackDays config

        Returns:
            Tuple of (start_time, pagination_token) where:
              - start_time: ISO timestamp to start fetching from
              - pagination_token: None (new window) or token (resume mid-window)
        """
        __method_name = inspect.currentframe().f_code.co_name
        checkpoint = self.get_checkpoint()

        if checkpoint:
            page_start = checkpoint.get("pageStartTime", "")
            page_token = checkpoint.get("pageToken")

            # Check if checkpoint is still valid
            if page_start or page_token:
                if self._is_stale(page_start):
                    # Checkpoint too old: reset to safe lookback
                    new_start = self._compute_start_time(consts.MAX_LOOKBACK_DAYS)
                    applogger.warning(
                        consts.LOG_FORMAT.format(
                            consts.LOG_PREFIX,
                            __method_name,
                            "StateManager",
                            f"Checkpoint stale (>{consts.MAX_LOOKBACK_DAYS} days), resetting to {new_start[:10]}",
                        )
                    )
                    return new_start, None

                applogger.info(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "StateManager",
                        f"Resuming from checkpoint (date={page_start[:10]}, token={page_token if page_token else 'no'})",
                    )
                )
                return page_start, page_token

        # No checkpoint: compute start time from configuration
        lookback_days = min(consts.LOOKBACK_DAYS, consts.MAX_LOOKBACK_DAYS)
        start_time = self._compute_start_time(lookback_days)

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                "StateManager",
                f"No checkpoint, computed start (lookback={lookback_days} days): {start_time[:10]}",
            )
        )
        return start_time, None

    # ═══════════════════════════════════════════════════════════════════════════════
    # INTERNAL: Time Window Utilities
    # ═══════════════════════════════════════════════════════════════════════════════

    def _is_stale(self, iso_timestamp: str) -> bool:
        """Check if timestamp is older than MAX_LOOKBACK_DAYS.

        Args:
            iso_timestamp: ISO 8601 timestamp (e.g., "2026-04-23T07:30:00Z")

        Returns:
            True if timestamp is older than MAX_LOOKBACK_DAYS, False otherwise
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            # Parse ISO timestamp, handling both Z and +00:00 suffix
            parsed_time = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))

            # Compute cutoff: now - MAX_LOOKBACK_DAYS
            cutoff_time = datetime.now(timezone.utc) - timedelta(
                days=consts.MAX_LOOKBACK_DAYS
            )

            # Stale if timestamp is before cutoff
            is_stale = parsed_time < cutoff_time
            if is_stale:
                applogger.debug(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        "StateManager",
                        f"Timestamp {iso_timestamp} is stale (older than {consts.MAX_LOOKBACK_DAYS} days)",
                    )
                )
            return is_stale
        except (ValueError, AttributeError) as err:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    "StateManager",
                    f"Could not parse timestamp {iso_timestamp}: {err}",
                )
            )
            return False

    def _compute_start_time(self, days_ago: int) -> str:
        """Compute ISO timestamp for N days ago with buffer.

        Adds a buffer to prevent missing data at time window boundaries.
        Useful when Google SecOps time windows align with exact seconds.

        Formula: now - days_ago - LOOKBACK_BUFFER_MINUTES

        Args:
            days_ago: How many days back to fetch from

        Returns:
            ISO 8601 timestamp (UTC, Z suffix)

        Example:
            If current time is 2026-04-23T07:38:03Z and days_ago=7:
            Returns: 2026-04-16T07:33:03Z (7 days ago minus 5 min buffer)
        """
        # Subtract days and buffer minutes from now
        target_time = datetime.now(timezone.utc) - timedelta(
            days=days_ago,
            minutes=LOOKBACK_BUFFER_MINUTES,
        )

        # Format as ISO timestamp with Z suffix (not +00:00)
        return target_time.isoformat().replace("+00:00", "Z")
