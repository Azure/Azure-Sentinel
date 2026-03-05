"""
Constant File
"""

from dataclasses import dataclass
from os import environ

# pylint: disable=invalid-name


@dataclass
class JoeConfig:
    """
    JoeSandbox Configuration
    """

    API_KEY: str
    BASE_URL: str
    JOE_ANALYSIS_VERDICTS: str
    INITIAL_FETCH_DAYS: str
    VALID_UNTIL: str
    API_URL: str = ""
    CONNECTOR_NAME: str = "JoeSandboxThreatIntelligence:1.0.0"
    RETRIES: int = 5
    TIMEOUT = 300

    def __post_init__(self):
        self.BASE_URL = self.BASE_URL.rstrip("/")
        self.API_URL = f"{self.BASE_URL}/api"


joe_config = JoeConfig(
    API_KEY=environ.get("JoeSandboxAPIKey", ""),
    BASE_URL=environ.get("JoeSandboxBaseURL", "https://jbxcloud.joesecurity.org"),
    JOE_ANALYSIS_VERDICTS=environ.get("JoeAnalysisVerdict", "Malicious & Suspicious"),
    INITIAL_FETCH_DAYS=environ.get("JoeSandboxInitialFetchDate", ""),
    VALID_UNTIL=environ.get("IndicatorExpirationInDays", "30"),
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
    USER_AGENT: str = "MSSentinelJoeSandboxIntelligenceSentinel:1.0.0"
    SLEEP: int = 60
    TIMEOUT: int = 300
    MAX_TI_INDICATORS_PER_REQUEST: int = 100


SENTINEL_API = APIConfig(
    APPLICATION_ID=environ.get("AzureClientID", ""),
    APPLICATION_SECRET=environ.get("AzureClientSecret", ""),
    AUTH_URL=f"https://login.microsoftonline.com/{environ.get('AzureTenantID', '')}/oauth2/token",
    URL=f"https://api.ti.sentinel.azure.com/workspaces/{environ.get('AzureWorkspaceID', '')}/"
    f"threat-intelligence-stix-objects:upload?api-version=2024-02-01-preview",
)

RETRY_STATUS_CODE = [500, 501, 502, 503, 504, 429]
CONFIDENCE = {"malicious": "100", "suspicious": "75"}
HASH_TYPE_LIST = [
    ("MD5", "md5_hash"),
    ("SHA-1", "sha1_hash"),
    ("SHA-256", "sha256_hash"),
]
IOC_LIST = ["domains", "ips", "urls", "files"]
DATE_FORMAT = "%Y-%m-%d"
UTC_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
