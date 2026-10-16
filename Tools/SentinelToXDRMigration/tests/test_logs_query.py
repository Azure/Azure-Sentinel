from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import yaml
from azure.monitor.query import (
    LogsQueryError,
    LogsQueryPartialResult,
    LogsQueryResult,
    LogsTable,
)
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest

from sentinel_xdr_migration import cli
from sentinel_xdr_migration.artifacts import create_run, report_directory
from sentinel_xdr_migration.graph_client_config import configure_azure_cli_profile
from sentinel_xdr_migration.logs_query import (
    LogsQueryFailure,
    azure_cli_credential,
    execute_workspace_query,
    logs_query_client,
    preflight_read_executor,
    query_family,
    verify_azure_cli_target,
)
from sentinel_xdr_migration.runtime import current_runtime_evidence, validate_sentinel_sdk


TENANT = "11111111-2222-3333-4444-555555555555"
SUBSCRIPTION = "22222222-3333-4444-5555-666666666666"
WORKSPACE = "33333333-4444-5555-6666-777777777777"
TARGET = {
    "tenantId": TENANT,
    "subscriptionId": SUBSCRIPTION,
    "workspaceResourceId": (
        "/subscriptions/22222222-3333-4444-5555-666666666666/resourceGroups/lab/"
        "providers/Microsoft.OperationalInsights/workspaces/sentinel"
    ),
    "workspaceCustomerId": WORKSPACE,
}


def logs_table(name, columns, rows, column_types=None):
    return LogsTable(
        name=name,
        columns=columns,
        columns_types=column_types or ["string"] * len(columns),
        rows=rows,
    )


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.closed = False

    def query_workspace(self, workspace_id, query, **kwargs):
        self.calls.append((workspace_id, query, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        self.closed = True


class FakeClock:
    def __init__(self):
        self.value = 100.0
        self.sleeps = []

    def monotonic(self):
        return self.value

    def sleep(self, value):
        self.sleeps.append(value)
        self.value += value


def success(*tables):
    return LogsQueryResult(tables=list(tables))


def partial(*tables, error="partial result"):
    return LogsQueryPartialResult(
        partial_data=list(tables),
        partial_error=LogsQueryError(code="PartialError", message=error),
    )


class LogsQueryExecutionTests(unittest.TestCase):
    def test_exact_multiline_query_and_unbounded_timespan_are_sent(self):
        query = 'let cutoff = ago(2h);\nDeviceEvents\n| where TimeGenerated > cutoff\n| where InitiatingProcessCommandLine contains "a|b;''c"\n| summarize count()'
        response = success(logs_table("PrimaryResult", ["Count"], []))
        client = FakeClient([response])
        result = execute_workspace_query(client, WORKSPACE, query)
        self.assertEqual(query, client.calls[0][1])
        self.assertIsNone(client.calls[0][2]["timespan"])
        self.assertEqual(0, result["rowCount"])
        self.assertEqual("passed", result["status"])
        self.assertEqual([{"name": "Count", "type": "string"}], result["schema"])

    def test_actual_sdk_deserialization_preserves_zero_row_schema(self):
        response = LogsQueryResult._from_generated({
            "tables": [{
                "name": "PrimaryResult",
                "columns": [
                    {"name": "Computer", "type": "string"},
                    {"name": "TimeGenerated", "type": "datetime"},
                ],
                "rows": [],
            }],
        })
        result = execute_workspace_query(
            FakeClient([response]),
            WORKSPACE,
            "DeviceEvents | project Computer, TimeGenerated",
        )
        self.assertEqual("passed", result["status"])
        self.assertEqual(
            [
                {"name": "Computer", "type": "string"},
                {"name": "TimeGenerated", "type": "datetime"},
            ],
            result["schema"],
        )
        self.assertEqual([], result["tables"][0]["rows"])

    def test_actual_sdk_partial_deserialization_preserves_schema_and_error(self):
        response = LogsQueryPartialResult._from_generated({
            "tables": [{
                "name": "PrimaryResult",
                "columns": [{"name": "Computer", "type": "string"}],
                "rows": [["host-a"]],
            }],
            "error": {"code": "PartialError", "message": "incomplete"},
        }, LogsQueryError)
        result = execute_workspace_query(
            FakeClient([response]),
            WORKSPACE,
            "DeviceEvents | project Computer",
        )
        self.assertEqual("failed", result["status"])
        self.assertEqual([{"name": "Computer", "type": "string"}], result["schema"])
        self.assertEqual([["host-a"]], result["tables"][0]["rows"])
        self.assertEqual("incomplete", result["error"])

    def test_malformed_sdk_column_metadata_is_an_explicit_provider_failure(self):
        malformed_models = (
            (
                LogsTable(
                    name="PrimaryResult",
                    columns=["Computer"],
                    columns_types=[],
                    rows=[],
                ),
                "missing or mismatched column types",
            ),
            (
                LogsTable(
                    name="PrimaryResult",
                    columns=[""],
                    columns_types=["string"],
                    rows=[],
                ),
                "invalid column name",
            ),
            (
                LogsTable(
                    name="PrimaryResult",
                    columns=["Computer"],
                    columns_types=[""],
                    rows=[],
                ),
                "invalid column type",
            ),
        )
        for malformed, message in malformed_models:
            with self.subTest(message=message):
                with self.assertRaisesRegex(LogsQueryFailure, message) as caught:
                    execute_workspace_query(
                        FakeClient([success(malformed)]),
                        WORKSPACE,
                        "DeviceEvents | project Computer",
                    )
                self.assertEqual("provider", caught.exception.failure_kind)

    def test_successful_sdk_result_without_tables_is_not_accepted(self):
        with self.assertRaisesRegex(LogsQueryFailure, "no result tables"):
            execute_workspace_query(
                FakeClient([LogsQueryResult(tables=[])]),
                WORKSPACE,
                "print 1",
            )

    def test_typed_results_keep_full_schema_and_rows(self):
        query = "DeviceEvents | project TimeGenerated, Amount, Id"
        values = [
            datetime(2026, 10, 11, tzinfo=timezone.utc),
            Decimal("1.25"),
            uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
        ]
        client = FakeClient([success(logs_table(
            "events",
            ["TimeGenerated", "Amount", "Id"],
            [values],
        ))])
        result = execute_workspace_query(client, WORKSPACE, query)
        self.assertEqual(
            [
                {"$datetime": "2026-10-11T00:00:00+00:00"},
                {"$decimal": "1.25"},
                {"$uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
            ],
            result["tables"][0]["rows"][0],
        )
        self.assertEqual(["TimeGenerated", "Amount", "Id"], [c["name"] for c in result["schema"]])

    def test_partial_results_are_failed_and_retain_available_data_and_error(self):
        client = FakeClient([partial(logs_table("events", ["A", "B"], [[1, 2]]), error="incomplete")])
        result = execute_workspace_query(client, WORKSPACE, "T | project A, B")
        self.assertEqual("failed", result["status"])
        self.assertTrue(result["partial"])
        self.assertEqual("incomplete", result["error"])
        self.assertEqual(2, len(result["schema"]))
        self.assertEqual([[1, 2]], result["tables"][0]["rows"])

    def test_auth_authorization_and_kql_errors_are_not_retried(self):
        for status, expected in ((401, "authentication"), (403, "authorization"), (400, "query")):
            with self.subTest(status=status):
                error = RuntimeError("service rejected request")
                error.status_code = status
                client = FakeClient([error])
                with self.assertRaises(LogsQueryFailure) as caught:
                    execute_workspace_query(client, WORKSPACE, "T | take 1")
                self.assertEqual(expected, caught.exception.failure_kind)
                self.assertEqual(1, len(client.calls))

    def test_transient_retries_are_bounded_and_kql_errors_do_not_stop_other_rules(self):
        transient = RuntimeError("temporarily unavailable")
        transient.status_code = 503
        client = FakeClient([
            transient,
            success(logs_table("events", ["A"], [[1]])),
            RuntimeError("bad KQL"),
        ])
        client.responses[-1].status_code = 400
        clock = FakeClock()
        query_hash = hashlib.sha256(b"T | take 1").hexdigest()
        results = query_family(
            client,
            WORKSPACE,
            [
                {"detection": "one.yaml", "query": "T | take 1", "querySha256": query_hash},
                {"detection": "two.yaml", "query": "bad kql", "querySha256": "0" * 64},
            ],
            retry_count=1,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        self.assertEqual(3, len(client.calls))
        self.assertEqual([2], clock.sleeps)
        self.assertEqual(["passed", "failed"], [item["status"] for item in results])
        self.assertEqual("query", results[1]["failureKind"])

    def test_provider_failure_stops_family_and_records_remaining_queries_not_run(self):
        error = RuntimeError("no access")
        error.status_code = 403
        client = FakeClient([error])
        items = [
            {"detection": "one.yaml", "query": "T | take 1", "querySha256": "1" * 64},
            {"detection": "two.yaml", "query": "U | take 1", "querySha256": "2" * 64},
        ]
        results = query_family(client, WORKSPACE, items)
        self.assertEqual(["blocked", "not-run"], [item["status"] for item in results])
        self.assertEqual(1, len(client.calls))

    def test_family_timeout_marks_unstarted_queries_not_run(self):
        clock = FakeClock()

        class SlowClient(FakeClient):
            def query_workspace(self, workspace_id, query, **kwargs):
                call = super().query_workspace(workspace_id, query, **kwargs)
                clock.value += 2
                return call

        client = SlowClient([
            success(logs_table("events", ["A"], [[1]])),
            success(logs_table("events", ["B"], [[2]])),
        ])
        results = query_family(
            client,
            WORKSPACE,
            [
                {"detection": "one.yaml", "query": "T | take 1", "querySha256": "1" * 64},
                {"detection": "two.yaml", "query": "U | take 1", "querySha256": "2" * 64},
            ],
            family_timeout_seconds=1,
            monotonic=clock.monotonic,
        )
        self.assertEqual(["passed", "not-run"], [item["status"] for item in results])
        self.assertEqual(1, len(client.calls))

    def test_preflight_adapter_reuses_sdk_executor_and_locked_workspace(self):
        client = FakeClient([success(logs_table("events", ["A"], []))])
        request = {
            "provider": "logAnalytics",
            "query": "T\n| take 0",
            "target": TARGET,
        }
        with (
            mock.patch("sentinel_xdr_migration.logs_query.verify_azure_cli_target") as verify,
            mock.patch("sentinel_xdr_migration.logs_query.azure_cli_credential", return_value=object()),
            mock.patch("sentinel_xdr_migration.logs_query.logs_query_client", return_value=client),
        ):
            result = preflight_read_executor(request)
        verify.assert_called_once_with(TARGET)
        self.assertEqual(WORKSPACE, client.calls[0][0])
        self.assertEqual(request["query"], client.calls[0][1])
        self.assertIsNone(client.calls[0][2]["timespan"])
        self.assertTrue(result["ok"])
        self.assertEqual(0, result["rowCount"])

    def test_credential_construction_is_pinned_and_does_not_launch_login(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "state"
            profile = str((Path(temp) / "isolated-cli").resolve())
            configure_azure_cli_profile(state, profile)
            observations = []

            def construct(*, tenant_id, subscription=None, process_timeout=10):
                def get_token(*scopes, **kwargs):
                    observations.append((scopes, kwargs, os.environ.get("AZURE_CONFIG_DIR")))
                    return SimpleNamespace(token="mock-token", expires_on=4070908800)

                return SimpleNamespace(
                    tenant_id=tenant_id,
                    subscription=subscription,
                    _process_timeout=process_timeout,
                    get_token=mock.Mock(side_effect=get_token),
                )

            with (
                mock.patch("azure.identity.AzureCliCredential", side_effect=construct) as constructor,
                mock.patch("sentinel_xdr_migration.logs_query._state_dir", return_value=state),
            ):
                previous_profile = os.environ.get("AZURE_CONFIG_DIR")
                credential = azure_cli_credential(TARGET)
                constructor.assert_called_once_with(tenant_id=TENANT, subscription=None)
                self.assertEqual(TENANT, credential.tenant_id)
                self.assertIsNone(credential.subscription)
                self.assertEqual(10, credential._process_timeout)
                credential.get_token("https://api.loganalytics.io/.default")
                self.assertEqual(
                    [(("https://api.loganalytics.io/.default",), {}, profile)],
                    observations,
                )
                self.assertEqual(previous_profile, os.environ.get("AZURE_CONFIG_DIR"))

    def test_logs_query_bearer_policy_uses_tenant_pinned_cli_without_subscription_flag(self):
        calls = []

        class OfflineCliCredential:
            def __init__(self, *, tenant_id, subscription=None, process_timeout=10):
                self.tenant_id = tenant_id
                self.subscription = subscription
                self._process_timeout = process_timeout

            def get_token_info(self, *scopes, options=None):
                # Record the CLI-shaped contract without invoking SDK auth or a process.
                command = ["account", "get-access-token", "--output", "json", "--resource",
                           scopes[0].removesuffix("/.default")]
                if self.tenant_id:
                    command.extend(["--tenant", self.tenant_id])
                if self.subscription:
                    command.extend(["--subscription", self.subscription])
                calls.append((scopes, options, command, self._process_timeout))
                return SimpleNamespace(
                    token="mock-token", expires_on=4070908800, refresh_on=None,
                )

        with tempfile.TemporaryDirectory() as temp:
            with (
                mock.patch("azure.identity.AzureCliCredential", side_effect=OfflineCliCredential) as constructor,
                mock.patch("sentinel_xdr_migration.logs_query._state_dir", return_value=Path(temp)),
            ):
                credential = azure_cli_credential(TARGET)
                constructor.assert_called_once_with(tenant_id=TENANT, subscription=None)
                client = logs_query_client(credential, retry_total=0)
                policy = client._query_op._config.authentication_policy
                request = PipelineRequest(
                    HttpRequest("POST", "https://api.loganalytics.io/v1/workspaces/query"),
                    PipelineContext(None),
                )
                try:
                    with mock.patch.object(
                        credential, "get_token_info", wraps=credential.get_token_info,
                    ) as get_token_info:
                        policy.on_request(request)
                        get_token_info.assert_called_once_with(
                            "https://api.loganalytics.io/.default", options={},
                        )
                finally:
                    client.close()

        self.assertEqual("Bearer mock-token", request.http_request.headers["Authorization"])
        self.assertEqual(1, len(calls))
        scopes, options, command, process_timeout = calls[0]
        self.assertEqual(("https://api.loganalytics.io/.default",), scopes)
        self.assertEqual({}, options)
        self.assertEqual(10, process_timeout)
        self.assertIn("--tenant", command)
        self.assertIn(TENANT, command)
        self.assertNotIn("--subscription", command)

    def test_azure_cli_target_requires_exact_tenant_and_subscription(self):
        completed = SimpleNamespace(returncode=0)
        account = {"tenantId": TENANT, "id": SUBSCRIPTION}
        with (
            mock.patch("sentinel_xdr_migration.target_context._run_az", return_value=completed) as run,
            mock.patch("sentinel_xdr_migration.target_context._json_output", return_value=account),
        ):
            verify_azure_cli_target(TARGET)
        run.assert_called_once()
        self.assertEqual(("account", "show"), run.call_args.args[0])
        with (
            mock.patch("sentinel_xdr_migration.target_context._run_az", return_value=completed),
            mock.patch(
                "sentinel_xdr_migration.target_context._json_output",
                return_value={"tenantId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "id": SUBSCRIPTION},
            ),
        ):
            with self.assertRaisesRegex(LogsQueryFailure, "does not match"):
                verify_azure_cli_target(TARGET)


class SentinelSdkProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.solution = Path(self.temp.name) / "Example"
        self.analytic = self.solution / "Analytic Rules"
        self.detections = self.solution / "XDR Detections"
        self.analytic.mkdir(parents=True)
        self.detections.mkdir(parents=True)
        self.sources = {
            "Rule.yaml": 'let allowed = dynamic(["x", "y"]);\nDeviceEvents\n| where ActionType in (allowed)\n| where InitiatingProcessCommandLine contains "a|b;''c"',
            "Nested/Other.yaml": "SecurityEvent\n| where EventID == 4624\n| project TimeGenerated, Computer",
        }
        for relative, query in self.sources.items():
            source = self.analytic / relative
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(
                yaml.safe_dump({"id": self._guid(relative), "query": query}),
                encoding="utf-8",
            )
            target = self.detections / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                yaml.safe_dump({
                    "kind": "CustomDetection",
                    "contentProvenance": {
                        "requiredWorkloads": [{
                            "workload": "mde" if relative == "Rule.yaml" else "sentinel",
                            "dataTypes": ["DeviceEvents" if relative == "Rule.yaml" else "SecurityEvent"],
                        }],
                        "requiredDataConnectors": [],
                        "source": {
                            "path": f"Analytic Rules/{relative}",
                            "querySha256": hashlib.sha256(query.encode()).hexdigest(),
                        }
                    },
                    "properties": {"queryCondition": {"queryText": query}},
                }),
                encoding="utf-8",
            )
        self.target = dict(TARGET)

    @staticmethod
    def _guid(value):
        return (
            "11111111-2222-3333-4444-"
            + ("555555555555" if value == "Rule.yaml" else "666666666666")
        )

    def _factory(self, client):
        return lambda credential, **kwargs: client

    def _write_provider_gap_evidence(self):
        evidence = self.solution / "provider-gap.json"
        evidence.write_text(json.dumps({
            "mcpProvider": "triage-mcp",
            "advertisedTool": "unavailable",
            "queryFamily": "sentinel",
            "fallbackProvider": "azure-monitor-sdk",
            "scopeReference": TARGET["workspaceResourceId"],
            "reasonCode": "tool-unavailable",
            "reason": "No Triage workspace query tool was available.",
            "batchComplete": True,
            "scopeVerified": True,
            "permissionsVerified": True,
            "kqlError": False,
        }))
        return evidence

    def test_complete_inventory_is_run_through_cli_and_full_rows_are_reported(self):
        responses = [
            success(logs_table("PrimaryResult", ["A", "B"], [[1, "row"]])),
            success(logs_table("PrimaryResult", ["TimeGenerated", "Computer"], [])),
        ]
        client = FakeClient(responses)
        output = io.StringIO()
        create_run(self.solution, run_id="20261011T000000Z-" + "a" * 32, migrating=True)
        with (
            mock.patch("sentinel_xdr_migration.logs_query.verify_azure_cli_target") as verify,
            mock.patch("sentinel_xdr_migration.logs_query.azure_cli_credential", return_value=object()),
            mock.patch("sentinel_xdr_migration.logs_query.logs_query_client", side_effect=self._factory(client)),
            mock.patch("sentinel_xdr_migration.cli.require_locked_target", return_value=self.target),
            contextlib.redirect_stdout(output),
        ):
            code = cli.main([
                "validate-sentinel-sdk",
                "--solution", str(self.solution),
                "--run-id", "20261011T000000Z-" + "a" * 32,
            ])
        self.assertEqual(0, code)
        verify.assert_called_once_with(self.target)
        self.assertEqual(2, len(client.calls))
        self.assertIn(self.sources["Rule.yaml"], [call[1] for call in client.calls])
        self.assertTrue(all(call[2]["timespan"] is None for call in client.calls))
        report_path = report_directory(self.solution) / "runtime-validation.azure-monitor-sdk.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual("azure-monitor-sdk", report["provider"])
        self.assertTrue(report["familyComplete"])
        self.assertEqual(2, report["valid"])
        self.assertEqual(["passed", "passed"], [item["status"] for item in report["results"]])
        self.assertEqual(0, report["results"][1]["rowCount"])
        self.assertEqual([[1, "row"]], report["results"][0]["tables"][0]["rows"])
        self.assertEqual(
            [{"name": "A", "type": "string"}, {"name": "B", "type": "string"}],
            report["results"][0]["tables"][0]["columns"],
        )
        self.assertTrue(client.closed)

    def test_sdk_auth_failure_is_provider_block_not_per_rule_kql_failure(self):
        error = RuntimeError("access denied")
        error.status_code = 403
        client = FakeClient([error])
        report = validate_sentinel_sdk(
            self.solution,
            target=self.target,
            _scope_verifier=lambda _target: None,
            _credential_factory=lambda _target: object(),
            _client_factory=self._factory(client),
        )
        self.assertEqual(0, report["invalid"])
        self.assertEqual(1, report["blocked"])
        self.assertEqual(1, report["notRun"])
        self.assertEqual("authorization", report["providerFailure"]["failureKind"])
        self.assertFalse(report["familyComplete"])

    def test_full_sdk_family_can_record_only_explicit_triage_provider_gap(self):
        evidence = self._write_provider_gap_evidence()
        client = FakeClient([
            success(logs_table("events", ["A"], [])),
            success(logs_table("events", ["B"], [])),
        ])
        report = validate_sentinel_sdk(
            self.solution,
            target=self.target,
            provider_gap_evidence=evidence,
            _scope_verifier=lambda _target: None,
            _credential_factory=lambda _target: object(),
            _client_factory=self._factory(client),
        )
        self.assertEqual(2, report["valid"])
        self.assertTrue(report["familyComplete"])
        self.assertEqual("azure-monitor-sdk", report["providerFallback"]["fallbackProvider"])

    def test_sdk_kql_failure_with_provider_gap_is_persisted_then_rejected(self):
        evidence = self._write_provider_gap_evidence()
        previous_client = FakeClient([
            success(logs_table("events", ["A"], [])),
            success(logs_table("events", ["B"], [])),
        ])
        previous_report = validate_sentinel_sdk(
            self.solution,
            target=self.target,
            provider_gap_evidence=evidence,
            _scope_verifier=lambda _target: None,
            _credential_factory=lambda _target: object(),
            _client_factory=self._factory(previous_client),
        )
        self.assertEqual(2, previous_report["valid"])

        query_error = RuntimeError("Failed to resolve table 'MissingTable'")
        query_error.status_code = 400
        client = FakeClient([
            query_error,
            success(logs_table("events", ["B"], [])),
        ])
        with self.assertRaisesRegex(ValueError, "Failed to resolve table 'MissingTable'"):
            validate_sentinel_sdk(
                self.solution,
                target=self.target,
                provider_gap_evidence=evidence,
                _scope_verifier=lambda _target: None,
                _credential_factory=lambda _target: object(),
                _client_factory=self._factory(client),
            )

        report_path = report_directory(self.solution) / "runtime-validation.azure-monitor-sdk.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        failed = next(item for item in report["results"] if item["status"] == "failed")
        self.assertEqual("query", failed["failureKind"])
        self.assertEqual(400, failed["statusCode"])
        self.assertIn("Failed to resolve table 'MissingTable'", failed["errorDetails"])
        self.assertEqual(
            hashlib.sha256(self.sources["Nested/Other.yaml"].encode()).hexdigest(),
            failed["querySha256"],
        )
        self.assertEqual("azure-monitor-sdk", report["providerFallback"]["fallbackProvider"])
        self.assertTrue(report["familyComplete"])
        self.assertEqual(["failed", "passed"], [item["status"] for item in report["results"]])
        self.assertEqual(2, len(client.calls))
        current = current_runtime_evidence(self.solution)
        self.assertIsNone(current["sentinelProvider"])
        self.assertTrue(any("Failed to resolve table" in issue for issue in current["currentQueryFailures"]))

    def test_sdk_blocked_and_unexecuted_fallback_results_are_persisted(self):
        evidence = self._write_provider_gap_evidence()
        error = RuntimeError("access denied")
        error.status_code = 403
        client = FakeClient([error])
        with self.assertRaisesRegex(ValueError, "is blocked: access denied"):
            validate_sentinel_sdk(
                self.solution,
                target=self.target,
                provider_gap_evidence=evidence,
                _scope_verifier=lambda _target: None,
                _credential_factory=lambda _target: object(),
                _client_factory=self._factory(client),
            )

        report_path = report_directory(self.solution) / "runtime-validation.azure-monitor-sdk.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(["blocked", "not-run"], [item["status"] for item in report["results"]])
        self.assertEqual("authorization", report["providerFailure"]["failureKind"])
        self.assertFalse(report["familyComplete"])
        self.assertEqual("azure-monitor-sdk", report["providerFallback"]["fallbackProvider"])

    def test_sdk_partial_fallback_result_is_persisted_with_diagnostics(self):
        evidence = self._write_provider_gap_evidence()
        response = partial(logs_table("events", ["A"], [[1]]), error="partial response details")
        client = FakeClient([
            response,
            success(logs_table("events", ["B"], [])),
        ])
        with self.assertRaisesRegex(ValueError, "partial response details"):
            validate_sentinel_sdk(
                self.solution,
                target=self.target,
                provider_gap_evidence=evidence,
                _scope_verifier=lambda _target: None,
                _credential_factory=lambda _target: object(),
                _client_factory=self._factory(client),
            )

        report_path = report_directory(self.solution) / "runtime-validation.azure-monitor-sdk.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        partial_result = next(item for item in report["results"] if item.get("partial"))
        self.assertEqual("failed", partial_result["status"])
        self.assertEqual("partial response details", partial_result["error"])
        self.assertEqual("partial-response", partial_result["failureKind"])
        self.assertEqual([[1]], partial_result["tables"][0]["rows"])
        self.assertTrue(report["familyComplete"])

    def test_empty_and_stale_source_inventory_fail_before_sdk_calls(self):
        client = FakeClient([])
        target_file = self.detections / "Rule.yaml"
        stale_target = yaml.safe_load(target_file.read_text(encoding="utf-8"))
        stale_target["contentProvenance"]["source"]["querySha256"] = "0" * 64
        target_file.write_text(yaml.safe_dump(stale_target), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale source-query hash"):
            validate_sentinel_sdk(
                self.solution,
                target=self.target,
                _scope_verifier=lambda _target: None,
                _credential_factory=lambda _target: object(),
                _client_factory=self._factory(client),
            )
        self.assertEqual([], client.calls)
        original_query = self.sources["Rule.yaml"]
        stale_target["contentProvenance"]["source"]["querySha256"] = hashlib.sha256(
            original_query.encode()
        ).hexdigest()
        target_file.write_text(yaml.safe_dump(stale_target), encoding="utf-8")
        (self.detections / "Rule.yaml").unlink()
        with self.assertRaisesRegex(ValueError, "complete source inventory"):
            validate_sentinel_sdk(
                self.solution,
                target=self.target,
                _scope_verifier=lambda _target: None,
                _credential_factory=lambda _target: object(),
                _client_factory=self._factory(client),
            )
        self.assertEqual([], client.calls)
        for path in self.analytic.rglob("*.yaml"):
            path.unlink()
        with self.assertRaisesRegex(ValueError, "inventory is empty"):
            validate_sentinel_sdk(
                self.solution,
                target=self.target,
                _scope_verifier=lambda _target: None,
                _credential_factory=lambda _target: object(),
                _client_factory=self._factory(client),
            )

    def test_target_mismatch_blocks_cli_before_any_sdk_query(self):
        client = FakeClient([])
        create_run(self.solution, run_id="20261011T000000Z-" + "b" * 32, migrating=True)
        run_path = report_directory(self.solution)
        (run_path / "workflow-state.json").write_text(json.dumps({
            "context": {
                "workflowProfile": "qualification",
                "targetContextLocked": True,
                "tenantId": TENANT,
                "subscriptionId": SUBSCRIPTION,
                "workspaceResourceId": TARGET["workspaceResourceId"],
                "workspaceCustomerId": WORKSPACE,
            }
        }))
        (run_path / "qualification-target.json").write_text(json.dumps({
            "schemaVersion": "1.0.0",
            "locked": True,
            **{key: value for key, value in self.target.items() if key != "workspaceCustomerId"},
            "workspaceCustomerId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        }))
        out = io.StringIO()
        with (
            mock.patch("sentinel_xdr_migration.logs_query.verify_azure_cli_target"),
            mock.patch("sentinel_xdr_migration.logs_query.azure_cli_credential", return_value=object()),
            mock.patch("sentinel_xdr_migration.logs_query.logs_query_client", side_effect=self._factory(client)),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            code = cli.main([
                "validate-sentinel-sdk",
                "--solution", str(self.solution),
                "--run-id", "20261011T000000Z-" + "b" * 32,
            ])
        self.assertEqual(2, code)
        self.assertEqual([], client.calls)

    def test_partial_schema_and_rows_are_retained_in_sdk_report_as_failed(self):
        response = partial(logs_table("events", ["A"], [[1]]), error="partial")
        client = FakeClient([response, success(logs_table("events", ["B"], []))])
        report = validate_sentinel_sdk(
            self.solution,
            target=self.target,
            _scope_verifier=lambda _target: None,
            _credential_factory=lambda _target: object(),
            _client_factory=self._factory(client),
        )
        self.assertEqual(1, report["invalid"])
        partial_result = next(item for item in report["results"] if item["detection"] == "Nested/Other.yaml")
        self.assertEqual("failed", partial_result["status"])
        self.assertTrue(partial_result["partial"])
        self.assertEqual("partial", partial_result["error"])
        self.assertEqual([[1]], partial_result["tables"][0]["rows"])


if __name__ == "__main__":
    unittest.main()
