# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import typing


class AbstractKafkaEvent(abc.ABC):

    @abc.abstractmethod
    def get_body(self) -> bytes:
        pass

    @property
    @abc.abstractmethod
    def key(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def offset(self) -> typing.Optional[int]:
        pass

    @property
    @abc.abstractmethod
    def partition(self) -> typing.Optional[int]:
        pass

    @property
    @abc.abstractmethod
    def topic(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def timestamp(self) -> typing.Optional[str]:
        pass
