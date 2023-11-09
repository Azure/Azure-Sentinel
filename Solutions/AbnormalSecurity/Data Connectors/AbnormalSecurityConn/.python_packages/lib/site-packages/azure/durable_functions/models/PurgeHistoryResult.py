from typing import Dict, Any


class PurgeHistoryResult:
    """Information provided when the request to purge history has been made."""

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    def __init__(self, instancesDeleted: int, **kwargs):
        self._instances_deleted: int = instancesDeleted
        if kwargs is not None:
            for key, value in kwargs.items():
                self.__setattr__(key, value)

    @classmethod
    def from_json(cls, json_obj: Dict[Any, Any]):
        """Convert the value passed into a new instance of the class.

        Parameters
        ----------
        json_obj: Dict[Any, Any]
            JSON object to be converted into an instance of the class

        Returns
        -------
        PurgeHistoryResult
            New instance of the durable orchestration status class
        """
        return cls(**json_obj)

    @property
    def instances_deleted(self):
        """Get the number of deleted instances."""
        return self._instances_deleted
