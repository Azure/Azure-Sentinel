from azure.storage.fileshare.aio import ShareClient
from azure.storage.fileshare.aio import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from typing import Optional
import datetime
from dateutil.parser import parse as parse_date
import logging


class StateManagerAsync:
    def __init__(self, connection_string, share_name='funcstatemarkershare', file_path='funcstatemarkerfile'):
        self.connection_string = connection_string
        self.share_name = share_name
        self.file_path = file_path
        self._last_date: Optional[datetime.datetime] = None

    def _get_file_cli(self):
        return ShareFileClient.from_connection_string(conn_str=self.connection_string, share_name=self.share_name, file_path=self.file_path)

    def _get_share_cli(self):
        return ShareClient.from_connection_string(conn_str=self.connection_string, share_name=self.share_name)

    async def post(self, marker_text: str) -> None:
        file_cli = self._get_file_cli()
        async with file_cli:
            try:
                await file_cli.upload_file(marker_text)
            except ResourceNotFoundError:
                share_cli = self._get_share_cli()
                async with share_cli:
                    try:
                        await share_cli.create_share()
                    except ResourceExistsError:
                        pass
                    await file_cli.upload_file(marker_text)

    async def get(self) -> Optional[str]:
        file_cli = self._get_file_cli()
        async with file_cli:
            try:
                cor = await file_cli.download_file()
                f = await cor.readall()
                return f.decode()
            except ResourceNotFoundError:
                return None

    async def get_last_date_from_storage(self) -> Optional[datetime.datetime]:
        s = await self.get()
        try:
            date = parse_date(s)
        except Exception:
            date = None
        return date

    def remember_last_date(self, date: Optional[datetime.datetime]) -> None:
        if isinstance(date, datetime.datetime):
            if not self._last_date or date > self._last_date:
                self._last_date = date

    async def save_last_date_to_storage(self) -> None:
        if isinstance(self._last_date, datetime.datetime):
            date_str = self._last_date.isoformat()
            await self.post(date_str)
            logging.info(f'Saved last scan date - {date_str}')
