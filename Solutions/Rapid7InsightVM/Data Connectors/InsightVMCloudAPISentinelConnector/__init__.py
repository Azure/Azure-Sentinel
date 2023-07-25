import os
from typing import List, Optional, AsyncIterable, Set
import asyncio
import logging
import re
import json
import datetime
import azure.functions as func
import aiohttp
from dateutil.parser import parse as parse_date

from .sentinel_connector_async import AzureSentinelConnectorAsync
from .state_manager_async import StateManagerAsync

logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
logging.getLogger('charset_normalizer').setLevel(logging.ERROR)

INSIGHTVM_APIKEY = os.environ['InsightVMAPIKey']
INSIGHTVM_REGION = os.environ['InsightVMCloudRegion']
WORKSPACE_ID = os.environ['WorkspaceID']
SHARED_KEY = os.environ['WorkspaceKey']
AZURE_WEB_JOBS_STORAGE_CONNECTION_STRING = os.environ['AzureWebJobsStorage']

LOG_TYPE_ASSETS = 'NexposeInsightVMCloud_assets'
LOG_TYPE_VULNS = 'NexposeInsightVMCloud_vulnerabilities'

VULNERS_API_REQUEST_CHUNK_SIZE = 50
ASSETS_API_REQUSET_CHUNK_SIZE = 500


LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')

if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")


async def main(mytimer: func.TimerRequest):
    logging.info('Script started.')
    async with aiohttp.ClientSession() as session_api:
        async with aiohttp.ClientSession() as session_sentinel:
            delay = os.environ.get('Delay', "60")
            shift_start_time = os.environ.get('ShiftStartTime', "60")
            current_time = datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0, second=0)
            end_time = current_time - datetime.timedelta(minutes=int(delay))
            api = InsightVMAPI(session_api, INSIGHTVM_REGION, INSIGHTVM_APIKEY)
            sentinel = AzureSentinelConnectorAsync(session=session_sentinel, log_analytics_uri=LOG_ANALYTICS_URI,
                                                   workspace_id=WORKSPACE_ID, shared_key=SHARED_KEY)
            state_manager = StateManagerAsync(connection_string=AZURE_WEB_JOBS_STORAGE_CONNECTION_STRING,
                                              file_path='rapid7_last_scan_date')
            start_time = await state_manager.get_last_date_from_storage(end_time=end_time, current_time=current_time,
                                                                        shift_start_time=shift_start_time)
            if(datetime.timedelta(days=4) < (end_time - start_time)):
                end_time = start_time + datetime.timedelta(days=4)
            logging.info(f'Data processing. Period(UTC): {start_time} - {end_time}')
            last_processed_date = None
            async for assets in api.get_assets(start_time=start_time, end_time=end_time):
                last_processed_date = await process_assets(assets=assets, api=api, sentinel=sentinel,
                                                           state_manager=state_manager)
                state_manager.remember_last_date(last_processed_date)
            if(last_processed_date is None):
                logging.info('Last Processed date is None so setting EndDate {}'.format(end_time))
                state_manager.remember_last_date(end_time)
            await state_manager.save_last_date_to_storage()
    logging.info(f'Script finished. Total sent events: {sentinel.successfull_sent_events_number}')


class InsightVMAPI:
    def __init__(self, session: aiohttp.ClientSession, region: str, api_key: str):
        self.session = session
        self.base_url = f'https://{region}.api.insight.rapid7.com/vm'
        self._api_key = api_key
        self.processed_vulner_ids: Set[str] = set()

    async def get_assets(self, start_time: Optional[datetime.datetime] = None,
                         end_time: Optional[datetime.datetime] = None) -> AsyncIterable[list]:
        cursor = None
        while True:
            res = await self._make_get_assets_request(cursor, start_time=start_time, end_time=end_time)
            assets = res['data']
            logging.info(f'Assets found: {len(assets)}')
            yield assets
            cursor = res['metadata'].get('cursor')
            if not assets or not cursor:
                break
        logging.info(f'Finish getting assets.')

    async def _make_get_assets_request(self, cursor: Optional[str] = None,
                                       start_time: Optional[datetime.datetime] = None,
                                       end_time: Optional[datetime.datetime] = None) -> dict:
        method = 'POST'
        endpoint = '/v4/integration/assets'
        params = {
            'size': ASSETS_API_REQUSET_CHUNK_SIZE,
            'includeSame': 'true',
            'includeUniqueIdentifiers': 'true'
        }
        if cursor:
            params['cursor'] = cursor
        if isinstance(start_time, datetime.datetime):
            date = start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
            payload = {
                'asset': f'last_scan_end > {date}'
            }
        else:
            payload = None
        res = await self._make_api_request(method=method, endpoint=endpoint, params=params, payload=payload)

        delay_res = []
        if res:
            for event in res["data"]:
                if "last_scan_end" in event and parse_date(event["last_scan_end"]) < end_time:
                    delay_res.append(event)
        else:
            res = {}

        filtered_res = res
        filtered_res["data"] = delay_res

        return filtered_res

    async def get_all_vulners(self) -> dict:
        logging.info('Start getting vulners.')
        vulners = {}
        cursor = None
        while True:
            res = await self._make_get_vulners_request(cursor)
            for vuln in res['data']:
                vulners[vuln['id']] = vuln
            logging.info(f'Vulners found: {len(vulners)}')

            cursor = res['metadata'].get('cursor')
            if not res['data'] or not cursor:
                break

        logging.info(f'Finish getting vulners. Total found: {len(vulners)}')
        return vulners

    async def search_vulners_by_ids(self, vulner_ids: List[str]) -> List[dict]:
        if not vulner_ids:
            return []
        logging.info(f'Start searching {len(vulner_ids)} vulnerabilities in API.')
        res = await self._make_get_vulners_request(vulner_ids=vulner_ids)
        return res['data']

    async def _make_get_vulners_request(self, cursor: Optional[str] = None, vulner_ids: Optional[List[str]] = None) -> dict:
        method = 'POST'
        endpoint = '/v4/integration/vulnerabilities'
        params = {
            'size': 500,
            'sort': 'id,asc'
        }
        if cursor:
            params['cursor'] = cursor

        payload = {'vulnerability': f"id IN {vulner_ids}"} if vulner_ids else None
        res = await self._make_api_request(method=method, endpoint=endpoint, params=params, payload=payload)
        res = res if res else {}
        return res

    async def _make_api_request(self, method: str, endpoint: str, params: Optional[dict] = None, payload: Optional[dict] = None) -> Optional[dict]:
        url = f'{self.base_url}{endpoint}'
        headers = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'X-Api-Key': self._api_key
        }
        body = json.dumps(payload) if payload else None

        try_number = 1
        while True:
            try:
                res = await self._make_http_request(method, url, params, headers, body)
                return res
            except Exception as err:
                if try_number < 3:
                    logging.warning('Error during making request to InsightVM API. Try number: {}. Trying one more time. {}'.format(try_number, err))
                    await asyncio.sleep(try_number)
                    try_number += 1
                else:
                    logging.error(str(err))
                    raise err

    async def _make_http_request(self, method: str, url: str, params: Optional[dict], headers: Optional[dict], body: Optional[str]) -> Optional[dict]:
        async with self.session.request(method=method, url=url, headers=headers, params=params, data=body) as response:
            response_body = await response.text()
            if not response.ok:
                raise Exception("Error during making request to InsightVM API. Response code: {}. Response body: {}".format(response.status, response_body))
            return json.loads(response_body)


async def process_assets(assets: list, api: InsightVMAPI, sentinel: AzureSentinelConnectorAsync, state_manager=StateManagerAsync) -> Optional[datetime.datetime]:
    await asyncio.gather(
        send_assets_to_sentinel(assets=assets, sentinel=sentinel),
        process_vulners_in_assets(assets=assets, api=api, sentinel=sentinel)
    )
    return get_last_scan_date_from_assets(assets)


async def process_vulners_in_assets(assets: list, api: InsightVMAPI, sentinel: AzureSentinelConnectorAsync) -> None:
    vulner_ids = get_vuner_ids_from_assets(assets)
    vulner_ids = [x for x in vulner_ids if x not in api.processed_vulner_ids]
    logging.info(f'Found {len(vulner_ids)} new unique vulnerabilities from assets. Start obtaining vulnerabilities from API.')
    vulners = await get_vulners_by_vulner_ids(vulner_ids=vulner_ids, api=api)
    logging.info(f'{len(vulners)} vulnerabilities obtained.')
    await send_vulners_to_sentinel(vulners=vulners, sentinel=sentinel)
    for vulner_id in vulner_ids:
        api.processed_vulner_ids.add(vulner_id)


def get_vuner_ids_from_assets(assets: List[dict]) -> List[str]:
    vulner_ids = set()
    for asset in assets:
        vulns = asset.get('same') if asset.get('same') else []
        for vuln in vulns:
            vuln_id = vuln.get('vulnerability_id')
            if vuln_id:
                vulner_ids.add(vuln_id)
    return list(vulner_ids)


async def get_vulners_by_vulner_ids(vulner_ids: List[str], api: InsightVMAPI) -> List[dict]:
    vulners = []
    cors = []
    for chunk in get_chunks_from_list(lst=vulner_ids, n=VULNERS_API_REQUEST_CHUNK_SIZE):
        cors.append(api.search_vulners_by_ids(vulner_ids=chunk))
    res = await asyncio.gather(*cors)
    for vulners_list in res:
        vulners.extend(vulners_list)
    return vulners


def get_chunks_from_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def send_assets_to_sentinel(assets: list, sentinel: AzureSentinelConnectorAsync) -> None:
    await sentinel.send_events(data=assets, log_type=LOG_TYPE_ASSETS)


async def send_vulners_to_sentinel(vulners: list, sentinel: AzureSentinelConnectorAsync) -> None:
    vulners = [{'asset_id': '', 'host_name': '', 'ip': '', 'vuln_details': vuln} for vuln in vulners]
    await sentinel.send_events(data=vulners, log_type=LOG_TYPE_VULNS)


def get_last_scan_date_from_assets(assets: List[dict]) -> Optional[datetime.datetime]:
    dates = []
    for asset in assets:
        try:
            date = parse_date(asset.get('last_scan_end'))
        except Exception:
            date = None
        if date:
            dates.append(date)
    if dates:
        return max(dates)
