import logging
import typing as t
from datetime import datetime, timedelta, timezone

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.data.tables import TableServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient
from cryptography.fernet import Fernet, InvalidToken
from integration.models import TokenStorage
from integration.utils import LastDataTimeHandler, RequestSender, TokenProvider, TransformerData

from models_sentinel import EnvVariablesSentinel


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
            logging.error(f"Exception occurred: {e}")


class TokenProviderSentinel(TokenProvider):
    def __init__(
        self,
        token: TokenStorage,
        requests_sender: RequestSender,
        env_vars_sentinel: EnvVariablesSentinel,
        buffer: int,
    ) -> None:
        super().__init__(token, requests_sender, env_vars_sentinel, buffer)
        assert isinstance(self.env_vars, EnvVariablesSentinel)
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

    def set_token_params_locally(self, response: t.Dict[str, t.Union[str, int]]) -> None:
        super().set_token_params_locally(response)
        self.set_token_params_remote()

    def set_token_params_remote(self) -> None:
        self.storage_table_handler.input_entity(
            {
                k: self.fernet.encrypt(v.encode("utf-8")) if type(v) is str else v
                for k, v in self.token.to_dict().items()
            }
        )  # type: ignore[call-arg]

    def manage_token_refresh_issue(self) -> None:
        self.storage_table_handler.input_entity({k: "" for k in self.token.to_dict()})  # type: ignore[call-arg]


class TransformerDataSentinel(TransformerData):
    def __init__(self, env_vars: EnvVariablesSentinel) -> None:
        super().__init__(env_vars)

    async def _send_data_to_destination(
        self, validated_data: t.List[dict[str, t.Any]], last_data: str | None, endp: str = ""
    ) -> tuple[str | None, bool]:
        assert isinstance(self.env_vars, EnvVariablesSentinel)
        credential = DefaultAzureCredential()  # Env vars: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
        client = LogsIngestionClient(endpoint=self.env_vars.endpoint_uri, credential=credential, logging_enable=True)

        steam_name = self.env_vars.stream_name_incidents if "incidents" in endp else self.env_vars.stream_name
        successful_data_upload: bool = False

        async with client:
            try:
                await client.upload(
                    rule_id=self.env_vars.dcr_immutableid,
                    stream_name=steam_name,
                    logs=validated_data,
                )
                time_key = "createTime" if "incidents" in endp else "occurTime"
                last_data = max(validated_data, key=lambda data: data.get(time_key) or "").get(time_key)
                successful_data_upload = True
            except ServiceRequestError as e:
                logging.error(f"Authentication to Azure service failed: {e}")
            except HttpResponseError as e:
                logging.error(f"Upload failed: {e}")

        await credential.close()
        return last_data, successful_data_upload


class LastDataTimeHandlerSentinel(LastDataTimeHandler):
    def __init__(self, data_source: str, interval: int, storage_table_conn_str: str) -> None:
        self.storage_table_name = f"LastDetectionTime{data_source}"
        self.storage_table_handler = StorageTableHandler(storage_table_conn_str, self.storage_table_name)
        self.storage_table_handler.set_entity()
        super().__init__(data_source, interval)

    def get_last_data_time(self, data_source: t.Optional[str] = None, interval: int = 5) -> t.Any:
        if self.storage_table_handler.entities:
            return self.storage_table_handler.entities.get(self.storage_table_name)
        return (datetime.now(timezone.utc) - timedelta(seconds=10 * interval * 60)).strftime("%Y-%m-%dT%H:%M:%SZ")

    async def update_last_data_time(self, cur_ld_time: str | None, data_source: str = "") -> None:
        if cur_ld_time and cur_ld_time != self.last_data_time:
            self.storage_table_handler.input_entity(
                new_entity=self.get_entity_schema(cur_ld_time)  # type: ignore[call-arg]
            )

    def get_entity_schema(self, cur_last_data_time: str) -> dict[str, t.Any]:
        return {
            self.storage_table_name: self.prepare_date_plus_timedelta(cur_last_data_time),
        }
