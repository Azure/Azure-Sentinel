# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import typing

from azure.functions import _abc as azf_abc
from . import meta


class TimerRequest(azf_abc.TimerRequest):

    def __init__(self, *, past_due: bool = False, schedule_status: dict = {},
                 schedule: dict = {}) -> None:
        self.__past_due = past_due
        self.__schedule_status = schedule_status
        self.__schedule = schedule

    @property
    def past_due(self) -> bool:
        return self.__past_due

    @property
    def schedule_status(self) -> dict:
        return self.__schedule_status

    @property
    def schedule(self) -> dict:
        return self.__schedule


class TimerRequestConverter(meta.InConverter,
                            binding='timerTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, azf_abc.TimerRequest)

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        if data.type != 'json':
            raise NotImplementedError

        info = json.loads(data.value)

        return TimerRequest(
            past_due=info.get('IsPastDue', False),
            schedule_status=info.get('ScheduleStatus', {}),
            schedule=info.get('Schedule', {}))
