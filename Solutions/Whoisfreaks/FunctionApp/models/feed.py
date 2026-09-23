from dataclasses import dataclass


@dataclass(frozen=True)
class FeedConfig:
    name: str
    endpoint: str
    stream_name: str
    table_name: str
    page_size: int = 5000
    date_parameter: str = "date"
    status_section: str = "threat_feed"
    status_name: str | None = None
    # Which WhoisFreaks status document (keyed by API version) contains
    # this feed's status_section/status_name path. Threat feeds (malware,
    # phishing, spam) are served from v3.4 and their status lives in the
    # v3.4 status document; NRD feeds are served from v3.3 and their
    # "newly" section lives in the v3.3 status document. The two status
    # documents are fetched separately and cached per invocation (see
    # services/whoisfreaks.py / services/processor.py) so a feed is never
    # looked up in the wrong status payload.
    status_api_version: str = "v3.4"

    def checkpoint_blob_name(self) -> str:
        return f"{self.name}.json"
