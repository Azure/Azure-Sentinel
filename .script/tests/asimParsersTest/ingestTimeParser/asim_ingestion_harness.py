#!/usr/bin/env python3
"""Execute prepared ASIM fixtures through raw and parser DCRs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asim_ingestion.azure.client import AzureMonitorClient
from asim_ingestion.azure.common import (
    DEFAULT_DCE_NAME,
    DEFAULT_INGESTION_ENDPOINT,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP,
    DEFAULT_SUBSCRIPTION_ID,
    DEFAULT_WORKSPACE_ID,
    DEFAULT_WORKSPACE_NAME,
    MANAGEMENT_SCOPE,
    HARNESS_RESULT_VERSION,
    CanaryConfig,
    Clock,
    DcrHandle,
    DefaultAzureTokenProvider,
    HarnessError,
    OutcomeUnknownError,
    TokenProvider,
    ValidationRunner,
    _load_json_object,
    _load_parser_yaml,
    _write_json_no_clobber,
    build_exact_timestamp_query,
    build_resource_names,
    build_source_snapshot,
    build_upload_batches,
    count_rows_by_timestamp,
)
from asim_ingestion.azure.runner import AsimIngestionHarness

__all__ = [
    "AsimIngestionHarness",
    "AzureMonitorClient",
    "CanaryConfig",
    "Clock",
    "DcrHandle",
    "DefaultAzureTokenProvider",
    "HarnessError",
    "MANAGEMENT_SCOPE",
    "OutcomeUnknownError",
    "TokenProvider",
    "ValidationRunner",
    "build_exact_timestamp_query",
    "build_resource_names",
    "build_source_snapshot",
    "build_upload_batches",
    "count_rows_by_timestamp",
    "main",
]

def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_fixture", type=Path)
    parser.add_argument("parser_yaml", type=Path)
    parser.add_argument("--snapshot-output", type=Path, required=True)
    parser.add_argument("--result-output", type=Path)
    parser.add_argument(
        "--expected-target-counts", type=Path, required=True
    )
    parser.add_argument(
        "--deadline-seconds", type=float, default=900
    )
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
        "version": HARNESS_RESULT_VERSION,
        "status": "failed",
        "cleanup": [],
    }
    exit_code = 1
    try:
        prepared_fixture = _load_json_object(args.prepared_fixture)
        parser_document = _load_parser_yaml(args.parser_yaml)
        expected_counts = _load_json_object(
            args.expected_target_counts
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
            expected_target_counts=expected_counts,
        )
        exit_code = 0
    except (HarnessError, OSError, ValueError, KeyError, yaml.YAMLError) as exc:
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
        print(f"::error::{exc}", file=sys.stderr)
    if args.result_output is not None:
        _write_json_no_clobber(result, args.result_output)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code



if __name__ == "__main__":
    raise SystemExit(main())
