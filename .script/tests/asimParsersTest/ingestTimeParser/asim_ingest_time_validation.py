#!/usr/bin/env python3
"""Discover and statically validate ASIM ingestion-time parser targets."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asim_ingestion.parser.common import (
    DuplicateKeyError,
    Finding,
    PairResolution,
    ParserRecord,
    classify_changed_path,
    classify_parser_path,
    load_yaml_file,
    normalize_changed_path,
)
from asim_ingestion.parser import common as parser_common
from asim_ingestion.parser.discovery import (
    build_parser_record,
    build_validation_manifest,
    get_changed_files,
    resolve_query_time_pair,
)
from asim_ingestion.parser.kql import (
    compact_kql,
    mask_kql,
    resolve_source_specific_fixture,
    split_kql_statements,
    split_pipeline,
)
from asim_ingestion.parser.static_validation import validate_ingest_time_parser

__all__ = [
    "DuplicateKeyError",
    "Finding",
    "PairResolution",
    "ParserRecord",
    "build_parser_record",
    "build_validation_manifest",
    "classify_changed_path",
    "classify_parser_path",
    "compact_kql",
    "get_changed_files",
    "load_yaml_file",
    "main",
    "mask_kql",
    "normalize_changed_path",
    "parser_common",
    "resolve_query_time_pair",
    "resolve_source_specific_fixture",
    "split_kql_statements",
    "split_pipeline",
    "validate_ingest_time_parser",
]


def _write_json(payload: dict, output: Path | None) -> None:
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(serialized)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8")
    print(f"Wrote {output}")


def _resolve_repo_path(repo_root: Path, value: str) -> Path:
    normalized = normalize_changed_path(value)
    resolved = (repo_root / normalized).resolve()
    resolved.relative_to(repo_root.resolve())
    return resolved


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    discover = subparsers.add_parser(
        "discover", help="Build the changed-input ITP validation target manifest."
    )
    discover.add_argument("--repo-root", default=".")
    discover.add_argument("--base-ref", default="upstream/master")
    discover.add_argument("--changed-file", action="append", default=[])
    discover.add_argument("--output", type=Path)
    validate = subparsers.add_parser(
        "validate", help="Validate one ingestion-time parser YAML."
    )
    validate.add_argument("path")
    validate.add_argument("--repo-root", default=".")
    validate.add_argument("--query-time-path")
    validate.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        if args.command == "discover":
            changed_files = (
                args.changed_file
                if args.changed_file
                else get_changed_files(repo_root, args.base_ref)
            )
            _write_json(
                build_validation_manifest(repo_root, changed_files), args.output
            )
            return 0
        parser_path = _resolve_repo_path(repo_root, args.path)
        query_time_path = (
            _resolve_repo_path(repo_root, args.query_time_path)
            if args.query_time_path
            else None
        )
        result = validate_ingest_time_parser(
            parser_path, query_time_path=query_time_path, repo_root=repo_root
        )
        _write_json(result, args.output)
        return 0 if result["valid"] else 1
    except (
        DuplicateKeyError,
        OSError,
        subprocess.CalledProcessError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
