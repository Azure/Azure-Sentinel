#!/usr/bin/env python3
"""Prepare an ASIM CSV fixture with exact, run-specific Kusto timestamps."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asim_ingestion.fixtures import data as fixture_data
from asim_ingestion.fixtures.data import (
    MAX_FIXTURE_BYTES,
    MAX_SCHEMA_BYTES,
    _write_json,
    assert_disjoint_timestamp_sets,
    convert_rows_to_schema,
    infer_schema,
    load_fixture_csv,
    prepare_fixture,
)
from asim_ingestion.fixtures.timestamps import (
    MAX_SAMPLE_SPAN_TICKS,
    TimestampNamespace,
    allocate_timestamp_namespaces,
    build_run_key,
    compute_latest_rebased_tick,
    datetime_to_ticks,
    parse_kusto_datetime_ticks,
    rebase_time_generated,
    ticks_to_kusto_datetime,
    timestamp_quantum_for_target_count,
)

__all__ = [
    "MAX_FIXTURE_BYTES",
    "MAX_SAMPLE_SPAN_TICKS",
    "MAX_SCHEMA_BYTES",
    "TimestampNamespace",
    "allocate_timestamp_namespaces",
    "assert_disjoint_timestamp_sets",
    "build_run_key",
    "compute_latest_rebased_tick",
    "convert_rows_to_schema",
    "datetime_to_ticks",
    "fixture_data",
    "infer_schema",
    "load_fixture_csv",
    "main",
    "parse_kusto_datetime_ticks",
    "prepare_fixture",
    "rebase_time_generated",
    "ticks_to_kusto_datetime",
    "timestamp_quantum_for_target_count",
    "_write_json",
]


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser(
        "prepare", help="Prepare one ASIM fixture artifact."
    )
    prepare.add_argument("fixture", type=Path)
    prepare.add_argument("--expected-source-raw-table", required=True)
    prepare.add_argument("--target-id", required=True)
    prepare.add_argument("--target-group", required=True)
    prepare.add_argument("--repository", default="Azure/Azure-Sentinel")
    prepare.add_argument("--pull-request", default="0")
    prepare.add_argument("--run-id", required=True)
    prepare.add_argument("--run-attempt", type=int, default=1)
    prepare.add_argument("--target-slot", type=int, default=0)
    prepare.add_argument("--target-count", type=int, default=1)
    prepare.add_argument("--schema-path", type=Path)
    prepare.add_argument("--now")
    prepare.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    try:
        if args.output is not None and args.output.resolve() == args.fixture.resolve():
            raise ValueError("Output path must not replace the source fixture.")
        now_ticks = parse_kusto_datetime_ticks(args.now) if args.now else None
        artifact = prepare_fixture(
            fixture_path=args.fixture,
            expected_source_raw_table=args.expected_source_raw_table,
            target_id=args.target_id,
            target_group=args.target_group,
            repository=args.repository,
            pull_request=args.pull_request,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            target_slot=args.target_slot,
            target_count=args.target_count,
            schema_path=args.schema_path,
            now_ticks=now_ticks,
        )
        _write_json(artifact, args.output)
        return 0
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
