"""Shared parser models, safe YAML loading, and repository evidence lookup."""

from __future__ import annotations

import functools
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml

MANIFEST_VERSION = 2
VALIDATION_RESULT_VERSION = 2
MAX_YAML_BYTES = 1024 * 1024

QUERY_TIME_PATH_RE = re.compile(
    r"^Parsers/ASim(?P<schema>[^/]+)/Parsers/(?P<name>ASim[^/]+)\.yaml$"
)
INGEST_TIME_PATH_RE = re.compile(
    r"^Parsers/ASim(?P<schema>[^/]+)/IngestTimeParsers/(?P<name>[^/]+)\.yaml$"
)
FIXTURE_PATH_RE = re.compile(
    r"^Sample Data/ASIM/[^/]+_IngestedLogs\.csv$"
)
PARSER_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]+$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
STREAM_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

ADDITIONAL_UNION_PARSERS = {
    "ProcessEvent": {
        "ASimProcessEventCreate.yaml",
        "ASimProcessEventTerminate.yaml",
    }
}

TARGET_TABLE_BY_SCHEMA = {
    "AgentEvent": "ASimAgentEventLogs",
    "AlertEvent": "ASimAlertEventLogs",
    "AssetEntity": "ASimAssetEntityLogs",
    "AuditEvent": "ASimAuditEventLogs",
    "Authentication": "ASimAuthenticationEventLogs",
    "DhcpEvent": "ASimDhcpEventLogs",
    "Dns": "ASimDnsActivityLogs",
    "EmailEvent": "ASimEmailEventLogs",
    "FileEvent": "ASimFileEventLogs",
    "NetworkSession": "ASimNetworkSessionLogs",
    "ProcessEvent": "ASimProcessEventLogs",
    "RegistryEvent": "ASimRegistryEventLogs",
    "UserManagement": "ASimUserManagementActivityLogs",
    "WebSession": "ASimWebSessionLogs",
}

class DuplicateKeyError(ValueError):
    """Raised when a YAML mapping contains the same key more than once."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(
                f"Duplicate YAML key '{key}' at line {key_node.start_mark.line + 1}."
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class Finding:
    code: str
    field: str
    message: str
    line: int | None = None
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
        }
        if self.line is not None:
            payload["line"] = self.line
        return payload


@dataclass(frozen=True)
class ParserRecord:
    path: str
    kind: str
    document: dict[str, Any]
    parser_name: str
    schema: str
    schema_version: str | None
    product: str
    parser_query: str
    source_raw_table: str | None = None
    target_asim_table: str | None = None
    event_vendor: str | None = None
    event_product: str | None = None
    fixture_path: str | None = None
    fixture_errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class PairResolution:
    status: str
    selected: ParserRecord | None
    candidates: tuple[ParserRecord, ...]
    evidence: dict[str, Any]


def _get_nested(document: dict[str, Any], *keys: str) -> Any:
    value: Any = document
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def normalize_changed_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    pure_path = PurePosixPath(normalized)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        raise ValueError(f"Changed path must stay inside the repository: {path}")
    return pure_path.as_posix().lstrip("./")


def classify_parser_path(path: str) -> str | None:
    normalized = normalize_changed_path(path)
    if INGEST_TIME_PATH_RE.fullmatch(normalized):
        return "ingest-time"
    match = QUERY_TIME_PATH_RE.fullmatch(normalized)
    if not match:
        return None
    schema = match.group("schema")
    filename = PurePosixPath(normalized).name
    if filename == f"ASim{schema}.yaml":
        return None
    if filename in ADDITIONAL_UNION_PARSERS.get(schema, set()):
        return None
    return "query-time"


def classify_changed_path(path: str) -> str | None:
    normalized = normalize_changed_path(path)
    parser_kind = classify_parser_path(normalized)
    if parser_kind is not None:
        return parser_kind
    if FIXTURE_PATH_RE.fullmatch(normalized):
        return "fixture"
    return None


def load_yaml_file(path: Path) -> dict[str, Any]:
    file_size = path.stat().st_size
    if file_size > MAX_YAML_BYTES:
        raise ValueError(
            f"{path} exceeds the {MAX_YAML_BYTES}-byte YAML limit."
        )
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} must be UTF-8 text.") from exc
    document = yaml.load(content, Loader=UniqueKeyLoader)
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the document root.")
    return document


def _find_repo_root(path: Path) -> Path | None:
    matches: list[Path] = []
    for candidate in (path.parent, *path.parents):
        if (candidate / "Parsers").is_dir():
            matches.append(candidate)
    return matches[-1] if matches else None


def _collect_output_streams(value: Any) -> set[str]:
    streams: set[str] = set()
    if isinstance(value, dict):
        output_stream = value.get("outputStream")
        if isinstance(output_stream, str):
            streams.add(output_stream)
        for child in value.values():
            streams.update(_collect_output_streams(child))
    elif isinstance(value, list):
        for child in value:
            streams.update(_collect_output_streams(child))
    return streams


def _collect_dcr_resources(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        resource_type = value.get("type")
        if (
            isinstance(resource_type, str)
            and resource_type.casefold()
            == "microsoft.insights/datacollectionrules"
        ):
            yield value
        for child in value.values():
            yield from _collect_dcr_resources(child)
    elif isinstance(value, list):
        for child in value:
            yield from _collect_dcr_resources(child)


@functools.lru_cache(maxsize=128)
def find_dcr_output_stream_evidence(
    repo_root_text: str, output_stream: str
) -> tuple[str, ...]:
    repo_root = Path(repo_root_text)
    candidate_paths: set[Path] = set()
    if (repo_root / ".git").exists():
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "grep",
                "-l",
                "-F",
                output_stream,
                "--",
                "Solutions/**/*.json",
                "DataConnectors/**/*.json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        candidate_paths.update(
            repo_root / line
            for line in result.stdout.splitlines()
            if "/Data Connectors/" in line.replace("\\", "/")
            or line.replace("\\", "/").startswith("DataConnectors/")
        )
    else:
        solutions_root = repo_root / "Solutions"
        if solutions_root.is_dir():
            candidate_paths.update(
                solutions_root.glob("*/Data Connectors/**/*.json")
            )
        data_connectors_root = repo_root / "DataConnectors"
        if data_connectors_root.is_dir():
            candidate_paths.update(data_connectors_root.rglob("*.json"))

    evidence_paths: set[str] = set()
    for path in sorted(candidate_paths):
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if "outputStream" not in raw:
            continue
        try:
            document = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for resource in _collect_dcr_resources(document):
            if output_stream in _collect_output_streams(resource):
                evidence_paths.add(_repo_relative_path(repo_root, path))
    return tuple(sorted(evidence_paths))
