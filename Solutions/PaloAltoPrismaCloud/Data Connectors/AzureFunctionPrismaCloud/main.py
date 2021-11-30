import asyncio
import aiohttp
import json
import time
import os
import re
import logging

import azure.functions as func

from .state_manager_async import StateManagerAsync
from .sentinel_connector_async import AzureSentinelMultiConnectorAsync

logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)

WORKSPACE_ID = os.environ['AzureSentinelWorkspaceId']
SHARED_KEY = os.environ['AzureSentinelSharedKey']
API_URL = os.environ['PrismaCloudAPIUrl']
USER = os.environ['PrismaCloudAccessKeyID']
PASSWORD = os.environ['PrismaCloudSecretKey']
FILE_SHARE_CONN_STRING = os.environ['AzureWebJobsStorage']
ALERT_LOG_TYPE = 'PaloAltoPrismaCloudAlert'
AUDIT_LOG_TYPE = 'PaloAltoPrismaCloudAudit'


# if ts of last event is older than now - MAX_PERIOD_MINUTES -> script will get events from now - MAX_PERIOD_MINUTES
MAX_PERIOD_MINUTES = 60 * 24 * 7


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


async def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    prisma = PrismaCloudConnector(API_URL, USER, PASSWORD)

    tasks = [
        prisma.process_alerts(),
        prisma.process_audit_logs()
    ]
    await asyncio.gather(*tasks)

    logging.info('Program finished. {} events have been sent.'.format(prisma.sentinel.successfull_sent_events_number))


class PrismaCloudConnector:
    def __init__(self, api_url, username, password):
        self.api_url = api_url
        self.__username = username
        self.__password = password
        self._token = None
        self._auth_lock = asyncio.Lock()
        self.alerts_state_manager = StateManagerAsync(FILE_SHARE_CONN_STRING, share_name='prismacloudcheckpoint', file_path='prismacloudlastalert')
        self.auditlogs_state_manager = StateManagerAsync(FILE_SHARE_CONN_STRING, share_name='prismacloudcheckpoint', file_path='prismacloudlastauditlog')
        self.sentinel = AzureSentinelMultiConnectorAsync(LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, queue_size=10000)
        self.sent_alerts = 0
        self.sent_audit_logs = 0
        self.last_alert_ts = None
        self.last_audit_ts = None

    async def process_alerts(self):
        last_alert_ts_ms = await self.alerts_state_manager.get()
        max_period = (int(time.time()) - MAX_PERIOD_MINUTES * 60) * 1000
        if not last_alert_ts_ms or int(last_alert_ts_ms) < max_period:
            alert_start_ts_ms = max_period
            logging.info('Last alert was too long ago or there is no info about last alert timestamp.')
        else:
            alert_start_ts_ms = int(last_alert_ts_ms) + 1
        logging.info('Starting searching alerts from {}'.format(alert_start_ts_ms))

        async for alert in self.get_alerts(start_time=alert_start_ts_ms):
            last_alert_ts_ms = alert['alertTime']
            alert = self.clear_alert(alert)
            await self.sentinel.send(alert, log_type=ALERT_LOG_TYPE)
            self.sent_alerts += 1

        self.last_alert_ts = last_alert_ts_ms

        conn = self.sentinel.get_log_type_connector(ALERT_LOG_TYPE)
        if conn:
            await conn.flush()
            logging.info('{} alerts have been sent'.format(self.sent_alerts))
        await self.save_alert_checkpoint()

    async def process_audit_logs(self):
        last_log_ts_ms = await self.auditlogs_state_manager.get()
        max_period = (int(time.time()) - MAX_PERIOD_MINUTES * 60) * 1000
        if not last_log_ts_ms or int(last_log_ts_ms) < max_period:
            log_start_ts_ms = max_period
            logging.info('Last audit log was too long ago or there is no info about last log timestamp.')
        else:
            log_start_ts_ms = int(last_log_ts_ms) + 1
        logging.info('Starting searching audit logs from {}'.format(log_start_ts_ms))

        async for event in self.get_audit_logs(start_time=log_start_ts_ms):
            if not last_log_ts_ms:
                last_log_ts_ms = event['timestamp']
            elif event['timestamp'] > int(last_log_ts_ms):
                last_log_ts_ms = event['timestamp']
            await self.sentinel.send(event, log_type=AUDIT_LOG_TYPE)
            self.sent_audit_logs += 1

        self.last_audit_ts = last_log_ts_ms

        conn = self.sentinel.get_log_type_connector(AUDIT_LOG_TYPE)
        if conn:
            await conn.flush()
            logging.info('{} audit logs have been sent'.format(self.sent_audit_logs))
        await self.save_audit_checkpoint()

    async def _authorize(self):
        async with self._auth_lock:
            if not self._token:
                uri = self.api_url + '/login'
                headers = {
                    "Accept": "application/json; charset=UTF-8",
                    "Content-Type": "application/json; charset=UTF-8"
                }
                data = {
                    'username': self.__username,
                    'password': self.__password
                }
                data = json.dumps(data)
                async with aiohttp.ClientSession() as session:
                    async with session.post(uri, data=data, headers=headers) as response:
                        if response.status != 200:
                            raise Exception('Error while getting Prisma Cloud auth token. HTTP status code: {}'.format(response.status))
                        res = await response.text()

                res = json.loads(res)
                self._token = res['token']
                logging.info('Auth token for Prisma Cloud was obtained.')

    async def get_alerts(self, start_time):
        await self._authorize()
        uri = self.api_url + '/v2/alert'
        headers = {
            'x-redlock-auth': self._token,
            "Accept": "application/json; charset=UTF-8",
            "Content-Type": "application/json; charset=UTF-8"
        }
        async with aiohttp.ClientSession() as session:
            unix_ts_now = (int(time.time()) - 10) * 1000
            data = {
                "timeRange": {
                    "type": "absolute",
                    "value": {
                        "startTime": start_time,
                        "endTime": unix_ts_now
                    }
                },
                "sortBy": ["alertTime:asc"],
                "detailed": True
            }
            data = json.dumps(data)
            async with session.post(uri, headers=headers, data=data) as response:
                if response.status != 200:
                    raise Exception('Error while getting alerts. HTTP status code: {}'.format(response.status))
                res = await response.text()
                res = json.loads(res)

            for item in res['items']:
                yield item

            while 'nextPageToken' in res:
                data = {
                    'pageToken': res['nextPageToken']
                }
                data = json.dumps(data)
                async with session.post(uri, headers=headers, data=data) as response:
                    if response.status != 200:
                        raise Exception('Error while getting alerts. HTTP status code: {}'.format(response.status))
                    res = await response.text()
                    res = json.loads(res)
                for item in res['items']:
                    yield item

    @staticmethod
    def clear_alert(alert):
        if 'resource' in alert and 'data' in alert['resource']:
            del alert['resource']['data']
        return alert

    async def get_audit_logs(self, start_time):
        await self._authorize()
        uri = self.api_url + '/audit/redlock'
        headers = {
            'x-redlock-auth': self._token,
            "Accept": "*/*",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            unix_ts_now = (int(time.time()) - 10) * 1000
            params = {
                'timeType': 'absolute',
                'startTime': start_time,
                'endTime': unix_ts_now
            }
            async with session.get(uri, headers=headers, params=params) as response:
                if response.status != 200:
                    raise Exception('Error while getting audit logs. HTTP status code: {}'.format(response.status))
                res = await response.text()
                res = json.loads(res)

            for item in res:
                yield item

    async def save_alert_checkpoint(self):
        if self.last_alert_ts:
            await self.alerts_state_manager.post(str(self.last_alert_ts))
            logging.info('Last alert ts saved - {}'.format(self.last_alert_ts))

    async def save_audit_checkpoint(self):
        if self.last_audit_ts:
            await self.auditlogs_state_manager.post(str(self.last_audit_ts))
            logging.info('Last audit ts saved - {}'.format(self.last_audit_ts))
