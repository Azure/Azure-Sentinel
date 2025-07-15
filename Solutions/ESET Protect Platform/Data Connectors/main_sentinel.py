import asyncio
import logging
import time

from integration.main import ServiceClient
from integration.models import Config, TokenStorage

from models_sentinel import EnvVariablesSentinel
from utils_sentinel import LastDataTimeHandlerSentinel, TokenProviderSentinel, TransformerDataSentinel


class ServiceClientSentinel(ServiceClient):
    def __init__(self) -> None:
        super().__init__()

    def _get_config(self) -> Config:
        return Config("MS-Sentinel", "3.2.0")

    def _get_env_vars(self) -> EnvVariablesSentinel:
        return EnvVariablesSentinel()

    def _get_token_provider(self) -> TokenProviderSentinel:
        return TokenProviderSentinel(TokenStorage(), self.request_sender, self.env_vars, self.config.buffer)

    def _get_transformer_data(self) -> TransformerDataSentinel:
        return TransformerDataSentinel(self.env_vars)

    def _get_last_data_time_handler(self, data_source: str) -> LastDataTimeHandlerSentinel:
        return LastDataTimeHandlerSentinel(data_source, self.env_vars.interval, self.env_vars.conn_str)  # type: ignore

    def _validate_if_run_instance_old_version(self, data_source: str) -> bool:
        if data_source not in ["EP", "INCIDENTS"] and all(
            v == "" for v in [self.env_vars.ep_instance, self.env_vars.ei_instance, self.env_vars.ecos_instance]
        ):
            self.config.version = "3.0.0"
            return True
        return False

    def _validate_if_run_incidents(self) -> bool:
        return True if self.env_vars.stream_name_incidents != "" else False  # type: ignore

    async def _old_version_check(
        self, data_source: str, last_data_time_handler: LastDataTimeHandlerSentinel
    ) -> tuple[str, LastDataTimeHandlerSentinel]:
        if (
            self.config.version == "3.0.0"
            and data_source == "EI"
            and not last_data_time_handler.storage_table_handler.entities
        ):
            endp = self.config.data_sources.get(data_source).get("endpoint")  # type: ignore
            response_data = await self._call_service(
                last_data_time_handler, next_page_token=None, page_size=1, data_endpoint=endp
            )
            if not response_data or not response_data.get("detectionGroups"):
                data_source, last_data_time_handler = (
                    "EP",
                    LastDataTimeHandlerSentinel("EP", self.env_vars.interval, self.env_vars.conn_str),  # type: ignore
                )
        return data_source, last_data_time_handler


def main() -> None:
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
    )
    service_client = ServiceClientSentinel()
    asyncio.run(service_client.run())


if __name__ == "__main__":
    main()
