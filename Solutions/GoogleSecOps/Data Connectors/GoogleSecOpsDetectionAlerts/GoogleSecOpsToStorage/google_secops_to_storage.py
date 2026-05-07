"""Fetch detection alerts from Google SecOps and save to Azure File Share.

Streams the SecOps API at detection granularity — one detection object at a
time — and writes them directly into 50 MB JSON array files on Azure File Share.
The companion AzureStorageToSentinel function monitors and ingests the files
into Microsoft Sentinel.

Memory profile: O(single detection size) during fetch, O(50 MB) during flush.
"""

import inspect
import io
import time
from typing import Optional
from azure.storage.fileshare import ShareDirectoryClient
from azure.core.exceptions import ResourceNotFoundError

from ..SharedCode import consts
from ..SharedCode.google_secops_client import GoogleSecOpsClient
from ..SharedCode.exceptions import GoogleSecOpsConnectorError
from ..SharedCode.google_auth import GoogleServiceAccountAuth
from ..SharedCode.logger import applogger
from ..SharedCode.state_manager import StateManager

_MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB per output file


class _DetectionFileWriter():
    """Buffer individual detection JSON strings and flush to Azure File Share.

    Writes files as JSON arrays: [{det1},{det2},...,{detN}]
    Rotates to a new file when the current buffer reaches _MAX_FILE_BYTES.

    Memory: holds at most one ~50 MB StringIO buffer + one detection at a time.
    """

    def __init__(self, conn_string: str, share_name: str, start_time: int = None) -> None:
        self._conn_string = conn_string
        self._share_name = share_name
        self._buf = io.StringIO()
        self._buf.write("[")
        self._byte_size = 1  # opening [
        self._first = True   # no detections written to current file yet
        self._file_index = 0
        self._files_written = 0
        self._start_time = start_time if start_time is not None else int(time.time())
        applogger.debug(f"DetectionFileWriter initialized: share={share_name}, start_time={self._start_time}")

    def write_detection(self, raw: str, batch: int) -> None:
        """Append one detection to the current file, rotating at _MAX_FILE_BYTES."""
        raw = raw.strip()
        if not raw:
            return

        prefix = "" if self._first else ","
        entry = prefix + raw
        entry_bytes = len(entry.encode("utf-8"))

        # Rotate: flush current file before writing if it would exceed the limit
        # Always write at least one detection per file (handles oversized detections)
        if not self._first and self._byte_size + entry_bytes + 1 > _MAX_FILE_BYTES:
            applogger.debug(
                f"File rotation triggered: current_size={self._byte_size}B, "
                f"entry_size={entry_bytes}B, max={_MAX_FILE_BYTES}B"
            )
            self._flush(batch)
            entry = raw
            entry_bytes = len(raw.encode("utf-8"))

        self._buf.write(entry)
        self._byte_size += entry_bytes
        self._first = False
        applogger.debug(f"Detection written: batch={batch}, buffer_size={self._byte_size}B")

    def flush(self, batch: int) -> int:
        """Flush current buffer to Azure File Share. Returns count of files written."""
        return self._flush(batch)

    def close(self, batch: int) -> None:
        """Flush any remaining detections and release the buffer."""
        self._flush(batch)
        self._buf.close()

    def _flush(self, batch: int) -> int:
        if self._first:
            applogger.debug(f"Flush skipped: no detections in buffer for batch={batch}")
            return 0  # nothing buffered

        self._buf.write("]")
        content = self._buf.getvalue()

        filename = f"{consts.FILE_NAME_PREFIX}_{self._start_time}_{batch}_{self._file_index}"
        applogger.debug(f"Flushing file: {filename}, size={len(content.encode('utf-8'))}B")

        sm = StateManager(
            connection_string=self._conn_string,
            file_path=filename,
            share_name=self._share_name,
        )
        sm.post(content)
        applogger.info(
            f"File written to Azure: filename={filename}, batch={batch}, "
            f"size={len(content.encode('utf-8'))}B"
        )

        self._file_index += 1
        self._files_written += 1

        # Reset buffer for next file
        self._buf.seek(0)
        self._buf.truncate()
        self._buf.write("[")
        self._byte_size = 1
        self._first = True

        return 1

    def flush_batch(self, batch: int):
        applogger.debug(f"Flushing batch: batch={batch}, start_time={self._start_time}")
        data_dir = ShareDirectoryClient.from_connection_string(
            conn_str=self._conn_string,
            share_name=self._share_name,
            directory_path="",
        )
        try:
            entries = list(
                data_dir.list_directories_and_files(name_starts_with=consts.FILE_NAME_PREFIX)
            )
        except ResourceNotFoundError:
            applogger.debug(f"Share does not exist yet, nothing to flush for batch={batch}")
            return
        all_files = [e["name"] for e in entries if not e.get("is_directory")]
        applogger.debug(f"Found {len(all_files)} files matching prefix: {consts.FILE_NAME_PREFIX}")

        if not all_files:
            applogger.debug(f"No files found to delete for batch={batch}")
            return

        deleted_count = 0
        for file in all_files:
            parts = file.split("_")
            if self._start_time == int(parts[3]) and batch == int(parts[4]):
                sm = StateManager(
                    connection_string=self._conn_string,
                    file_path=file,
                    share_name=self._share_name,
                )
                sm.delete()
                deleted_count += 1
                applogger.debug(f"Deleted file on error: {file}")
        applogger.warning(f"Cleaned up {deleted_count} files for failed batch={batch}")


class GoogleSecOpsToStorage:
    """Stream detection alerts from Google SecOps directly into Azure File Share."""

    def __init__(self) -> None:
        """Initialize Google SecOps client, checkpoint manager, and validate configuration."""
        self._auth = GoogleServiceAccountAuth()
        self._client = GoogleSecOpsClient(self._auth)
        self._checkpoint = StateManager(
            connection_string=consts.CONN_STRING,
            file_path=consts.CHECKPOINT_FILE_NAME,
            share_name=consts.FILE_SHARE_NAME,
        )
        self._start_time = int(time.time())

    def run(self) -> None:
        """Stream detections from SecOps API and write directly to Azure File Share.

        Calls stream_detections once per page. Each call yields individual
        detections followed by a sentinel carrying (next_token, next_start).
        On sentinel: flush files, update checkpoint, then either continue to
        the next page (next_token) or stop (next_start or no token).
        """
        __method_name = inspect.currentframe().f_code.co_name
        page_start, page_token = self._checkpoint.resolve_initial_start_time()

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"Fetching: start={page_start[:10]}, token={'yes' if page_token else 'no'}",
            )
        )

        file_writer = _DetectionFileWriter(consts.CONN_STRING, consts.FILE_SHARE_NAME_DATA, self._start_time)
        total_detections = 0
        batch_count = 0
        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"Starting stream processing with initial page_start={page_start[:10]}",
            )
        )

        try:
            while True:
                applogger.debug(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        consts.FUNCTION_NAME_FETCHER,
                        f"Processing batch {batch_count + 1}: page_start={page_start[:10]}, "
                        f"token={'yes' if page_token else 'no'}",
                    )
                )
                for raw, next_token, next_start in self._client.stream_detections(
                    page_start_time=page_start,
                    page_token=page_token,
                ):
                    if raw:
                        file_writer.write_detection(raw, batch_count+1)
                        total_detections += 1
                    else:
                        # Sentinel — flush and update checkpoint
                        files_written = file_writer.flush(batch_count+1)
                        batch_count += 1
                        self._update_checkpoint(page_start, next_token, next_start)
                        applogger.info(
                            consts.LOG_FORMAT.format(
                                consts.LOG_PREFIX,
                                __method_name,
                                consts.FUNCTION_NAME_FETCHER,
                                f"Batch {batch_count} flushed: files={files_written},"
                                f" total_detections={total_detections}, "
                                f"next_token={'yes' if next_token else 'no'}, "
                                f"next_start={'yes' if next_start else 'no'}",
                            )
                        )

                # Return when window is complete or no more pages
                if next_start or not next_token:
                    applogger.debug(
                        consts.LOG_FORMAT.format(
                            consts.LOG_PREFIX,
                            __method_name,
                            consts.FUNCTION_NAME_FETCHER,
                            f"Stopping stream: window_complete={bool(next_start)}, "
                            f"no_more_pages={not bool(next_token)}",
                        )
                    )
                    break

                # Advance to next page
                applogger.debug(
                    consts.LOG_FORMAT.format(
                        consts.LOG_PREFIX,
                        __method_name,
                        consts.FUNCTION_NAME_FETCHER,
                        "Advancing to next page with token",
                    )
                )
                page_token = next_token

        except GoogleSecOpsConnectorError as exc:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"CRITICAL: API error (batch={batch_count}, detections={total_detections}): {exc}",
                )
            )
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Cleaning up files for failed batch {batch_count}",
                )
            )
            file_writer.flush_batch(batch_count)
            raise
        except Exception as exc:
            applogger.error(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"CRITICAL: Unexpected error (batch={batch_count}, detections={total_detections}): {exc}",
                )
            )
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Cleaning up files for failed batch {batch_count}",
                )
            )
            file_writer.flush_batch(batch_count)
            raise
        finally:
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Closing file writer, files_written={file_writer._files_written}",
                )
            )
            file_writer.close(batch_count)

        applogger.info(
            consts.LOG_FORMAT.format(
                consts.LOG_PREFIX,
                __method_name,
                consts.FUNCTION_NAME_FETCHER,
                f"Fetch cycle complete: batches={batch_count},"
                f" detections={total_detections}, files={file_writer._files_written}",
            )
        )

    def _update_checkpoint(
        self, page_start: str, next_token: Optional[str], next_start: Optional[str]
    ) -> None:
        """Update checkpoint after successful file flush.

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
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Setting checkpoint: window_complete=True, next_start={next_start}",
                )
            )
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
            applogger.debug(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    f"Setting checkpoint: mid_window=True, page_start={page_start}, token_length={len(next_token)}",
                )
            )
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
        else:
            applogger.warning(
                consts.LOG_FORMAT.format(
                    consts.LOG_PREFIX,
                    __method_name,
                    consts.FUNCTION_NAME_FETCHER,
                    "No checkpoint update: both next_token and next_start are None",
                )
            )
