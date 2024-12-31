import os

os.environ["ABNORMAL_SECURITY_REST_API_TOKEN"] = "123"

import unittest
from SentinelFunctionsOrchestrator.utils import (
    FilterParam,
    OptionalEndTimeRange,
    Context,
    TimeRange,
    try_str_to_datetime,
)
from datetime import datetime, timedelta
from uuid import UUID
import pytest
import aiohttp
from aiohttp import web
from unittest.mock import patch, MagicMock, AsyncMock
import json
import asyncio

from SentinelFunctionsOrchestrator.soar_connector_async_v2 import (
    get_query_params,
    get_headers,
    compute_url,
    fetch_with_retries,
    get_threats,
    get_cases,
)


class TestGetQueryParams(unittest.TestCase):
    def test_query_params_with_end_time(self):
        # Test case where interval has both start and end times
        filter_param = FilterParam.receivedTime
        interval = OptionalEndTimeRange(
            start=datetime(2024, 10, 1, 12, 0, 0), end=datetime(2024, 10, 1, 13, 0, 0)
        )
        query_params = get_query_params(filter_param, interval)
        expected_filter = (
            "receivedTime gte 2024-10-01T12:00:00Z lte 2024-10-01T13:00:00Z"
        )
        self.assertEqual(query_params, {"filter": expected_filter})

    def test_query_params_without_end_time(self):
        # Test case where interval has only the start time
        filter_param = FilterParam.createdTime
        interval = OptionalEndTimeRange(start=datetime(2024, 10, 1, 12, 0, 0), end=None)
        query_params = get_query_params(filter_param, interval)
        expected_filter = "createdTime gte 2024-10-01T12:00:00Z"
        self.assertEqual(query_params, {"filter": expected_filter})

    def test_empty_filter_param_name(self):
        # Test case where filter_param name is empty
        filter_param = FilterParam.customerVisibleTime
        interval = OptionalEndTimeRange(
            start=datetime(2024, 10, 1, 12, 0, 0), end=datetime(2024, 10, 1, 13, 0, 0)
        )
        query_params = get_query_params(filter_param, interval)
        expected_filter = (
            "customerVisibleTime gte 2024-10-01T12:00:00Z lte 2024-10-01T13:00:00Z"
        )
        self.assertEqual(query_params, {"filter": expected_filter})

    def test_start_and_end_time_are_the_same(self):
        # Test case where interval start and end times are the same
        filter_param = FilterParam.firstObserved
        interval = OptionalEndTimeRange(
            start=datetime(2024, 10, 1, 12, 0, 0), end=datetime(2024, 10, 1, 12, 0, 0)
        )
        query_params = get_query_params(filter_param, interval)
        expected_filter = (
            "firstObserved gte 2024-10-01T12:00:00Z lte 2024-10-01T12:00:00Z"
        )
        self.assertEqual(query_params, {"filter": expected_filter})


class TestGetHeaders(unittest.TestCase):
    def setUp(self):
        # Common data used in multiple test cases
        self.trace_id = UUID("bdb2a127-ed3d-464a-b205-3820ccf6d3f2")
        self.api_token = "exampletoken"
        self.ctx = Context(
            LAG_ON_BACKEND=timedelta(seconds=30),
            OUTAGE_TIME=timedelta(minutes=15),
            FREQUENCY=timedelta(minutes=5),
            LIMIT=timedelta(minutes=6),
            NUM_CONCURRENCY=5,
            MAX_PAGE_NUMBER=100,
            BASE_URL="http://example.com",
            API_TOKEN="exampletoken",
            TIME_RANGE=TimeRange(
                start=datetime(2024, 10, 1, 12, 55), end=datetime(2024, 10, 1, 13, 0)
            ),
            CLIENT_FILTER_TIME_RANGE=TimeRange(
                start=datetime(2024, 10, 1, 12, 54, 30),
                end=datetime(2024, 10, 1, 12, 59, 30),
            ),
            STORED_TIME=datetime(2024, 10, 1, 12, 55),
            CURRENT_TIME=datetime(2024, 10, 1, 13, 0),
            TRACE_ID=self.trace_id,
            PYTHON_VERSION="3.11",
            SINGLE_THREAT_PAGE_SIZE=40
        )

    def test_valid_headers(self):
        # Test case for valid headers
        headers = get_headers(self.ctx)
        expected_headers = {
            "X-Sentinel-Context": "eyJMQUdfT05fQkFDS0VORCI6IDMwLjAsICJPVVRBR0VfVElNRSI6IDkwMC4wLCAiRlJFUVVFTkNZIjogMzAwLjAsICJMSU1JVCI6IDM2MC4wLCAiTlVNX0NPTkNVUlJFTkNZIjogNSwgIk1BWF9QQUdFX05VTUJFUiI6IDEwMCwgIlNJTkdMRV9USFJFQVRfUEFHRV9TSVpFIjogNDAsICJCQVNFX1VSTCI6ICJodHRwOi8vZXhhbXBsZS5jb20iLCAiVElNRV9SQU5HRSI6IHsic3RhcnQiOiAiMjAyNC0xMC0wMVQxMjo1NTowMCIsICJlbmQiOiAiMjAyNC0xMC0wMVQxMzowMDowMCJ9LCAiQ0xJRU5UX0ZJTFRFUl9USU1FX1JBTkdFIjogeyJzdGFydCI6ICIyMDI0LTEwLTAxVDEyOjU0OjMwIiwgImVuZCI6ICIyMDI0LTEwLTAxVDEyOjU5OjMwIn0sICJTVE9SRURfVElNRSI6ICIyMDI0LTEwLTAxVDEyOjU1OjAwIiwgIkNVUlJFTlRfVElNRSI6ICIyMDI0LTEwLTAxVDEzOjAwOjAwIiwgIlRSQUNFX0lEIjogImJkYjJhMTI3LWVkM2QtNDY0YS1iMjA1LTM4MjBjY2Y2ZDNmMiIsICJQWVRIT05fVkVSU0lPTiI6ICIzLjExIn0=",
            "X-Abnormal-Trace-Id": str(self.trace_id),
            "Authorization": f"Bearer {self.api_token}",
            "Soar-Integration-Origin": "AZURE SENTINEL",
            "Azure-Sentinel-Version": "2024-12-24 V2",
        }
        self.maxDiff = None
        self.assertEqual(headers, expected_headers)


class TestComputeUrl(unittest.TestCase):
    def test_compute_url_with_params(self):
        # Test case with query parameters
        base_url = "https://example.com"
        pathname = "/api/resource"
        params = {
            "filter": "customerVisibleTime gte 2024-10-01T12:00:00Z lte 2024-10-01T13:00:00Z",
            "pageNumber": "2",
        }
        result = compute_url(base_url, pathname, params)
        expected = f"{base_url}{pathname}?filter=customerVisibleTime+gte+2024-10-01T12%3A00%3A00Z+lte+2024-10-01T13%3A00%3A00Z&pageNumber=2"
        self.assertEqual(result, expected)

    def test_compute_url_without_params(self):
        # Test case with no query parameters
        base_url = "https://example.com"
        pathname = "/api/resource"
        params = {}
        result = compute_url(base_url, pathname, params)
        expected = f"{base_url}{pathname}"
        self.assertEqual(result, expected)

    def test_compute_url_with_encoded_params(self):
        # Test case with query parameters that need encoding explicitly
        base_url = "https://example.com"
        pathname = "/api/resource"
        params = {
            "filter": "customerVisibleTime gte 2024-10-01T12:00:00Z lte 2024-10-01T13:00:00Z"
        }
        result = compute_url(base_url, pathname, params)
        expected = f"{base_url}{pathname}?filter=customerVisibleTime+gte+2024-10-01T12%3A00%3A00Z+lte+2024-10-01T13%3A00%3A00Z"
        self.assertEqual(result, expected)

    def test_compute_url_with_complex_pathname(self):
        # Test case with a pathname that includes folders and filename
        base_url = "https://example.com"
        pathname = "/api/resource/subresource"
        params = {
            "filter": "customerVisibleTime gte 2024-10-01T12:00:00Z lte 2024-10-01T13:00:00Z",
            "pageNumber": "2",
        }
        result = compute_url(base_url, pathname, params)
        expected = f"{base_url}{pathname}?filter=customerVisibleTime+gte+2024-10-01T12%3A00%3A00Z+lte+2024-10-01T13%3A00%3A00Z&pageNumber=2"
        self.assertEqual(result, expected)

    def test_compute_url_with_port_in_base_url(self):
        # Test case with port in base URL
        base_url = "https://example.com:8080"
        pathname = "/api/resource"
        params = {
            "filter": "customerVisibleTime gte 2024-10-01T12:00:00Z lte 2024-10-01T13:00:00Z",
            "pageNumber": "2",
        }
        result = compute_url(base_url, pathname, params)
        expected = f"{base_url}{pathname}?filter=customerVisibleTime+gte+2024-10-01T12%3A00%3A00Z+lte+2024-10-01T13%3A00%3A00Z&pageNumber=2"
        self.assertEqual(result, expected)


# Tests using pytest and unittest.mock for properly mocking aiohttp

# @pytest.mark.asyncio
# @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
# async def test_fetch_with_retries_success(mock_get):
#     url = "http://test.com/success"
#     headers = {"Authorization": "Bearer token"}
#     response_data = {"key": "value"}

#     mock_response = MagicMock()
#     mock_response.status = 200
#     mock_response.text = AsyncMock(return_value=json.dumps(response_data))
#     mock_get.return_value.__aenter__.return_value = mock_response

#     result = await fetch_with_retries(url, headers=headers)
#     assert result == response_data

# @pytest.mark.asyncio
# @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
# async def test_fetch_with_retries_server_error(mock_get):
#     url = "http://test.com/server-error"

#     mock_response = MagicMock()
#     mock_response.status = 500
#     mock_response.reason = "Server Error"
#     mock_response.request_info = None
#     mock_response.history = None
#     mock_response.headers = None
#     mock_get.return_value.__aenter__.return_value = mock_response

#     with pytest.raises(aiohttp.ClientResponseError):
#         await fetch_with_retries(url)

# @pytest.mark.asyncio
# @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
# async def test_fetch_with_retries_non_retryable_error(mock_get):
#     url = "http://test.com/non-retryable-error"

#     mock_response = MagicMock()
#     mock_response.status = 404
#     mock_response.reason = "Not Found"
#     mock_response.request_info = None
#     mock_response.history = None
#     mock_response.headers = None
#     mock_get.return_value.__aenter__.return_value = mock_response

#     with pytest.raises(aiohttp.ClientError) as exc_info:
#         await fetch_with_retries(url)
#     assert exc_info.value.status == 404

# @pytest.mark.asyncio
# @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
# async def test_fetch_with_retries_eventually_succeeds(mock_get):
#     url = "http://test.com/eventually-succeeds"
#     headers = {"Authorization": "Bearer token"}
#     response_data = {"key": "value"}
#     attempts = 0

#     async def mock_get_function(url, headers=None, timeout=None):
#         nonlocal attempts
#         attempts += 1
#         if attempts < 3:
#             mock_response = MagicMock()
#             mock_response.status = 500
#             mock_response.reason = "Server Error"
#             mock_response.request_info = None
#             mock_response.history = None
#             mock_response.headers = None
#         else:
#             mock_response = MagicMock()
#             mock_response.status = 200
#             mock_response.text = AsyncMock(return_value=json.dumps(response_data))

#         return MagicMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock())

#     mock_get.side_effect = mock_get_function

#     result = await fetch_with_retries(url, headers=headers, retries=3, backoff=0.01)
#     assert result == response_data
#     assert attempts == 3


@pytest.mark.asyncio
@patch(
    "SentinelFunctionsOrchestrator.soar_connector_async_v2.fetch_with_retries",
    new_callable=AsyncMock,
)
async def test_get_threats(mock_fetch: AsyncMock):
    mock_intervals = [
        MagicMock(start="2024-10-01T13:00:00Z", end=None),
    ]

    mock_threat_campaign_response = {
        "total": 1,
        "threats": [{"threatId": "threat1"}],
        "nextPageNumber": None,
    }

    mock_single_threat_response = {
        "messages": [
            {"abxMessageId": "message1", "remediationTimestamp": "2024-10-01T12:30:00Z"}
        ]
    }

    # Mock the context and output queue
    ctx = MagicMock()
    ctx.BASE_URL = "http://example.com"
    ctx.MAX_PAGE_NUMBER = 10
    ctx.NUM_CONCURRENCY = 2
    ctx.CLIENT_FILTER_TIME_RANGE.start = try_str_to_datetime("2024-10-01T12:00:00Z")
    ctx.CLIENT_FILTER_TIME_RANGE.end = try_str_to_datetime("2024-10-01T13:00:00Z")
    ctx.SINGLE_THREAT_PAGE_SIZE = 40

    output_queue = asyncio.Queue()

    # Mock the functions and methods used in get_threats
    mock_fetch.side_effect = [
        mock_threat_campaign_response,
        mock_single_threat_response,
    ]

    with patch(
        "SentinelFunctionsOrchestrator.soar_connector_async_v2.compute_intervals",
        return_value=mock_intervals,
    ):
        with patch(
            "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_query_params"
        ) as mock_get_query_params:
            with patch(
                "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_headers",
                return_value={"Authorization": "Bearer token"},
            ):
                await get_threats(ctx, output_queue)

    # Ensure fetch_with_retries was called with expected values
    mock_fetch.assert_any_call(url='http://example.com/v1/threats', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/threats/threat1?pageSize=40&pageNumber=1', headers={'Authorization': 'Bearer token'})
    assert mock_fetch.call_count == 2

    # Ensure the messages were put into the output queue
    assert output_queue.qsize() == 1

    # Validate the content of the output queue
    output_message = await output_queue.get()
    expected_record = (
        "ABNORMAL_THREAT_MESSAGES",
        {"abxMessageId": "message1", "remediationTimestamp": "2024-10-01T12:30:00Z"},
    )
    assert output_message == expected_record
    assert output_queue.empty()


@pytest.mark.asyncio
@patch(
    "SentinelFunctionsOrchestrator.soar_connector_async_v2.fetch_with_retries",
    new_callable=AsyncMock,
)
async def test_get_cases(mock_fetch):
    # Mock the context and output queue
    ctx = MagicMock()
    ctx.BASE_URL = "http://example.com"
    ctx.MAX_PAGE_NUMBER = 10
    ctx.NUM_CONCURRENCY = 2
    ctx.CLIENT_FILTER_TIME_RANGE.start = try_str_to_datetime("2024-10-01T12:00:00Z")
    ctx.CLIENT_FILTER_TIME_RANGE.end = try_str_to_datetime("2024-10-01T13:00:00Z")
    ctx.SINGLE_THREAT_PAGE_SIZE = 40

    output_queue = asyncio.Queue()

    mock_intervals = [
        MagicMock(start="2024-10-01T13:00:00Z", end=None),
    ]

    mock_cases_response = {
        "total": 1,
        "cases": [{"caseId": "case1"}],
        "nextPageNumber": None,
    }

    mock_single_case_response = {
        "caseId": "case1",
        "customerVisibleTime": "2024-10-01T12:30:00Z",
    }

    # Mock the functions and methods used in get_cases
    mock_fetch.side_effect = [mock_cases_response, mock_single_case_response]

    with patch(
        "SentinelFunctionsOrchestrator.soar_connector_async_v2.compute_intervals",
        return_value=mock_intervals,
    ):
        with patch(
            "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_query_params"
        ) as mock_get_query_params:
            with patch(
                "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_headers",
                return_value={"Authorization": "Bearer token"},
            ):
                await get_cases(ctx, output_queue)

    # Ensure fetch_with_retries was called with expected values
    mock_fetch.assert_any_call(url='http://example.com/v1/cases', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/cases/case1', headers={'Authorization': 'Bearer token'})
    assert mock_fetch.call_count == 2

    # Ensure the cases were put into the output queue
    assert output_queue.qsize() == 1

    # Validate the content of the output queue
    output_message = await output_queue.get()
    expected_record = (
        "ABNORMAL_CASES",
        {"caseId": "case1", "customerVisibleTime": "2024-10-01T12:30:00Z"},
    )
    assert output_message == expected_record


@pytest.mark.asyncio
@patch(
    "SentinelFunctionsOrchestrator.soar_connector_async_v2.fetch_with_retries",
    new_callable=AsyncMock,
)
async def test_get_threats_paginated(mock_fetch: AsyncMock):
    mock_intervals = [
        MagicMock(start="2024-10-01T13:00:00Z", end=None),
    ]

    mock_threat_campaign_response = {
        "total": 1,
        "threats": [{"threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc95"}],
        "nextPageNumber": None,
    }

    mock_single_threat_response_1 = {
        "threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc95",
        "messages": [
            {
                "abxMessageId": 8340091768378090492,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": -7487512360242110741,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": -1453682119958233571,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": -2738917250488486006,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": 482233753373918965,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": 9119659315270197918,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": 3546172484236699227,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            }
        ],
        "pageNumber": 1,
        "total": 16,
        "nextPageNumber": 2
    }
    mock_single_threat_response_2 = {
        "threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc95",
        "messages": [
            {
                "abxMessageId": -68647174525282065,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": 1025490956646620319,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": 8353208793487178298,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": -7300418853454868601,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": -559214588526485457,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": 4447975809254795357,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": -374721447240777722,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            }
        ],
        "pageNumber": 2,
        "total": 16,
        "nextPageNumber": 3
    }
    mock_single_threat_response_3 = {
        "threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc95",
        "messages": [
            {
                "abxMessageId": 3333927803157276490,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": -1777029380775902847,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            }
        ],
        "pageNumber": 3,
        "total": 16
    }
    # Mock the context and output queue
    ctx = MagicMock()
    ctx.BASE_URL = "http://example.com"
    ctx.MAX_PAGE_NUMBER = 10
    ctx.NUM_CONCURRENCY = 2
    ctx.CLIENT_FILTER_TIME_RANGE.start = try_str_to_datetime("2024-10-01T12:00:00Z")
    ctx.CLIENT_FILTER_TIME_RANGE.end = try_str_to_datetime("2024-10-01T13:00:00Z")
    ctx.SINGLE_THREAT_PAGE_SIZE = 7

    output_queue = asyncio.Queue()

    # Mock the functions and methods used in get_threats
    mock_fetch.side_effect = [
        mock_threat_campaign_response,
        mock_single_threat_response_1,
        mock_single_threat_response_2,
        mock_single_threat_response_3,
    ]

    with patch(
        "SentinelFunctionsOrchestrator.soar_connector_async_v2.compute_intervals",
        return_value=mock_intervals,
    ):
        with patch(
            "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_query_params"
        ) as mock_get_query_params:
            with patch(
                "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_headers",
                return_value={"Authorization": "Bearer token"},
            ):
                await get_threats(ctx, output_queue)

    # Ensure fetch_with_retries was called with expected values
    mock_fetch.assert_any_call(url='http://example.com/v1/threats', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/threats/abca34c0-04fc-222d-30f6-9e62e51dfc95?pageSize=7&pageNumber=1', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/threats/abca34c0-04fc-222d-30f6-9e62e51dfc95?pageSize=7&pageNumber=2', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/threats/abca34c0-04fc-222d-30f6-9e62e51dfc95?pageSize=7&pageNumber=3', headers={'Authorization': 'Bearer token'})
    assert mock_fetch.call_count == 4

    # Ensure the messages were put into the output queue
    assert output_queue.qsize() == 16

    # Validate the content of the output queue

    expected_records = [
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 8340091768378090492, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -7487512360242110741, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -1453682119958233571, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -2738917250488486006, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 482233753373918965, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 9119659315270197918, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 3546172484236699227, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -68647174525282065, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 1025490956646620319, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 8353208793487178298, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -7300418853454868601, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -559214588526485457, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 4447975809254795357, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -374721447240777722, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 3333927803157276490, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -1777029380775902847, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
    ]

    actual_records = []

    while not output_queue.empty():
        output_message = await output_queue.get()
        actual_records.append(output_message)

    assert sorted(map(lambda x: str(x), expected_records)) == sorted(map(lambda x: str(x), actual_records))
    assert len(expected_records) == len(actual_records)
    assert output_queue.empty()





@pytest.mark.asyncio
@patch(
    "SentinelFunctionsOrchestrator.soar_connector_async_v2.fetch_with_retries",
    new_callable=AsyncMock,
)
async def test_get_threats_paginated_early_exit(mock_fetch: AsyncMock):
    mock_intervals = [
        MagicMock(start="2024-10-01T13:00:00Z", end=None),
    ]

    mock_threat_campaign_response = {
        "total": 1,
        "threats": [{"threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc88"}],
        "nextPageNumber": None,
    }

    mock_single_threat_response_1 = {
        "threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc88",
        "messages": [
            {
                "abxMessageId": 8340091768378090492,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": -7487512360242110741,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": -1453682119958233571,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": -2738917250488486006,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": 482233753373918965,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": 9119659315270197918,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            },
            {
                "abxMessageId": 3546172484236699227,
                "remediationTimestamp": "2024-10-01T12:30:40Z"
            }
        ],
        "pageNumber": 1,
        "total": 16,
        "nextPageNumber": 2
    }
    mock_single_threat_response_2 = {
        "threatId": "abca34c0-04fc-222d-30f6-9e62e51dfc88",
        "messages": [
            {
                "abxMessageId": -68647174525282065,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": 1025490956646620319,
                "remediationTimestamp": "2024-10-01T12:30:40Z",
            },
            {
                "abxMessageId": 8353208793487178298,
                "remediationTimestamp": "2024-10-01T11:59:40Z",
            },
            {
                "abxMessageId": -7300418853454868601,
                "remediationTimestamp": "2024-10-01T11:59:40Z",
            },
            {
                "abxMessageId": -559214588526485457,
                "remediationTimestamp": "2024-10-01T11:59:40Z",
            },
            {
                "abxMessageId": 4447975809254795357,
                "remediationTimestamp": "2024-10-01T11:59:40Z",
            },
            {
                "abxMessageId": -374721447240777722,
                "remediationTimestamp": "2024-10-01T11:59:40Z",
            }
        ],
        "pageNumber": 2,
        "total": 16,
        "nextPageNumber": 3
    }
    
    # Mock the context and output queue
    ctx = MagicMock()
    ctx.BASE_URL = "http://example.com"
    ctx.MAX_PAGE_NUMBER = 10
    ctx.NUM_CONCURRENCY = 2
    ctx.CLIENT_FILTER_TIME_RANGE.start = try_str_to_datetime("2024-10-01T12:00:00Z")
    ctx.CLIENT_FILTER_TIME_RANGE.end = try_str_to_datetime("2024-10-01T13:00:00Z")
    ctx.SINGLE_THREAT_PAGE_SIZE = 7

    output_queue = asyncio.Queue()

    # Mock the functions and methods used in get_threats
    mock_fetch.side_effect = [
        mock_threat_campaign_response,
        mock_single_threat_response_1,
        mock_single_threat_response_2,
    ]

    with patch(
        "SentinelFunctionsOrchestrator.soar_connector_async_v2.compute_intervals",
        return_value=mock_intervals,
    ):
        with patch(
            "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_query_params"
        ) as mock_get_query_params:
            with patch(
                "SentinelFunctionsOrchestrator.soar_connector_async_v2.get_headers",
                return_value={"Authorization": "Bearer token"},
            ):
                await get_threats(ctx, output_queue)

    # Ensure fetch_with_retries was called with expected values
    mock_fetch.assert_any_call(url='http://example.com/v1/threats', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/threats/abca34c0-04fc-222d-30f6-9e62e51dfc88?pageSize=7&pageNumber=1', headers={'Authorization': 'Bearer token'})
    mock_fetch.assert_any_call(url='http://example.com/v1/threats/abca34c0-04fc-222d-30f6-9e62e51dfc88?pageSize=7&pageNumber=2', headers={'Authorization': 'Bearer token'})
    assert mock_fetch.call_count == 3

    # Ensure the messages were put into the output queue
    assert output_queue.qsize() == 9

    # Validate the content of the output queue

    expected_records = [
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 8340091768378090492, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -7487512360242110741, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -1453682119958233571, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -2738917250488486006, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 482233753373918965, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 9119659315270197918, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 3546172484236699227, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": -68647174525282065, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
        ("ABNORMAL_THREAT_MESSAGES", {"abxMessageId": 1025490956646620319, "remediationTimestamp": "2024-10-01T12:30:40Z"}),
    ]

    actual_records = []

    while not output_queue.empty():
        output_message = await output_queue.get()
        actual_records.append(output_message)

    assert sorted(map(lambda x: str(x), expected_records)) == sorted(map(lambda x: str(x), actual_records))
    assert len(expected_records) == len(actual_records)
    assert output_queue.empty()





if __name__ == "__main__":
    unittest.main()
    pytest.main()
