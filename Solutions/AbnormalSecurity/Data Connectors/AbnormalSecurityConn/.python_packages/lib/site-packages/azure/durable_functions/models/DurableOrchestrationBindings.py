import json
from typing import Dict, Optional

from azure.durable_functions.models.FunctionContext import FunctionContext


class DurableOrchestrationBindings:
    """Binding information.

    Provides information relevant to the creation and management of
    durable functions.
    """

    # parameter names are as defined by JSON schema and do not conform to PEP8 naming conventions
    def __init__(self, taskHubName: str, creationUrls: Dict[str, str],
                 managementUrls: Dict[str, str], rpcBaseUrl: Optional[str] = None, **kwargs):
        self._task_hub_name: str = taskHubName
        self._creation_urls: Dict[str, str] = creationUrls
        self._management_urls: Dict[str, str] = managementUrls
        # TODO: we can remove the Optional once we drop support for 1.x,
        # this is always provided in 2.x
        self._rpc_base_url: Optional[str] = rpcBaseUrl
        self._client_data = FunctionContext(**kwargs)

    @property
    def task_hub_name(self) -> str:
        """Get the name of the container that is used for orchestrations."""
        return self._task_hub_name

    @property
    def creation_urls(self) -> Dict[str, str]:
        """Get the URLs that are used for creating new orchestrations."""
        return self._creation_urls

    @property
    def management_urls(self) -> Dict[str, str]:
        """Get the URLs that are used for managing orchestrations."""
        return self._management_urls

    @property
    def rpc_base_url(self) -> Optional[str]:
        """Get the base url communication between out of proc workers and the function host."""
        return self._rpc_base_url

    @property
    def client_data(self) -> FunctionContext:
        """Get any additional client data provided within the context of the client."""
        return self._client_data

    @classmethod
    def from_json(cls, json_string):
        """Convert the value passed into a new instance of the class.

        Parameters
        ----------
        json_string
            Context passed a JSON serializable value to be converted into an
            instance of the class

        Returns
        -------
        DurableOrchestrationBindings
            New instance of the durable orchestration binding class
        """
        json_dict = json.loads(json_string)
        return cls(**json_dict)
