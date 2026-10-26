#!/usr/bin/env python3
"""Trusted GitHub Actions helpers for ASIM ingestion-time validation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asim_ingestion.workflow import contracts as workflow_contracts
from asim_ingestion.workflow.contracts import (
    WorkflowContractError,
    _append_summary,
    _load_json,
    _require_target_id,
    _write_github_output,
    _write_json,
    build_matrix_manifest,
    cleanup_target,
    export_static_decision,
    export_target,
    write_error_result,
)
from asim_ingestion.workflow.reporting import (
    _github_command_message,
    _read_optional_json,
    build_report,
    emit_annotations,
    render_summary,
)
from asim_ingestion.azure.common import (
    DEFAULT_DCE_NAME,
    DEFAULT_INGESTION_ENDPOINT,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP,
    DEFAULT_SUBSCRIPTION_ID,
    DEFAULT_WORKSPACE_ID,
    DEFAULT_WORKSPACE_NAME,
    CanaryConfig,
    build_resource_names,
)

__all__ = [
    "CanaryConfig",
    "WorkflowContractError",
    "build_matrix_manifest",
    "build_report",
    "build_resource_names",
    "cleanup_target",
    "emit_annotations",
    "export_static_decision",
    "export_target",
    "main",
    "render_summary",
    "workflow_contracts",
    "write_error_result",
]

def _config_from_args(args: argparse.Namespace) -> CanaryConfig:
    return CanaryConfig(
        subscription_id=args.subscription_id,
        resource_group=args.resource_group,
        workspace_name=args.workspace_name,
        workspace_id=args.workspace_id,
        dce_name=args.dce_name,
        ingestion_endpoint=args.ingestion_endpoint,
        location=args.location,
    )


def _add_canary_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--subscription-id",
        default=os.getenv(
            "ASIM_CANARY_SUBSCRIPTION_ID",
            DEFAULT_SUBSCRIPTION_ID,
        ),
    )
    parser.add_argument(
        "--resource-group",
        default=os.getenv(
            "ASIM_CANARY_RESOURCE_GROUP",
            DEFAULT_RESOURCE_GROUP,
        ),
    )
    parser.add_argument(
        "--workspace-name",
        default=os.getenv(
            "ASIM_CANARY_WORKSPACE_NAME",
            DEFAULT_WORKSPACE_NAME,
        ),
    )
    parser.add_argument(
        "--workspace-id",
        default=os.getenv(
            "ASIM_CANARY_WORKSPACE_ID",
            DEFAULT_WORKSPACE_ID,
        ),
    )
    parser.add_argument(
        "--dce-name",
        default=os.getenv("ASIM_CANARY_DCE_NAME", DEFAULT_DCE_NAME),
    )
    parser.add_argument(
        "--ingestion-endpoint",
        default=os.getenv(
            "ASIM_CANARY_INGESTION_ENDPOINT",
            DEFAULT_INGESTION_ENDPOINT,
        ),
    )
    parser.add_argument(
        "--location",
        default=os.getenv(
            "ASIM_CANARY_LOCATION", DEFAULT_LOCATION
        ),
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    matrix = subparsers.add_parser("matrix")
    matrix.add_argument("--manifest", type=Path, required=True)
    matrix.add_argument("--output", type=Path, required=True)
    matrix.add_argument("--repo-root", type=Path, default=Path("."))
    matrix.add_argument("--max-targets", type=int, default=25)
    matrix.add_argument(
        "--max-fixture-bytes", type=int, default=5 * 1024 * 1024
    )
    matrix.add_argument("--github-output", type=Path)
    matrix.add_argument("--summary", type=Path)

    export = subparsers.add_parser("export-target")
    export.add_argument("--manifest", type=Path, required=True)
    export.add_argument("--target-id", required=True)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--github-output", type=Path)

    static = subparsers.add_parser("export-static")
    static.add_argument("--result", type=Path, required=True)
    static.add_argument("--github-output", type=Path)

    error_result = subparsers.add_parser("error-result")
    error_result.add_argument("--stage", required=True)
    error_result.add_argument("--message", required=True)
    error_result.add_argument("--output", type=Path, required=True)

    cleanup = subparsers.add_parser("cleanup")
    cleanup.add_argument("--target-id", required=True)
    cleanup.add_argument("--pull-request", required=True)
    cleanup.add_argument("--run-id", required=True)
    cleanup.add_argument("--run-attempt", type=int, required=True)
    cleanup.add_argument("--output", type=Path, required=True)
    cleanup.add_argument("--deadline-seconds", type=float, default=120)
    _add_canary_arguments(cleanup)

    report = subparsers.add_parser("report")
    report.add_argument("--target", type=Path, required=True)
    report.add_argument("--static-result", type=Path)
    report.add_argument("--prepared-fixture", type=Path)
    report.add_argument("--validation-result", type=Path)
    report.add_argument("--cleanup-result", type=Path)
    report.add_argument("--repository", required=True)
    report.add_argument("--pull-request", required=True)
    report.add_argument("--run-id", required=True)
    report.add_argument("--run-attempt", required=True)
    report.add_argument("--enforcement-required", required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--summary", type=Path)
    report.add_argument("--github-output", type=Path)
    return parser


def _parse_bool(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no", ""}:
        return False
    raise WorkflowContractError(
        f"Expected a boolean value, received {value!r}."
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    try:
        if args.command == "matrix":
            manifest = _load_json(args.manifest)
            matrix_manifest = build_matrix_manifest(
                manifest,
                repo_root=args.repo_root.resolve(),
                max_targets=args.max_targets,
                max_fixture_bytes=args.max_fixture_bytes,
            )
            _write_json(matrix_manifest, args.output)
            target_ids = [
                target["targetId"]
                for target in matrix_manifest["targets"]
            ]
            _write_github_output(
                args.github_output,
                {
                    "has_targets": str(bool(target_ids)).lower(),
                    "target_ids": json.dumps(
                        target_ids, separators=(",", ":")
                    ),
                },
            )
            _append_summary(
                args.summary,
                "## ASIM ingestion target discovery\n\n"
                f"Selected `{len(target_ids)}` ITP target(s).\n",
            )
            return 0

        if args.command == "export-target":
            export_target(
                _load_json(args.manifest),
                args.target_id,
                target_output=args.output,
                github_output=args.github_output,
            )
            return 0

        if args.command == "export-static":
            export_static_decision(
                _load_json(args.result),
                args.github_output,
            )
            return 0

        if args.command == "error-result":
            write_error_result(
                stage=args.stage,
                message=args.message,
                output=args.output,
            )
            return 0

        if args.command == "cleanup":
            result = cleanup_target(
                target_id=_require_target_id(args.target_id),
                pull_request=args.pull_request,
                run_id=args.run_id,
                run_attempt=args.run_attempt,
                config=_config_from_args(args),
                deadline_seconds=args.deadline_seconds,
            )
            _write_json(result, args.output)
            for item in result["resources"]:
                if item.get("status") == "warning":
                    print(
                        "::warning title=ASIM DCR cleanup warning::"
                        + _github_command_message(item.get("message"))
                    )
            return 0

        target = _load_json(args.target)
        report = build_report(
            target=target,
            static_result=_read_optional_json(args.static_result),
            prepared_fixture=_read_optional_json(
                args.prepared_fixture
            ),
            validation_result=_read_optional_json(
                args.validation_result
            ),
            cleanup_result=_read_optional_json(args.cleanup_result),
            repository=args.repository,
            pull_request=args.pull_request,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            enforcement_required=_parse_bool(
                args.enforcement_required
            ),
        )
        _write_json(report, args.output)
        _append_summary(args.summary, render_summary(report))
        _write_github_output(
            args.github_output,
            {
                "required_failure": str(
                    report["requiredFailure"]
                ).lower(),
                "overall_status": report["status"],
            },
        )
        emit_annotations(report)
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        WorkflowContractError,
        KeyError,
        TypeError,
    ) as exc:
        print(
            f"::error::{_github_command_message(exc)}",
            file=sys.stderr,
        )
        return 1



if __name__ == "__main__":
    raise SystemExit(main())
