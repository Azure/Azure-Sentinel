import os

from models.feed import FeedConfig

WHOISFREAKS_FEED_BASE_URL = "https://files.whoisfreaks.com/v3.4"
WHOISFREAKS_NRD_BASE_URL = "https://files.whoisfreaks.com/v3.3"


def _stream_name(feed_name: str, default: str) -> str:
    return os.getenv(
        f"WHOISFREAKS_FEED_{feed_name.upper()}_STREAM",
        default,
    )


FEEDS = {
    "nrd_gtld_without_whois": FeedConfig(
        name="nrd_gtld_without_whois",
        endpoint=(f"{WHOISFREAKS_NRD_BASE_URL}" "/stream/domainer/gtld"),
        stream_name=_stream_name(
            "nrd_gtld_without_whois",
            "Custom-WhoisFreaksNRDGtldWithoutWhois",
        ),
        table_name="WhoisFreaksNRDGtldWithoutWhois_CL",
        page_size=10000,
        date_parameter="date",
        status_section="newly",
        status_name="gtld",
        status_api_version="v3.3",
    ),
    "nrd_cctld_without_whois": FeedConfig(
        name="nrd_cctld_without_whois",
        endpoint=(f"{WHOISFREAKS_NRD_BASE_URL}" "/stream/domainer/cctld"),
        stream_name=_stream_name(
            "nrd_cctld_without_whois",
            "Custom-WhoisFreaksNRDCctldWithoutWhois",
        ),
        table_name="WhoisFreaksNRDCctldWithoutWhois_CL",
        page_size=10000,
        date_parameter="date",
        status_section="newly",
        status_name="cctld",
        status_api_version="v3.3",
    ),
    "nrd_gtld_with_whois": FeedConfig(
        name="nrd_gtld_with_whois",
        endpoint=(f"{WHOISFREAKS_NRD_BASE_URL}" "/stream/domainer/gtld"),
        stream_name=_stream_name(
            "nrd_gtld_with_whois",
            "Custom-WhoisFreaksNRDGtldWithWhois",
        ),
        table_name="WhoisFreaksNRDGtldWithWhois_CL",
        page_size=10000,
        date_parameter="date",
        status_section="newly",
        status_name="gtld",
        status_api_version="v3.3",
    ),
    "nrd_cctld_with_whois": FeedConfig(
        name="nrd_cctld_with_whois",
        endpoint=(f"{WHOISFREAKS_NRD_BASE_URL}" "/stream/domainer/cctld"),
        stream_name=_stream_name(
            "nrd_cctld_with_whois",
            "Custom-WhoisFreaksNRDCctldWithWhois",
        ),
        table_name="WhoisFreaksNRDCctldWithWhois_CL",
        page_size=10000,
        date_parameter="date",
        status_section="newly",
        status_name="cctld",
        status_api_version="v3.3",
    ),
    "malware": FeedConfig(
        name="malware",
        endpoint=(f"{WHOISFREAKS_FEED_BASE_URL}" "/stream/threat-feed/malware"),
        stream_name=_stream_name(
            "malware",
            "Custom-WhoisFreaksMalware",
        ),
        table_name="WhoisFreaksMalware_CL",
        page_size=10000,
    ),
    "phishing": FeedConfig(
        name="phishing",
        endpoint=(f"{WHOISFREAKS_FEED_BASE_URL}" "/stream/threat-feed/phishing"),
        stream_name=_stream_name(
            "phishing",
            "Custom-WhoisFreaksPhishing",
        ),
        table_name="WhoisFreaksPhishing_CL",
        page_size=10000,
    ),
    "spam": FeedConfig(
        name="spam",
        endpoint=(f"{WHOISFREAKS_FEED_BASE_URL}" "/stream/threat-feed/spam"),
        stream_name=_stream_name(
            "spam",
            "Custom-WhoisFreaksSpam",
        ),
        table_name="WhoisFreaksSpam_CL",
        page_size=10000,
    ),
}
