import abc
import asyncio
import gzip
import io
import zlib
from enum import Enum, unique
from typing import BinaryIO


class GZIPCompressedStream(io.RawIOBase):
    def __init__(self, stream: BinaryIO, *, compression_level: int,
                 filename: str = None):
        assert 1 <= compression_level <= 9

        self._compression_level = compression_level
        self._stream = stream

        self._compressed_stream = io.BytesIO()
        self._compressor = gzip.GzipFile(
            filename=filename,
            mode='wb',
            fileobj=self._compressed_stream,
            compresslevel=compression_level
        )

        # because of the GZIP header written by `GzipFile.__init__`:
        self._compressed_stream.seek(0)

    @property
    def compression_level(self) -> int:
        return self._compression_level

    @property
    def stream(self) -> BinaryIO:
        return self._stream

    def readable(self) -> bool:
        return True

    def _read_compressed_into(self, b: memoryview) -> int:
        buf = self._compressed_stream.read(len(b))
        b[:len(buf)] = buf
        return len(buf)

    def readinto(self, b: bytearray) -> int:
        b = memoryview(b)

        offset = 0
        size = len(b)
        while offset < size:
            offset += self._read_compressed_into(b[offset:])
            if offset < size:
                # self._compressed_buffer now empty
                if self._compressor.closed:
                    # nothing to compress anymore
                    break
                # compress next bytes
                self._read_n_compress(size)

        return offset

    def _read_n_compress(self, size: int):
        assert size > 0

        data = self._stream.read(size)

        # rewind buffer to the start to free up memory
        # (because anything currently in the buffer should be already
        #  streamed off the object)
        self._compressed_stream.seek(0)
        self._compressed_stream.truncate(0)

        if data:
            self._compressor.write(data)
        else:
            # this will write final data (will flush zlib with Z_FINISH)
            self._compressor.close()

        # rewind to the buffer start
        self._compressed_stream.seek(0)

    def __repr__(self) -> str:
        return (
            '{self.__class__.__name__}('
            '{self.stream!r}, '
            'compression_level={self.compression_level!r}'
            ')'
        ).format(self=self)


BUFFER_SIZE = 2 ** 10


class BaseAsyncReader(abc.ABC):
    @abc.abstractmethod
    async def read(self, size: int):
        raise NotImplementedError


@unique
class CompressedType(int, Enum):
    gzip = 16
    zlib_gzip = 32


class BaseAsyncIteratorReader(BaseAsyncReader, abc.ABC):
    def __aiter__(self):
        return self

    async def __anext__(self):
        chunk = await self.read(BUFFER_SIZE)
        if not chunk:
            raise StopAsyncIteration
        return chunk


class AsyncGZIPDecompressedStream(BaseAsyncIteratorReader):
    def __init__(self, stream: BaseAsyncReader, *,
                 compression_type: CompressedType = CompressedType.zlib_gzip):

        self._stream = stream
        self._lock = asyncio.Lock()
        self._decompressed_stream = io.BytesIO()
        '''
        http://www.zlib.net/manual.html#Advanced

        windowBits can also be greater than 15 for optional gzip decoding.
        Add 32 to windowBits to enable zlib and gzip decoding with automatic
        header detection, or add 16 to decode only the gzip format
        (the zlib format will return a Z_DATA_ERROR).
        '''
        self._decompressor = (
            zlib.decompressobj(compression_type.value + zlib.MAX_WBITS)
        )

    @property
    def stream(self) -> BaseAsyncReader:
        return self._stream

    async def read(self, size: int):
        assert size > 0

        async with self._lock:
            while self._decompressed_stream.tell() < size:
                chunk = await self._stream.read(size)
                if not chunk:
                    break
                self._decompressed_stream.write(
                    self._decompressor.decompress(chunk)
                )
            self._decompressed_stream.seek(0)
            res = self._decompressed_stream.read()

            # clearing buffer and rollback tail
            self._decompressed_stream.seek(0)
            self._decompressed_stream.truncate(0)
            self._decompressed_stream.write(res[size:])
            return res[:size]

    def __repr__(self) -> str:
        return (
            '{self.__class__.__name__}('
            '{self.stream!r}, '
            ')'
        ).format(self=self)


__all__ = (
    'AsyncGZIPDecompressedStream',
    'GZIPCompressedStream',
)
