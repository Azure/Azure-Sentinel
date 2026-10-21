"""Validation of the Function App settings. Every problem is logged with the name of the setting, then the run stops with one error."""
import datetime
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from . import consts
from .exceptions import CensysException
from .logger import applogger
from .suppliers import parse_names

_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
_RFC3339 = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?([Zz]|[+-]\d{2}:\d{2})$")
_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_START_TIME_EXAMPLE = "2026-10-01T00:00:00Z"


@dataclass
class Settings:
    """The validated and cleaned settings of the main function."""

    api_token: str
    organization_id: str
    storage_connection: str
    data_collection_endpoint: str
    data_collection_rule_id: str
    start_time: str
    supplier_names: List[str] = field(default_factory=list)
    risk_type_ids: List[str] = field(default_factory=list)
    change_types: List[str] = field(default_factory=list)
    severity: List[str] = field(default_factory=list)
    rapid_response: Optional[str] = None

    def filters(self, supplier_ids: Optional[List[str]] = None) -> Dict[str, str]:
        """Return the query parameters of the filters. A filter without a value is never included."""
        filters: Dict[str, str] = {}
        for name, values in (("supplier_ids", supplier_ids), ("risk_type_ids", self.risk_type_ids),
                             ("change_types", self.change_types), ("severity", self.severity)):
            if values:
                filters[name] = ",".join(values)
        if self.rapid_response:
            filters["rapid_response"] = self.rapid_response
        return filters


class _Problems:
    def __init__(self):
        self.settings: List[str] = []

    def add(self, setting: str, message: str) -> None:
        applogger.error(f"{consts.LOG_PREFIX} validate_settings: setting '{setting}' {message}")
        self.settings.append(setting)

    def raise_if_any(self) -> None:
        if self.settings:
            raise CensysException(f"Invalid settings: {', '.join(self.settings)}. See the previous error logs for the details.")


def _value(raw: Optional[str], name: str) -> str:
    """Trimmed value. The name of the setting itself (a placeholder left in by mistake) counts as empty."""
    value = (raw or "").strip()
    return "" if value.lower() == name.lower() else value


def _items(raw: str, separator: str = ",") -> List[str]:
    items = []
    for item in raw.replace("\n", separator).split(separator):
        item = item.strip()
        if item and item not in items:
            items.append(item)
    return items


def parse_start_time(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return (start time in UTC as yyyy-MM-ddTHH:mm:ssZ, error). Empty means all events Censys still retains."""
    value = _value(raw, "InitialStartTime")
    if not value:
        return consts.DEFAULT_START_TIME, None
    match = _RFC3339.match(value)
    if not match:
        return None, f"must be a UTC time with date and time, for example {_START_TIME_EXAMPLE}, but is '{value}'."
    year, month, day, hour, minute, second = (int(match.group(i)) for i in range(1, 7))
    micro = int((match.group(7) or "0")[:6].ljust(6, "0"))
    zone = match.group(8)
    try:
        offset = datetime.timedelta(0)
        if zone not in ("Z", "z"):
            hours, minutes = int(zone[1:3]), int(zone[4:6])
            offset = datetime.timedelta(hours=hours, minutes=minutes) * (1 if zone[0] == "+" else -1)
        moment = datetime.datetime(year, month, day, hour, minute, second, micro, tzinfo=datetime.timezone(offset))
    except ValueError:
        return None, f"is not a real date and time: '{value}'. Use the form {_START_TIME_EXAMPLE}."
    moment = moment.astimezone(datetime.timezone.utc)
    if moment > datetime.datetime.now(datetime.timezone.utc):
        return None, f"must not be in the future: '{value}'."
    return moment.strftime(_TIME_FORMAT), None


def _choice_list(raw: str, name: str, allowed: Tuple[str, ...], upper: bool, problems: _Problems) -> List[str]:
    values = []
    for item in _items(_value(raw, name)):
        item = item.upper() if upper else item.lower()
        if item not in values:
            values.append(item)
    bad = [v for v in values if v not in allowed]
    if bad:
        problems.add(name, f"has unsupported values {bad}. Allowed values: {', '.join(allowed)}.")
    return values


def load_common(problems: Optional[_Problems] = None) -> Tuple[str, str, str]:
    """Validate and return (API token, organization id, storage connection string), used by both functions."""
    own = problems is None
    problems = problems or _Problems()
    token = (consts.API_TOKEN or "").strip()
    org = (consts.ORGANIZATION_ID or "").strip()
    storage = (consts.CONN_STRING or "").strip()
    if not token:
        problems.add("CensysApiToken", "is not set. Enter your Censys personal access token.")
    if not org:
        problems.add("OrganizationId", "is not set. Enter the UUID of your Censys organization.")
    elif not _UUID.match(org):
        problems.add("OrganizationId", f"must be a UUID, for example 00000000-0000-0000-0000-000000000000, but is '{org}'.")
    if not storage:
        problems.add("AzureWebJobsStorage", "is not set.")
    if own:
        problems.raise_if_any()
    return token, org, storage


def load_settings() -> Settings:
    """Validate every setting of the main function and return the cleaned values. Raises one CensysException listing the settings."""
    problems = _Problems()
    token, org, storage = load_common(problems)
    endpoint = (consts.DATA_COLLECTION_ENDPOINT or "").strip()
    rule = (consts.DATA_COLLECTION_RULE_ID or "").strip()
    if not endpoint:
        problems.add("AZURE_DATA_COLLECTION_ENDPOINT", "is not set.")
    if not rule:
        problems.add("AZURE_DATA_COLLECTION_RULE_ID", "is not set.")

    start_time, error = parse_start_time(consts.INITIAL_START_TIME)
    if error:
        problems.add("InitialStartTime", error)

    change_types = _choice_list(consts.CHANGE_TYPES, "ChangeTypes", consts.ALLOWED_CHANGE_TYPES, False, problems)
    severity = _choice_list(consts.SEVERITY, "Severity", consts.ALLOWED_SEVERITIES, True, problems)
    rapid = _value(consts.RAPID_RESPONSE, "RapidResponse").lower()
    if rapid and rapid not in ("true", "false"):
        problems.add("RapidResponse", f"must be true or false, but is '{rapid}'. Leave it empty for both.")
        rapid = ""

    risk_type_ids = _items(_value(consts.RISK_TYPE_IDS, "RiskTypeIds"))
    if len(risk_type_ids) > consts.MAX_RISK_TYPE_IDS:
        problems.add("RiskTypeIds", f"has {len(risk_type_ids)} values, at most {consts.MAX_RISK_TYPE_IDS} are allowed.")
    too_long = [r[:20] + "..." for r in risk_type_ids if len(r) > consts.MAX_RISK_TYPE_ID_LENGTH]
    if too_long:
        problems.add("RiskTypeIds", f"has values longer than {consts.MAX_RISK_TYPE_ID_LENGTH} characters: {too_long}.")

    raw_names = (consts.SUPPLIER_NAMES or "").strip()
    if len(raw_names) > consts.MAX_SUPPLIER_NAMES_LENGTH:
        problems.add("SupplierNames", f"has {len(raw_names)} characters, at most {consts.MAX_SUPPLIER_NAMES_LENGTH} are allowed.")
    supplier_names = parse_names(raw_names)

    problems.raise_if_any()
    return Settings(api_token=token, organization_id=org, storage_connection=storage, data_collection_endpoint=endpoint,
                    data_collection_rule_id=rule, start_time=start_time, supplier_names=supplier_names, risk_type_ids=risk_type_ids,
                    change_types=change_types, severity=severity, rapid_response=rapid or None)
