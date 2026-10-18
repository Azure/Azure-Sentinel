from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from .contract import Column, Contract, load_contract

def _default_package_root() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    if (repo_root / "registry.yaml").is_file():
        return repo_root
    bundled_root = Path(__file__).resolve().parent / "data"
    if (bundled_root / "registry.yaml").is_file():
        return bundled_root
    return Path(__file__).resolve().parent


PACKAGE_ROOT = _default_package_root()
DEFAULT_REGISTRY = PACKAGE_ROOT / "registry.yaml"
SUPPORTED_ROUTES = {"logs-ingestion-api"}
TYPE_ALIASES = {"bool": "boolean", "double": "real"}
ARM_TABLE_COLUMN_TYPES = {
    "string",
    "int",
    "long",
    "real",
    "boolean",
    "datetime",
    "guid",
    "dynamic",
}


@dataclass(frozen=True)
class TableCapability:
    table: str
    contract_path: Path
    route: str
    input_kind: str
    output_kind: str
    output_stream: str
    schema_reference: str
    metadata_reference: str
    capability_reference: str
    route_reference: str
    live_validated: bool


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _read_registry(path: str | Path = DEFAULT_REGISTRY) -> list[TableCapability]:
    registry_path = Path(path).resolve()
    document = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("ingestion capability registry version must be 1")
    entries = document.get("tables")
    if not isinstance(entries, list):
        raise ValueError("ingestion capability registry tables must be an array")

    capabilities: list[TableCapability] = []
    seen: set[str] = set()
    package_root = registry_path.parent
    for index, entry in enumerate(entries):
        field = f"registry.tables[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{field} must be an object")
        table = str(entry.get("table", "")).strip()
        if not table or table.casefold() in seen:
            raise ValueError(f"{field}.table must be present and unique")
        seen.add(table.casefold())
        route = str(entry.get("route", "")).strip()
        if route not in SUPPORTED_ROUTES:
            raise ValueError(
                f"{field}.route must be one of: {', '.join(sorted(SUPPORTED_ROUTES))}"
            )
        if entry.get("inputKind") != "custom-stream":
            raise ValueError(f"{field}.inputKind must be 'custom-stream'")
        if entry.get("outputKind") != "standard-table":
            raise ValueError(f"{field}.outputKind must be 'standard-table'")
        contract_relative = Path(str(entry.get("contract", "")))
        contract_path = (package_root / contract_relative).resolve()
        if package_root not in contract_path.parents:
            raise ValueError(f"{field}.contract must remain under the contract registry")
        if not contract_path.is_file():
            raise ValueError(f"{field}.contract does not exist: {contract_relative}")
        contract = load_contract(contract_path)
        if (
            contract.destination.kind != "standard"
            or contract.destination.table.casefold() != table.casefold()
            or contract.destination.output_stream != entry.get("outputStream")
        ):
            raise ValueError(f"{field} does not match its registered contract")
        if not all(
            entry.get(key)
            for key in (
                "schemaReference",
                "metadataReference",
                "capabilityReference",
                "routeReference",
            )
        ):
            raise ValueError(
                f"{field} must link public schema metadata, capability, and route references"
            )
        capabilities.append(
            TableCapability(
                table=table,
                contract_path=contract_path,
                route=route,
                input_kind="custom-stream",
                output_kind="standard-table",
                output_stream=str(entry["outputStream"]),
                schema_reference=str(entry["schemaReference"]),
                metadata_reference=str(entry["metadataReference"]),
                capability_reference=str(entry["capabilityReference"]),
                route_reference=str(entry["routeReference"]),
                live_validated=entry.get("liveValidated") is True,
            )
        )
    return capabilities


def find_capability(
    table: str, registry_path: str | Path = DEFAULT_REGISTRY
) -> TableCapability | None:
    requested = table.strip().casefold()
    if not requested:
        return None
    matches = [
        item
        for item in _read_registry(registry_path)
        if item.table.casefold() == requested
    ]
    if len(matches) > 1:
        raise ValueError(f"table {table!r} is ambiguous in the capability registry")
    return matches[0] if matches else None


def _type_name(value: str) -> str:
    normalized = value.strip().lower()
    return TYPE_ALIASES.get(normalized, normalized)


def _schema_fingerprint(contract: Contract) -> str:
    return fingerprint(
        {
            "table": contract.destination.table,
            "inputStream": contract.input_stream,
            "inputColumns": [
                {"name": column.name, "type": _type_name(column.type)}
                for column in sorted(contract.input_columns, key=lambda item: item.name.casefold())
            ],
            "outputStream": contract.destination.output_stream,
            "destinationColumns": [
                {"name": column.name, "type": _type_name(column.type)}
                for column in sorted(
                    contract.destination.columns, key=lambda item: item.name.casefold()
                )
            ],
        }
    )


def _transform_fingerprint(contract: Contract) -> str:
    normalized = "\n".join(
        line.rstrip() for line in contract.transform_kql.strip().splitlines()
    )
    return fingerprint({"transformKql": normalized})


def _field_map(columns: tuple[Column, ...]) -> dict[str, Column]:
    return {column.name.casefold(): column for column in columns}


def resolve_contract(
    table: str,
    required_fields: Mapping[str, str | None] | None = None,
    *,
    registry_path: str | Path = DEFAULT_REGISTRY,
) -> dict[str, Any]:
    """Resolve an exact, reviewed table capability without contacting Azure."""
    capability = find_capability(table, registry_path)
    if capability is None:
        return {
            "status": "blocked",
            "table": table,
            "blockers": [f"No reviewed ingestion capability is registered for {table!r}."],
        }

    contract = load_contract(capability.contract_path)
    declared = _field_map(contract.input_columns)
    destination_declared = _field_map(contract.destination.columns)
    blockers: list[str] = []
    for field, expected_type in sorted((required_fields or {}).items(), key=lambda item: item[0].casefold()):
        column = declared.get(field.casefold())
        if column is None:
            blockers.append(
                f"Required source field {field!r} is not declared by the registered input contract."
            )
        elif expected_type and _type_name(column.type) != _type_name(expected_type):
            blockers.append(
                f"Required source field {field!r} has registered type {column.type!r}, "
                f"not required type {expected_type!r}."
            )
        destination_column = destination_declared.get(field.casefold())
        if contract.destination.columns and destination_column is None:
            blockers.append(
                f"Required query field {field!r} is not projected to the registered destination."
            )
        elif (
            destination_column
            and expected_type
            and _type_name(destination_column.type) != _type_name(expected_type)
        ):
            blockers.append(
                f"Required query field {field!r} has destination type "
                f"{destination_column.type!r}, not expected type {expected_type!r}."
            )

    return {
        "status": "blocked" if blockers else "provisioning-plan",
        "registryVersion": 1,
        "table": capability.table,
        "route": capability.route,
        "inputKind": capability.input_kind,
        "outputKind": capability.output_kind,
        "outputStream": capability.output_stream,
        "contract": contract.as_dict(),
        "contractPath": capability.contract_path.relative_to(
            Path(registry_path).resolve().parent
        ).as_posix(),
        "schemaFingerprint": _schema_fingerprint(contract),
        "transformFingerprint": _transform_fingerprint(contract),
        "liveValidated": capability.live_validated,
        "references": {
            "schema": capability.schema_reference,
            "metadata": capability.metadata_reference,
            "capability": capability.capability_reference,
            "route": capability.route_reference,
        },
        "blockers": blockers,
        "plan": (
            {
                "operation": "provision-or-reuse-isolated-managed-resources",
                "writesPerformed": False,
                "requiresSeparateApproval": True,
                "resourceNames": {
                    "dce": contract.resources.dce,
                    "dcr": contract.resources.dcr,
                },
            }
            if not blockers
            else None
        ),
    }


def inspect_managed_resources(
    contract: Contract,
    workspace_id: str,
    dce: dict[str, Any] | None,
    dcr: dict[str, Any] | None,
    dce_resource_id: str | None = None,
    dcr_resource_id: str | None = None,
) -> dict[str, Any]:
    """Compare only exact, caller-selected resource candidates; never writes."""
    blockers: list[str] = []
    if not dce or not dcr:
        if dce or dcr:
            return {
                "status": "blocked",
                "writesPerformed": False,
                "requiresSeparateApproval": True,
                "missing": [
                    name
                    for name, value in (("DCE", dce), ("DCR", dcr))
                    if not value
                ],
                "blockers": [
                    "Only one of the contract-specific DCE/DCR candidates exists; "
                    "the partial resource pair requires manual review."
                ],
            }
        return {
            "status": "provisioning-plan",
            "writesPerformed": False,
            "requiresSeparateApproval": True,
            "missing": [
                name
                for name, value in (("DCE", dce), ("DCR", dcr))
                if not value
            ],
            "blockers": [],
        }

    dce_tags = dce.get("tags") or {}
    dcr_tags = dcr.get("tags") or {}
    for resource_name, tags in (("DCE", dce_tags), ("DCR", dcr_tags)):
        if tags.get("managed-by") != "azure-monitor-logs-ingestion":
            blockers.append(f"Candidate {resource_name} is not owned by this ingestion tool.")
        if tags.get("ingestion-contract") != contract.name:
            blockers.append(
                f"Candidate {resource_name} does not have the expected ingestion-contract owner tag."
            )
    if dce_resource_id and dce.get("id") and str(dce["id"]).casefold() != dce_resource_id.casefold():
        blockers.append("Candidate DCE resource ID does not match the exact contract candidate.")
    if dcr_resource_id and dcr.get("id") and str(dcr["id"]).casefold() != dcr_resource_id.casefold():
        blockers.append("Candidate DCR resource ID does not match the exact contract candidate.")
    if not (
        (dce.get("properties") or {}).get("logsIngestion") or {}
    ).get("endpoint"):
        blockers.append("Candidate DCE has no Logs Ingestion endpoint.")

    properties = dcr.get("properties") or {}
    if dcr.get("kind") != "Direct":
        blockers.append("Candidate DCR kind must be 'Direct' for Logs Ingestion API.")
    if dce_resource_id and str(
        properties.get("dataCollectionEndpointId", "")
    ).casefold() != dce_resource_id.casefold():
        blockers.append("Candidate DCR is not connected to the contract-specific DCE.")
    declarations = properties.get("streamDeclarations") or {}
    if set(declarations) != {contract.input_stream}:
        blockers.append("Candidate DCR does not declare exactly the requested input stream.")
    else:
        actual_columns = declarations[contract.input_stream].get("columns") or []
        expected_columns = [column.as_dict() for column in contract.input_columns]
        if _normalized_columns(actual_columns) != _normalized_columns(expected_columns):
            blockers.append("Candidate DCR input schema differs from the reviewed contract.")

    flows = properties.get("dataFlows") or []
    if len(flows) != 1 or flows[0].get("streams") != [contract.input_stream]:
        blockers.append("Candidate DCR must contain exactly one flow for the requested input stream.")
    else:
        flow = flows[0]
        if len(flow.get("destinations") or []) != 1:
            blockers.append("Candidate DCR flow must target exactly one workspace destination.")
        if flow.get("outputStream") != contract.destination.output_stream:
            blockers.append("Candidate DCR output stream differs from the reviewed contract.")
        if flow.get("transformKql", "").strip() != contract.transform_kql.strip():
            blockers.append("Candidate DCR transform differs from the reviewed contract.")
        destinations = properties.get("destinations") or {}
        log_analytics = destinations.get("logAnalytics") or []
        if len(log_analytics) != 1:
            blockers.append("Candidate DCR must contain exactly one Log Analytics destination.")
        target_ids = {
            str(item.get("workspaceResourceId", "")).casefold()
            for item in log_analytics
            if item.get("name") in (flow.get("destinations") or [])
        }
        if target_ids != {workspace_id.casefold()}:
            blockers.append("Candidate DCR does not target exactly the locked workspace.")
    return {
        "status": "blocked" if blockers else "compatible-existing",
        "writesPerformed": False,
        "requiresSeparateApproval": False,
        "blockers": blockers,
        "schemaFingerprint": _schema_fingerprint(contract),
        "transformFingerprint": _transform_fingerprint(contract),
    }


def destination_schema_blockers(
    contract: Contract, table_document: dict[str, Any]
) -> list[str]:
    blockers: list[str] = []
    if not isinstance(table_document, Mapping):
        return ["Table GET response must be an object."]
    properties = table_document.get("properties")
    if not isinstance(properties, Mapping):
        return ["Table GET response is missing an object-valued properties field."]
    schema = properties.get("schema")
    if not isinstance(schema, Mapping):
        return ["Table GET response is missing an object-valued properties.schema."]

    actual: dict[str, tuple[str, str]] = {}
    saw_column_list = False
    for field, label in (
        ("standardColumns", "standard"),
        ("columns", "custom"),
    ):
        if field not in schema:
            continue
        saw_column_list = True
        entries = schema[field]
        if not isinstance(entries, list):
            blockers.append(f"Table schema {field} must be an array.")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                blockers.append(
                    f"Table schema {field}[{index}] must be an object."
                )
                continue
            name = entry.get("name")
            column_type = entry.get("type")
            if not isinstance(name, str) or not name.strip():
                blockers.append(
                    f"Table schema {field}[{index}] is missing a non-empty column name."
                )
                continue
            if not isinstance(column_type, str) or not column_type.strip():
                blockers.append(
                    f"Table schema {field}[{index}] is missing a non-empty column type."
                )
                continue
            normalized_type = column_type.strip().lower()
            if normalized_type not in ARM_TABLE_COLUMN_TYPES:
                blockers.append(
                    f"Table schema {field}[{index}] has unsupported ARM column type "
                    f"{column_type!r}."
                )
                continue

            key = name.casefold()
            previous = actual.get(key)
            if previous:
                previous_type, previous_source = previous
                if previous_type != normalized_type:
                    blockers.append(
                        f"Table schema column {name!r} has conflicting types in "
                        f"{previous_source} and {label} columns "
                        f"({previous_type!r} vs {normalized_type!r})."
                    )
                else:
                    blockers.append(
                        f"Table schema column {name!r} appears more than once in "
                        "standardColumns/columns."
                    )
                continue
            actual[key] = (normalized_type, label)

    if not saw_column_list:
        blockers.append(
            "Table schema is missing both standardColumns and columns arrays."
        )
    elif not actual and not blockers:
        blockers.append("Table schema contains no standard or custom columns.")

    # The ARM schema is used only to confirm destination column presence and
    # type. Writable destinations remain the explicit contract/registry allowlist.
    for column in contract.destination.columns:
        actual_column = actual.get(column.name.casefold())
        if actual_column is None:
            blockers.append(
                f"Destination table {contract.destination.table!r} is missing "
                f"contract output column {column.name!r}."
            )
        elif actual_column[0] != _type_name(column.type):
            blockers.append(
                f"Destination table column {column.name!r} has type "
                f"{actual_column[0]!r}, not contract type {column.type!r}."
            )
    return blockers


def _normalized_columns(columns: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return sorted(
        (
            str(column.get("name", "")).casefold(),
            _type_name(str(column.get("type", ""))),
        )
        for column in columns
    )
