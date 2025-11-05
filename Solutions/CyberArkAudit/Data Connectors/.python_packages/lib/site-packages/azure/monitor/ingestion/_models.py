# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from typing import Any, List

if sys.version_info >= (3, 9):
    from collections.abc import Mapping
else:
    from typing import Mapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = Mapping[str, Any]  # pylint: disable=unsubscriptable-object


class LogsUploadError:
    """Error information for a failed upload to Azure Monitor.

    :param error: The error that occurred during the upload.
    :type error: Exception
    :param failed_logs: The list of logs that failed to upload.
    :type failed_logs: list[JSON]
    """

    error: Exception
    """The error that occurred during the upload."""
    failed_logs: List[JSON]
    """The list of logs that failed to upload."""

    def __init__(self, error: Exception, failed_logs: List[JSON]) -> None:
        self.error = error
        self.failed_logs = failed_logs
