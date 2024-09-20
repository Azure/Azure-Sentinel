from typing import Iterable
from urllib.parse import quote

from feedly.api_client.session import FeedlySession


class FeedlyDownloader:
    def __init__(self, api_key: str):
        self.session = FeedlySession(api_key, client_name="feedly.ms_sentinel.client")

    def download(self, stream_id: str, *, newer_than_s: float, older_than_s: float) -> Iterable[dict]:
        params = {
            "newerThan": int(newer_than_s * 1000),
            "continuation": int(older_than_s * 1000),
            "count": 250,
            "streamId": quote(stream_id),
        }
        while True:
            response = self.session.do_api_request("/v3/streams/contents", "GET", params)
            yield from response.get("items", [])
            if "continuation" not in response:
                break
            params["continuation"] = response["continuation"]
