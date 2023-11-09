import json
from datetime import datetime
from typing import List, Any, Optional, Dict, Union
from time import time
from asyncio import sleep
from urllib.parse import urlparse, quote

import azure.functions as func

from .PurgeHistoryResult import PurgeHistoryResult
from .DurableOrchestrationStatus import DurableOrchestrationStatus
from .EntityStateResponse import EntityStateResponse
from .RpcManagementOptions import RpcManagementOptions
from .OrchestrationRuntimeStatus import OrchestrationRuntimeStatus
from ..models.DurableOrchestrationBindings import DurableOrchestrationBindings
from .utils.http_utils import get_async_request, post_async_request, delete_async_request
from .utils.entity_utils import EntityId
from azure.functions._durable_functions import _serialize_custom_object


class DurableOrchestrationClient:
    """Durable Orchestration Client.

    Client for starting, querying, terminating and raising events to
    orchestration instances.
    """

    def __init__(self, context: str):
        self.task_hub_name: str
        self._uniqueWebHookOrigins: List[str]
        self._event_name_placeholder: str = "{eventName}"
        self._function_name_placeholder: str = "{functionName}"
        self._instance_id_placeholder: str = "[/{instanceId}]"
        self._reason_placeholder: str = "{text}"
        self._created_time_from_query_key: str = "createdTimeFrom"
        self._created_time_to_query_key: str = "createdTimeTo"
        self._runtime_status_query_key: str = "runtimeStatus"
        self._show_history_query_key: str = "showHistory"
        self._show_history_output_query_key: str = "showHistoryOutput"
        self._show_input_query_key: str = "showInput"
        self._orchestration_bindings: DurableOrchestrationBindings = \
            DurableOrchestrationBindings.from_json(context)
        self._post_async_request = post_async_request
        self._get_async_request = get_async_request
        self._delete_async_request = delete_async_request

    async def start_new(self,
                        orchestration_function_name: str,
                        instance_id: Optional[str] = None,
                        client_input: Optional[Any] = None) -> str:
        """Start a new instance of the specified orchestrator function.

        If an orchestration instance with the specified ID already exists, the
        existing instance will be silently replaced by this new instance.

        Parameters
        ----------
        orchestration_function_name : str
            The name of the orchestrator function to start.
        instance_id : Optional[str]
            The ID to use for the new orchestration instance. If no instance id is specified,
            the Durable Functions extension will generate a random GUID (recommended).
        client_input : Optional[Any]
            JSON-serializable input value for the orchestrator function.

        Returns
        -------
        str
            The ID of the new orchestration instance if successful, None if not.
        """
        request_url = self._get_start_new_url(
            instance_id=instance_id, orchestration_function_name=orchestration_function_name)

        response: List[Any] = await self._post_async_request(
            request_url, self._get_json_input(client_input))

        status_code: int = response[0]
        if status_code <= 202 and response[1]:
            return response[1]["id"]
        elif status_code == 400:
            # Orchestrator not found, report clean exception
            exception_data: Dict[str, str] = response[1]
            exception_message = exception_data["ExceptionMessage"]
            raise Exception(exception_message)
        else:
            # Catch all: simply surfacing the durable-extension exception
            # we surface the stack trace too, since this may be a more involed exception
            ex_message: Any = response[1]
            raise Exception(ex_message)

    def create_check_status_response(
            self, request: func.HttpRequest, instance_id: str) -> func.HttpResponse:
        """Create a HttpResponse that contains useful information for \
        checking the status of the specified instance.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request that triggered the current orchestration instance.
        instance_id : str
            The ID of the orchestration instance to check.

        Returns
        -------
        HttpResponse
           An HTTP 202 response with a Location header
           and a payload containing instance management URLs
        """
        http_management_payload = self.get_client_response_links(request, instance_id)
        response_args = {
            "status_code": 202,
            "body": json.dumps(http_management_payload),
            "headers": {
                "Content-Type": "application/json",
                "Location": http_management_payload["statusQueryGetUri"],
                "Retry-After": "10",
            },
        }
        return func.HttpResponse(**response_args)

    def create_http_management_payload(self, instance_id: str) -> Dict[str, str]:
        """Create a dictionary of orchestrator management urls.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance to check.

        Returns
        -------
        Dict[str, str]
            a dictionary object of orchestrator instance management urls
        """
        return self.get_client_response_links(None, instance_id)

    async def read_entity_state(
        self,
        entityId: EntityId,
        task_hub_name: Optional[str] = None,
        connection_name: Optional[str] = None,
    ) -> EntityStateResponse:
        """Read the state of the entity.

        Parameters
        ----------
        entityId : EntityId
            The EntityId of the targeted entity.
        task_hub_name : Optional[str]
            The task hub name of the target entity.
        connection_name : Optional[str]
            The name of the connection string associated with [task_hub_name].

        Raises
        ------
        Exception:
            When an unexpected status code is returned

        Returns
        -------
        EntityStateResponse
            container object representing the state of the entity
        """
        options = RpcManagementOptions(
            connection_name=connection_name,
            task_hub_name=task_hub_name,
            entity_Id=entityId,
        )

        request_url = options.to_url(self._orchestration_bindings.rpc_base_url)
        response = await self._get_async_request(request_url)

        switch_statement = {
            200: lambda: EntityStateResponse(True, response[1]),
            404: lambda: EntityStateResponse(False),
        }

        result = switch_statement.get(response[0])

        if not result:
            raise Exception(
                f"The operation failed with an unexpected status code {response[0]}"
            )

        return result()

    def get_client_response_links(
            self,
            request: Optional[func.HttpRequest], instance_id: str) -> Dict[str, str]:
        """Create a dictionary of orchestrator management urls.

        Parameters
        ----------
        request : Optional[HttpRequest]
            The HTTP request that triggered the current orchestration instance.
        instance_id : str
            The ID of the orchestration instance to check.

        Returns
        -------
        Dict[str, str]
            a dictionary object of orchestrator instance management urls
        """
        payload = self._orchestration_bindings.management_urls.copy()

        for key, _ in payload.items():
            if not(request is None) and request.url:
                payload[key] = self._replace_url_origin(request.url, payload[key])
            payload[key] = payload[key].replace(
                self._orchestration_bindings.management_urls["id"], instance_id)

        return payload

    async def raise_event(
            self, instance_id: str, event_name: str, event_data: Any = None,
            task_hub_name: str = None, connection_name: str = None) -> None:
        """Send an event notification message to a waiting orchestration instance.

        In order to handle the event, the target orchestration instance must be
        waiting for an event named `eventName` using waitForExternalEvent API.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance that will handle the event.
        event_name : str
            The name of the event.
        event_data : Any, optional
            The JSON-serializable data associated with the event.
        task_hub_name : str, optional
            The TaskHubName of the orchestration that will handle the event.
        connection_name : str, optional
            The name of the connection string associated with `taskHubName.`

        Raises
        ------
        ValueError
            event name must be a valid string.
        Exception
            Raises an exception if the status code is 404 or 400 when raising the event.
        """
        if event_name == "":
            raise ValueError("event_name must be a non-empty string.")

        request_url = self._get_raise_event_url(
            instance_id, event_name, task_hub_name, connection_name)

        response = await self._post_async_request(request_url, json.dumps(event_data))

        switch_statement = {
            202: lambda: None,
            410: lambda: f"Instance with ID {instance_id} is gone: either completed or failed",
            404: lambda: f"No instance with ID {instance_id} found.",
            400: lambda: "Only application/json request content is supported"
        }
        has_error_message = switch_statement.get(
            response[0], lambda: f"Webhook returned unrecognized status code {response[0]}")
        error_message = has_error_message()
        if error_message:
            raise Exception(error_message)

    async def get_status(self, instance_id: str, show_history: bool = False,
                         show_history_output: bool = False,
                         show_input: bool = False) -> DurableOrchestrationStatus:
        """Get the status of the specified orchestration instance.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance to query.
        show_history: bool
            Boolean marker for including execution history in the response.
        show_history_output: bool
            Boolean marker for including output in the execution history response.
        show_input: bool
            Boolean marker for including the input in the response.

        Returns
        -------
        DurableOrchestrationStatus
            The status of the requested orchestration instance
        """
        options = RpcManagementOptions(instance_id=instance_id, show_history=show_history,
                                       show_history_output=show_history_output,
                                       show_input=show_input)
        request_url = options.to_url(self._orchestration_bindings.rpc_base_url)
        response = await self._get_async_request(request_url)
        switch_statement = {
            200: lambda: None,  # instance completed
            202: lambda: None,  # instance in progress
            400: lambda: None,  # instance failed or terminated
            404: lambda: None,  # instance not found or pending
            500: lambda: None  # instance failed with unhandled exception
        }

        has_error_message = switch_statement.get(
            response[0],
            lambda: f"The operation failed with an unexpected status code {response[0]}")
        error_message = has_error_message()
        if error_message:
            raise Exception(error_message)
        else:
            return DurableOrchestrationStatus.from_json(response[1])

    async def get_status_all(self) -> List[DurableOrchestrationStatus]:
        """Get the status of all orchestration instances.

        Returns
        -------
        DurableOrchestrationStatus
            The status of the requested orchestration instances
        """
        options = RpcManagementOptions()
        request_url = options.to_url(self._orchestration_bindings.rpc_base_url)
        response = await self._get_async_request(request_url)
        switch_statement = {
            200: lambda: None,  # instance completed
        }

        has_error_message = switch_statement.get(
            response[0],
            lambda: f"The operation failed with an unexpected status code {response[0]}")
        error_message = has_error_message()
        if error_message:
            raise Exception(error_message)
        else:
            statuses: List[Any] = response[1]
            return [DurableOrchestrationStatus.from_json(o) for o in statuses]

    async def get_status_by(self, created_time_from: datetime = None,
                            created_time_to: datetime = None,
                            runtime_status: List[OrchestrationRuntimeStatus] = None) \
            -> List[DurableOrchestrationStatus]:
        """Get the status of all orchestration instances that match the specified conditions.

        Parameters
        ----------
        created_time_from : datetime
            Return orchestration instances which were created after this Date.
        created_time_to: datetime
            Return orchestration instances which were created before this Date.
        runtime_status: List[OrchestrationRuntimeStatus]
            Return orchestration instances which match any of the runtimeStatus values
            in this list.

        Returns
        -------
        DurableOrchestrationStatus
            The status of the requested orchestration instances
        """
        # TODO: do we really want folks to us this without specifying all the args?
        options = RpcManagementOptions(created_time_from=created_time_from,
                                       created_time_to=created_time_to,
                                       runtime_status=runtime_status)
        request_url = options.to_url(self._orchestration_bindings.rpc_base_url)
        response = await self._get_async_request(request_url)
        switch_statement = {
            200: lambda: None,  # instance completed
        }

        has_error_message = switch_statement.get(
            response[0],
            lambda: f"The operation failed with an unexpected status code {response[0]}")
        error_message = has_error_message()
        if error_message:
            raise Exception(error_message)
        else:
            return [DurableOrchestrationStatus.from_json(o) for o in response[1]]

    async def purge_instance_history(self, instance_id: str) -> PurgeHistoryResult:
        """Delete the history of the specified orchestration instance.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance to delete.

        Returns
        -------
        PurgeHistoryResult
            The results of the request to delete the orchestration instance
        """
        request_url = f"{self._orchestration_bindings.rpc_base_url}instances/{instance_id}"
        response = await self._delete_async_request(request_url)
        return self._parse_purge_instance_history_response(response)

    async def purge_instance_history_by(
            self, created_time_from: Optional[datetime] = None,
            created_time_to: Optional[datetime] = None,
            runtime_status: Optional[List[OrchestrationRuntimeStatus]] = None) \
            -> PurgeHistoryResult:
        """Delete the history of all orchestration instances that match the specified conditions.

        Parameters
        ----------
        created_time_from : Optional[datetime]
            Delete orchestration history which were created after this Date.
        created_time_to: Optional[datetime]
            Delete orchestration history which were created before this Date.
        runtime_status: Optional[List[OrchestrationRuntimeStatus]]
            Delete orchestration instances which match any of the runtimeStatus values
            in this list.

        Returns
        -------
        PurgeHistoryResult
            The results of the request to purge history
        """
        options = RpcManagementOptions(created_time_from=created_time_from,
                                       created_time_to=created_time_to,
                                       runtime_status=runtime_status)
        request_url = options.to_url(self._orchestration_bindings.rpc_base_url)
        response = await self._delete_async_request(request_url)
        return self._parse_purge_instance_history_response(response)

    async def terminate(self, instance_id: str, reason: str) -> None:
        """Terminate the specified orchestration instance.

        Parameters
        ----------
        instance_id : str
            The ID of the orchestration instance to query.
        reason: str
            The reason for terminating the instance.

        Raises
        ------
        Exception:
            When the terminate call failed with an unexpected status code

        Returns
        -------
        None
        """
        request_url = f"{self._orchestration_bindings.rpc_base_url}instances/{instance_id}/" \
                      f"terminate?reason={quote(reason)}"
        response = await self._post_async_request(request_url, None)
        switch_statement = {
            202: lambda: None,  # instance in progress
            410: lambda: None,  # instance failed or terminated
            404: lambda: lambda: f"No instance with ID '{instance_id}' found.",
        }

        has_error_message = switch_statement.get(
            response[0],
            lambda: f"The operation failed with an unexpected status code {response[0]}")
        error_message = has_error_message()
        if error_message:
            raise Exception(error_message)

    async def wait_for_completion_or_create_check_status_response(
            self, request, instance_id: str, timeout_in_milliseconds: int = 10000,
            retry_interval_in_milliseconds: int = 1000) -> func.HttpResponse:
        """Create an HTTP response.

        The response either contains a payload of management URLs for a non-completed instance or
        contains the payload containing the output of the completed orchestration.

        If the orchestration does not complete within the specified timeout, then the HTTP response
        will be identical to that of [[createCheckStatusResponse]].

        Parameters
        ----------
        request
            The HTTP request that triggered the current function.
        instance_id:
            The unique ID of the instance to check.
        timeout_in_milliseconds:
            Total allowed timeout for output from the durable function.
            The default value is 10 seconds.
        retry_interval_in_milliseconds:
            The timeout between checks for output from the durable function.
            The default value is 1 second.
        """
        if retry_interval_in_milliseconds > timeout_in_milliseconds:
            raise Exception(f'Total timeout {timeout_in_milliseconds} (ms) should be bigger than '
                            f'retry timeout {retry_interval_in_milliseconds} (ms)')

        checking = True
        start_time = time()

        while checking:
            status = await self.get_status(instance_id)

            if status:
                switch_statement = {
                    OrchestrationRuntimeStatus.Completed:
                        lambda: self._create_http_response(200, status.output),
                    OrchestrationRuntimeStatus.Canceled:
                        lambda: self._create_http_response(200, status.to_json()),
                    OrchestrationRuntimeStatus.Terminated:
                        lambda: self._create_http_response(200, status.to_json()),
                    OrchestrationRuntimeStatus.Failed:
                        lambda: self._create_http_response(500, status.to_json()),
                    None:
                        None
                }

                result = switch_statement.get(status.runtime_status)
                if result:
                    return result()

            elapsed = time() - start_time
            elapsed_in_milliseconds = elapsed * 1000
            if elapsed_in_milliseconds < timeout_in_milliseconds:
                remaining_time = timeout_in_milliseconds - elapsed_in_milliseconds
                sleep_time = retry_interval_in_milliseconds \
                    if remaining_time > retry_interval_in_milliseconds else remaining_time
                sleep_time /= 1000
                await sleep(sleep_time)
            else:
                return self.create_check_status_response(request, instance_id)
        return self.create_check_status_response(request, instance_id)

    async def signal_entity(self, entityId: EntityId, operation_name: str,
                            operation_input: Optional[Any] = None,
                            task_hub_name: Optional[str] = None,
                            connection_name: Optional[str] = None) -> None:
        """Signals an entity to perform an operation.

        Parameters
        ----------
        entityId : EntityId
            The EntityId of the targeted entity to perform operation.
        operation_name: str
            The name of the operation.
        operation_input: Optional[Any]
            The content for the operation.
        task_hub_name: Optional[str]
            The task hub name of the target entity.
        connection_name: Optional[str]
            The name of the connection string associated with [task_hub_name].

        Raises
        ------
        Exception:
            When the signal entity call failed with an unexpected status code

        Returns
        -------
        None
        """
        options = RpcManagementOptions(operation_name=operation_name,
                                       connection_name=connection_name,
                                       task_hub_name=task_hub_name,
                                       entity_Id=entityId)

        request_url = options.to_url(self._orchestration_bindings.rpc_base_url)
        response = await self._post_async_request(
            request_url,
            json.dumps(operation_input) if operation_input else None)

        switch_statement = {
            202: lambda: None  # signal accepted
        }

        has_error_message = switch_statement.get(
            response[0],
            lambda: f"The operation failed with an unexpected status code {response[0]}")

        error_message = has_error_message()

        if error_message:
            raise Exception(error_message)

    @staticmethod
    def _create_http_response(
            status_code: int, body: Union[str, Any]) -> func.HttpResponse:
        body_as_json = body if isinstance(body, str) else json.dumps(body)
        response_args = {
            "status_code": status_code,
            "body": body_as_json,
            "mimetype": "application/json",
            "headers": {
                "Content-Type": "application/json",
            }
        }
        return func.HttpResponse(**response_args)

    @staticmethod
    def _get_json_input(client_input: object) -> Optional[str]:
        """Serialize the orchestrator input.

        Parameters
        ----------
        client_input: object
            The client's input, which we need to serialize

        Returns
        -------
        Optional[str]
            If `client_input` is not None, return a string representing
            the JSON-serialization of `client_input`. Otherwise, returns
            None

        Exceptions
        ----------
        TypeError
            If the JSON serialization failed, see `serialize_custom_object`
        """
        if client_input is not None:
            return json.dumps(client_input, default=_serialize_custom_object)
        return None

    @staticmethod
    def _replace_url_origin(request_url: str, value_url: str) -> str:
        request_parsed_url = urlparse(request_url)
        value_parsed_url = urlparse(value_url)
        request_url_origin = '{url.scheme}://{url.netloc}/'.format(url=request_parsed_url)
        value_url_origin = '{url.scheme}://{url.netloc}/'.format(url=value_parsed_url)
        value_url = value_url.replace(value_url_origin, request_url_origin)
        return value_url

    @staticmethod
    def _parse_purge_instance_history_response(
            response: List[Any]) -> PurgeHistoryResult:
        switch_statement = {
            200: lambda: PurgeHistoryResult.from_json(response[1]),  # instance completed
            404: lambda: PurgeHistoryResult(instancesDeleted=0),  # instance not found
        }

        switch_result = switch_statement.get(
            response[0],
            lambda: f"The operation failed with an unexpected status code {response[0]}")
        result = switch_result()
        if isinstance(result, PurgeHistoryResult):
            return result
        else:
            raise Exception(result)

    def _get_start_new_url(
            self, instance_id: Optional[str], orchestration_function_name: str) -> str:
        instance_path = f'/{instance_id}' if instance_id is not None else ''
        request_url = f'{self._orchestration_bindings.rpc_base_url}orchestrators/' \
                      f'{orchestration_function_name}{instance_path}'
        return request_url

    def _get_raise_event_url(
            self, instance_id: str, event_name: str,
            task_hub_name: Optional[str], connection_name: Optional[str]) -> str:
        request_url = f'{self._orchestration_bindings.rpc_base_url}' \
                      f'instances/{instance_id}/raiseEvent/{event_name}'

        query: List[str] = []
        if task_hub_name:
            query.append(f'taskHub={task_hub_name}')

        if connection_name:
            query.append(f'connection={connection_name}')

        if len(query) > 0:
            request_url += "?" + "&".join(query)

        return request_url

    async def rewind(self,
                     instance_id: str,
                     reason: str,
                     task_hub_name: Optional[str] = None,
                     connection_name: Optional[str] = None):
        """Return / "rewind" a failed orchestration instance to a prior "healthy" state.

        Parameters
        ----------
        instance_id: str
            The ID of the orchestration instance to rewind.
        reason: str
            The reason for rewinding the orchestration instance.
        task_hub_name: Optional[str]
            The TaskHub of the orchestration to rewind
        connection_name: Optional[str]
            Name of the application setting containing the storage
            connection string to use.

        Raises
        ------
        Exception:
            In case of a failure, it reports the reason for the exception
        """
        request_url: str = ""
        if self._orchestration_bindings.rpc_base_url:
            path = f"instances/{instance_id}/rewind?reason={reason}"
            query: List[str] = []
            if not (task_hub_name is None):
                query.append(f"taskHub={task_hub_name}")
            if not (connection_name is None):
                query.append(f"connection={connection_name}")
            if len(query) > 0:
                path += "&" + "&".join(query)

            request_url = f"{self._orchestration_bindings.rpc_base_url}" + path
        else:
            raise Exception("The Python SDK only supports RPC endpoints."
                            + "Please remove the `localRpcEnabled` setting from host.json")

        response = await self._post_async_request(request_url, None)
        status: int = response[0]
        ex_msg: str = ""
        if status == 200 or status == 202:
            return
        elif status == 404:
            ex_msg = f"No instance with ID {instance_id} found."
            raise Exception(ex_msg)
        elif status == 410:
            ex_msg = "The rewind operation is only supported on failed orchestration instances."
            raise Exception(ex_msg)
        elif isinstance(response[1], str):
            ex_msg = response[1]
            raise Exception(ex_msg)
        else:
            ex_msg = "Received unexpected payload from the durable-extension: " + str(response)
            raise Exception(ex_msg)
