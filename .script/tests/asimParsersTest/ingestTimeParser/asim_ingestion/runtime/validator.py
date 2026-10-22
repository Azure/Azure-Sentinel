"""Orchestrate filter coverage, ASIM data checks, and optional parity."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from .parity import compare_parser_outputs
from .queries import (
    QueryClient,
    ValidationError,
    _count_snapshot_rows,
    _evaluate_tester_result,
    _is_source_passthrough,
    _load_tester_query,
    _normalize_query_table,
    _parse_filter_counts,
    build_asim_tester_query,
    build_exact_slice_expression,
    build_filter_count_query,
    build_query_time_parser_query,
)


def _intersect_schemas(
    qtp_schema: Sequence[Mapping[str, str]],
    itp_schema: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    itp_types = {
        str(column["name"]): str(column["type"])
        for column in itp_schema
    }
    return [
        {
            "name": str(column["name"]),
            "type": str(column["type"]),
        }
        for column in qtp_schema
        if itp_types.get(str(column["name"]))
        == str(column["type"])
    ]


def _filter_rows(
    rows: Sequence[Mapping[str, Any]],
    schema: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    columns = [str(column["name"]) for column in schema]
    return [
        {
            column: row.get(column)
            for column in columns
        }
        for row in rows
    ]


class AsimIngestionValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.data_tester_query = _load_tester_query(
            self.repo_root, "ASimDataTester"
        )

    def evaluate_filter(
        self,
        query_client: QueryClient,
        source_snapshot: Mapping[str, Any],
        parser_document: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        source_table = parser_document.get("SourceRawTable")
        filter_query = parser_document.get("ParserFilterQuery")
        timestamps = source_snapshot.get("timestampValues")
        if (
            not isinstance(source_table, str)
            or not isinstance(filter_query, str)
            or not isinstance(timestamps, list)
        ):
            raise ValidationError(
                "filter",
                "Parser or source snapshot is missing filter metadata.",
            )
        raw_counts = _count_snapshot_rows(source_snapshot)
        query = build_filter_count_query(
            source_table,
            [str(value) for value in timestamps],
            filter_query,
        )
        selected_counts = _parse_filter_counts(
            query_client.query_kql(query, stage="filter"),
            [str(value) for value in timestamps],
        )
        overages = {
            timestamp: {
                "raw": raw_counts[timestamp],
                "selected": selected_counts[timestamp],
            }
            for timestamp in raw_counts
            if selected_counts[timestamp] > raw_counts[timestamp]
        }
        if overages:
            raise ValidationError(
                "filter",
                "ParserFilterQuery selected more rows than exist in the "
                "raw snapshot.",
                details={"overages": overages},
            )
        selected = sum(selected_counts.values())
        raw = sum(raw_counts.values())
        rejected = raw - selected
        passthrough = _is_source_passthrough(filter_query)
        if selected <= 0:
            raise ValidationError(
                "filter",
                "ParserFilterQuery must select at least one fixture row.",
            )
        if not passthrough and rejected <= 0:
            raise ValidationError(
                "filter",
                "A selective ParserFilterQuery fixture must contain at "
                "least one rejected row.",
            )
        return {
            "status": "passed",
            "mode": "pass-through" if passthrough else "selective",
            "rawRowCount": raw,
            "selectedRowCount": selected,
            "rejectedRowCount": rejected,
            "rawCountsByTimestamp": raw_counts,
            "selectedCountsByTimestamp": selected_counts,
        }

    def validate_outputs(
        self,
        query_client: QueryClient,
        source_snapshot: Mapping[str, Any],
        parser_document: Mapping[str, Any],
        query_time_document: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        target_table = parser_document.get("TargetASIMTable")
        source_table = parser_document.get("SourceRawTable")
        schema_name = (
            parser_document.get("Normalization", {}).get("Schema")
            if isinstance(
                parser_document.get("Normalization"), Mapping
            )
            else None
        )
        timestamps = source_snapshot.get("timestampValues")
        if (
            not isinstance(target_table, str)
            or not isinstance(source_table, str)
            or not isinstance(schema_name, str)
            or not isinstance(timestamps, list)
        ):
            raise ValidationError(
                "output-validation",
                "Parser or source snapshot is missing output metadata.",
            )
        timestamp_values = [str(value) for value in timestamps]

        data_query = build_asim_tester_query(
            tester_name="ASimDataTester",
            tester_query=self.data_tester_query,
            target_table=target_table,
            timestamps=timestamp_values,
            schema_name=schema_name,
        )
        data_test = _evaluate_tester_result(
            query_client.query_kql(data_query, stage="asim-data"),
            "ASimDataTester",
        )
        if data_test["status"] == "failed":
            raise ValidationError(
                "asim-data",
                "ASimDataTester reported errors.",
                details=data_test,
            )

        result: dict[str, Any] = {
            "status": "passed",
            "schemaValidation": {
                "status": "passed",
                "authority": "parser-dcr-output-stream",
            },
            "dataTest": data_test,
            "queryTimeExecution": {
                "status": "not-applicable",
            },
            "parity": {
                "status": "not-applicable",
            },
        }
        if query_time_document is None:
            return result

        qtp_query = build_query_time_parser_query(
            query_time_document,
            source_table,
            timestamp_values,
        )
        qtp_schema, qtp_rows = _normalize_query_table(
            query_client.query_kql(
                qtp_query, stage="qtp-execution"
            ),
            "qtp-execution",
        )
        result["queryTimeExecution"] = {
            "status": "passed",
            "rowCount": len(qtp_rows),
        }
        itp_schema, itp_rows = _normalize_query_table(
            query_client.query_kql(
                build_exact_slice_expression(
                    target_table,
                    timestamp_values,
                ),
                stage="target-output",
            ),
            "target-output",
        )
        intersect_schema = _intersect_schemas(
            qtp_schema,
            itp_schema,
        )
        qtp_rows_filtered = _filter_rows(
            qtp_rows,
            intersect_schema,
        )
        itp_rows_filtered = _filter_rows(
            itp_rows,
            intersect_schema,
        )
        result.update(
            {
                "qtp_schema": qtp_schema,
                "qtp_rows": qtp_rows,
                "itp_schema": itp_schema,
                "itp_rows": itp_rows,
                "intersect_schema": intersect_schema,
                "qtp_rows_filtered": qtp_rows_filtered,
                "itp_rows_filtered": itp_rows_filtered,
            }
        )
        parity = compare_parser_outputs(
            expected_schema=intersect_schema,
            expected_rows=qtp_rows_filtered,
            actual_schema=intersect_schema,
            actual_rows=itp_rows_filtered,
        )
        result["parity"] = parity
        if parity["status"] != "passed":
            result["status"] = "failed"
            result["failure"] = {
                "stage": "parity",
                "message": (
                    "Query-time and ingestion-time outputs differ."
                ),
                "details": parity,
            }
        return result
