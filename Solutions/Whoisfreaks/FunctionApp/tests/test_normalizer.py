from services.normalizer import (
    normalize_feed_record,
    normalize_nrd_with_whois_record,
    normalize_nrd_without_whois_record,
)

def test_malware_normalizer():
    r = normalize_feed_record({"domain": "example.com", "threat_type": "malware", "confidence": "0.8"})
    assert r["domain"] == "example.com"
    assert r["confidence"] == 0.8
    assert r["TimeGenerated"]
    assert r["IngestionTimeUtc"]

def test_malware_normalizer_uses_first_seen_for_time_generated():
    r = normalize_feed_record({"domain": "example.com", "first_seen": "2026-01-01 00:00:00"})
    assert r["TimeGenerated"] == "2026-01-01T00:00:00+00:00"
    assert r["TimeGenerated"] != r["IngestionTimeUtc"]

def test_nrd_without_whois_normalizer():
    r = normalize_nrd_without_whois_record({"domain_name": "example.com"})
    assert r["domain_name"] == "example.com"
    assert r["TimeGenerated"]
    assert r["IngestionTimeUtc"]

def test_nrd_with_whois_normalizer_uses_create_date_for_time_generated():
    r = normalize_nrd_with_whois_record({"domain_name": "example.com", "create_date": "2026-02-01"})
    assert r["TimeGenerated"] == "2026-02-01T00:00:00+00:00"
