import importlib.util
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import requests


MODULE_PATH = Path(__file__).resolve().parents[1] / "asim_ingestion_harness.py"
SPEC = importlib.util.spec_from_file_location(
    "asim_ingestion_harness", MODULE_PATH
)
HARNESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HARNESS
SPEC.loader.exec_module(HARNESS)


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self.payload = payload
        self.headers = headers or {}
        self.text = (
            ""
            if payload is None
            else json.dumps(payload, separators=(",", ":"))
        )

    def json(self):
        if self.payload is None:
            raise ValueError("No JSON body")
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append(
            {"method": method, "url": url, **kwargs}
        )
        if not self.responses:
            raise AssertionError(f"Unexpected request: {method} {url}")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        if callable(response):
            return response(method, url, kwargs)
        return response


class FakeTokenProvider:
    def __init__(self):
        self.scopes = []

    def get_token(self, scope):
        self.scopes.append(scope)
        return f"token-for-{scope}"


class FakeValidationRunner:
    def __init__(
        self,
        timestamp,
        output_result=None,
        parity_result=None,
    ):
        self.timestamp = timestamp
        self.output_result = output_result
        self.parity_result = parity_result
        self.filter_calls = 0
        self.output_calls = 0
        self.parity_calls = 0

    def evaluate_filter(
        self, query_client, source_snapshot, parser_document
    ):
        self.filter_calls += 1
        return {
            "status": "passed",
            "selectedCountsByTimestamp": {
                self.timestamp: 1,
            },
        }

    def validate_outputs(
        self,
        query_client,
        source_snapshot,
        parser_document,
        query_time_document,
    ):
        self.output_calls += 1
        return self.output_result or {
            "status": "passed",
            "parity": {"status": "not-applicable"},
        }

    def validate_parity(
        self,
        query_client,
        source_snapshot,
        parser_document,
        query_time_document,
    ):
        self.parity_calls += 1
        return self.parity_result or {
            "status": "passed",
            "queryTimeExecution": {
                "status": "passed",
                "rowCount": 1,
            },
            "parity": {"status": "passed"},
        }


class FailingFilterRunner:
    def evaluate_filter(
        self, query_client, source_snapshot, parser_document
    ):
        raise RuntimeError("filter validation failed")

    def validate_outputs(
        self,
        query_client,
        source_snapshot,
        parser_document,
        query_time_document,
    ):
        raise AssertionError("Output validation must not run.")

    def validate_parity(
        self,
        query_client,
        source_snapshot,
        parser_document,
        query_time_document,
    ):
        raise AssertionError("Parity validation must not run.")


class FakeClock:
    def __init__(self):
        self.value = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.value

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.value += seconds


def query_payload(columns, rows):
    return {"tables": [{"columns": columns, "rows": rows}]}


class IngestionHarnessUnitTests(unittest.TestCase):
    def config(self):
        return HARNESS.CanaryConfig(
            subscription_id="subscription",
            resource_group="resource-group",
            workspace_name="workspace",
            workspace_id="workspace-id",
            dce_name="dce",
            ingestion_endpoint="https://example.ingest.monitor.azure.com",
            location="eastus2euap",
        )

    def harness(self, responses, deadline=900):
        session = FakeSession(responses)
        clock = FakeClock()
        harness = HARNESS.AsimIngestionHarness(
            self.config(),
            FakeTokenProvider(),
            session=session,
            clock=clock,
            deadline_seconds=deadline,
            poll_delays=(1, 2, 3),
            random_source=__import__("random").Random(0),
        )
        return harness, session, clock

    def test_builds_exact_timestamp_query(self):
        query = HARNESS.build_exact_timestamp_query(
            "Contoso_CL",
            [
                "2026-10-16T19:55:00.1234567Z",
                "2026-10-16T19:54:59.1234567Z",
                "2026-10-16T19:55:00.1234567Z",
            ],
        )
        self.assertIn("datatable(_AsimTestTime:datetime)", query)
        self.assertIn("Contoso_CL", query)
        self.assertEqual(
            1, query.count("2026-10-16T19:55:00.1234567Z")
        )
        self.assertIn("join kind=inner", query)

    def test_batches_keep_noncontiguous_equal_timestamps_together(self):
        rows = [
            {
                "TimeGenerated": "2026-10-16T19:55:00.0000001Z",
                "Value": "first",
            },
            {
                "TimeGenerated": "2026-10-16T19:54:59.0000001Z",
                "Value": "middle",
            },
            {
                "TimeGenerated": "2026-10-16T19:55:00.0000001Z",
                "Value": "second",
            },
        ]
        batches = HARNESS.build_upload_batches(rows, max_bytes=150)
        first_location = next(
            batch_index
            for batch_index, batch in enumerate(batches)
            if any(row["Value"] == "first" for row in batch)
        )
        second_location = next(
            batch_index
            for batch_index, batch in enumerate(batches)
            if any(row["Value"] == "second" for row in batch)
        )
        self.assertEqual(first_location, second_location)

    def test_dcr_creation_polls_404_then_succeeds(self):
        harness, session, clock = self.harness(
            [
                FakeResponse(202),
                FakeResponse(404),
                FakeResponse(
                    200,
                    {
                        "id": "/subscriptions/s/dcr",
                        "properties": {
                            "provisioningState": "Succeeded",
                            "immutableId": "dcr-immutable",
                        },
                    },
                ),
            ]
        )
        handle = harness.create_dcr(
            name="test-dcr",
            stream_name="Custom-test",
            destination_name="destination",
            schema=[
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            transform_kql="source",
            output_stream="Custom-Contoso_CL",
        )
        self.assertEqual("dcr-immutable", handle.immutable_id)
        self.assertEqual([1], clock.sleeps)
        put_body = session.calls[0]["json"]
        flow = put_body["properties"]["dataFlows"][0]
        self.assertEqual("source", flow["transformKql"])
        self.assertEqual("Custom-Contoso_CL", flow["outputStream"])

    def test_management_request_retries_429(self):
        harness, _, clock = self.harness(
            [
                FakeResponse(429, headers={"Retry-After": "2"}),
                FakeResponse(200, {"properties": {}}),
            ]
        )
        response = harness._request(
            "GET",
            "https://management.azure.com/resource",
            scope=HARNESS.MANAGEMENT_SCOPE,
            stage="test",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual([2.0], clock.sleeps)
        self.assertEqual(
            2, harness.request_attempts[0]["attemptCount"]
        )

    def test_wait_for_rows_polls_until_exact_count(self):
        harness, _, clock = self.harness(
            [
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [],
                    ),
                ),
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [["2026-10-16T19:55:00.1234567Z"]],
                    ),
                ),
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [["2026-10-16T19:55:00.1234567Z"]],
                    ),
                ),
            ]
        )
        table = harness.wait_for_exact_rows(
            "Contoso_CL",
            ["2026-10-16T19:55:00.1234567Z"],
            {"2026-10-16T19:55:00.1234567Z": 1},
            stage="raw-visibility",
        )
        self.assertEqual(1, len(table["rows"]))
        self.assertEqual([1, 5], clock.sleeps)

    def test_wait_for_rows_fails_on_contamination(self):
        harness, _, _ = self.harness(
            [
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [
                            ["2026-10-16T19:55:00.1234567Z"],
                            ["2026-10-16T19:55:00.1234567Z"],
                        ],
                    ),
                )
            ]
        )
        with self.assertRaisesRegex(
            HARNESS.HarnessError, "more rows than expected"
        ):
            harness.wait_for_exact_rows(
                "Contoso_CL",
                ["2026-10-16T19:55:00.1234567Z"],
                {"2026-10-16T19:55:00.1234567Z": 1},
                stage="raw-visibility",
            )

    def test_wait_for_rows_requires_exact_per_timestamp_distribution(self):
        first = "2026-10-16T19:55:00.1234567Z"
        second = "2026-10-16T19:54:59.1234567Z"
        harness, _, _ = self.harness(
            [
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [[first], [second], [second]],
                    ),
                )
            ]
        )
        with self.assertRaisesRegex(
            HARNESS.HarnessError, "more rows than expected"
        ):
            harness.wait_for_exact_rows(
                "Contoso_CL",
                [first, second],
                {first: 2, second: 1},
                stage="raw-visibility",
            )

    def test_unknown_upload_reconciles_exact_batch(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        harness, _, _ = self.harness(
            [
                requests.Timeout("unknown"),
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [[timestamp]],
                    ),
                ),
                FakeResponse(
                    200,
                    query_payload(
                        [{"name": "TimeGenerated", "type": "datetime"}],
                        [[timestamp]],
                    ),
                ),
            ]
        )
        handle = HARNESS.DcrHandle(
            "dcr",
            "/resource/dcr",
            "immutable",
            "Custom-stream",
            "Custom-Contoso_CL",
        )
        results = harness.upload_rows(
            handle,
            [{"TimeGenerated": timestamp, "Value": "value"}],
            reconcile_table="Contoso_CL",
            expected_counts_by_timestamp={timestamp: 1},
        )
        self.assertEqual("reconciled", results[0]["status"])

    def test_unknown_upload_with_zero_expected_output_fails(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        harness, _, _ = self.harness(
            [requests.Timeout("unknown")]
        )
        handle = HARNESS.DcrHandle(
            "dcr",
            "/resource/dcr",
            "immutable",
            "Custom-stream",
            "Microsoft-ASimAuthenticationEventLogs",
        )
        with self.assertRaisesRegex(
            HARNESS.OutcomeUnknownError, "zero expected output"
        ):
            harness.upload_rows(
                handle,
                [{"TimeGenerated": timestamp}],
                reconcile_table="ASimAuthenticationEventLogs",
                expected_counts_by_timestamp={timestamp: 0},
            )

    def test_cleanup_404_is_success(self):
        harness, _, _ = self.harness([FakeResponse(404)])
        result = harness.delete_dcr(
            HARNESS.DcrHandle(
                "dcr",
                "/resource/dcr",
                "immutable",
                "Custom-stream",
                "Custom-Contoso_CL",
            )
        )
        self.assertEqual("not-found", result["status"])

    def test_cleanup_uses_independent_deadline(self):
        harness, session, clock = self.harness([FakeResponse(204)])
        clock.value = 900
        result = harness.delete_dcr("/resource/dcr")
        self.assertEqual("deleted", result["status"])
        self.assertEqual("DELETE", session.calls[0]["method"])

    def test_full_run_uploads_fixture_directly_to_parser_dcr(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        query_result = query_payload(
            [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Value", "type": "string"},
            ],
            [[timestamp, "one"]],
        )
        harness, session, _ = self.harness(
            [
                FakeResponse(201),  # parser DCR PUT
                FakeResponse(
                    200,
                    {
                        "id": "/subscriptions/s/parser",
                        "properties": {
                            "provisioningState": "Succeeded",
                            "immutableId": "parser-immutable",
                        },
                    },
                ),
                FakeResponse(204),  # parser upload
                FakeResponse(200, query_result),  # target visibility
                FakeResponse(200, query_result),  # target stable
                FakeResponse(204),  # parser cleanup
            ]
        )
        prepared = {
            "version": 1,
            "targetId": "parser-a",
            "sourceRawTable": "Contoso_CL",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Value", "type": "string"},
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [
                {
                    "TimeGenerated": timestamp,
                    "Type": "Contoso_CL",
                    "Value": "one",
                }
            ],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "SourceRawTable": "Contoso_CL",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": (
                "    source // remove this comment\n"
                "      | project TimeGenerated, Type, Value"
            ),
        }
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = Path(directory) / "snapshot.json"
            result = harness.run(
                prepared,
                parser,
                snapshot_output=snapshot_path,
                expected_target_counts={timestamp: 1},
            )
            snapshot = json.loads(
                snapshot_path.read_text(encoding="utf-8")
            )

        self.assertEqual("completed", result["status"])
        self.assertEqual(
            ["deleted"],
            [entry["status"] for entry in result["cleanup"]],
        )
        self.assertEqual("prepared-fixture", snapshot["authority"])
        self.assertEqual([], snapshot["excludedColumns"])
        self.assertEqual(
            ["TimeGenerated", "Value", "Type"],
            [column["name"] for column in snapshot["schema"]],
        )
        self.assertEqual("Contoso_CL", snapshot["rows"][0]["Type"])
        self.assertIsNone(result["rawDcr"])
        self.assertEqual(
            "not-applicable",
            result["qtpSourceReplay"]["status"],
        )

        dcr_puts = [
            call
            for call in session.calls
            if call["method"] == "PUT"
            and "dataCollectionRules" in call["url"]
        ]
        self.assertEqual(1, len(dcr_puts))
        parser_flow = dcr_puts[0]["json"]["properties"]["dataFlows"][0]
        self.assertEqual(
            (
                "source\n"
                "| project TimeGenerated, Type, Value"
            ),
            parser_flow["transformKql"],
        )
        self.assertEqual(
            "Microsoft-ASimAuthenticationEventLogs",
            parser_flow["outputStream"],
        )

    def test_run_cleans_up_dcr_when_provisioning_fails(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        harness, session, _ = self.harness(
            [
                FakeResponse(201),  # parser DCR PUT
                FakeResponse(
                    200,
                    {"properties": {"provisioningState": "Failed"}},
                ),
                FakeResponse(204),  # parser cleanup
            ]
        )
        prepared = {
            "targetId": "parser-a",
            "sourceRawTable": "Contoso_CL",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [
                {
                    "TimeGenerated": timestamp,
                    "Type": "Contoso",
                }
            ],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "SourceRawTable": "Contoso_CL",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": "source",
        }
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                HARNESS.HarnessError, "entered Failed"
            ):
                harness.run(
                    prepared,
                    parser,
                    snapshot_output=Path(directory) / "snapshot.json",
                    expected_target_counts={timestamp: 1},
                )
        self.assertEqual("DELETE", session.calls[-1]["method"])
        self.assertEqual("failed", harness.last_result["status"])
        self.assertEqual(
            "deleted",
            harness.last_result["cleanup"][0]["status"],
        )
        self.assertIn(
            "cleanup",
            harness.last_result["telemetry"]["stageTimingsSeconds"],
        )

    def test_full_run_uses_validation_runner_counts_and_outputs(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        query_result = query_payload(
            [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Type", "type": "string"},
                {"name": "Value", "type": "string"},
            ],
            [[timestamp, "Contoso", "one"]],
        )
        harness, _, _ = self.harness(
            [
                FakeResponse(201),  # parser DCR PUT
                FakeResponse(
                    200,
                    {
                        "id": "/subscriptions/s/parser",
                        "properties": {
                            "provisioningState": "Succeeded",
                            "immutableId": "parser-immutable",
                        },
                    },
                ),
                FakeResponse(204),  # parser upload
                FakeResponse(200, query_result),  # target visibility
                FakeResponse(200, query_result),  # target stable
                FakeResponse(204),  # parser cleanup
            ]
        )
        prepared = {
            "version": 1,
            "targetId": "parser-a",
            "sourceRawTable": "Contoso",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Value", "type": "string"},
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [
                {
                    "TimeGenerated": timestamp,
                    "Type": "Contoso",
                    "Value": "one",
                }
            ],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "SourceRawTable": "Contoso",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": (
                "source\n| project TimeGenerated, Type, Value"
            ),
        }
        validation_runner = FakeValidationRunner(timestamp)

        with tempfile.TemporaryDirectory() as directory:
            result = harness.run(
                prepared,
                parser,
                snapshot_output=Path(directory) / "snapshot.json",
                validation_runner=validation_runner,
            )

        self.assertEqual("completed", result["status"])
        self.assertEqual(1, validation_runner.filter_calls)
        self.assertEqual(1, validation_runner.output_calls)
        self.assertEqual(
            "passed", result["filterValidation"]["status"]
        )
        self.assertEqual(
            "passed", result["outputValidation"]["status"]
        )
        self.assertIn(
            "filter-validation",
            result["telemetry"]["stageTimingsSeconds"],
        )
        self.assertIn(
            "output-validation",
            result["telemetry"]["stageTimingsSeconds"],
        )
        self.assertTrue(result["telemetry"]["requestAttempts"])

    def test_qtp_source_replay_uses_itp_input_stream(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        query_result = query_payload(
            [{"name": "TimeGenerated", "type": "datetime"}],
            [[timestamp]],
        )
        harness, session, _ = self.harness(
            [
                FakeResponse(201),  # parser DCR PUT
                FakeResponse(
                    200,
                    {
                        "id": "/subscriptions/s/parser",
                        "properties": {
                            "provisioningState": "Succeeded",
                            "immutableId": "parser-immutable",
                        },
                    },
                ),
                FakeResponse(204),  # parser upload
                FakeResponse(200, query_result),  # target visibility
                FakeResponse(200, query_result),  # target stable
                FakeResponse(201),  # QTP raw DCR PUT
                FakeResponse(
                    200,
                    {
                        "id": "/subscriptions/s/raw",
                        "properties": {
                            "provisioningState": "Succeeded",
                            "immutableId": "raw-immutable",
                        },
                    },
                ),
                FakeResponse(204),  # raw upload
                FakeResponse(200, query_result),  # raw visibility
                FakeResponse(200, query_result),  # raw stable
                FakeResponse(204),  # raw cleanup
                FakeResponse(204),  # parser cleanup
            ]
        )
        prepared = {
            "targetId": "parser-a",
            "sourceRawTable": "Contoso",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [
                {
                    "TimeGenerated": timestamp,
                    "Type": "Contoso",
                }
            ],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "InputStream": "Microsoft-SentinelContoso",
            "SourceRawTable": "Contoso",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": "source",
        }
        validation_runner = FakeValidationRunner(timestamp)

        with tempfile.TemporaryDirectory() as directory:
            result = harness.run(
                prepared,
                parser,
                snapshot_output=Path(directory) / "snapshot.json",
                validation_runner=validation_runner,
                query_time_document={"ParserQuery": "Contoso"},
            )

        dcr_puts = [
            call["json"]["properties"]
            for call in session.calls
            if call["method"] == "PUT"
            and "dataCollectionRules" in call["url"]
        ]
        self.assertEqual(2, len(dcr_puts))
        self.assertEqual(
            "Microsoft-ASimAuthenticationEventLogs",
            dcr_puts[0]["dataFlows"][0]["outputStream"],
        )
        self.assertEqual(
            "Microsoft-SentinelContoso",
            dcr_puts[1]["dataFlows"][0]["outputStream"],
        )
        parser_columns = next(
            iter(dcr_puts[0]["streamDeclarations"].values())
        )["columns"]
        raw_columns = next(
            iter(dcr_puts[1]["streamDeclarations"].values())
        )["columns"]
        self.assertIn(
            "Type",
            {column["name"] for column in parser_columns},
        )
        self.assertNotIn(
            "Type",
            {column["name"] for column in raw_columns},
        )
        self.assertEqual(
            "passed", result["qtpSourceReplay"]["status"]
        )
        self.assertEqual(
            "Microsoft-SentinelContoso",
            result["rawDcr"]["outputStream"],
        )
        self.assertEqual(1, validation_runner.output_calls)
        self.assertEqual(1, validation_runner.parity_calls)

    def test_qtp_raw_dcr_failure_warns_and_blocks_parity(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        query_result = query_payload(
            [{"name": "TimeGenerated", "type": "datetime"}],
            [[timestamp]],
        )
        harness, _, _ = self.harness(
            [
                FakeResponse(201),  # parser DCR PUT
                FakeResponse(
                    200,
                    {
                        "id": "/subscriptions/s/parser",
                        "properties": {
                            "provisioningState": "Succeeded",
                            "immutableId": "parser-immutable",
                        },
                    },
                ),
                FakeResponse(204),  # parser upload
                FakeResponse(200, query_result),  # target visibility
                FakeResponse(200, query_result),  # target stable
                FakeResponse(
                    400,
                    {
                        "error": {
                            "code": "InvalidPayload",
                            "details": [
                                {
                                    "code": "InvalidStream",
                                    "message": "Stream is unsupported.",
                                }
                            ],
                        }
                    },
                ),
                FakeResponse(404),  # raw cleanup
                FakeResponse(204),  # parser cleanup
            ]
        )
        prepared = {
            "targetId": "parser-a",
            "sourceRawTable": "Contoso",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [{"TimeGenerated": timestamp}],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "InputStream": "Microsoft-SentinelContoso",
            "SourceRawTable": "Contoso",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": "source",
        }
        validation_runner = FakeValidationRunner(timestamp)

        with tempfile.TemporaryDirectory() as directory:
            result = harness.run(
                prepared,
                parser,
                snapshot_output=Path(directory) / "snapshot.json",
                validation_runner=validation_runner,
                query_time_document={"ParserQuery": "Contoso"},
            )

        self.assertEqual("completed", result["status"])
        self.assertIsNone(result["rawDcr"])
        self.assertEqual(
            "warning", result["qtpSourceReplay"]["status"]
        )
        self.assertEqual(
            "dcr-create",
            result["qtpSourceReplay"]["error"]["stage"],
        )
        self.assertEqual(
            "blocked",
            result["outputValidation"]["queryTimeExecution"]["status"],
        )
        self.assertEqual(
            "blocked",
            result["outputValidation"]["parity"]["status"],
        )
        self.assertEqual(1, validation_runner.output_calls)
        self.assertEqual(0, validation_runner.parity_calls)

    def test_failed_output_validation_is_preserved_before_raise(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        query_table = {
            "columns": [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Type", "type": "string"},
                {"name": "Value", "type": "string"},
            ],
            "rows": [[timestamp, "Contoso_CL", "one"]],
        }
        harness, _, _ = self.harness([])
        prepared = {
            "version": 1,
            "targetId": "parser-a",
            "sourceRawTable": "Contoso_CL",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"},
                {"name": "Value", "type": "string"},
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [
                {
                    "TimeGenerated": timestamp,
                    "Type": "Contoso_CL",
                    "Value": "one",
                }
            ],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "SourceRawTable": "Contoso_CL",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": "source",
        }
        output_result = {
            "status": "failed",
            "failure": {
                "stage": "parity",
                "message": "rows differ",
                "details": {"missingRowCount": 1},
            },
            "qtp_schema": [{"name": "Value", "type": "string"}],
            "qtp_rows": [{"Value": "expected"}],
            "itp_schema": [{"name": "Value", "type": "string"}],
            "itp_rows": [{"Value": "actual"}],
            "intersect_schema": [
                {"name": "Value", "type": "string"}
            ],
            "qtp_rows_filtered": [{"Value": "expected"}],
            "itp_rows_filtered": [{"Value": "actual"}],
            "parity": {"status": "failed"},
        }
        validation_runner = FakeValidationRunner(
            timestamp,
            output_result=output_result,
        )
        handles = [
            HARNESS.DcrHandle(
                "parser",
                "/dcr/parser",
                "parser-immutable",
                "Custom-parser",
                "Microsoft-ASimAuthenticationEventLogs",
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            with (
                unittest.mock.patch.object(
                    harness,
                    "create_dcr",
                    side_effect=handles,
                ),
                unittest.mock.patch.object(
                    harness,
                    "upload_rows",
                    return_value=[{"status": "accepted"}],
                ),
                unittest.mock.patch.object(
                    harness,
                    "wait_for_exact_rows",
                    return_value=query_table,
                ),
                unittest.mock.patch.object(
                    harness,
                    "delete_dcr",
                    return_value={"status": "deleted"},
                ),
            ):
                with self.assertRaisesRegex(
                    HARNESS.HarnessError,
                    "rows differ",
                ):
                    harness.run(
                        prepared,
                        parser,
                        snapshot_output=(
                            Path(directory) / "snapshot.json"
                        ),
                        validation_runner=validation_runner,
                    )

        self.assertEqual(
            output_result,
            harness.last_result["outputValidation"],
        )

    def test_filter_validation_failure_creates_no_dcr(self):
        timestamp = "2026-10-16T19:55:00.1234567Z"
        harness, session, _ = self.harness([])
        prepared = {
            "targetId": "parser-a",
            "sourceRawTable": "Contoso",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [timestamp],
            },
            "rows": [{"TimeGenerated": timestamp}],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "SourceRawTable": "Contoso",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": "source",
        }

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                RuntimeError, "filter validation failed"
            ):
                harness.run(
                    prepared,
                    parser,
                    snapshot_output=Path(directory) / "snapshot.json",
                    validation_runner=FailingFilterRunner(),
                )

        self.assertEqual([], session.calls)
        self.assertEqual([], harness.last_result["cleanup"])

    def test_full_run_rejects_incomplete_expected_count_map(self):
        harness, _, _ = self.harness([])
        prepared = {
            "targetId": "parser-a",
            "sourceRawTable": "Contoso_CL",
            "rowCount": 1,
            "schema": [
                {"name": "TimeGenerated", "type": "datetime"}
            ],
            "namespace": {
                "pullRequest": "123",
                "runId": "456",
                "runAttempt": 1,
                "timestampValues": [
                    "2026-10-16T19:55:00.1234567Z"
                ],
            },
            "rows": [
                {
                    "TimeGenerated":
                        "2026-10-16T19:55:00.1234567Z"
                }
            ],
        }
        parser = {
            "ParserName": "ASimAuthenticationContoso",
            "SourceRawTable": "Contoso_CL",
            "TargetASIMTable": "ASimAuthenticationEventLogs",
            "ParserQuery": "source",
        }
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                ValueError, "every prepared timestamp"
            ):
                harness.run(
                    prepared,
                    parser,
                    snapshot_output=Path(directory) / "snapshot.json",
                    expected_target_counts={},
                )


if __name__ == "__main__":
    unittest.main()
