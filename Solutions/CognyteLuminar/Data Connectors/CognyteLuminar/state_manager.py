"""
state_manager.py

Per-collection resume checkpoints persisted in an Azure File Share (the same
share and file the previous connector version used, so an in-place upgrade
keeps its position).

File content (v2):

    {"version": 2, "checkpoints": {"iocs": "<luminar ts>", "cyberfeeds": "..."}}

Legacy content (v1) was a bare Luminar timestamp string that applied to every
collection; it is migrated transparently on first read.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareClient, ShareFileClient

logger = logging.getLogger(__name__)

STATE_VERSION = 2


class StateManager:
    def __init__(
        self,
        connection_string: str,
        share_name: str = "funcstatemarkershare",
        file_path: str = "funcstatemarkerfile",
    ):
        self.share_cli = ShareClient.from_connection_string(
            conn_str=connection_string, share_name=share_name
        )
        self.file_cli = ShareFileClient.from_connection_string(
            conn_str=connection_string, share_name=share_name, file_path=file_path
        )

    # ----- raw file access -----

    def _read_raw(self) -> Optional[str]:
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None

    def _write_raw(self, text: str) -> None:
        try:
            self.file_cli.upload_file(text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(text)

    # ----- checkpoint API -----

    def load(self) -> Dict[str, str]:
        """Return {collection_alias: luminar_timestamp}. Empty if no state."""
        raw = self._read_raw()
        if raw is None or not raw.strip():
            return {}
        text = raw.strip()
        try:
            data = json.loads(text)
        except ValueError:
            data = None
        if isinstance(data, dict) and isinstance(data.get("checkpoints"), dict):
            return {
                k: v
                for k, v in data["checkpoints"].items()
                if isinstance(k, str) and isinstance(v, str) and v
            }
        # v1: a bare timestamp that applied to every collection.
        logger.info(
            "Migrating legacy single checkpoint %r to per-collection state", text
        )
        return {"iocs": text, "cyberfeeds": text}

    def save(self, checkpoints: Dict[str, str]) -> None:
        payload = {"version": STATE_VERSION, "checkpoints": dict(checkpoints)}
        self._write_raw(json.dumps(payload, sort_keys=True))

    # Backwards-compatible helpers used by older callers.
    def get(self) -> Optional[str]:
        return self._read_raw()

    def post(self, marker_text: str) -> None:
        self._write_raw(marker_text)
