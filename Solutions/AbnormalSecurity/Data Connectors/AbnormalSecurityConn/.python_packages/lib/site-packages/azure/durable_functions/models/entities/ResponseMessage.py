from typing import Dict, Any


class ResponseMessage:
    """ResponseMessage.

    Specifies the response of an entity, as processed by the durable-extension.
    """

    def __init__(self, result: str):
        """Instantiate a ResponseMessage.

        Specifies the response of an entity, as processed by the durable-extension.

        Parameters
        ----------
        result: str
            The result provided by the entity
        """
        self.result = result
        # TODO: JS has an additional exceptionType field, but does not use it

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ResponseMessage':
        """Instantiate a ResponseMessage from a dict of the JSON-response by the extension.

        Parameters
        ----------
        d: Dict[str, Any]
            The dictionary parsed from the JSON-response by the durable-extension

        Returns
        -------
        ResponseMessage:
            The ResponseMessage built from the provided dictionary
        """
        result = cls(d["result"])
        return result
