# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import threading
import warnings
from io import BytesIO

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.common import with_current_context
from ._shared.encryption import decrypt_blob
from ._shared.request_handlers import validate_and_format_range_headers
from ._shared.response_handlers import process_storage_error, parse_length_from_content_range


def process_range_and_offset(start_range, end_range, length, encryption):
    start_offset, end_offset = 0, 0
    if encryption.get("key") is not None or encryption.get("resolver") is not None:
        if start_range is not None:
            # Align the start of the range along a 16 byte block
            start_offset = start_range % 16
            start_range -= start_offset

            # Include an extra 16 bytes for the IV if necessary
            # Because of the previous offsetting, start_range will always
            # be a multiple of 16.
            if start_range > 0:
                start_offset += 16
                start_range -= 16

        if length is not None:
            # Align the end of the range along a 16 byte block
            end_offset = 15 - (end_range % 16)
            end_range += end_offset

    return (start_range, end_range), (start_offset, end_offset)


def process_content(data, start_offset, end_offset, encryption):
    if data is None:
        raise ValueError("Response cannot be None.")
    try:
        content = b"".join(list(data))
    except Exception as error:
        raise HttpResponseError(message="Download stream interrupted.", response=data.response, error=error)
    if content and encryption.get("key") is not None or encryption.get("resolver") is not None:
        try:
            return decrypt_blob(
                encryption.get("required"),
                encryption.get("key"),
                encryption.get("resolver"),
                content,
                start_offset,
                end_offset,
                data.response.headers,
            )
        except Exception as error:
            raise HttpResponseError(message="Decryption failed.", response=data.response, error=error)
    return content


class _ChunkDownloader(object):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        client=None,
        total_size=None,
        chunk_size=None,
        current_progress=None,
        start_range=None,
        end_range=None,
        stream=None,
        parallel=None,
        validate_content=None,
        encryption_options=None,
        **kwargs
    ):
        self.client = client

        # Information on the download range/chunk size
        self.chunk_size = chunk_size
        self.total_size = total_size
        self.start_index = start_range
        self.end_index = end_range

        # The destination that we will write to
        self.stream = stream
        self.stream_lock = threading.Lock() if parallel else None
        self.progress_lock = threading.Lock() if parallel else None

        # For a parallel download, the stream is always seekable, so we note down the current position
        # in order to seek to the right place when out-of-order chunks come in
        self.stream_start = stream.tell() if parallel else None

        # Download progress so far
        self.progress_total = current_progress

        # Encryption
        self.encryption_options = encryption_options

        # Parameters for each get operation
        self.validate_content = validate_content
        self.request_options = kwargs

    def _calculate_range(self, chunk_start):
        if chunk_start + self.chunk_size > self.end_index:
            chunk_end = self.end_index
        else:
            chunk_end = chunk_start + self.chunk_size
        return chunk_start, chunk_end

    def get_chunk_offsets(self):
        index = self.start_index
        while index < self.end_index:
            yield index
            index += self.chunk_size

    def process_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        chunk_data = self._download_chunk(chunk_start, chunk_end - 1)
        length = chunk_end - chunk_start
        if length > 0:
            self._write_to_stream(chunk_data, chunk_start)
            self._update_progress(length)

    def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return self._download_chunk(chunk_start, chunk_end - 1)

    def _update_progress(self, length):
        if self.progress_lock:
            with self.progress_lock:  # pylint: disable=not-context-manager
                self.progress_total += length
        else:
            self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        if self.stream_lock:
            with self.stream_lock:  # pylint: disable=not-context-manager
                self.stream.seek(self.stream_start + (chunk_start - self.start_index))
                self.stream.write(chunk_data)
        else:
            self.stream.write(chunk_data)

    def _download_chunk(self, chunk_start, chunk_end):
        download_range, offset = process_range_and_offset(
            chunk_start, chunk_end, chunk_end, self.encryption_options
        )
        range_header, range_validation = validate_and_format_range_headers(
            download_range[0], download_range[1], check_content_md5=self.validate_content
        )

        try:
            _, response = self.client.download(
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                data_stream_total=self.total_size,
                download_stream_current=self.progress_total,
                **self.request_options
            )
        except HttpResponseError as error:
            process_storage_error(error)

        chunk_data = process_content(response, offset[0], offset[1], self.encryption_options)
        return chunk_data


class _ChunkIterator(object):
    """Async iterator for chunks in blob download stream."""

    def __init__(self, size, content, downloader):
        self.size = size
        self._current_content = content
        self._iter_downloader = downloader
        self._iter_chunks = None
        self._complete = (size == 0)

    def __len__(self):
        return self.size

    def __iter__(self):
        return self

    def __next__(self):
        """Iterate through responses."""
        if self._complete:
            raise StopIteration("Download complete")
        if not self._iter_downloader:
            # If no iterator was supplied, the download completed with
            # the initial GET, so we just return that data
            self._complete = True
            return self._current_content

        if not self._iter_chunks:
            self._iter_chunks = self._iter_downloader.get_chunk_offsets()
        else:
            chunk = next(self._iter_chunks)
            self._current_content = self._iter_downloader.yield_chunk(chunk)

        return self._current_content

    next = __next__  # Python 2 compatibility.


class StorageStreamDownloader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to download from Azure Storage.

    :ivar str name:
        The name of the file being downloaded.
    :ivar: str path:
        The full path of the file.
    :ivar str share:
        The name of the share where the file is.
    :ivar ~azure.storage.fileshare.FileProperties properties:
        The properties of the file being downloaded. If only a range of the data is being
        downloaded, this will be reflected in the properties.
    :ivar int size:
        The size of the total data in the stream. This will be the byte range if speficied,
        otherwise the total size of the file.
    """

    def __init__(
        self,
        client=None,
        config=None,
        start_range=None,
        end_range=None,
        validate_content=None,
        encryption_options=None,
        max_concurrency=1,
        name=None,
        path=None,
        share=None,
        encoding=None,
        **kwargs
    ):
        self.name = name
        self.path = path
        self.share = share
        self.properties = None
        self.size = None

        self._client = client
        self._config = config
        self._start_range = start_range
        self._end_range = end_range
        self._max_concurrency = max_concurrency
        self._encoding = encoding
        self._validate_content = validate_content
        self._encryption_options = encryption_options or {}
        self._request_options = kwargs
        self._location_mode = None
        self._download_complete = False
        self._current_content = None
        self._file_size = None
        self._response = None

        # The service only provides transactional MD5s for chunks under 4MB.
        # If validate_content is on, get only self.MAX_CHUNK_GET_SIZE for the first
        # chunk so a transactional MD5 can be retrieved.
        self._first_get_size = (
            self._config.max_single_get_size if not self._validate_content else self._config.max_chunk_get_size
        )
        initial_request_start = self._start_range if self._start_range is not None else 0
        if self._end_range is not None and self._end_range - self._start_range < self._first_get_size:
            initial_request_end = self._end_range
        else:
            initial_request_end = initial_request_start + self._first_get_size - 1

        self._initial_range, self._initial_offset = process_range_and_offset(
            initial_request_start, initial_request_end, self._end_range, self._encryption_options
        )

        self._response = self._initial_request()
        self.properties = self._response.properties
        self.properties.name = self.name
        self.properties.path = self.path
        self.properties.share = self.share

        # Set the content length to the download size instead of the size of
        # the last range
        self.properties.size = self.size

        # Overwrite the content range to the user requested range
        self.properties.content_range = "bytes {0}-{1}/{2}".format(
            self._start_range,
            self._end_range,
            self._file_size
        )

        # Overwrite the content MD5 as it is the MD5 for the last range instead
        # of the stored MD5
        # TODO: Set to the stored MD5 when the service returns this
        self.properties.content_md5 = None

        if self.size == 0:
            self._current_content = b""
        else:
            self._current_content = process_content(
                self._response,
                self._initial_offset[0],
                self._initial_offset[1],
                self._encryption_options
            )

    def __len__(self):
        return self.size

    def _initial_request(self):
        range_header, range_validation = validate_and_format_range_headers(
            self._initial_range[0],
            self._initial_range[1],
            start_range_required=False,
            end_range_required=False,
            check_content_md5=self._validate_content
        )

        try:
            location_mode, response = self._client.download(
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self._validate_content,
                data_stream_total=None,
                download_stream_current=0,
                **self._request_options
            )

            # Check the location we read from to ensure we use the same one
            # for subsequent requests.
            self._location_mode = location_mode

            # Parse the total file size and adjust the download size if ranges
            # were specified
            self._file_size = parse_length_from_content_range(response.properties.content_range)
            if self._end_range is not None:
                # Use the end range index unless it is over the end of the file
                self.size = min(self._file_size, self._end_range - self._start_range + 1)
            elif self._start_range is not None:
                self.size = self._file_size - self._start_range
            else:
                self.size = self._file_size

        except HttpResponseError as error:
            if self._start_range is None and error.response.status_code == 416:
                # Get range will fail on an empty file. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                try:
                    _, response = self._client.download(
                        validate_content=self._validate_content,
                        data_stream_total=0,
                        download_stream_current=0,
                        **self._request_options
                    )
                except HttpResponseError as error:
                    process_storage_error(error)

                # Set the download size to empty
                self.size = 0
                self._file_size = 0
            else:
                process_storage_error(error)

        # If the file is small, the download is complete at this point.
        # If file size is large, download the rest of the file in chunks.
        if response.properties.size == self.size:
            self._download_complete = True
        return response

    def chunks(self):
        if self.size == 0 or self._download_complete:
            iter_downloader = None
        else:
            data_end = self._file_size
            if self._end_range is not None:
                # Use the end range index unless it is over the end of the file
                data_end = min(self._file_size, self._end_range + 1)
            iter_downloader = _ChunkDownloader(
                client=self._client,
                total_size=self.size,
                chunk_size=self._config.max_chunk_get_size,
                current_progress=self._first_get_size,
                start_range=self._initial_range[1] + 1,  # start where the first download ended
                end_range=data_end,
                stream=None,
                parallel=False,
                validate_content=self._validate_content,
                encryption_options=self._encryption_options,
                use_location=self._location_mode,
                **self._request_options
            )
        return _ChunkIterator(
            size=self.size,
            content=self._current_content,
            downloader=iter_downloader)

    def readall(self):
        """Download the contents of this file.

        This operation is blocking until all data is downloaded.
        :rtype: bytes or str
        """
        stream = BytesIO()
        self.readinto(stream)
        data = stream.getvalue()
        if self._encoding:
            return data.decode(self._encoding)
        return data

    def content_as_bytes(self, max_concurrency=1):
        """Download the contents of this file.

        This operation is blocking until all data is downloaded.

        :keyword int max_concurrency:
            The number of parallel connections with which to download.
        :rtype: bytes
        """
        warnings.warn(
            "content_as_bytes is deprecated, use readall instead",
            DeprecationWarning
        )
        self._max_concurrency = max_concurrency
        return self.readall()

    def content_as_text(self, max_concurrency=1, encoding="UTF-8"):
        """Download the contents of this file, and decode as text.

        This operation is blocking until all data is downloaded.

        :keyword int max_concurrency:
            The number of parallel connections with which to download.
        :param str encoding:
            Test encoding to decode the downloaded bytes. Default is UTF-8.
        :rtype: str
        """
        warnings.warn(
            "content_as_text is deprecated, use readall instead",
            DeprecationWarning
        )
        self._max_concurrency = max_concurrency
        self._encoding = encoding
        return self.readall()

    def readinto(self, stream):
        """Download the contents of this file to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The number of bytes read.
        :rtype: int
        """
        # The stream must be seekable if parallel download is required
        parallel = self._max_concurrency > 1
        if parallel:
            error_message = "Target stream handle must be seekable."
            if sys.version_info >= (3,) and not stream.seekable():
                raise ValueError(error_message)

            try:
                stream.seek(stream.tell())
            except (NotImplementedError, AttributeError):
                raise ValueError(error_message)

        # Write the content to the user stream
        stream.write(self._current_content)
        if self._download_complete:
            return self.size

        data_end = self._file_size
        if self._end_range is not None:
            # Use the length unless it is over the end of the file
            data_end = min(self._file_size, self._end_range + 1)

        downloader = _ChunkDownloader(
            client=self._client,
            total_size=self.size,
            chunk_size=self._config.max_chunk_get_size,
            current_progress=self._first_get_size,
            start_range=self._initial_range[1] + 1,  # Start where the first download ended
            end_range=data_end,
            stream=stream,
            parallel=parallel,
            validate_content=self._validate_content,
            encryption_options=self._encryption_options,
            use_location=self._location_mode,
            **self._request_options
        )
        if parallel:
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(self._max_concurrency)
            list(executor.map(
                    with_current_context(downloader.process_chunk),
                    downloader.get_chunk_offsets()
                ))
        else:
            for chunk in downloader.get_chunk_offsets():
                downloader.process_chunk(chunk)
        return self.size

    def download_to_stream(self, stream, max_concurrency=1):
        """Download the contents of this file to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The properties of the downloaded file.
        :rtype: Any
        """
        warnings.warn(
            "download_to_stream is deprecated, use readinto instead",
            DeprecationWarning
        )
        self._max_concurrency = max_concurrency
        self.readinto(stream)
        return self.properties
