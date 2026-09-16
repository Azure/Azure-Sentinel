from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential

from .azure import ARM_SCOPE, AzureClient, AzureRequestError
from .contract import load_contract, load_records, validate_records


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

    for name in ("inspect", "provision", "ingest", "verify", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--contract", required=True)
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


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "doctor":
        result = doctor()
        print(json.dumps(result, indent=2))
        return 0 if result["ready"] else 1

    try:
        contract = load_contract(args.contract)
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
