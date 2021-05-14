import os
import asyncio
from azure.storage.blob.aio import ContainerClient
import json
import logging
from dateutil.parser import parse as parse_date
import datetime
import azure.functions as func
import re
import time

from .sentinel_connector_async import AzureSentinelMultiConnectorAsync
from .state_manager import StateManagerAsync


logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)


# interval of script execution
SCRIPT_EXECUTION_INTERVAL_MINUTES = 2
# if ts of last processed file is older than "now - MAX_PERIOD_MINUTES" then script will get events from "now - MAX_PERIOD_MINUTES"
MAX_PERIOD_MINUTES = 60 * 24 * 7

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
    last_date = await checkpoint_manager.get_last_date()
    exclude_files = []
    include_files = set()
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    if not last_date:
        last_date = now - datetime.timedelta(minutes=SCRIPT_EXECUTION_INTERVAL_MINUTES)
        logging.info('Last processed file date is not known. Getting files updated after {}'.format(last_date))
    else:
        diff_seconds = (now - last_date).days * 86400 + (now - last_date).seconds
        if diff_seconds > MAX_PERIOD_MINUTES * 60:
            old_last_date = last_date
            last_date = now - datetime.timedelta(minutes=MAX_PERIOD_MINUTES)
            logging.info('Last processed file date {} is older than max search period ({} minutes). Getting files for max search period (updated after {})'.format(old_last_date, MAX_PERIOD_MINUTES, last_date))
        else:
            exclude_files = await checkpoint_manager.get_exclude_files()
            include_files = await checkpoint_manager.get_include_files()
            logging.info('Getting files updated after {}'.format(last_date))

    conn = AzureBlobStorageConnector(AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME)
    await conn.get_blobs(updated_after=last_date, exclude_files=exclude_files, include_files=include_files)
    await conn.process_blobs()

    message = 'Program finished. {} events have been sent. {} events have not been sent'.format(
        conn.sentinel.successfull_sent_events_number,
        conn.sentinel.failed_sent_events_number
    )
    logging.info(message)

    await conn.save_checkpoint()
    await conn.delete_old_blobs()


def divide_chunks(ls, n):
    """
    Yield successive n-sized
    chunks from l.
    """
    # looping till length l
    for i in range(0, len(ls), n):
        yield ls[i:i + n]


class AzureBlobStorageConnector:
    def __init__(self, conn_string, container_name, queue_max_size=10):
        self.__conn_string = conn_string
        self.__container_name = container_name
        self.semaphore = asyncio.Semaphore(queue_max_size)
        self.blobs = []
        self.log_type = LOG_TYPE
        self.sentinel = AzureSentinelMultiConnectorAsync(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, queue_size=10000)
        self._processed_blobs = []
        self._blobs_to_delete = []
        self.checkpoint_manager = CheckpointManager(conn_string=os.environ['AzureWebJobsStorage'])
        self.script_start_time = int(time.time())

    def _create_container_client(self):
        return ContainerClient.from_connection_string(self.__conn_string, self.__container_name, logging_enable=False)

    async def get_blobs(self, updated_after: datetime.datetime, exclude_files: list, include_files: set):
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
        self.blobs = sorted(self.blobs, key=lambda x: x['last_modified'])
        logging.info('Finish getting blobs. Count {}'.format(len(self.blobs)))

    async def process_blobs(self):
        if self.blobs:
            all_blobs = list(divide_chunks(self.blobs, 20))
            for blobs in all_blobs:
                if self.check_if_script_runs_too_long():
                    logging.info('Script is running too long. Saving progress and exit.')
                    return
                container_client = self._create_container_client()
                async with container_client:
                    await asyncio.wait([self._process_blob(blob, container_client) for blob in blobs])
                await self.sentinel.flush()
                await self.save_checkpoint()

    def check_if_script_runs_too_long(self):
        now = int(time.time())
        duration = now - self.script_start_time
        max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.9)
        return duration > max_duration

    async def delete_old_blobs(self):
        if self._blobs_to_delete:
            all_blobs = list(divide_chunks(self._blobs_to_delete, 100))
            for blobs in all_blobs:
                container_client = self._create_container_client()
                async with container_client:
                    await asyncio.wait([self._delete_blob(blob, container_client) for blob in blobs])

    async def _delete_blob(self, blob, container_client):
        logging.info("Deleting blob {}".format(blob['name']))
        await container_client.delete_blob(blob['name'])

    async def _process_blob(self, blob, container_client):
        async with self.semaphore:
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
            self._processed_blobs.append(blob)
            logging.info("Finish processing {}".format(blob['name']))

    @property
    def _processed_blob_names(self):
        return set([x['name'] for x in self._processed_blobs])

    async def save_checkpoint(self):
        if self.sentinel.failed_sent_events_number:
            raise Exception('Program finished with errors. {} events have not been sent'.format(self.sentinel.failed_sent_events_number))

        last_date = self.get_last_blob_date()
        include_files = self.get_not_processed_files_names_before_date(last_date)
        exlude_files = self.get_last_date_blob_names()
        cors = []
        cors.append(self.checkpoint_manager.post_last_date(last_date))
        cors.append(self.checkpoint_manager.post_exclude_files(exlude_files))
        cors.append(self.checkpoint_manager.post_include_files(include_files))

        if cors:
            await asyncio.wait(cors)

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

    def get_not_processed_files_names_before_date(self, date: datetime.datetime):
        file_names = set()
        for blob in self.blobs:
            if blob['name'] not in self._processed_blob_names:
                if not isinstance(date, datetime.datetime) or blob['last_modified'] <= date:
                    file_names.add(blob['name'])
        return file_names


class CheckpointManager:
    def __init__(self, conn_string):
        self.last_date_state_manager = StateManagerAsync(connection_string=conn_string, file_path='last_date')
        self.exclude_files_state_manager = StateManagerAsync(connection_string=conn_string, file_path='exclude_files')
        self.include_files_state_manager = StateManagerAsync(connection_string=conn_string, file_path='include_files')

    async def get_last_date(self):
        logging.info('Checkpoint Manager - getting last_date')
        res = await self.last_date_state_manager.get()
        if res:
            return parse_date(res)

    async def post_last_date(self, date: datetime.datetime):
        logging.info(f'Checkpoint Manager - saving last_date: {date}')
        if date:
            await self.last_date_state_manager.post(date.isoformat())

    async def get_exclude_files(self):
        logging.info('Checkpoint Manager - getting exclude_files')
        res = await self.exclude_files_state_manager.get()
        if res:
            return [row.strip() for row in res.split('\n') if row.strip()]
        else:
            return []

    async def post_exclude_files(self, exclude_files: list):
        logging.info('Checkpoint Manager - saving exclude_files')
        if exclude_files:
            data = '\n'.join(exclude_files)
            await self.exclude_files_state_manager.post(data)

    async def get_include_files(self):
        logging.info('Checkpoint Manager - getting include_files')
        res = await self.include_files_state_manager.get()
        if res:
            return set([row.strip() for row in res.split('\n') if row.strip()])
        else:
            return set()

    async def post_include_files(self, include_files: list):
        logging.info('Checkpoint Manager - saving include_files')
        if include_files:
            data = '\n'.join(include_files)
        else:
            data = ''
        await self.include_files_state_manager.post(data)
