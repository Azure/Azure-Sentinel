# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import typing

from azure.functions import _abc as func_abc
from azure.functions import meta


class EventHubEvent(func_abc.EventHubEvent):
    """A concrete implementation of Event Hub message type."""

    def __init__(self, *,
                 body: bytes,
                 trigger_metadata: typing.Mapping[str, meta.Datum] = None,
                 enqueued_time: typing.Optional[datetime.datetime] = None,
                 partition_key: typing.Optional[str] = None,
                 sequence_number: typing.Optional[int] = None,
                 offset: typing.Optional[str] = None,
                 iothub_metadata: typing.Optional[
                     typing.Mapping[str, str]] = None) -> None:
        self.__body = body
        self.__trigger_metadata = trigger_metadata
        self.__enqueued_time = enqueued_time
        self.__partition_key = partition_key
        self.__sequence_number = sequence_number
        self.__offset = offset
        self.__iothub_metadata = iothub_metadata

        # Cache for trigger metadata after Python object conversion
        self._trigger_metadata_pyobj: typing.Optional[
            typing.Mapping[str, typing.Any]] = None

    def get_body(self) -> bytes:
        return self.__body

    @property
    def partition_key(self) -> typing.Optional[str]:
        return self.__partition_key

    @property
    def iothub_metadata(self) -> typing.Optional[typing.Mapping[str, str]]:
        return self.__iothub_metadata

    @property
    def sequence_number(self) -> typing.Optional[int]:
        return self.__sequence_number

    @property
    def enqueued_time(self) -> typing.Optional[datetime.datetime]:
        return self.__enqueued_time

    @property
    def offset(self) -> typing.Optional[str]:
        return self.__offset

    @property
    def metadata(self) -> typing.Optional[typing.Mapping[str, typing.Any]]:
        """Getting read-only trigger metadata in a Python dictionary.

        Exposing the raw trigger_metadata to our customer. For cardinality=many
        scenarios, each event points to the common metadata of all the events.

        So when using metadata field when cardinality=many, it only needs to
        take one of the events to get all the data (e.g. events[0].metadata).

        Returns:
        --------
        typing.Mapping[str, object]
            Return the Python dictionary of trigger metadata
        """
        if self.__trigger_metadata is None:
            return None

        if self._trigger_metadata_pyobj is None:
            self._trigger_metadata_pyobj = {
                k: v.python_value for (k, v) in self.__trigger_metadata.items()
            }
        return self._trigger_metadata_pyobj

    def __repr__(self) -> str:
        return (
            f'<azure.EventHubEvent '
            f'partition_key={self.partition_key} '
            f'sequence_number={self.sequence_number} '
            f'enqueued_time={self.enqueued_time} '
            f'at 0x{id(self):0x}>'
        )
