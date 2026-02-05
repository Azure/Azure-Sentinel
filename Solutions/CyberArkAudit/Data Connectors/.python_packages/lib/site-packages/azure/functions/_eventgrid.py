# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import typing

from azure.functions import _abc as azf_abc


class EventGridEvent(azf_abc.EventGridEvent):
    """An EventGrid event message."""

    def __init__(self, *,
                 id: str,
                 data: typing.Dict[str, object],
                 topic: str,
                 subject: str,
                 event_type: str,
                 event_time: typing.Optional[datetime.datetime],
                 data_version: str) -> None:
        self.__id = id
        self.__data = data
        self.__subject = subject
        self.__topic = topic
        self.__event_type = event_type
        self.__event_time = event_time
        self.__data_version = data_version

    @property
    def id(self) -> str:
        return self.__id

    def get_json(self) -> typing.Any:
        return self.__data

    @property
    def topic(self) -> str:
        return self.__topic

    @property
    def subject(self) -> str:
        return self.__subject

    @property
    def event_type(self) -> str:
        return self.__event_type

    @property
    def event_time(self) -> typing.Optional[datetime.datetime]:
        return self.__event_time

    @property
    def data_version(self) -> str:
        return self.__data_version

    def __repr__(self) -> str:
        return (
            f'<azure.EventGridEvent id={self.id} '
            f'topic={self.topic} '
            f'subject={self.subject} '
            f'at 0x{id(self):0x}>'
        )


class EventGridOutputEvent(azf_abc.EventGridOutputEvent):
    """An EventGrid event message."""

    def __init__(self, *,
                 id: str,
                 data: typing.Dict[str, object],
                 subject: str,
                 event_type: str,
                 event_time: typing.Optional[datetime.datetime],
                 data_version: str) -> None:
        self.__id = id
        self.__data = data
        self.__subject = subject
        self.__event_type = event_type
        self.__event_time = event_time
        self.__data_version = data_version

    @property
    def id(self) -> str:
        return self.__id

    def get_json(self) -> typing.Any:
        return self.__data

    @property
    def subject(self) -> str:
        return self.__subject

    @property
    def event_type(self) -> str:
        return self.__event_type

    @property
    def event_time(self) -> typing.Optional[datetime.datetime]:
        return self.__event_time

    @property
    def data_version(self) -> str:
        return self.__data_version

    def __repr__(self) -> str:
        return (
            f'<azure.EventGridEvent id={self.id} '
            f'event_type={self.event_type} '
            f'subject={self.subject} '
            f'at 0x{id(self):0x}>'
        )
