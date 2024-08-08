from itertools import zip_longest

import responses
from responses import matchers
from connections.zerofox import ZeroFoxClient

USER = "user"
TOKEN = "token"
ENDPOINT = "dummy-endpoint/"
CTI_TOKEN = "cti_token"
SECOND_PAGE_URL = "https://second_page"
URL = "https://api.zerofox.com"


class TestZeroFoxCTI():
    @responses.activate
    def test_cti_generator_is_provided(self):
        zf_client = ZeroFoxClient(user=USER, token=TOKEN)
        self.build_cti_responses()

        output = zf_client.cti_request(method="GET", url_suffix=ENDPOINT)
        expected = (dict(index=f"r{i}") for i in range(4))
        all_match = all(a == b for a, b in zip_longest(output, expected))
        assert all_match

    def build_cti_responses(self):
        """Prepare mock responses for queries through the requests package."""
        responses.post(
            url=f"{URL}/auth/token/",
            match=[matchers.urlencoded_params_matcher(
                dict(username=USER, password=TOKEN))
            ],
            json=dict(access=CTI_TOKEN),
        )

        cti_header = {
            "Authorization": f"Bearer {CTI_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        endpoint_first_page_json = dict(
            next=SECOND_PAGE_URL, results=[
                dict(index=f"r{i}") for i in range(2)]
        )
        responses.get(
            url=f"{URL}/cti/{ENDPOINT}", headers=cti_header,
            json=endpoint_first_page_json
        )

        endpoint_second_page_json = dict(
            next=None, results=[dict(index=f"r{i}") for i in range(2, 4)]
        )
        responses.get(
            url=SECOND_PAGE_URL, headers=cti_header,
            json=endpoint_second_page_json
        )
