# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
from typing import Dict, Any, List, Union, Optional, Mapping

from azure.functions import _eventhub

from . import meta


class EventHubConverter(meta.InConverter, meta.OutConverter,
                        binding='eventHub'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        valid_types = (_eventhub.EventHubEvent)
        return (
            meta.is_iterable_type_annotation(pytype, valid_types)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        valid_types = (str, bytes)
        return (
            meta.is_iterable_type_annotation(pytype, str)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata
    ) -> Union[_eventhub.EventHubEvent, List[_eventhub.EventHubEvent]]:
        data_type = data.type

        if data_type in ['string', 'bytes', 'json']:
            return cls.decode_single_event(data, trigger_metadata)

        elif data_type in ['collection_bytes', 'collection_string']:
            return cls.decode_multiple_events(data, trigger_metadata)

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

    @classmethod
    def decode_single_event(cls, data,
                            trigger_metadata) -> _eventhub.EventHubEvent:
        if data.type in ['string', 'json']:
            body = data.value.encode('utf-8')

        elif data.type == 'bytes':
            body = data.value

        return _eventhub.EventHubEvent(body=body)

    @classmethod
    def decode_multiple_events(
            cls, data, trigger_metadata
    ) -> List[_eventhub.EventHubEvent]:
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        events = []
        for parsed_datum in parsed_data:
            event = _eventhub.EventHubEvent(body=parsed_datum)
            events.append(event)

        return events

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]
               ) -> meta.Datum:
        data = meta.Datum(type=None, value=None)

        if isinstance(obj, str):
            data = meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            data = meta.Datum(type='bytes', value=obj)

        elif isinstance(obj, int):
            data = meta.Datum(type='int', value=obj)

        elif isinstance(obj, list):
            data = meta.Datum(type='json', value=json.dumps(obj))

        return data


class EventHubTriggerConverter(EventHubConverter,
                               binding='eventHubTrigger', trigger=True):
    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata: Mapping[str, meta.Datum]
    ) -> Union[_eventhub.EventHubEvent, List[_eventhub.EventHubEvent]]:
        data_type = data.type

        if cls._is_cardinality_one(trigger_metadata):
            return cls.decode_single_event(data, trigger_metadata)

        elif cls._is_cardinality_many(trigger_metadata):
            return cls.decode_multiple_events(data, trigger_metadata)

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

    @classmethod
    def decode_single_event(
        cls, data, trigger_metadata: Mapping[str, meta.Datum]
    ) -> _eventhub.EventHubEvent:
        if data.type in ['string', 'json']:
            body = data.value.encode('utf-8')

        elif data.type == 'bytes':
            body = data.value

        return _eventhub.EventHubEvent(
            body=body,
            trigger_metadata=trigger_metadata,
            enqueued_time=cls._parse_datetime_metadata(
                trigger_metadata, 'EnqueuedTimeUtc'),
            partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'PartitionKey', python_type=str),
            sequence_number=cls._decode_trigger_metadata_field(
                trigger_metadata, 'SequenceNumber', python_type=int),
            offset=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Offset', python_type=str),
            iothub_metadata=cls._decode_iothub_metadata(trigger_metadata)
        )

    @classmethod
    def decode_multiple_events(
            cls, data, trigger_metadata: Mapping[str, meta.Datum]
    ) -> List[_eventhub.EventHubEvent]:
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        # Input Trigger IotHub Event
        elif data.type == 'json':
            parsed_data = json.loads(data.value)

        sys_props = trigger_metadata.get('SystemPropertiesArray')

        parsed_sys_props: List[Any] = []
        if sys_props is not None:
            parsed_sys_props = json.loads(sys_props.value)

        if len(parsed_data) != len(parsed_sys_props):
            raise AssertionError('Number of bodies and metadata mismatched')

        events = []
        for i in range(len(parsed_data)):
            enqueued_time = parsed_sys_props[i].get('EnqueuedTimeUtc')
            partition_key = cls.encode(
                parsed_sys_props[i].get('PartitionKey'),
                expected_type=str)
            sequence_number = cls.encode(
                parsed_sys_props[i].get('SequenceNumber'),
                expected_type=int)
            offset = cls.encode(
                parsed_sys_props[i].get('Offset'),
                expected_type=int)

            event = _eventhub.EventHubEvent(
                body=cls._marshall_event_body(parsed_data[i], data.type),
                trigger_metadata=trigger_metadata,
                enqueued_time=cls._parse_datetime(enqueued_time),
                partition_key=cls._decode_typed_data(
                    partition_key, python_type=str),
                sequence_number=cls._decode_typed_data(
                    sequence_number, python_type=int),
                offset=cls._decode_typed_data(
                    offset, python_type=int),
                iothub_metadata=cls._extract_iothub_from_dict(
                    parsed_sys_props[i])
            )

            events.append(event)

        return events

    @classmethod
    def _marshall_event_body(cls, parsed_data, data_type):
        # In IoTHub, when setting the eventhub using cardinality = 'many'
        # The data is wrapped inside a json (e.g. '[{ "device-id": "1" }]')

        # Previously, since the IoTHub events has a 'json' datatype,
        # it is handled as single_event by mistake and our users handle the
        # data parsing. And we want to keep the same behavior here.
        if data_type == 'json':
            return json.dumps(parsed_data).encode('utf-8')
        elif data_type == 'bytes':
            return parsed_data
        elif data_type == 'string':
            return parsed_data.encode('utf-8')
        elif data_type == 'collection_bytes':
            return parsed_data
        elif data_type == 'collection_string':
            return parsed_data.encode('utf-8')

        return parsed_data

    @classmethod
    def _decode_iothub_metadata(
            cls, trigger_metadata) -> Dict[str, str]:
        # Try extracting iothub_metadata from trigger_metadata
        iothub_metadata = cls._extract_iothub_from_trigger_metadata(
            trigger_metadata)

        # Try extracting iothub_metadata from SystemProperties
        if not iothub_metadata and trigger_metadata.get('SystemProperties'):
            iothub_metadata = cls._extract_iothub_from_system_properties(
                trigger_metadata['SystemProperties'].value)

        return iothub_metadata

    @classmethod
    def _extract_iothub_from_trigger_metadata(
            cls, metadict: Mapping[str, meta.Datum]) -> Dict[str, str]:
        iothub_metadata = {}
        for f in metadict:
            if f.startswith('iothub-'):
                v = cls._decode_trigger_metadata_field(
                    metadict, f, python_type=str)
                iothub_metadata[f[len('iothub-'):]] = v
        return iothub_metadata

    @classmethod
    def _extract_iothub_from_system_properties(
            cls, system_properties_string: str) -> Dict[str, str]:
        system_properties = json.loads(system_properties_string)
        return cls._extract_iothub_from_dict(system_properties)

    @classmethod
    def _extract_iothub_from_dict(
            cls, metadict: Dict[str, str]) -> Dict[str, str]:
        iothub_metadata = {}
        for f in metadict:
            if f.startswith('iothub-'):
                iothub_metadata[f[len('iothub-'):]] = metadict[f]
        return iothub_metadata

    @classmethod
    def _is_cardinality_many(cls, trigger_metadata) -> bool:
        return 'SystemPropertiesArray' in trigger_metadata

    @classmethod
    def _is_cardinality_one(cls, trigger_metadata) -> bool:
        return 'SystemProperties' in trigger_metadata
