from typing import Dict, Any
from abc import ABC, abstractmethod


class Action(ABC):
    """Defines the base abstract class for Actions that need to be implemented."""

    @property
    @abstractmethod
    def action_type(self) -> int:
        """Get the type of action this class represents."""
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """Convert object into a json dictionary.

        Returns
        -------
        Dict[str, Any]
            The instance of the class converted into a json dictionary
        """
        pass
