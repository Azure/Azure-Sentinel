"""Orchestrate raw ingestion, source snapshotting, parser DCR execution, and cleanup."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..parser.kql import compact_kql
from .client import AzureMonitorClient
from .common import (
    HARNESS_RESULT_VERSION,
    HarnessError,
    ValidationRunner,
    _validate_timestamp,
    _write_json_no_clobber,
    build_fixture_snapshot,
    build_observed_query_rows,
    build_resource_names,
    count_rows_by_timestamp,
)


def _error_payload(exc: HarnessError) -> dict[str, Any]:
    details = exc.details
    if isinstance(details, Mapping) and "observedQueryTable" in details:
        details = dict(details)
        details.pop("observedQueryTable", None)
    return {
        "type": type(exc).__name__,
        "stage": exc.stage,
        "message": str(exc),
        "statusCode": exc.status_code,
        "details": details,
    }


def _record_qtp_observation(
    qtp_replay: dict[str, Any],
    query_table: Any,
) -> None:
    if not isinstance(query_table, Mapping):
        return
    observed = build_observed_query_rows(
        query_table,
        stage="raw-visibility",
    )
    qtp_replay["observedSchema"] = observed["schema"]
    qtp_replay["observedRows"] = observed["rows"]
    qtp_replay["observedCountsByTimestamp"] = observed[
        "countsByTimestamp"
    ]


def _block_optional_parity(
    output_validation: Mapping[str, Any],
    *,
    detail: str,
    qtp_replay: Mapping[str, Any],
) -> dict[str, Any]:
    blocked = dict(output_validation)
    blocked["queryTimeExecution"] = {
        "status": "blocked",
        "detail": detail,
    }
    blocked["parity"] = {
        "status": "blocked",
        "detail": detail,
    }
    blocked["qtpSourceReplay"] = qtp_replay
    return blocked


def _output_failure(
    output_validation: Mapping[str, Any],
) -> HarnessError | None:
    if output_validation.get("status") == "passed":
        return None
    failure = output_validation.get("failure")
    if isinstance(failure, Mapping):
        return HarnessError(
            str(failure.get("stage") or "output-validation"),
            str(
                failure.get("message")
                or "Output validation failed."
            ),
            details=failure.get("details"),
        )
    return HarnessError(
        "output-validation",
        "Output validation failed.",
        details=output_validation,
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
        input_stream = str(
            parser_document.get("InputStream") or ""
        ).strip()
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
            "qtpSourceReplay": {
                "status": (
                    "pending"
                    if query_time_document is not None
                    else "not-applicable"
                ),
                "inputStream": input_stream or None,
                "error": None,
                "observedSchema": [],
                "observedRows": [],
                "observedCountsByTimestamp": {},
            },
            "cleanup": cleanup,
            "telemetry": {
                "stageTimingsSeconds": self.stage_timings,
                "requestAttempts": self.request_attempts,
            },
        }
        self.last_result = result
        run_started = self.clock.monotonic()
        try:
            with self._stage("source-snapshot"):
                snapshot = build_fixture_snapshot(
                    target_id=target_id,
                    table_name=source_table,
                    timestamps=timestamps,
                    schema=schema,
                    fixture_rows=rows,
                )
                _write_json_no_clobber(snapshot, snapshot_output)
            result["snapshot"] = {
                "authority": snapshot["authority"],
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
                            None,
                        )
                    )
                    result["outputValidation"] = output_validation
                    output_failure = _output_failure(
                        output_validation
                    )
                    if output_failure is not None:
                        raise output_failure

            if (
                query_time_document is not None
                and validation_runner is not None
            ):
                qtp_replay = result["qtpSourceReplay"]
                try:
                    if (
                        not input_stream
                        or input_stream.casefold() == "none"
                    ):
                        raise HarnessError(
                            "raw-dcr",
                            "QTP source replay requires a non-none "
                            "InputStream.",
                        )
                    with self._stage("raw-table"):
                        self.ensure_raw_table(
                            source_table,
                            schema,
                        )
                    raw_resource_id = self.dcr_resource_id(
                        names["rawDcr"]
                    )
                    attempted_dcr_ids.append(raw_resource_id)
                    with self._stage("raw-dcr"):
                        raw_handle = self.create_dcr(
                            name=names["rawDcr"],
                            stream_name=names["rawStream"],
                            destination_name=names["destination"],
                            schema=schema,
                            transform_kql="source",
                            output_stream=input_stream,
                        )
                except HarnessError as exc:
                    qtp_replay["status"] = "warning"
                    qtp_replay["error"] = _error_payload(exc)
                else:
                    result["rawDcr"] = raw_handle.to_dict()
                    raw_counts = count_rows_by_timestamp(rows)
                    try:
                        with self._stage("raw-upload"):
                            result["rawUpload"] = self.upload_rows(
                                raw_handle,
                                rows,
                                reconcile_table=source_table,
                                expected_counts_by_timestamp=raw_counts,
                            )
                        with self._stage("raw-visibility"):
                            observed_query_table = (
                                self.wait_for_exact_rows(
                                    source_table,
                                    timestamps,
                                    raw_counts,
                                    stage="raw-visibility",
                                )
                            )
                        _record_qtp_observation(
                            qtp_replay,
                            observed_query_table,
                        )
                        qtp_replay["status"] = "passed"
                    except HarnessError as exc:
                        details = exc.details
                        if isinstance(details, Mapping):
                            _record_qtp_observation(
                                qtp_replay,
                                details.get("observedQueryTable"),
                            )
                            cleaned_details = dict(details)
                            cleaned_details.pop(
                                "observedQueryTable",
                                None,
                            )
                            exc.details = cleaned_details
                        qtp_replay["status"] = "failed"
                        qtp_replay["error"] = _error_payload(exc)
                        result["outputValidation"] = (
                            _block_optional_parity(
                                result["outputValidation"],
                                detail=(
                                    "Blocked by QTP raw ingestion "
                                    "failure."
                                ),
                                qtp_replay=qtp_replay,
                            )
                        )
                        raise

            if (
                validation_runner is not None
                and query_time_document is not None
            ):
                with self._stage("output-validation"):
                    qtp_replay = result["qtpSourceReplay"]
                    if qtp_replay.get("status") == "warning":
                        output_validation = _block_optional_parity(
                            result["outputValidation"],
                            detail=(
                                "Skipped because QTP raw DCR "
                                "creation failed."
                            ),
                            qtp_replay=qtp_replay,
                        )
                    else:
                        parity_validation = dict(
                            validation_runner.validate_parity(
                                self,
                                snapshot,
                                parser_document,
                                query_time_document,
                            )
                        )
                        output_validation = dict(
                            result["outputValidation"]
                        )
                        output_validation.update(
                            parity_validation
                        )
                    result["outputValidation"] = output_validation
                    output_failure = _output_failure(
                        output_validation
                    )
                    if output_failure is not None:
                        raise output_failure
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
