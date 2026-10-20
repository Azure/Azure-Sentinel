#!/usr/bin/env python3
"""Validate ASIM ingestion-time output and optional query-time parity."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asim_ingestion.parser.common import load_yaml_file
from asim_ingestion.runtime.parity import compare_parser_outputs
from asim_ingestion.runtime.queries import (
    ValidationError,
    build_asim_tester_query,
    build_exact_slice_expression,
    build_filter_count_query,
    build_query_time_parser_query,
)
from asim_ingestion.runtime.validator import AsimIngestionValidator
from asim_ingestion.azure.common import (
    DEFAULT_DCE_NAME,
    DEFAULT_INGESTION_ENDPOINT,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP,
    DEFAULT_SUBSCRIPTION_ID,
    DEFAULT_WORKSPACE_ID,
    DEFAULT_WORKSPACE_NAME,
    CanaryConfig,
    DefaultAzureTokenProvider,
    HarnessError,
)
from asim_ingestion.azure.runner import AsimIngestionHarness

VALIDATION_RESULT_VERSION = 1

__all__ = [
    "AsimIngestionValidator",
    "ValidationError",
    "build_asim_tester_query",
    "build_exact_slice_expression",
    "build_filter_count_query",
    "build_query_time_parser_query",
    "compare_parser_outputs",
    "main",
]

def _load_json_object(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return document


def _write_json(payload: Mapping[str, Any], path: Path | None) -> None:
    serialized = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n"
    )
    if path is None:
        sys.stdout.write(serialized)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized, encoding="utf-8")


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_fixture", type=Path)
    parser.add_argument("parser_yaml", type=Path)
    parser.add_argument("--query-time-yaml", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--snapshot-output", type=Path, required=True)
    parser.add_argument("--result-output", type=Path)
    parser.add_argument("--deadline-seconds", type=float, default=900)
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    harness: AsimIngestionHarness | None = None
    result: dict[str, Any] = {
        "version": VALIDATION_RESULT_VERSION,
        "status": "failed",
    }
    try:
        prepared_fixture = _load_json_object(args.prepared_fixture)
        parser_document = load_yaml_file(args.parser_yaml)
        query_time_document = (
            load_yaml_file(args.query_time_yaml)
            if args.query_time_yaml is not None
            else None
        )
        config = CanaryConfig(
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            workspace_name=args.workspace_name,
            workspace_id=args.workspace_id,
            dce_name=args.dce_name,
            ingestion_endpoint=args.ingestion_endpoint,
            location=args.location,
        )
        harness = AsimIngestionHarness(
            config,
            DefaultAzureTokenProvider(),
            deadline_seconds=args.deadline_seconds,
        )
        result = harness.run(
            prepared_fixture,
            parser_document,
            snapshot_output=args.snapshot_output,
            validation_runner=AsimIngestionValidator(args.repo_root),
            query_time_document=query_time_document,
        )
        exit_code = 0
    except (
        HarnessError,
        ValidationError,
        OSError,
        ValueError,
        KeyError,
        yaml.YAMLError,
    ) as exc:
        if harness is not None and harness.last_result is not None:
            result = dict(harness.last_result)
            result["status"] = "failed"
        result["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        if isinstance(exc, HarnessError):
            result["error"].update(
                {
                    "stage": exc.stage,
                    "statusCode": exc.status_code,
                    "details": exc.details,
                }
            )
        elif isinstance(exc, ValidationError):
            result["error"].update(
                {
                    "stage": exc.stage,
                    "details": exc.details,
                }
            )
        print(f"::error::{exc}", file=sys.stderr)
        exit_code = 1
    _write_json(result, args.result_output)
    return exit_code



if __name__ == "__main__":
    raise SystemExit(main())
