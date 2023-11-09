from .ActionType import ActionType
from azure.durable_functions.models.actions.CompoundAction import CompoundAction


class WhenAllAction(CompoundAction):
    """Defines the structure of the WhenAll Action object.

    Provides the information needed by the durable extension to be able to invoke WhenAll tasks.
    """

    @property
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        return ActionType.WHEN_ALL
