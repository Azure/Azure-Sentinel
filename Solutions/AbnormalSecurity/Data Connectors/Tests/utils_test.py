import unittest
from datetime import datetime, timedelta
from SentinelFunctionsOrchestrator.utils import (
    TIME_FORMAT_WITHMS,
    TIME_FORMAT,
    try_str_to_datetime,
    TimeRange,
    OptionalEndTimeRange,
    compute_intervals,
    Context,
)
from pydantic import ValidationError
from uuid import uuid4
import random 


class TestTryStrToDateTime(unittest.TestCase):
    def test_format_without_ms(self):
        # Test case for format without milliseconds
        time_str = "2024-10-01T12:34:56Z"
        expected = datetime.strptime(time_str, TIME_FORMAT)
        result = try_str_to_datetime(time_str)
        self.assertEqual(result, expected)

    def test_format_with_ms(self):
        # Test case for format with milliseconds
        time_str = "2024-10-01T12:34:56.123456Z"
        expected = datetime.strptime(time_str, TIME_FORMAT_WITHMS)
        result = try_str_to_datetime(time_str)
        self.assertEqual(result, expected)
    
    def test_format_with_ns(self):
        # Test case for format with milliseconds
        time_str_ns = "2024-10-01T12:34:56.123456789Z"
        time_str_ms = "2024-10-01T12:34:56.123456Z"
        expected = datetime.strptime(time_str_ms, TIME_FORMAT_WITHMS)
        result = try_str_to_datetime(time_str_ns)
        self.assertEqual(result, expected)

    def test_format_with_ns_2(self):
        # Test case for format with milliseconds
        time_str_ns = "2024-10-01T12:34:56.12345678913Z"
        result = try_str_to_datetime(time_str_ns)
        self.assertIsNotNone(result)
    
    def test_format_with_ns_3(self):
        # Test case for format with milliseconds
        f = ""
        for i in range(100):
            f +=  random.choice("1234567890")
            time_str_ns = f"2024-10-01T12:34:56.{f}Z"
            result = try_str_to_datetime(time_str_ns)
            self.assertIsNotNone(result)

    def test_invalid_format(self):
        # Test case for invalid format
        time_str = "2024-10-01 12:34:56"
        with self.assertRaises(ValueError):
            try_str_to_datetime(time_str)

    def test_incomplete_date(self):
        # Test case for incomplete date
        time_str = "2024-10-01T12:34"
        with self.assertRaises(ValueError):
            try_str_to_datetime(time_str)

    def test_empty_string(self):
        # Test case for empty string
        time_str = ""
        with self.assertRaises(ValueError):
            try_str_to_datetime(time_str)


class TestTimeRange(unittest.TestCase):
    def test_valid_timerange(self):
        # Test case where start is before end
        start = datetime(2024, 10, 1, 12, 0)
        end = datetime(2024, 10, 1, 13, 0)
        time_range = TimeRange(start=start, end=end)
        self.assertEqual(time_range.start, start)
        self.assertEqual(time_range.end, end)

    def test_invalid_timerange(self):
        # Test case where start is after end
        start = datetime(2024, 10, 1, 14, 0)
        end = datetime(2024, 10, 1, 13, 0)
        with self.assertRaises(ValidationError) as context:
            TimeRange(start=start, end=end)
        self.assertIn("Start time", str(context.exception))

    def test_start_equal_to_end(self):
        # Test case where start is equal to end
        start = end = datetime(2024, 10, 1, 12, 0)
        time_range = TimeRange(start=start, end=end)
        self.assertEqual(time_range.start, start)
        self.assertEqual(time_range.end, end)

    def test_missing_start(self):
        # Test case where start is missing
        end = datetime(2024, 10, 1, 13, 0)
        with self.assertRaises(ValidationError):
            TimeRange(end=end)

    def test_missing_end(self):
        # Test case where end is missing
        start = datetime(2024, 10, 1, 12, 0)
        with self.assertRaises(ValidationError):
            TimeRange(start=start)


class TestOptionalEndTimeRange(unittest.TestCase):
    def test_valid_timerange_with_end(self):
        # Test case where start is before end
        start = datetime(2024, 10, 1, 12, 0)
        end = datetime(2024, 10, 1, 13, 0)
        time_range = OptionalEndTimeRange(start=start, end=end)
        self.assertEqual(time_range.start, start)
        self.assertEqual(time_range.end, end)

    def test_valid_timerange_without_end(self):
        # Test case where end is None
        start = datetime(2024, 10, 1, 12, 0)
        time_range = OptionalEndTimeRange(start=start, end=None)
        self.assertEqual(time_range.start, start)
        self.assertIsNone(time_range.end)

    def test_invalid_timerange(self):
        # Test case where start is after end
        start = datetime(2024, 10, 1, 14, 0)
        end = datetime(2024, 10, 1, 13, 0)
        with self.assertRaises(ValidationError) as context:
            OptionalEndTimeRange(start=start, end=end)
        self.assertIn("Start time", str(context.exception))

    def test_start_equal_to_end(self):
        # Test case where start is equal to end
        start = end = datetime(2024, 10, 1, 12, 0)
        time_range = OptionalEndTimeRange(start=start, end=end)
        self.assertEqual(time_range.start, start)
        self.assertEqual(time_range.end, end)

    def test_missing_start(self):
        # Test case where start is missing
        end = datetime(2024, 10, 1, 13, 0)
        with self.assertRaises(ValidationError):
            OptionalEndTimeRange(end=end)


class TestComputeIntervals(unittest.TestCase):
    def setUp(self):
        # Common data used in multiple test cases
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
            TRACE_ID=uuid4(),
            PYTHON_VERSION="3.11",
            SINGLE_THREAT_PAGE_SIZE=40
        )

    def test_valid_intervals(self):
        # Test case for valid intervals
        intervals = compute_intervals(self.ctx)
        expected_intervals = [
            OptionalEndTimeRange(start=datetime(2024, 10, 1, 12, 54, 30), end=None)
        ]
        self.assertEqual(intervals, expected_intervals)

    def test_valid_intervals_2(self):
        # Test case for valid intervals
        self.ctx.TIME_RANGE = TimeRange(
            start=datetime(2024, 10, 1, 12, 54), end=datetime(2024, 10, 1, 13, 0)
        )
        intervals = compute_intervals(self.ctx)
        expected_intervals = [
            OptionalEndTimeRange(
                start=datetime(2024, 10, 1, 12, 53, 30),
                end=datetime(2024, 10, 1, 12, 58, 30),
            ),
            OptionalEndTimeRange(start=datetime(2024, 10, 1, 12, 58, 30), end=None),
        ]
        self.assertEqual(intervals, expected_intervals)

    def test_valid_intervals_3(self):
        # Test case for valid intervals
        self.ctx.TIME_RANGE = TimeRange(
            start=datetime(2024, 10, 1, 12, 0), end=datetime(2024, 10, 1, 13, 0)
        )
        intervals = compute_intervals(self.ctx)
        expected_intervals = [
            OptionalEndTimeRange(
                start=datetime(2024, 10, 1, 12, 44, 30),
                end=datetime(2024, 10, 1, 12, 49, 30),
            ),
            OptionalEndTimeRange(
                start=datetime(2024, 10, 1, 12, 49, 30),
                end=datetime(2024, 10, 1, 12, 54, 30),
            ),
            OptionalEndTimeRange(start=datetime(2024, 10, 1, 12, 54, 30), end=None),
        ]
        self.assertEqual(intervals, expected_intervals)

    def test_frequency_greater_than_limit(self):
        # Test case where frequency is greater than limit
        self.ctx.FREQUENCY = timedelta(hours=3)
        with self.assertRaises(AssertionError):
            compute_intervals(self.ctx)


if __name__ == "__main__":
    unittest.main()
