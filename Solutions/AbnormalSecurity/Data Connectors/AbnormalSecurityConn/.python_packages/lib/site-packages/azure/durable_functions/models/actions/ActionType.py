from enum import IntEnum


class ActionType(IntEnum):
    """Defines the values associated to the types of activities that can be scheduled."""

    CALL_ACTIVITY: int = 0
    CALL_ACTIVITY_WITH_RETRY: int = 1
    CALL_SUB_ORCHESTRATOR: int = 2
    CALL_SUB_ORCHESTRATOR_WITH_RETRY: int = 3
    CONTINUE_AS_NEW: int = 4
    CREATE_TIMER: int = 5
    WAIT_FOR_EXTERNAL_EVENT: int = 6
    CALL_ENTITY = 7
    CALL_HTTP: int = 8
    SIGNAL_ENTITY: int = 9
    WHEN_ANY = 11
    WHEN_ALL = 12
