"""
Unit tests for pagination termination, whois param serialization,
and upload batching — the paths called out in PR review.
"""
import json
import sys
from unittest.mock import MagicMock, patch

# Stub Azure SDKs so tests run without the full azure packages installed.
for mod in (
    "azure",
    "azure.core",
    "azure.core.exceptions",
    "azure.monitor",
    "azure.monitor.ingestion",
    "azure.identity",
    "azure.storage",
    "azure.storage.blob",
):
    sys.modules.setdefault(mod, MagicMock())

from models.feed import FeedConfig
from services.sentinel import SentinelIngestionService
from services.whoisfreaks import WhoisFreaksClient
from utils.csv_parser import parse_domain_list


def test_domain_list_raw_count_keeps_full_page_from_looking_short():
    # Simulate a 10k-line page with one header + one garbage line filtered out.
    lines = ["domain_name"] + [f"example{i}.com" for i in range(9998)] + ["not a domain"]
    text = "\n".join(lines)
    records, raw = parse_domain_list(text)
    assert raw == 10000
    assert len(records) == 9998
    # Processor must use raw (10000), not len(records), for last-page check.
    page_size = 10000
    assert raw >= page_size  # not treated as last page


def test_whois_param_is_lowercase_string():
    client = WhoisFreaksClient(api_key="test-key")
    feed = FeedConfig(
        name="nrd_gtld_with_whois",
        endpoint="https://example.invalid/feed",
        stream_name="Custom-Test",
        table_name="Test_CL",
        page_size=100,
        status_section="newly",
        status_name="nrd_gtld_with_whois",
        date_parameter="date",
        status_api_version="v3.3",
    )

    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured["params"] = params
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"Content-Type": "text/csv"}
        resp.text = "num,domain_name,query_time,create_date,update_date,expiry_date\n"
        resp.raise_for_status = MagicMock()
        return resp

    with patch.object(client.session, "get", side_effect=fake_get):
        records, raw = client.fetch_page(feed=feed, feed_date="2026-01-01", offset=0)

    assert captured["params"]["whois"] == "true"
    assert isinstance(captured["params"]["whois"], str)


def test_upload_chunks_when_payload_exceeds_limit():
    # Build records large enough that two of them exceed 900 KB when serialized.
    big_value = "x" * 500_000
    records = [
        {"domain": "a.example", "payload": big_value},
        {"domain": "b.example", "payload": big_value},
        {"domain": "c.example", "payload": "small"},
    ]

    # Bypass __init__ (would need real Azure credential)
    service = object.__new__(SentinelIngestionService)
    batches = SentinelIngestionService._chunk_by_bytes(records)
    assert len(batches) >= 2
    assert sum(len(b) for b in batches) == 3

    # Each batch JSON must stay under the soft 1 MB limit.
    for batch in batches:
        size = len(json.dumps(batch, separators=(",", ":")).encode("utf-8"))
        assert size < 1_000_000
