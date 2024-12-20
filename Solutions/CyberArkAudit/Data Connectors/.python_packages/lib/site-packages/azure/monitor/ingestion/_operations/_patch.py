# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import Sequence
from io import IOBase
import logging
import sys
from typing import Callable, cast, List, Any, Optional, Union, IO

from ._operations import LogsIngestionClientOperationsMixin as GeneratedOps
from .._helpers import _create_gzip_requests, GZIP_MAGIC_NUMBER
from .._models import LogsUploadError

if sys.version_info >= (3, 9):
    from collections.abc import Mapping, MutableMapping
else:
    from typing import Mapping, MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports


_LOGGER = logging.getLogger(__name__)
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class LogsIngestionClientOperationsMixin(GeneratedOps):
    def upload(
        self,
        rule_id: str,
        stream_name: str,
        logs: Union[List[JSON], IO],
        *,
        on_error: Optional[Callable[[LogsUploadError], None]] = None,
        **kwargs: Any
    ) -> None:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        A list of logs is divided into chunks of 1MB or less, then each chunk is gzip-compressed and uploaded.
        If an I/O stream is passed in, the stream is uploaded as-is.

        :param rule_id: The immutable ID of the Data Collection Rule resource.
        :type rule_id: str
        :param stream_name: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream_name: str
        :param logs: An array of objects matching the schema defined by the provided stream.
        :type logs: list[JSON] or IO
        :keyword on_error: The callback function that is called when a chunk of logs fails to upload.
            This function should expect one argument that corresponds to an "LogsUploadError" object.
            If no function is provided, then the first exception encountered will be raised.
        :paramtype on_error: Optional[Callable[[~azure.monitor.ingestion.LogsUploadError], None]]
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if isinstance(logs, IOBase):
            if not logs.readable():
                raise ValueError("The 'logs' stream must be readable.")
            content_encoding = None
            # Check if the stream is gzip-compressed if stream is seekable.
            if logs.seekable():
                if logs.read(2) == GZIP_MAGIC_NUMBER:
                    content_encoding = "gzip"
                logs.seek(0)

            super()._upload(rule_id, stream=stream_name, body=logs, content_encoding=content_encoding, **kwargs)
            return

        if not isinstance(logs, Sequence):
            raise ValueError("The 'logs' parameter must be a list of JSON objects or an I/O stream that is readable.")

        for gzip_data, log_chunk in _create_gzip_requests(cast(List[JSON], logs)):
            try:
                super()._upload(  # type: ignore
                    rule_id, stream=stream_name, body=gzip_data, content_encoding="gzip", **kwargs  # type: ignore
                )
            except Exception as err:  # pylint: disable=broad-except
                if on_error:
                    on_error(LogsUploadError(error=err, failed_logs=cast(List[Mapping[str, Any]], log_chunk)))
                else:
                    _LOGGER.error("Failed to upload chunk containing %d log entries", len(log_chunk))
                    raise err


__all__: List[str] = [
    "LogsIngestionClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
