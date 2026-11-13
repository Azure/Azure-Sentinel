import json
from pathlib import Path
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import requests

from dataverse_client import get_all_data


def json_response(body, status_code=200):
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode("utf-8")
    return response


class DataversePaginationUrlTests(unittest.TestCase):
    def setUp(self):
        self.client = requests.Session()
        self.client.trust_env = False
        self.addCleanup(self.client.close)
        self.first_url = "https://example.crm.dynamics.com/api/data/v9.2/systemusers"
        self.next_link = (
            self.first_url
            + "?$skiptoken=%3Ccookie%20pagenumber=%222%22%20"
            "pagingcookie=%22%253ccookie%2520page%253d%25221%2522%253e%22"
            "%20istracking=%22False%22%20/%3E"
        )

    def test_requests_preserves_encoded_skiptoken(self):
        prepared_url = self.client.prepare_request(
            requests.Request("GET", self.next_link)
        ).url

        self.assertEqual(prepared_url, self.next_link)
        self.assertIn("%3Ccookie", prepared_url)
        self.assertNotIn("%253Ccookie", prepared_url)

    def test_pagination_preserves_next_links_across_empty_page(self):
        third_link = self.next_link.replace("pagenumber=%222%22", "pagenumber=%223%22")
        self.client.headers["Authorization"] = "Bearer test-token"
        responses = [
            json_response({"value": [{"page": 1}], "@odata.nextLink": self.next_link}),
            json_response({"value": [], "@odata.nextLink": third_link}),
            json_response({"value": [{"page": 3}]}),
        ]

        with patch.object(self.client, "send", side_effect=responses) as send:
            pages = list(get_all_data(self.client, self.first_url, timeout=30))

        self.assertEqual(pages, [[{"page": 1}], [{"page": 3}]])
        self.assertEqual(
            [call.args[0].url for call in send.call_args_list],
            [self.first_url, self.next_link, third_link],
        )
        for call in send.call_args_list:
            self.assertEqual(call.kwargs["timeout"], 30)
            self.assertEqual(call.args[0].headers["Authorization"], "Bearer test-token")

    def test_empty_final_page_ends_pagination(self):
        with patch.object(
            self.client, "send", return_value=json_response({"value": []})
        ) as send:
            pages = list(get_all_data(self.client, self.first_url, timeout=30))

        self.assertEqual(pages, [])
        self.assertEqual(send.call_count, 1)

    def test_http_failure_on_later_page_is_not_silently_truncated(self):
        responses = [
            json_response({"value": [{"page": 1}], "@odata.nextLink": self.next_link}),
            json_response({"error": "Service unavailable"}, status_code=503),
        ]

        with patch.object(self.client, "send", side_effect=responses):
            pages = get_all_data(self.client, self.first_url, timeout=30)
            self.assertEqual(next(pages), [{"page": 1}])
            with self.assertLogs(level="ERROR"), self.assertRaises(requests.HTTPError):
                next(pages)

    def test_timeout_on_later_page_is_not_silently_truncated(self):
        responses = [
            json_response({"value": [{"page": 1}], "@odata.nextLink": self.next_link}),
            requests.Timeout("Continuation request timed out"),
        ]

        with patch.object(self.client, "send", side_effect=responses):
            pages = get_all_data(self.client, self.first_url, timeout=30)
            self.assertEqual(next(pages), [{"page": 1}])
            with self.assertLogs(level="ERROR"), self.assertRaises(requests.Timeout):
                next(pages)

    def test_deployment_zip_matches_checked_in_sources(self):
        source_dir = Path(__file__).resolve().parents[1]
        with ZipFile(source_dir / "dataversefunction110.zip") as archive:
            for name in (
                "function_app.py",
                "dataverse_client.py",
                "requirements.txt",
                "host.json",
            ):
                with self.subTest(name=name):
                    self.assertEqual(
                        archive.read(name).replace(b"\r\n", b"\n"),
                        (source_dir / name).read_bytes().replace(b"\r\n", b"\n"),
                    )


if __name__ == "__main__":
    unittest.main()
