"""Ingest detection responses from Azure File Share into Microsoft Sentinel.

Monitors for response files saved by GoogleSecOpsToStorage and posts
detections to Sentinel via the Log Analytics DCR API.
"""

import inspect
import json
import time

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareDirectoryClient

from ..SharedCode import consts
from ..SharedCode.exceptions import SentinelIngestionError
from ..SharedCode.logger import applogger
from ..SharedCode.sentinel import post_data
from ..SharedCode.state_manager import StateManager


class AzureStorageToSentinel:
    """Read response files from Azure File Share and post detections to Sentinel."""

    def __init__(self) -> None:
        """Initialize Azure File Share client."""
        __method_name = inspect.currentframe().f_code.co_name

        try:
            self._data_dir = ShareDirectoryClient.from_connection_string(
                conn_str=consts.CONN_STRING,
                share_name=consts.FILE_SHARE_NAME_DATA,
                directory_path="",
            )
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"Initialized Azure File Share client for share={consts.FILE_SHARE_NAME_DATA}",
                )
            )
        except Exception as exc:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Failed to initialize Azure File Share client: {exc}",
            )
            applogger.error(error_msg)
            raise

    def run(self) -> None:
        """Process response files from Azure File Share and post to Sentinel.

        Runs once per timer trigger. Processes all eligible aged files in one cycle.
        """
        __method_name = inspect.currentframe().f_code.co_name
        start_time = time.time()

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                "Ingestion cycle started",
            )
        )

        total_extracted = 0
        total_posted = 0
        files_processed = 0

        # Check for eligible files once per invocation
        file_names = self._list_eligible_files()

        if not file_names:
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    "No eligible files found",
                )
            )
            return

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Processing {len(file_names)} eligible files",
            )
        )

        # Process all eligible files in this cycle
        for filename in file_names:
            extracted, posted = self._process_response_file(filename)
            total_extracted += extracted
            total_posted += posted
            files_processed += 1

        runtime = time.time() - start_time
        success_rate = (
            (total_posted / total_extracted * 100) if total_extracted > 0 else 0
        )
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Cycle complete: files={files_processed}, extracted={total_extracted},"
                f" posted={total_posted}, success_rate={success_rate:.1f}%, runtime={runtime:.1f}s",
            )
        )

    def _list_eligible_files(self) -> list:
        """List response files ready for ingestion (aged files only).

        Filters out files younger than MAX_FILE_AGE_FOR_INGESTION to avoid
        race conditions where the fetcher is still writing.

        Returns:
            List of filenames sorted by creation time (oldest first).

        Raises:
            Exception: On critical file share access errors
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            entries = list(
                self._data_dir.list_directories_and_files(name_starts_with=consts.FILE_NAME_PREFIX)
            )
            all_files = [e["name"] for e in entries if not e.get("is_directory")]
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"Listed {len(all_files)} files in data share",
                )
            )
        except ResourceNotFoundError:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    "Data share not found, no files available (this is normal on first run)",
                )
            )
            return []

        if not all_files:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    "No files found in data share",
                )
            )
            return []

        # Filter: only include files older than MAX_FILE_AGE_FOR_INGESTION
        now = int(time.time())
        eligible_files = [
            f
            for f in all_files
            if now - self._get_epoch(f) > consts.MAX_FILE_AGE_FOR_INGESTION
        ]
        eligible_files.sort(key=self._get_epoch)

        if eligible_files:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"Found {len(eligible_files)} eligible files (aged > {consts.MAX_FILE_AGE_FOR_INGESTION}s)",
                )
            )

        return eligible_files

    @staticmethod
    def _get_epoch(filename: str) -> int:
        """Extract epoch timestamp from filename.

        Filename format: google_secops_raw_<epoch>_<index>
        """
        try:
            parts = filename.split("_")
            return int(parts[3])
        except (IndexError, ValueError):
            return 0

    def _process_response_file(self, filename: str) -> tuple:
        """Read response file, extract detections, post to Sentinel, and delete.

        Returns:
            Tuple of (detections_extracted, detections_posted)

        Raises:
            Exception: On critical failures (invalid JSON, Sentinel post failure)
        """
        __method_name = inspect.currentframe().f_code.co_name

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Processing file: {filename}",
            )
        )

        sm = StateManager(
            connection_string=consts.CONN_STRING,
            file_path=filename,
            share_name=consts.FILE_SHARE_NAME_DATA,
        )

        # Read and validate file
        raw_content = sm.get()
        if not raw_content:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"File empty: {filename} (0 bytes), skipping",
                )
            )
            sm.delete()
            return 0, 0

        content_size_kb = len(raw_content.encode("utf-8")) / 1024
        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"File read: {filename}, size={content_size_kb:.1f}KB",
            )
        )

        # Parse JSON response
        try:
            response = json.loads(raw_content)
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"JSON parsed: {filename}, structure={type(response).__name__},"
                    f" keys={list(response.keys()) if isinstance(response, dict) else 'N/A'}",
                )
            )
        except json.JSONDecodeError as err:
            error_msg = consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"CRITICAL: Invalid JSON in {filename}: char={err.pos}, line={err.lineno}, reason={err.msg}",
            )
            applogger.error(error_msg)
            sm.delete()
            raise SentinelIngestionError(error_msg)

        # Extract detections
        detections = self._extract_detections(response)
        if not detections:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"No detections: {filename} (response structure had no detections array), skipping",
                )
            )
            sm.delete()
            return 0, 0

        extracted_count = len(detections)
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Extracted: {extracted_count} detections from {filename} ({content_size_kb:.1f}KB file)",
            )
        )

        # Post to Sentinel (will raise exception on failure)
        posted_count = self._post_to_sentinel(detections, filename)

        # Cleanup
        sm.delete()
        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Deleted file {filename}",
            )
        )

        return extracted_count, posted_count

    @staticmethod
    def _extract_detections(response: dict | list) -> list:
        """Extract detections array from API response.

        Handles both dict responses (with 'detections' key) and array responses.
        """
        if isinstance(response, dict):
            return response.get("detections") or []
        if isinstance(response, list):
            return response
        return []

    def _post_to_sentinel(self, detections: list, filename: str) -> int:
        """Post detections to Sentinel.

        Args:
            detections: List of detection events to post
            filename: Source filename (for logging)

        Returns:
            Number of events successfully posted

        Raises:
            Exception: If posting fails
        """
        __method_name = inspect.currentframe().f_code.co_name
        total_count = len(detections)

        applogger.debug(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_INGESTER,
                f"Posting: total={total_count}, source={filename}",
            )
        )

        try:
            post_data(json.dumps(detections), consts.DCR_STREAM_NAME)
            applogger.info(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"Posted successfully: total={total_count}, stream={consts.DCR_STREAM_NAME}",
                )
            )
        except Exception as exc:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_INGESTER,
                    f"CRITICAL - Post failed: total={total_count}, error_type={type(exc).__name__}, reason={str(exc)[:150]}",
                )
            )
            raise

        return total_count
