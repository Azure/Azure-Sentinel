from enum import Enum


class OrchestrationRuntimeStatus(Enum):
    """The status of an orchestration instance."""

    Running = 'Running'
    """The orchestration instance has started running."""

    Completed = 'Completed'
    """The orchestration instance has completed normally."""

    ContinuedAsNew = 'ContinuedAsNew'
    """The orchestration instance has restarted itself with a new history.

    This is a transient state.
    """

    Failed = 'Failed'
    """The orchestration instance failed with an error."""

    Canceled = 'Canceled'
    """The orchestration was canceled gracefully."""

    Terminated = 'Terminated'
    """The orchestration instance was stopped abruptly."""

    Pending = 'Pending'
    """The orchestration instance has been scheduled but has not yet started running."""
