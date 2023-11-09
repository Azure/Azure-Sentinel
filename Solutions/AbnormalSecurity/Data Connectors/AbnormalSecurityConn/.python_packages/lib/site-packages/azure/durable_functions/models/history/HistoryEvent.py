import datetime
from dateutil.parser import parse as dt_parse
from .HistoryEventType import HistoryEventType


class HistoryEvent:
    """Used to communicate state relevant information from the durable extension to the client."""

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    def __init__(self, EventType: HistoryEventType, EventId: int, IsPlayed: bool, Timestamp: str,
                 **kwargs):
        self._event_type: HistoryEventType = EventType
        self._event_id: int = EventId
        self._is_played: bool = IsPlayed
        self._timestamp: datetime.datetime = dt_parse(Timestamp)
        self._is_processed: bool = False

        self.Name = None
        self.InstanceId = None
        self.TaskScheduledId = None
        self.Reason = None
        self.Details = None
        self.Input = None
        if kwargs is not None:
            for key, value in kwargs.items():
                self.__setattr__(key, value)

    @property
    def event_type(self) -> HistoryEventType:
        """Get the history event type property.

        Returns
        -------
        HistoryEventType
            The type of history event
        """
        return self._event_type

    @property
    def event_id(self) -> int:
        """Get the event ID property.

        Returns
        -------
        int
            The value that represents the event sequence
        """
        return self._event_id

    @property
    def is_played(self) -> bool:
        """Get the is played property.

        Returns
        -------
        bool
            Value indicating whether the event has been played
        """
        return self._is_played

    @property
    def is_processed(self) -> bool:
        """Get the is process property.

        Returns
        -------
        bool
            Value indicating whether the orchestrator has processed the event
        """
        return self._is_processed

    @is_processed.setter
    def is_processed(self, value: bool):
        """Set the is processed property.

        Parameters
        ----------
        bool
            Value to set the property to
        """
        self._is_processed = value

    @property
    def timestamp(self) -> datetime.datetime:
        """Get the timestamp property.

        Returns
        -------
        datetime
            Value indicating the the time the event occurred
        """
        return self._timestamp
