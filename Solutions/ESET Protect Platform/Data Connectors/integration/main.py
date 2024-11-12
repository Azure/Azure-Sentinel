import asyncio
import logging
import time
import typing as t
from datetime import datetime, timezone

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
        self.last_detection_time_handler = LastDetectionTimeHandler(
            self.env_vars.conn_str,
            self.env_vars.last_detection_time,
        )
        self.request_sender = RequestSender(self.config, self.env_vars)
        self.token_provider = TokenProvider(TokenStorage(), self.request_sender, self.env_vars, self.config.buffer)
        self.transformer_detections = TransformerDetections(self.env_vars)
        self._is_running = False
        self._next_page_token: str | None = None
        self._cur_ld_time: str | None = None

    async def run(self) -> None:
        if self._is_running:
            while self._is_running:
                await asyncio.gather(self._custom_sleep(), self._process_integration())
        else:
            await asyncio.gather(self._process_integration())

    async def _process_integration(self) -> None:
        start_time = time.time()
        max_duration = self.env_vars.interval * 60

        while self._next_page_token != "" and (time.time() - start_time) < (max_duration - 30):
            response_data = await self._call_service()
            self._next_page_token = response_data.get("nextPageToken") if response_data else ""

            if response_data and response_data.get("detections") and (time.time() - start_time) < (max_duration - 15):
                self._cur_ld_time, successful_data_upload = (
                    await self.transformer_detections.send_integration_detections(response_data, self._cur_ld_time)
                )
                self._next_page_token = "" if successful_data_upload is False else self._next_page_token
                self._update_last_detection_time()

    def _update_last_detection_time(self) -> None:
        if self._cur_ld_time and self._cur_ld_time != self.last_detection_time_handler.last_detection_time:
            self.last_detection_time_handler.storage_table_handler.input_entity(
                new_entity=self.last_detection_time_handler.get_entity_schema(self._cur_ld_time)  # type: ignore[call-arg]
            )

    async def _custom_sleep(self) -> None:
        logging.info(f"Start of the {self.env_vars.interval} seconds interval")
        await asyncio.sleep(self.env_vars.interval)
        logging.info(f"End of the {self.env_vars.interval} seconds interval")

    async def _call_service(self) -> dict[str, t.Any] | None:
        logging.info(f"Service call initiated")

        if not self.token_provider.token.access_token or datetime.now(timezone.utc) > self.token_provider.token.expiration_time:  # type: ignore
            await self.token_provider.get_token()

        try:
            if (
                self.token_provider.token.expiration_time
                and datetime.now(timezone.utc) < self.token_provider.token.expiration_time
            ):
                data = await self.request_sender.send_request(
                    self.request_sender.send_request_get,
                    {
                        "Authorization": f"Bearer {self.token_provider.token.access_token}",
                        "Content-Type": "application/json",
                    },
                    self.last_detection_time_handler.last_detection_time,
                    self._next_page_token,
                )
                logging.info(
                    f"Service call response data is {'obtained' if data and data.get('detections') else f'empty: {data}'}"
                )
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
