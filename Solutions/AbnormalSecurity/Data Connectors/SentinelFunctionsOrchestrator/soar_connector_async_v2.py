import json
from urllib.parse import urlencode, urljoin
import aiohttp
import logging
import asyncio
import itertools
from typing import Dict, List
from base64 import b64encode
from .utils import (
    OptionalEndTimeRange,
    FilterParam,
    MAP_RESOURCE_TO_LOGTYPE,
    Resource,
    TIME_FORMAT,
    compute_intervals,
    Context,
    try_str_to_datetime,
)


def get_query_params(
    filter_param: FilterParam, interval: OptionalEndTimeRange
) -> Dict[str, str]:
    filter = filter_param.name
    filter += f" gte {interval.start.strftime(TIME_FORMAT)}"
    if interval.end is not None:
        filter += f" lte {interval.end.strftime(TIME_FORMAT)}"

    return {"filter": filter}


def get_headers(ctx: Context) -> Dict[str, str]:
    sentinel_ctx = b64encode(ctx.json(exclude={'API_TOKEN'}).encode()).decode()
    return {
        "X-Sentinel-Context": sentinel_ctx,
        "X-Abnormal-Trace-Id": str(ctx.TRACE_ID),
        "Authorization": f"Bearer {ctx.API_TOKEN}",
        "Soar-Integration-Origin": "AZURE SENTINEL",
        "Azure-Sentinel-Version": "2024-12-24 V2",
    }


def compute_url(base_url: str, pathname: str, params: Dict[str, str]) -> str:
    endpoint = urljoin(base_url, pathname)

    params_str = urlencode(params)
    if params_str:
        endpoint += f"?{params_str}"

    return endpoint


async def fetch_with_retries(url, retries=3, backoff=8, timeout=60, headers=None):
    logging.info(f"Fetching url: {url}")
    async def fetch(session, url):
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if 500 <= response.status < 600:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    code=response.status,
                    message=response.reason,
                    headers=response.headers,
                )
            # response.raise_for_status()
            text = await response.text()
            logging.debug(f"API Response for URL: `{url}` is: `{text}`")
            logging.info(f"API Response Status for URL: `{url}` is `{response.status}`")
            return json.loads(text)

    for attempt in range(1, retries + 1):
        async with aiohttp.ClientSession() as session:
            try:
                logging.info(f"Fetch Attempt `{attempt}` for url: `{url}`")
                response = await fetch(session, url)
                return response
            except aiohttp.ClientResponseError as e:
                if 500 <= e.status < 600:
                    logging.error(f"Attempt {attempt} for {url} failed with error", exc_info=e)
                    if attempt == retries:
                        raise
                    else:
                        await asyncio.sleep(backoff**attempt)
                else:
                    raise
            except Exception as e:
                logging.error(f"Attempt {attempt} for {url} failed with error", exc_info=e)
                if attempt == retries:
                    raise
                else:
                    await asyncio.sleep(backoff**attempt)


async def call_threat_campaigns_endpoint(
    ctx: Context, interval: OptionalEndTimeRange, semaphore: asyncio.Semaphore
) -> List[str]:
    async with semaphore:
        params = get_query_params(
            filter_param=FilterParam.latestTimeRemediated, interval=interval
        )

        threat_campaigns = set()

        pageNumber = 1
        while pageNumber:
            params["pageNumber"] = pageNumber
            endpoint = compute_url(ctx.BASE_URL, "/v1/threats", params)
            headers = get_headers(ctx)

            response = await fetch_with_retries(url=endpoint, headers=headers)
            total = response["total"]
            assert total >= 0

            threat_campaigns.update(
                [threat["threatId"] for threat in response.get("threats", [])]
            )

            nextPageNumber = response.get("nextPageNumber")
            assert nextPageNumber is None or nextPageNumber == pageNumber + 1
            pageNumber = nextPageNumber

            if pageNumber is None or pageNumber > ctx.MAX_PAGE_NUMBER:
                break

        return list(threat_campaigns)


async def call_cases_endpoint(
    ctx: Context, interval: OptionalEndTimeRange, semaphore: asyncio.Semaphore
) -> List[str]:
    async with semaphore:
        params = get_query_params(
            filter_param=FilterParam.customerVisibleTime, interval=interval
        )

        case_ids = set()

        pageNumber = 1
        while pageNumber:
            params["pageNumber"] = pageNumber
            endpoint = compute_url(ctx.BASE_URL, "/v1/cases", params)
            headers = get_headers(ctx)

            response = await fetch_with_retries(url=endpoint, headers=headers)
            total = response["total"]
            assert total >= 0

            case_ids.update([case["caseId"] for case in response.get("cases", [])])

            nextPageNumber = response.get("nextPageNumber")
            assert nextPageNumber is None or nextPageNumber == pageNumber + 1
            pageNumber = nextPageNumber

            if pageNumber is None or pageNumber > ctx.MAX_PAGE_NUMBER:
                break

        return list(case_ids)


async def call_single_threat_endpoint(
    ctx: Context, threat_id: str, semaphore: asyncio.Semaphore
) -> List[str]:
    async with semaphore:
        filtered_messages = []

        pageNumber = 1
        params = {"pageSize": ctx.SINGLE_THREAT_PAGE_SIZE}
        while pageNumber:
            params["pageNumber"] = pageNumber
            print("Single Threat Params:", params)
            endpoint = compute_url(ctx.BASE_URL, f"/v1/threats/{threat_id}", params=params)
            headers = get_headers(ctx)

            response = await fetch_with_retries(url=endpoint, headers=headers)

            for message in response["messages"]:
                message_id = message["abxMessageId"]
                remediation_time_str = message["remediationTimestamp"]

                remediation_time = try_str_to_datetime(remediation_time_str)
                if (
                    remediation_time >= ctx.CLIENT_FILTER_TIME_RANGE.start
                    and remediation_time < ctx.CLIENT_FILTER_TIME_RANGE.end
                ):
                    filtered_messages.append(json.dumps(message, sort_keys=True))
                    logging.info(f"Successfully processed v2 threat message: {message_id}")
                elif remediation_time < ctx.CLIENT_FILTER_TIME_RANGE.start:
                    logging.info(f"Skipping further messages as remediationTime {remediation_time} of {message_id} < {ctx.CLIENT_FILTER_TIME_RANGE.start}")
                    return list(set(filtered_messages))
                else:
                    logging.warning(f"Skipped processing v2 threat message: {message_id}")

            nextPageNumber = response.get("nextPageNumber")
            assert nextPageNumber is None or nextPageNumber == pageNumber + 1
            pageNumber = nextPageNumber

            if pageNumber is None or pageNumber > ctx.MAX_PAGE_NUMBER:
                break
        
        return list(set(filtered_messages))


async def call_single_case_endpoint(
    ctx: Context, case_id: str, semaphore: asyncio.Semaphore
) -> str:
    async with semaphore:
        endpoint = compute_url(ctx.BASE_URL, f"/v1/cases/{case_id}", params={})
        headers = get_headers(ctx)

        response = await fetch_with_retries(url=endpoint, headers=headers)

        return json.dumps(response, sort_keys=True)


async def get_threats(ctx: Context, output_queue: asyncio.Queue) -> asyncio.Queue:
    intervals = compute_intervals(ctx)
    logging.info(
        "Computed threats intervals\n"
        + "\n".join(map(lambda x: f"{str(x.start)} : {str(x.end)}", intervals))
    )

    assert len(intervals) <= 5, "Intervals more than 5"
    semaphore = asyncio.Semaphore(ctx.NUM_CONCURRENCY)

    campaign_result = await asyncio.gather(
        *[
            call_threat_campaigns_endpoint(
                ctx=ctx, interval=interval, semaphore=semaphore
            )
            for interval in intervals
        ]
    )
    threat_ids = set(itertools.chain(*campaign_result))

    single_result = await asyncio.gather(
        *[
            call_single_threat_endpoint(
                ctx=ctx, threat_id=threat_id, semaphore=semaphore
            )
            for threat_id in threat_ids
        ]
    )
    messages = set(itertools.chain(*single_result))

    for message in messages:
        record = (MAP_RESOURCE_TO_LOGTYPE[Resource.threats], json.loads(message))
        logging.debug(f"Inserting threat message record {record}")
        await output_queue.put(record)

    return


async def get_cases(ctx: Context, output_queue: asyncio.Queue) -> asyncio.Queue:
    intervals = compute_intervals(ctx)
    logging.info(
        "Computed cases intervals\n"
        + "\n".join(map(lambda x: f"{str(x.start)} : {str(x.end)}", intervals))
    )

    assert len(intervals) <= 5, "Intervals more than 5"
    semaphore = asyncio.Semaphore(ctx.NUM_CONCURRENCY)

    result = await asyncio.gather(
        *[
            call_cases_endpoint(ctx=ctx, interval=interval, semaphore=semaphore)
            for interval in intervals
        ]
    )
    case_ids = set(itertools.chain(*result))

    cases = await asyncio.gather(
        *[
            call_single_case_endpoint(ctx=ctx, case_id=case_id, semaphore=semaphore)
            for case_id in case_ids
        ]
    )

    for case in cases:
        loaded_case = json.loads(case)
        record = (MAP_RESOURCE_TO_LOGTYPE[Resource.cases], loaded_case)
        visible_time = try_str_to_datetime(loaded_case["customerVisibleTime"])
        if visible_time >= ctx.CLIENT_FILTER_TIME_RANGE.start and visible_time < ctx.CLIENT_FILTER_TIME_RANGE.end:
            logging.info(f"Successfully processed v2 case id {loaded_case['caseId']}")
            await output_queue.put(record)
        else:
            logging.warning(f"Skipped processing v2 case id {loaded_case['caseId']}")

    return


