from azure.durable_functions.models.actions.Action import Action
from typing import Any, Dict


class NoOpAction(Action):
    """A no-op action, for anonymous tasks only."""

    def action_type(self) -> int:
        """Get the type of action this class represents."""
        raise Exception("Attempted to get action type of an anonymous Action")

    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        raise Exception("Attempted to convert an anonymous Action to JSON")
