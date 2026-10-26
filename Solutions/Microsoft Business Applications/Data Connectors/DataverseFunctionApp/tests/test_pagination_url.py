import unittest

import requests

from dataverse_client import get_all_data


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requested_urls = []

    def get(self, url, timeout):
        self.requested_urls.append((url, timeout))
        return FakeResponse(next(self.responses))


class DataversePaginationUrlTests(unittest.TestCase):
    def test_requests_preserves_encoded_skiptoken(self):
        next_link = (
            "https://example.crm.dynamics.com/api/data/v9.2/systemusers"
            "?$skiptoken=%3Ccookie%20pagenumber=%222%22%20"
            "pagingcookie=%22%253ccookie%2520page%253d%25221%2522%253e%22"
            "%20istracking=%22False%22%20/%3E"
        )

        prepared_url = requests.Request("GET", next_link).prepare().url

        self.assertEqual(prepared_url, next_link)
        self.assertIn("%3Ccookie", prepared_url)
        self.assertNotIn("%253Ccookie", prepared_url)

    def test_pagination_uses_next_link_without_modification(self):
        next_link = (
            "https://example.crm.dynamics.com/api/data/v9.2/systemusers"
            "?$skiptoken=%3Ccookie%20pagenumber=%222%22%20/%3E"
        )
        client = FakeSession(
            [
                {"value": [{"page": 1}], "@odata.nextLink": next_link},
                {"value": [{"page": 2}]},
            ]
        )

        pages = list(get_all_data(client, "https://example/first", timeout=30))

        self.assertEqual(pages, [[{"page": 1}], [{"page": 2}]])
        self.assertEqual(client.requested_urls[1], (next_link, 30))


if __name__ == "__main__":
    unittest.main()
