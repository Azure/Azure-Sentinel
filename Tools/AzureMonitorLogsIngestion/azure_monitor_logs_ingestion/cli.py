from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential

from .azure import ARM_SCOPE, AzureClient, AzureRequestError
from .contract import load_contract, load_records, validate_records
from .registry import (
    DEFAULT_REGISTRY,
    destination_schema_blockers,
    inspect_managed_resources,
    resolve_contract,
)


def _write_report(path: str | None, report: dict[str, Any]) -> None:
    if not path:
        return
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def _report_path(args: argparse.Namespace) -> str | None:
    if args.command == "inspect":
        return None
    if getattr(args, "report", None):
        return args.report
    source = getattr(args, "payload", None) or args.contract
    return str(Path(source).resolve().parent / "ingestion-report.json")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Provision and use Azure Monitor Logs Ingestion API pipelines for "
            "custom tables and supported Microsoft standard tables."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Check local authentication readiness.")
    resolve = subparsers.add_parser(
        "resolve",
        help="Resolve a registered table capability and print a no-write plan.",
    )
    resolve.add_argument("--table", required=True)
    resolve.add_argument(
        "--required-field",
        action="append",
        default=[],
        metavar="NAME[:TYPE]",
        help="Required source field and optional expected type; repeat as needed.",
    )
    resolve.add_argument(
        "--workspace",
        help="Optional exact workspace ARM ID. Resource checks never discover alternatives.",
    )
    resolve.add_argument(
        "--check-existing",
        action="store_true",
        help="Read only the exact table, DCE, and DCR candidates in --workspace.",
    )
    resolve.add_argument(
        "--report",
        help="Optional local JSON path to persist this dry-run resolution artifact.",
    )

    for name in ("inspect", "provision", "ingest", "verify", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--contract", required=True)
        command.add_argument(
            "--workspace",
            help=(
                "Override the workspace stored in the contract. Use the locked "
                "qualification workspace ARM ID for generated contracts."
            ),
        )
        if name in {"inspect", "ingest", "run"}:
            command.add_argument("--payload")
        if name in {"ingest", "run"}:
            command.add_argument("--max-records", type=int, default=500)
            command.add_argument("--max-bytes", type=int, default=900_000)
        if name in {"provision", "run"}:
            command.add_argument(
                "--principal-id",
                help=(
                    "Optional Entra object ID to grant Monitoring Metrics Publisher "
                    "on the DCR."
                ),
            )
            command.add_argument(
                "--principal-type",
                choices=["User", "Group", "ServicePrincipal", "ForeignGroup", "Device"],
                default="ServicePrincipal",
                help="Entra principal type used with --principal-id.",
            )
        if name in {"verify", "run"}:
            command.add_argument("--lookback-minutes", type=int, default=60)
        if name == "run":
            command.add_argument("--verify", action="store_true")
        if name != "inspect":
            command.add_argument("--report")
    return parser


def doctor() -> dict[str, Any]:
    result: dict[str, Any] = {
        "python": sys.version.split()[0],
        "azureCli": shutil.which("az") is not None,
        "armAuthentication": False,
    }
    try:
        DefaultAzureCredential(
            exclude_interactive_browser_credential=True
        ).get_token(ARM_SCOPE)
        result["armAuthentication"] = True
    except Exception as exc:
        result["authenticationError"] = str(exc)
    result["ready"] = result["armAuthentication"]
    return result


def _parse_required_fields(values: list[str]) -> dict[str, str | None]:
    required: dict[str, str | None] = {}
    for value in values:
        name, separator, column_type = value.partition(":")
        name = name.strip()
        if not name:
            raise ValueError("--required-field must include a field name")
        normalized_type = column_type.strip().lower() if separator else None
        previous = required.get(name)
        if name in required and previous and normalized_type and previous != normalized_type:
            raise ValueError(f"required field {name!r} has conflicting declared types")
        required[name] = normalized_type
    return required


def _resolve(args: argparse.Namespace) -> dict[str, Any]:
    required = _parse_required_fields(args.required_field)
    resolution = resolve_contract(args.table, required)
    if resolution["status"] == "blocked":
        return resolution
    contract = load_contract(
        DEFAULT_REGISTRY.parent / resolution["contractPath"]
    )
    if args.workspace:
        contract = replace(contract, workspace=args.workspace)
        resolution["contract"] = contract.as_dict()

    resolution["targetWorkspace"] = args.workspace
    resolution["writesPerformed"] = False
    if not args.check_existing:
        if args.workspace and not args.workspace.lower().startswith("/subscriptions/"):
            raise ValueError(
                "--workspace for resolve must be an exact workspace ARM resource ID"
            )
        return resolution
    if not args.workspace or not args.workspace.lower().startswith("/subscriptions/"):
        raise ValueError("--check-existing requires an exact --workspace ARM resource ID")

    client = AzureClient()
    workspace = client.resolve_workspace(args.workspace)
    if workspace.id.casefold() != args.workspace.casefold():
        raise RuntimeError("resolved workspace ARM ID does not match the requested target")
    table_id = f"{workspace.id}/tables/{contract.destination.table}"
    table_response = client.request(
        "GET",
        client._resource_url(table_id, "2022-10-01"),
        expected=(200, 404),
    )
    if table_response.status_code == 404:
        resolution["status"] = "blocked"
        resolution["blockers"].append(
            f"Standard table {contract.destination.table!r} is not registered "
            "in the locked workspace."
        )
        resolution["plan"] = None
        resolution["candidateResources"] = {"tableExists": False}
        return resolution
    table_blockers = destination_schema_blockers(contract, table_response.json())
    if table_blockers:
        resolution["status"] = "blocked"
        resolution["blockers"].extend(table_blockers)
        resolution["plan"] = None
        resolution["candidateResources"] = {"tableExists": True}
        return resolution

    dce_id, dcr_id = client._resource_ids(workspace, contract)
    dce_response = client.request(
        "GET", client._resource_url(dce_id, "2023-03-11"), expected=(200, 404)
    )
    dcr_response = client.request(
        "GET", client._resource_url(dcr_id, "2023-03-11"), expected=(200, 404)
    )
    dce = dce_response.json() if dce_response.status_code == 200 else None
    dcr = dcr_response.json() if dcr_response.status_code == 200 else None
    candidate = inspect_managed_resources(
        contract,
        workspace.id,
        dce,
        dcr,
        dce_resource_id=dce_id,
        dcr_resource_id=dcr_id,
    )
    resolution["candidateResources"] = {
        "tableExists": True,
        "dceId": dce_id,
        "dcrId": dcr_id,
        "dceExists": dce is not None,
        "dcrExists": dcr is not None,
    }
    resolution["resourceResolution"] = candidate
    resolution["status"] = candidate["status"]
    if candidate["status"] == "blocked":
        resolution["blockers"].extend(candidate["blockers"])
        resolution["plan"] = None
    return resolution


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "doctor":
        result = doctor()
        print(json.dumps(result, indent=2))
        return 0 if result["ready"] else 1
    if args.command == "resolve":
        try:
            result = _resolve(args)
            if args.report:
                if Path(args.report).exists():
                    raise ValueError(
                        f"resolution report already exists; choose a new path: {args.report}"
                    )
                result["reportPath"] = args.report
                _write_report(args.report, result)
            print(json.dumps(result, indent=2, default=str))
            return 1 if result["status"] == "blocked" else 0
        except (AzureRequestError, OSError, RuntimeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

    try:
        contract = load_contract(args.contract)
        if args.workspace:
            contract = replace(contract, workspace=args.workspace)
        records = load_records(args.payload) if getattr(args, "payload", None) else None
        warnings = validate_records(contract, records) if records else []
        result: dict[str, Any] = {
            "command": args.command,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "succeeded",
            "contract": contract.as_dict(),
            "warnings": warnings,
        }
        if args.command == "inspect":
            result["recordCount"] = len(records) if records else None
            print(json.dumps(result, indent=2))
            return 0

        client = AzureClient()
        if args.command in {"provision", "run"}:
            resources = client.provision(contract)
            result["resources"] = resources.as_dict()
            if args.principal_id:
                result["roleAssignmentId"] = client.authorize(
                    resources.dcr_id,
                    args.principal_id,
                    principal_type=args.principal_type,
                )
        else:
            resources = client.get_resources(contract)
            result["resources"] = resources.as_dict()

        if args.command in {"ingest", "run"}:
            if not records:
                raise ValueError("--payload is required for ingest and run")
            result["ingestion"] = client.ingest(
                contract,
                resources,
                records,
                max_records=args.max_records,
                max_bytes=args.max_bytes,
            )
        if args.command == "verify" or (args.command == "run" and args.verify):
            result["verification"] = client.verify(
                resources,
                contract.destination.table,
                args.lookback_minutes,
            )
            if not result["verification"]["found"]:
                result["status"] = "pending"
        report_path = _report_path(args)
        if report_path:
            result["reportPath"] = report_path
        _write_report(report_path, result)
        print(json.dumps(result, indent=2, default=str))
        return 1 if result["status"] == "pending" else 0
    except (AzureRequestError, OSError, RuntimeError, ValueError) as exc:
        report_path = _report_path(args)
        if report_path:
            _write_report(
                report_path,
                {
                    "command": args.command,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "failed",
                    "error": str(exc),
                },
            )
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
