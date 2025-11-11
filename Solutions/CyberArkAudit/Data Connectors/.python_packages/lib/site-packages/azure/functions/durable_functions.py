# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
import json

from azure.functions import _durable_functions
from . import meta


# Durable Function Orchestration Trigger
class OrchestrationTriggerConverter(meta.InConverter,
                                    meta.OutConverter,
                                    binding='orchestrationTrigger',
                                    trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.OrchestrationContext)

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # Implicit output should accept any return type
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.OrchestrationContext:
        return _durable_functions.OrchestrationContext(data.value)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        # Durable function context should be a json
        return meta.Datum(type='json', value=obj)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


class EnitityTriggerConverter(meta.InConverter,
                              meta.OutConverter,
                              binding='entityTrigger',
                              trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.EntityContext)

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # Implicit output should accept any return type
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.EntityContext:
        return _durable_functions.EntityContext(data.value)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        # Durable function context should be a json
        return meta.Datum(type='json', value=obj)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Durable Function Activity Trigger
class ActivityTriggerConverter(meta.InConverter,
                               meta.OutConverter,
                               binding='activityTrigger',
                               trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        # Activity Trigger's arguments should accept any types
        return True

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # The activity trigger should accept any JSON serializable types
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> typing.Any:
        data_type = data.type

        # Durable functions extension always returns a string of json
        # See durable functions library's call_activity_task docs
        if data_type in ['string', 'json']:
            try:
                callback = _durable_functions._deserialize_custom_object
                result = json.loads(data.value, object_hook=callback)
            except json.JSONDecodeError:
                # String failover if the content is not json serializable
                result = data.value
            except Exception:
                raise ValueError(
                    'activity trigger input must be a string or a '
                    f'valid json serializable ({data.value})')
        else:
            raise NotImplementedError(
                f'unsupported activity trigger payload type: {data_type}')

        return result

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        try:
            callback = _durable_functions._serialize_custom_object
            result = json.dumps(obj, default=callback)
        except TypeError:
            raise ValueError(
                f'activity trigger output must be json serializable ({obj})')

        return meta.Datum(type='json', value=result)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True
