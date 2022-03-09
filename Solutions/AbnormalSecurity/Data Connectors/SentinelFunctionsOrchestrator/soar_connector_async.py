import json
from urllib.parse import urlencode
from enum import Enum
import aiohttp
import logging
import asyncio


class Resources(Enum):
    threats = 0
    cases = 1

class FilterParam(Enum):
    receivedTime = 0
    createdTime = 1
    firstObserved = 2
    latestTimeRemediated = 3
    customerVisibleTime = 4


class AbnormalSoarConnectorAsync:
    BASEURL = "https://api.abnormalplatform.com/v1"
    MAP_RESOURCE_TO_LOGTYPE = {
        Resources.threats: "ABNORMAL_THREAT_MESSAGES",
        Resources.cases: "ABNORMAL_CASES"
    }

    def __init__(self, api_key, num_consumers=10) -> None:
        self.api_key = api_key
        self.num_consumers = num_consumers

    def _get_header(self):
        """
        returns header for all HTTP requests to Abnormal Security's API
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Soar-Integration-Origin": "AZURE SENTINEL",
        }

    def _get_filter_query(self, filter_param, gte_datetime=None, lte_datetime=None):
        """
        Receives an offset and determines if a commit should be done
        to the Kafka consumer. If a commit should be done, it will return the offset
        to commit. If not, it returns None.

        Args:
          offset (int): The record offset that is completed.
        """
        filter_string = f'{filter_param.name}'
        if gte_datetime:
            filter_string += ' ' + f'gte {gte_datetime}'
        if lte_datetime:
            filter_string += ' ' + f'lte {lte_datetime}'
        return {
            'filter': filter_string,
        }

    def _get_all_ids_url(self, resource, query_dict):
        return f"{self.BASEURL}/{resource.name}?{urlencode(query_dict)}"

    def _get_object_url(self, resource_name, resource_id):
        return f"{self.BASEURL}/{resource_name}/{resource_id}"

    def _extract_messages(self, context, threat_resp):
        return [message for message in threat_resp.get("messages") if message.get("receivedTime") >= context.get("gte_datetime") and message.get("receivedTime") <= context.get("lte_datetime")]

    def _extract_message_ids(self, threats_resp):
        return [threat.get("threatId") for threat in threats_resp.get('threats', [])]

    def _extract_case_ids(self, cases_resp):
        return [case.get("caseId") for case in cases_resp.get('cases', [])]

    async def _make_request(self, session, url, headers):
        async with session.get(url, headers=headers) as response:
            if not (200 <= response.status <= 299):
                raise Exception(
                    "Error during sending events to Abnormal SOAR API. Response code: {}. Text:{}".format(response.status, await response.text()))
            await asyncio.sleep(1)
            return json.loads(await response.text())

    async def _send_request(self, session, url):
        attempts = 1
        while True:
            try:
                response_data = await self._make_request(session, url, self._get_header())
            except Exception as e:
                if attempts < 3:
                    logging.warning(f'Error while getting data to Abnormal Soar API. Attempt:{attempts}. Err: {e}')
                    await asyncio.sleep(3)
                    attempts += 1
                else:
                    logging.error(f"Abnormal Soar API request Failed. Err: {e}")
                    return {}
            else:
                return response_data

    async def generate_resource_ids(self, session, resource, query_dict, output_queue, post_processing_func=lambda x:[x]):
        nextPageNumber = 1
        while nextPageNumber:
            query_dict["pageNumber"] = nextPageNumber
            response_data = await self._send_request(session, self._get_all_ids_url(resource, query_dict))
            for id in post_processing_func(response_data):
                await output_queue.put(id)
            nextPageNumber = response_data.get("nextPageNumber")

    async def process_resource_ids(self, session, resource, context, input_queue, output_queue, post_processing_func=lambda context, x:[x]):
        resource_log_type = self.MAP_RESOURCE_TO_LOGTYPE[resource]
        while True:
            current_id = await input_queue.get()
            try:
                response_data = await self._send_request(session, self._get_object_url(resource.name, current_id))
            except Exception:
                logging.error(f"Discarding enqueued resource id: {current_id}")
            else:
                for output in post_processing_func(context, response_data):
                    await output_queue.put((resource_log_type, output))
            input_queue.task_done()

    async def get_all_threat_messages(self, context, output_queue, caching_func=None):
        intermediate_queue = asyncio.Queue()
        async with aiohttp.ClientSession() as session:
            filter_query = self._get_filter_query(FilterParam.latestTimeRemediated, context.get("gte_datetime"), context.get("lte_datetime"))
            producer_post_process_func = lambda x: caching_func(self._extract_message_ids(x)) if caching_func else self._extract_message_ids(x)
            producer = asyncio.create_task(self.generate_resource_ids(session, Resources.threats, filter_query, intermediate_queue, producer_post_process_func))
            consumers = [asyncio.create_task(self.process_resource_ids(session, Resources.threats, context, intermediate_queue, output_queue, self._extract_messages)) for _ in range(self.num_consumers)]
            await asyncio.gather(producer)
            await intermediate_queue.join()  # Implicitly awaits consumers, too
            for c in consumers:
                c.cancel()


    async def get_all_cases(self, context, output_queue, caching_func=None):
        intermediate_queue = asyncio.Queue()
        async with aiohttp.ClientSession() as session:
            filter_query = self._get_filter_query(FilterParam.customerVisibleTime, context.get("gte_datetime"), context.get("lte_datetime"))
            producer_post_process_func = lambda x: caching_func(self._extract_case_ids(x)) if caching_func else self._extract_case_ids(x)
            producer = asyncio.create_task(self.generate_resource_ids(session, Resources.cases, filter_query, intermediate_queue, producer_post_process_func))
            consumers = [asyncio.create_task(self.process_resource_ids(session, Resources.cases, context, intermediate_queue, output_queue)) for _ in range(self.num_consumers)]
            await asyncio.gather(producer)
            await intermediate_queue.join()  # Implicitly awaits consumers, too
            for c in consumers:
                c.cancel()