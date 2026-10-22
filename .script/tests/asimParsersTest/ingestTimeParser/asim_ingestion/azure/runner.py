"""Orchestrate raw ingestion, source snapshotting, parser DCR execution, and cleanup."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..parser.kql import compact_kql
from .client import AzureMonitorClient
from .common import (
    HARNESS_RESULT_VERSION,
    DcrHandle,
    HarnessError,
    ValidationRunner,
    _validate_timestamp,
    _write_json_no_clobber,
    build_resource_names,
    build_source_snapshot,
    count_rows_by_timestamp,
)

class AsimIngestionHarness(AzureMonitorClient):
    def run(
        self,
        prepared_fixture: Mapping[str, Any],
        parser_document: Mapping[str, Any],
        *,
        snapshot_output: Path,
        expected_target_counts: Mapping[str, int] | None = None,
        validation_runner: ValidationRunner | None = None,
        query_time_document: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.request_attempts = []
        self.stage_timings = {}
        target_id = str(prepared_fixture["targetId"])
        namespace = prepared_fixture["namespace"]
        source_table = str(prepared_fixture["sourceRawTable"])
        target_table = str(parser_document["TargetASIMTable"])
        parser_query = compact_kql(
            str(parser_document["ParserQuery"])
        )
        if str(parser_document["SourceRawTable"]) != source_table:
            raise ValueError(
                "Prepared fixture SourceRawTable does not match parser."
            )
        timestamps = list(namespace["timestampValues"])
        rows = list(prepared_fixture["rows"])
        schema = list(prepared_fixture["schema"])
        if len(rows) != int(prepared_fixture["rowCount"]):
            raise ValueError("Prepared fixture rowCount does not match rows.")
        if set(count_rows_by_timestamp(rows)) != set(timestamps):
            raise ValueError(
                "Prepared fixture timestamps do not match its namespace."
            )
        if (
            validation_runner is not None
            and expected_target_counts is not None
        ):
            raise ValueError(
                "Use either validation_runner or expected_target_counts, "
                "not both."
            )
        normalized_target_counts: dict[str, int] | None = None
        if expected_target_counts is not None:
            normalized_target_counts = {
                _validate_timestamp(str(timestamp)): int(count)
                for timestamp, count in expected_target_counts.items()
            }
            if set(normalized_target_counts) != set(timestamps):
                raise ValueError(
                    "Expected target counts must include every prepared "
                    "timestamp exactly once."
                )
            if any(
                count < 0
                for count in normalized_target_counts.values()
            ):
                raise ValueError(
                    "Expected target counts cannot contain negative values."
                )

        names = build_resource_names(
            target_id,
            str(namespace.get("pullRequest", "0")),
            str(namespace["runId"]),
            int(namespace["runAttempt"]),
        )
        raw_handle: DcrHandle | None = None
        parser_handle: DcrHandle | None = None
        attempted_dcr_ids: list[str] = []
        cleanup: list[dict[str, Any]] = []
        result: dict[str, Any] = {
            "version": HARNESS_RESULT_VERSION,
            "status": "failed",
            "targetId": target_id,
            "sourceRawTable": source_table,
            "targetASIMTable": target_table,
            "rawDcr": None,
            "parserDcr": None,
            "rawUpload": [],
            "parserUpload": [],
            "snapshotPath": str(snapshot_output),
            "filterValidation": None,
            "outputValidation": None,
            "cleanup": cleanup,
            "telemetry": {
                "stageTimingsSeconds": self.stage_timings,
                "requestAttempts": self.request_attempts,
            },
        }
        self.last_result = result
        run_started = self.clock.monotonic()
        try:
            with self._stage("raw-table"):
                self.ensure_raw_table(source_table, schema)
            raw_resource_id = self.dcr_resource_id(names["rawDcr"])
            attempted_dcr_ids.append(raw_resource_id)
            with self._stage("raw-dcr"):
                raw_handle = self.create_dcr(
                    name=names["rawDcr"],
                    stream_name=names["rawStream"],
                    destination_name=names["destination"],
                    schema=schema,
                    transform_kql="source",
                    output_stream=(
                        f"Custom-{source_table}"
                        if source_table.lower().endswith("_cl")
                        else f"Microsoft-{source_table}"
                    ),
                )
            result["rawDcr"] = raw_handle.to_dict()
            raw_counts = count_rows_by_timestamp(rows)
            with self._stage("raw-upload"):
                result["rawUpload"] = self.upload_rows(
                    raw_handle,
                    rows,
                    reconcile_table=source_table,
                    expected_counts_by_timestamp=raw_counts,
                )
            with self._stage("raw-visibility"):
                raw_query_table = self.wait_for_exact_rows(
                    source_table,
                    timestamps,
                    raw_counts,
                    stage="raw-visibility",
                )
            with self._stage("source-snapshot"):
                snapshot = build_source_snapshot(
                    target_id=target_id,
                    table_name=source_table,
                    timestamps=timestamps,
                    query_table=raw_query_table,
                )
                _write_json_no_clobber(snapshot, snapshot_output)
            result["snapshot"] = {
                "rowCount": snapshot["rowCount"],
                "timestampSetHash": snapshot["timestampSetHash"],
                "excludedColumns": snapshot["excludedColumns"],
            }
            if validation_runner is not None:
                with self._stage("filter-validation"):
                    filter_validation = dict(
                        validation_runner.evaluate_filter(
                            self,
                            snapshot,
                            parser_document,
                        )
                    )
                selected_counts = filter_validation.get(
                    "selectedCountsByTimestamp"
                )
                if not isinstance(selected_counts, Mapping):
                    raise ValueError(
                        "Validation runner did not return "
                        "selectedCountsByTimestamp."
                    )
                normalized_target_counts = {
                    _validate_timestamp(str(timestamp)): int(count)
                    for timestamp, count in selected_counts.items()
                }
                result["filterValidation"] = filter_validation
            if normalized_target_counts is None:
                raise ValueError(
                    "Expected target counts or a validation runner "
                    "is required."
                )
            if set(normalized_target_counts) != set(timestamps):
                raise ValueError(
                    "Expected target counts must include every prepared "
                    "timestamp exactly once."
                )
            if any(
                count < 0
                for count in normalized_target_counts.values()
            ):
                raise ValueError(
                    "Expected target counts cannot contain negative values."
                )

            parser_resource_id = self.dcr_resource_id(
                names["parserDcr"]
            )
            attempted_dcr_ids.append(parser_resource_id)
            with self._stage("parser-dcr"):
                parser_handle = self.create_dcr(
                    name=names["parserDcr"],
                    stream_name=names["parserStream"],
                    destination_name=names["destination"],
                    schema=snapshot["schema"],
                    transform_kql=parser_query,
                    output_stream=f"Microsoft-{target_table}",
                )
            result["parserDcr"] = parser_handle.to_dict()
            with self._stage("parser-upload"):
                result["parserUpload"] = self.upload_rows(
                    parser_handle,
                    snapshot["rows"],
                    reconcile_table=target_table,
                    expected_counts_by_timestamp=normalized_target_counts,
                )
            with self._stage("target-visibility"):
                self.wait_for_exact_rows(
                    target_table,
                    list(normalized_target_counts),
                    normalized_target_counts,
                    stage="target-visibility",
                )
            if validation_runner is not None:
                with self._stage("output-validation"):
                    output_validation = dict(
                        validation_runner.validate_outputs(
                            self,
                            snapshot,
                            parser_document,
                            query_time_document,
                        )
                    )
                    result["outputValidation"] = output_validation
                    if output_validation.get("status") != "passed":
                        failure = output_validation.get("failure")
                        if isinstance(failure, Mapping):
                            stage = str(
                                failure.get("stage")
                                or "output-validation"
                            )
                            message = str(
                                failure.get("message")
                                or "Output validation failed."
                            )
                            details = failure.get("details")
                        else:
                            stage = "output-validation"
                            message = "Output validation failed."
                            details = output_validation
                        raise HarnessError(
                            stage,
                            message,
                            details=details,
                        )
            result["status"] = "completed"
            return result
        finally:
            with self._stage("cleanup"):
                for resource_id in reversed(attempted_dcr_ids):
                    cleanup.append(self.delete_dcr(resource_id))
            result["telemetry"]["elapsedSeconds"] = round(
                self.clock.monotonic() - run_started,
                3,
            )
