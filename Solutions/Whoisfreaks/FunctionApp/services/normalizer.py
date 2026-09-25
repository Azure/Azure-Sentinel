from datetime import datetime, timezone
from typing import Any

from models.feed import FeedConfig

# Feeds that have a normalizer implemented below. This is checked by
# services.processor.resolve_enabled_feeds() *before* any API calls
# are made. Malware/phishing/spam share normalize_feed_record (same
# domain+threat schema). NRD feeds use the with/without-WHOIS normalizers.
SUPPORTED_FEEDS = {"malware", "phishing", "spam", "nrd_gtld_with_whois", "nrd_cctld_with_whois", "nrd_cctld_without_whois", "nrd_gtld_without_whois"}


def parse_datetime(value: Any) -> str | None:
    """
    Convert a WhoisFreaks date/time value into
    an ISO-8601 timestamp suitable for Azure Monitor.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    # Already ISO-like.
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc).isoformat()

    except ValueError:
        pass

    # Common WhoisFreaks CSV format.
    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
    )

    for date_format in formats:

        try:

            parsed = datetime.strptime(
                value,
                date_format,
            )

            parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.isoformat()

        except ValueError:
            continue

    return None


def parse_float(value: Any) -> float | None:

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: Any) -> int | None:

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def normalize_feed_record(
    record: dict[str, Any],
) -> dict[str, Any]:

    now = datetime.now(timezone.utc).isoformat()
    first_seen = parse_datetime(record.get("first_seen"))
    last_seen = parse_datetime(record.get("last_seen"))

    # TimeGenerated reflects the feed's own observation time (first_seen,
    # falling back to last_seen) so time-based queries reflect when
    # WhoisFreaks observed the threat, not when this Function happened
    # to ingest it. Ingestion time is preserved separately in
    # IngestionTimeUtc so re-runs/retries don't lose that information.
    return {
        "TimeGenerated": first_seen or last_seen or now,
        "IngestionTimeUtc": now,
        "domain": (record.get("domain") or record.get("domain_name")),
        "threat_type": (record.get("threat_type") or record.get("threat")),
        "confidence": parse_float(record.get("confidence")),
        "first_seen": first_seen,
        "last_seen": last_seen,
        "No_of_threat_matched_pivots": parse_int(
            record.get("No_of_threat_matched_pivots")
        ),
    }


def normalize_nrd_with_whois_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize a WhoisFreaks NRD gTLD + WHOIS record
    for Azure Monitor Logs Ingestion API.
    """

    now = datetime.now(timezone.utc).isoformat()
    create_date = parse_datetime(record.get("create_date"))
    query_time = parse_datetime(record.get("query_time"))

    # TimeGenerated reflects the domain's registration event time
    # (create_date, falling back to query_time) rather than ingestion
    # time. Ingestion time is preserved in IngestionTimeUtc.
    return {
        "TimeGenerated": create_date or query_time or now,
        "IngestionTimeUtc": now,
        "num": parse_int(record.get("num")),
        "domain_name": record.get("domain_name"),
        "query_time": query_time,
        "create_date": create_date,
        "update_date": parse_datetime(record.get("update_date")),
        "expiry_date": parse_datetime(record.get("expiry_date")),
        "domain_registrar_id": record.get("domain_registrar_id"),
        "domain_registrar_name": record.get("domain_registrar_name"),
        "domain_registrar_whois": record.get("domain_registrar_whois"),
        "domain_registrar_url": record.get("domain_registrar_url"),
        "domain_registrar_email_address": record.get("domain_registrar_email_address"),
        "domain_registrar_phone": record.get("domain_registrar_phone"),
        "domain_registrar_authoritative_registry_name": record.get(
            "domain_registrar_authoritative_registry_name"
        ),
        "registrant_id": record.get("registrant_id"),
        "registrant_id_type": record.get("registrant_id_type"),
        "registrant_handle": record.get("registrant_handle"),
        "registrant_name": record.get("registrant_name"),
        "registrant_company": record.get("registrant_company"),
        "registrant_address": record.get("registrant_address"),
        "registrant_city": record.get("registrant_city"),
        "registrant_state": record.get("registrant_state"),
        "registrant_zip": record.get("registrant_zip"),
        "registrant_country_code": record.get("registrant_country_code"),
        "registrant_country": record.get("registrant_country"),
        "registrant_email": record.get("registrant_email"),
        "registrant_phone": record.get("registrant_phone"),
        "registrant_fax": record.get("registrant_fax"),
        "administrative_id": record.get("administrative_id"),
        "administrative_id_type": record.get("administrative_id_type"),
        "administrative_handle": record.get("administrative_handle"),
        "administrative_name": record.get("administrative_name"),
        "administrative_company": record.get("administrative_company"),
        "administrative_address": record.get("administrative_address"),
        "administrative_city": record.get("administrative_city"),
        "administrative_state": record.get("administrative_state"),
        "administrative_zip": record.get("administrative_zip"),
        "administrative_country_code": record.get("administrative_country_code"),
        "administrative_country": record.get("administrative_country"),
        "administrative_email": record.get("administrative_email"),
        "administrative_phone": record.get("administrative_phone"),
        "administrative_fax": record.get("administrative_fax"),
        "technical_id": record.get("technical_id"),
        "technical_id_type": record.get("technical_id_type"),
        "technical_handle": record.get("technical_handle"),
        "technical_name": record.get("technical_name"),
        "technical_company": record.get("technical_company"),
        "technical_address": record.get("technical_address"),
        "technical_city": record.get("technical_city"),
        "technical_state": record.get("technical_state"),
        "technical_zip": record.get("technical_zip"),
        "technical_country_code": record.get("technical_country_code"),
        "technical_country": record.get("technical_country"),
        "technical_email": record.get("technical_email"),
        "technical_phone": record.get("technical_phone"),
        "technical_fax": record.get("technical_fax"),
        "billing_id": record.get("billing_id"),
        "billing_id_type": record.get("billing_id_type"),
        "billing_handle": record.get("billing_handle"),
        "billing_name": record.get("billing_name"),
        "billing_company": record.get("billing_company"),
        "billing_address": record.get("billing_address"),
        "billing_city": record.get("billing_city"),
        "billing_state": record.get("billing_state"),
        "billing_zip": record.get("billing_zip"),
        "billing_country_code": record.get("billing_country_code"),
        "billing_country": record.get("billing_country"),
        "billing_email": record.get("billing_email"),
        "billing_phone": record.get("billing_phone"),
        "billing_fax": record.get("billing_fax"),
        "eligibility_id": record.get("eligibility_id"),
        "eligibility_name": record.get("eligibility_name"),
        "eligibility_type": record.get("eligibility_type"),
        "name_server_1": record.get("name_server_1"),
        "name_server_2": record.get("name_server_2"),
        "name_server_3": record.get("name_server_3"),
        "name_server_4": record.get("name_server_4"),
        "domain_status_1": record.get("domain_status_1"),
        "domain_status_2": record.get("domain_status_2"),
        "domain_status_3": record.get("domain_status_3"),
        "domain_status_4": record.get("domain_status_4"),
        "reseller_name": record.get("reseller_name"),
        "reseller_email": record.get("reseller_email"),
        "reseller_phone": record.get("reseller_phone"),
    }

def normalize_nrd_without_whois_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        # No event-time field is available in the "without WHOIS" domain
        # list response, so TimeGenerated is ingestion time here.
        "TimeGenerated": now,
        "IngestionTimeUtc": now,
        "domain_name": record.get("domain_name") or record.get("domain"),
    }
_NORMALIZERS = {
    "malware": normalize_feed_record,
    "phishing": normalize_feed_record,
    "spam": normalize_feed_record,
    "nrd_gtld_with_whois": normalize_nrd_with_whois_record,
    "nrd_cctld_with_whois": normalize_nrd_with_whois_record,
    "nrd_gtld_without_whois": normalize_nrd_without_whois_record,
    "nrd_cctld_without_whois": normalize_nrd_without_whois_record,
}


def normalize_records(
    feed: FeedConfig,
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalizer = _NORMALIZERS.get(feed.name)

    if normalizer is None:
        raise ValueError(f"No normalizer implemented for feed: {feed.name}")

    # Generate a single timestamp for the batch if records share the same ingestion time
    return [normalizer(record) for record in records]