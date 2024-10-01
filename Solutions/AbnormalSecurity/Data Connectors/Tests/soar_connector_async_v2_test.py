import os

os.environ["ABNORMAL_SECURITY_REST_API_TOKEN"] = "123"

import unittest
from SentinelFunctionsOrchestrator.utils import (
    FilterParam,
    OptionalEndTimeRange,
    Context,
    TimeRange,
)
from datetime import datetime, timedelta
from uuid import UUID
import pytest
import aiohttp
from aiohttp import web
from unittest.mock import patch, MagicMock, AsyncMock
import json

from SentinelFunctionsOrchestrator.soar_connector_async_v2 import (
    get_query_params,
    get_headers,
    compute_url,
    fetch_with_retries,
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
        )

    def test_valid_headers(self):
        # Test case for valid headers
        headers = get_headers(self.ctx)
        expected_headers = {
            "X-Sentinel-Context": "eyJMQUdfT05fQkFDS0VORCI6IlBUMzBTIiwiT1VUQUdFX1RJTUUiOiJQVDE1TSIsIkZSRVFVRU5DWSI6IlBUNU0iLCJMSU1JVCI6IlBUNk0iLCJOVU1fQ09OQ1VSUkVOQ1kiOjUsIk1BWF9QQUdFX05VTUJFUiI6MTAwLCJCQVNFX1VSTCI6Imh0dHA6Ly9leGFtcGxlLmNvbSIsIlRJTUVfUkFOR0UiOnsic3RhcnQiOiIyMDI0LTEwLTAxVDEyOjU1OjAwIiwiZW5kIjoiMjAyNC0xMC0wMVQxMzowMDowMCJ9LCJDTElFTlRfRklMVEVSX1RJTUVfUkFOR0UiOnsic3RhcnQiOiIyMDI0LTEwLTAxVDEyOjU0OjMwIiwiZW5kIjoiMjAyNC0xMC0wMVQxMjo1OTozMCJ9LCJTVE9SRURfVElNRSI6IjIwMjQtMTAtMDFUMTI6NTU6MDAiLCJDVVJSRU5UX1RJTUUiOiIyMDI0LTEwLTAxVDEzOjAwOjAwIiwiVFJBQ0VfSUQiOiJiZGIyYTEyNy1lZDNkLTQ2NGEtYjIwNS0zODIwY2NmNmQzZjIifQ==",
            "X-Abnormal-Trace-Id": str(self.trace_id),
            "Authorization": f"Bearer {self.api_token}",
            "Soar-Integration-Origin": "AZURE SENTINEL",
            "Azure-Sentinel-Version": "2024-09-30 V2",
        }
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

if __name__ == "__main__":
    unittest.main()
    pytest.main()
