#!/usr/bin/env python3

"""
test_helios.py

This script contains unit tests for the Helios module. It tests the functionality of the following functions:
- create_headers
- get_alerts_details
- get_alert_details
- get_alerts
- get_recoveries

The script utilizes the unittest framework and the unittest.mock module for mocking external dependencies like the requests library.
"""

import unittest
import os
import json
from unittest.mock import patch, Mock
from helios import *


class TestHelios(unittest.TestCase):
    @patch("helios.requests.get")
    def test_create_headers(self, mock_requests_get):
        api_key = "12345"
        headers = create_headers(api_key)
        expected_headers = {
            "Content-Type": "application/json",
            "authority": "helios.cohesity.com",
            "apiKey": api_key,
        }
        self.assertEqual(headers, expected_headers)

    @patch("helios.requests.get")
    def test_get_alerts_details(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = {"alert_details": "test"}
        mock_requests_get.return_value = mock_response
        api_key = "12345"
        alert_ids = ["1", "2", "3"]
        result = get_alerts_details(alert_ids, api_key)
        expected_result = {"alert_details": "test"}
        self.assertEqual(result, expected_result)

    @patch("helios.requests.get")
    def test_get_alert_details(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"alert_id": "1", "alert_details": "test"}
        ]
        mock_requests_get.return_value = mock_response
        api_key = "12345"
        alert_id = "1"
        result = get_alert_details(alert_id, api_key)
        expected_result = {"alert_id": "1", "alert_details": "test"}
        self.assertEqual(result, expected_result)

    @patch("helios.requests.get")
    def test_get_alerts(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ]
        mock_requests_get.return_value = mock_response
        api_key = "12345"
        start_days_ago = 7
        end_days_ago = 0
        result = get_alerts(api_key, start_days_ago, end_days_ago)
        expected_result = ["1", "2", "3"]
        self.assertEqual(result, expected_result)

    @patch("helios.requests.get")
    def test_get_recoveries(self, mock_requests_get):
        with open("./Data/recoveries.json") as f:
            json_str = json.load(f)
        mock_response = Mock()
        mock_response.json.return_value = json_str
        mock_requests_get.return_value = mock_response
        cluster_id = "12345"
        api_key = "67890"
        result = get_recoveries(cluster_id, api_key)
        expected_result = json_str
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    unittest.main()
