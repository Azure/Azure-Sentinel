import logging
import os
import typing as t
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from importlib import resources

import yaml


@dataclass
class TokenStorage:
    __access_token: str | None = field(default=None, init=False)
    __refresh_token: str | None = field(default=None, init=False)
    __expiration_time: datetime | None = field(default=None, init=False)

    @property
    def access_token(self) -> str | None:
        return self.__access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        self.__access_token = value

    @property
    def refresh_token(self) -> str | None:
        return self.__refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str) -> None:
        self.__refresh_token = value

    @property
    def expiration_time(self) -> datetime | None:
        return self.__expiration_time

    @expiration_time.setter
    def expiration_time(self, value: datetime) -> None:
        self.__expiration_time = value

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expiration_time": self.expiration_time,
        }


class Config:
    def __init__(self) -> None:
        config = self.get_config_params()
        if config:
            self.max_retries: int = config.get("max_retries")  # type: ignore
            self.retry_delay: float = float(config.get("retry_delay"))  # type: ignore
            self.requests_timeout = config.get("requests_timeout")
            self.buffer: int = config.get("buffer")  # type: ignore
            self.data_sources: dict[str, t.Any] = config.get("data_sources")  # type: ignore

    def get_config_params(self) -> dict[str, t.Any] | t.Any:
        try:
            return yaml.safe_load(
                resources.files(__package__ or "integration").parent.joinpath("config.yml").read_bytes()  # type: ignore
            )
        except FileNotFoundError as e:
            logging.error(e)
            raise FileNotFoundError("The config file is not found. Further processing is impossible.")


class EnvVariables:
    def __init__(self) -> None:
        self.__username: str | None = os.getenv("USERNAME_INTEGRATION")
        self.__password: str | None = os.getenv("PASSWORD_INTEGRATION")
        self.interval: int = int(os.getenv("INTERVAL", 5))
        self.last_detection_time: str = os.getenv(
            "LAST_DETECTION",
            (datetime.now(timezone.utc) - timedelta(seconds=self.interval * 60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.endpoint_uri: str = os.getenv("ENDPOINT_URI", "")
        self.dcr_immutableid: str = os.getenv("DCR_IMMUTABLEID", "")
        self.stream_name: str = os.getenv("STREAM_NAME", "")
        self.__conn_str: str = os.getenv("WEBSITE_CONTENTAZUREFILECONNECTIONSTRING", "")
        self.__key_base64: str = os.getenv("KEY_BASE64", "")

        region = os.getenv("INSTANCE_REGION", "eu")
        self.oauth_url: str = f"https://{region}.business-account.iam.eset.systems"
        self.detections_url: str = (
            f"https://{region}.incident-management.eset.systems"
        )

    @property
    def username(self) -> str | None:
        return self.__username

    @property
    def password(self) -> str | None:
        return self.__password

    @property
    def conn_str(self) -> str:
        return self.__conn_str

    @property
    def key_base64(self) -> str:
        return self.__key_base64
