import os

from integration.models import EnvVariables


class EnvVariablesSentinel(EnvVariables):
    def __init__(self) -> None:
        super().__init__()
        self.endpoint_uri: str = os.getenv("ENDPOINT_URI", "")
        self.dcr_immutableid: str = os.getenv("DCR_IMMUTABLEID", "")
        self.stream_name: str = os.getenv("STREAM_NAME", "")
        self.stream_name_incidents: str = os.getenv("STREAM_NAME_INCIDENTS", "")
        self.__conn_str: str = os.getenv("WEBSITE_CONTENTAZUREFILECONNECTIONSTRING", "")
        self.__key_base64: str = os.getenv("KEY_BASE64", "")

    @property
    def conn_str(self) -> str:
        return self.__conn_str

    @property
    def key_base64(self) -> str:
        return self.__key_base64
