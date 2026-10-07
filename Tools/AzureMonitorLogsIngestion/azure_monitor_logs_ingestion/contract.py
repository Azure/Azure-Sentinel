from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_COLUMN_TYPES = {
    "boolean",
    "datetime",
    "dynamic",
    "int",
    "long",
    "real",
    "string",
}


@dataclass(frozen=True)
class Column:
    name: str
    type: str

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
        field: str,
        *,
        allow_raw_name: bool = False,
    ) -> "Column":
        name = str(value.get("name", "")).strip()
        column_type = str(value.get("type", "")).strip().lower()
        pattern = r"[A-Za-z_][A-Za-z0-9_.-]*" if allow_raw_name else r"[A-Za-z_][A-Za-z0-9_]*"
        if not re.fullmatch(pattern, name):
            raise ValueError(f"{field}.name must be a valid column name")
        if column_type not in SUPPORTED_COLUMN_TYPES:
            allowed = ", ".join(sorted(SUPPORTED_COLUMN_TYPES))
            raise ValueError(f"{field}.type must be one of: {allowed}")
        return cls(name=name, type=column_type)

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "type": self.type}


@dataclass(frozen=True)
class Destination:
    kind: str
    table: str
    output_stream: str
    columns: tuple[Column, ...]


@dataclass(frozen=True)
class ResourceNames:
    dce: str
    dcr: str


@dataclass(frozen=True)
class Contract:
    name: str
    workspace: str
    input_stream: str
    input_columns: tuple[Column, ...]
    transform_kql: str
    destination: Destination
    resources: ResourceNames
    location: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "workspace": self.workspace,
            "location": self.location,
            "inputStream": self.input_stream,
            "inputColumns": [column.as_dict() for column in self.input_columns],
            "transformKql": self.transform_kql,
            "destination": {
                "kind": self.destination.kind,
                "table": self.destination.table,
                "outputStream": self.destination.output_stream,
                "columns": [column.as_dict() for column in self.destination.columns],
            },
            "resources": {
                "dce": self.resources.dce,
                "dcr": self.resources.dcr,
            },
        }


def _read_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    value = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("contract root must be an object")
    return value


def _columns(
    value: Any,
    field: str,
    required: bool = True,
    *,
    allow_raw_names: bool = False,
) -> tuple[Column, ...]:
    if value is None and not required:
        return ()
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty array")
    columns = tuple(
        Column.from_dict(
            item,
            f"{field}[{index}]",
            allow_raw_name=allow_raw_names,
        )
        for index, item in enumerate(value)
    )
    names = [column.name for column in columns]
    if len(names) != len(set(names)):
        raise ValueError(f"{field} contains duplicate column names")
    return columns


def load_contract(path: str | Path) -> Contract:
    contract_path = Path(path)
    value = _read_document(contract_path)
    if value.get("version") != 1:
        raise ValueError("contract version must be 1")

    name = str(value.get("name", "")).strip()
    workspace = str(value.get("workspace", "")).strip()
    input_stream = str(value.get("inputStream", "")).strip()
    transform_kql = str(value.get("transformKql", "")).strip()
    destination_value = value.get("destination")
    resources_value = value.get("resources", {})

    if not name:
        raise ValueError("name is required")
    if not workspace:
        raise ValueError("workspace is required")
    if not input_stream.startswith("Custom-"):
        raise ValueError("inputStream must start with 'Custom-'")
    if not transform_kql:
        raise ValueError("transformKql is required")
    if not isinstance(destination_value, dict):
        raise ValueError("destination must be an object")
    if not isinstance(resources_value, dict):
        raise ValueError("resources must be an object")

    kind = str(destination_value.get("kind", "")).strip().lower()
    table = str(destination_value.get("table", "")).strip()
    output_stream = str(destination_value.get("outputStream", "")).strip()
    if kind not in {"custom", "standard"}:
        raise ValueError("destination.kind must be 'custom' or 'standard'")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", table):
        raise ValueError("destination.table must be a valid table name")
    if kind == "custom":
        if not table.endswith("_CL"):
            raise ValueError("custom destination.table must end with '_CL'")
        expected_stream = f"Custom-{table}"
        if output_stream != expected_stream:
            raise ValueError(
                f"custom destination.outputStream must be {expected_stream!r}"
            )
    elif not output_stream.startswith("Microsoft-"):
        raise ValueError("standard destination.outputStream must start with 'Microsoft-'")

    destination_columns = _columns(
        destination_value.get("columns"),
        "destination.columns",
        required=kind == "custom",
    )
    if kind == "custom" and not any(
        column.name.lower() == "timegenerated" and column.type == "datetime"
        for column in destination_columns
    ):
        raise ValueError(
            "custom destination.columns must contain TimeGenerated with type datetime"
        )

    slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    if not slug:
        raise ValueError("name must contain at least one letter or number")
    dce_name = str(resources_value.get("dce", f"{slug}-dce")).strip()
    dcr_name = str(resources_value.get("dcr", f"{slug}-dcr")).strip()
    if not dce_name or not dcr_name:
        raise ValueError("resources.dce and resources.dcr cannot be empty")

    return Contract(
        name=name,
        workspace=workspace,
        location=str(value.get("location", "")).strip() or None,
        input_stream=input_stream,
        input_columns=_columns(
            value.get("inputColumns"),
            "inputColumns",
            allow_raw_names=True,
        ),
        transform_kql=transform_kql,
        destination=Destination(
            kind=kind,
            table=table,
            output_stream=output_stream,
            columns=destination_columns,
        ),
        resources=ResourceNames(dce=dce_name, dcr=dcr_name),
    )


def load_records(path: str | Path) -> list[dict[str, Any]]:
    payload_path = Path(path)
    text = payload_path.read_text(encoding="utf-8")
    if payload_path.suffix.lower() in {".jsonl", ".ndjson"}:
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        value = json.loads(text)
        records = value if isinstance(value, list) else [value]
    if not records:
        raise ValueError("payload contains no records")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("payload must contain JSON objects")
    return records


def _matches_type(value: Any, column_type: str) -> bool:
    if value is None:
        return True
    if column_type in {"string", "datetime"}:
        return isinstance(value, str)
    if column_type == "boolean":
        return isinstance(value, bool)
    if column_type in {"int", "long"}:
        return isinstance(value, int) and not isinstance(value, bool)
    if column_type == "real":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return column_type == "dynamic"


def validate_records(contract: Contract, records: list[dict[str, Any]]) -> list[str]:
    declared = {column.name: column.type for column in contract.input_columns}
    warnings: list[str] = []
    for index, record in enumerate(records):
        unknown = sorted(set(record) - set(declared))
        if unknown:
            raise ValueError(
                f"record {index} contains undeclared fields: {', '.join(unknown)}"
            )
        for name, value in record.items():
            if name in declared and not _matches_type(value, declared[name]):
                raise ValueError(
                    f"record {index} field {name!r} does not match declared "
                    f"type {declared[name]!r}"
                )
    return warnings
