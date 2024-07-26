# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import datetime
from typing import Optional, Dict, Any


class ServiceBusMessage(abc.ABC):

    @abc.abstractmethod
    def get_body(self) -> bytes:
        """Get the message body from ServiceBus

        Returns:
        --------
        bytes
            The ServiceBus message body in bytes form
        """
        pass

    @property
    @abc.abstractmethod
    def content_type(self) -> Optional[str]:
        """Optionally describes the payload of the message,
        with a descriptor following the format of RFC2045

        Returns:
        --------
        Optional[str]
            If content type is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def correlation_id(self) -> Optional[str]:
        """Enables an application to specify a context for the message for the
        purposes of correlation

        Returns:
        --------
        Optional[str]
            If correlation id set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def dead_letter_source(self) -> Optional[str]:
        """Only set in messages that have been dead-lettered and subsequently
        auto-forwarded from the dead-letter queue to another entity.
        Indicates the entity in which the message was dead-lettered.
        This property is read-only.

        Returns:
        --------
        Optional[str]
            If dead letter source is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def delivery_count(self) -> Optional[int]:
        """Number of deliveries that have been attempted for this message.
        The count is incremented when a message lock expires,
        or the message is explicitly abandoned by the receiver.
        This property is read-only.

        Returns:
        --------
        Optional[str]
            If delivery count is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def enqueued_time_utc(self) -> Optional[datetime.datetime]:
        """The UTC instant at which the message has been accepted and stored
        in the entity. This value can be used as an authoritative and neutral
        arrival time indicator when the receiver does not want to trust the
        sender's clock. This property is read-only.

        Returns:
        --------
        Optional[datetime.datetime]
            If enqueued time utc is set, returns a datetime.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def expires_at_utc(self) -> Optional[datetime.datetime]:
        """The UTC instant at which the message is marked for removal and no
        longer available for retrieval from the entity due to its expiration.
        Expiry is controlled by the TimeToLive property and this property is
        computed from EnqueuedTimeUtc+TimeToLive. This property is read-only.

        Returns:
        --------
        Optional[datetime.datetime]
            If expires at utc is set, returns a datetime.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def expiration_time(self) -> Optional[datetime.datetime]:
        """(Deprecated, use expires_at_utc instead)"""
        pass

    @property
    @abc.abstractmethod
    def label(self) -> Optional[str]:
        """This property enables the application to indicate the purpose of
        the message to the receiver in a standardized fashion, similar to an
        email subject line.

        Returns:
        --------
        Optional[str]
            If label is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def lock_token(self) -> Optional[str]:
        """	The lock token is a reference to the lock that is being held by
        the broker in peek-lock receive mode. The token can be used to pin the
        lock permanently through the Deferral API and, with that, take the
        message out of the regular delivery state flow.
        This property is read-only.

        Returns:
        --------
        Optional[str]
            If local token is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def message_id(self) -> str:
        """The message identifier is an application-defined value that
        uniquely identifies the message and its payload.
        The identifier is a free-form string and can reflect a GUID or an
        identifier derived from the application context. If enabled, the
        duplicate detection feature identifies and removes second and further
        submissions of messages with the same MessageId.

        Returns:
        --------
        str
            The message identifier
        """
        pass

    @property
    @abc.abstractmethod
    def partition_key(self) -> Optional[str]:
        """	For partitioned entities, setting this value enables assigning
        related messages to the same internal partition, so that submission
        sequence order is correctly recorded. The partition is chosen by a
        hash function over this value and cannot be chosen directly. For
        session-aware entities, the SessionId property overrides this value.

        Returns:
        --------
        Optional[str]
            If partition key is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def reply_to(self) -> Optional[str]:
        """This optional and application-defined value is a standard way to
        express a reply path to the receiver of the message. When a sender
        expects a reply, it sets the value to the absolute or relative path
        of the queue or topic it expects the reply to be sent to.

        Returns:
        --------
        Optional[str]
            If reply to is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def reply_to_session_id(self) -> Optional[str]:
        """This value augments the ReplyTo information and specifies which
        SessionId should be set for the reply when sent to the reply entity.

        Returns:
        --------
        Optional[str]
            If reply to session id is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def scheduled_enqueue_time(self) -> Optional[datetime.datetime]:
        """(Deprecated, use scheduled_enqueue_time_utc instead)"""
        pass

    @property
    @abc.abstractmethod
    def scheduled_enqueue_time_utc(self) -> Optional[datetime.datetime]:
        """For messages that are only made available for retrieval after a
        delay, this property defines the UTC instant at which the message
        will be logically enqueued, sequenced, and therefore made available
        for retrieval.

        Returns:
        --------
        Optional[datetime.datetime]
            If scheduled enqueue time utc is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def sequence_number(self) -> Optional[int]:
        """The sequence number is a unique 64-bit integer assigned to a message
        as it is accepted and stored by the broker and functions as its true
        identifier. For partitioned entities, the topmost 16 bits reflect the
        partition identifier. Sequence numbers monotonically increase and are
        gapless. They roll over to 0 when the 48-64 bit range is exhausted.
        This property is read-only.

        Returns:
        --------
        Optional[int]
            If sequence number is set, returns an integer.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def session_id(self) -> Optional[str]:
        """For session-aware entities, this application-defined value
        specifies the session affiliation of the message. Messages with the
        same session identifier are subject to summary locking and enable
        exact in-order processing and demultiplexing. For entities that are
        not session-aware, this value is ignored.

        Returns:
        --------
        Optional[str]
            If session id is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def time_to_live(self) -> Optional[datetime.timedelta]:
        """	This value is the relative duration after which the message
        expires, starting from the instant the message has been accepted and
        stored by the broker, as captured in EnqueueTimeUtc. When not set
        explicitly, the assumed value is the DefaultTimeToLive for the
        respective queue or topic. A message-level TimeToLive value cannot
        be longer than the entity's DefaultTimeToLive setting.
        If it is longer, it is silently adjusted.

        Returns:
        --------
        Optional[datetime.timedelta]
            If time to live is set, returns a timedelta.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def to(self) -> Optional[str]:
        """	This property is reserved for future use in routing scenarios and
        currently ignored by the broker itself. Applications can use this
        value in rule-driven auto-forward chaining scenarios to indicate the
        intended logical destination of the message.

        Returns:
        --------
        Optional[str]
            If the recipient is set, returns a string.
            Otherwise, returns None.
        """
        pass

    @property
    @abc.abstractmethod
    def user_properties(self) -> Dict[str, Any]:
        """Contains user defined message properties.

        Returns:
        --------
        Dict[str, Any]:
            If user has set properties for the message, returns a dictionary.
            If nothing is set, returns an empty dictionary.
        """
        pass

    @property
    @abc.abstractmethod
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Getting read-only trigger metadata in a Python dictionary.

        Exposing the raw trigger_metadata to our customer. For cardinality=many
        scenarios, each event points to the common metadata of all the events.

        So when using metadata field when cardinality=many, it only needs to
        take one of the events to get all the data (e.g. events[0].metadata).

        Returns:
        --------
        Dict[str, object]
            Return the Python dictionary of trigger metadata
        """
        pass
