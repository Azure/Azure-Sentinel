# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import io
from typing import Any, Optional, Union

from azure.functions import _abc as azf_abc
from . import meta


class InputStream(azf_abc.InputStream):
    def __init__(self, *, data: Union[bytes, meta.Datum],
                 name: Optional[str] = None,
                 uri: Optional[str] = None,
                 length: Optional[int] = None,
                 blob_properties: Optional[dict] = None,
                 metadata: Optional[dict] = None) -> None:
        self._io = io.BytesIO(data)  # type: ignore
        self._name = name
        self._length = length
        self._uri = uri
        self._blob_properties = blob_properties
        self._metadata = metadata

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def length(self) -> Optional[int]:
        return self._length

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    @property
    def blob_properties(self):
        return self._blob_properties

    @property
    def metadata(self):
        return self._metadata

    def read(self, size=-1) -> bytes:
        return self._io.read(size)

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def writable(self) -> bool:
        return False


class BlobConverter(meta.InConverter,
                    meta.OutConverter,
                    binding='blob',
                    trigger='blobTrigger'):
    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (azf_abc.InputStream, bytes, str))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return (
            issubclass(pytype, (str, bytes, bytearray, azf_abc.InputStream))
            or callable(getattr(pytype, 'read', None))
        )

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if callable(getattr(obj, 'read', None)):
            # file-like object
            obj = obj.read()

        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))

        else:
            raise NotImplementedError

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> Any:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type == 'string':
            data = data.value.encode('utf-8')
        elif data_type == 'bytes':
            data = data.value
        else:
            raise ValueError(
                f'unexpected type of data received for the "blob" binding '
                f': {data_type!r}'
            )

        if not trigger_metadata:
            return InputStream(data=data)
        else:
            properties = cls._decode_trigger_metadata_field(
                trigger_metadata, 'Properties', python_type=dict)
            if properties:
                blob_properties = properties
                length = properties.get('Length')
                length = int(length) if length else None
            else:
                blob_properties = None
                length = None

            metadata = None
            try:
                metadata = cls._decode_trigger_metadata_field(trigger_metadata,
                                                              'Metadata',
                                                              python_type=dict)
            except (KeyError, ValueError):
                # avoiding any exceptions when fetching Metadata as the
                # metadata type is unclear.
                pass

            return InputStream(
                data=data,
                name=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'BlobTrigger', python_type=str),
                length=length,
                uri=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'Uri', python_type=str),
                blob_properties=blob_properties,
                metadata=metadata
            )
