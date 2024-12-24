import asyncio
import logging
import typing as t
import urllib.parse
from datetime import datetime, timedelta, timezone

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError
from cryptography.fernet import Fernet, InvalidToken
from pydantic import ValidationError

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.data.tables import TableServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient
from integration.exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
    MissingCredentialsException,
    TokenRefreshException,
)
from integration.models import Config, EnvVariables, TokenStorage
from integration.models_detections import Detection, Detections


class RequestSender:
    def __init__(self, config: Config, env_vars: EnvVariables):
        self.config = config
        self.env_vars = env_vars

    async def send_request(
        self,
        send_request_fun: (
            t.Callable[
                [ClientSession, dict[str, t.Any] | None, str, str | None, int, str],
                t.Coroutine[t.Any, t.Any, dict[str, str | int] | t.Any],
            ]
            | t.Callable[
                [ClientSession, dict[str, t.Any] | None, str | None],
                t.Coroutine[t.Any, t.Any, dict[str, str | int] | t.Any],
            ]
        ),
        session: ClientSession,
        headers: dict[str, t.Any] | None = None,
        *data: t.Any,
    ) -> t.Dict[str, str | int] | None:
        retries = 0

        while retries < self.config.max_retries:
            try:
                return await send_request_fun(session, headers, *data)

            except ClientResponseError as e:
                if e.status in [400, 401, 403]:
                    raise AuthenticationException(status=e.status, message=e.message)
                if e.status == 404:
                    logging.info(f"Endpoint not found.")
                    return None

                retries += 1
                logging.error(
                    f"Exception: {e.status} {e.message}. Request failed. "
                    f"Request retry attempt: {retries}/{self.config.max_retries}"
                )
                await asyncio.sleep(self.config.retry_delay)
        return None

    async def send_request_post(
        self, session: ClientSession, headers: dict[str, t.Any] | None, grant_type: str | None
    ) -> t.Dict[str, str | int] | t.Any:
        logging.info("Sending token request")

        async with session.post(
            url=f"{self.env_vars.oauth_url}/oauth/token",
            headers=headers,
            data=urllib.parse.quote(f"grant_type={grant_type}", safe="=&/"),
            timeout=self.config.requests_timeout,
        ) as response:
            return await response.json()

    async def send_request_get(
        self,
        session: ClientSession,
        headers: dict[str, t.Any] | None,
        last_detection_time: str,
        next_page_token: str | None,
        page_size: int,
        data_endpoint: str,
    ) -> t.Dict[str, str | int] | t.Any:
        logging.info("Sending service request")

        async with session.get(
            self.env_vars.detections_url + data_endpoint,
            headers=headers,
            params=self._prepare_get_request_params(last_detection_time, next_page_token, page_size),
        ) as response:
            return await response.json()

    def _prepare_get_request_params(
        self, last_detection_time: str, next_page_token: str | None, page_size: int = 100
    ) -> dict[str, t.Any]:
        params = {"pageSize": page_size}
        if next_page_token not in ["", None]:
            params["pageToken"] = next_page_token  # type: ignore[assignment]
        if last_detection_time:
            params["startTime"] = last_detection_time  # type: ignore[assignment]

        return params


class TokenProvider:
    def __init__(self, token: TokenStorage, requests_sender: RequestSender, env_vars: EnvVariables, buffer: int):
        self.token = token
        self.requests_sender = requests_sender
        self.env_vars = env_vars
        self.buffer = buffer
        self.fernet = Fernet(self.env_vars.key_base64.encode("utf-8"))
        self.storage_table_name = "TokenParams"
        self.storage_table_handler = StorageTableHandler(self.env_vars.conn_str, self.storage_table_name)
        self.storage_table_handler.set_entity()

        self.get_token_params_from_storage()

    def get_token_params_from_storage(self) -> None:
        if not self.storage_table_handler.entities:
            return None
        for token_param in self.token.to_dict().keys():
            value = self.storage_table_handler.entities.get(token_param)
            if isinstance(value, bytes):
                try:
                    value = self.fernet.decrypt(value).decode("utf-8")
                except InvalidToken:
                    logging.warning("Issue with decrypt: Invalid Token")
                    value = ""
            setattr(self.token, token_param, value)

    async def get_token(self, session: ClientSession) -> None:

        if not self.token.access_token or datetime.now(timezone.utc) > self.token.expiration_time:  # type: ignore
            logging.info("Getting token")

            if not self.token.access_token and (not self.env_vars.username or not self.env_vars.password):
                raise MissingCredentialsException()

            grant_type = (
                f"refresh_token&refresh_token={self.token.refresh_token}"
                if self.token.access_token
                else f"password&username={self.env_vars.username}&password={self.env_vars.password}"
            )

            try:
                response = await self.requests_sender.send_request(
                    self.requests_sender.send_request_post,
                    session,
                    {"Content-type": "application/x-www-form-urlencoded", "3rd-integration": "MS-Sentinel"},
                    grant_type,
                )
            except AuthenticationException as e:
                if not self.token.access_token:
                    raise InvalidCredentialsException(e)
                else:
                    self.storage_table_handler.input_entity({k: "" for k in self.token.to_dict()})  # type: ignore[call-arg]
                    raise TokenRefreshException(e)

            if response:
                self.set_token_params_locally_and_in_storage(response)
                logging.info("Token obtained successfully")

    def set_token_params_locally_and_in_storage(self, response: t.Dict[str, str | int]) -> None:
        self.token.access_token = t.cast(str, response["access_token"])
        self.token.refresh_token = t.cast(str, response["refresh_token"])
        self.token.expiration_time = datetime.now(timezone.utc) + timedelta(
            seconds=int(response["expires_in"]) - self.buffer
        )
        self.storage_table_handler.input_entity(
            {
                k: self.fernet.encrypt(v.encode("utf-8")) if type(v) is str else v
                for k, v in self.token.to_dict().items()
            }
        )  # type: ignore[call-arg]


class TransformerDetections:
    def __init__(self, env_vars: EnvVariables) -> None:
        self.env_vars = env_vars

    async def send_integration_detections(
        self, detections: dict[str, t.Any] | None, last_detection: str | None
    ) -> tuple[str | None, bool]:
        validated_detections = self._validate_detections_data(detections)
        if not validated_detections:
            return last_detection, False
        return await self._send_data_to_log_analytics_workspace(validated_detections, last_detection)

    def _validate_detections_data(self, response_data: dict[str, t.Any] | None) -> list[dict[str, t.Any]] | None:
        if not response_data:
            logging.info("No new detections")
            return None

        response_data["detections"] = (
            response_data.pop("detectionGroups") if "detectionGroups" in response_data else response_data["detections"]
        )
        try:
            validated_data = Detections.model_validate(response_data)
            self._update_time_generated(validated_data.detections)
            return validated_data.model_dump().get("detections")

        except ValidationError as e:
            logging.error(e)
            validated_detections = []

            for detection in response_data.get("detections"):  # type: ignore
                try:
                    validated_detections.append(Detection.model_validate(detection))
                except ValidationError as e:
                    logging.error(e)

            self._update_time_generated(validated_detections)
            return [d.model_dump() for d in validated_detections]

    async def _send_data_to_log_analytics_workspace(
        self, validated_data: t.List[dict[str, t.Any]], last_detection: str | None, successful_data_upload: bool = False
    ) -> tuple[str | None, bool]:
        credential = DefaultAzureCredential()  # Env vars: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
        client = LogsIngestionClient(endpoint=self.env_vars.endpoint_uri, credential=credential, logging_enable=True)

        async with client:
            try:
                await client.upload(
                    rule_id=self.env_vars.dcr_immutableid,
                    stream_name=self.env_vars.stream_name,
                    logs=validated_data,  # type: ignore[arg-type]
                )
                last_detection = max(validated_data, key=lambda detection: detection.get("occurTime")).get("occurTime")  # type: ignore
                successful_data_upload = True
            except ServiceRequestError as e:
                logging.error(f"Authentication to Azure service failed: {e}")
            except HttpResponseError as e:
                logging.error(f"Upload failed: {e}")

        await credential.close()
        return last_detection, successful_data_upload

    def _update_time_generated(self, validated_data: t.List[Detection]) -> None:
        utc_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        for data in validated_data:
            data.TimeGenerated = utc_now


class StorageTableHandler:
    def __init__(self, env_conn_str: str, table_name_keys: str) -> None:
        self.conn_str = env_conn_str
        self.table_name_keys = table_name_keys
        self.entities = None
        self.table_client = None

    def with_table_client(func: t.Callable[[t.Any, t.Any], t.Any]) -> t.Callable[[t.Any], t.Any]:  # type: ignore
        def wrapper(storage_table_handler_instance, *args, **kwargs):  # type: ignore[no-untyped-def]
            try:
                with TableServiceClient.from_connection_string(
                    conn_str=storage_table_handler_instance.conn_str
                ) as table_service_client:
                    storage_table_handler_instance.table_client = table_service_client.create_table_if_not_exists(
                        table_name=storage_table_handler_instance.table_name_keys
                    )
                    return func(storage_table_handler_instance, *args, **kwargs)
            except ValueError as e:
                raise ValueError(f"Connection string WEBSITE_CONTENTAZUREFILECONNECTIONSTRING value error: {e}")

        return wrapper

    @with_table_client  # type: ignore
    def set_entity(self) -> None:
        if self.table_client:
            self.entities = next(self.table_client.query_entities(""), None)
        return None

    @with_table_client
    def input_entity(self, new_entity: dict[str, t.Any]) -> None:
        entity = {
            "PartitionKey": self.table_name_keys,
            "RowKey": self.table_name_keys,
            "TimeGenerated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        } | new_entity
        try:
            if self.table_client:
                (
                    self.table_client.update_entity(entity=entity)
                    if self.entities
                    else self.table_client.create_entity(entity=entity)
                )
                self.entities = next(self.table_client.query_entities(""), None)
                logging.info(f"Entity: {self.table_name_keys} updated")
        except Exception as e:
            print("Exception occurred:", e)


class LastDetectionTimeHandler:
    def __init__(self, storage_table_conn_str: str, env_last_occur_time: str, data_source: str) -> None:
        self.storage_table_name = f"LastDetectionTime{data_source}"
        self.storage_table_handler = StorageTableHandler(storage_table_conn_str, self.storage_table_name)
        self.storage_table_handler.set_entity()
        self.last_detection_time = self.get_last_occur_time(env_last_occur_time)

    def get_last_occur_time(self, env_last_occur_time: str) -> t.Any:
        if self.storage_table_handler.entities:
            return self.storage_table_handler.entities.get(self.storage_table_name)
        return env_last_occur_time

    def get_entity_schema(self, cur_last_detection_time: str) -> dict[str, t.Any]:
        return {
            self.storage_table_name: (
                datetime.strptime(
                    self.transform_date_with_miliseconds_to_second(cur_last_detection_time), "%Y-%m-%dT%H:%M:%SZ"
                )
                + timedelta(seconds=1)
            ).isoformat()
            + "Z"
        }

    def transform_date_with_miliseconds_to_second(self, cur_last_detection_time: str) -> str:
        return cur_last_detection_time if len(cur_last_detection_time) == 20 else cur_last_detection_time[:-5] + "Z"
