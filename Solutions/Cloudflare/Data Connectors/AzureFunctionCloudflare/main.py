import os
import asyncio
from azure.storage.blob.aio import ContainerClient
import json
import logging
from dateutil.parser import parse as parse_date
import datetime
import azure.functions as func
import re

from .sentinel_connector_async import AzureSentinelMultiConnectorAsync
from .state_manager import StateManagerAsync


# interval of script execution
SCRIPT_EXECUTION_INTERVAL_MINUTES = 2
# if ts of last processed file is older than now - MAX_PERIOD_MINUTES -> script will get events from now - SCRIPT_EXECUTION_INTERVAL_MINUTES
MAX_PERIOD_MINUTES = 1440

MAX_SCRIPT_EXEC_TIME_MINUTES = 35


AZURE_STORAGE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
CONTAINER_NAME = os.environ['CONTAINER_NAME']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
LOG_TYPE = 'Cloudflare'


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


async def main(mytimer: func.TimerRequest):
    checkpoint_manager = CheckpointManager(conn_string=os.environ['AzureWebJobsStorage'])
    script_is_active = await checkpoint_manager.script_is_active()
    last_date = await checkpoint_manager.get_last_date()
    exclude_files = await checkpoint_manager.get_exclude_files()
    include_files = await checkpoint_manager.get_include_files()
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    if last_date and (now - last_date).seconds > MAX_SCRIPT_EXEC_TIME_MINUTES * 60:
        script_is_active = False

    if script_is_active:
        print('Script is running now. Exit.')
        logging.info('Script is running now. Exit.')
        return

    if not last_date or (now - last_date).seconds > MAX_PERIOD_MINUTES * 60:
        last_date = now - datetime.timedelta(minutes=SCRIPT_EXECUTION_INTERVAL_MINUTES)
    print('Getting files updated after {}'.format(last_date))
    logging.info('Getting files updated after {}'.format(last_date))

    await checkpoint_manager.mark_script_as_active()

    conn = AzureBlobStorageConnector(AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME)
    await conn.get_blobs(updated_after=last_date, exclude_files=exclude_files, include_files=include_files)
    await conn.process_blobs()

    message = 'Program finished. {} events have been sent. {} events have not been sent'.format(
        conn.sentinel.successfull_sent_events_number,
        conn.sentinel.failed_sent_events_number
    )
    print(message)
    logging.info(message)

    if conn.sentinel.failed_sent_events_number:
        raise Exception('Program finished with errors. {} events have not been sent'.format(conn.sentinel.failed_sent_events_number))
    if conn.has_errors():
        raise Exception('Program finished with errors')

    await conn.delete_old_blobs()

    await checkpoint_manager.mark_script_as_inactive()


class AzureBlobStorageConnector:
    def __init__(self, conn_string, container_name, queue_max_size=10):
        self.__conn_string = conn_string
        self.__container_name = container_name
        self.semaphore = asyncio.Semaphore(queue_max_size)
        self.blobs = []
        self.log_type = LOG_TYPE
        self.sentinel = AzureSentinelMultiConnectorAsync(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, queue_size=10000)
        self._processed_blobs = []
        self._processed_blob_names = set()
        self._blobs_to_delete = []
        self.checkpoint_manager = CheckpointManager(conn_string=os.environ['AzureWebJobsStorage'])
        self.checkpoint_lock = asyncio.Lock()
        self.last_saved_date = None
        self.last_saved_exclude_files = None
        self.last_saved_include_files = set()

    def _create_container_client(self):
        return ContainerClient.from_connection_string(self.__conn_string, self.__container_name, logging_enable=False)

    async def get_blobs(self, updated_after: datetime.datetime, exclude_files: list, include_files: set):
        print('Start getting blobs')
        logging.info('Start getting blobs')
        container_client = self._create_container_client()
        async with container_client:
            async for blob in container_client.list_blobs():
                if 'ownership-challenge' in blob['name']:
                    continue
                if blob['name'] in include_files:
                    self.blobs.append(blob)
                    continue
                if updated_after and blob['last_modified'] < updated_after:
                    self._blobs_to_delete.append(blob)
                    continue
                if blob['name'] in exclude_files:
                    self._blobs_to_delete.append(blob)
                    continue
                self.blobs.append(blob)
        print('Finish getting blobs. Count {}'.format(len(self.blobs)))
        logging.info('Finish getting blobs. Count {}'.format(len(self.blobs)))

    async def process_blobs(self):
        if self.blobs:
            container_client = self._create_container_client()
            async with container_client:
                await asyncio.wait([self._process_blob(blob, container_client) for blob in self.blobs])
            await self.sentinel.flush()

    async def delete_old_blobs(self):
        if self._blobs_to_delete:
            container_client = self._create_container_client()
            async with container_client:
                await asyncio.wait([self._delete_blob(blob, container_client) for blob in self._blobs_to_delete])

    async def _delete_blob(self, blob, container_client):
        print("Deleting blob {}".format(blob['name']))
        logging.info("Deleting blob {}".format(blob['name']))
        await container_client.delete_blob(blob['name'])

    async def _process_blob(self, blob, container_client):
        async with self.semaphore:
            print("Start processing {}".format(blob['name']))
            logging.info("Start processing {}".format(blob['name']))
            blob_cor = await container_client.download_blob(blob['name'])
            s = ''
            async for chunk in blob_cor.chunks():
                s += chunk.decode()
                lines = s.splitlines()
                for n, line in enumerate(lines):
                    if n < len(lines) - 1:
                        if line:
                            event = json.loads(line)
                            await self.sentinel.send(event, log_type=self.log_type)
                s = line
            if s:
                event = json.loads(s)
                await self.sentinel.send(event, log_type=self.log_type)
            print("Finish processing {}".format(blob['name']))
            logging.info("Finish processing {}".format(blob['name']))
            await self.save_checkpoint(blob)
            
    def has_errors(self):
        return len(self._processed_blobs) != len(self.blobs)

    async def save_checkpoint(self, blob):
        async with self.checkpoint_lock:
            self._processed_blobs.append(blob)
            self._processed_blob_names.add(blob['name'])
            include_files = self.get_not_processed_files_names()
            last_date = self.get_last_blob_date()
            exlude_files = self.get_last_date_blob_names()
            cors = []
            if not self.last_saved_date or self.last_saved_date <= last_date:
                cors.append(self.checkpoint_manager.post_last_date(last_date))
            if self.last_saved_exclude_files != exlude_files:
                cors.append(self.checkpoint_manager.post_exclude_files(exlude_files))
            if self.last_saved_include_files != include_files:
                cors.append(self.checkpoint_manager.post_include_files(include_files))

            if cors:
                await asyncio.wait(cors)
                self.last_saved_date = last_date
                self.last_saved_exclude_files = exlude_files
                self.last_saved_include_files = include_files
                print('Checkpoint {} saved'.format(last_date))
                logging.info('Checkpoint {} saved'.format(last_date))

    def get_last_blob_date(self):
        if self._processed_blobs:
            return max([x['last_modified'] for x in self._processed_blobs])
        else:
            return None

    def get_last_date_blob_names(self):
        last_modified = self.get_last_blob_date()
        names = []
        for b in self._processed_blobs:
            if b['last_modified'] == last_modified:
                names.append(b['name'])
        return names

    def get_not_processed_files_names(self):
        return set([x['name'] for x in self.blobs if x['name'] not in self._processed_blob_names])


class CheckpointManager:
    def __init__(self, conn_string):
        self.last_date_state_manager = StateManagerAsync(connection_string=conn_string, file_path='last_date')
        self.exclude_files_state_manager = StateManagerAsync(connection_string=conn_string, file_path='exclude_files')
        self.exec_marker_state_manager = StateManagerAsync(connection_string=conn_string, file_path='exec_marker')
        self.include_files_state_manager = StateManagerAsync(connection_string=conn_string, file_path='include_files')

    async def get_last_date(self):
        res = await self.last_date_state_manager.get()
        if res:
            return parse_date(res)

    async def post_last_date(self, date: datetime.datetime):
        if date:
            await self.last_date_state_manager.post(date.isoformat())

    async def get_exclude_files(self):
        res = await self.exclude_files_state_manager.get()
        if res:
            return [row.strip() for row in res.split('\n') if row.strip()]
        else:
            return []

    async def post_exclude_files(self, exclude_files: list):
        if exclude_files:
            data = '\n'.join(exclude_files)
            await self.exclude_files_state_manager.post(data)

    async def script_is_active(self):
        res = await self.exec_marker_state_manager.get()
        if res == '1':
            return True
        else:
            return False

    async def mark_script_as_inactive(self):
        await self.exec_marker_state_manager.post('0')

    async def mark_script_as_active(self):
        await self.exec_marker_state_manager.post('1')

    async def get_include_files(self):
        res = await self.include_files_state_manager.get()
        if res:
            return set([row.strip() for row in res.split('\n') if row.strip()])
        else:
            return set()

    async def post_include_files(self, include_files: list):
        if include_files:
            data = '\n'.join(include_files)
        else:
            data = ''
        await self.include_files_state_manager.post(data)
