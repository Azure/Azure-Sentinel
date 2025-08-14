"""
Constant File
"""
from dataclasses import dataclass
from os import environ

# pylint: disable=invalid-name

@dataclass
class VMRayConfig:
    """
    VMRay Configuration
    """
    API_KEY: str
    BASE_URL: str
    VMRAY_SAMPLE_VERDICTS: str
    INITIAL_FETCH: str
    VALID_UNTIL: str
    CONNECTOR_NAME: str = "VMRayThreatIntelligenceSentinel:1.0.0"
    RETRIES: int = 5
    BACKOFF: int = 1


VMRay_CONFIG = VMRayConfig(
    API_KEY=environ.get("VmrayAPIKey", ""),
    BASE_URL=environ.get("VmrayBaseURL", ""),
    VMRAY_SAMPLE_VERDICTS=environ.get("VmraySampleVerdict", "Malicious & Suspicious"),
    INITIAL_FETCH=environ.get("VmrayInitialFetchDate", "90"),
    VALID_UNTIL=environ.get("IndicatorExpirationInDays", "30")
)


@dataclass
class APIConfig:
    """
    Microsoft API Configurations
    """
    APPLICATION_ID: str
    APPLICATION_SECRET: str
    AUTH_URL: str
    URL: str
    RESOURCE_APPLICATION_ID_URI: str = "https://management.azure.com"
    USER_AGENT: str = "MSSentinelVMRayThreatIntelligenceSentinel:1.0.0"
    SLEEP: int = 60
    TIMEOUT: int = 300
    MAX_TI_INDICATORS_PER_REQUEST:int = 100


SENTINEL_API = APIConfig(
    APPLICATION_ID=environ.get("AzureClientID", ""),
    APPLICATION_SECRET=environ.get("AzureClientSecret", ""),
    AUTH_URL=f"https://login.microsoftonline.com/{environ.get('AzureTenantID', '')}/oauth2/token",
    URL=f"https://api.ti.sentinel.azure.com/workspaces/{environ.get('AzureWorkspaceID', '')}/"
        f"threat-intelligence-stix-objects:upload?api-version=2024-02-01-preview"
    )

RETRY_STATUS_CODE = [500, 501, 502, 503, 504, 429]
IPV4REGEX = r"^(?P<ipv4>(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))[:]?(?P<port>\d+)?$"
IPV6REGEX = r"^(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:(?:(:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"  # noqa: E501
CONFIDENCE = {"malicious": "100", "suspicious": "75"}
HASH_TYPE_LIST = [
    ("MD5", "md5_hash"),
    ("SHA-1", "sha1_hash"),
    ("SHA-256", "sha256_hash"),
]
IOC_LIST = ["domains", "ips", "urls", "files"]

