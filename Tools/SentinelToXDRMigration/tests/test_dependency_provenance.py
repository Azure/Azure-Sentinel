from __future__ import annotations

import copy
import contextlib
import hashlib
import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import yaml
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.monitor.query import LogsQueryClient

from sentinel_xdr_migration.converter import build_xdr_document, convert_solution, validate_document
from sentinel_xdr_migration import cli
from sentinel_xdr_migration.dependencies import (
    dependency_plan, live_dependency_check, plan_solution_dependencies,
    resolve_data_types, solution_package_context,
)
from sentinel_xdr_migration.graph_readiness import graph_detection_payload
from sentinel_xdr_migration.logs_query import execute_workspace_query
from sentinel_xdr_migration.runtime import current_runtime_evidence, record_runtime_validation
from test_converter import RULE
from test_logs_query import WORKSPACE, logs_table, success


class DependencyProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory()
        self.addCleanup(self.fixture.cleanup)
        self.root = Path(self.fixture.name)
        self.source = self.root / "Analytic Rules/Rule.yaml"
        self.source.parent.mkdir()
        self.source.write_text(RULE)

    def document(self):
        return build_xdr_document(self.source, self.root, {})

    def test_conversion_is_offline_and_separates_dependencies_from_deployment_keys(self):
        with mock.patch("sentinel_xdr_migration.logs_query.execute_workspace_query") as query:
            document = self.document()
        query.assert_not_called()
        provenance = document["contentProvenance"]
        self.assertEqual([{"workload": "mde", "dataTypes": ["DeviceEvents"]}], provenance["requiredWorkloads"])
        self.assertEqual([], provenance["requiredDataConnectors"])
        for key in ("packageId", "packageVersion", "contentId", "contentVersion"):
            self.assertNotIn(key, provenance)
        self.assertEqual([], validate_document(document))

    def test_yaml_requires_dependency_fields_and_supported_workload_records(self):
        document = self.document()
        for key in ("requiredWorkloads", "requiredDataConnectors"):
            candidate = copy.deepcopy(document)
            del candidate["contentProvenance"][key]
            self.assertTrue(validate_document(candidate))
        for record in (
            "mde", {}, {"workload": "defender", "dataTypes": []},
            {"workload": "mde", "dataTypes": [""]},
            {"workload": "mde", "dataTypes": "DeviceEvents"},
        ):
            candidate = copy.deepcopy(document)
            candidate["contentProvenance"]["requiredWorkloads"] = [record]
            self.assertTrue(validate_document(candidate), record)
        document["contentProvenance"]["dependencyReviewRequired"] = True
        self.assertTrue(any("needs review" in error for error in validate_document(document)))

    def test_metadata_threshold_counts_distinct_input_tables(self):
        for count in (1, 10):
            tables = [f"Table{index}" for index in range(count)]
            result = resolve_data_types("DeviceEvents | take 1", [
                {"tables": tables + tables},
            ])
            self.assertEqual("log-analytics", result["method"])
            self.assertEqual(sorted(tables), result["dataTypes"])
        result = resolve_data_types("DeviceEvents | take 1", [
            {"tables": [{"name": f"Table{index}"} for index in range(11)]},
        ])
        self.assertEqual("regex", result["method"])
        self.assertEqual("more-than-10-tables", result["fallbackReason"])
        self.assertEqual(["DeviceEvents"], result["dataTypes"])
        self.assertEqual(11, len(result["returnedDataTypes"]))

    def test_missing_metadata_falls_back_but_malformed_metadata_is_an_error(self):
        for metadata in (None, [], [{"resourceId": "/workspace/example"}], [{"tables": None}]):
            result = resolve_data_types("DeviceInfo | take 1", metadata)
            self.assertEqual("regex", result["method"])
            self.assertEqual(["DeviceInfo"], result["dataTypes"])
        for metadata in ({}, [None], [{"tables": [""]}], [{"tables": "DeviceInfo"}]):
            with self.assertRaises(ValueError):
                resolve_data_types("DeviceInfo | take 1", metadata)
        result = dependency_plan("SavedFunction() | take 1")
        self.assertEqual([], result["dataTypes"])
        self.assertEqual([], result["requiredWorkloads"])
        self.assertEqual([], result["requiredDataConnectors"])
        self.assertTrue(result["reviewRequired"])

    def test_shared_security_alert_does_not_invent_defender_or_connector_requirements(self):
        result = dependency_plan("SecurityAlert | take 1")
        self.assertEqual([{"workload": "sentinel", "dataTypes": ["SecurityAlert"]}], result["requiredWorkloads"])
        self.assertEqual([], result["requiredDataConnectors"])
        self.assertTrue(result["reviewRequired"])

    def test_live_validation_compares_workloads_and_source_connector_declarations(self):
        document = self.document()
        metadata = [{"tables": ["DeviceEvents"]}]
        self.assertEqual("passed", live_dependency_check(
            document, "DeviceEvents | take 1", metadata,
        )["status"])
        connectors = [{"connectorId": "MicrosoftThreatProtection", "dataTypes": ["DeviceEvents"]}]
        result = live_dependency_check(
            document, "DeviceEvents | take 1", metadata, source_connectors=connectors,
        )
        self.assertEqual("failed", result["status"])
        self.assertIn("connector MicrosoftThreatProtection", "; ".join(result["errors"]))
        document["contentProvenance"]["requiredDataConnectors"] = connectors
        self.assertEqual("passed", live_dependency_check(
            document, "DeviceEvents | take 1", metadata, source_connectors=connectors,
        )["status"])
        document["contentProvenance"]["requiredWorkloads"] = []
        self.assertEqual("failed", live_dependency_check(
            document, "DeviceEvents | take 1", metadata,
        )["status"])

    def test_live_validation_covers_tables_added_to_the_converted_query(self):
        document = self.document()
        document["properties"]["queryCondition"]["queryText"] = (
            "DeviceEvents | join kind=inner (DeviceInfo) on DeviceId"
        )
        result = live_dependency_check(
            document, "DeviceEvents", [{"tables": ["DeviceEvents"]}],
        )
        self.assertEqual("failed", result["status"])
        self.assertTrue(any("DeviceInfo" in error for error in result["errors"]))

    def test_reviewed_unknown_table_mapping_can_be_declared_without_private_catalog(self):
        document = self.document()
        document["properties"]["queryCondition"]["queryText"] = "ReviewedIdentityTable | take 1"
        document["contentProvenance"]["requiredWorkloads"] = [
            {"workload": "entraid", "dataTypes": ["ReviewedIdentityTable"]},
        ]
        result = live_dependency_check(
            document, "ReviewedIdentityTable | take 1",
            [{"tables": ["ReviewedIdentityTable"]}],
        )
        self.assertEqual("passed", result["status"])

    def test_live_validation_checks_connector_identity_even_without_data_types(self):
        document = self.document()
        result = live_dependency_check(
            document, "DeviceEvents", [{"tables": ["DeviceEvents"]}],
            source_connectors=[{"connectorId": "OtherConnector", "dataTypes": []}],
        )
        self.assertEqual("failed", result["status"])
        self.assertTrue(any("OtherConnector" in error for error in result["errors"]))

    def test_live_validation_reports_malformed_source_connectors(self):
        document = self.document()
        for connectors in (False, 1, {}, [{"connectorId": 1, "dataTypes": []}]):
            result = live_dependency_check(
                document, "DeviceEvents", [{"tables": ["DeviceEvents"]}],
                source_connectors=connectors,
            )
            self.assertEqual("failed", result["status"])

    def test_import_rejects_failed_partial_stale_and_cross_workspace_metadata(self):
        convert_solution(self.root)
        query = yaml.safe_load(self.source.read_text())["query"]
        entry = {
            "detection": "Rule.yaml", "status": "passed", "workspaceId": WORKSPACE,
            "querySha256": hashlib.sha256(query.encode()).hexdigest(),
            "dataSources": [{"tables": ["DeviceEvents"]}],
        }
        results = self.root / "results.json"
        results.write_text(json.dumps({"results": [entry]}))
        proposed = plan_solution_dependencies(self.root, results_path=results, workspace_id=WORKSPACE)
        self.assertEqual("passed", proposed["results"][0]["validation"]["status"])
        for updates in (
            {"status": "failed"}, {"partial": True}, {"error": "permission denied"},
            {"querySha256": "stale"}, {"workspaceId": "another"},
        ):
            results.write_text(json.dumps({"results": [{**entry, **updates}]}))
            with self.assertRaises(ValueError):
                plan_solution_dependencies(self.root, results_path=results, workspace_id=WORKSPACE)

    def test_graph_projection_has_only_four_resolved_keys_and_preserves_yaml(self):
        document = self.document()
        document["contentProvenance"]["requiredDataConnectors"] = [
            {"connectorId": "Test", "dataTypes": ["DeviceEvents"]},
        ]
        before = copy.deepcopy(document)
        payload = graph_detection_payload(document, package_context={
            "packageId": "publisher.offer", "packageVersion": "3.1.2",
        })
        self.assertEqual({
            "packageId": "publisher.offer", "packageVersion": "3.1.2",
            "contentId": payload["id"], "contentVersion": document["version"],
        }, payload["contentProvenance"])
        self.assertEqual(before, document)
        self.assertNotIn("requiredWorkloads", payload["contentProvenance"])
        self.assertEqual("disabled", payload["status"])

    def test_deployment_context_uses_real_solution_metadata(self):
        (self.root / "Data").mkdir()
        (self.root / "Data/Solution_Test.json").write_text(json.dumps({
            "Version": "3.1.7", "Metadata": "SolutionMetadata.json",
        }))
        (self.root / "SolutionMetadata.json").write_text(json.dumps({
            "publisherId": "publisher", "offerId": "offer",
        }))
        self.assertEqual({"packageId": "publisher.offer", "packageVersion": "3.1.7"},
                         solution_package_context(self.root))

    def test_sdk_requests_and_captures_input_metadata_not_output_tables(self):
        metadata = [{"tables": ["DeviceEvents"]}]

        class Client:
            def query_workspace(inner_self, workspace, query, **kwargs):
                request = SimpleNamespace(http_request=SimpleNamespace(headers={"Prefer": "wait=90"}))
                kwargs["raw_request_hook"](request)
                self.assertEqual("wait=90,include-dataSources=true", request.http_request.headers["Prefer"])
                kwargs["raw_response_hook"](SimpleNamespace(
                    http_response=SimpleNamespace(
                        status_code=200, text=lambda: json.dumps({"dataSources": metadata}),
                    ),
                ))
                return success(logs_table("PrimaryResult", ["Count"], [["0"]]))

        result = execute_workspace_query(Client(), WORKSPACE, "DeviceEvents | count")
        self.assertEqual(metadata, result["dataSources"])
        self.assertEqual("PrimaryResult", result["tables"][0]["name"])

    def test_real_sdk_pipeline_preserves_wait_and_requests_input_metadata(self):
        body = {
            "dataSources": [{"tables": ["DeviceEvents"]}],
            "tables": [{"name": "PrimaryResult", "columns": [{"name": "Count", "type": "long"}], "rows": []}],
        }
        sent = []

        class Response(HttpResponse):
            def __init__(inner_self, request):
                super().__init__(request, None)
                inner_self.status_code = 200
                inner_self.headers = {"Content-Type": "application/json"}
                inner_self.content_type = "application/json"

            def body(inner_self):
                return json.dumps(body).encode()

            @property
            def content(inner_self):
                return inner_self.body()

            def json(inner_self):
                return json.loads(inner_self.body())

        class Transport(HttpTransport):
            def open(inner_self):
                pass

            def close(inner_self):
                pass

            def __exit__(inner_self, *args):
                inner_self.close()

            def send(inner_self, request, **kwargs):
                sent.append(request)
                return Response(request)

        credential = SimpleNamespace(get_token=lambda *args, **kwargs: AccessToken("mock", int(time.time()) + 3600))
        with LogsQueryClient(credential, transport=Transport()) as client:
            result = execute_workspace_query(client, WORKSPACE, "DeviceEvents | count")
        self.assertIn("include-dataSources=true", sent[0].headers["Prefer"])
        self.assertIn("wait=90", sent[0].headers["Prefer"])
        self.assertEqual(body["dataSources"], result["dataSources"])

    def test_reconversion_preserves_reviewed_dependencies_only_for_unchanged_queries(self):
        convert_solution(self.root)
        path = self.root / "XDR Detections/Rule.yaml"
        document = yaml.safe_load(path.read_text())
        reviewed = [{"workload": "mde", "dataTypes": ["DeviceEvents", "DeviceInfo"]}]
        document["contentProvenance"]["requiredWorkloads"] = reviewed
        path.write_text(yaml.safe_dump(document, sort_keys=False))
        convert_solution(self.root, overwrite=True)
        self.assertEqual(reviewed, yaml.safe_load(path.read_text())["contentProvenance"]["requiredWorkloads"])
        source = yaml.safe_load(self.source.read_text())
        source["query"] += "\n| take 1"
        self.source.write_text(yaml.safe_dump(source))
        convert_solution(self.root, overwrite=True)
        self.assertNotEqual(reviewed, yaml.safe_load(path.read_text())["contentProvenance"]["requiredWorkloads"])

    def test_helper_cli_reports_failed_dependency_comparison_with_nonzero_exit(self):
        convert_solution(self.root)
        path = self.root / "XDR Detections/Rule.yaml"
        document = yaml.safe_load(path.read_text())
        document["contentProvenance"]["requiredWorkloads"] = []
        path.write_text(yaml.safe_dump(document))
        results = self.root / "metadata.json"
        results.write_text(json.dumps({"results": [{
            "detection": "Rule.yaml", "status": "passed", "workspaceId": WORKSPACE,
            "querySha256": document["contentProvenance"]["source"]["querySha256"],
            "dataSources": [{"tables": ["DeviceEvents"]}],
        }]}))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main([
                "dependency-plan", "--solution", str(self.root),
                "--results", str(results), "--workspace-id", WORKSPACE,
            ])
        self.assertEqual(1, code)
        self.assertEqual("failed", json.loads(output.getvalue())["results"][0]["validation"]["status"])

    def test_dependency_edits_invalidate_source_validation_without_changing_query(self):
        convert_solution(self.root)
        path = self.root / "XDR Detections/Rule.yaml"
        document = yaml.safe_load(path.read_text())
        with mock.patch("sentinel_xdr_migration.runtime._runtime_consent_for_import", return_value=None):
            report = record_runtime_validation(self.root, provider="triage-mcp", results_data=[{
                "detection": "Rule.yaml", "status": "passed", "statusCode": 200,
                "querySha256": document["contentProvenance"]["source"]["querySha256"],
                "dataSources": [{"tables": ["DeviceEvents"]}],
            }])
        self.assertEqual(1, report["valid"])
        document["contentProvenance"]["requiredWorkloads"][0]["dataTypes"].append("DeviceInfo")
        path.write_text(yaml.safe_dump(document))
        evidence = current_runtime_evidence(self.root)
        self.assertFalse(evidence["passed"])
        self.assertTrue(any("dependency provenance" in issue for issue in evidence["issues"]))


if __name__ == "__main__":
    unittest.main()
