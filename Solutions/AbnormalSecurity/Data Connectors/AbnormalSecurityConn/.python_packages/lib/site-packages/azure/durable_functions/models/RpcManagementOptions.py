from datetime import datetime
from typing import Any, List, Optional

from azure.durable_functions.constants import DATETIME_STRING_FORMAT
from azure.durable_functions.models.OrchestrationRuntimeStatus import OrchestrationRuntimeStatus

from .utils.entity_utils import EntityId


class RpcManagementOptions:
    """Class used to collect the options for getting orchestration status."""

    def __init__(self, instance_id: str = None, task_hub_name: str = None,
                 connection_name: str = None, show_history: bool = None,
                 show_history_output: bool = None, created_time_from: datetime = None,
                 created_time_to: datetime = None,
                 runtime_status: List[OrchestrationRuntimeStatus] = None, show_input: bool = None,
                 operation_name: str = None,
                 entity_Id: EntityId = None):
        self._instance_id = instance_id
        self._task_hub_name = task_hub_name
        self._connection_name = connection_name
        self._show_history = show_history
        self._show_history_output = show_history_output
        self._created_time_from = created_time_from
        self._created_time_to = created_time_to
        self._runtime_status = runtime_status
        self._show_input = show_input
        self.operation_name = operation_name
        self.entity_Id = entity_Id

    @staticmethod
    def _add_arg(query: List[str], name: str, value: Any):
        if value:
            query.append(f'{name}={value}')

    @staticmethod
    def _add_date_arg(query: List[str], name: str, value: Optional[datetime]):
        if value:
            date_as_string = value.strftime(DATETIME_STRING_FORMAT)
            RpcManagementOptions._add_arg(query, name, date_as_string)

    def to_url(self, base_url: Optional[str]) -> str:
        """Get the url based on the options selected.

        Parameters
        ----------
        base_url: str
            The base url to prepend to the url path

        Raises
        ------
        ValueError
            When the `base_url` argument is None

        Returns
        -------
        str
            The Url used to get orchestration status information
        """
        if base_url is None:
            raise ValueError("orchestration bindings has not RPC base url")

        if self.entity_Id:
            url = f'{base_url}{EntityId.get_entity_id_url_path(self.entity_Id)}'
        else:
            url = f"{base_url}instances/{self._instance_id if self._instance_id else ''}"

        query: List[str] = []

        self._add_arg(query, 'taskHub', self._task_hub_name)
        self._add_arg(query, 'connectionName', self._connection_name)
        self._add_arg(query, 'showInput', self._show_input)
        self._add_arg(query, 'showHistory', self._show_history)
        self._add_arg(query, 'showHistoryOutput', self._show_history_output)
        self._add_date_arg(query, 'createdTimeFrom', self._created_time_from)
        self._add_date_arg(query, 'createdTimeTo', self._created_time_to)
        self._add_arg(query, 'op', self.operation_name)
        if self._runtime_status is not None and len(self._runtime_status) > 0:
            runtime_status = ",".join(r.value for r in self._runtime_status)
            self._add_arg(query, 'runtimeStatus', runtime_status)

        if len(query) > 0:
            url += "?" + "&".join(query)

        return url
