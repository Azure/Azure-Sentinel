# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
from base64 import b64decode
from datetime import datetime
from .utils._utils import _convert_to_isoformat, TZ_UTC
from .utils._messaging_shared import _get_json_content
from .serialization import NULL

try:
    from typing import TYPE_CHECKING, cast, Union
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Optional, Dict


__all__ = ["CloudEvent"]


class CloudEvent(object):  # pylint:disable=too-many-instance-attributes
    """Properties of the CloudEvent 1.0 Schema.
    All required parameters must be populated in order to send to Azure.

    :param source: Required. Identifies the context in which an event happened. The combination of id and source must
     be unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :type source: str
    :param type: Required. Type of event related to the originating occurrence.
    :type type: str
    :keyword data: Optional. Event data specific to the event type.
    :type data: object
    :keyword time: Optional. The time (in UTC) the event was generated.
    :type time: ~datetime.datetime
    :keyword dataschema: Optional. Identifies the schema that data adheres to.
    :type dataschema: str
    :keyword datacontenttype: Optional. Content type of data value.
    :type datacontenttype: str
    :keyword subject: Optional. This describes the subject of the event in the context of the event producer
     (identified by source).
    :type subject: str
    :keyword specversion: Optional. The version of the CloudEvent spec. Defaults to "1.0"
    :type specversion: str
    :keyword id: Optional. An identifier for the event. The combination of id and source must be
     unique for each distinct event. If not provided, a random UUID will be generated and used.
    :type id: Optional[str]
    :keyword extensions: Optional. A CloudEvent MAY include any number of additional context attributes
     with distinct names represented as key - value pairs. Each extension must be alphanumeric, lower cased
     and must not exceed the length of 20 characters.
    :type extensions: Optional[Dict]
    :ivar source: Identifies the context in which an event happened. The combination of id and source must
     be unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :vartype source: str
    :ivar data: Event data specific to the event type.
    :vartype data: object
    :ivar type: Type of event related to the originating occurrence.
    :vartype type: str
    :ivar time: The time (in UTC) the event was generated.
    :vartype time: ~datetime.datetime
    :ivar dataschema: Identifies the schema that data adheres to.
    :vartype dataschema: str
    :ivar datacontenttype: Content type of data value.
    :vartype datacontenttype: str
    :ivar subject: This describes the subject of the event in the context of the event producer
     (identified by source).
    :vartype subject: str
    :ivar specversion: Optional. The version of the CloudEvent spec. Defaults to "1.0"
    :vartype specversion: str
    :ivar id: An identifier for the event. The combination of id and source must be
     unique for each distinct event. If not provided, a random UUID will be generated and used.
    :vartype id: str
    :ivar extensions: A CloudEvent MAY include any number of additional context attributes
     with distinct names represented as key - value pairs. Each extension must be alphanumeric, lower cased
     and must not exceed the length of 20 characters.
    :vartype extensions: Dict
    """

    def __init__(self, source, type, **kwargs):  # pylint: disable=redefined-builtin
        # type: (str, str, **Any) -> None
        self.source = source  # type: str
        self.type = type  # type: str
        self.specversion = kwargs.pop("specversion", "1.0")  # type: Optional[str]
        self.id = kwargs.pop("id", str(uuid.uuid4()))  # type: Optional[str]
        self.time = kwargs.pop("time", datetime.now(TZ_UTC))  # type: Optional[datetime]

        self.datacontenttype = kwargs.pop("datacontenttype", None)  # type: Optional[str]
        self.dataschema = kwargs.pop("dataschema", None)  # type: Optional[str]
        self.subject = kwargs.pop("subject", None)  # type: Optional[str]
        self.data = kwargs.pop("data", None)  # type: Optional[object]

        try:
            self.extensions = kwargs.pop("extensions")  # type: Optional[Dict]
            for key in self.extensions.keys():  # type:ignore # extensions won't be None here
                if not key.islower() or not key.isalnum():
                    raise ValueError(
                        "Extension attributes should be lower cased and alphanumeric."
                    )
        except KeyError:
            self.extensions = None

        if kwargs:
            remaining = ", ".join(kwargs.keys())
            raise ValueError(
                "Unexpected keyword arguments {}. Any extension attributes must be passed explicitly using extensions."
                .format(remaining)
            )

    def __repr__(self):
        return "CloudEvent(source={}, type={}, specversion={}, id={}, time={})".format(
            self.source, self.type, self.specversion, self.id, self.time
        )[:1024]

    @classmethod
    def from_dict(cls, event):
        # type: (Dict) -> CloudEvent
        """
        Returns the deserialized CloudEvent object when a dict is provided.
        :param event: The dict representation of the event which needs to be deserialized.
        :type event: dict
        :rtype: CloudEvent
        """
        kwargs = {}  # type: Dict[Any, Any]
        reserved_attr = [
            "data",
            "data_base64",
            "id",
            "source",
            "type",
            "specversion",
            "time",
            "dataschema",
            "datacontenttype",
            "subject",
        ]

        if "data" in event and "data_base64" in event:
            raise ValueError(
                "Invalid input. Only one of data and data_base64 must be present."
            )

        if "data" in event:
            data = event.get("data")
            kwargs["data"] = data if data is not None else NULL
        elif "data_base64" in event:
            kwargs["data"] = b64decode(
                cast(Union[str, bytes], event.get("data_base64"))
            )

        for item in ["datacontenttype", "dataschema", "subject"]:
            if item in event:
                val = event.get(item)
                kwargs[item] = val if val is not None else NULL

        extensions = {k: v for k, v in event.items() if k not in reserved_attr}
        if extensions:
            kwargs["extensions"] = extensions

        try:
            event_obj = cls(
                id=event.get("id"),
                source=event["source"],
                type=event["type"],
                specversion=event.get("specversion"),
                time=_convert_to_isoformat(event.get("time")),
                **kwargs
            )
        except KeyError:
            # https://github.com/cloudevents/spec Cloud event spec requires source, type,
            # specversion. We autopopulate everything other than source, type.
            if not all([_ in event for _ in ("source", "type")]):
                if all([_ in event for _ in ("subject", "eventType", "data", "dataVersion", "id", "eventTime")]):
                    raise ValueError(
                        "The event you are trying to parse follows the Eventgrid Schema. You can parse" +
                        " EventGrid events using EventGridEvent.from_dict method in the azure-eventgrid library."
                    )
                raise ValueError(
                    "The event does not conform to the cloud event spec https://github.com/cloudevents/spec." +
                    " The `source` and `type` params are required."
                    )
        return event_obj

    @classmethod
    def from_json(cls, event):
        # type: (Any) -> CloudEvent
        """
        Returns the deserialized CloudEvent object when a json payload is provided.
        :param event: The json string that should be converted into a CloudEvent. This can also be
         a storage QueueMessage, eventhub's EventData or ServiceBusMessage
        :type event: object
        :rtype: CloudEvent
        :raises ValueError: If the provided JSON is invalid.
        """
        dict_event = _get_json_content(event)
        return CloudEvent.from_dict(dict_event)
