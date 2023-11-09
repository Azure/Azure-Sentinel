from typing import Any


class EntityStateResponse:
    """Entity state response object for [read_entity_state]."""

    def __init__(self, entity_exists: bool, entity_state: Any = None) -> None:
        self._entity_exists = entity_exists
        self._entity_state = entity_state

    @property
    def entity_exists(self) -> bool:
        """Get the bool representing whether entity exists."""
        return self._entity_exists

    @property
    def entity_state(self) -> Any:
        """Get the state of the entity.

        When [entity_exists] is False, this value will be None.
        Optional.
        """
        return self._entity_state
