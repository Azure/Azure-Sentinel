# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import json
import typing

from . import _abc


class QueueMessage(_abc.QueueMessage):
    """A Queue message object.

    :param str id:
        An optional string specifying the ID of the message.

    :param body:
        A string or bytes instance specifying the message body.

    :param str pop_receipt:
        An optional string containing the pop receipt token.
    """

    def __init__(self, *,
                 id: typing.Optional[str] = None,
                 body: typing.Optional[typing.Union[str, bytes]] = None,
                 pop_receipt: typing.Optional[str] = None) -> None:
        self.__id = id
        self.__body = b''
        self.__pop_receipt = pop_receipt

        if body is not None:
            self.__set_body(body)

    @property
    def id(self) -> typing.Optional[str]:
        """Message ID."""
        return self.__id

    @property
    def dequeue_count(self) -> typing.Optional[int]:
        """The number of times this message has been dequeued."""
        return None

    @property
    def expiration_time(self) -> typing.Optional[datetime.datetime]:
        """A datetime object with the message expiry time."""
        return None

    @property
    def insertion_time(self) -> typing.Optional[datetime.datetime]:
        """A datetime object with the message queue insertion time."""
        return None

    @property
    def time_next_visible(self) -> typing.Optional[datetime.datetime]:
        """A datetime object with the time the message will be visible next."""
        return None

    @property
    def pop_receipt(self) -> typing.Optional[str]:
        """The message pop receipt token as a string."""
        return self.__pop_receipt

    def __set_body(self, body):
        if isinstance(body, str):
            body = body.encode('utf-8')

        if not isinstance(body, (bytes, bytearray)):
            raise TypeError(
                f'response is expected to be either of '
                f'str, bytes, or bytearray, got {type(body).__name__}')

        self.__body = bytes(body)

    def get_body(self) -> bytes:
        """Return message content as bytes."""
        return self.__body

    def get_json(self) -> typing.Any:
        """Decode and return message content as a JSON object.

        :return:
            Decoded JSON data.

        :raises ValueError:
            when the body of the message does not contain valid JSON data.
        """
        return json.loads(self.__body)

    def __repr__(self) -> str:
        return (
            f'<azure.QueueMessage id={self.id} at 0x{id(self):0x}>'
        )
