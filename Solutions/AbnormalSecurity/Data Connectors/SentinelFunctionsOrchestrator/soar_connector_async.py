import json
from urllib.parse import urlencode
from enum import Enum
import aiohttp
import logging
import asyncio
import os
from datetime import datetime, timedelta
import azure.durable_functions as df

API_HOST = os.environ.get('API_HOST', 'https://api.abnormalplatform.com/v1')
MAX_THREATS = int(os.environ.get('MAX_NUMBER_OF_THREATS', 120))
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_FORMAT_WITHMS = "%Y-%m-%dT%H:%M:%S.%fZ"

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
    BASEURL = API_HOST
    MAP_RESOURCE_TO_LOGTYPE = {
        Resources.threats: "ABNORMAL_THREAT_MESSAGES",
        Resources.cases: "ABNORMAL_CASES"
    }
    
    MAP_RESOURCE_TO_ENTITY_VALUE = {
        Resources.threats: "threats_date",
        Resources.cases: "cases_date"
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
            "Azure-Sentinel-Version": "2024-12-24"
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
        threat_id = threat_resp.get("threatId")
        gte_datetime_str = context['gte_datetime']
        lte_datetime_str = context['lte_datetime']

        ctx = {
            "threat_id": threat_id,
            "gte_datetime_str": gte_datetime_str, 
            "lte_datetime_str": lte_datetime_str
        }

        try:
            gte_datetime = datetime.strptime(gte_datetime_str, TIME_FORMAT)
            lte_datetime = datetime.strptime(lte_datetime_str, TIME_FORMAT)
        except Exception as e:
            logging.error(f"Failed to parse time for threat_id: {ctx} with error {e}")
            return []

        filtered_messages = []
        for message in threat_resp.get("messages"):
            message_id = message.get("abxMessageId")
            remediation_time_str = message.get("remediationTimestamp")

            ctx = {
                **ctx,
                "message_id": message_id, 
                "remediation_time_str": remediation_time_str
            }

            try:
                remediation_time = datetime.strptime(remediation_time_str, TIME_FORMAT_WITHMS)
                if remediation_time >= gte_datetime and remediation_time <= lte_datetime:
                    filtered_messages.append(message)
                    logging.info(f"Successfully processed message for threat: {ctx}")
                else:
                    logging.warn(f"Skipped processing message for threat: {ctx}")
            except Exception as e:
                logging.error(f"Failed to process message for threat: {ctx} with error {e}")


        return filtered_messages

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
                    logging.warning(f'Error while getting data to Abnormal Soar API. Attempt:{attempts}. Err: {e} - URL: {url}')
                    await asyncio.sleep(3)
                    attempts += 1
                else:
                    logging.error(f"Abnormal Soar API request Failed. Err: {e}")
                    return {}
            else:
                return response_data

    async def generate_resource_ids(self, session, resource, date_filter, output_queue, filter_param, context, post_processing_func=lambda x:[x]):
        query_dict = self._get_filter_query(filter_param, date_filter.get("gte_datetime"), date_filter.get("lte_datetime"))
        entity_date_set = False 
        nextPageNumber = 1
        while nextPageNumber:
            query_dict["pageNumber"] = nextPageNumber
            response_data = await self._send_request(session, self._get_all_ids_url(resource, query_dict))
            total = response_data.get("total")
            logging.info(f"Total number of {resource} is: {total}")
            if self.should_date_range_be_halved(resource, total, date_filter):
                date_filter = self.halve_date_range(date_filter)
                await self.generate_resource_ids(session, Resources.threats, date_filter, output_queue, filter_param, context, post_processing_func)
                return 
            if not entity_date_set:
                self.set_date_on_entity(context, date_filter["lte_datetime"], self.MAP_RESOURCE_TO_ENTITY_VALUE[resource]) 
            for id in post_processing_func(response_data):
                await output_queue.put(id)
            nextPageNumber = response_data.get("nextPageNumber")
    
    def should_date_range_be_halved(self, resource, total, date_filter):
        return self.is_threats_threshold_breached(resource, total) and not self.is_date_range_minimum(date_filter)
            
    def is_threats_threshold_breached(self, resource, total):
        return resource == Resources.threats and total and total > MAX_THREATS

    def is_date_range_minimum(self, context):
        """
        Setting a base case for the recursive call of generate_resource_ids(). 
        """
        gte_datetime_str = context['gte_datetime']
        lte_datetime_str = context['lte_datetime']
        gte_datetime = datetime.strptime(gte_datetime_str, TIME_FORMAT)
        lte_datetime = datetime.strptime(lte_datetime_str, TIME_FORMAT)

        if (lte_datetime - gte_datetime) <= timedelta(minutes=1):
            logging.warning("Reached minimum date range for filter query")
            return True
        
        return False

    def set_date_on_entity(self, context, lte_datetime, entity_value):
        datetimeEntityId = df.EntityId("SoarDatetimeEntity", "latestDatetime")
        context.signal_entity(datetimeEntityId, "set", {"type": entity_value, "date": lte_datetime})
    
    def halve_date_range(self, threats_date_filter):
        """
        We want to halve the date range if the current one returns too many threats to avoid timeouts on the orchestration. 
        """
        try:
            gte_datetime_str = threats_date_filter['gte_datetime']
            lte_datetime_str = threats_date_filter['lte_datetime']
            gte_datetime = datetime.strptime(gte_datetime_str, TIME_FORMAT)
            lte_datetime = datetime.strptime(lte_datetime_str, TIME_FORMAT)
            midpoint_datetime = gte_datetime + (lte_datetime - gte_datetime) / 2
            midpoint_datetime_str = midpoint_datetime.strftime(TIME_FORMAT)
            threats_date_filter['lte_datetime'] = midpoint_datetime_str 
            logging.warning(f"Halved date range, too many results. New date range is {gte_datetime_str} - {midpoint_datetime_str}")
        except Exception as e:
            logging.error(f"Failed to halve date range: {e}")
        return threats_date_filter

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

    async def get_all_threat_messages(self, threats_date_filter, output_queue, context, caching_func=None):

        intermediate_queue = asyncio.Queue()
        async with aiohttp.ClientSession() as session:
            producer_post_process_func = lambda x: caching_func(self._extract_message_ids(x)) if caching_func else self._extract_message_ids(x)
            producer = asyncio.create_task(self.generate_resource_ids(session, Resources.threats,threats_date_filter, intermediate_queue, FilterParam.latestTimeRemediated, context, producer_post_process_func))
            consumers = [asyncio.create_task(self.process_resource_ids(session, Resources.threats, threats_date_filter, intermediate_queue, output_queue, self._extract_messages)) for _ in range(self.num_consumers)]
            await asyncio.gather(producer)
            await intermediate_queue.join()  # Implicitly awaits consumers, too
            for c in consumers:
                c.cancel()


    async def get_all_cases(self, cases_date_filter, output_queue, context, caching_func=None):
        intermediate_queue = asyncio.Queue()
        async with aiohttp.ClientSession() as session:
            producer_post_process_func = lambda x: caching_func(self._extract_case_ids(x)) if caching_func else self._extract_case_ids(x)
            producer = asyncio.create_task(self.generate_resource_ids(session, Resources.cases, cases_date_filter, intermediate_queue, FilterParam.customerVisibleTime,context, producer_post_process_func))
            consumers = [asyncio.create_task(self.process_resource_ids(session, Resources.cases, cases_date_filter, intermediate_queue, output_queue)) for _ in range(self.num_consumers)]
            await asyncio.gather(producer)
            await intermediate_queue.join()  # Implicitly awaits consumers, too
            for c in consumers:
                c.cancel()