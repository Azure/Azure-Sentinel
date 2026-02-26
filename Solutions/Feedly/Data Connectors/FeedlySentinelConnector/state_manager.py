import json
from typing import Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareClient, ShareFileClient


class FeedlyCheckpoint:
    def __init__(self, connection_string: str):
        self.state_manager = StateManager(
            connection_string=connection_string,
            share_name="feedlycheckpoint",
            file_path="feedly_stream_id2last_success.json",
        )
        self.state: dict[str, float] = json.loads(self.state_manager.get() or "{}")

    def __getitem__(self, stream_id: str) -> Optional[float]:
        return self.state.get(stream_id, None)

    def __setitem__(self, stream_id: str, ts: float) -> None:
        self.state[stream_id] = ts

    def save(self) -> None:
        self.state_manager.post(json.dumps(self.state))


class StateManager:
    def __init__(self, *, connection_string: str, share_name: str, file_path: str):
        self.share_cli = ShareClient.from_connection_string(conn_str=connection_string, share_name=share_name)
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )

    def post(self, marker_text: str) -> None:
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self) -> Optional[str]:
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None
