from azure.storage.fileshare.aio import ShareClient
from azure.storage.fileshare.aio import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError
import asyncio


class StateManagerAsync:
    def __init__(self, connection_string, share_name='funcstatemarkershare', file_path='funcstatemarkerfile'):
        self.connection_string = connection_string
        self.share_name = share_name
        self.file_path = file_path
        self._lock = asyncio.Lock()

    def _get_file_cli(self):
        return ShareFileClient.from_connection_string(conn_str=self.connection_string, share_name=self.share_name, file_path=self.file_path)

    def _get_share_cli(self):
        return ShareClient.from_connection_string(conn_str=self.connection_string, share_name=self.share_name)

    async def post(self, marker_text: str, validate_upload=True, tries=2):
        async with self._lock:
            if not validate_upload:
                await self._upload_file(marker_text)
            else:
                count = 0
                validated = False
                while count < tries:
                    await self._upload_file(marker_text)
                    validated = await self._validate(marker_text)
                    count += 1
                    if validated:
                        break
                if not validated:
                    raise Exception(f'File {self.share_name}/{self.file_path} was not saved correctly. Please update file manually.')

    async def _upload_file(self, text):
        file_cli = self._get_file_cli()
        async with file_cli:
            try:
                await file_cli.upload_file(text, validate_content=True)
            except ResourceNotFoundError:
                share_cli = self._get_share_cli()
                async with share_cli:
                    await share_cli.create_share()
                    await file_cli.upload_file(text, validate_content=True)

    async def get(self):
        file_cli = self._get_file_cli()
        async with file_cli:
            try:
                cor = await file_cli.download_file()
                f = await cor.readall()
                return f.decode()
            except ResourceNotFoundError:
                return None

    async def _validate(self, text):
        content = await self.get()
        return content == text
