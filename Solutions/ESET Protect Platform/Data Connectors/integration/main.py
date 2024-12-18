import asyncio
import logging
import time
import typing as t
from datetime import datetime, timezone

from aiohttp import ClientSession

from integration.models import Config, EnvVariables, TokenStorage
from integration.utils import (
    LastDetectionTimeHandler,
    RequestSender,
    TokenProvider,
    TransformerDetections,
)


class ServiceClient:
    def __init__(self) -> None:
        self.config = Config()
        self.env_vars = EnvVariables()
        self.request_sender = RequestSender(self.config, self.env_vars)
        self.token_provider = TokenProvider(TokenStorage(), self.request_sender, self.env_vars, self.config.buffer)
        self.transformer_detections = TransformerDetections(self.env_vars)
        self._session: ClientSession | None = None
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def run(self) -> None:
        self._session = ClientSession(raise_for_status=True)
        start_time = time.time()
        try:
            await asyncio.gather(
                self._process_integration("EI", start_time), self._process_integration("ECOS", start_time)
            )
        except Exception as e:
            logging.error("Unexpected error happened", exc_info=e)
            raise e
        finally:
            await self.close()

    async def _process_integration(self, data_source: str, start_time: float) -> None:
        last_detection_time_handler = LastDetectionTimeHandler(
            self.env_vars.conn_str, self.env_vars.last_detection_time, data_source=data_source
        )
        next_page_token: str | None = None
        cur_ld_time: str | None = None
        max_duration = self.env_vars.interval * 60

        if data_source == "EI" and not last_detection_time_handler.storage_table_handler.entities:
            data_source, last_detection_time_handler = await self._check_if_ei_is_right_data_source(
                last_detection_time_handler, next_page_token
            )
        endp = self.config.data_sources.get(data_source).get("endpoint")  # type: ignore

        while next_page_token != "" and (time.time() - start_time) < (max_duration - 30):
            response_data = await self._call_service(last_detection_time_handler, next_page_token, data_endpoint=endp)
            next_page_token = response_data.get("nextPageToken") if response_data else ""

            if (
                response_data
                and (response_data.get("detections") or response_data.get("detectionGroups"))
                and (time.time() - start_time) < (max_duration - 15)
            ):
                cur_ld_time, successful_data_upload = await self.transformer_detections.send_integration_detections(
                    response_data, cur_ld_time
                )
                next_page_token = "" if successful_data_upload is False else next_page_token
                self._update_last_detection_time(last_detection_time_handler, cur_ld_time)

    async def _check_if_ei_is_right_data_source(
        self,
        last_detection_time_handler: LastDetectionTimeHandler,
        next_page_token: str | None,
        data_source: str = "EI",
    ) -> tuple[str, LastDetectionTimeHandler]:
        endp = self.config.data_sources.get(data_source).get("endpoint")  # type: ignore
        response_data = await self._call_service(
            last_detection_time_handler, next_page_token, page_size=1, data_endpoint=endp
        )
        if not response_data or not response_data.get("detectionGroups"):
            data_source, last_detection_time_handler = (
                "EP",
                LastDetectionTimeHandler(self.env_vars.conn_str, self.env_vars.last_detection_time, data_source="EP"),
            )

        return data_source, last_detection_time_handler

    def _update_last_detection_time(
        self, last_detection_time_handler: LastDetectionTimeHandler, cur_ld_time: str | None
    ) -> None:
        if cur_ld_time and cur_ld_time != last_detection_time_handler.last_detection_time:
            last_detection_time_handler.storage_table_handler.input_entity(
                new_entity=last_detection_time_handler.get_entity_schema(cur_ld_time)  # type: ignore[call-arg]
            )

    async def _call_service(
        self,
        last_detection_time_handler: LastDetectionTimeHandler,
        next_page_token: str | None,
        page_size: int = 100,
        data_endpoint: str = "",
    ) -> dict[str, t.Any] | None:
        logging.info(f"Service call initiated")

        if not self.token_provider.token.access_token or datetime.now(timezone.utc) > self.token_provider.token.expiration_time:  # type: ignore
            assert self._session
            async with self._lock:
                await self.token_provider.get_token(self._session)

        try:
            if (
                self.token_provider.token.expiration_time
                and datetime.now(timezone.utc) < self.token_provider.token.expiration_time
            ):
                data = await self.request_sender.send_request(
                    self.request_sender.send_request_get,
                    self._session,  # type: ignore
                    {
                        "Authorization": f"Bearer {self.token_provider.token.access_token}",
                        "Content-Type": "application/json",
                        "3rd-integration": "MS-Sentinel",
                    },
                    last_detection_time_handler.last_detection_time,
                    next_page_token,
                    page_size,
                    data_endpoint,
                )
                is_obtained = True if data and (data.get("detections") or data.get("detectionGroups")) else False
                logging.info(f"Service call response data is {'obtained' if is_obtained else f'empty: {data}'}")
                return data

            logging.info("Service not called due to missing token.")
        except Exception as e:
            logging.error(f"Error in running service call: {e}")

        return None


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
    )
    service_client = ServiceClient()
    asyncio.run(service_client.run())


if __name__ == "__main__":
    main()
